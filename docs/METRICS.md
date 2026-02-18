# Metrics Reference 📊

Core metrics live under the `ndefender_` namespace.

## Service
- `ndefender_observability_up`
- `ndefender_observability_build_info{version,git_sha}`
- `ndefender_observability_poll_errors_total{subsystem,kind}`
- `ndefender_observability_poll_latency_seconds_bucket{subsystem,endpoint}`

## Subsystem Health
- `ndefender_subsystem_up{subsystem}`
- `ndefender_subsystem_last_update_age_seconds{subsystem}`
- `ndefender_subsystem_state{subsystem,state}`
- `ndefender_aggregator_up`

## JSONL Tails
- `ndefender_events_total{subsystem,type}`
- `ndefender_events_rate_60s{subsystem,type}`
- `ndefender_jsonl_tail_lag_seconds{subsystem}`
- `ndefender_jsonl_file_size_bytes{subsystem}`

## Raspberry Pi Stats
- `ndefender_pi_cpu_temp_c`
- `ndefender_pi_throttled_flags{flag}`
- `ndefender_pi_disk_free_bytes{mount}`
- `ndefender_pi_mem_available_bytes`
- `ndefender_pi_load1`
- `ndefender_pi_load5`
- `ndefender_pi_load15`

## UPS
- `ndefender_ups_pack_voltage_v`
- `ndefender_ups_current_a`
- `ndefender_ups_input_vbus_v`
- `ndefender_ups_input_power_w`
- `ndefender_ups_soc_percent`
- `ndefender_ups_time_to_empty_s`
- `ndefender_ups_time_to_full_s`
- `ndefender_ups_cell_voltage_v{cell}`
- `ndefender_ups_state{state}`
