---
type: Project Knowledge
title: NC DFT+U Mixed-Strain Occupation Response (s2 Term)
description: The s2 Sternheimer term that closes spinor NC DFT+U elastic residuals against occupation-matrix finite-difference oracles, with validation protocol and red flags.
created: '2026-09-25'
updated: '2026-09-25'
project: abinit
status: draft
audience: development
artifact_role: guideline
usage_stale: false
tags: [abinit, nc-dftu, dfpt, elastic, occupation-matrix]
---

# NC DFT+U Mixed-Strain Occupation Response (s2 Term)

## Scope

Spinor NC DFT+U strain-strain density-functional perturbation theory (DFPT) assembly in ABINIT. The goal is closure of elastic residuals against occupation-matrix finite-difference (FD) oracles.

## Key identity (sympy-verified; do not re-derive)

Dudarev mixed derivative: `d²E_U/dλdμ = (U_eff/2)Tr[N^λμ(I−2N⁰)] − U_eff Re Tr[N^λ N^μ]`.
Entrywise: `N^λμ_ij = Σ_f w_f [p_λμ,i p0,j* + p0,i p_λμ,j* + p_λ,i p_μ,j* + p_μ,i p_λ,j*]`, with `p_λ = pl+dl`, `p_λμ = s2+xl+xm+d2`.
After the frozen piece (`d2`, `dl·dm`) and the five-term response piece (`pl·pm`, `dl·pm`, `pl·dm`, `xl·p0`, `xm·p0`), the only missing term is:
`ΔN^λμ_ij = Σ_f occ_weight_f [s2_i p0_j* + p0_i s2_j*]`, where `s2 = <P0|ψ^(λμ)>` comes from the mixed second-order Sternheimer solve (sources `V1U^λ`, `V1U^μ`, `V1U^λμ`, eigenvalue shifts, mixed orthonormality).

## 2n+1 boundary (critical)

`ψ_λμ` cancels from the stationary ENERGY coefficient, but NOT from the entrywise occupation matrix.
Any ψ2-free rearrangement must reassemble every V1U-source term and multiplier-shift term together; substituting the five-term closure into V2M is not legal.
Never fix residuals by global rescaling: the needed factors differ per family (`h44` −2.0x, `h11` 0.40x, `h12` sign flip).

## Validation procedure

1. Instrument `prtvol`-gated element dumps: V2MF (frozen N̂ elements) and V2MN (response N̂ elements; optional `diagnostic_key`/`diagnostic_dump` arguments on `compute_nc_dftu_v2m_response_part`). Enable dumps only at the `prtvol>=20` audit call in `m_dfpt_scfcv.F90`.
2. Run the Si Gamma `U=0.1` fixture with `prtvol 20` (single dataset); parse the dumps from the log.
3. Oracle: occupation-FD npy files `rem1_block_audit/nfd/nlm_h{11,12,44}.npy`. Compare `h44` with a 1/2 factor: the Voigt convention `η=2ε` makes the code `η4` content equal FD/2.
4. Gate: require elementwise `(atom, ipack, im, jm)` agreement before trusting any total-energy or derivative-database (DDB) number.

## Red flags

- Response N̂ exactly atom-independent, or diagonal-only per family: per-atom or off-diagonal content is missing (the s2 term).
- 1e59-scale garbage in ledger blocks: suspect a corrupted build (zero-byte shadow objects) before hunting source bugs; allocations must be source-zeroed and slot-guarded.
- Repo rule: derive with sympy and cross-check against a mock-system FD run to 1e-10 or better; never hand-derive.
