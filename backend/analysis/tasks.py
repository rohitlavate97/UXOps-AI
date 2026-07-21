import asyncio
import logging
from uuid import UUID

from sqlalchemy import select

from agents.screenshot_validation_agent import ScreenshotValidationAgent
from analysis.accessibility_agent import AccessibilityAgent
from analysis.design_system_agent import DesignSystemAgent
from analysis.recommendation_agent import RecommendationAgent
from analysis.scoring_agent import ScoringAgent
from analysis.ui_analysis_agent import UIAnalysisAgent
from analysis.ux_analysis_agent import UXAnalysisAgent
from common.celery_app import celery_app
from database.models import Audit, Issue
from database.session import AsyncSessionLocal
from ocr.agent import OcrAgent
from reports.report_agent import ReportGenerationAgent
from reports.report_schemas import ReportFormat
from vision.component_agent import ComponentDetectionAgent

logger = logging.getLogger(__name__)


async def run_pipeline_async(audit_id: UUID) -> None:
    async with AsyncSessionLocal() as db:
        # Fetch audit
        stmt = select(Audit).where(Audit.id == audit_id)
        result = await db.execute(stmt)
        audit = result.scalar_one_or_none()

        if not audit:
            logger.error(f"Audit {audit_id} not found.")
            return

        try:
            # 1. Validation
            audit.status = "VALIDATING"
            await db.commit()
            validator = ScreenshotValidationAgent()
            validation_result = await validator.validate_screenshot(
                audit.screenshot_s3_key
            )
            if not validation_result.is_valid:
                audit.status = "FAILED"
                audit.error_message = f"Validation failed: {validation_result.reason}"
                await db.commit()
                return

            # 2. OCR
            audit.status = "OCR_RUNNING"
            await db.commit()
            ocr_agent = OcrAgent()
            await ocr_agent.extract_text(
                audit.screenshot_s3_key, audit.id, audit.workspace_id, db
            )

            # 3. Component Detection
            audit.status = "DETECTING_COMPONENTS"
            await db.commit()
            component_agent = ComponentDetectionAgent()
            await component_agent.detect_components(
                audit.screenshot_s3_key, audit.id, audit.workspace_id, db
            )

            # 4. Accessibility
            audit.status = "ANALYZING_ACCESSIBILITY"
            await db.commit()
            a11y_agent = AccessibilityAgent()
            await a11y_agent.evaluate_accessibility(audit.id, audit.workspace_id, db)

            # 5. UI Analysis
            audit.status = "ANALYZING_UI"
            await db.commit()
            ui_agent = UIAnalysisAgent()
            await ui_agent.evaluate_ui(audit.id, audit.workspace_id, db)

            # 6. UX Analysis
            audit.status = "ANALYZING_UX"
            await db.commit()
            ux_agent = UXAnalysisAgent()
            await ux_agent.evaluate_ux(audit.id, audit.workspace_id, db)

            # 7. Design System
            audit.status = "CHECKING_DESIGN_SYSTEM"
            await db.commit()
            ds_agent = DesignSystemAgent()
            await ds_agent.evaluate_design_system(audit.id, audit.workspace_id, db)

            # 8. Recommendations
            audit.status = "GENERATING_RECOMMENDATIONS"
            await db.commit()
            rec_agent = RecommendationAgent()
            await rec_agent.process_audit(audit.id, db)

            # 9. Scoring
            audit.status = "SCORING"
            await db.commit()
            scoring_agent = ScoringAgent()
            scoring_result = await scoring_agent.calculate_scores(audit.id, db)

            audit.overall_score = scoring_result.overall_score
            audit.ui_score = scoring_result.ui_score
            audit.ux_score = scoring_result.ux_score
            audit.accessibility_score = scoring_result.accessibility_score
            audit.consistency_score = scoring_result.consistency_score
            audit.readability_score = scoring_result.readability_score

            # 10. Reports
            audit.status = "GENERATING_REPORTS"
            await db.commit()

            # Fetch issues for report
            issue_stmt = (
                select(Issue)
                .where(Issue.audit_id == audit.id)
                .order_by(Issue.created_at.desc())
            )
            issue_result = await db.execute(issue_stmt)
            issues = list(issue_result.scalars().all())

            report_agent = ReportGenerationAgent()
            # Generate markdown report as default export cache
            report_agent.generate_report(audit, issues, ReportFormat.MARKDOWN)

            # Finish
            audit.status = "COMPLETED"
            await db.commit()

        except Exception as e:
            logger.exception(f"Pipeline failed for audit {audit_id}")
            audit.status = "FAILED"
            audit.error_message = str(e)
            await db.commit()


@celery_app.task(name="run_full_audit_pipeline")
def run_full_audit_pipeline(audit_id_str: str):
    """Celery task to run the full UXOps AI pipeline asynchronously."""
    audit_id = UUID(audit_id_str)
    asyncio.run(run_pipeline_async(audit_id))
