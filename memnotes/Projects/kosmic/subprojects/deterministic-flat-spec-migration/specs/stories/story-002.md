---
project_id: "kosmic"
subproject_id: "deterministic-flat-spec-migration"
record_kind: "story"
local_id: "002"
status: done
created: "2026-10-11"
updated: "2026-10-11"
linked_epic: "../epics/epic-001.md"
linked_architecture: "../architecture.md"
linked_prd: "../prd.md"
depends_on: ["story-001.md"]
related_notes: ["notes/cli-projection-commands.md"]
consumer_interface_change: true
proposal_required: false
routine_edge_change: false
routine_decision_required: true
routine_proposals: ["../../../../specs/skill-proposals/2026-10-11-migration-routine-decision.md"]
review_base: "22a36f09af5fce16c2d097c68ab9988f27c3705f"
review_round: 3
acceptance_evidence: ["evidence/2026-10-11-deterministic-flat-spec-migration/acceptance-002.json"]
review_record: "evidence/2026-10-11-deterministic-flat-spec-migration/review-002.json"
---

# Story 002: Apply approved plans and recover interruption

## User Story

As a Project maintainer, I want checked script-driven application and recovery of an approved migration plan, so that publication is safe, repeatable and independent of an agent.

## Scope

Implement `kosmic_migration.py` and real `migrate-subprojects-apply`/`migrate-subprojects-recover` CLI commands using Story 001's plan contract. Cover Architecture AD-M02 through AD-M06. Preserve the Project root/lock inode and use checked per-path transactions, not whole-Project replacement.

## Acceptance Criteria

- [ ] AC1: Both commands require the selected Project, saved plan, matching explicitly approved digest and current approved/in-progress shared Quick Task authority. Draft, terminal, foreign, revoked or owner-local records cannot authorize migration; bootstrap resolution does not require the catalog being established.
- [ ] AC2: Apply recomputes the canonical plan with saved inputs/assignments and checks complete source inventory, hashes, candidate bytes and destination state. Ambiguity, tampering, missing/new records, drift, collisions, traversal, symlink components and non-regular files reject without changing authoritative records.
- [ ] AC3: The staged candidate passes `SpecCatalog.validate` and intended live-link checks before authoritative mutation. New owner entries/indexes and record identities are correct; old feature files are removed only through checked operations.
- [ ] AC4: Under the existing creation lock, durable before images and ordered intent/result records precede each publication/deletion. Ordinary injected failure restores original affected bytes; unrelated work is unchanged and the Project root and lock remain intact.
- [ ] AC5: Actual subprocess interruption at intent/publication boundaries leaves a recognizable incomplete transaction. Explicit recovery reconciles recorded hashes, restores incomplete application or verifies/finalizes complete output; external edits cause a conflict instead of being overwritten. A second transaction refuses while recovery is required.
- [ ] AC6: A successful receipt records Project identity, exact plan/work-record identities, old-to-new mapping, input/output hashes, fingerprint review requirements and STATUS disposition. It is written last and is not work-completion authority.
- [ ] AC7: Repeating the same completed plan verifies its receipt/output hashes and makes no new content changes, owners or receipts. Completed-output drift reports a conflict rather than overwriting later work.
- [ ] AC8: Bound external STATUS belongs to the transaction and rollback; an unbound Project remains unbound. Lifecycle decisions, immutable evidence/log bytes and historical completion semantics are preserved without minted approvals.
- [ ] AC9: Actual apply/recover CLI smoke and permanent state-transition regressions prove success, rejection, ordinary rollback, interruption recovery and idempotence; focused checks pass and code receives independent review.

## Tasks

### Research and TDD

- [ ] Inspect existing lock, no-follow access, managed run, catalog and status seams; retain a single planner implementation.
- [ ] Start in a clean dedicated worktree and pin the review baseline.
- [ ] Write failing-before boundary and transaction tests, including real subprocess interruption and recovery conflicts.

### Implementation

- [ ] Implement schema/digest validation and current shared-task authorization before mutation.
- [ ] Stage the minimal complete candidate, validate it, and implement durable checked per-path transactions and recovery.
- [ ] Integrate real apply/recover commands, receipt verification and typed actionable errors.

### Verification and Review

- [ ] Run actual commands on disposable representative Projects; compare exact affected and unrelated bytes before/after.
- [ ] Record criterion-specific evidence/hashes and complete independent Standards/Spec review.
- [ ] Update consumer docs/knowledge and use checked completion; no hand-edited done status.

## Routine Decision

Transaction, recovery and receipt mechanics introduce reusable deterministic behavior. Task P must classify reuse/extension/new routine, produce the actual governed proposal, populate `routine_proposals` and satisfy its evidence/approval gates before completion. Do not pretend existing whole-tree publication recovery supports source deletions.

## Constraints

No model calls, installed-skill changes, automatic task approval or live migration without separately approved authority. Raw editors remain a compliance boundary; locking is not claimed filesystem isolation. Do not roll back externally modified files blindly.

## Progress

Approved by the user and implemented. Actual API/CLI scenarios prove authority and drift rejection, staged validation, ordinary rollback, interrupted recovery, external-edit protection, candidate-run finalization and receipt idempotence. The suite and independent reviews passed; criterion-specific evidence is declared above. Canonical checked terminal closure remains pending the separately approved Project migration, not further executor implementation.
