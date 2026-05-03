# ohm — Proxy Negotiation Cockpit (MVP)

A proxy negotiation cockpit for human discovery. Currently scoped to: **cofounder search for Haein Jung.**

## Core idea

You don't match humans by reducing them to profiles. You generate **purpose-bound proxies** for an intent, collide them, and let the collision tell you whether a first conversation is justified.

- **User proxy bundle** — generated from your private context, bound to one intent
- **Candidate proxy bundle** — generated only from public evidence
- **Proxy collision** — structured negotiation that outputs a recommendation with explicit failure modes
- **Outcome log** — what actually happened after intro, fed back into future intents

Nothing is global. Nothing is universal. Every proxy is intent-scoped and inspectable.

## Layout

```
ohm-founder-search/
├── input_sources/          # raw private context (text dumps, transcripts, notes)
├── state/                  # JSONL truth — every record append-only
├── prompts/                # model-agnostic LLM prompts
├── scripts/                # CLI for every step in the pipeline
├── credentials/            # service_account.json (gitignored)
├── .env                    # GROQ_API_KEY, GOOGLE_SHEETS_ID, ...
└── requirements.txt
```

## Setup

```bash
pip install -r requirements.txt

# fill in .env
#   GROQ_API_KEY=gsk_...        (get free key at console.groq.com)
#   GOOGLE_SHEETS_ID=...        (optional — for Sheets sync)

# drop credentials/service_account.json (Google service account JSON key)
```

## Pipeline (typical run)

```bash
# 1. add private context
python scripts/add_input_source.py --type notes --name "founder-thesis-v1" --file input_sources/thesis.md

# 2. create the intent
python scripts/create_intent.py --type cofounder --question "who should I talk to about X?"

# 3. generate user proxy bundle, then approve it
python scripts/generate_user_proxy_bundle.py --intent I001
python scripts/approve_user_proxy_bundle.py --id UPB001

# 4. add a candidate + evidence
python scripts/add_candidate.py --name "Jane Doe" --url "https://janedoe.com" --reason "shipped X"
python scripts/fetch_public_evidence.py --candidate C001 --url "https://janedoe.com/blog/post"
python scripts/add_evidence.py --candidate C001 --url "..." --type writing --snippet "..." --claim "..." --tag thesis_alignment --confidence 0.7

# 5. generate candidate proxy bundle
python scripts/generate_candidate_proxy_bundle.py --candidate C001

# 6. instantiate proxy agents and run dialogue
python scripts/instantiate_user_proxy_agent.py --user-proxy UPB001
python scripts/instantiate_candidate_proxy_agent.py --candidate-proxy CPB001
python scripts/run_proxy_dialogue.py --user-agent UPA001 --candidate-agent CPA001

# 7. collide + negotiate
python scripts/collide_and_negotiate.py --intent I001 --user-proxy UPB001 --candidate C001

# 8. rank, draft, send (manually), log outcome
python scripts/rank_collisions.py --intent I001
python scripts/draft_outreach.py --negotiation N001
python scripts/log_outcome.py --candidate C001 --negotiation N001

# 9. periodic batch analysis
python scripts/analyze_batch.py --intent I001 --last 10

# 10. sync with Google Sheets (for human edits)
python scripts/sync_sheets.py --push
python scripts/sync_sheets.py --pull
```

## Next manual steps

1. Fill in `.env` (`GROQ_API_KEY`, and optionally `GOOGLE_SHEETS_ID`)
2. Drop `credentials/service_account.json` (Google service account, share the Sheet with its email)
3. Add your first input sources to `input_sources/` and register them via `add_input_source.py`
