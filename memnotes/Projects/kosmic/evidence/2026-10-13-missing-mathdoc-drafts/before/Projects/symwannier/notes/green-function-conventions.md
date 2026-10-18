---
type: reference
status: stable
audience: both
artifact_role: knowledge
---

# Green Function and Liechtenstein Exchange in a Non-Orthogonal AO Basis

## Status: validated

## Scope and notation

$\hat H$ is an abstract one-electron Hamiltonian. Its plane-wave and atomic-orbital
(AO) matrices are different representations:

$$
H_{\mathrm{PW},GG'}=\langle G|\hat H|G'\rangle,
\qquad
H_{\mathrm{AO},ab}=\langle\phi_a|\hat H|\phi_b\rangle.
$$

The plane-wave basis is orthonormal. The AO basis has the positive-definite metric

$$
S_{ab}=\langle\phi_a|\phi_b\rangle.
$$

All AO matrices below are evaluated at one $\mathbf k$; $\mathbf k$ and spin labels
are suppressed until needed.

### Primal and dual AO bases

The dual orbitals are the columns of $\tilde\Phi=\Phi S^{-1}$, where the columns of
$\Phi$ are the primal orbitals:

$$
|\tilde\phi^a\rangle=\sum_b|\phi_b\rangle(S^{-1})^{ba}.
$$

They obey

$$
\langle\tilde\phi^a|\phi_b\rangle=\delta^a_b,
\qquad
\hat I_{\mathrm{AO}}=\sum_a|\phi_a\rangle\langle\tilde\phi^a|
=\sum_a|\tilde\phi^a\rangle\langle\phi_a|.
$$

For an operator $\hat A$, distinguish its covariant, mixed, and contravariant AO
matrices:

$$
A_{ab}=\langle\phi_a|\hat A|\phi_b\rangle,
\qquad
A^a{}_b=(S^{-1}A)^a{}_b,
\qquad
A^{ab}=(S^{-1}AS^{-1})^{ab}.
$$

The physical trace and product cannot be formed by ordinary multiplication of two
covariant matrices. For example,

$$
\operatorname{Tr}_{\mathrm{AO}}(\hat A\hat B)
=\operatorname{tr}\left[S^{-1}A\,S^{-1}B\right].
$$

Equivalently, a lower AO index must contract with an upper (dual) AO index.

## Collinear Liechtenstein kernel

Use TB2J's splitting convention

$$
\Delta_i=H^\uparrow_i-H^\downarrow_i.
$$

With the usual spin-Hamiltonian and contour conventions, TB2J's collinear
Liechtenstein kernel is

$$
\mathcal K_{ij}(z)
=\frac{1}{4\pi}
\operatorname{Tr}\!\left[
\hat\Delta_i\hat G^\uparrow(z)
\hat\Delta_j\hat G^\downarrow(z)
\right].
$$

The real-axis form is

$$
J_{ij}=\operatorname{Im}\int^{E_F}\mathcal K_{ij}(\epsilon+i0^+)\,d\epsilon.
$$

An overall sign or factor of two changes if the spin Hamiltonian or the definition of
$\Delta$ changes; the equations here match TB2J's
`$\Delta=H^\uparrow-H^\downarrow$` and `$1/(4\pi)$` implementation.

For site-local covariant splitting blocks $(\Delta_i)_{ab}$ and the dual Green
blocks $(G^\sigma_{ij})^{ab}$, this trace is exactly

$$
\mathcal K_{ij}(z)
=\frac{1}{4\pi}
(\Delta_i)_{ab}
(G^\uparrow_{ij})^{bc}
(\Delta_j)_{cd}
(G^\downarrow_{ji})^{da}.
$$

In ordinary matrix notation, lower-index $\Delta$ and upper-index $G$ contract
without extra displayed metrics:

$$
\boxed{
\mathcal K_{ij}(z)
=\frac{1}{4\pi}
\operatorname{tr}\!\left[
\Delta_i G^{\uparrow,\mathrm{dual}}_{ij}
\Delta_j G^{\downarrow,\mathrm{dual}}_{ji}
\right].
}
$$

This is the formula implemented by
`Delta_i @ Gij_up @ Delta_j @ Gji_dn`. It is a **primal--dual** contraction, not
an ordinary trace of four covariant matrices.

If only covariant Green matrices are available, the identical expression is

$$
\mathcal K_{ij}(z)
=\frac{1}{4\pi}
\operatorname{tr}\!\left[
S^{-1}\Delta_iS^{-1}G^\uparrow_{\mathrm{cov}}
S^{-1}\Delta_jS^{-1}G^\downarrow_{\mathrm{cov}}
\right].
$$

Here $S$ is the full AO overlap at that $\mathbf k$, not a site-local subblock.
Therefore the conversion must happen before the site blocks are selected and before
the $\mathbf k\to\mathbf R$ Fourier transform.

## SIESTA / native LCAO path

SIESTA supplies covariant $H^\sigma_{\mathrm{AO}}$ and $S$, and solves

$$
H^\sigma_{\mathrm{AO}}V^\sigma
=SV^\sigma\varepsilon^\sigma,
\qquad
(V^\sigma)^\dagger S V^\sigma=I.
$$

The normalized eigenstate is

$$
|\psi^\sigma_n\rangle=\sum_a|\phi_a\rangle V^\sigma_{an}.
$$

Consequently its primal and dual Green matrices are different:

$$
G^{\sigma}_{\mathrm{cov}}
=S V^\sigma D^\sigma (V^\sigma)^\dagger S,
\qquad
D^\sigma_{nn}=\frac{1}{z-\varepsilon^\sigma_n},
$$

$$
G^{\sigma,\mathrm{dual}}
=V^\sigma D^\sigma(V^\sigma)^\dagger.
$$

Using the generalized eigenproblem and completeness
$V^\sigma(V^\sigma)^\dagger=S^{-1}$ gives

$$
\boxed{
(zS-H^\sigma_{\mathrm{AO}})^{-1}
=G^{\sigma,\mathrm{dual}}
=S^{-1}G^\sigma_{\mathrm{cov}}S^{-1}.
}
$$

Thus the native SIESTA inverse is already the **dual--dual Green matrix** needed
by the non-orthogonal Liechtenstein contraction. It must be combined with the
covariant on-site block

$$
(\Delta_i)_{ab}
=\left(H^\uparrow_{\mathrm{AO},0}-H^\downarrow_{\mathrm{AO},0}\right)_{ab},
\qquad a,b\in i.
$$

The native kernel is therefore

$$
\mathcal K^{\mathrm{SIESTA}}_{ij}(z)
=\frac{1}{4\pi}\operatorname{tr}\!\left[
\Delta_i
(zS-H^\uparrow_{\mathrm{AO}})^{-1}_{ij}
\Delta_j
(zS-H^\downarrow_{\mathrm{AO}})^{-1}_{ji}
\right].
$$

Applying $S^{-1}$ a second time to the already dual SIESTA inverse produces
$S^{-1}G^{\mathrm{dual}}S^{-1}$, which is not the representation required by
this formula. The experimental `TB2J_SIESTA_GREEN_MODE=contravariant` switch did
exactly that extra transformation; its multi-zeta divergence is therefore expected
when $S$ has small eigenvalues.

## PAW dual projectors

PAW coefficients such as GPAW's $P_{in}=\langle\tilde p_i|\psi_n\rangle$ are
overlaps with projectors dual to the partial waves. Their spectral sum is therefore
already the dual--dual Green matrix. The absence of an AO overlap matrix in this
path means that no index conversion is needed; it does not mean that the PAW
channels are assumed orthogonal.

## ABINIT plane-wave projection path

ABINIT solves the orthogonal plane-wave problem

$$
H^\sigma_{\mathrm{PW}}|\psi^\sigma_n\rangle
=\varepsilon^\sigma_n|\psi^\sigma_n\rangle,
\qquad
G^\sigma_{\mathrm{PW}}(z)
=\sum_n\frac{|\psi^\sigma_n\rangle\langle\psi^\sigma_n|}
{z-\varepsilon^\sigma_n}.
$$

The stored projection coefficients are overlaps with primal AO orbitals. With
$C_{an}=\langle\phi_a|\psi_n\rangle$, the untransformed spectral sum is

$$
\left(G^\sigma_{\mathrm{proj,cov}}\right)_{ab}
=\sum_n\frac{C_{an}C^*_{bn}}{z-\varepsilon^\sigma_n}
=\langle\phi_a|G^\sigma_{\mathrm{PW}}(z)|\phi_b\rangle.
$$

It has two lower AO indices. Its dual--dual matrix is consequently

$$
\boxed{
G^{\sigma,\mathrm{proj,dual}}
=S^{-1}G^\sigma_{\mathrm{proj,cov}}S^{-1}
=\langle\tilde\phi|G^\sigma_{\mathrm{PW}}(z)|\tilde\phi\rangle.
}
$$

If the projected spin splitting is also supplied as covariant elements,

$$
(\Delta_i)_{ab}
=\langle\phi_a|\hat\Delta_i|\phi_b\rangle,
$$

then the ABINIT kernel has the same primal--dual form:

$$
\mathcal K^{\mathrm{ABINIT}}_{ij}(z)
=\frac{1}{4\pi}\operatorname{tr}\!\left[
\Delta_i
\left(S^{-1}G^\uparrow_{\mathrm{proj,cov}}S^{-1}\right)_{ij}
\Delta_j
\left(S^{-1}G^\downarrow_{\mathrm{proj,cov}}S^{-1}\right)_{ji}
\right].
$$

`ProjectorGreen.get_Gk` forms the covariant spectral sum first and performs this
full-$S(\mathbf k)$ conversion before Fourier transforming and extracting site
blocks. Therefore its default `Sinv @ Gk @ Sinv` is a required index conversion,
not an empirical correction.

### Truncated inverse and Lowdin construction

For an ill-conditioned overlap, TB2J can replace the direct inverse with a
truncated singular-value inverse. Singular modes satisfying

$$
s_i \le r_{\mathrm{cond}}s_{\max}
$$

are removed. A consistent Lowdin construction forms

$$
L=S^{-1/2},\qquad S^{-1}_{\mathrm{trunc}}=LL,
$$

with the same relative cutoff. Transforming both $G$ and $\Delta$ with $L$ is
algebraically equivalent to retaining covariant $\Delta$ and using
$S^{-1}_{\mathrm{trunc}}G_{\mathrm{cov}}S^{-1}_{\mathrm{trunc}}$. Consequently,
the SVD and consistent Lowdin paths must agree at equal cutoff. Applying only one
$L$ to each side of $G$ while leaving $\Delta$ covariant would mix representations
and is not implemented.

An unfiltered 30-pole BiFeO3 first-shell diagnostic at
$r_{\mathrm{cond}}=10^{-3}$ gave no change for UPF, while ion.nc shifted from
-31.7774 to -31.2140 meV and DZP `.orb` shifted from -31.4385 to -30.8960 meV.
These values bypassed NC-PAO shell filtering and must not be compared directly to
the production outputs. With the default charge/moment shell thresholds restored,
SVD at `rcond=0` exactly reproduced the old ion.nc result near -64.44 meV. Thus the
apparent improvement at zero cutoff came from retaining all local-operator shells,
not from changing the overlap inverse. A cutoff sweep and shell-selection choice
must be reported separately.

The complete unfiltered direct-inverse rerun showed that retaining all shells is
not a general cure. It made the BiFeO3 UPF, DZP, and ion.nc first-shell values
cluster near -31 meV, but ill-conditioned DZP bases remained catastrophic for
bccFe (-298391 meV), hcpCo (-2507 meV), FeO (-257 meV), and SrMnO3 (-1111 meV).
These are raw requested results, not validated physical exchange parameters.

Applying SVD truncation with $r_{\mathrm{cond}}=10^{-3}$ to SZ, DZP, and
ion.nc while retaining all operator shells removes most catastrophic values. The
first-shell array becomes: bccFe `16.28/-2.41/-59.91`, hcpCo
`71.95/48.04/50.39`, FeO `22.16/5.63/6.63`, SrMnO3
`-27.26/-23.69/--`, BiFeO3 `-16.32/-30.90/-31.21`, and CrI3
`1.13/9.16/--` meV for SZ/DZP/ion.nc. The remaining bccFe ion.nc anomaly and
basis dependence show that truncation stabilizes the inverse but does not guarantee
basis-independent physics.

A targeted cutoff sweep for bccFe, SrMnO3, and CrI3 found that
$r_{\mathrm{cond}}=10^{-2}$ is substantially more consistent than $10^{-3}$ for
these files: bccFe SZ/DZP/ion.nc gives `16.28/11.34/10.80` meV, SrMnO3 SZ/DZP
gives `-23.71/-22.52` meV, and CrI3 SZ/DZP gives `1.13/2.06` meV. In contrast,
$r_{\mathrm{cond}}=10^{-1}$ is too aggressive: SrMnO3 changes sign to
`39.56/45.37` meV and CrI3 SZ changes sign to `-1.56` meV. The main comparison
array was not changed by this diagnostic sweep.

### Smooth Tikhonov filter

Hard truncation can change retained rank between neighboring k-points. TB2J's
`tikhonov` mode instead applies the smooth spectral function

$$
f_\lambda(s)=\frac{s}{s^2+\lambda^2},
\qquad
S^{-1}_{\mathrm{reg}}=U f_\lambda(s) U^\dagger,
$$

where $\lambda=r_{\mathrm{cond}}s_{\max}$ at each k-point. This approaches the
ordinary inverse for $s\gg\lambda$, smoothly suppresses near-null modes, and has
no rank transition. With `rcond=1e-2`, no shell filtering, direct UPF, and
Tikhonov for SZ/DZP/ion.nc, the six-material first-shell array becomes:

- bccFe: `12.54/16.13/11.42/10.73` meV.
- hcpCo: `52.95/52.74/43.68/52.46` meV.
- FeO: `7.72/9.55/8.74/8.20` meV.
- SrMnO3: `-22.92/-24.05/-20.32/-21.91` meV.
- BiFeO3: `-30.95/-26.04/-27.11/-28.18` meV.
- CrI3: `1.54/0.81/2.24/2.41` meV.

Values in each row are UPF/SZ/DZP/ion.nc. The filter removes the catastrophic
hard-inverse values while preserving continuous dependence on the overlap spectrum.

## Why projected PW and static LCAO Green functions differ

Let $\Phi$ embed the AO basis in the PW Hilbert space and define the orthonormal
columns $X=\Phi S^{-1/2}$, $P=XX^\dagger$, and $Q=I-P$. The ABINIT projected
Green function contains the exact eliminated-space self-energy:

$$
G^{\mathrm{proj,dual}}
=S^{-1/2}
\left[
z-X^\dagger H_{\mathrm{PW}}X
-X^\dagger H_{\mathrm{PW}}Q
\left(z-QH_{\mathrm{PW}}Q\right)^{-1}
QH_{\mathrm{PW}}X
\right]^{-1}
S^{-1/2}.
$$

In contrast, the static projected-Hamiltonian resolvent is

$$
\left(zS-H_{\mathrm{AO}}\right)^{-1}
=S^{-1/2}
\left[z-X^\dagger H_{\mathrm{PW}}X\right]^{-1}
S^{-1/2}.
$$

They agree only if the AO space is invariant under $\hat H_{\mathrm{PW}}$, so that
$QH_{\mathrm{PW}}X=0$. This is a separate issue from the metric conversion:
both methods must use a dual Green matrix in the exchange trace.

## SymPy validation

The derivation was checked with exact SymPy arithmetic.

### Native LCAO identity

For

$$
B=\begin{pmatrix}1&1\\0&1\end{pmatrix},
\quad
S=B^\mathsf TB,
\quad
V=B^{-1},
\quad
\varepsilon=\operatorname{diag}(-2,3),
$$

SymPy verified all of

$$
V^\mathsf TSV=I,
\qquad
HV=SV\varepsilon,
\qquad
(zS-H)^{-1}=VDV^\mathsf T,
\qquad
G_{\mathrm{cov}}=S(zS-H)^{-1}S.
$$

It also verified exactly that the Hilbert-space operator trace equals both

$$
\operatorname{tr}\!\left[
\Delta_iG^{\uparrow,\mathrm{dual}}
\Delta_jG^{\downarrow,\mathrm{dual}}
\right]
$$

and its all-covariant metric form.

### Plane-wave projection identity

For the non-orthogonal two-orbital PW embedding

$$
\Phi=
\begin{pmatrix}
1&0\\
0&1\\
1&1
\end{pmatrix},
$$

with distinct exact $3\times3$ spin Hamiltonians, SymPy verified

$$
\operatorname{Tr}\!\left[
\hat\Delta_iG^\uparrow_{\mathrm{PW}}
\hat\Delta_jG^\downarrow_{\mathrm{PW}}
\right]
=
\operatorname{tr}\!\left[
\Delta_i(S^{-1}G^\uparrow_{\mathrm{proj,cov}}S^{-1})
\Delta_j(S^{-1}G^\downarrow_{\mathrm{proj,cov}}S^{-1})
\right].
$$

At $z=5$ the two sides were exactly $-7/198$; omitting the two $S^{-1}$ factors
gave an exact error of $5299/198$. This validates the metric placement, not a
physical material approximation.

## Consequences for the CrI3 comparison

- Native SIESTA's standard $(zS-H)^{-1}$ is already dual. Do not dress it with
  another $S^{-1}$ pair.
- ABINIT's raw band/projector spectral sum is covariant. Dress it once on both
  sides with the full $S^{-1}(\mathbf k)$ before using the standard TB2J trace.
- The prior statement that the ABINIT transformation was only a partial,
  empirical compensation is incorrect. It is the required primal-to-dual
  conversion when $\Delta$ is held in its covariant AO representation.
- Band-window dependence and the difference between projected PW and native LCAO
  exchange remain physical/numerical completeness questions. They arise from the
  finite band sum, the AO subspace, the self-energy of the eliminated PW space,
  and distinct DFT Hamiltonians—not from ambiguity about the overlap factors.
