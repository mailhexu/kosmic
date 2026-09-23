---
type: Project Knowledge
title: Dream Reflection workflow
status: stable
created: 2026-09-23
updated: 2026-09-23
audience: usage
artifact_role: knowledge
evidence: [evidence/2026-09-23-dream-reflection-release/MANIFEST.md]
---

# Dream Reflection workflow

Task D reflects on the previous workday and publishes one vault-level record
under `memnotes/dreams/`. The workflow splits deterministic mechanics from
judgment: `dream-harvest` begins a managed run and materializes a complete,
hash-pinned reflection contract; the agent reads only that `read_set`, writes
one candidate record and one ideas input; `dream-publish` merges, redacts,
validates, and atomically promotes the whole dreams tree; `dream-abort`
cancels.

## Commands

```bash
kosmic_project_skills.py dream-harvest   --vault {VAULT} [--date] [--timezone] [--project]
kosmic_project_skills.py validate-dreams --vault {VAULT} [--root STAGED]
kosmic_project_skills.py dream-publish   --vault {VAULT} --handle HANDLE [--replace]
kosmic_project_skills.py dream-abort     --vault {VAULT} --handle HANDLE --reason TEXT
```

## Contracts

- One record per date at `memnotes/dreams/{YYYY-MM-DD}.md`; the index is
  rebuilt newest-first by the CLI and idea IDs `{date}-{slug}` dedupe exactly.
- Records carry `generated_content_sha256`; a manually edited record requires
  `--replace` to overwrite, and whole-tree drift always requires a new harvest.
- Dream never mutates anything outside `memnotes/dreams/`; skill candidates
  stay in-record and enter governance only via Task 9 -> Task P.

## Linked Concepts

- [Managed Run Workspace Lifecycle](./managed-run-workspace-lifecycle.md): the run machinery dream reuses.
- **Notation**: standard symbols.
