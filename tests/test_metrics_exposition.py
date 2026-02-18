from fastapi.testclient import TestClient

from ndefender_observability.main import app


def test_metrics_contains_core_metrics() -> None:
    client = TestClient(app)
    resp = client.get("/metrics")
    assert resp.status_code == 200
    text = resp.text
    assert "ndefender_observability_up" in text
    assert "ndefender_observability_build_info" in text
