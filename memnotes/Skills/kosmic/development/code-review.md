---
type: Domain Topic
id: kosmic/development/code-review
domain: kosmic
audience: development
artifact_role: guideline
status: draft
summary: Review a diff since a fixed point along two axes, standards and spec, through parallel subagents.
triggers: [review since, two-axis review, standards spec review, branch review]
source_project: native
source_sha256: empty
aliases: [code review axes]
---

# Two-Axis Code Review

Review the diff between `HEAD` and a fixed point the user supplies: a
commit SHA, branch, tag, or `HEAD~5`. Ask when the user gives none.

## Setup

1. Confirm the fixed point resolves with `git rev-parse <fixed-point>` and
   the diff is non-empty. Fail here, not inside the subagents.
2. Capture one diff command, `git diff <fixed-point>...HEAD` (three dots,
   against the merge base), and the commit list through
   `git log <fixed-point>..HEAD --oneline`.
3. Find the spec source in this order: issue references in commit messages,
   a user-supplied path, and a PRD or spec file under `docs/`, `specs/`, or
   `.scratch/` matching the branch. Ask the user when nothing matches. With
   no spec, skip the Spec axis and say so.
4. Find standards sources: any file that documents how code is written,
   for example `CODING_STANDARDS.md` or `CONTRIBUTING.md`.

## Axes

- **Standards**: does the code follow the documented standards? The axis
  also carries a fixed baseline of Fowler code smells. A documented
  repository standard overrides the baseline. Every smell is a judgement
  call, never a hard violation. Skip anything tooling already enforces.
- **Spec**: does the code implement what the spec asked? Report missing or
  partial requirements, unrequested behavior, and implementations that look
  wrong. Quote the spec line for each finding.

Baseline smells: Mysterious Name, Duplicated Code, Feature Envy, Data
Clumps, Primitive Obsession, Repeated Switches, Shotgun Surgery, Divergent
Change, Speculative Generality, Message Chains, Middle Man, Refused
Bequest.

## Execution

Spawn both subagents in parallel in one batch, so their contexts stay
separate. Each brief carries the diff command, the commit list, its source
list, and a 400-word reporting limit. Aggregate the two reports under
`## Standards` and `## Spec` headings without merging or reranking. End
with the finding count and the worst issue within each axis, not a single
winner.

## Why two axes

Code can pass one axis and fail the other. Standards-conforming code can
implement the wrong thing; spec-faithful code can break conventions.
Separate reports stop one axis from masking the other.
