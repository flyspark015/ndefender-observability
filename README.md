# N-Defender Observability & Metrics Layer

Production observability layer for N-Defender deployments on Raspberry Pi 5. 📡📊

## Highlights
- Prometheus `/metrics` endpoint ✅
- Structured health endpoints for UI/debug 🩺
- Collectors for subsystems + JSONL tail monitoring 🧾
- Alert rules + Grafana dashboards 🧭

## Quickstart
1. Create a virtual env and install deps.
2. Run the API server.

```bash
uvicorn ndefender_observability.main:app --host 0.0.0.0 --port 9109
```

Then visit:
- `http://localhost:9109/api/v1/health`
- `http://localhost:9109/metrics`

## Status
- See `progress.md` for current step status. 🚦
