from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field
from vision.component_schemas import ComponentBoundingBox


class ContrastAnalysisResult(BaseModel):
    """Calculated WCAG 2.2 color contrast analysis metrics."""

    foreground_hex: str = Field(..., description="Foreground text color hex code.")
    background_hex: str = Field(..., description="Background color hex code.")
    contrast_ratio: float = Field(
        ..., ge=1.0, le=21.0, description="Calculated contrast ratio (1.0 to 21.0)."
    )
    passes_aa: bool = Field(
        ..., description="True if meets WCAG 2.2 AA (4.5:1 normal, 3:1 large text)."
    )
    passes_aaa: bool = Field(
        ..., description="True if meets WCAG 2.2 AAA (7:1 normal, 4.5:1 large text)."
    )


class AccessibilityIssue(BaseModel):
    """Automated WCAG 2.2 accessibility issue finding for a detected UI component."""

    issue_id: str = Field(
        ...,
        json_schema_extra={"example": "a11y_001"},
        description="Unique identifier for the accessibility finding.",
    )
    component_ref_id: Optional[str] = Field(
        None,
        json_schema_extra={"example": "comp_001"},
        description="Authoritative component reference ID from Component Detection Agent inventory.",
    )
    wcag_guideline: str = Field(
        ...,
        description="Relevant WCAG 2.2 Success Criterion (e.g., '1.4.3 Contrast (Minimum)', '2.5.8 Target Size').",
    )
    category: str = Field(
        default="ACCESSIBILITY",
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
        ..., description="Explanation of user impact and accessibility barrier."
    )
    recommendation: str = Field(
        ..., description="Actionable fix recommendation to achieve compliance."
    )
    automated_assessment: bool = Field(
        default=True,
        description="Flag indicating this is an automated assessment requiring human verification for compliance certification.",
    )
    bounding_box: Optional[ComponentBoundingBox] = Field(
        None, description="Spatial bounding box coordinates of defect."
    )


class AccessibilityResult(BaseModel):
    """Structured output contract for Accessibility Agent (Agent 4)."""

    audit_id: Optional[str] = Field(None, description="Associated Audit UUID.")
    accessibility_score: int = Field(
        ..., ge=0, le=100, description="Overall accessibility compliance score (0-100)."
    )
    total_issues: int = Field(
        ..., ge=0, description="Total count of accessibility issues reported."
    )
    issues_by_severity: Dict[str, int] = Field(
        default_factory=dict, description="Count of issues grouped by severity rating."
    )
    issues: List[AccessibilityIssue] = Field(
        default_factory=list,
        description="List of detected accessibility issue findings.",
    )
    disclaimer: str = Field(
        default="Automated WCAG assessment. Manual verification recommended for legal compliance.",
        description="Scope boundary disclaimer.",
    )

    model_config = ConfigDict(from_attributes=True)
