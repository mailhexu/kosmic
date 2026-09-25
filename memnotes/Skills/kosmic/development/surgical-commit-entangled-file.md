---
type: Domain Topic
id: kosmic/development/surgical-commit-entangled-file
domain: kosmic
audience: development
artifact_role: guideline
status: draft
summary: Commit only your own hunks from a file that also carries the user's uncommitted changes, leaving the working tree untouched.
triggers: [surgical commit, entangled file, partial staging, user dirty file]
source_project: native
source_sha256: empty
aliases: [surgical staging]
---

# Surgical Commit for Entangled Files

Use this procedure when committing your edits to a file that also carries
the user's uncommitted changes, for example a dirty `main.tex` in a paper
repository.

## Procedure

1. Map the entanglement with `git diff --stat` and the hunk headers of
   `git diff <file>`: which files are dirty against HEAD, and where.
2. Edit the working tree normally. The user's changes and yours coexist.
3. Stage clean-based files with plain `git add`.
4. For an entangled file, build the surgical blob: `git show HEAD:<file>`
   plus only your inserted hunks, which you know byte-exactly. Watch
   encoding and newline details; append a `\n` separator when the user's
   file lacks a trailing newline.

   ```bash
   git show HEAD:<file> > /tmp/base
   # splice your blocks into /tmp/base at the same anchors with python
   SHA=$(git hash-object -w /tmp/built)
   git update-index --cacheinfo 100644,$SHA,<file>
   ```

5. Commit with a note that staging was surgical and the user's
   working-tree changes remain untouched.
6. Verify both states. `git diff <file>` must now show only the user's
   changes, because your hunks sit in both HEAD and the working tree. Then
   check the committed state builds standalone: `git worktree add
   /tmp/verify <sha>`, run the build, and `git worktree remove --force
   /tmp/verify`.

## Caveats

- Your working-tree hunks must be byte-identical to the committed ones, or
  the post-commit diff shows spurious noise.
- Do not touch, reflow, or fix the user's uncommitted hunks.
- A failed `git worktree add` leaves the directory behind. Re-check before
  re-adding.
