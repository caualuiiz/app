from __future__ import annotations

import asyncio
import json
import os
from typing import Any

import requests

OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"


class OpenAIExecutionError(RuntimeError):
    pass


def _model() -> str:
    return os.environ.get("LANDING_BRAIN_MODEL", "gpt-5.6-luna").strip()


def _key() -> str:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise OpenAIExecutionError("OPENAI_API_KEY não configurada")
    return key


def _content_text(data: dict[str, Any]) -> str:
    text = data.get("output_text")
    if isinstance(text, str) and text.strip():
        return text.strip()
    parts: list[str] = []
    for item in data.get("output", []) or []:
        for block in item.get("content", []) or []:
            if block.get("type") == "output_text" and isinstance(block.get("text"), str):
                parts.append(block["text"])
    result = "".join(parts).strip()
    if not result:
        raise OpenAIExecutionError("OpenAI retornou resposta vazia")
    return result


async def _call(payload: dict[str, Any], timeout: int = 120) -> dict[str, Any]:
    def send() -> requests.Response:
        return requests.post(
            OPENAI_RESPONSES_URL,
            headers={"Authorization": f"Bearer {_key()}", "Content-Type": "application/json"},
            json=payload,
            timeout=timeout,
        )
    response = await asyncio.to_thread(send)
    if not response.ok:
        raise OpenAIExecutionError(f"OpenAI HTTP {response.status_code}: {response.text[:1000]}")
    try:
        return response.json()
    except ValueError as exc:
        raise OpenAIExecutionError("OpenAI retornou JSON inválido") from exc


async def generate_json(*, system_prompt: str, user_prompt: str, images: list[dict[str, str]] | None = None, model: str | None = None) -> dict[str, Any]:
    user_content: list[dict[str, Any]] = [{"type": "input_text", "text": user_prompt}]
    for image in (images or [])[:8]:
        mime = image.get("content_type") or "image/jpeg"
        b64 = image.get("data")
        if b64:
            user_content.append({"type": "input_image", "image_url": f"data:{mime};base64,{b64}", "detail": "high"})
    payload = {
        "model": model or _model(),
        "instructions": system_prompt,
        "input": [{"role": "user", "content": user_content}],
        "max_output_tokens": 12000,
    }
    data = await _call(payload)
    text = _content_text(data)
    if text.startswith("```"):
        text = text.split("```", 2)[1].lstrip("json").strip()
    try:
        result = json.loads(text)
    except json.JSONDecodeError as exc:
        raise OpenAIExecutionError("OpenAI retornou JSON fora do contrato") from exc
    if not isinstance(result, dict):
        raise OpenAIExecutionError("OpenAI retornou um objeto JSON inválido")
    return result