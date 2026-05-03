# ohm — Concept Overview

ohm — Concept Overview

ohm.’s fun layer is the feeling that someone, somewhere, is orbiting the same question as you. Instead of making users fill out heavy profiles or browse endless people, ohm. gives them small moments of recognition: “who is looking for someone like me?”, “who entered my orbit this week?”, “who is thinking about the same future from another angle?”, and “what kind of person would change my next chapter?” The product should feel less like professional networking and more like a living field of possible collisions, where your thoughts, quests, and private search states quietly attract people, projects, and conversations that make you feel found. It uses curiosity, ego, serendipity, and the desire to be recognized — but channels those desires toward meaningful introductions rather than likes, swipes, or status performance.

-&gt maybe something like biography in a short form - or auto generate someone else’s website through crawled data like the domain could be ohmmmm.com/haeinjung (which is also sharable), so there is disccovery layer but also help people make website and later on could be edited? now its auto generated showing what kind of person you are, kind of private and only discoverable through context

 “What does my public mind look like?”

One-Line Description

&quotAI that finds people, not information.&quot

First Principle

The most important opportunities in a person's life often arrive through another human being. Yet the internet has become extraordinarily good at helping people find information and remarkably poor at helping them find the right people.

ohm is built on the belief that AI should not only answer human questions — it should help humans find the other humans with whom those questions become alive.

The Problem

People do not lack access to other people. They lack access to the right people. Existing platforms fail in four ways:

- Shallow proxies — LinkedIn represents credentials, dating apps represent appearance, social media represents performance. None capture how someone thinks, what they're becoming, or whether a conversation with them would expand your life.

- Burden on the individual — users must manually browse, interpret fragmented signals, send cold messages, and hope the right person is visible.

- Profile-first, not intent-first — systems ask &quotwho are you?&quot instead of &quotwhat kind of person are you searching for right now?&quot Human compatibility is contextual.

- AI deepens the paradox — LLMs can answer almost any question, but some problems are only solved through another human being, not through answers.

Core Hypothesis

The most valuable human matches can be discovered by modeling people not as profiles, but as evolving search states — a history, a set of recurring questions, a current quest, a rhythm of attention, and a direction of becoming.

The role of AI is not to become the friend, lover, cofounder, or mentor. The role of AI is to help find them.

What ohm Actually Is

ohm is an agent-mediated human introduction network.

Every user has a private agent that understands their memory, current needs, trajectory, and constraints. The shared system only exchanges carefully abstracted negotiation objects — not raw private detail. Raw context is private input, not the exchange format.

The agent is a private representative for introductions. It understands what kinds of humans you should meet, exposes only an abstract search state, negotiates possible introductions using permissioned summaries, and asks for your approval before anything real happens.

North Star Metric

Number of life-altering introductions created — connections that lead to a company formed, a collaboration started, a mentor relationship developed, a major decision clarified, or a lasting partnership. Not DAU, not swipe volume, not time in app.

How It Works — The Core Pipeline

1. Private memory ingestionSelected chat exports, MCP-compatible memory, notes, and connected apps are read privately. The system extracts recurring questions, goals, values, style, constraints, and present search intent.

2. Search-state extractionThe agent transforms that context into an abstract representation of the user's current search state — what they need, what direction they are moving in, and what exclusions or dealbreakers matter.

3. Permissioned agent cardThe search state becomes a negotiation object with explicit disclosure level, allowed actions, and scope. This is the unit used for matching and comparison.

4. Negotiation and rankingThe system compares the seeker's intent representation with public candidate representations or opted-in user agent cards. It reasons about overlap, mismatch, timing, and possible introduction value.

5. Human approvalBefore any real contact, the user reviews the recommendation, sees the rationale and disclosure scope, and explicitly approves, modifies, or rejects the introduction.

Example Search-State Object

json

{

  &quotuser_id&quot: &quothaein-001&quot,

  &quotcurrent_quest&quot: &quotFind a technical cofounder for ohm&quot,

  &quotsearch_intent&quot: &quotbackend/AI systems builder with product taste&quot,

  &quotcore_direction&quot: &quotAI-mediated human discovery, agent memory, social search infrastructure&quot,

  &quotworking_style&quot: {

    &quotpace&quot: &quotfast&quot,

    &quotambiguity_tolerance&quot: &quothigh&quot,

    &quotcollaboration_mode&quot: &quotfounder-led, conceptually intense&quot

  },

  &quotvalues&quot: [&quothigh agency&quot, &quotcare for human depth&quot, &quottaste in product thinking&quot, &quotwillingness to ship&quot],

  &quotdealbreakers&quot: [&quotstatus-driven&quot, &quotlow shipping velocity&quot, &quotpurely academic orientation&quot, &quotlow ownership&quot],

  &quotevidence_basis&quot: &quotselected memory excerpts, recent search prompts, project notes&quot,

  &quotdisclosure_level&quot: &quotabstract_only&quot,

  &quotallowed_actions&quot: [&quotcompare_compatibility&quot, &quotsuggest_intro&quot],

  &quotcontact_policy&quot: &quotmanual approval required&quot

}

Example Candidate Output

text

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MATCH 1 — Marcus Osei  (@marcusosei_builds)

Match confidence: 91%  |  Source: GitHub + Substack

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHY:     Marcus has spent 2 years building distributed

         graph infrastructure and recently published an

         essay titled &quotWhy we keep building for engagement

         instead of meaning.&quot He is actively asking your

         exact question from the engineering side.

EVIDENCE:

  • 3 GitHub repos on semantic graph traversal (2024–25)

  • Substack: recurring theme of &quotconnection as signal&quot

  • Last post: &quotLooking for a product thinker who cares

    about what the internet has broken socially&quot

MISMATCH: He may be too early-stage for a technical

          co-founder role; hasn't shipped a consumer

          product yet.

OPENING MOVE: Reference his essay on meaning vs.

              engagement. Don't pitch — ask his diagnosis.

Three-Phase Roadmap

Phase 1 — One-sided agent search (Now)Only the searcher has an ohm agent. The system ingests selected context, generates a search-state object, searches public or network-accessible people data, ranks candidates, and returns reasoned introductions with evidence, mismatch, and outreach suggestions. No opted-in user network required — candidates are real people with public intellectual footprints.

Phase 2 — Two-sided opt-in negotiation (6–18 months)Both sides have ohm agents. Instead of matching a seeker against public evidence, the system compares two permissioned agent cards, applies compatibility thresholds, and only surfaces an introduction when both sides clear the reasoning and consent gates.

Phase 3 — Ambient attractor field (2–3 years)Agents continuously update search states and detect emerging overlaps without explicit queries. Resonance becomes ambient rather than purely request-driven, but still bounded by consent, exposure policies, and user-configured openness.

Technical Stack

Layer

Tool

Role

Memory

Mem0 (MCP)

Ingests conversation history, extracts recurring questions, values, trajectory, dealbreakers

App access

WithOne CLI

Terminal-native OAuth for Gmail, Notion, Slack, Calendar

Candidate search

Happenstance API

Natural language people search across professional networks

Matching engine

Jean Domain Embeddings

Asymmetric retrieval — seeker intent vs. candidate identity

Reasoning

Claude/GPT API

Generates WHY / EVIDENCE / MISMATCH / OPENING MOVE per candidate

Interface

CLI (Phase 1) → Web (Phase 2+)

Headless, API-first; positions ohm as a protocol, not a social app

CLI Surface

bash

$ ohm connect

# Connect selected context sources, review permissions,

# generate initial search-state draft

$ ohm search &quottechnical cofounder for ohm&quot

# Build seeker representation, search public/network

# candidate pool, rank and return top 5 with full reasoning

$ ohm review

# Inspect current search-state object,

# adjust disclosure level, edit dealbreakers

$ ohm feedback --candidate user204 --result useful

# Store outcome feedback for future reranking

Trust Model

Must be explicit:

- What memory sources are connected

- What exact data types are ingested

- What gets transformed into the search state

- What disclosure level is currently active

- What actions require manual approval

- How to edit or delete representations entirely

Must be avoided by default:

- Opaque background ingestion

- Raw memory exchange between agents

- Automatic outreach without approval

- Implicit permission escalation

- Irreversible stored inferences

Competitive Position

Dimension

LinkedIn

Dating Apps

ohm

Represents

Credentials

Appearance

Trajectory + intent

Discovery model

Keyword search

Proximity + swipe

Reasoned agent matching

Interface

Profile browsing

Swipe

Terminal → agent field

Phase 3 vision

Feed optimization

Engagement

Ambient resonance field

Why Now

The agent protocol landscape (A2A, MCP, ANP) is converging on interoperability standards that make agent-to-agent communication possible. The memory layer infrastructure (Mem0) is mature enough to build on. The semantic search capability (Happenstance, Perplexity API) is accessible via simple API calls.

The missing piece — a product that uses all of this to help people find people — is the gap ohm fills.

Recommended Next Step

Do not build the full attractor field now. Build the search-state artifact, the one-sided matching loop, and the reasoned introduction interface. If that loop reliably produces surprising and useful humans, then the agent-to-agent negotiation layer becomes not just ambitious, but earned.

ohm is not a social network for agents. It is a server where private representative agents negotiate introductions for humans using consented abstractions rather than raw private detail.
