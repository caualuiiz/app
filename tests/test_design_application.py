import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))

from ai.design_application import ApplyDesignRequest, ApplyDesignResponse  # noqa: E402
from ai.design_application_service import _landing_version_filter  # noqa: E402


def test_apply_request_requires_idempotency_and_preview():
    request = ApplyDesignRequest(preview_id="preview-1", request_id="request-1")
    assert request.expected_draft_version is None
    with pytest.raises(ValidationError):
        ApplyDesignRequest(preview_id="preview-1", request_id="")
    with pytest.raises(ValidationError):
        ApplyDesignRequest(preview_id="preview-1", request_id="request-1", expected_draft_version=-1)
    with pytest.raises(ValidationError):
        ApplyDesignRequest.model_validate({"preview_id": "preview-1", "request_id": "request-1", "company_id": "other"})


def test_apply_uses_optimistic_draft_version_filter():
    assert _landing_version_filter("company-a", 0) == {
        "company_id": "company-a",
        "$or": [{"draft_version": 0}, {"draft_version": {"$exists": False}}],
    }
    assert _landing_version_filter("company-a", 3) == {
        "company_id": "company-a",
        "$or": [{"draft_version": 3}],
    }


def test_apply_response_is_not_published_and_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        ApplyDesignResponse.model_validate({"published": True, "unknown": "blocked"})
