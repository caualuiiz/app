import { useCallback, useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import { Loader2, Plus, Search, Trash2 } from "lucide-react";
import AppShell from "@/components/AppShell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger,
} from "@/components/ui/dialog";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { api, formatApiError } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

export default function ClientsPage() {
  const { role } = useAuth();
  const isAdmin = role === "OWNER" || role === "MANAGER";
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ name: "", phone: "", email: "", birth_date: "", notes: "" });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [history, setHistory] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await api.get("/clients", { params: { search } });
      setItems(data);
    } catch (e) { toast.error(formatApiError(e)); }
    finally { setLoading(false); }
  }, [search]);

  useEffect(() => { load(); }, [load]);
  useEffect(() => { const t = setTimeout(load, 300); return () => clearTimeout(t); }, [load]);

  const openNew = () => { setEditing(null); setForm({ name: "", phone: "", email: "", birth_date: "", notes: "" }); setError(""); setOpen(true); };
  const openEdit = (c) => { setEditing(c); setForm({ name: c.name, phone: c.phone || "", email: c.email || "", birth_date: c.birth_date || "", notes: c.notes || "" }); setError(""); setOpen(true); };

  const save = async (e) => {
    e.preventDefault(); setError(""); setSaving(true);
    try {
      const payload = { ...form };
      Object.keys(payload).forEach((k) => (payload[k] === "" ? (payload[k] = null) : null));
      if (editing) await api.patch(`/clients/${editing.id}`, payload);
      else await api.post("/clients", payload);
      setOpen(false); toast.success("Cliente salvo"); load();
    } catch (err) { setError(formatApiError(err)); }
    finally { setSaving(false); }
  };

  const remove = async (id) => {
    if (!confirm("Excluir este cliente?")) return;
    try { await api.delete(`/clients/${id}`); toast.success("Cliente excluído"); load(); }
    catch (e) { toast.error(formatApiError(e)); }
  };

  const showHistory = async (c) => {
    try { const { data } = await api.get(`/clients/${c.id}/appointments`); setHistory({ client: c, list: data }); }
    catch (e) { toast.error(formatApiError(e)); }
  };

  return (
    <AppShell title="Clientes">
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
          <div className="relative max-w-sm w-full">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <Input className="pl-9" placeholder="Pesquisar por nome..." value={search} onChange={(e) => setSearch(e.target.value)} data-testid="clients-search" />
          </div>
          <Button className="bg-indigo-600 hover:bg-indigo-700" onClick={openNew} data-testid="new-client-btn"><Plus className="h-4 w-4 mr-2" /> Novo cliente</Button>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
          {loading ? <div className="p-6 flex items-center gap-2 text-slate-500"><Loader2 className="h-4 w-4 animate-spin" /> Carregando…</div>
            : items.length === 0 ? <div className="p-10 text-center text-slate-500">Nenhum cliente ainda.</div>
            : <Table><TableHeader><TableRow><TableHead>Nome</TableHead><TableHead>Telefone</TableHead><TableHead>E-mail</TableHead><TableHead className="text-right">Ações</TableHead></TableRow></TableHeader>
                <TableBody>{items.map(c => (
                  <TableRow key={c.id} data-testid={`client-row-${c.id}`}>
                    <TableCell className="font-medium">{c.name}</TableCell>
                    <TableCell className="text-slate-600">{c.phone || "-"}</TableCell>
                    <TableCell className="text-slate-600">{c.email || "-"}</TableCell>
                    <TableCell className="text-right space-x-1">
                      <Button variant="ghost" size="sm" onClick={() => showHistory(c)} data-testid={`history-${c.id}`}>Histórico</Button>
                      <Button variant="ghost" size="sm" onClick={() => openEdit(c)} data-testid={`edit-${c.id}`}>Editar</Button>
                      {isAdmin && <Button variant="ghost" size="icon" className="text-red-600" onClick={() => remove(c.id)} data-testid={`delete-${c.id}`}><Trash2 className="h-4 w-4"/></Button>}
                    </TableCell>
                  </TableRow>))}</TableBody></Table>}
        </div>
      </div>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent><DialogHeader><DialogTitle>{editing ? "Editar cliente" : "Novo cliente"}</DialogTitle></DialogHeader>
          <form onSubmit={save} className="space-y-3" data-testid="client-form">
            <div className="space-y-1"><Label>Nome completo</Label><Input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} data-testid="client-name-input"/></div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1"><Label>Telefone</Label><Input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} data-testid="client-phone-input"/></div>
              <div className="space-y-1"><Label>E-mail</Label><Input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} data-testid="client-email-input"/></div>
            </div>
            <div className="space-y-1"><Label>Data de nascimento</Label><Input type="date" value={form.birth_date} onChange={(e) => setForm({ ...form, birth_date: e.target.value })}/></div>
            <div className="space-y-1"><Label>Observações</Label><Textarea rows={3} value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })}/></div>
            {error && <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md px-3 py-2">{error}</div>}
            <DialogFooter><Button type="button" variant="ghost" onClick={() => setOpen(false)}>Cancelar</Button><Button type="submit" className="bg-indigo-600 hover:bg-indigo-700" disabled={saving} data-testid="save-client-btn">{saving && <Loader2 className="h-4 w-4 mr-2 animate-spin"/>}Salvar</Button></DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <Dialog open={!!history} onOpenChange={(v) => !v && setHistory(null)}>
        <DialogContent><DialogHeader><DialogTitle>Histórico – {history?.client?.name}</DialogTitle></DialogHeader>
          {history?.list?.length ? <div className="space-y-2 max-h-80 overflow-y-auto">
            {history.list.map(a => (
              <div key={a.id} className="border border-slate-200 rounded-md p-3 text-sm">
                <div className="flex justify-between font-medium"><span>{a.date} · {a.start_time}</span><span className="text-xs uppercase text-slate-500">{a.status}</span></div>
                <div className="text-slate-600">{a.service_name} · {a.professional_name}</div>
              </div>))}</div> : <p className="text-sm text-slate-500">Nenhum agendamento ainda.</p>}
        </DialogContent>
      </Dialog>
    </AppShell>
  );
}
