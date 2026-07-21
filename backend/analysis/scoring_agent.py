from typing import Optional

from analysis.scoring_schemas import (ScoreBreakdown, ScoreWeighting,
                                      ScoringResult)


class ScoringAgent:
    """Agent 9 in pipeline: Calculates the final deterministic score for the audit."""

    def __init__(self, weights: Optional[ScoreWeighting] = None):
        self.weights = weights or ScoreWeighting()

    def calculate_score(
        self,
        audit_id: str,
        ui_score: Optional[int] = None,
        ux_score: Optional[int] = None,
        accessibility_score: Optional[int] = None,
        consistency_score: Optional[int] = None,
    ) -> ScoringResult:
        """Deterministically aggregates sub-scores into an overall score."""

        # Determine available scores
        available_scores = {
            "ui": (ui_score, self.weights.ui_weight),
            "ux": (ux_score, self.weights.ux_weight),
            "a11y": (accessibility_score, self.weights.accessibility_weight),
            "consistency": (consistency_score, self.weights.consistency_weight),
        }

        # Calculate base score and total available weight
        raw_score = 0.0
        total_weight = 0.0

        for key, (score, weight) in available_scores.items():
            if score is not None:
                raw_score += score * weight
                total_weight += weight

        # Normalize score if some weights were skipped
        if total_weight > 0:
            final_score = int(round(raw_score / total_weight))
        else:
            final_score = 0

        breakdown = ScoreBreakdown(
            ui_score=ui_score,
            ux_score=ux_score,
            accessibility_score=accessibility_score,
            consistency_score=consistency_score,
        )

        return ScoringResult(
            audit_id=audit_id,
            overall_score=final_score,
            breakdown=breakdown,
            weights=self.weights,
        )
