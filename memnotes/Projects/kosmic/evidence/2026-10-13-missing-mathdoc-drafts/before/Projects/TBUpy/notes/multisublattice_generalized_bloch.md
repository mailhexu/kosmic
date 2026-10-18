---
artifact_role: knowledge
audience: both
confidence: 0.9
created: 2026-09-25
last_validated: 2026-09-25T00:00:00
validation_procedure: |
  Branch spiral (e7a1eed + 6271ff9). pytest tests/test_spiral_multisublattice.py tests/test_spiral_state.py -> 27 passed in mydev; examples/multisublattice_spiral_state.py runs end-to-end (SCF converged, torque 5e-17, sidecar round-trip, hermitian folded pencil).
validation_test: "tests/test_spiral_state.py, tests/test_spiral_multisublattice.py"
successful_usage_count: 1
last_used_successfully: 2026-09-25T00:00:00
usage_stale: false
related_files: ["tbupy/generalized_bloch.py", "tbupy/spiral_state.py", "tbupy/io.py", "tests/test_spiral_state.py", "tests/test_spiral_multisublattice.py", "examples/multisublattice_spiral_state.py", "README.md"]
related_functions: ["MultiSublatticeSpiralConfig", "assemble_multisublattice_hq_sq", "MultiSublatticeSpiralProvider", "run_spiral_scf", "check_torque_free", "spiral_state_from_scf", "save_spiral_state", "load_spiral_state"]
tags: ["generalized-bloch", "spin-spiral", "multi-sublattice", "rotating-frame", "spiral-state", "tb2j-interface"]
project: TBUpy
status: stable
validated_by: automatic
validation_date: 2026-09-25T00:00:00
links_to: ["generalized_bloch_implementation", "generalized_bloch_spin_spiral_theory"]
linked_from: []
type: Project Knowledge
---

# Multi-Sublattice Generalized Bloch Spirals And Frozen Reference Bundles

TBUpy supports multi-sublattice single-q flat spirals in the primitive
cell on top of the provider layer (branch `spiral`, stories 001-002 of
the TB2J spec `spin-spiral-mft`).

## Assembler

`MultiSublatticeSpiralConfig(q_frac, taus, phis)` holds per-orbital
basis offsets `taus` and sublattice phase offsets `phis`;
`assemble_multisublattice_hq_sq(HR_up, HR_dn, SR, Rlist, config, k)`
builds the folded pencil

$$
H_q(k)_{\mu s,\nu s'} = \sum_R e^{2\pi i k\cdot R}\, T_{\mu\nu}(R)\,
e^{+i s \alpha_\mu/2}\, e^{-i s' \alpha_\nu(R)/2},\qquad
\alpha_\mu = 2\pi q\cdot\tau_\mu + \phi_\mu,
$$

with the overlap rotated by the same site unitaries (FPLO
convention). `Delta phi = pi` builds an AFM reference into the folded
cell. Conventions are pinned by the sympy derivation
`TB2J/docs/sympy/spin_spiral_generalized_bloch.py`.

## Provider and rotating-frame SCF

`MultiSublatticeSpiralProvider(HR_up, HR_dn, SR, Rlist, config,
B_local)` wraps the assembler, adds the twisted-gauge on-site field
`B_mu sigma_z` (spin-interleaved), and rejects SOC / off-site spin
flip / spin-dependent sources with fail-loudly guards. Because
`TBUpyModel` accepts any provider, `run_spiral_scf(...)` is the
ordinary spinor SCF on the folded pencil: `V_U` is built from the
twisted-frame density by the Spinor Hubbard terms (FLL-ns / NoDC,
rotation-covariant to ~2e-16) and occupations come from the folded
bands — no new SCF machinery was needed.

## Torque gate and sidecar

A valid force-theorem reference must be torque-free:
`check_torque_free(rho)` measures the transverse local moment per
orbital and raises `SpiralTorqueError` (per-site norms, override flag)
above tolerance. `spiral_state_from_scf(provider, scf)` freezes the
reference into `SpiralState` (13 contract fields) and
`save/load_spiral_state` round-trip the `tbupy_spiral_state` v1
sidecar (`.spiral.nc`), which TB2J's spiral-state MFT exchange path
consumes (`python -m TB2J.scripts.tb2j_spiral`). The bundle contract
is pinned in `TB2J_dev/memnotes/Projects/TB2J/specs/spin-spiral-mft/
research-supporting/spiral-bundle-contract.md`.

Physics caveat: exact torque-free LAB references require
`q.tau_mu` sublattice-independent; intra-cell `q.tau` phases cant the
frozen reference at `O((t/B)^2)`.

## Example

`examples/multisublattice_spiral_state.py`: two-sublattice chain ->
config/provider -> rotating-frame SCF -> torque gate -> sidecar
round-trip -> folded-pencil rebuild (hermiticity check).

## Linked Concepts

- [generalized_bloch_implementation](generalized_bloch_implementation.md)
- [generalized_bloch_spin_spiral_theory](generalized_bloch_spin_spiral_theory.md)
