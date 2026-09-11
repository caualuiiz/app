import { Navigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";

export default function RequireRole({ roles, children }) {
  const { role, status } = useAuth();
  if (status !== "authenticated") return null;
  if (!role || !roles.includes(role)) {
    return <Navigate to="/dashboard" replace />;
  }
  return children;
}
