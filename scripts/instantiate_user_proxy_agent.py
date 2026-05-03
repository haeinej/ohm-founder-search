#!/usr/bin/env python3
"""Instantiate a user proxy agent from an approved user proxy bundle."""

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
    p = argparse.ArgumentParser(description="Instantiate user proxy agent.")
    p.add_argument("--user-proxy", required=True, help="user_proxy_bundle_id, e.g. UPB001")
    args = p.parse_args()

    bundle = find_by_id(STATE_DIR / "user_proxy_bundles.jsonl", "user_proxy_bundle_id", args.user_proxy)
    if not bundle:
        raise SystemExit(f"{args.user_proxy} not found")
    if not bundle.get("user_approved"):
        raise SystemExit(f"refusing — {args.user_proxy} is not user_approved. Run approve_user_proxy_bundle.py first.")

    template = read_prompt("instantiate_user_proxy_agent.txt")
    system_prompt = template.replace("{user_proxy_bundle}", json.dumps(bundle, ensure_ascii=False, indent=2))

    client = load_env()
    print(f"[instantiate_user_proxy_agent] calling Claude for {args.user_proxy}...")
    agent_record = call_llm_json(
        client,
        system_prompt=system_prompt,
        user_message="Instantiate the user proxy agent now. JSON only.",
        max_tokens=2048,
    )

    path = STATE_DIR / "proxy_agents.jsonl"
    upa_id = agent_record.get("user_proxy_agent_id") or next_id(path, "UPA", "user_proxy_agent_id")
    record = {
        **agent_record,
        "agent_kind": "user",
        "user_proxy_agent_id": upa_id,
        "user_proxy_bundle_id": args.user_proxy,
        "created_at": now_iso(),
    }
    append_jsonl(path, record)
    print(pretty(record))
    print(f"\nsaved -> {path}")


if __name__ == "__main__":
    main()
