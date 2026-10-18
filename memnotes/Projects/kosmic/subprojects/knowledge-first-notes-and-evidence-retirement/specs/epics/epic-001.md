---
project_id: "kosmic"
subproject_id: "knowledge-first-notes-and-evidence-retirement"
status: "approved"
record_kind: "epic"
local_id: "001"
created: 2026-10-17
updated: 2026-10-18
linked_prd: "../prd.md"
linked_architecture: "../architecture.md"
linked_stories:
  - ../stories/story-001.md
  - ../stories/story-002.md
  - ../stories/story-003.md
  - ../stories/story-004.md
  - ../stories/story-005.md
---

# Knowledge-first workflow and incremental skill curation

## Approval

Approved by the user on 2026-10-18. This authorizes creation of the five draft
Stories below, not their implementation. Each Story requires its own approval;
live-vault disposition and installation retain separate approval boundaries.

## Description

Deliver the approved knowledge-first workflow: memnotes `notes/` remains the permanent layer for independently reusable knowledge, while dataset-only material (metadata, units, run settings, schemas, calibration, single-dataset interpretation) lives embedded or adjacent to its dataset in its native repository, inside or outside memnotes. Mandatory Evidence Pack / manifest / forced-distillation / sidecar machinery is retired without relocating it, keeping real verification, source-bound two-axis independent review, and completion receipts authoritative. It adds the ADR-F skill-curation metadata plus the optional incremental manual/weekly curation routine, and cuts over all consumers consistently. Delivered as five gated story slices; each Story is individually approved before its implementation.

## Scope

### In Scope

- Note format and lifecycle (FR-002..FR-004, FR-009): concept-named, current-truth-first, self-contained notes; no length cap or confidence scores; `draft`/`stable`/`deprecated` retained; stable promotion by substantive human review only; refine/merge/split/correct/retract/deprecate rules preserving explained negatives and repairing links.
- Locality (FR-007, ADR-A): dataset-local documentation stays embedded/adjacent to its native data wherever that data lives; reusable findings are extracted with precise source links; no per-dataset duplicate note/pointer; native data stay in suitable stores, never flattened into Markdown, unique snapshots preserved.
- Skill-curation metadata (FR-010, ADR-F): `skill_candidate` (absent = false) assessed at creation and substantive updates, recorded in the note itself, never a completion dependency; `skill_resources` (absent = []) lists skill topics actually using the note, synced only after approved publication/removal; candidacy and actual use are independent; new notes emit both fields, legacy omissions read as defaults.
- Incremental curation routine (FR-011, ADR-F): metadata-driven selection over semantic UTC `updated` (created fallback, never fs mtime) with `L < updated <= U`, cutoff `U` frozen at run start; one per-scope shared checkpoint advanced only by successful full-scope runs (no-action advances; failed/partial/targeted do not); explicit first-run baseline; ambiguous legacy dates block advancement; same-scope runs serialize; candidate-first prioritization; nomination only — approval, publication, and installation stay separate gates; no scheduler, daemon, or automatic output.
- Compact completion (FR-005, ADR-B): `completion_observations`/`completion_review` embedded in the work record with both standards/spec review axes, per-axis reviewer identities, `review_base`/`reviewed_revision` source binding via the unchanged `source_revision`, and a stable finding ledger with named-human risk acceptance; mandatory sidecars/manifests/packs removed without any replacement dossier.
- Completion invariance and receipts (FR-006, ADR-C): completed records immutable after receipt; `record_sha256`/proof validated against unchanged original record bytes; legacy receipts validate against unchanged historical sidecar bytes until an approved disposition; unresolved legacy validity surfaces as pending/blocker, never re-blessed.
- Bounded renderer authorization (ADR-E): planning-phase records (approved PRD/Architecture; a draft refreshing its own hierarchy) accepted for the derived STATUS path only — no `work finish`, no source mutation, no receipt semantics.
- Coherent cutover (FR-008, FR-009, ADR-D): retire obsolete evidence-pack CLI modes, Task 9 forced pack-to-note chain, templates/`task_distill.md`/glossary machinery and `impact.md` ledger entries within existing task records; supersede `docs/adr/0002` with a new ADR written at implementation; generated projections regenerated via the canonical publisher, never hand-edited; `check-math`, MathDoc structural validation, derivation pairing, and completion linkage unchanged.
- Bounded demonstrations and disposition planning (ADR-D, NFR-002): the four audited content transformations shown on bounded copies; the finite source→destination disposition plan lives in an existing approved migration work record at execution time; supersession of the conflicting completed QuickTask (`restore-evidence-inventories-for-projection-hygiene`) is recorded in a new approved work record referencing it — completed historical records are never mutated.

### Out of Scope

- No live-vault migration, deletion, or destructive batch: a separately approved source→destination plan precedes any execution; no recreation of vault evidence archives.
- No new knowledge database/query system, proof hierarchy, confidence calculus, or note edition/versioning beyond existing frontmatter (PRD Non-Goals).
- No physics recomputation and no change to any recorded scientific verdict or math gate.
- No scheduler/daemon/automatic daily curation output; curation is one manual/scheduled bounded invocation.
- No skill proposal, publication, or installation triggered by candidacy or curation; existing Task P proposal gates unchanged.
- No mutation of completed historical records, their receipts, protected curated proposal snapshots, or historical doc records; supersession happens by reference in new approved records.
- No machine validator substituting for semantic content review; lifecycle prose stays enforced by bounded content review and human gates.
- No hand-edited generated guidance; regeneration via the canonical publisher only.

## Stories

| Story | Title | Requirement/ADR coverage | Depends on |
|-------|-------|--------------------------|------------|
| [001](../stories/story-001.md) | Bounded planning-phase STATUS rendering | ADR-E; FR-008 (renderer seam) | — |
| [002](../stories/story-002.md) | Note admission, locality, evolution, and curation metadata | FR-001..FR-004, FR-007, FR-009, FR-010; ADR-A; ADR-F (metadata) | — |
| [003](../stories/story-003.md) | Compact completion and durable historical receipts | FR-005, FR-006; ADR-B, ADR-C | — |
| [004](../stories/story-004.md) | Incremental manual/scheduled curation routine | FR-011; ADR-F (window/checkpoint) | Story 002 |
| [005](../stories/story-005.md) | Consumer cutover, legacy disposition planning, bounded-copy demonstrations | FR-008, FR-009; ADR-D; PRD success-criteria demonstrations | Stories 001–004 |

Slices 1–3 are independently designable; slice 4 consumes slice 2's metadata; slice 5 lands last for a clean release cutover, not runtime mixed with stale guidance. Each future Story carries focused research, TDD where behavior is machine-testable, real CLI smoke, and mandatory independent review.

## Success Criteria

- [ ] A default note and an in-use skill resource are distinguishable end to end: a new or substantively updated note carries only the default negative candidacy unless deliberately flagged; `skill_resources` lists only topics actually using the note after approved publication; the two fields are independent (a live resource may stay a candidate); legacy notes without the fields read as defaults, no bulk rewrite.
- [ ] Notes evolve in place: a campaign correction presents the supported current conclusion first and labels the superseded interpretation without erasing the failed approach; the conflicting-metadata example becomes one coherent note preserving differing settings, uncertainty, and negative results with links resolving.
- [ ] An ordinary code fix passes checked completion with no `evidence/`, no mandatory proof/review sidecars, and no manufactured note when no reusable finding emerged, while embedded criterion observations and the source-bound two-axis independent review remain checked.
- [ ] Later refinement, merge, or deprecation of a note leaves historical completion intact without rewriting prior approvals, pins, or receipts; legacy receipts validate against unchanged historical sidecar bytes; unresolved legacy validity surfaces as pending/blocker.
- [ ] Curation reviews only `L < updated <= U` with exact UTC boundary placement (equal to `L` excluded, equal to `U` included), candidate-first; a successful no-action full-scope run advances the shared checkpoint; failed and targeted-subset runs leave it unchanged; the first run needs an explicit baseline; ambiguous legacy dates block advancement; same-scope runs serialize.
- [ ] Planning records refresh derived STATUS within the bounded authorization while `work finish` still refuses planning-phase records and grants no receipt semantics.
- [ ] Current docs, runtime, and regenerated guidance agree: no mandatory pack-to-note chain or replacement dossier remains; math gates untouched; the conflicting old QuickTask is superseded by reference from a new approved work record with completed history unmutated.
- [ ] The four audited content transformations are demonstrated on bounded copies: dataset-local material stays beside native data with no per-dataset duplicate note/pointer, reusable findings surface as notes with precise source links, no numerical dataset is flattened into prose or lost, and unique/uncommitted snapshots are preserved.

## Progress

- Status: approved — five draft Story records created for individual approval; no implementation started.
- Next gate: review and approve each Story before implementation; live-vault disposition and installation remain separate, later approvals.
