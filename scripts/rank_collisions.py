#!/usr/bin/env python3
"""Rank collision records for an intent."""

from __future__ import annotations

import argparse

from utils import STATE_DIR, find_all_by

REC_ORDER = {"attempt_now": 0, "research_more": 1, "hold": 2, "not_now": 3}


def main() -> None:
    p = argparse.ArgumentParser(description="Rank collisions for an intent.")
    p.add_argument("--intent", required=True)
    p.add_argument("--limit", type=int, default=50)
    args = p.parse_args()

    rows = find_all_by(STATE_DIR / "collisions.jsonl", "intent_id", args.intent)
    if not rows:
        print(f"(no collisions for {args.intent})")
        return

    def sort_key(r):
        rec = r.get("intro_recommendation", "not_now")
        conf = r.get("confidence") or 0.0
        return (REC_ORDER.get(rec, 9), -float(conf))

    rows.sort(key=sort_key)
    rows = rows[: args.limit]

    print(f"{'collision_id':<10}  {'candidate_id':<12}  {'rec':<14}  {'conf':<6}  main_mismatch")
    print("-" * 110)
    for r in rows:
        mm = (r.get("main_mismatch") or "").replace("\n", " ")[:60]
        print(
            f"{r.get('collision_id',''):<10}  {r.get('candidate_id',''):<12}  "
            f"{r.get('intro_recommendation',''):<14}  {str(r.get('confidence','')):<6}  {mm}"
        )


if __name__ == "__main__":
    main()
