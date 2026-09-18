import asyncio

import pytest

from ai.claude_provider import ClaudeProvider
from ai.decision_validator import validate_decision
from ai.orchestrator import AIOrchestrator


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


def test_orchestrator_sanitizes_tenant_identifiers_and_validates_decision():
    decision = asyncio.run(AIOrchestrator(FakeProvider()).decide(
        context={"company": {"name": "Teste", "company_id": "must-not-leak"}, "landing": {"hero": "Teste"}},
    ))
    assert decision.confidence == 0.91
    assert decision.actions[0].type == "SET_THEME"


def test_validator_rejects_sensitive_fields():
    with pytest.raises(ValueError):
        validate_decision({
            "summary": "x",
            "actions": [],
            "confidence": 0.5,
            "warnings": [],
            "missing_data": [],
            "api_key": "secret",
        })


def test_claude_provider_accepts_explicit_test_configuration():
    provider = ClaudeProvider(api_key="test-key", model="claude-sonnet-5")
    assert provider.name == "claude"
    assert provider.model == "claude-sonnet-5"