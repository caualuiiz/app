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

def test_claude_provider_uses_native_structured_parser(monkeypatch):
    import sys
    from types import SimpleNamespace

    from ai.decision import StructuredDecision

    class FakeMessages:
        async def parse(self, **kwargs):
            assert kwargs["model"] == "claude-sonnet-5"
            assert kwargs["output_format"] is StructuredDecision
            parsed = StructuredDecision(
                summary="Teste real simulado",
                actions=[],
                confidence=0.88,
                warnings=[],
                missing_data=[],
            )
            return SimpleNamespace(parsed_output=parsed)

    class FakeAsyncAnthropic:
        def __init__(self, api_key):
            assert api_key == "test-key"
            self.messages = FakeMessages()

    monkeypatch.setitem(sys.modules, "anthropic", SimpleNamespace(AsyncAnthropic=FakeAsyncAnthropic))

    provider = ClaudeProvider(api_key="test-key", model="claude-sonnet-5")
    result = asyncio.run(
        provider.generate_structured_decision(
            system_prompt="Teste",
            context={"company": {"name": "Teste"}},
            schema_description="Contrato",
        )
    )

    assert result["summary"] == "Teste real simulado"
    assert result["confidence"] == 0.88
