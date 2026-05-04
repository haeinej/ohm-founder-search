#!/usr/bin/env python3
"""Build candidate dossiers from multiple public artifacts.

Two-pass architecture:
  Pass 1: Per-artifact extraction (one small LLM call per artifact)
  Pass 2: Aggregation into dossier (one LLM call per candidate)

This gives traceability (every claim links to a specific artifact),
better calibration, and source-weighted scoring.
"""

from __future__ import annotations

import argparse
import json
import re
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from utils import (
    CANDIDATE_FIT_WEIGHTS,
    DOSSIER_QUALITY_WEIGHTS,
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
    update_jsonl,
)

UA = "Mozilla/5.0 (compatible; ohm-founder-search/0.2; +https://example.invalid)"
FETCH_TIMEOUT = 15
FETCH_DELAY = 1.0
LLM_DELAY = 15  # seconds between LLM calls for Groq TPM
MAX_ARTIFACTS = 8
MAX_ARTIFACT_TEXT = 2000  # per artifact, for LLM prompt

# ---------------------------------------------------------------------------
# Source type classification
# ---------------------------------------------------------------------------

PLATFORM_DOMAINS = {
    "github.com": "github",
    "substack.com": "substack",
    "medium.com": "blog",
    "dev.to": "blog",
    "hackernoon.com": "blog",
    "mirror.xyz": "blog",
    "bearblog.dev": "blog",
    "notion.site": "personal_site",
    "linkedin.com": "linkedin",
    "crunchbase.com": "directory",
    "arxiv.org": "technical_essay",
    "huggingface.co": "project_page",
    "producthunt.com": "project_page",
    "youtube.com": "talk",
    "twitter.com": "social",
    "x.com": "social",
}

EXPANSION_PATHS = [
    "/about", "/projects", "/writing", "/blog", "/essays",
    "/work", "/research", "/now", "/talks", "/demos", "/portfolio",
]

EXPANSION_DOMAINS = [
    "github.com", "substack.com", "medium.com", "arxiv.org",
    "huggingface.co", "dev.to",
]

SOURCE_TYPE_INSTRUCTIONS = {
    "github": "Focus on: repo names, primary languages, commit recency signals, project complexity, README quality and substance, whether projects are toys or real systems.",
    "substack": "Focus on: thesis statements, reasoning quality, intellectual obsession, originality of framing, depth of argument, worldview coherence.",
    "blog": "Focus on: thesis statements, technical depth, writing clarity, originality, whether they explore ideas or just report them.",
    "personal_site": "Focus on: what they chose to make legible, project curation quality, self-description substance, current direction, evidence of agency and taste.",
    "technical_essay": "Focus on: research depth, novelty of approach, technical rigor, practical applicability.",
    "project_page": "Focus on: what was shipped, user-facing quality, problem framing, technical choices.",
    "default": "Focus on: key claims about the person, background signals, technical indicators, evidence of building or thinking.",
}

# Signal bucket → numeric value for scoring
BUCKET_VALUES = {"low": 0.2, "medium": 0.5, "high": 0.9}


def classify_source_type(url: str) -> str:
    """Deterministic source classification from URL domain."""
    host = urlparse(url).netloc.lower().removeprefix("www.")
    for domain, stype in PLATFORM_DOMAINS.items():
        if host == domain or host.endswith("." + domain):
            return stype
    parts = host.split(".")
    if len(parts) <= 3 and len(host) < 40:
        return "personal_site"
    return "unknown"


def fetch_page_content(url: str, max_chars: int = 4000) -> tuple[str, str, str] | None:
    """Fetch URL via requests+bs4. Returns (title, text, html) or None."""
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=FETCH_TIMEOUT)
        r.raise_for_status()
        html = r.text
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        title = (soup.title.string.strip() if soup.title and soup.title.string else "")
        text = " ".join(soup.get_text(separator=" ").split())[:max_chars]
        return title, text, html
    except Exception:
        return None


def expand_site(url: str, html: str, source_type: str) -> list[str]:
    """Extract high-signal links from a page for dossier expansion."""
    soup = BeautifulSoup(html, "html.parser")
    links: list[str] = []
    seen = {url.rstrip("/")}

    if source_type == "personal_site":
        for a in soup.find_all("a", href=True):
            href = a["href"]
            resolved = urljoin(url, href)
            parsed = urlparse(resolved)
            path = parsed.path.rstrip("/").lower()
            host = parsed.netloc.lower().removeprefix("www.")

            if parsed.netloc == urlparse(url).netloc:
                if any(path == ep or path.startswith(ep + "/") for ep in EXPANSION_PATHS):
                    norm = resolved.rstrip("/")
                    if norm not in seen:
                        seen.add(norm)
                        links.append(resolved)

            if any(host == d or host.endswith("." + d) for d in EXPANSION_DOMAINS):
                norm = resolved.rstrip("/")
                if norm not in seen:
                    seen.add(norm)
                    links.append(resolved)

    elif source_type == "github":
        for a in soup.find_all("a", href=True):
            href = a["href"]
            resolved = urljoin(url, href)
            parsed = urlparse(resolved)
            if "github.com" in parsed.netloc:
                path_parts = parsed.path.strip("/").split("/")
                if len(path_parts) == 2 and not path_parts[1].startswith("."):
                    norm = resolved.rstrip("/")
                    if norm not in seen:
                        seen.add(norm)
                        links.append(resolved)

    elif source_type in ("substack", "blog"):
        base_host = urlparse(url).netloc
        for a in soup.find_all("a", href=True):
            href = a["href"]
            resolved = urljoin(url, href)
            parsed = urlparse(resolved)
            path = parsed.path
            if parsed.netloc == base_host and len(path) > 10 and path != "/":
                norm = resolved.rstrip("/")
                if norm not in seen:
                    seen.add(norm)
                    links.append(resolved)

    return links[:MAX_ARTIFACTS]


def deduplicate_urls(urls: list[str]) -> list[str]:
    """Remove duplicate URLs by normalized form."""
    seen: set[str] = set()
    out: list[str] = []
    for u in urls:
        norm = urlparse(u)._replace(fragment="").geturl().rstrip("/").lower()
        if norm not in seen:
            seen.add(norm)
            out.append(u)
    return out


# ---------------------------------------------------------------------------
# Pass 1: Per-artifact extraction
# ---------------------------------------------------------------------------

def extract_single_artifact(
    client,
    candidate: dict,
    artifact: dict,
    intent: dict,
) -> dict:
    """One small LLM call per artifact. Returns structured extraction."""
    source_type = artifact["source_type"]
    instructions = SOURCE_TYPE_INSTRUCTIONS.get(source_type, SOURCE_TYPE_INSTRUCTIONS["default"])

    template = read_prompt("extract_artifact.txt")
    prompt = (
        template
        .replace("{intent_summary}", intent.get("question", ""))
        .replace("{candidate_name}", candidate.get("name", "Unknown"))
        .replace("{source_type}", source_type)
        .replace("{artifact_url}", artifact["url"])
        .replace("{source_type_instructions}", instructions)
        .replace("{artifact_text}", artifact["text"][:MAX_ARTIFACT_TEXT])
    )

    return call_llm_json(
        client,
        system_prompt=prompt,
        user_message="Extract evidence from this artifact. JSON only.",
        max_tokens=768,
    )


# ---------------------------------------------------------------------------
# Pass 2: Aggregation into dossier
# ---------------------------------------------------------------------------

def aggregate_into_dossier(
    client,
    candidate: dict,
    artifact_extractions: list[dict],
    intent: dict,
) -> dict:
    """One LLM call to synthesize per-artifact extractions into dossier."""
    # Format extractions for the prompt
    extraction_blocks = []
    for ae in artifact_extractions:
        block = json.dumps(ae, ensure_ascii=False, indent=1)
        extraction_blocks.append(block)

    extractions_text = "\n\n".join(extraction_blocks)

    # Truncate if too long
    if len(extractions_text) > 3000:
        extractions_text = extractions_text[:3000] + "\n... (truncated)"

    template = read_prompt("enrich_extract.txt")
    prompt = (
        template
        .replace("{intent_summary}", intent.get("question", ""))
        .replace("{candidate_name}", candidate.get("name", "Unknown"))
        .replace("{candidate_url}", candidate.get("url", ""))
        .replace("{artifact_extractions}", extractions_text)
    )

    return call_llm_json(
        client,
        system_prompt=prompt,
        user_message="Aggregate into candidate dossier. JSON only.",
        max_tokens=1024,
    )


# ---------------------------------------------------------------------------
# Scoring — hard structure + bucketed soft signals
# ---------------------------------------------------------------------------

def bucket_to_float(bucket: str | float | None) -> float:
    """Convert signal bucket to numeric. Accepts 'low'/'medium'/'high' or floats."""
    if bucket is None:
        return 0.0
    if isinstance(bucket, (int, float)):
        return float(bucket)
    return BUCKET_VALUES.get(str(bucket).lower(), 0.0)


def compute_dossier_quality_score(
    artifact_count: int,
    source_types: list[str],
    root_source_type: str,
) -> float:
    """Pure deterministic scoring — do we have enough evidence?"""
    w = DOSSIER_QUALITY_WEIGHTS

    ac = 1.0 if artifact_count >= 3 else (0.6 if artifact_count == 2 else 0.3)
    n_types = len(set(source_types))
    sd = 1.0 if n_types >= 3 else (0.6 if n_types == 2 else 0.3)
    ps = 1.0 if root_source_type == "personal_site" else 0.0
    ba = 1.0 if any(t in ("github", "project_page") for t in source_types) else 0.0
    wa = 1.0 if any(t in ("substack", "blog", "technical_essay") for t in source_types) else 0.0
    fr = 0.5

    return round(
        w["artifact_count"] * ac
        + w["source_diversity"] * sd
        + w["personal_site_root"] * ps
        + w["build_artifact"] * ba
        + w["writing_artifact"] * wa
        + w["freshness"] * fr,
        3,
    )


def compute_candidate_fit_score(signals: dict) -> float:
    """Convert bucketed signals to weighted fit score."""
    w = CANDIDATE_FIT_WEIGHTS
    score = 0.0
    for key, weight in w.items():
        val = signals.get(key)
        score += weight * bucket_to_float(val)

    performative = 1.0 if signals.get("performative_flag") else 0.0
    score *= (1 - 0.3 * performative)
    return round(min(max(score, 0.0), 1.0), 3)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    p = argparse.ArgumentParser(
        description="Build candidate dossiers from public artifacts (two-pass: per-artifact → aggregation)."
    )
    p.add_argument("--intent", required=True, help="intent_id, e.g. I001")
    p.add_argument("--limit", type=int, default=10, help="max candidates to enrich")
    p.add_argument("--candidate", help="enrich a specific candidate_id")
    p.add_argument("--dry-run", action="store_true", help="print without writing")
    args = p.parse_args()

    intent = find_by_id(STATE_DIR / "intents.jsonl", "intent_id", args.intent)
    if not intent:
        raise SystemExit(f"intent {args.intent} not found")

    client = load_env()

    candidates_path = STATE_DIR / "candidates.jsonl"
    evidence_path = STATE_DIR / "evidence.jsonl"
    dossier_path = STATE_DIR / "candidate_dossiers.jsonl"

    all_candidates = load_jsonl(candidates_path)
    existing_dossiers = {d["candidate_id"] for d in load_jsonl(dossier_path)}

    if args.candidate:
        targets = [c for c in all_candidates if c["candidate_id"] == args.candidate]
        if not targets:
            raise SystemExit(f"candidate {args.candidate} not found")
    else:
        targets = [
            c for c in all_candidates
            if c.get("status") in ("needs_review", "approved_for_research", "active")
            and c["candidate_id"] not in existing_dossiers
        ][:args.limit]

    if not targets:
        print("no candidates to enrich")
        return

    print(f"enriching {len(targets)} candidates for intent {args.intent}\n")
    llm_call_count = 0

    for ci, cand in enumerate(targets):
        cid = cand["candidate_id"]
        url = cand.get("url", "")
        print(f"\n[{ci+1}/{len(targets)}] {cid}: {cand.get('name', '?')} — {url}")

        # ---- Fetch root page ----
        root_result = fetch_page_content(url)
        if not root_result:
            print(f"  failed to fetch root URL, skipping")
            continue
        root_title, root_text, root_html = root_result
        root_type = classify_source_type(url)
        print(f"  root: {root_type} ({len(root_text)} chars)")

        # ---- Expand site ----
        expansion_urls = expand_site(url, root_html, root_type)
        expansion_urls = deduplicate_urls(expansion_urls)

        artifacts = [{"url": url, "source_type": root_type, "title": root_title, "text": root_text}]

        for eu in expansion_urls:
            if len(artifacts) >= MAX_ARTIFACTS:
                break
            time.sleep(FETCH_DELAY)
            result = fetch_page_content(eu)
            if result:
                et, etext, _ = result
                etype = classify_source_type(eu)
                if len(etext) > 200:  # skip near-empty pages
                    artifacts.append({"url": eu, "source_type": etype, "title": et, "text": etext})
                    print(f"  + {etype}: {eu[:80]}")

        source_types = [a["source_type"] for a in artifacts]
        print(f"  artifacts: {len(artifacts)} ({', '.join(set(source_types))})")

        # ---- Pass 1: Per-artifact extraction ----
        artifact_extractions = []
        for ai, artifact in enumerate(artifacts):
            if llm_call_count > 0:
                time.sleep(LLM_DELAY)
            try:
                extraction = extract_single_artifact(client, cand, artifact, intent)
                extraction["_url"] = artifact["url"]
                extraction["_source_type"] = artifact["source_type"]
                artifact_extractions.append(extraction)
                llm_call_count += 1

                n_claims = len(extraction.get("claims", []))
                print(f"    artifact {ai+1}: {n_claims} claims, signals extracted")
            except Exception as e:
                print(f"    artifact {ai+1}: extraction failed: {e}")
                continue

        if not artifact_extractions:
            print(f"  no artifacts extracted, skipping")
            continue

        # ---- Pass 2: Aggregation ----
        time.sleep(LLM_DELAY)
        try:
            dossier_data = aggregate_into_dossier(client, cand, artifact_extractions, intent)
            llm_call_count += 1
        except Exception as e:
            print(f"  aggregation failed: {e}")
            continue

        # ---- Compute scores ----
        dq = compute_dossier_quality_score(len(artifacts), source_types, root_type)
        agg_signals = dossier_data.get("aggregated_signals", {})
        cf = compute_candidate_fit_score(agg_signals)

        # ---- Build dossier record ----
        did = next_id(dossier_path, "D", "dossier_id")
        dossier = {
            "dossier_id": did,
            "candidate_id": cid,
            "intent_id": args.intent,
            "root_url": url,
            "root_source_type": root_type,
            "source_urls": [a["url"] for a in artifacts],
            "source_types": list(set(source_types)),
            "artifact_count": len(artifacts),
            "summary": dossier_data.get("summary", ""),
            "build_signal": dossier_data.get("build_signal", ""),
            "thinking_signal": dossier_data.get("thinking_signal", ""),
            "taste_signal": dossier_data.get("taste_signal", ""),
            "shipping_signal": dossier_data.get("shipping_signal", ""),
            "thesis_alignment": dossier_data.get("thesis_alignment", ""),
            "missing_evidence": dossier_data.get("missing_evidence", []),
            "candidate_lacks": dossier_data.get("candidate_lacks", []),
            "candidate_strong_in": dossier_data.get("candidate_strong_in", []),
            "signal_conflicts": dossier_data.get("signal_conflicts", []),
            "aggregated_signals": agg_signals,
            "dossier_quality_score": dq,
            "candidate_fit_score": cf,
            "created_at": now_iso(),
        }

        # ---- Create evidence records from per-artifact claims ----
        new_evidence_count = 0
        for ae in artifact_extractions:
            artifact_url = ae.get("_url", url)
            artifact_type = ae.get("_source_type", "unknown")
            for claim in ae.get("claims", []):
                if not claim.get("claim"):
                    continue
                eid = next_id(evidence_path, "E", "evidence_id")
                ev = {
                    "evidence_id": eid,
                    "candidate_id": cid,
                    "url": artifact_url,
                    "type": "dossier_extraction",
                    "snippet": claim.get("quote", ""),
                    "claim": claim["claim"],
                    "tag": claim.get("tag", "general"),
                    "confidence": claim.get("confidence", 0.3),
                    "source": "dossier_enrichment",
                    "source_type": artifact_type,
                    "created_at": now_iso(),
                }
                if not args.dry_run:
                    append_jsonl(evidence_path, ev)
                new_evidence_count += 1

        if args.dry_run:
            print(f"  [dry-run] dossier quality: {dq:.2f}, fit: {cf:.2f}")
            print(f"  [dry-run] summary: {dossier['summary'][:150]}")
            print(f"  [dry-run] lacks: {dossier['candidate_lacks']}")
            print(f"  [dry-run] strong in: {dossier['candidate_strong_in']}")
            print(f"  [dry-run] {new_evidence_count} claims extracted across {len(artifact_extractions)} artifacts")
        else:
            append_jsonl(dossier_path, dossier)
            update_jsonl(
                candidates_path, "candidate_id", cid,
                {
                    "dossier_quality_score": dq,
                    "candidate_fit_score": cf,
                    "enrichment_source_types": list(set(source_types)),
                    "enrichment_status": "enriched",
                    "enriched_at": now_iso(),
                },
            )
            print(f"  dossier quality: {dq:.2f}, fit: {cf:.2f}")
            print(f"  lacks: {dossier['candidate_lacks']}")
            print(f"  strong in: {dossier['candidate_strong_in']}")
            print(f"  {new_evidence_count} claims → evidence.jsonl")
            print(f"  saved → {dossier_path}")

    print("\n" + "=" * 50)
    print(f"candidates enriched: {len(targets)}")
    print(f"total LLM calls: {llm_call_count}")
    if args.dry_run:
        print("mode: DRY RUN — nothing written")


if __name__ == "__main__":
    main()
