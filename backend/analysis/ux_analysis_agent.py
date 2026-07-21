import os
from typing import Dict, List, Optional

from analysis.ux_analysis_schemas import (UXAnalysisIssue, UXAnalysisResult,
                                          UXMetricResult)
from vision.component_schemas import ComponentInventoryResult


class UXAnalysisAgent:
    """Agent 6 in pipeline: Evaluates UX heuristics (discoverability, feedback, cognitive load, etc.)."""

    def __init__(self, prompt_version: str = "v1"):
        self.prompt_version = prompt_version
        self.prompt_text = self._load_prompt(prompt_version)

    def _load_prompt(self, version: str) -> str:
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "prompts",
            f"ux_analysis_agent_{version}.txt",
        )
        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        return "Analyze UI components against UX heuristics."

    async def evaluate_ux(
        self,
        file_bytes: bytes,
        audit_id: Optional[str] = None,
        component_inventory: Optional[ComponentInventoryResult] = None,
    ) -> UXAnalysisResult:
        """Runs UX analysis on screenshot and component inventory.

        Args:
            file_bytes: Raw binary screenshot payload.
            audit_id: Optional Audit UUID string.
            component_inventory: ComponentInventoryResult from upstream Agent 3.

        Returns:
            UXAnalysisResult schema object.
        """
        if not file_bytes:
            return UXAnalysisResult(
                audit_id=audit_id,
                ux_score=100,
                metrics=[],
                total_issues=0,
                issues_by_severity={},
                issues=[],
            )

        issues: List[UXAnalysisIssue] = []
        severity_counts: Dict[str, int] = {}

        # Mock deterministic evaluation for UX heuristics based on component inventory
        if component_inventory and component_inventory.components:
            # Check for Cognitive Load: Too many components in a small area
            if len(component_inventory.components) > 15:
                issues.append(
                    UXAnalysisIssue(
                        issue_id=f"ux_{len(issues) + 1:03d}",
                        component_ref_id=None,
                        ux_heuristic="Cognitive Load",
                        category="UX",
                        severity="MEDIUM",
                        confidence=0.85,
                        title="High Cognitive Load",
                        impact="There are too many interactive components or elements visible at once, which may overwhelm the user.",
                        recommendation="Consider grouping related items, hiding secondary actions behind a menu, or using progressive disclosure.",
                        automated_assessment=True,
                        bounding_box=None,
                    )
                )

            # Check for Discoverability: Input without an associated label (simplified mock)
            for comp in component_inventory.components:
                if comp.component_type == "input" and not comp.label:
                    issues.append(
                        UXAnalysisIssue(
                            issue_id=f"ux_{len(issues) + 1:03d}",
                            component_ref_id=comp.component_ref_id,
                            ux_heuristic="Discoverability",
                            category="UX",
                            severity="HIGH",
                            confidence=0.90,
                            title="Input Missing Label",
                            impact="Input field lacks a visible label, forcing users to rely on placeholders that disappear upon focus, reducing discoverability.",
                            recommendation="Add a persistent visible label above or beside the input field.",
                            automated_assessment=True,
                            bounding_box=comp.bounding_box,
                        )
                    )

        # Baseline fallback issues if none found in raw payload
        if not issues:
            issues = [
                UXAnalysisIssue(
                    issue_id="ux_001",
                    component_ref_id=(
                        component_inventory.components[0].component_ref_id
                        if component_inventory and component_inventory.components
                        else "comp_001"
                    ),
                    ux_heuristic="Feedback",
                    category="UX",
                    severity="LOW",
                    confidence=0.75,
                    title="Missing Interactive State Feedback",
                    impact="Interactive element may lack clear hover, focus, or active states.",
                    recommendation="Ensure all interactive elements have visible state changes.",
                    automated_assessment=True,
                    bounding_box=(
                        component_inventory.components[0].bounding_box
                        if component_inventory and component_inventory.components
                        else None
                    ),
                )
            ]

        # Calculate severity counts and score
        for issue in issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1

        score = self._compute_ux_score(issues)

        metrics = [
            UXMetricResult(
                heuristic="Discoverability",
                score=score,
                observations=["Primary actions are mostly visible."],
            ),
            UXMetricResult(
                heuristic="Cognitive Load",
                score=score,
                observations=["Information density is generally acceptable."],
            ),
        ]

        return UXAnalysisResult(
            audit_id=audit_id,
            ux_score=score,
            metrics=metrics,
            total_issues=len(issues),
            issues_by_severity=severity_counts,
            issues=issues,
        )

    def _compute_ux_score(self, issues: List[UXAnalysisIssue]) -> int:
        """Computes a 0-100 UX score weighted by issue severities."""
        penalty = 0
        for issue in issues:
            if issue.severity == "CRITICAL":
                penalty += 20
            elif issue.severity == "HIGH":
                penalty += 10
            elif issue.severity == "MEDIUM":
                penalty += 5
            elif issue.severity == "LOW":
                penalty += 2
        return max(100 - penalty, 0)
