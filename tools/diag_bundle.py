"""Generate a diagnostics bundle on demand."""

from __future__ import annotations

import argparse

from ndefender_observability.diagnostics import DiagnosticsOptions, create_bundle


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="/tmp")
    parser.add_argument("--base-url", default="http://127.0.0.1:9109")
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--max-bytes", type=int, default=50 * 1024 * 1024)
    parser.add_argument("--skip-journal", action="store_true")
    parser.add_argument("--skip-commands", action="store_true")
    parser.add_argument("--skip-http", action="store_true")
    args = parser.parse_args()

    opts = DiagnosticsOptions(
        base_url=args.base_url,
        api_key=args.api_key,
        output_dir=args.output_dir,
        max_bundle_bytes=args.max_bytes,
    )
    result = create_bundle(
        opts,
        skip_http=args.skip_http,
        skip_commands=args.skip_commands,
        skip_journal=args.skip_journal,
    )
    print(f"bundle={result.path}")
    print(f"size_bytes={result.size_bytes}")
    print(f"created_ts={result.created_ts}")
    if result.errors:
        print("errors:")
        for err in result.errors:
            print(f"- {err}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
