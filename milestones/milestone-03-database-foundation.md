# Milestone 3: Database Foundation & Multi-Tenant Data Schema

## Status
- [x] Defined domain database models (`Audit`, `ComponentInventory`, `Issue`, `Report`, `DesignGuideline`) in `backend/database/models.py`
- [x] Generated and verified Alembic DDL migration `a6b7c8d9e0f1_create_domain_audit_tables.py`
- [x] Created composite indexes for workspace filtering and component referential integrity
- [x] Implemented CLI seed script `backend/database/seed.py` for automated environment population
- [x] Added domain model unit tests in `backend/tests/test_domain_models.py`
- [x] Added CLI seed script unit tests in `backend/tests/test_seed.py`
- [x] Added strict multi-tenant isolation and cascade deletion tests in `backend/tests/test_tenant_isolation.py`
- [x] Updated ER diagram in `docs/architecture.md` and CHANGELOG

## Tasks & Deliverables

### 1. Domain Database Models (`backend/database/models.py`)
* **`Audit`**: Stores audit run configuration, target url/image, status (`PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`), error message, and visual score metrics (`overall_score`, `ui_score`, `ux_score`, `accessibility_score`, `consistency_score`, `readability_score`).
* **`ComponentInventory`**: Authoritative inventory of detected UI components with bounding box coordinates, component type, label, confidence rating, and `component_ref_id` linkage.
* **`Issue`**: Categorized UI/UX/Accessibility findings (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`) with impact analysis, recommendations, confidence ratings, and `automated_assessment` flags.
* **`Report`**: Executive summary, JSON payload summary, and S3 artifact keys.
* **`DesignGuideline`**: Workspace brand and design system guidelines for RAG analysis.

### 2. Migration Versioning (`backend/database/migrations/versions/a6b7c8d9e0f1_create_domain_audit_tables.py`)
* Applied versioned schema changes linking `audits`, `component_inventories`, `issues`, `reports`, and `design_guidelines` to `workspaces` and `users`.
* Added performance composite indexes: `ix_audits_workspace_status`, `ix_component_inventories_audit_ref`, `ix_issues_workspace_severity`, and `ix_issues_audit_category`.

### 3. Automated Seeding (`backend/database/seed.py`)
* Executable script for seeding test workspaces (`acme-design`, `fintech-mobile`), admin/designer users, sample audit runs, component inventories, accessibility findings, reports, and design system documents.

### 4. Verification & Testing
* **Domain Model Tests**: Validated model fields, defaults, and foreign key relationships.
* **Seed Script Tests**: Verified schema creation and sample data population.
* **Multi-Tenant Isolation Tests**: Verified that queries filtering by `workspace_id` strictly prevent cross-tenant data leakage, and cascade deletes function properly.
