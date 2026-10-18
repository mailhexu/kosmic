---
artifact_role: knowledge
audience: both
confidence: 0.9
created: 2026-02-20
last_validated: 2026-02-20T16:00:00
validation_procedure: |
  Read TB2J/magnon/magnon3.py, check Jq() and Hq() methods.
  Verify tensor structure matches (nR, nspin, nspin, 3, 3).
project: TB2J
status: stable
validated_by: automatic
tags: [magnon, exchange, tensor]
type: Project Knowledge
---

# Exchange Tensor


## Overview

The exchange tensor **J** describes the magnetic interaction between two spins. It is a 3×3 tensor that can be decomposed into isotropic, symmetric anisotropic, and antisymmetric (DMI) components.

## Principles

- The full exchange tensor contains all magnetic interaction information
- Different physical effects can be selectively included/excluded
- The tensor is stored as (nR, nspin, nspin, 3, 3) array in TB2J

## Details

The exchange tensor between sites i and j is a 3×3 matrix **J**_{ij} that can be decomposed into three physically distinct components:

$$
\mathbf{J}_{ij} = J_{ij}^{\text{iso}} \mathbf{I} + \mathbf{J}_{ij}^{\text{sym}} + \mathbf{D}_{ij} \times
$$

### Isotropic Exchange (Heisenberg)

The scalar exchange coupling $J^{\text{iso}}$ represents the isotropic Heisenberg interaction:

$$
J^{\text{iso}} = \frac{1}{3}\text{Tr}(\mathbf{J})
$$

This is the dominant interaction in most magnetic systems.

### Symmetric Anisotropic Exchange

The traceless symmetric part captures anisotropy in the exchange:

$$
J^{\text{sym},\alpha\beta} = \frac{1}{2}(J^{\alpha\beta} + J^{\beta\alpha}) - J^{\text{iso}}\delta_{\alpha\beta}
$$

### Dzyaloshinskii-Moriya Interaction (DMI)

The antisymmetric part defines the DMI vector **D**:

$$
D^\gamma = \frac{1}{2}\epsilon_{\gamma\alpha\beta} J^{\alpha\beta}
$$

The DMI favors perpendicular spin alignments and is crucial for chiral magnetism.

## Variables

| Symbol | Description | Units |
|--------|-------------|-------|
| **J** | Full 3×3 exchange tensor | eV |
| J^iso | Isotropic exchange scalar | eV |
| **J**^sym | Symmetric anisotropic tensor | eV |
| **D** | DMI vector | eV |

## Implementation

In TB2J, the exchange tensor is retrieved from SpinIO:

```python
JR = exc.get_full_Jtensor_for_Rlist(
    order="ij33",  # Shape: (nR, nspin, nspin, 3, 3)
    asr=False,     # Don't enforce acoustic sum rule
    SIA=True,      # Include single-ion anisotropy
    Jiso=True,     # Include isotropic exchange
    Jani=True,     # Include anisotropic exchange
    DMI=True       # Include DMI
)
```

The parameters `Jiso`, `Jani`, `DMI`, `SIA` allow selective inclusion of different interaction types.

## Linked Concepts

- [magnon_Jq_transform](magnon_Jq_transform.md): Fourier transform of exchange tensors to q-space
- [magnon_hamiltonian](magnon_hamiltonian.md): How exchange tensors enter the magnon Hamiltonian
- [notation](notation.md): Standard variable notations
