# UXOps AI — Enterprise AI UI/UX Quality Engineering Platform

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![React Version](https://img.shields.io/badge/react-19.0-61dafb)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688)
![License](https://img.shields.io/badge/license-MIT-green)

**UXOps AI** is an enterprise-grade AI UI/UX quality engineering and automated design auditing platform. It combines multimodal vision models, EasyOCR text extraction, deterministic spacing/alignment rule engines, and automated PDF report generation to streamline design reviews, accessibility checks, and brand compliance verification.

---

## 🌟 Architecture & Key Features

* **Multimodal AI Auditing**: Automated visual defect detection, typography analysis, and design rule validation.
* **OCR & Visual Grounding**: High-precision text localization via EasyOCR and spatial alignment bounding.
* **FastAPI Async Backend**: High-concurrency microservice with JWT authentication, RBAC, and multi-tenant workspace isolation.
* **Distributed Task Execution**: Asynchronous queue processing using Redis and Celery workers for heavy visual workloads.
* **React 19 + Vite Frontend**: High-performance single-page application for real-time audit visualization and workspace management.
* **Database & Storage**: PostgreSQL relational storage with Alembic migrations and S3 object storage for UI assets.

---

## 🚀 Quick Start

### 1. Prerequisites
* **Python**: 3.12+
* **Node.js**: v20+ (with npm)
* **Docker & Docker Compose**: Docker 28+, Docker Compose v2+
* **Git**

### 2. Booting up with Docker Compose
To run the full UXOps AI stack (PostgreSQL, Redis, Celery, Backend, Frontend):

```bash
docker compose up --build
```

Access the application services:
* **Frontend App**: [http://localhost:5173](http://localhost:5173)
* **Backend REST API**: [http://localhost:8000](http://localhost:8000)
* **Interactive Swagger Specs**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc API Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🤖 Working with Antigravity CLI

This repository is fully optimized for pair-programming and automated workflows with **Antigravity CLI** (`agy`), Google's AI-first developer assistant.

### 1. Installation
To install the Antigravity CLI on your development machine, run:

```bash
# Install via official installer script
curl -fsSL https://antigravity.google/install.sh | bash
```
Verify the installation by running:
```bash
agy --version
```

### 2. Launching Antigravity CLI
You can launch Antigravity CLI using the provided cross-platform helper scripts located in the `scripts/` directory:

* **macOS / Linux (Bash/Zsh)**:
  ```bash
  ./scripts/start-agy.sh
  ```
* **Windows Command Prompt (Batch)**:
  ```cmd
  scripts\start-agy.bat
  ```
* **Windows PowerShell**:
  ```powershell
  .\scripts\start-agy.ps1
  ```

Alternatively, you can run `agy` directly from the project root directory.

### 3. How `AGENTS.md` is Ingested
When Antigravity CLI starts in this repository, it automatically reads and ingests the root [`AGENTS.md`](file:///Volumes/Element/Projects/AI/UXOps-AI/AGENTS.md) file. This gives Antigravity persistent context regarding:
* Repository architecture and folder layout
* Technology stack specifications (Python 3.12, FastAPI, React 19, Celery, Postgres)
* Strict coding standards (Black, Isort, Ruff, TypeScript strict mode)
* Naming conventions and security policies
* Testing requirements and Git commit rules

### 4. Project Conventions for AI Pair Programming
When collaborating with Antigravity CLI:
* **Read-First Directive**: Antigravity is instructed to analyze existing modules before introducing new logic.
* **Code Reuse**: Prioritize extending existing schemas in `/backend/database/` and components in `/frontend/src/`.
* **Zero Secrets Policy**: Never paste production API keys, passwords, or database credentials into chat prompts.
* **Automated Linting**: All AI-generated code should pass local formatters (`black backend/`, `isort backend/`, `oxlint frontend/`).

### 5. Best Practices with Antigravity
* **Slash Commands**: Use `/plan` for complex multi-step refactors, `/schedule` for background tasks, and `/goal` for autonomous long-running objectives.
* **Subagents**: Launch specialized background subagents using Antigravity's multi-agent capabilities for independent research or parallel test writing.
* **Command Verification**: Always review proposed terminal commands prior to execution.

---

## 🛠️ Development & Command Reference

For detailed command listings (building, testing, linting, formatting, database migrations, Docker, and CI), consult [`COMMANDS.md`](file:///Volumes/Element/Projects/AI/UXOps-AI/COMMANDS.md).

### Quick Commands Cheat Sheet

| Task | Local Command |
| :--- | :--- |
| **Backend Hot-Reload** | `cd backend && uvicorn main:app --reload` |
| **Frontend Hot-Reload** | `cd frontend && npm run dev` |
| **Run Backend Tests** | `cd backend && pytest tests/ -v` |
| **Format Python Code** | `black backend/ && isort backend/` |
| **Lint Python Code** | `ruff check backend/` |
| **Lint Frontend Code** | `cd frontend && npm run lint` |
| **Create DB Migration** | `cd backend && alembic revision --autogenerate -m "msg"` |

---

## 📚 Documentation Index

Detailed engineering documentation is available in the [`docs/`](file:///Volumes/Element/Projects/AI/UXOps-AI/docs) directory:

* [`docs/architecture.md`](file:///Volumes/Element/Projects/AI/UXOps-AI/docs/architecture.md) — System design, multi-tenancy, data flow, and vision pipeline.
* [`docs/coding-standards.md`](file:///Volumes/Element/Projects/AI/UXOps-AI/docs/coding-standards.md) — Detailed Python, TypeScript, and styling conventions.
* [`docs/development.md`](file:///Volumes/Element/Projects/AI/UXOps-AI/docs/development.md) — Local development environment setup & DB workflow.
* [`docs/testing.md`](file:///Volumes/Element/Projects/AI/UXOps-AI/docs/testing.md) — Unit testing, integration testing, and CI verification strategy.
* [`docs/deployment.md`](file:///Volumes/Element/Projects/AI/UXOps-AI/docs/deployment.md) — Production Docker Compose and Kubernetes deployment guide.
* [`docs/developer_guide.md`](file:///Volumes/Element/Projects/AI/UXOps-AI/docs/developer_guide.md) — Developer onboarding guide.

---

## 📄 License

This project is licensed under the MIT License — see the `LICENSE` file for details.
