---
artifact_role: knowledge
audience: both
confidence: 0.95
created: 2026-03-19
last_validated: 2026-03-19
validation_procedure: |
  Run: cd TB2J && python -m TB2J.scripts.dmft2J \
    --dmft_file=../Refs/DMFT/LaMnO3_DMFT_data/sig.inp \
    --path=../Refs/DMFT/LaMnO3_DMFT_data --prefix=wannier90 \
    --spin-channels=+1,-1,-1,+1 --magnetic-elements=Mn \
    --nspin=1 --mode=static-hamiltonian --kmesh 4 4 4 \
    --output_path=../.tmp/LaMnO3_static_ham
  Check exchange.out: Mn1,Mn4 w_magmom ≈ −3.2 μB, Mn2,Mn3 ≈ +3.2 μB, total = 0.0
project: TB2J
status: draft
validated_by: automatic
tags: [dmft, hamiltonian, patching, afm, exchange-splitting]
type: Project Knowledge
math_provenance: missing
math_provenance_reason: "dmft_static_hamiltonian_patching.md display math requires one MathDoc marker per equation"
---

# DMFTstaticManager: Spin-Aware H(R=0) Patching


## Overview

`DMFTstaticManager` folds the DMFT self-energy static correction (Σ(∞) − V_dc) directly into the Wannier Hamiltonian H(R=0), then runs the standard collinear `ExchangeCL2` calculation. The key challenge is patching `ham_up` and `ham_dn` such that `Delta = H_up(R=0) - H_dn(R=0)` has the correct sign per atom to reproduce the physical spin structure.

## Physical Principle

`ExchangeCL2` computes the exchange splitting matrix:

$$
\Delta_i = H^{\mathrm{up}}_{ii}(R=0) - H^{\mathrm{dn}}_{ii}(R=0)
$$

The sign of `Delta` at each atom determines the sign of the computed magnetic moment (`spinat`), which in turn sets the sign of J via the LKAG formula.

For an AFM system:
- **Spin-up atoms**: `Delta > 0` (majority spin is up)
- **Spin-down atoms**: `Delta < 0` (majority spin is down)

## Patching Rule

Starting from a single non-spin-polarized Wannier Hamiltonian (deep-copied into `ham_up` and `ham_dn`), apply the self-energy correction as follows:

| Atom type | Target model | Shift applied | Resulting Delta |
|-----------|-------------|---------------|-----------------|
| Spin-up (spin_ch = 0) | `ham_up` | `+σ_up` | `(base + σ_up) − base = σ_up > 0` ✓ |
| Spin-down (spin_ch = 1) | `ham_dn` | `−σ_dn` = `+|σ_dn|` | `base − (base + |σ_dn|) = −|σ_dn| < 0` ✓ |

Note: `σ_dn` values are **negative** (e.g., −2 to −3.6 eV), so `−σ_dn` is positive.

## Code (dmft.py, ~line 1277)

```python
spin_ch = orbital_map["spin_channels"][corr_idx]   # 0=up, 1=dn

if spin_ch == 0:
    # Spin-up atom: shift ham_up upward → Delta = +σ_up > 0
    target = ham_up
    sigma_diag = sigma_up_diag
    sign = 1.0
else:
    # Spin-down atom: shift ham_dn upward (by +|σ_dn|) → Delta < 0
    target = ham_dn
    sigma_diag = sigma_dn_diag
    sign = -1.0   # negate: +|σ_dn| pushes ham_dn above ham_up at this site

H0 = target.data[(0, 0, 0)]
for local_i, wann_i in enumerate(wann_orbs):
    H0[wann_i, wann_i] += sign * sigma_diag[local_i]
```

## Common Bug (and Why It Fails)

The original (wrong) code applied `+σ_dn` (negative value) directly to `ham_dn`:

```python
# BUG: For spin-down atom, σ_dn < 0
H0[wann_i, wann_i] += sigma_dn_diag[local_i]   # adds negative number to ham_dn
# Result: Delta[dn_atom] = base − (base + σ_dn) = −σ_dn > 0  ← WRONG SIGN
```

This made all atoms appear spin-up, destroying the AFM structure.

## Verified Results for LaMnO3

With correct patching (`--spin-channels=+1,-1,-1,+1`):

| Atom | w_magmom (μB) | Physical expectation |
|------|--------------|---------------------|
| Mn1  | −3.22        | ≈ ±3.5              |
| Mn2  | +3.20        | ≈ ±3.5 (opposite)   |
| Mn3  | +3.20        | ≈ ±3.5 (opposite)   |
| Mn4  | −3.22        | ≈ ±3.5              |
| Total| 0.000        | 0 (AFM)             |

Exchange J values (d ≈ 3.88 Å in-plane): +12.6 to +15.2 meV (FM in-plane, as expected for A-type AFM LaMnO3)
Exchange J values (d ≈ 3.94 Å out-of-plane): −3.82 meV (AFM between planes)

## Linked Concepts
- [self_energy_embedding](self_energy_embedding.md): How Σ is mapped to Wannier orbital indices
- [spin_channel_mapping](spin_channel_mapping.md): Manual `--spin-channels` CLI flag
- [dmft_tb2j_workflow](dmft_tb2j_workflow.md): Overall workflow context
