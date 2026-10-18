---
artifact_role: knowledge
type: reference
audience: both
status: draft
created: 2026-07-09
updated: 2026-07-13
tags: [abacus, tb2j, hamiltonio, soc, mae, workflow, scalar-projector]
related:
  - "[[lcao_hamiltonian_output]]"
  - "[[abacus_soc_in_lcao_codepath]]"
  - "[[abacus_nspin4_spinor_layout]]"
  - "[[cri3_story5_validation_result]]"
math_provenance: missing
math_provenance_reason: "one_dft_soc_tb2j_workflow.md display math requires one MathDoc marker per equation"
---

# One-DFT ABACUS SOC Workflow for TB2J

ABACUS emits the SOC-only real-space Hamiltonian as `hrs1-soc_nao.csr` alongside the total `hrs1_nao.csr` and overlap `srs1_nao.csr` in one `OUT.<suffix>` directory. Both keywords are required for the single-step path:

- `out_mat_hs2 1` writes the total H(R) and S(R) (`hrs1_nao.csr`, `srs1_nao.csr`);
- `out_mat_hs2_soc 1` writes the SOC-only H(R) (`hrs1-soc_nao.csr`).

The SOC-only container is gated on `out_mat_hs2_soc && nspin == 4 && lspinorb`, so there is no extra allocation when the output is disabled or the run is non-SOC.

## How the SOC-only H(R) is built (independent scalar projector)

`hrs1-soc_nao.csr` is the direct SOC contribution at the configured setting:

$$
H_{\rm SOC\text{-}only} = H(\text{configured SOC}) - H_{\rm scalar}
$$

The scalar projector is reconstructed independently, not read off a spin block:

- deep-copy the raw fully-relativistic PP data;
- apply the existing scalar-relativistic reduction `average_p(..., false)` plus `complete_default`, producing an independent scalar Beta/D and a freshly built two-center overlap table;
- accumulate the configured-SOC and scalar nonlocal operators through the same code path;
- write the direct difference.

This supersedes an earlier `d_delta = d_so - d_scalar` spin-block-shortcut description. Under a shared frozen density the result is exact: $H_{\rm SOC\text{-}only} = H_{\rm total\text{-}SOC} - H_{\rm frozen\text{-}noSOC}$ to ~`1e-7 eV`.

## HamiltonIO 0.3.8 parsing

HamiltonIO 0.3.8 consumes the files through the public `AbacusSingleStepSOCParser`:

- reads total H from `hrs1_nao.csr`, SOC H from `hrs1-soc_nao.csr`, S from `srs1_nao.csr`;
- requires the SOC file instead of silently falling back;
- uses a strict real-format CSR reader (`read_csr_new_format`);
- checks SOC and total `nbasis`/`Rlist` alignment (exact H alignment);
- builds `HR_full`, `HR_soc`, and `HR_nosoc = HR_full - HR_soc` with `split_soc=True`.

Overlap handling: the S(R) R-set is a subset of the H(R) R-set (e.g. 17 vs 19 vectors on CrI3). The comparison zero-fills the SR subset onto the canonical H R-set before differencing; it never invents H blocks. Overlap equality is then exact (`0.0`).

The old two-run path remains available as `split_soc="two"` / `AbacusSplitSOCParser` with `path_nosoc` + SOC path.

## TB2J consumption

- `abacus2J.py --split_soc single` for exchange from one SOC run;
- `gen_exchange_abacus(..., split_soc="single")` for programmatic exchange;
- `abacus_get_MAE(path_single=..., split_soc="single")` for MAE using the same split Hamiltonian path.

Requirements: TB2J needs Python >= 3.8 and HamiltonIO >= 0.3.8.

## Frozen vs relaxed density (QA distinction)

- Frozen-density comparison (shared converged no-SOC charge, one SCF iteration per orientation): the decomposition is exact. H error ~`1e-7 eV`, S error `0`, MAE difference `3.01e-6 meV`, J/DMI max `0 meV` over 194 rows.
- Independent-SCF comparison (separately converged SOC and no-SOC SCFs): MAE can differ by tens of percent because the densities relax differently. This is a density-relaxation effect, not a decomposition defect. Do not expect independently relaxed SOC/no-SOC SCFs to match MAE.

## Validation (2026-07-13)

- ABACUS: 5 focused CTests pass plus a successful `abacus_basic_para` build.
- HamiltonIO: 107 tests pass (0.3.8).
- TB2J: 10 tests pass (0.9.17).
- Runtime evidence under `/home/hexu/projects/abacus_dev/.tmp/soc-split-fix/` (scratch, not committed).

Packages are local source trees only, run via `uv run --no-cache --no-project --with <local path>`. Nothing has been committed, published, or released.

Notes:
- `out_mat_hs2`/`out_mat_hs2_soc` are not gamma-only workflows; use a non-gamma k-point setup.
- Full-relativistic pseudopotentials (`has_so=1`) and consistent `suffix`, `kmesh`, `Rcut`, and magnetic atom choices are required across exchange/MAE/rotate/merge comparisons.
