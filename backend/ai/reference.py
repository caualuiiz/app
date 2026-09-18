"""Contracts for Phase 2.2 Reference Intelligence."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class ReferenceAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    typography: list[str] = Field(default_factory=list, max_length=12)
    spacing: list[str] = Field(default_factory=list, max_length=12)
    composition: list[str] = Field(default_factory=list, max_length=12)
    color_strategy: list[str] = Field(default_factory=list, max_length=12)
    imagery: list[str] = Field(default_factory=list, max_length=12)
    motion: list[str] = Field(default_factory=list, max_length=12)
    interaction: list[str] = Field(default_factory=list, max_length=12)
    layout_philosophy: list[str] = Field(default_factory=list, max_length=12)
    visual_density: str | None = Field(default=None, max_length=120)
    editorial_characteristics: list[str] = Field(default_factory=list, max_length=12)
    premium_characteristics: list[str] = Field(default_factory=list, max_length=12)
    design_principles: list[str] = Field(default_factory=list, max_length=20)
    prohibited_copy: list[str] = Field(default_factory=list, max_length=12)
    confidence: float = Field(default=0, ge=0, le=1)


class AnalyzeReferencesRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: HttpUrl | None = None
    description: str | None = Field(default=None, min_length=1, max_length=4000)
    image_ids: list[str] = Field(default_factory=list, max_length=8)

    @model_validator(mode="after")
    def require_source(self):
        if self.url is None and not self.description and not self.image_ids:
            raise ValueError("Informe uma URL, descrição ou imagem de referência")
        return self


class ReferenceProfileResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str
    company_id: str
    source_types: list[Literal["url", "description", "image"]]
    source_url: str | None = None
    source_description: str | None = None
    image_count: int = Field(ge=0)
    image_paths: list[str] = Field(max_length=8)
    analysis: ReferenceAnalysis
    provider: Literal["existing"]
    model: str
    created_at: str


class ReferenceProfileListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profiles: list[ReferenceProfileResponse]
