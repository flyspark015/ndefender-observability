"""HTTP polling collector for Backend Aggregator."""

from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx

from ..health.model import HealthState
from ..metrics.registry import POLL_ERRORS_TOTAL, POLL_LATENCY_SECONDS
from ..state import ObservabilityState
from ..utils.time import now_ms


class AggregatorHttpCollector:
    def __init__(self, base_url: str, interval_s: int = 2, timeout_s: float = 2.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.interval_s = interval_s
        self.timeout_s = timeout_s
        self._stop = asyncio.Event()

    async def run(self, store: ObservabilityState) -> None:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout_s) as client:
            while not self._stop.is_set():
                try:
                    await self._poll_once(store, client)
                except Exception as exc:
                    POLL_ERRORS_TOTAL.labels(subsystem="aggregator", kind="loop_exception").inc()
                    store.update(
                        "aggregator",
                        state=HealthState.OFFLINE,
                        last_error=str(exc),
                        reasons=["poll loop error"],
                        updated_ts=now_ms(),
                        evidence={"base_url": self.base_url},
                    )
                try:
                    await asyncio.wait_for(self._stop.wait(), timeout=self.interval_s)
                except TimeoutError:
                    pass

    def stop(self) -> None:
        self._stop.set()

    async def _poll_once(self, store: ObservabilityState, client: httpx.AsyncClient) -> None:
        now = now_ms()
        reasons: list[str] = []
        evidence: dict[str, Any] = {"base_url": self.base_url}

        health_ok, health_status = await self._request_json(client, "/api/v1/health", "health")
        status_ok, status_payload = await self._request_json(client, "/api/v1/status", "status")

        if health_ok:
            evidence["health"] = health_status
        if status_ok:
            evidence["status_keys"] = list(status_payload.keys())

        if not health_ok:
            reasons.append("health endpoint failed")
        if not status_ok:
            reasons.append("status endpoint failed")

        if health_ok and status_ok:
            state = HealthState.OK
            last_error = None
        elif health_ok or status_ok:
            state = HealthState.DEGRADED
            last_error = "partial success"
        else:
            state = HealthState.OFFLINE
            last_error = "poll failed"

        store.update(
            "aggregator",
            state=state,
            updated_ts=now,
            last_error=last_error,
            reasons=reasons or ["ok"],
            evidence=evidence,
        )

    async def _request_json(
        self,
        client: httpx.AsyncClient,
        endpoint: str,
        kind: str,
    ) -> tuple[bool, dict[str, Any]]:
        start = time.perf_counter()
        try:
            resp = await client.get(endpoint)
            latency = time.perf_counter() - start
            POLL_LATENCY_SECONDS.labels(subsystem="aggregator", endpoint=kind).observe(latency)
            if resp.status_code != 200:
                POLL_ERRORS_TOTAL.labels(
                    subsystem="aggregator", kind=f"{kind}_http_{resp.status_code}"
                ).inc()
                return False, {}
            return True, resp.json()
        except Exception:
            latency = time.perf_counter() - start
            POLL_LATENCY_SECONDS.labels(subsystem="aggregator", endpoint=kind).observe(latency)
            POLL_ERRORS_TOTAL.labels(subsystem="aggregator", kind=f"{kind}_exception").inc()
            return False, {}
