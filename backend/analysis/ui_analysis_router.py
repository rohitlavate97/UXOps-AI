from uuid import UUID

from analysis.ui_analysis_agent import UIAnalysisAgent
from analysis.ui_analysis_schemas import UIAnalysisResult
from auth.dependencies import WorkspaceAccess
from auth.models import User
from database.models import Audit, Issue
from database.session import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from ocr.agent import OcrAgent
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from storage.provider import get_storage_provider
from vision.component_agent import ComponentDetectionAgent

router = APIRouter(tags=["UI Analysis Engine"])


@router.get(
    "/workspaces/{workspace_id}/audits/{audit_id}/ui-analysis",
    response_model=UIAnalysisResult,
    summary="Run UI Analysis audit for screenshot asset",
)
async def get_audit_ui_analysis(
    workspace_id: UUID,
    audit_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        WorkspaceAccess(allowed_roles=["owner", "admin", "member", "viewer"])
    ),
):
    """Executes Agent 5 (UI Analysis Agent) on audit screenshot asset.

    Evaluates UI design principles (spacing, alignment, typography),
    persists issues to database, and updates Audit ui_score.
    """
    stmt = select(Audit).where(Audit.id == audit_id, Audit.workspace_id == workspace_id)
    result = await db.execute(stmt)
    audit = result.scalar_one_or_none()

    if not audit or not audit.screenshot_s3_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit record or screenshot asset not found",
        )

    provider = get_storage_provider()
    try:
        file_bytes = await provider.get_file(audit.screenshot_s3_key)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unable to read screenshot asset: {str(e)}",
        )

    # 1. Execute Upstream Pipeline (Agent 2 OCR + Agent 3 Component Detection)
    ocr_agent = OcrAgent(prompt_version="v1")
    ocr_res = await ocr_agent.extract_text(file_bytes, audit_id=str(audit.id))

    comp_agent = ComponentDetectionAgent(prompt_version="v1")
    comp_res = await comp_agent.detect_components(
        file_bytes, audit_id=str(audit.id), ocr_result=ocr_res
    )

    # 2. Execute Agent 5 (UI Analysis Agent)
    ui_agent = UIAnalysisAgent(prompt_version="v1")
    ui_result = await ui_agent.evaluate_ui(
        file_bytes, audit_id=str(audit.id), component_inventory=comp_res
    )

    # 3. Update Audit ui_score and persist Issues to DB
    audit.ui_score = ui_result.ui_score

    issue_stmt = select(Issue).where(
        Issue.audit_id == audit_id,
        Issue.workspace_id == workspace_id,
        Issue.category == "UI",
    )
    existing_issues = (await db.execute(issue_stmt)).scalars().all()

    if not existing_issues:
        for issue in ui_result.issues:
            db_issue = Issue(
                audit_id=audit.id,
                workspace_id=workspace_id,
                component_ref_id=issue.component_ref_id,
                category=issue.category,
                severity=issue.severity,
                confidence=issue.confidence,
                title=issue.title,
                impact=issue.impact,
                recommendation=issue.recommendation,
                automated_assessment=issue.automated_assessment,
                bounding_box=(
                    issue.bounding_box.model_dump() if issue.bounding_box else None
                ),
            )
            db.add(db_issue)

    await db.commit()
    return ui_result
