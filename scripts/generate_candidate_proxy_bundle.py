#!/usr/bin/env python3
"""Generate a public-evidence candidate proxy bundle via Groq.

With --research the script runs up to MAX_RESEARCH_ROUNDS of evidence
enrichment: after each LLM call it checks suggested_research, fetches
any suggested public URLs, adds them as low-confidence evidence, and
re-runs — stopping when evidence gaps are resolved or the round limit
is reached.
"""

from __future__ import annotations

import argparse
import json
import re
from typing import Any

import requests
from bs4 import BeautifulSoup

from utils import (
    STATE_DIR,
    append_jsonl,
    call_llm_json,
    check_enrichment_gate,
    find_all_by,
    find_by_id,
    load_env,
    next_id,
    now_iso,
    pretty,
    read_prompt,
    render_evidence,
)

MAX_RESEARCH_ROUNDS = 2


def fetch_url_text(url: str, max_chars: int = 3000) -> str | None:
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        text = re.sub(r"\s+", " ", soup.get_text(separator=" ")).strip()
        return text[:max_chars]
    except Exception as e:
        print(f"  [fetch] failed {url}: {e}")
        return None


def add_evidence_record(candidate_id: str, url: str, snippet: str, reason: str) -> dict[str, Any]:
    evidence_path = STATE_DIR / "evidence.jsonl"
    ev_id = next_id(evidence_path, "E", "evidence_id")
    record = {
        "evidence_id": ev_id,
        "candidate_id": candidate_id,
        "url": url,
        "type": "auto_fetched",
        "retrieved_at": now_iso(),
        "snippet": snippet,
        "claim": reason,
        "tag": "auto_research",
        "confidence": "low",
    }
    append_jsonl(evidence_path, record)
    print(f"  [research] added evidence {ev_id} from {url}")
    return record


def run_bundle_generation(client: Any, candidate: dict, evidence: list[dict], template: str) -> dict:
    system_prompt = template.replace("{candidate}", json.dumps(candidate, ensure_ascii=False, indent=2))
    system_prompt = system_prompt.replace("{candidate_evidence}", render_evidence(evidence))
    return call_llm_json(
        client,
        system_prompt=system_prompt,
        user_message="Generate the candidate proxy bundle now. JSON only.",
        max_tokens=4096,
    )


def main() -> None:
    p = argparse.ArgumentParser(description="Generate candidate proxy bundle.")
    p.add_argument("--candidate", required=True, help="candidate_id, e.g. C001")
    p.add_argument(
        "--research",
        action="store_true",
        help="enable research loop: fetch suggested_research URLs and re-run up to 2 rounds",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="bypass dossier quality gate",
    )
    args = p.parse_args()

    cand = find_by_id(STATE_DIR / "candidates.jsonl", "candidate_id", args.candidate)
    if not cand:
        raise SystemExit(f"candidate {args.candidate} not found")

    # Dossier quality gate
    dossier = find_by_id(
        STATE_DIR / "candidate_dossiers.jsonl", "candidate_id", args.candidate
    )
    passed, reason = check_enrichment_gate(cand, dossier)
    if not passed and not args.force:
        raise SystemExit(
            f"gate blocked: {reason}\n"
            "Run enrich_candidates.py first, or use --force to override."
        )

    evidence = find_all_by(STATE_DIR / "evidence.jsonl", "candidate_id", args.candidate)
    if not evidence:
        raise SystemExit(
            f"refusing — no evidence for {args.candidate}. "
            "Add evidence first via add_evidence.py / fetch_public_evidence.py."
        )

    template = read_prompt("generate_candidate_proxy_bundle.txt")
    client = load_env()

    rounds_done = 0
    fetched_urls: set[str] = set()

    while True:
        rounds_done += 1
        print(f"[generate_candidate_proxy_bundle] round {rounds_done} — {len(evidence)} evidence items for {args.candidate}")
        bundle = run_bundle_generation(client, cand, evidence, template)

        if not args.research:
            break

        suggestions = bundle.get("suggested_research") or []
        new_suggestions = [s for s in suggestions if s.get("url") and s["url"] not in fetched_urls]

        if not new_suggestions or rounds_done > MAX_RESEARCH_ROUNDS:
            if new_suggestions:
                print(f"[research] round limit reached ({MAX_RESEARCH_ROUNDS}), stopping — gaps remain in suggested_research")
            else:
                print("[research] no new URLs suggested — evidence sufficient")
            break

        print(f"[research] {len(new_suggestions)} URL(s) to fetch")
        added = 0
        for s in new_suggestions:
            url = s["url"]
            fetched_urls.add(url)
            text = fetch_url_text(url)
            if text:
                rec = add_evidence_record(args.candidate, url, text, s.get("reason", ""))
                evidence.append(rec)
                added += 1

        if added == 0:
            print("[research] no URLs successfully fetched — stopping")
            break

    path = STATE_DIR / "candidate_proxy_bundles.jsonl"
    cpb_id = bundle.get("candidate_proxy_bundle_id") or next_id(path, "CPB", "candidate_proxy_bundle_id")
    record = {
        **bundle,
        "candidate_proxy_bundle_id": cpb_id,
        "candidate_id": args.candidate,
        "research_rounds": rounds_done,
        "created_at": now_iso(),
    }
    append_jsonl(path, record)
    print(pretty(record))
    print(f"\nsaved -> {path}")


if __name__ == "__main__":
    main()
