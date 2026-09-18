from __future__ import annotations

import json
import os
from typing import Any

from .decision import StructuredDecision
from .landing_blueprint import LandingBlueprint
from .openai_runtime import OpenAIExecutionError, generate_json
from .professional_brain import build_system_prompt
from .reasoning_engine import ReasoningEngine


class LandingBrain(ReasoningEngine):
    name = "landing-brain"
    version = "1.1"

    def __init__(self, *, model: str | None = None):
        self.model = model or os.environ.get("LANDING_BRAIN_MODEL", "gpt-5.6-luna")

    async def decide(self, *, context: dict[str, Any]) -> StructuredDecision:
        try:
            result = await generate_json(
                system_prompt=build_system_prompt(),
                user_prompt=(
                    "Analise o projeto como um profissional sênior e produza decisões concretas. "
                    "Use somente as evidências fornecidas. Para cada ação, o target deve apontar para uma decisão "
                    "de design executável. Faça autocrítica interna e registre riscos em warnings. "
                    "Retorne SOMENTE JSON compatível com StructuredDecision.\n\n"
                    + json.dumps(context, ensure_ascii=False, default=str)
                ),
                model=self.model,
            )
            return StructuredDecision.model_validate(result)
        except OpenAIExecutionError as exc:
            raise RuntimeError(str(exc)) from exc

    async def build_blueprint(self, *, context: dict[str, Any]) -> LandingBlueprint:
        try:
            result = await generate_json(
                system_prompt=build_system_prompt(),
                user_prompt=(
                    "Crie um blueprint completo de landing page como um profissional com mais de 20 anos. "
                    "Não aprenda com os dados e não invente fatos. Defina Design System, Layout Plan e posicionamento "
                    "de cada imagem. Cada image_path visual deve receber uma função, seções-alvo, prioridade, tratamento, "
                    "crop e ponto focal. A estrutura deve refletir o negócio real, não um template fixo. "
                    "Retorne SOMENTE JSON compatível com LandingBlueprint.\n\n"
                    + json.dumps(context, ensure_ascii=False, default=str)
                ),
                model=self.model,
            )
            return LandingBlueprint.model_validate(result)
        except OpenAIExecutionError as exc:
            raise RuntimeError(str(exc)) from exc