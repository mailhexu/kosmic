---
type: Project Knowledge
title: ABINIT v10 Test Workflow
description: Lifecycle guideline for claiming numbers, authoring, running, pinning, regenerating, and bisecting ABINIT v10 tests across parallel trees.
confidence: 0.85
created: '2026-09-25'
updated: '2026-09-25'
validation_procedure: "Re-run the pinned family v10[220:233] on a current build before trusting this note for a new campaign."
project: abinit
status: draft
audience: development
artifact_role: guideline
usage_stale: false
tags: [abinit, v10-tests, runtests, references, bisect, parallel-trees]
evidence: []
---

# ABINIT v10 Test Workflow

## Scope

This note gives the lifecycle of ABINIT v10 tests on the NC DFT+U port worktrees of 2026-09.
A deck is a `tests/v10/Input/t<NNN>.abi` file; a reference is a `tests/v10/Refs/t<NNN>.abo` file.

## Claim a test number

1. The `t<NNN>` namespace is shared across all trees and active sessions.
2. List `tests/v10/Input/` and the `tests/v10/__init__.py` history in every tree; take the next number free in all trees.
3. On a collision, `git mv` the deck and the reference to the next free number.
4. Update the TEST_INFO `files_to_test`, the `__init__.py` entry, all story references, and record the renumber in the commit and story.
5. Never renumber a buildbot-pinned number unilaterally; flag it for arbitration.
6. Keep the commit surface minimal: one deck, one reference, one `__init__.py` line.

## Author the deck and fixtures

1. Put the fldiff contract (`files_to_test`, `tolnlines`, `tolabs`, `tolrel`, `fld_options`) in TEST_INFO and register the deck in the `inp_files` list of `tests/v10/__init__.py`.
2. Declare a negative guard with `expected_failure` in TEST_INFO; it reports `passed` when it aborts with the pinned message.
3. Register a standalone checker in the `checkers` dict of `src/<dir>/abinit.src` plus an `abinit.amf` LDADD closure copied from `src/66_nc_dftu/abinit.amf`.
4. Run `./config/scripts/makemake` from the source root only; build the owning library before the checker target.
5. In a Fortran fixture, initialize every flag and write conjugate-transpose channels in a second pass.
6. Before a finite-difference (FD) campaign, run a self-consistent field (SCF) floor probe; a limit-cycle fixture cannot certify anything.
7. Break inversion symmetry in a displaced base so U-delta force channels stay non-vacuous.
8. Positive `getwfk`, `getden`, and `getddk` values are absolute dataset numbers; keep a U=0 control bitwise.

## Run the test

1. Run `runtests.py` from inside the build tree with `-b <build-dir>`; from a source `tests/` directory it fails with "Cannot find the ABINIT build tree".
2. Suite arguments are Python slices only, space-separated (`v10[220:233]`); comma lists fail.
3. Add `-n <ranks> --force-mpirun` for Message Passing Interface (MPI) legs; a `min_nprocs` skip counts as green.
4. A deck passed by absolute path drops the `.abo` next to the input file; locate all artifacts before cleanup.
5. Verify the `.abo` before copying; on an abort, read the `--- !BUG/ERROR` block at the tail of the `.log`.
6. Before blaming a commit, run `git status --short src/`; sibling work-in-progress in the binary changes physics.

## Pin and regenerate references

1. Trial-run the deck with `ABI_PSPDIR=<tree>/tests/Pspdir`, verify the physics, then copy the `.abo` to `tests/v10/Refs/` and rerun through `runtests.py`.
2. A reference is toolchain-pinned; state the reference toolchain in the commit message.
3. Treat a post-commit fldiff failure as a stale reference when the diffs touch SCF-trajectory columns or force tables, the converged etotal values match, and the commit chain contains certified numerics changes.
4. Before overwriting a reference, cross-verify the fresh output bitwise against a sibling certified test on the same fixture.
5. Never compare outputs from different decks; a k-mesh or nband change produces meaningless deltas.
6. Record the staleness reason and the cross-check in the commit message.

## Bisect a regression

1. Commit all work first; a bisect EXIT trap wipes uncommitted worktree edits.
2. Check reference provenance; if the predicate fails at the ref-import commit with identical input and pseudopotentials, classify upstream drift and stop.
3. Grep the reference for "not enough SCF" first; a branch-regenerated reference may already contain the stall.
4. Pin the deck and its pseudopotentials under `.tmp/<tNN>_bisect_input/`, never under `/tmp`.
5. In the predicate script, set `set -u`, capture `rc=$?` before other commands, run `python3 config/scripts/makemake` from the source root, and wipe `.mod` and `.o` files before the rebuild.
6. Signal with a grep count on the log (`grep -a`); exit 0 for good, 1 for bad, 125 for skip.
7. Verify the predicate at the good anchor before `git bisect start`.
8. After `git bisect reset`, rebuild HEAD fully and read the pinned diff before writing the fix.

## Cross-tree rules

1. Treat the develop integration tree as a foreign lane; check `hub list` for active peers before touching either tree.
2. The `abinit_pao_proj` tree commits references first; develop re-lands them on its own toolchain.
3. Reconcile every numbering and reference claim against both trees.
4. Read a numeric envelope in a commit message as bounding one specific comparison; toolchains differ by an ~0.85 mHa etotal floor.
