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


def load_env():
    """Load .env and return a Groq client. Raises if key missing."""
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "GROQ_API_KEY is empty in .env — fill it in before running this script."
        )
    from groq import Groq

    return Groq(api_key=key)


GROQ_MODEL = "llama-3.3-70b-versatile"


def call_llm_json(
    client,
    system_prompt: str,
    user_message: str,
    *,
    max_tokens: int = 4096,
    cache_system: bool = True,
    extra_cache_blocks: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Call Groq LLM and return parsed JSON dict (markdown fences stripped if present)."""
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
