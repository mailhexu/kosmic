---
type: Domain Topic
id: methods/development/spgrep-modulation-canonical-seeds
domain: methods
audience: development
artifact_role: guideline
status: draft
summary: Generate symmetry-canonical phonon eigenvector seeds and displacement patterns from degenerate subspaces with spgrep-modulation eigenspaces and order-parameter directions.
triggers: [canonical phonon seeds, order parameter direction, degenerate eigenspace, modulated structure, daughter space group]
source_project: native
source_sha256: empty
aliases: [spgrep modulation seeds]
---

# spgrep-Modulation Canonical Phonon Seeds

Generate symmetry-canonical phonon seeds from degenerate subspaces with spgrep-modulation.

## Recipe

1. Build eigenspaces at q; choose supercell denominators as the smallest d of 12 or less with `d
   q` integral per component.

   ```python
   from spgrep_modulation.modulation import Modulation
   md = Modulation.with_supercell_and_symmetry_search(
       dynamical_matrix=phonon.dynamical_matrix, supercell_matrix=np.diag(denoms),
       qpoint=q, factor=phonon.unit_conversion_factor, symprec=1e-5)
   ```

Blocks match plain `eigh` blocks one to one; verify with the minimal block-overlap singular
value near 1.

2. Canonicalize. The eigenspace basis is not canonical; use order-parameter directions (OPD)
   with one direction:

   ```python
   from spgrep_modulation.isotropy import IsotropyEnumerator
   ie = IsotropyEnumerator(md.little_rotations, md.little_translations, md.qpoint, irrep)
   for opd, sub in zip(ie.order_parameter_directions, ie.maximal_isotropy_subgroups):
       if len(opd) == 1:   # len > 1 is a subspace, not a seed
           psi = np.tensordot(opd[0], eigvecs, axes=(0, 0))
   ```

Each one-dimensional OPD seed is axis-pure to machine precision; its modulation yields the
daughter SG through spglib; default to the highest isotropy-subgroup order. The full seed set
is the chosen line plus its little-group images, QR-orthonormalized.

3. Convert gauge when the dynamical matrix carries phase factors `exp(-2 pi i (r_k - r_k') q)`
   (example: lawaf `PhonopyWrapper.solve`): `v(kappa) = exp(+2 pi i r_kappa q)
   v_spgrep(kappa)`; identity at Gamma.

## Traps

Time-reversal-invariant momenta (TRIM: Gamma, X, M, R) cannot expose a sign error; validate the
gauge at a non-TRIM commensurate q through a block-projector residual of 1e-10 or less. Mass-
weighted convention matches dynamical-matrix modes, not interatomic-force-constant modes.
Oracle: acoustic-triple OPDs must report the parent space group.

Validated on cubic BaTiO3 (Pm-3m): soft T1u gives P4mm (#99) polar seeds, Amm2 (#38), and R3m
(#160); T2u gives P-4m2 (#115) with oxygen-only motion. Two distinct P4mm OPD families can
share one SG number; prefer SG-number identification over enumeration index.
