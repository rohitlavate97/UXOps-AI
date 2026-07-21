# Milestone 18: Dashboard & Audits UI

## Status
- [x] Created `useAudits` hook to fetch and mutate audits
- [x] Built `Dashboard` page with metric cards and recent activity
- [x] Built `Audits` list page with a table/grid view
- [x] Built `NewAuditModal` for uploading screenshots and triggering analysis

## Tasks & Deliverables
1. **Data Hooks**: Create `src/hooks/useAudits.ts` that wraps `apiClient` calls for `GET /workspaces/{id}/audits`, `POST /workspaces/{id}/audits`, and `POST /workspaces/{id}/analyze`.
2. **Dashboard**: Implement `src/pages/dashboard/DashboardPage.tsx` using CSS modules to display mock or real metrics and recent audits.
3. **Audits List**: Implement `src/pages/audits/AuditsPage.tsx` with premium glassmorphism styling and status badges.
4. **Audit Creation**: Build a modal or dedicated page `src/components/audits/NewAuditModal.tsx` for file upload. Update `Navbar.tsx` "New Audit" button to trigger this modal.
5. **Routing**: Hook up the new pages in `App.tsx`.
