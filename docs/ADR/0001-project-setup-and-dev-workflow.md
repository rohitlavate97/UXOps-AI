# ADR 0001: Project Setup and Development Workflow

## Status
Proposed (to be Approved with milestone merge)

## Context
UXOps AI requires a standardized, modern local development environment and a robust CI/CD pipeline to support team collaboration and maintain enterprise-grade quality. We need a structure that allows local development using Docker Compose while preserving fast local rebuilds and linters/tests checks.

## Decision
1. **Repository Structure**: Implement a monorepo structure with a clear boundary:
   - `backend/` for the Python 3.12, FastAPI, and AI agent pipeline.
   - `frontend/` for the React 19, TypeScript, and Vite frontend.
2. **Containerization**: Use Docker Compose to orchestrate dependencies (PostgreSQL 16, Redis 7, Celery Worker, FastAPI backend, React frontend) for local parity.
3. **Continuous Integration**: Configure GitHub Actions to automatically run python linters (Ruff/Flake8, Black, Isort), frontend linters (Oxlint), and unit/integration tests on every push/PR.
4. **Git Branching**: Standardize on `milestone-<number>-<short-name>` branch formatting and prohibit direct commits to `main`.
5. **Code Hygiene**: Set up `pre-commit` to prevent badly-formatted code from being committed.

## Alternatives Considered
- **Polyrepo (Separate Frontend/Backend Repos)**:
  - *Pros*: Completely separate permissions and pipelines.
  - *Cons*: High overhead for a single workspace, harder to trace unified milestones and coordinate database schema changes with API and UI updates.
  - *Result*: Rejected in favor of a clean Monorepo setup to simplify development and coordination.

## Consequences
- Developers need Docker and Docker Compose installed.
- All code changes must pass linting and formatting gates before being pushed to the remote repository.
- Increased local environment reliability.
