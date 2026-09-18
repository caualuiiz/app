import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))

from ai.preview_application import CreatePreviewRequest, PreviewResponse  # noqa: E402
from ai.preview_service import _expire_if_needed, _spec_query  # noqa: E402


def test_preview_request_has_bounded_expiration():
    assert CreatePreviewRequest().expires_in_minutes == 30
    with pytest.raises(ValidationError):
        CreatePreviewRequest(expires_in_minutes=2)
    with pytest.raises(ValidationError):
        CreatePreviewRequest(expires_in_minutes=1441)


def test_preview_expiration_transitions_only_active_states():
    now = datetime.now(timezone.utc)
    expired = {"status": "ACTIVE", "expires_at": now - timedelta(minutes=1)}
    assert _expire_if_needed(expired, now) is True
    assert expired["status"] == "EXPIRED"

    applied = {"status": "APPLIED", "expires_at": now - timedelta(minutes=1)}
    assert _expire_if_needed(applied, now) is False
    assert applied["status"] == "APPLIED"


def test_preview_query_keeps_authenticated_company():
    assert _spec_query("company-a", "spec-1") == {"company_id": "company-a", "request_id": "spec-1"}
    assert _spec_query("company-a", None) == {"company_id": "company-a"}


def test_preview_response_contract_rejects_unknown_fields_and_requires_status():
    with pytest.raises(ValidationError):
        PreviewResponse.model_validate({"preview_id": "p", "company_id": "c", "unknown": True})
