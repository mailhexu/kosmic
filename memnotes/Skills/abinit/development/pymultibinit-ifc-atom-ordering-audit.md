---
type: Domain Topic
id: abinit/development/pymultibinit-ifc-atom-ordering-audit
domain: abinit
audience: development
artifact_role: guideline
status: draft
summary: Audit atom-order mismatches between phonopy and pymultibinit supercells when IFC fits or Hessian comparisons go wrong at ncell != (1,1,1).
triggers: [pymultibinit atom ordering, IFC fit ordering bug, supercell permutation mismatch, build_ifc_fit_data]
aliases: [IFC atom-order audit]
outcome: 
requires_procedures: []
governed_by: []
uses_knowledge: []
supported_by: []
supersedes: []
evidence: []
source_project: abinit
source_sha256: a9b262cd07a6ba37490a08359b933931cc4bd4c0c7c8739d5c307b2dff1d2290
---

# pymultibinit IFC Atom-Ordering Audit

Use this audit when an IFC (interatomic-force-constant) channel fit behaves pathologically at ncell ≠ (1,1,1): goal_ifc barely reducible, λ-arms with identical RMSEs, design columns disagreeing with analytic Hessians. Also use it when writing tests for `build_ifc_fit_data`/`_basis_ifc_columns`, or when comparing model and reference supercells built by different tools.

## The two orders

- Phonopy supercells are atom-major: all images of atom 0 first.
- pymultibinit fit-reference supercells (`_reference_frame_from_ddb`, `_supercell_indices`) are cell-major with the atom index fastest: `atom + natom_uc*(iz + nz*(iy + ny*ix))`.

At ncell = (1,1,1) the matcher permutation is the identity, so every ordering bug is invisible; all old 5-atom campaign numbers stay valid for that reason.

## Correct contract (build_ifc_fit_data)

Everything is reference-ordered:
- `u[perm[i]] = xcart_t[i] − ref_xcart_in_t[perm[i]]` with `perm = _greedy_assignment(_fractional_distance_matrix(xred_t, ref_xred))`; perm[i] is the reference atom matched to target i.
- Gather the target IFC matrix into reference order with `argsort(perm)` (the inverse), not with perm.
- `k_fixed` stays reference-ordered (no gather).
- Design columns from `_basis_ifc_columns` are reference-ordered because their scatter indices come from basis anchors through `_supercell_indices`.

## Fast diagnostics (no refit)

1. Displacement magnitude: matched `max|u|` must be physical (about 0.2-0.25 Bohr for GM4 BaTiO3 off-centering). Values near lattice scale (11 Bohr) mean unmatched differencing.
2. Worst matched fractional distance: `cost[arange(n), perm].max()` ≪ 0.25. Sublattice-symmetric cells can make the assignment ambiguous (an atom near mid-cell); pick test positions with a unique nearest match.
3. Design-vs-analytic parity: for a few coefficients j, build `MultibinitPotential.from_pyeffpot(ddb, xml_file=write_fitted(one-hot c_j), ncell=..., dipdip=True)`, take `analytic_blocks(pos, cell).ifc`, permute to reference order with `argsort(perm)`, and subtract the DDB-only potential blocks; the result must equal `ifc_data.designs[0][j]` exactly (0.0000 is achievable). Compare the large column (|col| about 10-20); tiny or zero columns (strain-gated terms) prove nothing.

## Traps

- Quadratic (power-2) pair terms have u-independent Hessians (E = w·d² is constant). A regression test built only from power-2 terms passes on buggy code; include at least one power-3 term so the column is linear in the pair displacement.
- Reference-state phonon identity: at u = 0 every anharmonic Hessian contribution (displacement powers >= 3) vanishes identically, even at nonzero strain η, because η·u^p still needs u ≠ 0 to curve. All fitted arms therefore give identical reference-state phonons by construction (arm-vs-arm about 1e-15 relative; a baseline arm equals the DDB-only potential to machine zero). Any max|Δf| at the reference state is a property of the shared fixed harmonic versus the FD reference, not arm evidence. Do not write prose implying arm-dependent reference behavior.

## Known commit

`b0d6232` on pymultibinit main carries the ordering fix plus the regression test `test_build_ifc_fit_data_matches_atoms_when_orders_differ` (a shuffled (2,1,1) supercell, verified to fail on both the positional and permute-after variants).
