---
type: Domain Topic
id: fourstate/usage/exchange-preflight
domain: fourstate
audience: usage
artifact_role: guideline
status: draft
summary: Run the matched ABINIT/QE four-state J1 preflight for primitive CrI3 (LDA PW92, 50 Ha) and the mandatory final-moment audit.
triggers: [fourstate preflight, CrI3 exchange, matched ABINIT QE, initspinden flip]
aliases: []
outcome: 
requires_procedures: []
governed_by: []
uses_knowledge: []
supported_by: []
supersedes: []
evidence: []
source_project: fourstate
source_sha256: c8881fb67801887add10c409f4c8ba274e5471a1275b1fea6924a9eead6324e4
---

# Exchange Preflight (CrI3 primitive, ABINIT vs QE)

Run or debug the cross-code four-state exchange comparison in
`/home/hexu/projects/fourstate/fourstate`, per `exchange_fourstate.docx`.

## Protocol (phase 1: primitive cell)

- Cell: primitive Cr2I6 monolayer (`data/structures/cri3_primitive.cif`, a=b=6.867 A, gamma=120, c=20 A vacuum). Phase 2 (only after the codes agree): 3x3x1 supercell.
- Shared settings: LDA PW92 — ABINIT `ixc=7`, QE `input_dft='PW'` (never PZ); 4x4x1 Gamma k-grid; Fermi-Dirac 1 meV (QE `degauss=7.3498644e-5 Ry`); cutoff 50 Ha = 1360.5693123 eV = 100 Ry (QE `ecutrho=800`).
- Identical pseudopotentials (required for any comparison): LDA PW92 SR UPFs at `/home/hexu/projects/siesta_dev/basis_matrix/abacus_v2_pseudodojo/lda_pw92_sr/upf/{Cr,I}.upf`. ABINIT `pps='UPF'`; QE `pseudopotentials={'Cr':'Cr.upf','I':'I.upf'}`. The JTH PAW variant (ABINIT only, `pps='jth'`, add `pawecutdg`) is a robustness check, never a matched comparison.
- States: FM ref, 1flip (one Cr spinat negative), 2flip. ABINIT flips: `compute_multi_neighbor_exchange(..., initspinden=True)` — ref first, then each flip deck gets `getden_filepath "<abs path to ref DEN>"` (quoted) + `initspinden 1`; no `constraint_kind` anywhere. QE: `run_qe_exchange` (native spin init, requires JOB DONE).
- Convention: S=1 normalized; report J*S^2. Primitive relation E_2flip = E_1flip, so `J1 = (E_ref − E_1flip)/4` in meV. Expected 3x3 magnitude PBE J1 ≈ −6 meV (code consensus); the primitive value is an effective estimator only.

## Final-state moment audit (mandatory before trusting any J)

For each state, in an isolated dir, build a deck from that state's own
converged run: copy its `.in`, drop `nstep`/`getden_filepath`/`initspinden`,
append `nstep 0` + `getden_filepath "<that state's *o_DEN>"` +
`initspinden 1`; run via the files contract. The table's
`Diff(up-dn)_before` gives final SCF sphere moments. Require ref (+,+),
1flip (−,+), 2flip (−,−); magnitude ~2.7-2.8 µB for Cr. Rerun a collapsed
state; never patch with `constraint_kind`.

## Execution environment

- `source /home/hexu/projects/myenvs/mydev/bin/activate` (ASE 3.29 + python-docx).
- Local ABINIT: `/home/hexu/projects/abinit_git/abinit_memory_optimization/abinit_dev/build/src/98_main/abinit` (10.9.0.3, has initspinden); `mpirun -np 8 <binary> < PREFIX.files > PREFIX.log`, `np_spkpt=8, paral_kgb=0`. Local QE: `~/.local/qe74_release/bin/pw.x` (ASE needs `EspressoProfile(command, pseudo_dir=...)`).
- nic6: QE via `QuantumESPRESSO/7.5-foss-2025b`; ABINIT `~/sw/abinit/dev@d5380e0cb-gcc/bin/abinit` + 2025b toolchain modules (OpenMPI/5.0.8, FlexiBLAS/3.4.5, libxc/7.0.0, netCDF-Fortran/4.6.2, FFTW.MPI/3.3.10). Staged at `/scratch/hexu/fourstate/{worktree,pseudos}`.
- Disk: /home is full; runs write under `/scratch/hexu/fourstate` (local `runs -> /scratch/hexu/fourstate/runs`). 50 Ha needs 0.6-1.1 GB/state. Disk-full kills ABINIT in `m_nctk write_eig` (MPI_ABORT). Free space by deleting WFK/EIG/GSR/`pwscf.save` only; keep .in/.log/.txt/DEN/JSON.

## Known package contracts (clean tree)

- Energies: read the final screen-log `ETOT` line in eV directly. The old `* Hartree` label on eV values was a bug (J 4.36x too large). Any failure (nonzero exit, missing ETOT, unconverged residual, missing ref DEN) aborts, never zeroes.
- `collect_results.py exchange <run_root> --S 3` expects grouped `ref/ 1flip/ J*_2flip/` subdirs (package writes sibling `<workdir>_<suffix>/`; regroup before collecting).
- The comparison is meaningful only when XC, pseudopotential files, cutoff, structure, k-grid, and smearing width/type all match. Otherwise label and discard.
