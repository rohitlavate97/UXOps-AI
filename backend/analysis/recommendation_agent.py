import os
from typing import Dict, List

from analysis.recommendation_schemas import (EnhancedRecommendation,
                                             RecommendationResult)
from database.models import Issue


class RecommendationAgent:
    """Agent 8 in pipeline: Enhances raw issues into prioritized, actionable recommendations."""

    def __init__(self, prompt_version: str = "v1"):
        self.prompt_version = prompt_version
        self.prompt_text = self._load_prompt(prompt_version)

    def _load_prompt(self, version: str) -> str:
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "prompts",
            f"recommendation_agent_{version}.txt",
        )
        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        return "Aggregate issues into prioritized recommendations."

    async def generate_recommendations(
        self,
        audit_id: str,
        issues: List[Issue],
    ) -> RecommendationResult:
        """Processes raw database issues and returns enhanced recommendations.

        Args:
            audit_id: Audit UUID string.
            issues: List of raw Issue models from upstream agents.

        Returns:
            RecommendationResult schema object.
        """
        enhanced_recs: List[EnhancedRecommendation] = []
        priority_counts: Dict[str, int] = {}

        # Mock deterministic enhancement
        for issue in issues:
            priority = self._map_severity_to_priority(issue.severity)

            # Formulate an estimated improvement based on category and priority
            improvement = self._estimate_improvement(issue.category, priority)

            rec = EnhancedRecommendation(
                issue_id=issue.id,
                component_ref_id=issue.component_ref_id,
                category=issue.category,
                problem_summary=issue.title,
                reason=issue.impact,
                severity=issue.severity,
                impact=issue.impact,
                actionable_recommendation=issue.recommendation,
                priority=priority,
                estimated_improvement=improvement,
            )
            enhanced_recs.append(rec)
            priority_counts[priority] = priority_counts.get(priority, 0) + 1

        # Sort recommendations by priority (P0 -> P4)
        priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "P4": 4}
        enhanced_recs.sort(key=lambda x: priority_order.get(x.priority, 5))

        return RecommendationResult(
            audit_id=audit_id,
            total_recommendations=len(enhanced_recs),
            priority_breakdown=priority_counts,
            recommendations=enhanced_recs,
        )

    def _map_severity_to_priority(self, severity: str) -> str:
        """Maps standard severity strings to PM-style priority buckets."""
        mapping = {
            "CRITICAL": "P0",
            "HIGH": "P1",
            "MEDIUM": "P2",
            "LOW": "P3",
            "INFO": "P4",
        }
        return mapping.get(severity.upper(), "P4")

    def _estimate_improvement(self, category: str, priority: str) -> str:
        """Generates a qualitative estimate of improvement."""
        if priority == "P0":
            return "Unblocks critical user flow and ensures strict compliance."
        elif priority == "P1":
            return "Significantly improves usability and builds user trust."
        elif priority == "P2":
            return "Enhances visual consistency and reduces minor cognitive friction."
        elif priority == "P3":
            return "Provides a slight polish to the interface."
        else:
            return "General backlog hygiene."
