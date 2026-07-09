# UXOps AI — Developer Guide

Welcome to the UXOps AI development repository. This document guides you through setting up and working on the platform.

## Prerequisites
- **Python**: 3.12 (or 3.9+ for running local tools)
- **Node.js**: v20+ (with npm)
- **Docker & Docker Compose**: Docker 28+, Docker Compose v2+
- **Git**

---

## Directory Layout
```text
uxops-ai/
├── frontend/             # React 19 + TypeScript + Vite
├── backend/              # FastAPI, Celery, and AI Agent Pipeline
│   ├── agents/           # Specialized vision/OCR agents
│   ├── vision/           # Visual model abstraction & grounding
│   ├── ocr/              # EasyOCR integration
│   ├── analysis/         # Spacing, alignment, consistency logic
│   ├── prompts/          # Version-controlled prompt templates
│   ├── reports/          # Report orchestration
│   ├── pdf/              # PDF export engine
│   ├── database/         # SQLAlchemy models and migrations
│   ├── storage/          # S3 connection and file helpers
│   ├── auth/             # Authentication & RBAC services
│   ├── common/           # Celery application & shared utilities
│   └── tests/            # pytest suite (unit, API, and vision evaluation)
├── docker/               # Docker configurations
├── kubernetes/           # Kubernetes manifests (deployments, services)
├── docs/                 # Documentation (Guides, ADRs)
└── .github/              # GitHub CI workflows
```

---

## Getting Started

### 1. Pre-commit Hooks Setup
Install and activate `pre-commit` locally to ensure formatting and linting standards:
```bash
pip install pre-commit
pre-commit install
```
This runs checks automatically on `git commit`. You can also trigger it manually:
```bash
pre-commit run --all-files
```

### 2. Running the Application via Docker Compose
To boot up the entire stack (PostgreSQL, Redis, Celery, Backend, Frontend):
```bash
docker compose up --build
```
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Frontend App**: [http://localhost:5173](http://localhost:5173)

### 3. Running Backend Locally (For Active Development)
If you prefer running the backend outside Docker for faster hot-reloading:
1. Create and activate a virtual environment:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start development server:
   ```bash
   uvicorn main:app --reload
   ```

### 4. Running Frontend Locally
To run the Vite dev server locally:
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   npm install
   ```
2. Run development server:
   ```bash
   npm run dev
   ```

---

## Testing Strategy

### Backend Tests
Run the test suite using `pytest`:
```bash
cd backend
pytest tests/
```

### CI/CD Pipeline
Every pull request and push to the `milestone-*` branches automatically triggers the CI/CD pipeline in GitHub Actions, which:
1. Checks code style with Ruff, Black, and Isort.
2. Audits frontend with Oxlint.
3. Runs unit/integration tests with Postgres and Redis.
