# ohm. — a mobile platform for intellectual resonance matching between…

ohm. — a mobile platform for intellectual resonance matching between strangers. The core technical problem: standard semantic similarity finds people who think alike, which produces echo chambers rather than genuine intellectual encounter. I wanted the opposite — productive topical distance, the kind of friction that generates new thinking.

I architected a dual-embedding system where each piece of content generates two separate vector representations: one for surface content (what is being said), one for the underlying question (what the person is actually reaching toward). Resonance is scored across the gap between matched users' underlying questions, not their surface overlap. The system runs on pgvector with HNSW indexing in PostgreSQL, with LLM-powered extraction of the underlying question layer at write time. The scoring formula actively penalizes topical closeness while rewarding conceptual adjacency.

The complexity wasn't scale — it was epistemological: how do you operationalize &quotintellectual resonance&quot as a computable signal without collapsing it into similarity? I had to make architectural decisions that encoded a philosophical position. Built the full stack: React Native/Expo, Fastify, PostgreSQL, LLM integration end-to-end.

—

The quality of the questions I'm living inside. Not answers, but questions have a longer half-life. A good question restructures how you see everything else for years. I optimize for finding those and staying close to them long enough to actually do something with them.

In practice this means I want the work I do to feel irreducible — to produce something that couldn't have been produced without the specific intersection of things I am. At Mistral that would mean being at the frontier of how language models actually reason and interact, not just applying them.

—

I built ohm.'s full stack solo in 3 weeks while taking a full course load, making 30 users live. That pace came from genuine pull, not discipline, through working 16 hours a day, because I could not stop doing what I love. I think the honest answer is: I work very hard when I'm working on the right thing, and I've gotten good at finding the right thing.

When I am stuck with the right question, I am obsessed for solving in different directions. Obsessed with ideating creative solutions.

—

I sit at an unusual intersection: I think in cognitive science and philosophy of mind, I build in React Native and pgvector, and I write essays about where AI architecture is getting the fundamental question wrong. Those three things aren't separate interests — they collapse into a single one: what does it mean to build intelligence that feels like genuine encounter rather than sophisticated output?

I published &quotLossy Synthesis&quot arguing that the industry's lossless representation paradigm misses what makes intelligence feel alive. I built ohm. as an attempt to prove the opposite architecturally. I'm applying to Mistral because Le Chat is the most serious attempt in Europe to make a frontier model that people actually want to be in conversation with and I want to understand how that's built from the inside.

I'm Korean, bilingual, based in San Francisco, studying Design and Computational Science at Minerva University. I think aesthetic rigor and technical rigor are the same thing looked at from different angles.

—

I am Korean, bilingual, and I think about language not as a medium for transmitting information but as a structure that shapes what can be thought at all. That's why Magistral matters to me in a way that other reasoning models don't — it's the first serious attempt to make reasoning natively multilingual, not translated. The question of whether a model reasons differently in French than in Korean is, to me, one of the most interesting open questions in AI, and Mistral is the only lab treating it as a research problem rather than a localization task.

The other thing I keep returning to is Voxtral's reward modeling architecture — scoring responses not on raw audio but on the semantics, style, and coherence of the transcription. I built something structurally similar in ohm.: a dual-embedding system that scores intellectual resonance not on surface content but on the underlying question a person is reaching toward. Different application, same epistemological bet — that meaning lives below the literal signal.

I wrote an essay arguing that the AI industry's obsession with lossless transformation misses what makes intelligence generative. Mistral's Magistral announcement used almost the same language to describe what they were building: thinking that &quotweaves through logic, insight, uncertainty, and discovery.&quot I want to be inside the lab developing that.

And practically: I'm a builder who thinks in cognitive science and ships in TypeScript and Python. Mistral is the place where those things would all be useful at once.
