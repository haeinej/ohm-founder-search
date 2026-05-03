#!/usr/bin/env python3
"""Add a piece of evidence for a candidate."""

from __future__ import annotations

import argparse

from utils import STATE_DIR, append_jsonl, find_by_id, next_id, now_iso, pretty


def main() -> None:
    p = argparse.ArgumentParser(description="Add evidence for a candidate.")
    p.add_argument("--candidate", required=True, help="candidate_id, e.g. C001")
    p.add_argument("--url", required=True)
    p.add_argument("--type", required=True, help="e.g. writing, code, talk, project, profile, post")
    p.add_argument("--snippet", required=True, help="raw quoted text or short description")
    p.add_argument("--claim", required=True, help="what this evidence is being used to support")
    p.add_argument("--tag", required=True, help="relevance tag, e.g. thesis_alignment, technical_evidence, taste, shipping")
    p.add_argument("--confidence", type=float, default=0.5, help="0.0-1.0")
    args = p.parse_args()

    cand = find_by_id(STATE_DIR / "candidates.jsonl", "candidate_id", args.candidate)
    if not cand:
        raise SystemExit(f"candidate {args.candidate} not found")

    path = STATE_DIR / "evidence.jsonl"
    eid = next_id(path, "E", "evidence_id")
    record = {
        "evidence_id": eid,
        "candidate_id": args.candidate,
        "url": args.url,
        "type": args.type,
        "snippet": args.snippet,
        "claim": args.claim,
        "tag": args.tag,
        "confidence": args.confidence,
        "source": "manual",
        "created_at": now_iso(),
    }
    append_jsonl(path, record)
    print(pretty(record))
    print(f"\nsaved -> {path}")


if __name__ == "__main__":
    main()
