"""Dev client for inspecting health and metrics."""

from __future__ import annotations

import argparse

import httpx


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://127.0.0.1:9109")
    parser.add_argument("--api-key", default=None)
    args = parser.parse_args()

    headers = {}
    if args.api_key:
        headers["x-api-key"] = args.api_key

    with httpx.Client(
        base_url=args.base,
        headers=headers,
        timeout=5,
        limits=httpx.Limits(max_keepalive_connections=1, max_connections=2),
    ) as client:
        health = client.get("/api/v1/health/detail")
        health.raise_for_status()
        status = client.get("/api/v1/status")
        status.raise_for_status()
        metrics = client.get("/metrics")
        metrics.raise_for_status()

    print("health/detail:")
    print(health.text)
    print("\nstatus:")
    print(status.text)
    print("\nmetrics sample:")
    print("\n".join(metrics.text.splitlines()[:20]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
