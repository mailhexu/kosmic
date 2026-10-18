---
artifact_role: knowledge
confidence: 0.90
created: 2026-05-11
last_validated: 2026-10-03
updated: 2026-10-03
audience: both
usage_stale: false
evidence: [evidence/2026-10-03-fulluj-finiteq]
validation_procedure: "Actual native scalar/collinear/packed signed-q response and independent commensurate force folding; exact SymPy phase and reciprocal-plane checks; convergent Standards/Spec review at fixed base200651d9. Historical sections retain their stated dates and scope."
project: abinit
status: stable
validated_by: source-reading-and-native-measurement
tags: [nc-dftu, dfpt, finite-q, paw-comparison, qphase]
type: Project Knowledge
---

# NC DFT+U Finite-Q Response Trace

## Context

Story 420 traces the historical non-Gamma integration; the current full-FLL source and validation delta follows.

## 2026-10-03 Full-FLL response and reciprocal NC source boundary

- The response uses the shared full matrix Hessian and complex bilinear for scalar and packed-spinor atomic perturbations. One-sided generic-q directions remain complex/non-Hermitian; explicit opposite-q ownership is completed after both harvests. Required native time-reversal metadata reconstructs the missing occupation arm in-place without Hermitian projection. Existing static/fixed-occupation/projector/MPI guards still delimit the envelope.
- Multi-atom force folding first exposed a separate GS atom-index boundary: NC gradients are input-order, while native grnl is type-sorted. The atindx1 correction restores interleaved Li/F force covariance; prior .174760/.147203 DDB attribution used corrupted force data and is withdrawn. See [force/energy consistency](nc-dftu-force-energy-consistency.md).
- The signed Brillouin-boundary defect was in two coupled dfpt_atm2fft NC branches, not the Hubbard Hessian: qeq05 zerosym used zero-based G-derived values as one-based FFT planes. At +q it deleted absent planes; at -q it deleted present coreG4 and local-sourceG8 planes. dfpt_looppert routes both vpsp1 and xccc3d1 through this function for nc_xccc_gspace1. Preserving the complete shifted spherical support in BOTH NC branches is required; correcting only the core leaves a .01858 raw DDB mismatch. Gamma and PAW conventions are unchanged. A cplex-only trial was ineffective and reverted; active DFPT Hartree izero0 means its similar legacy plane code is not the carrier.
- Matched LiF PW92 LDA UPF physical evidence (both Li/F NLCC), noSOC ecut20/ecutsm.5 U=.1/J=.005: scalar/packed genericq1/3 full36 force-folding errors1.43e-6/6.20e-7 on exact3x1x1 supercells and closed shifted3x2x2 primitive stars; strict selfq1/2 errors7.71e-7/7.40e-7 on exact2x1x1 supercells and shifted2x2x2 stars. No ASR, tensor symmetrization or fitted scale. Selfq signed-q covariance5.97e-8 at GS1e-22/RF1e-20; native reciprocity9.94e-9 and independent FD reciprocity floor~8e-7. Independent-branch/TR discrepancy1.68e-7. All six final-source raw signed-q controls (including explicit collinear) pass J0dc0/dc1<=1.18e-11 and exact-input ordinary k-MPI2<=1.48e-11; physical Spec/Standards R0 certification review passes for Story571.
- Source Standards/Spec R2 and physical Standards/Spec R0 converge PASS with zero blockers; Story571 complete after scoped evidence/canonical gates. Explicit collinear signed full36 force-folding errors<=7.22e-7 (selfq) and3.89e-7 (genericq); t244..250 pass7/0, post-header t2501/0. Both signs are explicitly asserted against2e-6 FD/2e-7 raw covariance pins. Native/control and collinear FD producers are a0e3599; scalar/packed FD producers are valid pre-incident239e4b59, recorded in the raw/certificate data with two measured final-binary GS-equivalence controls. No fabricated150-state final-binary replay. Portable suite regressions do not replace matched-UPF force physics; see the [paired feature matrix](nc-dftu-porting-feature-matrix.md).


## 2026-08-12 Spinor Finite-Q Storage Implementation

- `compute_nc_dftu_response_from_wfs` receives distinct input and output bases: `kg0/npwarr0/kpt` for $k$ and `kg1/npwarr1/kpt+q` for $k+q$.  It builds `phi0_kpg_tot` and `phi1_kpg_tot` on those respective bases, forces the response projection to `istwf=1` at nonzero $q$, and retains its complex real/imaginary components in packed `occ1` and `V1`.
- With `nspinor=2`, the localized response is accumulated in the shared uu/dd/ud/du order using a combined orbital-spin index.  The Dudarev linearized potential is the direct matrix derivative $V^{(1)}=-U_{\mathrm{eff}}N^{(1)}$; it does not transpose orbital or spin blocks.
- `m_dfpt_scfcv` holds independently computed native `+q` and `-q` `nc_dftu_data_type` outputs and evaluates their packed block-adjoint residual before density reconstruction.  The diagnostic never synthesizes a partner by transposing a local object.
- Verification: `tests_nc_dftu_spinor_response` rejects an altered partner block and confirms that the packed potential preserves the block adjoint. The two-rank NiO $q=(1/4,0,0)$ smoke ended with `Calculation completed.` and initially reported $\|\Delta N\|_\infty=1.03947883\times10^{-17}$ for `occ1` and $3.05609487\times10^{-18}$ for `V1`. Its short SCF run is deliberately unconverged, so later residuals are diagnostics rather than q-star validation.
- Story 503 completed the active native-q-star DDB path, including the packed frozen-projector curvature and eight-rank test. See [nc-dftu-spinor-finite-q-frozen-curvature](nc-dftu-spinor-finite-q-frozen-curvature.md) for the current evidence boundary.

## Superseded Gamma-Only Implementation

Before the response-storage and frozen-curvature work, `m_dfpt_vtorho.F90` rejected NC DFT+U DFPT when `qne0` was true with the diagnostic `NC DFT+U DFPT source currently supports only Gamma phonons`.
- `dfpt_vtorho` initializes NC response data with the native `cplex` value, but calls `compute_nc_dftu_response_from_wfs` with only the ground-state G-sphere inputs: `cg`, `cg1`, `kg`, `npwarr(:,1)`, `kpt_rbz`, `mpw`, and `istwfk_rbz`.
- `src/66_nc_dftu/m_nc_dftu.F90::compute_nc_dftu_response_from_wfs` therefore uses the same `npw_k`, `kg_k`, `kpt(:,ikpt)`, and `istwfk(ikpt)` for both `psi0` and `psi1` projections.
- Gamma explicit displacement terms use `build_nc_dftu_displacement_dphi_gamma`, which differentiates a PAO projector in the same basis by multiplying by `-i 2*pi (k+G)_idir`.
- `src/72_response/m_dfpt_cgwf.F90` adds the NC +U first-order source after `getgh1c` only when `npw == npw1`; this prevents finite-q source application where `psi0(k)` and the response vector in the `k+q` basis have different plane-wave lists.
- `src/66_wfs/m_nc_dftu_hamiltonian.F90::apply_dftu_h1_displacement_nc` builds one projector set from `gs_hamkq%kpt_k` and `gs_hamkq%kg_kp`, projects `cwave0` with that same set, and writes the source in the same `npw` basis.

## Native Finite-Q Metadata Owners

- `dfpt_vtorho` receives `qphon`, `cgq`, `kg1`, `npwar1`, `mpw1`, `mkqmem`, and `mk1mem` for ground-state and first-order wavefunctions at `k+q`.
- `dfpt_vtorho` constructs `kpq = kpoint + qphon` for atomic phonon perturbations and calls `getgh1c_setup` with both `kpoint` and `kpq`.
- `dfpt_scfcv` calls `dfpt_vtorho` once for `+q`, and when Kramers reconstruction is needed, calls it a second time for `-q` with `cg_mq`, `kg1_mq`, `npwar1_mq`, `ylm1_mq`, and `qphon_mq`.
- `dfpt_scfcv` mixes `+q` and `-q` second-order arrays as real/imaginary components before final DDB assembly.

## Required Finite-Q Data Model

- Occupation response must project `psi0(k)` with PAO projectors built from `(k, kg, npwarr)` and project `psi1(k+q)` with PAO projectors built from `(k+q, kg1, npwar1)`.
- The explicit displacement projector derivative has two appearances. In the localized occupation response it follows the PAW `pawaccrhoij(option=2)` pattern and is a symmetric derivative of the projector overlap on the zero-order localized-density side. In the first-order source operator it appears on both the input/right `k` projection and the output/left `k+q` projector expansion.
- `occ1` and `V1` must use `cplex=2` for non-Gamma q; Gamma can remain `cplex=1` or use the same complex path with zero imaginary part.
- MPI reductions must keep the existing collective-order fix: all band ranks enter projection reductions before non-owner ranks skip accumulation.

## PAW Finite-Q Reference Equations

The PAW reference path is `src/72_response/m_dfpt_mkrho.F90::dfpt_accrho`, which calls `src/65_paw/m_paw_occupancies.F90::pawaccrhoij` with `option=2` for first-order `rhoij`. For finite q, `pawrhoij%qphase=2`; the first phase block stores the real part and the second phase block stores the imaginary part of the response carrying the native finite-q phase.

For scalar spin and one packed pair `(i,j)`, the wavefunction-response part is accumulated as:

$$
\rho^{(1),\mathrm{wf}}_{ij}(\mathbf q)
= w_{\mathbf k} f_{n\mathbf k}
\left[
c^{(0)}_{i,n\mathbf k} c^{(1)}_{j,n\mathbf k+\mathbf q}
+ c^{(0)}_{j,n\mathbf k} c^{(1)}_{i,n\mathbf k+\mathbf q}
\right],
$$

where `cwaveprj` provides the zero-order PAW projections and `cwaveprj1` provides the first-order projections. In complex storage, the corresponding imaginary component is stored in the qphase-imaginary block rather than by dropping one of the two terms.

The explicit projector-derivative part is accumulated separately as:

$$
\rho^{(1),\mathrm{proj}}_{ij}(\mathbf q)
= w_{\mathbf k} f_{n\mathbf k}
\left[
\partial_\lambda c^{(0)}_{i,n\mathbf k} c^{(0)}_{j,n\mathbf k}
+ c^{(0)}_{i,n\mathbf k} \partial_\lambda c^{(0)}_{j,n\mathbf k}
\right].
$$

Thus the PAW counterpart is two-sided in the localized pair indices even for finite q. A one-sided NC dense-orbital formula is not PAW-consistent.

## NC Dense-Orbital Formula Matching PAW

The dense NC analog should keep the full matrix rather than PAW's triangular packed pair, but it should preserve the same two-sided first-order structure. Let

$$
P^0_{m,n\mathbf k}=\langle \phi_{m,\mathbf k}|\psi^0_{n\mathbf k}\rangle,
\qquad
P^1_{m,n\mathbf k}(\mathbf q)=\langle \phi_{m,\mathbf k+\mathbf q}|\psi^1_{n\mathbf k+\mathbf q}\rangle,
$$

and let

$$
D_{m,n\mathbf k}^{\lambda}=\langle \partial_\lambda\phi_{m,\mathbf k}|\psi^0_{n\mathbf k}\rangle
$$

denote the frozen explicit projector derivative entering the localized occupation response. The PAW-consistent dense response is:

$$
n^{(1),\lambda}_{mm'}(\mathbf q)=
\sum_{n\mathbf k} w_{\mathbf k}f_{n\mathbf k}
\left[
\left(P^1_{m,n\mathbf k}(\mathbf q)+D^{\lambda}_{m,n\mathbf k}\right)
\left(P^0_{m',n\mathbf k}\right)^*
+P^0_{m,n\mathbf k}
\left(P^1_{m',n\mathbf k}(\mathbf q)+D^{\lambda}_{m',n\mathbf k}\right)^*
\right].
$$

This is exactly the structure implemented by `compute_nc_dftu_occ1_from_projections`: `proj0` is `P0`, `proj1` is `P1`, `dproj` is `D`, and both the `m` and `m'` terms are accumulated. Finite-q complex storage is represented by `occ1(1,:,:,:)` and `occ1(2,:,:,:)`, analogous to PAW's `qphase=2` real and imaginary blocks.

The first-order source is a different object: it maps an input ground-state wavefunction in the `k` basis to an output vector in the `k+q` basis. Its separable form must use output-side projectors `\phi_{m,\mathbf k+\mathbf q}` and output-side explicit derivatives for the left projector, while its right projections are built from the input `k` side. This distinction should be explicit in the paper; the occupation-response derivative and source-left derivative are not the same array.

## Historical Implementation Consistency Check

- The former separate-basis and paired-response changes remain the required precursor to the active finite-q path.
- `m_dfpt_scfcv.F90` now executes the explicit mixed-DDB insertion after native response pairing; it does not retain the former disabled block.
- The active supported route is static Dudarev, fixed-occupation, same-site atomic finite-$\mathbf q$ response with `istwfk(:)=1` and no spinor MPI. It was revalidated by the U=0/U-on and eight-rank `t119` DDB fixtures.

## Historical Implementation Implications

- `compute_nc_dftu_response_from_wfs` needs separate `kg0/npw0/mpw0/kpt0/istwf0` and `kg1/npw1/mpw1/kpt1/istwf1` metadata rather than a single G-sphere.
- `dfpt_vtorho` must pass `cgq`/`kg1`/`npwar1` or equivalent finite-q descriptors into NC +U response construction.
- `apply_dftu_h1_displacement_nc` needs a finite-q sibling or generalized API that can project `cwave0` from the `k` basis while accumulating the source in the `k+q` basis.
- The `npw == npw1` guard in `dfpt_cgwf` can only be removed after the source API accepts separate input and output bases.
- The paper equations should distinguish three objects: the two-sided localized occupation response, the source operator with left/output and right/input projector derivatives, and the DDB response-energy contraction. Collapsing these into one finite-q derivative statement hides implementation errors.

## First Fixture Candidate

- Start from the existing compact NiO NC DFT+U DFPT fixture and change only the phonon q-point after confirming ordinary NC DFPT without +U is stable at that q.
- Use U=0/no-U controls before accepting nonzero-U diagnostics.
