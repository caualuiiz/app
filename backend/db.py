"""MongoDB connection singleton + index bootstrap."""
from __future__ import annotations

import os

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


def get_db() -> AsyncIOMotorDatabase:
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(os.environ["MONGO_URL"])
        _db = _client[os.environ["DB_NAME"]]
    return _db


async def create_indexes() -> None:
    db = get_db()
    await db.users.create_index("email", unique=True)
    await db.companies.create_index("slug", unique=True)
    await db.memberships.create_index(
        [("user_id", 1), ("company_id", 1)], unique=True
    )
    await db.memberships.create_index("company_id")
    await db.memberships.create_index("user_id")
    await db.password_reset_tokens.create_index("expires_at", expireAfterSeconds=0)
    await db.login_attempts.create_index("identifier")
    await db.clients.create_index([("company_id", 1), ("name", 1)])
    await db.services.create_index([("company_id", 1), ("name", 1)])
    await db.appointments.create_index([("company_id", 1), ("date", 1), ("start_time", 1)])
    await db.appointments.create_index([("company_id", 1), ("professional_id", 1), ("date", 1)])
    await db.appointments.create_index([("company_id", 1), ("client_id", 1)])
    await db.schedule_blocks.create_index([("company_id", 1), ("date", 1)])
    await db.assistant_sessions.create_index([("company_id", 1), ("user_id", 1)], unique=True)
    await db.assistant_audit.create_index([("company_id", 1), ("at", -1)])
    await db.visual_profiles.create_index([("company_id", 1), ("created_at", -1)])
    await db.reference_profiles.create_index([("company_id", 1), ("created_at", -1)])
    await db.art_directions.create_index([("company_id", 1), ("created_at", -1)])
    await db.design_systems.create_index([("company_id", 1), ("created_at", -1)])
    await db.layout_plans.create_index([("company_id", 1), ("created_at", -1)])
    await db.render_specifications.create_index([("company_id", 1), ("created_at", -1)])
    await db.preview_sessions.create_index("preview_id", unique=True)
    await db.preview_sessions.create_index([("company_id", 1), ("created_at", -1)])
    await db.preview_sessions.create_index("expires_at")
    await db.landing_decisions.create_index([("company_id", 1), ("request_id", 1)], unique=True)
    await db.landing_blueprints.create_index([("company_id", 1), ("created_at", -1)])
    await db.custom_domains.create_index("domain", unique=True)
    await db.custom_domains.create_index([("company_id", 1), ("status", 1)])
    await db.subscriptions.create_index([("company_id", 1), ("updated_at", -1)])
    await db.billing_events.create_index("event_id", unique=True)
    await db.draft_versions.create_index([("company_id", 1), ("version", 1)], unique=True)


def close_db() -> None:
    global _client, _db
    if _client is not None:
        _client.close()
    _client = None
    _db = None
