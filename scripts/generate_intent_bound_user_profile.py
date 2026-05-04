#!/usr/bin/env python3
"""Generate an intent-bound user profile — the subset of the user relevant to THIS intent."""

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
    render_input_source,
)


def truncate_source(text: str, max_chars: int = 1500) -> str:
    return text[:max_chars] + "\n... (truncated)" if len(text) > max_chars else text


def main() -> None:
    p = argparse.ArgumentParser(description="Generate intent-bound user profile.")
    p.add_argument("--intent", required=True)
    p.add_argument("--max-sources", type=int, default=10)
    args = p.parse_args()

    intent = find_by_id(STATE_DIR / "intents.jsonl", "intent_id", args.intent)
    if not intent:
        raise SystemExit(f"intent {args.intent} not found")

    sources = [s for s in load_jsonl(STATE_DIR / "input_sources.jsonl") if s.get("included", True)]
    sources = sources[:args.max_sources]
    rendered = "\n\n".join(truncate_source(render_input_source(s)) for s in sources)

    template = read_prompt("generate_intent_bound_user_profile.txt")
    system_prompt = (
        template
        .replace("{user_context}", rendered)
        .replace("{intent}", json.dumps(intent, ensure_ascii=False, indent=2))
    )

    client = load_env()
    print(f"[intent_bound_profile] generating for {args.intent} with {len(sources)} sources...")
    result = call_llm_json(
        client,
        system_prompt=system_prompt,
        user_message="Generate the intent-bound user profile. JSON only.",
        max_tokens=2048,
    )

    path = STATE_DIR / "intent_bound_user_profiles.jsonl"
    ibp_id = result.get("intent_bound_profile_id") or next_id(path, "IBP", "intent_bound_profile_id")
    record = {**result, "intent_bound_profile_id": ibp_id, "intent_id": args.intent, "created_at": now_iso()}
    append_jsonl(path, record)
    print(pretty(record))
    print(f"\nsaved -> {path}")


if __name__ == "__main__":
    main()
