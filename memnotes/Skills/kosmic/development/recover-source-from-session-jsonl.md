---
type: Domain Topic
id: kosmic/development/recover-source-from-session-jsonl
domain: kosmic
audience: development
artifact_role: guideline
status: draft
summary: Recover a lost uncommitted source file by replaying edit diffs from the omp session transcript JSONL, then prove equivalence with pinned tests.
triggers: [recover lost file, session jsonl, replay edits, uncommitted recovery]
source_project: native
source_sha256: empty
aliases: [jsonl recovery]
---

# Recover Source from Session JSONL

When a file with uncommitted work is destroyed and no sibling tree or stash
holds it, the omp session transcripts contain every tool call and result
verbatim. A full recovery restored about 140 lines of a Fortran module
bit-equivalently on 2026-09-21, proven by pinned tests.

## Where the data lives

`~/.omp/agent/sessions/<project-dir>/<session>.jsonl` holds one file per
session lineage, including the current conversation with its compaction
entries. Tool calls sit in `custom` entries with `data.toolName` and
`data.args`. Tool results sit in `message` entries with
`message.toolCallId` and `message.details`. Edit results carry
`details.diff`, `details.newText`, `details.oldText`, `details.op`, and
`details.path`. Read results carry `details.displayContent`. Eval-kernel
edits carry payloads under `message.content[].arguments.input`. Harness
edit results hold complete bodies, and `message.timestamp` orders edits
across sessions.

## Procedure

1. Run `git status` first. Identify which files are vanilla and which are
   still modified. `git diff --stat` sizes the recovery.
2. Walk the JSONL with Python. Collect every entry that mentions the file.
   Extract edits with timestamps and reads into a work directory.
3. Classify edits by timestamp: feature-evolution edits versus
   reverted-experiment edits. Replay vanilla HEAD plus the chronological
   feature edits only.
4. Cross-check the reconstructed signatures against intact call sites in
   still-modified files; the compiler is the surviving ground truth.
5. Rebuild, then prove equivalence with the fastest pinned regression that
   exercises the lost code.
6. Back up the recovered file outside the repository immediately, and
   recommend the commit to the user.

## Traps

- `git diff` compares the worktree against the index. A destroyed file that
  never appears in `git status` was already vanilla. Do not recover the
  wrong file.
- Edit-tool response hashes are session-scoped. Never reuse a tag from a
  previous turn or session.
- Before any `git checkout -- <file>` in a tree with uncommitted features,
  run `git diff <file>` first. Prevention beats recovery.
