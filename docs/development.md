# Development Workflow & Environment Setup

## Prerequisites

Ensure you have the following installed on your development machine:
* **Python**: 3.12 or higher
* **Node.js**: v20 or higher (with npm)
* **Docker & Docker Compose**: Docker Desktop or Docker Engine v28+
* **Git**
* **Antigravity CLI** (`agy`): Recommended for pair programming with AI agents

---

## 1. Local Environment Setup

### Clone Repository
```bash
git clone https://github.com/rohitlavate97/UXOps-AI.git
cd UXOps-AI
```

### Install Pre-commit Hooks
Install `pre-commit` to automatically run linters and formatters before code is committed:
```bash
pip install pre-commit
pre-commit install
```
Test pre-commit manually:
```bash
pre-commit run --all-files
```

---

## 2. Development Execution Options

### Option A: Full Stack via Docker Compose (Recommended for Complete Environment)
To launch all services (PostgreSQL, Redis, Celery, FastAPI, React):
```bash
docker compose up --build
```
* **Frontend**: [http://localhost:5173](http://localhost:5173)
* **Backend Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

To stop the stack:
```bash
docker compose down
```

---

### Option B: Local Backend + Frontend (Recommended for Active Development)

#### 1. Start Infrastructure Services Only
Run Postgres and Redis via Docker:
```bash
docker compose up -d postgres redis
```

#### 2. Setup & Start Backend
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start development server with hot reload
uvicorn main:app --reload --port 8000
```

#### 3. Setup & Start Frontend
In a separate terminal:
```bash
cd frontend

# Install node dependencies
npm install

# Start Vite dev server
npm run dev
```

---

## 3. Database Migrations (Alembic)

Whenever you add or modify a SQLAlchemy model in `backend/database/models.py`:

1. Generate migration script:
   ```bash
   cd backend
   alembic revision --autogenerate -m "add_audit_summary_column"
   ```
2. Inspect the generated migration file in `backend/alembic/versions/`.
3. Apply migration to local database:
   ```bash
   alembic upgrade head
   ```
4. Rollback migration if needed:
   ```bash
   alembic downgrade -1
   ```

---

## 4. Working with Antigravity CLI

To launch the Antigravity CLI from the project root:

```bash
./scripts/start-agy.sh
```

Antigravity CLI ingests [`AGENTS.md`](file:///Volumes/Element/Projects/AI/UXOps-AI/AGENTS.md) on launch, ensuring all code generation aligns with project coding standards, security requirements, and architectural rules.
