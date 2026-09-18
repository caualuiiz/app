import { useEffect, useState } from "react";
import { CreditCard, Globe2, Loader2, MessageCircle, Save } from "lucide-react";
import AppShell from "@/components/AppShell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api, formatApiError } from "@/lib/api";
import { toast } from "sonner";

export default function CommercialSettings() {
  const [billing, setBilling] = useState(null);
  const [domains, setDomains] = useState([]);
  const [domain, setDomain] = useState("");
  const [whatsapp, setWhatsapp] = useState({ phone_number_id: "", access_token: "", notification_numbers: "" });
  const [loading, setLoading] = useState(true);
  const [savingWhatsapp, setSavingWhatsapp] = useState(false);

  const load = async () => {
    try {
      const [b, d, w] = await Promise.all([api.get("/billing"), api.get("/domains"), api.get("/whatsapp/config")]);
      setBilling(b.data);
      setDomains(d.data || []);
      setWhatsapp({
        phone_number_id: w.data?.phone_number_id || "",
        access_token: "",
        notification_numbers: (w.data?.notification_numbers || []).join(", "),
      });
    } catch (err) { toast.error(formatApiError(err)); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const checkout = async (plan) => {
    try {
      const { data } = await api.post("/billing/checkout", { plan });
      window.location.href = data.url;
    } catch (err) { toast.error(formatApiError(err)); }
  };

  const addDomain = async () => {
    if (!domain.trim()) return;
    try {
      await api.post("/domains", { domain });
      setDomain("");
      await load();
      toast.success("Domínio adicionado. Configure o TXT indicado e verifique.");
    } catch (err) { toast.error(formatApiError(err)); }
  };

  const verifyDomain = async (id) => {
    try { await api.post(`/domains/${id}/verify`); await load(); toast.success("Domínio verificado."); }
    catch (err) { toast.error(formatApiError(err)); }
  };

  const removeDomain = async (id) => {
    try { await api.delete(`/domains/${id}`); await load(); }
    catch (err) { toast.error(formatApiError(err)); }
  };

  const saveWhatsapp = async () => {
    if (!whatsapp.access_token.trim()) { toast.error("Informe o token de acesso para salvar a configuração."); return; }
    setSavingWhatsapp(true);
    try {
      await api.put("/whatsapp/config", {
        phone_number_id: whatsapp.phone_number_id,
        access_token: whatsapp.access_token,
        notification_numbers: whatsapp.notification_numbers.split(",").map((n) => n.trim()).filter(Boolean),
      });
      setWhatsapp((v) => ({ ...v, access_token: "" }));
      toast.success("WhatsApp salvo com segurança.");
      await load();
    } catch (err) { toast.error(formatApiError(err)); }
    finally { setSavingWhatsapp(false); }
  };

  if (loading) return <AppShell title="Configuração comercial"><div className="flex items-center gap-2 text-slate-500"><Loader2 className="h-4 w-4 animate-spin"/>Carregando…</div></AppShell>;

  return (
    <AppShell title="Configuração comercial">
      <div className="max-w-5xl mx-auto space-y-6">
        <Card>
          <CardHeader><CardTitle className="flex items-center gap-2"><CreditCard className="h-5 w-5"/>Plano</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-3"><Badge>{billing?.plan || "TRIAL"}</Badge><span className="text-sm text-slate-500">{billing?.status || "trialing"}</span></div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <Button variant="outline" onClick={() => checkout("STARTER")}>Assinar Starter</Button>
              <Button className="bg-indigo-600 hover:bg-indigo-700" onClick={() => checkout("PRO")}>Assinar Pro</Button>
            </div>
            {billing?.status && billing.status !== "trialing" && <Button variant="ghost" onClick={async () => { try { const { data } = await api.post("/billing/portal"); window.location.href = data.url; } catch (err) { toast.error(formatApiError(err)); } }}>Gerenciar cobrança</Button>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="flex items-center gap-2"><Globe2 className="h-5 w-5"/>Domínio personalizado</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2"><Input value={domain} onChange={(e) => setDomain(e.target.value)} placeholder="www.suapagina.com.br"/><Button onClick={addDomain}>Adicionar</Button></div>
            <div className="space-y-3">
              {domains.map((item) => <div key={item.id} className="rounded-xl border p-4 space-y-2">
                <div className="flex items-center justify-between gap-3"><div className="font-medium">{item.domain}</div><Badge>{item.status}</Badge></div>
                {item.status === "PENDING" && <div className="text-sm text-slate-600 space-y-1">
                  <div>Tipo: TXT</div><div>Nome: <code>{item.verification_record}</code></div><div>Valor: <code className="break-all">{item.verification_value}</code></div>
                  <div className="flex gap-2 pt-2"><Button size="sm" onClick={() => verifyDomain(item.id)}>Verificar</Button><Button size="sm" variant="ghost" onClick={() => removeDomain(item.id)}>Remover</Button></div>
                </div>}
              </div>)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="flex items-center gap-2"><MessageCircle className="h-5 w-5"/>WhatsApp</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2"><Label>Phone Number ID</Label><Input value={whatsapp.phone_number_id} onChange={(e) => setWhatsapp({...whatsapp, phone_number_id: e.target.value})}/></div>
            <div className="space-y-2"><Label>Token de acesso</Label><Input type="password" value={whatsapp.access_token} onChange={(e) => setWhatsapp({...whatsapp, access_token: e.target.value})} placeholder="Cole apenas durante a configuração"/></div>
            <div className="space-y-2"><Label>Números que recebem novos agendamentos</Label><Input value={whatsapp.notification_numbers} onChange={(e) => setWhatsapp({...whatsapp, notification_numbers: e.target.value})} placeholder="+5511999999999, +5521999999999"/></div>
            <Button onClick={saveWhatsapp} disabled={savingWhatsapp}>{savingWhatsapp ? <Loader2 className="h-4 w-4 mr-2 animate-spin"/> : <Save className="h-4 w-4 mr-2"/>}Salvar WhatsApp</Button>
            <p className="text-xs text-slate-500">O token é criptografado antes de ser armazenado.</p>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}