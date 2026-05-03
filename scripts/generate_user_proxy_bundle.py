#!/usr/bin/env python3
"""Generate an intent-specific user proxy bundle from input sources via Claude."""

from __future__ import annotations

import argparse
import json

from utils import (
    STATE_DIR,
    append_jsonl,
    call_claude_json,
    find_by_id,
    load_env,
    load_jsonl,
    next_id,
    now_iso,
    pretty,
    read_prompt,
    render_input_source,
)


def main() -> None:
    p = argparse.ArgumentParser(description="Generate user proxy bundle.")
    p.add_argument("--intent", required=True, help="intent_id, e.g. I001")
    args = p.parse_args()

    intent = find_by_id(STATE_DIR / "intents.jsonl", "intent_id", args.intent)
    if not intent:
        raise SystemExit(f"intent {args.intent} not found in state/intents.jsonl")

    sources = [s for s in load_jsonl(STATE_DIR / "input_sources.jsonl") if s.get("included", True)]
    if not sources:
        raise SystemExit("no input sources registered. Run add_input_source.py first.")

    rendered_sources = "\n\n".join(render_input_source(s) for s in sources)

    template = read_prompt("generate_user_proxy_bundle.txt")
    system_prompt = template.replace("{intent}", json.dumps(intent, ensure_ascii=False, indent=2))
    system_prompt = system_prompt.replace("{input_sources}", rendered_sources)

    client = load_env()
    print(f"[generate_user_proxy_bundle] calling Claude for intent {args.intent} with {len(sources)} sources...")
    bundle = call_claude_json(
        client,
        system_prompt=system_prompt,
        user_message="Generate the user proxy bundle now. JSON only.",
        max_tokens=4096,
    )

    path = STATE_DIR / "user_proxy_bundles.jsonl"
    upb_id = bundle.get("user_proxy_bundle_id") or next_id(path, "UPB", "user_proxy_bundle_id")
    record = {
        **bundle,
        "user_proxy_bundle_id": upb_id,
        "intent_id": args.intent,
        "user_approved": False,
        "approved_at": None,
        "created_at": now_iso(),
    }
    append_jsonl(path, record)
    print(pretty(record))
    print(f"\nsaved -> {path}")
    print(f"NEXT: review and run `python scripts/approve_user_proxy_bundle.py --id {upb_id}`")


if __name__ == "__main__":
    main()
