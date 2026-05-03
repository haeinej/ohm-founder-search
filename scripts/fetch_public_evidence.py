#!/usr/bin/env python3
"""Fetch a public webpage and store its extracted text as low-confidence evidence draft."""

from __future__ import annotations

import argparse

import requests
from bs4 import BeautifulSoup

from utils import STATE_DIR, append_jsonl, find_by_id, next_id, now_iso, pretty

UA = "Mozilla/5.0 (compatible; ohm-founder-search/0.1; +https://example.invalid)"
MAX_SNIPPET_CHARS = 4000


def extract_text(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    title = (soup.title.string.strip() if soup.title and soup.title.string else "").strip()
    text = " ".join(soup.get_text(separator=" ").split())
    return title, text


def main() -> None:
    p = argparse.ArgumentParser(description="Fetch public webpage as evidence draft.")
    p.add_argument("--candidate", required=True, help="candidate_id")
    p.add_argument("--url", required=True)
    p.add_argument("--type", default="webpage")
    p.add_argument("--tag", default="general")
    args = p.parse_args()

    cand = find_by_id(STATE_DIR / "candidates.jsonl", "candidate_id", args.candidate)
    if not cand:
        raise SystemExit(f"candidate {args.candidate} not found")

    print(f"[fetch_public_evidence] GET {args.url}")
    r = requests.get(args.url, headers={"User-Agent": UA}, timeout=20)
    r.raise_for_status()
    title, text = extract_text(r.text)
    snippet = text[:MAX_SNIPPET_CHARS]

    path = STATE_DIR / "evidence.jsonl"
    eid = next_id(path, "E", "evidence_id")
    record = {
        "evidence_id": eid,
        "candidate_id": args.candidate,
        "url": args.url,
        "type": args.type,
        "snippet": snippet,
        "claim": f"public webpage content (title: {title or 'untitled'}) — needs human refinement",
        "tag": args.tag,
        "confidence": 0.3,
        "source": "auto_fetch",
        "page_title": title,
        "created_at": now_iso(),
    }
    append_jsonl(path, record)
    print(pretty({k: v for k, v in record.items() if k != "snippet"}))
    print(f"\n(snippet: {len(snippet)} chars stored)")
    print(f"saved -> {path}")


if __name__ == "__main__":
    main()
