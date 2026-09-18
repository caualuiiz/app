"""Company-scoped Reference Intelligence service for Phase 2.2."""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from fastapi import HTTPException

from db import get_db
from .reference import (
    AnalyzeReferencesRequest,
    ReferenceAnalysis,
    ReferenceProfileResponse,
)
from .visual_intelligence import (
    MODEL_NAME,
    _call_existing_provider,
    _load_image_inputs,
)

MAX_IMAGES = 8


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def select_reference_image_paths(
    company_id: str,
    landing: dict[str, Any],
    file_records: list[dict[str, Any]],
    image_ids: list[str],
) -> list[str]:
    """Resolve only images referenced by this tenant's landing gallery."""
    gallery = (landing.get("state") or {}).get("gallery") or []
    by_id = {str(item.get("id")): item for item in gallery if item.get("id") and item.get("path")}
    owned_paths = {
        str(record.get("storage_path"))
        for record in file_records
        if record.get("company_id") == company_id and not record.get("is_deleted", False)
    }
    paths = []
    for image_id in image_ids:
        item = by_id.get(image_id)
        if item and item["path"] in owned_paths and item["path"] not in paths:
            paths.append(item["path"])
    if image_ids and not paths:
        raise HTTPException(400, "Nenhuma imagem de referência autorizada encontrada")
    return paths[:MAX_IMAGES]


async def _call_reference_provider(
    images: list[dict[str, str]],
    source_url: str | None,
    source_description: str | None,
    company_context: str,
) -> ReferenceAnalysis:
    from .openai_runtime import OpenAIExecutionError, generate_json
    source_text = json.dumps({"url": source_url, "description": source_description, "company_context": company_context}, ensure_ascii=False)
    prompt = (
        "Analise a referência visual somente para extrair PRINCÍPIOS DE DESIGN. Não copie textos, logos, identidade, "
        "imagens, código ou layout proprietário. Retorne JSON compatível com ReferenceAnalysis. "
        f"Fonte da referência: {source_text}"
    )
    try:
        result = await generate_json(
            system_prompt="Você é um analista de princípios de design. Responda somente JSON válido.",
            user_prompt=prompt,
            images=images,
            model=MODEL_NAME,
        )
        return ReferenceAnalysis.model_validate(result)
    except OpenAIExecutionError as exc:
        raise RuntimeError(str(exc)) from exc

async def analyze_references(company_id: str, user_id: str, request: AnalyzeReferencesRequest) -> ReferenceProfileResponse:
    db = get_db()
    landing = await db.landing_pages.find_one({"company_id": company_id})
    if not landing:
        raise HTTPException(404, "Landing não encontrada")
    company = await db.companies.find_one({"_id": ObjectId(company_id)})
    if not company:
        raise HTTPException(404, "Empresa não encontrada")
    records = await db.files.find({"company_id": company_id, "is_deleted": False}).to_list(MAX_IMAGES * 2)
    paths = select_reference_image_paths(company_id, landing, records, request.image_ids)
    images = await _load_image_inputs(paths)
    context = json.dumps(
        {"name": company.get("name"), "business_type": company.get("business_type"), "description": company.get("description")},
        ensure_ascii=False,
    )
    try:
        analysis = await _call_reference_provider(images, str(request.url) if request.url else None, request.description, context)
    except RuntimeError as exc:
        raise HTTPException(503, "IA de referências indisponível") from exc
    request_id = str(uuid.uuid4())
    created_at = _now()
    source_types = []
    if request.url:
        source_types.append("url")
    if request.description:
        source_types.append("description")
    if paths:
        source_types.append("image")
    doc = {
        "request_id": request_id,
        "company_id": company_id,
        "user_id": user_id,
        "source_types": source_types,
        "source_url": str(request.url) if request.url else None,
        "source_description": request.description,
        "image_count": len(paths),
        "image_paths": paths,
        "analysis": analysis.model_dump(),
        "provider": "openai",
        "model": MODEL_NAME,
        "created_at": created_at,
    }
    await db.reference_profiles.insert_one(doc)
    return ReferenceProfileResponse.model_validate({key: doc[key] for key in ReferenceProfileResponse.model_fields})


async def list_profiles(company_id: str) -> list[ReferenceProfileResponse]:
    db = get_db()
    docs = await db.reference_profiles.find({"company_id": company_id}).sort("created_at", -1).to_list(20)
    fields = tuple(ReferenceProfileResponse.model_fields)
    return [ReferenceProfileResponse.model_validate({key: doc[key] for key in fields}) for doc in docs]
