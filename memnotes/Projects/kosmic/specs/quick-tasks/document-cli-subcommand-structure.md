---
project_id: "kosmic"
subproject_id: null
status: "approved"
record_kind: "quick-task"
local_id: "document-cli-subcommand-structure"
created: 2026-10-13
updated: 2026-10-13
approval_note: Owner selected README + SKILL.md scope on 2026-10-13 after hitting a missing-command failure caused by undocumented subcommand structure.
consumer_interface_change: true
related_notes: []
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
review_round: 0
acceptance_evidence: [evidence/2026-10-13-cli-docs/acceptance.json]
review_record: evidence/2026-10-13-cli-docs/review.json
---

# Document the Projection CLI subcommand structure

## Scope

- Add a `## Projection CLI` section to `README.md` stating that all
  functionality is subcommands of one script
  (`skills/scripts/kosmic_project_skills.py`), listing the subcommand
  groups, and including `generate-status`.
- Add one clarifying sentence to the installed skill `SKILL.md` (source
  `skills/kosmic/SKILL.md`) noting the single-CLI subcommand invocation.
- No behavior, code, or generated artifact changes; no installed-skill
  edits (skill regeneration follows the existing pipeline).

## Acceptance Criteria

- [x] README documents the single-CLI subcommand invocation and lists `generate-status`.
- [x] SKILL.md source states the single-CLI invocation model.
- [x] No code or generated artifacts changed.
