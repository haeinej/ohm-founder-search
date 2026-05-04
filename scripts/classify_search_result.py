#!/usr/bin/env python3
"""Classify raw search results into typed nodes — person, company, fund, event, etc.

Reads unclassified candidates from candidates.jsonl, classifies each via LLM,
and writes typed node records to nodes.jsonl. Nodes that need expansion
(companies, funds, events) are marked for expand_node.py.
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
    find_by_id,
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
    p = argparse.ArgumentParser(description="Classify search results into typed nodes.")
    p.add_argument("--intent", required=True)
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    cb_list = [b for b in load_jsonl(STATE_DIR / "context_briefs.jsonl") if b.get("intent_id") == args.intent]
    cb = cb_list[-1] if cb_list else {}

    candidates = load_jsonl(STATE_DIR / "candidates.jsonl")
    existing_nodes = {n.get("source_candidate_id") for n in load_jsonl(STATE_DIR / "nodes.jsonl")}

    # Only classify candidates that haven't been classified yet
    targets = [
        c for c in candidates
        if c["candidate_id"] not in existing_nodes
        and c.get("status") in ("needs_review", "approved_for_research", "active")
    ][:args.limit]

    if not targets:
        print("no unclassified candidates to process")
        return

    client = load_env()
    template = read_prompt("classify_node.txt")
    nodes_path = STATE_DIR / "nodes.jsonl"

    print(f"classifying {len(targets)} search results for {args.intent}\n")

    for i, cand in enumerate(targets):
        cid = cand["candidate_id"]
        url = cand.get("url", "")
        print(f"[{i+1}/{len(targets)}] {cid}: {cand.get('name', '?')} — {url[:70]}")

        page_text = fetch_text(url)
        evidence = [e for e in load_jsonl(STATE_DIR / "evidence.jsonl") if e.get("candidate_id") == cid]
        snippet = evidence[0].get("snippet", "") if evidence else ""

        prompt = (
            template
            .replace("{context_brief}", json.dumps(cb, ensure_ascii=False, indent=1))
            .replace("{url}", url)
            .replace("{title}", cand.get("name", ""))
            .replace("{snippet}", snippet[:500])
            .replace("{query}", cand.get("search_query", ""))
            .replace("{source_mode}", cand.get("source_mode", ""))
            .replace("{page_text}", page_text[:1500])
        )

        if i > 0:
            time.sleep(LLM_DELAY)

        try:
            classification = call_llm_json(
                client,
                system_prompt=prompt,
                user_message="Classify this search result. JSON only.",
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
            "node_type": classification.get("node_type", "unknown"),
            "name": classification.get("name", cand.get("name", "")),
            "url": url,
            "source": cand.get("source_provider", "exa"),
            "source_type": cand.get("source_mode", ""),
            "discovery_query": cand.get("search_query", ""),
            "discovery_reason": cand.get("reason_added", ""),
            "is_direct_person_candidate": classification.get("is_direct_person_candidate", False),
            "is_expandable_node": classification.get("is_expandable_node", False),
            "likely_value_type": classification.get("likely_value_type", "unknown"),
            "identity_confidence": classification.get("identity_confidence", 0.0),
            "reason_to_keep": classification.get("reason_to_keep", ""),
            "reason_to_reject": classification.get("reason_to_reject", ""),
            "recommended_next_action": classification.get("recommended_next_action", "research_more"),
            "expansion_targets": classification.get("expansion_targets", []),
            "human_label": "",
            "human_note": "",
            "status": "classified",
            "created_at": now_iso(),
        }

        ntype = node["node_type"]
        action = node["recommended_next_action"]
        print(f"  → {ntype} | {action} | value: {node['likely_value_type']}")

        if not args.dry_run:
            append_jsonl(nodes_path, node)

    print(f"\nclassified: {len(targets)} results")
    if args.dry_run:
        print("mode: DRY RUN — nothing written")


if __name__ == "__main__":
    main()
