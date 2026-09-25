---
type: Domain Topic
id: lawaf/development/window-gauge-mismatch-debug
domain: lawaf
audience: development
artifact_role: guideline
status: draft
summary: Diagnose lawaf window/gauge/downfold mismatches; builder-vs-phonopy spectra comparison, NAC conventions, character-projector label checks.
triggers: [window bands mismatch, downfold spectrum mismatch, anchor gauge, NAC convention]
aliases: []
outcome: 
requires_procedures: []
governed_by: []
uses_knowledge: []
supported_by: []
supersedes: []
evidence: []
source_project: lawaf
source_sha256: c2b3256b1bbd29e3bd3856f31dd6644c6917bd2221cccf2d3455dfcd58ae910a
---

# Window/Gauge Mismatch Debug

Use when lawaf downfolding or phonon-window work shows disagreeing fixture
bands, illegal windows, a wrong constrained gauge, or a broken folded round
trip — especially after changing `window_bands`, `is_nac`, or the phonopy
wrapper.

## Recipe

1. Compare builder vs phonopy-standard spectra at every mesh q (trust neither side alone): `std = phonon.run_qpoints(builder_kpts); std = phonon.get_qpoints_dict()["frequencies"]` (NAC via nac_params); `be = np.sign(builder.evals[ik]) * np.sqrt(np.abs(builder.evals[ik]))`. Builder evals are omega^2 in internal units (THz-ish vs cm-1); compare best-match residuals, not raw values. Agreement only at Gamma means a DM-construction/NAC divergence (`lawaf/interfaces/phonopy/phonopywrapper.py`; post-fix it must use native `run_qpoints` eigenpairs). Matching values with permuted rows mean a band-ordering bug (`_window_rows` / `builder.ibands`). `get_dynamical_matrix_at_q` is analytic-only and silently ignores `nac_params`; only `run_qpoints` applies NAC.
2. Per-anchor character-projector weights catch label/convention mismatches: `M(h) = psi† S'(h) psi` for the little group, `P_irrep = sum_h χ*(h) M(h) · dim/order`; print `|diag(P)|` per retained row. Full-block weight 0 where legality labels an irrep means the character table is inconsistent with the applied matrices (cocycle/ pure-point vs lawaf gauge) or an arm-convention swap (B1u↔B2u).
3. Physics checks before blaming code: - NAC at off-axis q (e.g. M=(0,½,½)) breaks the point little group down to the q̂-preserving subgroup; a window legal on one spectrum can straddle a block on the other — correct rejection, not a bug. - No Cartesian intertwiner exists when window irrep content differs from vector-rep content (Gamma T1u yes; X E+B1u vs A2u+Eu no). Re-gauge is a Gamma-window device only.

## Verification anchors

`tests/test_anharmonic_2x2x2_downfold.py` (round trip ≤ 3e-15, all 8 q);
`tests/test_anharmonic_anchor_gauge.py` (residuals ~1e-15). Vault note:
`Projects/lawaf/notes/phonopy_wrapper_nac_convention.md`.
