#!/usr/bin/env python3
"""Interpret raw search results as nodes with generative labels and stable functions.

Replaces classify_search_result.py with purpose-bound reasoning.
"""

from __future__ import annotations

import argparse
import json
import time

import requests
from bs4 import BeautifulSoup

from utils import (
    STATE_DIR,
    append_jsonl,
    call_llm_json,
    load_env,
    load_jsonl,
    next_id,
    now_iso,
    pretty,
    read_prompt,
)

UA = "Mozilla/5.0 (compatible; ohm-founder-search/0.2)"
LLM_DELAY = 15


def fetch_text(url: str, max_chars: int = 2000) -> str:
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        return " ".join(soup.get_text(separator=" ").split())[:max_chars]
    except Exception:
        return ""


def main() -> None:
    p = argparse.ArgumentParser(description="Interpret search results as nodes.")
    p.add_argument("--intent", required=True)
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    # Load intent-bound profile and search lens
    ibp_list = [x for x in load_jsonl(STATE_DIR / "intent_bound_user_profiles.jsonl") if x.get("intent_id") == args.intent]
    ibp = ibp_list[-1] if ibp_list else {}

    sl_list = [x for x in load_jsonl(STATE_DIR / "search_lenses.jsonl") if x.get("intent_id") == args.intent]
    sl = sl_list[-1] if sl_list else {}

    candidates = load_jsonl(STATE_DIR / "candidates.jsonl")
    existing_nodes = {n.get("source_candidate_id") for n in load_jsonl(STATE_DIR / "nodes.jsonl")}

    targets = [
        c for c in candidates
        if c["candidate_id"] not in existing_nodes
        and c.get("status") in ("needs_review", "approved_for_research", "active")
    ][:args.limit]

    if not targets:
        print("no uninterpreted candidates")
        return

    client = load_env()
    template = read_prompt("interpret_node.txt")
    nodes_path = STATE_DIR / "nodes.jsonl"

    print(f"interpreting {len(targets)} results for {args.intent}\n")

    for i, cand in enumerate(targets):
        cid = cand["candidate_id"]
        url = cand.get("url", "")
        print(f"[{i+1}/{len(targets)}] {cid}: {cand.get('name', '?')} — {url[:70]}")

        page_text = fetch_text(url)
        evidence = [e for e in load_jsonl(STATE_DIR / "evidence.jsonl") if e.get("candidate_id") == cid]
        snippet = evidence[0].get("snippet", "") if evidence else ""

        prompt = (
            template
            .replace("{intent_bound_profile}", json.dumps(ibp, ensure_ascii=False, indent=1))
            .replace("{search_lens}", json.dumps(sl, ensure_ascii=False, indent=1))
            .replace("{url}", url)
            .replace("{title}", cand.get("name", ""))
            .replace("{snippet}", snippet[:500])
            .replace("{query}", cand.get("search_query", ""))
            .replace("{page_text}", page_text[:1500])
        )

        if i > 0:
            time.sleep(LLM_DELAY)

        try:
            interp = call_llm_json(
                client,
                system_prompt=prompt,
                user_message="Interpret this search result as a node. JSON only.",
                max_tokens=512,
            )
        except Exception as e:
            print(f"  error: {e}")
            continue

        node_id = next_id(nodes_path, "N", "node_id")
        node = {
            "node_id": node_id,
            "source_candidate_id": cid,
            "intent_id": args.intent,
            # Generative label + stable functions
            "node_label": interp.get("node_label", "unknown"),
            "node_function": interp.get("node_function", []),
            "name": interp.get("name", cand.get("name", "")),
            "url": url,
            "source": cand.get("source_provider", "exa"),
            "source_mode": cand.get("source_mode", ""),
            "discovery_query": cand.get("search_query", ""),
            # Stable boolean flags from functions
            "is_directly_contactable": interp.get("is_directly_contactable", False),
            "contains_people": interp.get("contains_people", False),
            "reveals_evidence_about_person": interp.get("reveals_evidence_about_person", False),
            "helps_access_people": interp.get("helps_access_people", False),
            "helps_understand_context": interp.get("helps_understand_context", False),
            # Scoring
            "likely_value_type": interp.get("likely_value_type", "unknown"),
            "identity_confidence": interp.get("identity_confidence", 0.0),
            "reason_to_keep": interp.get("reason_to_keep", ""),
            "reason_to_reject": interp.get("reason_to_reject", ""),
            "reasoning": interp.get("reasoning", ""),
            # Stable action grammar
            "next_action": interp.get("next_action", "gather_more_evidence"),
            # Human review
            "human_label": "",
            "human_note": "",
            "status": "interpreted",
            "created_at": now_iso(),
        }

        label = node["node_label"]
        funcs = ", ".join(node["node_function"])
        action = node["next_action"]
        print(f"  → [{funcs}] {label} | {action}")

        if not args.dry_run:
            append_jsonl(nodes_path, node)

    print(f"\ninterpreted: {len(targets)} results")
    if args.dry_run:
        print("mode: DRY RUN")


if __name__ == "__main__":
    main()
