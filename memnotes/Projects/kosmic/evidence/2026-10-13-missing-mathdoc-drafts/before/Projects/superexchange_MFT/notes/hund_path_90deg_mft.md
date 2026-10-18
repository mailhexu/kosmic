---
artifact_role: knowledge
type: Project Knowledge
status: stable
audience: development
usage_stale: false
created: 2026-09-28
last_validated: 2026-09-29T00:00:00
validation_procedure: |
  Derived with sympy (superexchange_MFT/derivations/hund_path_90deg.py): fixed-E0
  Brillouin-Wigner downfolding of the 28-dimensional 6-electron 90-degree model;
  closed form asserted symbolically (no t^2 term, J_p-linear, exact
  susceptibility identity). Validated against exact diagonalization
  (ed_90deg_reference.py, 4 internal checks incl. Hubbard dimer benchmark and
  J(J_p=0)=0); relative deviation of the t^4 formula vs ED shrinks as t^2
  (0.8% at t=0.2, 4.0% at t=0.45).
validation_test: "python superexchange_MFT/derivations/hund_path_90deg.py"
successful_usage_count: 1
last_used_successfully: 2026-09-28T00:00:00
related_files:
  - "/home/hexu/projects/TB2J_dev/superexchange_MFT/derivations/hund_path_90deg.py"
  - "/home/hexu/projects/TB2J_dev/superexchange_MFT/derivations/hund_path_90deg.md"
  - "/home/hexu/projects/TB2J_dev/superexchange_MFT/derivations/ed_90deg_reference.py"
tags: ["superexchange", "mft", "hund", "90-degree", "goodenough-kanamori", "kernel"]
project: superexchange_MFT
status_detail: derivation asserted against ED
links_to:
  - "tb2j_fe_o_orbital_decomposition"
  - "streamlit_2m1l_exchange_demo"
linked_from: []
---

# 90-degree Hund-Path Exchange and the MFT Correction

The one-electron LKAG bubble (TB2J MFT) gives exactly $J = 0$ on a 90-degree
2M-1L bond because px and py never mix. The missing term is the two-particle
vertex path Fe1 -t-> px -Jp-> py -t-> Fe2 (Goodenough-Kanamori FM term; the
mechanism behind FM monolayer CrI3). The fourth-order collinear $S_z$
splitting of the **projected ED toy interaction** (determinant diagonal of
TBUpy's four-index spinor Kanamori; not the two-index collinear SCF term) is

$$
J_{90} = \frac{t^4 J_p}{2 D_S^3 D_D}, \qquad
D_S = \Delta + U_{Fe} - U_p - J_p, \qquad
D_D = 2\Delta + 2U_{Fe} - 2U_p - J_p,
$$

with $D_S$ the S-state (one virtual ligand-to-metal hop) and $D_D$ the
D-state (two hops, two ligand holes) cost. Fourth order in $t$, first order
in $J_p$, zero at $J_p = 0$.

> **FULL-TRANSVERSE CUTOVER (2026-09-29).** This projected-`S_z`
> derivation and the sections below are **historical only**. The current
> contract is [full_transverse_rebaseline](full_transverse_rebaseline.md):
> `J_frozen=-A12/2`, with the 180-degree TB2J NCL identification gate
> passed; `J_angle_curv=1/(2 dq/dh)` from the certified fixed-N spinor
> relative-field susceptibility; and the raw correction
> `J_relax=J_angle_curv-J_frozen`. Compose *only*
> `J_total=J_bubble+J_relax` after the identification gate. The matched
> four-sector `J_p=0` response has analytically zero curvature;
> `dJ_Hund=J_total(J_p)-J_total(0)` is measured, not inferred from
> linearity of the kernel. All five finite-Hund 90-degree mean-field
> exchanges are positive (ferromagnetic), agreeing in sign with the full-U4
> ED weak-hopping result and passing FR-005. The `J_p=0` finite-field
> oracle cannot bracket a twist and remains gate-blocked.
> Full-U4 ED at the defaults gives +0.1039 meV; its derived
> distinct full-tensor weak-hopping term is
> `J^(4)=J_p/[4(Delta+U_fe-U_p)(Delta-J_p+U_fe-U_p)^3]`.
> The former `tbupy.hund_response` import and the rotated-effective-field
> mixed response are removed. Historical examples below are not runnable.

## Susceptibility form and the double-counting rule

$$
J_{90} = h^2 \chi^{vert}, \qquad
h = \frac{t^2}{D_S} \;(\text{bare exchange field}), \qquad
\chi^{vert} = \frac{J_p}{2 D_S D_D} \;(\text{vertex-corrected ligand } \chi).
$$

Within the projected ED $S_z$ sector the factorization uses the **bare**
field $h$ and the **vertex** coefficient $\chi^{vert}$ from the same
unpolarized reference. Never stitch a converged TB2J bond $J_b$ (already
contains ligand polarization) to an independently measured $\chi$: that
would double-count response. Neither this rule nor the collinear splitting
certifies an isotropic transverse force-theorem kernel.

## Cross-functional numerical comparison (t=1, Delta=3, U_Fe=4, U_p=1, meV)

| bond | ED projected $J_{zz}$ | collinear-SCF FM/AFM mapping | TB2J LKAG bubble |
|---|---:|---:|---:|
| 90 deg, J_p=0.5 | +0.108 | +0.220 | 0 |
| 180 deg, J_p=0.5 | -12.21 | -8.95 | -9.10 |

These numbers use **different interaction functionals**. Their differences
cannot be attributed solely to a mean-field-versus-ED error. The ED toy is
$S_z$-diagonal; its fourth-order Hund operator is Ising, so collinear
splitting does not establish a transverse Heisenberg correction.

## Kernel design requirement

The projected ED coefficient factors as $h_1\chi^{vert}_{12}h_2$. TBUpy
Story 1 exposes those weak-hopping factors; Story 2 composes them with a
caller-provided bubble slot. No same-functional transverse MFT correction
has been established. A hybrid must not mix converged $J_b$ with a
susceptibility. The 2-index collinear Kanamori term and 4-index spinor term
also differ on diagonal densities; a new transverse oracle cannot silently
switch between them.

Full derivation with equations: `superexchange_MFT/derivations/hund_path_90deg.md`.

## Implementation Status (2026-09-28)

TBUpy Story 1 now provides `HundResponseParameters.from_model(data, ...)`,
`bare_exchange_field` and `ligand_vertex_susceptibility` in
`tbupy/hund_response.py` (including both 90-degree Fe-O bond identities,
unpolarized provenance and the `Sz`-only caveat). Both 90-degree bonds were
smoke-run: `0:s-1:px` and `2:s-1:py` have
`h = 0.1818181818 eV`, `chi_vert = 0.00395256917 /eV` at the default
parameters. Story 2 adds `VertexSusceptibilityMatrix.from_scalar(chi)` and
`vertex_exchange([h1, h2], chi_matrix)` with guards against converged
inputs and mismatched model parameters. The symmetric matrix has
`chi12 = chi21 = chi_vert/2`, giving the O(t^4) estimate
`J_vertex = +0.1306634436 meV` at the default parameters. This is a
**weak-hopping result**, not a validated full MFT curvature. TB2J itself
still emits only the bare bubble; do not infer a TB2J vertex-corrected mode
from this module.

## Transverse curvature parity blocker (Story 3 research, 2026-09-28)

The toy demo's collinear `TBUpyModel(..., hubbard_type="kanamori")` uses the
2-index density-density `KanamoriTerm`, whereas `spin_mode="spinor"`
selects the distinct 4-index `SpinorKanamoriTerm`. The constraint engine
provides spinor moment-component Lagrange multipliers, but no transverse
rotation of the *same* collinear density-density functional. The hard
`spin_moment_constraints` path rotates densities after diagonalization and
marks its energy uncertified; it is not a curvature oracle.

At the default 90-degree FM model, the collinear SCF converges to
`total_energy=-12.411294391979125 eV`; a spinor SCF initialized from the
same interleaved density converges and certifies `free_energy=-10.515555904736265 eV`.
Even on the **identical collinear density**, the two Hubbard terms return
`E_U=3.0500705839294113 eV` versus `1.1333769086354077 eV`,
respectively, and the ligand on-site potentials disagree. On pure ligand
determinants at $U_p=1$, $J_p=0.5$, the same-spin/opposite-spin energies
are -0.5/0 eV for the collinear term but 0/+0.5 eV for the spinor tensor;
the ED toy uses 0/+0.5 eV. Thus the ED closed form is **not** the
collinear SCF functional's exact reference. A new transverse interaction
and compatible ED/vertex references or a changed acceptance target require
a spec decision, not a numerical tolerance adjustment.

The sympy scripts `derivations/hund_path_90deg.py` and
`derivations/rotation_curvature_normalization.py` assert the
fourth-order effective Hund matrix is diagonal in $S_z$ and equal to
$C I-2J_{90}\,\mathrm{diag}(1,-1,-1,1)$. Its collinear FM/AFM splitting
is $4J_{90}$, but its transverse opposite-minus-parallel curvature and
mixed derivative are exactly **zero**. By contrast, for an isotropic TB2J
ordered-pair interaction, $J=(E''_{opposite}-E''_{parallel})/8$; the numeric
180-degree normalization control at $J=-9.095$ meV passes the
0.02/0.05/0.1-rad ladder. The latter does **not** validate an isotropic
90-degree Hund exchange.


## Selected direction (2026-09-28)

The user selected a full transverse, spin-rotational Kanamori rebaseline.
The revised PRD is approved; Architecture is in draft. Full four-index ED
must include spin-flip and pair-hop terms; TBUpy spinor SCF, response, and
ED must share one tensor. The projected $S_z$ result and old collinear demo
remain separately labelled historical references. Until the cutover is
implemented and reviewed, `tbupy.hund_response` is a weak-hopping
projected-$S_z$ calculation, **not** a validated transverse MFT correction.

The optional TB2J TBUpy adapter currently rejects spinor inputs, although
TB2J `ExchangeNCL` internally uses **interleaved** spin blocks (its
`set_tbmodels` docstring claiming separated spin is stale). A same-reference
bubble requires a verified interleaved spinor handoff; the old collinear
TB2J bubble must not be silently reused. The fixed-step spinor constraint
engine also failed to certify the opposite 0.05-rad branch in bounded
probes; a stable constrained solver is an implementation prerequisite.
A direct core `ExchangeNCL` smoke (bypassing the still-collinear-only adapter)
on the certified spinor FM model reported zero Fe–Fe pair exchange at 90 degrees
and finite raw transverse isotropic exchange at 180 degrees (-16.4857 meV
at `nz=20`, with contour convergence not yet checked). The 180-degree decomposition also
reported a nonzero zz component (+11.4309 meV): interpret the transverse
exchange tensor, not an unqualified scalar. These are adapter-feasibility
checks only, not certified acceptance numbers.
## Response decomposition gate

The algebraic `derivations/transverse_vertex_schur.py` check pins the
ordered-pair factor for a *stationary full-spinor* metal–ligand Hessian:

$$
H_{\mathrm{eff}}=A-BC^{-1}B^T, \qquad
J_{\mathrm{vertex}}=(BC^{-1}B^T)_{12}/2.
$$

This identity does not yet measure a full-Kanamori susceptibility.
The frozen metal block must first reproduce the same-state TB2J bubble
($J_b=-A_{12}/2$), or the additive decomposition is invalid. A generic
numeric minimization and symbolic verification passed, but full-SCF
curvature parity remains untested until the revised stories implement
the transverse response and certified constraint solve.
## Slow-review constraints (2026-09-29)

A bounded full-U4 Fock check verified that, at 90 degrees and `J_p=0`,
the Hamiltonian commutes with the **separate** transverse spin generators
for Fe1–px and Fe2–py. The zero-Hund response therefore has four
transverse null directions, not only the two from global SU(2); quotient
tests must identify both sectors before interpreting a pair exchange.

Sharing the same four-index bare tensor does not make exact ED and spinor
SCF energy functionals identical: the SCF has a density-dependent FLL-ns
double-counting energy absent from ED. A small exploratory full-U4 ED run
found positive singlet–triplet splitting at `J_p=0.5`, but this is not a
proof of the sign or magnitude of the **mean-field transverse vertex**.
The slow PRD/Architecture review reopened the approval gates and recorded
blocking requirements in their respective review ledgers.
## Linked Concepts

- [tb2j_fe_o_orbital_decomposition](tb2j_fe_o_orbital_decomposition.md)
- [streamlit_2m1l_exchange_demo](streamlit_2m1l_exchange_demo.md)
