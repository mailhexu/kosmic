---
audience: both
artifact_role: knowledge
type: reference

status: draft
created: 2026-08-18
math_provenance: missing
math_provenance_reason: "bond-descriptor-physics.md display math requires one MathDoc marker per equation"
---

# Bond-descriptor physics: ionicity, hybridization, remaining configuration

How to estimate the nature of the chemical bonds from the element descriptors
([[mae-reference-dataset]], [[element-descriptor-extension]] research memo) plus the
structure (CIF geometry) — no new DFT. All quantities below are per metal–ligand bond,
aggregatable per site/structure.

## Data inputs (all local)

| Quantity | Source |
|---|---|
| $\varepsilon_{nl}$, $\xi_{nl}$, occ, config | `ae_soc_strengths.json` (= UPF `pseudo_energy`, Ry) |
| PAO radials $u_{nl}(r)$ | FR UPF `PP_PSWFC` via `pypao.orbital.read_orbitals` |
| $S_{nl,n'l'}(d)$ at real bond distances | `pypao.overlap.compute_overlap` (UPF needs `upf_cutoffs_bohr`) |
| bond lengths, coordination | CIF geometry ([[mae-reference-dataset]]) |

## 1. Ionicity — level mismatch

Charge-transfer drive of a bond is the reference-level gap

$$
\Delta\varepsilon = \varepsilon_M(n_d d) - \varepsilon_X(n_p p) ,
$$

with the two-level covalent/ionic split ($g = V/|\Delta\varepsilon|$):

$$
\iota = \frac{1}{\sqrt{1+4g^2}}, \qquad
w_{\rm cov} = \frac{4g^2}{1+4g^2} .
$$

Ligand $p$ levels vs Fe 3d ($-7.44$ eV) order exactly along chemical intuition:

| ligand | $\varepsilon_p$ (eV) | $\xi_p$ (eV) | $\Delta\varepsilon$ vs Fe 3d |
|---|---|---|---|
| F 2p | −11.09 | 0.064 | +3.64 (ionic) |
| O 2p | −9.02 | 0.037 | +1.57 |
| Cl 3p | −8.55 | 0.124 | +1.11 |
| Br 4p | −7.70 | 0.496 | +0.25 |
| S 3p | −6.98 | 0.084 | −0.46 |
| I 5p | −6.78 | 1.000 | −0.67 |
| Se 4p | −6.39 | 0.375 | −1.06 |
| Te 5p | −5.71 | 0.792 | −1.74 (covalent) |

## 2. Hybridization — overlap at the real distance

$S_{dp}(d)$ computed directly from UPF PAOs with `pypao.overlap` (demo, FeBr₂
`stru_276`, $d_{\rm Fe-Br} = 2.640$ Å): $|S(3d,4p)| = 0.069$ (largest d–p block; s–p, p–p
blocks 0.01–0.05). Coupling scales:

- Harrison: $V(d) = \eta_{ll'm}\,\hbar^2/(m_e d^2)$ — at this $d$, $V \sim 1$ eV.
- Wolfsberg–Helmholtz: $V = K\,S(d)\,\bar\varepsilon$, $K \approx 1.75$.

Fe–Br is nearly resonant ($\Delta\varepsilon = 0.25$ eV) → $g \approx 3.8$ → strongly
covalent; Fe–F/O would sit at $g \lesssim 1$ → ionic. Use $\Delta\varepsilon$, $S(d)$,
$g$ as *relative* descriptors and let the model learn absolute mapping.

## 3. Remaining electronic configuration — electron counting

Ionic limit: anion closes its $p$ shell (halide $-1$, chalcogenide $-2$; ordering fixed by
$\varepsilon_p$ table), metal charge from formula neutrality, remaining count

$$
n_d = G - q_M \qquad (G = \text{group valence electrons}),
$$

fractional for mixed-metal formulas (e.g. Te₂CoNi). Covalency correction from the bond
ionicities:

$$
n_d^{\rm eff} = G - \sum_{\text{bonds}} \iota_b .
$$

This $n_d$ (and $n_d^{\rm eff}$) selects the crystal-field orbital occupation — the direct
Bruno input.

## 4. V_NA parametrization — final ionization and hybridization environment

The neutral-atom potential $V_{\rm NA} = V_{\rm local} + V_H[\rho_{\rm PAO}]$
(`vna_descriptors.py`, 70 elements, knot tables + exact evaluator) is parametrized by
**derived bond quantities** (no analytic form fits: multi-Gaussian and screened-Coulomb
sums reach only 3–24% relative error in the bond window — V_NA has shell-shoulder
structure):

| Parameter | Meaning | Example (Fe / Te) |
|---|---|---|
| $V_{\rm NA}(r_b)$ at $r_b$ = 1.5–5 bohr | attraction where the tails overlap — level-shift drive | −9.44 / −15.25 eV at 2 bohr |
| $q_{\rm eff}(r) = -Vr/(2\,{\rm Ry})$ | Coulomb-equivalent charge seen at $r$ — effective ionicity of the environment before transfer | 0.69 / 1.12 e at 2 bohr |
| $r_{\rm cross}$ (1 eV, 0.1 eV) | reach of the neutral attraction — hybridization range | 3.45/5.00 and 3.56/4.95 bohr |
| decay exponent $\lvert d\ln|V|/d\ln r\rvert$ over [2,5] bohr | how fast the perturbation falls with distance | 5.0 / 5.7 |

**Final ionization**: the effective charge-transfer gap at distance $d$ uses the
free-atom gap shifted by the neutral potentials:

$$
\Delta\varepsilon_{\rm eff}(d) = \bigl[\varepsilon_X + V_{\rm NA}^{M}(d)\bigr] -
\bigl[\varepsilon_M + V_{\rm NA}^{X}(d)\bigr] ,
$$

(electron lands in $M$'s well, hole stays in $X$'s) — plus the post-transfer Madelung
term once $\iota$ charges move. The neutral piece is small at full bond distances
(Fe–Br at 4.99 bohr: free +0.25 → effective +0.18 eV; $q_{\rm eff} \approx 0.005$ e)
because neutral potentials decay fast — the *covalent pre-ionization* environment is
quantified by $V_{\rm NA}$ and $q_{\rm eff}$ at the overlap radii (1.5–3 bohr), where
they are order 0.1–1 e.

**Hybridization/CF**: the ligand perturbation entering cation matrix elements is
$V_{\rm NA}^{X}(\cdot - \mathbf{d})$ — use it (multipole-expanded, $q_{\rm eff}(d)$ as
the monopole) in place of point-charge or bond-valence proxies for the $B_{kq}$
([[prd]] open question). Parsing: `vna_potential(sym, r)`, `q_effective(sym, r)`,
`bond_params(sym)`.

## Link to MAE (the target)

$$
\mathrm{MAE} \approx -\frac{\xi_d}{4\mu_B}\,\Delta\langle L_z\rangle :
$$

- **on-site** ≈ $\xi_d \times$ local orbital polarization ← ($n_d$, ligand-field geometry,
  $w_{\rm cov}$ quenching);
- **off-site** ≈ ligand-mediated paths ← ($\Delta\varepsilon$, $S(d)$, $\xi_{p}^{\rm ligand}$).

Per-metal-site feature vector: $(\xi_d, n_d^{\rm eff}, \{d_b, S_b, \Delta\varepsilon_b,
\xi^{\rm ligand}_p\}_b, \text{coordination geometry})$ — matches the MAE on-site/off-site
label decomposition in the dataset.

## Caveats

- Free-atom $\varepsilon$ lack solid-state level alignment (Madelung shifts several eV in
  ionic compounds) — descriptors are references, not absolute solid levels.
- Harrison $\eta$ values are order-of-magnitude; prefer $S(d)$ as the primary computed
  quantity, $V$ secondary.
- UPF overlaps need explicit cutoffs (`upf_cutoffs_bohr`, e.g. 8 bohr) and converged
  `spacing_bohr`; j-pair PAOs should be occupation-weighted.
