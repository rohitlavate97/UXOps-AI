# Milestone 9: UI Analysis Agent (Agent 5)

## Status
- [x] Defined structured output contracts `UIAnalysisIssue`, `UIMetricResult`, and `UIAnalysisResult` in `backend/analysis/ui_analysis_schemas.py`
- [x] Created version-controlled system prompt `backend/prompts/ui_analysis_agent_v1.txt`
- [x] Implemented `UIAnalysisAgent` in `backend/analysis/ui_analysis_agent.py` checking spacing, alignment, typography, and consistency
- [x] Enforced cross-agent referential integrity mapping findings to Agent 3 component inventory (`comp_XXX`)
- [x] Created FastAPI endpoint route `GET /workspaces/{id}/audits/{id}/ui-analysis` in `backend/analysis/ui_analysis_router.py`
- [x] Mounted `ui_analysis_router` under `/api/v1` in `backend/main.py`
- [x] Added unit, referential integrity, DB persistence, and API integration tests in `backend/tests/test_ui_analysis_agent.py`
- [ ] Updated CHANGELOG.md and documentation

## Tasks & Deliverables

### 1. Output Schema Contract (`backend/analysis/ui_analysis_schemas.py`)
* **`UIAnalysisIssue`**: Pydantic v2 schema returning `issue_id` (`ui_001`, ...), `component_ref_id` (`comp_001`), `design_principle` (e.g., `Alignment`, `Spacing`, `Typography`), `category` (`UI`), `severity` (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`), `confidence`, `title`, `impact`, `recommendation`, `automated_assessment`, and `bounding_box`.
* **`UIAnalysisResult`**: Aggregated contract returning `audit_id`, `ui_score` (0-100), `total_issues`, `issues_by_severity`, and `issues` finding list.

### 2. Versioned System Prompt (`backend/prompts/ui_analysis_agent_v1.txt`)
* `ui_analysis_agent_v1.txt`: Version-controlled instructions enforcing UI design standards (spacing, alignment, typography, consistency), referencing the Component Inventory.

### 3. Agent Implementation (`backend/analysis/ui_analysis_agent.py`)
* Evaluator for UI rules.
* Cross-agent referential integrity validation against Agent 3 (`ComponentInventoryResult`).

### 4. Integration & Automated Tests (`backend/tests/test_ui_analysis_agent.py`)
* Unit tests for UI rule evaluation, referential integrity, empty payloads, DB persistence, and HTTP GET API route access.
