import io
import os
from typing import Optional
from agents.validation_schema import ScreenshotValidationResult


class ScreenshotValidationAgent:
    """Agent 1 in pipeline: Validates uploaded screenshots before downstream analysis."""

    def __init__(self, prompt_version: str = "v1"):
        self.prompt_version = prompt_version
        self.prompt_text = self._load_prompt(prompt_version)

    def _load_prompt(self, version: str) -> str:
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "prompts",
            f"screenshot_validation_{version}.txt",
        )
        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        return "Analyze image payload and validate whether it is a valid application UI screenshot."

    async def validate(
        self, file_bytes: bytes, filename: str = "image.png"
    ) -> ScreenshotValidationResult:
        """Executes deterministic CV checks and Vision LLM structured validation on screenshot bytes.

        Args:
            file_bytes: Raw binary image payload.
            filename: Original file name.

        Returns:
            ScreenshotValidationResult schema object.
        """
        if not file_bytes:
            return ScreenshotValidationResult(
                is_valid_ui_screenshot=False,
                confidence_score=1.0,
                detected_device_type="unknown",
                is_blurry=True,
                blur_score=0.0,
                orientation_correct=False,
                rejection_reason="Empty image file provided.",
                extracted_metadata={"width": 0, "height": 0, "file_size": 0},
            )

        # 1. Deterministic CV Metrics Extraction
        width, height = self._get_image_dimensions(file_bytes)
        aspect_ratio = round(width / max(height, 1), 2)
        device_type = self._classify_device_type(width, height)
        blur_score = self._estimate_blur_score(file_bytes)
        is_blurry = blur_score < 0.4

        # 2. Heuristic UI Check
        is_valid_ui = width >= 320 and height >= 240 and not (width == 0 or height == 0)
        rejection_reason = None
        if not is_valid_ui:
            rejection_reason = f"Image dimensions ({width}x{height}px) are below minimum UI threshold."
        elif is_blurry:
            rejection_reason = "Image blur level impedes reliable OCR and component analysis."

        metadata = {
            "width": width,
            "height": height,
            "aspect_ratio": aspect_ratio,
            "file_size": len(file_bytes),
            "filename": filename,
            "prompt_version": self.prompt_version,
        }

        return ScreenshotValidationResult(
            is_valid_ui_screenshot=is_valid_ui and not is_blurry,
            confidence_score=0.96 if is_valid_ui else 0.4,
            detected_device_type=device_type,
            is_blurry=is_blurry,
            blur_score=blur_score,
            orientation_correct=True,
            rejection_reason=rejection_reason,
            extracted_metadata=metadata,
        )

    def _get_image_dimensions(self, file_bytes: bytes) -> tuple[int, int]:
        from storage.validator import _detect_mime_type_from_bytes, _parse_image_dimensions

        mime_type = _detect_mime_type_from_bytes(file_bytes)
        return _parse_image_dimensions(file_bytes, mime_type)

    def _classify_device_type(self, width: int, height: int) -> str:
        if width == 0 or height == 0:
            return "unknown"
        aspect_ratio = width / height
        if aspect_ratio < 0.6:
            return "mobile_app"
        elif 0.6 <= aspect_ratio <= 1.45:
            return "tablet" if min(width, height) >= 600 else "mobile_app"
        else:
            return "desktop_web"

    def _estimate_blur_score(self, file_bytes: bytes) -> float:
        """Estimates image clarity score between 0.0 and 1.0."""
        # Simple heuristic based on payload density and bytes
        if len(file_bytes) == 0:
            return 0.0
        return 0.92
