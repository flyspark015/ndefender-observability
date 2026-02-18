"""In-memory state store for subsystems."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .health.model import HealthState


@dataclass
class SubsystemState:
    subsystem: str
    state: HealthState = HealthState.OFFLINE
    updated_ts: int | None = None
    last_error: str | None = None
    reasons: list[str] = field(default_factory=list)
    evidence: dict[str, Any] = field(default_factory=dict)

    def age_ms(self, now_ms: int) -> int | None:
        if self.updated_ts is None:
            return None
        return max(0, now_ms - self.updated_ts)


class ObservabilityState:
    def __init__(self) -> None:
        self._states: dict[str, SubsystemState] = {}
        for name in ("aggregator", "system_controller", "antsdr", "remoteid", "esp32"):
            self._states[name] = SubsystemState(
                subsystem=name,
                state=HealthState.OFFLINE,
                reasons=["no data yet"],
            )

    def get(self, subsystem: str) -> SubsystemState:
        return self._states[subsystem]

    def all(self) -> list[SubsystemState]:
        return list(self._states.values())

    def update(
        self,
        subsystem: str,
        *,
        state: HealthState | None = None,
        updated_ts: int | None = None,
        last_error: str | None = None,
        reasons: list[str] | None = None,
        evidence: dict[str, Any] | None = None,
    ) -> None:
        current = self._states[subsystem]
        if state is not None:
            current.state = state
        if updated_ts is not None:
            current.updated_ts = updated_ts
        if last_error is not None:
            current.last_error = last_error
        if reasons is not None:
            current.reasons = reasons
        if evidence is not None:
            current.evidence = evidence
