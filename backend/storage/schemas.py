from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PresignedUrlRequest(BaseModel):
    title: str = Field(..., max_length=255, example="Homepage Q3 Audit")
    filename: str = Field(..., max_length=255, example="homepage.png")
    content_type: str = Field(..., max_length=100, example="image/png")


class PresignedUrlResponse(BaseModel):
    audit_id: UUID
    upload_url: str
    s3_key: str
    expires_in: int = 3600


class AuditResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    created_by_id: Optional[UUID] = None
    title: str
    target_type: str
    target_url: Optional[str] = None
    screenshot_s3_key: Optional[str] = None
    screenshot_url: Optional[str] = None
    annotated_s3_key: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    overall_score: Optional[int] = None
    ui_score: Optional[int] = None
    ux_score: Optional[int] = None
    accessibility_score: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
