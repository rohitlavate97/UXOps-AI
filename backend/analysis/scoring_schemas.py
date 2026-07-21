from typing import Optional

from pydantic import BaseModel, Field


class ScoreBreakdown(BaseModel):
    """Details the sub-scores used in the final calculation."""

    ui_score: Optional[int] = Field(None, description="UI Quality Score (0-100)")
    ux_score: Optional[int] = Field(None, description="UX Heuristics Score (0-100)")
    accessibility_score: Optional[int] = Field(
        None, description="Accessibility Score (0-100)"
    )
    consistency_score: Optional[int] = Field(
        None, description="Design System Consistency Score (0-100)"
    )


class ScoreWeighting(BaseModel):
    """Details the weights applied to each sub-score."""

    ui_weight: float = Field(0.40, description="Weight of UI score (40%)")
    ux_weight: float = Field(0.30, description="Weight of UX score (30%)")
    accessibility_weight: float = Field(0.20, description="Weight of A11y score (20%)")
    consistency_weight: float = Field(
        0.10, description="Weight of Design System score (10%)"
    )


class ScoringResult(BaseModel):
    """Output contract for the Scoring Agent (Agent 9)."""

    audit_id: str = Field(
        ...,
        description="The UUID of the audit this result belongs to.",
    )
    overall_score: int = Field(
        ...,
        description="Final aggregated score (0-100).",
    )
    breakdown: ScoreBreakdown = Field(
        ...,
        description="The raw sub-scores used for calculation.",
    )
    weights: ScoreWeighting = Field(
        default_factory=ScoreWeighting,
        description="The weights used in the deterministic calculation.",
    )
