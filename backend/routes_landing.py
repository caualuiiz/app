"""Landing Page + AI chat + análise de imagens + agendamento público — Fase 3+."""
from __future__ import annotations
import base64
import json
import os
import uuid
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from pydantic import BaseModel, EmailStr, Field
from auth import get_current_user, is_valid_object_id, require_membership, require_roles
from db import get_db
from storage import build_upload_path, get_object, put_object

router = APIRouter(prefix="/landing", tags=["landing"])
public_router = APIRouter(prefix="/public", tags=["public"])

def _now() -> str: return datetime.now(timezone.utc).isoformat()
def _oid(v: str):
    if not is_valid_object_id(v): raise HTTPException(400, "ID inválido")
    return ObjectId(v)

DEFAULT_STATE = {
    "sections": {"hero": True, "about": True, "services": True, "professionals": False,
                 "gallery": True, "differentiators": True, "hours": True, "contact": True},
    "hero": {"title": "", "subtitle": "", "description": "", "cta": "Agendar horário", "featured_image": None},
    "about": {"text": ""},
    "differentiators": [],
    "gallery": [],
    "style": {"theme": "modern", "primary_color": "#4f46e5", "secondary_color": "#0f172a"},
    "contact": {"whatsapp": "", "instagram": "", "facebook": ""},
    "photo_analysis": None,
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
    else:
        # Backfill new keys for pre-existing docs
        st = doc.get("state") or {}
        for k, v in DEFAULT_STATE.items():
            st.setdefault(k, v)
        doc["state"] = st
    return doc

@router.get("/me")
async def get_landing(m=Depends(require_membership)):
    return _serialize(await _get_or_create(m["company_id"]))

class StateUpdate(BaseModel):
    state: dict

@router.put("/me/state")
async def save_state(payload: StateUpdate, m=Depends(require_roles("OWNER", "MANAGER"))):
    db = get_db()
    await _get_or_create(m["company_id"])
    await db.landing_pages.update_one({"company_id": m["company_id"]},
                                      {"$set": {"state": payload.state, "updated_at": _now()}})
    return {"success": True}

@router.post("/me/publish")
async def publish(m=Depends(require_roles("OWNER", "MANAGER"))):
    db = get_db()
    doc = await _get_or_create(m["company_id"])
    st = doc.get("state", {}).copy(); st["is_published"] = True
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
    gallery.append({"url": url, "id": str(uuid.uuid4()), "path": result["path"]})
    st = doc.get("state", {}).copy(); st["gallery"] = gallery
    await db.landing_pages.update_one({"company_id": m["company_id"]},
                                      {"$set": {"state": st, "updated_at": _now()}})
    return {"url": url, "path": result["path"], "gallery": gallery}

@router.delete("/me/gallery/{item_id}")
async def delete_gallery(item_id: str, m=Depends(require_roles("OWNER", "MANAGER"))):
    db = get_db()
    doc = await _get_or_create(m["company_id"])
    st = doc.get("state", {}).copy()
    st["gallery"] = [g for g in st.get("gallery", []) if g.get("id") != item_id]
    await db.landing_pages.update_one({"company_id": m["company_id"]}, {"$set": {"state": st, "updated_at": _now()}})
    return {"gallery": st["gallery"]}


SYSTEM_PROMPT = """Você é uma assistente especialista em criar landing pages para pequenos negócios brasileiros de serviços (barbearias, salões, manicures, estética, pet shops). Fale português BR, tom natural, humano, entusiasmado com emojis moderados.

Faça UMA pergunta por vez, seja concisa (2-3 frases). Nunca invente certificações, prêmios, depoimentos ou dados não fornecidos.

FORMATO DE RESPOSTA OBRIGATÓRIO (JSON válido, sem texto extra):
{"reply": "sua fala natural", "state_patch": {...campos que devem mudar...}, "ask_photos": true|false, "suggestions": ["sugestão curta 1","sugestão curta 2","sugestão curta 3"]}

Campos possíveis do state_patch: hero.title, hero.subtitle, hero.description, hero.cta, about.text, differentiators (array de strings), contact.whatsapp, contact.instagram, contact.facebook, style.theme (modern|premium|minimal|elegant|urban), style.primary_color (#hex), style.secondary_color (#hex), sections.<name> (true|false).

Retorne 2-4 sugestões curtas de próximas ações que o usuário pode clicar (ex: "Deixar mais moderno", "Trocar cor primária", "Adicionar diferencial")."""

async def _run_llm(company_id: str, message: str, image_paths: list[str] | None = None):
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    db = get_db()
    doc = await _get_or_create(company_id)
    messages = doc.get("messages", [])
    state = doc.get("state") or DEFAULT_STATE.copy()
    company = await db.companies.find_one({"_id": _oid(company_id)})
    key = os.environ.get("EMERGENT_LLM_KEY")
    if not key: raise HTTPException(503, "IA indisponível")

    ctx_state = {k: state.get(k) for k in ["hero", "about", "differentiators", "style", "contact", "sections"]}
    context = f"State atual: {json.dumps(ctx_state, ensure_ascii=False)}\nEmpresa: {company['name']} ({company['business_type']})\n\nUsuário: {message}"

    session_id = f"landing-{company_id}"
    chat = LlmChat(api_key=key, session_id=session_id, system_message=SYSTEM_PROMPT).with_model("openai", "gpt-4o-mini")
    for msg in messages[-10:]:
        if msg["role"] in ("user", "assistant"):
            chat.messages.append({"role": msg["role"], "content": msg["content"]})

    # Attach images (multi-modal) if provided
    file_contents = None
    if image_paths:
        try:
            from emergentintegrations.llm.chat import ImageContent
            file_contents = []
            for p in image_paths[:4]:
                try:
                    data, _ = get_object(p)
                    b64 = base64.b64encode(data).decode()
                    file_contents.append(ImageContent(image_base64=b64))
                except Exception: pass
        except Exception:
            file_contents = None

    try:
        um = UserMessage(text=context, file_contents=file_contents) if file_contents else UserMessage(text=context)
        raw = await chat.send_message(um)
    except Exception as e:
        raise HTTPException(502, f"IA falhou: {e}")

    reply_text, patch, ask_photos, suggestions = raw, {}, False, []
    try:
        s = raw.strip()
        if s.startswith("```"): s = s.split("```", 2)[1].lstrip("json").strip()
        parsed = json.loads(s)
        reply_text = parsed.get("reply", raw)
        patch = parsed.get("state_patch", {}) or {}
        ask_photos = bool(parsed.get("ask_photos", False))
        suggestions = parsed.get("suggestions") or []
    except Exception:
        pass

    def merge(base, upd):
        for k, v in upd.items():
            if isinstance(v, dict) and isinstance(base.get(k), dict): merge(base[k], v)
            else: base[k] = v
    merge(state, patch)

    messages.append({"role": "user", "content": message, "at": _now()})
    messages.append({"role": "assistant", "content": reply_text, "at": _now(), "suggestions": suggestions})
    await db.landing_pages.update_one({"company_id": company_id},
                                      {"$set": {"messages": messages, "state": state, "updated_at": _now()}})
    return {"reply": reply_text, "state": state, "ask_photos": ask_photos, "messages": messages, "suggestions": suggestions}


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=4000)

@router.post("/me/chat")
async def chat(payload: ChatIn, m=Depends(require_roles("OWNER", "MANAGER"))):
    return await _run_llm(m["company_id"], payload.message)


@router.post("/me/analyze-gallery")
async def analyze_gallery(m=Depends(require_roles("OWNER", "MANAGER"))):
    """Envia fotos da galeria + fachada/logo para a IA e atualiza estilo/textos com base no que ela identificar."""
    db = get_db()
    doc = await _get_or_create(m["company_id"])
    company = await db.companies.find_one({"_id": _oid(m["company_id"])})
    paths = []
    if company.get("establishment_photo_url"):
        p = company["establishment_photo_url"].replace("/api/uploads/file/", "")
        paths.append(p)
    for g in (doc.get("state", {}).get("gallery") or [])[:3]:
        if g.get("path"): paths.append(g["path"])
        elif g.get("url"): paths.append(g["url"].replace("/api/uploads/file/", ""))
    if not paths:
        raise HTTPException(400, "Envie ao menos uma foto para eu analisar")

    prompt = (
        "Analise VISUALMENTE as fotos que enviei do meu estabelecimento. "
        "Descreva rapidamente ambiente/cores/estilo real que você vê nas imagens (não invente nada que não estiver na foto). "
        "Depois sugira: 1) uma cor primária hexadecimal derivada da paleta real das fotos, 2) tema (modern/premium/minimal/elegant/urban), "
        "3) um subtitle e um description novos para o hero que combinem com o que você viu, "
        "4) 3 diferenciais plausíveis com base no ambiente. "
        "Aplique tudo no state_patch."
    )
    return await _run_llm(m["company_id"], prompt, image_paths=paths)


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
        "company": _company_public(comp),
        "state": state,
        "services": [_svc_public(s) for s in services],
    }

def _company_public(comp: dict) -> dict:
    return {"id": str(comp["_id"]), "name": comp["name"], "slug": comp["slug"],
            "business_type": comp["business_type"], "logo_url": comp.get("logo_url"),
            "establishment_photo_url": comp.get("establishment_photo_url"),
            "description": comp.get("description"), "phone": comp.get("phone"),
            "email": comp.get("email"), "address": comp.get("address"),
            "city": comp.get("city"), "state": comp.get("state"), "zip_code": comp.get("zip_code"),
            "business_hours": comp.get("business_hours")}

def _svc_public(s: dict) -> dict:
    return {"id": str(s["_id"]), "name": s["name"], "description": s.get("description"),
            "duration_min": s["duration_min"], "price": s.get("price", 0),
            "professional_ids": s.get("professional_ids", [])}

@public_router.get("/uploads/{path:path}")
async def public_file(path: str):
    db = get_db()
    rec = await db.files.find_one({"storage_path": path, "is_deleted": False})
    if not rec: raise HTTPException(404, "Arquivo não encontrado")
    try: data, ct = get_object(path)
    except Exception as e: raise HTTPException(502, str(e))
    return Response(content=data, media_type=rec.get("content_type", ct))


# ============ PUBLIC BOOKING ============
async def _resolve_public_company(slug: str) -> dict:
    db = get_db()
    comp = await db.companies.find_one({"slug": slug, "status": "ACTIVE"})
    if not comp: raise HTTPException(404, "Empresa não encontrada")
    lp = await db.landing_pages.find_one({"company_id": str(comp["_id"])})
    if not lp or not (lp.get("state", {}) or {}).get("is_published"):
        raise HTTPException(404, "Página não publicada")
    return comp

@public_router.get("/{slug}/booking-context")
async def booking_context(slug: str):
    """Serviços ativos + profissionais + horários da empresa."""
    db = get_db()
    comp = await _resolve_public_company(slug)
    cid = str(comp["_id"])
    services = await db.services.find({"company_id": cid, "is_active": True}).to_list(100)
    memberships = await db.memberships.find({"company_id": cid, "status": "ACTIVE"}).to_list(100)
    users = {}
    if memberships:
        uids = [_oid(mm["user_id"]) for mm in memberships]
        for u in await db.users.find({"_id": {"$in": uids}}).to_list(100):
            users[str(u["_id"])] = u["name"]
    pros = [{"id": mm["user_id"], "name": users.get(mm["user_id"], "—"), "role": mm["role"]} for mm in memberships]
    return {
        "company": {"name": comp["name"], "slug": comp["slug"], "business_type": comp["business_type"]},
        "services": [_svc_public(s) for s in services],
        "professionals": pros,
        "business_hours": comp.get("business_hours"),
    }

@public_router.get("/{slug}/slots")
async def public_slots(slug: str, service_id: str, professional_id: str, date: str):
    """Slots livres HH:MM para service+professional+date, respeitando horários e conflitos."""
    from routes_scheduling import _default_hours, _to_minutes, _from_minutes, _weekday_of
    db = get_db()
    comp = await _resolve_public_company(slug)
    cid = str(comp["_id"])
    service = await db.services.find_one({"_id": _oid(service_id), "company_id": cid, "is_active": True})
    if not service: raise HTTPException(400, "Serviço inválido")
    allowed = service.get("professional_ids") or []
    if allowed and professional_id not in allowed:
        raise HTTPException(400, "Profissional não executa este serviço")
    memb = await db.memberships.find_one({"user_id": professional_id, "company_id": cid, "status": "ACTIVE"})
    if not memb: raise HTTPException(400, "Profissional inválido")

    hours = memb.get("availability") or comp.get("business_hours") or _default_hours()
    day = hours.get(_weekday_of(date), {})
    if not day.get("active"): return {"slots": []}

    dur = service["duration_min"]
    step = 30
    open_m = _to_minutes(day["open"]); close_m = _to_minutes(day["close"])
    br_s = _to_minutes(day["break_start"]) if day.get("break_start") else None
    br_e = _to_minutes(day["break_end"]) if day.get("break_end") else None

    existing = await db.appointments.find({
        "company_id": cid, "professional_id": professional_id, "date": date,
        "status": {"$ne": "CANCELLED"},
    }).to_list(500)
    busy = [(_to_minutes(a["start_time"]), _to_minutes(a["start_time"]) + a["duration_min"]) for a in existing]

    slots = []
    t = open_m
    while t + dur <= close_m:
        end = t + dur
        conflict = False
        if br_s is not None and not (end <= br_s or t >= br_e): conflict = True
        for (a1, a2) in busy:
            if not (end <= a1 or t >= a2): conflict = True; break
        if not conflict:
            slots.append(_from_minutes(t))
        t += step
    return {"slots": slots}


class PublicBookIn(BaseModel):
    service_id: str
    professional_id: str
    date: str
    start_time: str
    client_name: str = Field(min_length=2, max_length=120)
    client_phone: str = Field(min_length=6, max_length=40)
    client_email: EmailStr | None = None
    notes: str | None = Field(default=None, max_length=500)

@public_router.post("/{slug}/book", status_code=201)
async def public_book(slug: str, payload: PublicBookIn):
    from routes_scheduling import _validate_slot, _to_minutes, _from_minutes
    db = get_db()
    comp = await _resolve_public_company(slug)
    cid = str(comp["_id"])
    service = await db.services.find_one({"_id": _oid(payload.service_id), "company_id": cid, "is_active": True})
    if not service: raise HTTPException(400, "Serviço inválido")
    memb = await db.memberships.find_one({"user_id": payload.professional_id, "company_id": cid, "status": "ACTIVE"})
    if not memb: raise HTTPException(400, "Profissional inválido")
    pro_user = await db.users.find_one({"_id": _oid(payload.professional_id)})
    if not pro_user: raise HTTPException(400, "Profissional inválido")
    allowed = service.get("professional_ids") or []
    if allowed and payload.professional_id not in allowed:
        raise HTTPException(400, "Profissional não executa este serviço")

    duration = service["duration_min"]
    await _validate_slot(cid, payload.professional_id, payload.date, payload.start_time, duration)

    # find or create client (by phone) within this tenant
    client = await db.clients.find_one({"company_id": cid, "phone": payload.client_phone})
    n = _now()
    if not client:
        client_doc = {"company_id": cid, "name": payload.client_name.strip(),
                      "phone": payload.client_phone, "email": payload.client_email,
                      "created_at": n, "updated_at": n, "source": "public_landing"}
        res = await db.clients.insert_one(client_doc)
        client = {"_id": res.inserted_id, **client_doc}
    else:
        # update name if not set
        if client["name"] != payload.client_name.strip():
            await db.clients.update_one({"_id": client["_id"]}, {"$set": {"name": payload.client_name.strip(), "updated_at": n}})

    end_time = _from_minutes(_to_minutes(payload.start_time) + duration)
    appt = {
        "company_id": cid,
        "client_id": str(client["_id"]), "client_name": payload.client_name.strip(), "client_phone": payload.client_phone,
        "service_id": str(service["_id"]), "service_name": service["name"],
        "professional_id": payload.professional_id, "professional_name": pro_user["name"],
        "date": payload.date, "start_time": payload.start_time, "end_time": end_time,
        "duration_min": duration, "price": service.get("price", 0.0),
        "notes": payload.notes, "status": "PENDING",
        "source": "public_landing",
        "created_at": n, "updated_at": n,
    }
    res = await db.appointments.insert_one(appt)
    return {"id": str(res.inserted_id), "date": payload.date, "start_time": payload.start_time,
            "end_time": end_time, "service_name": service["name"], "professional_name": pro_user["name"],
            "company_name": comp["name"], "status": "PENDING"}
