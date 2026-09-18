import "@/index.css";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { Toaster } from "sonner";

import { AuthProvider } from "@/contexts/AuthContext";
import ProtectedRoute from "@/components/ProtectedRoute";
import RequireRole from "@/components/RequireRole";
import LoginPage from "@/pages/Login";
import RegisterPage from "@/pages/Register";
import OnboardingPage from "@/pages/Onboarding";
import DashboardPage from "@/pages/Dashboard";
import CompanySettingsPage from "@/pages/CompanySettings";
import UsersPage from "@/pages/Users";
import AgendaPage from "@/pages/Agenda";
import ClientsPage from "@/pages/Clients";
import ServicesPage from "@/pages/Services";
import AvailabilityPage from "@/pages/Availability";
import LandingBuilderPage from "@/pages/LandingBuilder";
import PublicLandingPage from "@/pages/PublicLanding";
import PublicBookingPage from "@/pages/PublicBooking";
import RootEntry from "@/pages/RootEntry";

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Toaster richColors position="top-right"/>
        <Routes>
          <Route path="/" element={<RootEntry />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          <Route element={<ProtectedRoute />}>
            <Route path="/onboarding" element={<OnboardingPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/agenda" element={<AgendaPage />} />
            <Route path="/clients" element={<ClientsPage />} />
            <Route path="/services" element={<RequireRole roles={["OWNER","MANAGER"]}><ServicesPage/></RequireRole>} />
            <Route path="/availability" element={<RequireRole roles={["OWNER","MANAGER"]}><AvailabilityPage/></RequireRole>} />
            <Route path="/landing" element={<RequireRole roles={["OWNER","MANAGER"]}><LandingBuilderPage/></RequireRole>} />
            <Route path="/settings/company" element={<RequireRole roles={["OWNER","MANAGER"]}><CompanySettingsPage/></RequireRole>} />
            <Route path="/settings/users" element={<RequireRole roles={["OWNER","MANAGER"]}><UsersPage/></RequireRole>} />
          </Route>

          <Route path="/:slug" element={<PublicLandingPage />} />
          <Route path="/:slug/agendar" element={<PublicBookingPage />} />

          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
export default App;
