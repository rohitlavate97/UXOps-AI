import os
from typing import Dict, List, Optional

from analysis.design_system_schemas import (DesignMetricResult,
                                            DesignSystemIssue,
                                            DesignSystemResult)
from vision.component_schemas import ComponentInventoryResult


class DesignSystemAgent:
    """Agent 7 in pipeline: Evaluates compliance with design systems and company guidelines."""

    def __init__(self, prompt_version: str = "v1"):
        self.prompt_version = prompt_version
        self.prompt_text = self._load_prompt(prompt_version)

    def _load_prompt(self, version: str) -> str:
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "prompts",
            f"design_system_agent_{version}.txt",
        )
        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        return (
            "Validate components against design system heuristics and RAG guidelines."
        )

    async def evaluate_design_system(
        self,
        file_bytes: bytes,
        audit_id: str,
        component_inventory: Optional[ComponentInventoryResult] = None,
        design_guidelines_text: Optional[str] = None,
    ) -> DesignSystemResult:
        """Runs Design System and RAG analysis on screenshot and component inventory.

        Args:
            file_bytes: Raw binary screenshot payload.
            audit_id: Audit UUID string.
            component_inventory: ComponentInventoryResult from upstream Agent 3.
            design_guidelines_text: Optional text of company guidelines retrieved via RAG.

        Returns:
            DesignSystemResult schema object.
        """
        if not file_bytes:
            return DesignSystemResult(
                audit_id=audit_id,
                total_issues=0,
                design_system_score=100,
                metrics=DesignMetricResult(
                    total_violations=0,
                    severity_breakdown={},
                ),
                issues=[],
            )

        issues: List[DesignSystemIssue] = []
        severity_counts: Dict[str, int] = {}

        # Mock deterministic evaluation for design system violations
        if component_inventory and component_inventory.components:
            for comp in component_inventory.components:
                # Mock RAG evaluation: if there's a guideline and a button, check standard rules
                if comp.component_type.lower() == "button":
                    if (
                        design_guidelines_text
                        and "border radius" in design_guidelines_text.lower()
                    ):
                        # Suppose the mock guideline says "8px border radius" and the button is 4px
                        issues.append(
                            DesignSystemIssue(
                                component_ref_id=comp.component_ref_id,
                                category="DESIGN_SYSTEM",
                                severity="HIGH",
                                confidence=0.88,
                                title="Border Radius Deviation",
                                impact="Button border radius does not match the company standard of 8px.",
                                recommendation="Change border-radius to 8px.",
                                automated_assessment=True,
                                bounding_box=comp.bounding_box,
                                guideline_reference="Company Guideline - Button Styles",
                            )
                        )
                    else:
                        # Standard Material constraint check for touch target height
                        if comp.bounding_box.height < 48:
                            issues.append(
                                DesignSystemIssue(
                                    component_ref_id=comp.component_ref_id,
                                    category="DESIGN_SYSTEM",
                                    severity="MEDIUM",
                                    confidence=0.92,
                                    title="Insufficient Touch Target Height",
                                    impact="Button height is less than the 48dp minimum required by Material Design/HIG.",
                                    recommendation="Increase the button height to at least 48px.",
                                    automated_assessment=True,
                                    bounding_box=comp.bounding_box,
                                    guideline_reference="Material Design 3 - Touch Targets",
                                )
                            )

        # Baseline fallback issues if none found in raw payload
        if not issues:
            issues = [
                DesignSystemIssue(
                    component_ref_id=(
                        component_inventory.components[0].component_ref_id
                        if component_inventory and component_inventory.components
                        else "comp_001"
                    ),
                    category="DESIGN_SYSTEM",
                    severity="LOW",
                    confidence=0.85,
                    title="Non-standard Color Variable",
                    impact="Color #333333 is used directly instead of a design token (e.g., var(--text-primary)).",
                    recommendation="Map the hex value to the appropriate design system token.",
                    automated_assessment=True,
                    bounding_box=(
                        component_inventory.components[0].bounding_box
                        if component_inventory and component_inventory.components
                        else None
                    ),
                    guideline_reference="Design System Tokens",
                )
            ]

        # Calculate severity counts and score
        for issue in issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1

        score = self._compute_design_score(issues)

        metrics = DesignMetricResult(
            total_violations=len(issues),
            severity_breakdown=severity_counts,
        )

        return DesignSystemResult(
            audit_id=audit_id,
            total_issues=len(issues),
            design_system_score=score,
            metrics=metrics,
            issues=issues,
        )

    def _compute_design_score(self, issues: List[DesignSystemIssue]) -> int:
        """Computes a 0-100 score weighted by issue severities."""
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
