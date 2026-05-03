#!/usr/bin/env python3
"""Mark a user proxy bundle as user-approved."""

from __future__ import annotations

import argparse

from utils import STATE_DIR, find_by_id, now_iso, pretty, update_jsonl


def main() -> None:
    p = argparse.ArgumentParser(description="Approve a user proxy bundle.")
    p.add_argument("--id", required=True, help="user_proxy_bundle_id, e.g. UPB001")
    args = p.parse_args()

    path = STATE_DIR / "user_proxy_bundles.jsonl"
    existing = find_by_id(path, "user_proxy_bundle_id", args.id)
    if not existing:
        raise SystemExit(f"{args.id} not found in {path}")

    updated = update_jsonl(
        path,
        "user_proxy_bundle_id",
        args.id,
        {"user_approved": True, "approved_at": now_iso()},
    )
    print(pretty(updated))
    print(f"\napproved {args.id}")


if __name__ == "__main__":
    main()
