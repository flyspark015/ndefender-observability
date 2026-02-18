"""Simple smoke test for /metrics endpoint."""

import argparse

import httpx


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:9109/metrics")
    args = parser.parse_args()

    resp = httpx.get(args.url, timeout=5)
    resp.raise_for_status()

    text = resp.text
    required = [
        "ndefender_observability_up",
        "ndefender_observability_build_info",
    ]
    missing = [name for name in required if name not in text]
    if missing:
        print(f"missing metrics: {missing}")
        return 2

    print("metrics ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
