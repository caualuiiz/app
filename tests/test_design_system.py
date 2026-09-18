import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))

from ai.art_direction import ArtDirection  # noqa: E402
from ai.design_system import DesignColors, DesignSystem, GenerateDesignSystemRequest  # noqa: E402
from ai.design_system_service import build_design_system_context, _art_direction_query  # noqa: E402


def valid_system():
    return {
        "colors": {
            "primary": "#111111", "secondary": "#222222", "accent": "#C08457",
            "background": "#FFFFFF", "surface": "#F7F7F7", "text": "#101010",
            "muted": "#777777", "border": "#DDDDDD",
        },
        "typography": {"display": "Cormorant", "heading": "Inter", "body": "Inter", "label": "Inter", "button": "Inter"},
        "spacing": {"xs": "4px", "sm": "8px", "md": "16px", "lg": "24px", "xl": "40px", "2xl": "64px", "section": "96px"},
        "radius": {"none": "0", "small": "4px", "medium": "8px", "large": "16px", "pill": "999px"},
        "grid": {"max_width": "1200px", "columns": 12, "gutter": "24px", "margins": "32px"},
        "motion": {"duration": "240ms", "easing": "ease-out", "intensity": "LOW"},
        "visual": {"image_treatment": "natural", "shadows": "subtle", "borders": "1px solid", "overlays": "none"},
        "responsive": {"mobile": "single column", "tablet": "two columns", "desktop": "editorial grid"},
    }


def test_design_system_validates_structured_tokens():
    system = DesignSystem.model_validate(valid_system())
    assert system.colors.primary == "#111111"
    assert system.spacing.two_xl == "64px"


def test_design_system_rejects_invalid_hex_color():
    payload = valid_system()
    payload["colors"]["primary"] = "red"
    with pytest.raises(ValidationError):
        DesignSystem.model_validate(payload)


def test_design_system_contract_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        DesignColors.model_validate({"primary": "#111111", "unknown": "#222222"})


def test_design_system_request_does_not_accept_company_id():
    with pytest.raises(ValidationError):
        GenerateDesignSystemRequest.model_validate({"company_id": "other-tenant"})


def test_design_system_context_excludes_sensitive_company_fields():
    direction = ArtDirection(
        visual_concept="Editorial premium",
        art_direction="Clareza e contraste",
        confidence=0.8,
    )
    context = build_design_system_context(
        {"name": "Studio A", "business_type": "BARBERSHOP", "description": "Cortes", "password_hash": "x", "api_key": "y"},
        direction,
    )
    serialized = str(context)
    assert context["company"] == {"name": "Studio A", "business_type": "BARBERSHOP", "description": "Cortes"}
    assert "password_hash" not in serialized
    assert "api_key" not in serialized


def test_art_direction_query_keeps_authenticated_company():
    assert _art_direction_query("company-a", "direction-1") == {"company_id": "company-a", "request_id": "direction-1"}
