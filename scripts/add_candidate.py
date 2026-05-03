#!/usr/bin/env python3
"""Add a candidate to state/candidates.jsonl."""

from __future__ import annotations

import argparse

from utils import STATE_DIR, append_jsonl, next_id, now_iso, pretty


def main() -> None:
    p = argparse.ArgumentParser(description="Add a candidate.")
    p.add_argument("--name", required=True)
    p.add_argument("--url", required=True, help="primary url (site, github, twitter)")
    p.add_argument("--reason", required=True, help="why this person, in one line")
    p.add_argument("--type", default="person", help="e.g. person, org")
    p.add_argument("--source", default="", help="how you discovered them")
    args = p.parse_args()

    path = STATE_DIR / "candidates.jsonl"
    cid = next_id(path, "C", "candidate_id")
    record = {
        "candidate_id": cid,
        "name": args.name,
        "type": args.type,
        "url": args.url,
        "reason_added": args.reason,
        "discovery_source": args.source,
        "status": "active",
        "created_at": now_iso(),
    }
    append_jsonl(path, record)
    print(pretty(record))
    print(f"\nsaved -> {path}")


if __name__ == "__main__":
    main()
