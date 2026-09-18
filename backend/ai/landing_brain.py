from __future__ import annotations

import json
import os
import uuid
from typing import Any

from .decision import StructuredDecision
from .landing_blueprint import LandingBlueprint
from .professional_brain import build_system_prompt
from .reasoning_engine import ReasoningEngine


class LandingBrain(ReasoningEngine):
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
    async def build_blueprint(self, *, context: dict[str, Any]) -> LandingBlueprint:
        key = os.environ.get("EMERGENT_LLM_KEY", "").strip()
        if not key:
            raise RuntimeError("EMERGENT_LLM_KEY não configurada")
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
        except ImportError as exc:
            raise RuntimeError("Engine de execução de IA indisponível") from exc
        prompt = (
            "Crie um blueprint completo de landing page como um profissional com mais de 20 anos. "
            "Não aprenda com os dados e não invente fatos. "
            "Defina um Design System completo, um Layout Plan coerente e o posicionamento de cada imagem. "
            "Cada image_path do contexto visual deve aparecer no máximo uma vez em media_placements e deve "
            "receber role, target_sections, priority, treatment, crop e focal_point. "
            "Os ids das seções devem ser curtos e descritivos, preferindo hero, about, services, professionals, "
            "gallery, differentiators, hours e contact quando aplicável. "
            "A estrutura deve refletir o negócio real e não um template fixo. "
            "Retorne SOMENTE JSON válido compatível com o contrato LandingBlueprint.\n\n"
            + json.dumps(context, ensure_ascii=False, default=str)
        )
        try:
            chat = LlmChat(
                api_key=key,
                session_id=f"landing-blueprint-{uuid.uuid4()}",
                system_message=build_system_prompt(),
            ).with_model("openai", self.model)
            raw = await chat.send_message(UserMessage(text=prompt))
        except Exception as exc:
            raise RuntimeError("Engine de execução falhou ao gerar o blueprint") from exc
        text = str(raw).strip()
        if text.startswith("```"):
            text = text.split("```", 2)[1].lstrip("json").strip()
        try:
            return LandingBlueprint.model_validate(json.loads(text))
        except Exception as exc:
            raise RuntimeError("Landing Brain retornou blueprint fora do contrato") from exc