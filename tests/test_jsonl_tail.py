import asyncio
import json
from pathlib import Path

from ndefender_observability.collectors.jsonl_tail import JsonlTailCollector
from ndefender_observability.health.model import HealthState
from ndefender_observability.metrics.registry import (
    EVENTS_RATE_60S,
    EVENTS_TOTAL,
    JSONL_TAIL_LAG_SECONDS,
)
from ndefender_observability.state import ObservabilityState
from ndefender_observability.utils.time import now_ms


def _write_lines(path: Path, lines: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for payload in lines:
            handle.write(json.dumps(payload))
            handle.write("\n")


def test_jsonl_tail_reads_events(tmp_path: Path) -> None:
    path = tmp_path / "antsdr.jsonl"
    _write_lines(
        path,
        [
            {"type": "RF_CONTACT_NEW", "timestamp_ms": now_ms()},
            {"type": "RF_CONTACT_UPDATE", "timestamp_ms": now_ms()},
        ],
    )
    store = ObservabilityState()
    collector = JsonlTailCollector(
        subsystem="antsdr",
        path=str(path),
        event_types=["RF_CONTACT_NEW", "RF_CONTACT_UPDATE", "RF_CONTACT_LOST"],
        interval_s=1,
        stale_after_s=10,
    )
    asyncio.run(collector._poll_once(store))

    state = store.get("antsdr")
    assert state.state == HealthState.OK
    assert state.updated_ts is not None

    count = EVENTS_TOTAL.labels(subsystem="antsdr", type="RF_CONTACT_NEW")._value.get()
    assert count >= 1
    rate = EVENTS_RATE_60S.labels(subsystem="antsdr", type="RF_CONTACT_NEW")._value.get()
    assert rate >= 0


def test_jsonl_tail_missing_file(tmp_path: Path) -> None:
    path = tmp_path / "missing.jsonl"
    store = ObservabilityState()
    collector = JsonlTailCollector(
        subsystem="remoteid",
        path=str(path),
        event_types=["CONTACT_NEW"],
        interval_s=1,
        stale_after_s=10,
    )
    asyncio.run(collector._poll_once(store))

    state = store.get("remoteid")
    assert state.state == HealthState.OFFLINE
    lag = JSONL_TAIL_LAG_SECONDS.labels(subsystem="remoteid")._value.get()
    assert lag == -1
