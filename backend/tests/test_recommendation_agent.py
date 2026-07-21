import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from analysis.recommendation_agent import RecommendationAgent
from analysis.recommendation_schemas import RecommendationResult
from auth.models import User, Workspace, WorkspaceMember
from auth.security import create_access_token
from database.models import Audit, Issue


@pytest.mark.asyncio
async def test_recommendation_agent_prioritization():
    """Test RecommendationAgent correctly maps severities to priorities and aggregates them."""
    agent = RecommendationAgent(prompt_version="v1")

    # Create mock issues
    issue1 = Issue(
        id=uuid.uuid4(),
        audit_id=uuid.uuid4(),
        workspace_id=uuid.uuid4(),
        category="ACCESSIBILITY",
        severity="CRITICAL",
        title="Missing Alt Text",
        impact="Screen readers cannot parse image.",
        recommendation="Add alt text.",
        component_ref_id="comp_1",
    )
    issue2 = Issue(
        id=uuid.uuid4(),
        audit_id=uuid.uuid4(),
        workspace_id=uuid.uuid4(),
        category="UI",
        severity="MEDIUM",
        title="Misaligned Button",
        impact="Looks slightly off.",
        recommendation="Align button.",
        component_ref_id="comp_2",
    )

    result = await agent.generate_recommendations(
        audit_id="test_audit", issues=[issue1, issue2]
    )

    assert isinstance(result, RecommendationResult)
    assert result.total_recommendations == 2
    assert result.priority_breakdown["P0"] == 1
    assert result.priority_breakdown["P2"] == 1

    # Check sorting order (P0 should be first)
    assert result.recommendations[0].priority == "P0"
    assert result.recommendations[0].issue_id == issue1.id

    assert result.recommendations[1].priority == "P2"
    assert result.recommendations[1].issue_id == issue2.id


@pytest.mark.asyncio
async def test_recommendation_agent_empty_issues():
    """Test RecommendationAgent handles empty issues gracefully."""
    agent = RecommendationAgent(prompt_version="v1")
    result = await agent.generate_recommendations("test_audit", [])

    assert result.total_recommendations == 0
    assert result.recommendations == []


@pytest.mark.asyncio
async def test_recommendation_api_endpoint_integration(
    client: AsyncClient, db_session: AsyncSession
):
    """Test HTTP GET Recommendations endpoint correctly aggregates DB issues."""
    user = User(email="rec_user@uxops.ai", hashed_password="pw", full_name="Rec User")
    workspace = Workspace(name="Rec Workspace", slug="rec-ws")
    db_session.add_all([user, workspace])
    await db_session.commit()

    member = WorkspaceMember(workspace_id=workspace.id, user_id=user.id, role="owner")

    audit = Audit(
        workspace_id=workspace.id,
        created_by_id=user.id,
        title="Rec Audit",
        status="PENDING",
    )
    db_session.add_all([member, audit])
    await db_session.commit()

    # Create issues in DB for the endpoint to find
    db_issue = Issue(
        audit_id=audit.id,
        workspace_id=workspace.id,
        category="UX",
        severity="HIGH",
        title="Confusing Navigation",
        impact="High cognitive load.",
        recommendation="Simplify nav.",
    )
    db_session.add(db_issue)
    await db_session.commit()

    token = create_access_token(str(user.id))
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(
        f"/api/v1/workspaces/{workspace.id}/audits/{audit.id}/recommendations",
        headers=headers,
    )

    assert response.status_code == 200
    res_json = response.json()
    assert res_json["audit_id"] == str(audit.id)
    assert res_json["total_recommendations"] == 1
    assert res_json["recommendations"][0]["priority"] == "P1"
    assert res_json["recommendations"][0]["issue_id"] == str(db_issue.id)
