#!/usr/bin/env python3
"""Expand non-person nodes (companies, funds, events, labs) into person nodes."""

from __future__ import annotations

import argparse
import json
import time
from urllib.parse import urljoin

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


def fetch_text(url: str, max_chars: int = 3000) -> str:
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        return " ".join(soup.get_text(separator=" ").split())[:max_chars]
    except Exception:
        return ""


def find_team_pages(url: str) -> list[str]:
    """Find team/about/people pages linked from the node URL."""
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        team_urls = []
        for a in soup.find_all("a", href=True):
            href = a["href"].lower()
            text = (a.get_text() or "").lower()
            if any(kw in href or kw in text for kw in ["team", "about", "people", "who-we-are", "founders", "portfolio", "speakers", "mentors"]):
                resolved = urljoin(url, a["href"])
                if resolved not in team_urls:
                    team_urls.append(resolved)
        return team_urls[:5]
    except Exception:
        return []


def main() -> None:
    p = argparse.ArgumentParser(description="Expand non-person nodes into people.")
    p.add_argument("--node", help="specific node_id to expand")
    p.add_argument("--intent", required=True)
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    nodes = load_jsonl(STATE_DIR / "nodes.jsonl")
    cb_list = [b for b in load_jsonl(STATE_DIR / "context_briefs.jsonl") if b.get("intent_id") == args.intent]
    cb = cb_list[-1] if cb_list else {}

    if args.node:
        targets = [n for n in nodes if n["node_id"] == args.node]
    else:
        targets = [
            n for n in nodes
            if n.get("is_expandable_node") and n.get("status") != "expanded"
            and n.get("intent_id") == args.intent
        ][:args.limit]

    if not targets:
        print("no expandable nodes found")
        return

    client = load_env()
    template = read_prompt("expand_node.txt")
    nodes_path = STATE_DIR / "nodes.jsonl"

    print(f"expanding {len(targets)} nodes\n")

    for i, node in enumerate(targets):
        nid = node["node_id"]
        url = node.get("url", "")
        print(f"[{i+1}/{len(targets)}] {nid}: {node.get('name', '?')} ({node['node_type']}) — {url[:60]}")

        page_text = fetch_text(url)
        team_pages = find_team_pages(url)
        expansion_text = ""
        for tp in team_pages:
            time.sleep(1)
            t = fetch_text(tp, 2000)
            if t:
                expansion_text += f"\n--- {tp} ---\n{t}\n"

        prompt = (
            template
            .replace("{context_brief}", json.dumps(cb, ensure_ascii=False, indent=1))
            .replace("{node}", json.dumps(node, ensure_ascii=False, indent=1))
            .replace("{page_text}", page_text[:2000])
            .replace("{expansion_pages}", expansion_text[:2000])
        )

        if i > 0:
            time.sleep(LLM_DELAY)

        try:
            result = call_llm_json(
                client,
                system_prompt=prompt,
                user_message="Expand this node into people. JSON only.",
                max_tokens=1024,
            )
        except Exception as e:
            print(f"  error: {e}")
            continue

        people = result.get("people_found", [])
        print(f"  found {len(people)} people")

        for person in people:
            pname = person.get("name", "Unknown")
            purl = person.get("url", "")
            child_id = next_id(nodes_path, "N", "node_id")
            child_node = {
                "node_id": child_id,
                "parent_node_id": nid,
                "intent_id": args.intent,
                "node_type": "person",
                "name": pname,
                "url": purl,
                "source": "node_expansion",
                "source_type": node["node_type"],
                "discovery_query": node.get("discovery_query", ""),
                "discovery_reason": f"Expanded from {node.get('name', nid)}: {person.get('relevance_reason', '')}",
                "is_direct_person_candidate": True,
                "is_expandable_node": False,
                "likely_value_type": node.get("likely_value_type", "unknown"),
                "identity_confidence": 0.5,
                "role_at_parent": person.get("role", ""),
                "evidence_from_expansion": person.get("evidence", ""),
                "recommended_next_action": "enrich_person",
                "human_label": "",
                "human_note": "",
                "status": "expanded_person",
                "created_at": now_iso(),
            }
            print(f"  + {child_id}: {pname} ({person.get('role', '?')})")
            if not args.dry_run:
                append_jsonl(nodes_path, child_node)

        # Mark parent as expanded
        if not args.dry_run:
            from utils import update_jsonl
            update_jsonl(nodes_path, "node_id", nid, {"status": "expanded"})

    if args.dry_run:
        print("\nmode: DRY RUN — nothing written")


if __name__ == "__main__":
    main()
