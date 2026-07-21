from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ReportFormat(str, Enum):
    """Supported export formats for the audit report."""

    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    JSON = "json"


class ReportResult(BaseModel):
    """Output contract for the Report Generation Agent."""

    audit_id: str = Field(
        ...,
        description="The UUID of the audit this report belongs to.",
    )
    format: ReportFormat = Field(
        ...,
        description="The requested output format.",
    )
    content: Optional[str] = Field(
        None,
        description="The raw text content of the report (populated for Markdown, HTML, JSON).",
    )
    download_url: Optional[str] = Field(
        None,
        description="A signed S3 URL or relative path to download the binary file (e.g., PDF).",
    )
