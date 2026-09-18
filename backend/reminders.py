from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

from bson import ObjectId

from db import get_db
from whatsapp import send_template, WhatsAppUnavailable


def _parse_iso_date_time(date_value: str, time_value: str) -> datetime:
    dt = datetime.fromisoformat(f"{date_value}T{time_value}:00")
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt


def _template_key(kind: str) -> str:
    return {
        "24h": "WHATSAPP_TEMPLATE_REMINDER_24H",
        "2h": "WHATSAPP_TEMPLATE_REMINDER_2H",
    }[kind]


async def run_reminders() -> int:
    db = get_db()
    now = datetime.now(timezone.utc)
    windows = {
        "24h": (now + timedelta(hours=23, minutes=30), now + timedelta(hours=24, minutes=30)),
        "2h": (now + timedelta(hours=1, minutes=30), now + timedelta(hours=2, minutes=30)),
    }

    sent = 0
    for kind, (start, end) in windows.items():
        template_name = os.environ.get(_template_key(kind), "").strip()
        if not template_name:
            continue

        cursor = db.appointments.find({
            "status": "CONFIRMED",
            "reminder_status": {"$nin": [kind]},
        })
        async for appointment in cursor:
            try:
                appointment_at = _parse_iso_date_time(
                    appointment["date"],
                    appointment["start_time"],
                )
            except Exception:
                continue

            if not (start <= appointment_at < end):
                continue

            company = await db.companies.find_one(
                {"_id": ObjectId(appointment["company_id"])}
            )
            phone = appointment.get("client_phone")
            if not company or not phone:
                continue

            try:
                send_template(
                    company,
                    to=phone,
                    template_name=template_name,
                    language=os.environ.get("WHATSAPP_TEMPLATE_LANGUAGE", "pt_BR"),
                    variables=[
                        appointment["client_name"],
                        appointment["service_name"],
                        appointment["date"],
                        appointment["start_time"],
                    ],
                )
            except WhatsAppUnavailable:
                continue
            except Exception:
                continue

            updated = await db.appointments.update_one(
                {
                    "_id": appointment["_id"],
                    "status": "CONFIRMED",
                    "reminder_status": {"$nin": [kind]},
                },
                {"$addToSet": {"reminder_status": kind}},
            )
            if updated.modified_count:
                sent += 1

    return sent
