"""Generate release notes from progress.md."""

from __future__ import annotations

from pathlib import Path


def main() -> int:
    progress = Path("progress.md").read_text(encoding="utf-8")
    lines = []
    lines.append("# v0.1.0 Observability (GREEN)")
    lines.append("")
    lines.append("## Highlights")
    lines.append("- Production observability service for N-Defender")
    lines.append("- Prometheus metrics + structured health endpoints")
    lines.append("- Collectors: aggregator, system controller (UPS), JSONL tails")
    lines.append("- Dashboards + alert rules")
    lines.append("")
    lines.append("## Verification Summary")
    for line in progress.splitlines():
        if line.startswith("- Step B") or line.startswith("- Step C"):
            lines.append(f"- {line[2:]}")
    lines.append("")
    lines.append("## Deployment")
    lines.append("- systemd unit: systemd/ndefender-observability.service")
    lines.append("- systemd docs: docs/DEPLOYMENT_SYSTEMD.md")
    lines.append("")
    notes = "\n".join(lines) + "\n"
    Path("/tmp/release_notes.md").write_text(notes, encoding="utf-8")
    print(notes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
