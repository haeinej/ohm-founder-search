#!/usr/bin/env python3
"""Run a structured 5-round proxy dialogue between user and candidate proxy agents."""

from __future__ import annotations

import argparse
import json

from utils import (
    STATE_DIR,
    append_jsonl,
    call_llm_json,
    find_by_id,
    find_by_id as _,
    load_env,
    load_jsonl,
    next_id,
    now_iso,
    pretty,
    read_prompt,
)


def find_user_agent(upa_id: str) -> dict | None:
    for r in load_jsonl(STATE_DIR / "proxy_agents.jsonl"):
        if r.get("user_proxy_agent_id") == upa_id:
            return r
    return None


def find_candidate_agent(cpa_id: str) -> dict | None:
    for r in load_jsonl(STATE_DIR / "proxy_agents.jsonl"):
        if r.get("candidate_proxy_agent_id") == cpa_id:
            return r
    return None


def main() -> None:
    p = argparse.ArgumentParser(description="Run a 5-round proxy dialogue.")
    p.add_argument("--user-agent", required=True, help="UPA###")
    p.add_argument("--candidate-agent", required=True, help="CPA###")
    p.add_argument("--intent", help="intent_id (defaults to the one bound to the user proxy bundle)")
    args = p.parse_args()

    upa = find_user_agent(args.user_agent)
    cpa = find_candidate_agent(args.candidate_agent)
    if not upa:
        raise SystemExit(f"user proxy agent {args.user_agent} not found")
    if not cpa:
        raise SystemExit(f"candidate proxy agent {args.candidate_agent} not found")

    intent_id = args.intent
    if not intent_id:
        upb = find_by_id(
            STATE_DIR / "user_proxy_bundles.jsonl",
            "user_proxy_bundle_id",
            upa.get("user_proxy_bundle_id"),
        )
        if upb:
            intent_id = upb.get("intent_id")
    if not intent_id:
        raise SystemExit("could not infer intent — pass --intent")

    intent = find_by_id(STATE_DIR / "intents.jsonl", "intent_id", intent_id)
    if not intent:
        raise SystemExit(f"intent {intent_id} not found")

    template = read_prompt("run_proxy_dialogue.txt")
    system_prompt = template.replace("{user_proxy_agent}", json.dumps(upa, ensure_ascii=False, indent=2))
    system_prompt = system_prompt.replace("{candidate_proxy_agent}", json.dumps(cpa, ensure_ascii=False, indent=2))
    system_prompt = system_prompt.replace("{intent}", json.dumps(intent, ensure_ascii=False, indent=2))

    client = load_env()
    print(f"[run_proxy_dialogue] calling Claude: {args.user_agent} <-> {args.candidate_agent} on {intent_id}")
    dialogue = call_llm_json(
        client,
        system_prompt=system_prompt,
        user_message="Run the 5-round dialogue now. JSON only.",
        max_tokens=6000,
    )

    path = STATE_DIR / "proxy_dialogues.jsonl"
    pd_id = dialogue.get("proxy_dialogue_id") or next_id(path, "PD", "proxy_dialogue_id")
    record = {
        **dialogue,
        "proxy_dialogue_id": pd_id,
        "user_proxy_agent_id": args.user_agent,
        "candidate_proxy_agent_id": args.candidate_agent,
        "intent_id": intent_id,
        "created_at": now_iso(),
    }
    append_jsonl(path, record)
    print(pretty(record))
    print(f"\nsaved -> {path}")


if __name__ == "__main__":
    main()
