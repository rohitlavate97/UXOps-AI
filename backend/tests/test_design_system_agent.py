import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from analysis.design_system_agent import DesignSystemAgent
from analysis.design_system_schemas import DesignSystemResult
from auth.models import User, Workspace, WorkspaceMember
from auth.security import create_access_token
from database.models import Audit, DesignGuideline, Issue
from storage.provider import LocalStorageProvider
from tests.test_storage import get_sample_png_bytes
from vision.component_schemas import (ComponentBoundingBox,
                                      ComponentInventoryResult,
                                      DetectedComponent)


@pytest.mark.asyncio
async def test_design_system_agent_lifecycle():
    """Test DesignSystemAgent evaluates material constraints and RAG rules."""
    agent = DesignSystemAgent(prompt_version="v1")
    sample_bytes = get_sample_png_bytes()

    comp_inventory = ComponentInventoryResult(
        audit_id="audit_ds_test",
        total_components=1,
        component_summary={"button": 1},
        components=[
            DetectedComponent(
                component_ref_id="comp_001",
                component_type="button",
                label="Submit",
                bounding_box=ComponentBoundingBox(
                    x=10, y=10, width=100, height=40
                ),  # Height < 48 to trigger issue
                confidence=0.95,
            )
        ],
    )

    # First test standard Material constraint (height < 48)
    result = await agent.evaluate_design_system(
        sample_bytes, audit_id="audit_ds_test", component_inventory=comp_inventory
    )

    assert isinstance(result, DesignSystemResult)
    assert result.audit_id == "audit_ds_test"
    assert result.total_issues > 0
    assert result.design_system_score < 100

    assert any(
        issue.title == "Insufficient Touch Target Height" for issue in result.issues
    )

    # Now test with RAG guideline injected
    result_rag = await agent.evaluate_design_system(
        sample_bytes,
        audit_id="audit_ds_test",
        component_inventory=comp_inventory,
        design_guidelines_text="Our buttons must use an 8px border radius.",
    )
    assert any(issue.title == "Border Radius Deviation" for issue in result_rag.issues)


@pytest.mark.asyncio
async def test_design_system_agent_empty_payload():
    """Test DesignSystemAgent handles empty payload gracefully."""
    agent = DesignSystemAgent(prompt_version="v1")
    result = await agent.evaluate_design_system(b"", audit_id="audit_empty")

    assert result.total_issues == 0
    assert result.design_system_score == 100
    assert result.issues == []


@pytest.mark.asyncio
async def test_design_system_api_endpoint_integration(
    client: AsyncClient, db_session: AsyncSession
):
    """Test HTTP GET Design System endpoint returns DesignSystemResult, updates score, and reads Guidelines."""
    user = User(email="ds_user@uxops.ai", hashed_password="pw", full_name="DS User")
    workspace = Workspace(name="DS Workspace", slug="ds-ws")
    db_session.add_all([user, workspace])
    await db_session.commit()

    member = WorkspaceMember(workspace_id=workspace.id, user_id=user.id, role="owner")

    # Add a mock Design Guideline for the RAG lookup
    guideline = DesignGuideline(
        workspace_id=workspace.id,
        title="Company Theme",
        description="Our buttons must use an 8px border radius.",
    )
    db_session.add_all([member, guideline])
    await db_session.commit()

    # Save screenshot asset via LocalStorageProvider
    provider = LocalStorageProvider()
    png_bytes = get_sample_png_bytes()
    s3_key = f"workspaces/{workspace.id}/screenshots/ds_test.png"
    await provider.upload_file(png_bytes, s3_key, "image/png")

    audit = Audit(
        workspace_id=workspace.id,
        created_by_id=user.id,
        title="Design System Audit",
        screenshot_s3_key=s3_key,
        status="PENDING",
    )
    db_session.add(audit)
    await db_session.commit()

    token = create_access_token(str(user.id))
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(
        f"/api/v1/workspaces/{workspace.id}/audits/{audit.id}/design-system",
        headers=headers,
    )

    assert response.status_code == 200
    res_json = response.json()
    assert res_json["audit_id"] == str(audit.id)
    assert "issues" in res_json
    assert res_json["total_issues"] > 0

    # Verify Audit score update in database
    await db_session.refresh(audit)
    assert audit.consistency_score is not None
    assert audit.consistency_score == res_json["design_system_score"]

    # Verify Issue DB persistence
    stmt = select(Issue).where(
        Issue.audit_id == audit.id, Issue.category == "DESIGN_SYSTEM"
    )
    db_res = await db_session.execute(stmt)
    db_issues = db_res.scalars().all()
    assert len(db_issues) > 0
    assert db_issues[0].automated_assessment is True
