---
audience: both
artifact_role: knowledge
type: reference

status: draft
created: 2026-08-19
last_validated: 2026-08-20
math_provenance: missing
math_provenance_reason: "cov-soc-two-channel.md display math requires one MathDoc marker per equation"
---

# Two-channel covalency-SOC finding (strongest single-feature MAE descriptor)

**Mechanism (user hypothesis, confirmed)**: covalency activates SOC *where it sits*.
- **Ligand channel**: covalency puts unpaired spin density on the (heavy) ligand; its
  xi_p couples it -> MAE. Feature f_lig_xi = <w_l2 * xi_p> over ligand sites.
- **Metal channel**: covalency on the magnetic site screens the CF (smaller Delta_CF
  -> larger second-order anisotropy) and wires two-site paths. f_met_xi = w_l2 * xi_d.

**Data (341 structures; w_l2 = sqrt(sum w_b^2), user-corrected L2 form)**:

| feature | |total| | |onsite| | |offsite| |
|---|---|---|---|---|---|---|
| covalency unweighted | -0.05 | -0.04 | -0.14 |
| ligand cov x xi_p | +0.26 | +0.28 | +0.43 |
| metal cov x xi_d | +0.16 | +0.18 | +0.24 |

Stratified by SOC site: ligand-SOC class (n=210): f_lig_xi = +0.43/+0.47/+0.46;
metal-SOC class (n=131): f_met_xi +0.19 (offsite +0.37). |MAE_total| medians across
f_lig_xi quartiles (ligand class): 0.06 -> 0.31 -> 0.59 -> 0.70 mJ/m^2 (>10x span).

**Why it matters**: beats every v0 aggregate feature (rho <= 0.19) and the v1 CF/Bruno
driver (rho ~ 0.09) as a SINGLE feature; the SOC-site stratifier is itself a classifier
(61% of the dataset is ligand-SOC dominated). Natural v2 baseline: two heads selected
by SOC-site class with these two features.

**Resources (paper repo, pushed d111c08)**:
- paper/magnetic_descriptor/data/cov_soc_channels.json (rows + summary + README entry)
- paper/magnetic_descriptor/figures/fig_cov_soc_channels.png (3 panels: scatter,
  quartile boxes, correlation bars)
- paper/magnetic_descriptor/scripts/plot_cov_soc_channels.py (regeneration;
  PREDICTMAG_DIR env or default workspace path)

**Caveats**: w from the STO-proxy coupling (ordering robust, absolute scale generous);
xi from AE neutral atoms (one-electron convention); correlation vs |MAE| (magnitude,
not sign - the sign problem remains open).

## Completion: metal SOC screened by covalency (2026-08-19, same day)

The fourth combination was tested: metal xi_d modulated by covalency.
- (1-w)xi_d (pure dilution): no independent signal (+0.04 |total| overall) — w is
  nearly constant 0.85-0.92 across compounds, so the factor does not vary; f_dil is
  just attenuated xi_d.
- xi_eff = (1-w)xi_d + w xi_p (admixture): strong ONLY through the ligand term
  (ligand class +0.36/+0.43/+0.46); in the metal class it UNDERPERFORMS bare xi_d
  (+0.12 vs +0.21 |total|).
- Bare xi_d: metal class +0.21/+0.42 (|total|/|offsite|) — the metal-SOC signal is
  real but not covalency-modulated in this dataset.

Conclusion: covalency acts by AMPLIFICATION (density where xi is large), not by
screening the metal SOC. Caveat: w's near-constancy is partly the two-level
saturation artifact (V >= Delta -> w -> 1); re-test the dilution channel after exact
overlap couplings replace the proxy.

## Metal-class within-family failure understood (2026-08-19)

The v2 baseline's worst folds (Ta -0.51, Mo -0.46, W) are diagnosed:
- xi_d is a BETWEEN-series variable (3d << 4d < 5d); LOEO removes that variance.
- Within series the varying chemistry is the d-count: Ta5+/W6+/Mo6+ are d0 (empty
  shell -> no single-ion anisotropy at any xi), Os4+/Ru4+ d4 give the largest MAEs.
  Bare xi on an empty shell is meaningless.
- Measured (metal class, LOEO): bare xi -0.01; xi^2/W -0.005 (bandwidth normalization
  does NOT repair it); n_d +0.12; xi*n_d +0.25. Occupation is the missing factor.
- Next refinement: Stevens-shaped occupation f(n_d) (theta2 + half-filling sign) as
  the metal-class feature.

## Ligand-site multipole anisotropy (user insight, 2026-08-19)

Ligands are less coordinated / more anisotropic than metals; many ligands in different
directions CANCEL. Scalar f_lig_xi is blind to this. Fix: rank-2 multipole of the
COVALENCY-WEIGHTED bond distribution at ligand sites, contracted along the label
directions (the v0 BVM d[L,m]/A_L machinery applied at ligand sites with covalency
weights): f_aniso = sum_lig xi_p |sum_b w_b [P2(u.z) - P2(u.x)]|.

Measured (ligand class, n=210): f_aniso 0.404/0.465/0.490 (tot/on/off) — comparable
to the scalar channel, better on offsite. PRODUCT scalar x anisotropy:
0.438/0.502/0.503 — the best feature yet (need heavy-SOC covalent ligands AND
un-cancelled rank-2 environment). Rank 4 weaker (0.32-0.43) — quadrupole dominates,
consistent with single-ion p-hole anisotropy. Signed contraction: no signal (-0.04)
— magnitude, not sign. Next: full d[L,m] tensor at ligand sites (v0 machinery).

## Descriptor-selection integration (2026-08-19)

`study_cf_ml.py` joins only the declared covalency-SOC descriptor columns by
`structure_id`; source MAE values never enter the feature map. On the 284 records shared
with the local CF inventory, the ligand-SOC subset (n=173) reproduces the descriptive
onsite-magnitude ranking: $w_2\xi_p=0.395$, $|Q_2|\xi_p=0.442$, and their product
$=0.454$. The product is absent in metal-SOC structures ($0.007$), confirming the
SOC-site stratification.

This does not yet give a transferable global predictor. Expanded nested
out-of-dominant-metal Lasso has signed onsite $\rho=+0.078$/RMSE 5.725 and absolute
onsite $\rho=-0.135$/RMSE 4.795, each worse than its mean baseline (4.709/4.509).
The correct interpretation is: the ligand product is the strongest current
**stratified descriptive magnitude** feature; it needs a separately justified,
fold-local ligand-SOC magnitude head before it can be called predictive.

## Compact nonlinear check (2026-08-19)

The same 20 label-free features were passed through a fixed 89-parameter
one-hidden-layer neural network under the same dominant-metal LOEO split. The signed
head improves OOF rank correlation to $+0.204$ but has RMSE 5.957 versus 4.709
fold-local mean baseline. The magnitude head has rank $\rho=+0.216$ but RMSE 7.716
versus 4.509. Smooth nonlinear mixing does not convert the stratified ligand-product
association into a transferable global magnitude model.

## Metal-site CF cancellation: tested, negative (2026-08-19)

Symmetric test of the Q2 cancellation factor at METAL sites (covalency-weighted,
z-x contraction): rank-2 HURTS (xi*n_d +0.17 -> +0.03 in the metal class), rank-4
neutral (+0.02), combined worse than without; signed Stevens-weighted version: no
signal. Contrast with ligand sites (+0.49 offsite). Two reasons:
1. p-hole (l=1) has ONLY rank-2 content - Q2 is its complete anisotropy; the d-shell
   MAE needs the level-splitting pattern (e_g/t_2g sigma/pi selectivity vs E_F and
   filling) - a bond-direction multipole with one weight per bond cannot represent it
   (the right object is the v1 CF Hamiltonian, whose own lesson was that E_F/filling
   detail is needed).
2. Dataset structure: metals are the symmetric (near-octahedral) sites -> Q2 ~ 0
   while MAE varies via xi*n_d; ligands are the asymmetric sites - the cancellation
   factor lives where the anisotropy lives.
Final channel structure: metal = xi_d * n_d (+Stevens shape); ligand = xi_p * w_2 *
un-cancelled Q2(ligand).

## Hund gating of the ligand channel: tested, negative (2026-08-19)

User question: does the ligand contribution depend on the neighboring metal's Hund
exchange (the spin-transfer gate)? Multiplying the ligand features by the metal Hund
moment 2S(n_d) HURTS everywhere (scalar 0.41 -> 0.31 |total|; product 0.50 -> 0.34).
Reasons:
1. Spin-transfer and charge covalency both scale as (t/Delta)^2 x exchange - w2
   already contains the amplitude wherever the metal is spin-polarized; x2S
   double-counts.
2. Low-spin counterexamples (d0-d2 4d/5d + heavy ligand: NbTe2 class) have small
   Hund but real MAE via the metal's own 4d/5d SOC and the covalent p-hole - the
   gate destroys exactly these. High-spin 3d metals saturate 2S (no variance).
Refined statement: the ligand channel needs magnetization SOMEWHERE in the cell
(interchangeable carrier: Hund-polarized 3d, itinerant 4d/5d, open p shell - CsF2).
A soft spin-resolved covalency would need spin-polarized quantities (not table-based).

## Covalency -> low spin? Tested, refuted; ionic/covalent split found (2026-08-19)

User hypothesis (nephelauxetic): covalency raises Delta_CF and shrinks B,C -> favors
low spin -> quenched MAE per xi*n_d. Measured: the OPPOSITE - efficiency
|MAE|/(xi*n_d) CORRELATES POSITIVELY with metal W (+0.35 metal class); xi*n_d ranks
MAE only in the HIGH-covalency half (+0.40/+0.43) and is dead in the ionic half
(-0.07). Reading:
1. The dataset has no strong-field ligands (halides/chalcogenides only) - the
   low-spin regime is never sampled; hund() high-spin assumption is safe here.
2. Covalency amplifies (not quenches) the metal anisotropy - consistent with the
   ligand-channel amplification finding.
3. NEW: the ionic 3d subset (fluorides/oxides) has NO xi*n_d signal - their MAE
   needs CF geometry detail / Stevens-shaped f(n_d) / dipolar terms (v1 territory).

## Octahedral orbital quenching at metals: tested, negative (2026-08-19)

User question: is quenching in octahedral environments captured (e.g., metal BVM
multipoles)? Tested the term-based flag (A/E quenched vs T unquenched, oct by cn>=6,
tet by cn<=5): medians REVERSED (T-term |MAE_onsite| 0.151 < A/E 0.308); x unq-flag
hurts (0.34 -> -0.18 onsite). Reason: MAE is second-order for everyone - quenched
A/E ions (d3,d5hs,d8,d4: Mn2+, Ni2+ abundant here) carry classic Stevens B2q
second-order anisotropy, often large; T-term first-order moments don't bypass the
second-order structure for E(z)-E(x). Geometry proxy crude (layered/trig-prismatic).
Full metal-site gate audit: CF Q2 (hurts), Q4 (neutral), Hund 2S (hurts), quenching
flag (hurts). The correct home for octahedral quenching physics is the v1 CF
machinery (actual e_g/t2g splitting + filling -> quenched dL_z automatically), not
scalar bond-multipoles.

## Environment-multipole weighting ablation: geometry carries the signal (2026-08-19)

User question: a SIMPLE structural-anisotropy measure (multipole of the chemical
environment of high-SOC atoms), not necessarily bond valence. Ablated the Q2
weighting at ligand sites (all sites averaged): unweighted COUNT +0.40/+0.45/+0.48,
covalency w_b +0.40/+0.47/+0.49, Z-weighted +0.32 (max-xi-site variant) — the
weighting changes correlations by ~0.01-0.02 only. Product features: count 0.434/
0.498/0.501 vs covalency 0.438/0.502/0.503 — indistinguishable. The GEOMETRY (which
neighbors in which directions) is the carrier; weights are nearly interchangeable
(and BVM would be too). Site selection matters more: single max-xi site ~0.32-0.38
vs all-ligand-site average ~0.40-0.49.
Practical: the simplest defensible descriptor is xi_p * |sum_neighbors
[P2(u.z)-P2(u.x)]| averaged over ligand sites — no bond valence, no covalency
tables needed for the anisotropy factor.

## Label-free source-gated neural check (2026-08-19)

Hard-gating by `soc_site` (`ligand` iff $\max\xi_p>\max\xi_d$) confirms that
the two mechanisms require different feature maps. An 11-parameter ligand
expert using covalency, ligand anisotropy, and their $\xi_p$ product achieves
signed onsite LOEO $\rho=+0.162$, RMSE 3.920 versus cohort baseline 3.970
($n=173$): a small calibration gain. Its absolute head improves rank
(+0.187) but not error (3.756 vs 3.664). The 9-parameter metal
$\xi_dn_d$ + Hund/Stevens expert remains below its baseline ($n=111$).
Routed overall scores remain negative: signed $\rho=+0.120$, RMSE 4.909
vs 4.743; absolute $\rho=+0.113$, RMSE 5.122 vs 4.542. This validates
classification as a diagnostic/feature-routing tool, not a predictive mixture.

## Final suggested model (2026-08-19)

Two-head, three scales, table-based:
- class: soc_site = ligand if max xi_p > max xi_d else metal
- ligand head: |MAE| ~ a * <xi_p w_2>_lig * <xi_p |Qzz-Qxx|>_lig  (a on train)
- metal head: |MAE| ~ b * xi_d * n_d
POOLED out-of-fold (LOEO, each structure held out once): rho(|MAE_total|) = +0.349,
|onsite| +0.439, |offsite| +0.425; ligand class +0.436, metal +0.182. (vs v0 <= 0.12,
v1 0.04.) Per-fold LOEO means are noisy (n_test 2-4 -> rho +-1; e.g. Au/Os folds) -
pooled OOF is the reported protocol. Sign: not predicted (screening model for |MAE|).

## Outlier analysis of the final model (2026-08-19)

UNDER-predictions (label >> pred):
1. Dilution: Mn2O8I2Mo2 (190x), AlMnI2S2 (117x) - the plain mean over ligand sites
   dilutes one heavy ligand (I, xi=1.0, cn=1) among 8 O (xi=0.037). FIX adopted:
   xi_p-weighted aggregation -> ligand subset +0.436 -> +0.466.
2. T-term metal in symmetric ligand field: VTe2 (117x), NbTe2 (61x) - d1 metals,
   Te Q2 ~ 0 (symmetric), |MAE| via the unquenched metal orbital moment - a channel
   the two heads do not cover (the first-order channel; doesn't correlate globally
   but dominates these).
3. Tail: Os2F8 (89x), Os2Cl8 (52x) - linear scale fitted to the median cannot reach
   d4 5d outliers; log-space fitting needed for RMSE.

OVER-predictions (pred >> label):
1. d8-d10 late 4d/5d halides: AgCl2 (100x), Au2I3Se3AgMn n_d=10! (71x), AuBr2, PdCl2 -
   LS t2g6 isotropy / d10 diamagnetism / Ir4+ Jeff=1/2 strong-SOC isotropy
   (Nb2S8NiIr 168x). The linear xi*n_d saturates wrongly. FIX tested: Hund theta2
   factor -> DESTROYS the metal subset (0.182 -> 0.015) because its zero points
   (d4 J=0, d5 S) are exactly where solid second-order MAE is LARGEST (Os2F8 is
   d4! free-ion term physics != solid MAE). d10-only cap: metal 0.182 -> 0.192,
   neutral. Conclusion: LS/strong-SOC regimes need the CF machinery, not scalar
   patches.
2. Suspect near-zero labels: FeI2 0.00, W18Te32 0.00, MnI2 0.04 - worth a DFT re-check.

ADOPTED final model: xi-weighted ligand product + plain xi*n_d metal:
pooled OOF +0.355 | ligand +0.466 | metal +0.182.

## Three user intuitions tested (2026-08-19)

(a) d5 metal in ligand class: CONFIRMED - spin polarization suffices. Median |MAE|
(d5 + heavy ligand, n=26) = 0.161 vs global 0.039 (4x baseline; channel alive),
~2x below ligand-class rest (0.311) = the missing metal-onsite addition, not a
suppression. Metal-onsite L=0 quenching does NOT kill the ligand channel.

(b) min(CF, SOC) crossover: physically right (Ir4+ xi>>CF -> Jeff locked -> 0.01;
Os2F8 xi~CF -> max) but NOT testable with our W proxy (always >> xi; harmonic and
hard-min forms both +0.208 vs +0.205 = no engagement). Needs the true DeltaCF:
v1 cf_spread from the CF cache is the follow-up scale.

(c) VTe2/NbTe2 ligand head silent: bond geometry, not 3D symmetry - V-Te bonds at
~49 deg from BOTH z and x (1T octahedron, 3up+3down; Q2=+0.01, dipole cancels too)
despite c/a~5.2 (strongly 2D). MAE carried by V d1 t2g degeneracy (t2g-restricted CF,
effective l~=1 inverted geometry) - same sigma/pi selectivity failure as at metal
sites; these are mechanism-wise METAL-head compounds misfiled by the xi class rule.
Fix direction: channel-aware class (e.g. ligand class AND metal T-term flag), or the
t2g-restricted CF feature from the v1 cache.

## Outlier fix attempts: what worked, what didn't (2026-08-19)

FIXED:
- Dilution class (stru_70 Mn2O8I2Mo2): 190x -> 48x by xi-weighted ligand aggregation
  (already adopted; ligand subset 0.436 -> 0.466).

ATTEMPTED, NOT FIXED (each with the measured reason):
- T-routing for VTe2/NbTe2 (3-head: L / M / T where T = symmetric-ligand Q2 < 0.05 +
  metal T-term): pooled 0.348 vs 0.355 - no gain. xi*n_d as T feature fails (V d1
  xi=0.066 -> tiny). v1 xi*|dLz| feature puts VTe2/NbTe2 at feature percentile 24/27
  - the mean-field CF model ALSO does not see their MAE. Verdict: VTe2/NbTe2 MAE is
  itinerant 2D band physics (t2g Fermi crossings) - beyond table-based scalars AND
  the v1 CF mean-field. Needs tier-2 DFT features or a real band calculation.
- min(CF, SOC) with the TRUE DeltaCF (v1 cf_spread, median 1.59 eV - the crossover
  IS in range for 5d xi~1): xi^2/CF form 0.180, min form 0.205 vs plain 0.205 - no
  improvement. cf_spread variation (driven by coordination/identity) does not order
  the metal-class MAE beyond xi*n_d. The crossover physics is real for the OUTLIERS
  (Ir4+ locked; Os2F8 resonant) but is a tail effect invisible to rank correlation.
- d8-d10/LS over-predictions: non-perturbative (Jeff isotropy) - not scalar-fixable.

FINAL ADOPTED MODEL (unchanged): two-head, xi-weighted ligand product + xi*n_d metal;
pooled OOF +0.355 (ligand 0.466, metal 0.182).

## Metal-ligand channel cancellation (2026-08-19)

User question: cancellation between metal and ligand contributions - addressable?
Measured structure of the labels:
- SIGNED mae_onsite vs mae_offsite anticorrelate (rho = -0.38): the two channels
  tend to OPPOSITE signs - systematic cancellation.
- MAGNITUDES co-vary (+0.69): big-anisotropy compounds have big channels.
- Cancellation metric ||on|-|off||/(|on|+|off|): median 0.43; 43% of structures
  above 0.5 (strong cancellation - the total is less than half the channel sum).
- This is exactly why |total| is harder to rank (pooled OOF 0.35) than either part
  (|onsite| 0.44, |offsite| 0.43).

Channel-matched reconstruction TESTED and rejected: fitting ligand->|offsite|,
metal->|onsite|, total = sum gives pooled 0.282 (vs 0.355) - adding two non-negative
magnitude predictions CANNOT reproduce cancellation (which needs opposite signs).
Parts are still well predicted separately (0.39-0.40).

PRACTICAL OUTPUT for cancellation-limited cases: report the two channel magnitudes
as a BAND: |MAE_total| in [ ||on|-|off|| , |on|+|off| ] - a factor-2 uncertainty
from full cancellation to full addition, with 43% of structures near the lower end.
Resolving the cancellation = the sign problem (open).

## Two-channel band model: implemented and calibrated (2026-08-19)

User: "let's try that" (the band output). Implementation:
- channel predictions: |mae_onsite| and |mae_offsite| each fitted on BOTH features
  (f_lig_product, xi*n_d) by 2-param lstsq, pooled OOF: rho 0.407 / 0.452.
- naive band [||on|-|off||, |on|+|off|] from PREDICTED channels: coverage 27.9% -
  both regressions pull to the mean, band too narrow. Rejected.
- CONFORMAL calibration (ratio quantiles on train folds, 90% nominal):
  coverage 88.9%, median width 5.99 mJ/m^2 = 19x the median |MAE|.
- ORACLE band (true channels): coverage 100% (verified with tol 1e-6; the earlier
  51.3% was floating-point boundary), median width 0.193.
VERDICT: the calibrated band is honest but nearly uninformative for screening
(19x wide). The two-channel decomposition buys interpretation, not precision:
for tight predictions the sign problem must be solved (the band from the TRUE
channels is 0.19 wide - the information is in the signs we cannot predict).
Deliverable: channel magnitudes (rho 0.41/0.45) + calibrated band as the
uncertainty statement; point prediction stays the two-head model (+0.355).

## RECOMMENDED OUTPUT CHANGED: predict the channels, not the total (2026-08-19)

Routed per-class, pooled OOF, per label:
- |onsite|  : +0.407 (ligand 0.472, metal 0.323)
- |offsite| : +0.451 (ligand 0.504, metal 0.327)
- |total|   : +0.355 (ligand 0.466, metal 0.182)  <- was the primary target
Findings:
1. Both channels beat the total - the total is corrupted by the sign cancellation.
2. The metal class nearly doubles (0.18 -> 0.32-0.33): the 4d/5d 'failure' was
   substantially the cancellation landing on the total label. xi*n_d carried real
   signal all along.
3. The ligand head predicts BOTH channels (0.47/0.50): the heavy-ligand p-hole drives
   its local anisotropy AND the Fert-Levy path - the DFT onsite/offsite split is a
   site-partition convention, not a mechanism split for the ligand channel.
NEW DELIVERABLE: |onsite| and |offsite| separately (primary), total = sum +/- the
calibrated band. Routing optional (2-feature unrouted matches routed on channels).


## Label decomposition semantics (user clarification, 2026-08-18)

The `onsite_offsite.xlsx` decomposition pools by site-pair topology, not chemistry:

- `MAE_onsite` = Σ_i intrasite(i) = **metal-site + ligand-site** CF anisotropy mixed
- `MAE_offsite` = Σ_{i≠j} intersite(i,j) = **M–M + L–L + M–L** cross terms pooled

Only 5 columns exist in the xlsx; no finer split is recoverable from the data.

**Measured consequences:**

1. Both model features predict |offsite| better than |onsite|
   (ligand 0.551 vs 0.505; metal 0.486 vs 0.350). The spin-transfer features
   (w_spin = √Σ w_b·min(n_d,10−n_d)) encode **M–L covalent cross physics**, so
   their success on the offsite label is consistent with offsite being dominated
   by the M–L cross term.

2. Site-resolved intrasite probes fail against both pooled labels:
   metal d-CF sum ρ ≈ +0.06–0.13; ligand p-CF sum ρ ≈ −0.07–+0.08
   (only exception: ligand p-CF vs |offsite| in metal class +0.22 — again the
   cross term). Single-site CF magnitude does not track the DFT channels.

3. Routing composites vs |total| are insensitive: max(on,off) 0.413 ==
   offsite-only 0.413; sqrt(on·off) or 0.3·on+0.7·off give 0.425 (marginal).
   No model change adopted.

4. Intersite-dominated structures (|off|≫|on|): Fe₂O₈I₂W₂ (8.6 vs 0.09),
   AgBr₂ (6.8 vs 0.94), Fe₃Se₄ — mostly multi-metal or heavy-ligand networks.
   Intrasite-dominated: Os₂F₈ (53.5 vs 1.8), ionic 3d compounds (CoF₂, FeF₄).

**Naming:** "onsite/offsite" in figures/notes = the pooled DFT decomposition
channels, NOT metal-vs-ligand chemistry. The physics story is: our features
capture M–L covalent anisotropy; the offsite label carries it best.


## v3.0: the ξ-scaling correction (the gate was a physics bug)

**User's methodological correction**: never use special rules (boolean gates,
tuned thresholds) — they overfit the outlier structure. Search for the real
physics instead.

**The real reason ionic 3d fluorides/oxides have μeV MAE while ionic 5d
Os₂F₈ has 51 mJ/m²**: MAE is a second-order spin-orbit effect,

  MAE ~ ξ² · |⟨g|L|e⟩|² / Δ_exc

— quadratic in ξ, suppressed by the excitation gap. The v2.x metal feature
(ξ_d·n_carrier) was linear: it over-predicted everything ionic with small ξ.
The ionicity gate was patching this scaling error structure-by-structure.

**Verification on ionic pairs** (same structure family, light ligands):

| pair | \|MAE\| ratio | ξ ratio | ξ² ratio |
|---|---|---|---|
| Os₂F₈ / FeF₄ | 57.1 | 6.9 | 47.4 |
| Os₂F₈ / CoF₂ | 53.8 | 5.4 | 29.7 |
| Os₂F₈ / FeF₂ (onsite) | 58 | 6.9 | 47.4 |
| Ru₂F₈ / FeF₄ | 6.4 | 2.1 | 4.5 |

The label ratios track ξ², not ξ.

**Definitive comparison (LOEO, composite vs |total|)**:

| metal feature | gate | comp ρ | met_off ρ |
|---|---|---|---|
| ξ (v2.1) | none | 0.390 | 0.486 |
| ξ | v2.2/v2.3 | 0.413/0.427 | 0.425/0.370 |
| **ξ²** | **none** | **0.455** | **0.573** |
| ξ² | v2.2/v2.3 | 0.409/0.411 | 0.484/0.473 |

ξ² without any gate beats every gated variant; adding a gate to ξ² is harmful.
Bootstrap: Δρ = +0.063 [+0.011, +0.115], 98.9% positive.

**The ligand feature was already quartic in ξ_p** (each ξ_p-weighted mean
contributes ξ_p²): ablation to squared collapses lig_off 0.551→0.322. The
M-L cross (kinetic exchange) channel needs two SOC insertions per amplitude
plus the transfer², consistent with Goodenough-type double perturbation.

**v3.0 model** (commit 4dd4815):
- ligand: f = ⟨ξ_p·w_spin·ξ_p⟩·⟨ξ_p·|Q₂|·ξ_p⟩, w_spin = √(Σ_b w_b·min(n_d,10−n_d))
- metal: f_on = max_i ξ_i²·n_i, f_off = Σ_i ξ_i²·n_i
- class routing by max ξ_p vs max ξ_d
- NO gates, NO thresholds
- ligand 0.505/0.551, metal 0.327/0.573, composite 0.455

**Rejected along the way**: ξ²/Δ_min (bond-model QEq gap too crude: 0.348).
The gap dependence is real physics but needs a better excitation-gap estimate
than QEq effective gaps (DFT-level CF gaps or experimental 10Dq tables would
be the principled sources).

## SOC-scale and ligand-path autoresearch (2026-08-20)

The final-model field named `xi_ae_eV` is the AE Dirac $j$-splitting
$\Delta_{\rm SO,nl}$, not the coefficient $\xi_l$ multiplying $\mathbf L\cdot\mathbf
S$.  The two obey

$$
\Delta_{\rm SO,nl} = \frac{2l+1}{2}\xi_l.
$$

Using $\Delta_{\rm SO}$ is physically coherent for this scalar descriptor: it is the
shell SOC energy span and already carries the angular scale.  In particular,
$\Delta_{\rm SO}/[\xi_l\sqrt{l(l+1)}]$ is $1.061$ for $p$ and $1.021$ for $d$ shells.
Replacing it everywhere by bare $\xi_l$ changed five SOC-route assignments and reduced
the deterministic LOEO composite from $+0.470312$ to $+0.440151$.  The model
documentation now calls this quantity $s_l=\Delta_{\rm SO,nl}$; the implementation is
otherwise unchanged.

Three continuous, parameter-free mechanism tests used the 337 SOC-bearing labels and
the same leave-dominant-element-out calibration.

| candidate | physical replacement | composite $\rho$ | ligand onsite/offsite $\rho$ | metal onsite/offsite $\rho$ | decision |
|---|---|---:|---:|---:|---|
| v3.3 baseline | separate ligand spin-transfer and local-$Q_2$ means | +0.470312 | +0.540930 / +0.585515 | +0.323005 / +0.520258 | retain |
| ion-stage metal SOC | $s_d\leftarrow(5/2)\xi_{\rm NIST}(M,q_{\rm formal})$ | +0.474370 | +0.547116 / +0.578299 | +0.325494 / +0.540132 | reject: inconclusive |
| local ligand product | $\sum_Xs_{p,X}^3w_{{\rm spin},X}|Q_{2,X}|/\sum_Xs_{p,X}$ | +0.463462 | +0.530417 / +0.580306 | unchanged | reject |
| direct M--X path | $\sum_Xs_{p,X}^3|\sum_{M\sim X}w_{MX}n_{d,M}a_{2,MX}|/\sum_Xs_{p,X}$ | +0.421709 | +0.480589 / +0.487856 | unchanged | reject |

Here $a_{2,MX}=P_2(\hat{\mathbf r}_{MX}\cdot\hat{\mathbf z})-
P_2(\hat{\mathbf r}_{MX}\cdot\hat{\mathbf x})$.  The ion-stage test used the NIST
one-electron convention and converted it to the model's $d$-shell energy span before
substitution; it did not introduce a charge gate or fitted interpolation.  Its
$+0.004058$ composite point change was not supported by paired resampling:
structure bootstrap 95% interval $[-0.007477,+0.015138]$, LOEO-group interval
$[-0.014680,+0.018907]$, and only 71.0% positive group draws.  It is therefore not an
evidence-supported refinement.

The two local-path variants fail for different reasons.  The local product loses a
small but consistent ligand signal, whereas explicitly binding the rank-2 response to
individual M--X bonds destroys the ligand offsite ranking.  The retained separated
means therefore encode a transferable ensemble-scale correlation that the present
geometry-only bond kernel cannot replace with a literal local path.  This leaves
Fermi-level-resolved ligand/metal hybridization, not another scalar bond contraction,
as the identifiable missing physics.

## Residual cancellation and Fermi-proximity boundary (2026-08-20)

The remaining large errors separate into channel cancellation, strong-SOC/low-spin
over-prediction, and missing itinerant or ligand-field response.  A structural
cancellation test was therefore evaluated before adding another magnitude feature:

$$
C_{\rm cancel} =
-\frac{2\,\mathrm{MAE}_{\rm onsite}\,\mathrm{MAE}_{\rm offsite}}
{\mathrm{MAE}_{\rm onsite}^2+\mathrm{MAE}_{\rm offsite}^2}.
$$

It is $+1$ for equal-magnitude opposite-sign channels and $-1$ for equal-magnitude
reinforcement.  Its label-free analogue $C_{\rm geom}$ uses the signed
ligand and metal rank-2 bond quadrupole sums in the same normalized product.  On the
337 SOC-bearing structures, $\rho(C_{\rm geom}, C_{\rm cancel})=-0.099152$ and the
channel-product sign agreement is 48.1%.  The available geometric quadrupoles do not
contain the missing channel-sign information.

The metal onsite over-prediction residual has a nonzero association with the largest
local $\Delta_{\rm SO,d}/\Delta_{\rm CF}$ ratio within the metal route
($\rho=+0.400926$).  This identifies the expected non-perturbative tail
(Au/Ir/late-shell sites), but not a transferable correction.  Three parameter-free,
nonnegative complements all failed the primary LOEO criterion:

| candidate | construction | composite $\rho$ | outcome |
|---|---|---:|---|
| v3.3 baseline | retained two-channel feature | +0.470312 | retain |
| bond resonance | ligand $p$--$d$ resonance $2|V|/\sqrt{\Delta\varepsilon^2+4V^2}$ | +0.471007 | reject: paired structure 95% $[-0.001100,+0.002502]$ and LOEO-group 95% $[-0.000922,+0.002452]$ |
| SOC saturation | $n_c\Delta_{\rm SO,d}^2/\sqrt{\Delta_{\rm SO,d}^2+\Delta_{\rm CF}^2}$ | +0.470170 | reject: primary decrease despite metal-offsite gain |
| directional exchange path | $n_c\xi_p^2w_{\rm cov}|P_2(\hat r_z)-P_2(\hat r_x)|$ | +0.470112 | reject: primary decrease despite metal-offsite gain |

The results bound this descriptor family: scalar geometry, atomic SOC, and two-level
level alignment can weakly move an offsite rank, but cannot identify band occupancy,
Fermi crossings, or the relative signs of the DFT decomposition channels.  The next
informative inputs are projected DOS moments, local magnetic/orbital moments, and
exchange splitting near $E_F$, or regenerated DFT labels for the suspect-zero cohort.
