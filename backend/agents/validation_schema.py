from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class ScreenshotValidationResult(BaseModel):
    """Structured output contract for Screenshot Validation Agent."""

    is_valid_ui_screenshot: bool = Field(
        ...,
        description="True if image is a valid web or mobile application interface screenshot.",
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence rating of validation assessment between 0.0 and 1.0.",
    )
    detected_device_type: str = Field(
        ...,
        description="Device classification: 'desktop_web', 'mobile_app', 'tablet', or 'unknown'.",
    )
    is_blurry: bool = Field(
        ...,
        description="True if image blurriness impedes OCR or component detection.",
    )
    blur_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Clarity rating score between 0.0 (extremely blurry) and 1.0 (crystal clear).",
    )
    orientation_correct: bool = Field(
        ...,
        description="True if screenshot is oriented upright (0 degrees rotation).",
    )
    rejection_reason: Optional[str] = Field(
        None,
        description="Detailed explanation if image is rejected from pipeline analysis.",
    )
    extracted_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Extracted metadata including width, height, aspect ratio, and mime type.",
    )

    model_config = ConfigDict(from_attributes=True)
