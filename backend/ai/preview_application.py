"""Contracts for Phase 2.8 Preview Application."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .render_specification import RenderSpecification

PreviewStatus = Literal["CREATED", "ACTIVE", "APPLIED", "EXPIRED", "CANCELLED"]


class CreatePreviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    render_spec_request_id: str | None = Field(default=None, min_length=1, max_length=100)
    expires_in_minutes: int = Field(default=30, ge=5, le=1440)


class PreviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    preview_id: str
    company_id: str
    landing_version: str
    render_spec: RenderSpecification
    created_at: datetime
    expires_at: datetime
    status: PreviewStatus


class PreviewListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    previews: list[PreviewResponse]
