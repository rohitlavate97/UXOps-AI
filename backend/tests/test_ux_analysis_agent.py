import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from analysis.ux_analysis_agent import UXAnalysisAgent
from analysis.ux_analysis_schemas import UXAnalysisResult
from auth.models import User, Workspace, WorkspaceMember
from auth.security import create_access_token
from database.models import Audit, Issue
from storage.provider import LocalStorageProvider
from tests.test_storage import get_sample_png_bytes
from vision.component_schemas import (ComponentBoundingBox,
                                      ComponentInventoryResult,
                                      DetectedComponent)


@pytest.mark.asyncio
async def test_ux_analysis_agent_lifecycle():
    """Test UXAnalysisAgent evaluates discoverability and cognitive load rules."""
    agent = UXAnalysisAgent(prompt_version="v1")
    sample_bytes = get_sample_png_bytes()

    comp_inventory = ComponentInventoryResult(
        audit_id="audit_ux_test",
        total_components=1,
        component_summary={"input": 1},
        components=[
            DetectedComponent(
                component_ref_id="comp_001",
                component_type="input",
                label=None,  # Missing label, should trigger Discoverability issue
                bounding_box=ComponentBoundingBox(x=10, y=10, width=200, height=40),
                confidence=0.95,
            )
        ],
    )

    result = await agent.evaluate_ux(
        sample_bytes, audit_id="audit_ux_test", component_inventory=comp_inventory
    )

    assert isinstance(result, UXAnalysisResult)
    assert result.audit_id == "audit_ux_test"
    assert result.total_issues > 0
    assert result.ux_score < 100

    # Verify component reference mapping
    for issue in result.issues:
        assert issue.component_ref_id in ("comp_001", None)
        assert issue.automated_assessment is True
        assert issue.confidence > 0.0
        assert issue.severity in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO")
        assert issue.category == "UX"


@pytest.mark.asyncio
async def test_ux_analysis_agent_empty_payload():
    """Test UXAnalysisAgent handles empty payload gracefully."""
    agent = UXAnalysisAgent(prompt_version="v1")
    result = await agent.evaluate_ux(b"")

    assert result.total_issues == 0
    assert result.ux_score == 100
    assert result.issues == []


@pytest.mark.asyncio
async def test_ux_analysis_api_endpoint_integration(
    client: AsyncClient, db_session: AsyncSession
):
    """Test HTTP GET UX Analysis endpoint returns UXAnalysisResult, updates Audit score, and persists issues."""
    user = User(email="ux_user@uxops.ai", hashed_password="pw", full_name="UX User")
    workspace = Workspace(name="UX Workspace", slug="ux-ws")
    db_session.add_all([user, workspace])
    await db_session.commit()

    member = WorkspaceMember(workspace_id=workspace.id, user_id=user.id, role="owner")
    db_session.add(member)
    await db_session.commit()

    # Save screenshot asset via LocalStorageProvider
    provider = LocalStorageProvider()
    png_bytes = get_sample_png_bytes()
    s3_key = f"workspaces/{workspace.id}/screenshots/ux_test.png"
    await provider.upload_file(png_bytes, s3_key, "image/png")

    audit = Audit(
        workspace_id=workspace.id,
        created_by_id=user.id,
        title="UX Analysis Audit",
        screenshot_s3_key=s3_key,
        status="PENDING",
    )
    db_session.add(audit)
    await db_session.commit()

    token = create_access_token(str(user.id))
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(
        f"/api/v1/workspaces/{workspace.id}/audits/{audit.id}/ux-analysis",
        headers=headers,
    )

    assert response.status_code == 200
    res_json = response.json()
    assert res_json["audit_id"] == str(audit.id)
    assert "issues" in res_json
    assert res_json["total_issues"] > 0

    # Verify Audit score update in database
    await db_session.refresh(audit)
    assert audit.ux_score is not None
    assert audit.ux_score == res_json["ux_score"]

    # Verify Issue DB persistence
    stmt = select(Issue).where(Issue.audit_id == audit.id, Issue.category == "UX")
    db_res = await db_session.execute(stmt)
    db_issues = db_res.scalars().all()
    assert len(db_issues) > 0
    assert db_issues[0].automated_assessment is True
