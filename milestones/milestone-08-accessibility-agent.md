# Milestone 8: Accessibility Agent (Agent 4)

## Status
- [x] Defined structured output contracts `AccessibilityIssue`, `ContrastAnalysisResult`, and `AccessibilityResult` in `backend/analysis/accessibility_schemas.py`
- [x] Created version-controlled system prompt `backend/prompts/accessibility_agent_v1.txt`
- [x] Implemented `AccessibilityAgent` in `backend/analysis/accessibility_agent.py` checking WCAG 2.2 contrast ratios, tap target sizes, and focus visibility
- [x] Enforced cross-agent referential integrity mapping findings to Agent 3 component inventory (`comp_XXX`)
- [x] Created FastAPI endpoint route `GET /workspaces/{id}/audits/{id}/accessibility` in `backend/analysis/accessibility_router.py`
- [x] Mounted `accessibility_router` under `/api/v1` in `backend/main.py`
- [x] Added unit, referential integrity, DB persistence, and API integration tests in `backend/tests/test_accessibility_agent.py`
- [x] Updated CHANGELOG.md and documentation

## Tasks & Deliverables

### 1. Output Schema Contract (`backend/analysis/accessibility_schemas.py`)
* **`AccessibilityIssue`**: Pydantic v2 schema returning `issue_id` (`a11y_001`, ...), `component_ref_id` (`comp_001`), `wcag_guideline` (e.g. `1.4.3 Contrast (Minimum)`, `2.5.8 Target Size`), `category` (`ACCESSIBILITY`), `severity` (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`), `confidence`, `title`, `impact`, `recommendation`, `automated_assessment=True`, and `bounding_box`.
* **`ContrastAnalysisResult`**: Detailed color contrast measurement (`foreground_hex`, `background_hex`, `contrast_ratio`, `passes_aa`, `passes_aaa`).
* **`AccessibilityResult`**: Aggregated contract returning `audit_id`, `accessibility_score` (0-100), `total_issues`, `issues_by_severity`, and `issues` finding list.

### 2. Versioned System Prompt (`backend/prompts/accessibility_agent_v1.txt`)
* `accessibility_agent_v1.txt`: Version-controlled instructions enforcing WCAG 2.2 standards, automated assessment disclaimers, component inventory reference enforcement, and confidence scoring.

### 3. Agent Implementation (`backend/analysis/accessibility_agent.py`)
* Deterministic contrast ratio calculator (L1 + 0.05 / L2 + 0.05) & touch target size validator (44x44px min).
* Cross-agent referential integrity validation against Agent 3 (`ComponentInventoryResult`).

### 4. Integration & Automated Tests (`backend/tests/test_accessibility_agent.py`)
* Unit tests for WCAG contrast calculation, tap target evaluation, empty payloads, DB persistence, and HTTP GET API route access.
