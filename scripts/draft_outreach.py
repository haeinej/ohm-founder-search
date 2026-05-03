#!/usr/bin/env python3
"""Draft an outreach message based on a collision/negotiation record."""

from __future__ import annotations

import argparse
import json

from utils import (
    STATE_DIR,
    append_jsonl,
    call_llm_json,
    find_by_id,
    load_env,
    next_id,
    now_iso,
    pretty,
    read_prompt,
)


def main() -> None:
    p = argparse.ArgumentParser(description="Draft outreach message.")
    p.add_argument("--negotiation", required=True, help="collision_id, e.g. N001")
    args = p.parse_args()

    neg = find_by_id(STATE_DIR / "collisions.jsonl", "collision_id", args.negotiation)
    if not neg:
        raise SystemExit(f"{args.negotiation} not found")

    intent = find_by_id(STATE_DIR / "intents.jsonl", "intent_id", neg.get("intent_id")) or {}
    cand = find_by_id(STATE_DIR / "candidates.jsonl", "candidate_id", neg.get("candidate_id")) or {}

    template = read_prompt("draft_outreach.txt")
    system_prompt = template.replace("{negotiation}", json.dumps(neg, ensure_ascii=False, indent=2))
    system_prompt = system_prompt.replace("{intent}", json.dumps(intent, ensure_ascii=False, indent=2))
    system_prompt = system_prompt.replace("{candidate}", json.dumps(cand, ensure_ascii=False, indent=2))

    client = load_env()
    print(f"[draft_outreach] calling Claude for {args.negotiation}...")
    record = call_llm_json(
        client,
        system_prompt=system_prompt,
        user_message="Draft the outreach message now. JSON only.",
        max_tokens=2048,
    )

    path = STATE_DIR / "outreach.jsonl"
    oid = record.get("outreach_id") or next_id(path, "O", "outreach_id")
    record = {
        **record,
        "outreach_id": oid,
        "negotiation_id": args.negotiation,
        "candidate_id": neg.get("candidate_id"),
        "created_at": now_iso(),
    }
    append_jsonl(path, record)
    print(pretty(record))
    print(f"\nsaved -> {path}")


if __name__ == "__main__":
    main()
