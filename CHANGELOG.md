# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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


