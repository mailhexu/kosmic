---
type: Domain Topic
id: abinit/development/phonopy-frozen-phonon-campaign
domain: abinit
audience: development
artifact_role: guideline
status: draft
summary: Run phonopy-driven frozen-phonon force-constant campaigns against ABINIT with SUPERCELL0 seeding, a restart idiom, and fixture-validity audits.
triggers: [frozen phonon campaign, phonopy ABINIT force constants, supercell0 seeding, phonon leg audit]
aliases: [frozen-phonon campaign recipe]
outcome: 
requires_procedures: []
governed_by: []
uses_knowledge: []
supported_by: []
supersedes: []
evidence: []
source_project: abinit
source_sha256: 5d3f78d87832262cf53cb37a3075ea8c137816616759e1359d19926ace8ab80e
---

# Phonopy Frozen-Phonon Campaign

Validated on the NC DFT+U port with a NiO 2x2x2 supercell in 2026-09.

## Orchestration

1. Copy `~/projects/pyDFTutils/pyDFTutils/ase_utils/frozenphonon.py` into the campaign directory; never edit pyDFTutils.
2. Take `calculate_phonon()` as the skeleton: symmetry-reduced displacement dataset, SUPERCELL0 reference, per-leg runs, restart pickle, `produce_force_constants`.
3. Write inputs as a raw template with `xred` and `kpt` overrides; do not use the pyDFTutils keyword mapping.
4. Seed restarts with `getwfk_filepath` and `getden_filepath` pointing at the SUPERCELL0 WFK and DEN.
5. Run the undisplaced supercell first; seed every displaced leg from its WFK and DEN.
6. Run one Message Passing Interface (MPI) leg at a time with `mpirun -np 8` and `OMP_NUM_THREADS=1`; skip completed legs on restart.
7. Parse the final "cartesian forces (hartree/bohr)" block from each `.abo`.
8. Audit the DFT+U basin: every leg must show an identical `dftu_nc_interaction` eigenvalue spectrum.

## Fixture validity audit

Run this audit before launching legs.

1. Compare every leg's scaled positions in the ABINIT cell against the certified equilibrium structure.
2. Difference each leg `xred` against the undisplaced reference to verify the displacement magnitude.
3. Check net forces at equilibrium; a nonzero value near 1e-3 signals a wrong structure, not an SCF problem.

A coordinate-convention slip or an Angstrom/bohr slip has invalidated a full 240-leg campaign.

## Post-processing

1. Run `produce_force_constants`, then symmetrize; ASR and permutation residuals stay near 1e-15.
2. Confirm an imaginary mode with an energy-curvature audit: modulate along the softest SC-Hessian eigenvector, run 3 to 4 seeded amplitudes, and check E curves down with E(+A) equal to E(-A).
3. Report Gamma shifts with the Delta-lambda equals Delta-omega-squared consistency identity.

## Pitfalls

1. `rfelfd 3` without a `getddk` or `irdddk` DDK source aborts "Missing 1WF7"; this is a documented contract, not a bug.
2. GGA printed forces are favg-subtracted; build finite-difference references from raw forces with `prtvol 10` partitions.
3. Fixture references are toolchain-sensitive; certify on the census toolchain, then refresh.
