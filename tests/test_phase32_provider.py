import pytest

from backend.ai.claude_provider import ClaudeProvider
from backend.ai.decision_validator import validate_decision
from backend.ai.orchestrator import AIOrchestrator


class FakeProvider:
    name = "fake"
    model = "test-model"

    async def generate_structured_decision(self, *, system_prompt, context, schema_description):
        assert "company_id" not in context["company"]
        return {
            "summary": "Direção visual coerente para o negócio.",
            "actions": [{"type": "SET_THEME", "target": "landing.theme", "value": "editorial"}],
            "confidence": 0.91,
            "warnings": [],
            "missing_data": [],
        }


@pytest.mark.asyncio
async def test_orchestrator_sanitizes_tenant_identifiers_and_validates_decision():
    decision = await AIOrchestrator(FakeProvider()).decide(
        context={"company": {"name": "Teste", "company_id": "must-not-leak"}, "landing": {"hero": "Teste"}},
    )
    assert decision.confidence == 0.91
    assert decision.actions[0].type == "SET_THEME"


def test_validator_rejects_sensitive_fields():
    with pytest.raises(ValueError):
        validate_decision({"summary": "x", "actions": [], "confidence": 0.5, "warnings": [], "missing_data": [], "api_key": "secret"})


def test_claude_provider_requires_key():
    provider = ClaudeProvider(api_key="")
    assert provider.name == "claude"
    assert provider.api_key is None