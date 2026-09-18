import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))

from ai.design_system import DesignSystem  # noqa: E402
from ai.layout_plan import GenerateLayoutPlanRequest, LayoutPlan  # noqa: E402
from ai.layout_plan_service import build_layout_context, _system_query  # noqa: E402


def valid_plan():
    return {
        "sections": [
            {
                "id": "hero",
                "purpose": "impact",
                "layout": "cinematic_fullscreen",
                "content_source": "landing.hero",
                "visual_treatment": "imagem autoral com contraste",
                "interaction": "cta visível",
                "motion": "fade suave",
                "responsive_behavior": "reduzir altura no mobile",
            },
            {
                "id": "services",
                "purpose": "conversion",
                "layout": "editorial_split",
                "content_source": "company.services",
                "visual_treatment": "tipografia e imagem",
                "interaction": "scroll reveal",
                "motion": "opacity",
                "responsive_behavior": "empilhar no mobile",
            },
        ],
        "page_rhythm": "abertura, prova de oferta, conversão",
        "responsive_strategy": "composição própria por breakpoint",
        "accessibility_strategy": "contraste e foco visível",
        "performance_strategy": "lazy loading e transform",
    }


def test_layout_plan_accepts_valid_sections():
    plan = LayoutPlan.model_validate(valid_plan())
    assert len(plan.sections) == 2
    assert plan.sections[0].layout == "cinematic_fullscreen"


def test_layout_plan_rejects_duplicate_section_ids():
    payload = valid_plan()
    payload["sections"][1]["id"] = "hero"
    with pytest.raises(ValidationError):
        LayoutPlan.model_validate(payload)


def test_layout_plan_rejects_unknown_layout_mode():
    payload = valid_plan()
    payload["sections"][0]["layout"] = "three_cards"
    with pytest.raises(ValidationError):
        LayoutPlan.model_validate(payload)


def test_layout_plan_request_does_not_accept_company_id():
    with pytest.raises(ValidationError):
        GenerateLayoutPlanRequest.model_validate({"company_id": "other-tenant"})


def test_layout_context_contains_only_public_company_data():
    system = DesignSystem.model_validate({
        "colors": {"primary": "#111111", "secondary": "#222222", "accent": "#C08457", "background": "#FFFFFF", "surface": "#F7F7F7", "text": "#101010", "muted": "#777777", "border": "#DDDDDD"},
        "typography": {"display": "Cormorant", "heading": "Inter", "body": "Inter", "label": "Inter", "button": "Inter"},
        "spacing": {"xs": "4px", "sm": "8px", "md": "16px", "lg": "24px", "xl": "40px", "2xl": "64px", "section": "96px"},
        "radius": {"none": "0", "small": "4px", "medium": "8px", "large": "16px", "pill": "999px"},
        "grid": {"max_width": "1200px", "columns": 12, "gutter": "24px", "margins": "32px"},
        "motion": {"duration": "240ms", "easing": "ease-out", "intensity": "LOW"},
        "visual": {"image_treatment": "natural", "shadows": "subtle", "borders": "1px solid", "overlays": "none"},
        "responsive": {"mobile": "single", "tablet": "two", "desktop": "grid"},
    })
    context = build_layout_context({"name": "Studio", "business_type": "BARBERSHOP", "description": "Cortes", "password": "blocked"}, system)
    assert context["company"] == {"name": "Studio", "business_type": "BARBERSHOP", "description": "Cortes"}
    assert "password" not in str(context)


def test_system_query_keeps_authenticated_company():
    assert _system_query("company-a", "system-1") == {"company_id": "company-a", "request_id": "system-1"}
