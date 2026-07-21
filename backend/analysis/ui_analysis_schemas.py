from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field
from vision.component_schemas import ComponentBoundingBox


class UIMetricResult(BaseModel):
    """Calculated UI metric result for a specific design principle."""

    principle: str = Field(
        ...,
        description="The UI principle being measured (e.g., Alignment, Spacing, Typography).",
    )
    score: float = Field(
        ..., ge=0.0, le=100.0, description="Score for this metric (0-100)."
    )
    observations: List[str] = Field(
        default_factory=list,
        description="General observations regarding this principle.",
    )


class UIAnalysisIssue(BaseModel):
    """Automated UI design finding for a detected component."""

    issue_id: str = Field(
        ...,
        json_schema_extra={"example": "ui_001"},
        description="Unique identifier for the UI finding.",
    )
    component_ref_id: Optional[str] = Field(
        None,
        json_schema_extra={"example": "comp_001"},
        description="Authoritative component reference ID from Component Detection Agent inventory.",
    )
    design_principle: str = Field(
        ...,
        description="Relevant UI design principle (e.g., 'Alignment', 'Spacing', 'Typography', 'Consistency').",
    )
    category: str = Field(
        default="UI",
        description="Issue category classification.",
    )
    severity: str = Field(
        ...,
        description="Severity level: CRITICAL, HIGH, MEDIUM, LOW, or INFO.",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Detection confidence score between 0.0 and 1.0.",
    )
    title: str = Field(..., description="Short summary title of finding.")
    impact: str = Field(
        ..., description="Explanation of user impact and visual design degradation."
    )
    recommendation: str = Field(
        ..., description="Actionable fix recommendation to improve design quality."
    )
    automated_assessment: bool = Field(
        default=True,
        description="Flag indicating this is an automated heuristic assessment.",
    )
    bounding_box: Optional[ComponentBoundingBox] = Field(
        None, description="Spatial bounding box coordinates of defect."
    )


class UIAnalysisResult(BaseModel):
    """Structured output contract for UI Analysis Agent (Agent 5)."""

    audit_id: Optional[str] = Field(None, description="Associated Audit UUID.")
    ui_score: int = Field(
        ..., ge=0, le=100, description="Overall UI quality score (0-100)."
    )
    metrics: List[UIMetricResult] = Field(
        default_factory=list,
        description="Detailed metrics broken down by design principle.",
    )
    total_issues: int = Field(
        ..., ge=0, description="Total count of UI issues reported."
    )
    issues_by_severity: Dict[str, int] = Field(
        default_factory=dict, description="Count of issues grouped by severity rating."
    )
    issues: List[UIAnalysisIssue] = Field(
        default_factory=list,
        description="List of detected UI issue findings.",
    )

    model_config = ConfigDict(from_attributes=True)
