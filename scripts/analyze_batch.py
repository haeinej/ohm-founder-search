#!/usr/bin/env python3
"""Run a batch analysis over recent collisions and outcomes for an intent."""

from __future__ import annotations

import argparse
import json

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
)


def main() -> None:
    p = argparse.ArgumentParser(description="Batch analysis for an intent.")
    p.add_argument("--intent", required=True)
    p.add_argument("--last", type=int, default=10)
    args = p.parse_args()

    intent = find_by_id(STATE_DIR / "intents.jsonl", "intent_id", args.intent)
    if not intent:
        raise SystemExit(f"intent {args.intent} not found")

    collisions = find_all_by(STATE_DIR / "collisions.jsonl", "intent_id", args.intent)
    collisions = collisions[-args.last :]

    outcomes = [
        o for o in load_jsonl(STATE_DIR / "outcomes.jsonl") if o.get("intent_id") == args.intent
    ][-args.last :]

    upbs = [
        b for b in load_jsonl(STATE_DIR / "user_proxy_bundles.jsonl") if b.get("intent_id") == args.intent
    ]
    current_upb = upbs[-1] if upbs else {}

    # Build outcome provenance by joining outcomes with candidate + dossier records
    outcome_provenance = []
    for o in outcomes:
        cand = find_by_id(STATE_DIR / "candidates.jsonl", "candidate_id", o.get("candidate_id"))
        dossier = find_by_id(STATE_DIR / "candidate_dossiers.jsonl", "candidate_id", o.get("candidate_id"))
        outcome_provenance.append({
            "outcome_id": o.get("outcome_id"),
            "candidate_id": o.get("candidate_id"),
            "conversation_quality": o.get("conversation_quality"),
            "search_query": o.get("search_query", cand.get("search_query", "") if cand else ""),
            "source_mode": o.get("source_mode", cand.get("source_mode", "") if cand else ""),
            "primary_source_type": o.get("primary_source_type", ""),
            "source_types": o.get("source_types", []),
            "artifact_count": o.get("artifact_count", 0),
            "pre_proxy_scores": o.get("pre_proxy_scores", {}),
            "evidence_tags": o.get("evidence_tags", []),
            "what_was_overvalued": o.get("what_was_overvalued", ""),
            "what_was_undervalued": o.get("what_was_undervalued", ""),
            "what_source_was_most_predictive": o.get("what_source_was_most_predictive", ""),
            "conversation_strategy_quality": o.get("conversation_strategy_quality", ""),
            "dossier_quality_score": dossier.get("dossier_quality_score") if dossier else None,
            "candidate_fit_score": dossier.get("candidate_fit_score") if dossier else None,
        })

    template = read_prompt("analyze_batch.txt")
    system_prompt = template.replace("{intent}", json.dumps(intent, ensure_ascii=False, indent=2))
    system_prompt = system_prompt.replace("{collisions}", json.dumps(collisions, ensure_ascii=False, indent=2))
    system_prompt = system_prompt.replace("{outcomes}", json.dumps(outcomes, ensure_ascii=False, indent=2))
    system_prompt = system_prompt.replace("{user_proxy_bundle}", json.dumps(current_upb, ensure_ascii=False, indent=2))
    system_prompt = system_prompt.replace("{outcome_provenance}", json.dumps(outcome_provenance, ensure_ascii=False, indent=2))

    client = load_env()
    print(f"[analyze_batch] {len(collisions)} collisions, {len(outcomes)} outcomes for {args.intent}")
    record = call_llm_json(
        client,
        system_prompt=system_prompt,
        user_message="Run the batch analysis now. JSON only.",
        max_tokens=4096,
    )

    path = STATE_DIR / "batch_analyses.jsonl"
    bid = record.get("batch_analysis_id") or next_id(path, "BA", "batch_analysis_id")
    record = {
        **record,
        "batch_analysis_id": bid,
        "intent_id": args.intent,
        "n_collisions_reviewed": len(collisions),
        "n_outcomes_reviewed": len(outcomes),
        "created_at": now_iso(),
    }
    append_jsonl(path, record)
    print(pretty(record))
    print(f"\nsaved -> {path}")


if __name__ == "__main__":
    main()
