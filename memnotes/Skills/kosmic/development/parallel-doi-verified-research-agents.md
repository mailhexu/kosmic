---
type: Domain Topic
id: kosmic/development/parallel-doi-verified-research-agents
domain: kosmic
audience: development
artifact_role: guideline
status: draft
summary: Fan out parallel literature-research agents that verify every citation against DOI, publisher, or arXiv sources.
triggers: [doi verified research, literature agents, citation verification, research fanout]
source_project: native
source_sha256: empty
aliases: [doi research agents]
---

# Parallel DOI-Verified Research Agents

Use this pattern when a research memo needs many verified primary-source
citations across several independent topics.

## Dispatch

Split the topic into 4 to 6 self-contained axes. Spawn one `task` agent per
axis, all in one batch. Each brief contains:

1. **Target file** under `.tmp/research/<slug>.md`. Scratch first; copy
   into the vault when the memo cites the file durably.
2. **CiteKey contract** for the file format: a `# Title / Date / Agent`
   header, a `## Findings` section with numbered results, each result
   carrying the exact equation and a `[CiteKey]`, and a `## References`
   section with authors, year, exact title, venue, DOI or arXiv id, and
   one-line relevance.
3. **Verification rules**: open every citation against the DOI registry,
   the publisher, or arXiv in this session; never guess pages or DOIs; mark
   unresolvable entries `UNVERIFIED:`; explicitly refute brief guesses that
   do not exist. Expect 12 to 30 references per agent.
4. **Honest adjudication section**: list every brief item that could not be
   verified or resolved to a different paper than suggested.

Seed each brief with candidate anchors, and expect 20 to 30 percent of them
to be wrong in venue, page, or existence. Catching that is the agents' job.

## Operational tips

- Crossref rate-limits parallel bursts with HTTP 429. Pace batches of about
  4 with the mailto polite pool. Single-work `?select=` queries return HTTP
  400; use the search endpoint with select instead. `curl` can be blocked
  in agent sandboxes; agents use fetch or web_search instead.
- An exhaustive verification agent can exhaust its runtime just before
  writing. Revive it with `hub send`: order no more lookups, an immediate
  file write, and `UNVERIFIED` marks for unresolved items.

## After collection

Read each file and synthesize the memo yourself. Preserve cited files
durably under `specs/research/<date>-supporting/`, then delete the `.tmp`
copies. Grep the memo for `?]`, `UNVERIFIED`, and placeholder keys before
finishing.
