# Configuration Guide ⚙️

The observability service loads YAML config and supports env overrides. ✅

## Default File
- `config/default.yaml`
- Override with `NDEFENDER_OBS_CONFIG=/path/to/config.yaml`

## Auth
- `auth.enabled: true`
- `auth.api_key: "secret"`

Send the API key via:
- `x-api-key` header, or
- `?api_key=secret` query param.

## Rate Limit
- `rate_limit.enabled: true`
- `rate_limit.max_requests: 60`
- `rate_limit.window_s: 60`

## Env Overrides
Use `NDEFENDER_OBS_` + double-underscore path segments.

Examples:
- `NDEFENDER_OBS_SERVICE__HOST=127.0.0.1`
- `NDEFENDER_OBS_SYSTEM_CONTROLLER__BASE_URL=http://127.0.0.1:9000`
- `NDEFENDER_OBS_AUTH__API_KEY=secret`
- `NDEFENDER_OBS_RATE_LIMIT__ENABLED=true`

Values are parsed with YAML rules (numbers/bools supported). 🧩
