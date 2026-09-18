"""Clientes, Serviços, Disponibilidade, Agendamentos - Fase 2."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Literal
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field
from auth import get_current_user, is_valid_object_id, require_membership, require_roles
from db import get_db
from feature_limits import enforce_limit
from whatsapp import send_booking_status, WhatsAppUnavailable

AppointmentStatus = Literal["PENDING", "CONFIRMED", "COMPLETED", "CANCELLED"]
Weekday = Literal["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
WEEKDAYS = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _oid(v: str) -> ObjectId:
    if not is_valid_object_id(v):
        raise HTTPException(status_code=400, detail="ID inválido")
    return ObjectId(v)


# ============ CLIENTES ============
clients_router = APIRouter(prefix="/clients", tags=["clients"])

class ClientIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    phone: str | None = Field(default=None, max_length=40)
    email: EmailStr | None = None
    birth_date: str | None = Field(default=None, max_length=10)  # YYYY-MM-DD
    notes: str | None = Field(default=None, max_length=2000)

def _client_out(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]), "name": doc["name"], "phone": doc.get("phone"),
        "email": doc.get("email"), "birth_date": doc.get("birth_date"),
        "notes": doc.get("notes"), "created_at": doc["created_at"],
        "updated_at": doc.get("updated_at", doc["created_at"]),
    }

@clients_router.get("")
async def list_clients(search: str = "", m=Depends(require_membership)):
    db = get_db()
    q = {"company_id": m["company_id"]}
    if search:
        q["name"] = {"$regex": search, "$options": "i"}
    docs = await db.clients.find(q).sort("name", 1).to_list(1000)
    return [_client_out(d) for d in docs]

@clients_router.post("", status_code=201)
async def create_client(payload: ClientIn, m=Depends(require_roles("OWNER", "MANAGER", "PROFESSIONAL"))):
    db = get_db()
    n = now_iso()
    doc = {**payload.model_dump(), "company_id": m["company_id"], "created_at": n, "updated_at": n}
    res = await db.clients.insert_one(doc)
    doc["_id"] = res.inserted_id
    return _client_out(doc)

@clients_router.get("/{cid}")
async def get_client(cid: str, m=Depends(require_membership)):
    db = get_db()
    doc = await db.clients.find_one({"_id": _oid(cid), "company_id": m["company_id"]})
    if not doc:
        raise HTTPException(404, "Cliente não encontrado")
    return _client_out(doc)

@clients_router.patch("/{cid}")
async def update_client(cid: str, payload: ClientIn, m=Depends(require_roles("OWNER", "MANAGER", "PROFESSIONAL"))):
    db = get_db()
    updates = {k: v for k, v in payload.model_dump().items() if v is not None or k in ("phone", "email", "birth_date", "notes")}
    updates["updated_at"] = now_iso()
    doc = await db.clients.find_one_and_update(
        {"_id": _oid(cid), "company_id": m["company_id"]},
        {"$set": updates}, return_document=True,
    )
    if not doc:
        raise HTTPException(404, "Cliente não encontrado")
    return _client_out(doc)

@clients_router.delete("/{cid}")
async def delete_client(cid: str, m=Depends(require_roles("OWNER", "MANAGER"))):
    db = get_db()
    res = await db.clients.delete_one({"_id": _oid(cid), "company_id": m["company_id"]})
    if res.deleted_count == 0:
        raise HTTPException(404, "Cliente não encontrado")
    return {"success": True}

@clients_router.get("/{cid}/appointments")
async def client_history(cid: str, m=Depends(require_membership)):
    db = get_db()
    await get_client(cid, m)  # ownership check
    docs = await db.appointments.find({"company_id": m["company_id"], "client_id": cid}).sort("date", -1).to_list(500)
    return [_appt_out(d) for d in docs]


# ============ SERVIÇOS ============
services_router = APIRouter(prefix="/services", tags=["services"])

class ServiceIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    duration_min: int = Field(ge=5, le=600)
    price: float = Field(ge=0)
    is_active: bool = True
    professional_ids: list[str] = Field(default_factory=list)

def _service_out(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]), "name": doc["name"], "description": doc.get("description"),
        "duration_min": doc["duration_min"], "price": doc.get("price", 0.0),
        "is_active": doc.get("is_active", True),
        "professional_ids": doc.get("professional_ids", []),
        "created_at": doc["created_at"], "updated_at": doc.get("updated_at", doc["created_at"]),
    }

@services_router.get("")
async def list_services(m=Depends(require_membership), only_active: bool = False):
    db = get_db()
    q = {"company_id": m["company_id"]}
    if only_active:
        q["is_active"] = True
    docs = await db.services.find(q).sort("name", 1).to_list(1000)
    return [_service_out(d) for d in docs]

@services_router.post("", status_code=201)
async def create_service(payload: ServiceIn, m=Depends(require_roles("OWNER", "MANAGER"))):
    db = get_db()
    await enforce_limit(db, m["company_id"], "services", "serviços", "max_services")
    n = now_iso()
    doc = {**payload.model_dump(), "company_id": m["company_id"], "created_at": n, "updated_at": n}
    res = await db.services.insert_one(doc)
    doc["_id"] = res.inserted_id
    return _service_out(doc)

@services_router.patch("/{sid}")
async def update_service(sid: str, payload: ServiceIn, m=Depends(require_roles("OWNER", "MANAGER"))):
    db = get_db()
    updates = payload.model_dump()
    updates["updated_at"] = now_iso()
    doc = await db.services.find_one_and_update(
        {"_id": _oid(sid), "company_id": m["company_id"]},
        {"$set": updates}, return_document=True,
    )
    if not doc:
        raise HTTPException(404, "Serviço não encontrado")
    return _service_out(doc)

@services_router.delete("/{sid}")
async def delete_service(sid: str, m=Depends(require_roles("OWNER", "MANAGER"))):
    db = get_db()
    res = await db.services.delete_one({"_id": _oid(sid), "company_id": m["company_id"]})
    if res.deleted_count == 0:
        raise HTTPException(404, "Serviço não encontrado")
    return {"success": True}


# ============ DISPONIBILIDADE ============
avail_router = APIRouter(prefix="/availability", tags=["availability"])

class DayHours(BaseModel):
    active: bool = True
    open: str = "08:00"
    close: str = "18:00"
    break_start: str | None = None
    break_end: str | None = None

class BusinessHoursIn(BaseModel):
    hours: dict[str, DayHours]  # keys: MON..SUN

def _default_hours() -> dict:
    d = {}
    for w in WEEKDAYS:
        d[w] = {"active": w != "SUN", "open": "08:00", "close": "18:00" if w != "SAT" else "14:00", "break_start": None, "break_end": None}
    return d

@avail_router.get("/company")
async def get_company_hours(m=Depends(require_membership)):
    db = get_db()
    comp = await db.companies.find_one({"_id": _oid(m["company_id"])})
    return {"hours": comp.get("business_hours") or _default_hours()}

@avail_router.put("/company")
async def set_company_hours(payload: BusinessHoursIn, m=Depends(require_roles("OWNER", "MANAGER"))):
    db = get_db()
    hrs = {k: v.model_dump() for k, v in payload.hours.items() if k in WEEKDAYS}
    await db.companies.update_one(
        {"_id": _oid(m["company_id"])},
        {"$set": {"business_hours": hrs, "updated_at": now_iso()}},
    )
    return {"hours": hrs}

@avail_router.get("/professional/{user_id}")
async def get_pro_hours(user_id: str, m=Depends(require_membership)):
    db = get_db()
    memb = await db.memberships.find_one({"user_id": user_id, "company_id": m["company_id"]})
    if not memb:
        raise HTTPException(404, "Profissional não encontrado")
    return {"hours": memb.get("availability")}  # None → uses company defaults

@avail_router.put("/professional/{user_id}")
async def set_pro_hours(user_id: str, payload: BusinessHoursIn, m=Depends(require_roles("OWNER", "MANAGER"))):
    db = get_db()
    memb = await db.memberships.find_one({"user_id": user_id, "company_id": m["company_id"]})
    if not memb:
        raise HTTPException(404, "Profissional não encontrado")
    hrs = {k: v.model_dump() for k, v in payload.hours.items() if k in WEEKDAYS}
    await db.memberships.update_one({"_id": memb["_id"]}, {"$set": {"availability": hrs, "updated_at": now_iso()}})
    return {"hours": hrs}


# ============ AGENDAMENTOS ============
appts_router = APIRouter(prefix="/appointments", tags=["appointments"])

class AppointmentIn(BaseModel):
    client_id: str
    service_id: str
    professional_id: str  # membership user_id
    date: str  # YYYY-MM-DD
    start_time: str  # HH:MM
    notes: str | None = Field(default=None, max_length=1000)
    status: AppointmentStatus = "PENDING"

class AppointmentUpdate(BaseModel):
    client_id: str | None = None
    service_id: str | None = None
    professional_id: str | None = None
    date: str | None = None
    start_time: str | None = None
    notes: str | None = None
    status: AppointmentStatus | None = None

def _to_minutes(hhmm: str) -> int:
    h, mm = hhmm.split(":")
    return int(h) * 60 + int(mm)

def _from_minutes(total: int) -> str:
    return f"{total//60:02d}:{total%60:02d}"

def _weekday_of(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return WEEKDAYS[dt.weekday()]

def _appt_out(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "client_id": doc["client_id"], "client_name": doc.get("client_name", ""),
        "client_phone": doc.get("client_phone"),
        "service_id": doc["service_id"], "service_name": doc.get("service_name", ""),
        "professional_id": doc["professional_id"], "professional_name": doc.get("professional_name", ""),
        "date": doc["date"], "start_time": doc["start_time"], "end_time": doc["end_time"],
        "duration_min": doc["duration_min"], "price": doc.get("price", 0.0),
        "notes": doc.get("notes"), "status": doc["status"],
        "created_at": doc["created_at"], "updated_at": doc.get("updated_at", doc["created_at"]),
    }

async def _resolve_snapshot(company_id: str, client_id: str, service_id: str, pro_id: str) -> dict:
    db = get_db()
    client = await db.clients.find_one({"_id": _oid(client_id), "company_id": company_id})
    if not client:
        raise HTTPException(400, "Cliente inválido")
    service = await db.services.find_one({"_id": _oid(service_id), "company_id": company_id})
    if not service:
        raise HTTPException(400, "Serviço inválido")
    if not service.get("is_active", True):
        raise HTTPException(400, "Serviço inativo")
    memb = await db.memberships.find_one({"user_id": pro_id, "company_id": company_id, "status": "ACTIVE"})
    if not memb:
        raise HTTPException(400, "Profissional inválido")
    pro_user = await db.users.find_one({"_id": _oid(pro_id)})
    if not pro_user:
        raise HTTPException(400, "Profissional inválido")
    # If service has explicit professional_ids restrictions
    allowed = service.get("professional_ids") or []
    if allowed and pro_id not in allowed:
        raise HTTPException(400, "Profissional não executa este serviço")
    return {
        "client": client, "service": service, "membership": memb, "pro_user": pro_user,
    }

async def _validate_slot(company_id: str, pro_id: str, date: str, start_time: str,
                        duration_min: int, ignore_appt_id: str | None = None) -> None:
    db = get_db()
    start_m = _to_minutes(start_time)
    end_m = start_m + duration_min
    if end_m > 24 * 60:
        raise HTTPException(400, "Horário ultrapassa o dia")

    # Fetch weekday hours: prefer pro override, fallback to company
    weekday = _weekday_of(date)
    memb = await db.memberships.find_one({"user_id": pro_id, "company_id": company_id})
    company = await db.companies.find_one({"_id": _oid(company_id)})
    hours_source = (memb or {}).get("availability") or company.get("business_hours") or _default_hours()
    day = hours_source.get(weekday, {})
    if not day.get("active", False):
        raise HTTPException(400, "Dia não disponível para atendimento")
    day_open = _to_minutes(day.get("open", "08:00"))
    day_close = _to_minutes(day.get("close", "18:00"))
    if start_m < day_open or end_m > day_close:
        raise HTTPException(400, "Horário fora do funcionamento")
    br_s, br_e = day.get("break_start"), day.get("break_end")
    if br_s and br_e:
        b1, b2 = _to_minutes(br_s), _to_minutes(br_e)
        if not (end_m <= b1 or start_m >= b2):
            raise HTTPException(400, "Horário conflita com intervalo de almoço")

    # Conflict with existing appointments for same professional
    q = {
        "company_id": company_id,
        "professional_id": pro_id,
        "date": date,
        "status": {"$ne": "CANCELLED"},
    }
    if ignore_appt_id:
        q["_id"] = {"$ne": _oid(ignore_appt_id)}
    existing = await db.appointments.find(q).to_list(500)
    for a in existing:
        a_start = _to_minutes(a["start_time"])
        a_end = a_start + a["duration_min"]
        if not (end_m <= a_start or start_m >= a_end):
            raise HTTPException(409, f"Conflito com agendamento das {a['start_time']} às {a['end_time']}")

    # Fase 4: bloqueios criados pelo assistente
    blocks = await db.schedule_blocks.find({"company_id": company_id, "date": date}).to_list(200)
    for b in blocks:
        if b.get("professional_id") and b["professional_id"] != pro_id:
            continue
        b_start = _to_minutes(b["start_time"]); b_end = _to_minutes(b["end_time"])
        if not (end_m <= b_start or start_m >= b_end):
            raise HTTPException(409, f"Horário bloqueado das {b['start_time']} às {b['end_time']}")

@appts_router.get("")
async def list_appts(
    date_from: str = Query(...), date_to: str = Query(...),
    professional_id: str | None = None,
    user: dict = Depends(get_current_user),
    m=Depends(require_membership),
):
    db = get_db()
    q = {"company_id": m["company_id"], "date": {"$gte": date_from, "$lte": date_to}}
    # Professionals only see their own appointments
    if m["role"] == "PROFESSIONAL":
        q["professional_id"] = user["id"]
    elif professional_id:
        q["professional_id"] = professional_id
    docs = await db.appointments.find(q).sort([("date", 1), ("start_time", 1)]).to_list(2000)
    return [_appt_out(d) for d in docs]

@appts_router.get("/{aid}")
async def get_appt(aid: str, user: dict = Depends(get_current_user), m=Depends(require_membership)):
    db = get_db()
    doc = await db.appointments.find_one({"_id": _oid(aid), "company_id": m["company_id"]})
    if not doc:
        raise HTTPException(404, "Agendamento não encontrado")
    if m["role"] == "PROFESSIONAL" and doc["professional_id"] != user["id"]:
        raise HTTPException(403, "Acesso negado")
    return _appt_out(doc)

@appts_router.post("", status_code=201)
async def create_appt(payload: AppointmentIn, m=Depends(require_roles("OWNER", "MANAGER", "PROFESSIONAL"))):
    db = get_db()
    snap = await _resolve_snapshot(m["company_id"], payload.client_id, payload.service_id, payload.professional_id)
    duration = snap["service"]["duration_min"]
    await _validate_slot(m["company_id"], payload.professional_id, payload.date, payload.start_time, duration)
    end_time = _from_minutes(_to_minutes(payload.start_time) + duration)
    n = now_iso()
    doc = {
        "company_id": m["company_id"],
        "client_id": payload.client_id, "client_name": snap["client"]["name"],
        "client_phone": snap["client"].get("phone"),
        "service_id": payload.service_id, "service_name": snap["service"]["name"],
        "professional_id": payload.professional_id, "professional_name": snap["pro_user"]["name"],
        "date": payload.date, "start_time": payload.start_time, "end_time": end_time,
        "duration_min": duration, "price": snap["service"].get("price", 0.0),
        "notes": payload.notes, "status": payload.status,
        "created_at": n, "updated_at": n,
    }
    res = await db.appointments.insert_one(doc)
    doc["_id"] = res.inserted_id
    return _appt_out(doc)

@appts_router.patch("/{aid}")
async def update_appt(aid: str, payload: AppointmentUpdate,
                      user: dict = Depends(get_current_user),
                      m=Depends(require_membership)):
    db = get_db()
    existing = await db.appointments.find_one({"_id": _oid(aid), "company_id": m["company_id"]})
    if not existing:
        raise HTTPException(404, "Agendamento não encontrado")

    # PROFESSIONAL can only change status of own appointments
    if m["role"] == "PROFESSIONAL":
        if existing["professional_id"] != user["id"]:
            raise HTTPException(403, "Acesso negado")
        data = payload.model_dump(exclude_unset=True)
        if set(data.keys()) - {"status"}:
            raise HTTPException(403, "Profissional só pode alterar status")

    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(400, "Nada para atualizar")

    # If rescheduling / changing key fields → re-validate
    keys = {"client_id", "service_id", "professional_id", "date", "start_time"}
    if keys & data.keys():
        client_id = data.get("client_id", existing["client_id"])
        service_id = data.get("service_id", existing["service_id"])
        pro_id = data.get("professional_id", existing["professional_id"])
        date = data.get("date", existing["date"])
        start_time = data.get("start_time", existing["start_time"])
        snap = await _resolve_snapshot(m["company_id"], client_id, service_id, pro_id)
        duration = snap["service"]["duration_min"]
        # Only validate slot if status will not be CANCELLED
        target_status = data.get("status", existing["status"])
        if target_status != "CANCELLED":
            await _validate_slot(m["company_id"], pro_id, date, start_time, duration, ignore_appt_id=aid)
        end_time = _from_minutes(_to_minutes(start_time) + duration)
        data.update({
            "client_name": snap["client"]["name"], "client_phone": snap["client"].get("phone"),
            "service_name": snap["service"]["name"], "professional_name": snap["pro_user"]["name"],
            "duration_min": duration, "price": snap["service"].get("price", 0.0),
            "end_time": end_time,
        })

    previous_status = existing["status"]
    data["updated_at"] = now_iso()
    doc = await db.appointments.find_one_and_update(
        {"_id": _oid(aid)}, {"$set": data}, return_document=True,
    )
    if previous_status != doc.get("status") and doc.get("status") in {"CONFIRMED", "CANCELLED"}:
        try:
            company = await db.companies.find_one({"_id": _oid(m["company_id"])})
            await send_booking_status(company or {}, doc, confirmed=doc["status"] == "CONFIRMED")
        except (WhatsAppUnavailable, Exception):
            pass
    return _appt_out(doc)

@appts_router.delete("/{aid}")
async def delete_appt(aid: str, m=Depends(require_roles("OWNER", "MANAGER"))):
    db = get_db()
    res = await db.appointments.delete_one({"_id": _oid(aid), "company_id": m["company_id"]})
    if res.deleted_count == 0:
        raise HTTPException(404, "Agendamento não encontrado")
    return {"success": True}


# ============ DASHBOARD METRICS ============
dashboard_router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@dashboard_router.get("/summary")
async def summary(date: str | None = None, user: dict = Depends(get_current_user), m=Depends(require_membership)):
    db = get_db()
    if not date:
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    q = {"company_id": m["company_id"], "date": date}
    if m["role"] == "PROFESSIONAL":
        q["professional_id"] = user["id"]
    docs = await db.appointments.find(q).sort("start_time", 1).to_list(500)
    counters = {"PENDING": 0, "CONFIRMED": 0, "COMPLETED": 0, "CANCELLED": 0}
    revenue = 0.0
    for d in docs:
        counters[d["status"]] = counters.get(d["status"], 0) + 1
        if d["status"] != "CANCELLED":
            revenue += float(d.get("price", 0) or 0)
    upcoming = [_appt_out(d) for d in docs if d["status"] in ("PENDING", "CONFIRMED")][:8]
    return {
        "date": date,
        "total": len(docs),
        "counters": counters,
        "revenue": round(revenue, 2),
        "upcoming": upcoming,
    }
