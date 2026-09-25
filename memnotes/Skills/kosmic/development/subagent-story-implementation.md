---
type: Domain Topic
id: kosmic/development/subagent-story-implementation
domain: kosmic
audience: development
artifact_role: guideline
status: draft
summary: Run approved kosmic stories through derivation, implementation, and review subagents while the parent verifies every claim.
triggers: [subagent story chain, story implementation, derivation agent, reviewer quota fallback]
source_project: native
source_sha256: empty
aliases: [story subagents]
---

# Subagent Story Implementation

Execute approved kosmic stories through `task` subagents. The parent keeps
control of verification, commits, and gates.

## Chain shape

1. **Derivation agent first** for math or physics stories: extend the
   sympy derivation script and run it to ALL-PASS. The parent re-runs it
   before committing; never trust a claimed green run.
2. **Implementation agent second.** It implements library code and tests
   against the committed derivation. The parent runs the full suite and
   visually verifies figures and outputs.
3. **Review agent last.** When the reviewer provider is quota-dead, the
   parent performs the review of record itself: a spec axis against the
   derivation, and a standards axis covering dead code, failure handling,
   input validation, and docstrings. Document the escalation in the story
   file and project log.

## Pinned cross-agent contracts

When two agents build complementary sides, pin the contract verbatim in
both prompts before spawning: exact file names, array keys, shapes,
dtypes, JSON keys with required or optional marks, units, and validation
rules. Spawn them in parallel. Instruct each agent to coordinate
deviations with the other agent through `hub send`. Have each agent report
the agreed amendment to the parent.

## Parent verification checklist

- Re-run every green claim yourself. Subagent output claims are unverified
  until the parent executes them.
- Check `git status --short`: only the intended files changed. Classify
  everything before committing.
- Run pre-commit hooks early. Format hooks can reject the first commit.
- On suspected changes to shared utilities, run the full suite; prove
  pre-existence of unrelated failures through `git stash` plus a re-run.

## Scratch, commits, escalation

E2E and demo runs live under `.tmp/<demo-slug>/`, scripts included.
Propose, do not decide, a promotion to a committed example. Subagents
never commit. The parent reviews and commits explicit paths only, and
never stages unrelated dirty files. When implementation reveals a missing
derivation identity, stop at the boundary: keep the verified part, block
the story with the precise missing-identity name, and revert inconsistent
hybrid attempts. Do not ship physics without its check.
