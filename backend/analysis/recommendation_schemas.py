import uuid
from typing import List, Optional

from pydantic import BaseModel, Field


class EnhancedRecommendation(BaseModel):
    """Represents a prioritized, enriched recommendation that maps to an upstream issue."""

    issue_id: uuid.UUID = Field(
        ...,
        description="The database ID of the raw upstream issue this recommendation resolves.",
    )
    component_ref_id: Optional[str] = Field(
        None,
        description="Reference ID of the component in the Agent 3 inventory, if applicable.",
        json_schema_extra={"example": "comp_001"},
    )
    category: str = Field(
        ...,
        description="The category of the upstream issue (e.g., UI, UX, ACCESSIBILITY).",
    )
    problem_summary: str = Field(
        ...,
        description="Clear, concise summary of the problem.",
    )
    reason: str = Field(
        ...,
        description="Explanation of why this problem matters to the user or system.",
    )
    severity: str = Field(
        ...,
        description="Original severity of the issue: CRITICAL, HIGH, MEDIUM, LOW, INFO.",
    )
    impact: str = Field(
        ...,
        description="The negative effect on user experience or accessibility.",
    )
    actionable_recommendation: str = Field(
        ...,
        description="Specific, implementable steps to fix the issue.",
    )
    priority: str = Field(
        ...,
        description="Assigned priority for fixing (P0 = Immediate, P1 = High, P2 = Medium, P3 = Low, P4 = Backlog).",
        json_schema_extra={"example": "P1"},
    )
    estimated_improvement: str = Field(
        ...,
        description="Qualitative or quantitative estimate of how fixing this improves the score or user experience.",
        json_schema_extra={
            "example": "+5 to UX Score, reduces cognitive load by grouping related items."
        },
    )


class RecommendationResult(BaseModel):
    """Output contract for the Recommendation Agent (Agent 8)."""

    audit_id: str = Field(
        ...,
        description="The UUID of the audit this result belongs to.",
    )
    total_recommendations: int = Field(
        ...,
        description="Total number of prioritized recommendations generated.",
    )
    priority_breakdown: dict[str, int] = Field(
        ...,
        description="Count of recommendations by priority (e.g., {'P0': 1, 'P1': 2}).",
    )
    recommendations: List[EnhancedRecommendation] = Field(
        default_factory=list, description="List of enhanced recommendations."
    )
