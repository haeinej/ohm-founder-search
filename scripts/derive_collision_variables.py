#!/usr/bin/env python3
"""Derive collision variables for a specific possible encounter.

Variables are NOT universal. They emerge from the interface between
the user's intent-bound state and the node's current position.
Max 5 per encounter, each evidence-linked.
"""

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
    p = argparse.ArgumentParser(description="Derive collision variables for a node.")
    p.add_argument("--intent", required=True)
    p.add_argument("--node", required=True, help="node_id")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    # Load all required context
    ibp_list = [x for x in load_jsonl(STATE_DIR / "intent_bound_user_profiles.jsonl") if x.get("intent_id") == args.intent]
    ibp = ibp_list[-1] if ibp_list else None
    if not ibp:
        raise SystemExit("no intent-bound profile — run generate_intent_bound_user_profile.py first")

    node = find_by_id(STATE_DIR / "nodes.jsonl", "node_id", args.node)
    if not node:
        raise SystemExit(f"node {args.node} not found")

    # Find position profile
    pp_list = [x for x in load_jsonl(STATE_DIR / "position_dossiers.jsonl") if x.get("person_node_id") == args.node]
    if not pp_list:
        pp_list = [x for x in load_jsonl(STATE_DIR / "position_profiles.jsonl") if x.get("person_node_id") == args.node]
    pp = pp_list[-1] if pp_list else {}

    # Gather evidence
    cid = node.get("source_candidate_id", "")
    evidence = find_all_by(STATE_DIR / "evidence.jsonl", "candidate_id", cid) if cid else []

    template = read_prompt("derive_collision_variables.txt")
    system_prompt = (
        template
        .replace("{intent_bound_profile}", json.dumps(ibp, ensure_ascii=False, indent=1))
        .replace("{node}", json.dumps(node, ensure_ascii=False, indent=1))
        .replace("{position_profile}", json.dumps(pp, ensure_ascii=False, indent=1))
        .replace("{evidence}", render_evidence(evidence) if evidence else "(no additional evidence)")
    )

    client = load_env()
    print(f"[derive_variables] {args.node}: {node.get('name', '?')}")

    result = call_llm_json(
        client,
        system_prompt=system_prompt,
        user_message="Derive the collision variables. JSON only.",
        max_tokens=1536,
    )

    path = STATE_DIR / "derived_collision_variables.jsonl"
    dvs_id = result.get("derived_variable_set_id") or next_id(path, "DVS", "derived_variable_set_id")
    record = {
        **result,
        "derived_variable_set_id": dvs_id,
        "intent_id": args.intent,
        "intent_bound_profile_id": ibp["intent_bound_profile_id"],
        "node_id": args.node,
        "created_at": now_iso(),
    }

    variables = result.get("variables", [])
    print(f"  derived {len(variables)} variables:")
    for v in variables:
        conf = v.get("confidence", 0)
        weight = v.get("decision_weight", 0)
        print(f"    - {v.get('name', '?')} (conf: {conf}, weight: {weight})")
    print(f"  top uncertainty: {result.get('top_uncertainty', '?')}")
    print(f"  highest upside: {result.get('highest_upside_variable', '?')}")
    print(f"  conversation test: {result.get('recommended_conversation_test', '?')}")

    if not args.dry_run:
        append_jsonl(path, record)
        print(f"\nsaved -> {path}")
    else:
        print("\nDRY RUN")


if __name__ == "__main__":
    main()
