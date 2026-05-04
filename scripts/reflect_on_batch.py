#!/usr/bin/env python3
"""Batch reflection — assess search quality before enriching more.

Uses intent-bound profile and search lens (not generic context brief).
Includes variable-generation critique.
"""

from __future__ import annotations

import argparse
import json

from utils import (
    STATE_DIR,
    append_jsonl,
    call_llm_json,
    load_env,
    load_jsonl,
    next_id,
    now_iso,
    pretty,
    read_prompt,
)


def main() -> None:
    p = argparse.ArgumentParser(description="Reflect on batch quality.")
    p.add_argument("--intent", required=True)
    args = p.parse_args()

    ibp_list = [x for x in load_jsonl(STATE_DIR / "intent_bound_user_profiles.jsonl") if x.get("intent_id") == args.intent]
    ibp = ibp_list[-1] if ibp_list else {}

    sl_list = [x for x in load_jsonl(STATE_DIR / "search_lenses.jsonl") if x.get("intent_id") == args.intent]
    sl = sl_list[-1] if sl_list else {}

    nodes = [n for n in load_jsonl(STATE_DIR / "nodes.jsonl") if n.get("intent_id") == args.intent]

    if not nodes:
        print("no nodes to reflect on")
        return

    # Summarize by node function
    func_counts: dict[str, int] = {}
    action_counts: dict[str, int] = {}
    for n in nodes:
        for f in n.get("node_function", []):
            func_counts[f] = func_counts.get(f, 0) + 1
        act = n.get("next_action", "unknown")
        action_counts[act] = action_counts.get(act, 0) + 1

    nodes_summary = json.dumps({
        "total": len(nodes),
        "by_function": func_counts,
        "by_action": action_counts,
        "sample_nodes": [
            {"name": n.get("name"), "label": n.get("node_label"), "functions": n.get("node_function"), "value": n.get("likely_value_type"), "action": n.get("next_action")}
            for n in nodes[:15]
        ],
    }, indent=2)

    interpretations_summary = json.dumps({
        "directly_contactable": sum(1 for n in nodes if n.get("is_directly_contactable")),
        "contains_people": sum(1 for n in nodes if n.get("contains_people")),
        "rejected": sum(1 for n in nodes if n.get("next_action") == "reject"),
    }, indent=2)

    template = read_prompt("reflect_on_batch.txt")
    system_prompt = (
        template
        .replace("{intent_bound_profile}", json.dumps(ibp, ensure_ascii=False, indent=1))
        .replace("{search_lens}", json.dumps(sl, ensure_ascii=False, indent=1))
        .replace("{nodes_summary}", nodes_summary)
        .replace("{interpretations_summary}", interpretations_summary)
    )

    client = load_env()
    print(f"[batch_reflection] {len(nodes)} nodes for {args.intent}...")
    result = call_llm_json(
        client,
        system_prompt=system_prompt,
        user_message="Reflect on this batch. JSON only.",
        max_tokens=1024,
    )

    path = STATE_DIR / "batch_reflections.jsonl"
    br_id = result.get("batch_reflection_id") or next_id(path, "BR", "batch_reflection_id")
    record = {**result, "batch_reflection_id": br_id, "intent_id": args.intent, "created_at": now_iso()}
    append_jsonl(path, record)
    print(pretty(record))

    if not result.get("should_continue_enrichment", True):
        print("\n** BATCH QUALITY LOW — revise profile/lens before enriching more")

    print(f"\nsaved -> {path}")


if __name__ == "__main__":
    main()
