"""Contracts for Phase 2.5 Layout Plan."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

LayoutMode = Literal[
    "cinematic_fullscreen", "editorial_split", "asymmetric_grid", "immersive_gallery",
    "horizontal_gallery", "sticky_storytelling", "oversized_typography", "project_showcase",
    "image_led_section", "comparison", "timeline", "process_storytelling", "interactive_visual",
]


class LayoutSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, max_length=60, pattern=r"^[a-z0-9][a-z0-9_-]*$")
    purpose: str = Field(min_length=1, max_length=240)
    layout: LayoutMode
    content_source: str = Field(min_length=1, max_length=240)
    visual_treatment: str = Field(min_length=1, max_length=240)
    interaction: str = Field(min_length=1, max_length=180)
    motion: str = Field(min_length=1, max_length=180)
    responsive_behavior: str = Field(min_length=1, max_length=300)


class LayoutPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sections: list[LayoutSection] = Field(min_length=1, max_length=12)
    page_rhythm: str = Field(min_length=1, max_length=240)
    responsive_strategy: str = Field(min_length=1, max_length=300)
    accessibility_strategy: str = Field(min_length=1, max_length=300)
    performance_strategy: str = Field(min_length=1, max_length=300)
    confidence: float = Field(default=0, ge=0, le=1)
    warnings: list[str] = Field(default_factory=list, max_length=12)

    @field_validator("sections")
    @classmethod
    def unique_section_ids(cls, sections: list[LayoutSection]) -> list[LayoutSection]:
        ids = [section.id for section in sections]
        if len(ids) != len(set(ids)):
            raise ValueError("IDs de seção devem ser únicos")
        return sections


class GenerateLayoutPlanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    design_system_request_id: str | None = Field(default=None, min_length=1, max_length=100)


class LayoutPlanResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str
    company_id: str
    design_system_request_id: str
    layout_plan: LayoutPlan
    provider: str
    model: str
    created_at: str


class LayoutPlanListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plans: list[LayoutPlanResponse]
