# UXOps AI — Developer Command Reference

Quick reference for commonly used commands across build, test, lint, format, run, debug, Docker, database, and CI/CD workflows.

---

## 1. Build Commands

### Backend
```bash
# Install backend requirements locally
cd backend && pip install -r requirements.txt

# Build backend Docker image
docker build -t uxops-backend:latest ./backend
```

### Frontend
```bash
# Install frontend node modules
cd frontend && npm install

# Build production bundle (TypeScript compile + Vite build)
cd frontend && npm run build

# Preview production build locally
cd frontend && npm run preview

# Build frontend Docker image
docker build -t uxops-frontend:latest ./frontend
```

---

## 2. Test Commands

### Backend Pytest Suite
```bash
# Run all backend unit & integration tests
cd backend && pytest tests/ -v

# Run specific test file
cd backend && pytest tests/test_auth.py -v

# Run tests matching a keyword expression
cd backend && pytest tests/ -k "login or workspace"

# Run tests with coverage report
cd backend && pytest tests/ --cov=. --cov-report=term-missing --cov-report=xml
```

### Frontend Tests
```bash
# Run frontend tests (if configured)
cd frontend && npm run test
```

---

## 3. Lint Commands

### Backend Linters
```bash
# Run Ruff lint check on backend code
cd backend && ruff check .

# Fix auto-fixable Ruff issues
cd backend && ruff check --fix .

# Run Flake8 check
cd backend && flake8 .
```

### Frontend Linters
```bash
# Run Oxlint on frontend code
cd frontend && npm run lint

# Run TypeScript type check without emitting files
cd frontend && npx tsc --noEmit
```

---

## 4. Format Commands

### Python Formatting (Black & Isort)
```bash
# Format Python code with Black
black backend/

# Check Black formatting without changing files
black --check backend/

# Sort imports with Isort
isort backend/

# Check import ordering without changing files
isort --check-only backend/

# Format and sort in one command
black backend/ && isort backend/
```

### Pre-commit Hooks
```bash
# Run all pre-commit hooks manually on all files
pre-commit run --all-files
```

---

## 5. Run & Development Commands

### Full Stack via Docker Compose
```bash
# Start full application stack (build if necessary)
docker compose up --build

# Start stack in detached background mode
docker compose up -d

# Stop running stack
docker compose down

# Stop stack and remove volumes (clears local DB)
docker compose down -v
```

### Local Services Separately
```bash
# 1. Start Postgres & Redis dependencies only
docker compose up -d postgres redis

# 2. Run backend dev server with hot-reload (Port 8000)
cd backend && uvicorn main:app --reload --port 8000

# 3. Run Celery worker process
cd backend && celery -A common.celery_app worker --loglevel=info

# 4. Run frontend dev server (Port 5173)
cd frontend && npm run dev
```

### Antigravity CLI Launcher
```bash
# Launch Antigravity CLI (POSIX Bash)
./scripts/start-agy.sh

# Launch Antigravity CLI (Windows Batch)
scripts\start-agy.bat

# Launch Antigravity CLI (PowerShell)
.\scripts\start-agy.ps1
```

---

## 6. Debug Commands

### Inspection & Logs
```bash
# Stream Docker Compose logs for backend service
docker compose logs -f backend

# Stream Docker Compose logs for Celery worker
docker compose logs -f celery_worker

# Stream Docker Compose logs for frontend
docker compose logs -f frontend

# Inspect Celery active tasks
cd backend && celery -A common.celery_app inspect active

# Inspect Celery ping response
cd backend && celery -A common.celery_app inspect ping
```

---

## 7. Docker & Container Commands

```bash
# List all running UXOps containers
docker compose ps

# Rebuild specific service container without cache
docker compose build --no-cache backend

# Shell into running backend container
docker compose exec backend bash

# Shell into running postgres container
docker compose exec postgres psql -U postgres -d uxops_db
```

---

## 8. Database Commands (SQLAlchemy & Alembic)

```bash
# Apply all pending database migrations
cd backend && alembic upgrade head

# Rollback last database migration
cd backend && alembic downgrade -1

# Generate new migration after updating database models
cd backend && alembic revision --autogenerate -m "describe_changes"

# View current database revision
cd backend && alembic current

# View migration history
cd backend && alembic history
```

---

## 9. CI/CD Commands

```bash
# Simulate GitHub Actions lint checks locally
ruff check backend/ && black --check backend/ && isort --check-only backend/

# Execute full local check pre-PR submission
black backend/ && isort backend/ && ruff check backend/ && (cd backend && pytest tests/) && (cd frontend && npm run lint)
```
