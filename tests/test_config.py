from pathlib import Path

from ndefender_observability.config import load_config


def test_default_config_exists() -> None:
    assert Path("config/default.yaml").exists()


def test_env_override_applies(tmp_path, monkeypatch) -> None:
    cfg_path = tmp_path / "cfg.yaml"
    cfg_path.write_text("service:\n  host: 0.0.0.0\n")
    monkeypatch.setenv("NDEFENDER_OBS_SERVICE__HOST", "127.0.0.1")
    cfg = load_config(cfg_path)
    assert cfg.service.host == "127.0.0.1"
