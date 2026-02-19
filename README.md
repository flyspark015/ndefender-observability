# N-Defender Observability & Metrics Layer

Production observability layer for N-Defender deployments on Raspberry Pi 5. 📡📊

## Highlights
- Prometheus `/metrics` endpoint ✅
- Structured health endpoints for UI/debug 🩺
- Collectors for subsystems + JSONL tail monitoring 🧾
- Alert rules + Grafana dashboards 🧭
- Optional API auth + rate limit 🔐

## Phase 2.1 Goals
- Production-grade alert rules (no outbound notifications)
- Runbooks for every alert
- Diagnostics bundle generator + API endpoint
- Golden-signal metrics expansion

## Quickstart
1. Create a virtual env and install deps.
2. Run the API server.

```bash
uvicorn ndefender_observability.main:app --host 0.0.0.0 --port 9109
```

Then visit:
- `http://localhost:9109/api/v1/health`
- `http://localhost:9109/metrics`

## Tools
- `tools/smoke_metrics.py` checks the `/metrics` endpoint.
- `tools/dev_client.py` prints deep health and a metrics sample.

## Docs
- `docs/METRICS.md`
- `docs/HEALTH_MODEL.md`
- `docs/DASHBOARDS.md`
- `docs/ALERTS.md`
- `docs/RUNBOOKS.md`
- `docs/DIAGNOSTICS.md`
- `docs/OPERATIONS.md`
- `docs/CONFIGURATION.md`

## Status
- See `progress.md` for current step status. 🚦
