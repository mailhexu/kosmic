---
status: "done"
created: "2026-09-14"
updated: "2026-09-15"
result: "update"
scope: "global-procedure"
target: "kosmic"
target_ref: "skill://kosmic"
target_sha256: "95a81cd212d1a27bfea5f094b184446b0757db7c7019902c3188bc562d1cf0b8"
proposer_mode: "subagent"
proposer_ref: "agent://ImplementManagedRunSuite.SkillCutoverProposer"
proposer_reason: "Fresh-context Task P assessment restricted to the hash-pinned curated manifest"
input_manifest: ["specs/skill-proposals/inputs/managed-run-workflow.md"]
related_notes: ["notes/managed-run-workspace-lifecycle.md", "notes/cli-projection-commands.md"]
evidence_packs: ["2026-09-15-managed-run-lifecycle"]
behavioral_evidence: ["evidence/2026-09-15-managed-run-lifecycle/behavioral-validation.md"]
decision: "accepted"
fingerprint: "7a7311f73bf174de9099103666560a44a507377ba365a2ba9e1f9425bdedd7ef"
reconsiders: ""
project_id: "kosmic"
subproject_id: null
record_kind: "proposal"
local_id: "2026-09-14-managed-run-workflow"
---

# Skill Proposal: Managed Run Orchestrator Step and Lifecycle Reference Cutover

## Problem

The Kosmic skill teaches scratch hygiene as prose only. `skills/SKILL.md` carries a "File Hygiene Before Coding and Before Final Status" section, echoed by seven other inventoried policy consumers, prescribing ad hoc `.tmp/<task-slug>/` placement, manual classification, and prose-only cleanup duties. Stories 044–048 and 052 delivered an executable managed-run lifecycle (lease-backed begin/finalize/status, deterministic retention, mandatory Git-state records, journaled owner cleanup), yet the orchestrator skill contains no step that uses it. Two policies now compete, and agents still have no checkable begin/finalize operation. Story 053 declares `proposal_required: true` for exactly this cutover.

## Evidence

From `evidence/2026-09-15-managed-run-lifecycle/behavioral-validation.md` (code state `c52ab6a1`):

- Suites: focused lifecycle suite `tests.test_kosmic_runs` 74 tests OK; full suite 394 tests OK (baseline 348).
- Live CLI across independent processes: `scratch begin` → JSON `code OK`, private `handle_file`, run tree mode `0700`; the detached lease survives the beginning process (independent probe `flock(LOCK_EX|LOCK_NB)` → `EWOULDBLOCK`); `scratch status` → `{"code":"OK","live":true,"state":"active"}`; `scratch succeed` from a third process removes the run and records cleanup with `git_before_sha256`/`git_after_sha256`; `scratch gc --apply` correctly refused (`GC_APPLY_DISABLED`).
- Promotion: `scratch promote` from a second process verifies bytes/hash and records the before/after Git delta.
- Automatic command integration: `validate` leaves zero run directories (disposable run finalized and cleaned); `provenance` leaves the worktree untouched; non-Git creation fails closed with `NO_GIT_WORKTREE`.
- Trigger evidence: the current SKILL.md hygiene section plus seven other policy consumers still prescribe ad hoc `.tmp/<task-slug>/` and `.scratch/{skill-name}` placement with prose-only cleanup; the orchestrator has no mandatory managed-run step.

Notes: `notes/managed-run-workspace-lifecycle.md` (draft; governing concept "managed run"; eight scratch-policy consumers inventoried with a source-policy audit) and `notes/cli-projection-commands.md` (stable; documents the `scratch begin|succeed|fail|extend|promote|status|gc` adapter and automatic command integration). Proposal history: `impact.md` records no rejected fingerprint for this target; the accepted 2026-09-07 atomic-publish-tree proposal is a shared-routine reuse with no overlap. Mechanics classification: the deterministic lifecycle already exists in `skills/scripts/kosmic_runs.py` and the `scratch` CLI — reuse, no new routine; remaining skill content (when to begin/finalize, durable-rule boundaries) is judgment prose. Story 053 declares `routine_edge_change: false`; no routine action is required.

## Proposed Change

One atomic `update` to `skill://kosmic` (sketch; final prose authored in Story 053 implementation):

1. **SKILL.md — replace "File Hygiene Before Coding and Before Final Status" with one mandatory step** using the leading concept `managed run`:

   > **Managed Run Before Scratch (MANDATORY).** Before creating any scratch, runtime, or generated output, begin a managed run:
   > `python3 {KOSMIC_SKILL_DIR}/scripts/kosmic_project_skills.py scratch begin --project {VAULT}/Projects/{TARGET} --purpose {task-slug}`
   > **Done when**: the JSON reply has `code: OK` and a run path under `.tmp/kosmic/runs/`; write all scratch inside that run. `NO_GIT_WORKTREE` → stop: the vault must sit in a Git worktree whose root ignores `.tmp/`.
   > **Before final status**: finalize with `scratch succeed` (or `scratch fail`). **Done when**: JSON `code: OK`; a successful diagnostic/disposable run leaves no run directory and history carries its start/final Git snapshots.
   > Durable files never live in run scratch: source/docs in the project tree; `pending_tests/<project>/<YYYY-MM-DD>-<slug>/original-paths/<original-path>` with `MANIFEST.md`, committed before finishing; Evidence Packs under `evidence/`; specs and project logs under their own governance.

2. **Add one lifecycle reference** `references/managed_run_lifecycle.md` owning path layout, retention classes and extension, promotion, recovery, cleanup, and the destination-sibling atomic-publication exception. SKILL.md names it once; agents load it only when lifecycle detail is needed (progressive disclosure, NFR-MRW08).

3. **Remove the duplicated scratch mechanics from the other seven inventoried policy consumers in the same cutover**: `skills/README.md` "File Hygiene" (collapse to the pointer), `references/task_implement_story.md` Step 3.1 (drop its four hygiene bullets; point at the mandatory step), `references/task_quick_task.md` Step 5 (same), and the remaining ADR/spec and inventory consumers (FR-MRW22). Each consumer keeps only audience-specific durable rules (pending tests, Evidence Packs, specs, logs). The duplicate-policy source check stays red until no competing scratch policy remains.

## Applicability

The step is procedural and reusable: every Kosmic task that creates Kosmic-owned scratch — story implementation, quick tasks, generated outputs, diagnostics — repeats the same begin/write-inside/finalize mechanics with checkable outcomes. It applies only to Kosmic-created scratch below the active Git worktree's `.tmp/kosmic/`; it does not govern durable files (source, `pending_tests/`, Evidence Packs, specs, project logs), user-created files, or destination-sibling atomic-publication staging. Branch-specific lifecycle detail is progressively disclosed via `references/managed_run_lifecycle.md`. Overlap analysis: no competing skill exists — this update removes the eight duplicated policy occurrences instead of adding a ninth.

## Behavioral Validation

Candidate paths: [pending_tests/kosmic/2026-09-15-managed-run-workflow/candidate/SKILL.md]

Invariant scenario: a fresh-context agent performing work that creates scratch begins a managed run, writes scratch only below its returned .tmp/kosmic/runs path, and terminally succeeds or fails it. Observable criterion: both commands return code OK and history contains the start and final Git snapshots. Baseline is prose-only ad hoc scratch; candidate is the executable lifecycle plus one leading workflow instruction and progressive reference.
## Baseline vs Candidate

| Behavior | Baseline (current hygiene prose) | Candidate (one step + one reference) |
|---|---|---|
| Scratch placement | Ad hoc `.tmp/<task-slug>/`, `.scratch/{skill-name}`, repo roots | One resolved run under `.tmp/kosmic/runs/` from `scratch begin` |
| Begin | None; classify-by-prose before creating files | Checkable: JSON `code: OK` + run path |
| Lease/ownership | None | OS lease spans tool calls (probe `flock` → `EWOULDBLOCK`) |
| Finalization | "Delete before review" prose duty | Checkable: `succeed`/`fail` → `code: OK`, run removed, history record |
| Git-state record | Manual `git status --short` classification only | Mandatory start/final porcelain-v2 snapshots plus cleanup before/after hashes |
| Failure retention | Undefined | Deterministic: diagnostic 72 h, disposable, extension ≤ 7 days |
| Detail location | Duplicated across eight consumers | One SKILL.md step + `references/managed_run_lifecycle.md` |
| Durable rules | Mixed into hygiene prose | Preserved as explicit distinct rules (pending_tests, Evidence Packs, specs, logs) |

## Risks

- **Cutover completeness**: eight consumers must change atomically; a partial cutover leaves competing policies. Mitigation: keep the Story 043 source-policy audit red until zero unexplained entries (FR-MRW20/22) and migrate every consumer in one reviewed change.
- **Reference breakage**: removing the hygiene section breaks consumers citing it by title (`task_implement_story.md` 3.1, `task_quick_task.md` 5); the same change rewrites those references and bumps the skill version (consumer interface change).
- **Over-reach**: the run lifecycle must not absorb durable governance; `pending_tests/`, Evidence Packs, specs, and logs keep their own rules (FR-MRW18), explicitly preserved above.
- **Agent bypass**: a fresh-context agent may skip the step; the checkable JSON criterion and finalization history record make omission detectable at review.
- **Scope creep**: the initial release refuses destructive `gc --apply` (`GC_APPLY_DISABLED`); the step text must not promise it. Non-Git vaults fail closed (`NO_GIT_WORKTREE`) — the README must state that prerequisite.
- **Skill surface**: one added mandatory step; net length decreases because the larger hygiene section and its echoes consolidate into one reference.
