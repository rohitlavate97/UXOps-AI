from typing import List, Optional

from pydantic import BaseModel, Field

from vision.component_schemas import ComponentBoundingBox


class DesignSystemIssue(BaseModel):
    """Represents a single design system compliance violation (Material, HIG, Custom Guidelines)."""

    component_ref_id: Optional[str] = Field(
        None,
        description="Reference ID of the component in the Agent 3 inventory, if applicable.",
        json_schema_extra={"example": "comp_001"},
    )
    category: str = Field(
        "DESIGN_SYSTEM",
        description="The category of the issue. Always 'DESIGN_SYSTEM'.",
    )
    severity: str = Field(
        ...,
        description="Severity of the issue: CRITICAL, HIGH, MEDIUM, LOW, INFO.",
        json_schema_extra={"example": "MEDIUM"},
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score for this finding (0.0 to 1.0).",
        json_schema_extra={"example": 0.9},
    )
    title: str = Field(
        ...,
        description="Short title summarizing the design system violation.",
        json_schema_extra={"example": "Material Design Drop Shadow Violation"},
    )
    impact: str = Field(
        ...,
        description="Explanation of why this violates design system guidelines.",
        json_schema_extra={
            "example": "The elevation drop shadow on this card exceeds Material Design specifications for 1dp."
        },
    )
    recommendation: str = Field(
        ...,
        description="Actionable recommendation to fix the issue to align with the system.",
        json_schema_extra={"example": "Reduce the box-shadow blur radius to 2px."},
    )
    automated_assessment: bool = Field(
        True, description="Whether this issue was detected by the automated AI agent."
    )
    bounding_box: Optional[ComponentBoundingBox] = Field(
        None, description="The bounding box of the affected component."
    )
    guideline_reference: Optional[str] = Field(
        None,
        description="Optional reference to the specific design system rule (e.g. 'Material M3 - Card', or 'Company Guideline - Button Colors').",
        json_schema_extra={"example": "Material M3 - Elevation"},
    )


class DesignMetricResult(BaseModel):
    """Aggregate metrics for design system analysis."""

    total_violations: int = Field(
        ...,
        description="Total number of design system violations detected.",
        json_schema_extra={"example": 3},
    )
    severity_breakdown: dict[str, int] = Field(
        ...,
        description="Count of issues by severity.",
        json_schema_extra={
            "example": {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 0}
        },
    )


class DesignSystemResult(BaseModel):
    """Complete output contract for the Design System Agent (Agent 7)."""

    audit_id: str = Field(
        ...,
        description="The UUID of the audit this result belongs to.",
        json_schema_extra={"example": "123e4567-e89b-12d3-a456-426614174000"},
    )
    total_issues: int = Field(
        ...,
        description="Total number of design system issues found.",
        json_schema_extra={"example": 3},
    )
    design_system_score: int = Field(
        ...,
        description="Overall design system compliance score (0-100).",
        json_schema_extra={"example": 88},
    )
    metrics: DesignMetricResult = Field(
        ..., description="Aggregate metrics for the design system analysis."
    )
    issues: List[DesignSystemIssue] = Field(
        default_factory=list, description="List of specific design system violations."
    )
