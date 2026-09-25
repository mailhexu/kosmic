---
type: Project Knowledge
title: NC+U Elastic Element-Level V2M Adjudication
description: Localize spinor NC DFT+U elastic DDB residuals by comparing per-element V2MF+V2MN occupation dumps against the occupation-FD oracle.
created: '2026-09-25'
updated: '2026-09-25'
project: abinit
status: draft
audience: development
artifact_role: guideline
usage_stale: false
tags: [abinit, nc-dftu, elastic, ddb, v2m, fd-oracle]
---

# NC+U Elastic Element-Level V2M Adjudication

## Scope

Use to localize elastic-DDB residuals in the ABINIT spinor NC DFT+U strain
response to individual occupation-matrix elements. Story 508 / REM-1.

## Preconditions

- Binary: `abinit_dev_clean/build_wann/src/98_main/abinit`. Rebuild with
  `rm -f build_wann/src/<module>.o && rtk proxy make -j10` from `build_wann`.
  The trailing `cd: tests` make error is benign.
- FD oracle: `/scratch/uscan/elastic_diag/rem1_block_audit/nfd/nlm_h{11,12,44}.npy`,
  shape `[2,norb,norb,natom,4]`, U=0.1 Si Gamma, ETA=6.25e-4. Scale the h44
  array by 1/2 (eta=2*epsilon Voigt convention).
- Element dumps behind `prtvol 20`: `V2MF` (frozen) and `V2MN` (response;
  commit ca7bd55, optional `diagnostic_key`/`diagnostic_dump` args of
  `compute_nc_dftu_v2m_response_part`, enabled only at `m_dfpt_scfcv.F90:2409`).

## Procedure

1. Copy the Si Gamma U=0.1 fixture `rem1_block_audit/si_gk_u.abi`. Set
   `prtvol2 20`. Run single-rank with
   `ABI_PSPDIR=<tree>/tests/Pspdir abinit si_gk_u.abi > si.log 2>&1`.
2. Parse BOTH dump formats. The field orders differ:
   - `V2MF iat ipk im jm re im idl ipl idm ipm: <vals>` (element indices
     first, block key last);
   - `V2MN idl ipl idm ipm iat ipk im jm re im: <vals>` (block key first).
   Keep the LAST occurrence per key. The routines run multiple times per
   block.
3. Block keys (natom=2): h11=(1,5,1,5), h12=(1,5,2,5), h44=(1,6,1,6).
   ipert natom+1..natom+6 maps to Voigt indices 1..6.
4. Compare `V2MF+V2MN` against the FD oracle elementwise (complex). Report
   max and rms deviation per family, plus top offenders with a
   frozen/response/FD decomposition.
5. Sanity gates: all 36 `[AUDIT-piece]` blocks are finite. DDB max
   |C - C^T| is about 1e-7.

## Known verdict (2026-08-28)

Max deviations: h11 1.67, h12 0.80, h44 1.23. All defects sit in the
response part. The response N-hat is atom-independent, diagonal-only per
family, and zero in packs 3-4. The needed factors are -2.0x, 0.40x, and a
sign flip. No rescale closes the gap. The psi2-free (pl,pm,dl,dm,xl,xm)
closure is structurally incomplete. The fix requires a sympy Lagrangian
2n+1 derivation (repo rule: never hand-derive), not empirical tuning.
See story 508 and Session 74 in the abinit MemNotes log.
