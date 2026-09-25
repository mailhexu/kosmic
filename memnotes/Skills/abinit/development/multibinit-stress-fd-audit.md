---
type: Domain Topic
id: abinit/development/multibinit-stress-fd-audit
domain: abinit
audience: development
artifact_role: guideline
status: draft
summary: Ground-truth audit of fitted MULTIBINIT model stresses with FD dE/deta, harmonic-anharmonic decomposition, and symmetry probes.
triggers: [MULTIBINIT stress audit, model stress wrong, JAX stress bug, lattice convention stress]
aliases: [stress FD audit]
outcome: 
requires_procedures: []
governed_by: []
uses_knowledge: []
supported_by: []
supersedes: []
evidence: []
source_project: abinit
source_sha256: 1b73b5d0dd2315759a3a1a8022c9d9c76494a1b47660d8c3f09073769355ef19
---

# MULTIBINIT Stress Audit

Use this ground-truth audit when fitted MULTIBINIT/pyeffpot model stresses look wrong (too small, too large, damped, dead components, xx/yy/zz asymmetry) and before changing fit weights, basis options, or blaming greedy selection. The 2026-08-28 BaTiO3 case: "asymmetric, damped stresses" were actually a JAX evaluator bug that doubled the η¹-term stress plus a transposed-lattice measurement artifact; the fit and the symmetry were fine.

## Procedure

1. Evaluate with the correct low-level convention; bypass the ASE wrapper:
```python
pot = EffectivePotential.from_files(ddb, xml_file=fitted_nc, ncell=(2,2,2), dipdip=True, asr=False)
e, f, s = pot.evaluate(xcart_bohr, rprimd.T)  # lattice COLUMNS; stress is 3x3 Ha/Bohr^3
```
   `MultibinitPotential.evaluate` expects ASE ROW-vector cells and transposes internally. Passing `rprimd.T` there injects a spurious shear (about 0.2% for near-cubic cells) that fakes per-component asymmetry and kills shear correlations.
2. Take a finite-difference (FD) ground truth before trusting any analytic stress. Deform lattice and positions affinely and consistently, with a central difference at eta about 1e-4 (large-amplitude FD on stiff fitted coefficients suffers truncation):
```python
F = np.eye(3) + eps            # eps = eta * e_a e_b (axial); eta/2 on both off-diagonals for shear
Ep = pot.evaluate(pos @ F.T, F @ lat)[0]
Em = pot.evaluate(pos @ (np.eye(3)-eps).T, (np.eye(3)-eps) @ lat)[0]
sigma_fd = (Ep - Em) / (2*eta) / abs(np.linalg.det(lat))
```
   Compare against the analytic tensor component. Engineering versus tensor shear differs by exactly 2x; that is convention, not a bug.
3. Decompose harmonic versus anharmonic: evaluate `from_files(ddb, xml_file=None)` and subtract. If `full − harmonic` differs from the fitter-feature predictions (`evaluate_basis_features(...).stress @ values`), the evaluator's anharmonic stress path is wrong, not the fit. Compare the JAX and numpy paths by forcing `_use_jax=False`; a divergence localizes the bug to one path. Known-fixed: the `evaluate_jax` column-max strain-power doubling (2026-08-28); regression test `tests/test_jax_eval_stress_parity.py` guards it.
4. Run a cheap, decisive symmetry check:
   - Phi point-group test: for each symrel operation S with supercell atom permutation P, `phi4[P][:,:,P] == S·phi4·S^T` (expect about 1e-16 for a symmetric DDB).
   - Single-atom probe: displace one high-symmetry atom by 0.05 Å along x/y/z on the evaluator's own reference structure; energies must be identical. A spread proportional to u² means harmonic asymmetry; an amplitude-invariant spread means a background artifact.
   - Coefficients are orbit sums (48/24/3-term orbits in cubic systems), so greedy selection of whole coefficients cannot break symmetry. Suspect orbit truncation only if single-coefficient probes show direction-dependent energy at large amplitude.

## Common pitfalls

- The reference stress for relaxed parents is about 0; the mean stress needs pure-strain linear terms. `even_pure_strain=True` skips odd powers, so `max_strain_power=1` yields an empty pure block.
- Rotating Cartesian coordinates without permuting sublattice labels explodes site-resolved models (about 1e10 eV); that is expected, not a bug.
- Run with `CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu`; the JAX anharmonic channel is float32 (about 1e-7 relative).
