"""Company-scoped Apply Design service for Phase 2.9."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError

from db import get_db
from .design_application import ApplyDesignRequest, ApplyDesignResponse
from .preview_service import _aware
from .render_specification import RenderSpecification


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: datetime) -> str:
    return value.isoformat()


def _landing_version_filter(company_id: str, version: int) -> dict[str, Any]:
    return {
        "company_id": company_id,
        "$or": [{"draft_version": version}, {"draft_version": {"$exists": False}}] if version == 0 else [{"draft_version": version}],
    }


def _response_from_decision(doc: dict[str, Any], idempotent: bool) -> ApplyDesignResponse:
    return ApplyDesignResponse(
        request_id=doc["request_id"],
        preview_id=doc["preview_id"],
        company_id=doc["company_id"],
        previous_version=doc["previous_version"],
        new_version=doc["new_version"],
        render_spec=RenderSpecification.model_validate(doc["render_spec"]),
        idempotent=idempotent,
        published=False,
        applied_at=doc["applied_at"],
    )


async def apply_design(company_id: str, user_id: str, request: ApplyDesignRequest) -> ApplyDesignResponse:
    db = get_db()
    existing = await db.landing_decisions.find_one({"company_id": company_id, "request_id": request.request_id})
    if existing:
        return _response_from_decision(existing, idempotent=True)

    preview = await db.preview_sessions.find_one({"company_id": company_id, "preview_id": request.preview_id})
    if not preview:
        raise HTTPException(404, "Preview não encontrado para esta empresa")
    now = _now()
    if preview.get("status") not in {"CREATED", "ACTIVE"}:
        raise HTTPException(409, "Preview não está disponível para aplicação")
    if _aware(preview["expires_at"]) <= now:
        await db.preview_sessions.update_one(
            {"company_id": company_id, "preview_id": request.preview_id, "status": preview["status"]},
            {"$set": {"status": "EXPIRED"}},
        )
        raise HTTPException(409, "Preview expirado")

    landing = await db.landing_pages.find_one({"company_id": company_id})
    if not landing:
        raise HTTPException(404, "Landing não encontrada")
    previous_version = int(landing.get("draft_version") or 0)
    if request.expected_draft_version is not None and request.expected_draft_version != previous_version:
        raise HTTPException(409, "Draft foi alterado; atualize a prévia antes de aplicar")
    new_version = previous_version + 1
    render_spec = RenderSpecification.model_validate(preview["render_spec"])
    applied_at = _iso(now)

    update_result = await db.landing_pages.update_one(
        _landing_version_filter(company_id, previous_version),
        {"$set": {
            "draft_render_spec": render_spec.model_dump(by_alias=True),
            "draft_version": new_version,
            "draft_updated_at": applied_at,
        }},
    )
    if update_result.modified_count != 1:
        raise HTTPException(409, "Draft foi alterado por outra aplicação")

    decision = {
        "request_id": request.request_id,
        "company_id": company_id,
        "user_id": user_id,
        "preview_id": request.preview_id,
        "previous_version": previous_version,
        "new_version": new_version,
        "operation": "APPLY_DESIGN",
        "render_spec": render_spec.model_dump(by_alias=True),
        "applied_at": applied_at,
    }
    try:
        await db.draft_versions.insert_one({
            "company_id": company_id,
            "version": new_version,
            "preview_id": request.preview_id,
            "request_id": request.request_id,
            "user_id": user_id,
            "previous_version": previous_version,
            "previous_render_spec": landing.get("draft_render_spec"),
            "render_spec": render_spec.model_dump(by_alias=True),
            "created_at": applied_at,
        })
        await db.landing_decisions.insert_one(decision)
    except DuplicateKeyError:
        existing = await db.landing_decisions.find_one({"company_id": company_id, "request_id": request.request_id})
        if existing:
            return _response_from_decision(existing, idempotent=True)
        raise HTTPException(409, "Aplicação concorrente detectada")

    await db.preview_sessions.update_one(
        {"company_id": company_id, "preview_id": request.preview_id, "status": preview["status"]},
        {"$set": {"status": "APPLIED", "applied_request_id": request.request_id, "applied_at": applied_at}},
    )
    return _response_from_decision(decision, idempotent=False)
