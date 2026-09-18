import { Navigate } from "react-router-dom";
import CustomDomainLandingPage from "@/pages/CustomDomainLanding";

export default function RootEntry() {
  const hostname = window.location.hostname.toLowerCase();
  const configuredAppHost = (process.env.REACT_APP_APP_HOST || "").toLowerCase();

  const isKnownAppHost =
    hostname === "localhost" ||
    hostname === "127.0.0.1" ||
    (configuredAppHost && hostname === configuredAppHost) ||
    hostname.endsWith(".onrender.com");

  return isKnownAppHost
    ? <Navigate to="/dashboard" replace />
    : <CustomDomainLandingPage />;
}
