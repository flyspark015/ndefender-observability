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
        assert "ndefender_pi_mem_available_bytes" in text
