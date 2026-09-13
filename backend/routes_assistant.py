"""Assistente Operacional — Fase 4.

Camada de ferramentas reais que a IA pode invocar. Reusa a infraestrutura
existente das fases 1-3 (mesmas coleções, mesmas regras de conflito, mesmas
permissões). NUNCA confia em company_id do frontend: sempre o membership atual.

Fluxo de tool-calling manual:
1. IA responde JSON `{"tool": "nome", "args": {...}}` OU `{"reply": "texto"}`.
2. Se `tool`, backend executa a função Python (com permissão) e envia o
   resultado como próxima user message para a IA, até ela emitir `reply`.
"""
from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime, timedelta, timezone
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from auth import get_current_user, is_valid_object_id, require_membership
from db import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/assistant", tags=["assistant"])


def _now() -> str: return datetime.now(timezone.utc).isoformat()
def _oid(v):
    if not v or not is_valid_object_id(v): raise ValueError("ID inválido")
    return ObjectId(v)


# ================= TOOLS =================
# Cada tool recebe (ctx, args) onde ctx = {user, membership, company_id, role}
# Retorna dict serializável.
async def t_get_summary(ctx, args):
    from routes_scheduling import _to_minutes, _from_minutes  # noqa
    db = get_db()
    date = args.get("date") or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    q = {"company_id": ctx["company_id"], "date": date}
    if ctx["role"] == "PROFESSIONAL": q["professional_id"] = ctx["user"]["id"]
    docs = await db.appointments.find(q).to_list(500)
    counters = {"PENDING": 0, "CONFIRMED": 0, "COMPLETED": 0, "CANCELLED": 0, "BLOCK": 0}
    revenue = 0.0
    for d in docs:
        counters[d["status"]] = counters.get(d["status"], 0) + 1
        if d["status"] != "CANCELLED": revenue += float(d.get("price", 0) or 0)
    return {"date": date, "total": len(docs), "counters": counters, "revenue": round(revenue, 2)}

async def t_list_appointments(ctx, args):
    db = get_db()
    date_from = args.get("date_from") or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    date_to = args.get("date_to") or date_from
    q = {"company_id": ctx["company_id"], "date": {"$gte": date_from, "$lte": date_to}}
    if ctx["role"] == "PROFESSIONAL": q["professional_id"] = ctx["user"]["id"]
    if args.get("status"): q["status"] = args["status"]
    docs = await db.appointments.find(q).sort([("date", 1), ("start_time", 1)]).to_list(200)
    return {"count": len(docs), "items": [{
        "id": str(d["_id"]), "date": d["date"], "start_time": d["start_time"], "end_time": d["end_time"],
        "client_name": d.get("client_name"), "service_name": d.get("service_name"),
        "professional_name": d.get("professional_name"), "status": d["status"],
        "price": d.get("price", 0),
    } for d in docs[:30]]}

async def t_list_services(ctx, args):
    db = get_db()
    q = {"company_id": ctx["company_id"]}
    if args.get("only_active"): q["is_active"] = True
    docs = await db.services.find(q).sort("name", 1).to_list(200)
    return {"count": len(docs), "items": [{
        "id": str(d["_id"]), "name": d["name"], "duration_min": d["duration_min"],
        "price": d.get("price", 0), "is_active": d.get("is_active", True),
    } for d in docs]}

async def t_create_service(ctx, args):
    if ctx["role"] not in ("OWNER", "MANAGER"): raise PermissionError("Sem permissão para criar serviço")
    name = (args.get("name") or "").strip()
    if len(name) < 1: raise ValueError("Nome obrigatório")
    duration = int(args.get("duration_min") or 30)
    if duration < 5 or duration > 600: raise ValueError("Duração entre 5 e 600 minutos")
    price = float(args.get("price") or 0)
    db = get_db(); n = _now()
    res = await db.services.insert_one({
        "company_id": ctx["company_id"], "name": name,
        "description": args.get("description"), "duration_min": duration,
        "price": price, "is_active": True, "professional_ids": args.get("professional_ids") or [],
        "created_at": n, "updated_at": n,
    })
    return {"id": str(res.inserted_id), "name": name, "duration_min": duration, "price": price}

async def t_update_service(ctx, args):
    if ctx["role"] not in ("OWNER", "MANAGER"): raise PermissionError("Sem permissão")
    db = get_db()
    sid = _oid(args.get("id"))
    updates = {k: v for k, v in args.items() if k in ("name", "description", "duration_min", "price", "is_active") and v is not None}
    if not updates: raise ValueError("Nada para atualizar")
    updates["updated_at"] = _now()
    doc = await db.services.find_one_and_update({"_id": sid, "company_id": ctx["company_id"]},
                                                 {"$set": updates}, return_document=True)
    if not doc: raise ValueError("Serviço não encontrado")
    return {"id": str(doc["_id"]), "name": doc["name"]}

async def t_list_clients(ctx, args):
    db = get_db()
    q = {"company_id": ctx["company_id"]}
    if args.get("search"): q["name"] = {"$regex": args["search"], "$options": "i"}
    docs = await db.clients.find(q).limit(30).to_list(30)
    return {"count": len(docs), "items": [{
        "id": str(d["_id"]), "name": d["name"], "phone": d.get("phone"), "email": d.get("email"),
    } for d in docs]}

async def t_create_client(ctx, args):
    name = (args.get("name") or "").strip()
    if len(name) < 2: raise ValueError("Nome deve ter ao menos 2 letras")
    db = get_db(); n = _now()
    doc = {"company_id": ctx["company_id"], "name": name,
           "phone": args.get("phone"), "email": args.get("email"),
           "birth_date": args.get("birth_date"), "notes": args.get("notes"),
           "created_at": n, "updated_at": n, "source": "assistant"}
    res = await db.clients.insert_one(doc)
    return {"id": str(res.inserted_id), "name": name, "phone": doc["phone"]}

async def t_list_professionals(ctx, args):
    db = get_db()
    memberships = await db.memberships.find({"company_id": ctx["company_id"], "status": "ACTIVE"}).to_list(100)
    if not memberships: return {"items": []}
    users = {}
    for u in await db.users.find({"_id": {"$in": [_oid(m["user_id"]) for m in memberships]}}).to_list(100):
        users[str(u["_id"])] = u["name"]
    return {"items": [{"id": m["user_id"], "name": users.get(m["user_id"], "—"), "role": m["role"]} for m in memberships]}

async def t_create_appointment(ctx, args):
    from routes_scheduling import _resolve_snapshot, _validate_slot, _to_minutes, _from_minutes
    db = get_db()
    client_id = args.get("client_id"); service_id = args.get("service_id")
    pro_id = args.get("professional_id"); date = args.get("date"); start_time = args.get("start_time")
    if not all([client_id, service_id, pro_id, date, start_time]):
        raise ValueError("Necessário: client_id, service_id, professional_id, date, start_time")
    snap = await _resolve_snapshot(ctx["company_id"], client_id, service_id, pro_id)
    duration = snap["service"]["duration_min"]
    await _validate_slot(ctx["company_id"], pro_id, date, start_time, duration)
    end_time = _from_minutes(_to_minutes(start_time) + duration)
    n = _now()
    doc = {
        "company_id": ctx["company_id"],
        "client_id": client_id, "client_name": snap["client"]["name"], "client_phone": snap["client"].get("phone"),
        "service_id": service_id, "service_name": snap["service"]["name"],
        "professional_id": pro_id, "professional_name": snap["pro_user"]["name"],
        "date": date, "start_time": start_time, "end_time": end_time,
        "duration_min": duration, "price": snap["service"].get("price", 0.0),
        "notes": args.get("notes"), "status": args.get("status") or "CONFIRMED",
        "created_at": n, "updated_at": n, "source": "assistant",
    }
    res = await db.appointments.insert_one(doc)
    return {"id": str(res.inserted_id), "start_time": start_time, "end_time": end_time,
            "client_name": doc["client_name"], "service_name": doc["service_name"]}

async def t_cancel_appointment(ctx, args):
    if ctx["role"] not in ("OWNER", "MANAGER"): raise PermissionError("Sem permissão")
    db = get_db()
    aid = _oid(args.get("id"))
    res = await db.appointments.find_one_and_update(
        {"_id": aid, "company_id": ctx["company_id"]},
        {"$set": {"status": "CANCELLED", "updated_at": _now()}}, return_document=True)
    if not res: raise ValueError("Agendamento não encontrado")
    return {"id": str(res["_id"]), "status": "CANCELLED"}

async def t_block_schedule(ctx, args):
    """Bloqueia um intervalo. Adiciona à collection `schedule_blocks` que é
    considerada em `_validate_slot`.
    """
    if ctx["role"] not in ("OWNER", "MANAGER"): raise PermissionError("Sem permissão")
    date = args.get("date"); start = args.get("start_time"); end = args.get("end_time")
    if not all([date, start, end]): raise ValueError("Necessário: date, start_time, end_time")
    db = get_db()
    doc = {"company_id": ctx["company_id"], "date": date, "start_time": start, "end_time": end,
           "professional_id": args.get("professional_id"), "reason": args.get("reason"),
           "created_by": ctx["user"]["id"], "created_at": _now()}
    res = await db.schedule_blocks.insert_one(doc)
    return {"id": str(res.inserted_id), "date": date, "start_time": start, "end_time": end}

async def t_get_availability(ctx, args):
    from routes_scheduling import _default_hours, _weekday_of
    db = get_db()
    date = args.get("date"); pro_id = args.get("professional_id")
    if not date: raise ValueError("date é obrigatório")
    company = await db.companies.find_one({"_id": _oid(ctx["company_id"])})
    hours = None
    if pro_id:
        memb = await db.memberships.find_one({"company_id": ctx["company_id"], "user_id": pro_id})
        if memb: hours = memb.get("availability")
    hours = hours or company.get("business_hours") or _default_hours()
    day = hours.get(_weekday_of(date), {})
    return {"date": date, "day": day, "closed": not day.get("active")}

async def t_update_landing(ctx, args):
    if ctx["role"] not in ("OWNER", "MANAGER"): raise PermissionError("Sem permissão")
    from routes_landing import _get_or_create
    db = get_db()
    doc = await _get_or_create(ctx["company_id"])
    state = doc.get("state") or {}
    patch = args.get("patch") or {}
    def merge(base, upd):
        for k, v in upd.items():
            if isinstance(v, dict) and isinstance(base.get(k), dict): merge(base[k], v)
            else: base[k] = v
    merge(state, patch)
    await db.landing_pages.update_one({"company_id": ctx["company_id"]},
                                      {"$set": {"state": state, "updated_at": _now()}})
    return {"updated": list(patch.keys()), "is_published": state.get("is_published", False)}

TOOLS = {
    "get_summary": (t_get_summary, "Retorna resumo do dia (total, contadores por status, faturamento). Args: {date?}"),
    "list_appointments": (t_list_appointments, "Lista agendamentos por período. Args: {date_from, date_to, status?}"),
    "list_services": (t_list_services, "Lista serviços. Args: {only_active?}"),
    "create_service": (t_create_service, "Cria novo serviço. Args: {name, duration_min, price, description?}"),
    "update_service": (t_update_service, "Atualiza serviço. Args: {id, name?, duration_min?, price?, is_active?}"),
    "list_clients": (t_list_clients, "Lista clientes. Args: {search?}"),
    "create_client": (t_create_client, "Cria cliente. Args: {name, phone?, email?, notes?}"),
    "list_professionals": (t_list_professionals, "Lista profissionais/membros da empresa."),
    "create_appointment": (t_create_appointment, "Cria agendamento. Args: {client_id, service_id, professional_id, date, start_time, notes?, status?}"),
    "cancel_appointment": (t_cancel_appointment, "Cancela agendamento. Args: {id}"),
    "block_schedule": (t_block_schedule, "Bloqueia intervalo na agenda. Args: {date, start_time, end_time, professional_id?, reason?}"),
    "get_availability": (t_get_availability, "Consulta horário do dia. Args: {date, professional_id?}"),
    "update_landing": (t_update_landing, "Atualiza state da landing page (patch profundo). Args: {patch: {...}}"),
}


# ================= AUDIT =================
async def _audit(ctx, event: str, payload: dict):
    try:
        db = get_db()
        await db.assistant_audit.insert_one({
            "company_id": ctx["company_id"], "user_id": ctx["user"]["id"], "role": ctx["role"],
            "event": event, "payload": payload, "at": _now(),
        })
    except Exception as e:
        logger.warning("audit failed: %s", e)


# ================= CHAT =================
def _tools_description() -> str:
    lines = []
    for name, (_, desc) in TOOLS.items():
        lines.append(f"- {name}: {desc}")
    return "\n".join(lines)

SYSTEM_PROMPT_TEMPLATE = """Você é a assistente operacional do Gestão SaaS. Fale sempre em português do Brasil, com ortografia, acentuação e concordância corretas. Tom natural, profissional, amigável — como uma gerente digital experiente conversando com o proprietário de um negócio local (barbearia, salão, manicure, estética, pet shop).

DATA/HORA ATUAL: {now}
EMPRESA: {company_name} ({business_type})
USUÁRIO: {user_name} (papel {role})
ROTA ATUAL: {route}

VOCÊ TEM ACESSO ÀS SEGUINTES FERRAMENTAS QUE EXECUTAM AÇÕES REAIS NO SISTEMA:
{tools}

REGRAS INEGOCIÁVEIS:
1. Responda SEMPRE em JSON válido, sem texto fora do JSON, sem markdown.
2. Use apenas UM destes dois formatos:
   • Ação: {{"tool": "nome_da_ferramenta", "args": {{...}}}}
   • Resposta final ao usuário: {{"reply": "sua mensagem", "suggestions": ["sugestão 1","sugestão 2","sugestão 3"]}}
3. Antes de executar operações destrutivas (cancelar múltiplos agendamentos, bloquear grandes períodos, excluir dados), responda com `reply` pedindo confirmação e liste o que acontecerá — só execute depois que o usuário confirmar.
4. NUNCA invente clientes, serviços, preços, faturamento, avaliações, depoimentos, disponibilidade ou horários. Se não sabe, consulte com uma ferramenta ou peça ao usuário.
5. Ao criar um agendamento você precisa dos IDs reais (client_id, service_id, professional_id). Se o usuário não informar, use `list_clients`, `list_services`, `list_professionals` para resolver — mas nunca invente IDs.
6. Se a ferramenta retornar erro (`error`), explique ao usuário de forma clara em português e sugira o próximo passo.
7. Datas: interprete "hoje", "amanhã", "sexta", etc., convertendo para YYYY-MM-DD com base na data atual. Horas: HH:MM 24h.
8. Sugira 2-4 próximas ações relevantes ao contexto atual (rota, últimas ações) no campo `suggestions`.
9. Nunca ultrapasse as permissões do usuário. Se a ferramenta retornar `permission_error`, informe educadamente.
"""


class AssistantIn(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    route: str | None = None  # rota atual do frontend, dá contexto para sugestões
    reset: bool = False


@router.get("/history")
async def history(user=Depends(get_current_user), m=Depends(require_membership)):
    db = get_db()
    doc = await db.assistant_sessions.find_one({"company_id": m["company_id"], "user_id": user["id"]})
    return {"messages": (doc or {}).get("messages", [])[-40:]}


@router.post("/reset")
async def reset_history(user=Depends(get_current_user), m=Depends(require_membership)):
    db = get_db()
    await db.assistant_sessions.update_one(
        {"company_id": m["company_id"], "user_id": user["id"]},
        {"$set": {"messages": [], "updated_at": _now()}}, upsert=True,
    )
    return {"success": True}


@router.post("/chat")
async def chat(payload: AssistantIn, user=Depends(get_current_user), m=Depends(require_membership)):
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    db = get_db()
    company = await db.companies.find_one({"_id": _oid(m["company_id"])})
    key = os.environ.get("EMERGENT_LLM_KEY")
    if not key: raise HTTPException(503, "IA indisponível")

    session_doc = await db.assistant_sessions.find_one(
        {"company_id": m["company_id"], "user_id": user["id"]}) or {"messages": []}
    history_msgs = [] if payload.reset else session_doc.get("messages", [])[-20:]

    ctx = {"user": user, "membership": m, "company_id": m["company_id"], "role": m["role"]}
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        now=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        company_name=company["name"], business_type=company["business_type"],
        user_name=user["name"], role=m["role"], route=payload.route or "/dashboard",
        tools=_tools_description(),
    )

    chat_client = LlmChat(api_key=key, session_id=f"assistant-{m['company_id']}-{user['id']}",
                          system_message=system_prompt).with_model("openai", "gpt-4o-mini")
    for h in history_msgs:
        if h.get("role") in ("user", "assistant"):
            chat_client.messages.append({"role": h["role"], "content": h["content"]})

    all_messages = list(history_msgs) + [{"role": "user", "content": payload.message, "at": _now()}]
    current_input = payload.message
    tool_trace = []

    for step in range(4):  # até 4 iterações de tool calling
        try:
            raw = await chat_client.send_message(UserMessage(text=current_input))
        except Exception as e:
            raise HTTPException(502, f"IA falhou: {e}")

        parsed = _parse_response(raw)

        if "tool" in parsed:
            tname = parsed["tool"]; targs = parsed.get("args") or {}
            fn = TOOLS.get(tname)
            if not fn:
                current_input = json.dumps({"error": f"Ferramenta desconhecida: {tname}"})
                continue
            try:
                result = await fn[0](ctx, targs)
                await _audit(ctx, f"tool.{tname}", {"args": targs, "ok": True})
                tool_trace.append({"tool": tname, "args": targs, "ok": True})
                current_input = json.dumps({"tool_result": {tname: result}}, ensure_ascii=False, default=str)
            except PermissionError as pe:
                await _audit(ctx, f"tool.{tname}.denied", {"args": targs})
                current_input = json.dumps({"permission_error": str(pe)})
            except Exception as ex:
                await _audit(ctx, f"tool.{tname}.error", {"args": targs, "err": str(ex)})
                current_input = json.dumps({"error": str(ex)})
            continue

        reply_text = parsed.get("reply") or raw
        suggestions = parsed.get("suggestions") or []
        all_messages.append({"role": "assistant", "content": reply_text, "at": _now(),
                             "suggestions": suggestions, "tools": tool_trace})
        await db.assistant_sessions.update_one(
            {"company_id": m["company_id"], "user_id": user["id"]},
            {"$set": {"messages": all_messages[-40:], "updated_at": _now()}}, upsert=True)
        return {"reply": reply_text, "suggestions": suggestions, "tools_used": tool_trace,
                "messages": all_messages[-40:]}

    # Se passou de 4 iterações
    fallback = "Não consegui concluir a operação. Pode tentar reformular?"
    all_messages.append({"role": "assistant", "content": fallback, "at": _now(),
                         "suggestions": [], "tools": tool_trace})
    await db.assistant_sessions.update_one(
        {"company_id": m["company_id"], "user_id": user["id"]},
        {"$set": {"messages": all_messages[-40:], "updated_at": _now()}}, upsert=True)
    return {"reply": fallback, "suggestions": [], "tools_used": tool_trace, "messages": all_messages[-40:]}


def _parse_response(raw: str) -> dict:
    s = (raw or "").strip()
    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?\s*", "", s)
        s = re.sub(r"\s*```$", "", s)
    try:
        return json.loads(s)
    except Exception:
        # tenta extrair JSON de dentro do texto
        m = re.search(r"\{[\s\S]*\}", s)
        if m:
            try: return json.loads(m.group(0))
            except Exception: pass
        return {"reply": raw}
