"""Company-scoped Design System service for Phase 2.4."""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from fastapi import HTTPException

from db import get_db
from .art_direction import ArtDirection
from .design_system import DesignSystem, DesignSystemResponse, GenerateDesignSystemRequest
from .visual_intelligence import MODEL_NAME


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _art_direction_query(company_id: str, request_id: str | None) -> dict[str, Any]:
    query: dict[str, Any] = {"company_id": company_id}
    if request_id:
        query["request_id"] = request_id
    return query


async def _get_art_direction(db, company_id: str, request_id: str | None) -> dict[str, Any] | None:
    query = _art_direction_query(company_id, request_id)
    if request_id:
        return await db.art_directions.find_one(query)
    return await db.art_directions.find_one(query, sort=[("created_at", -1)])


def build_design_system_context(company: dict[str, Any], direction: ArtDirection) -> dict[str, Any]:
    """Build a minimal context using only public company data and art direction."""
    return {
        "company": {
            "name": company.get("name"),
            "business_type": company.get("business_type"),
            "description": company.get("description"),
        },
        "art_direction": direction.model_dump(),
    }


async def _call_provider(context: dict[str, Any]) -> DesignSystem:
    from .openai_runtime import OpenAIExecutionError, generate_json
    prompt = (
        "Gere um Design System estruturado e validável derivado da Art Direction fornecida. "
        "Não invente dados da empresa. Retorne JSON compatível com DesignSystem. "
        "Todas as cores devem ser hexadecimais. Use tokens de design, não código.\n\n"
        + json.dumps(context, ensure_ascii=False)
    )
    try:
        result = await generate_json(
            system_prompt="Você é um designer de sistemas visuais sênior. Responda somente JSON válido.",
            user_prompt=prompt,
            model=MODEL_NAME,
        )
        return DesignSystem.model_validate(result)
    except OpenAIExecutionError as exc:
        raise RuntimeError(str(exc)) from exc

async def generate_design_system(
    company_id: str,
    user_id: str,
    request: GenerateDesignSystemRequest,
) -> DesignSystemResponse:
    db = get_db()
    company = await db.companies.find_one({"_id": ObjectId(company_id)})
    if not company:
        raise HTTPException(404, "Empresa não encontrada")
    direction_doc = await _get_art_direction(db, company_id, request.art_direction_request_id)
    if request.art_direction_request_id and not direction_doc:
        raise HTTPException(404, "Art Direction não encontrada para esta empresa")
    if not direction_doc:
        raise HTTPException(400, "Gere uma Art Direction antes do Design System")
    direction = ArtDirection.model_validate(direction_doc["direction"])
    design_system = await _call_provider(build_design_system_context(company, direction))
    request_id = str(uuid.uuid4())
    created_at = _now()
    doc = {
        "request_id": request_id,
        "company_id": company_id,
        "user_id": user_id,
        "art_direction_request_id": direction_doc.get("request_id"),
        "design_system": design_system.model_dump(by_alias=True),
        "provider": "openai",
        "model": MODEL_NAME,
        "created_at": created_at,
    }
    await db.design_systems.insert_one(doc)
    fields = DesignSystemResponse.model_fields
    return DesignSystemResponse.model_validate({key: doc[key] for key in fields})


async def list_design_systems(company_id: str) -> list[DesignSystemResponse]:
    db = get_db()
    docs = await db.design_systems.find({"company_id": company_id}).sort("created_at", -1).to_list(20)
    fields = tuple(DesignSystemResponse.model_fields)
    return [DesignSystemResponse.model_validate({key: doc[key] for key in fields}) for doc in docs]
