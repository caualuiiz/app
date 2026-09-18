import { isSafeRenderSpec, layoutClass, resolveRenderReference } from "./renderSpec";

const valid = {
  version: "1.0",
  theme: { primary: "#111111", secondary: "#222222", accent: "#C08457", background: "#FFFFFF", surface: "#F7F7F7", text: "#101010", muted: "#777777", border: "#DDDDDD" },
  sections: [{
    id: "hero", section_type: "hero", layout_mode: "cinematic_fullscreen",
    content_references: ["landing.hero.title"], image_references: ["media.gallery.0"],
    typography: "display", spacing: "section", colors: "theme.primary",
    responsive_behavior: "single column", accessibility: "heading", fallback_behavior: "legacy",
  }],
};

test("accepts a closed declarative AI_SPEC", () => {
  expect(isSafeRenderSpec(valid)).toBe(true);
});

test("rejects arbitrary fields, unsafe references, and duplicate ids", () => {
  expect(isSafeRenderSpec({ ...valid, javascript: "alert(1)" })).toBe(false);
  expect(isSafeRenderSpec({ ...valid, sections: [{ ...valid.sections[0], content_references: ["javascript:alert(1)"] }] })).toBe(false);
  expect(isSafeRenderSpec({ ...valid, sections: [{ ...valid.sections[0] }, { ...valid.sections[0] }] })).toBe(false);
});

test("maps only known layout modes and resolves safe references", () => {
  expect(layoutClass("editorial_split")).toContain("md:grid");
  expect(layoutClass("unknown")).toBe("");
  expect(resolveRenderReference("landing.hero.title", { state: { hero: { title: "Studio" } } })).toBe("Studio");
  expect(resolveRenderReference("company.password", { company: { password: "no" } })).toBeNull();
  expect(resolveRenderReference("javascript:alert(1)", { state: {} })).toBeNull();
});
