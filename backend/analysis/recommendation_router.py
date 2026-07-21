from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from analysis.recommendation_agent import RecommendationAgent
from analysis.recommendation_schemas import RecommendationResult
from auth.dependencies import WorkspaceAccess
from auth.models import User
from database.models import Audit, Issue
from database.session import get_db

router = APIRouter(tags=["Recommendation Engine"])


@router.get(
    "/workspaces/{workspace_id}/audits/{audit_id}/recommendations",
    response_model=RecommendationResult,
    summary="Generate prioritized recommendations for an audit",
)
async def get_audit_recommendations(
    workspace_id: UUID,
    audit_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        WorkspaceAccess(allowed_roles=["owner", "admin", "member", "viewer"])
    ),
):
    """Executes Agent 8 (Recommendation Agent) to aggregate and prioritize issues.

    Reads all defect findings from the database for the given audit and enriches
    them with prioritization and estimated impact mapping.
    """
    stmt = select(Audit).where(Audit.id == audit_id, Audit.workspace_id == workspace_id)
    result = await db.execute(stmt)
    audit = result.scalar_one_or_none()

    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit record not found",
        )

    # Fetch all issues associated with this audit
    issue_stmt = select(Issue).where(
        Issue.audit_id == audit_id,
        Issue.workspace_id == workspace_id,
    )
    issue_res = await db.execute(issue_stmt)
    issues = issue_res.scalars().all()

    # Execute Agent 8
    agent = RecommendationAgent(prompt_version="v1")
    rec_result = await agent.generate_recommendations(
        audit_id=str(audit.id),
        issues=list(issues),
    )

    return rec_result
