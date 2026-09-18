import json
import os
from typing import Any

from .provider import AIProvider


class ClaudeProvider(AIProvider):
    name = "claude"
    DEFAULT_MODEL = "claude-3-5-sonnet-20241022"

    def __init__(self, *, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.model = model or os.environ.get("ANTHROPIC_MODEL") or self.DEFAULT_MODEL

    async def generate_structured_decision(self, *, system_prompt: str, context: dict[str, Any], schema_description: str) -> dict[str, Any]:
        if not self.api_key:
            raise RuntimeError("ANTHROPIC_API_KEY não configurada")
        try:
            from anthropic import AsyncAnthropic
        except ImportError as exc:
            raise RuntimeError("Dependência anthropic não instalada") from exc
        client = AsyncAnthropic(api_key=self.api_key)
        prompt = "Retorne SOMENTE JSON válido, sem markdown. Siga o contrato. Não invente fatos.\\n\\nCONTRATO:\\n" + schema_description + "\\n\\nCONTEXTO:\\n" + json.dumps(context, ensure_ascii=False, default=str)
        try:
            response = await client.messages.create(model=self.model, max_tokens=4096, temperature=0, system=system_prompt, messages=[{"role": "user", "content": prompt}])
        except Exception as exc:
            raise RuntimeError("Falha na chamada da API Anthropic") from exc
        raw = "".join(getattr(block, "text", "") or "" for block in getattr(response, "content", [])).strip()
        if not raw:
            raise RuntimeError("Claude retornou resposta vazia")
        if raw.startswith("```"):
            raw = raw.split("```", 2)[1].strip()
            if raw.lower().startswith("json"):
                raw = raw[4:].strip()
        try:
            result = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Claude retornou JSON inválido") from exc
        if not isinstance(result, dict):
            raise RuntimeError("Claude retornou uma decisão que não é objeto JSON")
        return result