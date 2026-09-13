import { useState } from "react";
import { Settings2, Palette, LayoutGrid, ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";

const SECTION_LABELS = { hero: "Hero", about: "Sobre", services: "Serviços", professionals: "Profissionais", gallery: "Galeria", differentiators: "Diferenciais", hours: "Horários", contact: "Contato" };

export default function VisualEditor({ state, onChange }) {
  const [open, setOpen] = useState(false);
  if (!state) return null;
  const style = state.style || {};
  const sections = state.sections || {};

  const patch = (path, value) => {
    const next = JSON.parse(JSON.stringify(state));
    const parts = path.split(".");
    let cur = next;
    for (let i = 0; i < parts.length - 1; i++) { cur[parts[i]] = cur[parts[i]] || {}; cur = cur[parts[i]]; }
    cur[parts[parts.length - 1]] = value;
    onChange(next);
  };

  return (
    <div className="border-b border-slate-200 bg-white">
      <button onClick={() => setOpen(v => !v)} className="w-full px-4 py-2 flex items-center justify-between text-sm font-medium hover:bg-slate-50" data-testid="visual-editor-toggle">
        <span className="flex items-center gap-2"><Settings2 className="h-4 w-4 text-indigo-600"/>Editor visual</span>
        <ChevronDown className={`h-4 w-4 transition ${open ? "rotate-180" : ""}`}/>
      </button>
      {open && <div className="p-4 space-y-4 text-sm border-t border-slate-100 bg-slate-50">
        <div>
          <div className="flex items-center gap-2 mb-2 font-semibold text-slate-700"><Palette className="h-4 w-4"/>Cores</div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1"><Label className="text-xs">Primária</Label>
              <div className="flex items-center gap-2"><input type="color" value={style.primary_color || "#4f46e5"} onChange={(e) => patch("style.primary_color", e.target.value)} className="h-9 w-12 rounded border cursor-pointer" data-testid="color-primary"/><input value={style.primary_color || "#4f46e5"} onChange={(e) => patch("style.primary_color", e.target.value)} className="flex-1 border rounded px-2 py-1 text-xs font-mono"/></div>
            </div>
            <div className="space-y-1"><Label className="text-xs">Secundária</Label>
              <div className="flex items-center gap-2"><input type="color" value={style.secondary_color || "#0f172a"} onChange={(e) => patch("style.secondary_color", e.target.value)} className="h-9 w-12 rounded border cursor-pointer" data-testid="color-secondary"/><input value={style.secondary_color || "#0f172a"} onChange={(e) => patch("style.secondary_color", e.target.value)} className="flex-1 border rounded px-2 py-1 text-xs font-mono"/></div>
            </div>
          </div>
        </div>

        <div>
          <div className="flex items-center gap-2 mb-2 font-semibold text-slate-700"><LayoutGrid className="h-4 w-4"/>Seções</div>
          <div className="grid grid-cols-2 gap-2">
            {Object.keys(SECTION_LABELS).map(k => (
              <label key={k} className="flex items-center justify-between bg-white rounded px-2 py-1.5 border border-slate-200">
                <span>{SECTION_LABELS[k]}</span>
                <Switch checked={sections[k] !== false} onCheckedChange={(v) => patch(`sections.${k}`, v)} data-testid={`toggle-${k}`}/>
              </label>))}
          </div>
        </div>

        {state.gallery?.length > 0 && <div>
          <p className="font-semibold text-slate-700 mb-2">Imagem principal do Hero</p>
          <div className="grid grid-cols-4 gap-2">
            {state.gallery.slice(0, 8).map(g => (
              <button key={g.id} onClick={() => patch("hero.featured_image", g.url)} className={`aspect-square rounded overflow-hidden border-2 ${state.hero?.featured_image === g.url ? "border-indigo-600" : "border-transparent"}`} data-testid={`hero-img-${g.id}`}>
                <div className="w-full h-full bg-slate-200"/>
              </button>))}
          </div>
        </div>}
      </div>}
    </div>
  );
}
