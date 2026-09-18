"""Company-scoped Layout Plan service for Phase 2.5."""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from fastapi import HTTPException

from db import get_db
from .design_system import DesignSystem
from .layout_plan import GenerateLayoutPlanRequest, LayoutPlan, LayoutPlanResponse
from .visual_intelligence import MODEL_NAME


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _system_query(company_id: str, request_id: str | None) -> dict[str, Any]:
    query: dict[str, Any] = {"company_id": company_id}
    if request_id:
        query["request_id"] = request_id
    return query


async def _get_design_system(db, company_id: str, request_id: str | None) -> dict[str, Any] | None:
    query = _system_query(company_id, request_id)
    if request_id:
        return await db.design_systems.find_one(query)
    return await db.design_systems.find_one(query, sort=[("created_at", -1)])


def build_layout_context(company: dict[str, Any], system: DesignSystem) -> dict[str, Any]:
    """Build a minimal company-scoped context for layout composition."""
    return {
        "company": {
            "name": company.get("name"),
            "business_type": company.get("business_type"),
            "description": company.get("description"),
        },
        "design_system": system.model_dump(by_alias=True),
    }


async def _call_provider(context: dict[str, Any]) -> LayoutPlan:
    key = os.environ.get("EMERGENT_LLM_KEY")
    if not key:
        raise RuntimeError("EMERGENT_LLM_KEY ausente")
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
    except ImportError as exc:
        raise RuntimeError("provider existente indisponível") from exc

    prompt = (
        "Crie um Layout Plan específico para o negócio a partir do Design System fornecido. "
        "Não use sempre a mesma grade de cards. Escolha uma experiência adequada ao negócio. "
        "Retorne JSON válido com exatamente sections, page_rhythm, responsive_strategy, "
        "accessibility_strategy, performance_strategy, confidence e warnings. Cada seção deve conter "
        "id, purpose, layout, content_source, visual_treatment, interaction, motion e responsive_behavior. "
        "layout deve ser um destes valores: cinematic_fullscreen, editorial_split, asymmetric_grid, "
        "immersive_gallery, horizontal_gallery, sticky_storytelling, oversized_typography, project_showcase, "
        "image_led_section, comparison, timeline, process_storytelling ou interactive_visual. "
        "Não invente serviços, preços, profissionais, depoimentos ou resultados.\n\n"
        + json.dumps(context, ensure_ascii=False)
    )
    try:
        chat = LlmChat(
            api_key=key,
            session_id=f"layout-plan-{uuid.uuid4()}",
            system_message="Você é um arquiteto de experiências digitais. Responda somente JSON válido.",
        ).with_model("openai", MODEL_NAME)
        raw = await chat.send_message(UserMessage(text=prompt))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(502, "O provider de IA falhou ao gerar o Layout Plan") from exc

    try:
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("```", 2)[1].lstrip("json").strip()
        return LayoutPlan.model_validate(json.loads(text))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(502, "A resposta da IA não possui formato de Layout Plan válido") from exc


async def generate_layout_plan(
    company_id: str,
    user_id: str,
    request: GenerateLayoutPlanRequest,
) -> LayoutPlanResponse:
    db = get_db()
    company = await db.companies.find_one({"_id": ObjectId(company_id)})
    if not company:
        raise HTTPException(404, "Empresa não encontrada")
    system_doc = await _get_design_system(db, company_id, request.design_system_request_id)
    if request.design_system_request_id and not system_doc:
        raise HTTPException(404, "Design System não encontrado para esta empresa")
    if not system_doc:
        raise HTTPException(400, "Gere um Design System antes do Layout Plan")
    system = DesignSystem.model_validate(system_doc["design_system"])
    plan = await _call_provider(build_layout_context(company, system))
    request_id = str(uuid.uuid4())
    created_at = _now()
    doc = {
        "request_id": request_id,
        "company_id": company_id,
        "user_id": user_id,
        "design_system_request_id": system_doc["request_id"],
        "layout_plan": plan.model_dump(),
        "provider": "existing",
        "model": MODEL_NAME,
        "created_at": created_at,
    }
    await db.layout_plans.insert_one(doc)
    fields = LayoutPlanResponse.model_fields
    return LayoutPlanResponse.model_validate({key: doc[key] for key in fields})


async def list_layout_plans(company_id: str) -> list[LayoutPlanResponse]:
    db = get_db()
    docs = await db.layout_plans.find({"company_id": company_id}).sort("created_at", -1).to_list(20)
    fields = tuple(LayoutPlanResponse.model_fields)
    return [LayoutPlanResponse.model_validate({key: doc[key] for key in fields}) for doc in docs]
