import io
import pytest
from auth.models import User, Workspace, WorkspaceMember
from auth.security import create_access_token
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from storage.provider import LocalStorageProvider
from storage.validator import ImageValidationError, validate_image_file


# Helper to generate valid PNG bytes (1x1 transparent PNG expanded)
def get_sample_png_bytes() -> bytes:
    return (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x02\x00\x00\x00\x01\x80"
        b"\x08\x06\x00\x00\x00\xf4\x78\xd4\xfa\x00\x00\x00\x0cIDATx\x9cc`"
        b"\x00\x00\x00\x02\x00\x01\xe2\x21\xbc\x33\x00\x00\x00\x00IEND\xaeB`\x82"
    )


@pytest.mark.asyncio
async def test_local_storage_provider_lifecycle():
    """Test LocalStorageProvider upload, retrieve, and delete operations."""
    provider = LocalStorageProvider()
    key = "test/sample_image.png"
    data = get_sample_png_bytes()

    # Upload
    saved_key = await provider.upload_file(data, key, "image/png")
    assert saved_key == key

    # Fetch
    fetched_data = await provider.get_file(key)
    assert fetched_data == data

    # Delete
    deleted = await provider.delete_file(key)
    assert deleted is True


def test_image_validation_valid_and_invalid():
    """Test image validation logic against valid PNG bytes and malicious inputs."""
    valid_png = get_sample_png_bytes()
    mime = validate_image_file(valid_png, "screenshot.png")
    assert mime == "image/png"

    # Empty payload test
    with pytest.raises(ImageValidationError, match="empty"):
        validate_image_file(b"", "empty.png")

    # Invalid header format test
    with pytest.raises(ImageValidationError, match="Unsupported image format"):
        validate_image_file(b"<html><body>Not an image</body></html>", "test.html")


@pytest.mark.asyncio
async def test_audit_upload_api_endpoint(client: AsyncClient, db_session: AsyncSession):
    """Test HTTP POST screenshot upload endpoint creates Audit and returns pre-signed URL."""
    # 1. Create User & Workspace
    user = User(email="uploader@uxops.ai", hashed_password="pw", full_name="Uploader")
    workspace = Workspace(name="Upload Workspace", slug="upload-ws")
    db_session.add_all([user, workspace])
    await db_session.commit()

    member = WorkspaceMember(workspace_id=workspace.id, user_id=user.id, role="member")
    db_session.add(member)
    await db_session.commit()

    # Token
    token = create_access_token({"sub": str(user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    # Upload POST request
    png_bytes = get_sample_png_bytes()
    files = {"file": ("dashboard.png", io.BytesIO(png_bytes), "image/png")}
    data = {"title": "Main Dashboard Audit"}

    response = await client.post(
        f"/api/v1/workspaces/{workspace.id}/audits/upload",
        headers=headers,
        data=data,
        files=files,
    )

    assert response.status_code == 201
    res_json = response.json()
    assert res_json["title"] == "Main Dashboard Audit"
    assert res_json["status"] == "PENDING"
    assert res_json["target_type"] == "image_upload"
    assert "screenshot_url" in res_json
    assert res_json["screenshot_url"] is not None


@pytest.mark.asyncio
async def test_presigned_url_api_endpoint(client: AsyncClient, db_session: AsyncSession):
    """Test HTTP POST presigned URL generation endpoint."""
    user = User(email="presign@uxops.ai", hashed_password="pw", full_name="Presigner")
    workspace = Workspace(name="Presign Workspace", slug="presign-ws")
    db_session.add_all([user, workspace])
    await db_session.commit()

    member = WorkspaceMember(workspace_id=workspace.id, user_id=user.id, role="owner")
    db_session.add(member)
    await db_session.commit()

    token = create_access_token({"sub": str(user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "title": "Direct S3 Upload Audit",
        "filename": "hero_banner.png",
        "content_type": "image/png",
    }

    response = await client.post(
        f"/api/v1/workspaces/{workspace.id}/audits/presigned-url",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 201
    res_json = response.json()
    assert "upload_url" in res_json
    assert "audit_id" in res_json
    assert res_json["s3_key"].startswith(f"workspaces/{workspace.id}/screenshots/")


@pytest.mark.asyncio
async def test_unauthorized_upload_access(client: AsyncClient, db_session: AsyncSession):
    """Verify non-workspace member is denied upload access with HTTP 403 Forbidden."""
    user = User(email="stranger@uxops.ai", hashed_password="pw", full_name="Stranger")
    workspace = Workspace(name="Private Workspace", slug="private-ws")
    db_session.add_all([user, workspace])
    await db_session.commit()

    token = create_access_token({"sub": str(user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    png_bytes = get_sample_png_bytes()
    files = {"file": ("unauthorized.png", io.BytesIO(png_bytes), "image/png")}
    data = {"title": "Unauthorized Audit Attempt"}

    response = await client.post(
        f"/api/v1/workspaces/{workspace.id}/audits/upload",
        headers=headers,
        data=data,
        files=files,
    )

    assert response.status_code == 403
