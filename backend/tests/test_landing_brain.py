import asyncio

from ai.decision import StructuredDecision
from ai.orchestrator import AIOrchestrator
from ai.professional_brain import build_system_prompt
from ai.reasoning_engine import ReasoningEngine


class FakeEngine(ReasoningEngine):
    name = "fake-landing-brain"
    version = "test"

    async def decide(self, *, context):
        assert "company_id" not in context["company"]
        assert "password" not in context["landing"]
        return StructuredDecision(
            summary="Direção visual coerente.",
            actions=[
                {
                    "type": "SET_THEME",
                    "target": "landing.theme",
                    "value": "editorial",
                }
            ],
            confidence=0.91,
            warnings=[],
            missing_data=[],
        )


def test_professional_brain_is_experienced_and_does_not_learn():
    prompt = build_system_prompt().lower()
    assert "20 anos" in prompt
    assert "não está treinando" in prompt
    assert "não aprende" in prompt
    assert "autocrítica" in prompt


def test_orchestrator_uses_fixed_professional_engine():
    decision = asyncio.run(
        AIOrchestrator(FakeEngine()).decide(
            context={
                "company": {
                    "name": "Teste",
                    "company_id": "must-not-leak",
                },
                "landing": {
                    "hero": "Teste",
                    "password": "must-not-leak",
                },
            }
        )
    )
    assert decision.confidence == 0.91
    assert decision.actions[0].type == "SET_THEME"


def test_decision_contract_rejects_sensitive_fields():
    from ai.decision_validator import validate_decision

    try:
        validate_decision(
            {
                "summary": "x",
                "actions": [],
                "confidence": 0.5,
                "warnings": [],
                "missing_data": [],
                "api_key": "secret",
            }
        )
    except ValueError:
        return
    raise AssertionError("Sensitive field should be rejected")
