#!/usr/bin/env python3
"""Register a new input source in state/input_sources.jsonl."""

from __future__ import annotations

import argparse

from utils import STATE_DIR, append_jsonl, next_id, now_iso, pretty


def main() -> None:
    p = argparse.ArgumentParser(description="Add a new input source.")
    p.add_argument("--type", required=True, help="e.g. notes, transcript, doc, url")
    p.add_argument("--name", required=True)
    p.add_argument("--file", help="path (relative to project root) to source file")
    p.add_argument("--url", help="url for the source")
    p.add_argument("--notes", default="")
    p.add_argument("--include", action="store_true", help="include by default in proxy bundle generation (default true)")
    args = p.parse_args()

    if not args.file and not args.url:
        p.error("must supply --file or --url")

    path = STATE_DIR / "input_sources.jsonl"
    sid = next_id(path, "S", "source_id")
    record = {
        "source_id": sid,
        "type": args.type,
        "name": args.name,
        "file": args.file,
        "url": args.url,
        "notes": args.notes,
        "included": True if args.include or not args.include else True,
        "created_at": now_iso(),
    }
    append_jsonl(path, record)
    print(pretty(record))
    print(f"\nsaved -> {path}")


if __name__ == "__main__":
    main()
