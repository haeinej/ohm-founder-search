#!/usr/bin/env python3
"""Run a batch analysis over recent collisions and outcomes for an intent."""

from __future__ import annotations

import argparse
import json

from utils import (
    STATE_DIR,
    append_jsonl,
    call_llm_json,
    find_all_by,
    find_by_id,
    load_env,
    load_jsonl,
    next_id,
    now_iso,
    pretty,
    read_prompt,
)


def main() -> None:
    p = argparse.ArgumentParser(description="Batch analysis for an intent.")
    p.add_argument("--intent", required=True)
    p.add_argument("--last", type=int, default=10)
    args = p.parse_args()

    intent = find_by_id(STATE_DIR / "intents.jsonl", "intent_id", args.intent)
    if not intent:
        raise SystemExit(f"intent {args.intent} not found")

    collisions = find_all_by(STATE_DIR / "collisions.jsonl", "intent_id", args.intent)
    collisions = collisions[-args.last :]

    outcomes = [
        o for o in load_jsonl(STATE_DIR / "outcomes.jsonl") if o.get("intent_id") == args.intent
    ][-args.last :]

    upbs = [
        b for b in load_jsonl(STATE_DIR / "user_proxy_bundles.jsonl") if b.get("intent_id") == args.intent
    ]
    current_upb = upbs[-1] if upbs else {}

    template = read_prompt("analyze_batch.txt")
    system_prompt = template.replace("{intent}", json.dumps(intent, ensure_ascii=False, indent=2))
    system_prompt = system_prompt.replace("{collisions}", json.dumps(collisions, ensure_ascii=False, indent=2))
    system_prompt = system_prompt.replace("{outcomes}", json.dumps(outcomes, ensure_ascii=False, indent=2))
    system_prompt = system_prompt.replace("{user_proxy_bundle}", json.dumps(current_upb, ensure_ascii=False, indent=2))

    client = load_env()
    print(f"[analyze_batch] {len(collisions)} collisions, {len(outcomes)} outcomes for {args.intent}")
    record = call_llm_json(
        client,
        system_prompt=system_prompt,
        user_message="Run the batch analysis now. JSON only.",
        max_tokens=4096,
    )

    path = STATE_DIR / "batch_analyses.jsonl"
    bid = record.get("batch_analysis_id") or next_id(path, "BA", "batch_analysis_id")
    record = {
        **record,
        "batch_analysis_id": bid,
        "intent_id": args.intent,
        "n_collisions_reviewed": len(collisions),
        "n_outcomes_reviewed": len(outcomes),
        "created_at": now_iso(),
    }
    append_jsonl(path, record)
    print(pretty(record))
    print(f"\nsaved -> {path}")


if __name__ == "__main__":
    main()
