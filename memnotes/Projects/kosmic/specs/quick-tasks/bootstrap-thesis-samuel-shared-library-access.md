---
project_id: "kosmic"
subproject_id: null
record_kind: "quick-task"
local_id: "bootstrap-thesis-samuel-shared-library-access"
status: "approved"
created: "2026-10-12"
updated: "2026-10-12"
related_notes: ["notes/shared-domain-skill-library.md", "notes/cli-projection-commands.md"]
related_specs: []
related_files: []
consumer_interface_change: false
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
review_base: ""
review_round: 0
acceptance_evidence: []
review_record: ""
---

# Bootstrap thesis-samuel Shared Library access

## Request

Regenerate and validate the default vault Shared Skill Library (`memnotes`) so the new `thesis-samuel` Project can resolve a Recipe Packet, then make that library reachable for `thesis-samuel` per the approved Shared Domain Skill Library design.

## Scope

- Run `generate-library` and `validate-library` for the default vault with the routine source declarations.
- Establish `thesis-samuel`'s access to the shared vault library (vault-level `Skills/` is authoritative; no per-project copying of generated projections).
- Register the thesis-samuel workspace as a clean Git worktree binding for its approved work record.
- No shared-routine creation, migration of any other Project, or adapter reinstall.

## Out of Scope

- Editing generated library catalogs by hand; any regeneration goes through `generate-library`.
- Installing adapters or modifying installed user-authored skills.
- Performing the thesis PDF conversion itself (governed separately by thesis-samuel's approved Quick Task).

## Acceptance Criteria

- [ ] `validate-library` passes for the default vault.
- [ ] `thesis-samuel` can run `resolve-library` successfully against the shared vault library.
- [ ] The thesis-samuel workspace is a registered clean Git worktree with its `.kosmic/workdir.json` binding.
- [ ] Log updated; specs index updated if navigation changes.

## Routine Decision

No reusable deterministic procedure mechanics are introduced or materially changed.

## Implementation Notes

Library regeneration previously passed via `--work-record kosmic/...` resolution; this task is the approved implementation carrier for that mutation. `thesis-samuel` is a Git worktree at `/home/hexu/projects/review_papers/thesis_samuel` with an approved OCR Quick Task awaiting a registered clean worktree.

## Verification

- Pending implementation.

## Review

- [ ] Diff reviewed against scope.
- [ ] Acceptance criteria satisfied.
- [ ] Status set to `done` only after verification passes.
