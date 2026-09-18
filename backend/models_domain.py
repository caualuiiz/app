from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


DomainStatus = Literal["PENDING", "VERIFIED", "DISABLED"]


class DomainCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    domain: str = Field(min_length=3, max_length=253)


class DomainResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    domain: str
    status: DomainStatus
    verification_record: str
    verification_value: str
    created_at: str
    verified_at: str | None = None
