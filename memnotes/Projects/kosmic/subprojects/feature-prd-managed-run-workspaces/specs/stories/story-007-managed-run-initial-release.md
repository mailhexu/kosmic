---
status: "done"
created: "2026-09-14"
updated: "2026-09-16"
linked_epic: "../epics/epic-002-managed-run-initial-release.md"
linked_architecture: "../architecture.md"
linked_prd: "../prd.md"
related_notes: ["../../../../notes/managed-run-workspace-lifecycle.md", "../../../../notes/cli-projection-commands.md"]
consumer_interface_change: true
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
review_base: ""
review_round: 0
project_id: "kosmic"
subproject_id: "feature-prd-managed-run-workspaces"
record_kind: "story"
local_id: "007"
---

# Story 049: Managed Run Initial Release

## User Story

As a Kosmic contributor, I want the complete non-general-destructive lifecycle dogfooded and released so that new work stops creating unmanaged temporary debris before broad cleanup is enabled.

## Acceptance Criteria

- [ ] Stories 043–048, 052, 053, and 056 are done; required Task P artifacts are accepted before release work begins.
- [ ] An actual multi-tool-call run proves begin, live status, promotion, success cleanup, persisted receipt, and Git before/after evidence entirely under `.tmp/kosmic/`.
- [ ] A failed diagnostic run proves 72-hour retention, explicit capped extension, status byte accounting, and dry-run eligibility without destructive general GC.
- [ ] Holder crash and interrupted owner cleanup prove recovery snapshots, grace, operation replay, and preservation of unrelated worktree files.
- [ ] Seeded secrets do not appear in lifecycle outputs, manifests, receipts, history, or diagnostics.
- [ ] Complete focused and full suites, project/library generation and validation, completion gates, and supported adapter byte checks pass.
- [ ] Evidence Pack, Impact Ledger, notes, CLI docs, release notes, and mandatory Standards/Spec/security reviews are complete.

## Tasks

### Phase 1: Research
- [ ] Confirm supported adapter and filesystem matrix for the release environment.
- [ ] Define dogfood runs and expected Git deltas.

### Phase 2: Tests
- [ ] Add end-to-end success, retained failure, crash recovery, secret, linked-worktree, and no-system-temp scenarios.
- [ ] Run full regression suites before release changes.

### Phase 3: Implementation
- [ ] Complete generated outputs, docs, evidence, impact, and release metadata.
- [ ] Install and byte-verify supported adapters without enabling general `gc --apply`.

### Phase 4: Review
- [ ] Run complete Standards, Spec, and security review.
- [ ] Re-run all release and Git-status checks after corrections.

## Routine Decision

This story releases already approved interfaces and introduces no new procedure routine edge. No routine proposal is required.

## Definition of Done

- [ ] Initial-release acceptance matrix passes end to end.
- [ ] General `gc --apply` and destructive publication recovery remain disabled.
- [ ] Evidence, impact, notes, generated artifacts, adapters, and Git records are current.
- [ ] Review has no unresolved Blocking finding.
