import pytest
from auth.models import User, Workspace
from database.models import Audit, ComponentInventory, Issue, Report
from database.seed import seed_database
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_seed_database_execution(db_session: AsyncSession):
    """Test that seed_database initializes all sample users, workspaces, audits, components, issues, and reports."""
    await seed_database(session=db_session)
    session = db_session

    # Verify Users
    users = (await session.execute(select(User))).scalars().all()
    assert len(users) >= 2
    emails = [u.email for u in users]
    assert "admin@uxops.ai" in emails
    assert "designer@uxops.ai" in emails

    # Verify Workspaces
    workspaces = (await session.execute(select(Workspace))).scalars().all()
    assert len(workspaces) >= 2
    slugs = [w.slug for w in workspaces]
    assert "acme-design" in slugs

    # Verify Audits
    audits = (await session.execute(select(Audit))).scalars().all()
    assert len(audits) >= 2

    # Verify Components & Issues
    components = (await session.execute(select(ComponentInventory))).scalars().all()
    assert len(components) >= 3

    issues = (await session.execute(select(Issue))).scalars().all()
    assert len(issues) >= 2
    assert issues[0].category == "ACCESSIBILITY"

    # Verify Report
    reports = (await session.execute(select(Report))).scalars().all()
    assert len(reports) >= 1
