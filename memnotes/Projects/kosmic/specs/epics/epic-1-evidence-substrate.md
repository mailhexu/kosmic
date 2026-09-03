---
status: approved
created: 2026-09-02
updated: 2026-09-02 (approved)
linked_prd: ../prd.md
linked_architecture: ../architecture.md
linked_stories:
  - ../stories/story-001-evidence-tolerance.md
  - ../stories/story-002-manifest-validation.md
  - ../stories/story-003-migrate-research-memos.md
---

# Epic 1: Evidence Substrate

## Description

Establish the Evidence Pack layer at `{VAULT}/Projects/{TARGET}/evidence/{YYYY-MM-DD}-{slug}/` as a sibling of `notes/` (AD-1): Project-root walks tolerate it, `validate` checks MANIFEST.md conformance, and the existing research memos migrate into packs. Exclusion from OKF validation and projection is structural (packs live outside `notes/`), so the only code changes are root-walk tolerance and manifest validation.

## Scope

### In Scope

- Root-walk tolerance for `evidence/` and `impact.md` in project discovery/migrate paths
- MANIFEST.md schema validation (kind, produced_by, date, summary; body file roles)
- Migration of the two `specs/research/` memos to `kind: research` packs

### Out of Scope

- Note `evidence:` frontmatter (Epic 2), ledger (Epic 3), gate (Epic 4), task docs (Epic 5)

## Stories

| Story | Title | Status |
|-------|-------|--------|
| [[../stories/story-001-evidence-tolerance\|story-001]] | Project-root walks tolerate evidence layer | draft |
| [[../stories/story-002-manifest-validation\|story-002]] | Validate MANIFEST.md schema | draft |
| [[../stories/story-003-migrate-research-memos\|story-003]] | Migrate research memos into evidence packs | draft |

## Success Criteria

- [ ] Vault with evidence packs passes `validate`; packs never appear in any projection
- [ ] Malformed MANIFEST fails `validate` with a named error
- [ ] Both memos live as `kind: research` packs; PRD and INDEX links resolve

## Progress

- Stories: 3/3 done
- Last updated: 2026-09-02
