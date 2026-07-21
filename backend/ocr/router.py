from uuid import UUID

from auth.dependencies import WorkspaceAccess, get_current_user
from auth.models import User
from database.models import Audit
from database.session import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from ocr.agent import OcrAgent
from ocr.schemas import OcrResult
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from storage.provider import get_storage_provider

router = APIRouter(tags=["OCR Engine"])


@router.get(
    "/workspaces/{workspace_id}/audits/{audit_id}/ocr",
    response_model=OcrResult,
    summary="Run OCR ground-truth text extraction for audit screenshot",
)
async def get_audit_ocr_extraction(
    workspace_id: UUID,
    audit_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        WorkspaceAccess(allowed_roles=["owner", "admin", "member", "viewer"])
    ),
):
    """Executes Agent 2 (OCR Agent) on the audit screenshot asset and returns structured ground-truth text elements."""
    stmt = select(Audit).where(
        Audit.id == audit_id, Audit.workspace_id == workspace_id
    )
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

    ocr_agent = OcrAgent(prompt_version="v1")
    ocr_result = await ocr_agent.extract_text(file_bytes, audit_id=str(audit.id))
    return ocr_result
