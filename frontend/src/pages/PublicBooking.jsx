import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import axios from "axios";
import { ArrowLeft, CheckCircle2, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";

const BACKEND = process.env.REACT_APP_BACKEND_URL;

const BIZ_LABELS = { BARBERSHOP: "Barbearia", BEAUTY_SALON: "Salão de Beleza", MANICURE: "Manicure", AESTHETICS: "Estética", PET_SHOP: "Pet Shop" };

export default function PublicBookingPage() {
  const { slug } = useParams();
  const isCustomDomain = !slug;
  const [ctx, setCtx] = useState(null);
  const [err, setErr] = useState("");
  const [step, setStep] = useState(1);
  const [service, setService] = useState(null);
  const [professional, setProfessional] = useState(null);
  const [date, setDate] = useState(() => new Date().toISOString().split("T")[0]);
  const [slots, setSlots] = useState([]);
  const [slotsLoading, setSlotsLoading] = useState(false);
  const [chosenTime, setChosenTime] = useState("");
  const [client, setClient] = useState({ name: "", phone: "", email: "", notes: "" });
  const [submitting, setSubmitting] = useState(false);
  const [confirmed, setConfirmed] = useState(null);

  useEffect(() => {
    (async () => {
      try {
        const { data } = await axios.get(`${BACKEND}/api/public/${isCustomDomain ? "domain" : `${slug}/booking-context`}`);
        setCtx(data); document.title = `Agendar - ${data.company.name}`;
      } catch (e) { setErr(e?.response?.data?.detail || "Página não disponível"); }
    })();
  }, [slug]);

  const availablePros = useMemo(() => {
    if (!ctx || !service) return [];
    const allowed = service.professional_ids || [];
    return allowed.length ? ctx.professionals.filter(p => allowed.includes(p.id)) : ctx.professionals;
  }, [ctx, service]);

  useEffect(() => {
    if (step !== 3 || !service || !professional || !date) return;
    (async () => {
      setSlotsLoading(true);
      try {
        const { data } = await axios.get(`${BACKEND}/api/public/${isCustomDomain ? "domain/slots" : `${slug}/slots`}`, {
          params: { service_id: service.id, professional_id: professional.id, date },
        });
        setSlots(data.slots);
      } catch (e) { toast.error(e?.response?.data?.detail || "Erro ao buscar horários"); }
      finally { setSlotsLoading(false); }
    })();
  }, [step, service, professional, date, slug]);

  const submit = async () => {
    setSubmitting(true);
    try {
      const { data } = await axios.post(`${BACKEND}/api/public/${isCustomDomain ? "domain/book" : `${slug}/book`}`, {
        service_id: service.id, professional_id: professional.id, date, start_time: chosenTime,
        client_name: client.name, client_phone: client.phone,
        client_email: client.email || null, notes: client.notes || null,
      });
      setConfirmed(data);
    } catch (e) { toast.error(e?.response?.data?.detail || "Erro ao agendar"); }
    finally { setSubmitting(false); }
  };

  if (err) return <div className="min-h-screen flex items-center justify-center text-slate-500 p-6">{err}</div>;
  if (!ctx) return <div className="min-h-screen flex items-center justify-center"><Loader2 className="h-6 w-6 animate-spin text-slate-400"/></div>;

  if (confirmed) return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4 py-12">
      <div className="max-w-lg w-full bg-white rounded-2xl border border-slate-200 p-8 text-center shadow-sm" data-testid="booking-success">
        <div className="inline-flex h-16 w-16 rounded-full bg-emerald-100 items-center justify-center mb-4"><CheckCircle2 className="h-8 w-8 text-emerald-600"/></div>
        <h1 className="text-2xl font-extrabold mb-2" style={{ fontFamily: "'Plus Jakarta Sans'" }}>Agendamento confirmado!</h1>
        <p className="text-slate-500 mb-6">Enviaremos os detalhes para você. O estabelecimento também foi notificado.</p>
        <div className="text-left bg-slate-50 rounded-xl p-4 space-y-2 text-sm">
          <p><strong>Estabelecimento:</strong> {confirmed.company_name}</p>
          <p><strong>Serviço:</strong> {confirmed.service_name}</p>
          <p><strong>Profissional:</strong> {confirmed.professional_name}</p>
          <p><strong>Data:</strong> {new Date(confirmed.date + "T12:00").toLocaleDateString("pt-BR")}</p>
          <p><strong>Horário:</strong> {confirmed.start_time} → {confirmed.end_time}</p>
          <p><Badge className="bg-amber-100 text-amber-800">Pendente de confirmação</Badge></p>
        </div>
        <Link to={isCustomDomain ? "/" : `/${slug}`} className="inline-block mt-6 text-indigo-600 hover:text-indigo-700 text-sm font-medium">Voltar à página</Link>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-white border-b border-slate-200 px-4 md:px-8 py-4 flex items-center justify-between">
        <Link to={isCustomDomain ? "/" : `/${slug}`} className="text-sm text-slate-600 hover:text-slate-900 flex items-center gap-2"><ArrowLeft className="h-4 w-4"/>Voltar</Link>
        <div className="text-right">
          <p className="text-xs uppercase tracking-widest text-slate-400">{BIZ_LABELS[ctx.company.business_type]}</p>
          <p className="font-bold" style={{ fontFamily: "'Plus Jakarta Sans'" }}>{ctx.company.name}</p>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-8">
        <div className="flex items-center gap-2 mb-6" data-testid="booking-stepper">
          {[1,2,3,4].map(i => (
            <div key={i} className={`h-1 rounded-full flex-1 ${step >= i ? "bg-indigo-600" : "bg-slate-200"}`}/>
          ))}
        </div>

        {step === 1 && <section data-testid="step-service">
          <h2 className="text-2xl font-bold mb-4" style={{ fontFamily: "'Plus Jakarta Sans'" }}>Escolha o serviço</h2>
          {ctx.services.length === 0 && <p className="text-slate-500">Nenhum serviço disponível.</p>}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {ctx.services.map(s => (
              <button key={s.id} onClick={() => { setService(s); setProfessional(null); setStep(2); }} className={`text-left border-2 rounded-xl p-4 transition ${service?.id === s.id ? "border-indigo-600 bg-indigo-50" : "border-slate-200 hover:border-slate-300 bg-white"}`} data-testid={`service-${s.id}`}>
                <p className="font-bold text-slate-900">{s.name}</p>
                {s.description && <p className="text-sm text-slate-500 mt-1">{s.description}</p>}
                <div className="flex justify-between mt-3 text-sm"><span className="text-slate-500">{s.duration_min} min</span><span className="font-bold text-indigo-600">R$ {Number(s.price).toFixed(2)}</span></div>
              </button>))}
          </div>
        </section>}

        {step === 2 && <section data-testid="step-pro">
          <button onClick={() => setStep(1)} className="text-sm text-slate-500 hover:text-slate-700 mb-3 flex items-center gap-1"><ArrowLeft className="h-3 w-3"/>Voltar</button>
          <h2 className="text-2xl font-bold mb-4" style={{ fontFamily: "'Plus Jakarta Sans'" }}>Escolha o profissional</h2>
          {availablePros.length === 0 && <p className="text-slate-500">Nenhum profissional disponível para este serviço.</p>}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {availablePros.map(p => (
              <button key={p.id} onClick={() => { setProfessional(p); setStep(3); }} className={`text-left border-2 rounded-xl p-4 transition ${professional?.id === p.id ? "border-indigo-600 bg-indigo-50" : "border-slate-200 hover:border-slate-300 bg-white"}`} data-testid={`pro-${p.id}`}>
                <p className="font-bold text-slate-900">{p.name}</p>
                <p className="text-xs uppercase tracking-widest text-slate-400 mt-1">{p.role}</p>
              </button>))}
          </div>
        </section>}

        {step === 3 && <section data-testid="step-slot">
          <button onClick={() => setStep(2)} className="text-sm text-slate-500 hover:text-slate-700 mb-3 flex items-center gap-1"><ArrowLeft className="h-3 w-3"/>Voltar</button>
          <h2 className="text-2xl font-bold mb-4" style={{ fontFamily: "'Plus Jakarta Sans'" }}>Escolha data e horário</h2>
          <div className="space-y-4">
            <div><Label>Data</Label><Input type="date" min={new Date().toISOString().split("T")[0]} value={date} onChange={(e) => { setDate(e.target.value); setChosenTime(""); }} data-testid="booking-date-input"/></div>
            {slotsLoading ? <div className="flex items-center gap-2 text-slate-500"><Loader2 className="h-4 w-4 animate-spin"/>Buscando horários…</div>
              : slots.length === 0 ? <p className="text-slate-500 py-4 text-center bg-white border rounded-lg">Nenhum horário disponível nessa data.</p>
              : <div>
                <Label>Horários disponíveis</Label>
                <div className="grid grid-cols-3 md:grid-cols-6 gap-2 mt-2">
                  {slots.map(t => (
                    <button key={t} type="button" onClick={() => setChosenTime(t)} className={`py-2 rounded-md text-sm font-medium border transition ${chosenTime === t ? "bg-indigo-600 text-white border-indigo-600" : "bg-white border-slate-200 hover:border-indigo-500"}`} data-testid={`slot-${t}`}>{t}</button>))}
                </div>
              </div>}
            <Button className="w-full bg-indigo-600 hover:bg-indigo-700" disabled={!chosenTime} onClick={() => setStep(4)} data-testid="continue-to-form-btn">Continuar</Button>
          </div>
        </section>}

        {step === 4 && <section data-testid="step-form">
          <button onClick={() => setStep(3)} className="text-sm text-slate-500 hover:text-slate-700 mb-3 flex items-center gap-1"><ArrowLeft className="h-3 w-3"/>Voltar</button>
          <h2 className="text-2xl font-bold mb-4" style={{ fontFamily: "'Plus Jakarta Sans'" }}>Seus dados</h2>
          <div className="space-y-3 bg-white p-5 rounded-xl border border-slate-200">
            <div><Label>Nome completo</Label><Input required value={client.name} onChange={(e) => setClient({ ...client, name: e.target.value })} data-testid="client-name-input"/></div>
            <div><Label>Telefone / WhatsApp</Label><Input required value={client.phone} onChange={(e) => setClient({ ...client, phone: e.target.value })} placeholder="(11) 99999-0000" data-testid="client-phone-input"/></div>
            <div><Label>E-mail (opcional)</Label><Input type="email" value={client.email} onChange={(e) => setClient({ ...client, email: e.target.value })}/></div>
            <div><Label>Observações (opcional)</Label><Textarea rows={2} value={client.notes} onChange={(e) => setClient({ ...client, notes: e.target.value })}/></div>
            <div className="bg-slate-50 rounded-lg p-3 text-sm space-y-1">
              <p><strong>Resumo:</strong></p>
              <p>{service.name} · {service.duration_min} min · R$ {Number(service.price).toFixed(2)}</p>
              <p>Com {professional.name}</p>
              <p>{new Date(date + "T12:00").toLocaleDateString("pt-BR")} às {chosenTime}</p>
            </div>
            <Button className="w-full bg-indigo-600 hover:bg-indigo-700" disabled={submitting || !client.name || !client.phone} onClick={submit} data-testid="confirm-booking-btn">
              {submitting && <Loader2 className="h-4 w-4 mr-2 animate-spin"/>}Confirmar agendamento
            </Button>
          </div>
        </section>}
      </main>
    </div>
  );
}
