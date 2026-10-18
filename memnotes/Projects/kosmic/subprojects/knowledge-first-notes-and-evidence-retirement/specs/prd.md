---
project_id: "kosmic"
subproject_id: "knowledge-first-notes-and-evidence-retirement"
status: "approved"
record_kind: "prd"
local_id: "prd"
linked_research: []
linked_epics:
  - epics/epic-001.md
linked_architecture: architecture.md
created: 2026-10-17
updated: 2026-10-18
---

# Knowledge-first notes and evidence retirement

## Approval

**History.** The original PRD was approved by the user on 2026-10-17 with an
explicit locality clarification: metadata, explanations, units, run settings,
schemas, calibration, and interpretation that support only one dataset belong
within or near that dataset in its native data repository, outside memnotes when
appropriate; reusable standalone knowledge belongs in memnotes with precise
source links, and local documentation must not be duplicated. That approval
covered the original requirements plus the clarification only.

**Current status: approved (2026-10-17).** Also on 2026-10-17 the user had
requested a curation amendment (skill-material candidacy assessment at note
creation and substantive updates, default no; note metadata distinguishing
candidacy from actual approved skill-resource use; incremental weekly/manual
curation over notes changed since the last successful check). The user has now
approved the amended PRD — including FR-010 and FR-011 — and the accompanying
Architecture, including ADR-F with the designed candidacy/resource metadata
names and defaults and the per-scope checkpoint/interval contract as
presented. These approvals cover the design records only: they do not approve
implementation, Story creation (which waits for Epic approval), any live-vault
disposition, or installation.

## Problem Statement

Kosmic's Evidence Pack, manifest, distillation and completion-proof requirements
can preserve procedural paperwork separately from the explanations readers need.
The user wants contextual atomic notes, less permanent writing, and deliberate
evolution from provisional findings to maintained knowledge.

The preceding read-only audit found these concrete patterns:

1. `TBUpy/notes/formal_charge_campaign.md`: a retracted Si-chain interpretation
   appears before its correction; readers must reconstruct chronology.
2. `TB2J_dev/notes/bruno-realspace-options.md`: one file contains both a stable
   frontmatter status and a later draft metadata block.
3. Kosmic's `evidence/2026-10-15-completion-status-coherence/`: acceptance/review
   paperwork sits beside copies of implementation and test files.
4. `abinit/evidence/2026-10-15-nio-j02-campaign/report.md`: useful scientific
   findings, failed comparisons and interpretation limits are buried in a pack.
   Native outputs must remain recoverable; independently reusable interpretation
   belongs in notes, while interpretation needed only to understand that dataset
   may stay embedded or adjacent to the data.

Existing policy already says to avoid duplicate notes and requires human review
for stable promotion. The change must make those intentions effective, remove
forced pack-to-note writing, and avoid treating metadata checks as scientific
verification. Prescriptive note lengths and template confidence scores must not
substitute for self-contained explanations.

Related: [Experience Compilation PRD](../../experience-compilation-adapting-wikiskill-into-kosmic/specs/prd.md),
[semantic roles](../../semantic-artifact-roles/specs/prd.md),
[evidence-layer ADR](../../../../../../docs/adr/0002-single-evidence-layer.md),
[Task 9](../../../../../../skills/references/task_distill.md),
and [note writing style](../../../notes/note-writing-style.md).

## Goals

- Make memnotes' `notes/` layer the permanent knowledge layer for reusable
  knowledge — not a mandated home for all scientific documentation — and retire
  the mandatory Evidence Pack machinery.
- Keep data-local documentation (metadata, units, run settings, schemas,
  calibration, single-dataset interpretation) embedded or adjacent in its native
  data repository; extract independently reusable findings into memnotes with
  precise source links, without mandatory per-dataset duplicate notes/pointers.
- Define a note format that is self-contained, current-truth-first, and free of
  arbitrary size/score constraints.
- Define lifecycle rules (draft/stable/deprecated) grounded in substantive review,
  not test success or elapsed time.
- Cut over all consumers (CLI checks, docs, templates, projections, the proposal
  workflow, and the flat-spec migration) consistently.

## Non-Goals

- No new knowledge database or query system; `notes/` plus `index.md` stays.
- No proof hierarchy or formal confidence calculus for notes.
- No new note edition/versioning mechanism beyond existing frontmatter.
- No physics recomputation and no change to any scientific verdict already recorded.
- No unreviewed bulk deletion. Live vault cutover requires a separately approved
  source-to-destination disposition plan; this approval authorizes no such execution.

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-001 | Writers record only durable reusable explanations, results, or decisions. "No new knowledge" is a valid outcome of any session; task closure and routine verification stay compactly in the existing work record, with raw diagnostics as disposable scratch. | must |
| FR-002 | Notes are named by concept, question, or result; open with the current takeaway; are self-contained (assumptions, conditions, uncertainty, supporting links, reproducibility links); and connect to related concepts and `index.md`. No 30-line cap; no mandatory confidence scores. | must |
| FR-003 | Temporary working material belongs in managed scratch, not a new permanent note status. Retain `draft`, `stable`, and `deprecated`; stable promotion requires substantive human review, never elapsed time, formatting checks, or test success alone. Useful unresolved findings may remain draft. | must |
| FR-004 | Refine the current explanation in place; merge duplicate concepts without erasing differing settings or negative results; split independently maintainable topics. Prominently correct/retract invalid claims, retain consequential failure explanations, and update incoming/index links. Neither a newer timestamp nor a status label settles conflicting scientific claims. | must |
| FR-005 | Retire mandatory Evidence Packs, manifests, forced pack-to-note distillation, and acceptance/review sidecars. Criterion-specific observations and real review decisions belong compactly in the existing work record. Preserve actual verification, independent review, source binding and scope authority; do not recreate a dossier under another name or hidden directory. | must |
| FR-006 | Later note edits, merges or deprecations must not retroactively revoke historical task completion. Preserve what was actually verified and reviewed against its recorded source state; never fabricate approval or refresh historical hashes to current bytes merely to satisfy validation. | must |
| FR-007 | Independently reusable scientific findings become explanatory notes, including qualified negative/provisional results. Metadata, units, run settings, schemas, calibration, and interpretation needed only to understand one dataset may remain embedded or adjacent to that dataset in its native data repository, inside or outside memnotes; extracting reusable findings requires precise source links but never a mandatory duplicate note or pointer per dataset. Native data remain in suitable repositories/data stores with precise reproducibility links. Do not dump datasets into Markdown or destroy unique/uncommitted snapshots before durable recovery is established. | must |
| FR-008 | Cut over CLI checks, completion/STATUS readers, templates, skill references, generated guidance, proposal inputs and migration consumers consistently. Existing vault content follows a separately approved source-to-destination plan; unresolved ownership/provenance blocks destructive action. Installation retains its own approval boundary. | must |
| FR-009 | Frontmatter and OKF/Obsidian compatibility (`type`, `status`, relative links) is preserved; `index.md` remains the progressive-disclosure entry point. | should |
| FR-010 | Skill-material candidacy: on note creation and on substantive content updates, writers assess whether the note is suitable to evolve into skill material, defaulting to no; the assessment is recorded in the note's own metadata (missing = default), never as a separate assessment artifact, and candidacy is never a completion dependency — no forced proposal, no extra packs, and an explicit no-proposal outcome is valid. Knowledge and guideline notes remain legitimate skill references without becoming procedures. Note metadata separately distinguishes candidacy from actual use: a stable-identifier list of skill topics that actually use this note as a resource, updated only after approved publication or removal of that use (missing = empty); a note may be an in-use resource and still a candidate for further use. Dataset-local metadata stays beside its data (FR-007) and is excluded from the central note metadata set. | must |
| FR-011 | Incremental curation, independent of the creation-time assessment: weekly and manual full-scope curation runs share one per-scope last-successful-checkpoint and review only notes whose semantic updated timestamp (creation-date fallback when never updated; UTC with sufficient precision; never filesystem mtime) falls in the window since that checkpoint L through a cutoff U frozen at run start (L < changed_at ≤ U), reviewing candidacy-flagged notes first and existing skill-resource references for stale guidance. A successful run — including a no-action run — advances the shared checkpoint to U; a failed or incomplete run does not; a targeted manual run over a note subset does not advance the broader checkpoint; edits after U are reviewed next run. Equal timestamps resolve by the window rule; same-scope concurrent runs serialize; the first run uses an explicit bounded-from or a deliberate baseline; date-only legacy timestamps are handled without silently dropping notes; bookkeeping-only skill-metadata writes do not bump semantic updated (no self-requeue). No new queue, framework, or report; publication and installation stay behind their existing separate approval gates. | must |

For curation, changing candidacy is a semantic update and enters the next window;
syncing actual-use links or recording a check alone is bookkeeping, not a new
content timestamp. New notes explicitly emit the two metadata fields; omitted
legacy values retain their defaults without a mandatory bulk rewrite.

## Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-001 | Compatibility: notes remain Obsidian-readable and OKF v0.2 conformant; no separate export tree. | must |
| NFR-002 | Safety: no requirement forces deletion or rewriting of historical records; every destructive step requires a separate approved plan and resolved provenance. | must |
| NFR-003 | Simplicity: retirement removes machinery rather than relocating it; no replacement dossier format substitutes for evidence packs. | must |

## Success Criteria

Demonstrate the content transformations on bounded copies of the audited examples
before any separately approved live-vault batch.

- [ ] An ordinary code fix passes checked completion without creating `evidence/`, mandatory proof/review sidecars, or a manufactured note when no reusable finding emerged.
- [ ] A campaign correction presents the supported current conclusion first and labels the superseded interpretation without erasing the important failed approach.
- [ ] The conflicting metadata example becomes one coherent note; differences in physical settings, uncertainty and negative results survive consolidation, and existing links resolve.
- [ ] The scientific report example keeps dataset-local metadata, units, run settings, schema, calibration and single-dataset interpretation embedded or adjacent to the native data; independently reusable findings surface as notes with precise source links; no per-dataset duplicate note/pointer is manufactured and no numerical dataset is flattened into prose or lost.
- [ ] Later refinement, merge or deprecation of a note leaves the historical completion result intact without rewriting prior approvals or pins.
- [ ] Current documentation and runtime agree: no mandatory pack-to-note chain or replacement dossier remains; relevant verification/review obligations are still checked.
- [ ] A default note and an in-use skill resource are distinguishable: a newly created or substantively updated note carries only the default (negative) candidacy indicator unless candidacy is deliberately flagged, while a note actually used by an approved skill topic lists that topic's stable identifier — and the two are independent, so an in-use resource can still be a candidate for further use (exact field names per the approved architecture design).
- [ ] Curation reviews only eligible notes within L < changed_at ≤ U, prioritizing flagged candidates and changed actual-use resources: a successful no-action run advances the checkpoint shared by weekly and manual full-scope runs; a failed run and a targeted manual subset run leave it unchanged; notes at either boundary land on the correct side of the window.
- [ ] An explicit no-action curation outcome requires neither a skill proposal nor extra packs, and neither candidacy nor curation triggers publication or installation — the separate approval gate is unchanged.

## Next Gate

The amended PRD and Architecture are approved (2026-10-17), and
[Epic 001](epics/epic-001.md) is approved (2026-10-18). Its
[five Stories](epics/epic-001.md#stories) are draft; implementation requires
approval of each individual Story.
A concrete live-vault disposition plan and any installation remain later, separately
approved actions — not authorized by these approvals.

Next review: [the five draft Stories](epics/epic-001.md#stories); the approved
design is [Architecture](architecture.md).
