import { Link } from "react-router-dom";
import {
  Building2,
  Calendar,
  DollarSign,
  Scissors,
  Settings,
  Sparkles,
  UserCog,
  Users,
} from "lucide-react";
import AppShell from "@/components/AppShell";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useAuth } from "@/contexts/AuthContext";
import { ROLE_LABELS, businessTypeLabel } from "@/lib/api";

const MODULES = [
  {
    key: "agenda",
    title: "Agenda",
    desc: "Compromissos, horários e disponibilidade em tempo real.",
    icon: Calendar,
    color: "bg-indigo-50 text-indigo-600",
  },
  {
    key: "clients",
    title: "Clientes",
    desc: "Histórico, preferências e relacionamento com sua base.",
    icon: Users,
    color: "bg-emerald-50 text-emerald-600",
  },
  {
    key: "services",
    title: "Serviços",
    desc: "Catálogo, preços, duração e combos.",
    icon: Scissors,
    color: "bg-amber-50 text-amber-600",
  },
  {
    key: "professionals",
    title: "Profissionais",
    desc: "Equipe, agendas individuais e comissões.",
    icon: UserCog,
    color: "bg-sky-50 text-sky-600",
  },
  {
    key: "finance",
    title: "Financeiro",
    desc: "Faturamento, comandas e fluxo de caixa.",
    icon: DollarSign,
    color: "bg-rose-50 text-rose-600",
  },
];

export default function DashboardPage() {
  const { user, company, role } = useAuth();

  return (
    <AppShell title="Painel">
      <div className="max-w-6xl mx-auto space-y-8" data-testid="dashboard-container">
        <section
          className="bg-white border border-slate-200 rounded-xl p-6 md:p-8 shadow-sm"
          data-testid="dashboard-greeting-card"
        >
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-widest text-indigo-600 font-semibold mb-2">
                Fase 1 · Fundação ativa
              </p>
              <h2
                className="text-2xl md:text-3xl font-extrabold text-slate-900 tracking-tight"
                style={{ fontFamily: "'Plus Jakarta Sans'" }}
                data-testid="dashboard-greeting"
              >
                Olá, {user?.name?.split(" ")[0]} 👋
              </h2>
              <p className="text-slate-500 mt-1">
                Você está gerenciando{" "}
                <span className="font-semibold text-slate-900" data-testid="dashboard-company-name">
                  {company?.name}
                </span>{" "}
                como <span className="font-semibold">{ROLE_LABELS[role]}</span>.
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Badge className="bg-indigo-600 hover:bg-indigo-600" data-testid="dashboard-business-badge">
                <Building2 className="h-3 w-3 mr-1" />
                {businessTypeLabel(company?.business_type)}
              </Badge>
              <Badge variant="outline" className="border-slate-300 text-slate-600">
                {company?.slug}
              </Badge>
            </div>
          </div>
        </section>

        <section>
          <div className="flex items-baseline justify-between mb-4">
            <h3 className="text-lg font-bold text-slate-900" style={{ fontFamily: "'Plus Jakarta Sans'" }}>
              Módulos da plataforma
            </h3>
            <span className="text-xs text-slate-500">Novos módulos chegam nas próximas fases</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
            {MODULES.map((m) => (
              <Card
                key={m.key}
                className="border-slate-200 hover:shadow-md transition-shadow"
                data-testid={`module-card-${m.key}`}
              >
                <CardHeader className="pb-3">
                  <div className={`h-10 w-10 rounded-lg ${m.color} flex items-center justify-center mb-2`}>
                    <m.icon className="h-5 w-5" />
                  </div>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base font-bold text-slate-900">{m.title}</CardTitle>
                    <Badge className="bg-amber-100 text-amber-800 hover:bg-amber-100 border-none text-[10px] uppercase tracking-wider">
                      Em breve
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-sm text-slate-500 leading-relaxed">
                    {m.desc}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {(role === "OWNER" || role === "MANAGER") && (
          <section>
            <div className="flex items-baseline justify-between mb-4">
              <h3 className="text-lg font-bold text-slate-900" style={{ fontFamily: "'Plus Jakarta Sans'" }}>
                Atalhos rápidos
              </h3>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Link
                to="/settings/company"
                className="group bg-white border border-slate-200 rounded-xl p-5 hover:border-indigo-500 hover:shadow-md transition-all"
                data-testid="shortcut-company"
              >
                <div className="flex items-start gap-4">
                  <div className="h-10 w-10 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center">
                    <Settings className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="font-semibold text-slate-900 group-hover:text-indigo-600 transition-colors">
                      Configurações da empresa
                    </p>
                    <p className="text-sm text-slate-500 mt-1">
                      Atualize logo, foto, endereço e contatos.
                    </p>
                  </div>
                </div>
              </Link>
              <Link
                to="/settings/users"
                className="group bg-white border border-slate-200 rounded-xl p-5 hover:border-indigo-500 hover:shadow-md transition-all"
                data-testid="shortcut-users"
              >
                <div className="flex items-start gap-4">
                  <div className="h-10 w-10 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
                    <Users className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="font-semibold text-slate-900 group-hover:text-indigo-600 transition-colors">
                      Membros da empresa
                    </p>
                    <p className="text-sm text-slate-500 mt-1">
                      Convide gerentes e profissionais e defina permissões.
                    </p>
                  </div>
                </div>
              </Link>
            </div>
          </section>
        )}

        <section className="bg-gradient-to-r from-indigo-600 to-indigo-700 text-white rounded-xl p-6 md:p-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Sparkles className="h-4 w-4" />
              <span className="text-xs uppercase tracking-widest font-semibold">Próximas fases</span>
            </div>
            <h4 className="text-xl font-bold" style={{ fontFamily: "'Plus Jakarta Sans'" }}>
              Sua fundação está pronta.
            </h4>
            <p className="text-indigo-100 text-sm mt-1 max-w-xl">
              Fase 1 conclusa: autenticação, empresas, permissões e isolamento multi-tenant.
              As próximas fases trarão agenda, clientes, serviços, financeiro e página pública.
            </p>
          </div>
        </section>
      </div>
    </AppShell>
  );
}
