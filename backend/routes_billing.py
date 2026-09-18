from __future__ import annotations

import hashlib
import hmac
import os
import time
from datetime import datetime, timezone

import requests
from fastapi import APIRouter, Depends, HTTPException, Request

from auth import require_roles
from billing import current_subscription, normalize_plan
from db import get_db


router = APIRouter(prefix="/billing", tags=["billing"])


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stripe_headers() -> dict[str, str]:
    key = os.environ.get("STRIPE_SECRET_KEY", "").strip()
    if not key:
        raise HTTPException(503, "Cobrança ainda não configurada")
    return {"Authorization": f"Bearer {key}"}


@router.get("")
async def get_billing(m=Depends(require_roles("OWNER", "MANAGER"))):
    db = get_db()
    subscription = await current_subscription(db, m["company_id"])
    return {
        "plan": normalize_plan(subscription.get("plan")),
        "status": subscription.get("status", "trialing"),
        "current_period_end": subscription.get("current_period_end"),
        "cancel_at_period_end": bool(subscription.get("cancel_at_period_end", False)),
    }


@router.post("/checkout")
async def create_checkout_session(request: Request, m=Depends(require_roles("OWNER"))):
    body = await request.json()
    plan = normalize_plan(body.get("plan"))
    if plan not in {"STARTER", "PRO"}:
        raise HTTPException(400, "Plano de checkout inválido")

    price_id = os.environ.get(f"STRIPE_PRICE_{plan}", "").strip()
    if not price_id:
        raise HTTPException(503, "Price ID do plano ainda não configurado")

    frontend_url = os.environ.get("FRONTEND_URL", "").rstrip("/")
    if not frontend_url:
        raise HTTPException(503, "FRONTEND_URL não configurado")

    response = requests.post(
        "https://api.stripe.com/v1/checkout/sessions",
        headers=_stripe_headers(),
        data={
            "mode": "subscription",
            "line_items[0][price]": price_id,
            "line_items[0][quantity]": "1",
            "success_url": f"{frontend_url}/settings/billing?success=1",
            "cancel_url": f"{frontend_url}/settings/billing?cancelled=1",
            "metadata[company_id]": m["company_id"],
            "metadata[plan]": plan,
        },
        timeout=20,
    )
    if not response.ok:
        raise HTTPException(502, "Não foi possível criar a sessão de cobrança")
    data = response.json()
    return {"url": data.get("url"), "session_id": data.get("id")}


@router.post("/portal")
async def create_billing_portal(m=Depends(require_roles("OWNER"))):
    db = get_db()
    subscription = await current_subscription(db, m["company_id"])
    customer_id = subscription.get("stripe_customer_id")
    if not customer_id:
        raise HTTPException(400, "Empresa ainda não possui cliente Stripe")

    frontend_url = os.environ.get("FRONTEND_URL", "").rstrip("/")
    response = requests.post(
        "https://api.stripe.com/v1/billing_portal/sessions",
        headers=_stripe_headers(),
        data={
            "customer": customer_id,
            "return_url": f"{frontend_url}/settings/billing",
        },
        timeout=20,
    )
    if not response.ok:
        raise HTTPException(502, "Não foi possível abrir o portal de cobrança")
    return {"url": response.json().get("url")}


def _valid_signature(raw_body: bytes, signature: str, secret: str) -> bool:
    values = {}
    for part in signature.split(","):
        if "=" in part:
            key, value = part.split("=", 1)
            values.setdefault(key, []).append(value)
    timestamp = values.get("t", [None])[0]
    signatures = values.get("v1", [])
    if not timestamp or not signatures:
        return False
    try:
        if abs(time.time() - int(timestamp)) > 300:
            return False
    except ValueError:
        return False

    signed = f"{timestamp}.".encode() + raw_body
    expected = hmac.new(
        secret.encode(),
        signed,
        hashlib.sha256,
    ).hexdigest()
    return any(hmac.compare_digest(expected, value) for value in signatures)


@router.post("/webhook")
async def stripe_webhook(request: Request):
    secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "").strip()
    if not secret:
        raise HTTPException(503, "Webhook Stripe não configurado")

    raw = await request.body()
    signature = request.headers.get("stripe-signature", "")
    if not _valid_signature(raw, signature, secret):
        raise HTTPException(400, "Assinatura Stripe inválida")

    event = await request.json()
    event_id = event.get("id")
    event_type = event.get("type")
    data = event.get("data", {}).get("object", {}) or {}

    db = get_db()
    if event_id and await db.billing_events.find_one({"event_id": event_id}):
        return {"received": True, "duplicate": True}

    company_id = (
        data.get("metadata", {}).get("company_id")
        or data.get("subscription_details", {}).get("metadata", {}).get("company_id")
    )

    if company_id:
        if event_type in {"checkout.session.completed", "customer.subscription.created", "customer.subscription.updated"}:
            metadata = data.get("metadata", {}) or {}
            plan = normalize_plan(metadata.get("plan"))
            await db.subscriptions.update_one(
                {"company_id": company_id},
                {
                    "$set": {
                        "company_id": company_id,
                        "plan": plan,
                        "status": data.get("status", "active"),
                        "stripe_customer_id": data.get("customer"),
                        "stripe_subscription_id": data.get("id") if event_type.startswith("customer.subscription") else data.get("subscription"),
                        "current_period_end": data.get("current_period_end"),
                        "cancel_at_period_end": bool(data.get("cancel_at_period_end", False)),
                        "updated_at": _now(),
                    }
                },
                upsert=True,
            )
        elif event_type in {"customer.subscription.deleted"}:
            await db.subscriptions.update_one(
                {"company_id": company_id},
                {"$set": {"status": "canceled", "plan": "TRIAL", "updated_at": _now()}},
                upsert=True,
            )

    if event_id:
        await db.billing_events.insert_one(
            {"event_id": event_id, "type": event_type, "created_at": _now()}
        )

    return {"received": True}
