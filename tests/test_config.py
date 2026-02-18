from pathlib import Path


def test_default_config_exists() -> None:
    assert Path("config/default.yaml").exists()
