---
artifact_role: knowledge
audience: both
confidence: 0.9
created: 2026-06-05
last_validated: 2026-06-06
validation_procedure: "Compared ABINIT ordinary norm-conserving non-local DFPT code paths with NC PAO DFT+U DFPT source, scalar DDB, and frozen-D2 paths; rebuilt ABINIT and reran the NiO q06 finite-q DFPT surface validation with MPI-20."
project: abinit
status: stable
tags: [nc-dftu, dfpt, nonlocal, paper, ddb]
type: Project Knowledge
---

# NC DFT+U vs ordinary NC non-local DFPT implementation comparison

## Core distinction

ABINIT's ordinary norm-conserving non-local DFPT path and the NC PAO DFT+U DFPT path use the same separable-operator plumbing, but they do not have the same algebra.

Ordinary NC non-local DFPT differentiates a fixed pseudopotential operator:

$$
\hat V_{\mathrm{nl}} = \sum_a \sum_{ij} |\beta_i^a\rangle D_{ij}^a \langle \beta_j^a|.
$$

NC PAO DFT+U differentiates a separable PAO operator whose coefficient matrix is the Hubbard functional derivative:

$$
\hat V_U = \sum_a \sum_{mm'} |\phi_m^a\rangle V_{mm'}^a[n] \langle \phi_{m'}^a|.
$$

The shared separable form makes the ordinary non-local path the right reference for source placement, `gvnlx1` bookkeeping, `d2nl_k` sign/factor conventions, and DDB bucket placement. It is **not** a license to tune the DFT+U term by empirical prefactors because DFT+U adds occupation-response and frozen-PAO chain-rule terms that ordinary non-local DFPT does not have.

## Implementation map

- Ordinary source path:
  - `src/72_response/m_dfpt_cgwf.F90` calls `getgh1c` to build the ordinary first-order source.
  - `src/72_response/m_dfpt_nstwf.F90` documents that `getgh1c` gives the minus non-local contribution and then contracts `gvnlx1` with the response wavefunction.
  - The scalar non-stationary contribution accumulates through `dotprod_g`/`dotprod_g_batch_full` into `d2nl_k` with the native `two*wtk*occ` factor and ABINIT's stored imaginary-part convention.
- Ordinary frozen non-local path:
  - `src/72_response/m_d2frnl.F90` computes frozen-wavefunction non-local contributions.
  - `src/95_drive/m_respfn_driver.F90` assembles `d2nfr = d2lo + d2nl` for NC calculations, calls `dfpt_gatherdy`, then writes `d2matr` through `ddb%set_d2matr`.
- NC DFT+U source path:
  - `src/72_response/m_dfpt_vtorho.F90` builds `occ1` and `V1` and attaches the NC response object to the response Hamiltonian.
  - `src/72_response/m_dfpt_cgwf.F90` calls `apply_dftu_h1_displacement_nc(..., apply_v1=.true.)` after `getgh1c` for both `gh1c` and `gvnlx1`.
  - `src/66_wfs/m_nc_dftu_hamiltonian.F90` explicitly forms `V1*proj`, `V0*dproj`, and `dphi*V0*proj`, with source finite-difference diagnostics.
- NC DFT+U DDB path:
  - `src/72_response/m_dfpt_nstwf.F90` can use `apply_dftu_h1_displacement_nc(..., apply_v1=.false.)` in the same scalar non-stationary contraction used by ordinary non-local DFPT.
  - `src/72_response/m_dfpt_scfcv.F90` builds frozen partner responses, contracts `compute_nc_dftu_response_energy_pair`, computes `compute_nc_dftu_frozen_d2_energy_from_wfs`, and inserts mixed plus frozen terms into `d2nl`.
  - `src/66_nc_dftu/m_nc_dftu.F90` response-energy pair delegates to `hubbard_response_energy`; frozen D2 now keeps both `ddproj` and `cross` pieces.

## Diagnostic ledger

The paper section records the useful ledger:

$$
D_{\lambda\mu}^{U}
=
D_{\lambda\mu}^{U,\mathrm{bare\;H1}}
+D_{\lambda\mu}^{U,\mathrm{mixed}}
+D_{\lambda\mu}^{U,\mathrm{fr}}.
$$

This ledger should drive further debugging:

- `bare H1`: response-wavefunction contraction with the fixed-potential PAO derivative operator, compared against ordinary non-local `d2nl_k` conventions.
- `mixed`: dense Hubbard response-Hessian contraction between two first-order PAO occupation responses.
- `fr`: frozen PAO curvature at fixed ground-state Hubbard potential.

Any proposed fix should first identify which ledger term is missing, duplicated, or stored with the wrong orientation. Blind sign/factor sweeps are not evidence.

## 2026-06-06 q06 finite-q validation and band update

The NiO q06 finite-q production cleanup localized the remaining discrepancy to response-time ownership of the ordinary Hamiltonian action. The generic NC DFT+U ground-state Hamiltonian contribution in `getghc` must be skipped when a response NC DFT+U object with allocated `V1` is active; otherwise the response path double-counts the ground-state `H0+U` action already represented in the DFPT source/response flow. Ground-state use remains enabled when no response `V1` is allocated.

The production-clean source also keeps the explicit frozen PAO D2 bucket out of `dfpt_scfcv` for this finite-q path: the corrected analytic frozen-curvature routine owns the `ddproj + cross` accounting, while the final DDB mixed bucket should insert only the mixed response-energy contraction. The manual scalar H1 D2 insertion in `dfpt_nstwf` stays removed because split tests showed it duplicated existing accounting rather than fixing the q06 residual.

Clean validation used:

```bash
make
mpirun -np 20 ../../build/src/98_main/abinit dfpt_q06.abi > dfpt_q06_mpi20_clean_final.stdout 2>&1
```

The final q06 spectrum at `qpt 0.5 0 0.5` was:

$$
156.7111,\;156.7111,\;240.5884,\;321.5633,\;321.5633,\;388.3414\;\mathrm{cm}^{-1}.
$$

The finite-displacement target for the same q point is:

$$
156.0393,\;156.1840,\;240.9628,\;318.1671,\;318.2683,\;394.0388\;\mathrm{cm}^{-1}.
$$

The clean run completed with `0 WARNINGs` and `5 COMMENTs`; `.F90` LSP diagnostics were unavailable in this workspace, so compiler/build validation is the source-level gate.

After committing the production fix, the two-atom NiO `tests/permanent/nio_fm_2atom` full-band workflow was regenerated by rerunning all eight ABINIT DFPT q points, then `mrgddb`, `anaddb`, and the three-way plotting script. The updated `anaddb` X-point interpolation is:

$$
150.0417,\;150.0417,\;236.0499,\;325.2444,\;325.2444,\;391.5507\;\mathrm{cm}^{-1}.
$$

At X, FD minus ABINIT has RMS `5.81 cm^-1` and maximum absolute difference `7.08 cm^-1`; QE minus ABINIT has RMS `7.86 cm^-1` and maximum absolute difference `11.39 cm^-1`. Across the full 101-point path, FD minus ABINIT has RMS `15.21 cm^-1` and maximum absolute difference `54.17 cm^-1`; QE minus ABINIT has RMS `48.01 cm^-1` and maximum absolute difference `264.42 cm^-1`. This supports the q06/X finite-q correction while preserving a full-path QE projector/workflow caveat.

## Paper update

Added `\section{Comparison with ordinary norm-conserving non-local DFPT}` to `papers/DFTU_NC/main.tex` before `\section{Current DFPT Scope}`. The section includes equations, a side-by-side implementation table, source/DDB/frozen comparisons, and a warning that finite-q DDB production remains under revalidation until the full term ledger is verified.

Verification: `make` in `papers/DFTU_NC` completed and produced `main.pdf`. Tex LSP diagnostics were unavailable because `texlab` is not installed.
