# N-Defender Observability Roadmap

## Phase 1: Bootstrap + CI + Minimal Service
- Steps
- Create repo structure, pyproject, ruff/pytest, CI workflow
- FastAPI app with `/api/v1/health` and `/metrics`
- Add `tools/smoke_metrics.py`
- Acceptance criteria
- `ruff check .` passes
- `pytest` passes
- `uvicorn` runs and `/metrics` responds

## Phase 2: Config + Versioning
- Steps
- YAML config loader with env overrides
- `/api/v1/version` and `/api/v1/config` (sanitized)
- Acceptance criteria
- Unit tests green

## Phase 3: State Store + Health Model
- Steps
- Implement `HealthState` enum + DeepHealth schema
- `/api/v1/health/detail` and `/api/v1/status`
- Acceptance criteria
- Tests validate health model

## Phase 4: Raspberry Pi Stats Collector
- Steps
- psutil + `vcgencmd` for throttling + temperature
- Export required metrics
- Acceptance criteria
- `/metrics` includes Pi stats

## Phase 5: Backend Aggregator Collector
- Steps
- Poll `/health` + `/status`
- Latency histograms + freshness age + subsystem state
- Acceptance criteria
- Mocked tests green, optional live probe documented

## Phase 6: System Controller + UPS Collector
- Steps
- Poll `/ups` and export UPS metrics
- Document keepalive awareness
- Acceptance criteria
- Mocked tests green, optional live probe documented

## Phase 7: JSONL Tail Collectors
- Steps
- Rotation-safe tail + last event age + rate calc
- AntSDR + RemoteID
- Acceptance criteria
- Unit tests with temp files green

## Phase 8: Dashboards + Alerts
- Steps
- Grafana overview dashboard JSON
- Prometheus alert rules YAML
- Docs for setup
- Acceptance criteria
- Dashboard JSON valid, docs complete

## Phase 9: Ops Tools + Hardening
- Steps
- `dev_client.py` for deep health + metrics sample
- Optional auth + rate limit
- Acceptance criteria
- Tools verified locally

## Phase 10: GREEN Release Lock
- Steps
- Documentation audit
- Tag `v0.1.0-observability-green`
- Acceptance criteria
- ROADMAP done, progress GREEN
