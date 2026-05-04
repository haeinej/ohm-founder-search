#!/usr/bin/env python3
"""Search for candidates via Exa API and append to state."""

from __future__ import annotations

import argparse
import json
import os
import re
from urllib.parse import urlparse

from dotenv import load_dotenv
from exa_py import Exa

from utils import (
    STATE_DIR,
    ROOT,
    append_jsonl,
    find_by_id,
    load_jsonl,
    next_id,
    now_iso,
    pretty,
)

# ---------------------------------------------------------------------------
# Source modes — each mode targets different kinds of public artifacts
# ---------------------------------------------------------------------------

SOURCE_MODES = {
    "narrative_first": {
        "include_domains": [
            "substack.com", "medium.com", "dev.to", "mirror.xyz",
            "bearblog.dev", "hackernoon.com", "notion.site",
        ],
        "exclude_domains": [],
        "queries": [
            "I'm building an AI agent that remembers everything about you",
            "why I quit my job to build a people search engine",
            "my approach to building memory systems for AI agents",
            "how we built semantic search over personal data",
            "building a social discovery product from scratch",
            "why human connection needs better technology",
            "my thesis on AI-mediated introductions and serendipity",
            "building retrieval augmented generation for personal knowledge",
        ],
    },
    "github_first": {
        "include_domains": ["github.com"],
        "exclude_domains": [],
        "queries": [
            "AI agent memory system with persistent context",
            "semantic people search engine open source",
            "personal knowledge graph retrieval system",
            "social discovery matching algorithm",
            "human-AI interaction framework for introductions",
            "LLM agent with long-term memory and retrieval",
            "conversational AI with user modeling",
            "people recommendation engine based on interests",
        ],
    },
    "artifact_first": {
        "include_domains": [
            "github.com", "huggingface.co", "arxiv.org", "producthunt.com",
        ],
        "exclude_domains": [],
        "queries": [
            "AI agent memory and retrieval system",
            "people discovery semantic search tool",
            "personal data knowledge graph project",
            "social matching recommendation engine",
            "human connection AI product",
            "conversational agent with user context",
        ],
    },
    "broad": {
        "include_domains": [],
        "exclude_domains": ["linkedin.com"],
        "queries": [
            "building AI that understands people deeply",
            "why current social networks fail at real connection",
            "my approach to AI-mediated human discovery",
            "semantic search for finding the right people",
            "building memory systems for personalized AI agents",
            "founding engineer building social AI product",
        ],
    },
    "verification": {
        "include_domains": ["linkedin.com"],
        "exclude_domains": [],
        "category": "people",
        "queries": [
            "engineer building AI agent infrastructure",
            "founder semantic search people discovery",
            "researcher AI memory systems retrieval",
            "founding engineer early-stage AI startup",
        ],
    },
}


def normalize_url(url: str) -> str:
    """Strip scheme, www., trailing slash for dedup."""
    p = urlparse(url)
    host = (p.netloc or "").lower().removeprefix("www.")
    path = p.path.rstrip("/")
    return f"{host}{path}"


def existing_urls(candidates: list[dict]) -> set[str]:
    return {normalize_url(c["url"]) for c in candidates if c.get("url")}


def extract_name(result) -> str:
    """Best-effort name extraction from an Exa result title."""
    title = getattr(result, "title", None) or ""
    title = title.strip()
    if not title:
        return "Unknown — review required"
    title = re.split(r"\s*[|–—\-]\s*", title)[0].strip()
    words = title.split()
    if 1 <= len(words) <= 5 and all(w[0].isupper() or w[0] == "'" for w in words if w):
        return title
    return title[:120] if title else "Unknown — review required"


def load_exa() -> Exa:
    load_dotenv(ROOT / ".env")
    key = os.getenv("EXA_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "EXA_API_KEY is empty in .env — add it before running this script.\n"
            "Get a key at https://dashboard.exa.ai"
        )
    return Exa(api_key=key)


def search_exa(
    exa: Exa,
    query: str,
    *,
    limit: int = 10,
    category: str | None = None,
    include_domains: list[str] | None = None,
    exclude_domains: list[str] | None = None,
) -> list:
    """Run a single Exa search and return results."""
    kwargs = dict(
        query=query,
        type="deep",
        num_results=limit,
        contents={"highlights": True},
    )
    if category:
        kwargs["category"] = category
    if include_domains:
        kwargs["include_domains"] = include_domains
    if exclude_domains:
        kwargs["exclude_domains"] = exclude_domains
    resp = exa.search(**kwargs)
    return resp.results


def main() -> None:
    p = argparse.ArgumentParser(
        description="Search Exa for candidates and append to state."
    )
    p.add_argument("--intent", required=True, help="intent_id, e.g. I001")
    p.add_argument("--limit", type=int, default=10, help="results per query")
    p.add_argument("--query", help="single custom query (overrides defaults)")
    p.add_argument(
        "--num-queries",
        type=int,
        default=None,
        help="how many default queries to run (ignored if --query is set)",
    )
    p.add_argument(
        "--source-mode",
        default="narrative_first",
        choices=list(SOURCE_MODES.keys()),
        help="source targeting mode (default: narrative_first)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="print results without writing to state",
    )
    args = p.parse_args()

    intent = find_by_id(STATE_DIR / "intents.jsonl", "intent_id", args.intent)
    if not intent:
        raise SystemExit(f"intent {args.intent} not found in state/intents.jsonl")

    exa = load_exa()

    mode = SOURCE_MODES[args.source_mode]
    if args.query:
        queries = [args.query]
    else:
        queries = mode["queries"]
        if args.num_queries:
            queries = queries[: args.num_queries]

    search_kwargs: dict = dict(limit=args.limit)
    if mode.get("category"):
        search_kwargs["category"] = mode["category"]
    if mode["include_domains"]:
        search_kwargs["include_domains"] = mode["include_domains"]
    if mode["exclude_domains"]:
        search_kwargs["exclude_domains"] = mode["exclude_domains"]

    candidates_path = STATE_DIR / "candidates.jsonl"
    evidence_path = STATE_DIR / "evidence.jsonl"
    seen = existing_urls(load_jsonl(candidates_path))

    new_candidates = 0
    new_evidence = 0
    skipped_dupes = 0

    for qi, q in enumerate(queries, 1):
        print(f"\n[{qi}/{len(queries)}] searching: {q}")
        try:
            results = search_exa(exa, q, **search_kwargs)
        except Exception as e:
            print(f"  error: {e}")
            continue

        print(f"  got {len(results)} results")

        for r in results:
            url = getattr(r, "url", "") or ""
            if not url:
                continue
            norm = normalize_url(url)
            if norm in seen:
                skipped_dupes += 1
                continue
            seen.add(norm)

            name = extract_name(r)
            highlights = getattr(r, "highlights", None) or []
            snippet = " ".join(highlights)[:500] if highlights else ""

            cid = next_id(candidates_path, "C", "candidate_id")
            candidate_rec = {
                "candidate_id": cid,
                "name": name,
                "type": "person",
                "url": url,
                "reason_added": f"Exa search: {q}",
                "discovery_source": "exa_search",
                "source_provider": "exa",
                "source_mode": args.source_mode,
                "search_query": q,
                "status": "needs_review",
                "human_override": None,
                "next_action": "review",
                "proxy_status": "none",
                "outreach_status": "none",
                "created_at": now_iso(),
            }

            eid = next_id(evidence_path, "E", "evidence_id")
            evidence_rec = {
                "evidence_id": eid,
                "candidate_id": cid,
                "url": url,
                "type": "writing",
                "snippet": snippet,
                "claim": "Public Exa search result that may indicate relevance to the intent. Needs human refinement.",
                "tag": "exa_discovery",
                "confidence": 0.3,
                "source": "exa_search",
                "source_mode": args.source_mode,
                "search_query": q,
                "created_at": now_iso(),
            }

            if args.dry_run:
                print(f"  [dry-run] {cid}: {name} — {url}")
            else:
                append_jsonl(candidates_path, candidate_rec)
                append_jsonl(evidence_path, evidence_rec)
                print(f"  + {cid}: {name} — {url}")

            new_candidates += 1
            new_evidence += 1

    print("\n" + "=" * 50)
    print(f"intent:          {args.intent}")
    print(f"source mode:     {args.source_mode}")
    print(f"queries run:     {len(queries)}")
    print(f"new candidates:  {new_candidates}")
    print(f"new evidence:    {new_evidence}")
    print(f"skipped (dupes): {skipped_dupes}")
    if args.dry_run:
        print("mode:            DRY RUN — nothing written")
    else:
        print(f"written to:      {candidates_path}")
        print(f"                 {evidence_path}")


if __name__ == "__main__":
    main()
