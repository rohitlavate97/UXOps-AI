import asyncio
import logging
import os
import sys
from typing import Optional

# Ensure backend root is in sys.path
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from auth.models import User, Workspace, WorkspaceMember
from auth.service import get_password_hash
from database.base_class import Base
from database.models import (
    Audit,
    ComponentInventory,
    DesignGuideline,
    Issue,
    Report,
)
from database.session import async_engine
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uxops_seed")


async def seed_database(session: Optional[AsyncSession] = None) -> None:
    """Populate database with sample workspaces, users, audits, and design guidelines."""
    if session is not None:
        await _seed_with_session(session)
        return

    logger.info("Initializing database schema if not present...")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        await _seed_with_session(session)


async def _seed_with_session(session: AsyncSession) -> None:
    # Check idempotency
    stmt = select(User).where(User.email == "admin@uxops.ai")
    result = await session.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        logger.info("Seed data already present in database. Skipping seed.")
        return

    logger.info("Seeding users...")
    hashed_password = get_password_hash("password123")
    admin_user = User(
        email="admin@uxops.ai",
        hashed_password=hashed_password,
        full_name="Enterprise Admin",
        is_superuser=True,
    )
    designer_user = User(
        email="designer@uxops.ai",
        hashed_password=hashed_password,
        full_name="Lead UX Designer",
        is_superuser=False,
    )
    session.add_all([admin_user, designer_user])
    await session.commit()
    await session.refresh(admin_user)
    await session.refresh(designer_user)

    logger.info("Seeding workspaces...")
    acme_workspace = Workspace(
        name="Acme Corp Design Systems",
        slug="acme-design",
    )
    fintech_workspace = Workspace(
        name="Fintech Mobile App",
        slug="fintech-mobile",
    )
    session.add_all([acme_workspace, fintech_workspace])
    await session.commit()
    await session.refresh(acme_workspace)
    await session.refresh(fintech_workspace)

    logger.info("Seeding workspace memberships...")
    memberships = [
        WorkspaceMember(
            workspace_id=acme_workspace.id,
            user_id=admin_user.id,
            role="owner",
        ),
        WorkspaceMember(
            workspace_id=acme_workspace.id,
            user_id=designer_user.id,
            role="member",
        ),
        WorkspaceMember(
            workspace_id=fintech_workspace.id,
            user_id=admin_user.id,
            role="owner",
        ),
    ]
    session.add_all(memberships)
    await session.commit()

    logger.info("Seeding audit runs...")
    checkout_audit = Audit(
        workspace_id=acme_workspace.id,
        created_by_id=designer_user.id,
        title="Checkout Flow Q3 Audit",
        target_type="image_upload",
        screenshot_s3_key=f"workspaces/{acme_workspace.id}/screenshots/checkout.png",
        status="COMPLETED",
        overall_score=88,
        ui_score=92,
        ux_score=85,
        accessibility_score=82,
        consistency_score=90,
        readability_score=91,
    )
    dashboard_audit = Audit(
        workspace_id=fintech_workspace.id,
        created_by_id=admin_user.id,
        title="Mobile Dashboard Audit",
        target_type="image_upload",
        screenshot_s3_key=f"workspaces/{fintech_workspace.id}/screenshots/dashboard.png",
        status="COMPLETED",
        overall_score=94,
        ui_score=96,
        ux_score=92,
        accessibility_score=90,
        consistency_score=95,
        readability_score=97,
    )
    session.add_all([checkout_audit, dashboard_audit])
    await session.commit()
    await session.refresh(checkout_audit)
    await session.refresh(dashboard_audit)

    logger.info("Seeding component inventories...")
    components = [
        ComponentInventory(
            audit_id=checkout_audit.id,
            workspace_id=acme_workspace.id,
            component_ref_id="comp_001",
            component_type="button",
            label="Pay Now",
            bounding_box={"x": 120, "y": 450, "width": 200, "height": 48},
            confidence=0.98,
        ),
        ComponentInventory(
            audit_id=checkout_audit.id,
            workspace_id=acme_workspace.id,
            component_ref_id="comp_002",
            component_type="input",
            label="Card Number",
            bounding_box={"x": 120, "y": 200, "width": 400, "height": 40},
            confidence=0.96,
        ),
        ComponentInventory(
            audit_id=dashboard_audit.id,
            workspace_id=fintech_workspace.id,
            component_ref_id="comp_003",
            component_type="navbar",
            label="Header Navigation",
            bounding_box={"x": 0, "y": 0, "width": 375, "height": 64},
            confidence=0.99,
        ),
    ]
    session.add_all(components)

    logger.info("Seeding issues...")
    issues = [
        Issue(
            audit_id=checkout_audit.id,
            workspace_id=acme_workspace.id,
            component_ref_id="comp_001",
            category="ACCESSIBILITY",
            severity="HIGH",
            confidence=0.95,
            title="Insufficient Button Color Contrast",
            impact="Low contrast between button background (#7C3AED) and text (#A78BFA) fails WCAG 2.2 AA standards (ratio 3.2:1 < 4.5:1).",
            recommendation="Change button text color to white (#FFFFFF) to achieve a contrast ratio of 5.8:1.",
            automated_assessment=True,
            bounding_box={"x": 120, "y": 450, "width": 200, "height": 48},
        ),
        Issue(
            audit_id=checkout_audit.id,
            workspace_id=acme_workspace.id,
            component_ref_id="comp_002",
            category="UI_CONSISTENCY",
            severity="MEDIUM",
            confidence=0.91,
            title="Missing Active Input State Border",
            impact="Focused input field lacks visual focus outline or border highlight.",
            recommendation="Add a 2px blue focus ring (#2563EB) on focus.",
            automated_assessment=True,
            bounding_box={"x": 120, "y": 200, "width": 400, "height": 40},
        ),
    ]
    session.add_all(issues)

    logger.info("Seeding reports...")
    report = Report(
        audit_id=checkout_audit.id,
        workspace_id=acme_workspace.id,
        executive_summary="Checkout Flow Q3 Audit identified 2 primary findings across Accessibility and UI Consistency.",
        summary_json={
            "total_issues": 2,
            "severity_breakdown": {"HIGH": 1, "MEDIUM": 1, "LOW": 0},
        },
    )
    session.add(report)

    logger.info("Seeding design guidelines...")
    guideline = DesignGuideline(
        workspace_id=acme_workspace.id,
        title="Acme Brand & Design System 2026",
        description="Official Acme Corp design system documentation covering typography, colors, and accessibility rules.",
    )
    session.add(guideline)

    await session.commit()
    logger.info("Database seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())
