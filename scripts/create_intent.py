#!/usr/bin/env python3
"""Create an intent record."""

from __future__ import annotations

import argparse

from utils import STATE_DIR, append_jsonl, next_id, now_iso, pretty


def main() -> None:
    p = argparse.ArgumentParser(description="Create an intent.")
    p.add_argument("--type", required=True, help="e.g. cofounder, hire, advisor, collaborator")
    p.add_argument("--question", required=True, help="plain-language framing of the intent")
    p.add_argument("--scope", default="", help="optional scope notes")
    args = p.parse_args()

    path = STATE_DIR / "intents.jsonl"
    iid = next_id(path, "I", "intent_id")
    record = {
        "intent_id": iid,
        "type": args.type,
        "question": args.question,
        "scope": args.scope,
        "status": "active",
        "created_at": now_iso(),
    }
    append_jsonl(path, record)
    print(pretty(record))
    print(f"\nsaved -> {path}")


if __name__ == "__main__":
    main()
