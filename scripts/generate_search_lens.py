#!/usr/bin/env python3
"""Generate a search lens from an intent-bound user profile — defines what to look for and why."""

from __future__ import annotations

import argparse
import json

from utils import (
    STATE_DIR,
    append_jsonl,
    call_llm_json,
    find_by_id,
    load_env,
    load_jsonl,
    next_id,
    now_iso,
    pretty,
    read_prompt,
)


def main() -> None:
    p = argparse.ArgumentParser(description="Generate search lens from intent-bound profile.")
    p.add_argument("--intent", required=True)
    p.add_argument("--profile", help="intent_bound_profile_id (default: latest for intent)")
    args = p.parse_args()

    intent = find_by_id(STATE_DIR / "intents.jsonl", "intent_id", args.intent)
    if not intent:
        raise SystemExit(f"intent {args.intent} not found")

    profiles = load_jsonl(STATE_DIR / "intent_bound_user_profiles.jsonl")
    if args.profile:
        ibp = find_by_id(STATE_DIR / "intent_bound_user_profiles.jsonl", "intent_bound_profile_id", args.profile)
    else:
        matching = [p for p in profiles if p.get("intent_id") == args.intent]
        ibp = matching[-1] if matching else None
    if not ibp:
        raise SystemExit("no intent-bound profile — run generate_intent_bound_user_profile.py first")

    template = read_prompt("generate_search_lens.txt")
    system_prompt = (
        template
        .replace("{intent_bound_profile}", json.dumps(ibp, ensure_ascii=False, indent=2))
        .replace("{intent}", json.dumps(intent, ensure_ascii=False, indent=2))
    )

    client = load_env()
    print(f"[search_lens] generating for {args.intent}...")
    result = call_llm_json(
        client,
        system_prompt=system_prompt,
        user_message="Generate the search lens. JSON only.",
        max_tokens=3072,
    )

    path = STATE_DIR / "search_lenses.jsonl"
    sl_id = result.get("search_lens_id") or next_id(path, "SL", "search_lens_id")
    record = {
        **result,
        "search_lens_id": sl_id,
        "intent_id": args.intent,
        "intent_bound_profile_id": ibp["intent_bound_profile_id"],
        "created_at": now_iso(),
    }
    append_jsonl(path, record)
    print(pretty(record))
    print(f"\nsaved -> {path}")


if __name__ == "__main__":
    main()
