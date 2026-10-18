---
artifact_role: knowledge
audience: both
confidence: 0.95
created: 2026-04-05
last_validated: 2026-04-05T19:00:00
validation_procedure: |
  Read exchange_qspace.py and exchangeCL2.py alongside this note.
  Verify each formula matches the code at the referenced line numbers.
  Run test: pytest tests/tests/test_qspace_vs_realspace.py -v
  All 124 pairs should match within machine precision (max rel diff ~5e-10).
validation_test: "TB2J/tests/tests/test_qspace_vs_realspace.py"
successful_usage_count: 1
usage_stale: false
related_files:
  - TB2J/TB2J/exchange_qspace.py
  - TB2J/TB2J/exchangeCL2.py
  - TB2J/TB2J/exchange.py
  - TB2J/TB2J/green.py
  - TB2J/TB2J/mycfr.py
  - TB2J/TB2J/contour.py
related_functions:
  - ExchangeCLQspace.get_all_A
  - ExchangeCLQspace.integrate
  - ExchangeCLQspace.q_to_r
  - ExchangeCLQspace.bruno_renormalize
  - ExchangeCL2.get_all_A
  - ExchangeCL2.calculate_all
  - TBGreen.get_Gk
  - TBGreen.get_GR
  - CFR.integrate_values
tags: [qspace, exchange-coupling, green-function, fourier-transform, mathematical-derivation, energy-integration, bruno-renormalization]
project: TB2J
status: draft
validated_by: automatic
links_to: ["qspace_exchange_analysis", "qspace_exchange_fix_plan", "notation", "exchange_tensor", "magnon_Jq_transform"]
type: Project Knowledge
math_provenance: missing
math_provenance_reason: "qspace_exchange_mathematics.md display math requires one MathDoc marker per equation"
---

# Q-Space Exchange Coupling: Mathematical Derivation

## Overview

This note provides the complete mathematical derivation of the exchange coupling calculation in q-space, as implemented in `exchange_qspace.py`. It derives the q-space formulation from the real-space formulation and proves their equivalence. The q-space approach computes $J(\mathbf{q})$ directly in reciprocal space, then Fourier transforms back to $J(\mathbf{R})$, avoiding the intermediate step of computing real-space Green's functions.

See [qspace_exchange_analysis](qspace_exchange_analysis.md) for the bug analysis and [qspace_exchange_fix_plan](qspace_exchange_fix_plan.md) for the fix plan.

## Variables

The following variables are used throughout this note (see [notation](notation.md) for full definitions):

| Symbol | Description | Code Variable |
|--------|-------------|---------------|
| $J_{ij}(\mathbf{R})$ | Exchange coupling between atoms $i$ and $j$ separated by lattice vector $\mathbf{R}$ | `JJ_list[(R_vec, i, j)]` |
| $J_{ij}(\mathbf{q})$ | Exchange coupling in q-space | `self.Jq[iq, i, j]` |
| $G^{\sigma}(\mathbf{k}, E)$ | Spin-$\sigma$ Green's function at k-point and energy $E$ | `self.get_Gk(ik, energy)` |
| $G^{\sigma}(\mathbf{R}, E)$ | Spin-$\sigma$ real-space Green's function | `self.get_GR(Rpts, energy)` |
| $\Delta_i$ | Spin splitting matrix for magnetic atom $i$ | `self.get_Delta(iatom)` |
| $w_k$ | k-point weight ($= 1/N_k$ for Monkhorst-Pack) | `self.kweights[ik]` |
| $w(E_n)$ | Energy contour weight at pole $n$ | `self.contour.weights[n]` |
| $\mathbf{k}$ | k-point in Brillouin zone | `self.kpts[ik]` |
| $\mathbf{q}$ | q-point (equivalent to k-point grid) | `self.qpts[iq]` |
| $\mathbf{R}$ | Real-space lattice vector | `self.Rlist[iR]` |
| $N_k$ | Total number of k-points | `len(self.kpts)` |
| $N_q$ | Total number of q-points ($= N_k$) | `self.nqpt` |
| $E_F$ | Fermi energy | `self.efermi` |
| $M_i$ | Magnetic moment (z-component) of atom $i$ | `self.spinat[i, 2]` |

## 1. Starting Point: Real-Space Exchange Coupling

The exchange coupling in the real-space formulation is given by the Lichtenstein formula. For each pair of magnetic atoms $(i, j)$ at lattice vector $\mathbf{R}$:

$$
A_{ij}^{\sigma\sigma'}(\mathbf{R}, E) = \sum_{\alpha\beta} \left[\Delta_i\right]_{\alpha\alpha'} \cdot G^{\sigma}_{\alpha'\beta'}(\mathbf{R}, E)_{ij} \cdot \left[\Delta_j\right]_{\beta'\beta} \cdot G^{\sigma'}_{\beta\alpha}(-\mathbf{R}, E)_{ji}
$$

where the Einstein summation convention is used over orbital indices $\alpha, \beta$. In matrix notation:

$$
A_{ij}(\mathbf{R}, E) = \text{Tr}\left[\Delta_i \cdot G^{\uparrow}_{ij}(\mathbf{R}, E) \cdot \Delta_j \cdot G^{\downarrow}_{ji}(-\mathbf{R}, E)\right]
$$

**Code** (`exchangeCL2.py`, lines 136–141):
```python
t = np.einsum("ij, ji-> ij",
    np.matmul(self.get_Delta(iatom), Gij_up),
    np.matmul(self.get_Delta(jatom), Gji_dn))
tmp = np.sum(t)
```

The exchange coupling is obtained by integrating over energy along a contour in the complex plane:

$$
J_{ij}(\mathbf{R}) = -\frac{1}{\pi} \text{Im} \int_C A_{ij}(\mathbf{R}, E) \, dE
$$

In the code, this integral is discretized as:

$$
J_{ij}(\mathbf{R}) = \sum_n w(E_n) \cdot \frac{A_{ij}(\mathbf{R}, E_n)}{4\pi}
$$

followed by multiplication by the CFR integration factor $-\pi/2$ (see Section 4).

## 2. Green's Function: Fourier Transform Between Real and Reciprocal Space

The real-space Green's function is obtained from the k-space Green's function by discrete Fourier transform:

$$
G^{\sigma}_{ij}(\mathbf{R}, E) = \sum_{\mathbf{k}} w_k \, G^{\sigma}_{ij}(\mathbf{k}, E) \, e^{2\pi i \mathbf{k} \cdot \mathbf{R}}
$$

For Monkhorst-Pack grids, $w_k = 1/N_k$ uniformly.

**Code** (`green.py`, lines 467–471):
```python
for ik, kpt in enumerate(self.kpts):
    Gk = self.get_Gk(ik, energy)
    weight = self.kweights[ik]
    phase_k = np.exp(self.k2Rfactor * np.dot(Rvecs, kpt)) * weight
    GR += Gk[None, :, :] * phase_k[:, None, None]
```

The k-space Green's function itself is computed from the eigenvalue decomposition:

$$
G^{\sigma}_{ij}(\mathbf{k}, E) = \sum_n \frac{c_{in}(\mathbf{k}) \, c^{*}_{jn}(\mathbf{k})}{E + E_F - \varepsilon_n(\mathbf{k})}
$$

**Code** (`green.py`, lines 48–54):
```python
return np.einsum(
    "...ib, ...b, ...jb-> ...ij",
    evecs,
    1.0 / (-evals + (energy + efermi)),
    evecs.conj())
```

## 3. Derivation: From Real-Space to Q-Space Formulation

### 3.1 Substitution of the Fourier Transform

Substitute the Fourier transform of both Green's functions into the A-term formula:

$$
A_{ij}(\mathbf{R}, E) = \text{Tr}\left[\Delta_i \cdot \left(\sum_{\mathbf{k}} w_k \, G^{\uparrow}_{ij}(\mathbf{k}, E) \, e^{2\pi i \mathbf{k} \cdot \mathbf{R}}\right) \cdot \Delta_j \cdot \left(\sum_{\mathbf{k}'} w_{k'} \, G^{\downarrow}_{ji}(\mathbf{k}', E) \, e^{2\pi i \mathbf{k}' \cdot (-\mathbf{R})}\right)\right]
$$

Since $\Delta_i$ and $\Delta_j$ are independent of $\mathbf{k}$, they commute with the summation:

$$
A_{ij}(\mathbf{R}, E) = \sum_{\mathbf{k}} \sum_{\mathbf{k}'} w_k \, w_{k'} \, \text{Tr}\left[\Delta_i \cdot G^{\uparrow}_{ij}(\mathbf{k}, E) \cdot \Delta_j \cdot G^{\downarrow}_{ji}(\mathbf{k}', E)\right] \cdot e^{2\pi i (\mathbf{k} - \mathbf{k}') \cdot \mathbf{R}}
$$

### 3.2 Change of Variable: $\mathbf{q} = \mathbf{k}' - \mathbf{k}$

Define $\mathbf{q} = \mathbf{k}' - \mathbf{k}$ (the momentum transfer), so $\mathbf{k}' = \mathbf{k} + \mathbf{q}$:

$$
A_{ij}(\mathbf{R}, E) = \sum_{\mathbf{q}} e^{-2\pi i \mathbf{q} \cdot \mathbf{R}} \sum_{\mathbf{k}} w_k \, w_{k+\mathbf{q}} \, \text{Tr}\left[\Delta_i \cdot G^{\uparrow}_{ij}(\mathbf{k}, E) \cdot \Delta_j \cdot G^{\downarrow}_{ji}(\mathbf{k}+\mathbf{q}, E)\right]
$$

For a Monkhorst-Pack grid where $w_k = w_{k+\mathbf{q}} = 1/N_k$, this simplifies to:

$$
A_{ij}(\mathbf{R}, E) = \sum_{\mathbf{q}} e^{-2\pi i \mathbf{q} \cdot \mathbf{R}} \cdot \frac{1}{N_k} \underbrace{\left[\frac{1}{N_k} \sum_{\mathbf{k}} \text{Tr}\left[\Delta_i \cdot G^{\uparrow}_{ij}(\mathbf{k}, E) \cdot \Delta_j \cdot G^{\downarrow}_{ji}(\mathbf{k}+\mathbf{q}, E)\right]\right]}_{A_{ij}(\mathbf{q}, E)}
$$

### 3.3 The Q-Space A-Term

The quantity in brackets defines the q-space A-term:

$$
\boxed{A_{ij}(\mathbf{q}, E) = \frac{1}{N_k} \sum_{\mathbf{k}} \text{Tr}\left[\Delta_i \cdot G^{\uparrow}_{ij}(\mathbf{k}, E) \cdot \Delta_j \cdot G^{\downarrow}_{ji}(\mathbf{k}+\mathbf{q}, E)\right]}
$$

And the full exchange coupling in q-space is:

$$
J_{ij}(\mathbf{R}) = \frac{1}{N_q} \sum_{\mathbf{q}} J_{ij}(\mathbf{q}) \, e^{-2\pi i \mathbf{q} \cdot \mathbf{R}}
$$

where:

$$
J_{ij}(\mathbf{q}) = -\frac{1}{\pi} \text{Im} \int_C A_{ij}(\mathbf{q}, E) \, dE
$$

**Code** (`exchange_qspace.py`, lines 119–133):
```python
Gij_up_k = self.Gk_atom(Gup[ik], iatom, jatom)
Gji_dn_kq = self.Gk_atom(Gdn[ikq], jatom, iatom)

t = np.einsum("ij, ji-> ij",
    np.matmul(Deltai, Gij_up_k),
    np.matmul(Deltaj, Gji_dn_kq))
A = np.sum(t)

self.Jqe_list[ie, iq, i, j] += A * kw / (4.0 * np.pi)
```

Here `kw = self.kweights[ik] = 1/N_k` for Monkhorst-Pack grids.

### 3.4 Sign Convention

The exchange coupling tensor is obtained by extracting the imaginary part and normalizing by the spin alignment:

$$
J_{ij}(\mathbf{R}) = \frac{\text{Im}\left[J^{\text{raw}}_{ij}(\mathbf{R})\right]}{\text{sign}(\mathbf{S}_i \cdot \mathbf{S}_j)}
$$

**Code** (`exchangeCL2.py`, line 226):
```python
Jij = np.imag(val) / np.sign(np.dot(self.spinat[iatom], self.spinat[jatom]))
```

This ensures that antiferromagnetic couplings (where spins are anti-aligned) have the correct sign convention.

## 4. Energy Integration: Contour Integration with CFR

### 4.1 Complex Energy Contour

The energy integral is evaluated along a contour in the complex energy plane. For the CFR (Complex Fermi-Resolvent) method, the contour consists of Matsubara-like poles:

$$
E_n = \pm \frac{i \, k_B T}{p_n}
$$

where $p_n$ are the eigenvalues of the tridiagonal matrix constructed from the recursion coefficients, and $T$ is the electronic temperature.

### 4.2 CFR Weights

Each pole has a weight:

$$
w(E_n) = \frac{2i}{\beta} R_n
$$

where $\beta = 1/(k_B T)$ and $R_n$ is the residue:

$$
R_n = \frac{1}{4} \frac{|\text{res}_{1,n}|^2}{p_n^2}
$$

**Code** (`mycfr.py`, lines 33, 49–50):
```python
residules = 0.25 * np.abs(residules[0, :]) ** 2 / self.poles**2
# ...
w = 2.0j / self.beta * r
```

### 4.3 Energy Accumulation

For both real-space and q-space, the energy integration accumulates weighted contributions:

$$
\tilde{J}^{(n)}_{ij}(\mathbf{q}) = \sum_{n} w(E_n) \cdot \frac{A_{ij}(\mathbf{q}, E_n)}{4\pi}
$$

**Code** (`exchange_qspace.py`, lines 159–162):
```python
for ie in range(npole):
    w = weights[ie]
    self.Jq += self.Jqe_list[ie] * w
```

### 4.4 CFR Integration Factor

After accumulating all energy contributions, the CFR integration applies a factor of $-\pi/2$:

$$
J_{ij}(\mathbf{q}) = -\frac{\pi}{2} \cdot \tilde{J}_{ij}(\mathbf{q})
$$

This factor arises because the CFR method computes the Matsubara sum (which has a built-in factor from the Fermi function), and the $-\pi/2$ converts it to the standard contour integral form. The factor of 2 accounts for the spin degeneracy of the Fermi function.

**Code** (`mycfr.py`, lines 82–84):
```python
ret *= -np.pi / 2
```

The code computes this factor indirectly for compatibility with the general Contour interface:

**Code** (`exchange_qspace.py`, lines 165–167):
```python
dummy = np.zeros(npole)
dummy[0] = 1.0
factor = self.contour.integrate_values(dummy) / weights[0]
```

This evaluates to `(-π/2 × weights[0]) / weights[0] = -π/2`.

### 4.5 Complete Energy Integration Formula

Combining all factors:

$$
\boxed{J_{ij}(\mathbf{q}) = \text{Im}\left[-\frac{\pi}{2} \sum_{n} w(E_n) \cdot \frac{1}{4\pi} \sum_{\mathbf{k}} w_k \, \text{Tr}\left[\Delta_i \cdot G^{\uparrow}_{ij}(\mathbf{k}, E_n) \cdot \Delta_j \cdot G^{\downarrow}_{ji}(\mathbf{k}+\mathbf{q}, E_n)\right]\right]}
$$

The factors simplify: $-\pi/2 \times 1/(4\pi) = -1/8$. However, in the code these are applied in separate steps for clarity and compatibility with the contour interface.

## 5. Inverse Fourier Transform: Q-Space to Real-Space

After obtaining $J_{ij}(\mathbf{q})$ for all q-points, the real-space exchange coupling is recovered by inverse Fourier transform:

$$
J_{ij}(\mathbf{R}) = \frac{1}{N_q} \sum_{\mathbf{q}} \text{Re}\left[J_{ij}(\mathbf{q}) \cdot e^{-2\pi i \mathbf{q} \cdot \mathbf{R}}\right]
$$

The real part is taken because $J_{ij}(\mathbf{R})$ is a physical observable and must be real.

**Code** (`exchange_qspace.py`, lines 194–201):
```python
for iR, R in enumerate(self.Rlist):
    for iq, q in enumerate(self.qpts):
        phase = np.exp(-2.0j * np.pi * (R @ q))
        self.JR[iR] += np.real(self.Jq[iq] * phase) / self.nqpt
```

### 5.1 Normalization: Why $1/N_q$ (Not $1/N_q^2$)

The k-weight $w_k = 1/N_k$ is already applied inside `get_all_A` during the k-summation (see the `kw` factor in line 133). The only remaining normalization for the q→R transform is $1/N_q$. This is a common source of bugs — a double division by $N_q$ was one of the original bugs (Bug 5, see [qspace_exchange_analysis](qspace_exchange_analysis.md)).

The normalization chain is:

| Step | Factor | Where Applied |
|------|--------|---------------|
| k-summation | $w_k = 1/N_k$ per k-point | `get_all_A`: `kw = self.kweights[ik]` |
| Energy integration | $w(E_n)$ per pole | `integrate`: `self.Jq += self.Jqe_list[ie] * w` |
| CFR factor | $-\pi/2$ | `integrate`: `self.Jq *= factor` |
| q→R transform | $1/N_q$ per q-point | `q_to_r`: `/ self.nqpt` |

## 6. Bruno Renormalization

The Bruno renormalization corrects the exchange coupling for the finite magnetic moment. It is implemented only in the q-space formulation.

### 6.1 K and X Terms

In addition to the J-term (A-term), two auxiliary quantities are computed:

**K-term** (first-order correction):

$$
K_{ij}(\mathbf{q}, E) = -\frac{1}{2\pi N_k} \sum_{\mathbf{k}} \text{Tr}\left[G^{\uparrow}_{ij}(\mathbf{k}, E) \cdot \Delta_j \cdot G^{\downarrow}_{ji}(\mathbf{k}+\mathbf{q}, E)\right]
$$

**Code** (`exchange_qspace.py`, lines 126–128):
```python
K = Gij_up_k @ Deltaj @ Gji_dn_kq
self.Kqe_list[ie, iq, i, j] -= np.trace(K) * kw / (2.0 * np.pi)
```

**X-term** (normalization matrix):

$$
X_{ij}(\mathbf{q}, E) = \frac{2}{\pi N_k} \sum_{\mathbf{k}} \text{Tr}\left[G^{\uparrow}_{ij}(\mathbf{k}, E) \cdot G^{\downarrow}_{ji}(\mathbf{k}+\mathbf{q}, E)\right]
$$

**Code** (`exchange_qspace.py`, lines 130–132):
```python
X = Gij_up_k @ Gji_dn_kq
self.Xqe_list[ie, iq, i, j] += np.trace(X) * kw * (2.0 / np.pi)
```

Both K and X undergo the same energy integration as J (weighted summation over energy poles, multiplied by the CFR factor $-\pi/2$, then imaginary part extracted).

### 6.2 Bruno Correction Formula

After energy integration, the renormalized exchange coupling is:

$$
\boxed{J^{\text{norm}}_{ij}(\mathbf{q}) = J_{ij}(\mathbf{q}) + \frac{1}{2}\left(M - K_{ij}^T(\mathbf{q})\right) \cdot X_{ij}^{-1}(\mathbf{q}) \cdot \left(M - K_{ij}(\mathbf{q})\right)}
$$

where $M = \text{diag}(S^z_1, S^z_2, \ldots)$ is the diagonal matrix of z-components of the magnetic moments.

**Code** (`exchange_qspace.py`, lines 179–185):
```python
def bruno_renormalize(self):
    M = np.diag(self.spinat[self.ind_mag_atoms, 2])
    for iq in range(self.nqpt):
        self.Jnorm_q[iq] = self.Jq[iq] + 0.5 * (
            M - self.Kq[iq].T
        ) @ np.linalg.inv(self.Xq[iq]) @ (M - self.Kq[iq])
```

## 7. Equivalence Proof: Q-Space = Real-Space

### 7.1 Formal Argument

The equivalence of the two formulations follows from the convolution theorem for discrete Fourier transforms. Starting from the real-space formula:

$$
J_{ij}(\mathbf{R}) = -\frac{1}{\pi}\text{Im} \int_C dE \; \text{Tr}\left[\Delta_i \cdot G^{\uparrow}_{ij}(\mathbf{R}, E) \cdot \Delta_j \cdot G^{\downarrow}_{ji}(-\mathbf{R}, E)\right]
$$

Substituting the Fourier transforms of both Green's functions:

$$
G^{\uparrow}_{ij}(\mathbf{R}, E) = \frac{1}{N_k}\sum_{\mathbf{k}} G^{\uparrow}_{ij}(\mathbf{k}, E) \, e^{2\pi i \mathbf{k} \cdot \mathbf{R}}
$$

$$
G^{\downarrow}_{ji}(-\mathbf{R}, E) = \frac{1}{N_k}\sum_{\mathbf{k}'} G^{\downarrow}_{ji}(\mathbf{k}', E) \, e^{-2\pi i \mathbf{k}' \cdot \mathbf{R}}
$$

The product of the two phase factors gives $e^{2\pi i (\mathbf{k} - \mathbf{k}') \cdot \mathbf{R}}$. Summing over $\mathbf{R}$ with $e^{2\pi i \mathbf{q} \cdot \mathbf{R}}$ (inverse DFT) and using the orthogonality relation:

$$
\frac{1}{N_q}\sum_{\mathbf{R}} e^{2\pi i (\mathbf{k} - \mathbf{k}' + \mathbf{q}) \cdot \mathbf{R}} = \delta_{\mathbf{k}' - \mathbf{k}, \mathbf{q}}
$$

This collapses the double sum over $\mathbf{k}$ and $\mathbf{k}'$ to a single sum, yielding the q-space formula with $\mathbf{k}' = \mathbf{k} + \mathbf{q}$.

### 7.2 Practical Verification

The equivalence was verified numerically on the SrMnO₃ test system:

- **System**: SrMnO₃ with Wannier90 orbitals
- **k-mesh**: $5 \times 5 \times 5$
- **Energy poles**: 10 (CFR contour)
- **Fermi energy**: 6.15 eV
- **Result**: All 124 exchange coupling pairs match
- **Maximum relative difference**: $5.66 \times 10^{-10}$ (machine precision)
- **Dominant coupling**: Nearest-neighbor Mn-Mn at $(0,0,1)$ = $-6.114$ meV (antiferromagnetic)

**Test** (`tests/tests/test_qspace_vs_realspace.py`):
```bash
pytest tests/tests/test_qspace_vs_realspace.py -v
```

## 8. Implementation Pipeline

The complete q-space calculation pipeline in `exchange_qspace.py`:

```
┌──────────────────────────────────────────────────────┐
│  Step 1: _prepare()                                   │
│  Set up k/q grids, R vectors, contour, Delta matrices │
└──────────────────────┬───────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────┐
│  Step 2: get_all_A()                                  │
│  For each energy E_n and q-point q:                   │
│    For each k-point k:                                │
│      A(q, E_n) += Tr[Δ_i·G↑(k, E_n)·Δ_j·G↓(k+q, E_n)]│
│                       × w_k / (4π)                    │
│    Similarly accumulate K and X terms                  │
└──────────────────────┬───────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────┐
│  Step 3: integrate()                                  │
│  J(q) = Im[(-π/2) × Σ_n w(E_n) × A(q, E_n)]         │
│  K(q), X(q) computed analogously                      │
└──────────────────────┬───────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────┐
│  Step 4: bruno_renormalize()                          │
│  J_norm(q) = J(q) + ½(M - K(q)ᵀ)·X(q)⁻¹·(M - K(q)) │
└──────────────────────┬───────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────┐
│  Step 5: q_to_r()                                     │
│  J(R) = (1/N_q) Σ_q Re[J_norm(q) · e^(-2πiq·R)]     │
└──────────────────────┬───────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────┐
│  Step 6: get_Jdict()                                  │
│  Apply sign convention: J = Im[val] / sign(S_i · S_j) │
└──────────────────────────────────────────────────────┘
```

## Conventions

- **Phase factors**: `k2Rfactor = 2π` for k→R transform, `R2kfactor = -2π` for R→k. The negative sign ensures consistency with the Fourier transform convention.
- **Normalization**: Each k-point contributes weight $1/N_k$. The q→R transform divides by $N_q$. There is no double counting.
- **Spin convention**: Spin-up Green's function uses the full Hamiltonian; spin-down uses $-\mathbf{R}$ (equivalently, $\mathbf{k} + \mathbf{q}$ in q-space).
- **Energy contour**: CFR poles are on the imaginary axis. The imaginary part of the accumulated result gives the physical exchange coupling.

## Linked Concepts

- [qspace_exchange_analysis](qspace_exchange_analysis.md): Bug analysis of the original q-space implementation
- [qspace_exchange_fix_plan](qspace_exchange_fix_plan.md): Fix plan and verification results
- [exchange_tensor](exchange_tensor.md): Decomposition of J into isotropic, DMI, and anisotropic parts
- [magnon_Jq_transform](magnon_Jq_transform.md): Fourier transform of exchange tensors for magnon calculations
- [notation](notation.md): Standard variable notations used in this note
