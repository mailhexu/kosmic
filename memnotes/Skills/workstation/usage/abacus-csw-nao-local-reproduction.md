---
type: Domain Topic
id: workstation/usage/abacus-csw-nao-local-reproduction
domain: workstation
audience: usage
artifact_role: guideline
status: draft
summary: Reproduce or extend vendored ABACUS-CSW-NAO (SIAB orbgen) runs locally: Python 3.10 pins, running_scf.log fixture repair, and reuse of shipped ABACUS outputs.
triggers: [ABACUS-CSW-NAO, SIAB, orbgen, spillage, running_scf.log]
source_project: native
source_sha256: empty
aliases: [SIAB orbgen reproduction]
---

# Reproduce vendored ABACUS-CSW-NAO (SIAB orbgen) runs locally

Repo: `Refs/ABACUS-CSW-NAO` (git `3bd481d`, read-only). Python package `SIAB`, entry point `orbgen`.

## Environment

- Requires Python < 3.11 (`scipy<1.10`). Build a py3.10 venv with `uv venv --python /usr/bin/python3.10`. If `/home` is full, put the venv and `UV_CACHE_DIR` on /tmp.
- Install `torch==2.5.1+cpu` from `https://download.pytorch.org/whl/cpu` BEFORE `torch_optimizer`; otherwise the resolver pulls torch 2.14 and overflows disk. Then install `numpy==1.25.2 scipy==1.9.3 matplotlib<3.9 setuptools wheel setuptools_scm torch_optimizer torch_complex addict`, then `pip install --no-build-isolation Refs/ABACUS-CSW-NAO`.
- Local ABACUS is v3.10.1, outside the supported `>=3.7.5, <3.9.0.6` range. Reuse shipped ABACUS outputs instead of rerunning DFT.

## Fixture repair (uploads omit OUT.ABACUS/running_scf.log)

`_jy_data_extract` parses `running_scf.log` for natom, nzeta, nspin, and weights; 9 of 13 vendored unit tests fail without it. Reconstruct the log per job folder from its own artifacts:

- natom: STRU line `N  //number of atoms` after ATOMIC_POSITIONS.
- nspin: INPUT `nspin`.
- weights: `OUT.ABACUS/kpoints` (token 3 = nk; weights at tokens 16, 21, ... when flattened).
- nzeta: pool of the fixture family (jy-7au testfiles = 21/20/20; integrated Si_7au_jy = 13/12/12).
- Log format for `read_running_scf_log`: `ntype = 1`, then `READING ATOM TYPE 1`, then `atom label = Si`, then `L=i, number of zeta = N` lines, then `number of atom for this type = N`; then `nspin = N`; then `nkstot now = N`, exactly 2 filler lines, then N lines with the weight as last token. Add a `Finish Time` line so `job_done` skips ABACUS.

Copy fixtures to `.tmp` before patching (`Refs/` is read-only). Copy `spillage.py` and `listmanip.py` beside the copy and run `python -m unittest spillage` from that directory (legacy `from listmanip import merge`).

## End-to-end run (integrated Si_7au_jy pattern)

1. Copy `tests/integrated/Si_7au_jy/` to a run dir; fabricate `running_scf.log` per folder (nzeta 13/12/12, `--finish` marker).
2. Patch `jy.json`: absolute PP path (`tests/pporb/Si_ONCV_PBE-1.0.upf`); hardcode `pertmags` to the shipped geometry list — `"auto"` resolves through the built-in bond-length DB and will not regenerate the shipped five dimers; set `mpi_command` empty.
3. Run `orbgen -i jy.json -o out -l orbgen.log`. Shipped jobs are skipped via `job_done`; `_build_case` rewrites INPUT/STRU with local paths first.
4. Primitive pools regenerate byte-identically (`_build_atomspecies`); compare SHA-256. The code reuses an existing pool file, so regenerate in a separate directory to test.
5. Objective is pure kinetic spillage (`wov=0, wop=1`). Si 7au/40Ry reference: 1s1p gives 1.51546247e-02; checkpoint 1s1p1d gives 4.01825232e-03.
6. Zeta labels: `.orb` is 0-based, `.ion.nc` is 1-based — match channels by per-l ordinal rank.

Report pattern: `papers/autoresearch/abacusv3-csw-repro-si.md`; evidence in `.tmp/autoresearch/abacusv3-csw-repro-si/` (recreate `fabricate_running_log.py` there if lost).
