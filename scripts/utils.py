"""Shared utilities for ohm-founder-search scripts."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / "state"
PROMPTS_DIR = ROOT / "prompts"
INPUT_DIR = ROOT / "input_sources"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    path = Path(path)
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line))
    return out


def append_jsonl(path: str | Path, record: dict[str, Any]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def update_jsonl(
    path: str | Path,
    id_field: str,
    id_value: str,
    updates: dict[str, Any],
) -> dict[str, Any] | None:
    """Rewrite the file with updated record. Returns updated record or None."""
    path = Path(path)
    records = load_jsonl(path)
    updated: dict[str, Any] | None = None
    for r in records:
        if r.get(id_field) == id_value:
            r.update(updates)
            updated = r
    if updated is None:
        return None
    with path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return updated


def next_id(path: str | Path, prefix: str, id_field: str, width: int = 3) -> str:
    """Compute the next sequential id like S001, S002, ..."""
    records = load_jsonl(path)
    pat = re.compile(rf"^{re.escape(prefix)}(\d+)$")
    max_n = 0
    for r in records:
        m = pat.match(str(r.get(id_field, "")))
        if m:
            try:
                max_n = max(max_n, int(m.group(1)))
            except ValueError:
                pass
    return f"{prefix}{max_n + 1:0{width}d}"


def find_by_id(
    path: str | Path, id_field: str, id_value: str
) -> dict[str, Any] | None:
    for r in load_jsonl(path):
        if r.get(id_field) == id_value:
            return r
    return None


def find_all_by(
    path: str | Path, field: str, value: Any
) -> list[dict[str, Any]]:
    return [r for r in load_jsonl(path) if r.get(field) == value]


def read_prompt(name: str) -> str:
    p = PROMPTS_DIR / name
    return p.read_text(encoding="utf-8")


class ClaudeCLIClient:
    """LLM client that shells out to the `claude` CLI (uses Max plan, no API key)."""
    pass


def load_env():
    """Load .env and return an LLM client. Priority: claude CLI > Anthropic API > Groq."""
    from dotenv import load_dotenv
    import subprocess

    load_dotenv(ROOT / ".env")

    # Check LLM_BACKEND override
    backend = os.getenv("LLM_BACKEND", "").strip().lower()

    # 1. Claude CLI (Max plan — no API key needed)
    if backend == "claude_cli" or (not backend and not os.getenv("ANTHROPIC_API_KEY", "").strip()):
        try:
            subprocess.run(["claude", "--version"], capture_output=True, check=True, timeout=5)
            print("[llm] using claude CLI (Max plan)")
            return ClaudeCLIClient()
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pass

    # 2. Anthropic API
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if anthropic_key:
        import anthropic
        print("[llm] using Anthropic API")
        return anthropic.Anthropic(api_key=anthropic_key)

    # 3. Groq
    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    if groq_key:
        from groq import Groq
        print("[llm] using Groq API")
        return Groq(api_key=groq_key)

    raise RuntimeError(
        "No LLM backend available.\n"
        "Options: install claude CLI (Max plan), set ANTHROPIC_API_KEY, or set GROQ_API_KEY."
    )


GROQ_MODEL = "llama-3.3-70b-versatile"
CLAUDE_MODEL = "claude-sonnet-4-20250514"


def _call_claude_cli(system_prompt: str, user_message: str, max_tokens: int) -> str:
    """Call claude CLI with --print flag. Returns raw text response."""
    import subprocess

    full_prompt = f"{system_prompt}\n\n{user_message}"

    result = subprocess.run(
        ["claude", "--print"],
        input=full_prompt,
        capture_output=True,
        text=True,
        timeout=300,
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude CLI failed: {result.stderr[:500]}")
    return result.stdout.strip()


def _is_anthropic_client(client) -> bool:
    return type(client).__module__.startswith("anthropic")


def _is_claude_cli(client) -> bool:
    return isinstance(client, ClaudeCLIClient)


def call_llm_json(
    client,
    system_prompt: str,
    user_message: str,
    *,
    max_tokens: int = 4096,
    cache_system: bool = True,
    extra_cache_blocks: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Call LLM (Claude CLI, Anthropic API, or Groq) and return parsed JSON dict."""
    if _is_claude_cli(client):
        text = _call_claude_cli(system_prompt, user_message, max_tokens)
    elif _is_anthropic_client(client):
        resp = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        text = resp.content[0].text.strip()
    else:
        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        text = resp.choices[0].message.content.strip()
    return parse_json_response(text)


def parse_json_response(text: str) -> dict[str, Any]:
    """Strip ```json fences and parse."""
    s = text.strip()
    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?\s*", "", s)
        s = re.sub(r"\s*```$", "", s)
    s = s.strip()
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", s, re.DOTALL)
        if not m:
            raise ValueError(f"LLM response was not valid JSON:\n{text[:500]}")
        return json.loads(m.group(0))


# ---------------------------------------------------------------------------
# Dossier quality + candidate fit scoring
# ---------------------------------------------------------------------------

DOSSIER_QUALITY_WEIGHTS = {
    "artifact_count": 0.25,
    "source_diversity": 0.20,
    "personal_site_root": 0.20,
    "build_artifact": 0.15,
    "writing_artifact": 0.10,
    "freshness": 0.10,
}

CANDIDATE_FIT_WEIGHTS = {
    "thesis_alignment": 0.20,
    "shipping_signal": 0.20,
    "technical_depth": 0.15,
    "narrative_depth": 0.15,
    "taste_signal": 0.10,
    "availability_signal": 0.10,
    "warm_path": 0.05,
    "weirdness_originality": 0.05,
}

GATE_THRESHOLDS = {
    "dossier_quality_score": 0.3,
    "candidate_fit_score": 0.2,
}


def check_enrichment_gate(
    candidate: dict[str, Any], dossier: dict[str, Any] | None
) -> tuple[bool, str]:
    """Check if candidate passes the review gate for proxy generation.
    Returns (passed, reason_string).
    Passes if dossier exists AND scores above thresholds, OR human_override."""
    if candidate.get("human_override"):
        return True, "human_override"
    if dossier is None:
        return False, "no dossier — run enrich_candidates.py first"
    dq = dossier.get("dossier_quality_score", 0)
    cf = dossier.get("candidate_fit_score", 0)
    if dq < GATE_THRESHOLDS["dossier_quality_score"]:
        return False, f"dossier_quality_score {dq:.2f} < {GATE_THRESHOLDS['dossier_quality_score']}"
    if cf < GATE_THRESHOLDS["candidate_fit_score"]:
        return False, f"candidate_fit_score {cf:.2f} < {GATE_THRESHOLDS['candidate_fit_score']}"
    return True, "passed"


def needs_rate_limit(client) -> bool:
    """Returns True if the client needs rate-limit delays (Groq free tier)."""
    return not _is_claude_cli(client) and not _is_anthropic_client(client)


def pretty(record: dict[str, Any]) -> str:
    return json.dumps(record, indent=2, ensure_ascii=False)


def render_input_source(s: dict[str, Any]) -> str:
    """Render a single input source as text for prompt injection."""
    parts = [
        f"--- source_id: {s.get('source_id')} ---",
        f"type: {s.get('type')}",
        f"name: {s.get('name')}",
    ]
    if s.get("url"):
        parts.append(f"url: {s['url']}")
    if s.get("notes"):
        parts.append(f"notes: {s['notes']}")
    if s.get("file"):
        path = ROOT / s["file"] if not os.path.isabs(s["file"]) else Path(s["file"])
        if path.exists():
            try:
                content = path.read_text(encoding="utf-8")
                parts.append("content:")
                parts.append(content)
            except Exception as e:  # pragma: no cover
                parts.append(f"(could not read file: {e})")
        else:
            parts.append(f"(file not found: {path})")
    return "\n".join(parts)


def render_evidence(items: Iterable[dict[str, Any]]) -> str:
    blocks = []
    for e in items:
        blocks.append(
            "\n".join(
                [
                    f"--- evidence_id: {e.get('evidence_id')} ---",
                    f"candidate_id: {e.get('candidate_id')}",
                    f"type: {e.get('type')}",
                    f"url: {e.get('url')}",
                    f"tag: {e.get('tag')}",
                    f"confidence: {e.get('confidence')}",
                    f"claim: {e.get('claim')}",
                    f"snippet: {e.get('snippet')}",
                ]
            )
        )
    return "\n\n".join(blocks) if blocks else "(no evidence)"
