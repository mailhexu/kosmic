---
artifact_role: knowledge
audience: both
confidence: 0.9
created: 2026-09-03
last_validated: 2026-09-03
validation_procedure: "Executable sympy/mpmath asserts (dps=40): FLL->Dudarev reduction exact; strain projector first/second jets exact vs symbolic differentiation; Dudarev trace identities exact; exact psi2-free n-decomposition (2e-8); self-consistent 2DTE assembly identity vs finite differences (3.9e-11 / 1.3e-9). Machine verdicts cross-linked from nc-dftu-si-collinear-fd-oracle-report.md (stories 521/522)."
project: abinit
status: draft
validated_by: measurement
tags: [nc_dftu, dudarev, dfpt, sternheimer, 2n+1, 2dte, ddb, phonon, elastic, born, dielectric, epic-033]
type: Project Knowledge
math_provenance: missing
math_provenance_reason: "nc-dftu-dfpt-equations-and-code.md display math requires one MathDoc marker per equation"
---

# NC DFT+U DFPT: derivation chain and code map (epic-033)

Theory-to-source report for the norm-conserving (NC) DFT+U DFPT
implementation in `abinit_dev_clean` (branch `ProjWannPAO` @ `a3c96045a1`
plus the uncommitted NC DFT+U response changes in
`src/66_nc_dftu/m_nc_dftu.F90`, `src/66_nc_dftu/m_nc_dftu_data.F90`,
`src/66_wfs/m_nc_dftu_hamiltonian.F90`, `src/72_response/m_dfpt_scfcv.F90`,
`src/72_response/m_dfpt_vtorho.F90`, with integration touches in
`m_dfpt_nstwf.F90`, `m_dfpt_cgwf.F90`, `m_dfpt_looppert.F90`).

Every load-bearing derived formula below was derived/checked symbolically
(sympy exact, mpmath dps=40 for the numerical toys); the assert outcomes are
recorded in §8 and the reproducible session in §9. Statements about source
behavior carry file/line anchors from the working tree.

---

## 0. Introduction: the DFPT loop, the Sternheimer equation, the ABINIT design

### 0.1 What is being computed

DFPT delivers second-order total-energy derivatives

$$E^{\lambda\mu} \;=\; \frac{\partial^2 E_{\rm tot}}{\partial\lambda\,\partial\mu}$$

for perturbations $\lambda,\mu$ drawn from: atomic displacements
$u_{\kappa\alpha}$ (force constants → phonons at any q of the interpolation
mesh), homogeneous strains $\eta_\alpha$ (elastic tensors), the electric
field $E_\alpha$ / ddk (dielectric tensor, Born effective charges, and the
$q\to 0$ head of the force constants). All channels land in one object —
the second-order energy matrix $d2nl$, $d2lo$ — which is written to the DDB,
merged (`mrgddb`), and analyzed (`anaddb`).

The +U extension means $E_{\rm tot}$ contains a Hubbard correction
$E_U[n]$ whose *variational variables* — the PAO occupation matrix $n$ —
depend on the perturbation both through the wavefunctions *and* through the
projectors themselves. That is the one structural novelty vs ordinary DFPT:
the projector basis is perturbation-dependent.

### 0.2 The DFPT loop

A response calculation is three nested loops:

1. **Ground state.** Solve the usual KS+U SCF. Output: $\psi^0_{n\mathbf k}$,
   $\varepsilon^0_{n\mathbf k}$, and for +U the occupation matrix
   $n^0$ and the Hubbard potential matrix $V^0_U$ (site-local, one matrix per
   atom per spin channel).
2. **Per perturbation** $(\mathbf q; \mu = (\mathrm{idir},\mathrm{ipert}))$:
   a self-consistent **response SCF** (in ABINIT: `dfpt_looppert` →
   `dfpt_scfcv` → `dfpt_vtorho`). Each iteration:
   - build the first-order Hamiltonian $H^1$ (the "source") at each response
     k-point, including the *induced* Hubbard potential $V^1_U = -U\,(n^1)^T$
     from the previous iteration;
   - solve the **Sternheimer equation** for $\psi^1_{n\mathbf k}$ (CG in
     `m_dfpt_cgwf`);
   - rebuild the first-order density $\rho^1$ from $\psi^1$ **and** the
     first-order occupation matrix $n^1$ from $\psi^1$ *and* the first-order
     projectors (`compute_nc_dftu_response_from_wfs`); update $V^1_U$; feed
     back.
3. **Second-order assembly (2n+1 theorem).** Once all needed perturbations
   converged, $E^{\lambda\mu}$ is assembled **from $\psi^0$ and $\psi^1$
   only** — $\psi^2$ never appears in a variational formulation. The U
   channel completes its rows/buckets in `assemble_nc_dftu_current_ddb_row`
   (during the SCF) and `assemble_nc_dftu_ddb` (phonon/electric/strain
   completions after all runs, using cached responses).

Finally: DDB blocks (`d2nl`/`d2lo` with `blkflg` marks) → `mrgddb` →
`anaddb` (interpolated phonons, elastic constants, Born charges,
$\varepsilon_\infty$).

### 0.3 The Sternheimer equation (derivation)

Start from the perturbed one-electron equation
$(H(\lambda)-\varepsilon_n(\lambda))\,|\psi_n(\lambda)\rangle = 0$ with
$H(\lambda)=H^0+\lambda H^1$, $\psi_n(\lambda)=\psi^0_n+\lambda\psi^1_n$,
$\varepsilon_n(\lambda)=\varepsilon^0_n+\lambda\varepsilon^1_n$. Collecting
first-order terms:

$$\bigl(H^0-\varepsilon^0_n\bigr)\,|\psi^1_n\rangle
   \;=\; -\bigl(H^1-\varepsilon^1_n\bigr)\,|\psi^0_n\rangle
   \;=\; -\hat P_c\,H^1|\psi^0_n\rangle. \tag{0.1}$$

The last equality holds because
$\langle\psi^0_n|(H^1-\varepsilon^1_n)|\psi^0_n\rangle =
\varepsilon^1_n - \varepsilon^1_n = 0$: the $\varepsilon^1$ term lives only
on the occupied states, and the gauge condition
$\langle\psi^0_n|\psi^1_n\rangle = 0$ (from
$\partial_\lambda\langle\psi_n|\psi_n\rangle = 0$) removes it. $\hat P_c$
is the conduction projector of the **unperturbed** manifold at the response
wavevector. In ABINIT's $q\ne 0$ convention, eq. (0.1) is solved in the
$(\mathbf k + \mathbf q)$ PW sphere: the operator is
$H^0_{\mathbf k+\mathbf q} - \varepsilon^0_{n\mathbf k}$ and the source is
$-\hat P_c^{\mathbf k+\mathbf q} H^1|\psi^0_{n\mathbf k}\rangle$ with
$\psi^0$ transported from the $\mathbf k$ sphere. The implementation's
supported regime: static ($\omega = \eta = 0$) response, insulator
occupations (`occopt ≤ 2` warns; fixed occupations assumed,
`m_dfpt_vtorho.F90` L499–510).

For +U the source contains the three-arm first-order Hubbard Hamiltonian
(§3.2), and self-consistency adds $V^1_U$ to it (§3.1).

### 0.4 The 2n+1 theorem and the shape of $E^{\lambda\mu}$

For a variational (stationary) energy functional, second-order terms need
$\psi^0$, $\psi^1$ only. The $\varepsilon^1$ terms drop against
$\langle\psi^1|\psi^0\rangle = 0$, and one obtains the generic structure

$$E^{\lambda\mu}_{\rm tot} \;=\;
   \sum_{n\mathbf k} f\Bigl[\langle\psi^1_\lambda|H^\mu|\psi^0\rangle
   + \langle\psi^1_\mu|H^\lambda|\psi^0\rangle\Bigr]
   \;+\; \sum_{n\mathbf k} f\,\langle\psi^0|H^{\lambda\mu}|\psi^0\rangle,
\tag{0.2}$$

with $H$ the *self-consistent* one-electron Hamiltonian (Hartree/xc
response included in $H^\mu$ through the SCF — ABINIT never contracts an
explicit xc kernel). Section 4 derives and verifies the exact +U
refinement of (0.2) — the term inventory of $H^{\lambda\mu}$ and the
occupation-Hessian remainder $U\,\mathrm{Tr}(n^\lambda n^\mu)$ — as the
reference ledger identity for auditing the code.

### 0.5 ABINIT's dataset design and where +U hooks in

An RF run is a **dataset chain** in one input file. Canonical 11-dataset
phonon chain (LiF/Si campaign template):

- **DS 1** — GS (`irdwfk`/`getwfk` chain seed).
- **DS 2..4** — $\Gamma$: atom displacements (RF atom perturbations
  `rfphon` + `rfatpol` + `rfdir`), ddk, electric field; produce the Γ
  2DTE blocks + Born/dielectric.
- **DS 5..11** — finite-q displacements on the q mesh.

Perturbation indexing `ipert` (verified `m_dfpt_looppert.F90` L963–965):

| ipert | perturbation | idir |
|---|---|---|
| `1..natom` | atomic displacement $\tau_{\kappa}$ | 1..3 |
| `natom+1` | ddk $\partial/\partial k_\alpha$ | 1..3 |
| `natom+2` | electric field $E_\alpha$ (Berry phase machinery) | 1..3 |
| `natom+3` | strain, diagonal: `istr = idir` ∈ {xx,yy,zz} | 1..3 |
| `natom+4` | strain, shear: `istr = idir+3` ∈ {yz,xz,xy} | 1..3 |

Module layout of the implementation:

| directory | role |
|---|---|
| `src/66_nc_dftu/` | GS + response math: `m_nc_dftu.F90` (projectors, n⁰, V⁰, forces/stress, jets), `m_nc_dftu_data.F90` (response containers, V¹, kernel zoo) |
| `src/66_wfs/` | `m_nc_dftu_hamiltonian.F90`: the first-order Hubbard Hamiltonian $\hat H^1_U$ acting on wavefunction coefficients |
| `src/68_pao_hamiltonian/`, `src/65_pao/` | PAO projector/overlap machinery shared with the NC PAO Hamiltonian (`m_nc_pao_hamiltonian.F90`) |
| `src/66_hubbard/` | PAW/NC-shared Hubbard library: full tensor (`hubbard_build_interaction`, `hubbard_energy_dc`, `hubbard_potential`), scalar Dudarev (`hubbard_dudarev_energy_potential`), validated linearized potential (`hubbard_linearized_potential` — V¹ convention owner) |
| `src/72_response/` | DFPT integration: `m_dfpt_vtorho.F90` (response SCF, n¹/V¹, trial modes), `m_dfpt_scfcv.F90` (2DTE ledger, DDB buckets), `m_dfpt_nstwf.F90` (row harvest $d2nl\_u$), `m_dfpt_cgwf.F90` (Sternheimer CG consuming `gs_hamkq%nc_dftu`), `m_dfpt_looppert.F90` (schedule/caches) |

The NC gate in `dfpt_vtorho` (L494–497): NC only (`usepaw=0`,
`usedftu_nc=1`), perturbations ≤ natom, ddk, electric (q≠0 excluded), and
strain only for spinor+finite-q runs — i.e. production strain is the
spinor Γ channel; the collinear elastic route is the standard
stress/rfstrs machinery plus the scfcv U bucket (§5.7).

---

## 1. DFT framework

The total-energy functional for fixed occupations (the insulating regime;
$f_{n\mathbf k}$ = 2 (nsppol=1) or 1 (nsppol=2), `occopt=1`):

$$E_{\rm DFT}[{\psi_{n\mathbf k}}] \;=\;
   \sum_{n\mathbf k} f\,\langle\psi_{n\mathbf k}|\hat T + \hat V_{\rm ext}|\psi_{n\mathbf k}\rangle
   + E_{\rm H}[\rho] + E_{\rm xc}[\rho_\uparrow,\rho_\downarrow],$$

with orthonormality constraints $\langle\psi_{m\mathbf k}|\psi_{n\mathbf k}\rangle=\delta_{mn}$.
The stationarity of the Lagrangian
$\mathcal L = E_{\rm DFT} - \sum \varepsilon_{n\mathbf k}(\langle\psi|\psi\rangle - 1)$
gives the Kohn–Sham equations

$$\Bigl[\hat T + \hat V_{\rm ext} + \hat V_{\rm H}[\rho]
   + \hat V_{\rm xc}^{\sigma}[\rho_\uparrow,\rho_\downarrow]\Bigr]
   |\psi_{n\mathbf k}\rangle \;=\; \varepsilon_{n\mathbf k}\,|\psi_{n\mathbf k}\rangle,$$

$\hat V_{\rm H} = \delta E_H/\delta\rho$, $\hat V_{\rm xc}^\sigma = \partial E_{\rm xc}/\partial\rho_\sigma$.
Two facts used repeatedly below:

- **Variationality**: first-order errors in $\psi$ give second-order errors
  in $E$; this is what licenses the 2n+1 theorem and the mixed-ledger
  identities of §4.
- **Band-energy identity**: $\sum f\varepsilon =
  \sum f\langle\psi|\hat T+\hat V_{\rm ext}+\hat V_H+\hat V_{\rm xc}|\psi\rangle
  + \text{(onsite potential traces)}$; for +U the onsite trace is
  $\mathrm{Tr}(V_U n)$ (§4.1 uses exactly this).

Perturbations in ABINIT act on the *crystal*: displacement of atom κ in
Cartesian direction α; strain via $\mathbf r' = (\mathbb 1 + \eta\,\mathbb
E)\mathbf r$ with $\mathbb E = \mathbf e_\alpha\mathbf e_\beta^T +
\mathbf e_\beta\mathbf e_\alpha^T$ (so that diagonal strain uses $\mathbb
E = \mathbf e_\alpha\mathbf e_\alpha^T$ at parameter $\eta$ and shear uses
the symmetrized pair at $\eta/2$; Voigt order xx,yy,zz,yz,xz,xy); electric
field via the $\tfrac{i}{c}[\hat V_{\rm nl}, \mathbf r]$ commutator
(equivalently ddk), which in the plane-wave basis acts through the
projector derivative $\partial\beta/\partial\mathbf k$.

---

## 2. DFT+U: from the Hubbard model to the implemented functionals

### 2.1 The Hubbard interaction and the rotationally invariant functional

The on-site Coulomb interaction among $(2l{+}1)$l orbitals of atom κ:

$$\hat V_{ee} \;=\; \tfrac12 \sum_{\substack{m_1 m_2 m_3 m_4\\ \sigma\sigma'}}
   U_{m_1 m_2 m_3 m_4}\,
   \hat c^\dagger_{m_1\sigma}\hat c^\dagger_{m_3\sigma'}
   \hat c_{m_4\sigma'}\hat c_{m_2\sigma},\qquad
   U_{m_1 m_2 m_3 m_4} = \langle m_1 m_2|v_{ee}|m_3 m_4\rangle,$$

with $U_{m_1m_2m_3m_4} = \sum_{kl} G_{kl}\,g_k\,g_l\cdots$ expanded in Gaunt
coefficients times Slater integrals $F^k$ ($k=0,2,4(,6)$) — the
construction `hubbard_build_interaction` performs (`m_nc_dftu.F90`
L2159–2287, `dftu_dc≠0` branch; realgnt tables, mode 3 = spinor interaction
layout).

The DFT+U total energy adds the Hubbard functional of the occupation
matrix

$$n^{\kappa\sigma}_{mm'} \;=\; \sum_{n\mathbf k} f_{n\mathbf k}\,
   \langle \psi_{n\mathbf k} | \hat P^{\kappa\dagger}_{m'}\hat P^{\kappa}_{m} | \psi_{n\mathbf k}\rangle$$

($\hat P^\kappa_m$ = projector onto orbital $m$ of atom κ, spin σ; the
spinor form packs the four spin outer products, §5.2) minus a double
counting $E_{\rm dc}$ of the interactions already treated by the mean-field
DFT:

$$E_{\rm DFT+U} = E_{\rm DFT} + E_{\rm Hub}[n] - E_{\rm dc}[n].$$

### 2.2 The Dudarev (rotationally averaged) functional — verified reduction

Averaging the angular dependence over the shell leaves two Kanamori
parameters: the intra/inter-orbital direct average $U$ and the exchange
average $J$. The Hubbard expectation in the mean-field (Slater-determinant)
state with spin-orbital occupations $n_{m\sigma}\in[0,1]$ is

$$E_{\rm Hub} = U\sum_m n_{m\uparrow}n_{m\downarrow}
 + U\!\!\sum_{m\ne m'}\!\! n_{m\uparrow}n_{m'\downarrow}
 + (U-J)\!\!\sum_{m<m',\sigma}\!\! n_{m\sigma}n_{m'\sigma},$$

(intra-orbital pairs $U$; inter-orbital opposite-spin $U$; inter-orbital
same-spin $U-J$ — direct minus exchange), and the around-mean-field/FLL
double counting is

$$E_{\rm dc}^{\rm FLL} = \tfrac{U}{2}N(N-1) - \tfrac{J}{2}\sum_\sigma N^\sigma(N^\sigma-1),
   \qquad N = \sum_{m\sigma} n_{m\sigma}.$$

**Verified identity (sympy, exact; §9.1)**: for arbitrary fractional
diagonal occupations, symbolic $U, J$:

$$\boxed{\;E_{\rm Hub} - E_{\rm dc}^{\rm FLL} \;=\; \frac{U_{\rm eff}}{2}\sum_{m\sigma} n_{m\sigma}\bigl(1 - n_{m\sigma}\bigr)\;=\;
\frac{U_{\rm eff}}{2}\sum_\sigma\Bigl[\mathrm{Tr}\,n^\sigma - \mathrm{Tr}\,(n^\sigma n^\sigma)\Bigr],\quad U_{\rm eff} = U - J.}$$

This is the Dudarev functional, and its two cardinal properties follow
immediately: (i) it vanishes for integer occupations (the spurious DFT
curvature is cancelled), (ii) its curvature w.r.t. fractional occupation is
$-U_{\rm eff}$. The implementation (`hubbard_dudarev_energy_potential` in
`66_hubbard`; `u_eff = dftu_u - dftu_j` applied at every call site)
realizes

$$E_U[n] = \frac{U_{\rm eff}}{2}\Bigl(\mathrm{Tr}\,n - \mathrm{Tr}\,n^2\Bigr),
\qquad V_{U,ij} = \frac{\partial E_U}{\partial n_{ji}} = U_{\rm eff}\Bigl(\tfrac12\delta_{ij} - n_{ij}\Bigr),
\tag{2.1}$$

the header formula of `compute_dftu_vmatrix_nc` (m_nc_dftu.F90 L3118–3200).
For the spinor (nspinor=2/nspden=4 packed) channel, the same functional is
applied to the full $2(2l{+}1)\times2(2l{+}1)$ complex block
(`nc_dftu_spinor_dudarev_energy/potential`, L3203–3276):

$$E_U = \frac{U_{\rm eff}}{2}\Bigl(\mathrm{Tr}\,n - \mathrm{Tr}\,n^2\Bigr)
\quad\text{with}\quad
\mathrm{Tr}\,n^2 = \mathrm{Tr}\,n_{uu}^2 + \mathrm{Tr}\,n_{dd}^2 + 2\,\mathrm{Tr}\,(n_{ud}n_{du}),$$

which reduces to the scalar form when $n_{ud}=0$ and penalizes transverse
spin mixing through $|n_{ud}|^2$ — the noncollinear/SOC continuation of
Dudarev. (`dftu_dc` = 2..4 are guarded out in the spinor path; `dftu_dc=1`
routes to the full-tensor `hubbard_energy_dc`/`hubbard_potential`.)

### 2.3 The projector realization in the code (PAO projectors)

The NC DFT+U projector for orbital $m$ (real $Y_{lm}$), atom at reduced
position $\boldsymbol\tau$, in the PAO/tphi basis from the UPF pseudo
(`pspcod` 11/12 required, `init_dftu_nc` guard):

$$\phi^{\kappa}_{m}(\mathbf k+\mathbf G) \;=\;
\frac{4\pi}{\sqrt{\Omega}}\; t_\kappa\bigl(|\mathbf k+\mathbf G|\bigr)\;
Y_{lm}\bigl(\widehat{\mathbf k+\mathbf G}\bigr)\;
e^{-2\pi i(\mathbf k+\mathbf G)\cdot\boldsymbol\tau_\kappa},
\qquad p^{\kappa}_{m,n\mathbf k} \equiv \langle \phi^\kappa_m | \psi_{n\mathbf k}\rangle = \sum_\mathbf G \phi^{\kappa\,*}_{m}\,\psi_{n\mathbf k}(\mathbf G).
\tag{2.2}$$

$t_\kappa(q)$ = radial PAO (spline fit `splfit`); the structure factor
carries the atom position. Then

$$n^{\kappa\sigma}_{mm'} = \sum_{n\mathbf k} w_{\mathbf k}\, f_{n\mathbf k}\,
\mathrm{Re}\bigl[p^{\kappa}_{m,n\mathbf k}\, p^{\kappa\,*}_{m',n\mathbf k}\bigr]
\quad(\text{scalar; } \texttt{compute\_occmatrix\_nc}\ \text{L2377–2829}),
\tag{2.3}$$

and for the packed spinor: $n^{\kappa}_{mm'}{}^{ss'} = \sum w f\,p_m^s\,p^{s'\,*}_{m'}$ stored in the four channels
`ipack` = 1:uu, 2:dd, 3:ud, 4:du (`packed_indices = reshape((/1,4,3,2/),(/2,2/))`,
`m_nc_dftu_data.F90` L316–333 — the ABINIT shared `ndij=4` convention).

Space-group symmetrization: $n \leftarrow \frac{1}{N}\sum_R D(R)\,n^{\kappa_R}\,D(R)^T$
with real-Ylm rotation matrices `zarot` from `setsym_ylm` (transpose-index
PAW convention; AFM ops conjugate and swap spin channels), plus — in the
spinor path — rotation of the magnetization vector
$\mathbf m = (n_{ud}+n_{du},\, i(n_{ud}-n_{du})\,{}^{\!*},\, n_{uu}-n_{dd})$
by the Cartesian symrec and AFM conjugation
(`symmetrize_nc_occmatrix[_spinor]`, L2836–3001). Skipped for `kptopt=3`
(full-BZ sampling, collinear limit protection).

### 2.4 Are the projectors orthonormal? Assumption and consequences

The PAO projectors (2.2) are **not orthonormal in general**, and the
implementation **assumes they are**, at two distinct levels:

1. **Intra-site**: `compute_occmatrix_nc` builds $n = \sum wf\,\beta\beta^\dagger$
   with **no overlap metric** $S_{mm'} = \langle\beta_m|\beta_{m'}\rangle$
   anywhere (verified: no overlap/metric code in the DFT+U path), and
   `compute_dftu_vmatrix_nc` inserts $V = U_{\rm eff}(\tfrac12\mathbb1 - n)$
   directly as $\hat V_U = \hat P^\dagger V\hat P$. The Dudarev derivation
   (§2.2) presumes an orthonormal Hubbard basis: only then are the
   eigenvalues of $n$ occupation numbers in $[0,1]$ and $E_U=0$ for integer
   occupations exact. The rigorous treatment for non-orthonormal projectors
   uses the **dual basis** $\tilde\beta = \beta S^{-1}$ so that
   $n = \tilde B^\dagger(\sum f|\psi\rangle\langle\psi|)\tilde B$
   (or Löwdin-orthonormalized projectors — QE's `ortho-atomic` mode; QE's
   `pseudo` mode inserts the same $S$ transform via `q_ae`, see
   [qe_dftu_reference](qe_dftu_reference.md)). ABINIT's tphi route uses the raw PAOs — the
   "non-normalized projectors" QE-compatibility item of story-418.
2. **Inter-site**: sites are treated as mutually orthogonal ($V_U$ strictly
   site-diagonal, $\langle\beta^\kappa|\beta^{\kappa'}\rangle$ ignored) —
   the standard DFT+U site-local approximation.

What the assumption does **not** affect: the DFPT algebra of §4. The
verified ledger identity (4.3) was proven with an *arbitrary*
non-isometric $B$ — given the functional is *defined* with
ñ $= B^\dagger(\cdot)B$, the double-counting algebra and all response
identities are exact for any projector set. Orthonormality is a
*physics-interpretability* assumption (meaning of $U$, integer-occupation
limit, rotational averaging), not an algebraic-consistency one.

Quantified status (Gaussian-PAO estimates, verified numerically):

| effect | magnitude |
|---|---|
| cutoff truncation of $\langle\beta|\beta\rangle$ | spectral weight outside $|\mathbf K|<\sqrt{2\,ecut}$: σ=0.5 bohr PAO → 1.9% (ecut 10), 2e-4 (20), 1e-8 (40 Ha); σ≥0.7 → negligible already at ecut 20 |
| k-to-k norm fluctuation | same order as above (each k offsets the G-sphere differently) |
| inter-site overlap $e^{-d^2/4\sigma^2}$ | σ=0.7, d=3.8 bohr: 6e-4; σ=1.0: 2.7%; σ=1.5: 20% — fatal for diffuse Hubbard shells, fine for compact ones |

For the campaign systems (LiF F-l=1, Si, NiO compact d/p shells) the
assumption is quantitatively safe at production ecut — projector
non-orthonormality is **not** a suspect for the finite-U DFPT defects
(§8.2; those are byte-stable algebra issues). It *would* matter for
diffuse shells (weakly bound p states, large-U supercells with short
Hubbard-shell distances) and for ABINIT↔QE absolute-energy comparability.

---

## 3. DFPT with +U: first order

### 3.1 First-order occupation matrix and the induced potential

Differentiating (2.3) at fixed $w f$ (insulator): with
$a^{\lambda}_{m} \equiv$ (ket amplitude of the perturbed projector acting
on the perturbed state),

$$a^{\lambda}_{m,n\mathbf k} \;=\;
\underbrace{\langle\phi^0_m|\psi^1_{\lambda,n\mathbf k}\rangle}_{p1}
\;+\;\underbrace{\langle\phi^\lambda_m|\psi^0_{n\mathbf k}\rangle}_{d1},
\qquad
n^1{}^\lambda \;=\; \sum_{n\mathbf k} w f\,\bigl[a^\lambda\,p^{0\,\dagger} + p^0\,a^{\lambda\,\dagger}\bigr],
\tag{3.1}$$

(the code's amplitude vocabulary: `p0,p1,p01,d1,x,e`, §5.4). The induced
potential (Dudarev derivative of (2.1)):

$$\boxed{\;V^1_{U,ij} \;=\; -\,U_{\rm eff}\,\bigl(n^1_{\,ji}\bigr)\;}
\qquad\text{(index-transposed!)},
\tag{3.2}$$

because $V_{ij} = \partial E_U/\partial n_{ji}$. The transpose is
load-bearing: at Γ the displacement response $n^1$ is Hermitian and purely
imaginary ($n^1 = iA$, $A$ real antisymmetric), so $n^{1T} = -n^1$ —
omitting the transpose flips the sign of the dominant imaginary part and
drives the response SCF to a false fixed point. This exact bug (defect B)
was found and fixed on 2026-09-03
(`nc_dftu_spinor_dudarev_response_potential`, m_nc_dftu_data.F90 L785–816,
verbatim comment; verified against the sympy derivative
$\partial E_U/\partial n_{pq} = \tfrac12\delta_{pq}U - U\,n_{qp}$).

### 3.2 The first-order Hubbard Hamiltonian: three-arm product rule

$\hat V_U = \hat P^\dagger\,V_U\,\hat P$ (a rank-$(2l{+}1)$ separable
operator per atom). Differentiate:

$$\hat H^1_U = \hat P^{1\dagger} V^0_U \hat P^0
   \;+\; \hat P^{0\dagger} V^1_U \hat P^0
   \;+\; \hat P^{0\dagger} V^0_U \hat P^{1},
\tag{3.3}$$

i.e. displaced-projector arm $\beta^1 V^0 p^0$ + induced-potential arm
$\beta^0 V^1 p^0$ + displaced-ket arm $\beta^0 V^0 p^1$. Implemented as
`apply_dftu_h1_displacement_nc` (m_nc_dftu_hamiltonian.F90 L399–1349;
flags `apply_v1`, `apply_first_order_projector`) and
`apply_dftu_h1_strain_nc` (L1431–1820, Γ, β¹ on every atom, no q-phase).

The three consumers with different arm subsets:

| consumer | arms | why |
|---|---|---|
| Sternheimer CG (`m_dfpt_cgwf.F90` L602–606) | β¹V⁰p⁰ + β⁰V¹p⁰ + β⁰V⁰p¹ | full self-consistent source |
| 2DTE row harvest `d2nl_u` (`m_dfpt_nstwf.F90` L1383–1392, L2631–2649) | `apply_v1=.false.`, frozen projectors | the native ledger already carries the ψ¹-carrying part of the row; §5.6 |

For **displacement**, the projector derivative is the structure factor
chain rule — trivially

$$\boxed{\;\frac{\partial \phi_m}{\partial \tau_{\kappa,\mu}} = -2\pi i\,(\mathbf k+\mathbf G)_\mu\;\phi_m\;}
\qquad(\texttt{build\_nc\_dftu\_displacement\_dphi\_gamma},\ \text{L179–196}),
\tag{3.4}$$

with $(\mathbf k+\mathbf G)$ in *reduced* coordinates in the code (callers
contract reduced force components). For **electric field** the projector
derivative is $\partial\phi/\partial k$ (inline in
`apply_dftu_h1_displacement_nc`; the $\hat V_{\rm nl}$ structure-factor
terms cancel inside the commutator $[V_{\rm nl},\mathbf r]$; special case
l=1 G=0). The DDK source needs only $V^0$.

**q ≠ 0 phase gauge.** A displacement perturbation at wavevector q: the
displaced projector is evaluated in the $(\mathbf k+\mathbf q)$ sphere and
carries $e^{2\pi i\mathbf q\cdot\boldsymbol\tau}$ per site arm; the induced
$V^1$ (built from occ1) carries the conjugate site phase
$e^{-2\pi i\mathbf q\cdot\boldsymbol\tau_a}$; the −q partner relates by
`nc_dftu_set_packed_partner` (m_nc_dftu_data.F90 L748–784):
$n^{-q}(\mathrm{pack}(ji)) = e^{-i2\pi\mathbf G\cdot\tau}\,\overline{n^q(ji)}$
(−q represented as q−G with 2q = G; `nc_dftu_pair_spinor_responses`
completes both branches: $n^{1,q} \mathrel{+}= n^{1,\rm ket,-q}$ etc.).
Env switch `ABI_NC_DFTU_PHASE_MODE=folded|trueq|off` audits the gauge.

### 3.3 Strain: projector jets (verified)

Strain is Cartesian and *volume-normalized*: $\mathbf r' = (\mathbb 1 +
\eta\mathbb E)\mathbf r$, so at **fixed reduced k**,
$\mathbf K(\eta) = (\mathbb 1 + \eta\mathbb E)^{-1}\mathbf K_0$,
$\dot{\mathbf K} = -\mathbb E\mathbf K$, and the PAO normalization
$s = \det(\mathbb 1+\eta\mathbb E)^{-1/2}$ gives $\dot s/s = -\tfrac12
\mathrm{tr}\,\mathbb E$ (diagonal) or $0$ (shear). With
$\phi(\mathbf K) = t(q)Y_{lm}(\hat{\mathbf K})\,(\text{sf})\,s$
(structure factor fixed: fractional τ unchanged):

$$\boxed{\;\frac{\partial\phi}{\partial\eta}\Big|_{\rm diag}
 = -\,\bigl(\nabla_{\mathbf K}\phi\bigr)_{\alpha}\,K_\alpha \;-\; \tfrac12\,\phi,
 \qquad
 \frac{\partial\phi}{\partial\eta}\Big|_{\rm shear}
 = -\tfrac12\Bigl[\bigl(\nabla\phi\bigr)_{\alpha}K_\beta + \bigl(\nabla\phi\bigr)_{\beta}K_\alpha\Bigr]\;}
\tag{3.5}$$

**Verified (sympy, exact)** against explicit symbolic differentiation of
$\phi((\mathbb1+\eta\mathbb E)^{-1}\mathbf K)\det^{-1/2}$ for a concrete
l=1 PAO ($t(q)=e^{-aq^2}$ stand-in), both diagonal and shear:
`expand(diff − code) == 0` (§9.2). Implemented in
`build_nc_dftu_strain_dphi_gamma` (L198–252; Cartesian gradients via
reduced `ylmgr` folded with `gprimd`), and the same reduced-space form is
used in the stress branch of `forstrnps_dftu` (§6).

The **exact second jet** (`build_nc_dftu_strain_d2phi_gamma`, L255–363):

$$\frac{\partial^2\phi}{\partial\eta_\lambda\partial\eta_\mu} = \Bigl[\tfrac{\mathrm{tr}E_\lambda\mathrm{tr}E_\mu}{4} + \tfrac12\mathrm{tr}(E_\lambda E_\mu)\Bigr]\phi
 - \tfrac12\bigl(\mathrm{tr}E_\lambda\,F_\mu + \mathrm{tr}E_\mu\,F_\lambda\bigr) + F_{\lambda\mu},
\tag{3.6}$$

with $F_\lambda = (-g_\lambda \dot t\, Y + t\,dY/d\eta_\lambda)\,\mathrm{sf}$
($g_\lambda = \hat{\mathbf K}\cdot E_\lambda\mathbf K$) and
$F_{\lambda\mu}$ the full radial+angular second derivative (d2K from
$E_\lambda E_\mu + E_\mu E_\lambda$, d²q from $\hat K$, Ylm Hessian via
`ylmgr` 3+ihess); the normalization factor
$\bigl[\mathrm{tr}E_\lambda\mathrm{tr}E_\mu/4 + \mathrm{tr}(E_\lambda E_\mu)/2\bigr]$
was verified symbolically (handoff verification 4). The finite-difference
oracle `build_nc_dftu_strained_phi_gamma` (L365–430) rebuilds the PAO on
the exactly strained cell (cofactor inverse, det^{−1/2} rescale) for
validating (3.5)–(3.6).

---

## 4. Second-order assembly: the verified central identity

This section is the analytic core the code ledger must reproduce.

### 4.1 The double-counting form of the total energy

From §1's band-energy identity and (2.1):
$\sum f\varepsilon = \sum f\langle\hat T+\hat V_H+\hat V_{xc}+\hat V_{\rm ext}\rangle + \mathrm{Tr}(V_U n)$
with $\mathrm{Tr}(V_U n) = \tfrac{U}{2}\mathrm{Tr}n - U\,\mathrm{Tr}n^2$
(writing $U \equiv U_{\rm eff}$), and
$E_{\rm tot} = \sum f\langle\hat T+\hat V_H+\hat V_{xc}+\hat V_{\rm ext}\rangle + \tfrac{U}{2}\mathrm{Tr}n - \tfrac{U}{2}\mathrm{Tr}n^2$, so the
**exact** algebraic identity

$$\boxed{\;E_{\rm tot} \;=\; \sum_{n\mathbf k} f\,\varepsilon_{n\mathbf k} \;+\; \frac{U}{2}\,\mathrm{Tr}\,n^2\;}
\tag{4.1}$$

(double-counting form; $T$ may carry an explicit λ-dependence — kinetic
strain term — which is kept in mind below).

### 4.2 Second derivative: the ψ²-carrier cancellation

Differentiate (4.1) twice, using the amplitude decomposition
$n^{\lambda\mu} = $ explicit-projector part + ψ¹ψ¹ part + ψ²-carrier part
($n^{\lambda\mu} \ni \sum wf\,[p^0 p^{2\dagger} + p^2 p^{0\dagger}]$):

$$E^{\lambda\mu}_{\rm tot} = \sum f\,\varepsilon^{\lambda\mu}
 \;+\; U\,\mathrm{Tr}(n^\lambda n^\mu)
 \;+\; U\,\mathrm{Tr}(n\,n^{\lambda\mu}).$$

Each $\varepsilon^{\lambda\mu}_{n\mathbf k}$ by second-order perturbation
theory (the $\varepsilon^1$ terms drop against
$\langle\psi^1|\psi^0\rangle = 0$):

$$\varepsilon^{\lambda\mu}_{n\mathbf k} =
 \langle\psi^1_{\lambda,n\mathbf k}|H^\mu|\psi^0_{n\mathbf k}\rangle
 + \langle\psi^1_{\mu,n\mathbf k}|H^\lambda|\psi^0_{n\mathbf k}\rangle
 + \langle\psi^0_{n\mathbf k}|\,H^{\lambda\mu}\,|\psi^0_{n\mathbf k}\rangle,
\tag{4.2}$$

with $H = T + \hat V_U$ (+ external, folded into T for brevity),
$\hat V_U = \hat P^\dagger V \hat P$, and the product rules

$$H^\mu = T^\mu + \hat P^{\mu\dagger}V\hat P + \hat P^\dagger V^\mu\hat P + \hat P^\dagger V\hat P^\mu,
\qquad V^\mu = -U\,n^{\mu T},$$
$$H^{\lambda\mu} = T^{\lambda\mu}
 + \underbrace{\hat P^{\lambda\mu\dagger}V\hat P + \hat P^\dagger V\hat P^{\lambda\mu}
 + \hat P^{\lambda\dagger}V\hat P^\mu + \hat P^{\mu\dagger}V\hat P^\lambda
 + \hat P^{\lambda\dagger}V^\mu\hat P + \hat P^{\mu\dagger}V^\lambda\hat P
 + \hat P^\dagger V^\mu\hat P^\lambda + \hat P^\dagger V^\lambda\hat P^\mu}_{F^{\lambda\mu}_{\rm expl}}
 \;+\; \hat P^\dagger\bigl(-U\,n^{\lambda\mu T}\bigr)\hat P.$$

The last (ψ²-carrying) arm, summed over occupied states, is
$\sum f\langle\psi^0|\hat P^\dagger(-U n^{\lambda\mu T})\hat P|\psi^0\rangle
= -U\,\mathrm{Tr}(n\,n^{\lambda\mu})$ — **exactly cancelling** the
$+U\,\mathrm{Tr}(n\,n^{\lambda\mu})$ term of the double-counting form.
(An equivalent statement: at fixed Hamiltonian the ψ² amplitude drops out
of a variational functional; here it is hidden inside $n^{\lambda\mu}$ and
comes back only through $V^{\lambda\mu}$ — with the same coefficient with
opposite sign.)

### 4.3 The canonical ledger identity (machine-verified)

$$\boxed{\;
E^{\lambda\mu}_{\rm tot} \;=\;
 \sum_{n\mathbf k} f\Bigl[\langle\psi^1_\lambda|H^\mu|\psi^0\rangle
 + \langle\psi^1_\mu|H^\lambda|\psi^0\rangle\Bigr]
 + \sum_{n\mathbf k} f\,\langle\psi^0|\,T^{\lambda\mu} + F^{\lambda\mu}_{\rm expl}\,|\psi^0\rangle
 + U\,\mathrm{Tr}\bigl(n^\lambda n^\mu\bigr)
\;}
\tag{4.3}$$

with $H^\mu$ the *full* first-order Hamiltonian (all three arms of (3.3),
self-consistent) and $F^{\lambda\mu}_{\rm expl}$ the 8-arm explicit
projector-potential Hessian *excluding* $\hat P^\dagger(-Un^{\lambda\mu})\hat P$.

**Verification (mpmath dps=40, §9.3)**: self-consistent toy model
$H = T(\lambda,\mu) + B\,V_U(n)\,B^\dagger$,
$E_{\rm tot} = \sum f\varepsilon + \tfrac{U}{2}\mathrm{Tr}n^2$, U=1,
N=6 orbitals/Nproj=3/one occupied band; ψ¹ solved from the *linearized
self-consistent* equations (Sternheimer iterated to the fixed point of
$V^1 = -Un^{1T}$), $n^{\lambda\mu}$ built ψ²-free from the jets. RHS of
(4.3) vs finite-difference $\partial^2 E_{\rm tot}/\partial\lambda\partial\mu$:
**diff 3.9e-11** (λ≠μ) and **1.3e-9** (λλ) — FD precision. The pure
n-decomposition (explicit $-U\,\mathrm{Tr}(n^\lambda n^\mu)$ + ψ¹/ψ²
carriers reproduces the functional-alone trace to 2e-8).

### 4.4 The two ledgers and the sign trap

Two different, individually correct decompositions coexist:

**(A) Functional-split ledger** — differentiate $E_U$ alone:
with $V = U(\tfrac12\mathbb 1 - n)$,

$$\frac{dE_U}{d\lambda} = \mathrm{Tr}\bigl(V\,n^\lambda\bigr),
\qquad
 \frac{d^2E_U}{d\lambda d\mu} = \mathrm{Tr}\bigl(V\,n^{\lambda\mu}\bigr) \;\mathbf{-}\;U\,\mathrm{Tr}\bigl(n^\lambda n^{\mu}\bigr),
\tag{4.4}$$

**verified symbolically** (exact, generic 2×2 symbolic Hermitian
$n(\lambda,\mu)$; §9.4). The occupation-Hessian piece enters (4.4) with a
**minus** sign.

> **Erratum (2026-09-03, from stories 524/525):** the superscript ${}^T$ on
$n^\mu$ in earlier drafts of (4.4) was a notation slip:
$\mathrm{Tr}(n^\lambda n^{\mu T}) - \mathrm{Tr}(n^\lambda n^\mu)
= 4\,\mathrm{Im}\,n^\lambda\!:\!\mathrm{Im}\,n^\mu \ne 0$ in the complex
channel; the exact derivative carries **no** transpose, and the code's
real-representation `ReTr` pair kernel is correct as-is
($V^\mu = -U\,n^{\mu T}$ at L543 remains a storage convention, not part of
this identity).

**(B) Assembled-total ledger** — eq. (4.3): the occupation-Hessian piece
appears with a **plus** sign, $+U\,\mathrm{Tr}(n^\lambda n^\mu)$, because
the $\varepsilon^{\lambda\mu}$ rows already carry the induced-potential
Hessian arm which cancels the ψ²-carrier (§4.2).

Both signs are correct *in their own ledger*. The rule for auditing the
code:

> If the 2DTE assembly takes the **rows** $\langle\psi^1|H^\mu|\psi^0\rangle$
> with the *full* first-order $H^\mu$ (induced $V^1$ included — which it
> does, the ψ¹ are self-consistent Sternheimer solutions), then the total
> requires **+U Tr(n^λ n^μ)** and must **not** carry a second
> Tr[V n^{λμ}] beyond the explicit F arms; if instead one assembles
> from the E_U functional derivatives (4.4), the ψ²-carrying
> Tr(V n^{λμ}) must be kept **with** the −U Tr(n^λn^μ). Mixing the
> two conventions double-counts Tr(V n^{λμ}) or drops
> U Tr(n^λ n^μ) — a deterministic (bit-reproducible) error, the signature
> of the finite-U defects in §8.2.

This is the number-one audit item against the code: the collinear phonon
bucket (§5.7) and the elastic sum (L3164–3168) mix rows (ledger B) with
kernels classified as ledger-A pieces (`dudarev_response_energy_pair` =
−U Tr, `t2` frozen Tr(Vn^{λμ}) pieces, missing-occ arm). Which subset
composes to ledger B exactly is the open analytic question (§8.3 item 1).

### 4.5 What the ledger looks like per channel (code-side formulas)

Phonon row harvest (`m_dfpt_nstwf.F90` L2631–2649), per k and band:

$$\mathrm{row}_\lambda(\mu) = w_{\mathbf k} f\; 2\,\mathrm{Re}\,\langle\psi^1_\lambda|\,\hat H^1_{U,\mu}\,\text{(frozen projectors, no }V^1)\,|\psi^0\rangle,
\qquad
\mathrm{Im}\ \text{sign-flipped (ABINIT dotprod convention)},
$$

combined over ±q as $\tfrac12(q + (-q))$ for Re and $\tfrac12(q - (-q))$
for Im (`m_dfpt_scfcv.F90` L1708–1714).

Collinear final phonon bucket (`assemble_nc_dftu_ddb`, Γ scalar branch):

$$
\begin{aligned}
B_{\mu\lambda}={}&d2nl_u
+\tfrac12\bigl[
(rv1_q+rv1_{-q})+(missing_q+missing_{-q})\\
&+(rs_q+rs_{-q})+(rf_q+rf_{-q})
+(fp_q+fp_{-q})-(mixed_q+mixed_{-q})
\bigr],
\end{aligned}
$$

for the real channel, with $q-(-q)$ parity for every imaginary term. Here
`rs` is the response-square contraction, `rf` the response/frozen
contraction, and `fp` the explicit frozen-potential Hessian. Production then
applies `d2nl += B - d2nl_u`: this preserves the native nonlocal row already
carrying the frozen-$H^1$/$\psi^2$ content and adds the missing
assembled-total-ledger partners. It is therefore ledger B of eq. (4.3), with
the positive occupation-response-square content and without a second
$\mathrm{Tr}(Vn^{\lambda\mu})$.

Story 531 validates this composition only for Γ scalar-collinear,
`dftu_dc=0`, atom-atom blocks: Si gives exact acoustic zero and 604.9953
cm⁻¹ optical modes versus the 605.16 cm⁻¹ FD oracle, while U=0 atom rows
remain within $5.34\times10^{-6}$. The finite-$q$ fallback remains a
separate story-532 acceptance problem; this Γ result must not be generalized
to finite $q$, strain, or electric channels.

Elastic bucket (L3134–3168, spinor Γ strain):

$$d2nl^{(U)}_{\mathrm{elastic}} \mathrel{+}= \text{frozen Hessian}(\mathrm{Tr}[V^0 n^{\lambda\mu}_{\rm expl}])
 + \tfrac12\bigl[\mathrm{Fpair}(\lambda,\mu) + \mathrm{Fpair}(\mu,\lambda)\bigr]
 + t2_{\rm full} + t2_{\rm cross} + \mathrm{geom\ Hessian}(\texttt{forstrnps\_dftu}),
$$

with `t2_full` = $\langle\psi^1{+}d|V^0|\psi^1{+}d\rangle$-type and
`t2_cross`/`t2_exact_cross` = Tr[V⁰ (dPψ¹ + dP¹ψ⁰)] mixed pieces (§5.4),
and `v2m_response_part` explicitly **audit-only** (comment L3162–3163).

Born/dielectric (L2834–2870): electric×atom and electric×electric =
$\tfrac12(q\pm(-q))$ response-pair contractions only; Γ electric has
**fixed PAOs** (no $\phi^E$), so no frozen-projector curvature exists
(comment L2795–2798).

---

## 5. Code map: equations ↔ functions

### 5.1 `src/66_nc_dftu/m_nc_dftu.F90` — ground state + jets (3737 lines)

| routine | lines | equation |
|---|---|---|
| `compute_pao_proj_istwfk` | 139–176 | $p_m = \sum_G \phi_m^*\psi$; istwfk=2 time-reversal packing: $2\mathrm{Re}$ weighting |
| `build_nc_dftu_displacement_dphi_gamma` | 179–196 | (3.4) $\partial_\tau\phi = -2\pi i(k+G)_\mu\phi$ |
| `build_nc_dftu_strain_dphi_gamma` | 198–252 | (3.5) verified; Voigt $\alpha\beta$ = (1,2,3,3,3,2)/(1,2,3,2,1,1) |
| `build_nc_dftu_strain_d2phi_gamma` | 255–363 | (3.6) exact second jet (verified normalization) |
| `build_nc_dftu_strained_phi_gamma` | 365–430 | FD oracle: strained-cell φ (cofactor inverse, det^{−1/2}) |
| `init_dftu_nc` | 2159–2287 | UPF/tphi requirement; norb = 2l+1; tensor build (dc≠0) |
| `compute_occmatrix_nc` | 2377–2829 | (2.3) n⁰ = Σwf Re[ββ†]; spinor packed 4 channels; symmetrize + energy/potential calls |
| `symmetrize_nc_occmatrix[_spinor]` | 2836–3001 | $D(R)nD(R)^T$ average (+magnetization rotation, AFM conj) |
| `compute_dftu_energy_nc` | 3008–3093 | $E_U$ Dudarev (2.1) / tensor `hubbard_energy_dc` |
| `compute_dftu_vmatrix_nc` | 3118–3200 | $V^0 = U_{\rm eff}(\tfrac12\mathbb1 - n)$; packed `V_cplex` |
| `nc_dftu_spinor_dudarev_{energy,potential}` | 3203–3276 | full 2norb×2norb block form (§2.2) |
| `forstrnps_dftu` | 3292–3733 | forces/stress (§6) |

Response side: `compute_nc_dftu_response_from_wfs` (n¹ from cg/cg1/
first-order projectors, eq. (3.1); first-order projector amplitudes from
the jets of §3.3), `compute_nc_dftu_response_energy`,
`build_nc_dftu_response_partner` (frozen/displacement-only partner caches).

### 5.2 `src/66_wfs/m_nc_dftu_hamiltonian.F90` — first-order Hamiltonian

- `apply_dftu_h1_displacement_nc` (L399–1349): (3.3) three arms; two-sphere
  (k+q) structure; per-site q-phases (β¹ arm × $e^{+2\pi iq\cdot\tau}$,
  V¹ arm × conjg site phase); ddk arm inline; electric: dproj=0.
- `apply_dftu_h1_strain_nc` (L1431–1820): strain β¹ on every atom (Γ, no
  pattern phase).
- `rotate_overlap_matrix_nc` = $D(R)SD(R)^T$ with real `zarot`
  (= $DSD^\dagger$ only because D is real) — audit item §8.3-3.

### 5.3 `src/66_nc_dftu/m_nc_dftu_data.F90` — containers + kernel zoo

Type `nc_dftu_data_type`: packed storage
`(cplex, norb, norb, natom, ipack/nsppol)`; response containers hold
`occ1`, `V1`, ket cache `occ1_wf_ket`, and the amplitude caches
(`proj0_amp` p0, `proj_amp` p1, `proj01_amp` p01, `dproj_amp` d1,
`dproj1_amp`/`dproj1_cross_amp` x, `d2proj_amp` e — dims
`(2, norb, natom, nspinor_amp, nkpt)`). Key builders:

- `nc_dftu_build_phonon_n2` (L128–258): ψ²-free mixed occupation

  $$\boxed{\;n^{\lambda\mu} = \sum_{n\mathbf k}wf\bigl[a^{\lambda\mu}a^{0\dagger} + a^0 a^{\lambda\mu\dagger} + a^\lambda a^{\mu\dagger} + a^\mu a^{\lambda\dagger}\bigr],\quad
  a^\lambda = p1 + d1,\ \ a^{\lambda\mu} = e + x_\mu(\lambda) + x_\lambda(\mu)\;}$$

  ($d^2P$ nonzero only on the common displaced site).
- `nc_dftu_spinor_dudarev_response_potential` (L785–816): (3.2) $V^1 = -U_{\rm eff} n^{1T}$.
- `nc_dftu_spinor_dudarev_response_energy_pair` (L818–864):
  $-U_{\rm eff}\,\mathrm{Tr}(n^\lambda n^{\mu})$ — the occupation-Hessian
  piece (ledger-A sign; audit §8.3-1).
- `nc_dftu_pair_spinor_responses` (L544–622): ±q completion + $V^1$
  (paired, no transpose here — transpose lives in the potential builder);
  `nc_dftu_set_packed_partner` (L748–784) = q↔−q gauge map.
- `nc_dftu_{spinor,scalar}_packed_frozen_energy` (L866–929):
  $\mathrm{Tr}(V^0 n^{(\cdot)})$.
- `compute_nc_dftu_response_energy_pair`: pair(response_λ, partner_μ)
  mixed energy; with `frozen_displacement_only=.true.` partners = frozen
  partner contractions (elastic/atom-strain/Born legs).

**Kernel zoo** — all share the skeleton
$E = 2\sum_{n\mathbf k}wf\,\mathrm{Re}\sum_{\rm atom,pack,ij}\overline{a_i}\,V_{ij}\,b_j$
(the ×2 = h.c./both orderings):

| kernel | lines | contraction | identity piece (§4) |
|---|---|---|---|
| `response_square01_energy` | 1194–1258 | ⟨p01^λ\|V⁰\|p01^μ⟩ | ψ¹ψ¹ (φ⁰-sphere part) of ledger A |
| `response_square_energy` | 1783–1854 | ⟨p1^λ\|V⁰\|p1^μ⟩ | production ψ¹ψ¹ curvature (B) |
| `response_square_full_energy` | 1710–1781 | ⟨p01+d\|V⁰\|p01+d⟩ | ψ¹ψ¹ incl. frozen cross |
| `t2_full_energy` | 1856–1930 | ⟨p1+d\|V⁰\|p1+d⟩ | Tr[V⁰n^{λμ}]-bilinear |
| `t2_resp_frozen_cross` | 2160–2235 | ⟨p1^λ\|V⁰\|d^μ⟩+h.c. | mixed response×frozen |
| `t2_exact_cross` | 2009–2088 | ⟨p0\|V⁰\|(x^μ+x^λ)⟩ | exact dP¹ψ⁰+dPψ¹ piece |
| `t2_cross_energy` | 1932–2007 | own-cache approx (superseded) | legacy |
| `t2_frozen_potential_cross` | 2090–2158 | ⟨d^λ\|V¹^μ\|p0⟩ | frozen×V¹ (≡ `t2_wbar_probe`) |
| `v1_proj01_cross` | 1260–1321 | ⟨p0\|V¹^λ\|p01^μ⟩ | ψ¹-leg of Tr[V¹n¹] |
| `v1_dproj_cross[_tr]` | 1391–1526 | ⟨p0\|(V¹^λ d^μ + V¹^μ d^λ)⟩ | ⟨ψ⁰\|V¹\|dPψ⁰⟩ |
| `rv1_cross` | 1528–1597 | ⟨p1^λ\|V¹^μ\|p0⟩ | ⟨ψ¹\|V¹\|ψ⁰⟩ leg (caller xmpi_sum) |
| `amp_overlap_energy` | 1323–1389 | $2U_{\rm eff}\mathrm{Re}\sum(p01{+}d)^λ_i(p01{+}d)^μ_i$ | "Tr n^{μλ}" piece (flag ×2) |
| `missing_occ_arm_energy_pair` | — | $-U\,\mathrm{Tr}[(S_\lambda{+}M_\lambda)M_\mu]$ | finite-q truncated-V¹ completion |
| `dudarev_response_energy_pair` | 818–864 | $-U\,\mathrm{Tr}(n^\lambda n^{\mu})$ | occupation Hessian (A) |
| probes: `t2_mach_probe`, `t2_wprobe`, `t2_wbar_probe`, `*_kres`, `v2m_response_part` | 2238–2656 | various | audit-only |

Flags from the source read: `amp_overlap` comment-vs-code ×2 mismatch
(L1386); `check_spinor_response_pair` message never emitted (L519–522);
`u_eff = dftu_u(1)` species-1-only inside `amp_overlap`/`v2m`; probe
duplicates.

### 5.4 `src/72_response/m_dfpt_vtorho.F90` — response SCF

- gate L494–497 (§0.5); guards L499–510 (static, nspinor≤2, occopt, dc).
- n⁰ rebuilt with **full space group** (L542–560) — the little-group
  response k-set cannot complete the star; unstarred sums leave an
  anisotropic $V_U$.
- n¹ rebuilt each call from cg/cg1 + first-order projectors
  (`compute_nc_dftu_response_from_wfs`, L561–566); DDK skipped (V⁰ only).
- trial modes (`ABI_NC_DFTU_TRIAL_MODE`, L74–78, 426–434): default |
  freeze (V⁰-only trial) | damped (mixfrac 0.5 default); paired q/−q
  trial (L419–420); under-relaxed persistence `occ1 ← (1−f)occ1 + f·occ1_new`
  (L590–623).
- $V^1$ feedback `gs_hamkq%nc_dftu` (L668–682);
  `ABI_NC_DFTU_NO_V1_FEEDBACK` A/B switch; diagnostics: block norms +
  Γ Hermiticity residuals of occ1/V1 (L636–655).

### 5.5 `src/72_response/m_dfpt_nstwf.F90` — row harvest

L1383–1392: frozen-projector $\hat H^1_U$ into the 1st-order Hamiltonian
(`apply_v1=.false.`, `apply_first_order_projector` as appropriate);
L2631–2649: $d2nl\_u$ harvest = $w f\cdot 2\mathrm{Re}\langle\psi^1|\hat H^1_{U,\mu}|\psi^0\rangle$
(Im sign-flipped); AUDIT-RW per-k dump (L2650: "k-parity of Im decides the
model-5 k-pairing question" — open, §8.3-5).

### 5.6 `src/72_response/m_dfpt_scfcv.F90` — ledger + DDB

- ±q pairing per SCF iter (L1115–1213): two vtorho calls; paired V¹
  damped 0.9/0.1; `nc_dftu_pair_spinor_responses` with $2q=G$ phase.
- $d2nl\_u$ ±q combine (L1708–1714).
- per-row bucket `assemble_nc_dftu_current_ddb_row` (L2006–2253):
  response_λ × partner_μ mixed pairs, ±q half-sums (Re sym / Im antisym),
  atom×strain cross with Hermitian swap (Im sign flip under perturbation
  exchange), `blkflg` marks, reciprocal slots.
- phonon completion `assemble_nc_dftu_ddb` (L2263–2793): caches per
  converged perturbation; computes (all channels, for diagnostics and the
  spinor channel) mixed−frozen, rv1, missing-occ arm, response_square,
  t2_resp_frozen_cross, t2_exact_cross, t2_frozen_potential_cross,
  v2m (diag); collinear final override L2738–2754 (§4.5), spinor
  mixed−frozen pair L2756–2759; d2nl insert + `d2nl_u` subtract-back
  (double-count guard) L2770–2776.
- electric cache/Born/dielectric L2800–2870 (§4.5); strain/elastic
  L2950–3240 with the sum at L3164–3168 (§4.5) and
  `dftu_geom_hessian` from `forstrnps_dftu`.
- AUDIT env switches: `ABI_NC_DFTU_{TRIAL_MODE,NO_V1_FEEDBACK,FLIP_ROWS,
  DUFINAL,DUMP_CWAVEF,NO_RV1,RV1_DEBUG}`, `ABI_NC_DFTU_H1_GEOM_FD`,
  `ABI_NC_DFTU_NO_DPHI_V0`, `ABI_NC_DFTU_DUMP_H1_PAO`,
  `ABI_NC_DFTU_PHASE_MODE`, `ABI_NC_DFTU_HARVEST`.

### 5.7 What reaches the DDB

All U terms land in `d2nl(1:2, μ_dir, μ_pert, λ_dir, λ_pert)` with
`blkflg=1`; `d2nl_u` itself never leaves scfcv (tree-wide grep: only
nstwf/scfcv/looppert). Channel map:

| channel | λ×μ | U terms |
|---|---|---|
| phonon (any q) | atom×atom | rows(native d2nl, frozen H1_U) + response-square curvature (collinear); spinor: ±q mixed−frozen pair |
| internal strain | atom×strain | frozen d2 + reciprocal bucket (Im swap) |
| elastic | strain×strain (Γ, spinor) | frozen Hessian + ½ frozen-pair + t2_full + t2_cross + geom Hessian |
| Born | E×atom (Γ, spinor) | response pairs only (fixed PAOs) |
| dielectric | E×E (Γ, spinor) | response pairs only |

---

## 6. Forces and stress (`forstrnps_dftu`)

Energy gradient w.r.t. reduced atomic coordinates (header verbatim):

$$\frac{\partial E_U}{\partial\tau_\mu} = \sum_{n\mathbf k} w f\cdot
2\,\mathrm{Re}\sum_{mm'} V_{mm'}\,
\overline{\langle\partial_\mu\beta_m|\psi\rangle}\,\langle\beta_{m'}|\psi\rangle,
\tag{6.1}$$

with $\partial_\mu\beta$ from (3.4) (projected with istwf_k=1 — derivative
projectors break time reversal). Spinor: both arms explicit
$\mathrm{Re}[V(\overline{d\,p} + \overline{p}\,d)]$, no net factor 2.
Stress: same structure with the *reduced-space* strain projector
(diagonal: $-k^{red}_\beta\,\partial\phi/\partial k_\alpha - \tfrac12\phi$;
shear: $-\tfrac12(k^{red}_\beta\partial_\alpha + k^{red}_\alpha\partial_\beta)$,
with $\partial\phi/\partial k_{red}$ built from dtphidq·$\partial q/\partial k_{red}$ +
reduced ylmgr), accumulated into str_unsym and divided by ucvol — the
$dE/d\eta$ chain rule equivalent of (3.5) at fixed reduced k.

**Known machine verdict (§8.2)**: finite-U analytic stress is
energy-inconsistent in the current tree (dσ/dε vs d²E/dε²), and
`dftu_geom_hessian` carries the strain-derivative of (6.1) into the
elastic bucket — this chain is part of the elastic audit surface.

---

## 7. Born charges and dielectric tensor (electric channel)

Route: DDK (ipert=natom+1) + electric (natom+2) datasets at Γ; the E×u
(Born) and E×E (dielectric) 2DTE blocks. For +U: no explicit
$\phi^E$ exists (fixed PAOs), so the *entire* U contribution is
wavefunction-driven: $\psi^1_E$ from the Sternheimer equation with the U
potential in H⁰ (+ the frozen H1_U source if any — none for E since dproj=0),
then $n^1{}^E$, $V^1{}_E$, and the response-pair contractions of §4.5.
anaddb converts E×u to Born charges $Z^* = -\partial^2 E/\partial E\partial u$.

Adjudication summary (details in [nc-dftu-si-collinear-fd-oracle-report](nc-dftu-si-collinear-fd-oracle-report.md)
§§5–7): the DDB route is correct at U=0 (LiF ±1.098 vs Berry-FD ±1.0978);
at finite U the F-atom charge is wrong (+3.747 vs −1.089) while the
DS3-only merge reproduces the full-DDB value — defect localized in the
E×u block assembly. The Berry-FD oracle (finite-field dP/du) needs the
explicit-mesh workaround (kptopt 0) because of the NC-overlap BZ-expansion
EOF crash at `m_nc_pao_hamiltonian.F90` ~592 for displaced cells with
usedftu_nc 1.

---

## 8. Verification ledger

### 8.1 Symbolic/numerical asserts (this report; §9 = code)

1. **FLL→Dudarev reduction** — exact symbolic residual 0 for
   $E_{\rm Hub}-E_{\rm dc}^{\rm FLL} = \tfrac{U_{\rm eff}}2\sum n(1-n)$
   (2-orbital shell, symbolic U,J, fractional n).
2. **Strain projector jets** — `simplify(diff − code) == 0` exact, diagonal
   and shear, l=1 PAO, analytic radial stand-in; second-jet normalization
   $\mathrm{tr}E_\lambda\mathrm{tr}E_\mu/4+\mathrm{tr}(E_\lambda E_\mu)/2$ exact.
3. **Dudarev trace derivatives** — exact: $\partial_\lambda E_U =
   \mathrm{Tr}(Vn^\lambda)$; $\partial_{\lambda\mu}E_U =
   \mathrm{Tr}(Vn^{\lambda\mu}) - U\,\mathrm{Tr}(n^\lambda n^{\mu})$
   (generic symbolic Hermitian 2×2 $n(\lambda,\mu)$).
4. **Exact n-decomposition** — mpmath dps 40, non-SC toy (N=5, Nproj=3):
   explicit $-U\,\mathrm{Tr}(n^\lambda n^\mu)$ + ψ¹/ψ² carriers reproduce
   the trace to 2e-8 (FD noise).
5. **Central identity (4.3)** — self-consistent toy (Sternheimer iterated
   with $V^1$ feedback), **3.9e-11** (λμ) / **1.3e-9** (λλ) vs FD.

### 8.2 Machine verdicts (cross-links)

- **U=0 certified** (NC machinery sound): LiF k6 phonons ≤0.8 cm⁻¹ whole
  2×2×2 mesh incl. imaginary modes; Born ±1.098 = Berry-FD; elastic C11
  1.8%; Si u0 phonopy ≤0.1–0.71 cm⁻¹.
- **Finite-U defective** (deterministic — elastic byte-identical across
  builds back to a442ea21 Jul-8 lineage): finite-q phonons wrong at every
  mesh q (Si L/X imaginary-vs-real flips; LiF up to 2800 cm⁻¹); elastic
  C44 sign-flip (LiF: DDB +1.214 vs stress-FD −0.483), C12 −93% (Si);
  Born F-atom +3.747 vs −1.089; dielectric U-leg off (Si 45×).
- **Fixed on the way**: spinor V¹ transpose (defect B, 2026-09-03); q/-q
  NaN forwards (762ac4dbca, 9639f57175); occ1 k-set star-completion
  (NiO −0.36% vs paper with kptopt 3).
- Full data: [nc-dftu-si-collinear-fd-oracle-report](nc-dftu-si-collinear-fd-oracle-report.md) (§§1–7), stories
  521/522 campaign dirs `/scratch/uscan/{si_suite_521,lif_sc_522}`.

### 8.3 Open audit items (theory-side, ranked)

1. **Ledger composition vs identity (4.3).** The collinear production
   bucket = rows + response-square only; spinor/elastic buckets mix
   ledger-A kernels (−U Tr pieces, Tr(V⁰n^{λμ}) frozen pieces,
   missing-occ arm) with ledger-B rows. Which combination equals (4.3)
   exactly is unresolved — and (4.3) is the reference. Notably (4.3)
   contains **no separate** $\langle\psi^1|V^0|\psi^1\rangle$ term beyond
   what the self-consistent ψ¹ rows carry (the identity holds *through*
   the SCF); the code's explicit `response_square` must therefore be
   replacing, not adding to, a row-carried piece — verify no
   double count. The elastic channel (no rows harvested? — strain rows
   via `dftu_geom_hessian` path) is the prime suspect for the
   byte-stable C44/C12 defects.
2. **`missing_occ_arm` −U Tr[(S+M)M] and `dudarev_response_energy_pair`
   −U Tr(n^λn^μ)**: signs are ledger-A; against ledger-B they
   enter with +. (ScoutB's II-sign flag on the pair kernel.)
3. **Rotation conventions**: `rotate_overlap_matrix_nc` uses
   $D(R)SD(R)^T$ with real zarot (fine only because D real); the BZ
   expansion parent search R vs R⁻¹ question; symmetrization transpose
   convention vs `setsym_ylm` PAW convention.
4. **`u_eff = dftu_u(1)`** species-1-only inside `amp_overlap_energy` and
   `v2m_response_part` (multi-species U would silently use the wrong U).
5. **k-parity of Im in harvested rows** (nstwf AUDIT-RW, L2650) — decides
   the ±q Im antisymmetrization at finite q.
6. **Probe/audit leftovers**: t2_wbar_probe duplicate, t2_cross
   superseded, v2m audit-only, env switches — hygiene, plus the
   `amp_overlap` ×2 comment/code mismatch.
7. `compute_pao_hamiltonian_direct_nc` kinetic-only dead scaffolding
   (flagged by ScoutC).

---

## 9. Appendix: reproducible verification session (sympy/mpmath, dps=40)

All asserts were run in the `mydev` python (per AGENTS.md; mpmath
`eigsy` is real-symmetric only — use real toys; no `mp.trace`, local
`mtrace`).

### 9.1 FLL → Dudarev (exact)

```python
import sympy as sp
U, J = sp.symbols('U J', real=True)
a, b, c, d = sp.symbols('a b c d', real=True)      # n_{1u} n_{1d} n_{2u} n_{2d}
E_hubb = U*(a*b + c*d) + U*(a*d + b*c) + (U-J)*(a*c + b*d)
N, Nu, Nd = a+b+c+d, a+c, b+d
E_dc = sp.Rational(1,2)*U*N*(N-1) - sp.Rational(1,2)*J*(Nu*(Nu-1)+Nd*(Nd-1))
E_dud = sp.Rational(1,2)*(U-J)*sum(x*(1-x) for x in (a,b,c,d))
assert sp.simplify(sp.expand(E_hubb - E_dc - E_dud)) == 0
```

### 9.2 Strain projector first jet (exact; l=1, t = exp(−a q²))

```python
q1,q2,q3,eta,a = sp.symbols('q1 q2 q3 eta a', real=True)
q = sp.Matrix([q1,q2,q3]); r = sp.sqrt(q.dot(q))
phi = sp.exp(-a*q.dot(q))*(q3/r)
# diagonal istr=1: K(eta)=(I+eta e1e1)^-1 q, s = (1+eta)^-1/2
K = sp.Matrix([q1/(1+eta), q2, q3])
phi_eta = sp.exp(-a*K.dot(K))*(K[2]/sp.sqrt(K.dot(K)))*(1+eta)**sp.Rational(-1,2)
assert sp.simplify(sp.expand(sp.diff(phi_eta, eta).subs(eta,0)
   - (-sp.diff(phi,q1)*q1 - phi/2))) == 0
# shear xy: E = (e1e2+e2e1)/2, no volume term
E12 = sp.Matrix([[0,sp.Rational(1,2),0],[sp.Rational(1,2),0,0],[0,0,0]])
K = (sp.eye(3)+eta*E12).inv()*q
phi_eta = sp.exp(-a*K.dot(K))*(K[2]/sp.sqrt(K.dot(K)))
assert sp.simplify(sp.expand(sp.diff(phi_eta, eta).subs(eta,0)
   - (-sp.Rational(1,2)*(sp.diff(phi,q1)*q2 + sp.diff(phi,q2)*q1)))) == 0
```

### 9.3 Central identity toy (mpmath; structure)

$H(\lambda,\mu) = T(\lambda,\mu) + B\,V_U(n)\,B^\dagger$ on N=6 real
orbitals, Nproj=3 PAOs (B tall random), one occupied band, U=1.

1. Fixed-point GS: $n = \sum f\,p\,p^T$, $V_U = U(\tfrac12 − n)$,
   $E_{\rm tot} = \sum f\varepsilon + \tfrac U2\mathrm{Tr}\,n^2$.
2. First-order: solve the linearized self-consistent system for ψ¹_λ,
   ψ¹_μ (iterate $V^1 = −U n^{1T}$ to its fixed point).
3. n^{λμ} ψ²-free from the jets; F^{λμ}_expl = the 8 product-rule arms.
4. Assert (4.3) vs central FD of $E_{\rm tot}(\lambda,\mu)$:
   |RHS − FD| = 3.9e-11 (λμ), 1.3e-9 (λλ).
   (Full session code preserved in the epic-033 working notes; the
   identity is the boxed equation (4.3).)

### 9.4 Trace identities (exact, generic Hermitian 2×2 n(λ,μ))

$n = n_0 + \lambda n_1 + \tfrac{\lambda^2}2 n_2$, symbolic Hermitian blocks
(w/ complex off-diagonals); sympy confirms
$\partial_\lambda E_U = \mathrm{Tr}(Vn^\lambda)$ and
$\partial_{\lambda\mu}E_U = \mathrm{Tr}(Vn^{\lambda\mu}) − U\,\mathrm{Tr}(n^\lambda n^{\mu})$
identically (simplify == 0).

---

*Source anchors are line numbers of the working tree
`abinit_dev_clean` @ `ProjWannPAO` + uncommitted epic-033 changes,
2026-09-03. Related notes: [nc-dftu-si-collinear-fd-oracle-report](nc-dftu-si-collinear-fd-oracle-report.md)
(machine adjudication), [nc-dftu-scalar-dudarev-2dte-audit](nc-dftu-scalar-dudarev-2dte-audit.md),
[nc-dftu-spinor-packing-convention](nc-dftu-spinor-packing-convention.md), [nc-dftu-derivation-audit](nc-dftu-derivation-audit.md),
[nc-dftu-dfpt-implementation-report](nc-dftu-dfpt-implementation-report.md), [nc-dftu-finite-q-occ1-pairing-debug](nc-dftu-finite-q-occ1-pairing-debug.md).*
