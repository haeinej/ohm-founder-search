# ohm — Context-Grounded Human Discovery

A reasoning pipeline for finding people worth talking to. Not a matching engine — a system that generates purpose-bound representations, derives encounter-specific variables, and designs conversations that test whether a possibility is real.

Currently scoped to: **founder search for Haein Jung** (cofounders, collaborators, investors, advisors in SG / globally).

## What this is

Most people-finding tools reduce humans to profiles and match on similarity. ohm does something different:

1. **Purpose-bound representation** — the system doesn't encode a person universally. It generates a temporary model of the user and each candidate, scoped to one specific intent, grounded in evidence, aware of what it doesn't know.

2. **Derived collision variables** — instead of scoring everyone on the same fixed fields, the system derives max 5 variables per encounter that emerge from the interface between the user's intent-bound state and the candidate's current position.

3. **Conversation strategy, not compatibility score** — the output is not "you're a 78% match." It's "here's the specific hypothesis this conversation would test, what to ask, what to offer, what not to say, and what would invalidate the lead."

Nothing is global. Nothing is universal. Every representation is intent-scoped and inspectable.

## How it works

```
Intent
  → Intent-Bound User Profile (which parts of me matter for THIS search)
  → Search Lens (what to look for + variable hypotheses)
  → Exa Search (source-mode-aware: narrative, github, artifact, broad, verification)
  → Node Interpretation (generative labels + stable functions)
  → Node Expansion (containers → people)
  → Dossier Enrichment (per-artifact extraction → aggregation)
  → Position Profile (where are they standing NOW)
  → Derived Collision Variables (max 5, evidence-linked, per-encounter)
  → Conversation Value Gate (is this conversation worth having)
  → Proxy Collision (hypothesis test on highest-upside variable)
  → Conversation Strategy (angles, questions, offers, what not to say)
  → Outreach → Outcome Log → Batch Reflection → Calibration
```

## Key concepts

**Node functions** (stable across all intents):
- `direct_human` — a person to contact
- `container` — gathers relevant people (company, fund, accelerator, event)
- `artifact` — reveals thinking, skill, or taste (essay, repo, project)
- `access_path` — helps reach someone
- `context_signal` — helps understand a field or scene
- `opportunity_surface` — where future relevant encounters may appear

**Action grammar** (stable):
`contact_directly` · `extract_people` · `gather_more_evidence` · `use_as_context` · `find_access_path` · `monitor_later` · `reject`

**Source hierarchy**:
- Writing (Substack, blogs) → how someone thinks
- GitHub / projects → what someone builds
- Personal websites → what they chose to make legible
- LinkedIn → graph position and reachability (verification, not discovery)
- Company / fund pages → ecosystem position
- Talks / podcasts → conviction and communication style

## Layout

```
ohm-founder-search/
├── input_sources/     # 20 private context docs (ohm thesis, manifesto, specs, notes)
├── state/             # 20 JSONL files — append-only truth
├── prompts/           # 21 LLM prompt templates
├── scripts/           # 32 Python CLI scripts
├── credentials/       # gitignored
├── .env               # GROQ_API_KEY, EXA_API_KEY, GOOGLE_SHEETS_ID
└── requirements.txt
```

## Setup

```bash
pip install -r requirements.txt

# .env
GROQ_API_KEY=gsk_...           # console.groq.com (free tier works)
EXA_API_KEY=...                # dashboard.exa.ai
GOOGLE_SHEETS_ID=...           # created by setup_sheets.py
```

For Google Sheets sync:
1. Create OAuth Desktop App credentials at console.cloud.google.com
2. Save JSON to `~/.config/ohm/google_credentials.json`
3. Run `python scripts/setup_sheets.py` (creates spreadsheet, saves ID to .env)

## Pipeline (full run)

```bash
# 0. Add private context
python scripts/add_input_source.py --type notes --name "thesis" --file input_sources/ohm.md

# 1. Create intent
python scripts/create_intent.py --type collaborator \
  --question "Who in Singapore should I talk to about ohm?"

# 2. Generate intent-bound user profile
python scripts/generate_intent_bound_user_profile.py --intent I002

# 3. Generate search lens
python scripts/generate_search_lens.py --intent I002

# 4. Search (source-mode-aware)
python scripts/search_candidates_exa.py --intent I002 --source-mode narrative_first --limit 10
python scripts/search_candidates_exa.py --intent I002 --source-mode github_first --limit 10

# 5. Interpret search results as nodes
python scripts/interpret_node.py --intent I002 --limit 20

# 6. Reflect on batch quality (stop if noise)
python scripts/reflect_on_batch.py --intent I002

# 7. Expand non-person nodes (companies → founders, funds → partners)
python scripts/expand_node.py --intent I002

# 8. Enrich person nodes (multi-artifact dossier)
python scripts/enrich_candidates.py --intent I002 --limit 5

# 9. Generate position profiles
python scripts/generate_position_dossier.py --intent I002

# 10. Derive collision variables (per-encounter, max 5)
python scripts/derive_collision_variables.py --intent I002 --node N001

# 11. Score conversation value (gate)
python scripts/score_conversation_value.py --intent I002

# 12. Generate proxy bundles + collide
python scripts/generate_user_proxy_bundle.py --intent I002
python scripts/approve_user_proxy_bundle.py --id UPB001
python scripts/generate_candidate_proxy_bundle.py --candidate C076
python scripts/collide_and_negotiate.py --intent I002 --user-proxy UPB001 --candidate C076

# 13. Draft outreach + log outcome
python scripts/draft_outreach.py --negotiation N001
python scripts/log_outcome.py --candidate C076 --negotiation N001

# 14. Batch analysis (feedback loop)
python scripts/analyze_batch.py --intent I002

# 15. Sync to Google Sheets
python scripts/sync_sheets.py --push
```

## Current state

**What exists:**
- 32 scripts implementing the full pipeline from intent to outreach
- 20 input sources (ohm concept docs, manifesto, thesis, tech specs)
- 2 intents (cofounder search global, collaborator search SG)
- 100 candidates searched, 25 classified as nodes, 3 dossiers built, 3 collisions run
- Google Sheets sync (OAuth, 20 tabs)
- Outcome logging with full search provenance tracing

**What works end-to-end:**
- Exa search with source modes (narrative_first, github_first, artifact_first, broad, verification)
- Two-pass dossier enrichment (per-artifact extraction → aggregation)
- Proxy collision producing conversation strategy (not just compatibility scores)
- Dossier quality gate before proxy generation
- Batch reflection that stops enrichment when search quality is low

## Where this is going

The system should become a **context-grounded human discovery engine** — not a matching system.

The core question is not "who is similar to me?" but "given where I'm standing, which person could change my next move, and what conversation would reveal whether that's real?"

**Near-term:**
- Wire derived collision variables into the collision prompt
- Build skeptical reviewer stage (challenge the system's own reasoning before recommendation)
- Richer human feedback labels (reject_generic, reject_wrong_stage, container_extract_people, etc.)
- Cross-mode source comparison (does narrative_first or github_first better predict good conversations?)

**Medium-term:**
- Calibration loop: outcomes → scoring weight adjustments → query refinements
- Counterfactual tracking (who we didn't reach out to)
- Fine-tune narrow tasks (source classification, noise rejection) after 100+ labeled records

**Not doing yet:**
- Universal profiles or embeddings
- Fine-tuning the strategic reasoning layer
- Any matching that isn't intent-scoped

## Design principles

1. **Variables are outputs of reasoning, not inputs.** The system derives what matters per encounter, not scores everyone on the same fields.
2. **The primitive is purpose-bound representation.** Not a profile — a temporary model valid for one decision.
3. **Generative labels, stable functions.** Node types are free-form descriptions. Node functions are fixed (direct_human, container, artifact, access_path, context_signal, opportunity_surface).
4. **Evidence discipline.** Every claim links to a source. Inferences are labeled. Speculative assumptions are explicit.
5. **The output is a conversation, not a score.** The system succeeds when it helps start a conversation that changes the next move.
