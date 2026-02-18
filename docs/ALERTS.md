# Alerts Pack 🧯

Prometheus alert rules are provided at:
- `alerts/prometheus/ndefender.rules.yml`

## Summary
- Subsystem down and stale detection
- JSONL tail lag warnings
- CPU temperature high
- Disk free low
- UPS SOC low
- Poll error surge

## Recommended Thresholds
- Subsystem stale: 30s
- JSONL lag: 15s
- CPU temp: 80C
- Disk free: 1GB
- UPS SOC: 20%
