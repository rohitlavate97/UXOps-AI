import json
from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User, Workspace, WorkspaceMember
from auth.security import create_access_token
from database.models import Audit, Issue
from reports.report_agent import ReportGenerationAgent
from reports.report_schemas import ReportFormat


@pytest.fixture
def sample_audit():
    return Audit(
        id="c5b207eb-1234-4000-8000-abcd1234abcd",
        workspace_id="a1b207eb-1234-4000-8000-abcd1234abcd",
        created_by_id="b2b207eb-1234-4000-8000-abcd1234abcd",
        title="Test Audit",
        status="COMPLETED",
        overall_score=85,
        ui_score=90,
        ux_score=80,
        accessibility_score=85,
        consistency_score=85,
    )


@pytest.fixture
def sample_issues():
    return [
        Issue(
            id="d3b207eb-1234-4000-8000-abcd1234abcd",
            audit_id="c5b207eb-1234-4000-8000-abcd1234abcd",
            workspace_id="a1b207eb-1234-4000-8000-abcd1234abcd",
            title="Button Missing Contrast",
            impact="The button does not meet WCAG AA contrast.",
            severity="CRITICAL",
            category="accessibility",
            recommendation="Change background to #0055cc",
        )
    ]



def test_report_agent_json_format(sample_audit, sample_issues):
    """Test generating a JSON report."""
    agent = ReportGenerationAgent()
    result = agent.generate_report(sample_audit, sample_issues, ReportFormat.JSON)

    assert result.format == ReportFormat.JSON
    assert result.audit_id == str(sample_audit.id)

    parsed = json.loads(result.content)
    assert parsed["audit"]["overall_score"] == 85
    assert len(parsed["issues"]) == 1
    assert parsed["issues"][0]["severity"] == "CRITICAL"


def test_report_agent_markdown_format(sample_audit, sample_issues):
    """Test generating a Markdown report."""
    agent = ReportGenerationAgent()
    result = agent.generate_report(sample_audit, sample_issues, ReportFormat.MARKDOWN)

    assert result.format == ReportFormat.MARKDOWN
    assert result.audit_id == str(sample_audit.id)
    assert "85/100" in result.content
    assert "Button Missing Contrast" in result.content
    assert "`CRITICAL`" in result.content


def test_report_agent_html_format(sample_audit, sample_issues):
    """Test generating an HTML report."""
    agent = ReportGenerationAgent()
    result = agent.generate_report(sample_audit, sample_issues, ReportFormat.HTML)

    assert result.format == ReportFormat.HTML
    assert result.audit_id == str(sample_audit.id)
    assert "<!DOCTYPE html>" in result.content
    assert "UXOps AI Audit Report" in result.content
    assert "Button Missing Contrast" in result.content


@pytest.mark.asyncio
async def test_report_api_endpoint(client: AsyncClient, db_session: AsyncSession):
    """Test HTTP GET Report endpoint."""
    user = User(
        email="report_user@uxops.ai", hashed_password="pw", full_name="Report User"
    )
    workspace = Workspace(name="Report Workspace", slug="report-ws")
    db_session.add_all([user, workspace])
    await db_session.commit()

    member = WorkspaceMember(workspace_id=workspace.id, user_id=user.id, role="owner")

    audit = Audit(
        workspace_id=workspace.id,
        created_by_id=user.id,
        title="Report API Audit",
        status="COMPLETED",
        overall_score=95,
        ui_score=95,
        ux_score=95,
        accessibility_score=95,
        consistency_score=95,
    )
    db_session.add_all([member, audit])
    await db_session.commit()

    issue = Issue(
        audit_id=audit.id,
        workspace_id=workspace.id,
        title="API Test Issue",
        impact="Testing API report output.",
        severity="INFO",
        category="ux",
        recommendation="None"
    )
    db_session.add(issue)
    await db_session.commit()

    token = create_access_token(str(user.id))
    headers = {"Authorization": f"Bearer {token}"}

    # Test Markdown format
    response = await client.get(
        f"/api/v1/workspaces/{workspace.id}/audits/{audit.id}/report?format=markdown",
        headers=headers,
    )

    assert response.status_code == 200
    res_json = response.json()
    assert res_json["format"] == "markdown"
    assert "95/100" in res_json["content"]
    assert "API Test Issue" in res_json["content"]
