---
artifact_role: knowledge
type: reference
audience: both
status: draft
created: 2026-08-18
math_provenance: missing
math_provenance_reason: "mae-reference-dataset.md display math requires one MathDoc marker per equation"
---

# MAE reference dataset

Merged DFT reference dataset for PredictMag training/validation: `MAE_data/mae_dataset.yaml`,
built and loaded by `predictmag/mae_data.py` (CLI: `convert` / `info` / `show <id>` / `validate`).

## Schema

One record per labeled structure, keyed by `structure_id` (`stru_<N>`, N = 0–400 with 60 gaps):

| Field | Meaning | Source |
|---|---|---|
| `index` | integer N | id |
| `formula` | chemical formula | CIF `_chemical_formula_sum` (authoritative) |
| `cif` | path relative to `MAE_data/` | `my_stru/stru_<N>.cif` |
| `mae_total` | MAE label, mJ/m² | `mae_results.xlsx` sheet `mae` (full float precision) |
| `mae_onsite` / `mae_offsite` | Bruno-type decomposition | `onsite_offsite.xlsx` sheet `分析` |

Loader API: `load_records()` (list of dicts, index-sorted), `to_frame()` (pandas),
`cif_path(record)`.

## Verified invariants (2026-08-18)

- 341 labeled structures; both xlsx sheets join 1:1 on the id; all have CIFs.
- `MAE_total` in `onsite_offsite.xlsx` duplicates the `mae` sheet value (max |diff| = 4.3e-9);
  `mae_onsite + mae_offsite = mae_total` holds for every row.
- All 362 CIFs (incl. 21 unlabeled): `_chemical_formula_sum` == `_atom_site` element counts,
  occupancy 1.0, site multiplicity 1, space group P1 → raw site rows = full cell contents.
- 58 labeled structures share formulas in 27 polymorph groups (e.g. `VOBr2`: stru_6/7) —
  distinct cells, not naming errors.

## Known quirks

- **`stru_276..278` are `FeBr2`**: the xlsx `Symbols` cells hold Excel date-serial `46055`
  (auto-typed). The CIF formula is authoritative; converter warns and records the mismatch in
  `metadata.xlsx_symbols_mismatch`.
- The xlsx `mae` sheet has 685 empty padding rows (1026 nominal rows / 341 real) — filter
  `structure_id is not None`.
- `mae_data.py validate` re-runs all cross-checks; exit 0 = consistent, xlsx-Symbols mismatches
  are warnings only.

## Relation to the model

Labels for the Bruno factorization check:

$$
\mathrm{MAE} \approx -\frac{\xi_l}{4\mu_B}\,\Delta\langle L_z\rangle ,
$$

with $\xi_l$ from the `magnetic_descriptor` MemNotes target (AE Dirac + NIST datasets in
`paper/magnetic_descriptor/data/`), and the on-site/off-site decomposition providing the
factorization test target.

## References
- [[abacus-cif-quirks]] — why CIF parsing needs a real loop parser
- `predictmag/mae_data.py`, `predictmag/README.md`
- MemNotes target `magnetic_descriptor` (element SOC descriptor datasets)
