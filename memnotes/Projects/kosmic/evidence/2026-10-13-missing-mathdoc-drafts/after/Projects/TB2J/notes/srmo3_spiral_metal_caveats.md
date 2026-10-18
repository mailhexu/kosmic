---
artifact_role: knowledge
audience: both
confidence: 0.85
created: 2026-10-06
last_validated: 2026-10-06T00:00:00
validation_procedure: |
  Real-model runs in workspace .tmp/srmo3-spiral (mydev): planar SCF converged at q=0/0.25; kernel == frozen-f FD to 5.6e-6; gates green at q=0, torque flagged at q=0.25; response CLI fails closed on the non-planar reference.
validation_test: ".tmp/srmo3-spiral/run_scf.py, run_tb2j.py, downfold_anchor.json"
successful_usage_count: 1
last_used_successfully: 2026-10-06T00:00:00
usage_stale: false
related_files: ["TB2J/TB2J/spiral_kernels.py", "TB2J/TB2J/exchange_spiral.py", "TBUpy/tbupy/planar_spiral.py", "TBUpy/tbupy/planar_spiral_scf.py", "TBUpy/tbupy/spiral_state.py"]
related_functions: ["inplane_response_fd", "q0_anchor_check", "ExchangeSpiral", "PlanarSpiralProvider", "run_planar_spiral_scf"]
tags: ["spiral-state-mft", "srmo3", "material-fixture", "smearing", "free-energy-term"]
project: TB2J
status: draft
validated_by: automatic
validation_date: 2026-10-06T00:00:00
links_to: ["../specs/spin-spiral-mft/prd"]
linked_from: []
type: Project Knowledge
math_provenance: missing
math_provenance_reason: "srmo3_spiral_metal_caveats.md display math requires one MathDoc marker per equation"
---

# Metallic-reference caveats for spiral-state MFT (SrMnO3 fixture)

First real-material exercise of the spiral-state MFT primary contract
(nonmagnetic cubic SrMnO3 Wannier, 14 bands, uniform Stoner field
B=1 eV, workspace `.tmp/srmo3-spiral`). The machinery itself is
correct on real bases; three caveats are physics/protocol facts to
carry forward:

## 1. Free-energy term in the smeared-FD anchor on metals

$$
M_{\\rm smeared} - M_{\\rm frozen} \\;\\propto\\; w\\cdot D(E_F)\\cdot B^2
$$

`inplane_response_fd` recomputes Fermi occupations from perturbed
eigenvalues; with bands crossing $E_F$ (width 0.02) the free-energy
term is O(1) (per-site ~0.13, worst anchor residual 1.95-9.8) while
the FROZEN-f FD matches the kernel to 5.6e-6. Gapped references (the
dimer fixtures) are unaffected (1e-4). Consequence: on metallic
references scale `q0_anchor_tol` to the free-energy term, or make the
M reference frozen-f. Route comparisons (spiral frozen-eigenbasis vs
ExchangeCL2 CFR-Matsubara) are smearing-dominated on metals and NOT a
valid anchor; the dimer matched (ratio 1) only because it was gapped.

## 2. Multi-orbital atom downfold missing

`ExchangeSpiral` SpinIO emits ORBITAL-level `index_spin`. Comparing
with standard atom-level SpinIO trees requires summing orbital-pair
exchanges per atom pair — missing machinery (candidate follow-up
story; the inline downfold used for the fixture comparison lives in
`.tmp/srmo3-spiral`).

## 3. Response CLI mesh contract

`spiral_nonstationary._dual_transform` requires extents-declared
complete product meshes; persisted (shifted) 1D bundle kpts fail the
check via the CLI — needs an extents-aware mesh path.

Also: the NM SrMnO3 Wannier maps NO orbitals onto the Mn site
(displaced centres) — use the upstream uniform-field convention
(owning atoms relabelled gapless: v2 provenance requires it).

## Linked Concepts

- [../specs/spin-spiral-mft/prd](../subprojects/spin-spiral-mft/specs/prd.md)
- [../specs/quick-tasks/2026-10-06-srmo3-spiral-fixture](../specs/quick-tasks/2026-10-06-srmo3-spiral-fixture.md)
