---
artifact_role: knowledge
audience: both
confidence: 0.8
created: 2026-08-09
last_validated: 2026-08-09
validation_procedure: "numpy probe of the hund_orb matrices (this note, corrected); reviewer-independent re-verification of eigenvalues; one-step fixed-DM z/x covariance test (see [2026-07-19 RI tests](../specs/research/2026-07-19-rotational-invariance-tests.md))"
project: siesta_plusB
status: draft
validated_by: automatic
tags: [scf, convergence, lanthanide, hund, occupation-matrix-control]
type: Project Knowledge
math_provenance: missing
math_provenance_reason: "scf-convergence-lanthanides.md display math requires one MathDoc marker per equation"
---

# SCF convergence difficulty for lanthanide DFT+U+J+B+SOC


## Overview

This note records *why* the self-consistent-field (SCF) convergence of the
DFT+U+J+B+SOC scheme is difficult for the Sm $4f$ shell, established during the
2026-08-09 brainstorm and then corrected after independent review. The difficulty
is attributed to **two plausible, distinct mechanisms** — a physical nucleation
problem (A) and a numerical oscillation problem (B). A third hypothesis (a
defective off-$z$ Hund seed) was **investigated and refuted** (see below); it is
recorded so the same path is not retraced.

A and B were *candidate explanations*; the release-path measurement
(2026-08-09, see "Release path — RESOLVED" below) now shows the forced seed works and
the free SCF is unstable at release, implicating the mixer (B) primarily and
metastability (A) secondarily.

## Principles

Two facts from the vault frame the discussion (each bounded, not general):

- A **fixed-DM $z/x$ covariance test** for one saved isolated-Sm density matrix
  agrees to 1–2 µeV after the B-potential correction
  ([2026-07-19 RI tests](../specs/research/2026-07-19-rotational-invariance-tests.md)).
  This shows that the eV-scale $z/x$ SCF differences for *that setup* are not
  explained by the tested fixed-DM functional; it is **not** a proof that the whole
  Hamiltonian is rotationally invariant (one DM, one axis pair; a $\phi$-dependent
  $z/y$ baseline SOC/DFT+U residual of ~9 meV is also recorded).
- The $+B$ **code is correct** (sympy-verified potential; GdN control $L\approx0$;
  spin-scalar; bounded occupations).
- SIESTA seeds the **spin** via `DM.InitSpin` but **not the orbital moment**.

## Details

### Layer A — Nucleation / basin selection (physics, candidate)

Getting *into* the Hund's-rules basin at all, from the atomic density matrix.

1. **The OP term has zero gradient and a local maximum at the origin.**
   $E^{OP}=-B\langle\vec L\rangle^2$ has Hessian $-2B\,I$ (for $B>0$), so the origin
   is a stationary **local maximum of the OP term**, with zero gradient. The atomic
   start therefore gets no restoring signal from OP to choose a direction. (Calling
   the *full DFT* stationary point a saddle would require evidence from the other
   energy terms.) Weak $B$ cannot nucleate $L$ (tests: $B{=}0.1\to L\approx0.14$);
   strong $B$ over-shoots ($B{=}1.0\to L\approx12$, past the $f^5$ maximum of 5).
2. **No orbital seed.** For spin-$z$, SOC plus the $z$-quantized $m_l$ basis (where
   $m_l$ is a good quantum number) naturally develop $L_z$. For spin-$x$ there is no
   such symmetry crutch, so $L_x\approx0$ — observed even at $B{=}0$ (pure SOC:
   $L_z\approx2.95$ vs $L_x\approx0.05$).
3. **Near-degenerate $f$ manifold.** Sm$^{3+}$ is $4f^5$, ground term
   ${}^6H_{5/2}$ ($L{=}5,S{=}2.5,J{=}2.5$). An $f$ shell has 14 spin-orbitals;
   $\binom{14}{5}=2002$ is the count of five-electron Slater determinants
   (configurations) before symmetry reduction. Many competing $LS$ terms lie
   close in energy (the "~eV" scale needs a source); in a solid SOC is *one*
   interaction that can select states of different $J$, not literally the only one.
   DFT+U can settle into non-Hund occupation patterns — the Lee 2025 metastability
   result ([OP references](../specs/research/2026-07-16-op-references.md) §5).

### Layer B — Within-basin oscillation (numerics, candidate)

Once near the right basin, converging without the moment oscillating.

1. **Coupled nonlinear feedback loops.** $\langle L\rangle\to V^{OP}\to\rho\to
   \langle L\rangle$ is one loop; the Pulay density-matrix mixer is a second loop on
   the same residual. When $\langle L\rangle$ swings, the induced Hamiltonian is
   non-stationary in a way full-DM Pulay cannot model.
2. **Pulay overshoots on a flat, multi-modal surface.** DIIS assumes a quasi-linear
   residual; on a near-degenerate manifold its low-rank history extrapolation can
   overshoot. Observed signature: reducing `SCF.Mixer.History` 16→4 is faster *and*
   lower-energy for one system — a symptom, not a principled fix.

### Investigated and REFUTED: defective off-$z$ Hund seed

A hypothesis was raised that the hardcoded off-$z$ Hund matrix
(`m_occ_proj_dftu.F90:861-886`) is an invalid density matrix and thus the cause of
off-$z$ collapse. **This is false** — it was an artifact of a buggy probe that
transcribed both matrix triangles and then re-Hermitianized, doubling every
off-diagonal.

Independent re-verification (numpy; reviewer-confirmed):

| matrix | occupation eigenvalues | $\lvert L\rvert$ | $\langle\vec L\rangle$ |
|---|---|---|---|
| $z$-template (828–836) | $\{0,0,1,1,1,1,1\}$ | 5 | $(0,0,-5)$ |
| **hardcoded off-$z$ (861–886)** | $\{-3{\rm e}{-7},1{\rm e}{-7},0.999999,\dots\}\approx\{0,0,1,1,1,1,1\}$ | 5 | $(-5,0,0)$ |
| $R_x^{\mathsf T}\,n^{(z)}\,R_x$ | $\{0,0,1,1,1,1,1\}$ | 5 | $(-5,0,0)$ |

The hardcoded off-$z$ matrix equals $R_x^{\mathsf T}\,n^{(z)}\,R_x$ to ~$5{\times}10^{-7}$
(six-decimal rounding) — a valid, correctly-oriented projector. It carries
$\langle L\rangle=-5\hat x$, **anti-parallel** to the $+x$ spin, which is the correct
less-than-half-filled $f^5$ Hund/SOC alignment ($J{=}L{-}S$). (Note: the opposite
transform $R_x\,n^{(z)}\,R_x^{\mathsf T}$ gives $+5\hat x$ — wrong sign; the existing
code uses the correct inverse.) This matches the vault's standing conclusion
(2026-07-19 memo #4): *the init correctly seeds the direction.*

### Release path — RESOLVED (2026-08-09 measurement)

Quick Task [[../specs/quick-tasks/2026-08-09-init-hund-release-instrumentation|InitHund
release instrumentation]] added a debug-gated print (`OP.DebugRelease`) of the **raw,
pre-overwrite projected orbital moment** every SCF step in `occ_proj_dftu`, through
the `OP.InitHund` window and past release. Isolated Sm (U=6, J=0, B=0.01, serial, 50
steps), spin-x and spin-z control.

**Findings (both directions):**

- **In-window** (forced potential active): $|L|_{\rm raw}$ oscillates 0↔5 and reaches
  ~4.97 by step 14–20. The forced $V$ *does* drive the DM to the Hund occupation.
- **At release** (step 21, forcing → 0): the DM does **not** retain Hund. $|L|_{\rm raw}$
  collapses to ≈0 for many steps, jumps to ~5, then drifts (spin-x → ~2–3; spin-z →
  sign-flipped, $L_z$ as negative as −4.85). It oscillates 0↔±5 and never settles in
  50 steps.

**Verdict.** The seed is **not** the problem (consistent with the refuted Layer C):
the forced potential brings the DM to Hund. The failure is at release, and the
0↔±5 oscillation *during the window* — when the potential is pinned — is the
signature of **Pulay/mixer overshoot (Layer B)** as the proximate cause. After
release the DM drifts away from Hund, so the state is also not a robust free-SCF
attractor (**Layer A**, secondary). The hypothesis above was correct in mechanism
(`OP.InitHund` clamps only the potential's occupation, not the AO DM) — but the
dominant symptom is mixer instability, not silent reversion. **Fix direction =
occupation-matrix control / mixer stabilization, not the seed.**

**Refined by the mixer sweep** ([Mixer-parameter sweep](../specs/quick-tasks/2026-08-09-mixer-sweep-release.md)): no FDF mixer setting retains Hund — H4/H2 (shorter history) and W0.1 (low weight) all leave the DM at a *wrong, sub-Hund* state ($|L|{\sim}1$–$2$); the baseline oscillates to ~2.75; post-release retention ≤ 0.30 for every config. Tuning the mixer cannot hold the Hund state, so **Layer A (metastability) is the root cause** and Layer B (the in-window oscillation) is proximate dynamics, not a tunable fix. The fix must be **continuous occupation-matrix control** — constrain/mix the occupation toward Hund through the *whole* SCF, not init-then-release (Lichtenstein-OMC / Lee-2025).

**Linear-mixing discriminator (2026-08-09).** Challenged whether the 0↔5 oscillation is Pulay "overshoot" or a **sign error** in the potential, a decisive test was run: pure **linear** mixing (weight 0.2, no Pulay history → overshoot impossible), spin-x and spin-z. Result: the oscillation **vanishes entirely** — $L$ decays *smoothly and monotonically to ≈0* (lin-x: $L_x$ −4.97 → −1.99 → −0.06; lin-z: $L_z$ +4.97 → +1.99 → −0.06, passing through zero without sign-chasing). Conclusions: (i) the 0↔5/±5 oscillation **was Pulay hopping** between near-degenerate $L$ states (at $J{=}0$ the DFT+U term is rotationally invariant and $B{=}0.01$ is tiny, so $L{\approx}0,\pm5$ are nearly degenerate) — *not* classical overshoot; (ii) a **sign error is ruled out** as the cause (a wrong-sign potential would persist under linear mixing); (iii) **metastability is confirmed clean of any mixer confound** — under linear mixing $L\to0$, so the free-SCF ground state at $J{=}0,B{\approx}0$ has $L{\approx}0$ and the Hund $|L|{=}5$ is metastable. So linear mixing removes the hopping *noise*, but $L$ still flows to 0 — the load-bearing fix remains continuous occupation-matrix control. **Open convention check:** the spin-z seed was `Lz=−5` in the numpy probe but the code's moment uses the `int_so_ang` `(A3,−A2,−A1)` convention and lin-z develops `Lz=+4.97` — reconcile by printing the *forced* occupation's moment next to the raw DM moment (likely a probe-vs-code convention artifact, not a physics error).

**Sign-convention loose end — RESOLVED (2026-08-09 decomposition).** The "forced `Lz=−5` but DM `Lz=+4.97`" opposite-sign response is **not a sign error**; it is SOC setting the DM's L direction. Decomposition (spin-z, linear mixing): (i) **SOC off, B=0.01** ⇒ DM $L_z{=}0.000$ exactly — V^OP *cannot nucleate L* without SOC (real Hamiltonian ⇒ real DM ⇒ $\langle L\rangle{\equiv}0$); V^OP only amplifies an existing moment. (ii) **B=0, SOC on** ⇒ DM $L_z{=}{+}4.97$ — SOC nucleates L **parallel** to S, independent of the forced occupation (which is ignored by V^U at J=0 and by V^OP at B=0). Since $E{=}{-}B\langle L\rangle^2$ pins only $|L|$, the opposite sign is benign. **Consequence:** the OP term needs SOC to nucleate L (strengthening B alone won't bootstrap from $\langle L\rangle{=}0$); and at B=0.01 V^OP is too weak to sustain $|L|{=}5$ against metastability. **Open physics question (not a code bug):** SOC drives L ∥ S here; for f⁵ Hund's 3rd rule wants L ∦ S ($J{=}L{-}S$). The RI tests verified z/x covariance, not the L·S sign vs physical J-ordering — check before OMC picks a target direction.

**Open physics question — RESOLVED (2026-08-09, Hund-filling check).** The L∥S is the expected mean-field Hund determinant, **not a SOC sign error**. Hund's 2nd rule for f⁵ spin-up gives max $M_L = +3{+}2{+}1{+}0{-}1 = +5$; the DM gives exactly $L_z{=}{+}5$ — the max-$M_L$ Hund filling with $S_z{=}{+}5/2$, so L∥S *by construction*. Hund's 3rd rule (L∦S, $J{=}L{-}S$) is an exact LS-coupled J-eigenstate statement that does **not** apply to the KS mean-field determinant (which has definite $M_L, M_S$). The SOC sign cannot be diagnosed from L∥S (it is set by the filling, not SOC), and even a wrong SOC sign would not cause the convergence failure (that is metastability) — it would only affect J-multiplet splitting / magnetocrystalline anisotropy, a separate finer validation, out of scope here. **The OP $|L|$ target is sign-agnostic; OMC can proceed.**

**Occupation-matrix control — RULED OUT (2026-08-09).** Implemented Lichtenstein OMC (`OP.OccControl`: `occ_in=(1−α)occ_in+α·n_out`, build $V$ from `occ_in`, never release) — [OMC QT](../specs/quick-tasks/2026-08-09-occupation-matrix-control.md). Result: $|L|_{\rm raw}$ **decays 4.97→0** over ~15 steps (mean 0.34), same as release — it does *not* hold Hund. Reason: $n_{\rm out}{\to}0$ (metastable DM), so occ_in tracks the SCF ground state ($0.8^{15}{\approx}0.035$). OMC *finds* the SCF ground state; it cannot *hold* a metastable one. Never-release pure forcing held 2–5 but oscillated period-2. **So no SCF-mixing trick (release, mixer tuning, OMC, pure forcing) yields stable $|L|{=}5$.**

**B scan — final avenue closed (2026-08-09).** Scanned B∈{0.1,0.2,0.3,0.5} with Hund init+release + linear mixing (spin-z), looking for a B giving free-SCF $|L|{\approx}5$. Result: the **post-release equilibrium $|L|{\approx}2.98$ for ALL B≥0.1** (B-independent); B<0.1 → 0 (metastable). B over-polarizes *while forced* (B=0.5 in-window $\to$ 10.9) but free SCF always relaxes back to ~3. That ~3 is the SOC+U mean-field orbital moment (= 2026-07-19 config a, $L_z{\approx}2.95$) — **the KS mean-field quenches L from the atomic Hund 5 to ~3, and no B recovers it.** Conclusion: **no B yields free-SCF $|L|{=}5$.** The atomic Hund $|L|{=}5$ is not a mean-field free-SCF equilibrium at any parameter tested; the mean-field gives ~3 (or 0). This is the known DFT orbital-moment quenching / Lee-2025 metastability — not fixable by mixing or B.

> ## ⚠️ CRITICAL CAVEAT (2026-08-09): the isolated-Sm test atom is NEUTRAL, not Sm³⁺
>
> The isolated-atom test uses `Sm.1.psml` with `z-pseudo=16` (16 valence e⁻) and **no `NetCharge`** ⇒ **neutral Sm (+0)**, ground configuration [Xe]4f⁶6s² ⇒ ground term **⁷F₀, L=3** (not 5). The free SCF \|L\|≈3 (config a $L_z{\approx}2.95$; B-scan ≈2.98) **is the correct neutral-Sm value** — the SCF was right all along. The **\|L\|=5 target is the Sm³⁺ f⁵ ⁶H₅/₂ value — the wrong charge state** for this neutral atom; the `OP.InitHund` seed (trace-5 f⁵ occupation + \|L\|=5) was forcing f⁵ onto an f⁶ atom. **All the neutral-Sm results above (mixer sweep, OMC, B-scan, "mean-field quenching") are TAINTED by the wrong charge state** and should not be trusted as metastability evidence.
>
> **Re-tested on Sm³⁺ (`NetCharge +3` → f⁵), the correct charge state (2026-08-09):** free SCF gives **\|L\|→0** (both Hund-init+release and cold start, last5 ≈0.09/0.10) — *not* 5, *not* 3. This **IS genuine metastability** (the f⁵ Hund $|L|{=}5$ is not reached; free SCF falls to $|L|{\approx}0$), consistent with Lee-2025. **Conclusion: the metastability holds, but only the Sm³⁺ result is valid evidence; the neutral-Sm tests were the wrong charge state.** Open: re-run the key probes (never-release forcing, OMC) on Sm³⁺ to see if any scheme holds $|L|{=}5$ for the correct charge state. Inputs: `/tmp/sm3p-{init,cold}/`.
>
> **Sm³⁺ never-release + OMC (2026-08-09):** on the correct charge state, **never-release forcing holds $|L|{\approx}4.99$ STABLY** (43/43 steps >4, no oscillation — vs neutral Sm's period-2). The neutral-Sm period-2 was the wrong-charge-state artifact (f⁵ forcing on f⁶). OMC still →0 (finds the metastable $L{=}0$ ground state). **Resolution: for Sm³⁺ the f⁵ Hund $|L|{=}5$ IS a stable state; the only issue is SCF state-selection (free SCF/OMC descend to $L{=}0$). Continuous forcing (never-release) reaches and holds it.** Inputs `/tmp/sm3p-{nr,omc}/`.
>
> **Sm³⁺ B scan — PARTIAL/RETRACTED (2026-08-09).** Scanned B∈{0.1,0.3,0.5,1.0} on Sm³⁺ (free SCF, spin-z) + x/y/z at B=0.5. **B=0.5 does NOT sustain $|L|{=}5$** — the $|L|{\approx}4.9$ was a *transient*: trajectories decay (z 4.99→4.90, x 4.99→4.28, y 4.99→4.44 over steps 30→52). B=0.1,0.3 → 0 (too weak). B=1.0 → $|L|{\approx}5$ from **cold start** (stable, 4.986) but $|L|{\approx}9$ from init+release (over-polarized basin) — **path-dependent, multiple basins**. The x/y/z B=0.5 check is **not a valid RI test** (non-converged, decaying, path-dependent; y sits along x = the `OP.InitHund` φ-routing seed bug). **Honest status: no clean, stable, rotationally-invariant free-SCF $|L|{=}5$ on Sm³⁺ at any B; the only robust route is never-release forcing (which holds it, but forced).** The +B Hamiltonian is RI (2 µeV one-step, separate); the SCF state-selection is the problem. Inputs `/tmp/sm3p-b*/`, `/tmp/sm3p-b0.5-{x,y}/`.
>
> **B×direction scan (Pulay) — over-polarized, inconclusive (2026-08-09).** Ran Sm³⁺ B∈{0.5,0.8,1.0}×{x,y,z} (Hund init+release, **Pulay** h16 w0.5, 120 steps). Result: |L| = 6–12 (over-polarized, past the Hund 5), moment vectors misaligned with spin axes, energies scattered by 10s of Ry — Pulay **hopping between over-polarized basins**, not converged. **Pulay was the wrong mixer here** (linear gave the controlled B=1.0-cold→5); the OP term at B≥0.5 over-polarizes (|L|→8–12), small B →0, and no B yields a clean stable RI-conforming |L|=5. The |L|≈5 seen earlier was one linear-mixing basin, not robust. **Honest conclusion stands: no clean free-SCF \|L|=5 at any B; reliable route is never-release forcing.** Inputs `/tmp/scan-b{0.5,0.8,1.0}-{z,x,y}/`.

### Existing `OP.InitHund` limitations (code quality, separate from convergence)

Independent of convergence, the current `OP.InitHund` block has generality gaps
worth recording for any future robustness work:

- **Direction routing ignores $\phi$.** The `theta > pi/4` branch maps *every*
  off-$z$ direction ($+y$, $-x$, $-z$, …) to the same $-x$ projector. Only the
  single $+x$ test case is correct; $\pm x,\pm y,\pm z$ and intermediate angles are
  not supported.
- **Per-atom template reset.** `hund_orb` is initialized to the $z$ template once
  *before* the atom loop; an atom taking the off-$z$ branch overwrites it, so a
  later $z$-directed atom inherits the previous atom's off-$z$ seed. Latent for
  multi-atom cells of mixed direction.
- **Shell identification by count.** `ndftuproj == 7` does not prove an ordered
  $l{=}3$ shell (`nprojsdftu` is the species total over all DFT+U shells). Should
  locate the shell via `pjdftu_l`/`pjdftu_m`/`pjdftu_index` and rotate only its
  contiguous $m{=}{-}3..3$ block.
- **Fixed $f^5$ template regardless of valence.** Enabling `OP.InitHund` writes a
  trace-5 spatial projector for every eligible 7-projector atom regardless of actual
  population/species. Note the `sm_ri_a_z` covariance input is neutral Sm ($f^6$),
  so using this initializer there changes the target electron count, not merely the
  direction — keep neutral-$f^6$ evidence separate from Sm$^{3+}$ $f^5$ evidence.

## Synthesis

| Layer | Nature | Status |
|---|---|---|
| A. Nucleation | physics | **root cause = SCF metastability (NOT a symmetry issue).** DFT+U(+J) is rotationally invariant (SO(3)) — verified: J=0.8 one-step z/x ΔE≈1 µeV (2026-07-19 controls). The free SCF just doesn't descend to the Hund $|L|{=}5$ minimum (settles at $L{\approx}0$–3); no mixer/OMC scheme reaches it. At J=0 $E_U$ depends only on occupation eigenvalues (penalizes fractional, agnostic to which integer filling) ⇒ doesn't single out $|L|{=}5$. |
| B. Oscillation | numerics | Pulay hopping on the flat $L$-landscape ($J{=}0$, $B{\approx}0$ ⇒ $0,\pm L$ near-degenerate). **Removable by linear mixing** (oscillation vanishes); **not a sign error** (would persist under linear). Not the root cause. |
| ~~C. Defective off-$z$ seed~~ | ~~bug~~ | **refuted** (probe artifact; matrix is a valid $R_x^{\mathsf T}n^{(z)}R_x$) |
| Release path | measured | forced seed works; free SCF leaves Hund. **All mixing schemes fail ⇒ not a mixer problem; it's SCF metastability. Direct $|L|$ levers: B (OP term) + SOC, not J (spin lever) or the mixer.** |

~~Continuous occupation-matrix control~~ — **RULED OUT** (OMC→0). The convergence failure is **SCF metastability, not a broken symmetry**: DFT+U(+J) is rotationally invariant (confirmed for J=0.8), and the free SCF simply doesn't reach the Hund $|L|{=}5$ minimum. **J (Hund exchange) is a *spin* lever, not an L lever** — J>0 favors high spin (Hund 1st rule); it does not couple to L directly, and J=0.8 + cold start already gave $L{\approx}0.06$ (2026-07-19 config b). The direct $|L|$ levers are **SOC** (nucleates L) and **B** (OP term $E{=}{-}B\langle L\rangle^2$, amplifies L). Open: whether some B gives a stable $|L|{=}5$ without over-polarizing (B=1.0 → L≈12, per handoff). *(Earlier "J breaks rotational invariance" / "J couples to L" framing was wrong — corrected 2026-08-09.)*

## Variables

The following variables are used in this note (see [notation](notation.md) for full definitions):

| Symbol | Description | Units |
|--------|-------------|-------|
| $R(\theta,\phi)$ | Real-SH orbital rotation matrix for spin direction $(\theta,\phi)$ | — |
| $n^{(z)}_{\mathrm{Hund}}$ | Hardcoded $z$-quantized Hund $f^5$ occupation template | electrons |

## Equations

The OP energy is a downward-opening paraboloid with a local maximum at the origin:

$$
E^{OP} = -B\,\langle\vec L\rangle^2, \qquad
\frac{\delta E^{OP}}{\delta\langle\vec L\rangle} = -2B\,\langle\vec L\rangle
$$

A direction-correct Hund seed (correct convention, anti-parallel to spin for
less-than-half-filled $f^5$) is the **inverse** rotation of the $z$-template:

$$
n^{(\theta,\phi)}_{\mathrm{Hund}} = R(\theta,\phi)^{\mathsf T}\; n^{(z)}_{\mathrm{Hund}}\; R(\theta,\phi)
$$

## Conventions

- The real-SH rotation $R(\theta,\phi)=C^\dagger\,R_z(\phi)\,d^l(\theta)\,R_z(-\phi)\,C$
  is the machinery in `papers/DFT_plus_B/rotate_dm.py` (`real_sh_rotation_angle`).
- For $l{=}3$, $R_x$ (the $z{\to}x$ rotation) maps $L_z\to -L_x$; hence the seed uses
  $R^{\mathsf T} n R$ (not $R n R^{\mathsf T}$) to keep $\langle L\rangle$ anti-parallel
  to spin.
- A valid occupation seed is Hermitian, positive-semidefinite, idempotent
  (eigenvalues $\in\{0,1\}$), trace = electron count.
- When probing such matrices: if a transcription already sets both triangles, do
  **not** re-Hermitianize (it doubles off-diagonals).

## Linked Concepts

- [notation](notation.md): Standard variable notations.
- [2026-07-19 RI tests](../specs/research/2026-07-19-rotational-invariance-tests.md): fixed-DM z/x covariance (1–2 µeV); bounded, not a general RI proof.
- [OP references](../specs/research/2026-07-16-op-references.md): Lee 2025 Hund metastability; Morbec frozen-$B$/no-dc.
