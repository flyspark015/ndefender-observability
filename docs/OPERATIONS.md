# Operations Notes 🛠️

## Running
```bash
uvicorn ndefender_observability.main:app --host 0.0.0.0 --port 9109
```

## System Controller + UPS
- UPS metrics are pulled from the System Controller `GET /api/v1/ups` endpoint.
- If any System Controller endpoint is unavailable, the subsystem health degrades gracefully.
- UPS state labels are normalized to: `IDLE`, `CHARGING`, `FAST_CHARGING`, `DISCHARGING`, `UNKNOWN`.

## Auth + Rate Limiting
- Optional API key is supported via `x-api-key` header or `api_key` query parameter.
- Rate limit can be enabled with `rate_limit.enabled` in config.
- For local dev, keep auth and rate limit disabled (default).

## Collector Control
- For local smoke tests, disable background collectors via:
  - `NDEFENDER_OBS_DISABLE_COLLECTORS=1`
