import pytest
from analysis.accessibility_agent import AccessibilityAgent
from analysis.accessibility_schemas import AccessibilityResult, ContrastAnalysisResult
from auth.models import User, Workspace, WorkspaceMember
from auth.security import create_access_token
from database.models import Audit, Issue
from httpx import AsyncClient
from ocr.agent import OcrAgent
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from storage.provider import LocalStorageProvider
from tests.test_storage import get_sample_png_bytes
from vision.component_agent import ComponentDetectionAgent
from vision.component_schemas import (
    ComponentBoundingBox,
    DetectedComponent,
    ComponentInventoryResult,
)


def test_contrast_ratio_calculator():
    """Test WCAG relative luminance and contrast ratio calculations."""
    # High contrast: Black on White -> 21:1
    res_high = AccessibilityAgent.calculate_contrast_ratio("#000000", "#FFFFFF")
    assert isinstance(res_high, ContrastAnalysisResult)
    assert res_high.contrast_ratio >= 20.0
    assert res_high.passes_aa is True
    assert res_high.passes_aaa is True

    # Low contrast: Light Gray on White -> < 3:1
    res_low = AccessibilityAgent.calculate_contrast_ratio("#D1D5DB", "#FFFFFF")
    assert res_low.contrast_ratio < 4.5
    assert res_low.passes_aa is False


@pytest.mark.asyncio
async def test_accessibility_agent_lifecycle():
    """Test AccessibilityAgent evaluates WCAG rules, small tap target sizes, and scores compliance."""
    agent = AccessibilityAgent(prompt_version="v1")
    sample_bytes = get_sample_png_bytes()

    comp_inventory = ComponentInventoryResult(
        audit_id="audit_a11y_test",
        total_components=2,
        component_summary={"button": 1, "input": 1},
        components=[
            DetectedComponent(
                component_ref_id="comp_001",
                component_type="button",
                label="Tiny Button",
                bounding_box=ComponentBoundingBox(x=10, y=10, width=20, height=20),
                confidence=0.95,
            ),
            DetectedComponent(
                component_ref_id="comp_002",
                component_type="input",
                label=None,
                bounding_box=ComponentBoundingBox(x=10, y=50, width=200, height=40),
                confidence=0.92,
            ),
        ],
    )

    result = await agent.evaluate_accessibility(
        sample_bytes, audit_id="audit_a11y_test", component_inventory=comp_inventory
    )

    assert isinstance(result, AccessibilityResult)
    assert result.audit_id == "audit_a11y_test"
    assert result.total_issues >= 2
    assert result.accessibility_score < 100

    # Verify component reference mapping and automated assessment label
    for issue in result.issues:
        assert issue.component_ref_id in ("comp_001", "comp_002")
        assert issue.automated_assessment is True
        assert issue.confidence > 0.0
        assert issue.severity in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO")


@pytest.mark.asyncio
async def test_accessibility_agent_empty_payload():
    """Test AccessibilityAgent handles empty payload gracefully."""
    agent = AccessibilityAgent(prompt_version="v1")
    result = await agent.evaluate_accessibility(b"")

    assert result.total_issues == 0
    assert result.accessibility_score == 100
    assert result.issues == []


@pytest.mark.asyncio
async def test_accessibility_api_endpoint_integration(
    client: AsyncClient, db_session: AsyncSession
):
    """Test HTTP GET Accessibility endpoint returns AccessibilityResult, updates Audit score, and persists issues."""
    user = User(email="a11y_user@uxops.ai", hashed_password="pw", full_name="A11y User")
    workspace = Workspace(name="A11y Workspace", slug="a11y-ws")
    db_session.add_all([user, workspace])
    await db_session.commit()

    member = WorkspaceMember(workspace_id=workspace.id, user_id=user.id, role="owner")
    db_session.add(member)
    await db_session.commit()

    # Save screenshot asset via LocalStorageProvider
    provider = LocalStorageProvider()
    png_bytes = get_sample_png_bytes()
    s3_key = f"workspaces/{workspace.id}/screenshots/a11y_test.png"
    await provider.upload_file(png_bytes, s3_key, "image/png")

    audit = Audit(
        workspace_id=workspace.id,
        created_by_id=user.id,
        title="Accessibility Audit",
        screenshot_s3_key=s3_key,
        status="PENDING",
    )
    db_session.add(audit)
    await db_session.commit()

    token = create_access_token(str(user.id))
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(
        f"/api/v1/workspaces/{workspace.id}/audits/{audit.id}/accessibility",
        headers=headers,
    )

    assert response.status_code == 200
    res_json = response.json()
    assert res_json["audit_id"] == str(audit.id)
    assert "issues" in res_json
    assert res_json["total_issues"] > 0

    # Verify Audit score update in database
    await db_session.refresh(audit)
    assert audit.accessibility_score is not None
    assert audit.accessibility_score == res_json["accessibility_score"]

    # Verify Issue DB persistence
    stmt = select(Issue).where(
        Issue.audit_id == audit.id, Issue.category == "ACCESSIBILITY"
    )
    db_res = await db_session.execute(stmt)
    db_issues = db_res.scalars().all()
    assert len(db_issues) > 0
    assert db_issues[0].automated_assessment is True
