"""Landing Page + AI chat construtora — Fase 3."""
from __future__ import annotations
import json
import os
import uuid
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from auth import get_current_user, is_valid_object_id, require_membership, require_roles
from db import get_db
from storage import build_upload_path, put_object

router = APIRouter(prefix="/landing", tags=["landing"])
public_router = APIRouter(prefix="/public", tags=["public"])

def _now() -> str: return datetime.now(timezone.utc).isoformat()

DEFAULT_STATE = {
    "sections": {"hero": True, "about": True, "services": True, "professionals": False,
                 "gallery": True, "differentiators": True, "hours": True, "contact": True},
    "hero": {"title": "", "subtitle": "", "description": "", "cta": "Agendar horário"},
    "about": {"text": ""},
    "differentiators": [],
    "gallery": [],  # list of {url, caption}
    "style": {"theme": "modern", "primary_color": "#4f46e5"},
    "contact": {"whatsapp": "", "instagram": "", "facebook": ""},
    "is_published": False,
}

def _serialize(doc: dict) -> dict:
    return {"id": str(doc["_id"]), **{k: v for k, v in doc.items() if k not in ("_id", "company_id")},
            "company_id": doc["company_id"]}

async def _get_or_create(company_id: str) -> dict:
    db = get_db()
    doc = await db.landing_pages.find_one({"company_id": company_id})
    if not doc:
        doc = {"company_id": company_id, "messages": [], "state": DEFAULT_STATE.copy(),
               "created_at": _now(), "updated_at": _now()}
        res = await db.landing_pages.insert_one(doc)
        doc["_id"] = res.inserted_id
    return doc

@router.get("/me")
async def get_landing(m=Depends(require_membership)):
    doc = await _get_or_create(m["company_id"])
    return _serialize(doc)

class StateUpdate(BaseModel):
    state: dict

@router.put("/me/state")
async def save_state(payload: StateUpdate, m=Depends(require_roles("OWNER", "MANAGER"))):
    db = get_db()
    await _get_or_create(m["company_id"])
    await db.landing_pages.update_one(
        {"company_id": m["company_id"]},
        {"$set": {"state": payload.state, "updated_at": _now()}},
    )
    return {"success": True}

@router.post("/me/publish")
async def publish(m=Depends(require_roles("OWNER", "MANAGER"))):
    db = get_db()
    doc = await _get_or_create(m["company_id"])
    st = doc.get("state", {}).copy()
    st["is_published"] = True
    await db.landing_pages.update_one({"company_id": m["company_id"]},
                                      {"$set": {"state": st, "updated_at": _now()}})
    return {"published": True}

@router.post("/me/gallery")
async def upload_gallery(file: UploadFile = File(...), m=Depends(require_roles("OWNER", "MANAGER"))):
    if file.content_type not in {"image/jpeg", "image/png", "image/webp", "image/gif"}:
        raise HTTPException(400, "Formato não suportado")
    data = await file.read()
    if len(data) > 6 * 1024 * 1024: raise HTTPException(413, "Máximo 6MB")
    path = build_upload_path(m["company_id"], file.filename or "img.jpg")
    result = put_object(path, data, file.content_type)
    db = get_db()
    await db.files.insert_one({"storage_path": result["path"], "company_id": m["company_id"],
                               "uploaded_by": m["user_id"], "content_type": file.content_type,
                               "kind": "landing_gallery", "is_deleted": False, "created_at": _now()})
    url = f"/api/uploads/file/{result['path']}"
    doc = await _get_or_create(m["company_id"])
    gallery = doc.get("state", {}).get("gallery", [])
    gallery.append({"url": url, "id": str(uuid.uuid4())})
    st = doc.get("state", {}).copy(); st["gallery"] = gallery
    await db.landing_pages.update_one({"company_id": m["company_id"]},
                                      {"$set": {"state": st, "updated_at": _now()}})
    return {"url": url, "path": result["path"], "gallery": gallery}


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=4000)

SYSTEM_PROMPT = """Você é uma assistente especialista em criar landing pages para pequenos negócios brasileiros de serviços (barbearias, salões, manicures, estética, pet shops). Fale português BR, tom natural, humano, entusiasmado com emojis moderados.

Você conversa com o proprietário para criar a página. Faça UMA pergunta por vez, adapte-se ao tipo de negócio, seja concisa (máximo 2-3 frases). Nunca invente certificações, prêmios, depoimentos ou dados não fornecidos.

FORMATO DE RESPOSTA OBRIGATÓRIO (JSON válido):
{
  "reply": "sua fala natural aqui",
  "state_patch": { ... campos do state que devem ser atualizados ... },
  "ask_photos": true/false
}

O state atual da landing page será fornecido. Atualize apenas campos que a nova informação permite preencher (title, subtitle, description, about.text, differentiators [array de strings], contact.whatsapp/instagram/facebook, style.theme in ['modern','premium','minimal','elegant','urban']). Não inclua campos vazios em state_patch. Quando fizer sentido pedir fotos, marque ask_photos=true.

Se o usuário pedir alteração ("mais moderno", "trocar frase", etc), aplique diretamente no state_patch. Quando tiver informações suficientes (nome + descrição + 1 diferencial + contato) diga que a página está pronta e sugira publicar."""

@router.post("/me/chat")
async def chat(payload: ChatIn, user=Depends(get_current_user), m=Depends(require_roles("OWNER", "MANAGER"))):
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    db = get_db()
    doc = await _get_or_create(m["company_id"])
    messages = doc.get("messages", [])
    state = doc.get("state") or DEFAULT_STATE.copy()
    company = await db.companies.find_one({"_id": ObjectId(m["company_id"])})

    session_id = f"landing-{m['company_id']}"
    key = os.environ.get("EMERGENT_LLM_KEY")
    if not key: raise HTTPException(503, "IA indisponível")

    context = f"State atual: {json.dumps(state, ensure_ascii=False)}\nEmpresa: {company['name']} ({company['business_type']})\n\nUsuário: {payload.message}"
    chat = LlmChat(api_key=key, session_id=session_id, system_message=SYSTEM_PROMPT).with_model("openai", "gpt-4o-mini")
    # Replay history
    for msg in messages[-12:]:
        if msg["role"] == "user": chat.messages.append({"role": "user", "content": msg["content"]})
        elif msg["role"] == "assistant": chat.messages.append({"role": "assistant", "content": msg["content"]})
    try:
        raw = await chat.send_message(UserMessage(text=context))
    except Exception as e:
        raise HTTPException(502, f"IA falhou: {e}")

    reply_text, patch, ask_photos = raw, {}, False
    try:
        # Extract JSON from response
        s = raw.strip()
        if s.startswith("```"): s = s.split("```", 2)[1].lstrip("json").strip()
        parsed = json.loads(s)
        reply_text = parsed.get("reply", raw)
        patch = parsed.get("state_patch", {}) or {}
        ask_photos = bool(parsed.get("ask_photos", False))
    except Exception:
        pass

    # Deep-merge patch into state
    def merge(base, upd):
        for k, v in upd.items():
            if isinstance(v, dict) and isinstance(base.get(k), dict):
                merge(base[k], v)
            else:
                base[k] = v
    merge(state, patch)

    messages.append({"role": "user", "content": payload.message, "at": _now()})
    messages.append({"role": "assistant", "content": reply_text, "at": _now(), "ask_photos": ask_photos})
    await db.landing_pages.update_one({"company_id": m["company_id"]},
                                      {"$set": {"messages": messages, "state": state, "updated_at": _now()}})
    return {"reply": reply_text, "state": state, "ask_photos": ask_photos, "messages": messages}


# ============ PUBLIC ============
@public_router.get("/{slug}")
async def public_page(slug: str):
    db = get_db()
    comp = await db.companies.find_one({"slug": slug, "status": "ACTIVE"})
    if not comp: raise HTTPException(404, "Página não encontrada")
    lp = await db.landing_pages.find_one({"company_id": str(comp["_id"])})
    state = (lp or {}).get("state", {}) if lp else {}
    if not state.get("is_published"): raise HTTPException(404, "Página ainda não publicada")
    services = await db.services.find({"company_id": str(comp["_id"]), "is_active": True}).to_list(100)
    return {
        "company": {"id": str(comp["_id"]), "name": comp["name"], "slug": comp["slug"],
                    "business_type": comp["business_type"], "logo_url": comp.get("logo_url"),
                    "establishment_photo_url": comp.get("establishment_photo_url"),
                    "description": comp.get("description"), "phone": comp.get("phone"),
                    "email": comp.get("email"), "address": comp.get("address"),
                    "city": comp.get("city"), "state": comp.get("state"), "zip_code": comp.get("zip_code"),
                    "business_hours": comp.get("business_hours")},
        "state": state,
        "services": [{"id": str(s["_id"]), "name": s["name"], "description": s.get("description"),
                      "duration_min": s["duration_min"], "price": s.get("price", 0)} for s in services],
    }

@public_router.get("/uploads/{path:path}")
async def public_file(path: str):
    """Public file access for images referenced in published landing pages."""
    from storage import get_object
    from fastapi import Response
    db = get_db()
    rec = await db.files.find_one({"storage_path": path, "is_deleted": False})
    if not rec: raise HTTPException(404, "Arquivo não encontrado")
    try:
        data, ct = get_object(path)
    except Exception as e:
        raise HTTPException(502, str(e))
    return Response(content=data, media_type=rec.get("content_type", ct))
