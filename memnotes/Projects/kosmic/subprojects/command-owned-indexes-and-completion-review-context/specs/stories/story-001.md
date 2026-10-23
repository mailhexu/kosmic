---
project_id: "kosmic"
subproject_id: "command-owned-indexes-and-completion-review-context"
status: done
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
routine_proposals: ["../../../../specs/skill-proposals/2026-10-23-native-cli-routine-decision.md"]
review_base: "216b709f0f33fd33c25e4fea77ba1c28752d3753"
review_round: 3
completion_observations:
  - criterion: "AC-001: Each supported kind (`prd`, `architecture`, `epic`, `story`, `quick-task`) returns non-null `operation_id` plus canonical Project-relative `record_path` and `index_path`; success occurs only after its draft and exactly one correct owning-index row are published."
    observation: "Final live CLI created all five indexed draft kinds with explicit canonical paths and non-null operation IDs; each native row/result case passed in the complete creation suite."
    source: "Final smoke_creation.py EXIT0; python3 -B -m unittest tests.test_kosmic_spec_creation -q:30 tests passed (4.033s)."
  - criterion: "AC-002: New rows contain the record title/kind/state and exact index-relative link in a table finish can update. Preserve unrelated prose/rows and legacy sections; create a missing index or append a compatible table without bulk conversion."
    observation: "Canonical table rows preserve escaped titles and unrelated index context. Native creation now selects only matching Kind/Record/Status layouts or appends its own compatible table; missing final newlines no longer glue rows. Actual native finish preserved links and changed only the status cell in all four historical-layout fixtures."
    source: "Creation suite33 tests passed (1.605s); four new layout regression subcases failed before repair; actual CLI smoke passed task-header, reordered, extra-column and missing-final-newline cases."
  - criterion: "AC-003: Resume after interruption at reservation/record/index/publication-marker boundaries retains the originally reserved owner, identity and output paths. It preserves unrelated intervening index edits, never duplicates the row and retains refusal for already-published operations."
    observation: "Current interrupted operations resumed the original identity and preserved unrelated index edits without duplicate rows; published operations and changed authored drafts were refused."
    source: "Creation suite33 tests passed; actual escaped-title probes and four historical-layout CLI finish fixtures passed after reproduced failures; prior smoke retained unrelated context and refused changed drafts."
  - criterion: "AC-004: Changed reserved-record bytes, ambiguous/conflicting entries and unsafe targets are refused without overwriting current content. Diagnostics identify the operation and incomplete/conflicting path; partial publication is never reported as success."
    observation: "Changed record bytes, unsafe symlinks, altered reserved index/documents targets and project/operation identity mismatches were refused before unsafe writes. The final actual containment probe left outside-Project bytes unchanged."
    source: "Seven new safety cases were RED before fixes; complete30-case suite passed; final probe_resume_containment.py exit2, outside_project_changed=false."
  - criterion: "AC-005: Supported concurrent creations preserve both reserved identities and all rows using the existing lock. Resume uses current index content rather than restoring an old whole-file snapshot."
    observation: "Pending sequential001 remained allocated while the next Epic received002; pending fixed identities refused fresh takeover. Concurrent rows and external index edits survived under the existing lock/current-content guard."
    source: "Complete30-case suite including pending identity and injected external-divergence cases; final live pending probe printed001/002, first operation still reserved."
  - criterion: "AC-006: Existing incomplete PRD operations remain safely resumable without historical operation rewrites on inspection. Existing owner/parent containment, identity rules, result fields and refusal precedence are retained."
    observation: "Literal historical PRD operations replayed the independent static baseline bytes and legacy bullet/prose without migration; current v2 valid resumes retained authoritative stored draft bytes and existing result representation/refusal rules."
    source: "Complete30-case creation suite passed, including literal-v1 and recorded-input/v2 recovery; final native five-kind/resume smoke EXIT0."
completion_review:
  reviewer: "Main"
  axes:
    standards:
      decision: "approved"
      reviewer: "CreationStandardsScout"
    spec:
      decision: "approved"
      reviewer: "CreationSpecResume"
  decision: "approved"
  review_base: "216b709f0f33fd33c25e4fea77ba1c28752d3753"
  reviewed_revision: "3cbbe6705fd99b9224ced1e734da84f34b3e33509e82f713ef78085983de38f9"
  findings:
    - id: "STD-001"
      axis: "standards"
      disposition: "Blocking"
      status: "resolved"
      introduced_round: 1
      summary: "Escaped bracket/pipe titles could not resume and finish corrupted pipe-title links."
      evidence: "Actual pre-fix CLI probe; two permanent methods reproduced3 failures. Shared escape-aware parsing repaired both consumers;32-case suite and actual native title finish now pass."
      required_resolution: "Repair emitted title roundtrip and preserve non-status cells at finish."
      resolution: "fixed"
    - id: "STD-002"
      axis: "standards"
      disposition: "Non-blocking"
      status: "resolved"
      introduced_round: 1
      summary: "Exceptional descriptor cleanup closed the same descriptor twice."
      evidence: "Removed except close; finally alone owns retained entry_fd cleanup."
      resolution: "fixed"
    - id: "STD-003"
      axis: "standards"
      disposition: "Blocking"
      status: "resolved"
      introduced_round: 1
      summary: "Canonical row inserted under incompatible status table columns causes link/status corruption and resume refusal."
      evidence: "Both first-pair reviewers escalated STD-003 after concrete live row/link corruption and interrupted-resume failures across incompatible table layouts."
      worker_response:
        kind: "fixed"
        detail: "Only exact canonical Kind/Record/Status table is selected; other existing layouts receive a separate canonical table without conversion."
        evidence: "Four layout subcases failed before repair;33 creation tests passed; actual CLI finish passed task-header, reordered, extra-column and no-final-newline layouts."
      resolution: "fixed"
    - id: "STD-004"
      axis: "standards"
      disposition: "Non-blocking"
      status: "open"
      introduced_round: 1
      summary: "Unused operation_id parameter in _ensure_index_row."
      evidence: "CreationStandardsReview optional cleanup advisory; unchanged."
    - id: "STD-005"
      axis: "standards"
      disposition: "Blocking"
      status: "resolved"
      introduced_round: 1
      summary: "Missing final newline concatenates inserted row with the previous physical table line."
      worker_response:
        kind: "fixed"
        detail: "Terminate the preceding compatible table line before inserting the new row."
        evidence: "Missing-final-newline regression RED before repair;33-case suite plus actual native finish fixture now pass."
      resolution: "fixed"
    - id: "SP-001"
      axis: "spec"
      disposition: "Non-blocking"
      status: "open"
      introduced_round: 1
      summary: "Unused record_parts parameter in _publish_reservation; optional cleanup intentionally unchanged."
    - id: "STD-006"
      axis: "standards"
      disposition: "Non-blocking"
      status: "open"
      introduced_round: 2
      summary: "Docstring omits exact canonical-table selection rule; optional clarification unchanged."
    - id: "STD-007"
      axis: "standards"
      disposition: "Non-blocking"
      status: "open"
      introduced_round: 2
      summary: "Canonical header-column literal could drift with future header changes; optional deduplication unchanged."
    - id: "STD-008"
      axis: "standards"
      disposition: "Non-blocking"
      status: "open"
      introduced_round: 2
      summary: "Extra test-module blank lines; cosmetic advisory unchanged."
    - id: "STD-009"
      axis: "standards"
      disposition: "Non-blocking"
      status: "open"
      introduced_round: 2
      summary: "Optional additional second-creation/corrupted-historical-row coverage; no defect found."
  scope:
    - "worktree:skills/scripts/kosmic_specs.py"
    - "worktree:tests/test_kosmic_spec_creation.py"
    - "worktree:skills/scripts/kosmic_completion.py"
    - "project:subprojects/command-owned-indexes-and-completion-review-context/specs/stories/story-001.md"
    - "project:notes/cli-projection-commands.md"
    - "project:notes/cli-extension-conventions.md"
    - "project:skills/"
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

The independent [routine disposition](../../../../specs/skill-proposals/2026-10-23-native-cli-routine-decision.md) is `no_action` / `none`, approved by the user through the required decision prompt. The knowledge-role sources do not establish a separately governed executable procedure; the sole inventoried atomic whole-tree publisher is not these CLI mechanics. No routine or skill is extracted or published. The existing routine gate remains enabled; the proposal is reviewed with this implementation.

## Technical Notes and Boundaries

- Publication is per-path and recoverable, not cross-file atomic. Unknown conflicting record bytes remain a conflict even when their frontmatter identity matches.
- Index lookup is by canonical link, not title substring; matching incompatible/non-table or multiple entries are conflicts, not permission to append a duplicate.
- Creation holds its existing lock. Helpers need an explicit lock-owned calling convention so Story 002 can coordinate finish without recursive acquisition.
- Caller migration is deliberately sequenced in Story 002; until then do not claim the overall Epic or native workflow cutover complete.

## Completion

AC observations, consumer-note/projection consistency, applicable routine decisions, actual CLI smoke, and converged independent review must pass the existing native completion gates. Capture only durable new knowledge; no separate evidence sidecar or duplicate completion log.

Two complete independent pairs converged on the authored source; the third pair confirmed exact baseline bytecode restoration and the resulting clean binding 3cbbe6705fd99b9224ced1e734da84f34b3e33509e82f713ef78085983de38f9. Native finish had correctly refused out-of-scope tracked bytecode drift and the stale prior fingerprint. CreationStandardsScout and CreationSpecResume independently confirmed all three authored files unchanged, baseline caches restored and approval applicable to this binding; no test rerun or fresh code audit was needed. The33-case suite and actual CLI creation/recovery/finish smokes passed, including four historical table layouts. All Blocking fixes are reviewer-accepted; optional advisories remain open. Provider-failed attempts count no round. The no-action routine disposition remains user-approved; native finish alone will publish completion.
