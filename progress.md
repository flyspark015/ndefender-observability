# Progress Tracker 🚦

Legend: ✅ completed | ⏳ in progress | ❌ pending

Completed ✅
- Step 1 — Bootstrap + CI + Minimal Service
- Step 2 — Config System + Versioning
- Step 3 — State Store + Health Model
- Step 4 — Raspberry Pi Stats Collector
- Step 5 — Backend Aggregator Collector
- Step 6 — System Controller + UPS Collector
- Step 7 — JSONL Tail Collectors
- Step 8 — Dashboards + Alerts Pack
- Step 9 — Ops Tools + Hardening
- Step 10 — GREEN Release Lock

In Progress ⏳
- None

Pending ❌
- None

## Deployment Progress 🚀

Legend: ✅ completed | ⏳ in progress | ❌ pending

Completed ✅
- Step A — systemd Unit + Runtime Verification

In Progress ⏳
- None

Pending ❌
- Step B — Live Integration Sanity
- Step C — Prometheus + Grafana Quickstart
- Step D — GitHub Release Object

## Step B — Live Integration Sanity ✅

Config keys set:
- backend_aggregator.base_url = http://127.0.0.1:8000
- system_controller.base_url = http://127.0.0.1:9000
- jsonl.antsdr_path = /opt/ndefender/logs/antsdr_scan.jsonl
- jsonl.remoteid_path = /opt/ndefender/logs/remoteid_engine.jsonl
- polling intervals = 2s-5s (default)

Commands run:
- sudo systemctl restart ndefender-observability
- sudo journalctl -u ndefender-observability -n 80 --no-pager
- python3 - <<'PY' ... (2-minute sampler) > /tmp/obs_stepB.txt
- curl -sS http://127.0.0.1:9109/metrics | rg '^ndefender_jsonl_'
- curl -sS http://127.0.0.1:8000/api/v1/status | head -n 3
- sudo systemctl stop ndefender-backend || true
- sleep 15 && curl -sS http://127.0.0.1:9109/metrics | rg 'subsystem_up.*aggregator'
- sudo systemctl start ndefender-backend || true

Journal snippet:
- Feb 18 19:12:55 ndefender-pi uvicorn[66862]: INFO:     Started server process [66862]
- Feb 18 19:12:55 ndefender-pi uvicorn[66862]: INFO:     Waiting for application startup.
- Feb 18 19:12:55 ndefender-pi uvicorn[66862]: INFO:     Application startup complete.
- Feb 18 19:12:55 ndefender-pi uvicorn[66862]: INFO:     Uvicorn running on http://0.0.0.0:9109 (Press CTRL+C to quit)

Sampler proof (/tmp/obs_stepB.txt):
- ndefender_subsystem_up{subsystem="aggregator"} 1.0
- ndefender_subsystem_up{subsystem="antsdr"} 1.0
- ndefender_subsystem_up{subsystem="remoteid"} 1.0
- ndefender_jsonl_tail_lag_seconds{subsystem="antsdr"} 0.12
- ndefender_jsonl_file_size_bytes{subsystem="remoteid"} 4.050262e+06
- ndefender_events_total{subsystem="antsdr",type="RF_CONTACT_UPDATE"} 6764.0

Offline truthfulness proof:
- ndefender_subsystem_up{subsystem="aggregator"} 0.0
