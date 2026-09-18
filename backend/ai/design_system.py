"""Contracts for Phase 2.4 Design System."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

HexColor = str


class DesignColors(BaseModel):
    model_config = ConfigDict(extra="forbid")

    primary: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    secondary: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    accent: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    background: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    surface: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    text: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    muted: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    border: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")


class DesignTypography(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display: str = Field(min_length=1, max_length=100)
    heading: str = Field(min_length=1, max_length=100)
    body: str = Field(min_length=1, max_length=100)
    label: str = Field(min_length=1, max_length=100)
    button: str = Field(min_length=1, max_length=100)


class DesignSpacing(BaseModel):
    model_config = ConfigDict(extra="forbid")

    xs: str = Field(min_length=1, max_length=30)
    sm: str = Field(min_length=1, max_length=30)
    md: str = Field(min_length=1, max_length=30)
    lg: str = Field(min_length=1, max_length=30)
    xl: str = Field(min_length=1, max_length=30)
    two_xl: str = Field(min_length=1, max_length=30, alias="2xl")
    section: str = Field(min_length=1, max_length=30)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class DesignRadius(BaseModel):
    model_config = ConfigDict(extra="forbid")

    none: str = Field(min_length=1, max_length=30)
    small: str = Field(min_length=1, max_length=30)
    medium: str = Field(min_length=1, max_length=30)
    large: str = Field(min_length=1, max_length=30)
    pill: str = Field(min_length=1, max_length=30)


class DesignGrid(BaseModel):
    model_config = ConfigDict(extra="forbid")

    max_width: str = Field(min_length=1, max_length=30)
    columns: int = Field(ge=1, le=24)
    gutter: str = Field(min_length=1, max_length=30)
    margins: str = Field(min_length=1, max_length=60)


class DesignMotion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    duration: str = Field(min_length=1, max_length=30)
    easing: str = Field(min_length=1, max_length=80)
    intensity: Literal["LOW", "MEDIUM", "HIGH"]


class DesignVisual(BaseModel):
    model_config = ConfigDict(extra="forbid")

    image_treatment: str = Field(min_length=1, max_length=240)
    shadows: str = Field(min_length=1, max_length=160)
    borders: str = Field(min_length=1, max_length=160)
    overlays: str = Field(min_length=1, max_length=240)


class DesignResponsive(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mobile: str = Field(min_length=1, max_length=300)
    tablet: str = Field(min_length=1, max_length=300)
    desktop: str = Field(min_length=1, max_length=300)


class DesignSystem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    colors: DesignColors
    typography: DesignTypography
    spacing: DesignSpacing
    radius: DesignRadius
    grid: DesignGrid
    motion: DesignMotion
    visual: DesignVisual
    responsive: DesignResponsive
    accessibility_notes: list[str] = Field(default_factory=list, max_length=12)
    confidence: float = Field(default=0, ge=0, le=1)
    warnings: list[str] = Field(default_factory=list, max_length=12)


class GenerateDesignSystemRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    art_direction_request_id: str | None = Field(default=None, min_length=1, max_length=100)


class DesignSystemResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str
    company_id: str
    art_direction_request_id: str | None = None
    design_system: DesignSystem
    provider: str
    model: str
    created_at: str


class DesignSystemListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    systems: list[DesignSystemResponse]
