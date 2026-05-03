#!/usr/bin/env python3
"""Log the outcome of an outreach + (optional) first conversation."""

from __future__ import annotations

import argparse

from utils import STATE_DIR, append_jsonl, find_by_id, next_id, now_iso, pretty


def prompt(label: str, default: str = "") -> str:
    suf = f" [{default}]" if default else ""
    val = input(f"{label}{suf}: ").strip()
    return val or default


def main() -> None:
    p = argparse.ArgumentParser(description="Log an outcome.")
    p.add_argument("--candidate", required=True)
    p.add_argument("--negotiation", required=True, help="collision_id, e.g. N001")
    p.add_argument("--reached", help="yes|no")
    p.add_argument("--responded", help="yes|no")
    p.add_argument("--met", help="yes|no")
    p.add_argument("--quality", help="0-5 subjective")
    p.add_argument("--notes", help="freeform")
    p.add_argument("--what_proxies_missed", help="freeform")
    args = p.parse_args()

    cand = find_by_id(STATE_DIR / "candidates.jsonl", "candidate_id", args.candidate)
    neg = find_by_id(STATE_DIR / "collisions.jsonl", "collision_id", args.negotiation)
    if not cand:
        raise SystemExit(f"candidate {args.candidate} not found")
    if not neg:
        raise SystemExit(f"negotiation {args.negotiation} not found")

    reached = args.reached or prompt("reached out? (yes/no)", "yes")
    responded = args.responded or prompt("responded? (yes/no/pending)", "pending")
    met = args.met or prompt("met / had first conversation? (yes/no/pending)", "pending")
    quality = args.quality or prompt("conversation quality 0-5 (or blank)", "")
    notes = args.notes or prompt("notes", "")
    missed = args.what_proxies_missed or prompt("what the proxies missed (most useful field)", "")

    path = STATE_DIR / "outcomes.jsonl"
    oid = next_id(path, "OUT", "outcome_id")
    record = {
        "outcome_id": oid,
        "candidate_id": args.candidate,
        "negotiation_id": args.negotiation,
        "intent_id": neg.get("intent_id"),
        "reached_out": reached,
        "responded": responded,
        "met": met,
        "conversation_quality": quality,
        "notes": notes,
        "what_proxies_missed": missed,
        "logged_at": now_iso(),
    }
    append_jsonl(path, record)
    print(pretty(record))
    print(f"\nsaved -> {path}")


if __name__ == "__main__":
    main()
