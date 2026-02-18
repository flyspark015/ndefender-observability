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


def init_metrics(version: str, git_sha: str) -> None:
    OBSERVABILITY_UP.set(1)
    BUILD_INFO.labels(version=version, git_sha=git_sha).set(1)


def render_metrics() -> bytes:
    return generate_latest(REGISTRY)
