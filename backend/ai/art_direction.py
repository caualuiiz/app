"""Contracts for Phase 2.3 Art Direction."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ArtDirection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    brand_personality: list[str] = Field(default_factory=list, max_length=12)
    visual_concept: str = Field(max_length=500)
    art_direction: str = Field(max_length=1200)
    image_direction: list[str] = Field(default_factory=list, max_length=12)
    typography_direction: list[str] = Field(default_factory=list, max_length=12)
    color_direction: list[str] = Field(default_factory=list, max_length=12)
    composition_direction: list[str] = Field(default_factory=list, max_length=12)
    motion_direction: list[str] = Field(default_factory=list, max_length=12)
    interaction_direction: list[str] = Field(default_factory=list, max_length=12)
    three_d_direction: str = Field(default="NONE", pattern="^(NONE|SUBTLE|HERO|IMMERSIVE)$")
    background_direction: list[str] = Field(default_factory=list, max_length=12)
    conversion_direction: list[str] = Field(default_factory=list, max_length=12)
    confidence: float = Field(default=0, ge=0, le=1)
    warnings: list[str] = Field(default_factory=list, max_length=12)
    missing_data: list[str] = Field(default_factory=list, max_length=12)


class GenerateArtDirectionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    visual_profile_request_id: str | None = Field(default=None, min_length=1, max_length=100)
    reference_profile_request_id: str | None = Field(default=None, min_length=1, max_length=100)


class ArtDirectionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str
    company_id: str
    visual_profile_request_id: str | None = None
    reference_profile_request_id: str | None = None
    direction: ArtDirection
    provider: str
    model: str
    created_at: str


class ArtDirectionListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    directions: list[ArtDirectionResponse]
