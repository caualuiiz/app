import { useCallback, useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import { ChevronLeft, ChevronRight, Loader2, Plus, Trash2 } from "lucide-react";
import AppShell from "@/components/AppShell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle,
} from "@/components/ui/dialog";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import { api, formatApiError } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

const STATUS_COLORS = {
  PENDING: "bg-amber-100 text-amber-800 border-amber-300",
  CONFIRMED: "bg-indigo-100 text-indigo-800 border-indigo-300",
  COMPLETED: "bg-emerald-100 text-emerald-800 border-emerald-300",
  CANCELLED: "bg-slate-200 text-slate-600 border-slate-300 line-through",
};
const STATUS_LABELS = { PENDING: "Pendente", CONFIRMED: "Confirmado", COMPLETED: "Concluído", CANCELLED: "Cancelado" };

function fmtDate(d) { return d.toISOString().split("T")[0]; }
function addDays(d, n) { const x = new Date(d); x.setDate(x.getDate() + n); return x; }
function startOfWeek(d) { const x = new Date(d); const day = x.getDay(); x.setDate(x.getDate() - day); return x; }
function startOfMonth(d) { return new Date(d.getFullYear(), d.getMonth(), 1); }

export default function AgendaPage() {
  const { role, user } = useAuth();
  const isAdmin = role === "OWNER" || role === "MANAGER";
  const [view, setView] = useState("day");
  const [cursor, setCursor] = useState(new Date());
  const [appts, setAppts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pros, setPros] = useState([]);
  const [services, setServices] = useState([]);
  const [clients, setClients] = useState([]);
  const [proFilter, setProFilter] = useState("all");
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [detail, setDetail] = useState(null);
  const [form, setForm] = useState({ client_id: "", service_id: "", professional_id: "", date: fmtDate(new Date()), start_time: "09:00", notes: "", status: "CONFIRMED" });
  const [newClient, setNewClient] = useState(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const range = useMemo(() => {
    if (view === "day") return { from: fmtDate(cursor), to: fmtDate(cursor) };
    if (view === "week") { const s = startOfWeek(cursor); return { from: fmtDate(s), to: fmtDate(addDays(s, 6)) }; }
    const s = startOfMonth(cursor); const e = new Date(s.getFullYear(), s.getMonth() + 1, 0);
    return { from: fmtDate(s), to: fmtDate(e) };
  }, [view, cursor]);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params = { date_from: range.from, date_to: range.to };
      if (isAdmin && proFilter !== "all") params.professional_id = proFilter;
      const { data } = await api.get("/appointments", { params });
      setAppts(data);
    } catch (e) { toast.error(formatApiError(e)); }
    finally { setLoading(false); }
  }, [range.from, range.to, isAdmin, proFilter]);

  useEffect(() => { load(); }, [load]);

  useEffect(() => {
    (async () => {
      try {
        const [m, s, c] = await Promise.all([api.get("/memberships"), api.get("/services", { params: { only_active: true } }), api.get("/clients")]);
        setPros(m.data); setServices(s.data); setClients(c.data);
      } catch (e) { /* ignore */ }
    })();
  }, []);

  const openNew = () => {
    setEditing(null);
    setForm({ client_id: "", service_id: "", professional_id: role === "PROFESSIONAL" ? user.id : "", date: fmtDate(cursor), start_time: "09:00", notes: "", status: "CONFIRMED" });
    setError(""); setNewClient(null); setOpen(true);
  };
  const openEdit = (a) => {
    setEditing(a); setDetail(null);
    setForm({ client_id: a.client_id, service_id: a.service_id, professional_id: a.professional_id, date: a.date, start_time: a.start_time, notes: a.notes || "", status: a.status });
    setError(""); setOpen(true);
  };

  const save = async (e) => {
    e.preventDefault(); setError(""); setSaving(true);
    try {
      let clientId = form.client_id;
      if (clientId === "__new__") {
        if (!newClient?.name) throw new Error("Informe o nome do cliente");
        const { data: c } = await api.post("/clients", { name: newClient.name, phone: newClient.phone || null, email: newClient.email || null });
        clientId = c.id; setClients((cs) => [...cs, c]);
      }
      const payload = { ...form, client_id: clientId };
      if (editing) await api.patch(`/appointments/${editing.id}`, payload);
      else await api.post("/appointments", payload);
      setOpen(false); toast.success("Agendamento salvo"); load();
    } catch (err) { setError(err.response ? formatApiError(err) : err.message); }
    finally { setSaving(false); }
  };

  const changeStatus = async (a, status) => {
    try { await api.patch(`/appointments/${a.id}`, { status }); toast.success("Status atualizado"); setDetail(null); load(); }
    catch (e) { toast.error(formatApiError(e)); }
  };
  const del = async (a) => {
    if (!confirm("Excluir agendamento?")) return;
    try { await api.delete(`/appointments/${a.id}`); toast.success("Excluído"); setDetail(null); load(); }
    catch (e) { toast.error(formatApiError(e)); }
  };

  const shiftCursor = (dir) => {
    if (view === "day") setCursor(addDays(cursor, dir));
    else if (view === "week") setCursor(addDays(cursor, dir * 7));
    else setCursor(new Date(cursor.getFullYear(), cursor.getMonth() + dir, 1));
  };

  const cursorLabel = view === "day"
    ? cursor.toLocaleDateString("pt-BR", { weekday: "long", day: "2-digit", month: "long", year: "numeric" })
    : view === "week"
      ? `Semana de ${startOfWeek(cursor).toLocaleDateString("pt-BR")} – ${addDays(startOfWeek(cursor), 6).toLocaleDateString("pt-BR")}`
      : cursor.toLocaleDateString("pt-BR", { month: "long", year: "numeric" });

  const grouped = useMemo(() => {
    const g = {};
    appts.forEach(a => { (g[a.date] ||= []).push(a); });
    Object.values(g).forEach(arr => arr.sort((a, b) => a.start_time.localeCompare(b.start_time)));
    return g;
  }, [appts]);

  const daysInView = useMemo(() => {
    if (view === "day") return [fmtDate(cursor)];
    if (view === "week") { const s = startOfWeek(cursor); return [...Array(7)].map((_, i) => fmtDate(addDays(s, i))); }
    const s = startOfMonth(cursor); const e = new Date(s.getFullYear(), s.getMonth() + 1, 0);
    return [...Array(e.getDate())].map((_, i) => fmtDate(addDays(s, i)));
  }, [view, cursor]);

  return (
    <AppShell title="Agenda">
      <div className="max-w-7xl mx-auto space-y-4">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
          <div className="flex items-center gap-2 flex-wrap">
            <Button variant="outline" size="sm" onClick={() => setCursor(new Date())} data-testid="agenda-today-btn">Hoje</Button>
            <Button variant="outline" size="icon" onClick={() => shiftCursor(-1)} data-testid="agenda-prev-btn"><ChevronLeft className="h-4 w-4"/></Button>
            <Button variant="outline" size="icon" onClick={() => shiftCursor(1)} data-testid="agenda-next-btn"><ChevronRight className="h-4 w-4"/></Button>
            <span className="font-medium capitalize" data-testid="agenda-cursor-label">{cursorLabel}</span>
          </div>
          <div className="flex items-center gap-2">
            <Tabs value={view} onValueChange={setView}><TabsList><TabsTrigger value="day" data-testid="view-day">Dia</TabsTrigger><TabsTrigger value="week" data-testid="view-week">Semana</TabsTrigger><TabsTrigger value="month" data-testid="view-month">Mês</TabsTrigger></TabsList></Tabs>
            {isAdmin && <Select value={proFilter} onValueChange={setProFilter}><SelectTrigger className="w-40" data-testid="pro-filter"><SelectValue/></SelectTrigger><SelectContent><SelectItem value="all">Todos</SelectItem>{pros.map(p => <SelectItem key={p.user_id} value={p.user_id}>{p.user_name}</SelectItem>)}</SelectContent></Select>}
            <Button className="bg-indigo-600 hover:bg-indigo-700" onClick={openNew} data-testid="new-appt-btn"><Plus className="h-4 w-4 mr-2"/>Novo</Button>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-4 md:p-6 min-h-[400px]">
          {loading ? <div className="flex items-center gap-2 text-slate-500"><Loader2 className="h-4 w-4 animate-spin"/>Carregando…</div>
            : daysInView.every(d => !grouped[d]) ? <div className="text-center text-slate-400 py-16">Nenhum agendamento no período.</div>
            : <div className={view === "month" ? "grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-2" : "space-y-4"}>
                {daysInView.map(d => (
                  <div key={d} className={view === "month" ? "border border-slate-100 rounded-lg p-2 min-h-[100px]" : ""}>
                    <div className={`text-xs font-semibold text-slate-500 uppercase tracking-wider ${view === "month" ? "mb-1" : "mb-2"}`}>{new Date(d + "T12:00").toLocaleDateString("pt-BR", { weekday: "short", day: "2-digit", month: "2-digit" })}</div>
                    <div className="space-y-1">
                      {(grouped[d] || []).map(a => (
                        <button key={a.id} type="button" onClick={() => setDetail(a)} className={`w-full text-left border rounded-md px-3 py-2 text-sm hover:shadow-sm transition ${STATUS_COLORS[a.status]}`} data-testid={`appt-${a.id}`}>
                          <div className="font-semibold">{a.start_time} · {a.client_name}</div>
                          <div className="text-xs opacity-80">{a.service_name} · {a.professional_name}</div>
                        </button>))}
                    </div>
                  </div>))}
              </div>}
        </div>
      </div>

      {/* Create / Edit modal */}
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-lg"><DialogHeader><DialogTitle>{editing ? "Editar agendamento" : "Novo agendamento"}</DialogTitle></DialogHeader>
          <form onSubmit={save} className="space-y-3" data-testid="appt-form">
            <div className="space-y-1"><Label>Cliente</Label>
              <Select value={form.client_id} onValueChange={(v) => { setForm({ ...form, client_id: v }); if (v === "__new__") setNewClient({ name: "", phone: "", email: "" }); else setNewClient(null); }}>
                <SelectTrigger data-testid="appt-client-select"><SelectValue placeholder="Selecionar cliente"/></SelectTrigger>
                <SelectContent><SelectItem value="__new__">+ Novo cliente</SelectItem>{clients.map(c => <SelectItem key={c.id} value={c.id}>{c.name}</SelectItem>)}</SelectContent>
              </Select>
            </div>
            {newClient && <div className="grid grid-cols-2 gap-2 bg-slate-50 border rounded-md p-3">
              <Input placeholder="Nome" value={newClient.name} onChange={(e) => setNewClient({ ...newClient, name: e.target.value })} data-testid="new-client-name" required/>
              <Input placeholder="Telefone" value={newClient.phone} onChange={(e) => setNewClient({ ...newClient, phone: e.target.value })}/>
              <Input className="col-span-2" placeholder="E-mail" value={newClient.email} onChange={(e) => setNewClient({ ...newClient, email: e.target.value })}/>
            </div>}
            <div className="space-y-1"><Label>Serviço</Label>
              <Select value={form.service_id} onValueChange={(v) => setForm({ ...form, service_id: v })}>
                <SelectTrigger data-testid="appt-service-select"><SelectValue placeholder="Selecionar serviço"/></SelectTrigger>
                <SelectContent>{services.map(s => <SelectItem key={s.id} value={s.id}>{s.name} · {s.duration_min}min · R$ {Number(s.price).toFixed(2)}</SelectItem>)}</SelectContent>
              </Select>
            </div>
            <div className="space-y-1"><Label>Profissional</Label>
              <Select value={form.professional_id} onValueChange={(v) => setForm({ ...form, professional_id: v })} disabled={role === "PROFESSIONAL"}>
                <SelectTrigger data-testid="appt-pro-select"><SelectValue placeholder="Selecionar profissional"/></SelectTrigger>
                <SelectContent>{pros.map(p => <SelectItem key={p.user_id} value={p.user_id}>{p.user_name}</SelectItem>)}</SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1"><Label>Data</Label><Input type="date" required value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} data-testid="appt-date-input"/></div>
              <div className="space-y-1"><Label>Horário</Label><Input type="time" required value={form.start_time} onChange={(e) => setForm({ ...form, start_time: e.target.value })} data-testid="appt-time-input"/></div>
            </div>
            <div className="space-y-1"><Label>Status</Label>
              <Select value={form.status} onValueChange={(v) => setForm({ ...form, status: v })}>
                <SelectTrigger data-testid="appt-status-select"><SelectValue/></SelectTrigger>
                <SelectContent>{Object.entries(STATUS_LABELS).map(([k, l]) => <SelectItem key={k} value={k}>{l}</SelectItem>)}</SelectContent>
              </Select>
            </div>
            <div className="space-y-1"><Label>Observações</Label><Textarea rows={2} value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })}/></div>
            {error && <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md px-3 py-2" data-testid="appt-error">{error}</div>}
            <DialogFooter><Button type="button" variant="ghost" onClick={() => setOpen(false)}>Cancelar</Button><Button type="submit" className="bg-indigo-600 hover:bg-indigo-700" disabled={saving} data-testid="save-appt-btn">{saving && <Loader2 className="h-4 w-4 mr-2 animate-spin"/>}Salvar</Button></DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Detail modal */}
      <Dialog open={!!detail} onOpenChange={(v) => !v && setDetail(null)}>
        <DialogContent><DialogHeader><DialogTitle>Detalhes do agendamento</DialogTitle></DialogHeader>
          {detail && <div className="space-y-2 text-sm" data-testid="appt-detail">
            <div className="flex justify-between"><span className="text-slate-500">Cliente</span><span className="font-medium">{detail.client_name}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Telefone</span><span>{detail.client_phone || "-"}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Serviço</span><span>{detail.service_name}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Profissional</span><span>{detail.professional_name}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Data</span><span>{new Date(detail.date + "T12:00").toLocaleDateString("pt-BR")}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Horário</span><span>{detail.start_time} → {detail.end_time}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Duração</span><span>{detail.duration_min} min</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Valor</span><span>R$ {Number(detail.price).toFixed(2)}</span></div>
            <div className="flex justify-between items-center"><span className="text-slate-500">Status</span><Badge className={STATUS_COLORS[detail.status]}>{STATUS_LABELS[detail.status]}</Badge></div>
            {detail.notes && <div className="pt-2 border-t border-slate-100"><span className="text-slate-500 block mb-1">Observações</span><p>{detail.notes}</p></div>}
            <div className="pt-3 flex flex-wrap gap-2">
              <Select value={detail.status} onValueChange={(v) => changeStatus(detail, v)}>
                <SelectTrigger className="w-40" data-testid="detail-status-select"><SelectValue/></SelectTrigger>
                <SelectContent>{Object.entries(STATUS_LABELS).map(([k, l]) => <SelectItem key={k} value={k}>{l}</SelectItem>)}</SelectContent>
              </Select>
              <Button variant="outline" onClick={() => openEdit(detail)} data-testid="detail-edit-btn">Editar</Button>
              {isAdmin && <Button variant="ghost" className="text-red-600 hover:text-red-700 ml-auto" onClick={() => del(detail)} data-testid="detail-delete-btn"><Trash2 className="h-4 w-4 mr-1"/>Excluir</Button>}
            </div>
          </div>}
        </DialogContent>
      </Dialog>
    </AppShell>
  );
}
