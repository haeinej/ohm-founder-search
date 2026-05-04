#!/usr/bin/env python3
"""Generate a search strategy from a context brief — decomposes intent into search buckets."""

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
    p = argparse.ArgumentParser(description="Generate search strategy from context brief.")
    p.add_argument("--intent", required=True)
    p.add_argument("--context-brief", help="context_brief_id (default: latest for intent)")
    args = p.parse_args()

    intent = find_by_id(STATE_DIR / "intents.jsonl", "intent_id", args.intent)
    if not intent:
        raise SystemExit(f"intent {args.intent} not found")

    if args.context_brief:
        cb = find_by_id(STATE_DIR / "context_briefs.jsonl", "context_brief_id", args.context_brief)
    else:
        cbs = [b for b in load_jsonl(STATE_DIR / "context_briefs.jsonl") if b.get("intent_id") == args.intent]
        cb = cbs[-1] if cbs else None
    if not cb:
        raise SystemExit("no context brief found — run generate_context_brief.py first")

    template = read_prompt("generate_search_strategy.txt")
    system_prompt = (
        template
        .replace("{context_brief}", json.dumps(cb, ensure_ascii=False, indent=2))
        .replace("{intent}", json.dumps(intent, ensure_ascii=False, indent=2))
    )

    client = load_env()
    print(f"[search_strategy] generating for {args.intent}...")
    strategy = call_llm_json(
        client,
        system_prompt=system_prompt,
        user_message="Generate the search strategy now. JSON only.",
        max_tokens=3072,
    )

    path = STATE_DIR / "search_strategies.jsonl"
    ss_id = strategy.get("search_strategy_id") or next_id(path, "SS", "search_strategy_id")
    record = {
        **strategy,
        "search_strategy_id": ss_id,
        "intent_id": args.intent,
        "context_brief_id": cb["context_brief_id"],
        "created_at": now_iso(),
    }
    append_jsonl(path, record)
    print(pretty(record))
    print(f"\nsaved -> {path}")


if __name__ == "__main__":
    main()
