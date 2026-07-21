import io
import pytest
from agents.screenshot_validation_agent import ScreenshotValidationAgent
from agents.validation_schema import ScreenshotValidationResult
from tests.test_storage import get_sample_png_bytes


@pytest.mark.asyncio
async def test_screenshot_validation_agent_valid_image():
    """Test ScreenshotValidationAgent correctly validates sample PNG screenshot."""
    agent = ScreenshotValidationAgent(prompt_version="v1")
    sample_bytes = get_sample_png_bytes()

    result = await agent.validate(sample_bytes, "dashboard.png")

    assert isinstance(result, ScreenshotValidationResult)
    assert result.is_valid_ui_screenshot is True
    assert result.confidence_score >= 0.9
    assert result.detected_device_type in ("desktop_web", "mobile_app", "tablet")
    assert result.is_blurry is False
    assert result.orientation_correct is True
    assert result.rejection_reason is None
    assert "width" in result.extracted_metadata


@pytest.mark.asyncio
async def test_screenshot_validation_agent_empty_bytes():
    """Test ScreenshotValidationAgent handles empty file payload with rejection."""
    agent = ScreenshotValidationAgent(prompt_version="v1")

    result = await agent.validate(b"", "empty.png")

    assert result.is_valid_ui_screenshot is False
    assert result.rejection_reason is not None
    assert "Empty image file" in result.rejection_reason


def test_device_type_classification_heuristics():
    """Test device classification helper for mobile, tablet, and desktop layouts."""
    agent = ScreenshotValidationAgent(prompt_version="v1")

    assert agent._classify_device_type(375, 812) == "mobile_app"
    assert agent._classify_device_type(768, 1024) == "tablet"
    assert agent._classify_device_type(1920, 1080) == "desktop_web"
    assert agent._classify_device_type(0, 0) == "unknown"
