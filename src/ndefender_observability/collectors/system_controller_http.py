"""HTTP polling collector for System Controller (UPS metrics)."""

from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx

from ..health.model import HealthState
from ..metrics.registry import (
    POLL_ERRORS_TOTAL,
    POLL_LATENCY_SECONDS,
    UPS_CELL_VOLTAGE_V,
    UPS_CURRENT_A,
    UPS_INPUT_POWER_W,
    UPS_INPUT_VBUS_V,
    UPS_PACK_VOLTAGE_V,
    UPS_SOC_PERCENT,
    UPS_STATE,
    UPS_TIME_TO_EMPTY_S,
    UPS_TIME_TO_FULL_S,
)
from ..state import ObservabilityState
from ..utils.time import now_ms

_UPS_STATE_LABELS = [
    "IDLE",
    "CHARGING",
    "FAST_CHARGING",
    "DISCHARGING",
    "UNKNOWN",
]


class SystemControllerHttpCollector:
    def __init__(self, base_url: str, interval_s: int = 5, timeout_s: float = 2.0) -> None:
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
                    POLL_ERRORS_TOTAL.labels(
                        subsystem="system_controller", kind="loop_exception"
                    ).inc()
                    store.update(
                        "system_controller",
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

        health_ok, health_payload = await self._request_json(client, "/api/v1/health", "health")
        status_ok, status_payload = await self._request_json(client, "/api/v1/status", "status")
        ups_ok, ups_payload = await self._request_json(client, "/api/v1/ups", "ups")

        if health_ok:
            evidence["health"] = health_payload
        if status_ok:
            evidence["status_keys"] = list(status_payload.keys())
        if ups_ok:
            evidence["ups_keys"] = list(ups_payload.keys())
            self._record_ups_metrics(ups_payload)

        if not health_ok:
            reasons.append("health endpoint failed")
        if not status_ok:
            reasons.append("status endpoint failed")
        if not ups_ok:
            reasons.append("ups endpoint failed")

        if health_ok and status_ok and ups_ok:
            state = HealthState.OK
            last_error = None
        elif health_ok or status_ok or ups_ok:
            state = HealthState.DEGRADED
            last_error = "partial success"
        else:
            state = HealthState.OFFLINE
            last_error = "poll failed"

        store.update(
            "system_controller",
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
            POLL_LATENCY_SECONDS.labels(
                subsystem="system_controller", endpoint=kind
            ).observe(latency)
            if resp.status_code != 200:
                POLL_ERRORS_TOTAL.labels(
                    subsystem="system_controller", kind=f"{kind}_http_{resp.status_code}"
                ).inc()
                return False, {}
            return True, resp.json()
        except Exception:
            latency = time.perf_counter() - start
            POLL_LATENCY_SECONDS.labels(
                subsystem="system_controller", endpoint=kind
            ).observe(latency)
            POLL_ERRORS_TOTAL.labels(
                subsystem="system_controller", kind=f"{kind}_exception"
            ).inc()
            return False, {}

    def _record_ups_metrics(self, payload: dict[str, Any]) -> None:
        def _get_number(key: str) -> float | None:
            value = payload.get(key)
            if value is None:
                return None
            try:
                return float(value)
            except (TypeError, ValueError):
                return None

        pack_voltage = _get_number("pack_voltage_v")
        if pack_voltage is not None:
            UPS_PACK_VOLTAGE_V.set(pack_voltage)

        current_a = _get_number("current_a")
        if current_a is not None:
            UPS_CURRENT_A.set(current_a)

        input_vbus = _get_number("input_vbus_v")
        if input_vbus is not None:
            UPS_INPUT_VBUS_V.set(input_vbus)

        input_power = _get_number("input_power_w")
        if input_power is not None:
            UPS_INPUT_POWER_W.set(input_power)

        soc_percent = _get_number("soc_percent")
        if soc_percent is not None:
            UPS_SOC_PERCENT.set(soc_percent)

        time_to_empty = _get_number("time_to_empty_s")
        if time_to_empty is not None:
            UPS_TIME_TO_EMPTY_S.set(time_to_empty)

        time_to_full = _get_number("time_to_full_s")
        if time_to_full is not None:
            UPS_TIME_TO_FULL_S.set(time_to_full)

        per_cell = payload.get("per_cell_v") or payload.get("cell_voltage_v")
        if isinstance(per_cell, dict):
            for cell, value in per_cell.items():
                try:
                    UPS_CELL_VOLTAGE_V.labels(cell=str(cell)).set(float(value))
                except (TypeError, ValueError):
                    continue

        state = payload.get("state")
        if state:
            state = str(state).upper()
        else:
            state = "UNKNOWN"
        if state not in _UPS_STATE_LABELS:
            state = "UNKNOWN"
        for label in _UPS_STATE_LABELS:
            UPS_STATE.labels(state=label).set(1 if label == state else 0)
