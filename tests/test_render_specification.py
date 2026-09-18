import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))

from ai.design_system import DesignColors, DesignSpacing, DesignTypography  # noqa: E402
from ai.layout_plan import LayoutMode  # noqa: E402
from ai.render_specification import RenderSection, RenderSpecification, GenerateRenderSpecRequest  # noqa: E402
from ai.render_specification_service import build_render_context, _plan_query  # noqa: E402


def valid_spec():
    return {
        "version": "1.0",
        "theme": {"primary": "#111111", "secondary": "#222222", "accent": "#C08457", "background": "#FFFFFF", "surface": "#F7F7F7", "text": "#101010", "muted": "#777777", "border": "#DDDDDD"},
        "typography": {"display": "Cormorant", "heading": "Inter", "body": "Inter", "label": "Inter", "button": "Inter"},
        "spacing": {"xs": "4px", "sm": "8px", "md": "16px", "lg": "24px", "xl": "40px", "2xl": "64px", "section": "96px"},
        "sections": [{
            "id": "hero", "section_type": "hero", "layout_mode": "cinematic_fullscreen",
            "content_references": ["landing.hero.title"], "image_references": ["media.gallery.0"],
            "typography": "display", "spacing": "section", "colors": "theme.primary",
            "motion": "fade", "interaction": "cta", "responsive_behavior": "single column on mobile",
            "accessibility": "heading hierarchy", "fallback_behavior": "render legacy hero",
        }],
        "motion": {"intensity": "LOW", "reduced_motion": "disable transforms", "fallback": "opacity only"},
        "interactions": {"keyboard": "tab order", "touch": "tap targets", "focus": "visible outline"},
        "responsive": {"mobile": "single column", "tablet": "two columns", "desktop": "editorial grid"},
        "media": {"lazy_loading": True, "allowed_types": ["image", "gallery"], "fallback": "omit missing image"},
        "accessibility": {"contrast": "WCAG AA", "semantics": "landmark sections", "alt_text": "from media metadata", "reduced_motion": "respect preference"},
    }


def test_render_spec_accepts_valid_declarative_structure():
    spec = RenderSpecification.model_validate(valid_spec())
    assert spec.version == "1.0"
    assert spec.sections[0].content_references == ["landing.hero.title"]


def test_render_spec_rejects_arbitrary_code_and_unknown_fields():
    payload = valid_spec()
    payload["javascript"] = "alert(1)"
    with pytest.raises(ValidationError):
        RenderSpecification.model_validate(payload)


def test_render_spec_rejects_unsafe_reference_namespace():
    with pytest.raises(ValidationError):
        RenderSection.model_validate({
            "id": "hero", "section_type": "hero", "layout_mode": "cinematic_fullscreen",
            "content_references": ["javascript:alert(1)"], "image_references": [],
            "typography": "display", "spacing": "section", "colors": "theme.primary",
            "motion": "none", "interaction": "none", "responsive_behavior": "safe",
            "accessibility": "safe", "fallback_behavior": "legacy",
        })


def test_render_spec_rejects_duplicate_section_ids():
    payload = valid_spec()
    payload["sections"].append(dict(payload["sections"][0]))
    with pytest.raises(ValidationError):
        RenderSpecification.model_validate(payload)


def test_render_spec_request_does_not_accept_company_id():
    with pytest.raises(ValidationError):
        GenerateRenderSpecRequest.model_validate({"company_id": "other-tenant"})


def test_render_context_contains_only_public_company_data():
    system = RenderSpecification.model_validate(valid_spec())
    # The service consumes LayoutPlan, so validate the boundary through a minimal fake object.
    class Plan:
        def model_dump(self):
            return {"sections": [{"id": "hero"}]}
    context = build_render_context({"name": "Studio", "business_type": "BARBERSHOP", "description": "Cortes", "token": "blocked"}, Plan())
    assert context["company"] == {"name": "Studio", "business_type": "BARBERSHOP", "description": "Cortes"}
    assert "token" not in str(context)


def test_plan_query_keeps_authenticated_company():
    assert _plan_query("company-a", "plan-1") == {"company_id": "company-a", "request_id": "plan-1"}
