# ohm. — generative mind index

ohm. — generative mind index 

Problem: Interesting minds exist but are unfindable by thought.

The only necessary assumption: Public content contains enough initial signal to make a mind findable by thought-resonance.

Hypothesis: Public content can be synthesized into stances that make otherwise unreachable minds discoverable through thought-matching.

What ohm. is (ohm is not a social product, it is an intelligence tool.)

ohm. is a generative mind index. You type what's on your mind — any thought, question, struggle, or idea — and it returns people's thoughts whose thinking resonates with yours. Not links, not AI-generated answers, not profiles. Portraits of how real people think, synthesized from their public content.

The unit of result is a person's stance. The unit of query is a thought. You cannot search for someone by name. You can only be found through ideas.

Why it matters

Every existing tool returns information. Google returns pages. ChatGPT returns generated answers. LinkedIn returns professional profiles. Happenstance returns people by role and relationship. None of them answer the question: &quotWho is thinking about what I'm thinking about, and how do they think about it?&quot

The value is specifically that the results are human. A real person wrestling with a real problem has texture that AI-generated answers don't — adjacent thoughts, unexpected connections, the shape of a lived curiosity. When you find the right mind, you get something no information tool can give you: the feeling of not being alone in a thought, and the inspiration that comes from seeing how someone else's mind moves through similar territory.

How it works

The core loop is one gesture with two outputs. You write what's on your mind. That input simultaneously becomes your own thought-card (searchable by others) and your search query. ohm. returns thought-stances from people in your extended network whose thinking resonates.

You encounter the thinking first, the person second. A stance resonates with you, and then you discover who's behind it. This is the opposite of every people-search tool.

From there, two natural behaviors:

- Connect. The stance intrigues you enough that you want to talk to this person. Tap to see their LinkedIn profile, mutual connections for warm reach-out, and start a conversation.

- Explore. You gain inspiration from the stance and want to see what else this person thinks about. Because someone whose thinking resonates on one thing is likely interesting across the board. &quotWhat else are they thinking about?&quot becomes the natural next action. That's where unexpected connections happen — you came for one thought and discovered an adjacent idea you never would have searched for.

Each person's mind-portrait is a constellation of stances — not a bio, not a summary, but a map of where they stand on the things they think about. Generated from their public writing: Substack essays, LinkedIn posts, personal websites, tweets, published work.

You can reply to any stance, and your reply becomes a card itself. The mind graph grows from both directions.

The product — two views, nothing more

Home. Input bar at the bottom, always present. Cards above. Type a thought, get resonant stances back — swipe through them like cards. Before you type anything, you see recent thinking from your network as a passive stream. The more specific your input, the more targeted the results. The vaguer your input, the more serendipitous. Discovery isn't a separate tab — it's what happens when you write what's on your mind. The input controls the discovery mode.

Profile. Your own mind-portrait. Your constellation of stances — everything you've searched, replied, and what ohm. synthesized from your public content. This is where you see yourself the way others might encounter you. You can edit, remove, or refine stances that don't represent you well.

Profile serves a critical product function beyond vanity: every search and reply adds to your portrait. Your mind gets richer over time. It becomes an intellectual artifact you're building for yourself, not just a tool you query. And when someone else's thought matches one of your stances, you show up in their results. Refining your profile makes you more findable for the right conversations.

Two views. That's the whole product.

The cold start solution (and why it's self-reinforcing)

Three sources feed the index simultaneously:

1. Crawled public content. Connect your LinkedIn, and ohm. crawls the public content of your ~500 connections. Happenstance's API handles enrichment — surfacing linked profiles and accounts. ohm.'s generative layer synthesizes that into stances. When a friend joins, their connections get mapped too. 500 becomes 800 becomes 2,000.

2. Active searches. When you type what's on your mind, that thought becomes a card — searchable by others. This means even people who never post on social media, who have no public writing, still contribute to the index just by using ohm. Their searches reveal what they're thinking about.

3. Replies and connections. When you reply to someone's stance, your reply becomes a card too. Every interaction generates new searchable content.

This means the index grows from three directions at once: crawled content from the public internet, active queries from users, and organic responses between them. Early on, most cards may come from heavy public writers. But as more people search and reply, the index fills in with people who think deeply but don't publish — and that's a population no other tool can reach.

The core technical bet

The entire product lives or dies on the synthesis quality. Can you take 30 LinkedIn posts, 5 Substack essays, and a personal website and generate stances that feel like encountering how someone thinks? Not keyword clouds. Not resume rewrites. Stances — a person + a subject + a direction. &quotShe thinks systematic design tokens lose something essential.&quot &quotHe believes the best communities are curated through taste, not scale.&quot

One person might have 30 stances extracted from their public content. When you type what's on your mind, you're matching against stances, not people. A person surfaces because one of their stances resonated. Then you can explore their constellation.

This synthesis layer is the IP. The enrichment and crawling are solved problems. The matching infrastructure exists. The generative portrait — turning scattered digital presence into a coherent mind — is the thing nobody else is building and the thing that makes this a new category.

Why ambiguity is a feature

The input can be anything. &quotWhere can I find HK investors&quot might return: an actual HK investor's recent thinking, someone who wrote about navigating that landscape, and someone sharing the same struggle. ohm. doesn't disambiguate intent the way a search engine does. Every interpretation is valid because the result is a stance, and stances are multidimensional. You scan, something catches you, you go deeper.

Key design constraint

You cannot search for a person by name. You can only search with a thought. People are the result, never the query. This prevents ohm. from becoming a people-search tool and preserves the philosophy: you find minds through ideas, not the other way around.

The marketing hook

Two natural entry points:

- Need: &quotFind the right mind for what you're thinking about.&quot A need most people recognize immediately.

- Curiosity: &quotSee how ohm. sees your mind.&quot Your public thinking synthesized into a constellation of stances. Almost irresistible. This doubles as onboarding: someone sees their portrait, wants to refine it, and is now in the graph.

How this connects to other work

The enrichment-to-portrait pipeline is the same engine across three current projects:

- Cecil's wine community: Crawl mailing list members' presence → generate taste portraits → match to curated events.

- SFMTA stakeholder mapping: Crawl public figures' positions → generate stakeholder portraits → map the landscape.

- ohm.: Crawl connections' content → generate mind portraits (stances) → match against live thoughts.

Same pipeline, different synthesis layers. Each project improves the engine for the others.

Next steps

Week 1: Start building the pipeline on whichever project has the nearest deadline (Cecil or SFMTA). Test Happenstance's free tier with own LinkedIn to evaluate enrichment data quality. Build the first synthesis prompt and generate 5 stance-portraits of people whose thinking you know well enough to judge quality.

Week 2-3: Generate 20-30 real portraits across all three projects. Evaluate: do the stances capture how someone thinks, or do they flatten into keywords? Iterate on the synthesis prompt until the portraits feel like minds. This is the make-or-break period.

By end of month: Working prototype where you type a thought and get back resonant stances from your own network. Use it daily. If the core moment feels like magic — if you write what's on your mind and discover a connection you didn't know existed — then you have the product. Everything else follows.

1. What is the problem in human terms?

- friction of introduction, titles, mutuals etc in human connect 

2. What assumptions am I inheriting?

- people want to remove friction

- people want genuine connection

- people are tired to legacy social media of seeing

- people want to be more connected

3. Which of these are actually necessary?

(delete aggressively)

4. What constraints are fundamentally true?

(attention, incentives, behavior)

- I feel fulfilled when I talk to the right people in sf

- how to map every mind of someone 

5. If I started from zero, what would I build?

- a map of someone who I am interested to talk to, like I wanted to be hired from archaetype but they never return my offer back, I want to map the mind of their 

could be used for hiring, dating, genuine knowledge discovery, friends, work, professional insight

Ohm. v1

A personal intelligence engine for thought-matching across your network

Premise

AI is winning the answers war. It is not winning — and probably cannot win — the resonance war: the experience of having your thought met by another real mind that has wrestled with something adjacent and arrived somewhere different. That experience is not replaceable by AI, because the value comes from it being real.

Most people, in most moments, want answers. Resonance is a smaller market, but a durable one — and one likely to grow as AI-generated content saturates the world. The same way vinyl came back when music went infinite, the same way handwritten letters carry weight in an age of email, there is a durable human appetite for the unoptimized real thing.

This product is a bet on that appetite.

Thesis

Thoughts match people.

Not profiles. Not credentials. Not interests. The specific shape of how someone thinks about a problem is a higher-fidelity signal of mind-compatibility than any bio or résumé could ever be. The conversations that mattered most in my life were sparked by an original comment, a sharp post, a framing I had not seen before. AI cannot generate this — but it can index it, surface it, and route it.

Humans are the substrate. AI is the infrastructure.

What it is

A webpage — not an app — that turns my existing network into a discoverable, scrollable surface of recent thinking.

I connect my LinkedIn account. The system crawls a chosen set of connections, and for each one performs an extensive search across their digital presence — LinkedIn posts, personal websites, other social accounts, Google search results, podcast appearances — within roughly the past year.

From those traces, the system generates a stance card per person: a distilled representation of what they have been thinking about lately, written in a way that protects the originality and authenticity of their voice. Stance cards must feel like the person, not like a summary of the person.

Core loop

- Discover. Open the page. Scroll cards Tinder-style — recent thoughts from my dormant network, made legible at the level of mind, not job title.

- Write. Write down something I am thinking about. This becomes a node on my own mind map.

- Match. The system surfaces stance cards from people whose recent thinking resonates with — or productively challenges — what I just wrote.

- Engage. Comment on a card (the comment hyperlinks back to the source thought). Spawn a new card from the exchange. Optionally reach out to the person directly.

- Connect. View that person's full mind map. See where their thinking and mine overlap, diverge, or open new territory.

Design principles

1. AI indexes, humans think

AI is for crawling, embedding, matching, and routing. Humans are for the actual thoughts. The product gets worse — not better — as it becomes more AI-mediated. Every feature decision should be tested against this line. Resist the temptation to add AI summaries that flatten voice, AI-generated cards that simulate thinking, or AI suggestions that pre-chew the spark.

2. Authenticity is non-negotiable

Stance cards must preserve the originality of each person's voice. Better to surface a raw quote with context than a polished summary. The whole product breaks the moment a user senses the cards have been homogenized.

3. Random, but not noisy

The discovery feed should feel serendipitous, not algorithmic. Some randomness is essential — the magic of a 1517-style community came from unexpected adjacencies, not optimized recommendations. But randomness without taste is just noise.

4. Webpage, not platform

This is a tool I open when I have a thought. It is not a feed I doomscroll, not a network I have to maintain, not a social platform with notifications. The unit is the visit, not the session.

5. Built for one user first

Me. Not founders, not artists, not investors, not 'high-agency creative people.' One real person with one real graph and one real problem. Other users come later, named, after the product works for me.

Build plan

Phase 0 — Janky prototype (this week)

Goal: prove the spark. Forget polish.

- Map my personal traces first. Make my personal mindmap of thoughts like obsidian, but more visible. This is the context for better matching.

- Connect my Linkedin Account and for each: scrape their LinkedIn posts (past 12 months), find their other public surfaces (personal site, X/Twitter, Substack, podcasts, GitHub, Medium), pull recent content.

- Generate a stance card for each — ~3 to 5 sentences, in their voice, capturing what they have been thinking about.

- Build a single static webpage: a stack of 20 cards I can scroll, plus a text box where I type a thought.

- On submit: embed my thought, embed each card, return the top 3 matches.

- Use it for one week. Note every spark. Note every dud.

Phase 1 — Make it real (weeks 2–4)

Goal: turn the prototype into something I actually want to open daily.

- Add commenting — comments hyperlink to the original source so the person knows what I am responding to.

- Add per-person mind maps: click a card, see the structure of their public thinking.

- Tune the matching: experiment with resonance (similar) vs. provocation (productively different). Decide which produces better conversations.

- Add a simple refresh mechanic so cards stay current as people post new things.

Phase 2 — Second user (weeks 5–8)

Goal: see if the spark transfers.

- Identify one specific person — by name — whose pain I already know and whose thinking I respect.

- Onboard them. Watch them use it. Do not interpret — observe.

- Ask: did the matching feel uncanny, or generic? Did they message anyone? Would they pay?

- Decide: tool, product, or company. Three different futures, all of them fine.

Open questions to answer through building

- Resonance or provocation? Does the best conversation happen when someone is thinking near me, or thinking against me?

- What is on the card? Raw quote with context? AI-generated summary in their voice? A single sentence pulled from their most recent post? Each produces a different product.

- How fresh is fresh enough? Does a stale stance card kill the magic? How often do cards need to refresh?

- What is the right corpus per person? LinkedIn alone is too thin and too performative. The full digital trace is richer but creepier. Where is the line?

- Is friction load-bearing? Some friction in finding people is what makes the connection feel earned. Which friction is a bug, and which is a feature?

Risks I am taking seriously

- Tool-for-one trap. It might be perfect for me and not transfer. That is a real possibility, not a failure mode to dismiss.

- Audience paradox. The people whose thoughts are most original tend to enjoy the hunt and may resist optimization. The people who would happily pay to skip friction often do not have thoughts worth matching. The wedge is the rare overlap.

- AI-mediation drift. Every easy product decision pushes toward more AI in the loop. Each one degrades the core value. Discipline required.

- Privacy and consent. Crawling someone's full digital presence to generate a stance card raises real questions, even when everything is public. Need to think hard about norms before scaling beyond myself.

Where defensibility comes from

Not the technology. The mechanic — crawl, embed, match — is a weekend build for any competent engineer. Defensibility lives in two places:

- The network. Becoming the place where a critical mass of high-quality thinkers have made their public thinking legible and matchable. That graph is hard to rebuild.

- The taste. The matching surfaces things in a way that feels uncannily right because of judgment calls a competitor without my sensibility will not replicate.

Both moats are human. Fitting, given the thesis.

North star

Replicate the experience of walking into 1517, or the right room in SF — the moment a stranger says something that makes me sit up — but with less friction, using the network I already have. Not faster answers. Better encounters.

If the prototype produces one real conversation I would not otherwise have had, the thesis holds. Build from there.

Tech specs to think about

- MemAlign

human thinking as a mathematical phenomenon, and design tools that treat minds 

language models are epistemically calibrated world models, not chat bots 

conventional computers are all turing machines 

cognitive computing = dnn deep neural network

capabitliies and subtrates 

Computational capability = what kind of problems a system can solve

Substrate = physical materical tht implements it 

silicon based cognitive 

sparse auto encoders - expand the vector into a much larger but sparse representation, where each active dimension coresspoonds to a single interpretable concept

- adaptation 

- generalization

- data compression 

- file:///Users/jeonghaein/thesephist-research-paper.html

- file:///Users/jeonghaein/ohm-product-architecture.html

- file:///Users/jeonghaein/ohm-reading-brief.html
