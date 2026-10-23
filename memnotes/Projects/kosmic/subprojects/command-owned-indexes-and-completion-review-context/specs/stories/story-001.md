---
project_id: "kosmic"
subproject_id: "command-owned-indexes-and-completion-review-context"
status: "approved"
record_kind: "story"
local_id: "001"
linked_prd: "../prd.md"
linked_epic: "../epics/epic-001.md"
linked_architecture: "../architecture.md"
depends_on: []
created: "2026-10-23"
updated: "2026-10-23"
related_notes: ["notes/cli-projection-commands.md"]
consumer_interface_change: true
proposal_required: false
routine_edge_change: false
routine_decision_required: true
routine_proposals: []
review_round: 0
completion_observations: []
completion_review: {}
---

# Indexed spec creation and deterministic recovery

## User Story

As a Kosmic caller, I want each successful spec creation to publish its indexed draft and return the canonical paths, so I do not construct rows, discover paths or verify successful administrative output again.

## Authority and Scope

Parent: [Epic 001](../epics/epic-001.md); requirements: PRD FR-001–004; design: Architecture ADR-002–003 and creation-side ADR-004.

Own all five kinds' reservation, record/index publication, explicit result paths, deterministic resume and creation-writer serialization. Keep existing identity/parent admission and historical `paths` representations. No historical index migration, approval changes, generic transaction framework or arbitrary-editor transaction guarantee.

Primary implementation is `skills/scripts/kosmic_specs.py`, creation dispatch/result handling in `kosmic_project_skills.py`, and existing creation regression suites. [Story 002](story-002.md) owns finish-writer coordination and the complete guidance cutover.

## Acceptance Criteria

- [ ] AC-001: Each supported kind (`prd`, `architecture`, `epic`, `story`, `quick-task`) returns non-null `operation_id` plus canonical Project-relative `record_path` and `index_path`; success occurs only after its draft and exactly one correct owning-index row are published.
- [ ] AC-002: New rows contain the record title/kind/state and exact index-relative link in a table finish can update. Preserve unrelated prose/rows and legacy sections; create a missing index or append a compatible table without bulk conversion.
- [ ] AC-003: Resume after interruption at reservation/record/index/publication-marker boundaries retains the originally reserved owner, identity and output paths. It preserves unrelated intervening index edits, never duplicates the row and retains refusal for already-published operations.
- [ ] AC-004: Changed reserved-record bytes, ambiguous/conflicting entries and unsafe targets are refused without overwriting current content. Diagnostics identify the operation and incomplete/conflicting path; partial publication is never reported as success.
- [ ] AC-005: Supported concurrent creations preserve both reserved identities and all rows using the existing lock. Resume uses current index content rather than restoring an old whole-file snapshot.
- [ ] AC-006: Existing incomplete PRD operations remain safely resumable without historical operation rewrites on inspection. Existing owner/parent containment, identity rules, result fields and refusal precedence are retained.

## Implementation and Verification

1. Reuse the approved design and existing knowledge; inspect only unresolved implementation seams. Pin one fixed review baseline before source edits.
2. TDD in existing creation tests: assert public record/row/path behavior, preservation, operation replay and conflict outcomes. Replace incidental template-byte assertions rather than repinning wording.
3. Extend current creation operations/staging under the existing lock. Reserve before publication, merge only the owned row, publish the operation marker last, and preserve no-follow/no-overwrite safeguards.
4. Smoke the actual documented CLI across all kinds and an interrupted/resumed creation in governed disposable fixtures. Observe retained identity/content and returned paths; no second administrative confirmation command.
5. Record actual criterion observations and revision-bound independent Standards/Spec review in this record. Finish through the native checked path; no hand-written `done`.

## Routine Decision

This materially changes reusable deterministic creation mechanics, so the existing routine-decision gate applies. Before completion, inspect the generated routine inventory and record the applicable governed Task P disposition in `routine_proposals`. Do not manufacture a new shared routine, publish a skill, or claim a disposition before the implementation evidence supports it. CLI ownership remains as approved; a proposal requiring extra authority retains its own gate.

## Technical Notes and Boundaries

- Publication is per-path and recoverable, not cross-file atomic. Unknown conflicting record bytes remain a conflict even when their frontmatter identity matches.
- Index lookup is by canonical link, not title substring; matching incompatible/non-table or multiple entries are conflicts, not permission to append a duplicate.
- Creation holds its existing lock. Helpers need an explicit lock-owned calling convention so Story 002 can coordinate finish without recursive acquisition.
- Caller migration is deliberately sequenced in Story 002; until then do not claim the overall Epic or native workflow cutover complete.

## Completion

AC observations, consumer-note/projection consistency, applicable routine decisions, actual CLI smoke, and converged independent review must pass the existing native completion gates. Capture only durable new knowledge; no separate evidence sidecar or duplicate completion log.

Approved by the user in this conversation. Implementation and its required verification/review may proceed; no results are claimed yet.
