"""Company-scoped Render Specification service for Phase 2.6."""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from fastapi import HTTPException

from db import get_db
from .layout_plan import LayoutPlan
from .render_specification import GenerateRenderSpecRequest, RenderSpecification, RenderSpecificationResponse
from .visual_intelligence import MODEL_NAME


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _plan_query(company_id: str, request_id: str | None) -> dict[str, Any]:
    query: dict[str, Any] = {"company_id": company_id}
    if request_id:
        query["request_id"] = request_id
    return query


async def _get_layout_plan(db, company_id: str, request_id: str | None) -> dict[str, Any] | None:
    query = _plan_query(company_id, request_id)
    if request_id:
        return await db.layout_plans.find_one(query)
    return await db.layout_plans.find_one(query, sort=[("created_at", -1)])


def build_render_context(company: dict[str, Any], plan: LayoutPlan) -> dict[str, Any]:
    """Build only public company data and validated layout data."""
    return {
        "company": {
            "name": company.get("name"),
            "business_type": company.get("business_type"),
            "description": company.get("description"),
        },
        "layout_plan": plan.model_dump(),
    }


async def _call_provider(context: dict[str, Any]) -> RenderSpecification:
    from .openai_runtime import OpenAIExecutionError, generate_json
    prompt = (
        "Converta o Layout Plan em uma Render Specification declarativa e segura. "
        "Retorne JSON compatível com RenderSpecification. Não retorne HTML, CSS, JavaScript, React, Python, SQL "
        "ou comandos. Use somente referências estruturadas e inclua fallback seguro.\n\n"
        + json.dumps(context, ensure_ascii=False)
    )
    try:
        result = await generate_json(
            system_prompt="Você é um arquiteto de especificações declarativas. Responda somente JSON válido.",
            user_prompt=prompt,
            model=MODEL_NAME,
        )
        return RenderSpecification.model_validate(result)
    except OpenAIExecutionError as exc:
        raise RuntimeError(str(exc)) from exc

async def generate_render_spec(
    company_id: str,
    user_id: str,
    request: GenerateRenderSpecRequest,
) -> RenderSpecificationResponse:
    db = get_db()
    company = await db.companies.find_one({"_id": ObjectId(company_id)})
    if not company:
        raise HTTPException(404, "Empresa não encontrada")
    plan_doc = await _get_layout_plan(db, company_id, request.layout_plan_request_id)
    if request.layout_plan_request_id and not plan_doc:
        raise HTTPException(404, "Layout Plan não encontrado para esta empresa")
    if not plan_doc:
        raise HTTPException(400, "Gere um Layout Plan antes da Render Specification")
    plan = LayoutPlan.model_validate(plan_doc["layout_plan"])
    specification = await _call_provider(build_render_context(company, plan))
    request_id = str(uuid.uuid4())
    created_at = _now()
    doc = {
        "request_id": request_id,
        "company_id": company_id,
        "user_id": user_id,
        "layout_plan_request_id": plan_doc["request_id"],
        "render_specification": specification.model_dump(by_alias=True),
        "provider": "existing",
        "model": MODEL_NAME,
        "created_at": created_at,
    }
    await db.render_specifications.insert_one(doc)
    fields = RenderSpecificationResponse.model_fields
    return RenderSpecificationResponse.model_validate({key: doc[key] for key in fields})


async def list_render_specs(company_id: str) -> list[RenderSpecificationResponse]:
    db = get_db()
    docs = await db.render_specifications.find({"company_id": company_id}).sort("created_at", -1).to_list(20)
    fields = tuple(RenderSpecificationResponse.model_fields)
    return [RenderSpecificationResponse.model_validate({key: doc[key] for key in fields}) for doc in docs]
