"""Prometheus registry and core instruments."""

from prometheus_client import CollectorRegistry, Gauge, generate_latest

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


def render_metrics() -> bytes:
    return generate_latest(REGISTRY)
