import { useCallback, useEffect, useRef, useState } from "react";
import { useLocation } from "react-router-dom";
import { toast } from "sonner";
import { Bot, Loader2, RotateCcw, Send, Sparkles, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api, formatApiError } from "@/lib/api";

const ROUTE_SUGGESTIONS = {
  "/dashboard": ["Quanto tenho de agendamentos hoje?", "Quanto faturei este mês?", "Quem trabalha hoje?"],
  "/agenda": ["Ver horários livres amanhã", "Bloquear amanhã das 15h às 19h", "Cadastrar cliente"],
  "/clients": ["Cadastre o João (11) 99999-0000", "Buscar clientes com João no nome"],
  "/services": ["Adicione corte masculino 40 reais 30 minutos", "Liste os serviços ativos"],
  "/landing": ["Melhorar os textos", "Trocar cor primária", "Analisar minhas fotos"],
  "/availability": ["Configurar horário: terça a sábado 9 às 19", "Almoço das 12 às 13"],
};

function pickSuggestions(pathname) {
  const key = Object.keys(ROUTE_SUGGESTIONS).find(k => pathname.startsWith(k));
  return ROUTE_SUGGESTIONS[key] || ROUTE_SUGGESTIONS["/dashboard"];
}

export default function FloatingAssistant() {
  const location = useLocation();
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [msg, setMsg] = useState("");
  const [sending, setSending] = useState(false);
  const [loaded, setLoaded] = useState(false);
  const [dynamicSuggestions, setDynamicSuggestions] = useState([]);
  const scrollRef = useRef(null);

  const loadHistory = useCallback(async () => {
    try { const { data } = await api.get("/assistant/history"); setMessages(data.messages || []); setLoaded(true); }
    catch { setLoaded(true); }
  }, []);

  useEffect(() => { if (open && !loaded) loadHistory(); }, [open, loaded, loadHistory]);
  useEffect(() => { if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight; }, [messages.length]);

  const send = async (text) => {
    const t = (text ?? msg).trim(); if (!t || sending) return;
    setSending(true); setMsg("");
    setMessages(prev => [...prev, { role: "user", content: t }]);
    try {
      const { data } = await api.post("/assistant/chat", { message: t, route: location.pathname });
      setMessages(data.messages || []);
      setDynamicSuggestions(data.suggestions || []);
      if (data.tools_used?.length) {
        toast.success(`✓ ${data.tools_used.length} ação(ões) executada(s)`);
      }
    } catch (e) {
      toast.error(formatApiError(e));
      setMessages(prev => [...prev, { role: "assistant", content: "Não consegui responder agora. Tente novamente." }]);
    } finally { setSending(false); }
  };

  const reset = async () => {
    if (!confirm("Reiniciar a conversa com a assistente?")) return;
    try { await api.post("/assistant/reset"); setMessages([]); setDynamicSuggestions([]); toast.success("Conversa reiniciada"); }
    catch (e) { toast.error(formatApiError(e)); }
  };

  const suggestions = dynamicSuggestions.length ? dynamicSuggestions.slice(0, 4) : pickSuggestions(location.pathname);
  const emptyChat = messages.length === 0;

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="fixed bottom-4 right-4 md:bottom-6 md:right-6 z-40 h-14 w-14 rounded-full bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg flex items-center justify-center transition hover:scale-105"
        data-testid="assistant-fab"
        aria-label="Abrir assistente"
      >
        <Sparkles className="h-6 w-6"/>
      </button>

      {open && (
        <div className="fixed inset-0 z-50 md:inset-auto md:bottom-24 md:right-6 md:w-[420px] md:h-[640px] md:rounded-2xl md:shadow-2xl bg-white flex flex-col overflow-hidden border border-slate-200" data-testid="assistant-panel">
          <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100 bg-gradient-to-r from-indigo-600 to-indigo-700 text-white">
            <div className="flex items-center gap-2"><Bot className="h-4 w-4"/><span className="font-semibold text-sm">Assistente do seu negócio</span></div>
            <div className="flex items-center gap-1">
              <button onClick={reset} className="p-1.5 rounded hover:bg-white/10" title="Reiniciar" data-testid="assistant-reset"><RotateCcw className="h-4 w-4"/></button>
              <button onClick={() => setOpen(false)} className="p-1.5 rounded hover:bg-white/10" data-testid="assistant-close"><X className="h-4 w-4"/></button>
            </div>
          </div>

          <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-3 bg-slate-50" data-testid="assistant-messages">
            {emptyChat && loaded && (
              <div className="text-center py-6">
                <div className="inline-flex h-12 w-12 bg-indigo-100 rounded-full items-center justify-center mb-3"><Sparkles className="h-5 w-5 text-indigo-600"/></div>
                <p className="text-sm text-slate-700 font-medium mb-1">Olá! Sou sua assistente digital 👋</p>
                <p className="text-xs text-slate-500 mb-4">Me diga em linguagem natural o que você precisa. Eu executo direto no sistema.</p>
              </div>
            )}
            {!loaded && <div className="flex justify-center py-6"><Loader2 className="h-5 w-5 animate-spin text-slate-400"/></div>}
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-[85%] rounded-2xl px-3 py-2 text-sm whitespace-pre-wrap ${m.role === "user" ? "bg-indigo-600 text-white" : "bg-white text-slate-800 border border-slate-200"}`}>
                  {m.content}
                  {m.tools?.length > 0 && m.role === "assistant" && (
                    <div className="mt-2 pt-2 border-t border-slate-100 text-[10px] text-slate-400 uppercase tracking-wider">
                      {m.tools.map((t, j) => <span key={j} className="inline-block mr-2">✓ {t.tool}</span>)}
                    </div>
                  )}
                </div>
              </div>))}
            {sending && <div className="flex justify-start"><div className="bg-white border border-slate-200 rounded-2xl px-3 py-2"><Loader2 className="h-4 w-4 animate-spin text-slate-400"/></div></div>}
          </div>

          {suggestions.length > 0 && !sending && (
            <div className="px-3 py-2 border-t border-slate-100 bg-white flex flex-wrap gap-1.5" data-testid="assistant-suggestions">
              {suggestions.map((s, i) => (
                <button key={i} onClick={() => send(s)} className="text-xs bg-indigo-50 text-indigo-700 hover:bg-indigo-100 px-2.5 py-1 rounded-full font-medium transition" data-testid={`assistant-suggestion-${i}`}>{s}</button>
              ))}
            </div>
          )}

          <div className="border-t border-slate-100 p-3 bg-white flex gap-2">
            <Input value={msg} onChange={(e) => setMsg(e.target.value)} onKeyDown={(e) => e.key === "Enter" && !sending && send()} placeholder="Ex: cadastre o João (11) 99999-0000" disabled={sending} data-testid="assistant-input"/>
            <Button onClick={() => send()} disabled={sending || !msg.trim()} className="bg-indigo-600 hover:bg-indigo-700" data-testid="assistant-send"><Send className="h-4 w-4"/></Button>
          </div>
        </div>
      )}
    </>
  );
}
