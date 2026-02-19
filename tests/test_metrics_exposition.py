from fastapi.testclient import TestClient

from ndefender_observability.main import app


def test_metrics_contains_core_metrics() -> None:
    with TestClient(app) as client:
        resp = client.get("/metrics")
        assert resp.status_code == 200
        text = resp.text
        assert "ndefender_observability_up" in text
        assert "ndefender_observability_build_info" in text
        assert "ndefender_pi_cpu_temp_c" in text
        assert "ndefender_pi_disk_free_bytes" in text
        assert "ndefender_pi_disk_used_percent" in text
        assert "ndefender_pi_mem_available_bytes" in text
        assert "ndefender_jsonl_last_event_ts" in text
        assert "ndefender_jsonl_file_bytes_delta_5m" in text
        assert "ndefender_subsystem_last_success_ts" in text
        assert "ndefender_subsystem_last_error_ts" in text
        assert "ndefender_collector_exceptions_total" in text
