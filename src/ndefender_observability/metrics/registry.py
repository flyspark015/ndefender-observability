"""Prometheus registry and core instruments."""

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, generate_latest

from ..health.model import HealthState
from ..state import ObservabilityState
from ..utils.time import now_ms

REGISTRY = CollectorRegistry()

OBSERVABILITY_UP = Gauge(
    "ndefender_observability_up",
    "Observability service up",
    registry=REGISTRY,
)
BUILD_INFO = Gauge(
    "ndefender_observability_build_info",
    "Build info",
    ["version", "git_sha"],
    registry=REGISTRY,
)

POLL_ERRORS_TOTAL = Counter(
    "ndefender_observability_poll_errors_total",
    "Poll errors by subsystem",
    ["subsystem", "kind"],
    registry=REGISTRY,
)
POLL_LATENCY_SECONDS = Histogram(
    "ndefender_observability_poll_latency_seconds",
    "Poll latency seconds",
    ["subsystem", "endpoint"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 5),
    registry=REGISTRY,
)

SUBSYSTEM_UP = Gauge(
    "ndefender_subsystem_up",
    "Subsystem up",
    ["subsystem"],
    registry=REGISTRY,
)
SUBSYSTEM_LAST_UPDATE_AGE_SECONDS = Gauge(
    "ndefender_subsystem_last_update_age_seconds",
    "Subsystem last update age in seconds",
    ["subsystem"],
    registry=REGISTRY,
)
SUBSYSTEM_STATE = Gauge(
    "ndefender_subsystem_state",
    "Subsystem health state",
    ["subsystem", "state"],
    registry=REGISTRY,
)

AGGREGATOR_UP = Gauge(
    "ndefender_aggregator_up",
    "Backend aggregator up",
    registry=REGISTRY,
)

PI_CPU_TEMP_C = Gauge(
    "ndefender_pi_cpu_temp_c",
    "Raspberry Pi CPU temperature in C",
    registry=REGISTRY,
)
PI_THROTTLED_FLAG = Gauge(
    "ndefender_pi_throttled_flags",
    "Raspberry Pi throttled flags",
    ["flag"],
    registry=REGISTRY,
)
PI_DISK_FREE_BYTES = Gauge(
    "ndefender_pi_disk_free_bytes",
    "Disk free bytes",
    ["mount"],
    registry=REGISTRY,
)
PI_MEM_AVAILABLE_BYTES = Gauge(
    "ndefender_pi_mem_available_bytes",
    "Memory available bytes",
    registry=REGISTRY,
)
PI_LOAD1 = Gauge(
    "ndefender_pi_load1",
    "System load average (1m)",
    registry=REGISTRY,
)
PI_LOAD5 = Gauge(
    "ndefender_pi_load5",
    "System load average (5m)",
    registry=REGISTRY,
)
PI_LOAD15 = Gauge(
    "ndefender_pi_load15",
    "System load average (15m)",
    registry=REGISTRY,
)


def init_metrics(version: str, git_sha: str) -> None:
    OBSERVABILITY_UP.set(1)
    BUILD_INFO.labels(version=version, git_sha=git_sha).set(1)


def update_subsystem_metrics(store: ObservabilityState) -> None:
    now = now_ms()
    for item in store.all():
        is_up = 1 if item.state != HealthState.OFFLINE else 0
        SUBSYSTEM_UP.labels(subsystem=item.subsystem).set(is_up)
        age_ms = item.age_ms(now)
        age_seconds = age_ms / 1000 if age_ms is not None else -1
        SUBSYSTEM_LAST_UPDATE_AGE_SECONDS.labels(subsystem=item.subsystem).set(age_seconds)
        for state in HealthState:
            SUBSYSTEM_STATE.labels(subsystem=item.subsystem, state=state.value).set(
                1 if item.state == state else 0
            )
        if item.subsystem == "aggregator":
            AGGREGATOR_UP.set(is_up)


def render_metrics() -> bytes:
    return generate_latest(REGISTRY)
