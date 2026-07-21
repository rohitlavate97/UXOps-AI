# AGENTS.md — Antigravity AI Agent Instructions

This document provides definitive project context, architectural guidelines, technical specifications, and operational rules for AI assistants (including Antigravity CLI `agy`, Antigravity IDE, and subagents) working in the **UXOps AI** repository.

---

## 1. Project Overview

**UXOps AI** is an enterprise-grade AI UI/UX quality engineering and automated design auditing platform. It leverages multimodal AI agents, computer vision, OCR, and deterministic design rule engines to analyze web and mobile application interfaces for visual defects, spacing inconsistencies, accessibility flaws, typography issues, and brand compliance.

### Core Architecture Components
* **Backend API (`/backend`)**: Asynchronous Python FastAPI microservice providing REST endpoints for authentication, multi-tenant workspace management, design asset uploads, analysis orchestration, and report generation.
* **Asynchronous Task Engine (`/backend/common/celery_app.py`)**: Celery worker pool backed by Redis for distributed execution of heavy visual processing, EasyOCR extraction, and multimodal vision analysis.
* **Frontend Web App (`/frontend`)**: React 19 + TypeScript + Vite single-page application built for high-performance visual design reviews, real-time audit feedback, and team workspace collaboration.
* **Database & Persistence (`/backend/database`)**: PostgreSQL database managed via SQLAlchemy 2.0 async engine with Alembic migrations. S3-compatible object storage for UI screenshot uploads.
* **Containerization & Orchestration (`/docker-compose.yml`, `/kubernetes`)**: Docker Compose for local multi-container development; Kubernetes manifests for production deployment.

---

## 2. Technology Stack & Key Dependencies

| Domain | Technology / Library | Usage & Details |
| :--- | :--- | :--- |
| **Backend Language** | Python 3.12+ | Type hinted, async-first Python codebase |
| **Web Framework** | FastAPI (>= 0.111.0) | OpenAPI compliant async REST framework |
| **Async ORM** | SQLAlchemy (>= 2.0.31) | Async engine with declarative base and UUID primary keys |
| **DB Migrations** | Alembic (>= 1.13.1) | Automated schema migration tracking |
| **Database** | PostgreSQL 16 | Relational store for users, workspaces, audits, reports |
| **Task Queue / Cache** | Redis 7 + Celery 5.4 | Background job execution and caching |
| **AI / OCR / Vision** | EasyOCR, Instructor, Pydantic | OCR extraction, structured AI outputs, grounding |
| **Testing Engine** | Pytest, Pytest-Asyncio, HTTPX | Async unit and API integration testing |
| **Code Quality** | Ruff, Black, Isort, Flake8 | Automated linting, import sorting, and formatting |
| **Frontend Framework** | React 19 + TypeScript 5.x | Modern UI components with strict type checking |
| **Build Tooling** | Vite (>= 8.1.1) | Lightning-fast module bundler and dev server |
| **Frontend Linting** | Oxlint (>= 1.71.0) | High-speed JavaScript/TypeScript linter |

---

## 3. Directory Structure

```text
uxops-ai/
├── .github/              # GitHub Actions CI/CD workflows
│   └── workflows/
│       └── ci.yml        # Automated test, lint, and build verification
├── .vscode/              # Editor tasks, launch configs, and extension recommendations
├── backend/              # FastAPI Application & AI Pipeline
│   ├── agents/           # Multimodal AI agents & prompt execution logic
│   ├── alembic.ini       # Alembic database migration configuration
│   ├── alembic/          # Database migration revisions and env script
│   ├── analysis/         # Alignment, spacing, and design rule engines
│   ├── auth/             # Authentication, JWT handling, and RBAC policies
│   ├── common/           # Celery application & shared utility modules
│   ├── database/         # SQLAlchemy models, async session, and repositories
│   ├── main.py           # FastAPI application entrypoint & router mounts
│   ├── ocr/              # EasyOCR processing and text element bounding
│   ├── pdf/              # PDF report generation and exporting engine
│   ├── prompts/          # Version-controlled AI prompts and system instructions
│   ├── reports/          # Audit summary report builders
│   ├── requirements.txt  # Backend Python dependencies
│   ├── storage/          # S3 file storage wrappers & object management
│   ├── tests/            # Unit and API integration test suite
│   └── vision/           # Computer vision utilities & visual grounding
├── docs/                 # Architectural & developer documentation
│   ├── ADR/              # Architecture Decision Records (0001, 0002)
│   ├── architecture.md   # System architecture & data flow specification
│   ├── coding-standards.md # Python & TypeScript style guide
│   ├── deployment.md     # Container & Kubernetes deployment guide
│   ├── development.md    # Local environment setup & workflow
│   ├── developer_guide.md# Developer onboarding guide
│   └── testing.md        # Comprehensive testing guidelines
├── frontend/             # React 19 + TypeScript + Vite Client Application
│   ├── src/              # App components, pages, hooks, and services
│   ├── index.html        # HTML entrypoint
│   ├── package.json      # Dependencies and script definitions
│   └── vite.config.ts    # Vite bundler configuration
├── kubernetes/           # K8s manifests (Deployments, Services, ConfigMaps)
├── milestones/           # Project roadmap and milestone tracking
├── scripts/              # Helper launcher scripts (start-agy.sh, start-agy.bat, start-agy.ps1)
├── AGENTS.md             # Antigravity CLI instructions (This file)
├── COMMANDS.md           # Developer & CI command cheat sheet
├── docker-compose.yml    # Local multi-container stack configuration
└── README.md             # Project overview and Antigravity guide
```

---

## 4. Coding Standards & Conventions

### Python Standards (Backend)
1. **Formatting**: Follow PEP 8 guidelines. Black is configured with an 88-character max line length.
2. **Import Ordering**: Format imports with `isort`. Grouping order: standard library -> 3rd-party dependencies -> local application modules.
3. **Type Annotations**: All function signatures (arguments and return types) must include explicit Python type hints (`str`, `UUID`, `AsyncSession`, `Optional[...]`).
4. **Async-First**: Use `async def` for FastAPI endpoint handlers and database operations using SQLAlchemy's `AsyncSession`. Avoid blocking I/O calls inside async routes.
5. **Schema Validation**: Use Pydantic v2 `BaseModel` models for request validation and response serialisation.

### TypeScript / React Standards (Frontend)
1. **Strict Type Safety**: Enable strict mode in TypeScript (`tsconfig.json`). Never use `any`; use `unknown` with type narrowing or define explicit interfaces.
2. **Functional Components**: Write React components using functional syntax with explicitly typed props interfaces (e.g., `interface ButtonProps`).
3. **Linting**: Ensure code passes `oxlint` without errors or warnings.
4. **Modularity**: Small, single-responsibility components placed in `src/components/`. Business logic belongs in custom hooks (`src/hooks/`).

---

## 5. Naming Conventions

* **Files & Directories**:
  * Python files & directories: `snake_case.py` (e.g., `auth_service.py`, `workspace_router.py`).
  * TypeScript components: `PascalCase.tsx` (e.g., `AuditReportCard.tsx`).
  * TS utilities & hooks: `camelCase.ts` or `useCamelCase.ts` (e.g., `useWorkspace.ts`, `apiClient.ts`).
  * CSS/Asset files: `kebab-case.css` or `kebab-case.png`.
* **Variables & Functions**:
  * Python: `snake_case` for variables, functions, and methods (`get_user_by_id`, `is_authenticated`).
  * TypeScript: `camelCase` for variables, functions, and object keys (`fetchAuditLogs`, `userRole`).
* **Classes & Models**:
  * Python/TypeScript classes & interfaces: `PascalCase` (`UserModel`, `WorkspaceMember`, `AuditResult`).
* **Database Tables & Columns**:
  * Tables: plural `snake_case` (e.g., `users`, `workspaces`, `workspace_members`).
  * Primary Keys: `id` (UUID v4 format).
  * Foreign Keys: `singular_table_id` (e.g., `workspace_id`, `user_id`).

---

## 6. Architecture & Design Guidelines

1. **Layered FastAPI Architecture**:
   * **Routers (`/backend/auth`, etc.)**: Transport layer. Validate requests and format responses. Contain no raw database queries.
   * **Services / Logic (`/backend/auth/service.py`, etc.)**: Business logic layer.
   * **Models / Repositories (`/backend/database`)**: Persistence layer using SQLAlchemy declarative entities.
2. **Multi-Tenancy & Security Scoping**:
   * All database queries for workspace resources **must** be scoped by `workspace_id`.
   * Enforce Role-Based Access Control (RBAC) on all protected endpoints (`owner`, `admin`, `member`, `viewer`).
3. **Asynchronous Background Processing**:
   * Heavy computations (OCR processing, PDF generation, computer vision audits) must be dispatched to Celery tasks (`/backend/common/celery_app.py`).

---

## 7. Security Rules

1. **No Credentials in Code**: Never commit secrets, API keys, passwords, JWT secrets, or tokens. Use environment variables managed via Pydantic `BaseSettings`.
2. **Password Hashing**: Store passwords using `bcrypt` algorithm with proper salting.
3. **JWT Tokens**: Authenticate API requests using Bearer JWT tokens with reasonable expiration times.
4. **Input Sanitization**: Validate all client inputs through Pydantic models to prevent injection vulnerabilities.

---

## 8. Testing Requirements

* **Backend Unit & Integration Tests**:
  * Tests reside in `/backend/tests/`.
  * Run pytest using: `cd backend && pytest tests/ -v`.
  * Every new endpoint or feature requires corresponding integration tests covering successful execution and failure edge cases (e.g., unauthorized access, missing workspace).
* **Frontend Tests**:
  * Place unit and component tests alongside source files or in `/frontend/src/__tests__/`.
  * Run tests via `npm run test` inside `/frontend`.

---

## 9. Git & Pull Request Workflow

1. **Branch Naming**:
   * Features: `feat/short-description` (e.g., `feat/ocr-bounding-box`)
   * Fixes: `fix/short-description` (e.g., `fix/jwt-expiration-handling`)
   * Milestones: `milestone-N` (e.g., `milestone-2`)
2. **Commit Messages**: Use Conventional Commits formatting:
   * `feat: add workspace creation endpoint`
   * `fix: handle async db connection timeout`
   * `docs: update deployment instructions`
3. **Pull Request Checklist**:
   * All CI checks (linting, formatting, backend tests, frontend build) must pass cleanly.
   * Code coverage must not decrease.
   * Documentation (`AGENTS.md`, `COMMANDS.md`, or `docs/`) updated if architectural changes are made.

---

## 10. AI Assistant Mandatory Rules (Task 8 Requirements)

When operating inside this repository, AI agents (Antigravity CLI, IDE, and subagents) **MUST** strictly adhere to the following directives:

1. **Read Before Writing**: Inspect existing files and understand the current codebase layout before creating or modifying code.
2. **Architectural Awareness**: Review relevant architecture documents (`docs/architecture.md`, `docs/ADR/`) prior to implementing non-trivial features.
3. **Reuse Over Duplication**: Search for existing helper utilities, database models, or React components instead of reimplementing logic.
4. **Strict Style Compliance**: Follow Python (PEP 8 / Black / Isort) and TypeScript naming and structural conventions strictly.
5. **Small & Modular Functions**: Write concise, focused functions with single responsibilities. Avoid long monolithic procedures.
6. **Production-Quality Output**: Provide clean, fully formatted, typed, and error-handled code. Do not introduce half-baked scripts or placeholders.
7. **Document Public APIs**: Add complete docstrings (Python) or TSDoc comments (TypeScript) for any newly created public functions, endpoints, or interfaces.
8. **Add Comprehensive Tests**: Always write unit/integration tests alongside new features or bug fixes.
9. **Zero Secret Leaks**: Never hardcode API keys, passwords, database credentials, or secret tokens into any file.
10. **Protect Immutable Artifacts**: Do NOT modify Alembic migration histories, lockfiles, or core configuration files unless explicitly requested.
11. **Seek Clarification**: If a prompt or requirement is ambiguous, stop and ask the user for clarification before executing risky modifications.
12. **Explain Decisions**: Summarize key design choices and architectural considerations when submitting changes or PR descriptions.

---

## 11. Things That Must Never Be Modified Without Instructions

* Existing Alembic migration script history (`/backend/alembic/versions/*`)
* System database models core schema without an accompanying Alembic migration
* `.pre-commit-config.yaml` or `.github/workflows/ci.yml` matrix without explicit instruction
* Third-party license declarations or project master prompt specs (`uxops-ai-master-prompt-v2.md`)

---

## 12. Preferred Development Commands

| Action | Command |
| :--- | :--- |
| **Launch Stack (Docker)** | `docker compose up --build` |
| **Backend Hot-Reload** | `cd backend && uvicorn main:app --reload` |
| **Frontend Dev Server** | `cd frontend && npm run dev` |
| **Backend Tests** | `cd backend && pytest tests/ -v` |
| **Frontend Lint** | `cd frontend && npm run lint` |
| **Python Formatting** | `black backend/ && isort backend/` |
| **Python Linting** | `ruff check backend/` |
| **DB Migration Creation** | `cd backend && alembic revision --autogenerate -m "description"` |
| **DB Migration Upgrade** | `cd backend && alembic upgrade head` |
| **Launch Antigravity** | `./scripts/start-agy.sh` |

---

## 13. Code Review & PR Verification Checklist

Before submitting or approving code changes, verify that:

- [ ] Code compiles and builds without syntax or type errors.
- [ ] Pytest suite passes cleanly (`cd backend && pytest tests/`).
- [ ] Python code is formatted with Black and Isort (`black backend/ && isort backend/`).
- [ ] Ruff / Flake8 checks report zero violations (`ruff check backend/`).
- [ ] Frontend Oxlint checks pass (`cd frontend && npm run lint`).
- [ ] Database migrations are created and tested if schema changed.
- [ ] No hardcoded passwords, secrets, or local environment overrides are committed.
- [ ] New public methods contain complete type hints and docstrings.
