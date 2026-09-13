import { useEffect, useState } from "react";
import { toast } from "sonner";
import { Loader2, Save } from "lucide-react";
import AppShell from "@/components/AppShell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import { api, formatApiError } from "@/lib/api";

const WD = [["MON","Segunda"],["TUE","Terça"],["WED","Quarta"],["THU","Quinta"],["FRI","Sexta"],["SAT","Sábado"],["SUN","Domingo"]];
const empty = () => Object.fromEntries(WD.map(([k]) => [k, { active: k !== "SUN", open: "08:00", close: k === "SAT" ? "14:00" : "18:00", break_start: "", break_end: "" }]));

function DayRow({ day, label, value, onChange }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-6 items-center gap-3 border-b border-slate-100 py-3">
      <div className="flex items-center gap-3"><Switch checked={value.active} onCheckedChange={(v) => onChange({ ...value, active: v })} data-testid={`day-${day}-active`}/><span className="font-medium">{label}</span></div>
      <div><Label className="text-xs">Abertura</Label><Input type="time" disabled={!value.active} value={value.open} onChange={(e) => onChange({ ...value, open: e.target.value })} data-testid={`day-${day}-open`}/></div>
      <div><Label className="text-xs">Fechamento</Label><Input type="time" disabled={!value.active} value={value.close} onChange={(e) => onChange({ ...value, close: e.target.value })} data-testid={`day-${day}-close`}/></div>
      <div><Label className="text-xs">Almoço início</Label><Input type="time" disabled={!value.active} value={value.break_start || ""} onChange={(e) => onChange({ ...value, break_start: e.target.value })}/></div>
      <div><Label className="text-xs">Almoço fim</Label><Input type="time" disabled={!value.active} value={value.break_end || ""} onChange={(e) => onChange({ ...value, break_end: e.target.value })}/></div>
    </div>
  );
}

export default function AvailabilityPage() {
  const [companyHours, setCompanyHours] = useState(empty());
  const [pros, setPros] = useState([]);
  const [selectedPro, setSelectedPro] = useState("");
  const [proHours, setProHours] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const [c, m] = await Promise.all([api.get("/availability/company"), api.get("/memberships")]);
      setCompanyHours({ ...empty(), ...c.data.hours });
      setPros(m.data);
    } catch (e) { toast.error(formatApiError(e)); }
    finally { setLoading(false); }
  };
  useEffect(() => { load(); }, []);

  const saveCompany = async () => {
    setSaving(true);
    try {
      const payload = { hours: {} };
      Object.entries(companyHours).forEach(([k, v]) => {
        payload.hours[k] = { ...v, break_start: v.break_start || null, break_end: v.break_end || null };
      });
      await api.put("/availability/company", payload);
      toast.success("Horários da empresa salvos");
    } catch (e) { toast.error(formatApiError(e)); }
    finally { setSaving(false); }
  };

  useEffect(() => {
    if (!selectedPro) { setProHours(null); return; }
    (async () => {
      try {
        const { data } = await api.get(`/availability/professional/${selectedPro}`);
        setProHours(data.hours ? { ...empty(), ...data.hours } : empty());
      } catch (e) { toast.error(formatApiError(e)); }
    })();
  }, [selectedPro]);

  const saveProHours = async () => {
    setSaving(true);
    try {
      const payload = { hours: {} };
      Object.entries(proHours).forEach(([k, v]) => {
        payload.hours[k] = { ...v, break_start: v.break_start || null, break_end: v.break_end || null };
      });
      await api.put(`/availability/professional/${selectedPro}`, payload);
      toast.success("Disponibilidade do profissional salva");
    } catch (e) { toast.error(formatApiError(e)); }
    finally { setSaving(false); }
  };

  if (loading) return <AppShell title="Disponibilidade"><div className="flex items-center gap-2 text-slate-500"><Loader2 className="h-4 w-4 animate-spin"/>Carregando…</div></AppShell>;

  return (
    <AppShell title="Disponibilidade">
      <div className="max-w-5xl mx-auto space-y-6">
        <Tabs defaultValue="company">
          <TabsList><TabsTrigger value="company" data-testid="tab-company-hours">Empresa</TabsTrigger><TabsTrigger value="pro" data-testid="tab-pro-hours">Por profissional</TabsTrigger></TabsList>
          <TabsContent value="company">
            <Card><CardContent className="p-6">
              {WD.map(([k, l]) => <DayRow key={k} day={k} label={l} value={companyHours[k]} onChange={(v) => setCompanyHours({ ...companyHours, [k]: v })}/>)}
              <div className="pt-4 flex justify-end"><Button className="bg-indigo-600 hover:bg-indigo-700" onClick={saveCompany} disabled={saving} data-testid="save-company-hours-btn">{saving ? <Loader2 className="h-4 w-4 mr-2 animate-spin"/> : <Save className="h-4 w-4 mr-2"/>}Salvar</Button></div>
            </CardContent></Card>
          </TabsContent>
          <TabsContent value="pro">
            <Card><CardContent className="p-6 space-y-4">
              <div className="space-y-1"><Label>Selecione o profissional</Label>
                <Select value={selectedPro} onValueChange={setSelectedPro}>
                  <SelectTrigger data-testid="select-pro"><SelectValue placeholder="Escolha um membro"/></SelectTrigger>
                  <SelectContent>{pros.map(p => <SelectItem key={p.user_id} value={p.user_id}>{p.user_name}</SelectItem>)}</SelectContent>
                </Select>
              </div>
              {proHours && <>
                {WD.map(([k, l]) => <DayRow key={k} day={k} label={l} value={proHours[k]} onChange={(v) => setProHours({ ...proHours, [k]: v })}/>)}
                <div className="pt-4 flex justify-end"><Button className="bg-indigo-600 hover:bg-indigo-700" onClick={saveProHours} disabled={saving} data-testid="save-pro-hours-btn">{saving ? <Loader2 className="h-4 w-4 mr-2 animate-spin"/> : <Save className="h-4 w-4 mr-2"/>}Salvar disponibilidade</Button></div>
              </>}
            </CardContent></Card>
          </TabsContent>
        </Tabs>
      </div>
    </AppShell>
  );
}
