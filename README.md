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

## What This Catches
- Subsystem offline/stale (aggregator, system controller, AntSDR, RemoteID)
- JSONL tail lag + log growth anomalies
- Disk usage high (log partition pressure)
- CPU throttling flags
- UPS SOC/time-to-empty critical (if UPS metrics present)
- Polling error bursts + collector exceptions

## Viewing Alerts (Prometheus UI)
1. Open Prometheus UI and go to **Alerts** tab.
2. Ensure `alerts/prometheus/ndefender.rules.yml` is loaded.
3. Verify alerts are `FIRING` or `PENDING` with labels `{severity, subsystem, component}`.

## GUI Consumption (Health + Metrics + Diag)
- Use `/api/v1/health` for lightweight status badges.
- Use `/api/v1/health/detail` and `/api/v1/status` for detailed UI panels.
- Trigger `/api/v1/diag/bundle` for a support bundle (local-only).

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
