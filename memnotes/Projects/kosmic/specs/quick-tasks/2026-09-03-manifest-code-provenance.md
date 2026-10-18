---
id: "qt-2026-09-03-manifest-code-provenance"
status: "done"
created: "2026-09-03"
updated: "2026-09-03 (done)"
consumer_interface_change: false
project_id: "kosmic"
subproject_id: null
record_kind: "quick-task"
local_id: "2026-09-03-manifest-code-provenance"
---

# Quick Task: Manifest code provenance

## Goal

Reproducible results: every evidence pack can record the exact code state it was
produced under — including dirty working trees (jj snapshot / git tree hash).

## Change

1. `validate_evidence_pack`: optional MANIFEST frontmatter keys `git_head`
   (commit hash) and `worktree_tree` (tree hash or `clean`). Present ⇒ both
   required and shape-checked (40/64 lowercase hex). Absent ⇒ no gate
   (existing packs are immutable).
2. New `provenance` command: prints paste-ready `git_head:` / `worktree_tree:`
   lines from the current repo via a temporary GIT_INDEX_FILE
   (`git add -A` + `git write-tree`, compared against `HEAD^{tree}`).
   No index or working-tree side effects.

## Acceptance

- New tests: valid provenance passes; bad hex fails; tree without head fails;
  `provenance` command output shape + cleanliness detection.
- Full suite green; `validate`/`review` exit 0 on the real vault.

## Evidence

- evidence/2026-09-03-manifest-code-provenance/
