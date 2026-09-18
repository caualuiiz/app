"""Company-scoped Art Direction service for Phase 2.3."""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from fastapi import HTTPException

from db import get_db
from .art_direction import ArtDirection, ArtDirectionResponse, GenerateArtDirectionRequest
from .reference import ReferenceAnalysis
from .visual import VisualAnalysis
from .visual_intelligence import MODEL_NAME


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _profile_query(company_id: str, request_id: str | None) -> dict[str, Any]:
    query: dict[str, Any] = {"company_id": company_id}
    if request_id:
        query["request_id"] = request_id
    return query


async def _get_profile(db, collection: str, company_id: str, request_id: str | None) -> dict[str, Any] | None:
    query = _profile_query(company_id, request_id)
    if request_id:
        return await getattr(db, collection).find_one(query)
    return await getattr(db, collection).find_one(query, sort=[("created_at", -1)])


def build_art_direction_context(
    company: dict[str, Any],
    landing: dict[str, Any],
    visual: VisualAnalysis | None,
    reference: ReferenceAnalysis | None,
) -> dict[str, Any]:
    """Build a non-sensitive, company-scoped context for the model."""
    state = landing.get("state") or {}
    return {
        "company": {
            "name": company.get("name"),
            "business_type": company.get("business_type"),
            "description": company.get("description"),
            "city": company.get("city"),
        },
        "landing": {
            "hero": state.get("hero"),
            "about": state.get("about"),
            "style": state.get("style"),
            "sections": state.get("sections"),
        },
        "visual_intelligence": visual.model_dump() if visual else None,
        "reference_intelligence": reference.model_dump() if reference else None,
    }


async def _call_provider(context: dict[str, Any]) -> ArtDirection:
    key = os.environ.get("EMERGENT_LLM_KEY")
    if not key:
        raise RuntimeError("EMERGENT_LLM_KEY ausente")
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
    except ImportError as exc:
        raise RuntimeError("provider existente indisponível") from exc

    prompt = (
        "Crie uma direção de arte específica para este negócio usando somente os dados fornecidos. "
        "Não invente depoimentos, avaliações, prêmios, números, clientes, profissionais, serviços, preços, "
        "endereço, certificações ou resultados. Quando faltar dado factual, registre MISSING em missing_data "
        "ou omita. Não copie referências: extraia apenas princípios de design. Retorne JSON válido com exatamente "
        "brand_personality, visual_concept, art_direction, image_direction, typography_direction, color_direction, "
        "composition_direction, motion_direction, interaction_direction, three_d_direction, background_direction, "
        "conversion_direction, confidence, warnings e missing_data. three_d_direction deve ser NONE, SUBTLE, HERO "
        "ou IMMERSIVE. A proposta deve priorizar identidade, clareza, experiência e conversão.\n\n"
        + json.dumps(context, ensure_ascii=False)
    )
    try:
        chat = LlmChat(
            api_key=key,
            session_id=f"art-direction-{uuid.uuid4()}",
            system_message="Você é um diretor de arte digital. Responda somente JSON válido.",
        ).with_model("openai", MODEL_NAME)
        raw = await chat.send_message(UserMessage(text=prompt))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(502, "O provider de IA falhou ao gerar a direção de arte") from exc

    try:
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("```", 2)[1].lstrip("json").strip()
        return ArtDirection.model_validate(json.loads(text))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(502, "A resposta da IA não possui formato de Art Direction válido") from exc


async def generate_art_direction(
    company_id: str,
    user_id: str,
    request: GenerateArtDirectionRequest,
) -> ArtDirectionResponse:
    db = get_db()
    company = await db.companies.find_one({"_id": ObjectId(company_id)})
    landing = await db.landing_pages.find_one({"company_id": company_id})
    if not company or not landing:
        raise HTTPException(404, "Empresa ou landing não encontrada")

    visual_doc = await _get_profile(db, "visual_profiles", company_id, request.visual_profile_request_id)
    reference_doc = await _get_profile(db, "reference_profiles", company_id, request.reference_profile_request_id)
    if request.visual_profile_request_id and not visual_doc:
        raise HTTPException(404, "Perfil visual não encontrado para esta empresa")
    if request.reference_profile_request_id and not reference_doc:
        raise HTTPException(404, "Perfil de referência não encontrado para esta empresa")

    visual = VisualAnalysis.model_validate(visual_doc["analysis"]) if visual_doc else None
    reference = ReferenceAnalysis.model_validate(reference_doc["analysis"]) if reference_doc else None
    context = build_art_direction_context(company, landing, visual, reference)
    try:
        direction = await _call_provider(context)
    except RuntimeError as exc:
        raise HTTPException(503, "IA de Art Direction indisponível") from exc

    request_id = str(uuid.uuid4())
    created_at = _now()
    doc = {
        "request_id": request_id,
        "company_id": company_id,
        "user_id": user_id,
        "visual_profile_request_id": visual_doc.get("request_id") if visual_doc else None,
        "reference_profile_request_id": reference_doc.get("request_id") if reference_doc else None,
        "direction": direction.model_dump(),
        "provider": "existing",
        "model": MODEL_NAME,
        "created_at": created_at,
    }
    await db.art_directions.insert_one(doc)
    fields = ArtDirectionResponse.model_fields
    return ArtDirectionResponse.model_validate({key: doc[key] for key in fields})


async def list_directions(company_id: str) -> list[ArtDirectionResponse]:
    db = get_db()
    docs = await db.art_directions.find({"company_id": company_id}).sort("created_at", -1).to_list(20)
    fields = tuple(ArtDirectionResponse.model_fields)
    return [ArtDirectionResponse.model_validate({key: doc[key] for key in fields}) for doc in docs]
