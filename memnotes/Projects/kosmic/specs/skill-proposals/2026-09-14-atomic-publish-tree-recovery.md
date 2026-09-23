---
status: done
created: 2026-09-14
updated: 2026-09-15
result: update
scope: shared-routine
target_kind: routine
routine_action: extend
routine_id: kosmic/atomic-publish-tree
linked_proposals: []
consumer_approvals: []
target: kosmic/atomic-publish-tree
target_ref: routine://kosmic/atomic-publish-tree
target_sha256: aeaad9c360fe1a0a046196208d3bb5d17919cf6d418d4da0ce79e9d3016057fc
proposer_mode: subagent
proposer_ref: agent://ImplementManagedRunSuite.RoutineExtendProposer
proposer_reason: "Fresh-context Task P assessment restricted to the hash-pinned curated manifest"
input_manifest: [specs/skill-proposals/inputs/atomic-publish-tree-recovery.md]
related_notes: [notes/managed-run-workspace-lifecycle.md, notes/atomic-skill-publication.md]
evidence_packs: [2026-09-15-managed-run-lifecycle]
behavioral_evidence: [evidence/2026-09-15-managed-run-lifecycle/behavioral-validation.md]
decision: accepted
fingerprint: ead7ac18dcb22578d90a8eaeb69f8a218110db4e5de1e2e6e18be0c6cf4ae57b
reconsiders: "2026-09-07-atomic-publish-tree-reuse"
---

# Skill Proposal: Extend Atomic Publish Tree With Staging Markers and Detection

## Problem

`publish_tree` creates its backup sibling with `tempfile.mkdtemp(prefix=".kosmic-publish-backup-", dir=destination.parent)` and relies entirely on in-process `except`/`finally` for cleanup. Exception-path rollback is proven, but a crash inside the transaction window (SIGKILL between `os.replace` calls) bypasses both handlers and strands the sibling with no ownership metadata. Stories 056 and 051 therefore require versioned markers with bounded, attributable status for every destination-sibling stage and backup, report-only detection in the initial release, and destructive recovery only behind a later evidence gate.

Task P search-first resolution against the pinned inventory: `reuse` cannot satisfy the contract because the pinned routine has no marker emission and no detection surface at all; `create` is barred because an owning module exists and the lifecycle note reserves destination-sibling staging under the atomic-publication module ("same-filesystem replacement and recovery have different invariants"); `keep_as_prose` is barred because marker lifecycle and bounded-state classification are deterministic mechanics with a repeatable trigger, typed inputs/outputs, explicit invariants, expected failures, behavioral evidence, and owning domain `kosmic`. The procedure resolves to `extend`, reconsidering the accepted 2026-09-07 `reuse` decision on materially new crash evidence.

## Evidence

From the pinned 2026-09-15 behavioral validation (code state `git_head c52ab6a15b2dab0df9cbd450a76fcdc386612cdb`):

- **Rollback-success baseline**: Python-level failure injection (`KOSMIC_FAIL_STAGE=after-backup`) inside `publish_tree` propagates the exception, restores the prior canonical tree byte-identically, and the `finally` clause removes the backup sibling — the existing rollback contract holds and must be preserved unchanged.
- **SIGKILL stranded-sibling baseline**: a child process killed on the first `os.replace` after backup creation leaves the prior canonical tree intact but strands an empty, unattributable `.kosmic-publish-backup-<random>` sibling with no marker, phase, owner, or expiry metadata; nothing in the current system can detect, attribute, or bound it. This is the concrete gap; it is materially new relative to the 2026-09-07 reuse pack, which contained no crash-ownership scenario.
- Supporting context: the managed-run lifecycle (Stories 044–048, 052; full suite 394 tests OK) already established the staged-destructive-capability precedent (`scratch gc --apply` exits 2 `GC_APPLY_DISABLED`) and deliberately excludes destination-sibling staging from run cleanup authority.

## Applicability

The marker and detection contract applies to every `publish_tree` destination-sibling stage and backup — all four consuming callers (`generate`, `migrate_notes_bundle`, `update_mathdocs`, `generate_library`) and any future consumer of the routine. Detection is destination-scoped and report-only; interpretation of reported states, content approval, and the decision to act on a report remain outside the routine. Destructive recovery applies only after the separately gated Story 051 release.

## Behavioral Validation

Candidate paths: [pending_tests/kosmic/2026-09-15-atomic-publish-tree-recovery/candidate/kosmic_routines.py]

Baseline: KOSMIC_FAIL_STAGE=after-backup restores the prior canonical tree byte-identically and removes the backup in finally; SIGKILL after backup creation strands an unattributable sibling. Candidate: marker v1 precedes destructive publication steps, destination-scoped detection reports active, grace, expired, malformed, or ambiguous without mutation, and existing rollback and one-visible-tree behavior remain intact. Acceptance requires failing-first marker-schema, bounded-state, destination-scope, no-mutation, one-visible-tree, and crash-phase tests in the declared execution Evidence Pack.
## Proposed Change

Extend `kosmic/atomic-publish-tree` in `skills/scripts/kosmic_routines.py` (owning procedure `kosmic/development/atomic-skill-publication`) with three additions; the existing `publish_tree` signature and caller-visible rollback behavior are unchanged.

1. **Marker schema v1** — every destination-sibling stage and backup the transaction touches carries a marker file written before any destructive step, with fields: `schema: kosmic.publish-marker/v1`, `operation_id` (unique per publication attempt), `destination` (resolved destination identity), `source_git_sha256` (source Git hash recorded at begin), `phase` (advancing across the transaction checkpoints: backup-open, prior-tree-saved, staged-installed, committed), `created_at`, `grace_expires_at` (= `created_at` + 24 h, the abandoned-candidate grace), and `retire_by` (= `created_at` + 7 d, the maximum retention bound). Markers live inside the reserved sibling directories and are removed by normal `finally` cleanup, so the one-visible-tree publication invariant is preserved.
2. **Destination-scoped report-only detection** — a read-only query taking a caller-supplied destination, examining only exact reserved sibling names of that destination (never a glob over the parent), returning per-sibling typed records classified `active`, `grace`, `expired`, `malformed`, or `ambiguous`, with no mutation and no destination lock. The initial release explicitly rejects `restore`, `finish`, `retire`, and general-glob cleanup operations, failing closed in the `GC_APPLY_DISABLED` pattern.
3. **Separately gated recovery authority (Story 051, dormant here)** — destructive recovery is declared in this contract but activates only after a later evidence gate: caller-supplied destination plus exact reserved siblings only, destination lock acquired, Story 056 markers validated, restore/finish/retire proven against old/new canonical state with exactly one valid canonical tree visible at every observable point, and ambiguous, malformed, active, unrelated, wrong-owner, and unsupported candidates remaining report-only. Story 056's initial release ships markers and detection only.

## Routine Candidate

Repetition: Four known sibling-staging callers stage under the destination parent on every publication — python:kosmic_project_skills:generate, python:kosmic_project_skills:migrate_notes_bundle, python:kosmic_project_skills:update_mathdocs, and python:kosmic_shared_library:generate_library; each call is a repeatable crash-exposure trigger.

Contract: Typed inputs publish_tree(staged: Path, destination: Path, managed_paths: Sequence[str] | None = None) -> None (unchanged) plus a new detection query (destination: Path) -> tuple[SiblingState, ...] with typed per-sibling state records. Invariant: exactly one canonical tree is visible at every observable point (s² = s; mixed visibility 0; visible count 1), preserved under marker writes, normal finally cleanup, and — once gated in — every recovery branch.

Expected failures: Marker-less reserved sibling (crash before marker write) reports malformed or ambiguous and is never silently deleted; unreadable or wrong-schema marker reports malformed; reserved-name sibling whose destination identity does not match reports ambiguous (report-only); staged tree missing raises RoutineError (existing); wrong-owner or unrelated candidates stay report-only; any destructive operation requested in the initial release is rejected fail-closed.

Leverage: One extension at the single publication seam covers all four callers and every future publish_tree consumer; managed-run reporting can surface sibling states without owning them; Stories 056 and 051 share this one decision; the marker gives crash forensics (operation, owner, phase, age, bounds) that anonymous backup debris cannot.

## Baseline vs Candidate

| Dimension | Baseline (pinned coordinate `44e467e8…`) | Candidate |
| --- | --- | --- |
| Exception rollback | Byte-identical restore; backup removed by `finally` (proven) | Unchanged; regression-pinned by the three existing routine tests |
| Crash (SIGKILL) mid-transaction | Prior tree survives; stranded anonymous sibling — undetectable, unattributable, unbounded | Stranded sibling carries marker v1; detection reports bounded, attributable state with 24 h grace and 7 d retention |
| Detection | None | Destination-scoped, report-only, five-state classification, no mutation |
| Recovery | None | Declared but dormant; activated only after the Story 051 evidence gate |
| One-visible-tree | Holds on success and rollback; crash leaves prior tree plus debris | Holds in all cases; markers live inside reserved siblings |

## Risks

- **Marker-write window**: a crash between sibling creation and marker write leaves a marker-less reserved sibling; detection must classify it `malformed`/`ambiguous` rather than assume safety — mitigated by marker-before-any-destructive-step ordering and fail-closed classification.
- **Shared-seam regression**: the extension touches the transaction used by all four callers; mitigated by the existing rollback regressions plus new failing-first marker-schema, bounded-state, destination-scope, no-mutation, and one-visible-tree tests, with injected crashes at each publication phase.
- **Destructive authority**: recovery can delete trees; it remains dormant until the separate gate proves every-phase crash convergence, unrelated-sibling safety, and wrong-owner refusal.
- **Clock dependence**: grace and retention classification read marker `created_at`; classification is report-only in the initial release, so skew cannot cause mutation.
- **Inherited**: cross-filesystem rename behavior remains unexercised; callers must keep staging under the destination parent to preserve same-filesystem atomic replacement.
