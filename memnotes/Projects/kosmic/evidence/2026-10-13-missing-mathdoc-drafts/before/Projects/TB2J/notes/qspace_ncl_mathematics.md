---
artifact_role: knowledge
audience: both
confidence: 0.9
created: 2026-04-05
last_validated: 2026-04-06T12:00:00
validation_procedure: |
  Read exchange_qspace.py (ExchangeNCLQspace) and exchange.py (ExchangeNCL) alongside this note.
  Verify each formula matches the code at the referenced line numbers.
  Run NCL q-space test and compare with real-space NCL results.
validation_test: "TB2J/tests/tests/test_qspace_ncl_vs_realspace.py"
successful_usage_count: 1
usage_stale: false
related_files:
  - TB2J/TB2J/exchange_qspace.py
  - TB2J/TB2J/exchange.py
  - TB2J/TB2J/pauli.py
  - TB2J/TB2J/green.py
related_functions:
  - ExchangeNCLQspace.get_all_A
  - ExchangeNCLQspace.integrate
  - ExchangeNCLQspace.q_to_r
  - ExchangeNCL.get_A_ijR
  - ExchangeNCL.get_all_A_vectorized
  - ExchangeNCL.A_to_Jtensor
  - pauli_block_all
  - pauli_block_sigma_norm
tags: [qspace, exchange-coupling, green-function, non-collinear, pauli-matrices, spinor, fourier-transform, mathematical-derivation]
project: TB2J
status: stable
validated_by: automatic
links_to: ["qspace_exchange_mathematics", "exchange_tensor", "notation"]
type: Project Knowledge
---

# Q-Space Non-Collinear Exchange Coupling: Mathematical Derivation

## Overview

This note derives the q-space formulation of non-collinear (NCL) exchange coupling, generalizing the collinear derivation in [qspace_exchange_mathematics](qspace_exchange_mathematics.md). The NCL formulation uses a single spinor Green's function (2×2 in spin space) and computes the full 4×4 A-tensor $A^{uv}(\mathbf{q})$, from which isotropic exchange $J_\text{iso}$, anisotropic exchange $J_\text{ani}^{\alpha\beta}$, and Dzyaloshinskii-Moriya interaction (DMI) $\mathbf{D}$ are extracted.

## Variables

| Symbol | Description | Code Variable |
|--------|-------------|---------------|
| $G(\mathbf{k}, E)$ | Spinor Green's function at k-point and energy $E$; shape $(2n_\text{orb}, 2n_\text{orb})$ | `self.G.get_Gk(ik, energy)` |
| $G_{ij}(\mathbf{k}, E)$ | Atom-projected spinor Green's function for atoms $i, j$ | `self.GR_atom(Gk, iatom, jatom)` |
| $G^u_{ij}(\mathbf{k}, E)$ | $u$-th Pauli block of atom-projected Green's function; shape $(n_i, n_j)$ | `pauli_block_all(Gij)[u]` |
| $P_i$ | Spin projection operator for atom $i$; shape $(n_i, n_i)$ | `self.get_P_iatom(iatom)` |
| $A^{uv}(\mathbf{R})$ | Real-space A-tensor; shape $(4, 4)$ | `self.A_ijR[(R, i, j)]` |
| $A^{uv}(\mathbf{q})$ | Q-space A-tensor; shape $(4, 4)$ | `self.Aq[iq, i, j]` |
| $u, v$ | Pauli indices: $0 = I, 1 = \sigma_x, 2 = \sigma_y, 3 = \sigma_z$ | — |
| $n_i$ | Number of orbitals for atom $i$ (spinor-reduced) | `self.norb_reduced[iatom]` |

## 1. Starting Point: Real-Space NCL A-Tensor

The non-collinear A-tensor in real space is defined as (see `exchange.py`, lines 442–497):

$$
A^{uv}_{ij}(\mathbf{R}, E) = \frac{1}{\pi} \text{Tr}\left[P_i \cdot G^u_{ij}(\mathbf{R}, E) \cdot P_j \cdot G^v_{ji}(-\mathbf{R}, E)\right]
$$

where:
- $u, v \in \{0, 1, 2, 3\}$ corresponding to Pauli matrices $\{I, \sigma_x, \sigma_y, \sigma_z\}$
- $P_i = \texttt{pauli\_block\_sigma\_norm}(H_i)$ is the spin projection matrix for atom $i$
- $G^u_{ij} = \texttt{pauli\_block\_all}(G_{ij})[u]$ is the $u$-th Pauli block of the atom-projected spinor Green's function
- The trace is over orbital indices

**Code** (`exchange.py`, lines 491–495):
```python
for a in range(4):
    pGp = self.get_P_iatom(iatom) @ Gij_Ixyz[a] @ self.get_P_iatom(jatom)
    for b in range(4):
        AijRab = pGp @ Gji_Ixyz[b]
        tmp[a, b] = np.trace(AijRab) / np.pi
```

### 1.1 Spin Projection Operator $P_i$

For each magnetic atom $i$, the local Hamiltonian $H_i$ (a $2n_i \times 2n_i$ spinor matrix) is decomposed via Pauli matrices:

$$
H_i = H_i^0 \otimes I + H_i^x \otimes \sigma_x + H_i^y \otimes \sigma_y + H_i^z \otimes \sigma_z
$$

The spin projection operator is the normalized vector part:

$$
P_i = \frac{\text{Tr}(H_i^x) \cdot H_i^x + \text{Tr}(H_i^y) \cdot H_i^y + \text{Tr}(H_i^z) \cdot H_i^z}{|\text{Tr}(H_i^x), \text{Tr}(H_i^y), \text{Tr}(H_i^z)|}
$$

This projects onto the dominant spin direction of atom $i$.

**Code** (`pauli.py`, lines 226–237):
```python
def pauli_block_sigma_norm(M):
    MI, Mx, My, Mz = pauli_block_all(M)
    ex, ey, ez = np.trace(Mx), np.trace(My), np.trace(Mz)
    evec = np.array((ex, ey, ez))
    evec = evec / np.linalg.norm(evec)
    return Mx * evec[0] + My * evec[1] + Mz * evec[2]
```

### 1.2 Pauli Block Decomposition

The spinor Green's function $G_{ij}$ (shape $2n_i \times 2n_j$) is decomposed into four blocks:

$$
G^0_{ij} = \frac{G_{ij}^{\uparrow\uparrow} + G_{ij}^{\downarrow\downarrow}}{2} \quad \text{(identity/charge block)}
$$

$$
G^1_{ij} = \frac{G_{ij}^{\uparrow\downarrow} + G_{ij}^{\downarrow\uparrow}}{2} \quad \text{($\sigma_x$ block)}
$$

$$
G^2_{ij} = \frac{G_{ij}^{\uparrow\downarrow} - G_{ij}^{\downarrow\uparrow}}{2} i \quad \text{($\sigma_y$ block)}
$$

$$
G^3_{ij} = \frac{G_{ij}^{\uparrow\uparrow} - G_{ij}^{\downarrow\downarrow}}{2} \quad \text{($\sigma_z$ block)}
$$

where $G^{\alpha\beta}_{ij}$ denotes the spin-$\alpha$ to spin-$\beta$ block (extracted by `G[::2, ::2]`, `G[::2, 1::2]`, etc.).

**Code** (`pauli.py`, lines 146–166):
```python
def pauli_block_all(array):
    A00 = array[..., ::2, ::2]    # up-up block
    A01 = array[..., ::2, 1::2]   # up-dn block
    A10 = array[..., 1::2, ::2]   # dn-up block
    A11 = array[..., 1::2, 1::2]  # dn-dn block
    block[..., 0, :, :] = (A00 + A11) * 0.5       # I component
    block[..., 1, :, :] = (A01 + A10) * 0.5       # sigma_x component
    block[..., 2, :, :] = (A01 - A10) * 0.5j      # sigma_y component
    block[..., 3, :, :] = (A00 - A11) * 0.5       # sigma_z component
    return block
```

The output has shape `(..., 4, n_i, n_j)`.

## 2. Fourier Transform of the Spinor Green's Function

The real-space spinor Green's function is obtained from k-space by the same Fourier transform as the collinear case:

$$
G_{ij}(\mathbf{R}, E) = \sum_{\mathbf{k}} w_k \, G_{ij}(\mathbf{k}, E) \, e^{2\pi i \mathbf{k} \cdot \mathbf{R}}
$$

Since `pauli_block_all` is a linear operation, it commutes with the Fourier transform:

$$
G^u_{ij}(\mathbf{R}, E) = \sum_{\mathbf{k}} w_k \, G^u_{ij}(\mathbf{k}, E) \, e^{2\pi i \mathbf{k} \cdot \mathbf{R}}
$$

This is key — the Pauli decomposition can be done either before or after the Fourier transform.

## 3. Derivation: From Real-Space to Q-Space NCL A-Tensor

### 3.1 Substitution

Starting from the real-space A-tensor:

$$
A^{uv}_{ij}(\mathbf{R}, E) = \frac{1}{\pi} \text{Tr}\left[P_i \cdot G^u_{ij}(\mathbf{R}, E) \cdot P_j \cdot G^v_{ji}(-\mathbf{R}, E)\right]
$$

Substitute the Fourier transforms of both $G^u$ and $G^v$:

$$
A^{uv}_{ij}(\mathbf{R}, E) = \frac{1}{\pi} \text{Tr}\left[P_i \cdot \left(\sum_{\mathbf{k}} w_k \, G^u_{ij}(\mathbf{k}, E) \, e^{2\pi i \mathbf{k} \cdot \mathbf{R}}\right) \cdot P_j \cdot \left(\sum_{\mathbf{k}'} w_{k'} \, G^v_{ji}(\mathbf{k}', E) \, e^{-2\pi i \mathbf{k}' \cdot \mathbf{R}}\right)\right]
$$

Since $P_i$, $P_j$ are independent of $\mathbf{k}$:

$$
A^{uv}_{ij}(\mathbf{R}, E) = \frac{1}{\pi} \sum_{\mathbf{k}} \sum_{\mathbf{k}'} w_k \, w_{k'} \, \text{Tr}\left[P_i \cdot G^u_{ij}(\mathbf{k}, E) \cdot P_j \cdot G^v_{ji}(\mathbf{k}', E)\right] \, e^{2\pi i (\mathbf{k} - \mathbf{k}') \cdot \mathbf{R}}
$$

### 3.2 Change of Variable: $\mathbf{q} = \mathbf{k}' - \mathbf{k}$

Define $\mathbf{q} = \mathbf{k}' - \mathbf{k}$, so $\mathbf{k}' = \mathbf{k} + \mathbf{q}$:

$$
A^{uv}_{ij}(\mathbf{R}, E) = \frac{1}{\pi} \sum_{\mathbf{q}} e^{-2\pi i \mathbf{q} \cdot \mathbf{R}} \sum_{\mathbf{k}} w_k \, w_{k+\mathbf{q}} \, \text{Tr}\left[P_i \cdot G^u_{ij}(\mathbf{k}, E) \cdot P_j \cdot G^v_{ji}(\mathbf{k}+\mathbf{q}, E)\right]
$$

For uniform Monkhorst-Pack weights $w_k = w_{k+\mathbf{q}} = 1/N_k$:

$$
A^{uv}_{ij}(\mathbf{R}, E) = \sum_{\mathbf{q}} e^{-2\pi i \mathbf{q} \cdot \mathbf{R}} \cdot \frac{1}{N_k} \underbrace{\frac{1}{N_k} \sum_{\mathbf{k}} \frac{1}{\pi} \text{Tr}\left[P_i \cdot G^u_{ij}(\mathbf{k}, E) \cdot P_j \cdot G^v_{ji}(\mathbf{k}+\mathbf{q}, E)\right]}_{A^{uv}_{ij}(\mathbf{q}, E)}
$$

### 3.3 The Q-Space NCL A-Tensor

$$
\boxed{A^{uv}_{ij}(\mathbf{q}, E) = \frac{1}{\pi N_k} \sum_{\mathbf{k}} \text{Tr}\left[P_i \cdot G^u_{ij}(\mathbf{k}, E) \cdot P_j \cdot G^v_{ji}(\mathbf{k}+\mathbf{q}, E)\right]}
$$

where $u, v \in \{0, 1, 2, 3\}$.

This is a 4×4 tensor in Pauli space for each $(i, j, \mathbf{q}, E)$, compared to the collinear case which produces a scalar.

### 3.4 Inverse Fourier Transform

The real-space A-tensor is recovered by:

$$
A^{uv}_{ij}(\mathbf{R}) = \frac{1}{N_q} \sum_{\mathbf{q}} A^{uv}_{ij}(\mathbf{q}) \, e^{+2\pi i \mathbf{q} \cdot \mathbf{R}}
$$

> **Note on sign convention**: The forward transform (R→q) uses $e^{-2\pi i \mathbf{q} \cdot \mathbf{R}}$, so the inverse transform (q→R) uses $e^{+2\pi i \mathbf{q} \cdot \mathbf{R}}$. This differs from the collinear `ExchangeCLQspace` convention which uses $e^{-2\pi i \mathbf{q} \cdot \mathbf{R}}$ for both directions — a legacy of its different derivation path. The NCL implementation follows the mathematically correct inverse FT.

Each of the 16 components $(u, v)$ is transformed independently.

## 4. Energy Integration

The energy integration follows the same pattern as the collinear case (see [qspace_exchange_mathematics](qspace_exchange_mathematics.md) §4). For each energy pole $E_n$ with weight $w(E_n)$:

$$
\tilde{A}^{uv}_{ij}(\mathbf{q}) = \sum_n w(E_n) \cdot A^{uv}_{ij}(\mathbf{q}, E_n)
$$

Then the CFR integration factor $-\pi/2$ is applied:

$$
A^{uv}_{ij}(\mathbf{q}) = -\frac{\pi}{2} \cdot \tilde{A}^{uv}_{ij}(\mathbf{q})
$$

Note: The $1/\pi$ factor in the A-tensor definition is already included in `get_all_A()`, so the energy integration pipeline is:

| Step | Factor | Where Applied |
|------|--------|---------------|
| k-summation | $w_k / \pi$ per k-point | `get_all_A`: `kw / np.pi` |
| Energy integration | $w(E_n)$ per pole | `integrate`: `Aq += Aqe_list[ie] * w` |
| CFR factor | $-\pi/2$ | `integrate`: `Aq *= factor` |

## 5. Extracting Exchange Parameters from A-Tensor

After energy integration and q→R Fourier transform, the real-space A-tensor $A^{uv}_{ij}(\mathbf{R})$ is decomposed into physical exchange parameters following `exchange.py` lines 634–693:

### 5.1 Isotropic Heisenberg Exchange

$$
J^{\text{iso}}_{ij}(\mathbf{R}) = \text{Im}\left[A^{00}_{ij}(\mathbf{R}) - A^{11}_{ij}(\mathbf{R}) - A^{22}_{ij}(\mathbf{R}) - A^{33}_{ij}(\mathbf{R})\right]
$$

### 5.2 Anisotropic Symmetric Exchange

$$
J^{\alpha\beta}_{\text{ani}}(\mathbf{R}) = \text{Im}\left[A^{\alpha+1,\beta+1}_{ij}(\mathbf{R}) + A^{\alpha+1,\beta+1}_{ji}(-\mathbf{R})\right], \quad \alpha, \beta \in \{x, y, z\}
$$

Note: The $-R$ term uses $A_{ji}(-\mathbf{R})$, i.e., the A-tensor for the swapped pair at the negative lattice vector.

### 5.3 Dzyaloshinskii-Moriya Interaction

$$
D^\alpha_{ij}(\mathbf{R}) = \text{Re}\left[A^{0,\alpha+1}_{ij}(\mathbf{R}) - A^{\alpha+1,0}_{ij}(\mathbf{R})\right], \quad \alpha \in \{x, y, z\}
$$

There is an alternative DMI expression using the antisymmetric part of the anisotropic tensor:

$$
D^x = \text{Im}[A^{23} - A^{33}], \quad D^y = \text{Im}[A^{31} - A^{13}], \quad D^z = \text{Im}[A^{12} - A^{21}]
$$

Both should give equivalent results (stored as `debug_dict["DMI2"]`).

## 6. Implementation Pipeline

The NCL q-space calculation pipeline:

```
┌────────────────────────────────────────────────────────────────┐
│  Step 1: _prepare()                                             │
│  Set up q-mesh, R vectors, compute P matrices for all atoms     │
│  Compute charges and spinat from density matrix                 │
└───────────────────────────┬────────────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────────────┐
│  Step 2: get_all_A()                                            │
│  For each energy E_n:                                           │
│    Get G(k, E_n) for all k-points (spinor, shape 2norb×2norb)  │
│    For each q-point q:                                          │
│      Find k+q indices                                           │
│      For each magnetic pair (i, j):                             │
│        Gij(k) = project G(k) onto atoms i,j                    │
│        Gji(k+q) = project G(k+q) onto atoms j,i                │
│        Gij_Ixyz = pauli_block_all(Gij(k))   # shape (4, ni, nj)│
│        Gji_Ixyz = pauli_block_all(Gji(k+q)) # shape (4, nj, ni)│
│        For u, v in {0,1,2,3}:                                   │
│          A^uv(q, E_n) += Tr[Pi @ Gij^u(k) @ Pj @ Gji^v(k+q)] │
│                           × kw / π                               │
└───────────────────────────┬────────────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────────────┐
│  Step 3: integrate()                                            │
│  A(q) = (-π/2) × Σ_n w(E_n) × A(q, E_n)                       │
│  A(q) is kept COMPLEX (no premature Im/Re extraction)           │
│  so that downstream A_to_Jtensor() can extract Im[A] correctly  │
└───────────────────────────┬────────────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────────────┐
│  Step 4: q_to_r()                                               │
│  A(R) = (1/N_q) Σ_q A(q) · e^(+2πiq·R)                        │
│  Note: inverse FT uses +2πi (matches forward FT e^(-2πiq·R))   │
│  Apply for all 16 components (u,v) independently                │
└───────────────────────────┬────────────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────────────┐
│  Step 5: A_to_Jtensor()                                         │
│  Extract Jiso, Jani, DMI from A-tensor (inherited from NCL)     │
└────────────────────────────────────────────────────────────────┘
```

## 7. Key Differences from Collinear Q-Space

| Aspect | Collinear (`ExchangeCLQspace`) | Non-Collinear (`ExchangeNCLQspace`) |
|--------|-------------------------------|--------------------------------------|
| Green's function | Separate $G^\uparrow$, $G^\downarrow$ (2 TBGreen objects) | Single spinor $G$ (1 TBGreen, `nbasis = 2norb`) |
| Perturbation | $\Delta_i = (G^\uparrow_0 - G^\downarrow_0)$ scalar matrix | $P_i = \texttt{pauli\_block\_sigma\_norm}(H_i)$ matrix |
| A-term output | Scalar $A(\mathbf{q})$ per $(i,j)$ | 4×4 tensor $A^{uv}(\mathbf{q})$ per $(i,j)$ |
| Energy accumulator | `Jqe_list[ie, iq, i, j]` (scalar) | `Aqe_list[ie, iq, i, j, u, v]` (4×4) |
| Post-integration | Bruno renormalization (K, X terms) | Direct A→J tensor decomposition |
| Output | `exchange_Jdict` (J only) | `exchange_Jdict`, `Jani`, `DMI` (full tensor) |

## 8. Vectorization Strategy

For efficiency, the inner loops can be vectorized:

### 8.1 Batch Pauli Decomposition

For all k-points at once, `pauli_block_all` operates on shape `(nkpts, nbasis, nbasis)`:

```python
Gij_allk = Gk_all[:, idx, :][:, :, jdx]  # (nkpts, 2ni, 2nj)
Gij_pauli = pauli_block_all(Gij_allk)     # (nkpts, 4, ni, nj)
```

### 8.2 Einstein Summation for A-Tensor

The 4×4 A-tensor for all k-points at once:

$$
A^{uv}(\mathbf{q}) = \frac{1}{\pi N_k} \sum_{\mathbf{k}} \text{Tr}\left[(P_i \cdot G^u_{ij}(\mathbf{k})) \cdot (P_j \cdot G^v_{ji}(\mathbf{k}+\mathbf{q}))\right]
$$

In vectorized form:

```python
X = Pi @ Gij_pauli  # (nkpts, 4, ni, nj)
Y = Pj @ Gji_pauli  # (nkpts, 4, nj, ni)
A_uv = np.einsum("kuij,kvji->uv", X[k_indices], Y[kq_indices]) / (np.pi * nkpts)
```

## Conventions

- **Spinor basis**: $[\text{orb}_1^\uparrow, \text{orb}_2^\uparrow, \ldots, \text{orb}_1^\downarrow, \text{orb}_2^\downarrow, \ldots]$ (interleaved up/down)
- **Pauli indexing**: $0=I, 1=\sigma_x, 2=\sigma_y, 3=\sigma_z$
- **Phase factors**: Forward FT (R→q): $e^{-2\pi i \mathbf{q} \cdot \mathbf{R}}$; Inverse FT (q→R): $e^{+2\pi i \mathbf{q} \cdot \mathbf{R}}$
- **Normalization**: $1/N_k$ per k-point weight, $1/N_q$ for q→R transform

## Linked Concepts

- [qspace_exchange_mathematics](qspace_exchange_mathematics.md): Collinear q-space mathematical derivation
- [exchange_tensor](exchange_tensor.md): Decomposition of J into isotropic, DMI, and anisotropic parts
- [notation](notation.md): Standard variable notations used in this note
