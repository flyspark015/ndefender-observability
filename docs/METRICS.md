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

## Raspberry Pi Stats
- `ndefender_pi_cpu_temp_c`
- `ndefender_pi_throttled_flags{flag}`
- `ndefender_pi_disk_free_bytes{mount}`
- `ndefender_pi_mem_available_bytes`
- `ndefender_pi_load1`
- `ndefender_pi_load5`
- `ndefender_pi_load15`
