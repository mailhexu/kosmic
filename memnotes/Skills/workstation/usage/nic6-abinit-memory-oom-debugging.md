---
type: Domain Topic
id: workstation/usage/nic6-abinit-memory-oom-debugging
domain: workstation
audience: usage
artifact_role: guideline
status: draft
summary: Diagnose ABINIT OOM failures on nic6: per-core cgroup caps, layout-versus-functional rule, the replicated fatsph allocation bug class, and custom-branch builds.
triggers: [nic6, ABINIT OOM, OUT_OF_MEMORY, initspinden, fatsph, slurm memory]
source_project: native
source_sha256: empty
aliases: [ABINIT OOM debugging]
---

# ABINIT OOM debugging on nic6

## Cluster memory model

- nic6 nodes: 373,850 MB RAM, 192 cores. Slurm applies a per-core cgroup cap of about 1900 MiB. A 96-task job is capped near 178 GiB and a 192-task job near 356 GiB, regardless of `--mem=0`.
- A job that legitimately needs more than 178 GiB at 96 ranks must run 192 ranks; wavefunction memory halves with rank count. Example: `spinmagntarget` runs whose occupation solver reaches about 187 GiB RSS.
- Never co-schedule multiple large jobs on the same nodes: they kill each other with SIGSEGV and OOM. Use `--exclusive` for jobs of 96 tasks or more, and check `squeue %R` node assignment after submit.
- OOM evidence chain: `sacct` State `OUT_OF_MEMORY`, plus `oom_kill events in StepId` in the slurm `.out`, plus the ABINIT log's LAST line, which names the fatal phase (death right after `read_rhor` = import machinery; death in `gstate` = startup or layout).

## Diagnostic rule: layout versus functional

If two maximally different MPI layouts (for example np_spkpt2/npband32/npfft3 versus npband96/npfft1) die at the same log line, the failure is in code or the memory path, not the layout. No deck tuning fixes it. Layout regressions show as deck diffs in `npband`, `npfft`, `np_spkpt` against a known-good run; always diff the generated decks' parallel lines when jobs OOM at startup. With `npfft=1`, every rank holds the full fine-grid FFT and density arrays (about 1.5 GB per rank at 250x250x243), which fills the node.

## Known replicated-allocation bug class (initspinden)

The NC (`usepaw=0`) initspinden path in `src/95_drive/m_gstate.F90` (about lines 1190-1234) allocates `fatsph(nfftf, dtset%natom)` replicated per rank. For NiI2 (ngfft 240x240x192 = 11.06M points, 75 atoms) that is 6.63 GB per rank times 192 ranks = 1.27 TB: guaranteed OOM at any rank count, right after `read_rhor`. Fix: use a per-atom `(nfftf)` buffer reused across the flip and zero loops (numerically identical). The PAW fix near line 1237 covers `usepaw==1` only.

## DEN-restart and initspinden gotchas

- The `dev@d5380e0cb-gcc` binary segfaults in `m_gstate` after about 14 s on any density restart (`getden_filepath` or `irdden` plus `initspinden 1`). Use the patched `dev@initspinden-fix-gcc` binary.
- Deck-rewriting drivers can silently drop `getden_filepath`. Check the log for both `mkfilename: getden from:` and `read_rhor`; otherwise initspinden 1 is ignored.
- `spinmagntarget` plus DEN restart can be SCF-unstable (ETOT bounces about 20 Ha for 200 iterations). Fix: `diemix 0.3` plus `diemixmag -4`, each exactly once — duplicate keywords abort chkinp.
- WFK is usually not saved for converged states; only DEN is available for restarts.

## Building a custom branch on nic6

- Recipe (skill `abinit-git-cmake-build` applies): modules GCC/14.3.0, OpenMPI/5.0.8-GCC-14.3.0, FlexiBLAS/3.4.5-GCC-14.3.0, libxc/7.0.0, netCDF-Fortran/4.6.2, FFTW.MPI/3.3.10; CMake with FlexiBLAS for BLAS/LAPACK; compile inside sbatch with `-c 64`; install under `~/sw/abinit/<tag>-gcc`.
- Branch merge_cdft_damping (721ca38742) needs three fixes (applied remote-only on nic6): `include(CheckIncludeFile)` above levmar in CMakeLists; `fftw3_fftpad_spc` missing the `plan_cache` dummy arg in `m_fftw3.F90`; and the removed gpu_option guard in `m_hamiltonian.F90` causing a null `nfft_blocks` abort for any WFK-writing run — fix with `if (present(nfft_blocks) .and. nfft_blocks>0)`.
- Installed optimized prefix: `~/sw/abinit/spinopt@721ca387-gcc`; source at `/scratch/hexu/build/src_abinit_spinopt`; build script `build_spinopt.sh`.
- MPI-layout validity: `nproc <= np_spkpt x npband x npfft x npspinor` when set manually; ABINIT aborts otherwise. `nband` must divide by `npband`.
