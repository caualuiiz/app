from __future__ import annotations

import json
import os
import uuid
from typing import Any

from .decision import StructuredDecision
from .professional_brain import build_system_prompt


class LandingBrain:
    name = "landing-brain"
    version = "1.0"

    def __init__(self, *, model: str | None = None):
        self.model = model or os.environ.get("LANDING_BRAIN_MODEL", "gpt-4o-mini")

    async def decide(self, *, context: dict[str, Any]) -> StructuredDecision:
        key = os.environ.get("EMERGENT_LLM_KEY", "").strip()
        if not key:
            raise RuntimeError("EMERGENT_LLM_KEY não configurada")
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
        except ImportError as exc:
            raise RuntimeError("Engine de execução de IA indisponível") from exc
        prompt = (
            "Analise o projeto como um profissional sênior e produza decisões concretas. "
            "Use somente as evidências fornecidas. "
            "Para cada ação, o target deve apontar para uma decisão de design executável. "
            "Antes de finalizar, faça uma autocrítica interna e registre riscos em warnings. "
            "Retorne SOMENTE JSON válido com os campos summary, actions, confidence, warnings e missing_data.\\n\\n"
            "CONTRATO:\\n" + StructuredDecision.schema_description()
            + "\\n\\nCONTEXTO DO PROJETO:\\n"
            + json.dumps(context, ensure_ascii=False, default=str)
        )
        try:
            chat = LlmChat(
                api_key=key,
                session_id=f"landing-brain-{uuid.uuid4()}",
                system_message=build_system_prompt(),
            ).with_model("openai", self.model)
            raw = await chat.send_message(UserMessage(text=prompt))
        except Exception as exc:
            raise RuntimeError("Engine de execução falhou ao gerar a decisão") from exc
        text = str(raw).strip()
        if text.startswith("```"):
            text = text.split("```", 2)[1].lstrip("json").strip()
        try:
            return StructuredDecision.model_validate(json.loads(text))
        except Exception as exc:
            raise RuntimeError("Landing Brain retornou decisão fora do contrato") from exc