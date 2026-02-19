"""JSONL tail collector for AntSDR and RemoteID engines."""

from __future__ import annotations

import asyncio
import json
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..health.model import HealthState
from ..metrics.registry import (
    EVENTS_RATE_60S,
    EVENTS_TOTAL,
    JSONL_BYTES_DELTA_5M,
    JSONL_FILE_SIZE_BYTES,
    JSONL_LAST_EVENT_TS,
    JSONL_TAIL_LAG_SECONDS,
)
from ..state import ObservabilityState
from ..utils.time import now_ms


@dataclass
class _FileCursor:
    inode: int | None = None
    offset: int = 0


class _RateTracker:
    def __init__(self, window_s: int = 60) -> None:
        self.window_s = window_s
        self._events: dict[str, deque[float]] = {}

    def add(self, event_type: str, ts_s: float) -> None:
        bucket = self._events.setdefault(event_type, deque())
        bucket.append(ts_s)
        self._prune(bucket, ts_s)

    def rate(self, event_type: str, now_s: float) -> float:
        bucket = self._events.setdefault(event_type, deque())
        self._prune(bucket, now_s)
        return len(bucket) / self.window_s

    def _prune(self, bucket: deque[float], now_s: float) -> None:
        while bucket and now_s - bucket[0] > self.window_s:
            bucket.popleft()


class JsonlTailCollector:
    def __init__(
        self,
        subsystem: str,
        path: str,
        event_types: list[str],
        interval_s: int = 2,
        stale_after_s: int = 10,
        bootstrap_bytes: int = 65536,
    ) -> None:
        self.subsystem = subsystem
        self.path = Path(path)
        self.event_types = event_types
        self.interval_s = interval_s
        self.stale_after_s = stale_after_s
        self.bootstrap_bytes = bootstrap_bytes
        self._cursor = _FileCursor()
        self._rates = _RateTracker(window_s=60)
        self._stop = asyncio.Event()
        self._last_event_ts_ms: int | None = None
        self._last_event_type: str | None = None
        self._size_samples: deque[tuple[int, int]] = deque(maxlen=64)

    async def run(self, store: ObservabilityState) -> None:
        while not self._stop.is_set():
            try:
                await self._poll_once(store)
            except Exception as exc:
                store.update(
                    self.subsystem,
                    state=HealthState.OFFLINE,
                    last_error=str(exc),
                    last_error_ts=now_ms(),
                    reasons=["jsonl poll error"],
                    updated_ts=now_ms(),
                    evidence={"path": str(self.path)},
                )
            try:
                await asyncio.wait_for(self._stop.wait(), timeout=self.interval_s)
            except TimeoutError:
                pass

    def stop(self) -> None:
        self._stop.set()

    async def _poll_once(self, store: ObservabilityState) -> None:
        now = now_ms()
        if not self.path.exists():
            JSONL_FILE_SIZE_BYTES.labels(subsystem=self.subsystem).set(0)
            JSONL_TAIL_LAG_SECONDS.labels(subsystem=self.subsystem).set(-1)
            store.update(
                self.subsystem,
                state=HealthState.OFFLINE,
                last_error="file missing",
                last_error_ts=now,
                reasons=["jsonl file missing"],
                updated_ts=None,
                evidence={"path": str(self.path)},
            )
            return

        stat = self.path.stat()
        JSONL_FILE_SIZE_BYTES.labels(subsystem=self.subsystem).set(stat.st_size)
        self._size_samples.append((now, stat.st_size))

        inode = getattr(stat, "st_ino", None)
        bootstrap = self._cursor.inode is None or self._cursor.inode != inode
        if bootstrap:
            self._cursor = _FileCursor(inode=inode, offset=0)
        if stat.st_size < self._cursor.offset:
            self._cursor.offset = 0

        last_event_ts_ms: int | None = None
        last_event_type: str | None = None

        with self.path.open("rb") as handle:
            if bootstrap:
                tail_start = max(0, stat.st_size - self.bootstrap_bytes)
                handle.seek(tail_start)
                data = handle.read()
                lines = data.splitlines()
                if tail_start > 0 and lines:
                    lines = lines[1:]
                for raw in lines:
                    decoded = raw.decode("utf-8", errors="ignore").strip()
                    if not decoded:
                        continue
                    payload = _parse_json(decoded)
                    if payload is None:
                        continue
                    event_type = _extract_event_type(payload)
                    if event_type:
                        EVENTS_TOTAL.labels(subsystem=self.subsystem, type=event_type).inc()
                        self._rates.add(event_type, now / 1000)
                        last_event_type = event_type
                    ts_ms = _extract_timestamp_ms(payload)
                    if ts_ms is not None:
                        last_event_ts_ms = ts_ms
                    elif event_type:
                        last_event_ts_ms = now
                self._cursor.offset = stat.st_size
            else:
                handle.seek(self._cursor.offset)
                for line in handle:
                    decoded = line.decode("utf-8", errors="ignore").strip()
                    if not decoded:
                        continue
                    payload = _parse_json(decoded)
                    if payload is None:
                        continue
                    event_type = _extract_event_type(payload)
                    if event_type:
                        EVENTS_TOTAL.labels(subsystem=self.subsystem, type=event_type).inc()
                        self._rates.add(event_type, now / 1000)
                        last_event_type = event_type
                    ts_ms = _extract_timestamp_ms(payload)
                    if ts_ms is not None:
                        last_event_ts_ms = ts_ms
                    elif event_type:
                        last_event_ts_ms = now
                self._cursor.offset = handle.tell()

        if last_event_ts_ms is not None:
            self._last_event_ts_ms = last_event_ts_ms
        if last_event_type is not None:
            self._last_event_type = last_event_type

        last_event_ts_ms = self._last_event_ts_ms

        if last_event_ts_ms is None:
            JSONL_TAIL_LAG_SECONDS.labels(subsystem=self.subsystem).set(-1)
            age_s = self.stale_after_s + 1
        else:
            age_s = max(0.0, (now - last_event_ts_ms) / 1000)
            JSONL_TAIL_LAG_SECONDS.labels(subsystem=self.subsystem).set(age_s)
            JSONL_LAST_EVENT_TS.labels(subsystem=self.subsystem).set(last_event_ts_ms / 1000)

        for event_type in self.event_types:
            rate = self._rates.rate(event_type, now / 1000)
            EVENTS_RATE_60S.labels(subsystem=self.subsystem, type=event_type).set(rate)

        delta = _growth_over_window(self._size_samples, window_ms=300_000)
        JSONL_BYTES_DELTA_5M.labels(subsystem=self.subsystem).set(delta)

        if last_event_ts_ms is None:
            state = HealthState.DEGRADED
            reasons = ["no events yet"]
            last_error = "no events"
        elif age_s <= self.stale_after_s:
            state = HealthState.OK
            reasons = ["ok"]
            last_error = None
        else:
            state = HealthState.DEGRADED
            reasons = ["stale events"]
            last_error = "stale"

        store.update(
            self.subsystem,
            state=state,
            updated_ts=last_event_ts_ms,
            last_error=last_error,
            last_error_ts=now if last_error else None,
            reasons=reasons,
            evidence={
                "path": str(self.path),
                "last_event_type": self._last_event_type,
                "last_event_ts": last_event_ts_ms,
                "file_size": stat.st_size,
            },
        )


def _parse_json(line: str) -> dict[str, Any] | None:
    try:
        data = json.loads(line)
    except json.JSONDecodeError:
        return None
    if isinstance(data, dict):
        return data
    return None


def _extract_event_type(payload: dict[str, Any]) -> str | None:
    for key in ("type", "event_type", "event", "kind"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _extract_timestamp_ms(payload: dict[str, Any]) -> int | None:
    for key in ("timestamp_ms", "timestamp", "time_ms", "ts_ms", "ts"):
        value = payload.get(key)
        if value is None:
            continue
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if key in {"timestamp", "ts"} and number < 1_000_000_000_000:
            return int(number * 1000)
        if number < 1_000_000_000_000:
            return int(number * 1000)
        return int(number)
    return None


def _growth_over_window(samples: deque[tuple[int, int]], window_ms: int) -> float:
    if len(samples) < 2:
        return 0.0
    newest_ts, newest_size = samples[-1]
    oldest_ts, oldest_size = samples[0]
    for ts, size in samples:
        if newest_ts - ts <= window_ms:
            oldest_ts, oldest_size = ts, size
            break
    if newest_ts == oldest_ts:
        return 0.0
    return float(max(0, newest_size - oldest_size))
