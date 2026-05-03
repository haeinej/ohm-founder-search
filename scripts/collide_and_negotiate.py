#!/usr/bin/env python3
"""Run a proxy collision / negotiation between user and candidate proxy bundles."""

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

REQUIRED_FIELDS = ["main_mismatch", "unsafe_assumptions", "what_would_change_the_decision"]


def latest_dialogue_for(upa_bundle_id: str | None, candidate_id: str | None) -> dict | None:
    if not upa_bundle_id and not candidate_id:
        return None
    dialogues = load_jsonl(STATE_DIR / "proxy_dialogues.jsonl")
    matching = []
    for d in dialogues:
        upa = next(
            (a for a in load_jsonl(STATE_DIR / "proxy_agents.jsonl") if a.get("user_proxy_agent_id") == d.get("user_proxy_agent_id")),
            None,
        )
        cpa = next(
            (a for a in load_jsonl(STATE_DIR / "proxy_agents.jsonl") if a.get("candidate_proxy_agent_id") == d.get("candidate_proxy_agent_id")),
            None,
        )
        if upa and upa.get("user_proxy_bundle_id") == upa_bundle_id and cpa and cpa.get("candidate_id") == candidate_id:
            matching.append(d)
    return matching[-1] if matching else None


def main() -> None:
    p = argparse.ArgumentParser(description="Collide and negotiate.")
    p.add_argument("--intent", required=True, help="intent_id, e.g. I001")
    p.add_argument("--user-proxy", required=True, help="user_proxy_bundle_id, e.g. UPB001")
    p.add_argument("--candidate", required=True, help="candidate_id, e.g. C001")
    p.add_argument("--candidate-proxy", help="candidate_proxy_bundle_id (default: most recent for candidate)")
    args = p.parse_args()

    intent = find_by_id(STATE_DIR / "intents.jsonl", "intent_id", args.intent)
    if not intent:
        raise SystemExit(f"intent {args.intent} not found")
    upb = find_by_id(STATE_DIR / "user_proxy_bundles.jsonl", "user_proxy_bundle_id", args.user_proxy)
    if not upb:
        raise SystemExit(f"user proxy bundle {args.user_proxy} not found")
    if not upb.get("user_approved"):
        raise SystemExit(f"refusing — {args.user_proxy} not user_approved")

    cand = find_by_id(STATE_DIR / "candidates.jsonl", "candidate_id", args.candidate)
    if not cand:
        raise SystemExit(f"candidate {args.candidate} not found")

    if args.candidate_proxy:
        cpb = find_by_id(
            STATE_DIR / "candidate_proxy_bundles.jsonl",
            "candidate_proxy_bundle_id",
            args.candidate_proxy,
        )
    else:
        cpbs = find_all_by(STATE_DIR / "candidate_proxy_bundles.jsonl", "candidate_id", args.candidate)
        cpb = cpbs[-1] if cpbs else None
    if not cpb:
        raise SystemExit(f"no candidate proxy bundle for {args.candidate}")

    pd = latest_dialogue_for(args.user_proxy, args.candidate)

    template = read_prompt("collide_and_negotiate.txt")
    system_prompt = template.replace("{intent}", json.dumps(intent, ensure_ascii=False, indent=2))
    system_prompt = system_prompt.replace("{user_proxy_bundle}", json.dumps(upb, ensure_ascii=False, indent=2))
    system_prompt = system_prompt.replace("{candidate_proxy_bundle}", json.dumps(cpb, ensure_ascii=False, indent=2))
    system_prompt = system_prompt.replace(
        "{proxy_dialogue_record}", json.dumps(pd or {}, ensure_ascii=False, indent=2)
    )

    client = load_env()
    print(f"[collide_and_negotiate] {args.user_proxy} x {args.candidate} on {args.intent}")
    record = call_llm_json(
        client,
        system_prompt=system_prompt,
        user_message="Generate the collision_record now. JSON only.",
        max_tokens=4096,
    )

    missing = [f for f in REQUIRED_FIELDS if not record.get(f)]
    if missing:
        raise SystemExit(f"refusing — collision record missing required fields: {missing}\n{pretty(record)}")

    path = STATE_DIR / "collisions.jsonl"
    nid = record.get("collision_id") or next_id(path, "N", "collision_id")
    record = {
        **record,
        "collision_id": nid,
        "intent_id": args.intent,
        "user_proxy_bundle_id": args.user_proxy,
        "candidate_id": args.candidate,
        "candidate_proxy_bundle_id": cpb.get("candidate_proxy_bundle_id"),
        "proxy_dialogue_id": (pd or {}).get("proxy_dialogue_id"),
        "created_at": now_iso(),
    }
    append_jsonl(path, record)
    print(pretty(record))
    print(f"\nsaved -> {path}")


if __name__ == "__main__":
    main()
