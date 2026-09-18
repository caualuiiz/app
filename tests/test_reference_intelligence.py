import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))

from ai.reference import AnalyzeReferencesRequest, ReferenceAnalysis  # noqa: E402
from ai.reference_intelligence import select_reference_image_paths  # noqa: E402


def test_reference_request_requires_at_least_one_source():
    with pytest.raises(ValidationError):
        AnalyzeReferencesRequest()


def test_reference_contract_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        ReferenceAnalysis.model_validate({"copy_this_site": True})


def test_reference_image_selection_is_scoped_to_company():
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
    selected = select_reference_image_paths("company-a", landing, records, ["a", "b"])
    assert selected == ["gestao/companies/company-a/a.jpg"]


def test_reference_image_selection_rejects_cross_tenant_only_input():
    landing = {"state": {"gallery": [{"id": "b", "path": "b.jpg"}]}}
    with pytest.raises(Exception) as exc:
        select_reference_image_paths(
            "company-a",
            landing,
            [{"company_id": "company-b", "storage_path": "b.jpg", "is_deleted": False}],
            ["b"],
        )
    assert "Nenhuma imagem de referência autorizada" in str(exc.value)
