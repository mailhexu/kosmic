---
status: "done"
created: "2026-09-02"
updated: "2026-09-02 (done)"
consumer_interface_change: true
related_notes: ["cli-projection-commands.md"]
review_base: "uncommitted-working-tree"
review_round: 0
project_id: "kosmic"
subproject_id: null
record_kind: "quick-task"
local_id: "2026-09-02-projected-link-rewriting"
---

# Quick Task: Package-consistent link rewriting in projection

## Scope

- `projected_reference` in `skills/scripts/kosmic_project_skills.py`: body links whose target is not projected into the same Skill Pair package are demoted to bold plain text; same-package links kept verbatim; rewriting skips code fences, external schemes, fragments, non-Markdown targets.
- `generate` prints a stderr warning listing demoted links.
- Tests in `tests/test_project_skills_cli.py` (new class).
- Doc line in `references/task_project_skills.md` + one Principles bullet in the stable usage note (triggers ledger publication entry on regenerate).

## Out of scope

- Cross-package linking (companion-skill naming already covers it); validation failures; draft projection.

## Acceptance criteria

- [ ] Same-package link between two stable usage notes survives verbatim in both references.
- [ ] Stable note linking a draft note (or a stable note in the other package) → link demoted to `**Text**` in the projected reference.
- [ ] `generate` warns on stderr naming demoted targets; no warning when nothing demoted.
- [ ] Ledger gains a publication entry for the changed usage note after regenerate; `validate` exit 0.

## Rationale

WikiSkill principle (arXiv 2608.27454): a delivered knowledge package is internally consistent by construction — its navigation derives from shipped content, not the vault superset. Kosmic's router already does this; reference bodies violated it (three dangling links in the first published pair).

## Verification

- `python3 -m unittest tests.test_project_skills_cli` — all green.
- Regenerate + `validate` on the kosmic vault; confirm dangling links gone in `skills/kosmic-usage/references/cli-projection-commands.md`.

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-09-02 | Created | Approved by user at creation |
