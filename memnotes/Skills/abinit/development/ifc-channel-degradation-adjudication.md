---
type: Domain Topic
id: abinit/development/ifc-channel-degradation-adjudication
domain: abinit
audience: development
artifact_role: guideline
status: draft
summary: Adjudicate whether an IFC fit target that worsens held-out IFC or phonons is a bug or Pareto capacity competition in pymultibinit campaigns.
triggers: [IFC channel degradation, held-out IFC worse, Pareto capacity competition, lambda arm adjudication]
aliases: [IFC degradation adjudication]
outcome: 
requires_procedures: []
governed_by: []
uses_knowledge: []
supported_by: []
supersedes: []
evidence: []
source_project: abinit
source_sha256: 9528ca4d3f8e9d822500ecf93f1aa16167374b38639f2835a86d0fd55d0ab68c
---

# IFC-Channel Degradation Adjudication

Use this adjudication when an IFC (interatomic-force-constant) fit target makes held-out IFC or phonons worse than not fitting it, and a bug is suspected.

## Procedure

1. Same-machinery decomposition: evaluate the fixed DDB harmonic (`xml_file=None`), the force-only baseline, and every λ arm at each structure with MACE FD references through `compare_ifc.model_ifc` (analytic_blocks, ncell=(1,1,1)). Record the RMSE and the anharmonic correction norm `‖model − fixed‖_F`.
2. Evaluate all arms on the fit targets. Only channel-carrying arms have `ifc_report` in fit_manifest.json. Evaluate the baseline (and any arm) on the 40-atom targets through the channel contraction: `read_basis_netcdf(basis.nc)` → `_reference_frame_from_ddb(ddb, ncell)` → `build_ifc_fit_data(basis, reference, ddb, config, targets)` → `ifc.rmse_per_target(np.array(record["coefficients"]))`. Coefficients live in the manifest; no refit is needed.
3. Lockstep test: correlate the suspect metric (held-out IFC) with an independent metric (held-out test-frame forces) across λ. Lockstep degradation through independent evaluation paths means the models are genuinely worse away from the target, not an evaluation artifact.
4. Contraction sanity: a real bug would show as design columns ≠ analytic Hessian. Verify on probe columns (max|diff| must be 0.0) and confirm the target residual actually drops (0.64 → 0.070 eV/Å²).

## Interpretation

- The channel improves its target exactly, held-out degrades in lockstep with forces, and corrections shrink away from the target → Pareto competition for shared capacity; the IFC target is largely redundant with force data but consumed at higher weight. Not a bug.
- Multi-target fits that reach neither target (per-target RMSE ≫ single-target value) → capacity split, not family coverage; more targets do not help at fixed ncoeff.
- Known real bugs in this channel (fixed and regression-tested): cross-chunk normal drops (b332709); atom-order mismatch at ncell ≠ (1,1,1). Regression tests need power >= 3 terms because quadratic pair Hessians are u-independent.

## Reference numbers (BaTiO3 ex10, ex08 base, ncoeff=40)

fixed 0.685 (T222) / 0.976 (T5) / 1.317 (R); baseline 0.643/0.165/0.268 with test forces 0.044; IFC arms T222 0.070 but R 0.32-0.58 and forces 0.056-0.221. Probes: `/tmp/ifc_decompose.py`, `/tmp/ifc_222_all_arms.py`.
