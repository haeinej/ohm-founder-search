#!/usr/bin/env python3
"""Instantiate a candidate proxy agent from a candidate proxy bundle."""

from __future__ import annotations

import argparse
import json

from utils import (
    STATE_DIR,
    append_jsonl,
    call_llm_json,
    find_by_id,
    load_env,
    next_id,
    now_iso,
    pretty,
    read_prompt,
)


def main() -> None:
    p = argparse.ArgumentParser(description="Instantiate candidate proxy agent.")
    p.add_argument("--candidate-proxy", required=True, help="candidate_proxy_bundle_id, e.g. CPB001")
    args = p.parse_args()

    bundle = find_by_id(
        STATE_DIR / "candidate_proxy_bundles.jsonl",
        "candidate_proxy_bundle_id",
        args.candidate_proxy,
    )
    if not bundle:
        raise SystemExit(f"{args.candidate_proxy} not found")

    template = read_prompt("instantiate_candidate_proxy_agent.txt")
    system_prompt = template.replace(
        "{candidate_proxy_bundle}", json.dumps(bundle, ensure_ascii=False, indent=2)
    )

    client = load_env()
    print(f"[instantiate_candidate_proxy_agent] calling Claude for {args.candidate_proxy}...")
    agent_record = call_llm_json(
        client,
        system_prompt=system_prompt,
        user_message="Instantiate the candidate proxy agent now. JSON only.",
        max_tokens=2048,
    )

    path = STATE_DIR / "proxy_agents.jsonl"
    cpa_id = agent_record.get("candidate_proxy_agent_id") or next_id(path, "CPA", "candidate_proxy_agent_id")
    record = {
        **agent_record,
        "agent_kind": "candidate",
        "candidate_proxy_agent_id": cpa_id,
        "candidate_proxy_bundle_id": args.candidate_proxy,
        "candidate_id": bundle.get("candidate_id"),
        "created_at": now_iso(),
    }
    append_jsonl(path, record)
    print(pretty(record))
    print(f"\nsaved -> {path}")


if __name__ == "__main__":
    main()
