# Milestone 7: Component Detection Agent (Agent 3)

## Status
- [x] Defined structured output contracts `DetectedComponent`, `ComponentBoundingBox`, and `ComponentInventoryResult` in `backend/vision/component_schemas.py`
- [x] Created version-controlled system prompt `backend/prompts/component_detection_v1.txt`
- [x] Implemented `ComponentDetectionAgent` in `backend/vision/component_agent.py` establishing authoritative component inventory (`comp_001`, `comp_002`, ...)
- [x] Created FastAPI endpoint route `GET /workspaces/{id}/audits/{id}/components` in `backend/vision/component_router.py`
- [x] Mounted `component_router` under `/api/v1` in `backend/main.py`
- [x] Added unit, referential integrity, and API integration tests in `backend/tests/test_component_agent.py`
- [x] Updated CHANGELOG.md and documentation

## Tasks & Deliverables

### 1. Output Schema Contract (`backend/vision/component_schemas.py`)
* **`ComponentBoundingBox`**: Bounding box geometry (`x`, `y`, `width`, `height`).
* **`DetectedComponent`**: Pydantic v2 schema returning `component_ref_id` (`comp_001`, `comp_002`, ...), `component_type` (`button`, `input`, `dropdown`, `checkbox`, `radio`, `card`, `table`, `chart`, `image`, `icon`, `sidebar`, `navbar`, `footer`, `modal`, `dialog`), `label`, `bounding_box`, `confidence`, and linked upstream text IDs (`associated_text_ids`).
* **`ComponentInventoryResult`**: Aggregated result contract containing `total_components`, `component_summary` counts by type, and `components` inventory list.

### 2. Versioned System Prompt (`backend/prompts/component_detection_v1.txt`)
* `component_detection_v1.txt`: System instructions enforcing ground-truth component detection, sequential `comp_XXX` reference IDs, bounding box boundaries, and cross-agent referential integrity checks against upstream OCR text elements.

### 3. Agent Implementation (`backend/vision/component_agent.py`)
* Vision-capable component detection engine with computer vision heuristics and deterministic fallback parser for local dev/testing environments.
* Cross-agent referential integrity: associates components with OCR text elements extracted by Agent 2 (OCR Agent).

### 4. Integration & Automated Tests (`backend/tests/test_component_agent.py`)
* Verified Agent 3 component detection lifecycle, component classification, upstream OCR cross-referencing, and HTTP GET Components API route integration.
