---
type: reference
status: draft
audience: both
artifact_role: knowledge
math_provenance: missing
math_provenance_reason: "paw-basis-choices-lkag.md display math requires one MathDoc marker per equation"
---

# PAW Basis Choices for the LKAG Exchange Trace: Partial Waves vs Projectors

**Status:** self-contained derivation report.
**Companion:** [`PAW_LKAG_derivation.py`](../../mypapers/TB2J_projector/derivations/PAW_LKAG_derivation.py)
(SymPy-verified identities [A]–[E]).
**Prerequisite:** the existing [PAW LKAG derivation](../../mypapers/TB2J_projector/derivations/PAW_LKAG_derivation.md).

## Abstract

The Liechtenstein–Katsnelson–Antropov–Gubanov (LKAG) magnetic-force-theorem
exchange trace can be evaluated in the PAW representation using either the PAW
**partial waves** $\tilde\phi_i$ or the PAW **projector functions** $\tilde p_i$
as the local basis for projection. This report derives both forms, proves their
equivalence, and identifies the practical implications for each DFT code path
(GPAW, ABINIT WFK+Vxc, ABINIT NC-PAO).

The central result: because of the PAW duality $\langle\tilde p_i \vert \tilde\phi_j\rangle = \delta_{ij}$, the exchange field $\Delta_{ij}$ is the **same
matrix** in both bases — the only difference is whether the Green matrix
requires $S^{-1}$ dualisation (partial-wave/primal coefficients) or not
(projector/dual coefficients).

---

## 1. PAW setup

### 1.1 PAW transformation

$$
|\psi\rangle = \mathcal T |\tilde\psi\rangle, \qquad
\mathcal T = 1 + \sum_{a,i} (|\phi_i^a\rangle - |\tilde\phi_i^a\rangle)\langle\tilde p_i^a|
$$

with duality inside each augmentation sphere:

$$
\langle \tilde p_i^a \vert \tilde\phi_j^a \rangle = \delta_{ij}.
$$

### 1.2 Overlap and transformed operators

$$
S = \mathcal T^\dagger \mathcal T, \qquad \tilde H = \mathcal T^\dagger \hat H \mathcal T.
$$

The PAW-transformed operator decomposes into smooth + one-center:

$$
\tilde A = \hat A\big|_{\text{smooth}} + \sum_a \sum_{ij} |\tilde p_i^a\rangle \Delta A_{ij}^a \langle\tilde p_j^a|,
$$

$$
\Delta A_{ij}^a = \langle\phi_i^a \vert \hat A \vert \phi_j^a\rangle_{\Omega_a} - \langle\tilde\phi_i^a \vert \hat A \vert \tilde\phi_j^a\rangle_{\Omega_a}.
$$

### 1.3 The two local basis sets

Inside each augmentation sphere, the pseudo wave function has the expansion:

$$
|\tilde\psi\rangle\big|_{\Omega_a} = \sum_i |\tilde\phi_i^a\rangle \underbrace{\langle\tilde p_i^a \vert \tilde\psi\rangle}_{P_i^a} = \sum_i |\tilde\phi_i^a\rangle P_i^a.
$$

This defines **two equivalent local bases**:

| Basis | Functions | Overlap with $\tilde\psi_n$ | Name |
|---|---|---|---|
| **Partial waves** $\tilde\phi_i$ | Smooth partial waves from PAW-XML | $C_{ni}^a = \langle\tilde\phi_i^a \vert \tilde\psi_n\rangle$ | Primal (covariant) |
| **Projectors** $\tilde p_i$ | PAW projector functions | $P_{ni}^a = \langle\tilde p_i^a \vert \tilde\psi_n\rangle$ | Dual |

They are related by the on-site overlap:

$$
C_{ni}^a = \sum_j \langle\tilde\phi_i^a \vert \tilde\phi_j^a\rangle \langle\tilde p_j^a \vert \tilde\psi_n\rangle = \sum_j S_{ij}^a P_{nj}^a = (S^a P_n^a)_i,
$$

where $S_{ij}^a = \langle\tilde\phi_i^a \vert \tilde\phi_j^a\rangle$ is the on-site
pseudo partial-wave overlap. Equivalently $P_n^a = (S^a)^{-1} C_n^a$.

---

## 2. The exchange field $\Delta_{ij}$

The local exchange field at site $a$ is the spin difference of the XC potential:

$$
\hat\Delta_a = V_{xc}^\uparrow - V_{xc}^\downarrow.
$$

Its one-center PAW matrix element is:

$$
\boxed{\Delta_{ij}^a = \langle\phi_i^a \vert \hat\Delta_a \vert \phi_j^a\rangle_{\Omega_a} - \langle\tilde\phi_i^a \vert \hat\Delta_a \vert \tilde\phi_j^a\rangle_{\Omega_a}}
$$

**This is the same matrix regardless of which basis is used for projection.**
The indices $i,j$ label partial-wave channels (equivalently projector channels,
via the 1:1 duality mapping). The matrix $\Delta_{ij}^a$ is what ABINIT outputs
as `paw_ij%dijxc` (XC contribution to Dij, spin-differenced) or `paw_ij%dij`
(total Dij, spin-differenced).

### 2.1 If only the smooth XC is available (prtvxc route)

If the one-center correction is not available, one can approximate:

$$
\Delta_{ij}^a \approx \langle\tilde p_i^a \vert \Delta V_{xc}^{\text{FFT}} \vert \tilde p_j^a\rangle,
$$

where $\Delta V_{xc}^{\text{FFT}}$ is the spin-difference of the smooth FFT-grid
XC potential. This **misses the AE–pseudo XC residual** inside the augmentation
sphere — the approximation that motivates the full one-center reconstruction
(Phase B in the original PRD). Using the `pawprt` total Dij avoids this
approximation entirely.

---

## 3. The Green matrix: dual vs primal

### 3.1 Projector (dual) coefficients

Using $P_{ni}^a = \langle\tilde p_i^a \vert \tilde\psi_n\rangle$:

$$
[G_{\text{dual}}^{\sigma}]_{ij}^{ab} = \sum_n \frac{P_{ni}^{a*} P_{nj}^b}{z - \epsilon_{n\sigma}} = \langle\tilde p_i^a \vert (zS - \tilde H^\sigma)^{-1} \vert \tilde p_j^b \rangle.
$$

This is the **dual Green matrix** — it equals the PAW resolvent directly, with
**no additional $S^{-1}$** needed. `[D, SymPy-verified]`

### 3.2 Partial-wave (primal) coefficients

Using $C_{ni}^a = \langle\tilde\phi_i^a \vert \tilde\psi_n\rangle = (S^a P_n^a)_i$:

$$
[G_{\text{cov}}^{\sigma}]_{ij}^{ab} = \sum_n \frac{C_{ni}^{a*} C_{nj}^b}{z - \epsilon_{n\sigma}} = [S^a \, G_{\text{dual}}^{\sigma} \, S^b]_{ij}^{ab}.
$$

This is the **covariant Green matrix** — it equals $S \, G_{\text{dual}} \, S$,
and must be **dualised** before use in the trace:

$$
G_{\text{dual}} = (S^a)^{-1} \, G_{\text{cov}}^{\sigma} \, (S^b)^{-1}.
$$

`[D, SymPy-verified]`

### 3.3 Equivalence

Both routes give the same $G_{\text{dual}}$; the partial-wave route just requires
the extra $S^{-1}$ step. The overhead is negligible for the on-site blocks
($S^a$ is small: $n_{\text{channels}} \times n_{\text{channels}}$), but requires
the overlap matrix $S_{ij}^a$ to be known.

---

## 4. The LKAG trace in each basis

### 4.1 The exact PAW LKAG trace `[C, SymPy-verified]`

$$
J_{ij} = -\frac{1}{4\pi} \int^{E_F} dE \; \text{Im} \; \text{Tr}[\tilde\Delta_i (ES - \tilde H^\uparrow)^{-1} \tilde\Delta_j (ES - \tilde H^\downarrow)^{-1}]
$$

### 4.2 Projector-basis contraction (Option A — dual)

Using dual Green matrix directly:

$$
\boxed{J_{ij} = -\frac{1}{4\pi} \int^{E_F} dE \; \text{Im} \sum_{\alpha\beta\gamma\delta} \Delta_{\alpha\beta}^i [G_{\text{dual}}^\uparrow]^{\beta\gamma} \Delta_{\gamma\delta}^j [G_{\text{dual}}^\downarrow]^{\delta\alpha}}
$$

**No $S^{-1}$ needed.** Each contraction pairs a partial-wave index (from
$\Delta$) with a projector index (from $G_{\text{dual}}$), and by duality
$\langle\tilde p_i \vert \tilde\phi_j\rangle = \delta_{ij}$ this is a plain
matrix product.

### 4.3 Partial-wave-basis contraction (Option B — primal)

If the Green matrix is built from partial-wave overlaps $C_{ni}$:

$$
J_{ij} = -\frac{1}{4\pi} \int^{E_F} dE \; \text{Im} \sum_{\alpha\beta\gamma\delta} \Delta_{\alpha\beta}^i [(S^i)^{-1} G_{\text{cov}}^\uparrow (S^j)^{-1}]^{\beta\gamma} \Delta_{\gamma\delta}^j [(S^j)^{-1} G_{\text{cov}}^\downarrow (S^i)^{-1}]^{\delta\alpha}
$$

**Requires $S^{-1}$ dualisation** at each site pair. The result is identical to
Option A (they are the same contraction, just with the dualisation done
explicitly).

### 4.4 Why the duality makes $\Delta$ basis-independent

The exchange field $\Delta_{ij}^a$ has two partial-wave indices. The Green
matrix $[G_{\text{dual}}]_{ij}$ has two projector indices. In the trace
contraction, each pair of indices is summed:

$$
\Delta_{\alpha\beta} \cdot G^{\beta\gamma}
$$

Here $\beta$ is a partial-wave index from $\Delta$ and a projector index from
$G$. Because $\langle\tilde p_\beta \vert \tilde\phi_\beta\rangle = \delta_{\beta\beta}$
(Kronecker delta), this is an ordinary matrix product. No overlap matrix
appears — the duality is what makes it work.

If we used $G_{\text{cov}}$ (partial-wave indices), the contraction
$\Delta_{\alpha\beta} G_{\text{cov}}^{\beta\gamma}$ would pair two partial-wave
indices, which is **not** a simple matrix product — it would need the overlap
$S_{\beta\beta'}$ to connect them. The $S^{-1}$ dualisation in Section 4.3 is
precisely what converts $G_{\text{cov}}$ back to $G_{\text{dual}}$ to restore
the mixed covariant-dual contraction.

---

## 5. Practical comparison

### 5.1 What each DFT code provides

| Code | Spectral coefficients | Type | $\Delta$ source | Dualisation |
|---|---|---|---|---|
| **GPAW** | $P_{ni} = \langle\tilde p_i \vert \tilde\psi_n\rangle$ | Dual | `dH_asp` (onsite $\Delta H_{xc}$) | None |
| **ABINIT pawprt** | $P_{ni}$ (recomputed from WFK) | Dual | Total Dij spin-diff | None |
| **ABINIT savetb2j** | $P_{ni}$ (from cprj) | Dual | `delta_total` / `dijxc` | None |
| **ABINIT NC-PAO** | $C_{ni} = \langle\varphi_i \vert \psi_n\rangle$ | Primal | Projected $\Delta V_{xc}$ | $S^{-1} G S^{-1}$ |

### 5.2 Basis choice for the ABINIT WFK+Vxc route

The WFK+Vxc route projects WFK plane-wave coefficients onto PAW functions. Two
options:

**Option A: Project Fourier-transformed $\tilde p_i$ onto $\tilde\psi_n$** → dual coefficients → no dualisation.

$$
P_{ni}^a = \sum_G \tilde p_i^{a*}(\mathbf k + \mathbf G) \cdot c_{nk}(\mathbf G)
$$

where $\tilde p_i^a(\mathbf k + \mathbf G) = \frac{4\pi}{\sqrt\Omega} f_i(|\mathbf k + \mathbf G|) Y_{lm}(\widehat{\mathbf k + \mathbf G}) e^{-i(\mathbf k + \mathbf G)\cdot \mathbf x_a}$

and $f_i(q) = \int \tilde p_i(r) j_l(2\pi q r) r^2 dr$ is the radial Fourier transform of the projector.

**Option B: Project Fourier-transformed $\tilde\phi_i$ onto $\tilde\psi_n$** → primal coefficients → needs $S^{-1}$.

$$
C_{ni}^a = \sum_G \tilde\phi_i^{a*}(\mathbf k + \mathbf G) \cdot c_{nk}(\mathbf G)
$$

### 5.3 Recommendation

**Use Option A (projector basis).** Reasons:

1. **No $S^{-1}$ needed** — the Green matrix is the dual resolvent directly.
2. **Matches GPAW** — the only production PAW exchange path uses dual coefficients.
3. **Matches `savetb2j`** — ABINIT's cprj are projector overlaps.
4. **$\Delta$ is the same** — the pawprt Dij is basis-independent (partial-wave = projector indices via duality).
5. **Less code** — no overlap matrix construction or inversion needed.

Option B would only be preferred if the partial-wave Fourier transforms are
significantly cheaper than the projector transforms — which they are not
(both are radial functions with the same $l$-structure).

---

## 6. The complete exchange pipeline (Option A)

For the ABINIT WFK+pawprt route:

1. **Read PAW-XML** via `liblsp.read_pseudopotential` → get $\tilde p_i$, $\phi_i$, $\tilde\phi_i$.
2. **Compute $s_{ij}$** via `liblsp.augmentation` → on-site overlap correction (for metadata only, not needed for dual Green).
3. **Fourier-transform $\tilde p_i$** → $f_i(q) = \int \tilde p_i(r) j_l(qr) r^2 dr$.
4. **Project WFK** → $P_{ni}^a = \langle\tilde p_i^a \vert \tilde\psi_n\rangle$ (dual coefficients).
5. **Build dual Green** → $G_{\text{dual},ij}^{\sigma,ab}(E) = \sum_n P_{ni}^{a*} P_{nj}^b / (E - \epsilon_{n\sigma})$.
6. **Parse pawprt Dij** → $\Delta_{ij}^a = D_{ij}^{a,\uparrow} - D_{ij}^{a,\downarrow}$ (complete spin-splitting).
7. **LKAG trace** → $J_{ij} = -\frac{1}{4\pi} \int^{E_F} \text{Im}[\Delta^i G_{\text{dual}}^\uparrow \Delta^j G_{\text{dual}}^\downarrow] dE$.
8. **No $S^{-1}$** — the contraction is plain matrix multiplication.

---

## 7. Summary

| Question | Answer |
|---|---|
| Are the two basis choices equivalent? | Yes — related by $S$; give the same $J_{ij}$. |
| Does $\Delta_{ij}$ depend on the basis? | No — same matrix via duality $\langle\tilde p_i \vert \tilde\phi_j\rangle = \delta_{ij}$. |
| Does $G$ depend on the basis? | Yes — partial-wave overlaps give $G_{\text{cov}} = S G_{\text{dual}} S$; need $S^{-1}$ dualisation. |
| Which to use for ABINIT WFK+Vxc? | **Projectors** — dual coefficients, no $S^{-1}$, matches GPAW/savetb2j. |
| What about the NC-PAO route? | Uses primal coefficients → needs $S^{-1}(\mathbf k) G S^{-1}(\mathbf k)$. This is the existing abinao path. |
