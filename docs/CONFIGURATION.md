# Configuration Guide ⚙️

The observability service loads YAML config and supports env overrides. ✅

## Default File
- `config/default.yaml`
- Override with `NDEFENDER_OBS_CONFIG=/path/to/config.yaml`

## Env Overrides
Use `NDEFENDER_OBS_` + double-underscore path segments.

Examples:
- `NDEFENDER_OBS_SERVICE__HOST=127.0.0.1`
- `NDEFENDER_OBS_SYSTEM_CONTROLLER__BASE_URL=http://127.0.0.1:9000`
- `NDEFENDER_OBS_AUTH__API_KEY=secret`

Values are parsed with YAML rules (numbers/bools supported). 🧩
