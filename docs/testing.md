# Testing Strategy & Guidelines

## Overview

Quality assurance across UXOps AI involves unit tests, integration tests, static code analysis, and automated CI pipeline checks.

---

## 1. Backend Testing (`/backend/tests`)

Backend tests are written using `pytest`, `pytest-asyncio`, and `httpx.AsyncClient`.

### Test Directory Layout
```text
backend/tests/
├── conftest.py            # Global Pytest fixtures (async engine, test db session, client)
├── test_auth.py           # Authentication, signup, JWT token tests
├── test_workspaces.py     # Multi-tenancy, workspace management & RBAC tests
└── test_audits.py         # Visual audit & rule engine processing tests
```

### Running Backend Tests
Ensure your virtual environment is active and run:
```bash
cd backend
pytest tests/ -v
```

To run with coverage reports:
```bash
pytest tests/ --cov=. --cov-report=term-missing --cov-report=xml
```

### Database Test Fixtures
Tests use a separate test database or dynamic database transaction rollback fixture to ensure test isolation. Environment variable during test runs:
```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/uxops_test
ENVIRONMENT=test
```

---

## 2. Frontend Testing (`/frontend`)

Frontend static checking and unit tests ensure UI reliability.

### Running Frontend Linters & Tests
```bash
cd frontend

# Run Oxlint static analysis
npm run lint

# Run type check
npx tsc --noEmit
```

---

## 3. Automated CI/CD Pipeline

Every push to `main` or `milestone-*` branches and every pull request against `main` triggers `.github/workflows/ci.yml`.

### Pipeline Jobs
1. **Lint and Format Check**:
   - Python: `ruff check backend/`, `black --check backend/`, `isort --check-only backend/`
   - Frontend: `npm run lint`
2. **Backend Tests**:
   - Spins up PostgreSQL and Redis service containers in GitHub Actions.
   - Runs `pytest` suite with coverage tracking.
3. **Frontend Verification**:
   - Verifies TypeScript compilation and frontend build artifacts.

---

## 4. Writing Good Tests

* **AAA Pattern**: Structure test functions clearly with **Arrange**, **Act**, **Assert**.
* **Edge Cases**: Test non-happy paths (e.g., unauthorized access, invalid UUIDs, expired tokens).
* **Isolation**: Tests should not rely on order of execution or persistent state from other tests.
