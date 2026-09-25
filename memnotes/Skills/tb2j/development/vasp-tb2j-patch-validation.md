---
type: Domain Topic
id: tb2j/development/vasp-tb2j-patch-validation
domain: tb2j
audience: development
artifact_role: guideline
status: draft
summary: Validate the VASP_TB2J_patch native exporter end-to-end against pristine VASP 6.4.1 and consume the result with vasp_native2J.
triggers: [VASP TB2J patch validation, apply_patch.sh, vasp 6.4.1 serial build, FeO native export fixture]
aliases: [VASP native patch test]
outcome: 
requires_procedures: []
governed_by: []
uses_knowledge: []
supported_by: []
supersedes: []
evidence: []
source_project: tb2j
source_sha256: 6ba259a04fafe941ee6a05dd39bb6c609fa0e75e4ad8b140a2516773ce89f3d4
---

# VASP TB2J Patch Validation

Validate the `VASP_TB2J_patch` native exporter end-to-end against pristine VASP 6.4.1 and consume the result. Facts verified 2026-09-22.

## Locations

- Patch: `/home/hexu/projects/VASP_TB2J_patch` (symlinked into `TB2J_dev/`). It ships `tb2j_export.F`, `tb2j_main_block.inc` (a 38-line main.F hook extracted from the worked tree), and `apply_patch.sh` (idempotent over three states: pristine, v5-hooked, already-v6).
- Worked reference tree (not a git repo): `/home/hexu/.local/src/vasp.6.4.1_cpu`; its `src/main.F` lines 4791-4828 are the authoritative exporter hook.
- Pristine VASP git: `TB2J_dev/vasp.6.4.1_cpu` (`master` = `04cab27` pristine; `07a693f` = XML hooks plus the `src/lib/timing_.c`/`dclock_.c` prototype fix).
- projector (POTCAR) library: `/STORAGE2/Xibu4T/document/bak_hexu/.local/pp/vasp/vasp54/potpaw/<EL>/POTCAR` (5.4 PBE PAW, per element; concatenate in POSCAR species order).
- Consumer: `vasp_native2J.py` in the mydev environment.

## Apply and verify (static, before any build)

1. Create an isolated tree: `git -C TB2J_dev/vasp.6.4.1_cpu worktree add <tmp>/vasp.6.4.1_cpu 04cab27`.
2. Reapply the lib fix for modern gcc: `git show 07a693f:src/lib/timing_.c > WT/src/lib/timing_.c`, and the same for `dclock_.c`. Without it the build fails on obsolete `getrusage`/`gettimeofday` prototypes.
3. Apply the patch with `bash .../apply_patch.sh`; it must report the USE line, the export block, and the `.objects` insertion after `mkpoints_full.o`. Then prove equivalence instead of trusting "no errors": `git apply --check --verbose x.patch`, apply, then `cmp` each touched file against the worked tree.
4. The object list is `src/.objects`, not `src/makefile`, and it is dependency-order sensitive: a new module must come after every module it USEs (`tb2j_export.o` after `mkpoints_full.o`).

## Build (serial only)

Run `mkdir -p bin` first (untracked, so worktrees lack it and the final `cp` fails), then `make std -j1`. Never build with `-jN`: the VASP 6.4.1 makefiles track no module dependencies, and parallel builds die on missing `.mod` files (`gg_base.mod`, `elphon_util.mod`, ...). Harness shells can report `nproc` = 1; pass an explicit count only on a -j-safe path.

## Run and consume (FeO reference fixture)

1. Inputs: `~/projects/mypapers/TB2J_projector/data/projector_examples/runs/cross_code/FeO/vasp_pbe/U5_sym/` (INCAR ISPIN=2 ISYM=1 NBANDS=32 U=5 eV; POSCAR 2-atom rocksalt; KPOINTS 7x7x7 Gamma). The archived `POTCAR.sha256` (`dc7e41...`) is not reproducible from local variants; use plain Fe+O and expect exchange shifts of about 0.4%.
2. Run `OMP_NUM_THREADS=1 mpirun -np 8 WT/bin/vasp_std` (mpirun is OpenMPI at `/usr/bin/mpirun`); the run takes seconds. Success banner: `TB2J: native PAW v6 IBZ export written to tb2j_native.bin (IBZ=20, BZ=343)`; SCF magnetic moment about 4.0.
3. Consume: `source ~/projects/myenvs/mydev/bin/activate && vasp_native2J.py --input tb2j_native.bin --elements Fe --Rcut 6.0 --nz 20`; this writes `TB2J_results_vasp/exchange.out`.
4. Reference result: 12 first-shell Fe-Fe entries at 3.063 Å, FM J1 = +7.71 meV with spread <= 0.005 meV (archive worked-tree value 7.685 meV). Onsites are absent by design (post 2026-08-26 Rpts cutover).

## Traps

- `LFULL_KPOINTS`/`KPOINTS_FULL` already resolve in pristine main.F through `USE full_kpoints`; do not add a second USE.
- The worked tree also carries a non-TB2J local edit (`CALL UPDATE_CMBJ` after POTLOK); do not mistake it for part of the hook.
- Set `OMP_NUM_THREADS=1` to avoid oversubscription.

## Hygiene

Run from `~/projects/TB2J_dev/.tmp/<slug>/`. After validation, delete `build/`, `WAVECAR`, and `CHGCAR` (disk pressure: /home about 100% full), and `git worktree remove` verification worktrees. Keep `bin/vasp_std`, `tb2j_native.bin`, and `exchange.out` as evidence.
