#!/usr/bin/env python3
"""Batch reflection — assess search quality before enriching more. Stop if results are noise."""

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
    p = argparse.ArgumentParser(description="Reflect on batch quality before enriching more.")
    p.add_argument("--intent", required=True)
    args = p.parse_args()

    cb_list = [b for b in load_jsonl(STATE_DIR / "context_briefs.jsonl") if b.get("intent_id") == args.intent]
    cb = cb_list[-1] if cb_list else {}

    ss_list = [s for s in load_jsonl(STATE_DIR / "search_strategies.jsonl") if s.get("intent_id") == args.intent]
    ss = ss_list[-1] if ss_list else {}

    nodes = [n for n in load_jsonl(STATE_DIR / "nodes.jsonl") if n.get("intent_id") == args.intent]

    if not nodes:
        print("no nodes to reflect on — run classify_search_result.py first")
        return

    # Summarize nodes
    type_counts: dict[str, int] = {}
    action_counts: dict[str, int] = {}
    for n in nodes:
        nt = n.get("node_type", "unknown")
        type_counts[nt] = type_counts.get(nt, 0) + 1
        act = n.get("recommended_next_action", "unknown")
        action_counts[act] = action_counts.get(act, 0) + 1

    nodes_summary = json.dumps({
        "total": len(nodes),
        "by_type": type_counts,
        "by_action": action_counts,
        "sample_nodes": [
            {"name": n.get("name"), "type": n.get("node_type"), "value": n.get("likely_value_type"), "action": n.get("recommended_next_action")}
            for n in nodes[:15]
        ],
    }, indent=2)

    classifications_summary = json.dumps({
        "persons_direct": sum(1 for n in nodes if n.get("is_direct_person_candidate")),
        "expandable": sum(1 for n in nodes if n.get("is_expandable_node")),
        "rejected": sum(1 for n in nodes if n.get("recommended_next_action") == "reject"),
    }, indent=2)

    template = read_prompt("reflect_on_batch.txt")
    system_prompt = (
        template
        .replace("{context_brief}", json.dumps(cb, ensure_ascii=False, indent=1))
        .replace("{search_strategy}", json.dumps(ss, ensure_ascii=False, indent=1))
        .replace("{nodes_summary}", nodes_summary)
        .replace("{classifications_summary}", classifications_summary)
    )

    client = load_env()
    print(f"[batch_reflection] reflecting on {len(nodes)} nodes for {args.intent}...")
    result = call_llm_json(
        client,
        system_prompt=system_prompt,
        user_message="Reflect on this batch. JSON only.",
        max_tokens=1024,
    )

    path = STATE_DIR / "batch_reflections.jsonl"
    br_id = result.get("batch_reflection_id") or next_id(path, "BR", "batch_reflection_id")
    record = {
        **result,
        "batch_reflection_id": br_id,
        "intent_id": args.intent,
        "created_at": now_iso(),
    }
    append_jsonl(path, record)
    print(pretty(record))

    if not result.get("should_continue_enrichment", True):
        print("\n⚠ BATCH QUALITY LOW — revise search strategy before enriching more")

    print(f"\nsaved -> {path}")


if __name__ == "__main__":
    main()
