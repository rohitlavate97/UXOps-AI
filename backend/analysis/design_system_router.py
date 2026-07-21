from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from analysis.design_system_agent import DesignSystemAgent
from analysis.design_system_schemas import DesignSystemResult
from auth.dependencies import WorkspaceAccess
from auth.models import User
from database.models import Audit, DesignGuideline, Issue
from database.session import get_db
from ocr.agent import OcrAgent
from storage.provider import get_storage_provider
from vision.component_agent import ComponentDetectionAgent

router = APIRouter(tags=["Design System Engine"])


@router.get(
    "/workspaces/{workspace_id}/audits/{audit_id}/design-system",
    response_model=DesignSystemResult,
    summary="Run Design System audit for screenshot asset",
)
async def get_audit_design_system(
    workspace_id: UUID,
    audit_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        WorkspaceAccess(allowed_roles=["owner", "admin", "member", "viewer"])
    ),
):
    """Executes Agent 7 (Design System Agent) on audit screenshot asset.

    Evaluates Design System heuristics against standard frameworks and custom RAG guidelines,
    persists issues to database, and updates Audit consistency_score.
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

    # 2. Retrieve RAG Design Guidelines (if any exist for the workspace)
    guideline_stmt = select(DesignGuideline).where(
        DesignGuideline.workspace_id == workspace_id
    )
    guideline_res = await db.execute(guideline_stmt)
    guidelines = guideline_res.scalars().all()

    # Combine texts if multiple
    rag_text = None
    if guidelines:
        rag_text = "\n".join(g.description for g in guidelines if g.description)

    # 3. Execute Agent 7 (Design System Agent)
    ds_agent = DesignSystemAgent(prompt_version="v1")
    ds_result = await ds_agent.evaluate_design_system(
        file_bytes,
        audit_id=str(audit.id),
        component_inventory=comp_res,
        design_guidelines_text=rag_text,
    )

    # 4. Update Audit consistency_score and persist Issues to DB
    if hasattr(audit, "consistency_score"):
        audit.consistency_score = ds_result.design_system_score

    issue_stmt = select(Issue).where(
        Issue.audit_id == audit_id,
        Issue.workspace_id == workspace_id,
        Issue.category == "DESIGN_SYSTEM",
    )
    existing_issues = (await db.execute(issue_stmt)).scalars().all()

    if not existing_issues:
        for issue in ds_result.issues:
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
    return ds_result
