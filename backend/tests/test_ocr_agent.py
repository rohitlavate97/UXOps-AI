import io
import pytest
from auth.models import User, Workspace, WorkspaceMember
from auth.security import create_access_token
from database.models import Audit
from httpx import AsyncClient
from ocr.agent import OcrAgent
from ocr.schemas import OcrResult
from sqlalchemy.ext.asyncio import AsyncSession
from storage.provider import LocalStorageProvider
from tests.test_storage import get_sample_png_bytes


@pytest.mark.asyncio
async def test_ocr_agent_extraction_lifecycle():
    """Test OcrAgent extracts text, assigns sequential element_ids, and classifies element types."""
    agent = OcrAgent(prompt_version="v1")
    sample_bytes = get_sample_png_bytes()

    result = await agent.extract_text(sample_bytes, audit_id="audit_test_123")

    assert isinstance(result, OcrResult)
    assert result.audit_id == "audit_test_123"
    assert result.total_text_elements > 0
    assert len(result.elements) == result.total_text_elements

    first_elem = result.elements[0]
    assert first_elem.element_id.startswith("txt_")
    assert first_elem.confidence > 0.0
    assert first_elem.bounding_box.width > 0
    assert first_elem.element_type in (
        "heading",
        "button_label",
        "input_label",
        "body_text",
        "nav_link",
        "error_message",
    )


@pytest.mark.asyncio
async def test_ocr_agent_empty_payload():
    """Test OcrAgent handles empty payload gracefully with 0 elements."""
    agent = OcrAgent(prompt_version="v1")
    result = await agent.extract_text(b"")

    assert result.total_text_elements == 0
    assert len(result.elements) == 0
    assert result.extracted_text_block == ""


@pytest.mark.asyncio
async def test_ocr_api_endpoint_integration(client: AsyncClient, db_session: AsyncSession):
    """Test HTTP GET OCR endpoint returns OcrResult schema."""
    user = User(email="ocr_user@uxops.ai", hashed_password="pw", full_name="OCR User")
    workspace = Workspace(name="OCR Workspace", slug="ocr-ws")
    db_session.add_all([user, workspace])
    await db_session.commit()

    member = WorkspaceMember(workspace_id=workspace.id, user_id=user.id, role="owner")
    db_session.add(member)
    await db_session.commit()

    # Save screenshot asset via LocalStorageProvider
    provider = LocalStorageProvider()
    png_bytes = get_sample_png_bytes()
    s3_key = f"workspaces/{workspace.id}/screenshots/ocr_test.png"
    await provider.upload_file(png_bytes, s3_key, "image/png")

    audit = Audit(
        workspace_id=workspace.id,
        created_by_id=user.id,
        title="OCR Extraction Audit",
        screenshot_s3_key=s3_key,
        status="PENDING",
    )
    db_session.add(audit)
    await db_session.commit()

    token = create_access_token(str(user.id))
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(
        f"/api/v1/workspaces/{workspace.id}/audits/{audit.id}/ocr",
        headers=headers,
    )

    assert response.status_code == 200
    res_json = response.json()
    assert res_json["audit_id"] == str(audit.id)
    assert "elements" in res_json
    assert len(res_json["elements"]) > 0
    assert res_json["elements"][0]["element_id"].startswith("txt_")
