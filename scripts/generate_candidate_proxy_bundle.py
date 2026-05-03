#!/usr/bin/env python3
"""Generate a public-evidence candidate proxy bundle via Claude."""

from __future__ import annotations

import argparse
import json

from utils import (
    STATE_DIR,
    append_jsonl,
    call_claude_json,
    find_all_by,
    find_by_id,
    load_env,
    next_id,
    now_iso,
    pretty,
    read_prompt,
    render_evidence,
)


def main() -> None:
    p = argparse.ArgumentParser(description="Generate candidate proxy bundle.")
    p.add_argument("--candidate", required=True, help="candidate_id, e.g. C001")
    args = p.parse_args()

    cand = find_by_id(STATE_DIR / "candidates.jsonl", "candidate_id", args.candidate)
    if not cand:
        raise SystemExit(f"candidate {args.candidate} not found")

    evidence = find_all_by(STATE_DIR / "evidence.jsonl", "candidate_id", args.candidate)
    if not evidence:
        raise SystemExit(
            f"refusing — no evidence for {args.candidate}. Add evidence first via add_evidence.py / fetch_public_evidence.py."
        )

    template = read_prompt("generate_candidate_proxy_bundle.txt")
    system_prompt = template.replace("{candidate}", json.dumps(cand, ensure_ascii=False, indent=2))
    system_prompt = system_prompt.replace("{candidate_evidence}", render_evidence(evidence))

    client = load_env()
    print(f"[generate_candidate_proxy_bundle] calling Claude for {args.candidate} with {len(evidence)} evidence items...")
    bundle = call_claude_json(
        client,
        system_prompt=system_prompt,
        user_message="Generate the candidate proxy bundle now. JSON only.",
        max_tokens=4096,
    )

    path = STATE_DIR / "candidate_proxy_bundles.jsonl"
    cpb_id = bundle.get("candidate_proxy_bundle_id") or next_id(path, "CPB", "candidate_proxy_bundle_id")
    record = {
        **bundle,
        "candidate_proxy_bundle_id": cpb_id,
        "candidate_id": args.candidate,
        "created_at": now_iso(),
    }
    append_jsonl(path, record)
    print(pretty(record))
    print(f"\nsaved -> {path}")


if __name__ == "__main__":
    main()
