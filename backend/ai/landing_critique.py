from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


Severity = Literal["LOW", "MEDIUM", "HIGH"]


class CritiqueFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: Literal["hierarchy", "visual_consistency", "media", "conversion", "content", "responsive", "accessibility", "performance"]
    severity: Severity
    finding: str = Field(min_length=1, max_length=500)
    reason: str = Field(min_length=1, max_length=600)
    recommendation: str = Field(min_length=1, max_length=600)


class LandingCritique(BaseModel):
    model_config = ConfigDict(extra="forbid")

    overall_assessment: str = Field(min_length=1, max_length=1000)
    findings: list[CritiqueFinding] = Field(default_factory=list, max_length=30)
    strengths: list[str] = Field(default_factory=list, max_length=12)
    priority_actions: list[str] = Field(default_factory=list, max_length=10)
    ready_for_publish: bool
    confidence: float = Field(ge=0, le=1)


class LandingCritiqueResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str
    preview_id: str
    company_id: str
    critique: LandingCritique
    created_at: str