# Runbooks 📒

Runbooks for every Prometheus alert. All commands are Raspberry Pi compatible.

---

## NdefenderSubsystemDown
**What it means**: A subsystem is not reporting (`ndefender_subsystem_up == 0`).

**Why it happens**:
- Service is stopped or crashed.
- Network endpoint unreachable.
- JSONL log missing for file-based subsystems.

**Confirm**:
```bash
curl -sS http://127.0.0.1:9109/metrics | rg 'subsystem_up'
```
Check service status:
```bash
sudo systemctl status ndefender-observability --no-pager
sudo systemctl status ndefender-backend --no-pager || true
sudo systemctl status ndefender-system-controller --no-pager || true
```

**Fast mitigation**:
- Restart the subsystem service.
- Verify endpoints in `config/default.yaml`.

**Root-cause steps**:
- Inspect logs:
```bash
journalctl -u ndefender-observability -n 200 --no-pager
journalctl -u ndefender-backend -n 200 --no-pager || true
journalctl -u ndefender-system-controller -n 200 --no-pager || true
```

**When to escalate**:
- Repeated crashes after restart or persistent network failures.

---

## NdefenderSubsystemStale
**What it means**: Last update age exceeded 30s.

**Why it happens**:
- Subsystem alive but not producing updates.
- JSONL logs not being written.

**Confirm**:
```bash
curl -sS http://127.0.0.1:9109/metrics | rg 'last_update_age_seconds'
```

**Fast mitigation**:
- Restart subsystem or log producer.

**Root-cause steps**:
- Check JSONL write activity:
```bash
ls -lah /opt/ndefender/logs/*.jsonl
```

**When to escalate**:
- Stale condition persists after restart.

---

## NdefenderJsonlLagHigh
**What it means**: JSONL tail lag > 30s.

**Why it happens**:
- Log writer slowed or stopped.
- Storage bottlenecks.

**Confirm**:
```bash
curl -sS http://127.0.0.1:9109/metrics | rg 'jsonl_tail_lag_seconds'
```

**Fast mitigation**:
- Restart log producer (AntSDR/RemoteID engine).

**Root-cause steps**:
- Verify disk IO and free space:
```bash
df -h /
```

**When to escalate**:
- Lag grows continuously or repeats after restart.

---

## NdefenderJsonlLogStalled
**What it means**: JSONL tail lag > 120s (critical).

**Why it happens**:
- Log writer stopped.
- File permission or disk full.

**Confirm**:
```bash
curl -sS http://127.0.0.1:9109/metrics | rg 'jsonl_tail_lag_seconds'
```

**Fast mitigation**:
- Restart the producing service.

**Root-cause steps**:
- Inspect log file permissions and size:
```bash
ls -lah /opt/ndefender/logs/antsdr_scan.jsonl /opt/ndefender/logs/remoteid_engine.jsonl
```

**When to escalate**:
- Files are not updating after restart.

---

## NdefenderDiskLow
**What it means**: Disk free below 1GB.

**Why it happens**:
- Logs or captures growing without rotation.

**Confirm**:
```bash
df -h /
```

**Fast mitigation**:
- Rotate or archive logs in `/opt/ndefender/logs`.

**Root-cause steps**:
- Find large files:
```bash
du -sh /opt/ndefender/logs
```

**When to escalate**:
- Disk usage continues to grow rapidly.

---

## NdefenderCpuThrottling
**What it means**: CPU throttling flags active.

**Why it happens**:
- Power undervoltage or thermal limits.

**Confirm**:
```bash
vcgencmd get_throttled || true
curl -sS http://127.0.0.1:9109/metrics | rg 'pi_throttled_flags'
```

**Fast mitigation**:
- Verify power supply and cooling.

**Root-cause steps**:
- Check CPU temp:
```bash
vcgencmd measure_temp || true
```

**When to escalate**:
- Persistent throttling despite correct power/cooling.

---

## NdefenderPiCpuHot
**What it means**: CPU temperature > 80C.

**Why it happens**:
- Insufficient cooling, high CPU load.

**Confirm**:
```bash
vcgencmd measure_temp || true
curl -sS http://127.0.0.1:9109/metrics | rg 'pi_cpu_temp_c'
```

**Fast mitigation**:
- Improve airflow or lower workload.

**Root-cause steps**:
- Check running processes:
```bash
ps aux --sort=-%cpu | head -n 10
```

**When to escalate**:
- Sustained high temperature with no obvious load.

---

## NdefenderUpsCriticalLow
**What it means**: UPS SOC < 10%.

**Why it happens**:
- Power loss with low battery.

**Confirm**:
```bash
curl -sS http://127.0.0.1:9109/metrics | rg 'ups_soc_percent'
```

**Fast mitigation**:
- Restore external power immediately.

**Root-cause steps**:
- Confirm UPS health and charging:
```bash
curl -sS http://127.0.0.1:9000/api/v1/ups | head -n 5 || true
```

**When to escalate**:
- UPS not charging or SOC not recovering.

---

## NdefenderUpsLow
**What it means**: UPS SOC < 20%.

**Why it happens**:
- Running on battery longer than expected.

**Confirm**:
```bash
curl -sS http://127.0.0.1:9109/metrics | rg 'ups_soc_percent'
```

**Fast mitigation**:
- Restore external power.

**Root-cause steps**:
- Check time-to-empty:
```bash
curl -sS http://127.0.0.1:9109/metrics | rg 'ups_time_to_empty_s'
```

**When to escalate**:
- SOC drops rapidly under normal load.

---

## NdefenderUpsTimeToEmptyLow
**What it means**: UPS time-to-empty < 15 minutes.

**Why it happens**:
- Load spike or degraded battery.

**Confirm**:
```bash
curl -sS http://127.0.0.1:9109/metrics | rg 'ups_time_to_empty_s'
```

**Fast mitigation**:
- Reduce load, restore external power.

**Root-cause steps**:
- Verify UPS voltage and current:
```bash
curl -sS http://127.0.0.1:9109/metrics | rg 'ups_(pack_voltage_v|current_a)'
```

**When to escalate**:
- Time-to-empty remains low with stable load.

---

## NdefenderPollErrorsHigh
**What it means**: Poll errors > 10 in 5 minutes.

**Why it happens**:
- Unreachable subsystem endpoint or timeouts.

**Confirm**:
```bash
curl -sS http://127.0.0.1:9109/metrics | rg 'poll_errors_total'
```

**Fast mitigation**:
- Restart affected subsystem.

**Root-cause steps**:
- Validate endpoint reachability:
```bash
curl -sS http://127.0.0.1:8000/api/v1/status | head -n 3 || true
curl -sS http://127.0.0.1:9000/api/v1/status | head -n 3 || true
```

**When to escalate**:
- Errors persist after endpoint recovery.

---

## NdefenderPollLatencyHigh
**What it means**: p95 poll latency > 1s.

**Why it happens**:
- Subsystem is slow or overloaded.

**Confirm**:
```bash
curl -sS http://127.0.0.1:9109/metrics | rg 'poll_latency_seconds'
```

**Fast mitigation**:
- Reduce subsystem load or restart.

**Root-cause steps**:
- Check CPU load and IO.

**When to escalate**:
- Persistent high latency with no load issues.

