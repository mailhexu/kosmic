---
artifact_role: knowledge
audience: both
confidence: 0.95
created: 2026-04-14
last_validated: 2026-04-14
validation_procedure: "Cross-reference with SIESTA manual and CrI3 example basis files"
project: siesta_simplex_basis
status: stable
validated_by: code_analysis
tags: [siesta, basis-set, pao]
type: Project Knowledge
---

# SIESTA PAO Basis Set Structure


## Overview
SIESTA uses Numerical Atomic Orbitals (NAOs) as its basis set. Each basis function is a product of a radial part (strictly zero beyond a cutoff radius) and a spherical harmonic. The basis is organized hierarchically by species, angular momentum shells, and zeta levels.

## Principles
- Basis functions have **finite support**: strictly zero beyond a user-specified cutoff radius `rc`
- Multiple-zeta basis sets use **contraction** of several radial functions per angular momentum channel
- The `split` (Sankey-Nelson) scheme generates multiple zetas by splitting a confined atomic orbital at successively smaller radii
- Soft confinement potentials (`E vcte rinn`) shape the orbitals near their boundaries

## Details

### Species Block Structure
For each species in the `PAO.Basis` block:

```
Label  nshells  ionic_charge
  n=N  L  Nzeta  E  vcte  rinn
    rc_1  rc_2  ...  rc_Nzeta
    lambda_1  lambda_2  ...  lambda_Nzeta
```

**Line 1**: Species label, number of l-shells, ionic charge (net charge transferred to/from atom).

**Shell line**: `n=N` (principal quantum number, mandatory for semicore), `L` (angular momentum: 0=s, 1=p, 2=d), `Nzeta` (number of zetas), `E` (enables soft confinement), `vcte` (potential strength in Ry), `rinn` (inner radius in Bohr).

**rc line**: Cutoff radii for each zeta in Bohr. Must satisfy `rc(1) > rc(2) > ... > rc(Nzeta)` and `rc(1) > rinn`.

**lambda line**: Contraction (scale) factors. Always 1.0 during simplex optimization.

### Valence Electronic Configuration for Cr (Z=24)
Ground state: [Ar] 3d^5 4s^1. In SIESTA with semicore:
- 3s (n=3, l=0): 1 zeta, semicore (fully fixed, not optimized)
- 3p (n=3, l=1): 1 zeta, semicore (fully fixed)
- 4s (n=4, l=0): valence s-shell
- 3d (n=3, l=2): valence d-shell
- 4p (n=4, l=1): polarization shell

### Valence Electronic Configuration for I (Z=53)
Ground state: [Kr] 4d^10 5s^2 5p^5. Valence:
- 5s (n=5, l=0): valence s-shell
- 5p (n=5, l=1): valence p-shell
- 5d (n=5, l=2): polarization shell

### Soft Confinement Potential
The soft confinement potential prevents the orbital from having a sharp cutoff at `rc`:

$$
V_{soft}(r) = V_{cte} \quad \text{for} \quad r_{inn} < r < r_c
$$

Without soft confinement (`vcte=0`), orbitals are zero beyond `rc` but may have a discontinuous derivative. With it, they decay smoothly. `rinn` defines where the soft potential begins; between `rinn` and `rc`, the orbital is gently pushed to zero.

### Basis Size Naming Convention
- **SZ**: Single-Zeta (1 orbital per angular momentum)
- **DZ**: Double-Zeta (2 orbitals per angular momentum)
- **TZ**: Triple-Zeta (3 orbitals)
- **P**: Plus polarization (extra angular momentum shell)
- **D**: Plus diffuse (extra zeta for polarization shells)

## Variables
| Symbol | Description | Units |
|--------|-------------|-------|
| `n` | Principal quantum number | dimensionless |
| `L` | Angular momentum quantum number | dimensionless |
| `Nzeta` | Number of PAOs per shell | dimensionless |
| `rc` | Cutoff radius | Bohr |
| `vcte` | Soft confinement strength | Ry |
| `rinn` | Inner soft-confinement radius | Bohr |
| `lambda` | Contraction factor | dimensionless |
| `ionic_charge` | Net charge on species | e |

## Linked Concepts
- [simplex_input_format](simplex_input_format.md): How basis blocks are specified in simplex.in
- [basis_optimization_strategy](basis_optimization_strategy.md): Strategy for choosing which parameters to optimize
- [notation](notation.md): Standard variable notations
