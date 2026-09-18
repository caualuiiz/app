from __future__ import annotations

from fastapi import HTTPException

from billing import current_subscription, limit_for


async def enforce_limit(db, company_id: str, collection: str, field: str, plan_key: str) -> None:
    subscription = await current_subscription(db, company_id)
    limit = limit_for(subscription.get("plan"), plan_key)
    if limit is None:
        return
    count = await db[collection].count_documents({"company_id": company_id})
    if count >= limit:
        raise HTTPException(
            402,
            f"Limite do plano atingido para {field}. Faça upgrade para continuar.",
        )


async def enforce_monthly_ai_limit(db, company_id: str) -> None:
    from datetime import datetime, timezone

    subscription = await current_subscription(db, company_id)
    limit = limit_for(subscription.get("plan"), "max_ai_blueprints_per_month")
    if limit is None:
        return

    now = datetime.now(timezone.utc)
    prefix = now.strftime("%Y-%m")
    count = await db.landing_blueprints.count_documents(
        {"company_id": company_id, "created_at": {"$regex": f"^{prefix}"}}
    )
    if count >= limit:
        raise HTTPException(
            402,
            "Limite mensal de gerações de IA atingido. Faça upgrade para continuar.",
        )
