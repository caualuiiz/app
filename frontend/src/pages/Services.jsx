import { useEffect, useState } from "react";
import { toast } from "sonner";
import { Loader2, Plus, Trash2 } from "lucide-react";
import AppShell from "@/components/AppShell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle,
} from "@/components/ui/dialog";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { api, formatApiError } from "@/lib/api";

export default function ServicesPage() {
  const [items, setItems] = useState([]);
  const [pros, setPros] = useState([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ name: "", description: "", duration_min: 30, price: 0, is_active: true, professional_ids: [] });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const load = async () => {
    setLoading(true);
    try {
      const [s, p] = await Promise.all([api.get("/services"), api.get("/memberships")]);
      setItems(s.data); setPros(p.data);
    } catch (e) { toast.error(formatApiError(e)); }
    finally { setLoading(false); }
  };
  useEffect(() => { load(); }, []);

  const openNew = () => { setEditing(null); setForm({ name: "", description: "", duration_min: 30, price: 0, is_active: true, professional_ids: [] }); setError(""); setOpen(true); };
  const openEdit = (s) => { setEditing(s); setForm({ name: s.name, description: s.description || "", duration_min: s.duration_min, price: s.price, is_active: s.is_active, professional_ids: s.professional_ids || [] }); setError(""); setOpen(true); };

  const save = async (e) => {
    e.preventDefault(); setError(""); setSaving(true);
    try {
      const payload = { ...form, duration_min: Number(form.duration_min), price: Number(form.price) };
      if (editing) await api.patch(`/services/${editing.id}`, payload);
      else await api.post("/services", payload);
      setOpen(false); toast.success("Serviço salvo"); load();
    } catch (err) { setError(formatApiError(err)); }
    finally { setSaving(false); }
  };

  const remove = async (id) => {
    if (!confirm("Excluir este serviço?")) return;
    try { await api.delete(`/services/${id}`); toast.success("Excluído"); load(); }
    catch (e) { toast.error(formatApiError(e)); }
  };

  const toggleProf = (id) => {
    setForm((f) => ({ ...f, professional_ids: f.professional_ids.includes(id) ? f.professional_ids.filter(x => x !== id) : [...f.professional_ids, id] }));
  };

  return (
    <AppShell title="Serviços">
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="flex justify-end"><Button className="bg-indigo-600 hover:bg-indigo-700" onClick={openNew} data-testid="new-service-btn"><Plus className="h-4 w-4 mr-2"/>Novo serviço</Button></div>
        <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
          {loading ? <div className="p-6 flex items-center gap-2 text-slate-500"><Loader2 className="h-4 w-4 animate-spin"/>Carregando…</div>
            : items.length === 0 ? <div className="p-10 text-center text-slate-500">Nenhum serviço cadastrado.</div>
            : <Table><TableHeader><TableRow><TableHead>Nome</TableHead><TableHead>Duração</TableHead><TableHead>Preço</TableHead><TableHead>Status</TableHead><TableHead className="text-right">Ações</TableHead></TableRow></TableHeader>
                <TableBody>{items.map(s => (
                  <TableRow key={s.id} data-testid={`service-row-${s.id}`}>
                    <TableCell className="font-medium">{s.name}</TableCell>
                    <TableCell>{s.duration_min} min</TableCell>
                    <TableCell>R$ {Number(s.price).toFixed(2)}</TableCell>
                    <TableCell><Badge className={s.is_active ? "bg-emerald-600 hover:bg-emerald-600" : "bg-slate-400 hover:bg-slate-400"}>{s.is_active ? "Ativo" : "Inativo"}</Badge></TableCell>
                    <TableCell className="text-right space-x-1"><Button variant="ghost" size="sm" onClick={() => openEdit(s)} data-testid={`edit-service-${s.id}`}>Editar</Button><Button variant="ghost" size="icon" className="text-red-600" onClick={() => remove(s.id)} data-testid={`delete-service-${s.id}`}><Trash2 className="h-4 w-4"/></Button></TableCell>
                  </TableRow>))}</TableBody></Table>}
        </div>
      </div>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent><DialogHeader><DialogTitle>{editing ? "Editar serviço" : "Novo serviço"}</DialogTitle></DialogHeader>
          <form onSubmit={save} className="space-y-3" data-testid="service-form">
            <div className="space-y-1"><Label>Nome</Label><Input required value={form.name} onChange={(e) => setForm({...form,name:e.target.value})} data-testid="service-name-input"/></div>
            <div className="space-y-1"><Label>Descrição</Label><Textarea rows={2} value={form.description} onChange={(e) => setForm({...form,description:e.target.value})}/></div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1"><Label>Duração (min)</Label><Input type="number" min="5" max="600" required value={form.duration_min} onChange={(e) => setForm({...form,duration_min:e.target.value})} data-testid="service-duration-input"/></div>
              <div className="space-y-1"><Label>Preço (R$)</Label><Input type="number" step="0.01" min="0" required value={form.price} onChange={(e) => setForm({...form,price:e.target.value})} data-testid="service-price-input"/></div>
            </div>
            <div className="flex items-center justify-between"><Label>Ativo</Label><Switch checked={form.is_active} onCheckedChange={(v) => setForm({...form,is_active:v})} data-testid="service-active-switch"/></div>
            <div className="space-y-2"><Label>Profissionais que executam</Label>
              <div className="border rounded-md p-2 max-h-40 overflow-y-auto space-y-1">
                {pros.length === 0 && <p className="text-xs text-slate-500 px-2">Nenhum membro cadastrado.</p>}
                {pros.map(p => (
                  <label key={p.user_id} className="flex items-center gap-2 text-sm px-2 py-1 hover:bg-slate-50 rounded cursor-pointer">
                    <Checkbox checked={form.professional_ids.includes(p.user_id)} onCheckedChange={() => toggleProf(p.user_id)}/>
                    <span>{p.user_name} <span className="text-xs text-slate-500">({p.role})</span></span>
                  </label>))}
              </div>
              <p className="text-xs text-slate-500">Deixe vazio para permitir todos os profissionais.</p>
            </div>
            {error && <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md px-3 py-2">{error}</div>}
            <DialogFooter><Button type="button" variant="ghost" onClick={() => setOpen(false)}>Cancelar</Button><Button type="submit" className="bg-indigo-600 hover:bg-indigo-700" disabled={saving} data-testid="save-service-btn">{saving && <Loader2 className="h-4 w-4 mr-2 animate-spin"/>}Salvar</Button></DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </AppShell>
  );
}
