#!/usr/bin/env python3
"""Score conversation value — gate before collision. Not every relevant person is worth talking to."""

from __future__ import annotations

import argparse
import json
import time

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
    update_jsonl,
)

LLM_DELAY = 15


def main() -> None:
    p = argparse.ArgumentParser(description="Score conversation value for person nodes.")
    p.add_argument("--intent", required=True)
    p.add_argument("--node", help="specific node_id")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    cb_list = [b for b in load_jsonl(STATE_DIR / "context_briefs.jsonl") if b.get("intent_id") == args.intent]
    cb = cb_list[-1] if cb_list else {}

    nodes = load_jsonl(STATE_DIR / "nodes.jsonl")
    pd_list = load_jsonl(STATE_DIR / "position_dossiers.jsonl")

    if args.node:
        targets = [n for n in nodes if n["node_id"] == args.node]
    else:
        # Score person nodes that have position dossiers but haven't been scored
        pd_ids = {d["person_node_id"] for d in pd_list}
        targets = [
            n for n in nodes
            if n["node_id"] in pd_ids
            and n.get("node_type") == "person"
            and n.get("intent_id") == args.intent
            and not n.get("conversation_value_score")
        ][:args.limit]

    if not targets:
        print("no person nodes to score")
        return

    client = load_env()
    template = read_prompt("score_conversation_value.txt")
    nodes_path = STATE_DIR / "nodes.jsonl"

    print(f"scoring conversation value for {len(targets)} person nodes\n")

    for i, node in enumerate(targets):
        nid = node["node_id"]
        pd = next((d for d in pd_list if d.get("person_node_id") == nid), {})

        print(f"[{i+1}/{len(targets)}] {nid}: {node.get('name', '?')}")

        prompt = (
            template
            .replace("{context_brief}", json.dumps(cb, ensure_ascii=False, indent=1))
            .replace("{node}", json.dumps(node, ensure_ascii=False, indent=1))
            .replace("{position_dossier}", json.dumps(pd, ensure_ascii=False, indent=1))
        )

        if i > 0:
            time.sleep(LLM_DELAY)

        try:
            result = call_llm_json(
                client,
                system_prompt=prompt,
                user_message="Score conversation value. JSON only.",
                max_tokens=512,
            )
        except Exception as e:
            print(f"  error: {e}")
            continue

        score = result.get("conversation_value_score", 0)
        vtype = result.get("value_type", "unknown")
        action = result.get("recommended_next_action", "hold")
        passed = result.get("gate_passed", False)

        print(f"  score: {score} | type: {vtype} | action: {action} | gate: {'PASS' if passed else 'FAIL'}")
        print(f"  reason: {result.get('specific_reason_to_talk', '')[:100]}")

        if not args.dry_run:
            update_jsonl(
                nodes_path, "node_id", nid,
                {
                    "conversation_value_score": score,
                    "conversation_value_type": vtype,
                    "conversation_gate_passed": passed,
                    "conversation_test": result.get("what_conversation_would_test", ""),
                    "recommended_next_action": action,
                },
            )

    if args.dry_run:
        print("\nmode: DRY RUN — nothing written")


if __name__ == "__main__":
    main()
