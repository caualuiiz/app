from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .design_system import DesignSystem
from .layout_plan import LayoutPlan

MediaRole = Literal[
    "hero",
    "environment",
    "service",
    "process",
    "detail",
    "proof",
    "support",
    "gallery",
]


class MediaPlacement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    image_path: str = Field(min_length=1, max_length=300)
    role: MediaRole
    target_sections: list[str] = Field(default_factory=list, max_length=8)
    priority: int = Field(default=1, ge=1, le=10)
    treatment: str = Field(min_length=1, max_length=240)
    crop: str = Field(default="preserve", max_length=120)
    focal_point: str = Field(default="center", max_length=120)


class LandingBlueprint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    professional_profile: str = Field(min_length=1, max_length=240)
    design_system: DesignSystem
    layout_plan: LayoutPlan
    media_placements: list[MediaPlacement] = Field(default_factory=list, max_length=8)
    content_tone: str = Field(min_length=1, max_length=240)
    conversion_strategy: list[str] = Field(default_factory=list, max_length=12)
    confidence: float = Field(ge=0, le=1)
    warnings: list[str] = Field(default_factory=list, max_length=20)
    missing_data: list[str] = Field(default_factory=list, max_length=20)
