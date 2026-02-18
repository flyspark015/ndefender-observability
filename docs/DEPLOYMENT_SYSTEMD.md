# systemd Deployment 🚀

This service is designed for Raspberry Pi 5 (Debian 12).

## Install Unit
```bash
sudo cp /home/toybook/ndefender-observability/systemd/ndefender-observability.service \
  /etc/systemd/system/ndefender-observability.service
```

## Optional Environment Overrides
Create `/etc/default/ndefender-observability` to override config values:

```bash
NDEFENDER_OBS_CONFIG=/home/toybook/ndefender-observability/config/default.yaml
# NDEFENDER_OBS_AUTH__ENABLED=true
# NDEFENDER_OBS_AUTH__API_KEY=change-me
# NDEFENDER_OBS_RATE_LIMIT__ENABLED=true
```

## Enable + Start
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now ndefender-observability
```

## Verify
```bash
systemctl status ndefender-observability --no-pager
curl -sS http://127.0.0.1:9109/api/v1/health | jq .
curl -sS http://127.0.0.1:9109/metrics | head -n 40
```
