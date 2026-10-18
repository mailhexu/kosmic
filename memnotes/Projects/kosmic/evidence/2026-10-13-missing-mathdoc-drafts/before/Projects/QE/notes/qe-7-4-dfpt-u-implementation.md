---
audience: both
type: reference
status: stable
artifact_role: knowledge
created: 2026-06-02
updated: 2026-06-02
project: QE
tags: [quantum-espresso, qe-7.4, dfpt, dftu, phonon, finite-q]
---

# QE 7.4 DFPT+U implementation report

## Scope

This report traces the Quantum ESPRESSO 7.4 PHonon DFT+U implementation in:

```text
/home/hexu/projects/abinit_git/abinit_aicoding/Refs/q-e-7.4
```

The goal is to understand how QE handles finite-q DFT+U occupation responses, the Hubbard response potential, and Hubbard contributions to the dynamical matrix, with emphasis on lessons for the ABINIT NC PAO DFT+U DFPT finite-q debugging.

## Supported PHonon DFT+U scope in QE 7.4

`PHonon/PH/phq_readin.f90` restricts the PHonon DFT+U implementation:

- only `Hubbard_projectors == "atomic"` is accepted;
- only `lda_plus_u_kind == 0` is accepted;
- multiple Hubbard channels per atomic type are rejected;
- electron-phonon and Raman with Hubbard U are rejected in the ordinary PH path.

The setup path `PHonon/PH/phq_setup.f90` defines `effU(nt) = Hubbard_U(nt)` or `Hubbard_U(nt) - Hubbard_J0(nt)` and initializes rotation matrices for Hubbard spherical harmonics.

## High-level call graph

QE splits the DFPT+U phonon implementation into several distinct stages.

### 1. Initialization of Hubbard projectors and bare occupation derivatives

`PHonon/PH/phq_init.f90` does the DFT+U initialization before the ordinary bare dynamical matrix is built:

```text
lr_orthoUwfc(.TRUE.)
dnsq_bare()
if (okvan) dnsq_orth()
```

`lr_orthoUwfc` writes atomic Hubbard orbitals and `S phi` at `k` and `k+q` to buffers. `dnsq_bare` computes first bare derivatives of the occupation matrix for all Cartesian atom displacements. `dnsq_orth` adds the USPP orthogonality correction when needed.

### 2. Bare/frozen Hubbard dynamical-matrix contribution

`PHonon/PH/dynmat0.f90` calls:

```text
if (lda_plus_u) dynmat_hub_bare()
```

`PHonon/PH/dynmat_hub_bare.f90` either reads or computes `d2ns_bare`, then adds the bare Hubbard block to `dyn` and stores it in `dyn_hub_bare`.

For the effective-U part the implemented Cartesian block is documented and coded as:

$$
\sum_{I,\sigma,m_1,m_2} U_{\mathrm{eff}}(I)
\left[
\left(\frac{1}{2}\delta_{m_1m_2} - n^{I\sigma}_{m_1m_2}\right)
d^2 n^{I\sigma,\mathrm{bare}}_{m_1m_2}
- d n^{I\sigma,\mathrm{bare}}_{m_1m_2}(L\alpha)^*
d n^{I\sigma,\mathrm{bare}}_{m_1m_2}(L'\beta)
\right].
$$

In code this is the `work` accumulation using `rho%ns`, `d2ns_bare`, and `dnsbare` in `dynmat_hub_bare.f90`:

```text
if (m1==m2) work += 0.5*d2ns_bare_aux
work = work - nsaux*d2ns_bare_aux - dnsaux1*conjg(dnsaux2)
dynwrk += work * effU(nt)
```

Then `dynwrk` is multiplied by 2 for `nspin == 1`, transformed from Cartesian coordinates to the pattern basis `u`, and added to the total dynamical matrix.

### 3. Bare Hubbard potential in the Sternheimer right-hand side

During the linear-response solve, `PHonon/PH/solve_linter.f90` first builds the bare perturbing potential times the unperturbed wavefunction. For each perturbation mode it calls the ordinary nonlocal bare term and then:

```text
if (lda_plus_u) dvqhub_barepsi_us(ik, u(1,mode))
```

`PHonon/PH/dvqhub_barepsi_us.f90` computes the bare derivative of the Hubbard potential acting on `psi(k)` and adds it to `dvpsi`. Its header gives the implemented form:

$$
|\Delta V_{\mathrm{Hub}}^{\mathrm{bare}}\psi\rangle
= U\left(\frac{1}{2}\delta - n\right)
\left(|\Delta_q S\phi_{k}\rangle\langle S\phi_k|\psi_k\rangle
+ |S\phi_{k+q}\rangle\langle\Delta_{-q} S\phi_{k+q}|\psi_k\rangle\right)
- U\,dn^{\mathrm{bare}} |S\phi_{k+q}\rangle\langle S\phi_k|\psi_k\rangle.
$$

Important implementation detail: QE explicitly uses both finite-q projector-side derivatives:

- `dqsphi`: $\Delta_q(S_k\phi(k,I,m))$, a ket at `k+q`;
- `dmqsphi`: $\Delta_{-q}(S_{k+q}\phi(k+q,I,m))$, paired with the bra/projection on `psi(k)`.

This path is a source term in the Sternheimer equation, not just a later DDB correction.

### 4. SCF Hubbard response potential inside every Sternheimer iteration

`LR_Modules/response_kernels.f90` adds the SCF potential from the previous iteration to `dvpsi`; immediately after the ordinary SCF potential, it calls:

```text
if (lda_plus_u .and. .not. exclude_hubbard_) adddvhubscf(ipert, ik)
```

`LR_Modules/adddvhubscf.f90` applies the response Hubbard potential from the current first-order occupation matrix `dnsscf`:

$$
|\Delta V_{\mathrm{Hub}}^{\mathrm{SCF}}\psi\rangle
= -U_{\mathrm{eff}}
\sum_{I,m_1,m_2}
dn^{I\sigma,\mathrm{SCF}}_{m_1m_2}
|S\phi_{I m_1,k+q}\rangle
\langle S\phi_{I m_2,k}|\psi_{k}\rangle.
$$

The code expression is:

```text
dvqi -= effU(nt) * dnsscf(m1,m2,current_spin,nah,ipert) *
        swfcatomkpq(ig,ihubst1) * conjg(proj1(ibnd,ihubst2))
dvpsi += dvhubscf
```

This is the crucial screening path: the Hubbard response potential participates self-consistently in the Sternheimer solve. QE recomputes `dnsscf` on iterations after the first in `solve_linter.f90`:

```text
if (lda_plus_u .and. iter /= 1) dnsq_scf(...)
```

### 5. SCF/mixed Hubbard dynamical-matrix contribution after convergence

After `solve_linter` converges for an irreducible representation, `PHonon/PH/phqscf.f90` calls:

```text
dynmat_hub_scf(irr, imode0, npe)
```

`PHonon/PH/dynmat_hub_scf.f90` adds the SCF and USPP-orthogonality Hubbard terms to `dyn`, `dyn_rec`, and `dyn_hub_scf`.

For norm-conserving logic, the key two terms are:

1. A `dpsi`-contracted term, implemented by building `dvqhbar` via `dvqhub_barepsi_us2` and then summing:

   ```text
   dyn1(ipert,imode) += wk(ikk) * <dpsi(ipert,k+q)| dV_hub_bare(imode) |psi(k)>
   ```

2. A direct occupation-response cross term:

   ```text
   dvi += conjg(dnsscf(m1,m2,is,nah,ipert)) * dnsbare(m2,m1,is,nah,icar,na)
   term(na,icar) -= dvi * effU(nt)
   dyn1 += transform_cartesian_term_to_pattern(term)
   ```

QE therefore has both a wavefunction-response contraction and an explicit `dnsscf * dnsbare` mixed term in the final dynamical matrix.

## Finite-q occupation conventions

`PHonon/PH/dnsq_scf.f90` defines the SCF first-order occupation response as:

$$
dn^{I\sigma}_{m_1m_2}(\lambda)
= \sum_{kn} w_k
\left[
\langle \psi_{nk}|S_k\phi_{I m_1,k}\rangle^*
\langle S_{k+q}\phi_{I m_2,k+q}|d\psi^{\lambda}_{n,k+q}\rangle
+ (m_1 \leftrightarrow m_2)
\right].
$$

The code uses:

```text
proj1 = <S_k phi(k,I,m)|psi(k)>
proj2 = <S_{k+q} phi(k+q,I,m)|dpsi(k+q)>
dnsscf += wk * (conjg(proj1_m1)*proj2_m2 + conjg(proj1_m2)*proj2_m1)
```

Then it fills the lower triangular part by simple symmetry and calls `sym_dns` for phonons. `sym_dns.f90` first imposes Hermiticity-like symmetrization in the local Hubbard indices, then applies small-group-of-q symmetry operations and q/-q handling. The comments and code show that QE makes the object symmetric/Hermitian in the Hubbard subspace before using it in `adddvhubscf` and `dynmat_hub_scf`.

The bare first derivative `dnsbare` is analogous, but uses `dmqsphi = Delta_{-q}(S_{k+q} phi)` instead of `dpsi`. It is symmetrized through `sym_dns_wrapper` and also stored as `dnsbare_all_modes`.

## Key comparison to ABINIT NC PAO DFPT debugging

The important QE design point is that the mixed/screening effect is not represented only by a final DDB scalar contraction. QE has three coupled mechanisms:

1. **Bare/frozen source term in Sternheimer**: `dvqhub_barepsi_us` adds the bare displacement derivative of the Hubbard potential to the linear-system RHS.
2. **SCF Hubbard response potential in Sternheimer**: `adddvhubscf` adds `-U dnsscf` as a response potential during the iterative solve. This changes `dpsi`, not just the final DDB.
3. **Final dynamical-matrix corrections**: `dynmat_hub_bare` adds the frozen/bare second derivative and first-derivative product terms; `dynmat_hub_scf` adds the converged SCF/mixed terms from `dpsi` and `dnsscf*dnsbare`.

For the ABINIT finite-q NC PAO issue, this suggests the next comparison should not focus only on local variants of the final `occ1` contraction. The QE analogue of the potentially missing large screening term is likely the self-consistent Hubbard response potential path (`adddvhubscf`) and its normalization/sign/q-pairing, because that path modifies the Sternheimer response itself.

## ABINIT-relevant diagnostic checklist derived from QE

Use the QE split as a checklist for ABINIT NC PAO finite-q DFT+U:

1. **Bare Hubbard RHS**: confirm the ABINIT H1 source contains the finite-q analogues of both QE projector-side terms, i.e. $\Delta_q$ ket-side and $\Delta_{-q}$ bra/projection-side derivatives, with the same `k -> k+q` phase convention.
2. **SCF Hubbard response potential**: verify that ABINIT's first-order Hubbard potential from `occ1` is added inside the Sternheimer iteration, not only after convergence as a DDB insertion.
3. **Response potential scale**: instrument the norm/energy contribution of the first-order Hubbard potential applied to `dpsi` and compare it with QE's `adddvhubscf` formula `-U dnsscf |Sphi(k+q)><Sphi(k)|psi(k)>`.
4. **Final mixed DDB term**: compare ABINIT's mixed contraction with QE's two pieces in `dynmat_hub_scf`: the explicit `<dpsi|dV_hub_bare|psi>` contraction and the direct `conjg(dnsscf)*dnsbare` term.
5. **Frozen D2 term**: compare ABINIT's corrected fixed-wavefunction frozen D2 with QE's `dynmat_hub_bare` form: $(0.5\delta-n)d^2n_{bare} - dn_{bare}^*dn_{bare}$. The local fixed-wavefunction FD validation in ABINIT maps most closely to this stage.
6. **Symmetry/Hermiticity timing**: QE symmetrizes `dnsscf` and `dnsbare` before using them in final matrix assembly. ABINIT should distinguish whether its finite-q `occ1` is a raw directional-q object or the symmetrized q-star object expected by the DDB contraction.

## Most relevant QE files

```text
PHonon/PH/phq_readin.f90        # feature restrictions and citation message
PHonon/PH/phq_setup.f90         # effU setup
PHonon/PH/phq_init.f90          # lr_orthoUwfc, dnsq_bare, dnsq_orth
PHonon/PH/dnsq_bare.f90         # first bare occupation derivative
PHonon/PH/dynmat_hub_bare.f90   # frozen/bare Hubbard dynamical matrix
PHonon/PH/solve_linter.f90      # Sternheimer loop; calls dvqhub_barepsi_us and dnsq_scf
PHonon/PH/dvqhub_barepsi_us.f90 # bare Hubbard potential times psi, added to RHS
LR_Modules/response_kernels.f90 # calls adddvhubscf during Sternheimer iterations
LR_Modules/adddvhubscf.f90      # SCF Hubbard response potential times psi
PHonon/PH/dnsq_scf.f90          # first SCF occupation response dnsscf
PHonon/PH/dynmat_hub_scf.f90    # SCF/mixed Hubbard dynamical matrix
PHonon/PH/sym_dns.f90           # phonon occupation-response symmetrization
PHonon/PH/syme_dns.f90          # electric-field occupation-response symmetrization
```

## Bottom line

QE's finite-q DFPT+U implementation treats Hubbard screening as a self-consistent response-potential problem plus final dynamical-matrix terms. The final mixed matrix term is only one part of the implementation. For ABINIT, the small `~1e-3 Ha` final mixed-only diagnostics after the corrected frozen-D2 term should be followed by a direct audit of the first-order Hubbard potential inserted in the Sternheimer solve: its construction from finite-q `occ1`, its sign and factor, and its `k/k+q` projector convention relative to QE's `adddvhubscf`.
