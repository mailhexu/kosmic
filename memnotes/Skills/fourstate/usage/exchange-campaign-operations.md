---
type: Domain Topic
id: fourstate/usage/exchange-campaign-operations
domain: fourstate
audience: usage
artifact_role: guideline
status: draft
summary: Operate the fourstate ABINIT+QE exchange campaign on nic6 and locally; run layout, binary choice, parallelization, memory, units, FSM protocol, moment validation.
triggers: [fourstate campaign, run_supercell_nic6, exchange campaign nic6, OOM supercell]
aliases: [fourstate nic6 campaign ops]
outcome: 
requires_procedures: []
governed_by: []
uses_knowledge: []
supported_by: []
supersedes: []
evidence: []
source_project: fourstate
source_sha256: d96a0fc0792b450c76a8919485fe99e967c09c35ca84b3d159bc5ec72d02754d
---

# Exchange Campaign Operations

Operate the fourstate/ase_fourstate ABINIT+QE exchange campaign on nic6 and
locally: run layout, parallelization, memory, unit pitfalls, debug builds.
## Layout
- Production tree on nic6: `/scratch/hexu/fourstate/worktree`. Pseudos: `pseudos/` (LDA PW92 SR UPF), `pseudos_jth/` (JTH PAW XML), `pseudos_jth_pbe/`, `pseudos_nc_pbe_upf/` (SG15 PBE). No ABACUS psp8 — the ABINIT parser rejects them.
- Drivers: `nic6/run_supercell_nic6.py` (env `FS_MATERIAL=cri3|nii2|mncl2 FS_XC=lda|pbe FS_PSP=jth|dojo FS_U=<eV>`), `run_abinit_nic6.py`, `run_qe_nic6.py`. Jobs `job_supercell_campaign.sh`, `job_run_once.sh`, `job_abinit_{upf,jth}.sh`. Outputs `runs/<tag>_{ref,1flip,J*_2flip}/` + `exchange_summary.json`. Local runs write `/scratch/hexu/fourstate/local_runs` (never /home). Collector: `collect_results.py exchange <run_root> --S 1`.
- Recipe: 3x3x1 supercell, 4x4x1 Gamma k-grid supercells (12x12x1 primitive 2-Cr cell), Fermi-Dirac 1 meV (tsmear 0.001 eV / degauss 7.3498644e-5 Ry), LDA PW92 (ixc=7 / input_dft='PW'), 50 Ha (pawecutdg=50), S=1 normalized, iscf=17, +U = 3/6 eV Dudarev J=0.
## Binary and known defect
- `dev@d5380e0cb-gcc` segfaults (SIGSEGV in `m_gstate`, ~14 s) on any density-restart run (`getden_filepath`/`irdden` + `initspinden 1`). Use `~/sw/abinit/dev@initspinden-fix-gcc/bin/abinit` (env `FS_ABINIT`); fresh-start runs work with either.
- JTH PAW + initspinden=1 flip: density flip succeeds, then ABINIT segfaults (exit 139) in the flip-state SCF. NC UPF works.
- Debug builds: nic6 `~/sw/abinit/debug@c6f863f2-gcc` (configure via `~/bin/nic6-abinit-configure-debug.sh`; first pass fails on an m_cppopts_dumper race, rerun). Local `build_debug` needs `-DABINIT_FFT_FLAVOR=GOEDECKER`.
## Parallelization, memory, scheduling
- Cluster caps ~1900 MiB/core; use `--mem=0` or ntasks × 1900 MB. Nodes: 2×96c EPYC 9655, 374 GB. npband=96/npfft=1 OOMs the PAW fine grid. Proven layout: npband 16, npfft 6 (CrI3 JTH peaks 244-280 GB). On startup OOM, diff the deck's npband/npfft/npkpt against a known-good run.
- nband multiple of npband*bandpp; no `autonp` in ABINIT 10.9. Never co-schedule two 96-task jobs on one node (`--exclusive`); 192 ranks does not halve memory. `sbatch` snapshots job.sh; cancel and resubmit.
- NiI2/MnCl2 3x3 cells have 2 distinct magnetic shells (driver falls back from 3).
## Units and parsing
- ABINIT screen `ETOT` is Hartree; myabinit.read_results and collect_results.py convert by x27.211386245988; `exchange_summary.json` is eV. Driver J formula (negative = FM): `J*S² = (E_ref + E_2flip − 2*E_1flip)/4`; with E_2flip=E_1flip compute `J = (E_ref − E_1flip)/4`. Missing ETOT / nonzero exit / OOM is fatal; never zero-fill.
- Gaps: read `*_o_EIG.nc` `Eigenvalues` (nsppol × nk × nband, Hartree). QE: parse `bands (ev)` blocks (lsda: first nk up, next nk down). Occupied counts: (nelect ± mag)/2.
## Constrained-moment (FSM) protocol for NiI2
Unconstrained flips collapse (~1.5 µB). Use `spinmagntarget` on all states:
ref 50.0, 1-flip 46.0, 2-flip 42.0 µB (25 Ni × 2 µB). Flip decks keep
`initspinden 1`, absolute `getden_filepath` to the constrained parent DEN,
fixed binary. Release check: `v2r_*` dirs drop `spinmagntarget`, gate on
the parent moment, chained `afterok`.
## Validation before trusting J
- Total magnetization quantizes: CrI3 54/48/42 µB (18 Cr × 3); MnCl2 125/115/105 (50 × 5/2); NiI2 FSM 50/46/42.
- Per-atom PAW sphere moments print in each `.log` (grep `^ +[0-9]+ Cr `). Refs must be N-fold degenerate; exactly the targeted atoms flip. Sphere moment shrinking with U is an rc≈2.11 bohr integration artifact; the aug-region Rhoij trace is reliable.
- `usepawu 2` = AMF (wrong for d³); `usepawu 1` = FLL (standard). Driver env `FS_UTYPE`, tags `_ut<N>`.
## Environment
- nic6 QE: `module load QuantumESPRESSO/7.5-foss-2025b`. ABINIT dev binaries need 2025b toolchain modules, called directly. Python `Python-bundle-PyPI/2025.07-GCCcore-14.3.0` + `pip install --user ase netCDF4`. Local ABINIT: `/home/hexu/projects/abinit_git/abinit_memory_optimization/abinit_dev/build/src/98_main/abinit` (branch `initspinden`); `mpirun -np 8`, no oversubscribe.
- Pitfalls: `reuse=True` poisons reruns (set False); command needs `abinit < PREFIX.files > PREFIX.log`; ASE 3.29 Espresso needs `EspressoProfile(command, pseudo_dir=...)`; QE `label` is ignored.
- Validated primitive result (LDA PW92 UPF, S=1): ABINIT J1 = −17.9872 meV = QE J1 (exact). Gaps up 1.097 / down 1.759 eV in both codes.