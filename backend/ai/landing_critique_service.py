from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import HTTPException

from db import get_db
from .landing_brain import LandingBrain
from .landing_critique import LandingCritique, LandingCritiqueResponse
from .professional_brain import build_system_prompt
from .render_specification import RenderSpecification


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def create_critique(company_id: str, user_id: str, preview_id: str) -> LandingCritiqueResponse:
    db = get_db()
    preview = await db.preview_sessions.find_one({"preview_id": preview_id, "company_id": company_id})
    if not preview:
        raise HTTPException(404, "Preview não encontrado")
    render_spec = RenderSpecification.model_validate(preview["render_spec"])
    company = await db.companies.find_one({"_id": ObjectId(company_id)})
    landing = await db.landing_pages.find_one({"company_id": company_id})
    if not company or not landing:
        raise HTTPException(404, "Empresa ou landing não encontrada")

    context = {
        "company": {"name": company.get("name"), "business_type": company.get("business_type"), "description": company.get("description")},
        "landing_state": landing.get("state") or {},
        "render_specification": render_spec.model_dump(by_alias=True),
    }
    prompt = ("Avalie esta landing como um diretor de arte e especialista em conversão com mais de 20 anos. "
              "Não invente fatos. Verifique hierarquia, coerência visual, mídia, conversão, mobile, acessibilidade "
              "e performance. Retorne somente JSON compatível com LandingCritique.\n\n" +
              json.dumps(context, ensure_ascii=False, default=str))

    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        key = os.environ.get("EMERGENT_LLM_KEY", "").strip()
        if not key:
            raise RuntimeError("EMERGENT_LLM_KEY não configurada")
        engine = LandingBrain()
        chat = LlmChat(api_key=key, session_id=f"landing-critique-{uuid.uuid4()}", system_message=build_system_prompt()).with_model("openai", engine.model)
        raw = await chat.send_message(UserMessage(text=prompt))
        text = str(raw).strip()
        if text.startswith("```"):
            text = text.split("```", 2)[1].lstrip("json").strip()
        critique = LandingCritique.model_validate(json.loads(text))
    except Exception as exc:
        raise HTTPException(503, "Landing Brain indisponível para a autocrítica") from exc

    request_id = str(uuid.uuid4())
    created_at = _now()
    await db.landing_critiques.insert_one({"request_id": request_id, "preview_id": preview_id, "company_id": company_id, "user_id": user_id, "critique": critique.model_dump(), "created_at": created_at})
    return LandingCritiqueResponse(request_id=request_id, preview_id=preview_id, company_id=company_id, critique=critique, created_at=created_at)