# Managed Run Lifecycle — Behavioral Validation

Execution evidence for Stories 044–048 and 052 and the Task P proposals for Stories 053 and 056. All scenarios ran on 2026-09-15 at code state `git_head c52ab6a15b2dab0df9cbd450a76fcdc386612cdb`, `worktree_tree d492f9630d3f99afdf217dd62d0c07d8fb9d2762` (the tree includes the managed-run implementation itself).

## Suites

- Focused module suite: `python3 -m unittest tests.test_kosmic_runs` — 75 tests, OK. Coverage: strict porcelain-v2 parsing (all record kinds, NUL paths, unknown-record rejection), snapshot identity (branch/detached/unborn), manifest/handle schema validation, begin privacy/lease evidence, cross-process holder survival and terminal finalization, 72-hour exact expiry boundaries, seven-day extension cap and idempotence, receipt 30-day expiry, token/secret absence, holder-crash abandoned-candidate with grace, TTL expiry under lock, `LIVE_UNREACHABLE` no-mutation, interrupted-finalization recovery at every fault checkpoint, cleanup journal recovery at every boundary plus conflict/orphan quadrants, rotation bounds, promotion containment/no-clobber/overwrite-precondition/hash agreement, mixed-category reporting with byte accounting and partial state, and real cross-process CLI lifecycle runs.
- Full suite: `python3 -m unittest discover -s tests` — 394 tests, OK (baseline before this feature: 348).

## Live CLI evidence (independent processes)

1. `scratch begin --project W --purpose "cross call"` → JSON `code OK`, private `handle_file` under `W/.tmp/kosmic/handles/`, run tree `input/output/logs/scratch/git` at mode `0700`, `RUN.lock` at `0600`.
2. Independent probe process: fresh `flock(LOCK_EX|LOCK_NB)` on `RUN.lock` answers `EWOULDBLOCK` — the detached holder keeps the lease after the beginning process exited.
3. `scratch promote --source scratch/artifact.txt --destination from-cli.txt` from a second process → `code OK`, destination bytes/hash equal the source, operation record `recorded`, Git before/after hashes differ exactly by the introduced file.
4. `scratch status --project W --run ID` → `{"code":"OK","live":true,"state":"active"}`.
5. `scratch succeed` from a third process → run directory removed, `history.jsonl` holds one cleanup record with `git_before_sha256`/`git_after_sha256`, terminal receipt retained under `handles/`.
6. `scratch gc --apply` → exit 2, `GC_APPLY_DISABLED` (staged destructive capability, AD-MRW10).

## Automatic command integration (Story 048)

- `validate --project <git-vault>` after `generate`: succeeds, leaves zero run directories (disposable run finalized and cleaned), and records a history entry whose `run_summary.purpose` is `validate-projection`.
- `provenance --repo <clean-repo>`: reports `worktree_tree: clean`; `git status --porcelain` remains empty afterwards — the temporary index lived inside run scratch and the worktree is untouched.
- Non-Git vault: `validate` exits 2 with `NO_GIT_WORKTREE` (fail-closed).

## Publication staging crash baseline (Story 056/051 Task P input)

- Python-level failure injection (`KOSMIC_FAIL_STAGE=after-backup`) inside `publish_tree`: exception propagates, the prior canonical tree is restored byte-identically, and the `finally` clause removes the backup sibling — the existing routine's rollback contract holds.
- **SIGKILL inside the transaction window** (child process killed on the first `os.replace` after backup creation): the prior canonical tree survives, but a stranded, empty, unattributable sibling `.kosmic-publish-backup-<random>` directory remains with **no marker, phase, owner, or expiry metadata**, and nothing in the current system can detect, attribute, or bound it. This is the concrete baseline gap the Story 056 marker/detection contract and the Story 051 recovery contract address.

## Skill-workflow trigger evidence (Story 053 Task P input)

- The current `skills/SKILL.md` "File Hygiene Before Coding and Before Final Status" section and seven other inventoried policy consumers still prescribe ad hoc `.tmp/<task-slug>/` and `.scratch/{skill-name}` placement with prose-only cleanup duties; with the lifecycle now executable, the orchestrator has no mandatory managed-run step and agents have no checkable begin/finalize operation. The proposal input manifest pins the exact current policy text for the baseline-vs-candidate comparison.
