---
type: Domain Topic
id: tb2j/development/mft-curvature-probe-protocol
domain: tb2j
audience: development
artifact_role: guideline
status: draft
summary: Certify LKAG-type magnetic-force-theorem second-order curvature identities on toy ring models with finite differences before sympy promotion.
triggers: [MFT curvature probe, LKAG second-order identity, exchange response derivation, frozen occupation FD check]
aliases: [curvature probe protocol]
outcome: 
requires_procedures: []
governed_by: []
uses_knowledge: []
supported_by: []
supersedes: []
evidence: []
source_project: tb2j
source_sha256: c60c63033b256797bdb0a06f330036bb5bce119d3832c5c0644741905bda46be
---

# MFT Curvature Probe Protocol

Certify a second-order magnetic force theorem (MFT) identity of Liechtenstein-Katsnelson-Antropov-Gubin (LKAG) type on a toy tight-binding ring before promoting it to an assertion-checked sympy script in `TB2J/docs/sympy/`.

## Setup

The reference H0 is a ring or supercell: spin-independent hoppings plus local exchange fields `B(cosΘ_a σ_z + sinΘ_a σ_x)` at angles Θ_a (spiral pattern) or 0 (collinear). Frozen occupations `f_n = f(ε_n^0)` at fixed μ are the force-theorem object. Perturbations are local transverse rotations in each site's local frame: out-of-plane tilt δ_a (operator B σ_y) and in-plane rotation β_a (operator ∂_θ field).

## Checks (in order)

1. FD equals trace, the central identity: compare the 4-point finite difference (FD) of the frozen-occupation band sum `Σ f_n^0 ε̃_n` with `E^(2) = Tr[V2 ρ0] + ½Σ_{n≠m}(f_n−f_m)|V1_nm|²/(ε_n−ε_m)`. Use step d = 1e-4 (truncation-limited, about 4e-7 absolute error); assert relative deviation < 5e-6.
2. Exact zero mode: a global rotation with a perturbation pattern uniform in one channel (for example R_y gives `C_ββ·1 = 0`) holds at any reference; assert about 1e-6.
3. Torque-conditioned zero modes: patterns from other global rotations (for example cosΘ_a, sinΘ_a in the out-of-plane block) hold only for torque-balanced references. Assert at a commensurate torque-free reference; at a generic reference, report the breakage (about 1e-2) as the diagnostic.

## Traps (each cost one debug cycle)

- Spiral references have symmetry-protected exact pair degeneracies; plain `f_n/(ε_n−ε_m)` hits 0/0. Use the antisymmetrized form `(f_n−f_m)/2`; it is algebraically identical, and intra-pair splitting is first order and cancels in the 4-point FD. Mask `|ε_n−ε_m| < 1e-10`.
- Uniform out-of-plane tilts of an in-plane spiral are not a global rotation (each site rotates about its own local axis), so no row-sum zero mode exists. Zero modes come from global SO(3) decomposed into channel patterns; some require torque balance (torque = first-order term = J^(1) of the Szilva RMP review).
- Pair reference occupations with sorted tilted eigenvalues in the frozen-f band sum; f is a function of ε, so degenerate permutations are harmless.
- Field blocks go complex when σ_y enters: call `.astype(complex)` before adding, or the numpy add-cast fails.

## Two-channel physics

- Out-of-plane block C_δδ: pairwise exchange `J_ab = −C^δδ_ab` for a≠b; the diagonal is `Σ_b J_ab cosΘ_ab` and shows the zero-mode structure.
- In-plane block C^ββ: flux/stiffness sector; equals `J∘cosΘ` only for pairwise-cosine energies, and a deviation is a quantitative non-Heisenbergity diagnostic.
- At q = 0 the channels coincide (SO(2)) and C^ββ equals the collinear response matrix M with `j(R) = −M(0,R)`; this is the LKAG anchor.

## Promotion

After direction approval, graduate the probe to `TB2J/docs/sympy/<name>.py` with every identity as an assertion, plus a companion `.md` report (Motivation/Context/Notation/Procedure/Results per repo convention). Run it in the mydev environment.
