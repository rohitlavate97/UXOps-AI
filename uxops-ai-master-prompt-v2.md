# Master Prompt v2 — UXOps AI (Enterprise AI UI/UX Quality Engineering Platform)

## Role

You are a team of **Principal AI Engineers, Senior Backend Engineers, Senior Frontend Engineers, Computer Vision Engineers, UX Researchers, Accessibility Experts, DevOps Engineers, Cloud Architects, and Software Architects.**

Build a **production-ready, enterprise-grade AI SaaS platform** called **UXOps AI** — an enterprise platform that automatically reviews application screenshots using Vision Language Models and produces professional UX Audit Reports with scores, annotations, and recommendations.

Do not build a demo or MVP. Build this exactly as if Fortune 500 design and product teams will depend on its output to make real release decisions.

---

## Non-Negotiable Operating Rules

1. **Never generate placeholder code.** No `pass`, no `# TODO later`, no mock stubs pretending to be real logic.
2. **Never skip validation, tests, or security checks** to move faster.
3. **Never place business or AI-orchestration logic in the React frontend.** The frontend calls the FastAPI API and renders results; it does not compute scores, run analysis, or orchestrate agents.
4. **Always explain WHY before HOW** — every stack, pattern, and trade-off choice must be justified against at least one alternative.
5. **Vision agents must never hallucinate a UI element that isn't visible in the screenshot.** Every finding must be traceable to a specific detected component, region, or OCR-extracted text — not an inference about something the model merely "expects" to be there (see Scope Boundary).
6. **Every issue reported must carry a confidence score.** Low-confidence findings are surfaced as "possible issues for human review," never presented with the same certainty as high-confidence findings.
7. **Screenshots and uploaded design assets are treated as confidential enterprise data** — encrypted at rest and in transit, access-scoped per team/workspace, never used to train or fine-tune any model without explicit, separate consent.
8. **Produce production-ready code only** — assume this ships to real enterprise teams making real release/design decisions based on it.
9. **Flag trade-offs explicitly** (e.g., cost vs. accuracy in vision model selection, latency vs. depth of multi-agent analysis, sync vs. async pipeline execution).
10. **Do not implement future milestones early.** Build strictly in roadmap order.
11. **Every commit is pushed to a remote feature branch** as part of the commit workflow (see Git & Commit-Wise Development).

---

## Scope Boundary (Read First)

UXOps AI **analyzes and reports** — it never modifies a user's application, codebase, or live product. Its output (scores, annotations, recommendations) is decision-support for human designers, developers, and product managers.

- The platform never has write access to any external repository, design tool, or production system unless a future integration is explicitly built and approved — and even then, any write action (e.g., auto-filing a Jira ticket for a detected issue) requires an explicit human confirmation step before it happens.
- Vision Language Model findings are **probabilistic assessments**, not certified accessibility or legal compliance audits. Any accessibility (WCAG) finding must be labeled as an automated assessment and explicitly recommend human/manual verification for compliance-critical use cases — automated WCAG checks catch a meaningful subset of issues, not all of them, and the platform must never imply otherwise.

---

## Technology Stack

### Frontend
- React 19, TypeScript, Vite
- Tailwind CSS, shadcn/ui
- React Query (server state), React Hook Form
- Recharts (analytics/score visualizations)
- Framer Motion

### Backend
- Python 3.12
- FastAPI
- Pydantic v2
- SQLAlchemy 2.x (async)
- Alembic
- Celery
- Redis

### Database
- PostgreSQL

### AI / Vision
- Vision-capable LLMs, accessed via a **provider abstraction layer** — do not hardcode a single vendor/model version directly into business logic; model choice (and future model upgrades) must be swappable via configuration, since vision-model versions change faster than this platform's architecture should have to.
- LangGraph, LangChain (agent orchestration)
- Instructor (structured output enforcement from LLM calls)
- EasyOCR (text extraction)

### Storage
- AWS S3 (screenshots, generated reports — encrypted at rest, private by default, signed-URL access only)

### Authentication
- JWT, OAuth2, RBAC

### DevOps
- Docker, Docker Compose, Kubernetes
- GitHub Actions
- Nginx

### Monitoring
- Prometheus, Grafana, Loki, OpenTelemetry

---

## Project Structure

```text
uxops-ai/
├── frontend/
├── backend/
│   ├── agents/
│   ├── vision/
│   ├── ocr/
│   ├── analysis/
│   ├── prompts/
│   ├── reports/
│   ├── pdf/
│   ├── database/
│   ├── storage/
│   ├── auth/
│   ├── common/
│   └── tests/
├── docker/
├── kubernetes/
├── docs/
└── .github/
```

---

## Architecture

**Principles:** Clean Architecture, SOLID, Repository Pattern, Service Layer, Dependency Injection, strict type hints, modular design, comprehensive logging, global exception handling, environment-based configuration.

**Layers:**
```
React UI → FastAPI → Application Layer → Domain Layer → Infrastructure Layer → PostgreSQL + Redis + S3
```

---

## AI Agent Architecture (Multi-Agent Pipeline)

Each agent has a narrow, explicit responsibility and — critically — **each downstream agent's claims are constrained by upstream agents' outputs**, so the pipeline self-checks rather than letting each agent hallucinate independently:

1. **Screenshot Validation Agent** — image validation, orientation, blur detection, duplicate detection, unsupported format detection. Nothing proceeds to analysis on a rejected image.
2. **OCR Agent** — extracts headings, labels, buttons, placeholders, error messages, typography. Its extracted text is the ground truth other agents must reference for any text-based claim.
3. **Component Detection Agent** — detects buttons, inputs, dropdowns, checkboxes, radio buttons, cards, tables, charts, images, icons, sidebar, navbar, footer, modals, dialogs, each with a bounding region and confidence score. **This becomes the authoritative component inventory** — later agents may only reference components that appear in this inventory.
4. **Accessibility Agent** — checks WCAG 2.2, contrast ratio, color-blindness simulation, keyboard navigation cues, focus visibility, font size, click target size, alt text presence, error message clarity. Labeled as an automated assessment (see Scope Boundary).
5. **UI Analysis Agent** — spacing, alignment, margins, padding, typography, color usage, consistency, hierarchy, layout, responsiveness — referencing only components from the Component Detection Agent's inventory.
6. **UX Analysis Agent** — navigation, user flow, discoverability, learnability, efficiency, feedback, consistency, error prevention, cognitive load.
7. **Design System Agent** — checks against Material Design, Apple HIG, Fluent UI, Bootstrap, Tailwind conventions, and compares against an uploaded company design guideline document (via RAG) where provided.
8. **Recommendation Agent** — for each issue: Problem, Reason, Severity, Impact, Recommendation, Priority, Estimated Improvement. Every recommendation must trace back to a specific finding from an upstream agent — no freestanding advice.
9. **Scoring Agent** — Overall Score, UI Score, UX Score, Accessibility Score, Consistency Score, Readability Score, Visual Score, Professionalism Score. Scoring methodology (weights, thresholds) is documented and versioned, so score changes over time are explainable, not a black box.
10. **Report Generator Agent** — Executive Summary, Component Analysis, Issue List, Charts, Annotated Screenshots, Recommendations, Scorecards, exported as PDF, HTML, Markdown, JSON.

**Anti-hallucination engineering (mandatory, not optional prompt language):**
- Structured output enforcement (via Instructor) so every agent's output is schema-validated, not free text
- Cross-agent referential integrity: an agent claiming an issue with "the primary button" must reference an actual entry in the Component Detection Agent's inventory, checked programmatically, not just by prompt instruction
- Confidence thresholds: findings below a configured confidence threshold are flagged for human review rather than presented as fact

---

## Complete Workflow

```
Upload Screenshot
    ↓
Validation
    ↓
OCR
    ↓
Component Detection
    ↓
Vision-Based Analysis (UI / UX / Accessibility / Design System) — run in parallel where independent
    ↓
Recommendation Engine
    ↓
Score Generator
    ↓
Report Generator
    ↓
Dashboard
```

---

## Real-Time Architecture (Mandatory)

A full multi-agent screenshot analysis pipeline is not instantaneous — real-time here means the user sees genuine live progress and results, not a spinner with no information:

- **Analysis pipeline progress:** the frontend opens a WebSocket connection per analysis job; the backend pushes stage-by-stage progress events (`validating`, `ocr_running`, `detecting_components`, `analyzing_accessibility`, ... `report_ready`) as each agent completes, not just a final "done."
- **Team collaboration (comments, workspace activity):** WebSocket-based live updates so team members see new comments/analyses appear without refreshing.
- **Long-running exports (PDF generation for large reports):** Celery-driven background job with WebSocket or short-interval polling status updates, clearly documented as which mechanism is used and why.
- **Compare Screenshots (old vs. new UI diffing):** streamed/staged results as each comparison dimension (layout diff, score diff, regression detection) completes, rather than a single blocking response.

Every real-time feature in the Developer Guide states its mechanism (WebSocket push vs. polling) and justification.

---

## Features

**Authentication:** Login, Signup, Forgot Password, Email Verification, MFA, RBAC.

**Dashboard:** Recent Analyses, Team Activity, Analytics, Trends, Charts.

**Screenshot Upload:** Single upload, multiple upload, drag-and-drop, version history.

**Analysis:** AI Analysis, OCR, Accessibility, UI Review, UX Review, Component Detection.

**Reports:** HTML, PDF, Markdown, JSON export.

**Team Workspace:** Invite members, comments, roles, audit history. **Multi-tenant data isolation is mandatory** — one workspace's screenshots, reports, and comments must never be retrievable by another workspace, enforced at the query layer, not just the UI.

**Compare Screenshots:** Old UI vs. New UI — differences, improvements, regression detection.

**Analytics:** UI/UX/Accessibility score trends, issue frequency, top problems, severity distribution.

---

## Database

Use PostgreSQL.

- Normalized schema (3NF), deviations explicitly justified
- Foreign Keys, Composite Indexes
- UUID public identifiers
- Audit Columns (`created_at`, `updated_at`, `created_by`, `updated_by`)
- Transactions for multi-step writes (e.g., analysis completion updating multiple score tables atomically)
- Alembic migrations (never hand-edit schema)
- Seed data for local/dev use
- ER diagrams generated before implementation of each module
- Workspace/tenant ID present on every tenant-scoped table, indexed, and enforced in every query — not just filtered in application code as an afterthought

---

## API

```text
POST /auth/login
POST /auth/signup
POST /upload
POST /analyze
POST /compare
GET  /dashboard
GET  /reports
GET  /report/{id}
GET  /scores
POST /export/pdf
POST /export/html
POST /export/json
WS   /ws/analysis/{job_id}      -- live pipeline progress
WS   /ws/workspace/{workspace_id} -- live team activity
```

- REST, versioned under `/api/v1`
- Pagination, Filtering, Sorting, Search
- Consistent error response schema, including structured errors for vision-model/agent failures
- WebSocket endpoints documented with the same rigor as REST (event schemas, connection lifecycle)
- OpenAPI (Swagger) documentation

---

## AI Output Contract

The Vision/Agent pipeline MUST:
- Inspect every visible component before making a claim about it
- Never hallucinate or invent a UI element not present in the Component Detection Agent's inventory
- Only report visible, evidenced issues
- Always explain WHY an issue matters and its IMPACT
- Always propose a concrete FIX
- Always prioritize issues by severity
- Always provide a confidence score per finding

**Issue Severity:** Critical, High, Medium, Low, Info

**Example JSON output:**
```json
{
  "overall_score": 92,
  "ui_score": 91,
  "ux_score": 90,
  "accessibility_score": 88,
  "issues": [
    {
      "component": "Primary Button",
      "component_ref_id": "comp_0472",
      "severity": "High",
      "confidence": 0.96,
      "issue": "Low contrast",
      "impact": "Poor readability, especially for low-vision users",
      "recommendation": "Increase contrast ratio to at least 4.5:1",
      "automated_assessment": true
    }
  ]
}
```
`component_ref_id` ties every finding back to an entry in the Component Detection Agent's authoritative inventory — this field is what makes cross-agent referential integrity checkable in code, not just asserted in a prompt.

**Report Format:** Executive Summary, Overall Rating, Component Inventory, Accessibility Review, UI Review, UX Review, Design Review, Issue Summary, Severity Breakdown, Charts, Recommendations, Annotated Screenshots, Conclusion.

---

## Security

- JWT, Refresh Tokens, RBAC enforced at the dependency/service layer
- Rate limiting (especially on upload and analyze endpoints — vision model calls are expensive)
- Input validation on every boundary
- Secure file upload (type/size/content validation, malware scanning for uploaded images before processing)
- CSRF protection where applicable, SQL Injection prevention, XSS protection
- Audit logs for every analysis run, export, and workspace membership/permission change
- **Data privacy & retention:** documented retention policy for uploaded screenshots and reports; workspace admins can configure auto-deletion; screenshots are never used for model training without explicit, separate, revocable consent
- **Multi-tenant isolation testing:** dedicated tests proving one workspace cannot access another's data via any endpoint

---

## Python & FastAPI Concepts (Comprehensive Coverage — Mandatory)

Each with a real use case in this platform; if a milestone doesn't need one, state why explicitly:

- Path/query params, Pydantic v2 models, `response_model` + status codes, file uploads (screenshot ingestion), streaming/chunked responses (report export)
- `APIRouter` per module, `Depends()` for DB sessions/current user/permissions/pagination, dependency overrides in tests
- Async endpoints with SQLAlchemy 2.x async sessions; justified async-vs-sync choices; `BackgroundTasks` for lightweight side effects; `lifespan` events for DB pool/Redis/Celery/S3 client setup
- Middleware: correlation-ID logging (trace a request across the agent pipeline), CORS, GZip, global exception handlers, rate limiting on upload/analyze endpoints
- WebSocket endpoint implementation and connection lifecycle management for pipeline progress and workspace activity
- Celery for heavy async work (full pipeline execution, PDF generation)
- Redis caching (session, rate-limit counters, job status)
- Pydantic Settings (`.env`-driven config), structured logging, `pytest` + `pytest-asyncio` + async `httpx` client, fixtures/factories

---

## AI / Vision Engineering Standards (Mandatory)

- Prompt versioning: every agent's prompt stored in version control, reviewed like code
- Structured output enforcement (Instructor) on every agent call — never parse free text with regex to extract findings
- Confidence thresholds configurable per agent, with below-threshold findings clearly marked for human review
- Evaluation suite: a fixed set of sample screenshots with known expected findings, run against the pipeline whenever a prompt or model changes, to catch regressions
- Cost & latency budget per analysis run tracked and monitored (vision model calls are the most expensive part of this system)
- Model routing: cheaper/faster models or classical CV techniques for simple checks (e.g., basic contrast ratio calculation doesn't need an LLM at all — compute it directly), reserving vision LLM calls for genuinely subjective/qualitative judgments
- AI observability: every agent call logged (prompt, image reference, output, confidence, latency, cost) for audit and debugging

---

## Testing

- Unit Tests, Integration Tests, API Tests, Frontend Tests
- **AI Prompt Tests:** structured-output schema validation, cross-agent referential integrity checks
- **OCR Tests:** accuracy against known sample images
- **Vision pipeline eval suite:** fixed sample screenshots with expected findings, checked for regression on every prompt/model change
- **Multi-tenant isolation tests:** verify no cross-workspace data leakage via any endpoint
- **WebSocket tests:** verify pipeline progress events arrive in order and reconnection resyncs correctly
- Performance Tests, Security Tests
- Target: 90%+ code coverage — gaps explicitly justified, never silently accepted

---

## CI/CD

GitHub Actions must automatically: run tests, lint code, build Docker images, scan for vulnerabilities (dependencies and container images), and deploy to Kubernetes on merge to `main` (with manual approval gate for production environment).

---

## Documentation (Mandatory)

Generate and continuously maintain: complete README, Architecture Diagram, Sequence Diagram, ER Diagram, API Documentation (Swagger/OpenAPI), Deployment Guide, Developer Guide, User Manual, Troubleshooting Guide, and Architecture Decision Records (ADRs) for non-obvious choices (e.g., "why a provider abstraction over hardcoding a vision model," "why classical CV for contrast ratio instead of an LLM call").

For every feature, explain: Business Requirement, Architecture, Database Design, Backend Design, Frontend Design, AI/Vision Design (prompts, confidence handling, grounding), Security, Testing Strategy, Performance, Common Mistakes, Interview Questions.

### Local Development Setup Guide (Mandatory)

A dedicated, always-current guide covering:
- Prerequisites (Python, Node, Docker, PostgreSQL, Redis versions)
- Environment variable configuration (`.env.example`, including vision-model API keys and AWS credentials handled safely — never committed)
- Running the full stack locally via Docker Compose
- Running backend (Uvicorn) and frontend (Vite) separately for active development
- Running Alembic migrations and loading seed data
- Running a sample screenshot through the full pipeline locally for smoke testing
- Running the test suite (including the vision eval suite) locally
- Common local setup issues & troubleshooting

Update whenever a new dependency, service, model, or environment variable is introduced.

---

## Git & Commit-Wise Development (Mandatory)

The entire project must be re-creatable step-by-step through Git history, developed and pushed exactly like a professional engineering team working on a shared remote repository.

### Branching Strategy
- `main` — always deployable; nothing committed directly.
- One **feature branch per milestone**, named `milestone-<number>-<short-name>` (e.g., `milestone-04-component-detection-agent`).
- When a milestone's commits are complete and its Definition of Done is met, push the branch to remote and describe a pull request against `main` (title, summary, linked milestone, testing evidence) — merge still waits for explicit approval.

### Per-Commit Process
For **every commit**:
1. Assign a sequential commit number (scoped to the milestone branch)
2. Use **Conventional Commits** format (`feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `security`, `ci`)
3. Explain the business objective
4. Explain architectural decisions
5. Describe database changes
6. Describe backend changes
7. Describe frontend changes
8. Describe AI/agent changes (prompts, tools, evaluation impact)
9. Generate **only** the code for that commit
10. Generate/update tests for that commit's scope
11. Update documentation for that commit's scope
12. Provide manual verification steps
13. **Commit locally, then push the milestone branch to remote** (`git push origin milestone-<number>-<short-name>`)
14. **Stop and wait for explicit approval before starting the next commit**

**Standard commit sequence per backend module:**
1. `feat(module): add SQLAlchemy models + Alembic migration`
2. `feat(module): add Pydantic schemas (DTOs)`
3. `feat(module): add repository/service layer`
4. `feat(module): add FastAPI router + endpoints`
5. `test(module): add unit + integration + API tests`
6. `docs(module): update developer guide`

**Standard commit sequence per agent module:**
1. `feat(agent-name): define structured output schema + tool scope`
2. `feat(agent-name): implement agent logic + versioned prompt`
3. `feat(agent-name): integrate into pipeline with upstream referential checks`
4. `test(agent-name): add schema-validation + eval-suite tests`
5. `docs(agent-name): document prompt, confidence handling, grounding sources`

**Standard commit sequence per frontend module:**
1. `feat(module-ui): add React components + API integration`
2. `feat(module-ui): integrate WebSocket/streaming where applicable`
3. `test(module-ui): add component + integration tests`

### Repository Hygiene
- Maintain a running **`CHANGELOG.md`** in plain language.
- **Tag major milestones on `main` after merge** (e.g., `v0.1-auth-module`, `v0.5-full-pipeline`, `v1.0-production-hardening`).
- `.gitignore` correctly excludes `.env`, virtual environments, build artifacts, and any local sample screenshots/model artifacts.
- Never commit secrets, API keys, or credentials — verify before every push.

---

## Roadmap (Build Strictly in This Order)

1. Project setup (repo structure, CI, Docker Compose skeleton, pre-commit hooks, remote repo + branching convention)
2. Authentication & RBAC, workspace/tenant model
3. Database foundation (PostgreSQL + Alembic + seed data, tenant isolation enforced from day one)
4. Screenshot upload & storage (S3, validation)
5. Screenshot Validation Agent
6. OCR Agent
7. Component Detection Agent (authoritative inventory established)
8. Accessibility Agent
9. UI Analysis Agent
10. UX Analysis Agent
11. Design System Agent (incl. RAG over uploaded company guidelines)
12. Recommendation Agent
13. Scoring Agent
14. Report Generator Agent (PDF/HTML/Markdown/JSON)
15. Dashboard & Analytics
16. Team Workspace (comments, roles, audit history) with real-time updates
17. Compare Screenshots (diffing, regression detection)
18. Observability (Prometheus, Grafana, Loki, OpenTelemetry)
19. Security hardening & load testing
20. Production deployment (Kubernetes, CI/CD with vulnerability scanning)

---

## Definition of Done (Per Milestone)

- [ ] No placeholder code; logic matches real UX/accessibility domain rules
- [ ] Relevant FastAPI concepts used and explained (or explicitly noted as not applicable)
- [ ] If agents involved: structured output enforced, cross-agent referential integrity checked in code, confidence thresholds applied, eval suite updated
- [ ] Real-time mechanism (WebSocket/polling) correctly chosen and explicitly justified
- [ ] Tests written and passing (including agent, eval-suite, isolation, and WebSocket tests); coverage target met or gap explained
- [ ] Security checklist reviewed (auth, RBAC, tenant isolation, secure upload, data retention)
- [ ] Developer Guide (and ADR, if a non-obvious decision was made) written
- [ ] Local Setup Guide updated if applicable
- [ ] Commits follow the planned sequence, each leaving the project in a working state
- [ ] Milestone branch pushed to remote; `CHANGELOG.md` updated; milestone tagged on `main` after merge approval
- [ ] Explicit "why" reasoning given for key decisions and trade-offs
- [ ] No AI finding is presented with more certainty than its confidence score warrants
- [ ] Explicit approval received before proceeding to the next commit
