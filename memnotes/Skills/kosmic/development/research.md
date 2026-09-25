---
type: Domain Topic
id: kosmic/development/research
domain: kosmic
audience: development
artifact_role: guideline
status: draft
summary: Delegate a research question to a background agent that reads primary sources and writes one cited Markdown file.
triggers: [research topic, gather docs, look up api facts, background research]
source_project: native
source_sha256: empty
aliases: [research memo]
---

# Research

Spin up a background agent for the reading, so the main work continues
while the agent reads. The agent has three duties:

1. Investigate the question against primary sources: official
   documentation, source code, specifications, and first-party APIs. Do not
   accept a secondary write-up of a source. Follow every claim back to the
   source that owns it.
2. Write the findings to one Markdown file and cite the source of each
   claim.
3. Save the file where the repository already keeps such notes. Match the
   existing convention. When no convention exists, choose a sensible
   location and state the location in the report.

For memo-scale work that needs many verified citations across several
independent axes, use the parallel DOI-verified research agent pattern
(kosmic/development/parallel-doi-verified-research-agents) instead of one
agent.
