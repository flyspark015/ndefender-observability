"""Config loading with env overrides."""

from __future__ import annotations

import copy
import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class ServiceConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 9109


class AuthConfig(BaseModel):
    enabled: bool = False
    api_key: str | None = None


class RateLimitConfig(BaseModel):
    enabled: bool = False
    max_requests: int = 60
    window_s: int = 60


class PollingConfig(BaseModel):
    aggregator_s: int = 2
    system_controller_s: int = 5
    antsdr_jsonl_s: int = 2
    remoteid_jsonl_s: int = 2
    esp32_s: int = 2


class BackendAggregatorConfig(BaseModel):
    base_url: str = "http://127.0.0.1:8000"


class SystemControllerConfig(BaseModel):
    base_url: str = "http://127.0.0.1:9000"


class JsonlConfig(BaseModel):
    antsdr_path: str = "/opt/ndefender/logs/antsdr_scan.jsonl"
    remoteid_path: str = "/opt/ndefender/logs/remoteid_engine.jsonl"


class WsConfig(BaseModel):
    enabled: bool = False
    metrics_update_hz: int = 1


class StaleThresholds(BaseModel):
    aggregator: int = 5
    system_controller: int = 10
    antsdr: int = 10
    remoteid: int = 10
    esp32: int = 5


class ErrorBudgetConfig(BaseModel):
    max_poll_errors_per_min: int = 5


class AlertThresholds(BaseModel):
    disk_free_min_bytes: int = 1_073_741_824
    cpu_temp_max_c: int = 80
    ups_soc_min_percent: int = 20


class ThresholdsConfig(BaseModel):
    stale_after_s: StaleThresholds = Field(default_factory=StaleThresholds)
    error_budget: ErrorBudgetConfig = Field(default_factory=ErrorBudgetConfig)
    alerts: AlertThresholds = Field(default_factory=AlertThresholds)


class AppConfig(BaseModel):
    service: ServiceConfig = Field(default_factory=ServiceConfig)
    auth: AuthConfig = Field(default_factory=AuthConfig)
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    polling: PollingConfig = Field(default_factory=PollingConfig)
    backend_aggregator: BackendAggregatorConfig = Field(default_factory=BackendAggregatorConfig)
    system_controller: SystemControllerConfig = Field(default_factory=SystemControllerConfig)
    jsonl: JsonlConfig = Field(default_factory=JsonlConfig)
    ws: WsConfig = Field(default_factory=WsConfig)
    thresholds: ThresholdsConfig = Field(default_factory=ThresholdsConfig)

    def sanitized(self) -> dict[str, Any]:
        data = self.model_dump()
        if data.get("auth"):
            data["auth"]["api_key"] = None if data["auth"].get("api_key") is None else "***"
        return data


def _parse_env_value(value: str) -> Any:
    try:
        return yaml.safe_load(value)
    except yaml.YAMLError:
        return value


def _set_nested(data: dict[str, Any], keys: list[str], value: Any) -> None:
    cur = data
    for key in keys[:-1]:
        if key not in cur or not isinstance(cur[key], dict):
            cur[key] = {}
        cur = cur[key]
    cur[keys[-1]] = value


def apply_env_overrides(data: dict[str, Any], prefix: str = "NDEFENDER_OBS_") -> dict[str, Any]:
    updated = copy.deepcopy(data)
    for key, value in os.environ.items():
        if not key.startswith(prefix):
            continue
        suffix = key[len(prefix) :]
        if not suffix:
            continue
        parts = [part.lower() for part in suffix.split("__") if part]
        if not parts:
            continue
        _set_nested(updated, parts, _parse_env_value(value))
    return updated


def load_config(path: str | Path | None = None) -> AppConfig:
    config_path = Path(path or os.getenv("NDEFENDER_OBS_CONFIG", "config/default.yaml"))
    data: dict[str, Any] = {}
    if config_path.exists():
        data = yaml.safe_load(config_path.read_text()) or {}
    else:
        if path is not None or "NDEFENDER_OBS_CONFIG" in os.environ:
            raise FileNotFoundError(f"Config file not found: {config_path}")
    data = apply_env_overrides(data)
    return AppConfig.model_validate(data)
