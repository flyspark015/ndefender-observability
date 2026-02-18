# Health Model 🩺

The service exposes a deep health snapshot per subsystem.

## HealthState
- `OK`
- `DEGRADED`
- `OFFLINE`
- `REPLAY`

## Deep Health Fields
Each subsystem includes:
- `subsystem`
- `state`
- `updated_ts`
- `last_error`
- `last_response_ago_ms`
- `reasons[]`
- `evidence{}`

## Endpoints
- `GET /api/v1/health` basic liveness
- `GET /api/v1/health/detail` deep health snapshot
- `GET /api/v1/status` summarized snapshot
