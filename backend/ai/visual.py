"""Contracts for Phase 2.1 Visual Intelligence."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class VisualAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dominant_colors: list[str] = Field(default_factory=list, max_length=8)
    secondary_colors: list[str] = Field(default_factory=list, max_length=8)
    brightness: float | None = Field(default=None, ge=0, le=1)
    contrast: float | None = Field(default=None, ge=0, le=1)
    saturation: float | None = Field(default=None, ge=0, le=1)
    mood: str | None = Field(default=None, max_length=160)
    style: str | None = Field(default=None, max_length=160)
    environment: str | None = Field(default=None, max_length=240)
    composition: str | None = Field(default=None, max_length=240)
    subject: str | None = Field(default=None, max_length=240)
    materials: list[str] = Field(default_factory=list, max_length=12)
    lighting: str | None = Field(default=None, max_length=240)
    luxury_level: float | None = Field(default=None, ge=0, le=1)
    minimalism_level: float | None = Field(default=None, ge=0, le=1)
    visual_density: float | None = Field(default=None, ge=0, le=1)
    photographic_characteristics: list[str] = Field(default_factory=list, max_length=12)
    confidence: float = Field(default=0, ge=0, le=1)


class AnalyzeImagesRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    image_ids: list[str] = Field(default_factory=list, max_length=8)
    include_establishment_photo: bool = False


class VisualProfileResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str
    company_id: str
    image_count: int = Field(ge=1)
    image_paths: list[str] = Field(max_length=8)
    analysis: VisualAnalysis
    provider: Literal["existing"]
    model: str
    created_at: str


class VisualProfileListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profiles: list[VisualProfileResponse]
