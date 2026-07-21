import asyncio
import logging
import os
import sys

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


async def seed_database() -> None:
    """Populate database with sample workspaces, users, audits, and design guidelines."""
    logger.info("Initializing database schema if not present...")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
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

        logger.info("Seeding sample audit runs...")
        checkout_audit = Audit(
            workspace_id=acme_workspace.id,
            created_by_id=designer_user.id,
            title="Checkout Page Q3 Audit",
            target_type="image_upload",
            target_url="https://checkout.acme.com",
            screenshot_s3_key="screenshots/checkout_q3.png",
            annotated_s3_key="annotated/checkout_q3_annotated.png",
            status="COMPLETED",
            overall_score=88,
            ui_score=90,
            ux_score=85,
            accessibility_score=89,
            consistency_score=92,
            readability_score=84,
        )
        dashboard_audit = Audit(
            workspace_id=acme_workspace.id,
            created_by_id=admin_user.id,
            title="Analytics Dashboard Audit",
            target_type="url",
            target_url="https://app.acme.com/analytics",
            status="PROCESSING",
        )
        session.add_all([checkout_audit, dashboard_audit])
        await session.commit()
        await session.refresh(checkout_audit)
        await session.refresh(dashboard_audit)

        logger.info("Seeding component inventory...")
        components = [
            ComponentInventory(
                audit_id=checkout_audit.id,
                workspace_id=acme_workspace.id,
                component_ref_id="comp_01",
                component_type="button",
                label="Complete Purchase",
                bounding_box={"x": 120, "y": 450, "width": 200, "height": 48},
                confidence=0.97,
            ),
            ComponentInventory(
                audit_id=checkout_audit.id,
                workspace_id=acme_workspace.id,
                component_ref_id="comp_02",
                component_type="input",
                label="Cardholder Name",
                bounding_box={"x": 120, "y": 280, "width": 400, "height": 40},
                confidence=0.99,
            ),
            ComponentInventory(
                audit_id=checkout_audit.id,
                workspace_id=acme_workspace.id,
                component_ref_id="comp_03",
                component_type="navbar",
                label="Main Header Nav",
                bounding_box={"x": 0, "y": 0, "width": 1440, "height": 64},
                confidence=0.95,
            ),
        ]
        session.add_all(components)

        logger.info("Seeding sample issues...")
        issues = [
            Issue(
                audit_id=checkout_audit.id,
                workspace_id=acme_workspace.id,
                component_ref_id="comp_01",
                category="ACCESSIBILITY",
                severity="HIGH",
                confidence=0.96,
                title="Low Contrast on Primary Action Button",
                impact="Contrast ratio 3.1:1 fails WCAG 2.2 AA minimum requirement (4.5:1).",
                recommendation="Darken button background from #4A90E2 to #1F60B8 for higher contrast.",
                automated_assessment=True,
                bounding_box={"x": 120, "y": 450, "width": 200, "height": 48},
            ),
            Issue(
                audit_id=checkout_audit.id,
                workspace_id=acme_workspace.id,
                component_ref_id="comp_02",
                category="UI_DESIGN",
                severity="MEDIUM",
                confidence=0.92,
                title="Inconsistent Input Margin Spacing",
                impact="Cardholder Name input padding is 14px instead of design system 16px standard.",
                recommendation="Set vertical and horizontal padding to 16px.",
                automated_assessment=True,
                bounding_box={"x": 120, "y": 280, "width": 400, "height": 40},
            ),
        ]
        session.add_all(issues)

        logger.info("Seeding sample audit report...")
        report = Report(
            audit_id=checkout_audit.id,
            workspace_id=acme_workspace.id,
            executive_summary="The checkout page demonstrates strong visual hierarchy but requires primary CTA contrast adjustment to achieve WCAG 2.2 compliance.",
            summary_json={
                "overall_score": 88,
                "issues_count": {"HIGH": 1, "MEDIUM": 1, "LOW": 0},
                "key_takeaway": "Darken primary CTA button background.",
            },
            pdf_s3_key="reports/checkout_q3_report.pdf",
        )
        session.add(report)

        logger.info("Seeding design guidelines...")
        guideline = DesignGuideline(
            workspace_id=acme_workspace.id,
            title="Acme Brand & Design System 2026",
            description="Official guidelines specifying color tokens, typography scales, and WCAG AA contrast rules.",
            doc_s3_key="guidelines/acme_design_system_2026.pdf",
        )
        session.add(guideline)

        await session.commit()
        logger.info("Database seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_database())
