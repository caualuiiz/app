import os
from typing import Any

from .config import get_ai_config
from .decision import StructuredDecision
from .provider import AIProvider


class ClaudeProvider(AIProvider):
    name = "claude"

    def __init__(self, *, api_key: str | None = None, model: str | None = None):
        if api_key is None and model is None:
            config = get_ai_config()
            self.api_key = config.anthropic_api_key
            self.model = config.anthropic_model
            return

        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "").strip()
        self.model = model or os.environ.get("ANTHROPIC_MODEL", "").strip()
        if not self.api_key:
            raise RuntimeError("ANTHROPIC_API_KEY não configurada")
        if not self.model:
            raise RuntimeError("ANTHROPIC_MODEL não configurado")

    async def generate_structured_decision(
        self,
        *,
        system_prompt: str,
        context: dict[str, Any],
        schema_description: str,
    ) -> dict[str, Any]:
        try:
            from anthropic import AsyncAnthropic
        except ImportError as exc:
            raise RuntimeError("Dependência anthropic não instalada") from exc

        client = AsyncAnthropic(api_key=self.api_key)
        prompt = (
            system_prompt
            + "\n\nContrato de decisão: "
            + schema_description
            + "\n\nContexto confiável:\n"
            + __import__("json").dumps(context, ensure_ascii=False, default=str)
        )
        try:
            response = await client.messages.parse(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}],
                output_format=StructuredDecision,
            )
        except Exception as exc:
            raise RuntimeError("Falha na chamada da API Anthropic") from exc

        parsed = getattr(response, "parsed_output", None)
        if parsed is None:
            raise RuntimeError("Claude não retornou saída estruturada")
        if isinstance(parsed, StructuredDecision):
            return parsed.model_dump()
        if isinstance(parsed, dict):
            return parsed
        raise RuntimeError("Claude retornou saída estruturada em formato inesperado")