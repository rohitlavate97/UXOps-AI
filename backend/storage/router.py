import uuid
from uuid import UUID

from auth.dependencies import WorkspaceAccess, get_current_user
from auth.models import User
from database.models import Audit
from database.session import get_db
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from storage.provider import get_storage_provider
from storage.schemas import AuditResponse, PresignedUrlRequest, PresignedUrlResponse
from storage.validator import ImageValidationError, validate_image_file

router = APIRouter(tags=["Audits & Storage"])


@router.post(
    "/workspaces/{workspace_id}/audits/upload",
    response_model=AuditResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload UI screenshot and create audit run",
)
async def upload_audit_screenshot(
    workspace_id: UUID,
    title: str = Form(..., max_length=255),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        WorkspaceAccess(allowed_roles=["owner", "admin", "member"])
    ),
):
    """Uploads a UI screenshot file, validates format/dimensions, saves to object storage, and initializes an Audit record."""
    file_bytes = await file.read()

    try:
        content_type = validate_image_file(file_bytes, file.filename or "screenshot.png")
    except ImageValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Generate storage key
    s3_key = f"workspaces/{workspace_id}/screenshots/{uuid.uuid4().hex}_{file.filename}"
    provider = get_storage_provider()
    saved_key = await provider.upload_file(file_bytes, s3_key, content_type)

    audit = Audit(
        workspace_id=workspace_id,
        created_by_id=current_user.id,
        title=title,
        target_type="image_upload",
        screenshot_s3_key=saved_key,
        status="PENDING",
    )
    db.add(audit)
    await db.commit()
    await db.refresh(audit)

    screenshot_url = await provider.get_presigned_download_url(saved_key)
    res = AuditResponse.model_validate(audit)
    res.screenshot_url = screenshot_url
    return res


@router.post(
    "/workspaces/{workspace_id}/audits/presigned-url",
    response_model=PresignedUrlResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate pre-signed S3 upload URL for direct upload",
)
async def generate_presigned_upload_url(
    workspace_id: UUID,
    payload: PresignedUrlRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        WorkspaceAccess(allowed_roles=["owner", "admin", "member"])
    ),
):
    """Generates a pre-signed S3 upload URL allowing direct client browser upload."""
    s3_key = f"workspaces/{workspace_id}/screenshots/{uuid.uuid4().hex}_{payload.filename}"
    provider = get_storage_provider()
    upload_url = await provider.get_presigned_upload_url(s3_key, payload.content_type)

    audit = Audit(
        workspace_id=workspace_id,
        created_by_id=current_user.id,
        title=payload.title,
        target_type="image_upload",
        screenshot_s3_key=s3_key,
        status="PENDING",
    )
    db.add(audit)
    await db.commit()
    await db.refresh(audit)

    return PresignedUrlResponse(
        audit_id=audit.id,
        upload_url=upload_url,
        s3_key=s3_key,
        expires_in=3600,
    )


@router.get(
    "/workspaces/{workspace_id}/audits/{audit_id}",
    response_model=AuditResponse,
    summary="Get audit details and pre-signed image download URL",
)
async def get_audit_by_id(
    workspace_id: UUID,
    audit_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        WorkspaceAccess(allowed_roles=["owner", "admin", "member", "viewer"])
    ),
):
    """Fetches single audit record scoped by workspace ID."""
    stmt = select(Audit).where(
        Audit.id == audit_id, Audit.workspace_id == workspace_id
    )
    result = await db.execute(stmt)
    audit = result.scalar_one_or_none()

    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit record not found in specified workspace",
        )

    provider = get_storage_provider()
    res = AuditResponse.model_validate(audit)
    if audit.screenshot_s3_key:
        res.screenshot_url = await provider.get_presigned_download_url(audit.screenshot_s3_key)
    return res
