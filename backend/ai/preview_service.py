"""Company-scoped Preview Session service for Phase 2.8."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from bson import ObjectId
from fastapi import HTTPException

from db import get_db
from .preview_application import CreatePreviewRequest, PreviewResponse
from .render_specification import RenderSpecification


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _spec_query(company_id: str, request_id: str | None) -> dict[str, Any]:
    query: dict[str, Any] = {"company_id": company_id}
    if request_id:
        query["request_id"] = request_id
    return query


def _serialize_preview(doc: dict[str, Any]) -> PreviewResponse:
    fields = tuple(PreviewResponse.model_fields)
    return PreviewResponse.model_validate({key: doc[key] for key in fields})


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def _expire_if_needed(doc: dict[str, Any], now: datetime) -> bool:
    if doc["status"] in {"CREATED", "ACTIVE"} and _aware(doc["expires_at"]) <= now:
        doc["status"] = "EXPIRED"
        return True
    return False


async def _get_render_spec(db, company_id: str, request_id: str | None) -> dict[str, Any] | None:
    query = _spec_query(company_id, request_id)
    if request_id:
        return await db.render_specifications.find_one(query)
    return await db.render_specifications.find_one(query, sort=[("created_at", -1)])


async def create_preview(company_id: str, user_id: str, request: CreatePreviewRequest) -> PreviewResponse:
    db = get_db()
    company = await db.companies.find_one({"_id": ObjectId(company_id)})
    landing = await db.landing_pages.find_one({"company_id": company_id})
    if not company or not landing:
        raise HTTPException(404, "Empresa ou landing não encontrada")
    spec_doc = await _get_render_spec(db, company_id, request.render_spec_request_id)
    if request.render_spec_request_id and not spec_doc:
        raise HTTPException(404, "Render Specification não encontrada para esta empresa")
    if not spec_doc:
        raise HTTPException(400, "Gere uma Render Specification antes do Preview")
    render_spec = RenderSpecification.model_validate(spec_doc["render_specification"])
    created_at = _now()
    expires_at = created_at + timedelta(minutes=request.expires_in_minutes)
    doc = {
        "preview_id": str(uuid.uuid4()),
        "company_id": company_id,
        "user_id": user_id,
        "landing_version": str(landing.get("updated_at") or landing.get("created_at") or "unknown"),
        "render_spec": render_spec.model_dump(by_alias=True),
        "render_spec_request_id": spec_doc["request_id"],
        "created_at": created_at,
        "expires_at": expires_at,
        "status": "ACTIVE",
    }
    await db.preview_sessions.insert_one(doc)
    return _serialize_preview(doc)


async def get_preview(company_id: str, preview_id: str) -> PreviewResponse:
    db = get_db()
    doc = await db.preview_sessions.find_one({"preview_id": preview_id, "company_id": company_id})
    if not doc:
        raise HTTPException(404, "Preview não encontrado")
    if _expire_if_needed(doc, _now()):
        await db.preview_sessions.update_one(
            {"preview_id": preview_id, "company_id": company_id},
            {"$set": {"status": "EXPIRED"}},
        )
    return _serialize_preview(doc)


async def list_previews(company_id: str) -> list[PreviewResponse]:
    db = get_db()
    docs = await db.preview_sessions.find({"company_id": company_id}).sort("created_at", -1).to_list(20)
    now = _now()
    result = []
    for doc in docs:
        if _expire_if_needed(doc, now):
            await db.preview_sessions.update_one(
                {"preview_id": doc["preview_id"], "company_id": company_id},
                {"$set": {"status": "EXPIRED"}},
            )
        result.append(_serialize_preview(doc))
    return result
