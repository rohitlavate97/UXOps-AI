import uuid
import pytest
from auth.models import User, Workspace
from database.models import (
    Audit,
    ComponentInventory,
    DesignGuideline,
    Issue,
    Report,
)
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_audit_model_creation_and_relationships(db_session: AsyncSession):
    """Test creating an Audit instance with related User and Workspace."""
    user = User(
        email="auditor@uxops.ai",
        hashed_password="hashedpassword123",
        full_name="Audit Tester",
    )
    workspace = Workspace(name="Design Audit Org", slug="design-audit-org")
    db_session.add_all([user, workspace])
    await db_session.commit()
    await db_session.refresh(user)
    await db_session.refresh(workspace)

    audit = Audit(
        workspace_id=workspace.id,
        created_by_id=user.id,
        title="Homepage Audit Q3",
        target_type="image_upload",
        status="PENDING",
        overall_score=88,
    )
    db_session.add(audit)
    await db_session.commit()
    await db_session.refresh(audit)

    assert audit.id is not None
    assert audit.title == "Homepage Audit Q3"
    assert audit.status == "PENDING"
    assert audit.overall_score == 88
    assert audit.workspace_id == workspace.id
    assert audit.created_by_id == user.id


@pytest.mark.asyncio
async def test_component_inventory_and_issues(db_session: AsyncSession):
    """Test ComponentInventory and Issue referential binding for downstream vision agents."""
    workspace = Workspace(name="Component Test Org", slug="component-test-org")
    db_session.add(workspace)
    await db_session.commit()

    audit = Audit(
        workspace_id=workspace.id,
        title="Checkout Page Audit",
        status="PROCESSING",
    )
    db_session.add(audit)
    await db_session.commit()

    component = ComponentInventory(
        audit_id=audit.id,
        workspace_id=workspace.id,
        component_ref_id="comp_01",
        component_type="button",
        label="Submit Order",
        bounding_box={"x": 50, "y": 100, "width": 120, "height": 40},
        confidence=0.98,
    )
    issue = Issue(
        audit_id=audit.id,
        workspace_id=workspace.id,
        component_ref_id="comp_01",
        category="ACCESSIBILITY",
        severity="HIGH",
        confidence=0.95,
        title="Low Contrast Primary Button",
        impact="Low contrast ratio 2.8:1 violates WCAG 2.2 AA standards.",
        recommendation="Adjust background color to increase contrast ratio to >= 4.5:1.",
        automated_assessment=True,
    )
    db_session.add_all([component, issue])
    await db_session.commit()

    assert component.component_ref_id == "comp_01"
    assert issue.component_ref_id == component.component_ref_id
    assert issue.severity == "HIGH"
    assert issue.automated_assessment is True


@pytest.mark.asyncio
async def test_report_and_design_guidelines(db_session: AsyncSession):
    """Test Report summary creation and DesignGuideline entity."""
    workspace = Workspace(name="Report Org", slug="report-org")
    db_session.add(workspace)
    await db_session.commit()

    audit = Audit(workspace_id=workspace.id, title="Dashboard Audit", status="COMPLETED")
    db_session.add(audit)
    await db_session.commit()

    report = Report(
        audit_id=audit.id,
        workspace_id=workspace.id,
        executive_summary="The dashboard exhibits minor spacing flaws.",
        summary_json={"total_issues": 3, "score": 91},
    )
    guideline = DesignGuideline(
        workspace_id=workspace.id,
        title="Brand Identity System v2",
        description="Official primary color palette and typography rules.",
    )
    db_session.add_all([report, guideline])
    await db_session.commit()

    assert report.id is not None
    assert report.audit_id == audit.id
    assert guideline.id is not None
    assert guideline.title == "Brand Identity System v2"
