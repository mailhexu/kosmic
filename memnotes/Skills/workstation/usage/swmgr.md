---
type: Domain Topic
id: workstation/usage/swmgr
domain: workstation
audience: usage
artifact_role: guideline
status: draft
summary: Swmgr records and manages group scientific-software installs; delegate builds to Spack or conda and follow the record gates.
triggers: [swmgr, software install, spack, conda, module load]
source_project: native
source_sha256: empty
aliases: [software installation manager]
---

# Swmgr Software Installation Manager

Swmgr manages scientific software across group machines. It answers three questions: what is installed where, how to use it, and how to install it.

## Design

- Swmgr wraps Spack for the Fortran and DFT stack and conda for standalone Python tools. Swmgr never reimplements a package manager.
- The agent suggests, and the manager approves each environment in chat. On failure the agent finishes independent targets and reports failures as a batch.
- Three toolchains exist: GCC plus OpenMPI plus OpenBLAS, Intel oneAPI plus Intel MPI plus MKL, and NVIDIA CUDA.
- Two install tracks exist. `release` is an immutable upstream version with no local changes. `development` is any group branch, commit, or patch set. Records, lockfiles, and published pages live under matching track directories.

## Vault layout

The vault is one shared git repo. Key directories:

- `machines/` — one note per computer.
- `software/` — shared catalog and install procedure per product.
- `installs/<track>/` — one record per software, version, toolchain, and machine.
- `locks/<track>/` — committed lockfiles. Lockfiles are never deleted.
- `playbook/` — one note per failure signature and the fix that worked.
- `published/` — generated Hugo usage pages for the group.

Relations use wikilinks: an install record links `[[<software>]]` and `[[<machine>]]`.

## Tasks

- `install <software> on <machine> [--toolchain T]` — read the procedure, enforce the supported toolchain matrix, plan on the control machine, run Spack or conda over SSH, get in-chat approval, build, verify with reference tests, then record.
- `record <details>` — three enforced gates: classify the track, commit the lockfile, and log source provenance (source path, git remote, branch, commit, submodule commits, or tarball URL plus checksum). No provenance means no record.
- `usage <software> on <machine>` — print the track, `module load` lines, and a filled job script.
- `reconcile <machine>` — run on demand. Compare modules, prefix trees, `spack find`, and conda envs against declared installs. Flag hand-builds as `unmanaged` and stale records as `drifted`.

## Statuses

- Install record: `converged`, `in-progress`, `drifted`, `unmanaged`.
- A non-`converged` install gets a module suffix `.partial` and a loud warning on load.
- `converged` means the reference tests pass, not only that the build finished.

## Conventions

- One fact, one place: the procedure lives in `software/`, machine facts in `machines/`, the instance in `installs/`. Link, never duplicate.
- Module names are flat: `<sw>/<ver>-<toolchain>`; development builds carry the commit: `<sw>/dev@<shortsha>-<toolchain>`.
- Run `reconcile` routinely. The scanner is the only way to see drift and unmanaged builds.
