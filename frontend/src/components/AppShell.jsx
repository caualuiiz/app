import { useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import {
  Calendar,
  ChevronDown,
  Clock,
  DollarSign,
  LayoutDashboard,
  LogOut,
  Menu,
  Scissors,
  Settings,
  Sparkles,
  Users,
  UserCog,
  X,
} from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { ROLE_LABELS, businessTypeLabel } from "@/lib/api";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import FloatingAssistant from "@/components/FloatingAssistant";

const NAV = [
  { to: "/dashboard", label: "Painel", icon: LayoutDashboard, testId: "nav-dashboard" },
  { to: "/agenda", label: "Agenda", icon: Calendar, testId: "nav-agenda" },
  { to: "/clients", label: "Clientes", icon: Users, testId: "nav-clients" },
  { to: "/services", label: "Serviços", icon: Scissors, testId: "nav-services", roles: ["OWNER", "MANAGER"] },
  { to: "/availability", label: "Disponibilidade", icon: Clock, testId: "nav-availability", roles: ["OWNER", "MANAGER"] },
  { to: "/landing", label: "Minha Landing", icon: Sparkles, testId: "nav-landing", roles: ["OWNER", "MANAGER"] },
  { to: "/settings/company", label: "Empresa", icon: Settings, testId: "nav-company", roles: ["OWNER", "MANAGER"] },
  { to: "/settings/users", label: "Membros", icon: UserCog, testId: "nav-users", roles: ["OWNER", "MANAGER"] },
  { to: "/settings/commercial", label: "Comercial", icon: DollarSign, testId: "nav-commercial", roles: ["OWNER"] },
];

const COMING_SOON = [
  { label: "Financeiro", icon: DollarSign },
];

function Initials({ name }) {
  const initials = (name || "?")
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((n) => n[0]?.toUpperCase() || "")
    .join("");
  return <AvatarFallback className="bg-indigo-600 text-white text-sm">{initials}</AvatarFallback>;
}

function SidebarContent({ role, company, onNavigate }) {
  return (
    <div className="flex h-full flex-col bg-slate-900 text-slate-100">
      <div className="flex items-center gap-3 px-6 py-5 border-b border-slate-800">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-600 text-white font-bold">
          G
        </div>
        <div>
          <p className="font-bold tracking-tight" style={{ fontFamily: "'Plus Jakarta Sans'" }}>
            Gestão
          </p>
          <p className="text-[11px] uppercase tracking-widest text-slate-400">
            SaaS
          </p>
        </div>
      </div>

      {company && (
        <div className="px-6 py-4 border-b border-slate-800">
          <p className="text-xs uppercase tracking-widest text-slate-500 mb-1">Empresa ativa</p>
          <p className="font-semibold text-white text-sm truncate" data-testid="sidebar-company-name">
            {company.name}
          </p>
          <Badge variant="secondary" className="mt-2 bg-slate-800 text-slate-300 hover:bg-slate-800 border-none">
            {businessTypeLabel(company.business_type)}
          </Badge>
        </div>
      )}

      <nav className="flex-1 px-3 py-4 space-y-1">
        {NAV.filter((n) => !n.roles || n.roles.includes(role)).map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            onClick={onNavigate}
            data-testid={item.testId}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors",
                isActive
                  ? "bg-indigo-600 text-white"
                  : "text-slate-300 hover:bg-slate-800 hover:text-white"
              )
            }
          >
            <item.icon className="h-4 w-4" />
            {item.label}
          </NavLink>
        ))}

        <div className="pt-6">
          <p className="px-3 text-[11px] uppercase tracking-widest text-slate-500 mb-2">
            Em breve
          </p>
          {COMING_SOON.map((c) => (
            <div
              key={c.label}
              className="flex items-center justify-between px-3 py-2 rounded-md text-sm text-slate-400"
            >
              <span className="flex items-center gap-3">
                <c.icon className="h-4 w-4" />
                {c.label}
              </span>
              <Badge className="bg-amber-100 text-amber-800 hover:bg-amber-100 border-none text-[10px]">
                em breve
              </Badge>
            </div>
          ))}
        </div>
      </nav>

      <div className="px-6 py-4 border-t border-slate-800 text-[11px] text-slate-500">
        Fase 1 · Fundação
      </div>
    </div>
  );
}

export default function AppShell({ children, title }) {
  const { user, company, role, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  const doLogout = async () => {
    await logout();
    navigate("/login", { replace: true });
  };

  return (
    <div className="flex min-h-screen bg-slate-50">
      {/* Desktop sidebar */}
      <aside className="hidden md:flex md:w-64 md:flex-col md:fixed md:inset-y-0">
        <SidebarContent role={role} company={company} />
      </aside>

      {/* Mobile sidebar */}
      {mobileOpen && (
        <div className="fixed inset-0 z-40 md:hidden">
          <div className="absolute inset-0 bg-slate-900/60" onClick={() => setMobileOpen(false)} />
          <div className="relative w-72 h-full">
            <button
              className="absolute top-3 right-3 p-1.5 rounded-md text-slate-300 hover:bg-slate-800 z-10"
              onClick={() => setMobileOpen(false)}
              data-testid="close-mobile-nav"
            >
              <X className="h-4 w-4" />
            </button>
            <SidebarContent role={role} company={company} onNavigate={() => setMobileOpen(false)} />
          </div>
        </div>
      )}

      <div className="flex-1 md:pl-64 flex flex-col">
        <header className="sticky top-0 z-30 bg-white border-b border-slate-200 h-16 px-4 md:px-8 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              className="md:hidden p-2 rounded-md hover:bg-slate-100"
              onClick={() => setMobileOpen(true)}
              data-testid="open-mobile-nav"
            >
              <Menu className="h-5 w-5" />
            </button>
            <h1 className="text-lg md:text-xl font-bold text-slate-900" style={{ fontFamily: "'Plus Jakarta Sans'" }}>
              {title}
            </h1>
          </div>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                className="flex items-center gap-2 px-2 py-1.5 rounded-md hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                data-testid="user-menu-trigger"
              >
                <Avatar className="h-8 w-8">
                  <Initials name={user?.name} />
                </Avatar>
                <div className="hidden sm:flex flex-col items-start leading-tight">
                  <span className="text-sm font-semibold text-slate-900" data-testid="header-user-name">
                    {user?.name}
                  </span>
                  {role && (
                    <span className="text-[11px] text-slate-500">{ROLE_LABELS[role]}</span>
                  )}
                </div>
                <ChevronDown className="h-4 w-4 text-slate-400" />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel>
                <div className="flex flex-col">
                  <span className="text-sm font-semibold">{user?.name}</span>
                  <span className="text-xs text-slate-500">{user?.email}</span>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild>
                <Link to="/settings/company" data-testid="menu-company">
                  <Settings className="h-4 w-4 mr-2" /> Configurações
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Link to="/settings/users" data-testid="menu-users">
                  <UserCog className="h-4 w-4 mr-2" /> Membros
                </Link>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={doLogout} data-testid="logout-btn" className="text-red-600 focus:text-red-600">
                <LogOut className="h-4 w-4 mr-2" /> Sair
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </header>

        <main className="flex-1 px-4 md:px-8 py-8">{children}</main>
      </div>
      <FloatingAssistant/>
    </div>
  );
}
