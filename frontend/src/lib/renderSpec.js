const SECTION_TYPES = new Set(["hero", "about", "services", "professionals", "gallery", "differentiators", "hours", "contact"]);
const LAYOUT_MODES = new Set([
  "cinematic_fullscreen", "editorial_split", "asymmetric_grid", "immersive_gallery",
  "horizontal_gallery", "sticky_storytelling", "oversized_typography", "project_showcase",
  "image_led_section", "comparison", "timeline", "process_storytelling", "interactive_visual",
]);
const NAMESPACES = ["landing.", "company.", "media.", "profile."];
const HEX = /^#[0-9a-f]{6}$/i;
const SAFE_COMPANY_FIELDS = new Set(["name", "slug", "business_type", "logo_url", "establishment_photo_url", "description", "phone", "email", "address", "city", "state", "zip_code"]);
const SAFE_LANDING_PATHS = new Set(["hero.title", "hero.subtitle", "hero.description", "hero.cta", "hero.featured_image", "about.text", "contact.whatsapp", "contact.instagram", "contact.facebook", "style.theme", "style.primary_color", "style.secondary_color", "sections.hero", "sections.about", "sections.services", "sections.professionals", "sections.gallery", "sections.differentiators", "sections.hours", "sections.contact"]);
const SPEC_KEYS = new Set(["version", "theme", "typography", "spacing", "sections", "motion", "interactions", "responsive", "media", "accessibility"]);
const SECTION_KEYS = new Set(["id", "section_type", "layout_mode", "content_references", "image_references", "typography", "spacing", "colors", "motion", "interaction", "responsive_behavior", "accessibility", "fallback_behavior"]);

function safeReference(value) {
  return typeof value === "string" && value.length <= 160
    && /^[a-zA-Z0-9_.-]+$/.test(value)
    && NAMESPACES.some((prefix) => value.startsWith(prefix));
}

export function isSafeRenderSpec(spec) {
  if (!spec || Object.keys(spec).some((key) => !SPEC_KEYS.has(key)) || spec.version !== "1.0" || !Array.isArray(spec.sections) || spec.sections.length < 1 || spec.sections.length > 12) return false;
  const ids = new Set();
  for (const section of spec.sections) {
    if (!section || Object.keys(section).some((key) => !SECTION_KEYS.has(key)) || !SECTION_TYPES.has(section.section_type) || !LAYOUT_MODES.has(section.layout_mode)) return false;
    if (typeof section.id !== "string" || !/^[a-z0-9][a-z0-9_-]*$/.test(section.id) || ids.has(section.id)) return false;
    ids.add(section.id);
    if (!Array.isArray(section.content_references) || !section.content_references.every(safeReference)) return false;
    if (!Array.isArray(section.image_references) || !section.image_references.every(safeReference)) return false;
    if (["typography", "spacing", "colors", "responsive_behavior", "accessibility", "fallback_behavior"].some((key) => typeof section[key] !== "string")) return false;
  }
  const colors = spec.theme || {};
  return ["primary", "secondary", "accent", "background", "surface", "text", "muted", "border"].every((key) => HEX.test(colors[key] || ""));
}

export function resolveRenderReference(reference, { state, company, services = [] } = {}) {
  if (typeof reference !== "string") return null;
  if (reference.startsWith("landing.")) {
    const pathValue = reference.slice("landing.".length);
    if (!SAFE_LANDING_PATHS.has(pathValue)) return null;
    const path = pathValue.split(".");
    return path.reduce((value, key) => value?.[key], state || {});
  }
  if (reference.startsWith("company.")) {
    const field = reference.slice("company.".length);
    return SAFE_COMPANY_FIELDS.has(field) ? company?.[field] ?? null : null;
  }
  if (reference === "media.gallery") return state?.gallery || [];
  const match = reference.match(/^media\.gallery\.(\d+)$/);
  if (match) return state?.gallery?.[Number(match[1])] || null;
  if (reference === "company.services") return services;
  return null;
}

export function layoutClass(layoutMode) {
  return {
    cinematic_fullscreen: "min-h-[380px] md:min-h-[480px]",
    editorial_split: "md:grid md:grid-cols-2 md:items-center",
    asymmetric_grid: "md:grid md:grid-cols-[1.25fr_0.75fr] md:items-start",
    immersive_gallery: "grid grid-cols-2 md:grid-cols-4",
    horizontal_gallery: "flex gap-3 overflow-x-auto",
    sticky_storytelling: "md:grid md:grid-cols-[0.35fr_0.65fr] md:items-start",
    oversized_typography: "text-2xl md:text-5xl",
    project_showcase: "md:grid md:grid-cols-3",
    image_led_section: "md:grid md:grid-cols-2 md:items-center",
    comparison: "md:grid md:grid-cols-2",
    timeline: "space-y-4",
    process_storytelling: "space-y-6",
    interactive_visual: "md:grid md:grid-cols-2",
  }[layoutMode] || "";
}
