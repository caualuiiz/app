"""Real MongoDB validation for Priority 6.

Run explicitly with a disposable database:
  MONGO_URL='mongodb+srv://...' MONGO_TEST_DB='saas_priority6_<run>' \
    python -m pytest -q tests/test_real_mongodb_two_tenants.py -o addopts='-n 0'

The test never uses the normal DB_NAME and drops only its generated test DB.
"""
from __future__ import annotations

import asyncio
import os
from uuid import uuid4

import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError

pytestmark = pytest.mark.integration


@pytest.mark.skipif(
    not os.environ.get("MONGO_URL") or not os.environ.get("MONGO_TEST_DB"),
    reason="MONGO_URL and disposable MONGO_TEST_DB are required",
)
def test_real_mongodb_two_tenants_and_concurrent_slot_claim():
    asyncio.run(_exercise_real_mongodb())


async def _exercise_real_mongodb() -> None:
    client = AsyncIOMotorClient(os.environ["MONGO_URL"], serverSelectionTimeoutMS=5000)
    db = client[os.environ["MONGO_TEST_DB"]]
    company_a = f"company-a-{uuid4().hex}"
    company_b = f"company-b-{uuid4().hex}"
    try:
        await client.admin.command("ping")
        await db.appointments.create_index(
            [("company_id", 1), ("professional_id", 1), ("date", 1), ("start_time", 1)],
            unique=True,
            name="priority6_active_slot_unique",
            partialFilterExpression={"status": {"$in": ["PENDING", "CONFIRMED", "COMPLETED"]}},
        )

        # Tenant isolation: identical business data is allowed across tenants,
        # but each tenant's query must return only its own records.
        await db.appointments.insert_many([
            {
                "company_id": company_a,
                "professional_id": "professional-1",
                "date": "2030-01-02",
                "start_time": "10:00",
                "status": "PENDING",
            },
            {
                "company_id": company_b,
                "professional_id": "professional-1",
                "date": "2030-01-02",
                "start_time": "10:00",
                "status": "PENDING",
            },
        ])
        visible_a = await db.appointments.count_documents({"company_id": company_a})
        visible_b = await db.appointments.count_documents({"company_id": company_b})
        assert visible_a == 1
        assert visible_b == 1
        assert await db.appointments.count_documents({"company_id": company_a, "professional_id": "professional-1"}) == 1

        # Concurrency: two simultaneous writes to the same tenant/professional/
        # date/time must produce exactly one winner at the database boundary.
        async def claim_same_slot(request_id: str):
            try:
                await db.appointments.insert_one({
                    "request_id": request_id,
                    "company_id": company_a,
                    "professional_id": "professional-2",
                    "date": "2030-01-03",
                    "start_time": "11:00",
                    "status": "PENDING",
                })
                return "won"
            except DuplicateKeyError:
                return "conflict"

        results = await asyncio.gather(
            claim_same_slot("request-1"),
            claim_same_slot("request-2"),
        )
        assert sorted(results) == ["conflict", "won"]
        assert await db.appointments.count_documents({
            "company_id": company_a,
            "professional_id": "professional-2",
            "date": "2030-01-03",
            "start_time": "11:00",
        }) == 1
    finally:
        await client.drop_database(os.environ["MONGO_TEST_DB"])
        client.close()
