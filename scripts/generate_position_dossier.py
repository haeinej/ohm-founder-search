#!/usr/bin/env python3
"""Generate position dossiers — where is this person standing NOW and why might they matter?"""

from __future__ import annotations

import argparse
import json
import time

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
    render_evidence,
)

LLM_DELAY = 15


def main() -> None:
    p = argparse.ArgumentParser(description="Generate position dossiers for person nodes.")
    p.add_argument("--intent", required=True)
    p.add_argument("--node", help="specific node_id")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    cb_list = [b for b in load_jsonl(STATE_DIR / "context_briefs.jsonl") if b.get("intent_id") == args.intent]
    cb = cb_list[-1] if cb_list else {}

    nodes = load_jsonl(STATE_DIR / "nodes.jsonl")
    existing_pd = {d.get("person_node_id") for d in load_jsonl(STATE_DIR / "position_dossiers.jsonl")}

    if args.node:
        targets = [n for n in nodes if n["node_id"] == args.node]
    else:
        targets = [
            n for n in nodes
            if n.get("node_type") == "person"
            and n.get("is_direct_person_candidate")
            and n["node_id"] not in existing_pd
            and n.get("intent_id") == args.intent
            and n.get("recommended_next_action") != "reject"
        ][:args.limit]

    if not targets:
        print("no person nodes to process")
        return

    client = load_env()
    template = read_prompt("generate_position_dossier.txt")
    pd_path = STATE_DIR / "position_dossiers.jsonl"

    print(f"generating position dossiers for {len(targets)} person nodes\n")

    for i, node in enumerate(targets):
        nid = node["node_id"]
        cid = node.get("source_candidate_id", "")
        print(f"[{i+1}/{len(targets)}] {nid}: {node.get('name', '?')}")

        # Gather evidence from candidate or node
        evidence = []
        if cid:
            evidence = find_all_by(STATE_DIR / "evidence.jsonl", "candidate_id", cid)

        prompt = (
            template
            .replace("{context_brief}", json.dumps(cb, ensure_ascii=False, indent=1))
            .replace("{node}", json.dumps(node, ensure_ascii=False, indent=1))
            .replace("{evidence}", render_evidence(evidence) if evidence else "(no additional evidence)")
        )

        if i > 0:
            time.sleep(LLM_DELAY)

        try:
            result = call_llm_json(
                client,
                system_prompt=prompt,
                user_message="Generate the position dossier. JSON only.",
                max_tokens=1024,
            )
        except Exception as e:
            print(f"  error: {e}")
            continue

        pd_id = next_id(pd_path, "PDOS", "position_dossier_id")
        record = {
            **result,
            "position_dossier_id": pd_id,
            "person_node_id": nid,
            "intent_id": args.intent,
            "created_at": now_iso(),
        }

        conf = result.get("position_confidence", 0)
        print(f"  role: {result.get('current_role', '?')} | confidence: {conf}")
        print(f"  timeliness: {result.get('timeliness_reason', 'none')[:80]}")

        if not args.dry_run:
            append_jsonl(pd_path, record)

    if args.dry_run:
        print("\nmode: DRY RUN — nothing written")


if __name__ == "__main__":
    main()
