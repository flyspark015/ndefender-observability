"""Health model definitions."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class HealthState(StrEnum):
    OK = "OK"
    DEGRADED = "DEGRADED"
    OFFLINE = "OFFLINE"
    REPLAY = "REPLAY"


class DeepHealth(BaseModel):
    subsystem: str
    state: HealthState
    updated_ts: int | None = None
    last_error: str | None = None
    last_error_ts: int | None = None
    last_response_ago_ms: int | None = None
    reasons: list[str] = Field(default_factory=list)
    evidence: dict[str, Any] = Field(default_factory=dict)
