---
project_id: "kosmic"
subproject_id: "knowledge-first-notes-and-evidence-retirement"
status: "in_progress"
record_kind: "story"
local_id: "002"
linked_prd: "../prd.md"
linked_epic: "../epics/epic-001.md"
linked_architecture: "../architecture.md"
depends_on: []
created: 2026-10-18
updated: 2026-10-18
consumer_interface_change: true
review_base: "02426c2"
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
---

# Story 002: Note admission, locality, evolution, and curation metadata

## User Story

As a memnotes writer and reviewer,
I want a single authoritative rule for where knowledge lives (reusable knowledge in `notes/`, dataset-only documentation beside its data), a self-contained current-truth-first note format with concrete refine/merge/split/correct/retract/deprecate rules, and two note-metadata fields distinguishing skill-material candidacy from actual approved skill-resource use,
So that notes stay a trustworthy permanent knowledge layer without forced pack-to-note writing, per-dataset pointer stubs, length caps, confidence scores, or any promotion automaton.

Covers FR-001..FR-004, FR-007, FR-009, FR-010; ADR-A (locality) and ADR-F
(metadata fields, defaults, and the candidacy update-bump rule only). The
curation window/checkpoint mechanics are Story 004's slice, consuming this
Story's metadata contract.

## Acceptance Criteria

### Locality and admission (FR-001, FR-007; ADR-A)

- [ ] AC1: Given a session that produced only an ordinary code fix with no reusable finding, when it closes, then no note is manufactured and "no new knowledge" is a valid recorded outcome (compact completion fields are Story 003's slice; this AC asserts only that no note is forced).
- [ ] AC2: Given documentation that supports only one dataset (metadata, units, run settings, schema, calibration, single-dataset interpretation), when it is written, then it lives embedded or adjacent to that dataset in its native repository — including a dataset living entirely outside the memnotes vault — and no memnotes note or per-dataset pointer note is created for it.
- [ ] AC3: Given an independently reusable finding demonstrated on a dataset (including a qualified negative or provisional result), when it is extracted, then it becomes a concept-named note with a precise source/reproducibility link, and the native dataset is neither flattened into Markdown prose nor moved or destroyed.
- [ ] AC4: No implemented validator, path scanner, or store-scan classifies or enforces locality: misplacement is caught only by bounded human content review (ADR-A rejects central dataset-doc indexes and mandatory pointer stubs). Any machine checks added in this Story test metadata shape/parsing only, never scientific or keyword classification of note content.

### Note format (FR-002, FR-009)

- [ ] AC5: A note created under the new guidance is named by concept/question/result, opens with its current takeaway, and is self-contained: assumptions, conditions, uncertainty, supporting links, and reproducibility links are present or explicitly bounded. No 30-line cap and no mandatory confidence score appear anywhere in the format, templates, or checks touched here.
- [ ] AC6: Frontmatter keeps `type`, `status: draft|stable|deprecated` (plus optional `stale_after`), relative links, and OKF/Obsidian compatibility; `index.md` remains the progressive-disclosure entry point and the note connects to related concepts.
- [ ] AC7: The ungated reproducibility `sources:` link set replaces any mandatory `evidence:` list in the note contract; existing notes with `evidence: []` remain valid inputs without rewrite.

### Evolution (FR-003, FR-004)

- [ ] AC8: `draft`/`stable`/`deprecated` are the only note statuses; stable promotion requires substantive human review, and useful unresolved findings may remain draft indefinitely — no elapsed-time, formatting-check, or test-success route to stable exists in any consumer this Story touches.
- [ ] AC9: Given a correction/retraction of an invalid claim, when the note is refined, then the supported current conclusion appears first, the superseded interpretation is prominently labeled (not deleted), consequential failure explanations and differing settings/conditions survive, and incoming/index links are repaired.
- [ ] AC10: Given two notes covering one concept with differing settings, uncertainty, or negative results, when they merge, then the result is one coherent current-truth-first note in which those differences and negative findings all survive and previously existing links to either note are repaired so they resolve (clean cutover: repair incoming/index links to the merged note; no redirect shim or alias note is introduced).
- [ ] AC11: Given independently maintainable aspects of one topic, when the note is split, then each resulting note is self-contained with its own frontmatter and links, and cross-references replace duplicated content. No newer timestamp and no status label is ever treated as resolving a conflicting scientific claim — only substantive content is.
- [ ] AC12: Note edits, merges, splits, and deprecations performed by this Story's guidance never mutate or revoke any historical completion record or receipt (the invariance machinery itself is Story 003).

### Curation metadata (FR-010; ADR-F metadata)

- [ ] AC13: A newly created note emits `skill_candidate: false` and `skill_resources: []` (exact approved ADR-F names) with a real UTC `created`/`updated` — default false is the emitted baseline, and the creation-time assessment MAY deliberately mark `skill_candidate: true` when the writer judges the note suitable skill material; candidacy is assessed at creation and on substantive content updates, recorded in the note's own frontmatter, never as a separate assessment artifact, and is never a completion dependency — an explicit no-proposal outcome is valid.
- [ ] AC14: Given a legacy note without the fields, when any reader (doc guidance, or the metadata parser if one is implemented) reads it, then missing `skill_candidate` reads as `false` and missing `skill_resources` as `[]`, with no bulk rewrite and no fabricated timestamps for date-only legacy values.
- [ ] AC15: `skill_resources` holds only stable identifiers of skill topics that actually use the note, written only after approved publication or removal of that use; it is never a wish list of desired targets. A note may be an in-use resource and simultaneously `skill_candidate: true` — the two fields are independent.
- [ ] AC16: Setting `skill_candidate` false→true, or deliberately clearing/reassessing it, is a semantic change that bumps the note's semantic UTC `updated` (so a manually nominated old note enters the next curation window). Syncing `skill_resources` after approved publication/removal, and any check/bookkeeping-only write, never bumps `updated` (no self-requeue). Post-cutoff saves receive timestamps greater than the consumed cutoff, never rounded back.
- [ ] AC17: Where the approved schema warrants consumer behavior, it is machine-tested: absent fields read as the defaults, and both fields are parsed as declared shapes (boolean / list of stable ids). Invalid-shape handling (e.g. non-boolean candidate, non-list or non-stable-id resource entries) is an implementation decision resolved during Research and recorded in Technical Notes with its tests — it is not invented as approved schema, and no machine test classifies whether a note's content is "science".
- [ ] AC18: Dataset-local metadata is excluded from the central note metadata set: the two new fields are the only addition to the note frontmatter contract in this Story.

## Tasks

### Phase 1: Research

- [ ] Read approved [PRD](../prd.md) FR-001..004/007/009/010, [Architecture](../architecture.md) ADR-A and ADR-F (metadata parts), and [Epic 001](../epics/epic-001.md) scope rows for this slice.
- [ ] Survey existing note-writing guidance: `memnotes/Projects/kosmic/notes/note-writing-style.md`, `Projects/kosmic/skills/kosmic-usage/references/note-writing-style.md`, Task 9 `task_distill.md`, and the audited examples (`TBUpy/notes/formal_charge_campaign.md`, `TB2J_dev/notes/bruno-realspace-options.md`).
- [ ] Inventory all readers/parsers of note frontmatter in the kosmic runtime that would observe the new fields, and decide the invalid-shape behavior (AC17).
- [ ] Record findings and any interface decisions in Technical Notes.

### Phase 2: Tests (TDD where behavior is machine-testable)

- [ ] TEST-001: ADR-F defaults — absent `skill_candidate`/`skill_resources` read false/empty; explicit values parse as declared shapes (bounded copy of a legacy note, not a source-text assertion).
- [ ] TEST-002: Timestamp mutation contract — a false→true candidacy change bumps the note's semantic UTC `updated`; a `skill_resources` sync write and a check-only write leave `updated` unchanged. (End-to-end next-window inclusion is Story 004 integration; only the mutation contract is tested here.)
- [ ] TEST-003: New-note emission — bounded real note-writing smoke: write a fresh note per the implemented guidance and content-review its emitted fields and real UTC values (not a permanent unit test, and not a template-echo check). A permanent test exists only if an actually existing callable consumer emits or parses the metadata — no writer API is invented for this purpose; absent such a consumer, this remains a reviewed smoke only.
- [ ] TEST-004 (bounded-copy content demonstration, reviewed not unit-tested): the conflicting-metadata example merges into one coherent note preserving differing settings, uncertainty, and negative results with links resolving (AC10); the campaign correction presents current truth first with the superseded reading labeled (AC9). Execution of the full four-example demonstration set is Story 005's release slice; here only the two examples owned by this slice are rehearsed on bounded copies.

### Phase 3: Implementation

- [ ] IMPL-001: Note-writing style guidance (writer-owned docs for this slice: the note format/lifecycle/evolution rules and ADR-F field documentation, including the updated-bump rule) updated to the approved contract.
- [ ] IMPL-002: ADR-F field defaults/shape parsing where the runtime reads note metadata; no keyword/content classifiers.
- [ ] IMPL-003: Templates touched by this slice updated (no length cap, no confidence scores, `sources:` replacing mandatory `evidence:`).
- [ ] IMPL-004: Bounded-copy demonstrations per TEST-004; no live-vault edits.

### Phase 4: Review

- [ ] All machine tests pass; real smoke of any consumer changed.
- [ ] Lifecycle prose (AC8–AC12) verified by bounded content review, not new machine tests (per approved Architecture test strategy).
- [ ] Independent Standards + Spec review against PRD/Architecture, recorded per the then-current completion rules (Story 003 defines the embedded form; until cutover the existing review channels remain authoritative).

## Non-Goals

- No curation routine, window/checkpoint machinery, serialization, or scheduler (Story 004).
- No completion-record, receipt, or STATUS renderer changes (Stories 003/001).
- No consumer-wide cutover: templates/reference retirement beyond this slice's owned docs, CLI mode removal, ADR 0002 supersession, projections, and disposition planning belong to Story 005.
- No live-vault migration, deletion, or rewrite of legacy notes; legacy defaults are read, never bulk-written.
- No skill proposal, publication, installation, or change to Task P approval gates; candidacy never forces a proposal.
- No external dataset store scanning; no knowledge database, proof hierarchy, or confidence calculus.

## Technical Notes

- Approved ADR-F names are `skill_candidate` (bool, absent = false) and `skill_resources` (list of stable skill-topic ids, absent = []). These are fixed by the approved Architecture; this Story must not rename or reshape them.
- Semantic-update contract for Story 004's consumer: candidacy assessment/reassessment is a semantic change and bumps `updated`; linkage sync and bookkeeping are not. Ambiguous date-only legacy timestamps blocking checkpoint advancement are Story 004's window mechanics; this Story only forbids fabricating instants (AC14).
- Locality per ADR-A is audience-keyed, not path-keyed: "outside the vault" is valid placement for dataset-only docs (AC2), and the retirement explicitly rejects central dataset-doc indexes and pointer stubs.
- Merge link handling is a clean cutover: repair incoming/index links to point at the merged/split note; no redirect shim, alias note, or compatibility stub is introduced (AC10/AC11).
- Bounded copies only: all demonstrations run on scratch copies of the audited examples; the live vault is untouched until the separately approved disposition plan.

## Assumptions & Verification

| Assumption | Verified? | Source |
|------------|-----------|--------|
| ADR-F field names/defaults as written are the approved schema | ✅ | [Architecture](../architecture.md) ADR-F |
| Note contract otherwise unchanged (type/status/relative links/index.md) | ✅ | Architecture, System Design — Data models |
| Invalid-shape parsing behavior is unapproved and decided in Research | ⬜ | Implementation check, not approved schema |
| Which frontmatter readers exist in the runtime today (gates TEST-003 permanence) | ⬜ | Phase 1 Research |

### Implementation decisions (2026-10-18, observed in `skills/scripts/kosmic_project_skills.py`)

- Runtime note-metadata reader is `_validate_note_document`, reached via `validate_project_content` → `validate_notes_bundle` and via `_validate_record_content` for record-declared related notes; no other runtime parser reads note curation fields today.
- Invalid-shape handling (AC17, unapproved schema → decided here, fail-closed): new module-level readers `note_skill_candidate(metadata, relative) -> bool` and `note_skill_resources(metadata, relative) -> list[str]`; absent/empty read defaults; non-bool candidate, non-list resources, and non-string/empty/whitespace-containing resource entries raise `KosmicError`. A "stable id" is a non-empty string without whitespace (bounded shape check; no registry lookup, no name pattern invented).
- `updated` accepts legacy `YYYY-MM-DD` or aware UTC instant `YYYY-MM-DDTHH:MM:SS[.ffffff]Z` (`validated_note_updated`); naive or offset timestamps are rejected; nothing is invented for date-only legacy values. The artifact_role requirement cutoff compares the first 10 characters, so both forms keep the 2026-09-07 semantics.
- No scientific/keyword classification anywhere: only declared metadata shape is machine-checked.
- Emission/timestamp-bump behavior stays prose (`note-writing-style.md`, `skills/references/task_add_note.md`); no writer API exists in the runtime, so TEST-002/003 remain reviewed smoke per spec. Generated audience copies untouched for the Story 005 publisher to regenerate.
- Bounded consumer smoke (managed scratch run, synthetic authority fixture — not a Feature approval): 16/16 checks on the real `load_project` + `validate_project_content` seam. Valid: keys absent; declared false/[] with aware-UTC `updated`; legacy date-only `updated`. Rejected: quoted/explicit-null/blank `skill_candidate`; scalar/explicit-null/blank/non-string/whitespace-id `skill_resources`; naive and offset timestamps. Nomination via existing `update_markdown_metadata` wrote candidate true + bumped `updated` (2026-10-18T15:52:10.500000Z); bookkeeping resources sync left `updated` unchanged; no writer API added. Dataset-local `data/README.md` outside `notes/` produced no central index pointer. Full CLI `validate` not run (needs projection/STATUS scaffolding owned by Stories 001/003/005); exercised seam is the `validate_notes_bundle` path that command calls.
- Explicit-null/blank fail-closed correction applied during smoke prep (only an absent key defaults; null/blank fail closed in both readers); negative regressions added to the existing shape test methods. Keyword-prose classification test removed per test-policy review — no scientific classifier is asserted by source review plus this smoke, not a permanent prose test.
- Run terminalized via real CLI `scratch succeed` (2026-10-18T15:52:46Z, `state: succeeded`): scratch discarded on success; cleanup receipt in the fixture's `history.jsonl` with empty git delta; synthetic authority root `/tmp/kf002-story002-smoke` preserved untouched for parent-confirmed cleanup. Source sha256 `b8eb36a6…c295ba0`; tests sha256 `63eadd31…752359`.

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-10-18 | Created | Initial draft; no implementation started |
| 2026-10-18 | Approved | User approved this story as part of the full five-story set; awaiting implementation |
| 2026-10-18 | Started | Work start accepted at setup commit 02426c2; implementation delegated |
