from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from analysis.scoring_agent import ScoringAgent
from analysis.scoring_schemas import ScoringResult
from auth.dependencies import WorkspaceAccess
from auth.models import User
from database.models import Audit
from database.session import get_db

router = APIRouter(tags=["Scoring Engine"])


@router.get(
    "/workspaces/{workspace_id}/audits/{audit_id}/score",
    response_model=ScoringResult,
    summary="Calculate final audit score and complete audit",
)
async def get_audit_score(
    workspace_id: UUID,
    audit_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        WorkspaceAccess(allowed_roles=["owner", "admin", "member", "viewer"])
    ),
):
    """Executes Agent 9 (Scoring Agent) to finalize the audit.

    Reads the sub-scores from the database, runs the deterministic weighting calculation,
    updates the overall_score, and transitions the Audit status to COMPLETED.
    """
    stmt = select(Audit).where(Audit.id == audit_id, Audit.workspace_id == workspace_id)
    result = await db.execute(stmt)
    audit = result.scalar_one_or_none()

    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit record not found",
        )

    # Execute Agent 9
    agent = ScoringAgent()
    scoring_result = agent.calculate_score(
        audit_id=str(audit.id),
        ui_score=audit.ui_score,
        ux_score=audit.ux_score,
        accessibility_score=audit.accessibility_score,
        consistency_score=audit.consistency_score,
    )

    # Update Audit record
    audit.overall_score = scoring_result.overall_score
    audit.status = "COMPLETED"

    await db.commit()

    return scoring_result
