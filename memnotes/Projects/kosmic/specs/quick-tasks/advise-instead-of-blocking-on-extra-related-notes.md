---
project_id: "kosmic"
subproject_id: null
status: "approved"
approved_by: user
approved_on: 2026-10-25
approval_provenance: "User explicitly selected 'Approve and run'."
record_kind: "quick-task"
local_id: "advise-instead-of-blocking-on-extra-related-notes"
registration_root: "/home/hexu/projects/myagentskills/kosmic"
registration_outputs: [".kosmic/working-directories.json", "worktree:.kosmic/workdir.json"]
consumer_interface_change: false
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
created: "2026-10-25"
updated: "2026-10-25"
---

# Advise instead of blocking on extra related notes

## Request

The user hit `COMPLETION_PRECHECK_FAILED: related Consumer knowledge is not stable` for a related note and asked that the consumer-interface completion gate not be this strict: extra related notes that are not stable Consumer knowledge should not block completion.

## Scope

- Change only the `consumer_interface_change: true` branch of `_check_existing_completion` in `skills/scripts/kosmic_project_skills.py`: a missing related note still refuses, and the change still requires at least one stable, fresh, usage/both related note as the Consumer anchor; every additional related note that fails stability, freshness, or audience becomes a stderr warning naming the note and reason, and projection validation runs on the anchors only.
- With no stable anchor at all, the gate still refuses, with the aggregated reasons in the diagnostic.
- Add behavioral regressions in `tests/test_record_scoped_completion.py` for both the advisory path and the retained no-anchor refusal.
- Reinstall the release `skills/` package to the OMP adapter after the commit (backup-then-copy) and verify with `check-installation`; the Project pair is unchanged.
- Register this repository root as the episode writer and remove the registration during owned-run cleanup so the published registry stays empty.

## Out of Scope

- No change to the math/proposal/routine related-note gates, the non-interface path, proof, scope, review, or receipt mechanics; no canonical note or pair regeneration (no projected guidance text changes).

## Acceptance Criteria

- [ ] A consumer-interface record whose related notes include one stable fresh usage/both note plus additional non-stable or non-Consumer notes completes successfully, with a stderr warning naming each non-anchor note and reason.
- [ ] A consumer-interface record with no stable fresh usage/both related note still refuses, and the diagnostic names the offending notes and reasons.
- [ ] A missing related-note path still refuses unchanged.
- [ ] The existing stable/fresh/projection consumer regressions keep passing, the new regressions cover the advisory and no-anchor behaviors, and the full suite passes.

## Routine Decision

No new deterministic procedure mechanics: the gate keeps its ordered precheck position and helper structure; only the failure classification of extra related notes changes.
