from __future__ import annotations

import os
from typing import Any

import requests

from field_crypto import decrypt


class WhatsAppUnavailable(RuntimeError):
    pass


def _config(doc: dict[str, Any]) -> tuple[str, str, str]:
    phone_number_id = doc.get("whatsapp_phone_number_id")
    encrypted_token = doc.get("whatsapp_access_token")
    version = os.environ.get("WHATSAPP_API_VERSION", "").strip()
    if not phone_number_id or not encrypted_token or not version:
        raise WhatsAppUnavailable("WhatsApp não configurado")
    return version, phone_number_id, decrypt(encrypted_token)


def send_template(
    company: dict[str, Any],
    *,
    to: str,
    template_name: str,
    language: str,
    variables: list[str],
) -> dict[str, Any]:
    version, phone_number_id, token = _config(company)
    url = f"https://graph.facebook.com/{version}/{phone_number_id}/messages"
    payload: dict[str, Any] = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language},
        },
    }
    if variables:
        payload["template"]["components"] = [{
            "type": "body",
            "parameters": [{"type": "text", "text": value} for value in variables],
        }]

    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=20,
    )
    if not response.ok:
        raise WhatsAppUnavailable("WhatsApp recusou o envio")
    return response.json()


def send_new_booking(company: dict[str, Any], appointment: dict[str, Any]) -> list[dict[str, Any]]:
    recipients = company.get("whatsapp_notification_numbers") or []
    template_name = os.environ.get("WHATSAPP_TEMPLATE_NEW_BOOKING", "").strip()
    language = os.environ.get("WHATSAPP_TEMPLATE_LANGUAGE", "pt_BR").strip()
    if not recipients or not template_name:
        return []

    variables = [
        appointment["client_name"],
        appointment["service_name"],
        appointment["date"],
        appointment["start_time"],
    ]
    return [
        send_template(
            company,
            to=number,
            template_name=template_name,
            language=language,
            variables=variables,
        )
        for number in recipients
    ]


def send_booking_status(company: dict[str, Any], appointment: dict[str, Any], confirmed: bool) -> dict[str, Any] | None:
    template_key = (
        "WHATSAPP_TEMPLATE_BOOKING_CONFIRMED"
        if confirmed
        else "WHATSAPP_TEMPLATE_BOOKING_REJECTED"
    )
    template_name = os.environ.get(template_key, "").strip()
    language = os.environ.get("WHATSAPP_TEMPLATE_LANGUAGE", "pt_BR").strip()
    phone = appointment.get("client_phone")
    if not template_name or not phone:
        return None

    variables = [
        appointment["client_name"],
        appointment["service_name"],
        appointment["date"],
        appointment["start_time"],
    ]
    return send_template(
        company,
        to=phone,
        template_name=template_name,
        language=language,
        variables=variables,
    )
