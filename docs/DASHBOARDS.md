# Dashboards 🧭

Grafana dashboard template is provided at:
- `dashboards/grafana/ndefender-overview.json`

## Import
1. Open Grafana.
2. Import the JSON file.
3. Select your Prometheus datasource.

## Panels Included
- Subsystem up state
- Subsystem last update age
- Event rate (60s)
- JSONL tail lag
- CPU temperature
- Disk free
- UPS state of charge
