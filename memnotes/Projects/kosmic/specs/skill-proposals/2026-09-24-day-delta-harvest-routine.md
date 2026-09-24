---
status: draft
created: 2026-09-24
updated: 2026-09-24
result: create
scope: shared-routine
target_kind: routine
routine_action: create
routine_id: kosmic/day-delta-harvest
linked_proposals: []
consumer_approvals: []
target: kosmic/day-delta-harvest
target_ref: routine://kosmic/day-delta-harvest
target_sha256: empty
proposer_mode: subagent
proposer_ref: agent://DayDeltaProposer
proposer_reason: "Fresh-context Task P assessment from the hash-pinned curated manifest only: three dream records establish repetition; collect_harvest's helpers form a typed, deterministic union with byte-pinned outputs, so shared-routine create is justified"
input_manifest: [specs/skill-proposals/inputs/day-delta-harvest.md]
related_notes: [notes/dream-reflection-workflow.md]
evidence_packs: [2026-09-23-dream-reflection-release]
behavioral_evidence: [evidence/2026-09-23-dream-reflection-release/dogfood-results.json]
decision: pending
fingerprint: ""
reconsiders: ""
---

# Proposal: create shared routine kosmic/day-delta-harvest

## Problem

Collecting "what observably changed in a vault on date D" now exists only
inside the Kosmic dream collector (`kosmic_dreams.collect_harvest`). The same
union — Git window commits with before/after blobs, frontmatter dates, and
dirty state — is useful outside dreams: Task 4 review sweeps, evidence-pack
freshness audits, and any cross-project day report.

## Proposed Change

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

## Routine Candidate

Repetition: Three independent dream records (2026-09-16/22/23) required
  the same day-delta union; Task 4 review sweeps and evidence-freshness audits
  re-derive it ad hoc.
Contract: Inputs `vault: Path`, `date: str | None`, `zone: str | None`;
  output canonical JSON bytes of {window commits with before/after blobs,
  frontmatter dates, dirty classification}; deterministic, no network, pure
  read over the Git repository.
Expected failures: no Git repository under the vault; malformed or
  missing dates; timezone resolution failure; dirty-state race during harvest
  (entries flagged dirty, not silently dropped).
Leverage: one canonical collector replaces per-consumer reimplementation;
  byte-identical outputs pinned by the existing 42 dream tests keep the dream
  caller and future consumers aligned.

## Applicability

Procedural and deterministic: fixed trigger (collect day-delta for date D),
typed inputs/outputs, byte-pinned invariants. Dream-specific judgment (open
work, flags, read set) stays prose and local; only the source-union mechanics
are shared. No overlap: routine inventory holds only
`kosmic/atomic-publish-tree`.

## Behavioral Validation

Candidate paths: [pending_tests/kosmic/2026-09-24-day-delta-harvest/candidate]
Scenario: harvest the same vault/date before and after extraction; invariant:
canonical JSON bytes byte-identical, 42 dream tests pass; baseline =
pre-extraction `kosmic_dreams.py`, candidate = routine-backed collector;
evidence pack recorded at acceptance under
`evidence/2026-09-24-day-delta-harvest/`.

## Scope

- Add `KOSMIC_ROUTINES` declaration + regenerate inventory; no behavior change
  to dream outputs (byte-identical harvest before/after extraction).

## Risks

- Routine edge adds inventory governance; extraction must not alter canonical
  JSON bytes (pinned by tests).
