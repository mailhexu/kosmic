# Implementation record — Experience Compilation, stories 1-9

Session: 2026-09-02. Work items: stories 001-009 (epics 1-5), kosmic vault.

## What was built

- Evidence layer (FR-001/002): packs at `{VAULT}/Projects/{TARGET}/evidence/{YYYY-MM-DD}-{slug}/`, `MANIFEST.md` with kind/produced_by/date/summary + body file-role list; exclusion is structural (siblings of `notes/`; `validate_notes_bundle` and `collect_projection_plan` walk only `notes/`).
- Note linkage (FR-004): optional `evidence:` frontmatter; stable notes must resolve (Project-root-relative); drafts may dangle. Hooked into the existing per-note loop.
- Impact ledger (FR-005/006): flat `impact.md`, six fixed fields, append-only; `generate` appends publication entries (old→new source hashes from prior pair manifests) only after atomic publish and only when publishing to the canonical root; `validate` enforces schema.
- Completion gate (FR-007): `evidence_packs: [slugs]` work-item frontmatter; `check-completion` fails naming any declared pack lacking a draft-or-stable linking note; runs before the `consumer_interface_change` early-return so it applies to non-interface work too; absent key = no gate.
- Task 9 Distill (FR-003/009): `skills/references/task_distill.md` — Appendix E.2 analysis rules wholesale minus JSON contract/index rewrite; attribution + pinned upstream revision 02fac2c804fe156e43b12c691e4ae527614d63a1.
- Docs (FR-008/012): SKILL.md + README matrix rows/sections; task_add_note / task_implement_story / task_quick_task / task_review / task_project_skills updates.
- Migration (FR-011): two research memos became `kind: research` packs; INDEX + PRD links updated; `specs/research/` removed.

## Test evidence

- Baseline before change: 24 tests, OK (unittest; no pytest on host).
- TDD: 18 new tests written first → red (11 failing) → implemented → 66/66 OK.
- `check-required-skills --adapter codex`: passes.
- Real vault: `validate_evidence_packs` + `validate_impact_ledger` pass on the migrated kosmic vault; full `validate` correctly blocked by the no-pair publication gate (no stable usage note yet — by design).

## Process observations (raw, for distillation)

- Line-anchored edits on a rapidly renumbering 1600-line file misfired three times (insert into wrong function, lost statements); recovery cost exceeded the original edit. Re-reading before every anchor would have prevented all three.
- `generate`'s early `return`-shaped control flow made post-publish hook placement subtle; the unscoped-warning swallow showed tests would NOT have caught a mis-nested warning (it only triggers with unscoped notes).
- The completion gate had to be inserted BEFORE the `if not affects_interface: return` — an easy-to-miss control-flow trap; the test for "declared but not interface-affecting" pins it.
