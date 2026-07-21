# Milestone 14: Report Generation Agent (Agent 10)

## Status
- [x] Added `Jinja2` and `reportlab` dependencies to `backend/requirements.txt`
- [x] Defined structured output contracts `ReportFormat` and `ReportResult` in `backend/reports/report_schemas.py`
- [x] Created Jinja2 templates (Markdown and HTML) for audit reports in `backend/reports/templates/`
- [x] Implemented `ReportGenerationAgent` in `backend/reports/report_agent.py` to aggregate Audit, Issues, and Scores into formatted documents
- [x] Created FastAPI endpoint route `GET /workspaces/{id}/audits/{id}/report` in `backend/reports/report_router.py`
- [x] Mounted `report_router` under `/api/v1` in `backend/main.py`
- [x] Added unit and formatting validation tests in `backend/tests/test_report_agent.py`
- [x] Updated CHANGELOG.md and documentation

## Tasks & Deliverables

### 1. Data Contracts & Dependencies
- **File**: `backend/requirements.txt`, `backend/reports/report_schemas.py`
- **Goal**: Schemas that define the payload of the generated report (e.g. `download_url`, `content`, `format`), and required template rendering tools.

### 2. Templates
- **File**: `backend/reports/templates/report.md.j2`, `backend/reports/templates/report.html.j2`
- **Goal**: Clean, brand-compliant layout showing the audit overall score, category breakdown, prioritized recommendations, and components.

### 3. Agent Implementation
- **File**: `backend/reports/report_agent.py`
- **Goal**: Read the Audit, its associated Issues, and the final scoring from the database. Pass these as context into Jinja2 to render the final report, optionally exporting as PDF using ReportLab.

### 4. Router Integration
- **File**: `backend/reports/report_router.py`
- **Goal**: Provide the endpoint `GET .../report?format=pdf` to return the generated report to the frontend or user.

### 5. Tests
- **File**: `backend/tests/test_report_agent.py`
- **Goal**: Verify Jinja2 template rendering succeeds given mock DB data, and API returns correct formats.

## Commits
1. `feat(report-agent): define schemas and add templating dependencies`
2. `feat(report-agent): create jinja templates and formatting engine`
3. `feat(report-agent): integrate router for pdf/markdown downloads`
4. `test(report-agent): add template rendering and router tests`
5. `docs(report-agent): document report generation architecture`
