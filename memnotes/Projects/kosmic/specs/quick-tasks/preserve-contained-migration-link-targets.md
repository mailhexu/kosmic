---
project_id: kosmic
subproject_id: null
record_kind: quick-task
local_id: preserve-contained-migration-link-targets
status: done
created: 2026-10-13
updated: 2026-10-13
approval_note: Owner requested next to repair the unsafe EMC migration planner; proceed after the approved library prerequisite, without applying EMC migration.
consumer_interface_change: true
related_notes: [notes/cli-projection-commands.md]
proposal_required: false
routine_edge_change: false
routine_decision_required: false
review_base: 75ac6513af98fa6f07e0cf94c779352432226aed
writer_root: /home/hexu/projects/myagentskills/kosmic/.tmp/kosmic/runs/20261012T160259Z-library-consistency-repa-858b8785823aa920eff9be7d05247e11/scratch/dev
acceptance_evidence: [evidence/2026-10-13-contained-migration-targets/acceptance.json]
review_record: evidence/2026-10-13-contained-migration-targets/review.json
---

# Preserve explicit contained Markdown targets during spec migration

## Problem

EMC's flat PRD and visualization Epic already link to an existing Project-root research document. That document is outside the planner's authoritative/protected inventory. Moving the citing specs leaves the old relative link pointing at a nonexistent destination.

## Scope

Separate explicit target validity from write/repair eligibility. Recognize existing regular Project-contained Markdown targets through no-follow path reads, preserve them as target-only inputs, pin their content hashes, and rebase links from moving documents without altering target bytes. Do not add research or arbitrary directories to authoritative write roots or filename/stem repair candidates. Missing/escaping references retain existing reporting; symlink sources/parents fail closed. Keep determinism, guarded metadata precedence and query/fragment/title handling.

Source scope: skills/scripts/kosmic_specs.py and existing migration plan/apply regression fixtures. Documentation: existing CLI knowledge note and session evidence/log. Use the already registered clean private writer. Integrate only owned deltas after source-drift checks; never reset/stash/bulk-commit the owner's primary checkout. Review both axes independently.

## Acceptance Criteria

- [x] Migrating documents keep explicit research targets reachable with query/fragment/title preserved, while research bytes are unchanged and never scheduled for write/delete.
- [x] Target-only inputs are hash-pinned; target changes alter the plan digest and prevent stale-plan application.
- [x] Missing targets do not become filename repair candidates, and symlink target/parent escapes fail with SCOPE_DENIED.
- [x] Existing migration regressions pass and the actual EMC CLI proposal preserves both reported research references without applying the plan.

## Non-goals

No EMC migration application, owner reassignment, Architecture creation, installed skill changes, or expanded authoritative write roots. EMC proposal application still requires exact digest approval.

## Verification

Integrated source suite: 673 tests passed. Regression scenarios observed
red before the fix and green after, including local linked-metadata
precedence and moving/staying WikiLinks. Independent Standards and Spec
re-review resolved all findings. Actual EMC proposal and copied-input
preview preserve both research destinations; live-link validation passes
and research write/delete count is zero. Whole preview catalog validation
separately exposed eight historical stories without linked_epic ancestry;
that legacy reconciliation is outside this source-fix scope. No migration
application or scientific calculation occurred.
