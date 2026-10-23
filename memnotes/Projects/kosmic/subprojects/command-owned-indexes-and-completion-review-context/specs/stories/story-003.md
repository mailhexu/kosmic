---
project_id: "kosmic"
subproject_id: "command-owned-indexes-and-completion-review-context"
status: done
record_kind: "story"
local_id: "003"
linked_prd: "../prd.md"
linked_epic: "../epics/epic-002.md"
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
review_round: 1
completion_observations:
  - criterion: "AC-001: Without `--worktree`, existing `work prepare-completion` arguments, output and refusal behavior remain unchanged; no writer is inferred from the current directory."
    observation: "Default invocation retained its original three-key payload and refused invalid records as before; the tracer ran from a Git directory and inferred no writer."
    source: "Focused preparation/record-scoped suites (45 cases; 44 passed initially, one unrelated YAML-spelling assertion corrected and its case passed)."
  - criterion: "AC-002: With an explicit writer, successful output adds only top-level `source_revision` to the existing payload and computes it through the unchanged function. Preserve authored observation entries field-for-field, including adverse/extra fields, and leave unauthored criteria blank."
    observation: "Explicit writer output preserved adverse and extra authored fields, kept blank drafts blank, and added only source_revision; the live client also verified unchanged observations."
    source: "tests.test_prepare_completion_prefill; smoke_completion.py actual CLI, EXIT 0."
  - criterion: "AC-003: Real staged/unstaged/untracked/deleted source and excluded metadata affect the returned value exactly as the existing algorithm dictates for its same-root, nested and external Project relationships. Do not substitute Git HEAD or introduce new exclusions."
    observation: "External, same-root and nested layouts exercised staged/unstaged/untracked/deleted source and the existing exclusions; meaningful source changed the digest while excluded metadata did not."
    source: "Focused tests.test_prepare_completion_prefill behavioral cases passed."
  - criterion: "AC-004: Preparation leaves Project/writer bytes unchanged on success and refusal, creates no persistent operational outputs, and adds no clean/start/registration requirement, lock, state repair or planning/terminal-record bypass. Existing record/ancestry/acceptance and invalid-writer diagnostics remain."
    observation: "Project/writer byte snapshots were unchanged on success and WORK_PHASE_DENIED refusal; invalid writer diagnostics passed. Live preparation also left the fixture unchanged."
    source: "tests.test_prepare_completion_prefill; smoke_completion.py read_only=true."
  - criterion: "AC-005: Finish accepts a matching actually reviewed revision and refuses subsequent source drift through its existing binding/freshness checks; preparation fabricates no evidence, approval or outcome and never repins a stale review."
    observation: "The live CLI refused REVIEW_INVALID after source drift without mutating the record, then returned a successful receipt after restoring the actually reviewed source; matching/stale finish regression cases passed."
    source: "smoke_completion.py EXIT 0 at 2026-10-23T06:31:15Z; corrected drift-refusal case EXIT 0, 0.367s."
  - criterion: "AC-006: All affected callers use the supported explicit-writer preparation output; the internal-import fingerprint recipe is removed, related canonical knowledge/projections are consistent, and the documented CLI sequence works without an extra administrative confirmation command."
    observation: "Replaced the internal-import recipe with supported explicit-writer preparation and documented the optional branch. Updated the existing canonical CLI note; native generation published the atomic Skill Pair successfully."
    source: "Worker manifest: work_completion.md, task_project_skills.md; native generate EXIT 0; live preparation/finish client EXIT 0."
completion_review:
  reviewer: "Main"
  axes:
    standards: {decision: "approved", reviewer: "PrepStandardsReview"}
    spec: {decision: "approved", reviewer: "PrepSpecReview"}
  decision: "approved"
  review_base: "216b709f0f33fd33c25e4fea77ba1c28752d3753"
  reviewed_revision: "726aaecc1af1305d0ee32b0238cbdb3f183d11ff033d1500bb8d58e7125cd2ef"
  findings:
    - id: "STD-001"
      axis: "standards"
      disposition: "Non-blocking"
      status: "open"
      introduced_round: 1
      summary: "Optional snapshot(root) argument annotation consistency."
      evidence: "tests/test_prepare_completion_prefill.py:119; PrepStandardsReview advisory only."
      required_resolution: "None; optional suggestion intentionally left unchanged."
  scope: ["worktree:skills/scripts/kosmic_project_skills.py","worktree:skills/references/work_completion.md","worktree:tests/test_prepare_completion_prefill.py","worktree:tests/test_record_scoped_completion.py","worktree:skills/references/task_project_skills.md","project:subprojects/command-owned-indexes-and-completion-review-context/specs/stories/story-003.md","project:notes/cli-projection-commands.md","project:skills/","project:specs/skill-proposals/2026-10-23-native-cli-routine-decision.md","project:specs/skill-proposals/inputs/2026-10-23-native-cli-routine-decision.md"]
---

# Explicit-writer completion preparation and caller cutover

## User Story

As a Kosmic worker or reviewer, I want completion preparation to return the current writer fingerprint alongside preserved criterion drafts, so I can bind review without importing internal Python modules or learning another command.

## Authority and Scope

Parent: [Epic 002](../epics/epic-002.md); requirements: FR-005–007 and fingerprint FR-008; design: Architecture ADR-001 and Fingerprint and Authority Invariants.

Own the optional explicit-writer argument/output, read-only preservation and binding coverage, internal-import recipe removal and all affected fingerprint callers/references. No functional dependency on Stories 001/002, but shared CLI/guidance edits have one integration owner.

Primary seams: `kosmic_project_skills.py` preparation parser/dispatch, unchanged `kosmic_completion.prepare_completion`/`source_revision`, existing preparation/finish regression suites, `work_completion.md`, command references and canonical CLI knowledge. Regenerate canonical projections after the source-note update; no direct generated/installed-file edits or implicit installation/push authority.

## Acceptance Criteria

- [ ] AC-001: Without `--worktree`, existing `work prepare-completion` arguments, output and refusal behavior remain unchanged; no writer is inferred from the current directory.
- [ ] AC-002: With an explicit writer, successful output adds only top-level `source_revision` to the existing payload and computes it through the unchanged function. Preserve authored observation entries field-for-field, including adverse/extra fields, and leave unauthored criteria blank.
- [ ] AC-003: Real staged/unstaged/untracked/deleted source and excluded metadata affect the returned value exactly as the existing algorithm dictates for its same-root, nested and external Project relationships. Do not substitute Git HEAD or introduce new exclusions.
- [ ] AC-004: Preparation leaves Project/writer bytes unchanged on success and refusal, creates no persistent operational outputs, and adds no clean/start/registration requirement, lock, state repair or planning/terminal-record bypass. Existing record/ancestry/acceptance and invalid-writer diagnostics remain.
- [ ] AC-005: Finish accepts a matching actually reviewed revision and refuses subsequent source drift through its existing binding/freshness checks; preparation fabricates no evidence, approval or outcome and never repins a stale review.
- [ ] AC-006: All affected callers use the supported explicit-writer preparation output; the internal-import fingerprint recipe is removed, related canonical knowledge/projections are consistent, and the documented CLI sequence works without an extra administrative confirmation command.

## Implementation and Verification

1. Reuse the approved design and known implementation seams; resolve only remaining facts from current code/docs. Pin one fixed review baseline before source changes.
2. TDD in existing preparation and finish suites: both argument paths, observation preservation/blanks, meaningful source changes/exclusions, existing refusals and filesystem snapshots on success/failure.
3. Add optional `--worktree` and the conditional output field. Resolve the writer exactly as finish/source_revision do; retain live record resolution and existing error handling. Do not reimplement hashing.
4. Smoke the real preparation → reviewed revision → finish path in governed disposable fixtures, including stale-source refusal. The emitted digest is a point-in-time observation, not cached permission.
5. Replace the obsolete recipe and update every affected command/guidance caller plus the canonical CLI invariant note. Regenerate projections through their normal owner; reconcile shared edits with Story 002.
6. Record actual AC observations and independent revision-bound Standards/Spec review, then complete through native finish.

## Routine Decision

The independent [routine disposition](../../../../specs/skill-proposals/2026-10-23-native-cli-routine-decision.md) is `no_action` / `none`, approved by the user through the required decision prompt. Knowledge-role inputs do not establish executable-reuse eligibility, and the existing fingerprint remains owned by the supported CLI rather than an unrelated shared publisher. No routine or skill is extracted or published. The existing routine gate remains enabled; the proposal is reviewed with this implementation.

## Technical Notes and Boundaries

- `--worktree` is optional for compatibility but explicit when hashing; there is no `--source-root` alias, new sibling command or `--write` mode.
- The existing algorithm deliberately distinguishes same-root/nested/external layouts. Preserve its exact behavior rather than introducing preparation-only registration or containment policy.
- Excluded work-record bytes still need the existing context/scope review; unchanged digest does not prove unchanged approval context.
- Run meaningful consumer-visible tests, not parser-forwarding mocks, source-text checks or exact incidental wording assertions.

## Completion

Require all AC observations, read-only/binding smoke, related-note/projection consistency, applicable routine decisions, converged independent review and native completion receipt. Use the integrated affected suite after implementation stabilizes. Capture findings locally in this record or the existing durable note, not a new evidence sidecar.

Both independent axes approved the held implementation and no-action disposition in Round 1. The optional annotation suggestion remains advisory; no source edits followed approval. Native finish alone publishes completion.
