from fastapi.testclient import TestClient

from ndefender_observability.health.model import HealthState
from ndefender_observability.main import app


def test_health_endpoint_ok() -> None:
    with TestClient(app) as client:
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


def test_health_detail_schema() -> None:
    with TestClient(app) as client:
        resp = client.get("/api/v1/health/detail")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        subsystems = data["subsystems"]
        assert len(subsystems) == 5
        for item in subsystems:
            required = {
                "subsystem",
                "state",
                "updated_ts",
                "last_error",
                "last_error_ts",
                "last_response_ago_ms",
                "reasons",
                "evidence",
            }
            assert required <= set(item.keys())
            assert item["state"] in {state.value for state in HealthState}


def test_status_snapshot() -> None:
    with TestClient(app) as client:
        resp = client.get("/api/v1/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "overall_state" in data
        assert len(data["subsystems"]) == 5
