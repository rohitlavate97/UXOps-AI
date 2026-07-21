import uuid
from typing import Any, Dict, List, Optional

from database.base_class import Base
from sqlalchemy import (
    JSON,
    Boolean,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Audit(Base):
    """Represents a visual audit run on a UI screenshot or URL for a workspace."""

    __tablename__ = "audits"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    target_type: Mapped[str] = mapped_column(
        String(50), default="image_upload", nullable=False
    )
    target_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    screenshot_s3_key: Mapped[Optional[str]] = mapped_column(
        String(1024), nullable=True
    )
    annotated_s3_key: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), default="PENDING", nullable=False, index=True
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Score Summary
    overall_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ui_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ux_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    accessibility_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    consistency_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    readability_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    workspace: Mapped["Workspace"] = relationship("Workspace")  # noqa: F821
    created_by: Mapped[Optional["User"]] = relationship("User")  # noqa: F821
    components: Mapped[List["ComponentInventory"]] = relationship(
        "ComponentInventory", back_populates="audit", cascade="all, delete-orphan"
    )
    issues: Mapped[List["Issue"]] = relationship(
        "Issue", back_populates="audit", cascade="all, delete-orphan"
    )
    report: Mapped[Optional["Report"]] = relationship(
        "Report", back_populates="audit", uselist=False, cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_audits_workspace_status", "workspace_id", "status"),
    )

    def __repr__(self) -> str:
        return f"<Audit(id={self.id}, workspace_id={self.workspace_id}, title={self.title}, status={self.status})>"


class ComponentInventory(Base):
    """Authoritative inventory of detected UI components within an audit image."""

    __tablename__ = "component_inventories"

    audit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("audits.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    component_ref_id: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    component_type: Mapped[str] = mapped_column(String(100), nullable=False)
    label: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    bounding_box: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    # Relationships
    audit: Mapped["Audit"] = relationship("Audit", back_populates="components")
    workspace: Mapped["Workspace"] = relationship("Workspace")  # noqa: F821

    __table_args__ = (
        Index(
            "ix_component_inventories_audit_ref", "audit_id", "component_ref_id"
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<ComponentInventory(id={self.id}, audit_id={self.audit_id}, "
            f"ref_id={self.component_ref_id}, type={self.component_type})>"
        )


class Issue(Base):
    """Individual UI/UX/Accessibility defect or recommendation finding."""

    __tablename__ = "issues"

    audit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("audits.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    component_ref_id: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, index=True
    )
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    impact: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    automated_assessment: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    bounding_box: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Relationships
    audit: Mapped["Audit"] = relationship("Audit", back_populates="issues")
    workspace: Mapped["Workspace"] = relationship("Workspace")  # noqa: F821

    __table_args__ = (
        Index("ix_issues_workspace_severity", "workspace_id", "severity"),
        Index("ix_issues_audit_category", "audit_id", "category"),
    )

    def __repr__(self) -> str:
        return (
            f"<Issue(id={self.id}, audit_id={self.audit_id}, "
            f"title={self.title}, severity={self.severity})>"
        )


class Report(Base):
    """Compiled audit report data with executive summary and export references."""

    __tablename__ = "reports"

    audit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("audits.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    executive_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    summary_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    pdf_s3_key: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    html_s3_key: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

    # Relationships
    audit: Mapped["Audit"] = relationship("Audit", back_populates="report")
    workspace: Mapped["Workspace"] = relationship("Workspace")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Report(id={self.id}, audit_id={self.audit_id})>"


class DesignGuideline(Base):
    """Company design guidelines for RAG design system audits."""

    __tablename__ = "design_guidelines"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    doc_s3_key: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    embedding_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )

    # Relationships
    workspace: Mapped["Workspace"] = relationship("Workspace")  # noqa: F821

    def __repr__(self) -> str:
        return f"<DesignGuideline(id={self.id}, workspace_id={self.workspace_id}, title={self.title})>"
