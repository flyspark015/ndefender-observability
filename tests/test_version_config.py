from fastapi.testclient import TestClient

from ndefender_observability.main import app
from ndefender_observability.version import GIT_SHA, VERSION


def test_version_endpoint() -> None:
    with TestClient(app) as client:
        resp = client.get("/api/v1/version")
        assert resp.status_code == 200
        assert resp.json() == {"version": VERSION, "git_sha": GIT_SHA}


def test_config_sanitized(monkeypatch) -> None:
    monkeypatch.setenv("NDEFENDER_OBS_AUTH__API_KEY", "super-secret")
    with TestClient(app) as client:
        resp = client.get("/api/v1/config")
        assert resp.status_code == 200
        data = resp.json()
        assert data["auth"]["api_key"] == "***"
