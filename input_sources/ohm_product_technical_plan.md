# # ohm — Product & Technical Plan

# ohm — Product &amp Technical Plan

*Synthesized from founder conversations, April 2026*

***

## First Principle

The most important opportunities in a person's life often arrive through another human being. Yet the internet has become extraordinarily good at helping people find information and remarkably poor at helping them find the right people.

ohm is built on the belief that AI should not only answer human questions — it should help humans find the other humans with whom those questions become alive.

***

## One-Line Description

&gt **&quotAI that finds people, not information.&quot**

***

## The Problem

People do not lack access to other people. They lack access to the *right* people. Existing platforms fail in four ways:

- **Shallow proxies** — LinkedIn represents credentials, dating apps represent appearance, social media represents performance. None capture how someone thinks, what they're becoming, or whether conversation with them would expand your life.

- **Burden on the individual** — users must manually browse, interpret fragmented signals, send cold messages, and hope the right person is visible.

- **Profile-first, not intent-first** — systems ask &quotwho are you?&quot instead of &quotwhat kind of person are you searching for right now?&quot Human compatibility is contextual.

- **AI deepens the paradox** — LLMs can answer almost any question, but some problems are solved through another human being, not through answers.

***

## Core Hypothesis

The most valuable human matches can be discovered by modeling people not as profiles, but as **evolving search states** — a history, a set of recurring questions, a current quest, a rhythm of attention, and a direction of becoming.

The role of AI is not to become the friend, lover, cofounder, or mentor. The role of AI is to help find them.

***

## North Star Metric

**Number of life-altering introductions created** — connections that lead to a company formed, a collaboration started, a mentor relationship developed, a major decision clarified, or a lasting partnership. Not DAU, not swipe volume, not time in app.

***

## Three-Phase Architecture

### Phase 1 — Cold Start: Search-Built Representations (MVP)

No users required on the candidate side. ohm aggregates public signals from arXiv, GitHub, Substack, personal sites, and professional networks via search APIs. For each person discovered, ohm builds a **directional representation** — not a profile summary, but an embedding of their trajectory, recurring questions, and intellectual obsessions.

The searcher connects their agent (via Mem0 MCP + Claude/GPT history, or a one-time JSON export of chat logs), declares a search intent in natural language, and receives 3–5 highly reasoned introductions with explanations of why each person matters, what evidence supports the match, where friction might exist, and how to open the conversation.

### Phase 2 — Live Agent Matching (6–18 months)

Users opt in to be searchable. Each user's agent holds private context via Mem0's persistent memory layer. Jean Domain Embeddings match seeker intent vectors against candidate trajectory vectors asymmetrically — the seeker representation encodes intent, not identity. Every accepted or rejected introduction feeds a feedback loop that trains a custom ohm ranker over time. The candidate pool shifts from primarily public-signal-derived to primarily opted-in user representations.

### Phase 3 — The Attractor Field (2–3 years)

Agents representing opted-in users inhabit a shared latent space, emitting context and gravitating toward resonant others without explicit queries. This is ambient discovery — closer to how discovery works in real life, where you enter a scene and certain people begin to appear repeatedly. An agent is pulled into the field when its embedding crosses a proximity threshold to an existing cluster (implemented as a semantic drift detector — a background process monitoring public digital activity). No explicit query needed. The field shapes what surfaces.

***

## Technical Stack

### Memory Layer

**Mem0** — open source, API-native, integrates with Claude and GPT via MCP. Ingests conversation history, extracts structured memories (recurring questions, values, intellectual style, trajectory, dealbreakers), and retrieves them semantically. Users connect once; every subsequent AI session enriches their ohm representation passively.

### Permission &amp App Access

**WithOne CLI** — terminal-native OAuth that grants ohm authenticated access to users' connected apps (Gmail, Notion, Slack, Calendar, etc.) in one install. Handles the consent layer without building custom auth flows.

### Candidate Search

**Happenstance API** — natural language people search across professional networks, returning candidates with warm intro paths. Powers the cold-start candidate pool without manual scraping.

### Matching Engine

**Jean Domain Embeddings** — outcome-trained embedding model + asymmetric reranker. Critically: Jean separates seeker intent from candidate identity via asymmetric matching, which maps directly to ohm's architecture. The `/feedback` → `/train` loop improves the custom ranker over time as ohm accumulates match outcome data.

### Reasoning Layer

**Claude/GPT API** — ohm's unique value over raw matching. For each candidate, the reasoning layer generates: why this person, what evidence, honest mismatch, and a specific opening move. This layer is not provided by any matching infrastructure — it is ohm's core product logic.

### Interface

**Terminal / CLI** — headless, API-first. No app, no UI in Phase 1. ohm runs as a CLI tool (`npm i -g @withone/ohm`). This is a strategic choice: the first users (founders, researchers, technical collaborators) are comfortable in a terminal, and headless infrastructure positions ohm as a protocol, not a social app.

***

## The Representation Schema (Most Critical Design Decision)

The `raw_context` fed to Jean's `/ingest` endpoint determines everything. It must encode trajectory and intent, not identity and credentials. A correctly designed representation survives from Phase 1 through Phase 3 — it is the same artifact at different levels of richness.

**Example representation for a candidate built from public signals:**

&gt &quotThis person has spent three years asking how distributed systems fail under Byzantine conditions. Their GitHub shows obsessive attention to edge cases others ignore. Their Substack essays circle back repeatedly to the question of what it means to build something that outlasts you. They are moving toward founding, not just building. Their intellectual rhythm is slow, deep, and contrarian.&quot

Jean extracts from this: Identity (contrarian deep-thinker, pre-founder), Intent (build something lasting), Vibe (slow, obsessive, independent). In Phase 2, this same schema is enriched with private context from the user's own agent. In Phase 3, it becomes the agent identity card for the latent field.

***

## MVP End-to-End Loop

```

1. CONNECT

   $ ohm connect

   → WithOne CLI auth (user approves scopes)

   → Mem0 MCP reads Claude/GPT history (user-initiated)

   → One-time Claude chat history JSON import (optional, for depth)

2. MEMORY SYNC

   Mem0 /stream ingests conversation history

   Extracts: questions, values, trajectory, style, dealbreakers

   Builds living self-model that updates with each new session

3. DECLARE INTENT

   $ ohm search &quottechnical cofounder who understands why human

     connection is broken and can build backend systems&quot

   ohm creates asymmetric seeker representation via Jean /ingest

4. MATCH

   Jean /match: seeker intent vs. candidate pool

   Pool A: public signal representations (Happenstance + scraped)

   Pool B (grows): opted-in ohm users

5. REASON

   Claude API generates per-candidate reasoning:

   WHY / EVIDENCE / MISMATCH / OPENING MOVE

6. INTRODUCE

   Terminal output: 3–5 candidates with full reasoning

   User accepts or ignores → Jean /feedback → ranker improves

   Accepted candidates receive framed invitation to join ohm

```

***

## The Cold Start Strategy

The cold start problem is less severe than it appears because Phase 1 is not a social network — it is a **search index of latent human resonance**. It has value with zero opted-in users because candidates are real people with public intellectual footprints. The first user of ohm does not need other ohm users to exist; they need the index to be good. Network effects become the mechanism only in Phase 2, by which point users have already experienced value.

As invited candidates join ohm, they enrich their own representations and become searchable. The public-data phase seeds the field; the invitation converts passive representation to active participation.

***

## Competitive Position

| Dimension | LinkedIn | Dating Apps | Jean Technologies | ohm |

|---|---|---|---|---|

| Customer | Professionals | Individuals | B2B platforms | Individuals |

| Represents | Credentials | Appearance | Compatibility score | Trajectory + intent |

| Interface | Profile browsing | Swipe | API/infrastructure | Terminal → agent field |

| Discovery model | Keyword search | Proximity + swipe | Matching engine | Ambient resonance |

| Phase 3 vision | Feed optimization | Engagement | Better ranker | Agent latent field |

Jean Technologies is the closest technical adjacent — building outcome-trained embedding infrastructure for matching platforms. ohm is the consumer experience layer and the philosophical architecture that Jean does not address. Jean could power ohm's matching engine; they are not competitors.

***

## Why Now

The agent protocol landscape (A2A, MCP, ANP) is converging on interoperability standards that make agent-to-agent communication possible. The memory layer infrastructure (Mem0, Jean Memory) is mature enough to build on. The semantic search capability (Happenstance, Perplexity API) is accessible via simple API calls. The missing piece — a product that uses all of this to help people find people — is the gap ohm fills.

The attractor field vision is 2–3 years away from being buildable as ambient infrastructure. But the representation schema, the matching engine, and the reasoning layer can be built today. The right move is to design the MVP under the constraint that every component must survive the transition to Phase 3.

***
