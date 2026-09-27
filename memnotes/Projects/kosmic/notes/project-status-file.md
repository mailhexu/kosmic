---
type: Project Knowledge
title: Project status file
status: stable
created: 2026-09-27
updated: 2026-09-27
audience: usage
artifact_role: knowledge
evidence: [evidence/2026-09-27-status-file-release/session-record.md]
---

# Project status file

`STATUS.md` at a bound working-directory root states the current spec
statuses. The Projection CLI derives it from vault spec frontmatter; the
vault stays the single authority. Never edit the file by hand.

## Commands

```bash
kosmic_project_skills.py init --project {DIR} --project-id {ID} [--status-root {DIR}]
kosmic_project_skills.py migrate --project {DIR} --project-id {ID} [--status-root {DIR}]
kosmic_project_skills.py generate-status --project {VAULT}/Projects/{TARGET}
```

## Contracts

- The binding is the optional `status_root:` field in `ProjectEntry.md`.
  It must be a directory inside a Git worktree. Two projects cannot bind
  the same directory (`STATUS_ROOT_COLLISION`).
- Content: one table per class (PRD, Architecture, Epics, Stories,
  Quick Tasks, Skill Proposals) plus an Open Work summary. The header
  records the vault HEAD; output is byte-stable for identical state.
- `validate` fails `STATUS_STALE` when the file is missing or drifts.
  The completion gate refuses `done` on a stale file. Fix: run
  `generate-status` again.

## Linked Concepts

- [Projection CLI experience commands](./cli-projection-commands.md): the
  command surface this command joins.
