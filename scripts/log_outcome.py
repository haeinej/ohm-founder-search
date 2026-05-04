#!/usr/bin/env python3
"""Log the outcome of an outreach + (optional) first conversation.

Auto-populates search provenance from candidate, dossier, and collision records
so outcomes can be traced back to retrieval and evidence features.
"""

from __future__ import annotations

import argparse

from utils import STATE_DIR, append_jsonl, find_all_by, find_by_id, next_id, now_iso, pretty


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
    p.add_argument("--what-proxies-missed", help="freeform")
    p.add_argument("--what-overvalued", help="what scoring dimension was overvalued")
    p.add_argument("--what-undervalued", help="what scoring dimension was undervalued")
    p.add_argument("--most-predictive-source", help="which source type was most predictive")
    p.add_argument("--strategy-quality", help="0-5: did the collision conversation strategy help?")
    args = p.parse_args()

    cand = find_by_id(STATE_DIR / "candidates.jsonl", "candidate_id", args.candidate)
    neg = find_by_id(STATE_DIR / "collisions.jsonl", "collision_id", args.negotiation)
    if not cand:
        raise SystemExit(f"candidate {args.candidate} not found")
    if not neg:
        raise SystemExit(f"negotiation {args.negotiation} not found")

    # Interactive prompts for required fields
    reached = args.reached or prompt("reached out? (yes/no)", "yes")
    responded = args.responded or prompt("responded? (yes/no/pending)", "pending")
    met = args.met or prompt("met / had first conversation? (yes/no/pending)", "pending")
    quality = args.quality or prompt("conversation quality 0-5 (or blank)", "")
    notes = args.notes or prompt("notes", "")
    missed = args.what_proxies_missed or prompt("what the proxies missed (most useful field)", "")
    overvalued = args.what_overvalued or prompt("what was overvalued in scoring", "")
    undervalued = args.what_undervalued or prompt("what was undervalued in scoring", "")
    predictive = args.most_predictive_source or prompt("most predictive source type (github/substack/blog/personal_site)", "")
    strategy_q = args.strategy_quality or prompt("conversation strategy quality 0-5 (did collision advice help?)", "")

    # Auto-populate provenance from candidate + dossier + collision
    dossier = find_by_id(STATE_DIR / "candidate_dossiers.jsonl", "candidate_id", args.candidate)
    evidence = find_all_by(STATE_DIR / "evidence.jsonl", "candidate_id", args.candidate)

    pre_proxy_scores = {}
    for k in ["dossier_quality_score", "candidate_fit_score"]:
        val = cand.get(k) if cand else None
        if val is not None:
            pre_proxy_scores[k] = val

    path = STATE_DIR / "outcomes.jsonl"
    oid = next_id(path, "OUT", "outcome_id")
    record = {
        "outcome_id": oid,
        "candidate_id": args.candidate,
        "negotiation_id": args.negotiation,
        "intent_id": neg.get("intent_id"),
        # Core outcome
        "reached_out": reached,
        "responded": responded,
        "met": met,
        "conversation_quality": quality,
        "notes": notes,
        "what_proxies_missed": missed,
        # Feedback on scoring
        "what_was_overvalued": overvalued,
        "what_was_undervalued": undervalued,
        "what_source_was_most_predictive": predictive,
        "conversation_strategy_quality": strategy_q,
        # Auto-populated provenance
        "search_query": cand.get("search_query", ""),
        "source_provider": cand.get("source_provider", ""),
        "source_mode": cand.get("source_mode", ""),
        "primary_source_type": (dossier.get("source_types", ["unknown"]) if dossier else ["unknown"])[0],
        "source_types": dossier.get("source_types", []) if dossier else [],
        "artifact_count": dossier.get("artifact_count", 0) if dossier else 0,
        "pre_proxy_scores": pre_proxy_scores,
        "evidence_tags": list(set(e.get("tag", "") for e in evidence if e.get("tag"))),
        "intro_recommendation": neg.get("intro_recommendation", ""),
        "logged_at": now_iso(),
    }
    append_jsonl(path, record)
    print(pretty(record))
    print(f"\nsaved -> {path}")


if __name__ == "__main__":
    main()
