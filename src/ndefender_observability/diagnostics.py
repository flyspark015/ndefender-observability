"""Diagnostics bundle generation."""

from __future__ import annotations

import json
import socket
import tarfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx


@dataclass
class DiagnosticsOptions:
    base_url: str = "http://127.0.0.1:9109"
    api_key: str | None = None
    output_dir: str = "/tmp"
    journal_lines: int = 200
    max_bundle_bytes: int = 50 * 1024 * 1024
    prometheus_url: str = "http://127.0.0.1:9090"


@dataclass
class DiagnosticsResult:
    path: str
    size_bytes: int
    created_ts: int
    errors: list[str]


def create_bundle(
    options: DiagnosticsOptions,
    *,
    skip_http: bool = False,
    skip_commands: bool = False,
    skip_journal: bool = False,
    skip_prometheus: bool = False,
) -> DiagnosticsResult:
    created_ts = int(time.time() * 1000)
    bundle_dir = Path(options.output_dir) / f"ndefender_diag_{created_ts}"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []

    headers = {}
    if options.api_key:
        headers["x-api-key"] = options.api_key

    if not skip_http:
        _write_json(
            bundle_dir / "health.json",
            _safe_get_json(f"{options.base_url}/api/v1/health", headers, errors),
        )
        _write_json(
            bundle_dir / "health_detail.json",
            _safe_get_json(f"{options.base_url}/api/v1/health/detail", headers, errors),
        )
        _write_json(
            bundle_dir / "status.json",
            _safe_get_json(f"{options.base_url}/api/v1/status", headers, errors),
        )
        config_data = _safe_get_json(f"{options.base_url}/api/v1/config", headers, errors)
        _write_json(bundle_dir / "config.json", _sanitize_config(config_data))
        metrics_text = _safe_get_text(f"{options.base_url}/metrics", headers, errors)
        if metrics_text is not None:
            _write_text(bundle_dir / "metrics.txt", metrics_text)
            _write_json(
                bundle_dir / "metrics_extract.json",
                _extract_metrics(metrics_text),
            )
    else:
        _write_text(bundle_dir / "health.json", "skipped")
        _write_text(bundle_dir / "health_detail.json", "skipped")
        _write_text(bundle_dir / "status.json", "skipped")
        _write_text(bundle_dir / "config.json", "skipped")
        _write_text(bundle_dir / "metrics.txt", "skipped")

    if not skip_commands:
        _write_text(bundle_dir / "df.txt", _run_cmd(["df", "-h"], errors))
        _write_text(
            bundle_dir / "logs_usage.txt",
            _run_cmd(["du", "-sh", "/opt/ndefender/logs"], errors),
        )
        _write_text(bundle_dir / "ps_aux.txt", _run_cmd(["ps", "aux"], errors))
        _write_text(
            bundle_dir / "ps_filtered.txt",
            _filter_processes(bundle_dir / "ps_aux.txt"),
        )
    else:
        _write_text(bundle_dir / "df.txt", "skipped")
        _write_text(bundle_dir / "logs_usage.txt", "skipped")
        _write_text(bundle_dir / "ps_aux.txt", "skipped")

    if not skip_journal:
        _write_text(
            bundle_dir / "journal_observability.txt",
            _run_cmd(
                [
                    "journalctl",
                    "-u",
                    "ndefender-observability",
                    "-n",
                    str(options.journal_lines),
                    "--no-pager",
                ],
                errors,
            ),
        )
        for unit in [
            "ndefender-backend",
            "ndefender-system-controller",
            "ndefender-remoteid-engine",
            "ndefender-antsdr-scan",
            "antsdr-scan",
        ]:
            _write_text(
                bundle_dir / f"journal_{unit}.txt",
                _run_cmd(
                    ["journalctl", "-u", unit, "-n", str(options.journal_lines), "--no-pager"],
                    errors,
                ),
            )
    else:
        _write_text(bundle_dir / "journal_observability.txt", "skipped")

    if skip_prometheus:
        _write_json(bundle_dir / "prometheus_targets.json", {"status": "skipped"})
    else:
        prom_targets = _safe_get_json(f"{options.prometheus_url}/api/v1/targets", {}, errors)
        _write_json(bundle_dir / "prometheus_targets.json", prom_targets)

    manifest = {
        "created_ts": created_ts,
        "hostname": socket.gethostname(),
        "bundle_dir": str(bundle_dir),
        "files": [p.name for p in bundle_dir.iterdir() if p.is_file()],
        "errors": errors,
    }
    _write_json(bundle_dir / "manifest.json", manifest)

    bundle_path = Path(options.output_dir) / f"ndefender_diag_{created_ts}.tar.gz"
    with tarfile.open(bundle_path, "w:gz") as tar:
        for item in bundle_dir.iterdir():
            tar.add(item, arcname=item.name)

    size_bytes = bundle_path.stat().st_size
    if size_bytes > options.max_bundle_bytes:
        bundle_path.unlink(missing_ok=True)
        raise RuntimeError("diagnostics bundle exceeds size limit")

    return DiagnosticsResult(
        path=str(bundle_path),
        size_bytes=size_bytes,
        created_ts=created_ts,
        errors=errors,
    )


def _safe_get_json(url: str, headers: dict[str, str], errors: list[str]) -> dict[str, Any]:
    try:
        resp = httpx.get(url, headers=headers, timeout=2)
        resp.raise_for_status()
        data = resp.json()
        return data if isinstance(data, dict) else {"value": data}
    except Exception as exc:
        errors.append(f"http_json_failed:{url}:{exc}")
        return {"error": str(exc)}


def _safe_get_text(url: str, headers: dict[str, str], errors: list[str]) -> str | None:
    try:
        resp = httpx.get(url, headers=headers, timeout=2)
        resp.raise_for_status()
        return resp.text
    except Exception as exc:
        errors.append(f"http_text_failed:{url}:{exc}")
        return None


def _run_cmd(cmd: list[str], errors: list[str]) -> str:
    import subprocess

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except Exception as exc:
        errors.append(f"cmd_failed:{' '.join(cmd)}:{exc}")
        return str(exc)


def _sanitize_config(data: dict[str, Any]) -> dict[str, Any]:
    data = json.loads(json.dumps(data)) if data else {}
    auth = data.get("auth")
    if isinstance(auth, dict) and "api_key" in auth:
        auth["api_key"] = "***" if auth["api_key"] else None
    return data


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _filter_processes(ps_path: Path) -> str:
    keywords = ("ndefender", "antsdr", "remoteid", "prometheus")
    lines = ps_path.read_text(encoding="utf-8").splitlines()
    filtered = [line for line in lines if any(key in line.lower() for key in keywords)]
    return "\n".join(filtered)


def _extract_metrics(text: str) -> dict[str, Any]:
    lag = []
    sizes = []
    for line in text.splitlines():
        if line.startswith("ndefender_jsonl_tail_lag_seconds"):
            lag.append(line)
        if line.startswith("ndefender_jsonl_file_size_bytes"):
            sizes.append(line)
    return {"jsonl_tail_lag": lag, "jsonl_file_size": sizes}
