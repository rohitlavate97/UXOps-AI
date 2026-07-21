import { Routes, Route } from "react-router";
import { Layout } from "./components/layout/Layout";
import { ProtectedRoute } from "./components/layout/ProtectedRoute";
import { LoginPage } from "./pages/auth/LoginPage";
import { SignupPage } from "./pages/auth/SignupPage";
import { DashboardPage } from "./pages/dashboard/DashboardPage";
import { AuditsPage } from "./pages/audits/AuditsPage";
import { AuditReportPage } from "./pages/audits/AuditReportPage";

// Temporary placeholder pages
const Reports = () => <div><h1>Reports</h1><p>Generated PDF and HTML reports</p></div>;
const Activity = () => <div><h1>Activity</h1><p>System and user activity logs</p></div>;
const Settings = () => <div><h1>Settings</h1><p>Workspace and user settings</p></div>;

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />
      
      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/audits" element={<AuditsPage />} />
          <Route path="/audits/:auditId" element={<AuditReportPage />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/activity" element={<Activity />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      </Route>
    </Routes>
  );
}

export default App;
