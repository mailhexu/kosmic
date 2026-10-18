---
artifact_role: knowledge
audience: both
title: PSML Full-Relativistic (lj) j-Averaging and PAO/KB Handling
id: psml_full_relativistic_j_averaging
date: 2026-08-02
project: siesta_simplex_basis
status: draft
validated_by: source_inspection
tags: [pypao, psml, siesta, relativistic, fr, lj, basis, kb-projector, radial-solver]
related_files:
  - siesta_dev/siesta/Src/ncps/src/m_ncps_translators.f90
  - siesta_dev/siesta/Src/atom.F
  - pypao/src/pypao/psml.py
  - pypao/src/pypao/session.py
  - pypao/src/pypao/basis/kb.py
links_to: [pypao_ion_serialization_parity, psml_external_kb_projectors]
linked_from: []
type: Project Knowledge
math_provenance: missing
math_provenance_reason: "psml_full_relativistic_j_averaging.md display math requires one MathDoc marker per equation"
---

# PSML full-relativistic (lj) → scalar handling

## The problem

pypao's parser is **set-blind**: it never reads the `set` attribute, so it iterates ALL
`<semilocal-potentials>`/`<nonlocal-projectors>` blocks and overwrites `v_ps[l]`. This is
silently wrong for FR in two distinct ways (no exception raised):

1. **lj-only** (e.g. `withf/PBE_FR/La.psml`, ONCVPSP-4.0.1 FR): one `set="lj"` block,
   `<slps l=.. j=..>` (`j=l±1/2`; l=0 → only 1/2). The two j-channels per l collapse to one
   (last-parsed wins). `PSMLNonlocalProjector` has no `j` field, so j is discarded.
2. **SR+SO split** (e.g. the fixture `ABACUS-orbitals/generated_v3/Dojo-NC-FR/PBE/Si.psml`,
   ONCVPSP-3.3.1 FR, full periodic table H…Bi): `set="scalar_relativistic"` PLUS
   `set="spin_orbit"` blocks (both l-indexed, no j), no `lj`. The SO block (p,d) **overwrites**
   the SR block's p/d. Demonstrated on Si: `v_ps[1][1]`=−0.056 (the SO *difference*) instead
   of the SR value −3.50; only `v_ps[0]` (s) is correct (SO has no s channel). KB lists also
   collide (8 SR + 7 SO projectors flattened, set lost).

## PSML set taxonomy

`set` attribute on `<semilocal-potentials>`/`<nonlocal-projectors>`:
`scalar_relativistic` (SET_SREL), `non_relativistic` (SET_NONREL), `spin_orbit` (SET_SO,
the l-indexed SO *difference*), `lj` (SET_LJ, raw (l,j)). Pure-SR files carry SREL only;
SR+SO-split FR files carry SREL+SO; lj-only FR files carry lj. SIESTA's docs recommend the
SREL+SO+lj ("three-set") file.

## How SIESTA converts lj → scalar (authoritative)

`ncps_psml2froyen` (`m_ncps_translators.f90`), `relativity="dirac"` branch with only lj
present (`:398-477`): j-average in-house per-l into `vdown` (scalar) and `vup` (SO):

$$
V_l^{\mathrm{SR}}(r)=\frac{(l+1)\,V_{l,j=l+1/2}(r)+l\,V_{l,j=l-1/2}(r)}{2l+1},
\qquad V_{s}^{\mathrm{SR}}=V_{s,1/2}
$$

$$
V_l^{\mathrm{SO}}(r)=\frac{2}{2l+1}\bigl(V_{l,j=l+1/2}(r)-V_{l,j=l-1/2}(r)\bigr)\quad(l>0)
$$

Stored in Froyen `r·V` Rydberg form (`vdown = 2·r·V^SR`, `:470-472`). If the file already
has SREL+SO, read directly (`:370-394`). `relativity="scalar"` requires SREL and **dies**
if absent — no lj fallback (`:264-267`). libpsml `sets.md`: SET_SREL = "lj averaged over j".

## PAOs: scalar Schrödinger, no Dirac term

`atom.F` PAO generation uses **only** the scalar `vps` (=`vp%vdown/r`, `:2523`); `vps_u`
(SO) is never used for PAOs. The solver `schro_eq` (`atom.F:1655-1657`) is **plain
non-relativistic Schrödinger**: `vtot = vps + ve + l(l+1)/r²`, `h = vtot·s + a²/4`, legacy
Numerov eigensolver `egofv`. Grep for `koelling|harmon|cvel|bsc|B(r)|mass.velocity` in
atom.F = zero matches. `irel` only branches the XC call, never the radial operator. SR vs FR
collapse to the same scalar `vps` upstream → identical solver. The `j` quantum number never
enters the PAO path.

**Consequence for pypao:** once lj semilocal potentials are j-averaged into the scalar
`v_ps` dict, pypao's whole pipeline (Schrödinger Numerov `solver.py`, SCF, all basis
generators, `compute_vlocal`, `.ion` writers) is reused **unchanged**. No Dirac /
Koelling-Harmon solver is needed — matches SIESTA exactly, and matches the existing SR
parity.

## KB projectors: regenerate from scalar vps, do NOT j-average

`atom.F` does **not** j-average KB projectors. Three branches:
1. offsite-SOC (`dirac`) run (`:3070`): use raw SET_LJ projectors in `nlefsm_SO_off`.
2. scalar run with explicit SET_SREL projectors (`:3084`): use them.
3. scalar run with only SET_LJ projectors (`:3091-3103`): **die** ("generation of
   scalar-relativistic part is not available yet") — UNLESS `psml_kb_fallback` (`:612-629`):
   regenerate KB from the j-averaged scalar `vps` via `KBgen`.

pypao already has `generate_kb_projectors(grid, v_ps, v_local, …)` (`basis/kb.py`) =
SIESTA's `psml_kb_fallback`. So for a scalar (basis-optimization) run on an FR file, pypao
must **ignore the external lj projectors** and regenerate KB from the j-averaged scalar
`v_ps`. Preserving raw lj projectors matters only for a future offsite-SOC objective.

## Implementation shape (set-aware parser, 3 localized changes)

1. `psml.py`: read the `set` attribute on each block; store per-set channels
   (`v_ps_sr`, `v_ps_so`, `v_ps_lj` + `j` on projectors). Add `PSMLNonlocalProjector.j`.
   Add a single `scalar_potentials()` accessor mirroring SIESTA (`m_ncps_translators.f90:
   228-303`): **SR set present → use it** (pure-SR and SR+SO-split like the Si fixture);
   **only lj → j-average** via `j_averaged_potentials()` (Finding above). Public `v_ps`
   becomes this accessor (backward-compatible for all SR tests).
2. `session.py:342,363`: `v_ps_ry` ← `scalar_potentials()`. KB: prefer the SR projector set
   if present (Si fixture has it → use `psml.kb_projectors()` filtered to SREL); else (lj-only)
   regenerate via `generate_kb_projectors(...)` from scalar `v_ps`. Never feed lj/SO
   projectors to the scalar `.ion` writer.
3. Tests: both FR conventions — `ABACUS-orbitals/.../Dojo-NC-FR/PBE/Si.psml` (SR+SO split;
   assert `v_ps[1][1]≈−3.50` not SO −0.056) and `withf/PBE_FR/La.psml` (lj; assert
   j-average numerics) + pypao-vs-SIESTA-`atom` `.ion`/basis parity on Si.

**Implemented (2026-08-02, quick task `2026-08-02-fr-psml-set-aware-parser`):** set-aware
parser landed in `pypao/src/pypao/psml.py`; `session.py` needed ZERO changes
(`kb_projectors() or generate_kb_projectors(...)` routes correctly). **SIESTA parity
validated (controlled FR-vs-SR)**: KB `ekb` bit-identical (0.000 Ry) and valence PAOs match
to ~1e-4 in both FR and SR; the only larger diff (d-pol ~4 %) is identical in the SR
control → pre-existing pypao polarization detail, not an FR regression. See
[pypao_fr_siesta_parity](pypao_fr_siesta_parity.md).

## References

- Research memo: `specs/research/2026-08-02-full-relativistic-psml-pypao.md`
- `m_ncps_translators.f90:228-303` (relativity select), `:398-477` (lj averaging)
- `atom.F:1633-1688` (`schro_eq`), `:2518-2527` (`vps` unpack), `:3546/3577` (PAO solve),
  `:612-629` (`psml_kb_fallback`), `:3066-3126` (KB set filter)
- libpsml `sets.md`, `m_psml_api.F90:688-779`, `m_psml_parsing_helpers.F90:377-379`

## Related notes

- [pypao_ion_serialization_parity](pypao_ion_serialization_parity.md) — SR parity baseline this extends.
- [psml_external_kb_projectors](psml_external_kb_projectors.md) — external-projector preservation (FR must bypass these).
