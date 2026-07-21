from uuid import UUID

from analysis.accessibility_agent import AccessibilityAgent
from analysis.accessibility_schemas import AccessibilityResult
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

router = APIRouter(tags=["Accessibility Engine"])


@router.get(
    "/workspaces/{workspace_id}/audits/{audit_id}/accessibility",
    response_model=AccessibilityResult,
    summary="Run WCAG 2.2 accessibility audit for screenshot asset",
)
async def get_audit_accessibility_review(
    workspace_id: UUID,
    audit_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        WorkspaceAccess(allowed_roles=["owner", "admin", "member", "viewer"])
    ),
):
    """Executes Agent 4 (Accessibility Agent) on audit screenshot asset.

    Evaluates WCAG 2.2 guidelines, checks component target sizes & contrast ratios,
    persists issues to database, and updates Audit accessibility_score.
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

    # 2. Execute Agent 4 (Accessibility Agent)
    a11y_agent = AccessibilityAgent(prompt_version="v1")
    a11y_result = await a11y_agent.evaluate_accessibility(
        file_bytes, audit_id=str(audit.id), component_inventory=comp_res
    )

    # 3. Update Audit accessibility_score and persist Issues to DB
    audit.accessibility_score = a11y_result.accessibility_score

    issue_stmt = select(Issue).where(
        Issue.audit_id == audit_id,
        Issue.workspace_id == workspace_id,
        Issue.category == "ACCESSIBILITY",
    )
    existing_issues = (await db.execute(issue_stmt)).scalars().all()

    if not existing_issues:
        for issue in a11y_result.issues:
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
    return a11y_result
