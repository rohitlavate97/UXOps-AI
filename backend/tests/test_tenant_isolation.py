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
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_strict_multi_tenant_query_isolation(db_session: AsyncSession):
    """Verify queries scoped by workspace_id strictly isolate resources between tenants."""
    # 1. Setup Tenant Alpha
    ws_alpha = Workspace(name="Alpha Corp", slug="alpha-corp")
    # 2. Setup Tenant Beta
    ws_beta = Workspace(name="Beta Industries", slug="beta-industries")
    db_session.add_all([ws_alpha, ws_beta])
    await db_session.commit()

    # Create Audits for Alpha
    audit_alpha = Audit(workspace_id=ws_alpha.id, title="Alpha Security Audit", status="COMPLETED")
    # Create Audits for Beta
    audit_beta = Audit(workspace_id=ws_beta.id, title="Beta Mobile Audit", status="COMPLETED")
    db_session.add_all([audit_alpha, audit_beta])
    await db_session.commit()

    # Create Issues for Alpha
    issue_alpha = Issue(
        audit_id=audit_alpha.id,
        workspace_id=ws_alpha.id,
        category="ACCESSIBILITY",
        severity="HIGH",
        confidence=0.98,
        title="Alpha Contrast Flaw",
        impact="Low contrast on main action.",
        recommendation="Fix color ratio.",
    )
    # Create Issues for Beta
    issue_beta = Issue(
        audit_id=audit_beta.id,
        workspace_id=ws_beta.id,
        category="UI_DESIGN",
        severity="LOW",
        confidence=0.91,
        title="Beta Padding Flaw",
        impact="Suboptimal padding.",
        recommendation="Adjust padding.",
    )
    db_session.add_all([issue_alpha, issue_beta])

    # Create Guidelines for Alpha
    guideline_alpha = DesignGuideline(workspace_id=ws_alpha.id, title="Alpha Brand Specs")
    # Create Guidelines for Beta
    guideline_beta = DesignGuideline(workspace_id=ws_beta.id, title="Beta Brand Specs")
    db_session.add_all([guideline_alpha, guideline_beta])
    await db_session.commit()

    # --- ASSERTIONS: Querying Alpha's Workspace must return ONLY Alpha resources ---
    alpha_audits = (
        await db_session.execute(select(Audit).where(Audit.workspace_id == ws_alpha.id))
    ).scalars().all()
    assert len(alpha_audits) == 1
    assert alpha_audits[0].id == audit_alpha.id
    assert alpha_audits[0].title == "Alpha Security Audit"

    alpha_issues = (
        await db_session.execute(select(Issue).where(Issue.workspace_id == ws_alpha.id))
    ).scalars().all()
    assert len(alpha_issues) == 1
    assert alpha_issues[0].id == issue_alpha.id
    assert alpha_issues[0].title == "Alpha Contrast Flaw"

    alpha_guidelines = (
        await db_session.execute(
            select(DesignGuideline).where(DesignGuideline.workspace_id == ws_alpha.id)
        )
    ).scalars().all()
    assert len(alpha_guidelines) == 1
    assert alpha_guidelines[0].title == "Alpha Brand Specs"

    # --- ASSERTIONS: Cross-tenant lookup attempt must yield None ---
    cross_tenant_audit = (
        await db_session.execute(
            select(Audit).where(
                Audit.id == audit_alpha.id, Audit.workspace_id == ws_beta.id
            )
        )
    ).scalar_one_or_none()
    assert cross_tenant_audit is None, "Tenant Beta was able to access Tenant Alpha's audit record!"


@pytest.mark.asyncio
async def test_tenant_deletion_cascade_isolation(db_session: AsyncSession):
    """Verify deleting a tenant workspace cascades delete to its domain resources without affecting other tenants."""
    ws_del = Workspace(name="Ephemeral Corp", slug="ephemeral-corp")
    ws_safe = Workspace(name="Safe Corp", slug="safe-corp")
    db_session.add_all([ws_del, ws_safe])
    await db_session.commit()

    audit_del = Audit(workspace_id=ws_del.id, title="Ephemeral Audit", status="COMPLETED")
    audit_safe = Audit(workspace_id=ws_safe.id, title="Safe Audit", status="COMPLETED")
    db_session.add_all([audit_del, audit_safe])
    await db_session.commit()

    # Delete Ephemeral workspace
    await db_session.delete(ws_del)
    await db_session.commit()

    # Verify audit_del is removed
    deleted_audit = (
        await db_session.execute(select(Audit).where(Audit.id == audit_del.id))
    ).scalar_one_or_none()
    assert deleted_audit is None

    # Verify audit_safe is unaffected
    safe_audit = (
        await db_session.execute(select(Audit).where(Audit.id == audit_safe.id))
    ).scalar_one_or_none()
    assert safe_audit is not None
    assert safe_audit.id == audit_safe.id
