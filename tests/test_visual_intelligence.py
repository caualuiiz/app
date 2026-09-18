import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))

from ai.visual import AnalyzeImagesRequest, VisualAnalysis  # noqa: E402
from ai.visual_intelligence import select_company_image_paths  # noqa: E402


def test_visual_contract_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        VisualAnalysis.model_validate({"unknown": "blocked"})


def test_image_selection_is_scoped_to_company_and_landing_gallery():
    landing = {
        "state": {
            "gallery": [
                {"id": "a", "path": "gestao/companies/company-a/a.jpg"},
                {"id": "b", "path": "gestao/companies/company-b/b.jpg"},
            ]
        }
    }
    records = [
        {"company_id": "company-a", "storage_path": "gestao/companies/company-a/a.jpg", "is_deleted": False},
        {"company_id": "company-b", "storage_path": "gestao/companies/company-b/b.jpg", "is_deleted": False},
    ]
    selected = select_company_image_paths(
        "company-a", landing, records, AnalyzeImagesRequest(image_ids=["a", "b"])
    )
    assert selected == ["gestao/companies/company-a/a.jpg"]


def test_image_selection_rejects_missing_or_deleted_images():
    landing = {"state": {"gallery": [{"id": "a", "path": "a.jpg"}]}}
    with pytest.raises(Exception) as exc:
        select_company_image_paths(
            "company-a",
            landing,
            [{"company_id": "company-a", "storage_path": "a.jpg", "is_deleted": True}],
            AnalyzeImagesRequest(image_ids=["a"]),
        )
    assert "Nenhuma imagem autorizada" in str(exc.value)
