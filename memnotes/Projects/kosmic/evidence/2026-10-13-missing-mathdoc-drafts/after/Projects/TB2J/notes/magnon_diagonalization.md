---
artifact_role: knowledge
audience: both
confidence: 0.9
created: 2026-02-20
last_validated: 2026-02-20T16:00:00
validation_procedure: |
  Read TB2J/magnon/magnon3.py, check Magnon._magnon_energies() method (lines 184-209).
  Verify Cholesky decomposition and bosonic metric eigendecomposition.
project: TB2J
status: draft
validated_by: automatic
tags: [magnon, diagonalization, cholesky]
type: Project Knowledge
math_provenance: missing
math_provenance_reason: "magnon_diagonalization.md display math requires one MathDoc marker per equation"
---

# Magnon Diagonalization


## Overview

Magnon energies are obtained by diagonalizing the Hamiltonian with the bosonic metric. Due to the indefinite nature of the bosonic metric, we use Cholesky decomposition followed by standard eigendecomposition to obtain positive magnon frequencies.

## Principles

- Bosonic systems have an indefinite metric (positive for creation, negative for annihilation)
- Cholesky decomposition requires positive semi-definite matrix
- Only positive eigenvalues correspond to physical magnon modes
- Negative eigenvalues indicate ground state instability

## Details

### The Problem

We need to solve the generalized eigenvalue problem:

$$
\mathbf{H} \mathbf{v} = \omega \mathbf{g} \mathbf{v}
$$

where the bosonic metric **g** has signature (+, ..., +, -, ..., -):

$$
\mathbf{g} = \begin{pmatrix} \mathbf{I}_N & 0 \\ 0 & -\mathbf{I}_N \end{pmatrix}
$$

### Cholesky Decomposition Approach

First, decompose **H** using Cholesky:

$$
\mathbf{H} = \mathbf{K}^\dagger \mathbf{K}
$$

This requires **H** to be positive semi-definite.

### Standard Eigendecomposition

Transform to a standard eigenvalue problem:

$$
\mathbf{K}^\dagger \mathbf{g} \mathbf{K} \mathbf{v} = \omega \mathbf{v}
$$

The eigenvalues come in pairs ±ω. Only the positive ones (N values) are physical magnon energies.

### Handling Non-Positive-Definite H

If Cholesky fails, the matrix may have negative eigenvalues, indicating the magnetic ground state is not stable:

```python
try:
    K = np.linalg.cholesky(H)
except np.linalg.LinAlgError:
    try:
        K = np.linalg.cholesky(H + 1e-6 * np.eye(2*n))
    except np.linalg.LinAlgError:
        min_eig = np.min(np.linalg.eigvalsh(H))
        K = np.linalg.cholesky(H - (min_eig - 1e-6) * np.eye(2*n))
        warn(f"WARNING: System may be far from magnetic ground-state. Min eigenvalue: {min_eig}")
```

The minimum eigenvalue is tracked and added back to the energies.

## Variables

| Symbol | Description | Units |
|--------|-------------|-------|
| **H** | Magnon Hamiltonian (2N×2N) | eV |
| **g** | Bosonic metric | dimensionless |
| **K** | Cholesky factor of H | √eV |
| ω | Magnon energy | eV |
| **v** | Eigenvector | dimensionless |
| min_eig | Minimum eigenvalue (stability check) | eV |

## Equations

The magnon energies are obtained as:

$$
\omega_n = \text{eigval}_n(\mathbf{K}^\dagger \mathbf{g} \mathbf{K}) + \min(\text{eig}(\mathbf{H}))
$$

where we take only the N positive eigenvalues.

## Implementation

```python
def _magnon_energies(self, kpoints):
    H = self.Hq(kpoints)  # Shape: (nkpt, 2N, 2N)
    n = H.shape[-1] // 2  # N magnetic atoms
    I = np.eye(n)
    
    min_eig = 0.0
    try:
        K = np.linalg.cholesky(H)
    except np.linalg.LinAlgError:
        min_eig = np.min(np.linalg.eigvalsh(H))
        K = np.linalg.cholesky(H - (min_eig - 1e-6) * np.eye(2*n))
    
    g = np.block([[1*I, 0*I], [0*I, -1*I]])
    KH = K.swapaxes(-1, -2).conj()
    energies = np.linalg.eigvalsh(KH @ g @ K)[:, n:] + min_eig
    
    return energies  # Shape: (nkpt, N)
```

## Quality Checks

1. **Goldstone mode**: For ferromagnets, ω(Γ) should be ~0
2. **Positive energies**: All ω > 0 indicates stable ground state
3. **Smooth dispersion**: No sudden jumps in band structure

## Linked Concepts

- [magnon_hamiltonian](magnon_hamiltonian.md): How the Hamiltonian H is constructed
- [magnon_dos](magnon_dos.md): How energies are used for DOS calculation
- [notation](notation.md): Standard variable notations
