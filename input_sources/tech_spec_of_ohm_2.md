# Tech spec of ohm.

Tech spec of ohm.

What Ohm Is

A social discovery app that matches people based on resonance — the underlying human experience behind what they write — rather than topic, interests, or social graph. No followers, no likes, no metrics. Three screens: Worlds (feed), Conversations, Me (profile).

Core Algorithm: Dual-Embedding Resonance Matching

Every &quotthought&quot (a 200-char sentence + 600-char context) goes through an LLM-powered extraction pipeline that produces:

- Surface Embedding (768-dim vector) — standard document embedding of the raw text

- Resonance Embedding (768-dim vector) — generated from extracted resonance phrases and tensions, capturing what the person is really grappling with across 17 human experience domains (identity, time, control, belonging, creativity, mortality, etc.)

The key insight: two people writing about completely different topics (say, parenting and architecture) can have nearly identical resonance embeddings if they're both navigating the same underlying tension (e.g., control vs. freedom).

Feed Pipeline: Retrieve → Score → Rank

Layer 1 — RETRIEVE (pgvector with HNSW indexes):

- Resonance matches: k-nearest neighbors by resonance embedding

- Adjacent territory: k-nearest by surface embedding (topical diversity)

- Wild cards: random quality-filtered thoughts

- Recent bucket: 50 most recent

Layer 2 — SCORE:

score = resonance_similarity × (1 + α × surface_distance) × quality_score

- surface_distance = 1 - surface_similarity — this is the creative distance bonus, actively rewarding topical novelty while maintaining resonance alignment

- α is learned per user (default 0.3, range 0.05–0.95)

Layer 3 — RANK (post-ranking with learned weights):

rank = (Q × w_q) + (D × w_d) + (F × w_f) + (R × w_r)

- Q: quality score (openness-weighted)

- D: diversity composite (cohort distance + concentration diff + cluster novelty)

- F: freshness (full boost 0–6h, decay to 48h, 0.1 residual after)

- R: reply quality (accepted replies + sustained conversations + cross-concentration ratio)

Learning Loop

Daily job (3am UTC):

- Computes cross-domain affinity between concentration pairs (e.g., do Philosophy×Engineering conversations sustain?)

- Updates per-user adaptive weights (w_q, w_d, w_f, w_r, α) based on what each user actually engages with

- Tracks temporal resonance (cohort distance → sustain rate)

Weekly job (Sunday 4am):

- K-means++ clustering on all resonance embeddings with cosine distance, k = √(n/2) clamped [10, 100]

- LLM-generated cluster labels

- Cross-cluster affinity analysis (which resonance clusters produce sustained conversations when paired?)

Interaction Model

- See thought in feed → swipe through 3 panels (sentence+photo, context, existing replies)

- Write a reply (50–300 chars) → goes to pending status

- Author accepts or silently ignores (no rejection notification)

- Accepted reply → conversation created (ephemeral, no archive)

- After 10+ messages → can co-create a Crossing (private two-person artifact on both profiles) or a Shift (before/after evolution story, appears in feeds)

Anti-Pattern Design Choices

- No metrics exposed — &quotwarmth&quot levels (none/low/medium) replace counts

- Creative distance as a feature — the scoring formula actively boosts topically dissimilar but resonance-aligned matches to prevent filter bubbles

- Cold-start bridge — new users with no resonance history get matched via interest embeddings with a 0.7 dampening factor

- Silent rejection — ignored replies just disappear, no notification, reducing social anxiety

- Convergent personalization — the system learns each user's unique balance of quality vs. diversity vs. freshness vs. reply-quality over time

Tech Stack

- API: Fastify + Drizzle ORM + PostgreSQL with pgvector

- Embeddings: 768-dim vectors stored in PostgreSQL, indexed with HNSW

- ML: LLM calls for resonance extraction + quality scoring, custom K-means++ in TypeScript

- Mobile: React Native / Expo with a swipeable card deck UI

- Cron: Built-in Fastify plugin running daily/weekly learning jobs with distributed locking

The whole system is essentially a recommendation engine that optimizes for conversation depth rather than engagement time — it measures success by whether two people sustain a 10+ message conversation across domain boundaries, not by clicks or time-on-app.
