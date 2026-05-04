#!/usr/bin/env python3
"""Generate a context brief before search — grounds discovery in the user's actual situation."""

from __future__ import annotations

import argparse
import json

from utils import (
    STATE_DIR,
    append_jsonl,
    call_llm_json,
    find_by_id,
    load_jsonl,
    next_id,
    now_iso,
    pretty,
    read_prompt,
    render_input_source,
)


def truncate_source(text: str, max_chars: int = 1500) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n... (truncated)"


def main() -> None:
    p = argparse.ArgumentParser(description="Generate a context brief for an intent.")
    p.add_argument("--intent", required=True, help="intent_id, e.g. I002")
    p.add_argument("--max-sources", type=int, default=10)
    args = p.parse_args()

    intent = find_by_id(STATE_DIR / "intents.jsonl", "intent_id", args.intent)
    if not intent:
        raise SystemExit(f"intent {args.intent} not found")

    sources = [s for s in load_jsonl(STATE_DIR / "input_sources.jsonl") if s.get("included", True)]
    sources = sources[:args.max_sources]
    rendered = "\n\n".join(truncate_source(render_input_source(s)) for s in sources)

    template = read_prompt("generate_context_brief.txt")
    system_prompt = (
        template
        .replace("{user_context}", rendered)
        .replace("{intent}", json.dumps(intent, ensure_ascii=False, indent=2))
    )

    client = load_env()
    print(f"[context_brief] generating for intent {args.intent} with {len(sources)} sources...")
    brief = call_llm_json(
        client,
        system_prompt=system_prompt,
        user_message="Generate the context brief now. JSON only.",
        max_tokens=2048,
    )

    path = STATE_DIR / "context_briefs.jsonl"
    cb_id = brief.get("context_brief_id") or next_id(path, "CB", "context_brief_id")
    record = {
        **brief,
        "context_brief_id": cb_id,
        "intent_id": args.intent,
        "created_at": now_iso(),
    }
    append_jsonl(path, record)
    print(pretty(record))
    print(f"\nsaved -> {path}")


def load_env():
    from utils import load_env as _load_env
    return _load_env()


if __name__ == "__main__":
    main()
