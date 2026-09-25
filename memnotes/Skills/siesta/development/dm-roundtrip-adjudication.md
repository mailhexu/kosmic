---
type: Domain Topic
id: siesta/development/dm-roundtrip-adjudication
domain: siesta
audience: development
artifact_role: guideline
status: draft
summary: Adjudicate suspected SIESTA DM-file round-trip or rotated-DM corruption for spinor runs before blaming the writer or reader.
triggers: [dm roundtrip, restart energy jump, rotated dm charge deficit, Tr D.S mismatch]
source_project: native
source_sha256: empty
aliases: [dm adjudication]
---

# DM Round-Trip Adjudication

Use when a SIESTA restart or rotated-DM seed shows a large energy change
and file corruption is suspected, especially in the perspin_DFTB fork
with `Spin = Spin-Orbit` (off-site), 8-column spinor DMs, +U/OP.
## Protocol (order matters)

1. Confirm the file was read. Grep the output for `Attempting to read DM
   from file... Succeeded` (m_new_dm.F90) or `Reading matrix from file`
   (m_iodm_old). No message means no read. Fdf flags the active path
   ignores (for example `DFTU.FirstIteration`) are not controls.
2. Diff the restart fdf against the writing run's fdf, all options. Prime
   suspect: a regenerated fdf whose `%block DM.InitSpin` is empty or
   changed. Exact control: copy the writer fdf verbatim; edit only
   `MaxSCFIterations` and the SCF converge/tolerance keys. A converged
   restart must give dDmax about 1e-6 and the writer's E_KS.
3. Check the writer converged: read the LAST `scf:` row, never
   `grep -m1 FreeEng` (iteration-1 energies masquerade as converged).
4. Cross-binary read: run a 1-shot with a different build on the same
   file. Equal moments mean consistent readers.
5. Parse the binary DM directly (Fortran unformatted sequential): record
   1 = 5 ints `no_u, nspin, nsc(3)`; record 2 = `numd(no_u)`; then `no_u`
   `listd` records; then `nspin x no_u` double records, spin-major. The
   spinor 8-column layout equals sisl M11r..M21i with col8 = -Im du.
6. Validation pitfalls: raw c1+c2 row sums are not Mulliken charges
   (S-weighting needed). A sisl read-write roundtrip is identity even
   under a wrong interpretation; only rotations expose convention
   mismatches. Fortran is case-insensitive.
7. SCF-vs-final energy discrepancies are a verified non-issue; earlier
   gaps were iteration-1 misreads or non-converged writers.
8. Rotated-DM seeding: check the printed `Qtot, Tr[D*S]`. A deficit means
   the rotation is not S-unitary; coefficient-orthogonal R x W loses
   percent-level charge on dense solids (about 1.9 keV on TmFeO3).
   Isolated-atom fixtures cannot detect this. Rotate in the S-orthonormal
   dual representation instead.
9. Ops traps: `SCF.H.Tolerance 5e-3` without a unit exits silently. No
   active convergence criterion means SIESTA exits after 1 iteration. On
   nic6, call the venv python by absolute path.
10. Tooling: local builds `siesta_DFTB/_build/build_dbg` (-O0 -fcheck)
    and `build_o3g` (-O3 -g); valgrind on small serial fixtures; verify
    source lineage of heap-corruption claims (stale CMakeCache).
