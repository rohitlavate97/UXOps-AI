# Milestone 19: Detailed Audit Report UI

## Status
- [x] Added `fetchAuditDetails` to `useAudits.ts` hook
- [x] Built `ImageViewer.tsx` for rendering uploaded screenshots with dynamic SVG bounding boxes
- [x] Built `AuditReportPage.tsx` with scorecards and grouped finding lists
- [x] Updated `App.tsx` router to handle `/audits/:auditId`

## Tasks & Deliverables
1. **API Integration**: Extend the data fetching hooks to call `GET /workspaces/{id}/audits/{audit_id}` and retrieve the `findings` list.
2. **ImageViewer**: Build `src/components/audits/ImageViewer.tsx`. It should render the S3 image and overlay SVG boxes based on coordinates returned in findings.
3. **Report Page**: Create `src/pages/audits/AuditReportPage.tsx`. Split the view: left side for the image viewer, right side for the scorecards and categorized findings (UI, UX, A11y, etc.).
4. **Router & Navigation**: Add `<Route path="/audits/:auditId" element={<AuditReportPage />} />` to `App.tsx`. Update the "View Report" button in `AuditsPage.tsx` to link to it.
