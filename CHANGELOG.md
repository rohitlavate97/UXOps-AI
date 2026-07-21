# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Detailed Audit Report UI**: Added `AuditReportPage.tsx` to visualize the results of an individual audit, complete with scorecards for overall, UI, UX, and Accessibility scores.
- **Visual Bounding Boxes**: Created `ImageViewer.tsx` which overlays dynamic SVG bounding boxes directly over the uploaded screenshot, mapping coordinates provided by the backend vision agents.
- **Interactive Findings**: Linked the sidebar findings list to the image viewer, allowing users to highlight specific bounding boxes when they click a finding.
- **Audit Details Hook**: Extended `useAudits` with `fetchAuditDetails` to retrieve a specific audit and its nested findings from the backend API.
- **Audits Hooks**: Created `useAudits` hook to encapsulate API calls for fetching, creating, and triggering analysis of audits.
- **Dashboard UI**: Built the Dashboard page featuring high-level workspace metrics (Total Audits, Average Score, etc.) and a recent activity feed.
- **Audits List UI**: Implemented the Audits view showing a searchable, filterable grid of all design audits with dynamic status badges.
- **Audit Creation Flow**: Added a `NewAuditModal` containing a file upload drag-and-drop zone with image preview capabilities.
- **API Client**: Added centralized Axios client with request/response interceptors for JWT injection in `frontend/src/api/apiClient.ts`.
- **Global Auth State**: Created `AuthContext` to handle JWT persistence, user profile fetching, and centralized login/logout logic.
- **Workspace State**: Created `WorkspaceContext` to fetch the user's workspaces and persist active workspace selection.
- **Auth UI**: Built premium `LoginPage` and `SignupPage` with dark mode glassmorphism UI.
- **Protected Routing**: Implemented `ProtectedRoute` to restrict unauthenticated access to the dashboard in `App.tsx`.
- **Frontend App Structure**: Initialized a React 19 + TypeScript + Vite project in the `frontend` directory.
- **Frontend Design System**: Added `frontend/src/index.css` defining global CSS variables for colors, typography (Inter), and layout utilities to support a rich UI experience.
- **Base Components**: Added `Sidebar` and `Navbar` components using vanilla CSS modules (`.module.css`) for layout scaffolding.
- **Frontend Routing**: Integrated `react-router` and defined base placeholder pages (Dashboard, Audits, Reports, Activity, Settings) in `App.tsx`.
- **Pipeline Orchestration (Celery)**: Configured Celery worker with Redis broker in `backend/common/celery_app.py`.
- **Full Audit Pipeline Task**: Implemented asynchronous `run_full_audit_pipeline` in `backend/analysis/tasks.py` orchestrating all 10 agents sequentially, with granular `Audit.status` tracking (e.g., `VALIDATING`, `OCR_RUNNING`, `COMPLETED`).
- **Pipeline API Endpoint**: Created `POST /workspaces/{id}/analyze` in `backend/analysis/pipeline_router.py` to trigger the background Celery task and return a `task_id` (`202 Accepted`).
- **Pipeline Tests**: Added integration tests in `backend/tests/test_celery_pipeline.py`.
- **Report Generation Agent (Agent 10)**: Created `ReportFormat` and `ReportResult` schemas in `backend/reports/report_schemas.py`.
- **Report Formatting Engine**: Implemented `ReportGenerationAgent` in `backend/reports/report_agent.py` to aggregate DB metrics and render Markdown, HTML, JSON, and PDF reports via Jinja2 and ReportLab.
- **Report API Endpoint**: Created FastAPI route `GET /workspaces/{id}/audits/{id}/report` in `backend/reports/report_router.py` to expose formatted audit exports.
- **Report Test Suite**: Added `backend/tests/test_report_agent.py` testing template rendering outputs and endpoint format routing.
- **Scoring Agent (Agent 9)**: Created `ScoreWeighting`, `ScoreBreakdown`, and `ScoringResult` schemas in `backend/analysis/scoring_schemas.py`.
- **Scoring Engine**: Implemented deterministic `ScoringAgent` in `backend/analysis/scoring_agent.py` to calculate the final `overall_score` (UI: 40%, UX: 30%, A11y: 20%, Design System: 10%), handling partial/missing scores.
- **Scoring API Endpoint**: Created FastAPI route `GET /workspaces/{id}/audits/{id}/score` in `backend/analysis/scoring_router.py` which computes the score and marks the Audit status as `COMPLETED`.
- **Scoring Test Suite**: Added `backend/tests/test_scoring_agent.py` testing math normalization and API state transitions.
- **Recommendation Agent (Agent 8)**: Created `EnhancedRecommendation` and `RecommendationResult` schemas in `backend/analysis/recommendation_schemas.py` and version-controlled prompt `recommendation_agent_v1.txt`.
- **Recommendation Prioritization Engine**: Implemented `RecommendationAgent` in `backend/analysis/recommendation_agent.py` to aggregate raw DB issues, assign PM-style priorities (P0-P4), and estimate improvement metrics.
- **Recommendation API Endpoint**: Created FastAPI route `GET /workspaces/{id}/audits/{id}/recommendations` in `backend/analysis/recommendation_router.py`.
- **Recommendation Test Suite**: Added `backend/tests/test_recommendation_agent.py` testing prioritization mappings, sorting, and end-to-end DB aggregation logic.
- **Design System Agent (Agent 7)**: Created `DesignSystemIssue`, `DesignMetricResult`, and `DesignSystemResult` schemas in `backend/analysis/design_system_schemas.py` and version-controlled prompt `design_system_agent_v1.txt`.
- **RAG Guidelines Validation**: Implemented `DesignSystemAgent` in `backend/analysis/design_system_agent.py` to check standard material constraints and validate against user-uploaded company design rules via RAG.
- **Design System API Endpoint**: Created FastAPI route `GET /workspaces/{id}/audits/{id}/design-system` in `backend/analysis/design_system_router.py`.
- **Design System Test Suite**: Added `backend/tests/test_design_system_agent.py` testing Material guidelines enforcement, RAG rule lookup, empty payloads, score computation, and API integration.
- **UX Analysis Agent (Agent 6)**: Created `UXAnalysisIssue`, `UXMetricResult`, and `UXAnalysisResult` schemas in `backend/analysis/ux_analysis_schemas.py` and version-controlled prompt `ux_analysis_agent_v1.txt`.
- **UX Heuristics Engine**: Implemented `UXAnalysisAgent` in `backend/analysis/ux_analysis_agent.py` supporting evaluation of discoverability, cognitive load, and feedback, referring to Agent 3's components.
- **UX Analysis API Endpoint**: Created FastAPI route `GET /workspaces/{id}/audits/{id}/ux-analysis` in `backend/analysis/ux_analysis_router.py`.
- **UX Analysis Test Suite**: Added `backend/tests/test_ux_analysis_agent.py` testing UX heuristics, empty payload handling, score computation, database persistence, and API route authorization.
- **UI Analysis Agent (Agent 5)**: Created `UIAnalysisIssue`, `UIMetricResult`, and `UIAnalysisResult` schemas in `backend/analysis/ui_analysis_schemas.py` and version-controlled prompt `ui_analysis_agent_v1.txt`.
- **UI Design Engine**: Implemented `UIAnalysisAgent` in `backend/analysis/ui_analysis_agent.py` supporting alignment and spacing analysis, relying on Agent 3 component references.
- **UI Analysis API Endpoint**: Created FastAPI route `GET /workspaces/{id}/audits/{id}/ui-analysis` in `backend/analysis/ui_analysis_router.py`.
- **UI Analysis Test Suite**: Added `backend/tests/test_ui_analysis_agent.py` testing alignment logic, empty payload handling, score computation, issue persistence, and API route authorization.
- **Accessibility Agent (Agent 4)**: Created `AccessibilityIssue`, `ContrastAnalysisResult`, and `AccessibilityResult` schemas in `backend/analysis/accessibility_schemas.py` and version-controlled prompt `accessibility_agent_v1.txt`.
- **WCAG 2.2 Compliance Engine**: Implemented `AccessibilityAgent` in `backend/analysis/accessibility_agent.py` supporting relative luminance contrast calculations, minimum touch target size checks (44x44px), and cross-referencing Agent 3 component IDs.
- **Accessibility API Endpoint**: Created FastAPI route `GET /workspaces/{id}/audits/{id}/accessibility` in `backend/analysis/accessibility_router.py`.
- **Accessibility Test Suite**: Added `backend/tests/test_accessibility_agent.py` testing contrast math, WCAG 2.2 rules, score computation, issue persistence, and API route authorization.

## [0.7.0] - 2026-07-21

### Added
- **Component Detection Agent (Agent 3)**: Created `DetectedComponent`, `ComponentBoundingBox`, and `ComponentInventoryResult` schemas in `backend/vision/component_schemas.py` and version-controlled prompt `component_detection_v1.txt`.
- **Authoritative Component Inventory**: Implemented `ComponentDetectionAgent` in `backend/vision/component_agent.py` establishing master component references (`comp_001`, `comp_002`, ...) and cross-referencing upstream OCR text elements.
- **Component API Endpoint**: Created FastAPI route `GET /workspaces/{id}/audits/{id}/components` in `backend/vision/component_router.py`.
- **Component Test Suite**: Added `backend/tests/test_component_agent.py` testing Agent 3 lifecycle, component classification, OCR cross-referencing, DB persistence, and API route integration.

## [0.6.0] - 2026-07-21

### Added
- **OCR Agent (Agent 2)**: Created `OcrTextElement`, `OcrBoundingBox`, and `OcrResult` schema contracts in `backend/ocr/schemas.py` and version-controlled system prompt `ocr_agent_v1.txt`.
- **OCR Extraction Engine**: Implemented `OcrAgent` in `backend/ocr/agent.py` supporting EasyOCR extraction, sequential element ID assignment (`txt_001`), and element classification (`heading`, `button_label`, `input_label`, `nav_link`).
- **OCR API Endpoint**: Created FastAPI route `GET /workspaces/{id}/audits/{id}/ocr` in `backend/ocr/router.py`.
- **OCR Test Suite**: Created `backend/tests/test_ocr_agent.py` testing Agent 2 extraction lifecycle, element classification, empty payload handling, and HTTP GET OCR API route integration.

## [0.5.0] - 2026-07-21

### Added
- **Screenshot Validation Agent (Agent 1)**: Created `ScreenshotValidationResult` output schema in `backend/agents/validation_schema.py` and version-controlled prompt `screenshot_validation_v1.txt`.
- **Validation Agent Logic**: Implemented `ScreenshotValidationAgent` in `backend/agents/screenshot_validation_agent.py` combining classical computer vision metrics (dimensions, aspect ratio, blur score) with structured visual validation.
- **Pipeline Upload Gate**: Integrated `ScreenshotValidationAgent` into FastAPI upload endpoint `POST /workspaces/{id}/audits/upload` in `backend/storage/router.py`.
- **Validation Test Suite**: Created `backend/tests/test_validation_agent.py` testing Agent 1 on valid PNG bytes, empty payloads, and layout device classifications (`desktop_web`, `mobile_app`, `tablet`).

## [0.4.0] - 2026-07-21

### Added
- **Storage Provider Abstraction**: Implemented `StorageProvider` interface with `LocalStorageProvider` and `S3StorageProvider` in `backend/storage/provider.py`.
- **Image Validation Utility**: Added binary magic byte inspection, 20 MB size limit enforcement, and resolution validation in `backend/storage/validator.py`.
- **Screenshot Ingestion API**: Created FastAPI routes for screenshot multipart upload (`POST /workspaces/{id}/audits/upload`) and presigned S3 upload URL generation (`POST /workspaces/{id}/audits/presigned-url`).
- **Storage Test Suite**: Added comprehensive unit and integration tests in `backend/tests/test_storage.py`.

## [0.3.0] - 2026-07-21

### Added
- **Domain Database Schema**: Implemented `Audit`, `ComponentInventory`, `Issue`, `Report`, and `DesignGuideline` SQLAlchemy models in `backend/database/models.py`.
- **Alembic Domain Migration**: Generated and applied migration `a6b7c8d9e0f1` with composite tenant indexes (`ix_audits_workspace_status`, `ix_component_inventories_audit_ref`, `ix_issues_workspace_severity`).
- **Database Seeding CLI**: Added `backend/database/seed.py` for automated environment population with workspaces, users, audit runs, component inventories, accessibility findings, and design guidelines.
- **Multi-Tenant Isolation Tests**: Created `backend/tests/test_tenant_isolation.py` verifying strict multi-tenant query isolation and cascade deletion behavior.
- **Antigravity CLI Optimization**: Added `AGENTS.md`, cross-platform launcher scripts (`scripts/start-agy.sh`, `scripts/start-agy.bat`, `scripts/start-agy.ps1`), VS Code tasks/settings, `COMMANDS.md`, and comprehensive documentation in `docs/`.

## [0.2.0] - 2026-07-09

### Added
- **Authentication & RBAC**: Implemented secure sign-up, JWT-based sign-in, and Role-Based Access Control (RBAC) with roles like `owner`, `admin`, `member`, and `viewer`.
- **Workspace/Tenant Model**: Set up multi-tenant workspace structures mapping user memberships to isolated workspace environments.
- **Database Models**: Defined SQLAlchemy declarative base with UUID identifiers and audit columns, alongside User, Workspace, and WorkspaceMember entities.
- **Alembic Migrations**: Initialized database versioning with Alembic and generated/applied the initial schema migrations dynamically.
- **Async Database Connection**: Configured SQLAlchemy async engine and dependency session injections for FastAPI routers.
- **Test Coverage**: Added Pytest fixtures and 8 integration tests validating login, signup, workspace creation, membership scoping, and RBAC constraints.
- **ADR & Documentation**: Drafted ADR 0002 for authentication and isolation strategies, and established tracking for Milestone 2.

## [0.1.0] - 2026-07-09

### Added
- **Project Structure**: Initialized backend directories (agents, vision, ocr, analysis, prompts, reports, pdf, database, storage, auth, common, tests) and frontend directory.
- **Docker Compose Skeleton**: Created `docker-compose.yml` defining services for PostgreSQL, Redis, Celery worker, FastAPI backend, and React/Vite frontend.
- **CI/CD Pipeline**: Configured GitHub Actions CI (`.github/workflows/ci.yml`) for automated linting (Ruff, Flake8, Black, Isort, Oxlint) and backend/frontend test suite.
- **Pre-commit Configuration**: Established pre-commit hooks (`.pre-commit-config.yaml`) for code formatting and formatting checks.
- **Backend Dockerization**: Added `backend/Dockerfile` and `backend/requirements.txt` with foundational FastAPI/Pydantic/Celery packages.
- **Frontend Scaffolding**: Initialized React 19 + TypeScript + Vite project in `frontend/` using non-interactive CLI.
- **Developer Documentation**: Drafted Developer Guide (`docs/developer_guide.md`) and Architecture Decision Record (`docs/ADR/0001-project-setup-and-dev-workflow.md`).
