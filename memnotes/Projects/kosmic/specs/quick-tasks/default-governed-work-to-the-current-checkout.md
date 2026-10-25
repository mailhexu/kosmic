---
project_id: "kosmic"
subproject_id: null
status: done
approved_by: user
approved_on: 2026-10-25
approval_provenance: "User explicitly selected 'Approve and run the episode'."
record_kind: "quick-task"
local_id: "default-governed-work-to-the-current-checkout"
registration_root: "/home/hexu/projects/myagentskills/kosmic"
registration_outputs: [".kosmic/working-directories.json", "worktree:.kosmic/workdir.json"]
consumer_interface_change: true
related_notes: ["notes/cli-projection-commands.md"]
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
created: "2026-10-25"
updated: "2026-10-25"
review_base: ea44bf59f0c26aa6f8747135513681930d8e30a0
review_round: 2
completion_observations:
  - criterion: "Projected usage and development guidance states the current checkout as the default for record-governed work, with a new worktree only on explicit user request, and keeps the dirty-worktree refusal and the unrelated-work rule."
    observation: "The regenerated pair embeds the new writable-work default in kosmic-usage/SKILL.md and kosmic-development/SKILL.md, and skills/SKILL.md keeps the dirty-worktree refusal while now requiring unrelated in-progress work to be left untouched and the user asked how to clear it before starting."
    source: "Native generate output; grep counts of the new contract sentence (one per generated SKILL.md); check-installation reported installed Skill Pair bytes and identity verified."
  - criterion: "`record_first_contract` carries the same default and every generated adapter projection embeds it."
    observation: "The contract's writable-work line now states the current-checkout default with dedicated worktrees created only on user request, and both generated projections carry that sentence; the only Python change in the episode diff is this string constant, so no enforcement path changed."
    source: "git diff skills/scripts/kosmic_project_skills.py (single hunk); grep over the regenerated pair."
  - criterion: "No guidance site still instructs creating a dedicated or isolated worktree for record-governed work without the ask-first default."
    observation: "grep over skills/ finds no remaining isolated-writer, clean-dedicated-worktree, one-worktree-one-writer, or separate-clean-worktree mandate in Markdown or Python source; separate-worktree integration language survives only in the asked-for case."
    source: "grep outputs from this episode; diff -r -x __pycache__ between skills/ and the installed package returned no differences."
  - criterion: "The source diff is limited to guidance text; the affected suites and the full suite pass unchanged in enforcement behavior."
    observation: "The full suite ran 823 tests OK on this tree; no test pins the replaced wording, and the production diff is five guidance text sites plus one string constant."
    source: "python -m unittest discover -s tests (823 tests, OK); grep over tests/ for the replaced phrases returned nothing."
  - criterion: "The regenerated pair validates and the installed OMP adapters match the episode's outputs, with the previous installation preserved outside skill discovery."
    observation: "install --adapter omp published the regenerated pair and check-installation verified bytes and identity; the release skills/ package was refreshed after backing up the previous installation, and the installed copy equals the working tree excluding __pycache__."
    source: "CLI install and check-installation outputs; backup /home/hexu/.omp/agent/skill-backups/kosmic-before-1a16622-20261025T075252Z; diff -r result."
completion_review:
  reviewer: main-assistant-coordinator
  axes:
    standards:
      decision: approved
      reviewer: CheckoutDefaultStandards
    spec:
      decision: approved
      reviewer: CheckoutDefaultSpec
  decision: approved
  review_base: ea44bf59f0c26aa6f8747135513681930d8e30a0
  reviewed_revision: 39f3db084cf897cb18c5cf72c27d52b37a17002784b02de1bd85f4cb66ea44c9
  scope:
    - worktree:skills/SKILL.md
    - worktree:skills/references/task_implement_story.md
    - worktree:skills/references/task_review.md
    - worktree:skills/references/work_completion.md
    - worktree:skills/scripts/kosmic_project_skills.py
    - project:skills/.kosmic-pair.json
    - project:skills/kosmic-development/SKILL.md
    - project:skills/kosmic-usage/SKILL.md
    - project:specs/quick-tasks/default-governed-work-to-the-current-checkout.md
    - project:log/kosmic-2026-10-25.md
  findings:
    - id: GUID-R1-01
      disposition: Blocking
      status: resolved
      resolution: fixed
      detail: "The rewritten guidance told agents to commit or stash unrelated in-progress work, weakening the untouched-unrelated-work rule."
      worker_response:
        kind: fixed
        detail: "Both guidance sites now require leaving unrelated work untouched and asking the user how to clear it before starting; the current-checkout default and the ask-only worktree rule are unchanged."
        evidence: "Focused Standards/Spec re-review of the corrected skills/SKILL.md diff and the final /home/hexu/AGENTS.md section returned approved with no findings on both axes."
---

# Default governed work to the current checkout

## Request

The user asked that agents stop creating a new worktree for kosmic memnotes work unless asked to, and apply the same default for other repositories.

## Scope

- Change only guidance text: the projected work-record authority contract (`record_first_contract` in `skills/scripts/kosmic_project_skills.py`), `skills/SKILL.md`, and the `task_implement_story`, `work_completion`, and `task_review` references. Enforcement code paths are not changed.
- The new default: record-governed work runs in the current checkout; a new worktree is created only when the user asks. The dirty-worktree refusal at start, the unrelated-work rule, one record-governed session per checkout at a time, live authority re-resolution, scope checks, review gates, and receipt publication are all kept unchanged. Separate-worktree integration language survives only for the asked-for case.
- Register this repository root as the episode writer and remove that registration during owned-run cleanup, so the published registry stays empty.
- Regenerate the Project-owned Skill Pair with the native generator; refresh the installed OMP adapters (the generated pair through the documented install command, the release `skills/` package through the established backup-then-copy installer) and verify with `check-installation`.
- Mirror the cross-repository default in the user-level `/home/hexu/AGENTS.md` (outside this repository; not a committed output).

## Out of Scope

- No change to `work start`/`work finish` enforcement, scope checks, proof, receipt, identity, approval, or review gates; the dirty-worktree refusal stays.
- No new commands, flags, or session bookkeeping; no adapter mechanism changes beyond the regenerated pair and the documented install invocations.
- No historical record, receipt, or log rewrite.

## Acceptance Criteria

- [x] Projected usage and development guidance states the current checkout as the default for record-governed work, with a new worktree only on explicit user request, and keeps the dirty-worktree refusal and the unrelated-work rule.
- [x] `record_first_contract` carries the same default and every generated adapter projection embeds it.
- [x] No guidance site still instructs creating a dedicated or isolated worktree for record-governed work without the ask-first default.
- [x] The source diff is limited to guidance text; the affected suites and the full suite pass unchanged in enforcement behavior.
- [x] The regenerated pair validates and the installed OMP adapters match the episode's outputs, with the previous installation preserved outside skill discovery.

## Routine Decision

No new deterministic procedure mechanics: registration, work start/finish, generation, installation, and validation commands are reused unchanged.

## Verification

- The full suite ran 823 tests OK on this tree; the only production change is guidance text, and no test pins the replaced wording.
- The installed OMP adapters were refreshed (generated pair through `install --adapter omp`, release package through backup-then-copy) and `check-installation` verified bytes and identity.

## Links

- Related notes: none; this Quick Task is the governing record.
- Related specs: none.
- Related files: `skills/SKILL.md`, `skills/references/task_implement_story.md`,
  `skills/references/task_review.md`, `skills/references/work_completion.md`,
  `skills/scripts/kosmic_project_skills.py`, the regenerated Project pair, and
  the user-level `/home/hexu/AGENTS.md`.

## Review

Round 1 reviewed the episode packet against base `ea44bf5`: the Spec axis
approved and the Standards axis returned one Blocking finding (GUID-R1-01).
Round 2 re-reviewed the correction on both axes and approved with no findings.
`review_round` is 2 and `completion_review` records the actual approvals.

## Code Review

**Review Base**: `ea44bf59f0c26aa6f8747135513681930d8e30a0`  
**Current Round**: 2  
**Reviewed Revision**: `39f3db084cf897cb18c5cf72c27d52b37a17002784b02de1bd85f4cb66ea44c9`  
**Decision**: approved  
**Standards Reviewer**: `CheckoutDefaultStandards` — approved (Round 2)  
**Spec Reviewer**: `CheckoutDefaultSpec` — approved (Rounds 1 and 2)

### Standards

| ID | Disposition | Evidence | Required Resolution | Introduced | Status | Resolution | Worker Response |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GUID-R1-01 | Blocking (confidence 0.9) | `skills/SKILL.md:95` replaced "use a separate clean worktree … leave unrelated work untouched" with "commit or stash unrelated work first", and the new `/home/hexu/AGENTS.md` Git Worktrees section repeated that imperative. | Preserve the unrelated-work safety rule: leave unrelated work untouched and ask the user how to clear it; never direct agents to commit or stash work they do not own. | Round 1 | resolved | fixed | kind=fixed; detail=Both sites now leave unrelated work untouched and ask the user how to proceed; the current-checkout default and ask-only worktree rule are unchanged. Evidence=Focused both-axis re-review of the corrected diff approved with no findings. |

### Spec

| ID | Disposition | Evidence | Required Resolution | Introduced | Status | Resolution | Worker Response |
| --- | --- | --- | --- | --- | --- | --- | --- |
| (none) | — | Round 1 found no Spec finding; the change stays inside the declared scope and keeps every refusal and gate. | — | — | — | — | — |

### Re-review History

| Round | Reviewed Revision | Findings Checked | New REG/LATE Evidence | Decision |
| --- | --- | --- | --- | --- |
| 1 | `39f3db084cf897cb18c5cf72c27d52b37a17002784b02de1bd85f4cb66ea44c9` | Complete first-pass inventory | n/a | Changes requested (Standards) |
| 2 | `39f3db084cf897cb18c5cf72c27d52b37a17002784b02de1bd85f4cb66ea44c9` | GUID-R1-01 resolved | none | Approved |
