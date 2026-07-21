from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ComponentBoundingBox(BaseModel):
    """Spatial bounding box coordinates for detected UI components."""

    x: int = Field(..., ge=0, description="X coordinate of top-left corner in pixels.")
    y: int = Field(..., ge=0, description="Y coordinate of top-left corner in pixels.")
    width: int = Field(..., ge=0, description="Width of bounding box in pixels.")
    height: int = Field(..., ge=0, description="Height of bounding box in pixels.")


class DetectedComponent(BaseModel):
    """Authoritative UI component entry detected in UI screenshot."""

    component_ref_id: str = Field(
        ...,
        json_schema_extra={"example": "comp_001"},
        description="Unique authoritative component reference ID for cross-agent referential integrity.",
    )
    component_type: str = Field(
        ...,
        description="Component classification: button, input, dropdown, checkbox, radio, card, table, chart, image, icon, sidebar, navbar, footer, modal, dialog, badge, avatar, link, or unknown.",
    )
    label: Optional[str] = Field(
        None, description="Visible text label or title associated with component."
    )
    bounding_box: ComponentBoundingBox = Field(
        ..., description="Spatial bounding box coordinates in pixels."
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Component detection confidence rating between 0.0 and 1.0.",
    )
    associated_text_ids: List[str] = Field(
        default_factory=list,
        description="Upstream OCR text element IDs (e.g. ['txt_001', 'txt_002']) contained inside or associated with this component.",
    )


class ComponentInventoryResult(BaseModel):
    """Structured output contract for Component Detection Agent (Agent 3)."""

    audit_id: Optional[str] = Field(None, description="Associated Audit UUID.")
    total_components: int = Field(
        ..., ge=0, description="Total count of detected UI components."
    )
    component_summary: Dict[str, int] = Field(
        default_factory=dict,
        description="Breakdown of detected component counts categorized by type.",
    )
    components: List[DetectedComponent] = Field(
        default_factory=list,
        description="Authoritative inventory list of detected UI components.",
    )

    model_config = ConfigDict(from_attributes=True)
