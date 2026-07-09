# ADR 0002: Authentication, RBAC, and Tenant Isolation

## Status
Proposed (to be Approved with milestone merge)

## Context
UXOps AI requires secure user authentication, granular role permissions (RBAC), and strict data isolation between customer workspaces (multi-tenancy). One tenant must never access another tenant's screenshots, audit results, or workspace settings.

## Decision
1. **Stateless Authentication**: Use JSON Web Tokens (JWT) signed with HS256 for secure, stateless requests.
2. **Workspace/Tenant Model**:
   - Establish `workspaces` as the tenant boundary.
   - Map Users to Workspaces through a `workspace_members` association table.
   - Save user role permissions (`owner`, `admin`, `member`, `viewer`) inside the membership table to support workspace-specific access control.
3. **Multi-Tenant Access Enforcement**:
   - Create a reusable FastAPI dependency `WorkspaceAccess(allowed_roles)` that intercepts incoming requests, extracts the user profile from the JWT, queries their workspace membership, checks their role permissions, and blocks the request with a 403 Forbidden error if unauthorized.
   - Enforce this check on every tenant-scoped API router.

## Alternatives Considered
- **Global RBAC Roles**: Assigning roles (like User, Admin) globally on the `users` table.
  - *Pros*: Simpler schema.
  - *Cons*: Fails to support users belonging to multiple workspaces with different roles (e.g., Owner of Workspace A, but Visitor of Workspace B).
  - *Result*: Rejected.
- **Session-Based Authentication**:
  - *Pros*: Easy invalidation.
  - *Cons*: Harder to scale horizontally and integrate with webSockets.
  - *Result*: Rejected in favor of JWTs.

## Consequences
- Every tenant-scoped endpoint must explicitly request `workspace_id` in the URL path and pass it through the `WorkspaceAccess` dependency.
- Guarantees complete data privacy and security.
