# Milestone 15: Celery Pipeline Orchestration

## Status
- [x] Configured Celery application and Redis broker in `backend/common/celery_app.py`
- [x] Created `run_full_audit_pipeline` Celery task that sequentially orchestrates all 10 agents
- [x] Updated `Audit` model/schema to include granular status tracking (e.g., `VALIDATING`, `OCR_RUNNING`)
- [x] Created FastAPI `POST /analyze` endpoint in `backend/analysis/pipeline_router.py` to trigger the Celery task
- [x] Mounted `pipeline_router` under `/api/v1` in `backend/main.py`
- [x] Added unit and integration tests for the task execution in `backend/tests/test_celery_pipeline.py`
- [x] Updated CHANGELOG.md and documentation

## Tasks & Deliverables

### 1. Celery Application Setup
- **File**: `backend/common/celery_app.py`
- **Goal**: Initialize the Celery application to connect to the Redis broker, allowing for background task execution.

### 2. Pipeline Task Implementation
- **File**: `backend/analysis/tasks.py`
- **Goal**: Implement a Celery task that receives an `audit_id` and runs the 10-agent pipeline step-by-step, updating the `Audit.status` field as it progresses through each stage.

### 3. API Integration
- **File**: `backend/analysis/pipeline_router.py`
- **Goal**: Provide the endpoint that clients call to kick off a new asynchronous background audit.

### 4. Tests
- **File**: `backend/tests/test_celery_pipeline.py`
- **Goal**: Validate that the task correctly transitions the state of the audit and orchestrates the backend correctly.

## Commits
1. `feat(pipeline): configure celery application and redis broker`
2. `feat(pipeline): implement full 10-agent background orchestration task`
3. `feat(pipeline): expose async POST /analyze endpoint`
4. `test(pipeline): add unit tests for async task execution`
5. `docs(pipeline): document orchestration architecture`
