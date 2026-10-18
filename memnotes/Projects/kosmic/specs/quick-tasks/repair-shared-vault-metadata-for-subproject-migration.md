---
project_id: "kosmic"
subproject_id: null
status: done
record_kind: "quick-task"
local_id: "repair-shared-vault-metadata-for-subproject-migration"
approval_note: User directed Next on the migration assessment; repairs are the stated prerequisite phase.
consumer_interface_change: false
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
review_base: "24ebc6d6b84f058c34c8bee1991b77220624e873"
review_round: 0
acceptance_evidence: [evidence/2026-10-13-vault-metadata-repair/acceptance.json]
review_record: evidence/2026-10-13-vault-metadata-repair/review.json
---

# Repair shared vault metadata for subproject migration

## Scope

In a private writer snapshot of `/home/hexu/projects/memnotes/memnotes`, repair only the metadata defects that block `migrate-subprojects-plan` in the 28 failed Projects: add missing ProjectEntry frontmatter with the Project's established identifier, fix malformed/duplicate spec frontmatter, repair one unterminated note frontmatter, and restore one missing SubprojectEntry.md from its own specs content. Plan-only verification afterwards; never apply a migration plan, touch unrelated in-flight work, or edit live vault bytes. Integrate only owned, baseline-checked deltas after independent review.

## Acceptance Criteria

- [ ] Every previously failing Project plans successfully or its residual blocker is a documented ownership/link decision requiring user assignment, not malformed metadata.
- [ ] Each repaired file retains its original body bytes; only frontmatter/identity lines changed, with before/after hashes recorded.
- [ ] Re-planning runs read-only against the writer copy; the live vault is byte-unchanged outside owned deltas after reviewed integration.