from typing import Any, Literal

from pydantic import BaseModel, Field


DecisionType = Literal[
    "SET_THEME",
    "SET_COLORS",
    "SET_TYPOGRAPHY",
    "SET_LAYOUT",
    "SET_CONTENT_TONE",
    "SET_MEDIA_TREATMENT",
    "SET_MOTION",
    "SET_CONVERSION",
]


class DecisionAction(BaseModel):
    type: DecisionType
    target: str = Field(min_length=1, max_length=120)
    value: Any


class StructuredDecision(BaseModel):
    summary: str = Field(min_length=1, max_length=1000)
    actions: list[DecisionAction] = Field(default_factory=list, max_length=30)
    confidence: float = Field(ge=0, le=1)
    warnings: list[str] = Field(default_factory=list, max_length=30)
    missing_data: list[str] = Field(default_factory=list, max_length=30)

    @classmethod
    def schema_description(cls) -> str:
        return (
            "JSON com summary, actions, confidence, warnings e missing_data. "
            "Actions usam tipos SET_THEME, SET_COLORS, SET_TYPOGRAPHY, "
            "SET_LAYOUT, SET_CONTENT_TONE, SET_MEDIA_TREATMENT, SET_MOTION ou SET_CONVERSION."
        )


class AIDecisionResponse(BaseModel):
    request_id: str
    agent: str
    model: str | None = None
    decision: StructuredDecision
    created_at: str
