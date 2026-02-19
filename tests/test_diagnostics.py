import tarfile
from pathlib import Path

from ndefender_observability.diagnostics import DiagnosticsOptions, create_bundle


def test_diag_bundle_manifest(tmp_path: Path) -> None:
    options = DiagnosticsOptions(output_dir=str(tmp_path))
    result = create_bundle(
        options,
        skip_http=True,
        skip_commands=True,
        skip_journal=True,
        skip_prometheus=True,
    )
    bundle = Path(result.path)
    assert bundle.exists()
    assert result.size_bytes > 0
    with tarfile.open(bundle, "r:gz") as tar:
        names = tar.getnames()
    assert "manifest.json" in names
