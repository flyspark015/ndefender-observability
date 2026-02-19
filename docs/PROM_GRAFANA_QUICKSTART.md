# Prometheus + Grafana Quickstart 📈

## Prometheus (local)
Install on Debian/Raspberry Pi:
```bash
sudo apt-get update
sudo apt-get install -y prometheus
```

Minimal config to scrape observability:
```yaml
global:
  scrape_interval: 5s

scrape_configs:
  - job_name: ndefender-observability
    static_configs:
      - targets: ['127.0.0.1:9109']
```

Apply config:
```bash
sudo cp /path/to/prometheus.yml /etc/prometheus/prometheus.yml
promtool check config /etc/prometheus/prometheus.yml
sudo systemctl restart prometheus
```

Verify:
```bash
curl -sS http://127.0.0.1:9090/metrics | head -n 5
```

## Grafana
Grafana is not installed by default on this Pi. Recommended options:
- Install from official Grafana repo, or
- Use Docker on a separate host.

Once Grafana is available:
1. Add Prometheus datasource (URL: `http://<pi-ip>:9090`).
2. Import `dashboards/grafana/ndefender-overview.json`.
3. Set datasource to Prometheus.
