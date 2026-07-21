# Milestone 11: Design System Agent (Agent 7)

## Status
- [x] Defined structured output contracts `DesignSystemIssue`, `DesignMetricResult`, and `DesignSystemResult` in `backend/analysis/design_system_schemas.py`
- [x] Created version-controlled system prompt `backend/prompts/design_system_agent_v1.txt`
- [x] Implemented `DesignSystemAgent` in `backend/analysis/design_system_agent.py` checking design systems (Material Design, Apple HIG, Tailwind) and RAG design guidelines
- [x] Enforced cross-agent referential integrity mapping findings to Agent 3 component inventory (`comp_XXX`)
- [x] Created FastAPI endpoint route `GET /workspaces/{id}/audits/{id}/design-system` in `backend/analysis/design_system_router.py`
- [x] Mounted `design_system_router` under `/api/v1` in `backend/main.py`
- [x] Added unit, referential integrity, DB persistence, and API integration tests in `backend/tests/test_design_system_agent.py`
- [ ] Updated CHANGELOG.md and documentation

## Tasks & Deliverables

### 1. Data Contracts (Schemas)
- **File**: `backend/analysis/design_system_schemas.py`
- **Goal**: Pydantic v2 schemas defining a list of `DesignSystemIssue`. Includes severity, category (`DESIGN_SYSTEM`), component reference ID, and RAG references.

### 2. Prompt & Agent Implementation
- **File**: `backend/prompts/design_system_agent_v1.txt` and `backend/analysis/design_system_agent.py`
- **Goal**: Implement deterministic check evaluating standard design systems (Material, HIG) and RAG (DesignGuideline) matching against component inventory.

### 3. Router Integration
- **File**: `backend/analysis/design_system_router.py`
- **Goal**: Expose a `GET` endpoint ensuring dependencies and storing `Issue` instances. Include loading `DesignGuideline` embeddings to pass as context (or mocked context for now).

### 4. Tests
- **File**: `backend/tests/test_design_system_agent.py`
- **Goal**: Test valid payload, empty payload, and endpoint authorization/persistence, validating design system compliance logic.

## Commits
1. `feat(design-system-agent): define schema contracts`
2. `feat(design-system-agent): implement agent engine and prompt`
3. `feat(design-system-agent): integrate into pipeline with RAG guidelines`
4. `test(design-system-agent): add schema-validation + eval-suite tests`
5. `docs(design-system-agent): document prompt, score methodology`
