---
type: Domain Topic
id: workstation/usage/boss-yale-octave-runner
domain: workstation
audience: usage
artifact_role: guideline
status: draft
summary: Patch the Yale BOSS slave-boson code for Octave and run it on this workstation to validate TBUpy RISB.
triggers: [BOSS, slave-boson, Octave, RISB validation]
source_project: native
source_sha256: empty
aliases: [Yale BOSS runner]
---

# Run Yale BOSS (slave-boson) under Octave

Use this topic to run a BOSS subsidiary-boson calculation on this workstation, for example to validate TBUpy `RestrictedRisbSolver` against BOSS.

## Setup

1. Clone `https://bitbucket.org/yalebosscode/boss.git` (v1.4 or later). Patched runnable copies already exist at `/home/hexu/projects/BOSS_pilot` (p-d chain) and `/home/hexu/projects/BOSS_pilot_pured`.
2. Octave 9.4 is installed as `/bin/octave`. Apply three mechanical patches:
   - Rename the variable `do` to `doloop` in `inputhrbin.m`, `hsearch.m`, `gettsub.m`, `getdcount.m`, `buildHspinon.m`, `Csearch.m`. `do` is an Octave keyword.
   - Extract the script-local functions `packdcounttsub` and `unpackdcounttsub` from the bottom of `functions/SCFloop.m` into their own files. Octave does not register MATLAB script-local functions across script calls.
   - In `hsearch.m`, evaluate the `HamSub(...)` call once before the `while` loop, so `Eigvals` exists when the loop is skipped on entry (trivially converged cases).

## Run

```bash
cd <workdir>   # contains mainprogram.m, setup_system.m, functions/, <base>.bin
octave --no-gui -q --eval "addpath(pwd); convert_hrdat_to_bin('model_hr.dat','model.bin','1.2');"
octave --no-gui -q --eval "mainprogram;" > out.txt 2>&1
```

- Convert Wannier90 `_hr.dat` files with the BOSS converter; hand-written hr.dat works (see `example2_manual`).
- Copy `setup_system.m` from `example1_SVO` and patch the parameter block: `corbs`, `porbs`, `hrbinfileup/dn`, `spinoninfo.Ne`, `nk`, `kTspinon`, `subinfo.U/J`, `subinfo.nsubspersite`, `ncorbspersub`.
- Disable the `plot_*` flags for headless runs.
- Key output lines: `Etot = ... Eband = ... Eint = ...`, `Final dcount` (per-spin d occupancy), `Final Oavg`.

## Conventions (pinned by machine-precision comparison 2026-09-19)

- `Oavg = sqrt(Z)`; spinon hoppings scale as `sqrt(Z) * t`.
- The saddle lambda (d spinon level shift) can be 0. Beware spurious lambda branches when scanning; the filling equation is multi-branched.
- tbupy `RestrictedRisbSolver` kappa equals the per-spin bare kinetic energy at Z=1 (Gutzwiller BR Uc = -16*kappa).
- Reference pilot (p-d chain): d onsite 0, p onsite -3, t = ±1, Ne=3, U=4, kT=0.05, nk=1x1x16. Results: Etot=-5.98014424, Eband=-6.33312565, Eint=0.35298141, Oavg=0.59757, dcount=0.54497 per spin.

## Known limitation

Pure correlated models (no uncorrelated p orbitals) crash downstream with NaN in `diagH_kspinon`, even with the hsearch patch. BOSS tested paths assume uncorrelated orbitals are present.
