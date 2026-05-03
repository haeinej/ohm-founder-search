# ohm. -- First Principles Analysis & Plan Draft

ohm. -- First Principles Analysis &amp Plan Draft

  1. The Honest Picture: What You Actually Have

  You have four layers of material that don't fully agree with each other:

  ┌──────────────────────────────────────────┬───────────────────────────────────────────────────────────────────────────┬───────────────────────────────────────┐

  │                  Layer                   │                               What it says                                │               Fidelity                │

  ├──────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────┤

  │ Product vision (generative mind index)   │ Stance-based people discovery through thought-matching                    │ Clear, compelling, original           │

  ├──────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────┤

  │ v1 spec (personal intelligence engine)   │ Webpage, scroll cards, match from your network                            │ Grounded, scoped to one user          │

  ├──────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────┤

  │ Research brief (17 sources, 6 layers)    │ Enterprise-grade bitemporal KG architecture with Crawl4AI, Graphiti, EDC, │ Thorough but overbuilt for where you  │

  │                                          │  4-stage retrieval                                                        │ are                                   │

  ├──────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────┤

  │ Architecture doc                         │ Maps the research brief onto the product, identifies stance synthesis as  │ Good bridge doc but assumes the       │

  │ (product-architecture.html)              │ the IP                                                                    │ brief's stack                         │

  └──────────────────────────────────────────┴───────────────────────────────────────────────────────────────────────────┴───────────────────────────────────────┘

  The advisor feedback is the most honest input in the whole stack. Two things from it matter more than everything else:

  1. You are committing early to a synthetic representation (stances) and that's a lossy compression

  2. You haven't defined precisely what a &quotstance&quot is

  The thesephist paper is intellectual fuel, not implementation guidance. But it contains the single most relevant conceptual frame for your core problem.

  ---

  2. First Principles: What's Actually True vs. Assumed

  True (physics of the problem):

  - Public content contains signal about how someone thinks. You've personally verified this by reading people's work and forming mental models of them.

  - Cosine similarity over embeddings can match semantically related text. This is proven infrastructure.

  - The matching experience (&quotsomeone is thinking about what I'm thinking about&quot) is real and valuable. You've felt it in person in SF.

  - Nobody is building this specific thing. The competitive gap is real.

  Assumed (test these):

  - That LLM synthesis can produce stances that feel like encountering a person's mind, not a summary of their posts. This is the entire bet. Untested.

  - That ~30 LinkedIn posts + a personal website is enough raw signal per person. Maybe. Maybe not. LinkedIn posts are performative. The signal-to-noise may be

  terrible.

  - That thought-to-stance matching via embedding similarity captures &quotresonance.&quot Embeddings optimize for topical similarity, not philosophical alignment. &quotWe're

  both thinking about AI creativity&quot is not the same as &quotwe have the same instinct about AI creativity.&quot

  - That your network (500 LinkedIn connections of a first-year student) is rich enough to produce the core moment. Cold start is real.

  What follows from this: The stance synthesis prompt is the ONLY thing worth building first. Everything else -- Crawl4AI, Graphiti, bitemporal models, 5-tier entity

   resolution, MCP servers -- is infrastructure for a product whose core moment hasn't been validated.

  ---

  3. The Unit of Thought Problem (Your Deepest Question)

  You asked: what's the new unit of thought that is easy for agents to process, easy to webcrawl/match, intuitive for humans, and less lossy?

  This is the right question. Let me work through it.

  Why current units fail:

  ┌──────────────────┬──────────────────┬─────────────────┬─────────────────────────────────────────┐

  │       Unit       │ Agent-friendly?  │ Human-readable? │                Lossiness                │

  ├──────────────────┼──────────────────┼─────────────────┼─────────────────────────────────────────┤

  │ URL / webpage    │ Yes (crawlable)  │ Too coarse      │ Extremely lossy -- one page, many ideas │

  ├──────────────────┼──────────────────┼─────────────────┼─────────────────────────────────────────┤

  │ Paragraph chunk  │ Yes (embeddable) │ Sort of         │ Loses attribution, context, direction   │

  ├──────────────────┼──────────────────┼─────────────────┼─────────────────────────────────────────┤

  │ Embedding vector │ Yes (matchable)  │ No (opaque)     │ Lossy by definition (compression)       │

  ├──────────────────┼──────────────────┼─────────────────┼─────────────────────────────────────────┤

  │ KG entity triple │ Yes (structured) │ Barely          │ Loses nuance, voice, texture            │

  ├──────────────────┼──────────────────┼─────────────────┼─────────────────────────────────────────┤

  │ Social profile   │ Yes (API)        │ Yes             │ Catastrophically lossy -- title != mind │

  ├──────────────────┼──────────────────┼─────────────────┼─────────────────────────────────────────┤

  │ Your &quotstance&quot    │ Partially        │ Yes             │ Medium -- depends on synthesis quality  │

  └──────────────────┴──────────────────┴─────────────────┴─────────────────────────────────────────┘

  The problem with your current stance definition:

  person + subject + direction

  &quotDirection&quot is doing all the work and it's undefined. Is it a sentence? A sentiment? A vector? This vagueness is why the advisor said &quotdefine what a stance is

  precisely.&quot

  A better unit: the Positioned Claim

  From first principles, what you actually need is a unit that captures:

  - WHO holds the position (attribution)

  - WHAT it's about (topicality, for matching)

  - WHERE they stand on it (direction, the actual IP)

  - HOW strongly (not all stances are equal)

  - FROM WHERE (provenance, for trust)

  - WHEN (temporality)

  Here's a concrete schema:

  PositionedClaim {

    person_id: string          // who

    claim: string              // human-readable sentence, in their voice

    topic: string              // what domain this is about (matchable)

    direction: enum            // advocates | questions | opposes | explores | builds

    intensity: float           // 0-1, how central this is to their thinking

    evidence_urls: string[]    // where this was derived from

    source_quotes: string[]    // actual text that supports this (raw chunks!)

    topic_embedding: float[]   // embeds the TOPIC (for &quotwhat are they thinking about&quot)

    claim_embedding: float[]   // embeds the FULL CLAIM (for &quothow do they think about it&quot)

    valid_time: date           // when they expressed this

  }

  Why two embeddings matter:

  This is the key insight from connecting Lee's latent space work to your matching problem. A single embedding conflates WHAT someone is talking about with HOW they

  think about it. You need both:                           

  - Topic embedding: matches &quotI'm thinking about AI creativity&quot to stances ABOUT AI creativity. This is the recall layer.                                            

  - Claim embedding: matches the full directional position. This is the resonance layer. &quotAI will kill creativity&quot and &quotAI will amplify creativity&quot have high topic

  similarity but opposite claim similarity.                                                                                                                          

                                                                                                                                                                     

  This dual-embedding approach lets you do something no one else can: retrieve by topic, then rank by resonance (or provocation). The user's thought matches TOPICS

  broadly, then CLAIMS precisely.                                                                                                                                    

                                         

  Why this is less lossy:                                                                                                                                            

                                                           

  Because you keep source_quotes alongside the generated claim. The advisor was right: store raw chunks AND synthetic stances. The raw text is ground truth. The     

  claim is the navigational surface. The human sees the claim; the system can fall back to the raw quote if the claim feels wrong.                                   

   

  Why this is agent-friendly:                                                                                                                                        

                                         

  Structured JSON with typed fields. An agent can filter by direction == &quotopposes&quot, rank by intensity, traverse person_id to find all stances by one person.         

  Webcrawlers can verify evidence_urls. LLMs can regenerate claim from source_quotes if the synthesis prompt improves later.

  Why this is human-readable:                                                                                                                                        

   

  The claim field IS the stance card text. It's a sentence in the person's voice. The topic is the pill label. The direction is implicit in the claim but explicit in

   the data.                                               

  Connection to Lee's work:                                                                                                                                          

                                                           

  Lee's sparse autoencoders decompose dense vectors into interpretable features. Your positioned claims decompose a person's writing into interpretable stances. Same

   principle, different substrate. The claim IS a &quotfeature&quot of a person's mind, extracted and made navigable.                                                        

   

  ---                                                                                                                                                                

  4. Cross-Verified: What to Actually Use

                                                                                                                                                                     

  Cutting through the research brief's 17 sources to what matters for YOU, NOW:

                                         

  Use immediately:                                         

  - Happenstance API (free tier): Test on your own LinkedIn. See what enrichment data you actually get. This determines whether the &quotcrawl 500 connections&quot cold     

  start is viable or fantasy.                              

  - Claude API with structured output: For stance synthesis. Not Crawl4AI, not Graphiti. Claude with a carefully designed prompt and a Pydantic/JSON schema for      

  PositionedClaim output. This is day 1.                                                                                                                             

  - Embeddings (OpenAI text-embedding-3-small or Voyage): For the dual-embedding approach. Cheap, fast, good enough.

  - Simple vector similarity (numpy or pgvector): For matching. No graph database yet.                                                                               

  - SQLite: For storing everything. Not Graphiti, not Neo4j. One file, zero ops.                                                                                     

                                                           

  Use in week 2-3 if the core moment works:                                                                                                                          

                                                                                                                                                                     

  - Crawl4AI: For automating ingestion beyond manual URL pasting                                                                                                     

  - Brave Search API: For discovering more content about a person beyond what Happenstance gives you                                                                 

  - Exa Find Similar: For &quotpeople who write like this person&quot discovery                                                                                              

                                                                                                                                                                     

  Skip entirely for now:                                   

                                                                                                                                                                     

  - Graphiti / bitemporal KG: Massive overengineering for a prototype. Add timestamps to your SQLite rows. That's your &quotbitemporal model&quot for now.                   

  - 5-tier entity resolution: You're indexing people you personally know. You can manually deduplicate 20 people.                                                    

  - MCP server: Distribution channel, not product.                                                                                                                   

  - Chrome extension: Same.                                                                                                                                          

  - Graph visualization: ohm is cards, not a graph viz. The architecture doc's &quotMind Portrait View&quot is a constellation of stances, not a force-directed graph.

  - EDC extraction pipeline: You're doing one thing (stance synthesis), not general entity extraction.                                                               

                                                           

  ---                                                                                                                                                                

  5. Points Requiring Research (With Specific Experiments)                                                                                                           

                                                                                                                                                                     

  Experiment 1: Can you synthesize stances from LinkedIn posts? (Day 1-2)                                                                                            

                                                                                                                                                                     

  This is the make-or-break. The architecture doc correctly identifies it. The advisor correctly says it's the hardest prompt engineering challenge.

                                                           

  Method:                                                                                                                                                            

  1. Pick 5 people whose thinking you know well enough to judge                                                                                                      

  2. Manually collect their last 20-30 LinkedIn posts + any Substack/personal site                                                                                   

  3. Run your synthesis prompt                                                                                                                                       

  4. Judge: do the stances capture how they THINK, or just what they TALK ABOUT?

                                                                                                                                                                     

  The hard sub-problem (from the architecture doc): most LinkedIn posts are NOT argumentative. They're updates, observations, humble-brags. Your prompt needs to

  INFER direction from evidence, not just extract stated opinions.                                                                                                   

                                                           

  Test prompt structure:                                                                                                                                             

  Given these {N} posts by {person_name}, extract 5-10 positioned claims.                                                                                            

  Each claim should capture WHERE THEY STAND, not just what they mention.                                                                                            

  Look for: recurring themes they return to, positions they defend,                                                                                                  

  assumptions they never question, tensions in their thinking.     

  Output as PositionedClaim JSON.                             

                                                                                                                                                                     

  Success signal: You read the stances and think &quotyes, that IS how they think.&quot Not &quotyes, they did mention those topics.&quot                                            

                                                                                                                                                                     

  Experiment 2: Does dual-embedding matching actually produce resonance? (Day 3-4)                                                                                   

                                                                                                                                                                     

  Method:                                                                                                                                                            

  1. Generate stances for 10-20 people                                                                                                                               

  2. Write 5 of your own real thoughts                                                                                                                               

  3. Embed with topic_embedding and claim_embedding separately                                                                                                       

  4. Compare: does topic-only matching give different (worse?) results than topic + claim matching?

  5. Critical test: can you distinguish resonance from mere topical overlap?                                                                                         

                                                                            

  Success signal: Your thought &quotI think design systems kill the soul of design&quot returns someone who said something SIMILAR in spirit, not just someone who mentioned 

  &quotdesign systems.&quot                                        

                                                                                                                                                                     

  Experiment 3: Is your network rich enough? (Day 1, parallel)                                                                                                       

                                                                                                                                                                     

  Method:                                                                                                                                                            

  1. Connect Happenstance to your LinkedIn                                                                                                                           

  2. Look at what you get for 20 random connections

  3. Count: how many have enough public writing to generate meaningful stances?                                                                                      

                                                                               

  Possible outcome: Most of your connections (first-year student network) may have thin public presences. If so, the cold start strategy needs rethinking. Maybe you 

  start with a curated set of public intellectuals + your SF network, not your full LinkedIn graph.

                                                                                                                                                                     

  Experiment 4: What does the non-argumentative content problem look like? (Day 2)                                                                                   

                                                                                                                                                                     

  Method:                                                                                                                                                            

  1. Categorize 50 LinkedIn posts from one person:                                                                                                                   

    - Explicitly argumentative (has a position): N%

    - Observational (shares without taking a position): N%                                                                                                           

    - Performative (humble-brag, announcement, congratulations): N%

  2. Try generating stances from each category separately                                                                                                            

  3. See which category produces real stances vs. keyword clouds

                                                                                                                                                                     

  Why this matters: If 80% of LinkedIn content is performative, you need to either (a) find better source material, (b) build a prompt that can infer stance from    

  thin evidence, or (c) accept that many people will have low-quality mind portraits and design around it.                                                           

                                                                                                                                                                     

  ---                                                                                                                                                                

  6. Plan Draft                                                                                                                                                      

                                                                                                                                                                     

  Phase 0: Validate the Synthesis (Days 1-5)                                                                                                                         

                                         

  Goal: Answer the one question that determines whether ohm exists.

                                                           

  No infrastructure. No crawling pipeline. No database. Just you, Claude API, and 5 people you know well.                                                            

                                                                                                                                                                     

  ┌─────┬─────────────────────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────────────────────┐   

  │ Day │                                   Do                                    │                                Decision gate                                 │   

  ├─────┼─────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────┤

  │ 1   │ Collect raw content for 5 people manually. Test Happenstance free tier  │ Does Happenstance give you enough to find their public writing?              │   

  │     │ on your own LinkedIn.                                                   │                                                                              │

  ├─────┼─────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────┤   

  │ 2   │ Write and iterate the stance synthesis prompt. Generate                 │ Do the stances feel like MINDS or SUMMARIES?                                 │

  │     │ PositionedClaims for all 5.                                             │                                                                              │

  ├─────┼─────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────┤   

  │ 3   │ Embed stances (dual-embedding). Write 5 of your own real thoughts. Run  │ Does the right person surface? Does it feel like magic or like search?       │

  │     │ matching.                                                               │                                                                              │   

  ├─────┼─────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────┤

  │ 4   │ Iterate on prompt based on day 3 results. Try different claim           │ Can you improve resonance matching by changing how claims are written?       │   

  │     │ structures.                                                             │                                                                              │

  ├─────┼─────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────┤   

  │ 5   │ Honest assessment: is the core moment real?                             │ GO / NO-GO gate. If yes, proceed. If no, pivot the synthesis approach before │   

  │     │                                                                         │  touching infrastructure.                                                    │

  └─────┴─────────────────────────────────────────────────────────────────────────┴──────────────────────────────────────────────────────────────────────────────┘   

                                                                                                                                                                     

  Phase 1: Working Prototype (Days 6-14)

                                                                                                                                                                     

  Only enter this phase if Phase 0 produces at least one &quotholy shit&quot moment.

                                                           

  ┌───────┬─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐

  │  Day  │                                                                   Do                                                                    │                

  ├───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤

  │ 6-7   │ Expand to 20-30 people. Automate ingestion with Crawl4AI for personal sites/Substacks. LinkedIn posts still manual or via Happenstance. │                

  ├───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤

  │ 8-9   │ Build the simplest possible web UI: text input at bottom, stance cards above. SQLite backend. No auth, no profiles, just the core loop. │

  ├───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤

  │ 10-11 │ Add the &quotyour own mind portrait&quot view: stances generated from your own content + your search queries become cards.                      │

  ├───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤                

  │ 12-14 │ Use it daily. Take notes on every spark and every dud. This is the user research phase.                                                 │                

  └───────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘                

                                                                                                                                                                     

  Phase 2: Real Product Shape (Weeks 3-4)

                                                                                                                                                                     

  Only enter this if Phase 1 produces conversations you wouldn't have had otherwise.

                                                                                                                                                                     

  - Add reply-to-stance (your reply becomes a card)

  - Add the dual-view: Home (discovery) + Profile (your constellation)                                                                                               

  - Add Brave Search for discovering more content per person

  - Consider: does this map onto the v2 mobile prototype you already designed? Cards, swipe, sync?                                                                   

                                                           

  ---                                                                                                                                                                

  7. What the Thesephist Paper Actually Gives You                                                                                                                    

                                                                                                                                                                     

  Not implementation guidance, but three conceptual tools:                                                                                                           

                                                                                                                                                                     

  1. The synthesizer metaphor applies directly to ohm. Sound had physics -&gt wave math -&gt synthesizer -&gt new genres. People's thinking has public writing -&gt stance

  extraction -&gt ohm -&gt new kinds of connection. You are building a synthesizer for minds. This is your intellectual positioning.

  2. Notation shapes cognition. The PositionedClaim schema IS a notation for how someone thinks. The quality of that notation determines whether ohm enables         

  &quotunthinkable thoughts&quot (Lee's bar) or is just a slightly better LinkedIn search. The four properties of good notation (unambiguity, expressiveness, suggestiveness,

   natural transformation) should guide how you design the claim format.                                                                                             

  3. Knowledge tools should be infinite, not finite. Roam and Notion are finite boxes. ohm should be an interface to something generative -- your search creates     

  cards, their stances create your discovery, the graph grows from use. This is the &quotinfinite knowledge tool&quot Lee describes. Don't build an archive. Build a         

  generative surface.                                      

                                                                                                                                                                     

  ---                                                                                                                                                                

  8. The Honest Risks

                                                                                                                                                                     

  1. Synthesis quality may not be good enough. This is the scenario where LLMs produce plausible-sounding but actually generic stances that don't capture individual

  voice. If all stances read the same, the product is dead. The advisor's suggestion to keep raw source quotes alongside synthetic claims is your insurance policy.

  2. Your network may be too thin. A first-year student's LinkedIn graph is not a 10-year SF veteran's. You may need to supplement with curated public figures whose 

  writing is rich enough to generate real stances.

  3. Embedding similarity != resonance. This is the deepest technical risk. Two people can write about the same topic with the same vocabulary and have completely   

  different intellectual instincts. Current embeddings don't separate these. The dual-embedding approach is an attempt to solve this but it's unproven.

  4. The audience paradox (from your own spec): the people with the most interesting minds tend to resist being systematized. The people who'd happily use a         

  people-matching tool may not have thoughts worth matching. This is a real tension with no easy answer.

                                                                                                                                                                     

  ---                                    

  The single thing I'd do tomorrow morning: open Claude, paste in 30 LinkedIn posts from someone whose mind you deeply respect, and see if what comes out feels like 

  encountering their mind.                                                                                                                                          

                                                                                                                                                                     

  Everything else follows from whether that works.

                                                                                                                                                                     

  Recalled 1 memory, wrote 2 memories (ctrl+o to expand)    

                                                                                                                                                                     

⏺ That's the full synthesis. The core message: your entire product lives or dies on whether the synthesis prompt produces stances that feel like minds, not          

  summaries. Everything in the research brief is infrastructure for a moment that hasn't been validated yet. Validate that moment first, with nothing but Claude and 

  5 people you know well. The PositionedClaim schema with dual embeddings is your answer to the &quotunit of thought&quot question -- it gives agents structure, gives humans

   readability, and is less lossy because you keep the raw evidence alongside the synthesis.                                                                         

                                                                                                                                                                     

  What do you want to dig into first?
