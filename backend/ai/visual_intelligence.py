"""Company-scoped Visual Intelligence service for Phase 2.1."""
from __future__ import annotations

import base64
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from fastapi import HTTPException

from db import get_db
from storage import get_object
from .visual import AnalyzeImagesRequest, VisualAnalysis, VisualProfileResponse

MAX_IMAGES = 8
MODEL_NAME = "gpt-4o-mini"


class VisualProviderUnavailable(RuntimeError):
    """Raised when the configured existing provider cannot be used."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _path_from_url(value: str | None) -> str | None:
    if not value:
        return None
    marker = "/api/uploads/file/"
    return value.split(marker, 1)[1] if marker in value else None


def select_company_image_paths(
    company_id: str,
    landing: dict[str, Any],
    file_records: list[dict[str, Any]],
    request: AnalyzeImagesRequest,
) -> list[str]:
    """Select only stored images already referenced by this company's landing."""
    state = landing.get("state") or {}
    gallery = state.get("gallery") or []
    by_id = {str(item.get("id")): item for item in gallery if item.get("id") and item.get("path")}
    selected: list[str] = []
    ids = request.image_ids or list(by_id)
    for image_id in ids:
        item = by_id.get(image_id)
        if item and item["path"] not in selected:
            selected.append(item["path"])

    if request.include_establishment_photo:
        establishment_path = _path_from_url(landing.get("establishment_photo_url"))
        if establishment_path and establishment_path not in selected:
            selected.append(establishment_path)

    owned_paths = {
        str(record.get("storage_path"))
        for record in file_records
        if record.get("company_id") == company_id and not record.get("is_deleted", False)
    }
    selected = [path for path in selected if path in owned_paths]
    if not selected:
        raise HTTPException(400, "Nenhuma imagem autorizada encontrada")
    return selected[:MAX_IMAGES]


async def _load_image_inputs(paths: list[str]) -> list[dict[str, str]]:
    images: list[dict[str, str]] = []
    for path in paths:
        try:
            data, content_type = get_object(path)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(502, "Não foi possível carregar uma imagem") from exc
        images.append({"path": path, "content_type": content_type, "data": base64.b64encode(data).decode()})
    return images


async def _call_existing_provider(images: list[dict[str, str]], company_context: str) -> VisualAnalysis:
    key = os.environ.get("EMERGENT_LLM_KEY")
    if not key:
        raise VisualProviderUnavailable("EMERGENT_LLM_KEY ausente")
    try:
        from emergentintegrations.llm.chat import ImageContent, LlmChat, UserMessage
    except ImportError as exc:
        raise VisualProviderUnavailable("provider existente indisponível") from exc

    prompt = (
        "Analise somente as imagens fornecidas. Não invente fatos. "
        "Retorne JSON válido com exatamente estes campos: "
        "dominant_colors, secondary_colors, brightness, contrast, saturation, mood, style, image_insights, "
        "environment, composition, subject, materials, lighting, luxury_level, minimalism_level, "
        "visual_density, photographic_characteristics, confidence. image_insights deve ser uma lista de objetos, um por imagem, contendo image_path, likely_role, strengths, recommended_sections, treatment e confidence. "
        "brightness, contrast, saturation, luxury_level, minimalism_level, visual_density e confidence "
        "são números entre 0 e 1. Use null quando não for possível observar. "
        f"Contexto não factual adicional do negócio: {company_context}. Manifesto das imagens: {manifest}. Use exatamente os image_path do manifesto."
    )
    manifest = json.dumps([{"index": index + 1, "image_path": image["path"]} for index, image in enumerate(images)], ensure_ascii=False)
    contents = [ImageContent(image_base64=image["data"]) for image in images]
    try:
        chat = LlmChat(
            api_key=key,
            session_id=f"visual-{uuid.uuid4()}",
            system_message="Você é um analista visual. Responda apenas JSON válido.",
        ).with_model("openai", MODEL_NAME)
        raw = await chat.send_message(UserMessage(text=prompt, file_contents=contents))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(502, "O provider de IA falhou ao analisar as imagens") from exc

    try:
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("```", 2)[1].lstrip("json").strip()
        return VisualAnalysis.model_validate(json.loads(text))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(502, "A resposta da IA não possui formato visual válido") from exc


async def analyze_images(company_id: str, user_id: str, request: AnalyzeImagesRequest) -> VisualProfileResponse:
    db = get_db()
    landing = await db.landing_pages.find_one({"company_id": company_id})
    if not landing:
        raise HTTPException(404, "Landing não encontrada")
    company = await db.companies.find_one({"_id": ObjectId(company_id)})
    if not company:
        raise HTTPException(404, "Empresa não encontrada")
    paths = select_company_image_paths(
        company_id,
        {**landing, "establishment_photo_url": company.get("establishment_photo_url")},
        await db.files.find({"company_id": company_id, "is_deleted": False}).to_list(MAX_IMAGES * 2),
        request,
    )
    images = await _load_image_inputs(paths)
    context = json.dumps(
        {"name": company.get("name"), "business_type": company.get("business_type"), "description": company.get("description")},
        ensure_ascii=False,
    )
    try:
        analysis = await _call_existing_provider(images, context)
    except VisualProviderUnavailable as exc:
        raise HTTPException(503, "IA visual indisponível") from exc
    request_id = str(uuid.uuid4())
    created_at = _now()
    doc = {
        "request_id": request_id,
        "company_id": company_id,
        "user_id": user_id,
        "image_count": len(paths),
        "image_paths": paths,
        "analysis": analysis.model_dump(),
        "provider": "existing",
        "model": MODEL_NAME,
        "created_at": created_at,
    }
    await db.visual_profiles.insert_one(doc)
    return VisualProfileResponse(
        request_id=request_id,
        company_id=company_id,
        image_count=len(paths),
        image_paths=paths,
        analysis=analysis,
        provider="existing",
        model=MODEL_NAME,
        created_at=created_at,
    )


async def list_profiles(company_id: str) -> list[VisualProfileResponse]:
    db = get_db()
    docs = await db.visual_profiles.find({"company_id": company_id}).sort("created_at", -1).to_list(20)
    fields = ("request_id", "company_id", "image_count", "image_paths", "analysis", "provider", "model", "created_at")
    return [VisualProfileResponse.model_validate({key: doc[key] for key in fields}) for doc in docs]
