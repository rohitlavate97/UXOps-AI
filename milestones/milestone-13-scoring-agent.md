# Milestone 13: Scoring Agent (Agent 9)

## Status
- [x] Defined structured output contracts `ScoreWeighting` and `ScoringResult` in `backend/analysis/scoring_schemas.py`
- [ ] Implemented deterministic `ScoringAgent` in `backend/analysis/scoring_agent.py` to calculate final `overall_score` based on UI (40%), UX (30%), A11y (20%), Design System (10%)
- [ ] Added state transition logic to mark `Audit.status = "COMPLETED"` upon successful scoring
- [ ] Created FastAPI endpoint route `GET /workspaces/{id}/audits/{id}/score` in `backend/analysis/scoring_router.py`
- [ ] Mounted `scoring_router` under `/api/v1` in `backend/main.py`
- [ ] Added unit and API integration tests in `backend/tests/test_scoring_agent.py`
- [ ] Updated CHANGELOG.md and documentation

## Tasks & Deliverables

### 1. Data Contracts (Schemas)
- **File**: `backend/analysis/scoring_schemas.py`
- **Goal**: Schemas that return the calculated overall score and the breakdown of weights used.

### 2. Agent Implementation
- **File**: `backend/analysis/scoring_agent.py`
- **Goal**: Implement deterministic logic to aggregate component scores (`ui_score`, `ux_score`, `accessibility_score`, `consistency_score`) into an `overall_score`. No LLM prompt is needed for pure deterministic math.

### 3. Router Integration
- **File**: `backend/analysis/scoring_router.py`
- **Goal**: Provide the endpoint that reads existing audit scores, calls the Scoring Agent, updates the `Audit.overall_score`, and transitions the audit `status` to `COMPLETED`.

### 4. Tests
- **File**: `backend/tests/test_scoring_agent.py`
- **Goal**: Validate math for missing vs present sub-scores, test DB updates, and API integration.

## Commits
1. `feat(scoring-agent): define schema contracts`
2. `feat(scoring-agent): implement deterministic engine and router pipeline`
3. `test(scoring-agent): add math validation + db state tests`
4. `docs(scoring-agent): document weighting methodology`
