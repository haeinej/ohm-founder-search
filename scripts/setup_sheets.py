#!/usr/bin/env python3
"""Create the ohm Proxy Negotiation Cockpit Google Spreadsheet.

Uses Google OAuth2 (installed-app flow) to authenticate as the user and creates
a fresh spreadsheet with all 11 cockpit tabs and headers. Stores the sheet id
in the project .env as GOOGLE_SHEETS_ID and prints the sheet URL.
"""

from __future__ import annotations

import sys
from pathlib import Path

import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

PROJECT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT / ".env"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

CREDS_DIR = Path.home() / ".config" / "ohm"
CREDS_PATH = CREDS_DIR / "google_credentials.json"
TOKEN_PATH = CREDS_DIR / "google_token.json"

SPREADSHEET_TITLE = "ohm — Proxy Negotiation Cockpit"

TABS: list[tuple[str, list[str]]] = [
    (
        "Input Sources",
        [
            "source_id", "user_id", "source_type", "source_name",
            "source_url_or_file", "included_for_extraction",
            "raw_text_or_excerpt", "last_ingested", "notes",
        ],
    ),
    (
        "Intents",
        [
            "intent_id", "user_id", "intent_type", "user_question",
            "desired_outcome", "proxy_dimensions", "success_criteria",
            "disclosure_policy", "status",
        ],
    ),
    (
        "User Proxy Bundles",
        [
            "user_proxy_bundle_id", "intent_id", "generated_from_sources",
            "technical_need_proxy", "product_thesis_proxy",
            "collaboration_style_proxy", "offer_proxy", "dealbreaker_proxy",
            "uncertainties_for_user_review", "user_approved", "approved_at",
        ],
    ),
    (
        "Candidates",
        [
            "candidate_id", "name_or_handle", "candidate_url", "source_channel",
            "raw_reason_found", "candidate_type_guess", "date_sourced", "status",
        ],
    ),
    (
        "Evidence",
        [
            "evidence_id", "candidate_id", "source_url", "source_type",
            "retrieved_at", "evidence_snippet", "observed_claim",
            "relevance_tag", "confidence",
        ],
    ),
    (
        "Candidate Proxy Bundles",
        [
            "candidate_proxy_bundle_id", "candidate_id",
            "generated_from_evidence", "technical_evidence_proxy",
            "thesis_interest_proxy", "shipping_execution_proxy",
            "taste_originality_proxy", "availability_timing_proxy",
            "proxy_confidence", "created_at",
        ],
    ),
    (
        "Proxy Agents",
        [
            "proxy_agent_id", "proxy_type", "linked_proxy_bundle_id",
            "candidate_id", "intent_id", "role", "evidence_base",
            "inferred_lens", "allowed_capabilities", "forbidden_actions",
            "allowed_tools", "epistemic_status", "created_at",
        ],
    ),
    (
        "Proxy Dialogues",
        [
            "dialogue_id", "intent_id", "user_proxy_agent_id",
            "candidate_proxy_agent_id", "round_1_user_position",
            "round_2_candidate_counterposition", "round_3_user_clarification",
            "round_4_candidate_intro_threshold", "candidate_objections",
            "candidate_questions", "user_safe_disclosures",
            "representation_loss", "minimum_viable_conversation",
            "mediator_recommendation", "intro_recommendation",
            "first_question", "suggested_message", "confidence", "created_at",
        ],
    ),
    (
        "Collisions / Negotiations",
        [
            "collision_id", "intent_id", "user_proxy_bundle_id",
            "candidate_proxy_bundle_id", "shared_context", "collision_summary",
            "representation_loss", "possible_mutual_value",
            "productive_difference", "main_mismatch", "unsafe_assumptions",
            "minimum_viable_first_conversation", "first_question_to_ask",
            "recommended_conversation_type", "intro_recommendation",
            "confidence", "what_would_change_the_decision",
            "suggested_message", "created_at",
        ],
    ),
    (
        "Outcomes",
        [
            "outcome_id", "candidate_id", "collision_id", "outreach_date",
            "outreach_channel", "message_used", "replied",
            "conversation_happened", "conversation_date", "thesis_challenged",
            "technically_credible", "mutual_energy", "want_second_conversation",
            "referred_someone", "result_category", "what_surprised_you",
            "what_proxy_missed", "update_proxy_or_rubric",
        ],
    ),
    (
        "Batch Analysis",
        [
            "batch_id", "date_run", "candidate_count", "overvalued_signals",
            "undervalued_signals", "new_positive_signals",
            "new_negative_signals", "query_adjustments", "proxy_adjustments",
            "rubric_adjustments", "state_update_suggestions", "human_approved",
        ],
    ),
    (
        "Candidate Dossiers",
        [
            "dossier_id", "candidate_id", "intent_id", "root_url",
            "root_source_type", "source_urls", "source_types",
            "artifact_count", "summary", "build_signal", "thinking_signal",
            "taste_signal", "shipping_signal", "thesis_alignment",
            "missing_evidence", "dossier_quality_score", "candidate_fit_score",
            "created_at",
        ],
    ),
]


def get_credentials() -> Credentials:
    CREDS_DIR.mkdir(parents=True, exist_ok=True)

    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
        if creds and creds.valid:
            return creds
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            TOKEN_PATH.write_text(creds.to_json())
            return creds

    if not CREDS_PATH.exists():
        print("To set up Google Sheets, you need Google OAuth credentials.")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a project, enable Google Sheets API and Google Drive API")
        print("3. Create OAuth 2.0 credentials (Desktop App)")
        print(f"4. Download the JSON and save it to: {CREDS_PATH}")
        print("\nOnce saved, run this script again.")
        sys.exit(0)

    flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_PATH), SCOPES)
    creds = flow.run_local_server(port=0)
    TOKEN_PATH.write_text(creds.to_json())
    return creds


def upsert_env(key: str, value: str) -> None:
    lines: list[str] = []
    if ENV_FILE.exists():
        lines = ENV_FILE.read_text().splitlines()
    found = False
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}"
            found = True
            break
    if not found:
        lines.append(f"{key}={value}")
    ENV_FILE.write_text("\n".join(lines) + "\n")


def main() -> None:
    creds = get_credentials()
    gc = gspread.authorize(creds)

    print(f"Creating spreadsheet: {SPREADSHEET_TITLE}")
    sh = gc.create(SPREADSHEET_TITLE)

    # Rename first sheet to first tab; add the rest
    first_title, first_headers = TABS[0]
    default_ws = sh.sheet1
    default_ws.update_title(first_title)
    default_ws.update("A1", [first_headers])

    for title, headers in TABS[1:]:
        ws = sh.add_worksheet(title=title, rows=200, cols=max(26, len(headers) + 2))
        ws.update("A1", [headers])

    sheet_id = sh.id
    sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}"

    upsert_env("GOOGLE_SHEETS_ID", sheet_id)

    print()
    print(f"GOOGLE_SHEETS_ID={sheet_id}")
    print(f"URL: {sheet_url}")
    print(f"Saved id to {ENV_FILE}")


if __name__ == "__main__":
    main()
