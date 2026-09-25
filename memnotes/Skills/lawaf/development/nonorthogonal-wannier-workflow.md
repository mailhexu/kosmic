---
type: Domain Topic
id: lawaf/development/nonorthogonal-wannier-workflow
domain: lawaf
audience: development
artifact_role: guideline
status: draft
summary: Build, verify, and optimize non-orthogonal Wannier/phonon LWF models in lawaf; raw gauge, constant GL, k-dependent optimizer, exact S-metric target, certified Mmn-form spread.
triggers: [nonorthogonal wannier, optimize nonorthogonal gauge, mmn form spread, exact smetric]
aliases: []
outcome: 
requires_procedures: []
governed_by: []
uses_knowledge: []
supported_by: []
supersedes: []
evidence: []
source_project: lawaf
source_sha256: c6249f18a2d1eab1c2f9810dae57fa0c7a512541e292dc91c600e39c1ccb2346
---

# Non-Orthogonal Wannier Workflow

Build and optimize non-orthogonal Wannier/LWF models in lawaf. Verified
2026-09-18 (commits 0ef42c8..47f3c34; HamiltonIO 829fc0f).
## Modes
- Raw projected (`orthogonal=False`): only `method="projected"` + `weight_func="unity"`. scdm-k always orthonormalizes; `mlwf` raises. Per-k weighting plus raw gauge is rank-deficient at selection arms. Off-mesh truncation ~5e-2 native phonon units (BaTiO3 2×2×2).
- Constant GL (`nonorthogonal_gauge=G`): every pipeline. `S^w = G†G delta_R0`; pencil `(G†HG, G†G)` congruence, bands exact at every k. Machine-exact with `use_ws_distance=False`.
- Optimized G: `lawaf.optimize_nonorthogonal_gauge(lwf.wannR, lwf.Rlist, lwf.Rdeg, pos)` with `pos = np.repeat(lwf.atoms.get_scaled_positions(), 3, axis=0)` (phonons), then `lawaf.apply_gauge_transform(lwf, G)`. Mandatory: logdet barrier `-mu log det(G†G)` and multi-start tilts. k-dependent: `optimize_kdependent_gauge(..., shells=1, G0=Gc)` with scale-invariant per-k `logdet(S/diag S)`, Tikhonov smoothness, optional offmesh_weight penalty. Large gains only when the orthonormal gauge is symmetry-pinned (BaTiO3 triplet 0.332735→0.332704).
## Exact S-metric and covariant MMN
`lawaf.exact_smetric_spread(lwf)`: exact discrete-site target, phonon LWFs
only (S=I); EWF/Siesta/W90 consumers raise. `lawaf.phonon_mmn(Uref, kpts,
cell)` + `lawaf.covariant_mmn_links`: exact phonon M(k,b), GL-covariant
links, verified 1e-15; diagnostics, not a full non-orthogonal MV optimizer.
Electron provider `lawaf.io.w90.read_mmn(path)`; never synthesize links
from same-k H/S.
## Mmn-form spread — `lawaf.mmn_form_spread` (certified)
`mmn_form_spread(mmn, nnlist, bvecs, wb, G=None)` gives per-state `omega_I`,
`total`, `centres`. Certified 8.5e-8 (Gaussian oracle, NK=512) and 4.2e-3
(quantum metric, 24^3). Link traps: use periodic parts
`u = e^{-2 pi i k x} phi`; BZ-wrap pairs need the G-phase on the second
reduced representative; b is `2 pi/NK` (1/NK inflates `Omega_I` by
`4 pi^2`); no 1/L normalization; the exact per-state target needs the
Berry-connection-squared subtraction; rough random-phase frames are invalid
providers.
## Verification
On-mesh pencil bands equal the orthogonal control (< 1e-8); off-mesh
equality only for constant G with WS off (< 1e-12); `SwannR` PSD, constant
G `max |S(R≠0)| < 1e-12`, `S(0) == G†G`; netCDF round trip preserves
`SwannR`. Examples: `example/Siesta/SrMnO3_SOC/downfold_nonorthogonal.py`,
`example/Phonopy/BaTiO3/DM_dip_wang/genwann_nonorthogonal.py`.
## Gotchas
Never run overlapping pytest (shared `phon_cache/` corrupts). Stage
uncommitted WIP surgically (`git add -p`); never stage
`phonon_downfolder.py` wholesale. Kosmic records: notes/downfolder_interface.md,
notes/nonorthogonal_wannier.md, research/2026-09-18..21 memos.