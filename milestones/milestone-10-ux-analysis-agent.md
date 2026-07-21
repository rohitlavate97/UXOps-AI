# Milestone 10: UX Analysis Agent (Agent 6)

## Status
- [x] Defined structured output contracts `UXAnalysisIssue`, `UXMetricResult`, and `UXAnalysisResult` in `backend/analysis/ux_analysis_schemas.py`
- [x] Created version-controlled system prompt `backend/prompts/ux_analysis_agent_v1.txt`
- [x] Implemented `UXAnalysisAgent` in `backend/analysis/ux_analysis_agent.py` checking navigation, discoverability, learnability, and feedback
- [x] Enforced cross-agent referential integrity mapping findings to Agent 3 component inventory (`comp_XXX`)
- [ ] Created FastAPI endpoint route `GET /workspaces/{id}/audits/{id}/ux-analysis` in `backend/analysis/ux_analysis_router.py`
- [ ] Mounted `ux_analysis_router` under `/api/v1` in `backend/main.py`
- [ ] Added unit, referential integrity, DB persistence, and API integration tests in `backend/tests/test_ux_analysis_agent.py`
- [ ] Updated CHANGELOG.md and documentation

## Tasks & Deliverables

### 1. Output Schema Contract (`backend/analysis/ux_analysis_schemas.py`)
* **`UXAnalysisIssue`**: Pydantic v2 schema returning `issue_id` (`ux_001`, ...), `component_ref_id` (`comp_001`), `ux_heuristic` (e.g., `Discoverability`, `Feedback`, `Cognitive Load`), `category` (`UX`), `severity` (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`), `confidence`, `title`, `impact`, `recommendation`, `automated_assessment`, and `bounding_box`.
* **`UXAnalysisResult`**: Aggregated contract returning `audit_id`, `ux_score` (0-100), `total_issues`, `issues_by_severity`, and `issues` finding list.

### 2. Versioned System Prompt (`backend/prompts/ux_analysis_agent_v1.txt`)
* `ux_analysis_agent_v1.txt`: Version-controlled instructions enforcing UX heuristics (navigation, user flow, discoverability, learnability, efficiency, feedback, consistency, error prevention, cognitive load), referencing the Component Inventory.

### 3. Agent Implementation (`backend/analysis/ux_analysis_agent.py`)
* Evaluator for UX heuristic rules.
* Cross-agent referential integrity validation against Agent 3 (`ComponentInventoryResult`).

### 4. Integration & Automated Tests (`backend/tests/test_ux_analysis_agent.py`)
* Unit tests for UX rule evaluation, referential integrity, empty payloads, DB persistence, and HTTP GET API route access.
