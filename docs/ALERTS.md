# Alerts Pack 🧯

No external notifications are used. Alerts are visible in Prometheus UI and API only.

## Where Alerts Live
- Rules: `alerts/prometheus/ndefender.rules.yml`
- Prometheus UI: `http://<pi-ip>:9090/alerts`
- Prometheus API: `/api/v1/alerts`

## Alert Summary
- `NdefenderSubsystemDown` (critical) — subsystem not reporting
- `NdefenderSubsystemStale` (warning) — stale updates > 30s
- `NdefenderJsonlLagHigh` (warning) — JSONL tail lag > 30s
- `NdefenderJsonlLogStalled` (critical) — JSONL tail lag > 120s
- `NdefenderDiskLow` (warning) — disk free below 1GB
- `NdefenderCpuThrottling` (critical) — throttling flags active
- `NdefenderPiCpuHot` (warning) — CPU temp > 80C
- `NdefenderUpsLow` (warning) — UPS SOC < 20%
- `NdefenderUpsCriticalLow` (critical) — UPS SOC < 10%
- `NdefenderUpsTimeToEmptyLow` (warning) — UPS time-to-empty < 15m
- `NdefenderPollErrorsHigh` (warning) — poll errors > 10 / 5m
- `NdefenderPollLatencyHigh` (warning) — p95 poll latency > 1s

## Labels
All alerts include:
- `severity` (info/warning/critical)
- `component` (subsystem/pi/jsonl/ups/collector)
- `subsystem` label where relevant
