---
type: Domain Topic
id: methods/development/nist-multiplet-calibration-4f
domain: methods
audience: development
artifact_role: guideline
status: draft
summary: Calibrate DFT+U+J+B Hund (J) and orbital-polarization (B) parameters for rare-earth ions by fitting Racah parameters to NIST fine-structure levels.
triggers: [nist multiplet fit, racah parameters, hund exchange calibration, orbital polarization, 4f ion spectra]
source_project: native
source_sha256: empty
aliases: [multiplet calibration]
---

# NIST Multiplet Calibration of DFT+U+J+B Parameters

Calibrate the Hund-exchange (J) and orbital-polarization (B) parameters of a DFT+U+J+B
functional for an f-shell ion (example: Sm3+ 4f5 in SmN) against National Institute of
Standards and Technology (NIST) fine-structure levels.

## Identifiability rules

The Hubbard U (F0 monopole) is not identifiable from fixed-configuration splittings: F0 shifts
every level of a configuration uniformly; keep U from linear response or pinned policy. J maps
to the Racah parameter E1 (spin-state splitting) and B maps to E3 (orbital splitting); distinct
Racah parameters, identifiable with no collinearity. In the OP-tensor path
(`DFTB_full/Src/dftu_specs.f`, lines 1817-1835): `E1 = 7J/9`, `E3 = 10B/9`, `E2 = 0`, `F2 =
25J/6 + 1375B/21`, `F4 = 11J + 440B/7`, `F6 = (1859/150)(J - 10B)`; positivity gives `B <
J/10`, and the code clamps B at 0.099 J. Build caveat: the pilot SIESTA tree
(`siesta_DFTB/Src/dftu_specs.f`) has no op_tensor branch; it hard-codes `F4/F2 = 0.668`, `F6/F2
= 0.494`, so `E3 = 10B/9` is only a borrowed prior; check the binary's tree.

## Data reality checks

NIST ion stage N+ carries roman numeral N+1: Sm3+ is "Sm IV"; verify stage, configuration, and
term before use. Availability is limited: NIST Sm IV returns 24 levels, so two complete terms
constrain E1 and E3 well and E2 weakly; audit availability before promising a full multiplet
fit. Infrastructure: `magnetic_descriptor/scripts/fetch_nist_ions_all.py` (element-granularity
resume; verify completeness) and `extract_nist_xi_nl.py` (Lande-interval zeta fits; the
"regular" flag at interval ratio below 1.5 is a screening heuristic, not LS purity).

## Fit protocol

1. Fetch all levels of the ion configuration, config-filtered.
2. Fit in the full Fock-space determinant basis (2002 determinants for f5); build `H(F2, F4, F6,
   zeta)` by Slater-Condon rules with SymPy angular algebra; no coefficients of fractional
   parentage, no hand-derived Racah algebra.
3. Treat F0 as an unconstrained offset; fit E1, E2, E3, and optionally an effective zeta by least
   squares to the level energies.
4. Validate the pseudo SOC separately against the fitted zeta; never vary `Spin.OrbitStrength` (a
   debug knob, physical value 1.0); regenerate the pseudopotential instead.
5. Report screening honestly: parameterize `beta_k = Fk(solid)/Fk(free)` per k and separately for
   the OP coefficient; state no numeric transfer bound without host-specific evidence.
6. Seed a small solid-state confirmation grid around the fitted (J, B) at pinned U; keep manifest
   caveats on experimental anchors (field, temperature, normalization).

## Pitfalls

Do not claim J and B share one Racah parameter (J is E1, B is E3). Do not call a pure 4f5
diagonalization a configuration-mixing treatment; state the configuration-interaction and
crystal-field exclusions. One ground term's J intervals constrain only an effective zeta, not
Coulomb ratios.