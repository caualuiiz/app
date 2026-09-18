from __future__ import annotations

import hashlib
import hmac
import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, ConfigDict, Field

from auth import require_roles
from db import get_db
from field_crypto import encrypt


router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])


class WhatsAppConfigIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    phone_number_id: str = Field(min_length=5, max_length=100)
    access_token: str = Field(min_length=20, max_length=500)
    notification_numbers: list[str] = Field(default_factory=list, max_length=10)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.get("/config")
async def get_config(m=Depends(require_roles("OWNER", "MANAGER"))):
    db = get_db()
    company = await db.companies.find_one({"_id": __import__("bson").ObjectId(m["company_id"])})
    if not company:
        raise HTTPException(404, "Empresa não encontrada")
    return {
        "configured": bool(
            company.get("whatsapp_phone_number_id")
            and company.get("whatsapp_access_token")
        ),
        "phone_number_id": company.get("whatsapp_phone_number_id"),
        "notification_numbers": company.get("whatsapp_notification_numbers", []),
    }


@router.put("/config")
async def set_config(payload: WhatsAppConfigIn, m=Depends(require_roles("OWNER"))):
    db = get_db()
    await db.companies.update_one(
        {"_id": __import__("bson").ObjectId(m["company_id"])},
        {"$set": {
            "whatsapp_phone_number_id": payload.phone_number_id,
            "whatsapp_access_token": encrypt(payload.access_token),
            "whatsapp_notification_numbers": payload.notification_numbers,
            "updated_at": _now(),
        }},
    )
    return {"success": True, "configured": True}


@router.delete("/config")
async def clear_config(m=Depends(require_roles("OWNER"))):
    db = get_db()
    await db.companies.update_one(
        {"_id": __import__("bson").ObjectId(m["company_id"])},
        {"$unset": {
            "whatsapp_phone_number_id": "",
            "whatsapp_access_token": "",
            "whatsapp_notification_numbers": "",
        }, "$set": {"updated_at": _now()}},
    )
    return {"success": True}


@router.get("/webhook")
async def verify_webhook(
    hub_mode: str | None = Query(default=None, alias="hub.mode"),
    hub_verify_token: str | None = Query(default=None, alias="hub.verify_token"),
    hub_challenge: str | None = Query(default=None, alias="hub.challenge"),
):
    expected = __import__("os").environ.get("WHATSAPP_VERIFY_TOKEN", "")
    if hub_mode == "subscribe" and hub_verify_token and hub_verify_token == expected:
        return int(hub_challenge or "0")
    raise HTTPException(403, "Webhook não autorizado")


@router.post("/webhook")
async def receive_webhook(request: Request):
    secret = os.environ.get("WHATSAPP_APP_SECRET", "").strip()
    if not secret:
        raise HTTPException(503, "Webhook WhatsApp não configurado")
    raw = await request.body()
    signature = request.headers.get("x-hub-signature-256", "")
    if not signature.startswith("sha256="):
        raise HTTPException(403, "Assinatura WhatsApp ausente")
    expected = hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature[7:]):
        raise HTTPException(403, "Assinatura WhatsApp inválida")
    return {"received": True}
