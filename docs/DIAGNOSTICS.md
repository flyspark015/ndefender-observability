# Diagnostics Bundle 🧰

Generates a local support bundle with health, status, logs, and system context.

## CLI Tool
```bash
python3 tools/diag_bundle.py
```

Options:
- `--output-dir /tmp`
- `--base-url http://127.0.0.1:9109`
- `--api-key <key>` (if auth enabled)
- `--skip-journal` / `--skip-commands` / `--skip-http`

## API Endpoint
- `POST /api/v1/diag/bundle`
- Local-only (127.0.0.1 / ::1)
- Cooldown: 60s

Response:
```json
{"path": "/tmp/ndefender_diag_<ts>.tar.gz", "size_bytes": 12345, "created_ts": 1234567890}
```

## Bundle Contents
- `/api/v1/health`, `/api/v1/health/detail`, `/api/v1/status`
- Sanitized config (`/api/v1/config`)
- `/metrics` + extracted JSONL metrics
- journalctl tail (observability + related services)
- `df -h`, `du -sh /opt/ndefender/logs`
- process list + filtered list
- Prometheus targets (if reachable)

## Safety
- Secrets stripped from config
- Max bundle size enforced (default 50MB)
