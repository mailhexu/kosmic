---
type: Domain Topic
id: lawaf/development/wigner-irrep-probe
domain: lawaf
audience: development
artifact_role: guideline
status: draft
summary: Build and validate Wigner irrep-sector projectors and trial orbitals on lawaf phonon fixtures; character_table recipe, gauge-free checks, phonopy 4.1 traps.
triggers: [wigner projector, irrep sector, site irrep, symmetry trial orbitals]
aliases: []
outcome: 
requires_procedures: []
governed_by: []
uses_knowledge: []
supported_by: []
supersedes: []
evidence: []
source_project: lawaf
source_sha256: f7544bc5c97764043a56a902d25cef18bf3f824a1f721e045cfd84cd231214d5
---

# Wigner Irrep-Sector Probe

Prototype symmetry-projected trial orbitals or irrep-sector diagnostics on a
lawaf phonon fixture (R1 IrrepField / R2 SymmetryTrialOrbitals work), or
debug a per-q irrep decomposition against phonopy.

## Recipe (validated on BaTiO3 DM_dip_wang, Gamma)

1. Build lawaf's own action: `sga = build_space_group_action(phonon)` from `lawaf.anharmonic`; `lg = little_group(sga, q)`; `ct = character_table(sga, lg)` from `lawaf.anharmonic.compatibility`.
2. Matrices `M = {g: sga.matrix(g, q)}`. Decompose via characters `chi = [tr M[g]]` to `ct.labels(ct.multiplicities(chi, per_op=True))`; cross-checks phonopy `set_irreps` labels (4×T1u+T2u on BaTiO3 Gamma).
3. Site-irrep characters: `site_ops = [g for g in lg if sga.atom_maps[g][kappa]==kappa]`; `tau = site_irrep_matrices(sga, site_ops, name)` from `lawaf.anharmonic.gauge`; `chi_site[g] = tr tau[g]`.
4. Central projector `P = (d/|lg|) Σ_g conj(chi_site[g]) M[g]`. Verify idempotency `|P²−P|` and trace = copies×d.
5. Seeds: unit displacement columns `v[3κ+a]`; `U = orth(P @ seeds)` (SVD). Validate gauge-FREE: isotypic covariance `max|P D(g)U − D(g)U| ≈ 0` AND character match `|tr(U†D(g)U) − χ(g)| ≈ 0`. NEVER check `D(g)U == U τ(g)` directly — the site-τ gauge differs from the projector gauge (fails at O(1) even when correct).
6. Copy-selection diagnostic: per-band membership `<v_j|P|v_j>`, then svmin of `U† Q_soft` and per-copy expansion (product of singular values). Symmetry alone gives svmin < 1 (0.68 on BaTiO3); copy choice needs anchors or energy.

## Traps

- Eigenvectors: `PhonopyWrapper(phonon, mode='dm', is_nac=False). solve_all([q])`; phonopy `DynamicalMatrix` has no `get_eigenvectors()`/ `.eigenvectors` in 4.1.
- `np.linalg.svd(X, compute_uv=False)` returns one array; no unpacking.
- phonopy `set_irreps(q)` on 4.1: labels None off-Gamma on this fixture; spgrep is the engine. lawaf-to-spgrep gauge: identity at Gamma; at non-TRIM q multiply per atom by `e^{+2πi r·q}` (memo 2026-08-29, finding 4).
- NAC: probe the non-NAC model (builder convention); NAC enters after downfold.

## Reference numbers (BaTiO3 Gamma, native cm⁻¹)

Soft triplet −201.76 (×3). Decomposition 4×T1u+T2u. P idempotency 1.6e-15.
Ti-seed character deviation 3.1e-15. svmin against soft 0.6796.
