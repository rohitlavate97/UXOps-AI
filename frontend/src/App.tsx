import { Routes, Route } from "react-router";
import { Layout } from "./components/layout/Layout";

// Temporary placeholder pages
const Dashboard = () => <div><h1>Dashboard</h1><p>Welcome to UXOps AI</p></div>;
const Audits = () => <div><h1>Audits</h1><p>Your recent design audits</p></div>;
const Reports = () => <div><h1>Reports</h1><p>Generated PDF and HTML reports</p></div>;
const Activity = () => <div><h1>Activity</h1><p>System and user activity logs</p></div>;
const Settings = () => <div><h1>Settings</h1><p>Workspace and user settings</p></div>;

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/audits" element={<Audits />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/activity" element={<Activity />} />
        <Route path="/settings" element={<Settings />} />
      </Route>
    </Routes>
  );
}

export default App;
