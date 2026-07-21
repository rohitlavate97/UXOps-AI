"""create_domain_audit_tables

Revision ID: a6b7c8d9e0f1
Revises: 55b40b7ed848
Create Date: 2026-07-21 12:10:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a6b7c8d9e0f1"
down_revision: Union[str, Sequence[str], None] = "55b40b7ed848"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to include audits, component_inventories, issues, reports, and design_guidelines."""
    # 1. Audits Table
    op.create_table(
        "audits",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("workspace_id", sa.UUID(), nullable=False),
        sa.Column("created_by_id", sa.UUID(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("target_type", sa.String(length=50), nullable=False, server_default="image_upload"),
        sa.Column("target_url", sa.String(length=1024), nullable=True),
        sa.Column("screenshot_s3_key", sa.String(length=1024), nullable=True),
        sa.Column("annotated_s3_key", sa.String(length=1024), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="PENDING"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("overall_score", sa.Integer(), nullable=True),
        sa.Column("ui_score", sa.Integer(), nullable=True),
        sa.Column("ux_score", sa.Integer(), nullable=True),
        sa.Column("accessibility_score", sa.Integer(), nullable=True),
        sa.Column("consistency_score", sa.Integer(), nullable=True),
        sa.Column("readability_score", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audits_id"), "audits", ["id"], unique=False)
    op.create_index(op.f("ix_audits_workspace_id"), "audits", ["workspace_id"], unique=False)
    op.create_index(op.f("ix_audits_created_by_id"), "audits", ["created_by_id"], unique=False)
    op.create_index(op.f("ix_audits_status"), "audits", ["status"], unique=False)
    op.create_index("ix_audits_workspace_status", "audits", ["workspace_id", "status"], unique=False)

    # 2. Component Inventories Table
    op.create_table(
        "component_inventories",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("audit_id", sa.UUID(), nullable=False),
        sa.Column("workspace_id", sa.UUID(), nullable=False),
        sa.Column("component_ref_id", sa.String(length=100), nullable=False),
        sa.Column("component_type", sa.String(length=100), nullable=False),
        sa.Column("label", sa.String(length=255), nullable=True),
        sa.Column("bounding_box", sa.JSON(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["audit_id"], ["audits.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_component_inventories_id"), "component_inventories", ["id"], unique=False)
    op.create_index(op.f("ix_component_inventories_audit_id"), "component_inventories", ["audit_id"], unique=False)
    op.create_index(op.f("ix_component_inventories_workspace_id"), "component_inventories", ["workspace_id"], unique=False)
    op.create_index(op.f("ix_component_inventories_component_ref_id"), "component_inventories", ["component_ref_id"], unique=False)
    op.create_index("ix_component_inventories_audit_ref", "component_inventories", ["audit_id", "component_ref_id"], unique=False)

    # 3. Issues Table
    op.create_table(
        "issues",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("audit_id", sa.UUID(), nullable=False),
        sa.Column("workspace_id", sa.UUID(), nullable=False),
        sa.Column("component_ref_id", sa.String(length=100), nullable=True),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("severity", sa.String(length=50), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("impact", sa.Text(), nullable=False),
        sa.Column("recommendation", sa.Text(), nullable=False),
        sa.Column("automated_assessment", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("bounding_box", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["audit_id"], ["audits.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_issues_id"), "issues", ["id"], unique=False)
    op.create_index(op.f("ix_issues_audit_id"), "issues", ["audit_id"], unique=False)
    op.create_index(op.f("ix_issues_workspace_id"), "issues", ["workspace_id"], unique=False)
    op.create_index(op.f("ix_issues_component_ref_id"), "issues", ["component_ref_id"], unique=False)
    op.create_index("ix_issues_workspace_severity", "issues", ["workspace_id", "severity"], unique=False)
    op.create_index("ix_issues_audit_category", "issues", ["audit_id", "category"], unique=False)

    # 4. Reports Table
    op.create_table(
        "reports",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("audit_id", sa.UUID(), nullable=False),
        sa.Column("workspace_id", sa.UUID(), nullable=False),
        sa.Column("executive_summary", sa.Text(), nullable=True),
        sa.Column("summary_json", sa.JSON(), nullable=True),
        sa.Column("pdf_s3_key", sa.String(length=1024), nullable=True),
        sa.Column("html_s3_key", sa.String(length=1024), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["audit_id"], ["audits.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("audit_id"),
    )
    op.create_index(op.f("ix_reports_id"), "reports", ["id"], unique=False)
    op.create_index(op.f("ix_reports_audit_id"), "reports", ["audit_id"], unique=True)
    op.create_index(op.f("ix_reports_workspace_id"), "reports", ["workspace_id"], unique=False)

    # 5. Design Guidelines Table
    op.create_table(
        "design_guidelines",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("workspace_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("doc_s3_key", sa.String(length=1024), nullable=True),
        sa.Column("embedding_data", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_design_guidelines_id"), "design_guidelines", ["id"], unique=False)
    op.create_index(op.f("ix_design_guidelines_workspace_id"), "design_guidelines", ["workspace_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_design_guidelines_workspace_id"), table_name="design_guidelines")
    op.drop_index(op.f("ix_design_guidelines_id"), table_name="design_guidelines")
    op.drop_table("design_guidelines")

    op.drop_index(op.f("ix_reports_workspace_id"), table_name="reports")
    op.drop_index(op.f("ix_reports_audit_id"), table_name="reports")
    op.drop_index(op.f("ix_reports_id"), table_name="reports")
    op.drop_table("reports")

    op.drop_index("ix_issues_audit_category", table_name="issues")
    op.drop_index("ix_issues_workspace_severity", table_name="issues")
    op.drop_index(op.f("ix_issues_component_ref_id"), table_name="issues")
    op.drop_index(op.f("ix_issues_workspace_id"), table_name="issues")
    op.drop_index(op.f("ix_issues_audit_id"), table_name="issues")
    op.drop_index(op.f("ix_issues_id"), table_name="issues")
    op.drop_table("issues")

    op.drop_index("ix_component_inventories_audit_ref", table_name="component_inventories")
    op.drop_index(op.f("ix_component_inventories_component_ref_id"), table_name="component_inventories")
    op.drop_index(op.f("ix_component_inventories_workspace_id"), table_name="component_inventories")
    op.drop_index(op.f("ix_component_inventories_audit_id"), table_name="component_inventories")
    op.drop_index(op.f("ix_component_inventories_id"), table_name="component_inventories")
    op.drop_table("component_inventories")

    op.drop_index("ix_audits_workspace_status", table_name="audits")
    op.drop_index(op.f("ix_audits_status"), table_name="audits")
    op.drop_index(op.f("ix_audits_created_by_id"), table_name="audits")
    op.drop_index(op.f("ix_audits_workspace_id"), table_name="audits")
    op.drop_index(op.f("ix_audits_id"), table_name="audits")
    op.drop_table("audits")
