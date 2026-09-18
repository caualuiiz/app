"""Contracts for Phase 2.9 Apply Design."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from .render_specification import RenderSpecification


class ApplyDesignRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    preview_id: str = Field(min_length=1, max_length=100)
    request_id: str = Field(min_length=1, max_length=100)
    expected_draft_version: int | None = Field(default=None, ge=0)


class ApplyDesignResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str
    preview_id: str
    company_id: str
    previous_version: int
    new_version: int
    render_spec: RenderSpecification
    idempotent: bool
    published: bool
    applied_at: str


class DraftVersionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    company_id: str
    version: int
    preview_id: str
    request_id: str
    created_at: str
