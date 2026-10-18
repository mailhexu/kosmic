---
project_id: "kosmic"
subproject_id: "knowledge-first-notes-and-evidence-retirement"
status: done
record_kind: "story"
local_id: "002"
linked_prd: "../prd.md"
linked_epic: "../epics/epic-001.md"
linked_architecture: "../architecture.md"
depends_on: []
related_notes: ["notes/note-writing-style.md"]
created: 2026-10-18
updated: 2026-10-18
consumer_interface_change: true
review_base: "02426c2"
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
review_round: 3
completion_review:
  reviewer: "OMP/Main (coordinating reviewer)"
  review_base: "02426c2"
  reviewed_revision: "5b5f7640e9733c80f85207ffccb13927872a119896639495b548e060c612880f"
  decision: "approved"
  axes:
    standards:
      reviewer: "Review002Standards"
      decision: "approved"
    spec:
      reviewer: "Review002Spec"
      decision: "approved"
  findings:
    - id: "02STD-1"
      disposition: "Blocking"
      status: "resolved"
      resolution: "Raw-resource handling: task_add_note.md Sources rules no longer require stripping or normalizing whitespace in reproduced resource text; raw resource text is carried as-is."
    - id: "02STD-2"
      disposition: "Blocking"
      status: "resolved"
      resolution: "Real UTC validation: emitted created/updated instants are genuine calendar/clock UTC values observed from the real clock, never synthesized placeholders."
    - id: "02SPEC-1"
      disposition: "Blocking"
      status: "resolved"
      resolution: "Conditional admission: only sessions with reusable findings admit notes; 'no new knowledge' is a valid recorded outcome and no note is manufactured (AC1)."
    - id: "02SPEC-2"
      disposition: "Blocking"
      status: "resolved"
      resolution: "Locality: audience-keyed ADR-A placement is restated in the owned docs with no central dataset-doc index or pointer stub, and machine checks classify metadata shape only (AC2/AC4)."
    - id: "02SPEC-3"
      disposition: "Blocking"
      status: "resolved"
      resolution: "Lifecycle: draft/stable/deprecated statuses with human-review-only stable promotion and the correct/merge/split/retract/deprecate rules are stated in both owned docs (AC8-AC11)."
    - id: "02SPEC-4"
      disposition: "Blocking"
      status: "resolved"
      resolution: "Template UTC default role: the Task 2 template treats created/updated as writer-emitted real instants with legacy date-only values read as dates, never invented by consumers."
    - id: "02SPEC-5"
      disposition: "Blocking"
      status: "resolved"
      resolution: "Note UTC: the reviewed fresh emission carries one real UTC instant in created and updated, substantive updates bump updated, and linkage bookkeeping does not."
    - id: "02SPEC-6"
      disposition: "Blocking"
      status: "resolved"
      resolution: "UTC parser: the changed readers accept absent keys as defaults, real UTC instants, and legacy date-only strings; null/blank fail closed (validated by the reviewed fixture sets)."
    - id: "02SPEC-7"
      disposition: "Blocking"
      status: "resolved"
      resolution: "Raw resources: skill_resources holds stable published ids only (shape-only check, no registry lookup) and Sources links are reproduced verbatim without normalization."
  scope:
    - "worktree:skills/scripts/"
    - "worktree:skills/references/"
    - "worktree:tests/"
    - "project:notes/note-writing-style.md"
    - "project:skills/"
    - "project:impact.md"
    - "project:subprojects/knowledge-first-notes-and-evidence-retirement/specs/stories/story-002.md"
completion_observations:
  - criterion: "AC1: Given a session that produced only an ordinary code fix with no reusable finding, when it closes, then no note is manufactured and \"no new knowledge\" is a valid recorded outcome (compact completion fields are Story 003's slice; this AC asserts only that no note is forced)."
    observation: "Resolved: the changed task_add_note.md removed the 'Finish session -> Session summary' auto-trigger row and states that producing no new knowledge is a valid outcome, and the changed validators add no note-forcing gate (source review). Grounded in the prose-fix inventory of the official lifecycle run; independent review pending."
    source: "OBSERVATIONS.md prose-fix list of official managed run 20261018T173337Z-note-lifecycle-review + task_add_note.md changes; source review of kosmic_project_skills.py readers, 2026-10-18."
  - criterion: "AC2: Given documentation that supports only one dataset (metadata, units, run settings, schema, calibration, single-dataset interpretation), when it is written, then it lives embedded or adjacent to that dataset in its native repository — including a dataset living entirely outside the memnotes vault — and no memnotes note or per-dataset pointer note is created for it."
    observation: "Runtime partial: the smoke wrote dataset-local data/README.md outside notes/ and the notes bundle validated with no central index pointer created and the file untouched (one of the 16 checks). The embedded-or-adjacent, out-of-vault placement doctrine itself is ADR-A prose not restated in this slice's changed docs; content review pending."
    source: "Bounded consumer smoke 2026-10-18, 16/16 on load_project + validate_project_content, recorded in this record's Technical Notes."
  - criterion: "AC3: Given an independently reusable finding demonstrated on a dataset (including a qualified negative or provisional result), when it is extracted, then it becomes a concept-named note with a precise source/reproducibility link, and the native dataset is neither flattened into Markdown prose nor moved or destroyed."
    observation: "Prose only: task_add_note.md requires concept-named notes with a Sources section of reproducibility links, and nothing in the changed docs flattens or relocates native datasets. No bounded-copy extraction demonstration is recorded in this record; review pending."
    source: "Content review skills/references/task_add_note.md template and Principles, 2026-10-18."
  - criterion: "AC4: No implemented validator, path scanner, or store-scan classifies or enforces locality: misplacement is caught only by bounded human content review (ADR-A rejects central dataset-doc indexes and mandatory pointer stubs). Any machine checks added in this Story test metadata shape/parsing only, never scientific or keyword classification of note content."
    observation: "Runtime + source: the smoke exercised declared metadata shape only (valid and rejected fixture sets); the six unit tests cover shape parsing with negative regressions, and the keyword-prose classification test was removed per test-policy review. Source review of the changed readers found no path scanner or content classifier. Full CLI validate not exercised (projection/STATUS scaffolding is Story 005)."
    source: "python3 -m unittest tests.test_note_curation_metadata -v = 6 tests OK (run by coordinating parent, 2026-10-18; not rerun here) + 16/16 smoke + source review of kosmic_project_skills.py readers."
  - criterion: "AC5: A note created under the new guidance is named by concept/question/result, opens with its current takeaway, and is self-contained: assumptions, conditions, uncertainty, supporting links, and reproducibility links are present or explicitly bounded. No 30-line cap and no mandatory confidence score appear anywhere in the format, templates, or checks touched here."
    observation: "Prose + fresh runtime emission: the re-read format rules keep no length cap and no confidence score in both changed docs, and the official run's fresh note orphan-mercury-cli-flag.md demonstrates the format for real - concept-named, Current Takeaway first, self-contained assumptions/conditions including a negative finding, Sources links. Independent review pending."
    source: "Content review task_add_note.md + note-writing-style.md Note format (2026-10-18); fresh note read in official run 20261018T173337Z scratch/story-002-note-lifecycle/scratch-story-002/notes/."
  - criterion: "AC6: Frontmatter keeps `type`, `status: draft|stable|deprecated` (plus optional `stale_after`), relative links, and OKF/Obsidian compatibility; `index.md` remains the progressive-disclosure entry point and the note connects to related concepts."
    observation: "Prose + source: the Task 2 template keeps type/status/audience frontmatter, relative Markdown links, the reserved index.md update (Step 4) and optional stale_after (Step 6); note-writing-style.md keeps its type/status frontmatter and Linked Concepts section. No machine check on these fields was added (source review of the changed readers)."
    source: "Content review task_add_note.md + note-writing-style.md; source review kosmic_project_skills.py note readers, 2026-10-18."
  - criterion: "AC7: The ungated reproducibility `sources:` link set replaces any mandatory `evidence:` list in the note contract; existing notes with `evidence: []` remain valid inputs without rewrite."
    observation: "Prose only: both changed docs replace the mandatory evidence list with ungated sources: body links and keep legacy evidence values valid (task_add_note.md Step 6: a stable note is never rejected for missing evidence metadata). The exercised metadata seam imposes no evidence requirement; no machine gate belongs to this AC; review pending."
    source: "Content review task_add_note.md Step 6 and Principles + note-writing-style.md 'Note format', 2026-10-18."
  - criterion: "AC8: `draft`/`stable`/`deprecated` are the only note statuses; stable promotion requires substantive human review, and useful unresolved findings may remain draft indefinitely — no elapsed-time, formatting-check, or test-success route to stable exists in any consumer this Story touches."
    observation: "Prose + fixture evidence: task_add_note.md Step 6 now requires explicit substantive human review for promotion, note-writing-style.md Lifecycle states checks, formatting, and timestamps never substitute for that review, and the smoke split results were left status: draft - no promotion was performed or implied. No elapsed-time or check-success route exists in the changed validators (source review)."
    source: "note-writing-style.md ## Lifecycle + task_add_note.md Step 6 (read 2026-10-18); split notes source-hash-freshness.md and semantic-updated-rules.md stayed draft in official run 20261018T173337Z."
  - criterion: "AC9: Given a correction/retraction of an invalid claim, when the note is refined, then the supported current conclusion appears first, the superseded interpretation is prominently labeled (not deleted), consequential failure explanations and differing settings/conditions survive, and incoming/index links are repaired."
    observation: "Resolved prose + bounded demonstration: both changed docs now carry the correct/retract rules (current conclusion first, superseded reading labeled not deleted, failure explanations, settings, and negative findings survive), and the merge result projection-cache.md demonstrates the pattern - superseded legacy-date regime labeled in Details with negative conditions preserved. Human content review remains the gate; independent review pending."
    source: "note-writing-style.md ## Lifecycle + task_add_note.md ## Evolution of Existing Notes (read 2026-10-18); merge result read in official run 20261018T173337Z scratch."
  - criterion: "AC10: Given two notes covering one concept with differing settings, uncertainty, or negative results, when they merge, then the result is one coherent current-truth-first note in which those differences and negative findings all survive and previously existing links to either note are repaired so they resolve (clean cutover: repair incoming/index links to the merged note; no redirect shim or alias note is introduced)."
    observation: "Runtime demonstration on bounded copies: official run merged cache-invalidation.md (UTC regime) and the legacy-dated cache-debug-session material into one current-truth-first projection-cache.md; legacy dates kept as dates with no fabricated instants, negative conditions and the mercury negative finding preserved, the incoming link in cache-debug-session.md and the index.md row repaired to the survivor, the duplicate deleted with no alias or redirect; load_project + validate_project_content PASSED post-merge. Merge semantics were judged by hand, not classified by machine."
    source: "Official run 20261018T173337Z-note-lifecycle-review scratch: projection-cache.md, cache-debug-session.md repaired link, index.md row, OBSERVATIONS.md merge log (all read 2026-10-18)."
  - criterion: "AC11: Given independently maintainable aspects of one topic, when the note is split, then each resulting note is self-contained with its own frontmatter and links, and cross-references replace duplicated content. No newer timestamp and no status label is ever treated as resolving a conflicting scientific claim — only substantive content is."
    observation: "Runtime demonstration on bounded copies: official run split one note into source-hash-freshness.md and semantic-updated-rules.md, each self-contained with its own frontmatter, cross-references replacing duplicated content, both left status: draft, and validate_project_content PASSED. No newer timestamp is treated as resolving a conflicting claim (prose) and no human promotion occurred."
    source: "Official run 20261018T173337Z-note-lifecycle-review scratch: source-hash-freshness.md, semantic-updated-rules.md, index.md, OBSERVATIONS.md split log (all read 2026-10-18)."
  - criterion: "AC12: Note edits, merges, splits, and deprecations performed by this Story's guidance never mutate or revoke any historical completion record or receipt (the invariance machinery itself is Story 003)."
    observation: "Source review only: this slice's owned delta (task_add_note.md, note-writing-style.md, the note-metadata readers in kosmic_project_skills.py, tests/test_note_curation_metadata.py) touches no completion-record, receipt, or STATUS code, so guidance-driven note edits cannot mutate receipts; the invariance machinery itself is Story 003. No runtime receipt scenario exercised."
    source: "Source review of the slice's owned files, 2026-10-18."
  - criterion: "AC13: A newly created note emits `skill_candidate: false` and `skill_resources: []` (exact approved ADR-F names) with a real UTC `created`/`updated` — default false is the emitted baseline, and the creation-time assessment MAY deliberately mark `skill_candidate: true` when the writer judges the note suitable skill material; candidacy is assessed at creation and on substantive content updates, recorded in the note's own frontmatter, never as a separate assessment artifact, and is never a completion dependency — an explicit no-proposal outcome is valid."
    observation: "Runtime: the official run's fresh emission orphan-mercury-cli-flag.md carries skill_candidate: false, skill_resources: [], artifact_role: knowledge, and one real current UTC instant (2026-10-18T17:31:40.814773Z) in created/updated; the substantive note-writing-style.md update likewise emitted false/[] with artifact_role: guideline and real UTC updated (17:29:16Z) while keeping its legacy created date as a date. Emission is template-guided authoring checked by the validator - no writer API exists (source review). TEST-003 reviewed smoke now recorded."
    source: "Official run 20261018T173337Z scratch: orphan-mercury-cli-flag.md + note-writing-style.md frontmatter (both read 2026-10-18); OBSERVATIONS.md emission checks."
  - criterion: "AC14: Given a legacy note without the fields, when any reader (doc guidance, or the metadata parser if one is implemented) reads it, then missing `skill_candidate` reads as `false` and missing `skill_resources` as `[]`, with no bulk rewrite and no fabricated timestamps for date-only legacy values."
    observation: "Runtime: the smoke accepted a note with both keys absent (read as the defaults) and a legacy date-only updated preserved without invention; the unit tests cover absent-field defaults and legacy date acceptance. No bulk-rewrite path exists in the changed code (source review)."
    source: "16/16 smoke (absent-keys and legacy-date checks) + six-test unittest run + source review validated_note_updated, 2026-10-18."
  - criterion: "AC15: `skill_resources` holds only stable identifiers of skill topics that actually use the note, written only after approved publication or removal of that use; it is never a wish list of desired targets. A note may be an in-use resource and simultaneously `skill_candidate: true` — the two fields are independent."
    observation: "Prose only: both changed docs state skill_resources lists stable ids only after approved publication or removal, is never a wish list, and that the two fields are independent (a note may be in use and still skill_candidate: true). The stable-id check is shape-only by design with no registry lookup (source review); no machine check exists for the wish-list rule; review pending."
    source: "Content review task_add_note.md Curation Metadata + note-writing-style.md Curation metadata; source review note_skill_resources, 2026-10-18."
  - criterion: "AC16: Setting `skill_candidate` false→true, or deliberately clearing/reassessing it, is a semantic change that bumps the note's semantic UTC `updated` (so a manually nominated old note enters the next curation window). Syncing `skill_resources` after approved publication/removal, and any check/bookkeeping-only write, never bumps `updated` (no self-requeue). Post-cutoff saves receive timestamps greater than the consumed cutoff, never rounded back."
    observation: "Runtime: the smoke's manual nomination via the existing update_markdown_metadata wrote skill_candidate true and bumped updated to the real instant 2026-10-18T15:52:10.500000Z (after the consumed cutoff, not rounded back); the subsequent skill_resources sync and check-only writes left updated unchanged. The unit tests cover the bump contract (TEST-002)."
    source: "16/16 smoke (nomination-bump and sync-no-bump checks) + six-test unittest run, 2026-10-18."
  - criterion: "AC17: Where the approved schema warrants consumer behavior, it is machine-tested: absent fields read as the defaults, and both fields are parsed as declared shapes (boolean / list of stable ids). Invalid-shape handling (e.g. non-boolean candidate, non-list or non-stable-id resource entries) is an implementation decision resolved during Research and recorded in Technical Notes with its tests — it is not invented as approved schema, and no machine test classifies whether a note's content is \"science\"."
    observation: "Runtime: absent fields read as defaults and both fields parse as declared shapes (boolean / list of whitespace-free stable ids), with invalid shapes failing closed - the failing-closed decision stands recorded in this record's Technical Notes. The consumer unit suite now passes 8 tests after whitespace stable-id and impossible-UTC regressions were added (the initial 6 remain historical); full CLI validate still not exercised (Story 005)."
    source: "python3 -m unittest tests.test_note_curation_metadata -v = 8 tests OK (coordinating parent run 2026-10-18, after whitespace + impossible-UTC regressions; parent-observed, not rerun here)."
  - criterion: "AC18: Dataset-local metadata is excluded from the central note metadata set: the two new fields are the only addition to the note frontmatter contract in this Story."
    observation: "Runtime + source: the smoke's data/README.md outside notes/ stayed untouched with no central pointer, and source review of the changed note contract (Task 2 template, note-writing-style.md) shows exactly two added frontmatter fields, skill_candidate and skill_resources; no dataset-local metadata joined the central set."
    source: "16/16 smoke (data README check) + content review of both changed docs, 2026-10-18."
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

## Routine Decision

`routine_decision_required` stays false. This Story's deterministic mechanics are scoped metadata validation plus prose guidance: the existing parser seam (`load_project` + `validate_project_content`, unit-tested by `tests.test_note_curation_metadata`) already covers the field-shape and timestamp mechanics, so no new deterministic routine is introduced and `routine_proposals` stays empty.

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-10-18 | Created | Initial draft; no implementation started |
| 2026-10-18 | Approved | User approved this story as part of the full five-story set; awaiting implementation |
| 2026-10-18 | Started | Work start accepted at setup commit 02426c2; implementation delegated |
