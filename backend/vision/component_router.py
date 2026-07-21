from uuid import UUID

from auth.dependencies import WorkspaceAccess
from auth.models import User
from database.models import Audit, ComponentInventory
from database.session import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from ocr.agent import OcrAgent
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from storage.provider import get_storage_provider
from vision.component_agent import ComponentDetectionAgent
from vision.component_schemas import ComponentInventoryResult

router = APIRouter(tags=["Component Detection"])


@router.get(
    "/workspaces/{workspace_id}/audits/{audit_id}/components",
    response_model=ComponentInventoryResult,
    summary="Detect UI components and establish authoritative component inventory",
)
async def get_audit_component_inventory(
    workspace_id: UUID,
    audit_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        WorkspaceAccess(allowed_roles=["owner", "admin", "member", "viewer"])
    ),
):
    """Executes Agent 3 (Component Detection Agent) on audit screenshot asset.

    Establishes the authoritative component inventory (comp_001, comp_002, ...)
    and performs cross-agent referential integrity check with upstream OCR text elements.
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

    # 1. Execute Upstream Agent 2 (OCR Agent)
    ocr_agent = OcrAgent(prompt_version="v1")
    ocr_result = await ocr_agent.extract_text(file_bytes, audit_id=str(audit.id))

    # 2. Execute Agent 3 (Component Detection Agent)
    comp_agent = ComponentDetectionAgent(prompt_version="v1")
    inventory = await comp_agent.detect_components(
        file_bytes, audit_id=str(audit.id), ocr_result=ocr_result
    )

    # 3. Persist authoritative component inventory entries to DB if missing
    comp_stmt = select(ComponentInventory).where(
        ComponentInventory.audit_id == audit_id,
        ComponentInventory.workspace_id == workspace_id,
    )
    comp_res = await db.execute(comp_stmt)
    existing_comps = comp_res.scalars().all()

    if not existing_comps:
        for comp in inventory.components:
            db_comp = ComponentInventory(
                audit_id=audit.id,
                workspace_id=workspace_id,
                component_ref_id=comp.component_ref_id,
                component_type=comp.component_type,
                label=comp.label,
                bounding_box=comp.bounding_box.model_dump(),
                confidence=comp.confidence,
            )
            db.add(db_comp)
        await db.commit()

    return inventory
