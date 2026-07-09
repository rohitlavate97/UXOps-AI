# Milestone 2: Authentication & RBAC, Workspace/Tenant Model

## Status
- [x] Database models defined (User, Workspace, WorkspaceMember)
- [x] Pydantic DTO schemas created for Auth, Tokens, and Workspaces
- [x] Password hashing and JWT generation implemented
- [x] Dependency-injection access control (`WorkspaceAccess`) established
- [x] Alembic migration generated and applied to the database
- [x] SignUp, Login, and Workspace router endpoints operational
- [x] Test suite with 8 integration tests passing (100% success rate)
- [x] ADR 0002 and CHANGELOG updated

## Tasks & Deliverables

### 1. Database & Schema
- **SQLAlchemy Models**: Created user registration tables, workspaces, and unique-constrained workspace member associations.
- **Alembic Versioning**: Initialized migrations and migrated Postgres tables successfully.
- **Pydantic Validation**: Added strict validation schemas with custom regex checks for role levels.

### 2. JWT Security & RBAC
- **Password Safety**: Integrated `bcrypt` to hash and verify passwords.
- **FastAPI Dependency Injection**: Created `get_current_user` to authenticate JWTs, and `WorkspaceAccess(allowed_roles)` to enforce multi-tenant isolation.

### 3. API Router Endpoints
- `POST /api/v1/auth/signup`: User registration.
- `POST /api/v1/auth/login`: Form-encoded token sign-in.
- `POST /api/v1/workspaces`: Create a workspace.
- `GET /api/v1/workspaces`: List active workspaces for a user.
- `POST /api/v1/workspaces/{workspace_id}/members`: Invite members (requires Admin/Owner role).
- `GET /api/v1/workspaces/{workspace_id}/members`: List workspace members.

### 4. Verification & Testing
- Automated checks running via Pytest verify:
  - Registration validations and duplicate email rejections.
  - Token acquisition and wrong password blockages.
  - Workspace memberships and multi-tenant isolation queries (non-members get 403 Forbidden).
