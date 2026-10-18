---
project_id: "kosmic"
subproject_id: "knowledge-first-notes-and-evidence-retirement"
status: "in_progress"
record_kind: "story"
local_id: "005"
created: 2026-10-18
updated: 2026-10-18
linked_prd: "../prd.md"
linked_epic: "../epics/epic-001.md"
linked_architecture: "../architecture.md"
depends_on:
  - ../stories/story-001.md
  - ../stories/story-002.md
  - ../stories/story-003.md
  - ../stories/story-004.md
review_base: "139f91b"
review_round: 0
consumer_interface_change: true
proposal_required: false
acceptance_evidence: []
review_record: ""
---

# Story 005: Coherent consumer cutover, legacy authority resolution, and bounded knowledge demonstrations

## User Story

As a kosmic maintainer,
I want every consumer of the retired evidence-pack machinery (CLI checks, docs, templates, generated guidance, proposal inputs, migration references) cut over consistently in one release, with legacy authority resolved by reference rather than mutation,
So that runtime and documentation never disagree, historical completed records and curated inputs stay verifiable as originally produced, and the four audited content transformations are demonstrated safely on bounded copies before any separately approved live-vault batch.

This story lands last (after [Story 001](story-001.md), [Story 002](story-002.md), [Story 003](story-003.md), [Story 004](story-004.md)) for a clean release cutover, not runtime mixed with stale guidance. It owns the cross-cutting retirement surface: obsolete CLI modes and Task 9 forced pack-to-note chain, `impact.md` ledger entries, ADR 0002 supersession, the conflicting completed inventory QuickTask, existing proposals and source pins, generated topics/guidance, and the legacy disposition authority boundary. It is the release integrator, not an excuse for earlier stories shipping mixed runtime/docs; each earlier story updates its own consumers, and this story reconciles what remains.

## Acceptance Criteria

### Retirement without shims (FR-008, ADR-D(a))

- [ ] Given a user invoking an obsolete evidence-pack mode after cutover (the `evidence_packs:` gate, sidecar-file acceptance inputs, stable-note `evidence:` path checks, and the forced pack-to-note distillation chain), when the command is run, then the invocation is rejected as unknown/unsupported — no no-op shim, alias, or replacement dossier under another name or hidden directory.
- [ ] Given the cutover CLI, when `--help` and current docs/templates are exercised once via a throwaway CLI/content smoke run, then they no longer name the retired modes; this is a one-time cutover smoke, not a permanent test of help text or source wording.
- [ ] Given the surviving commands (`work start/finish` identity/scope checks, `check-math`, MathDoc structural validation, derivation pairing, proposal gates, completion linkage, receipt validation), when invoked per their remaining duties, then the surviving invariants and gates are unchanged (including Story 003's changed completion proof contract — record-embedded observations and receipts, no sidecar inputs); only pack-specific duties were removed.
- [ ] Given an existing task record containing `impact.md` generation/publication ledger entries and a forced Task 9 note-writing step, when the cutover guidance applies within already-existing task records, then those entries/steps are retired in place without creating any replacement ledger, and finished records are never edited.

### Docs and generated surfaces (FR-008, FR-009)

- [ ] Given docs, references, templates, glossary, proposal inputs, and generated guidance that named Evidence Packs, when the cutover completes, then current consumers describe the knowledge-first workflow with `docs/adr/0002` superseded by a new ADR written at implementation ("knowledge-first notes; no separate evidence layer"); the new ADR supersedes by reference and the old file is preserved, not rewritten.
- [ ] Given generated projections (STATUS.md and other generated topics/guidance), when any regeneration is needed, then it is produced only by the canonical publisher path (bounded per ADR-E) and never hand-edited; installation of any changed skill remains an unchanged separate approval boundary — this story refreshes and publishes nothing into the live skill set.

### Legacy authority by reference (ADR-C/D, NFR-002)

- [ ] Given old immutable curated inputs (historical proposal input snapshots, source pins referenced by completed records, completed historical doc records), when current readers and validators run, then they continue to support and validate those inputs against their original recorded bytes; nothing is repinned, re-blessed, refreshed to current bytes, or re-validated "live" in a way that revokes or blesses history; unresolved validity surfaces as pending/blocker per Story 003's rules.
- [ ] Given the completed QuickTask `restore-evidence-inventories-for-projection-hygiene`, which conflicts with this retirement, when supersession is recorded, then this Story — once user-approved and governing — records the supersession **by reference** (naming its record path/identity and the superseding rationale) within its own record; its pack-inventory rows are not executed post-cutover, and the completed historical record itself is byte-for-byte unmutated.
- [ ] Given a completed record predating the cutover, when its completion is later inspected, then its verdict, reviewer identities, `source_revision`/`review_base` binding, and receipt validity are intact — the cutover changed no recorded approval.

### Bounded-copy demonstrations (ADR-D, NFR-002, PRD success criteria)

- [ ] TBUpy retracted Si interpretation (bounded copy): the correction presents the supported current conclusion first and labels the superseded retracted interpretation without erasing the failed approach; no recorded physics verdict changes.
- [ ] TB2J `bruno-realspace-options` (bounded copy): the conflicting stable/draft metadata becomes one coherent note; differing physical settings, uncertainty, and negative results survive consolidation and existing links resolve.
- [ ] Kosmic `evidence/2026-10-15-completion-status-coherence` (bounded copy): unique/uncommitted snapshots are copied to durable recovery before any transformation; duplicated paperwork is classified disposable without touching the originals; no real data is destroyed.
- [ ] abinit NiO J₀² campaign (bounded copy): dataset-local metadata, units, run settings, schema, calibration, and single-dataset interpretation stay embedded or adjacent to the native data near its native store; only the independently reusable interpretation surfaces as a note with precise source links; no per-dataset duplicate note/pointer is manufactured and no numerical dataset is flattened into prose or lost.
- [ ] Given the finite source→destination disposition map covering the audited legacy packs, when drafted, then it lives only in a future separately approved migration work record at execution time (never a universal registry, never authored in this story's runtime); every demonstration in this story operates on bounded copies only — no live-vault deletion, migration, or installation occurs.

### Source consistency after approved publication/removal (FR-010, ADR-F, current-source)

- [ ] Given a note whose `skill_resources` actual-use list changes after approved publication or removal of a skill topic, when the sync updates the note's frontmatter, then the note's source bytes change while its semantic `updated` timestamp stays unchanged (bookkeeping write, not a semantic update).
- [ ] Given that byte change, when the same approved publication/removal flow reconciles the affected current generated projections and library `source_sha256`/manifest entries against the note's final bytes, then the refreshed artifacts load coherently against the final source, preserving the exact reviewed scope — no stale-pin blessing, and installation remains a separate unchanged approval gate; historical curated snapshots and historical work-record pins are untouched (current-source consistency, not repinning history).
- [ ] Given `skill_resources` metadata, when written by any flow in this story, then it contains only stable topic IDs — no content hashes and no proposed/unapproved targets.
- [ ] Given a genuine consumer holding a source pin whose recorded hash no longer matches the note's current bytes, when the approved refreshed flow runs, then the consumer loads against the coherent final source (behavior test on a real consumer; no wording/copy assertions). Existing source-pin primitives are the expected seam: `project_skills.py` lines 1273-1275, 1313-1315, 1648-1650; shared library lines 951-962 (source-byte hashes) — confirmed as implementation-time starting points, not a completed inventory.

### Whole-system smoke (integration gap coverage)

- [ ] Given a real test-vault invocation of the full workflow (`work start` → edit → `work finish --scope`), when completed, then no `evidence/` tree, mandatory sidecar, or forced pack-to-note step is produced; embedded criterion observations and the two-axis independent review are still checked; receipted completion renders via the canonical publisher; and a session yielding no reusable finding manufactures no note.
- [ ] Given the same smoke run, when math and proposal surfaces are exercised, then `check-math`, MathDoc structural validation, derivation pairing, completion linkage, and proposal/source binding still pass — verification was not weakened by locality (ADR-D(b)).

## Tasks

### Phase 1: Research

- [ ] Inventory every current consumer of retired machinery: CLI modes/gate keys, templates, `task_distill.md`/Task 9 references, glossary, docs naming Evidence Packs, proposal inputs, generated-topic guidance, migration consumers naming `docs/adr/0002` — record exact file/mode list in Technical Notes.
- [ ] Confirm the ADR-E-bounded publisher path and which projections refresh at cutover; confirm no new subcommand modes are introduced.
- [ ] Locate the completed QuickTask record and the historical proposal/source-pin inputs; record their exact paths, hashes, and the reference fields the in-Story supersession entry must carry.
- [ ] Scope the four bounded-copy demonstration inputs and their copy/sandbox locations; verify original paths stay read-only throughout.
- [ ] Document findings and any human clarifications in Technical Notes.

### Phase 2: Tests (TDD — red first, only where machine-testable)

- [ ] TEST-001: invoking each retired pack mode is rejected as unknown/unsupported; no shim routes to a no-op (runtime behavior, not help/source text assertions).
- [ ] TEST-002: surviving commands' remaining duties pass unchanged (identity/scope, `check-math`, pairing, proposal/source binding, receipt validation vs unchanged original bytes — including legacy sidecar-byte receipts) under Story 003's record-embedded proof contract.
- [ ] TEST-003: completed-record immutability — cutover writes never touch finished records; the superseding section references, does not modify, the QuickTask.
- [ ] TEST-004: a real consumer loads regenerated guidance/metadata through the canonical publisher path (or, for the bounded derived STATUS output, the renderer authority path) and shows meaningful behavior — writes confined to the derived target, no source or live-skill mutation, `work finish` still refuses planning-phase records (Story 001 boundary holds in the integrated release). Help/docs/naming consistency stays in the throwaway Phase 4 content smoke, not a permanent content-text test.
- [ ] Content-review-only items (the four bounded-copy content demonstrations — checksum smoke that originals are byte-identical before/after, durable recovery existing before any copy is classified disposable; lifecycle prose quality; supersession rationale wording) are routed to the Phase 4 demonstration/review pass, not made permanent copy/source-text tests and not faked as machine tests.

### Phase 3: Implementation

- [ ] IMPL-001: remove obsolete CLI modes and the Task 9 forced pack-to-note chain; reuse only meaningful existing duties; delete rather than stub.
- [ ] IMPL-002: retire `impact.md` ledger entries and forced note gates within existing task-record guidance; no replacement ledger.
- [ ] IMPL-003: write the new superseding ADR; update docs/templates/references/glossary/proposal-input guidance; keep historical doc records labeled, untouched.
- [ ] IMPL-004: after this Story's own user approval, record in this governing work record (Story 005 itself) the supersession of the conflicting QuickTask by reference — no extra record is created.
- [ ] IMPL-005: regenerate affected projections via the canonical publisher only.
- [ ] IMPL-007: in the approved publication/removal flow, sync `skill_resources` (stable topic IDs only, no hashes/proposed targets) and reconcile affected current generated projections and library `source_sha256`/manifests against the note's final bytes, preserving exact reviewed scope — no stale-pin blessing, no automatic installation, historical snapshots/pins untouched.
- [ ] IMPL-006: execute the four bounded-copy demonstrations in a sandbox; record copy locations and pre/post checksums of originals in the work record.

### Phase 4: Review

- [ ] Real whole-CLI smoke in a test vault per the acceptance criteria above.
- [ ] Independent Standards review (both axes, named reviewers, fixed `review_base`) covering the cutover completeness and shim-absence.
- [ ] Independent Spec review covering FR-008/FR-009 traceability, ADR-D compliance, NFR-002 safety, and that no live-vault action or verdict change occurred. Destructive/live disposition and installation remain separate later approvals; no additional human gate is inserted before any disposition plan is drafted.

## Technical Notes

- Grounding: the seams below come from the approved Architecture (ADRs B–F) and files actually inspected while drafting (`docs/adr/0002-single-evidence-layer.md`; `skills/references/task_distill.md` (Task 9); `kosmic_project_skills.py` renderer (`generate_status`/`render_status`, bounded per ADR-E by Story 001); `impact.md` ledger entries inside existing task records; generated STATUS.md). Exact mode/gate keys and the full remaining-consumer inventory are Phase 1 research deliverables — this list is the bounded starting map, not a claim of completed verification.
- The new ADR is written **during implementation of this story**, per ADR-D(a). Supersession of the conflicting QuickTask is recorded in this Story's own record, effective once Story 005 is itself user-approved and governing; no extra superseding record is created, and the superseded historical record is never mutated.
- Legacy receipts remain verifiable against unchanged historical sidecar bytes (Story 003 contract); current readers keep supporting them until a separately approved migration establishes equivalent durable historical records. Missing/unresolved records surface pending/blocker; never re-pinned or re-blessed.
- The source→destination disposition map is **not** authored here. It lives in a future, separately approved migration work record at execution time. This story only demonstrates on bounded copies and honors the authority boundary.
- Demonstrations never change a recorded scientific verdict, destroy real data, or flatten a dataset into prose; originals are checksummed before and after.
- Assumption (implementation check, not fabricated verification): the canonical publisher refresh covers every generated surface naming packs; if research finds a generator outside the publisher path, surface it as a scope question before cutting over.

## Assumptions & Verification

| Assumption | Verified? | Source |
|------------|-----------|--------|
| Obsolete pack modes are confined to the inventoried CLI surfaces | ⬜ | Phase 1 research |
| All generated projections flow through the ADR-E-bounded canonical publisher | ⬜ | Phase 1 research |
| QuickTask record path/identity and its current bytes are stable | ⬜ | Phase 1 research |
| The four demonstration inputs exist at the audited paths | ⬜ | Phase 1 research |

## Definition of Done

- [ ] All acceptance criteria met; retired machinery absent with no shims; surviving invariants/gates unchanged under Story 003's record-embedded proof contract
- [ ] Historical records, curated inputs, pins, and receipts intact and still validatable as originally produced
- [ ] Bounded-copy demonstrations pass with originals unmodified; no live-vault deletion/migration/installation and no scheduler introduced
- [ ] New superseding ADR written; QuickTask supersession recorded by reference in this Story's own governing record; completed QuickTask unmutated
- [ ] Independent Standards + Spec review completed; all tests green; no regressions

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-10-18 | Created | Initial draft; approved - awaiting implementation |
| 2026-10-18 | Approved | User approved this story as part of the full five-story set; awaiting implementation |
| 2026-10-18 | Started | Work start accepted at setup commit 139f91b; implementation delegated |
