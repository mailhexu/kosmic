---
type: Domain Topic
id: abinit/development/phonopy-fc-cross-pipeline-comparison
domain: abinit
audience: development
artifact_role: guideline
status: draft
summary: Compare phonon force constants and bands between phonopy and a custom evaluator while separating ordering, frame, and FD-convergence defects.
triggers: [phonopy force constant comparison, FC pipeline mismatch, supercell ordering phonopy, band comparison disagreement]
aliases: [phonopy FC comparison]
outcome: 
requires_procedures: []
governed_by: []
uses_knowledge: []
supported_by: []
supersedes: []
evidence: []
source_project: abinit
source_sha256: ed9c78ce788aec5878497b498f405eeba10148ead4dbf858acb785a8c332f2d0
---

# Phonopy FC Cross-Pipeline Comparison

Compare force constants (FC) or phonon bands between phonopy and a custom evaluator (pymultibinit, ASE calculator, DFT code) with different atom orderings, or when FC and band comparisons disagree unexpectedly.

## Order of operations (do not skip step 1)

1. Validate reference-cache internal consistency first: read `FC_yaml = ph.force_constants`; rerun `ph.produce_force_constants()` on the yaml's own stored `ph.dataset["first_atoms"][i]["forces"]`; compare. A mismatch (a 28 eV/Å² case in batio3_rattle_fw_s0.25 fd_cache) means the cache mixes orderings or sets, and it is unusable as a precision reference; regenerate the FD through the current evaluator.
2. Take a direct finite difference (FD) of the evaluator (h about 1e-4 Bohr, central differences on energies or forces) versus the analytic or other block, in one frame, one atom row first. This isolates convention bugs (sign, units, prefactors) from ordering bugs. Machine precision here (1e-17) proves the analytic side regardless of everything below.
3. Only then compare full FC matrices or bands across pipelines.

## Ordering pitfalls (each cost real debugging time)

- Phonopy standardizes cells silently: even with `primitive_matrix=eye`, `Phonopy(...)` may shift origins, permute lattice rows, or change atom order, and freshly built objects and loaded objects (from `phonopy_load`) can differ. Never assume reduced positions correspond 1:1.
- Build the mapping from Cartesian positions plus a species check, periodic-boundary-wrapped, with per-atom `argmin` and a tolerance; assert a bijection (all matched, unique). Position matching alone can be degenerate under the crystal point group (cubic: 48 signed permutations align positions equally well).
- Supercell orders differ: phonopy is atom-major (all images of atom 0, then atom 1, ...), and pymultibinit-style builders are cell-major (origin cell atoms first). Compact FC `(n_unit, n_sc, 3, 3)` rows map through unit-atom position matching, not `arange(n_unit)`.
- Component sign flips at position-matched sites (a yz flip with xx agreeing) are a mirror/frame relabeling of a symmetry-equivalent site, not an error in the data; band frequencies stay identical (unitary conjugation), but elementwise FC comparison breaks with h-independent systematic differences. An h-independent error is systematic (ordering/frame); an h-dependent error is FD truncation. Do not chase it as an FD-convergence issue.
- `ph.dataset` may be one-sided (only +displacements); central differences need your own ± configs: displace `ph.supercell` directly.
- Permute evaluator forces back to phonopy order (`F_ph = F_ev[m]`, not `F_ph[m] = F_ev`) before `ph.forces = ...`.
- `PhonopyAtoms` has no `set_masses` (use the `masses` property); `get_band_qpoints_by_seekpath` returns 3 values in current phonopy.

## Sanity anchors (BaTiO3 cubic, 7.56 Bohr supercell)

Ba on-site FC about +8.49 eV/Å² (diagonal; from 0.08737 Ha/Bohr² × 97.17). Ba-Ti nearest-neighbor [111] block: diagonal about (−0.44, ...), off-diagonal about 1.23. Ba-Ba [100] nearest-neighbor block: diagonal about (−2.27, 0.53, 0.53).
