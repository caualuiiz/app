from __future__ import annotations

from typing import Any


PLAN_LIMITS: dict[str, dict[str, Any]] = {
    "TRIAL": {
        "max_services": 20,
        "max_professionals": 5,
        "max_gallery_images": 8,
        "max_ai_blueprints_per_month": 5,
    },
    "STARTER": {
        "max_services": 50,
        "max_professionals": 10,
        "max_gallery_images": 30,
        "max_ai_blueprints_per_month": 30,
    },
    "PRO": {
        "max_services": 200,
        "max_professionals": 50,
        "max_gallery_images": 100,
        "max_ai_blueprints_per_month": 200,
    },
}


def normalize_plan(value: str | None) -> str:
    plan = (value or "TRIAL").upper().strip()
    return plan if plan in PLAN_LIMITS else "TRIAL"


def limits_for(plan: str | None) -> dict[str, Any]:
    return PLAN_LIMITS[normalize_plan(plan)]


def limit_for(plan: str | None, key: str) -> int | None:
    value = limits_for(plan).get(key)
    return value if isinstance(value, int) else None


async def current_subscription(db, company_id: str) -> dict[str, Any]:
    doc = await db.subscriptions.find_one(
        {"company_id": company_id},
        sort=[("updated_at", -1)],
    )
    if doc:
        return doc
    return {
        "company_id": company_id,
        "plan": "TRIAL",
        "status": "trialing",
    }
