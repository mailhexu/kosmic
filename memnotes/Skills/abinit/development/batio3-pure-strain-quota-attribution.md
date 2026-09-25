---
type: Domain Topic
id: abinit/development/batio3-pure-strain-quota-attribution
domain: abinit
audience: development
artifact_role: guideline
status: draft
summary: Attribute BaTiO3 example-08 fit-metric changes to quota, generator, reference-stress, or parent-structure factors with one-factor-per-arm scratch runs.
triggers: [BaTiO3 retraining attribution, pure strain quota, stress regression example-08, basis fingerprint change]
aliases: [pure-strain quota attribution]
outcome: 
requires_procedures: []
governed_by: []
uses_knowledge: []
supported_by: []
supersedes: []
evidence: []
source_project: abinit
source_sha256: 9d60957969a9bb5984a1cf0a7394f26aac5f80b6ad78fa5888f677b72b3ad549
---

# BaTiO3 Pure-Strain Quota Attribution

Use this procedure to attribute fit-metric changes on `atomchain/examples/08_training_set_strategies_batio3` after retraining or after pymultibinit basis-generation changes.

## Procedure

1. Replicate the production path on a scratch copy: build a `WorkflowContext` from the workflow YAML, seed `manifest['stages']` from the copied manifest.yaml (ddb and evaluate outputs), then call `run_training_stage`, `_model_calculator_from_training`, and `validate_fitted_model` on the cached `training/test.traj`.
2. Vary one factor per arm: `training.options.min_pure_strain_ratio` (quota), `include_pure_strain`/`max_strain_power` (generator), reference-stress restoration (`context.reference_stress_ha_bohr3` from prepare outputs), or the parent structure (`BaTiO3.vasp` unrelaxed versus output-dir `parent.vasp` relaxed).
3. Check `model/basis_pair_diagnostics.json` (fingerprint, cutoff, ncoeff) to confirm which basis a run actually used. The basis fingerprint includes parent positions, so the parent choice silently changes the candidate pool (18,535 cubic versus 51,380 relaxed for npt_md).
4. Interpret: the quota helps stress about 30% on the enriched basis; enrichment itself costs about 3x stress versus the old parameters (`include_pure_strain=False`, `max_strain_power=1`); metastable and large-strain training sets suffer most.

## Pitfalls

- `_stage_signature` hashes the whole config, so any YAML edit re-runs ALL stages; use the scratch-context method instead of editing YAMLs.
- Background bash jobs die at 3600 s, and fits with basis regeneration take about 45-70 min under load; use `timeout 0` plus async, and check the `basis.nc` mtime to distinguish reuse from regeneration.
- `shutil.copytree` preserves mtimes; compare content hashes, not mtimes, to detect regeneration.
- A killed process can leave a corrupt NetCDF basis file (MaskError on read); rerun the arm.
