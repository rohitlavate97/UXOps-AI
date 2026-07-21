import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from analysis.scoring_agent import ScoringAgent
from analysis.scoring_schemas import ScoringResult
from auth.models import User, Workspace, WorkspaceMember
from auth.security import create_access_token
from database.models import Audit


def test_scoring_agent_math_all_scores():
    """Test deterministic math when all scores are present."""
    agent = ScoringAgent()
    # Weights: UI (0.4), UX (0.3), A11y (0.2), Consistency (0.1)
    # Total score = (100 * 0.4) + (80 * 0.3) + (50 * 0.2) + (90 * 0.1)
    # Total score = 40 + 24 + 10 + 9 = 83

    result = agent.calculate_score(
        audit_id="audit_1",
        ui_score=100,
        ux_score=80,
        accessibility_score=50,
        consistency_score=90,
    )

    assert isinstance(result, ScoringResult)
    assert result.overall_score == 83


def test_scoring_agent_math_partial_scores():
    """Test deterministic math when some scores are missing (normalizes weights)."""
    agent = ScoringAgent()
    # Weights: UI (0.4), UX (0.3), A11y (0.2), Consistency (0.1)
    # Given: UI=100, A11y=50. Missing: UX, Consistency
    # Total used weight = 0.4 + 0.2 = 0.6
    # Raw score = (100 * 0.4) + (50 * 0.2) = 40 + 10 = 50
    # Final normalized score = round(50 / 0.6) = round(83.333...) = 83

    result = agent.calculate_score(
        audit_id="audit_2",
        ui_score=100,
        ux_score=None,
        accessibility_score=50,
        consistency_score=None,
    )

    assert result.overall_score == 83


def test_scoring_agent_math_no_scores():
    """Test deterministic math when no scores are present."""
    agent = ScoringAgent()
    result = agent.calculate_score(
        audit_id="audit_3",
        ui_score=None,
        ux_score=None,
        accessibility_score=None,
        consistency_score=None,
    )

    assert result.overall_score == 0


@pytest.mark.asyncio
async def test_scoring_api_endpoint_integration(
    client: AsyncClient, db_session: AsyncSession
):
    """Test HTTP GET Score endpoint calculates score and updates DB state."""
    user = User(
        email="score_user@uxops.ai", hashed_password="pw", full_name="Score User"
    )
    workspace = Workspace(name="Score Workspace", slug="score-ws")
    db_session.add_all([user, workspace])
    await db_session.commit()

    member = WorkspaceMember(workspace_id=workspace.id, user_id=user.id, role="owner")

    audit = Audit(
        workspace_id=workspace.id,
        created_by_id=user.id,
        title="Score Audit",
        status="PENDING",
        ui_score=90,
        ux_score=90,
        accessibility_score=90,
        consistency_score=90,
    )
    db_session.add_all([member, audit])
    await db_session.commit()

    token = create_access_token(str(user.id))
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(
        f"/api/v1/workspaces/{workspace.id}/audits/{audit.id}/score",
        headers=headers,
    )

    assert response.status_code == 200
    res_json = response.json()
    assert res_json["audit_id"] == str(audit.id)
    assert res_json["overall_score"] == 90

    # Verify DB State updated
    await db_session.refresh(audit)
    assert audit.overall_score == 90
    assert audit.status == "COMPLETED"
