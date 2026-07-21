from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class OcrBoundingBox(BaseModel):
    """Spatial bounding box coordinates for extracted text elements."""

    x: int = Field(..., ge=0, description="X coordinate of top-left corner in pixels.")
    y: int = Field(..., ge=0, description="Y coordinate of top-left corner in pixels.")
    width: int = Field(..., ge=0, description="Width of bounding box in pixels.")
    height: int = Field(..., ge=0, description="Height of bounding box in pixels.")


class OcrTextElement(BaseModel):
    """Ground truth text element extracted by OCR Agent."""

    element_id: str = Field(
        ...,
        example="txt_001",
        description="Unique identifier for downstream agent referential tracking.",
    )
    text: str = Field(..., description="Extracted text string.")
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="OCR extraction confidence rating between 0.0 and 1.0.",
    )
    element_type: str = Field(
        ...,
        description="Classification: 'heading', 'button_label', 'input_label', 'placeholder', 'body_text', 'error_message', 'nav_link', or 'unknown'.",
    )
    bounding_box: OcrBoundingBox = Field(
        ..., description="Spatial bounding box coordinates."
    )


class OcrResult(BaseModel):
    """Structured output contract for OCR Agent (Agent 2)."""

    audit_id: Optional[str] = Field(None, description="Associated Audit UUID.")
    total_text_elements: int = Field(
        ..., ge=0, description="Total count of text elements extracted."
    )
    language_detected: str = Field(
        default="en", description="Primary language detected in screenshot."
    )
    elements: List[OcrTextElement] = Field(
        default_factory=list, description="Ground truth text element inventory."
    )
    extracted_text_block: str = Field(
        default="", description="Full concatenated text string for indexing."
    )

    model_config = ConfigDict(from_attributes=True)
