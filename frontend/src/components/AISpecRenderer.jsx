import { businessTypeLabel } from "@/lib/api";
import { layoutClass, resolveRenderReference } from "@/lib/renderSpec";

function ImageSlot({ path, resolveUrl, className = "w-full h-full object-cover" }) {
  if (!path) return <div className={`${className} bg-slate-100`} aria-hidden="true"/>;
  const src = resolveUrl ? resolveUrl(path?.url || path) : path?.url || path;
  return <img src={src} className={className} alt="" loading="lazy"/>;
}

function SectionContent({ section, state, company, services, publicMode, resolveUrl, colors }) {
  const type = section.section_type;
  const bookHref = publicMode ? `/${company?.slug}/agendar` : "#";
  if (type === "hero") return <>
    <p className="text-xs uppercase tracking-widest opacity-80 mb-2">{businessTypeLabel(company?.business_type)}</p>
    <h1 className="text-3xl md:text-6xl font-extrabold mb-3">{resolveRenderReference("landing.hero.title", { state, company, services }) || company?.name || "Sua Empresa"}</h1>
    {state?.hero?.subtitle && <p className="text-lg md:text-xl mb-3 opacity-95">{state.hero.subtitle}</p>}
    {state?.hero?.description && <p className="mb-6 max-w-2xl opacity-90">{state.hero.description}</p>}
    <a href={bookHref} className="inline-block bg-white text-slate-900 px-6 py-3 rounded-lg font-semibold" data-testid="ai-spec-hero-cta">{state?.hero?.cta || "Agendar horário"}</a>
  </>;
  if (type === "about") return <><h2 className="text-2xl md:text-3xl font-bold mb-4">Sobre o negócio</h2><p className="leading-relaxed whitespace-pre-wrap opacity-80">{state?.about?.text || ""}</p></>;
  if (type === "services") return <><h2 className="text-2xl md:text-3xl font-bold mb-6">Serviços</h2><div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">{services.map((sv) => <div key={sv.id} className="border rounded-xl p-5"><h3 className="font-bold text-lg">{sv.name}</h3>{sv.description && <p className="text-sm opacity-70 mt-2">{sv.description}</p>}<p className="mt-4 font-semibold" style={{ color: colors.primary }}>R$ {Number(sv.price).toFixed(2)}</p></div>)}</div></>;
  if (type === "gallery") return <><h2 className="text-2xl md:text-3xl font-bold mb-6">Galeria</h2><div className="grid grid-cols-2 md:grid-cols-4 gap-3">{(state?.gallery || []).map((image, index) => <div key={image.id || index} className="aspect-square overflow-hidden rounded-lg"><ImageSlot path={image} resolveUrl={resolveUrl}/></div>)}</div></>;
  if (type === "differentiators") return <><h2 className="text-2xl md:text-3xl font-bold mb-6">Diferenciais</h2><div className="grid grid-cols-1 md:grid-cols-3 gap-4">{(state?.differentiators || []).map((item, index) => <div key={index} className="rounded-xl p-5 border"><div className="h-8 w-8 rounded-lg mb-3 flex items-center justify-center font-bold" style={{ background: `${colors.primary}22`, color: colors.primary }}>{index + 1}</div><p>{item}</p></div>)}</div></>;
  if (type === "contact") return <><h2 className="text-2xl md:text-3xl font-bold mb-4">Contato</h2><div className="space-y-2 opacity-80">{company?.phone && <p><strong>Telefone:</strong> {company.phone}</p>}{company?.address && <p><strong>Endereço:</strong> {company.address}{company.city && `, ${company.city}`}</p>}{state?.contact?.whatsapp && <p><strong>WhatsApp:</strong> {state.contact.whatsapp}</p>}</div></>;
  if (type === "professionals") return <><h2 className="text-2xl md:text-3xl font-bold mb-4">Profissionais</h2><p className="opacity-70">Conheça nossa equipe.</p></>;
  if (type === "hours") return <><h2 className="text-2xl md:text-3xl font-bold mb-4">Horários</h2><p className="opacity-70">Consulte nossos horários de atendimento.</p></>;
  return null;
}

export default function AISpecRenderer({ specification, state, company, services = [], publicMode = false, resolveUrl }) {
  const colors = specification.theme;
  return <div className="h-full overflow-y-auto" data-testid="ai-spec-renderer" data-renderer-mode="AI_SPEC" style={{ background: colors.background, color: colors.text }}>
    {specification.sections.map((section) => <section key={section.id} className={`relative px-6 md:px-12 py-12 ${layoutClass(section.layout_mode)}`} style={{ background: section.section_type === "hero" ? `linear-gradient(135deg, ${colors.primary}, ${colors.secondary})` : undefined, color: section.section_type === "hero" ? "#FFFFFF" : colors.text }} data-section-id={section.id} data-layout-mode={section.layout_mode}>
      <div className="max-w-6xl mx-auto w-full"><SectionContent section={section} state={state} company={company} services={services} publicMode={publicMode} resolveUrl={resolveUrl} colors={colors}/></div>
    </section>)}
    <footer className="px-6 md:px-12 py-6 text-center text-sm" style={{ background: colors.secondary, color: colors.background }}>© {new Date().getFullYear()} {company?.name} · Feito com Gestão SaaS</footer>
  </div>;
}
