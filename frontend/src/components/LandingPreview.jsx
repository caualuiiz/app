import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { businessTypeLabel } from "@/lib/api";
import AISpecRenderer from "@/components/AISpecRenderer";
import { isSafeRenderSpec } from "@/lib/renderSpec";

function AuthedImg({ path, className }) {
  const [src, setSrc] = useState(null);
  useEffect(() => {
    if (!path) return;
    let url;
    (async () => {
      try {
        const u = path.startsWith("/api/") ? path.replace(/^\/api/, "") : `/uploads/file/${path}`;
        const r = await api.get(u, { responseType: "blob" });
        url = URL.createObjectURL(r.data); setSrc(url);
      } catch {}
    })();
    return () => { if (url) URL.revokeObjectURL(url); };
  }, [path]);
  return src ? <img src={src} className={className} alt=""/> : <div className={`${className} bg-slate-200 animate-pulse`}/>;
}

export default function LandingPreview({ state, company, publicMode = false, services = [], resolveUrl, renderSpecification }) {
  if (isSafeRenderSpec(renderSpecification)) {
    return <AISpecRenderer specification={renderSpecification} state={state} company={company} services={services} publicMode={publicMode} resolveUrl={resolveUrl}/>;
  }
  const s = state || {};
  const sec = s.sections || {};
  const primary = s.style?.primary_color || "#4f46e5";
  const secondary = s.style?.secondary_color || "#0f172a";
  const heroImage = s.hero?.featured_image || company?.establishment_photo_url;
  const bookHref = publicMode ? `/${company?.slug}/agendar` : "#";
  const ImgTag = publicMode
    ? ({ path, className }) => (<img src={resolveUrl ? resolveUrl(path) : path} className={className} alt=""/>)
    : AuthedImg;

  return (
    <div className="h-full overflow-y-auto bg-white text-slate-900" data-testid="preview-root">
      {sec.hero !== false && (
        <section className="relative min-h-[380px] md:min-h-[480px] flex items-center px-6 md:px-12 py-16 text-white" style={{ background: `linear-gradient(135deg, ${primary} 0%, ${secondary} 100%)` }}>
          {heroImage && (
            <div className="absolute inset-0 opacity-30">
              <ImgTag path={heroImage} className="w-full h-full object-cover"/>
            </div>
          )}
          <div className="relative max-w-3xl">
            {company?.logo_url && <div className="mb-4 h-16 w-16 rounded-lg bg-white/20 backdrop-blur overflow-hidden"><ImgTag path={company.logo_url} className="w-full h-full object-contain"/></div>}
            <p className="text-xs uppercase tracking-widest opacity-80 mb-2">{businessTypeLabel(company?.business_type)}</p>
            <h1 className="text-3xl md:text-5xl font-extrabold mb-3" style={{ fontFamily: "'Plus Jakarta Sans'" }}>{s.hero?.title || company?.name || "Sua Empresa"}</h1>
            {s.hero?.subtitle && <p className="text-lg md:text-xl opacity-95 mb-3">{s.hero.subtitle}</p>}
            {s.hero?.description && <p className="opacity-85 mb-6 max-w-2xl">{s.hero.description}</p>}
            <a href={bookHref} className="inline-block bg-white text-slate-900 px-6 py-3 rounded-lg font-semibold hover:bg-slate-100 transition" data-testid="hero-cta">{s.hero?.cta || "Agendar horário"}</a>
          </div>
        </section>
      )}

      {sec.about !== false && s.about?.text && (
        <section className="px-6 md:px-12 py-12 max-w-4xl mx-auto">
          <h2 className="text-2xl md:text-3xl font-bold mb-4" style={{ fontFamily: "'Plus Jakarta Sans'" }}>Sobre o negócio</h2>
          <p className="text-slate-600 leading-relaxed whitespace-pre-wrap">{s.about.text}</p>
        </section>
      )}

      {sec.differentiators !== false && s.differentiators?.length > 0 && (
        <section className="px-6 md:px-12 py-12 bg-slate-50">
          <div className="max-w-5xl mx-auto">
            <h2 className="text-2xl md:text-3xl font-bold mb-6" style={{ fontFamily: "'Plus Jakarta Sans'" }}>Diferenciais</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {s.differentiators.map((d, i) => (
                <div key={i} className="bg-white rounded-xl p-5 border border-slate-200">
                  <div className="h-8 w-8 rounded-lg mb-3 flex items-center justify-center font-bold" style={{ background: `${primary}22`, color: primary }}>{i+1}</div>
                  <p className="text-slate-700">{d}</p>
                </div>))}
            </div>
          </div>
        </section>
      )}

      {sec.services !== false && services?.length > 0 && (
        <section className="px-6 md:px-12 py-12">
          <div className="max-w-5xl mx-auto">
            <h2 className="text-2xl md:text-3xl font-bold mb-6" style={{ fontFamily: "'Plus Jakarta Sans'" }}>Serviços</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {services.map(sv => (
                <div key={sv.id} className="border border-slate-200 rounded-xl p-5 hover:shadow-md transition flex flex-col">
                  <h3 className="font-bold text-lg mb-1">{sv.name}</h3>
                  {sv.description && <p className="text-sm text-slate-500 mb-3">{sv.description}</p>}
                  <div className="flex items-center justify-between text-sm mt-auto">
                    <span className="text-slate-500">{sv.duration_min} min</span>
                    <span className="font-bold" style={{ color: primary }}>R$ {Number(sv.price).toFixed(2)}</span>
                  </div>
                  {publicMode && <a href={`${bookHref}?service=${sv.id}`} className="mt-3 block text-center py-2 rounded-md font-semibold text-white" style={{ background: primary }}>Agendar</a>}
                </div>))}
            </div>
          </div>
        </section>
      )}

      {sec.gallery !== false && s.gallery?.length > 0 && (
        <section className="px-6 md:px-12 py-12 bg-slate-50">
          <div className="max-w-5xl mx-auto">
            <h2 className="text-2xl md:text-3xl font-bold mb-6" style={{ fontFamily: "'Plus Jakarta Sans'" }}>Galeria</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {s.gallery.map((g, i) => <div key={i} className="aspect-square overflow-hidden rounded-lg"><ImgTag path={g.url} className="w-full h-full object-cover"/></div>)}
            </div>
          </div>
        </section>
      )}

      {sec.contact !== false && (
        <section className="px-6 md:px-12 py-12">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-2xl md:text-3xl font-bold mb-4" style={{ fontFamily: "'Plus Jakarta Sans'" }}>Contato</h2>
            <div className="space-y-2 text-slate-700">
              {company?.phone && <p><strong>Telefone:</strong> {company.phone}</p>}
              {company?.address && <p><strong>Endereço:</strong> {company.address}{company.city && `, ${company.city}`}{company.state && ` - ${company.state}`}</p>}
              {s.contact?.whatsapp && <p><strong>WhatsApp:</strong> {s.contact.whatsapp}</p>}
              {s.contact?.instagram && <p><strong>Instagram:</strong> @{s.contact.instagram.replace(/^@/, "")}</p>}
            </div>
            {publicMode && <a href={bookHref} className="inline-block mt-6 px-6 py-3 rounded-lg font-semibold text-white" style={{ background: primary }} data-testid="contact-cta">Agendar agora</a>}
          </div>
        </section>
      )}

      <footer className="px-6 md:px-12 py-6 text-slate-400 text-center text-sm" style={{ background: secondary }}>
        © {new Date().getFullYear()} {company?.name} · Feito com Gestão SaaS
      </footer>
    </div>
  );
}
