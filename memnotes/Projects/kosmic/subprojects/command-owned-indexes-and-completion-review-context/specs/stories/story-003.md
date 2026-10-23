---
project_id: "kosmic"
subproject_id: "command-owned-indexes-and-completion-review-context"
status: "draft"
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
routine_proposals: []
review_round: 0
completion_observations: []
completion_review: {}
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

This exposes reusable deterministic preparation mechanics through a supported CLI, so the existing routine-decision gate applies. Inspect the generated inventory and record the applicable governed Task P disposition(s) in `routine_proposals` before completion. Existing fingerprint implementation remains the owner; neither classification nor a successful hash authorizes routine publication, automatic review or extra functionality.

## Technical Notes and Boundaries

- `--worktree` is optional for compatibility but explicit when hashing; there is no `--source-root` alias, new sibling command or `--write` mode.
- The existing algorithm deliberately distinguishes same-root/nested/external layouts. Preserve its exact behavior rather than introducing preparation-only registration or containment policy.
- Excluded work-record bytes still need the existing context/scope review; unchanged digest does not prove unchanged approval context.
- Run meaningful consumer-visible tests, not parser-forwarding mocks, source-text checks or exact incidental wording assertions.

## Completion

Require all AC observations, read-only/binding smoke, related-note/projection consistency, applicable routine decisions, converged independent review and native completion receipt. Use the integrated affected suite after implementation stabilizes. Capture findings locally in this record or the existing durable note, not a new evidence sidecar.

Draft; awaiting user Story approval. No implementation or verification results are claimed.
