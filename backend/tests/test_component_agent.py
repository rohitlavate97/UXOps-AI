import pytest
from auth.models import User, Workspace, WorkspaceMember
from auth.security import create_access_token
from database.models import Audit, ComponentInventory
from httpx import AsyncClient
from ocr.agent import OcrAgent
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from storage.provider import LocalStorageProvider
from tests.test_storage import get_sample_png_bytes
from vision.component_agent import ComponentDetectionAgent
from vision.component_schemas import ComponentInventoryResult


@pytest.mark.asyncio
async def test_component_agent_lifecycle():
    """Test ComponentDetectionAgent detects UI components and links upstream OCR elements."""
    agent = ComponentDetectionAgent(prompt_version="v1")
    ocr_agent = OcrAgent(prompt_version="v1")
    sample_bytes = get_sample_png_bytes()

    ocr_result = await ocr_agent.extract_text(sample_bytes, audit_id="audit_comp_test")
    result = await agent.detect_components(
        sample_bytes, audit_id="audit_comp_test", ocr_result=ocr_result
    )

    assert isinstance(result, ComponentInventoryResult)
    assert result.audit_id == "audit_comp_test"
    assert result.total_components > 0
    assert len(result.components) == result.total_components

    first_comp = result.components[0]
    assert first_comp.component_ref_id.startswith("comp_")
    assert first_comp.confidence > 0.0
    assert first_comp.bounding_box.width > 0
    assert first_comp.component_type in (
        "button",
        "input",
        "dropdown",
        "checkbox",
        "radio",
        "card",
        "table",
        "chart",
        "image",
        "icon",
        "sidebar",
        "navbar",
        "footer",
        "modal",
        "dialog",
        "badge",
        "avatar",
        "link",
        "unknown",
    )


@pytest.mark.asyncio
async def test_component_agent_empty_payload():
    """Test ComponentDetectionAgent handles empty payload gracefully."""
    agent = ComponentDetectionAgent(prompt_version="v1")
    result = await agent.detect_components(b"")

    assert result.total_components == 0
    assert len(result.components) == 0
    assert result.component_summary == {}


@pytest.mark.asyncio
async def test_component_api_endpoint_integration(
    client: AsyncClient, db_session: AsyncSession
):
    """Test HTTP GET Components endpoint returns ComponentInventoryResult and persists records to DB."""
    user = User(email="comp_user@uxops.ai", hashed_password="pw", full_name="Comp User")
    workspace = Workspace(name="Comp Workspace", slug="comp-ws")
    db_session.add_all([user, workspace])
    await db_session.commit()

    member = WorkspaceMember(workspace_id=workspace.id, user_id=user.id, role="owner")
    db_session.add(member)
    await db_session.commit()

    # Save screenshot asset via LocalStorageProvider
    provider = LocalStorageProvider()
    png_bytes = get_sample_png_bytes()
    s3_key = f"workspaces/{workspace.id}/screenshots/comp_test.png"
    await provider.upload_file(png_bytes, s3_key, "image/png")

    audit = Audit(
        workspace_id=workspace.id,
        created_by_id=user.id,
        title="Component Detection Audit",
        screenshot_s3_key=s3_key,
        status="PENDING",
    )
    db_session.add(audit)
    await db_session.commit()

    token = create_access_token(str(user.id))
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(
        f"/api/v1/workspaces/{workspace.id}/audits/{audit.id}/components",
        headers=headers,
    )

    assert response.status_code == 200
    res_json = response.json()
    assert res_json["audit_id"] == str(audit.id)
    assert "components" in res_json
    assert len(res_json["components"]) > 0
    assert res_json["components"][0]["component_ref_id"].startswith("comp_")

    # Verify DB persistence in component_inventories table
    stmt = select(ComponentInventory).where(ComponentInventory.audit_id == audit.id)
    db_res = await db_session.execute(stmt)
    db_comps = db_res.scalars().all()
    assert len(db_comps) > 0
    assert db_comps[0].component_ref_id.startswith("comp_")
