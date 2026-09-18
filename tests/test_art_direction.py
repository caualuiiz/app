import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))

from ai.art_direction import ArtDirection, GenerateArtDirectionRequest  # noqa: E402
from ai.art_direction_service import build_art_direction_context, _profile_query  # noqa: E402
from ai.reference import ReferenceAnalysis  # noqa: E402
from ai.visual import VisualAnalysis  # noqa: E402


def test_art_direction_contract_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        ArtDirection.model_validate({"arbitrary_code": "blocked"})


def test_art_direction_request_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        GenerateArtDirectionRequest.model_validate({"company_id": "other-tenant"})


def test_context_contains_only_company_scoped_design_inputs():
    context = build_art_direction_context(
        {
            "name": "Studio A",
            "business_type": "BARBERSHOP",
            "description": "Cortes clássicos",
            "city": "São Paulo",
            "password_hash": "must-not-appear",
            "api_key": "must-not-appear",
        },
        {"state": {"hero": {"title": "Studio"}, "is_published": True}},
        VisualAnalysis(dominant_colors=["#111111"], confidence=0.8),
        ReferenceAnalysis(design_principles=["hierarquia editorial"], confidence=0.7),
    )
    serialized = str(context)
    assert context["company"] == {
        "name": "Studio A",
        "business_type": "BARBERSHOP",
        "description": "Cortes clássicos",
        "city": "São Paulo",
    }
    assert "password_hash" not in serialized
    assert "api_key" not in serialized
    assert "is_published" not in context["landing"]


def test_profile_query_always_contains_authenticated_company():
    assert _profile_query("company-a", "request-1") == {
        "company_id": "company-a",
        "request_id": "request-1",
    }
