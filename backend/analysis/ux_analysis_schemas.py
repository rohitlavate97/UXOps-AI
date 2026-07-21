from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from vision.component_schemas import ComponentBoundingBox


class UXMetricResult(BaseModel):
    """Calculated UX metric result for a specific heuristic."""

    heuristic: str = Field(
        ...,
        description="The UX heuristic being measured (e.g., Discoverability, Feedback).",
    )
    score: float = Field(
        ..., ge=0.0, le=100.0, description="Score for this metric (0-100)."
    )
    observations: List[str] = Field(
        default_factory=list,
        description="General observations regarding this heuristic.",
    )


class UXAnalysisIssue(BaseModel):
    """Automated UX heuristic finding for a detected component."""

    issue_id: str = Field(
        ...,
        json_schema_extra={"example": "ux_001"},
        description="Unique identifier for the UX finding.",
    )
    component_ref_id: Optional[str] = Field(
        None,
        json_schema_extra={"example": "comp_001"},
        description="Authoritative component reference ID from Component Detection Agent inventory.",
    )
    ux_heuristic: str = Field(
        ...,
        description="Relevant UX heuristic (e.g., 'Discoverability', 'Feedback', 'Cognitive Load', 'Error Prevention').",
    )
    category: str = Field(
        default="UX",
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
        ..., description="Explanation of user impact and usability degradation."
    )
    recommendation: str = Field(
        ..., description="Actionable fix recommendation to improve usability."
    )
    automated_assessment: bool = Field(
        default=True,
        description="Flag indicating this is an automated heuristic assessment.",
    )
    bounding_box: Optional[ComponentBoundingBox] = Field(
        None, description="Spatial bounding box coordinates of defect."
    )


class UXAnalysisResult(BaseModel):
    """Structured output contract for UX Analysis Agent (Agent 6)."""

    audit_id: Optional[str] = Field(None, description="Associated Audit UUID.")
    ux_score: int = Field(
        ..., ge=0, le=100, description="Overall UX usability score (0-100)."
    )
    metrics: List[UXMetricResult] = Field(
        default_factory=list, description="Detailed metrics broken down by heuristic."
    )
    total_issues: int = Field(
        ..., ge=0, description="Total count of UX issues reported."
    )
    issues_by_severity: Dict[str, int] = Field(
        default_factory=dict, description="Count of issues grouped by severity rating."
    )
    issues: List[UXAnalysisIssue] = Field(
        default_factory=list,
        description="List of detected UX issue findings.",
    )

    model_config = ConfigDict(from_attributes=True)
