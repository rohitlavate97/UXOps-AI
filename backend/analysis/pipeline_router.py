from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from analysis.tasks import run_full_audit_pipeline
from auth.dependencies import WorkspaceAccess
from auth.models import User
from database.models import Audit
from database.session import get_db

router = APIRouter(tags=["Pipeline Analysis"])


class AnalyzeRequest(BaseModel):
    audit_id: UUID = Field(
        json_schema_extra={"example": "123e4567-e89b-12d3-a456-426614174000"}
    )


class AnalyzeResponse(BaseModel):
    message: str
    task_id: str
    audit_id: UUID


@router.post(
    "/workspaces/{workspace_id}/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger the full AI audit pipeline",
)
async def trigger_analysis(
    workspace_id: UUID,
    request: AnalyzeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        WorkspaceAccess(allowed_roles=["owner", "admin", "member"])
    ),
):
    """
    Triggers the Celery background task that runs the complete 10-agent pipeline.
    The task will asynchronously update the audit status as it progresses.
    """
    stmt = select(Audit).where(
        Audit.id == request.audit_id, Audit.workspace_id == workspace_id
    )
    result = await db.execute(stmt)
    audit = result.scalar_one_or_none()

    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit not found or does not belong to this workspace",
        )

    # Trigger Celery task
    task = run_full_audit_pipeline.delay(str(audit.id))

    return AnalyzeResponse(
        message="Analysis pipeline triggered successfully.",
        task_id=task.id,
        audit_id=audit.id,
    )
