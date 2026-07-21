# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
