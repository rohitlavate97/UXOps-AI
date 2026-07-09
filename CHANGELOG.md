# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Project Structure**: Initialized backend directories (agents, vision, ocr, analysis, prompts, reports, pdf, database, storage, auth, common, tests) and frontend directory.
- **Docker Compose Skeleton**: Created `docker-compose.yml` defining services for PostgreSQL, Redis, Celery worker, FastAPI backend, and React/Vite frontend.
- **CI/CD Pipeline**: Configured GitHub Actions CI (`.github/workflows/ci.yml`) for automated linting (Ruff, Flake8, Black, Isort, Oxlint) and backend/frontend test suite.
- **Pre-commit Configuration**: Established pre-commit hooks (`.pre-commit-config.yaml`) for code formatting and formatting checks.
- **Backend Dockerization**: Added `backend/Dockerfile` and `backend/requirements.txt` with foundational FastAPI/Pydantic/Celery packages.
- **Frontend Scaffolding**: Initialized React 19 + TypeScript + Vite project in `frontend/` using non-interactive CLI.
- **Developer Documentation**: Drafted Developer Guide (`docs/developer_guide.md`) and Architecture Decision Record (`docs/ADR/0001-project-setup-and-dev-workflow.md`).
