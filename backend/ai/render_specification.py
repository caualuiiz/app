"""Contracts for Phase 2.6 Render Specification."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .design_system import DesignColors, DesignSpacing, DesignTypography
from .layout_plan import LayoutMode

SectionType = Literal["hero", "about", "services", "professionals", "gallery", "differentiators", "hours", "contact"]
InteractionMode = Literal["none", "link", "cta", "scroll", "gallery", "accordion", "form"]
MotionMode = Literal["none", "fade", "slide", "scale", "parallax"]


def _safe_reference(value: str) -> str:
    if not value or len(value) > 160 or not value.replace(".", "").replace("_", "").replace("-", "").isalnum():
        raise ValueError("Referência deve ser um caminho estruturado seguro")
    if not value.startswith(("landing.", "company.", "media.", "profile.")):
        raise ValueError("Referência fora do namespace permitido")
    return value


class RenderSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, max_length=60, pattern=r"^[a-z0-9][a-z0-9_-]*$")
    section_type: SectionType
    layout_mode: LayoutMode
    content_references: list[str] = Field(default_factory=list, max_length=12)
    image_references: list[str] = Field(default_factory=list, max_length=12)
    typography: str = Field(min_length=1, max_length=120)
    spacing: str = Field(min_length=1, max_length=120)
    colors: str = Field(min_length=1, max_length=160)
    motion: MotionMode
    interaction: InteractionMode
    responsive_behavior: str = Field(min_length=1, max_length=300)
    accessibility: str = Field(min_length=1, max_length=300)
    fallback_behavior: str = Field(min_length=1, max_length=300)

    @field_validator("content_references", "image_references")
    @classmethod
    def validate_references(cls, values: list[str]) -> list[str]:
        return [_safe_reference(value) for value in values]


class RenderMotion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intensity: Literal["LOW", "MEDIUM", "HIGH"]
    reduced_motion: str = Field(min_length=1, max_length=240)
    fallback: str = Field(min_length=1, max_length=240)


class RenderInteractions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    keyboard: str = Field(min_length=1, max_length=240)
    touch: str = Field(min_length=1, max_length=240)
    focus: str = Field(min_length=1, max_length=240)


class RenderResponsive(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mobile: str = Field(min_length=1, max_length=300)
    tablet: str = Field(min_length=1, max_length=300)
    desktop: str = Field(min_length=1, max_length=300)


class RenderMedia(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lazy_loading: bool
    allowed_types: list[Literal["image", "logo", "gallery"]] = Field(max_length=6)
    fallback: str = Field(min_length=1, max_length=240)


class RenderAccessibility(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contrast: str = Field(min_length=1, max_length=160)
    semantics: str = Field(min_length=1, max_length=240)
    alt_text: str = Field(min_length=1, max_length=240)
    reduced_motion: str = Field(min_length=1, max_length=240)


class RenderSpecification(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["1.0"]
    theme: DesignColors
    typography: DesignTypography
    spacing: DesignSpacing
    sections: list[RenderSection] = Field(min_length=1, max_length=12)
    motion: RenderMotion
    interactions: RenderInteractions
    responsive: RenderResponsive
    media: RenderMedia
    accessibility: RenderAccessibility

    @field_validator("sections")
    @classmethod
    def unique_section_ids(cls, sections: list[RenderSection]) -> list[RenderSection]:
        ids = [section.id for section in sections]
        if len(ids) != len(set(ids)):
            raise ValueError("IDs de seção devem ser únicos")
        return sections


class GenerateRenderSpecRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    layout_plan_request_id: str | None = Field(default=None, min_length=1, max_length=100)


class RenderSpecificationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str
    company_id: str
    layout_plan_request_id: str
    render_specification: RenderSpecification
    provider: str
    model: str
    created_at: str


class RenderSpecificationListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    specifications: list[RenderSpecificationResponse]
