# Operations Notes 🛠️

## System Controller + UPS
- UPS metrics are pulled from the System Controller `GET /api/v1/ups` endpoint.
- If any System Controller endpoint is unavailable, the subsystem health degrades gracefully.
- UPS state labels are normalized to: `IDLE`, `CHARGING`, `FAST_CHARGING`, `DISCHARGING`, `UNKNOWN`.
