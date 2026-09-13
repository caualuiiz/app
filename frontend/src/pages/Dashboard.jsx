import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Calendar, CheckCircle2, Clock, DollarSign, Loader2, Users, XCircle,
} from "lucide-react";
import AppShell from "@/components/AppShell";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { api, formatApiError, ROLE_LABELS } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { businessTypeLabel } from "@/lib/api";
import { toast } from "sonner";

const STATUS_LABELS = { PENDING: "Pendente", CONFIRMED: "Confirmado", COMPLETED: "Concluído", CANCELLED: "Cancelado" };
const STATUS_COLORS = {
  PENDING: "bg-amber-100 text-amber-800",
  CONFIRMED: "bg-indigo-100 text-indigo-800",
  COMPLETED: "bg-emerald-100 text-emerald-800",
  CANCELLED: "bg-slate-200 text-slate-600",
};

function Stat({ icon: Icon, label, value, color, testId }) {
  return (
    <Card className="border-slate-200" data-testid={testId}>
      <CardContent className="p-5">
        <div className={`h-10 w-10 rounded-lg ${color} flex items-center justify-center mb-3`}><Icon className="h-5 w-5"/></div>
        <p className="text-xs uppercase tracking-widest text-slate-500 font-semibold">{label}</p>
        <p className="text-2xl font-bold text-slate-900 mt-1" style={{ fontFamily: "'Plus Jakarta Sans'" }}>{value}</p>
      </CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  const { user, company, role } = useAuth();
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try { const { data } = await api.get("/dashboard/summary"); setSummary(data); }
      catch (e) { toast.error(formatApiError(e)); }
      finally { setLoading(false); }
    })();
  }, []);

  return (
    <AppShell title="Painel">
      <div className="max-w-6xl mx-auto space-y-8" data-testid="dashboard-container">
        <section className="bg-white border border-slate-200 rounded-xl p-6 md:p-8 shadow-sm" data-testid="dashboard-greeting-card">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-widest text-indigo-600 font-semibold mb-2">Painel principal</p>
              <h2 className="text-2xl md:text-3xl font-extrabold text-slate-900 tracking-tight" style={{ fontFamily: "'Plus Jakarta Sans'" }} data-testid="dashboard-greeting">
                Olá, {user?.name?.split(" ")[0]} 👋
              </h2>
              <p className="text-slate-500 mt-1">
                Você está gerenciando <span className="font-semibold text-slate-900" data-testid="dashboard-company-name">{company?.name}</span> como <span className="font-semibold">{ROLE_LABELS[role]}</span>.
              </p>
            </div>
            <Badge className="bg-indigo-600 hover:bg-indigo-600" data-testid="dashboard-business-badge">{businessTypeLabel(company?.business_type)}</Badge>
          </div>
        </section>

        {loading ? <div className="flex items-center gap-2 text-slate-500"><Loader2 className="h-4 w-4 animate-spin"/>Carregando indicadores…</div>
          : summary && <>
            <section>
              <h3 className="text-lg font-bold text-slate-900 mb-4" style={{ fontFamily: "'Plus Jakarta Sans'" }}>Indicadores de hoje</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                <Stat icon={Calendar} label="Hoje" value={summary.total} color="bg-indigo-50 text-indigo-600" testId="stat-total"/>
                <Stat icon={Clock} label="Pendentes" value={summary.counters.PENDING} color="bg-amber-50 text-amber-600" testId="stat-pending"/>
                <Stat icon={CheckCircle2} label="Confirmados" value={summary.counters.CONFIRMED} color="bg-sky-50 text-sky-600" testId="stat-confirmed"/>
                <Stat icon={CheckCircle2} label="Concluídos" value={summary.counters.COMPLETED} color="bg-emerald-50 text-emerald-600" testId="stat-completed"/>
                <Stat icon={DollarSign} label="Faturamento" value={`R$ ${summary.revenue.toFixed(2)}`} color="bg-rose-50 text-rose-600" testId="stat-revenue"/>
              </div>
            </section>

            <section className="bg-white border border-slate-200 rounded-xl p-6" data-testid="upcoming-section">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-slate-900" style={{ fontFamily: "'Plus Jakarta Sans'" }}>Próximos atendimentos</h3>
                <Link to="/agenda" className="text-sm text-indigo-600 hover:text-indigo-700 font-medium">Ver agenda completa →</Link>
              </div>
              {summary.upcoming.length === 0 ? <p className="text-sm text-slate-500 py-6 text-center">Nenhum atendimento pendente ou confirmado para hoje.</p>
                : <div className="divide-y divide-slate-100">
                  {summary.upcoming.map(a => (
                    <div key={a.id} className="py-3 flex items-center justify-between gap-3" data-testid={`upcoming-${a.id}`}>
                      <div className="flex items-center gap-4 min-w-0">
                        <div className="text-center min-w-[52px]"><p className="font-bold text-slate-900">{a.start_time}</p><p className="text-xs text-slate-400">{a.duration_min}min</p></div>
                        <div className="min-w-0"><p className="font-medium text-slate-900 truncate">{a.client_name}</p><p className="text-sm text-slate-500 truncate">{a.service_name} · {a.professional_name}</p></div>
                      </div>
                      <Badge className={STATUS_COLORS[a.status]}>{STATUS_LABELS[a.status]}</Badge>
                    </div>))}
                </div>}
            </section>
          </>}
      </div>
    </AppShell>
  );
}
