from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import WorkspaceAccess
from auth.models import User
from database.models import Audit, Issue
from database.session import get_db
from reports.report_agent import ReportGenerationAgent
from reports.report_schemas import ReportFormat, ReportResult

router = APIRouter(tags=["Report Generation"])


@router.get(
    "/workspaces/{workspace_id}/audits/{audit_id}/report",
    response_model=ReportResult,
    summary="Generate a formatted audit report",
)
async def generate_audit_report(
    workspace_id: UUID,
    audit_id: UUID,
    format: ReportFormat = Query(
        ReportFormat.MARKDOWN,
        description="The desired format of the report (markdown, html, pdf, json)",
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        WorkspaceAccess(allowed_roles=["owner", "admin", "member", "viewer"])
    ),
):
    """Executes Agent 10 (Report Generation Agent) to create the final exported document.

    Reads the Audit, its associated Issues, and delegates the layout rendering
    to the Jinja2 formatting engine.
    """
    stmt = select(Audit).where(Audit.id == audit_id, Audit.workspace_id == workspace_id)
    result = await db.execute(stmt)
    audit = result.scalar_one_or_none()

    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit record not found",
        )

    # Fetch issues associated with the audit
    issue_stmt = select(Issue).where(Issue.audit_id == audit_id).order_by(Issue.created_at.desc())
    issue_result = await db.execute(issue_stmt)
    issues = issue_result.scalars().all()

    # Execute Agent 10
    agent = ReportGenerationAgent()
    try:
        report_result = agent.generate_report(
            audit=audit,
            issues=list(issues),
            output_format=format,
        )
        return report_result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation failed: {str(e)}",
        )
