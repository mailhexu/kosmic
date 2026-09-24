---
status: draft
created: 2026-09-24
updated: 2026-09-24
target: routine://kosmic/day-delta-harvest
routine_action: create
decision: pending
approved_by: ""
---

# Proposal: create shared routine kosmic/day-delta-harvest

## Problem

Collecting "what observably changed in a vault on date D" now exists only
inside the Kosmic dream collector (`kosmic_dreams.collect_harvest`). The same
union — Git window commits with before/after blobs, frontmatter dates, and
dirty state — is useful outside dreams: Task 4 review sweeps, evidence-pack
freshness audits, and any cross-project day report.

## Proposed change

Extract the collector's source-union core (timezone/date resolution, window
commit walk, diff-tree parsing, frontmatter pass, dirty classification,
canonical file entries) into a shared routine declared in
`kosmic_dreams.py` and registered as `kosmic/day-delta-harvest`. The dream
harvest becomes the routine's first caller and keeps its Dream-specific
extensions (open work, flags, read set) local.

## Evidence

- Repetition across three dream records: candidates logged in
  `dreams/2026-09-16.md`, `dreams/2026-09-22.md`, and `dreams/2026-09-23.md`.
- Implementation proven by 42 dream tests and four real vault harvests.
- Task 3 search: no existing routine covers day-delta collection
  (`query-routines` returns only `kosmic/atomic-publish-tree`).

## Scope

- Add `KOSMIC_ROUTINES` declaration + regenerate inventory; no behavior change
  to dream outputs (byte-identical harvest before/after extraction).

## Risks

- Routine edge adds inventory governance; extraction must not alter canonical
  JSON bytes (pinned by tests).
