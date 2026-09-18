import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";
import {
  Bot, Camera, ExternalLink, Image as ImageIcon, Loader2, Send, Sparkles, Trash2, Wand2,
} from "lucide-react";
import AppShell from "@/components/AppShell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { api, formatApiError } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import LandingPreview from "@/components/LandingPreview";
import VisualEditor from "@/components/VisualEditor";

const DEFAULT_QUICK = [
  "Deixar mais moderno", "Deixar mais premium", "Trocar cor primária",
  "Melhorar os textos", "Destacar serviços", "Otimizar para celular",
];

export default function LandingBuilderPage() {
  const { company } = useAuth();
  const [data, setData] = useState(null);
  const [msg, setMsg] = useState("");
  const [sending, setSending] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [creatingPreview, setCreatingPreview] = useState(false);
  const [applyingPreview, setApplyingPreview] = useState(false);
  const [critiquing, setCritiquing] = useState(false);
  const [critique, setCritique] = useState(null);
  const [blueprintRequestId, setBlueprintRequestId] = useState(null);
  const [tab, setTab] = useState("chat");
  const fileRef = useRef(null);
  const scrollRef = useRef(null);

  const load = async () => {
    try {
      const [landingResult, specResult] = await Promise.allSettled([api.get("/landing/me"), api.get("/design/render-spec")]);
      if (landingResult.status !== "fulfilled") throw landingResult.reason;
      const landing = landingResult.value.data;
      const specifications = specResult.status === "fulfilled" ? specResult.value.data?.specifications || [] : [];
      setData({ ...landing, renderSpecification: specifications[0]?.render_specification || null });
    }
    catch (e) { toast.error(formatApiError(e)); }
  };
  useEffect(() => { load(); }, []);
  useEffect(() => { if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight; }, [data?.messages?.length]);

  const send = async (text) => {
    const t = (text ?? msg).trim(); if (!t) return;
    setSending(true); setMsg("");
    setData(d => ({ ...d, messages: [...(d?.messages || []), { role: "user", content: t }] }));
    try {
      const { data: r } = await api.post("/landing/me/chat", { message: t });
      setData(d => ({ ...d, messages: r.messages, state: r.state }));
    } catch (e) { toast.error(formatApiError(e)); }
    finally { setSending(false); }
  };

  const uploadPhoto = async (file) => {
    if (!file) return; setUploading(true);
    try {
      const fd = new FormData(); fd.append("file", file);
      const { data: r } = await api.post("/landing/me/gallery", fd, { headers: { "Content-Type": "multipart/form-data" }});
      setData(d => ({ ...d, state: { ...d.state, gallery: r.gallery }}));
      toast.success("Foto adicionada");
    } catch (e) { toast.error(formatApiError(e)); }
    finally { setUploading(false); }
  };

  const removePhoto = async (id) => {
    try { const { data: r } = await api.delete(`/landing/me/gallery/${id}`); setData(d => ({ ...d, state: { ...d.state, gallery: r.gallery }})); }
    catch (e) { toast.error(formatApiError(e)); }
  };

  const analyzePhotos = async () => {
    setAnalyzing(true);
    setData(d => ({ ...d, messages: [...(d?.messages || []), { role: "user", content: "Analise minhas fotos e ajuste a página" }] }));
    try {
      const { data: r } = await api.post("/landing/me/analyze-gallery");
      setData(d => ({ ...d, messages: r.messages, state: r.state }));
      toast.success("Fotos analisadas");
    } catch (e) { toast.error(formatApiError(e)); }
    finally { setAnalyzing(false); }
  };

  const saveState = async (state) => {
    setData(d => ({ ...d, state }));
    try { await api.put("/landing/me/state", { state }); }
    catch (e) { toast.error(formatApiError(e)); }
  };

  const publish = async () => {
    try { await api.post("/landing/me/publish"); toast.success("Página publicada!"); load(); }
    catch (e) { toast.error(formatApiError(e)); }
  };

  const runCritique = async () => {
    if (!data?.previewId) return;
    setCritiquing(true);
    try {
      const { data: result } = await api.post("/design/critique-preview", null, {
        params: { preview_id: data.previewId },
      });
      setCritique(result);
      if (result.critique?.ready_for_publish) {
        toast.success("Autocrítica concluída: página pronta para publicação");
      } else {
        toast.warning("A IA encontrou pontos para corrigir antes da publicação");
      }
    } catch (e) { toast.error(formatApiError(e)); }
    finally { setCritiquing(false); }
  };

  const createPreview = async () => {
    setCreatingPreview(true);
    try {
      const { data: blueprint } = await api.post("/design/ai-blueprint");
      const { data: preview } = await api.post("/design/create-preview", {
        render_spec_request_id: blueprint.render_spec_request_id,
      });
      setBlueprintRequestId(blueprint.request_id);
      setCritique(null);
      setData(d => ({
        ...d,
        previewId: preview.preview_id,
        renderSpecification: preview.render_spec,
      }));
      toast.success("Landing criada pelo Landing Brain e Preview gerado");
    } catch (e) { toast.error(formatApiError(e)); }
    finally { setCreatingPreview(false); }
  };

  const refineFromCritique = async () => {
    if (!blueprintRequestId || !critique?.request_id) return;
    setCreatingPreview(true);
    try {
      const { data: refined } = await api.post("/design/refine-blueprint", null, {
        params: {
          blueprint_request_id: blueprintRequestId,
          critique_request_id: critique.request_id,
        },
      });
      const { data: preview } = await api.post("/design/create-preview", {
        render_spec_request_id: refined.render_spec_request_id,
      });
      setBlueprintRequestId(refined.request_id);
      setCritique(null);
      setData(d => ({
        ...d,
        previewId: preview.preview_id,
        renderSpecification: preview.render_spec,
      }));
      toast.success("A IA refinou a landing e criou uma nova versão");
    } catch (e) { toast.error(formatApiError(e)); }
    finally { setCreatingPreview(false); }
  };

  const applyPreview = async () => {
    if (!data?.previewId) return;
    setApplyingPreview(true);
    try {
      const { data: applied } = await api.post("/design/apply-preview", {
        preview_id: data.previewId,
        request_id: (globalThis.crypto?.randomUUID && globalThis.crypto.randomUUID()) || `apply-${Date.now()}`,
        expected_draft_version: data.draft_version ?? 0,
      });
      setData(d => ({ ...d, draft_version: applied.new_version, renderSpecification: applied.render_spec }));
      toast.success("Preview aplicado ao Draft sem publicar");
    } catch (e) { toast.error(formatApiError(e)); }
    finally { setApplyingPreview(false); }
  };

  const messages = data?.messages || [];
  const emptyChat = messages.length === 0;
  const publicUrl = `/${company?.slug}`;
  const lastAssistant = [...messages].reverse().find(m => m.role === "assistant");
  const suggestions = (lastAssistant?.suggestions?.length ? lastAssistant.suggestions : DEFAULT_QUICK).slice(0, 6);

  return (
    <AppShell title="Minha Landing Page">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
          <div className="flex items-center gap-2"><Sparkles className="h-5 w-5 text-indigo-600"/><span className="text-sm text-slate-600">Crie sua página conversando com nossa IA</span></div>
          <div className="flex gap-2">
            <Button variant="outline" asChild data-testid="view-public-btn"><a href={publicUrl} target="_blank" rel="noreferrer"><ExternalLink className="h-4 w-4 mr-2"/>Visualizar</a></Button>
            <Button variant="outline" onClick={createPreview} disabled={creatingPreview} data-testid="create-preview-btn"><Wand2 className="h-4 w-4 mr-2"/>{creatingPreview ? "Gerando..." : "Gerar Preview"}</Button>
            <Button variant="outline" onClick={applyPreview} disabled={!data?.previewId || applyingPreview} data-testid="apply-preview-btn"><Wand2 className="h-4 w-4 mr-2"/>{applyingPreview ? "Aplicando..." : "Aplicar ao Draft"}</Button>
            <Button variant="outline" onClick={runCritique} disabled={!data?.previewId || critiquing} data-testid="critique-preview-btn"><Sparkles className="h-4 w-4 mr-2"/>{critiquing ? "Analisando..." : "Criticar Preview"}</Button>
            <Button variant="outline" onClick={refineFromCritique} disabled={!critique || critique.critique?.ready_for_publish || creatingPreview} data-testid="refine-preview-btn"><Wand2 className="h-4 w-4 mr-2"/>{creatingPreview ? "Refinando..." : "Corrigir com IA"}</Button>
            <Button className="bg-indigo-600 hover:bg-indigo-700" onClick={publish} disabled={!critique?.critique?.ready_for_publish} data-testid="publish-btn"><Sparkles className="h-4 w-4 mr-2"/>{data?.state?.is_published ? "Republicar" : "Publicar"}</Button>
          </div>
        </div>

        {critique?.critique && (
          <div className="mb-3 rounded-xl border border-slate-200 bg-white p-4" data-testid="landing-critique">
            <div className="flex items-center justify-between gap-3 mb-2">
              <div className="font-semibold text-sm">Revisão profissional da IA</div>
              <Badge className={critique.critique.ready_for_publish ? "bg-emerald-100 text-emerald-800" : "bg-amber-100 text-amber-800"}>
                {critique.critique.ready_for_publish ? "Pronta para publicar" : "Precisa de ajustes"}
              </Badge>
            </div>
            <p className="text-sm text-slate-600 mb-3">{critique.critique.overall_assessment}</p>
            {critique.critique.priority_actions?.length > 0 && (
              <div className="text-xs text-slate-600">
                <strong>Prioridades:</strong> {critique.critique.priority_actions.slice(0, 3).join(" • ")}
              </div>
            )}
          </div>
        )}

        <Tabs value={tab} onValueChange={setTab} className="md:hidden mb-3">
          <TabsList className="w-full"><TabsTrigger value="chat" className="flex-1">Chat</TabsTrigger><TabsTrigger value="preview" className="flex-1">Preview</TabsTrigger></TabsList>
        </Tabs>

        <div className="grid md:grid-cols-2 gap-4 h-[calc(100vh-220px)]">
          <div className={`bg-white border border-slate-200 rounded-xl flex flex-col ${tab === "preview" ? "hidden md:flex" : "flex"}`}>
            <div className="border-b border-slate-100 p-3 flex items-center justify-between">
              <div className="flex items-center gap-2"><Bot className="h-4 w-4 text-indigo-600"/><span className="font-semibold text-sm">Assistente IA</span></div>
              {data?.state?.gallery?.length > 0 && <Button size="sm" variant="outline" onClick={analyzePhotos} disabled={analyzing} data-testid="analyze-gallery-btn">{analyzing ? <Loader2 className="h-3 w-3 animate-spin mr-1"/> : <Wand2 className="h-3 w-3 mr-1"/>}Analisar fotos</Button>}
            </div>
            <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-3" data-testid="chat-messages">
              {emptyChat && <div className="text-center py-8">
                <div className="inline-flex h-14 w-14 bg-indigo-100 rounded-full items-center justify-center mb-3"><Sparkles className="h-6 w-6 text-indigo-600"/></div>
                <p className="text-sm text-slate-600 mb-4">Olá! 👋 Sou a IA que vai criar sua página profissional. Vamos começar?</p>
                <Button onClick={() => send("Olá! Quero criar minha landing page.")} className="bg-indigo-600 hover:bg-indigo-700" data-testid="start-chat-btn">Iniciar conversa</Button>
              </div>}
              {messages.map((m, i) => (
                <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                  <div className={`max-w-[85%] rounded-2xl px-4 py-2 text-sm whitespace-pre-wrap ${m.role === "user" ? "bg-indigo-600 text-white" : "bg-slate-100 text-slate-800"}`}>{m.content}</div>
                </div>))}
              {(sending || analyzing) && <div className="flex justify-start"><div className="bg-slate-100 rounded-2xl px-4 py-2"><Loader2 className="h-4 w-4 animate-spin text-slate-400"/></div></div>}
            </div>

            {!emptyChat && suggestions.length > 0 && (
              <div className="px-3 pt-2 pb-1 flex flex-wrap gap-1.5" data-testid="quick-actions">
                {suggestions.map((s, i) => (
                  <button key={i} onClick={() => send(s)} disabled={sending} className="text-xs bg-indigo-50 text-indigo-700 hover:bg-indigo-100 px-2.5 py-1 rounded-full font-medium transition" data-testid={`quick-${i}`}>{s}</button>))}
              </div>
            )}

            {data?.state?.gallery?.length > 0 && (
              <div className="px-3 py-2 border-t border-slate-100 flex gap-1.5 overflow-x-auto" data-testid="gallery-strip">
                {data.state.gallery.map(g => (
                  <div key={g.id} className="relative group flex-shrink-0">
                    <div className="h-12 w-12 rounded border bg-slate-100 flex items-center justify-center"><ImageIcon className="h-4 w-4 text-slate-400"/></div>
                    <button onClick={() => removePhoto(g.id)} className="absolute -top-1 -right-1 bg-red-600 text-white rounded-full h-4 w-4 flex items-center justify-center opacity-0 group-hover:opacity-100 transition" data-testid={`remove-${g.id}`}><Trash2 className="h-2.5 w-2.5"/></button>
                  </div>))}
              </div>
            )}

            <div className="border-t border-slate-100 p-3">
              <div className="flex gap-2">
                <input ref={fileRef} type="file" accept="image/*" className="hidden" onChange={(e) => { uploadPhoto(e.target.files?.[0]); e.target.value = ""; }} data-testid="upload-photo-input"/>
                <Button type="button" variant="outline" size="icon" onClick={() => fileRef.current?.click()} disabled={uploading} data-testid="upload-photo-btn">{uploading ? <Loader2 className="h-4 w-4 animate-spin"/> : <Camera className="h-4 w-4"/>}</Button>
                <Input value={msg} onChange={(e) => setMsg(e.target.value)} onKeyDown={(e) => e.key === "Enter" && !sending && send()} placeholder="Escreva sua resposta..." disabled={sending} data-testid="chat-input"/>
                <Button onClick={() => send()} disabled={sending || !msg.trim()} className="bg-indigo-600 hover:bg-indigo-700" data-testid="chat-send-btn"><Send className="h-4 w-4"/></Button>
              </div>
            </div>
          </div>

          <div className={`bg-slate-50 border border-slate-200 rounded-xl flex flex-col overflow-hidden ${tab === "chat" ? "hidden md:flex" : "flex"}`} data-testid="landing-preview">
            {data && <>
              <VisualEditor state={data.state} onChange={saveState}/>
              <div className="flex-1 overflow-hidden"><LandingPreview state={data.state} company={company} renderSpecification={data.renderSpecification}/></div>
            </>}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
