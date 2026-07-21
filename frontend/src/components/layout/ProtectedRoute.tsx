import { Navigate, Outlet } from "react-router";
import { useAuth } from "../../contexts/AuthContext";

export function ProtectedRoute() {
  const { token, isLoading } = useAuth();

  if (isLoading) {
    // Basic loading state for full-page
    return (
      <div style={{ display: 'flex', height: '100vh', alignItems: 'center', justifyContent: 'center' }}>
        <p>Loading application...</p>
      </div>
    );
  }

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}
