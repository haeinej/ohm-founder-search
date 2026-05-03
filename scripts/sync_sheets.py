#!/usr/bin/env python3
"""Sync local JSONL state <-> Google Sheets.

push: read all state JSONL, upsert into sheet tabs (by id field).
pull: read sheet tabs, overwrite local JSONL (so the human can edit in sheets).
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

from utils import ROOT, STATE_DIR, load_jsonl

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Tab name -> (jsonl filename, id field)
TABS: list[tuple[str, str, str]] = [
    ("Input Sources", "input_sources.jsonl", "source_id"),
    ("Intents", "intents.jsonl", "intent_id"),
    ("User Proxy Bundles", "user_proxy_bundles.jsonl", "user_proxy_bundle_id"),
    ("Candidates", "candidates.jsonl", "candidate_id"),
    ("Evidence", "evidence.jsonl", "evidence_id"),
    ("Candidate Proxy Bundles", "candidate_proxy_bundles.jsonl", "candidate_proxy_bundle_id"),
    ("Proxy Agents", "proxy_agents.jsonl", "user_proxy_agent_id"),
    ("Proxy Dialogues", "proxy_dialogues.jsonl", "proxy_dialogue_id"),
    ("Collisions", "collisions.jsonl", "collision_id"),
    ("Outcomes", "outcomes.jsonl", "outcome_id"),
    ("Batch Analysis", "batch_analyses.jsonl", "batch_analysis_id"),
]


def get_client():
    load_dotenv(ROOT / ".env")
    sa_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "credentials/service_account.json")
    sa_path = Path(sa_path)
    if not sa_path.is_absolute():
        sa_path = ROOT / sa_path
    if not sa_path.exists():
        raise SystemExit(f"service account file not found: {sa_path}")
    sheet_id = os.getenv("GOOGLE_SHEETS_ID", "").strip()
    if not sheet_id:
        raise SystemExit("GOOGLE_SHEETS_ID not set in .env")
    creds = Credentials.from_service_account_file(str(sa_path), scopes=SCOPES)
    gc = gspread.authorize(creds)
    return gc.open_by_key(sheet_id)


def get_or_create_ws(book, title: str):
    try:
        return book.worksheet(title)
    except gspread.WorksheetNotFound:
        return book.add_worksheet(title=title, rows=200, cols=20)


def flatten(value):
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    if value is None:
        return ""
    return value


def union_keys(records: list[dict], id_field: str) -> list[str]:
    keys: list[str] = []
    if id_field:
        keys.append(id_field)
    seen = set(keys)
    for r in records:
        for k in r.keys():
            if k not in seen:
                seen.add(k)
                keys.append(k)
    return keys


def push(book) -> None:
    for tab_title, fname, id_field in TABS:
        records = load_jsonl(STATE_DIR / fname)
        ws = get_or_create_ws(book, tab_title)
        if not records:
            ws.clear()
            ws.update("A1", [[id_field or "id", "(empty)"]])
            print(f"  [push] {tab_title:<28} 0 rows (cleared)")
            continue
        cols = union_keys(records, id_field)
        rows = [cols] + [[flatten(r.get(c, "")) for c in cols] for r in records]
        ws.clear()
        ws.update("A1", rows)
        print(f"  [push] {tab_title:<28} {len(records)} rows, {len(cols)} cols")


def parse_cell(value: str):
    if not isinstance(value, str):
        return value
    if value == "":
        return ""
    if (value.startswith("{") and value.endswith("}")) or (value.startswith("[") and value.endswith("]")):
        try:
            return json.loads(value)
        except Exception:
            return value
    return value


def pull(book) -> None:
    for tab_title, fname, id_field in TABS:
        try:
            ws = book.worksheet(tab_title)
        except gspread.WorksheetNotFound:
            print(f"  [pull] {tab_title:<28} (no tab — skipping)")
            continue
        rows = ws.get_all_values()
        if not rows or len(rows) < 2:
            print(f"  [pull] {tab_title:<28} (empty)")
            continue
        header = rows[0]
        records = []
        for r in rows[1:]:
            d = {h: parse_cell(v) for h, v in zip(header, r) if h}
            if id_field and not d.get(id_field):
                continue
            records.append(d)
        out = STATE_DIR / fname
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"  [pull] {tab_title:<28} {len(records)} rows -> {out}")


def main() -> None:
    p = argparse.ArgumentParser(description="Sync state with Google Sheets.")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--push", action="store_true", help="local JSONL -> Sheets")
    g.add_argument("--pull", action="store_true", help="Sheets -> local JSONL")
    args = p.parse_args()

    book = get_client()
    print(f"opened sheet: {book.title}")
    if args.push:
        push(book)
    else:
        pull(book)


if __name__ == "__main__":
    main()
