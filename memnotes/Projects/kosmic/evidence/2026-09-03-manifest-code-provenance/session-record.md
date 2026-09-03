# Session record: manifest code provenance

## Context

Reproducible results require recording the exact code state results were
produced under, including dirty working trees during ongoing development.
Jujutsu (jj) 0.45.0 was installed to `~/.local/bin/jj` and colocated with the
repo (`jj git init --colocate`): the working copy is always a commit, so any
moment has a recordable hash. Git-side clients unaffected.

## Changes

1. `PROVENANCE_HASH_RE` constant (40/64 lowercase hex).
2. `validate_evidence_pack`: optional `git_head` / `worktree_tree` MANIFEST
   frontmatter keys; present ⇒ both required and shape-checked;
   `worktree_tree` accepts `clean`. Absent ⇒ no gate (existing packs are
   append-only and stay valid).
3. `collect_provenance(repo)`: `git rev-parse HEAD` + temp-index
   (`GIT_INDEX_FILE`) `git add -A` + `git write-tree`, compared against
   `HEAD^{tree}`; no index or working-tree side effects.
4. `provenance` CLI command printing paste-ready `git_head:` / `worktree_tree:`
   lines.

## Verification

- Tests first (red → green): valid provenance (hash + `clean` variants),
  bad hash rejected, tree-without-head rejected, command emits clean-then-dirty
  with no index pollution. Suite 142/142 OK (`python3 -m unittest
  tests.test_project_skills_cli`).
- Live: `provenance --repo .` reports HEAD `e3daf526…`, dirty tree
  `482c5b3d…` (matches jj parent `e3daf526` = main).
- `validate` on the real vault exits 0 with this pack present.

## Notes

- jj change-id `tynzxpyq` snapshots the pre-quick-task dirty state;
  amending descriptions changes commit ids but not change ids — record both.
- jj identity configured (`hexu` / `hexu@localhost`; adjust before pushing).
