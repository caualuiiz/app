from typing import Any

from .decision import StructuredDecision
from .decision_validator import validate_decision
from .provider import AIProvider


class AIOrchestrator:
    def __init__(self, provider: AIProvider):
        self.provider = provider

    async def decide(self, *, context: dict[str, Any]) -> StructuredDecision:
        safe_context = {
            "company": self._pick(context.get("company"), ("name", "business_type", "description", "city")),
            "landing": self._pick(context.get("landing"), ("hero", "about", "style", "sections")),
            "visual_intelligence": self._sanitize(context.get("visual_intelligence")),
            "reference_intelligence": self._sanitize(context.get("reference_intelligence")),
            "art_direction": self._sanitize(context.get("art_direction")),
            "design_system": self._sanitize(context.get("design_system")),
            "layout_plan": self._sanitize(context.get("layout_plan")),
        }
        result = await self.provider.generate_structured_decision(
            system_prompt="Você é o Diretor de Arte Digital de uma plataforma SaaS multi-tenant. Transforme sinais visuais e dados públicos em decisões de design. Não invente fatos, não gere código e não altere dados fora do contrato.",
            context=safe_context,
            schema_description=StructuredDecision.schema_description(),
        )
        return validate_decision(result)

    @classmethod
    def _pick(cls, value: Any, keys: tuple[str, ...]) -> dict[str, Any]:
        source = value if isinstance(value, dict) else {}
        return {key: cls._sanitize(source.get(key)) for key in keys if key in source}

    @classmethod
    def _sanitize(cls, value: Any) -> Any:
        forbidden = {"company_id", "user_id", "password", "password_hash", "jwt", "token", "api_key", "secret"}
        if isinstance(value, dict):
            return {str(key): cls._sanitize(child) for key, child in value.items() if str(key).lower() not in forbidden and not any(part in str(key).lower() for part in ("api_key", "password", "secret"))}
        if isinstance(value, list):
            return [cls._sanitize(child) for child in value]
        return value