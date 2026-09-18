import uuid
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import HTTPException

from db import get_db
from .orchestrator import AIOrchestrator
from .provider_factory import get_ai_provider


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def _latest(db, collection: str, company_id: str):
    return await db[collection].find_one({"company_id": company_id}, sort=[("created_at", -1)])


async def create_ai_decision(company_id: str, user_id: str):
    db = get_db()
    try:
        company = await db.companies.find_one({"_id": ObjectId(company_id)})
    except Exception as exc:
        raise HTTPException(400, "Empresa inválida") from exc
    landing = await db.landing_pages.find_one({"company_id": company_id})
    if not company or not landing:
        raise HTTPException(404, "Empresa ou landing não encontrada")
    state = landing.get("state") or {}
    context = {
        "company": {"name": company.get("name"), "business_type": company.get("business_type"), "description": company.get("description"), "city": company.get("city")},
        "landing": {"hero": state.get("hero"), "about": state.get("about"), "style": state.get("style"), "sections": state.get("sections")},
        "visual_intelligence": await _latest(db, "visual_profiles", company_id),
        "reference_intelligence": await _latest(db, "reference_profiles", company_id),
        "art_direction": await _latest(db, "art_directions", company_id),
        "design_system": await _latest(db, "design_systems", company_id),
        "layout_plan": await _latest(db, "layout_plans", company_id),
    }
    orchestrator = AIOrchestrator(get_ai_provider())
    try:
        decision = await orchestrator.decide(context=context)
    except ValueError as exc:
        raise HTTPException(502, "Decisão da IA rejeitada pela validação") from exc
    except RuntimeError as exc:
        raise HTTPException(503, "Provider de IA indisponível") from exc
    doc = {"request_id": str(uuid.uuid4()), "company_id": company_id, "user_id": user_id, "provider": orchestrator.provider.name, "model": getattr(orchestrator.provider, "model", None), "decision": decision.model_dump(), "created_at": _now()}
    await db.landing_decisions.insert_one(doc)
    return {"request_id": doc["request_id"], "provider": doc["provider"], "model": doc["model"], "decision": decision, "created_at": doc["created_at"]}