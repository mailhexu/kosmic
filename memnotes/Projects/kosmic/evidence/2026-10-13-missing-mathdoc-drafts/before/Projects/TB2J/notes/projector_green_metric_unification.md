---
audience: both
okf_version: "0.2"
type: concept
artifact_role: knowledge
status: stable
created: 2026-10-02
updated: 2026-10-09
---

# Projector Green-function metric unification

## Canonical relation

For primal band-by-channel coefficients $C_{np}=\langle\phi_p|\psi_n\rangle$, the channel metric $S_{pq}=\langle\phi_p|\phi_q\rangle$, and spectral weights $g_{nn}=(z-\epsilon_n)^{-1}$,

$$
G_{\mathrm{cov}}=C^\dagger g C,\qquad C_{\mathrm{dual}}=C S^{-1},\qquad G_{\mathrm{dual}}=C_{\mathrm{dual}}^\dagger g C_{\mathrm{dual}}=S^{-1}G_{\mathrm{cov}}S^{-1}.
$$

The LKAG trace contracts the covariant local operator $\Delta$ with $G_{\mathrm{dual}}$. The metric may be applied to the Green matrix after its spectral sum or to coefficients before accumulation. For a Hermitian regularizing filter $F(S)$, the same identity is $F G_{\mathrm{cov}}F=(CF)^\dagger g(CF)$.

## Consequence for a shared implementation

The exporter should own basis-specific metric interpretation and present a canonical dual-channel coefficient representation (or primal coefficients plus an explicit metric/filter declaration). The shared core can then build one spectral Green matrix and evaluate the same LKAG contraction. Existing PAW coefficients are already dual in the paper's convention; NC--PAO coefficients require the overlap dressing, which can be performed on coefficients or on the completed Green matrix. See the [research memo](../subprojects/projector-green-unified/specs/research/2026-10-02-projector-green-metric-unification.md) and `mypapers/TB2J_projector/main.tex`, Sec. `sec:unified-green-implementation`.

## QE-specific separable-operator contract (verified algebra; G3-validated)

QE's ultrasoft generalized wavefunction overlap is $S_\psi=I+\beta q_{\mathrm{at}}\beta^\dagger$. Real QE 7.4 US and PAW dumps show that $q_{\mathrm{at}}$ and $I+q_{\mathrm{at}}$ are **not** the beta Gram $M=\beta^\dagger\beta$ (first-k block Frobenius discrepancies range from $121.609$ to $4223.086$). The nonlocal Hamiltonian instead has the separable form $V_{\mathrm{NL}}=\beta D\beta^\dagger$, with $D=\mathrm{deeq}$ and projector coefficients $P=\beta^\dagger\psi=\mathrm{becp}$. The exact contraction is

$$
\operatorname{Tr}[(\beta D_\uparrow\beta^\dagger)G_\uparrow(\beta D_\downarrow\beta^\dagger)G_\downarrow]=\operatorname{Tr}[D_\uparrow G_{\beta,\uparrow}D_\downarrow G_{\beta,\downarrow}],\qquad G_{\beta}=\beta^\dagger G\beta.
$$

Thus `becp` is already dual relative to the implicit basis dual to beta; `deeq` is its matching covariant separable-operator coefficient and `ProjectorGreenData.overlap_k=None`. Dressing only the Green matrix by $M^{-1}$ while leaving $D$ unchanged breaks the trace (three exact complex-rational SymPy trials). Jointly transforming both is equivalent but unnecessary. NC+KB has spin-independent `deeq` and no separable spin vertex; the exchange-vertex completeness question is settled in the next section. See the [QE research memo](../subprojects/qe-projector-exporter/specs/research/2026-10-08-qe-export-surface-and-operators.md) and [Architecture](../subprojects/qe-projector-exporter/specs/architecture.md).

## QE exchange vertex (validated on bccFe, 2026-10-09)

The separable pairing above is exact algebra but the **deeq-only spin vertex is physically incomplete**: bccFe G3 gave US $J_1\approx5.6$ meV and PAW $J_1\approx4.2$ meV vs GPAW $14.73$ / ABINIT-UPF $12.54$ meV with otherwise-exact diagnostics. `deeq↑−deeq↓` carries only the augmentation-channel term $\int Q\,\Delta V_{\mathrm{eff}}$ (plus PAW `ddd_paw`); the LKAG site vertex additionally needs the **beta-projected multiplicative** xc splitting $\langle\beta_i|\Delta V_{xc}|\beta_j\rangle$ (the GPAW `delta_xc` analog; d-channel $\approx2$ eV there vs $\approx1$ eV in deeq). QE dump v1.2 exports this projection (`dbeta_xc`, dense-grid, with a dump-time real/G-space Gram parity check). Because `dbeta_xc` is a **primal** matrix element while $G_\beta$ is undressed, the correct pairing applies the joint metric transformation to the new term only:

$$
\Delta_{\mathrm{op}}=M^{-1}\,\langle\beta|\Delta V_{xc}|\beta\rangle\,M^{-1}+(\mathrm{deeq}_\uparrow-\mathrm{deeq}_\downarrow),\qquad M=\beta^\dagger\beta
$$

(the deeq term is already a beta-representation operator; $\kappa(M)\approx58$ for Fe). Result: Fe PAW $J_1=14.76$ meV vs GPAW $14.73$ (0.2%); Fe US $J_1=16.15$ meV at $20^3$ full BZ, cutoff-insensitive (60→100 Ry) — inside the cross-code spread. See the [Architecture ADR-003 amendment](../subprojects/qe-projector-exporter/specs/architecture.md) and log 2026-10-09. NC+KB reconsideration: `dbeta_xc` is computable for any beta-projector family, so a future NC+KB phase no longer needs a separate χ-projection epic.

Sources: QE 7.4 `Modules/becmod.f90`, `PW/src/s_psi.f90`, `PW/src/newd.f90`; real golden-dump diagnostics and SymPy script in workspace `.tmp/qe-exporter/`; existing [PAW-vs-NC derivation note](paw_lkag_derivation.md).
