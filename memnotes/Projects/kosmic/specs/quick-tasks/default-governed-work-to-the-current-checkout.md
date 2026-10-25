---
project_id: "kosmic"
subproject_id: null
status: "approved"
approved_by: user
approved_on: 2026-10-25
approval_provenance: "User explicitly selected 'Approve and run the episode'."
record_kind: "quick-task"
local_id: "default-governed-work-to-the-current-checkout"
registration_root: "/home/hexu/projects/myagentskills/kosmic"
registration_outputs: [".kosmic/working-directories.json", "worktree:.kosmic/workdir.json"]
consumer_interface_change: true
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
created: "2026-10-25"
updated: "2026-10-25"
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

- [ ] Projected usage and development guidance states the current checkout as the default for record-governed work, with a new worktree only on explicit user request, and keeps the dirty-worktree refusal and the unrelated-work rule.
- [ ] `record_first_contract` carries the same default and every generated adapter projection embeds it.
- [ ] No guidance site still instructs creating a dedicated or isolated worktree for record-governed work without the ask-first default.
- [ ] The source diff is limited to guidance text; the affected suites and the full suite pass unchanged in enforcement behavior.
- [ ] The regenerated pair validates and the installed OMP adapters match the episode's outputs, with the previous installation preserved outside skill discovery.

## Routine Decision

No new deterministic procedure mechanics: registration, work start/finish, generation, installation, and validation commands are reused unchanged.
