# Milestone 17: API Client & Auth State

## Status
- [x] Created `apiClient.ts` to manage API requests and token injection
- [x] Created Auth Context and `useAuth` hook for managing JWT and user state
- [x] Created Workspace Context and `useWorkspace` hook for active workspace state
- [x] Built Login and Signup Page UIs
- [x] Configured `ProtectedRoute` wrapper and updated `App.tsx` routing

## Tasks & Deliverables
1. **API Client**: Install `axios` and configure `src/api/apiClient.ts` with interceptors.
2. **Auth Context**: Define `src/contexts/AuthContext.tsx` to handle login, signup, logout, and token persistence (localStorage).
3. **Workspace Context**: Define `src/contexts/WorkspaceContext.tsx` to handle fetching the user's workspaces and setting the active one.
4. **Auth Pages**: Build `src/pages/auth/LoginPage.tsx` and `SignupPage.tsx` using custom CSS modules.
5. **App Routing**: Create `src/components/layout/ProtectedRoute.tsx` and wrap the `Layout` routes in `App.tsx`.
