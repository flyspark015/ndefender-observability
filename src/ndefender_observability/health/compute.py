"""Health computations."""

from __future__ import annotations

from collections import Counter
from typing import Any

from ..state import ObservabilityState, SubsystemState
from ..utils.time import now_ms
from .model import DeepHealth, HealthState

_STATE_ORDER = {
    HealthState.OFFLINE: 3,
    HealthState.DEGRADED: 2,
    HealthState.REPLAY: 1,
    HealthState.OK: 0,
}


def _overall_state(states: list[SubsystemState]) -> HealthState:
    if not states:
        return HealthState.OFFLINE
    return max(states, key=lambda item: _STATE_ORDER.get(item.state, 0)).state


def compute_deep_health(store: ObservabilityState) -> dict[str, Any]:
    now = now_ms()
    subsystems = []
    for item in store.all():
        subsystems.append(
            DeepHealth(
                subsystem=item.subsystem,
                state=item.state,
                updated_ts=item.updated_ts,
                last_error=item.last_error,
                last_error_ts=item.last_error_ts,
                last_response_ago_ms=item.age_ms(now),
                reasons=item.reasons,
                evidence=item.evidence,
            ).model_dump()
        )
    return {
        "generated_ts": now,
        "subsystems": subsystems,
    }


def compute_status_snapshot(store: ObservabilityState) -> dict[str, Any]:
    now = now_ms()
    subsystems = []
    for item in store.all():
        subsystems.append(
            {
                "subsystem": item.subsystem,
                "state": item.state,
                "last_update_age_ms": item.age_ms(now),
                "last_error_ts": item.last_error_ts,
            }
        )

    counts = Counter(item["state"] for item in subsystems)
    overall = _overall_state(store.all())
    return {
        "generated_ts": now,
        "overall_state": overall,
        "state_counts": {str(k): int(v) for k, v in counts.items()},
        "subsystems": subsystems,
    }
