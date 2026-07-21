# Milestone 12: Recommendation Agent (Agent 8)

## Status
- [x] Defined structured output contracts `EnhancedRecommendation` and `RecommendationResult` in `backend/analysis/recommendation_schemas.py`
- [x] Created version-controlled system prompt `backend/prompts/recommendation_agent_v1.txt`
- [x] Implemented `RecommendationAgent` in `backend/analysis/recommendation_agent.py` to aggregate issues and prioritize recommendations
- [x] Enforced traceability so recommendations tie directly back to an upstream Agent's issue (`Issue` model referencing)
- [x] Created FastAPI endpoint route `GET /workspaces/{id}/audits/{id}/recommendations` in `backend/analysis/recommendation_router.py`
- [x] Mounted `recommendation_router` under `/api/v1` in `backend/main.py`
- [ ] Added unit, DB aggregation, and API integration tests in `backend/tests/test_recommendation_agent.py`
- [ ] Updated CHANGELOG.md and documentation

## Tasks & Deliverables

### 1. Data Contracts (Schemas)
- **File**: `backend/analysis/recommendation_schemas.py`
- **Goal**: Schemas that take a raw `Issue` and enhance it with fields like `priority` (P0-P4) and `estimated_improvement`.

### 2. Prompt & Agent Implementation
- **File**: `backend/prompts/recommendation_agent_v1.txt` and `backend/analysis/recommendation_agent.py`
- **Goal**: Implement logic that takes all database issues for a given audit and generates actionable, prioritized recommendations ensuring none are freestanding (must link to `issue_id` or `component_ref_id`).

### 3. Router Integration
- **File**: `backend/analysis/recommendation_router.py`
- **Goal**: Provide the endpoint that reads existing issues, calls the Recommendation Agent, and returns the unified recommendation set.

### 4. Tests
- **File**: `backend/tests/test_recommendation_agent.py`
- **Goal**: Validate that recommendations are accurately generated, mapped, and prioritized correctly.

## Commits
1. `feat(recommendation-agent): define schema contracts`
2. `feat(recommendation-agent): implement agent engine and prompt`
3. `feat(recommendation-agent): integrate into pipeline to aggregate DB issues`
4. `test(recommendation-agent): add schema-validation + eval-suite tests`
5. `docs(recommendation-agent): document prompt, priority methodology`
