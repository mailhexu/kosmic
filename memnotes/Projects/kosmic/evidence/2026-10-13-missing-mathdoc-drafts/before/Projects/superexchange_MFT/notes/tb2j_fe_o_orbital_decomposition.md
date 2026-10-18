---
artifact_role: knowledge
confidence: 0.8
created: 2026-05-15
last_validated: 2026-09-27T00:00:00
validation_procedure: |
  Ran TB2J through `TB2J.interfaces.tbupy_interface.gen_exchange_tbupy` on TBUpy two-metal/one-ligand results with `magnetic_elements=["Fe", "O"]` and `orb_decomposition=True`. Inspected AFM outputs in `/tmp/opencode/tb2j_orb_decomp_fe_o/angle90/TB2J/` and `/tmp/opencode/tb2j_orb_decomp_fe_o/angle180/TB2J/`, and FM outputs in `/tmp/opencode/tb2j_orb_decomp_fe_o_fm/angle90/TB2J/` and `/tmp/opencode/tb2j_orb_decomp_fe_o_fm/angle180/TB2J/`. Re-validated 2026-09-27 on the two-orbital ligand model: AFM nan pathology reproduced; FM references re-run for both angles.
validation_test: ".tmp/2m1l-2orb/fm90/TB2Jdir/exchange_orb_decomposition.out (2026-09-27)"
successful_usage_count: 9
last_used_successfully: 2026-09-27T00:00:00
usage_stale: false
related_files:
  - "/home/hexu/projects/TB2J_dev/TB2J/TB2J/interfaces/tbupy_interface.py"
  - "/home/hexu/projects/TB2J_dev/TB2J/TB2J/exchange_params.py"
  - "/home/hexu/projects/TB2J_dev/TB2J/TB2J/io_exchange/io_exchange.py"
  - "/home/hexu/projects/TB2J_dev/superexchange_MFT/workflows/streamlit_2m1l_exchange_demo.py"
related_functions:
  - "gen_exchange_tbupy"
  - "ExchangeNCL"
tags: ["superexchange", "tb2j", "orbital-decomposition", "ligand", "2metal-1ligand"]
project: superexchange_MFT
status: stable
audience: usage
validated_by: automatic
validation_date: 2026-05-15T17:00:00
links_to:
  - "streamlit_2m1l_exchange_demo"
linked_from: []
type: Project Knowledge
---

# TB2J Fe-O Orbital Decomposition

TB2J can treat the ligand O atom as a magnetic site in the two-metal/one-ligand model by running the TBUpy interface with `magnetic_elements=["Fe", "O"]` and `orb_decomposition=True`.

This is useful for separating one-electron exchange paths, but it is not a direct measurement of the local ligand Hund coupling between disconnected O orbitals. The TB2J orbital-decomposition output follows the Green-function exchange path and requires finite magnetic-site moments for atom-level normalization.

## Two-Orbital Ligand Update (2026-09-27)

The 2M-1L model now gives the ligand only the two planar p orbitals (`O1 : ('px', 'py')` in the TB2J output; `pz` never couples in the planar geometries). Re-run references with `nel=6`, `nz=20`:

| angle | pair | `J_iso` (meV) | orbital content |
| ---: | --- | ---: | --- |
| 90 | Fe1-O1 | 0.6549 | Fe1 couples through O `px` |
| 90 | O1-Fe2 | 0.6549 | Fe2 couples through O `py` |
| 90 | Fe1-Fe2 | 0.0000 | no connected one-electron path |
| 180 | Fe1-O1 | 0.6731 | Fe1 couples through O `px` |
| 180 | O1-Fe2 | 0.6731 | Fe2 couples through O `px` |
| 180 | Fe1-Fe2 | -9.4440 | common O `px` channel |

The AFM reference still shows the zero net O moment (`w_magmom 0.0000`) with `nan` O-involving entries, so the pathology below is unchanged. All tables in the AFM/FM Reference sections below and the Bruno section are 2026-05-15 records from the three-orbital ligand (`n_e=8`); the downfolding numbers in this note have been re-anchored to the new exact `J_b = 0.6549430391 meV`.

## AFM Reference

For the AFM reference, the net O moment cancels between O orbitals in both 90 degree and 180 degree cases. TB2J therefore normalizes by a zero O spin direction and emits `nan` for O-involving atom-pair exchanges.

Observed AFM moments were:

| angle | Fe1 | O px | O py | O pz | Fe2 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 90 | 0.9584 | 0.0416 | -0.0416 | 0.0000 | -0.9584 |
| 180 | 0.9490 | ~0.0000 | 0.0000 | 0.0000 | -0.9490 |

The 90 degree AFM reference contains opposite O `p_x` and `p_y` orbital spin polarizations but zero net O site moment. This makes O-as-magnetic-site TB2J ill-conditioned for O pairs even though the local O shell is internally spin polarized.

## FM Reference

For the FM reference, O has a finite induced moment, so Fe-O exchange entries are finite.

At 90 degrees, TB2J reports:

| pair    | `J_iso` (meV) | orbital content                |
| ------- | ------------: | ------------------------------ |
| Fe1-O1  |        0.6510 | Fe1 couples through O `p_x`    |
| O1-Fe2  |        0.6510 | Fe2 couples through O `p_y`    |
| Fe1-Fe2 |        0.0000 | no connected one-electron path |

At 180 degrees, TB2J reports:

| pair | `J_iso` (meV) | orbital content |
| --- | ---: | --- |
| Fe1-O1 | 0.6700 | Fe1 couples through O `p_x` |
| O1-Fe2 | 0.6700 | Fe2 couples through O `p_x` |
| Fe1-Fe2 | -9.3949 | direct Fe-Fe effective path through common O `p_x` channel |

## Interpretation

The 90 degree geometry has finite Fe-O exchange terms in an FM reference because each Fe polarizes its bonded O orbital. The Fe-Fe exchange remains zero when there is no O `p_x-p_y` one-electron mixing because the two Fe atoms couple to orthogonal ligand orbitals.

The ligand Hund contribution that changes the FM/AFM total-energy difference is a local interaction effect between O orbital spin polarizations. It should be estimated from local interaction-energy differences, constrained orbital-spin curvature, orbital-resolved susceptibility/kernel analysis, or a local Coulomb tensor, not from the Fe-only TB2J pair exchange.

## Rigid-Ligand Downfolding Estimate

A simple downfolding of the 90 degree FM exchange graph is possible only after assuming a ligand spin response. With the TB2J convention `E = -sum_ij J_ij e_i . e_j`, the symmetric graph has `J_Fe1-O = J_O-Fe2 = J_b = 0.6549 meV` and direct `J_Fe1-Fe2 = 0`.

If the O moment is treated as a freely rotating unit vector, eliminating its direction gives

$$
E_{\mathrm{eff}}(\theta) = -J_b |\mathbf{e}_1 + \mathbf{e}_2| = -2J_b\cos(\theta/2),
$$

where `theta` is the Fe-Fe angle. Matching the small-angle stiffness around the FM state, or matching the FM-AFM energy difference through `J_DeltaE = (E_AFM - E_FM)/4`, gives

$$
J_{\mathrm{eff}} = \frac{J_b}{2} = 0.3275\;\mathrm{meV}.
$$

This estimate has the same ferromagnetic sign as the self-consistent total-energy value `J_DeltaE = 0.2196 meV`, but it is larger. The difference is expected because the O moment in the TBUpy FM solution is small and induced (`m_O = 0.0842 mu_B`), not a rigid unit spin. A quantitative susceptibility-based downfolding requires the O transverse spin stiffness or local susceptibility, which cannot be determined from the three pair exchange constants alone.

If O `p_x` and O `p_y` are retained as two separate unit spins with ferromagnetic local Hund coupling `J_H^O = 500 meV`, the graph energy is

$$
E = -J_b \mathbf{e}_{\mathrm{Fe1}}\cdot\mathbf{e}_{p_x}
    -J_b \mathbf{e}_{p_y}\cdot\mathbf{e}_{\mathrm{Fe2}}
    -J_H^O \mathbf{e}_{p_x}\cdot\mathbf{e}_{p_y}.
$$

For Fe-Fe angle `theta`, symmetry reduces the minimization to

$$
E(\theta) = \min_\alpha [-2J_b\cos\alpha - J_H^O\cos(\theta-2\alpha)],
\quad
J_b\sin\alpha = J_H^O\sin(\theta-2\alpha).
$$

Using the FM-AFM energy mapping gives

$$
J_{\mathrm{eff}} = \frac{E_{\mathrm{AFM}}-E_{\mathrm{FM}}}{4}
= \frac{J_b}{2} - \frac{J_b^2}{8J_H^O}
= 0.3274\;\mathrm{meV}.
$$

The small-angle stiffness around FM gives `J_b J_H^O / (J_b + 2 J_H^O) = 0.3273 meV`. Since `J_H^O` is much larger than `J_b`, finite Hund coupling barely changes the rigid-ligand value.

A tabulated scan and plot for the ordinary Fe-O interaction are stored in `superexchange_MFT/data/models/2metal_1ligand/downfolding/`:

- `ordinary_fe_o_downfolding_vs_hund.csv`
- `ordinary_fe_o_downfolding_vs_hund.md`
- `ordinary_fe_o_downfolding_vs_hund.png`

For `J_H^O < J_b/2`, exact FM-AFM minimization gives `J_eff = J_H^O/2`; for `J_H^O >= J_b/2`, it gives `J_eff = J_b/2 - J_b^2/(8 J_H^O)`. The small-angle stiffness around FM is `J_eff = J_b J_H^O/(J_b + 2 J_H^O)`.

## Bruno-Renormalized Diagnostic

TB2J has a real-space Bruno correction implementation on branch `origin/bruno_realspace`. It adds `bruno_correction="fft"` and `bruno_correction="local"` to `ExchangeCL2`. The `fft` mode constructs real-space `J`, `K`, and `X`, Fourier-transforms to q-space, applies Bruno renormalization, and transforms back to real space.

For the 90 degree FM Fe+O reference with `magnetic_elements=["Fe", "O"]`, the branch was run in a detached worktree at `/tmp/opencode/TB2J_bruno_realspace` using the existing TBUpy result `/tmp/opencode/tb2j_orb_decomp_fe_o_fm/angle90/result.tbupy.nc`. The ordinary values are reproduced as `Fe-O = 0.6516 meV` and `Fe-Fe = 0.0 meV`. The `bruno_correction="fft"` atom-level matrix gives:

| pair | `Jnorm_R` (meV) |
| --- | ---: |
| Fe1-O1 | -49.3183 |
| O1-Fe2 | -49.3183 |
| Fe1-Fe2 | 24.7404 |

Using the two-orbital ligand downfolding model with `J_b = -49.3183 meV`, direct `J_12 = 24.7404 meV`, and `J_H^O = 500 meV`, the FM-AFM mapping gives

$$
J_{\mathrm{eff}} = J_{12} + \frac{|J_b|}{2} - \frac{J_b^2}{8J_H^O}
= 48.7915\;\mathrm{meV}.
$$

The small-angle stiffness gives `J_eff = J_12 + |J_b| J_H^O / (|J_b| + 2J_H^O) = 48.2405 meV`. The `bruno_correction="local"` approximation produced complex/non-symmetric values for this small induced-O-moment model and should not be used for this diagnostic.

The Bruno real-space implementation was patched in the detached worktree `/tmp/opencode/TB2J_bruno_realspace` after review. The patch keeps complex real-space `J/K/X` through the R-to-q transform and takes imaginary parts only in q-space, restores the Bruno left/right factors `(M-K^T) X^{-1} (M-K)`, makes q-space `calculate_all()` skip Bruno unless `bruno_correction` is enabled, and changes `local` mode into a real atom-level diagnostic approximation. Targeted tests pass with `pytest tests/unit/test_bruno_realspace.py tests/unit/test_bruno_correction.py`.

After the patch, real-space FFT and q-space Bruno agree for the 90 degree FM Fe+O reference. The large values remain (`Fe-O = -49.3183 meV`, `Fe-Fe = 24.7404 meV`), so they are not caused by a real-space/q-space mismatch. They are more likely due to the Bruno correction formula and magnetic-site choice for a small induced O moment. For this model, ordinary Fe-O downfolding remains the safer diagnostic.

## Bruno correction qualification (2026-09-30)

The numerical Bruno results above are **historical and unvalidated**. Primary
source [Bruno PRL 90, 087205](https://arxiv.org/html/cond-mat/0207592v2) corrects
the stiffness A in Eq. (11), with A=-J+diag(sum J), not J itself. The current
local q-space implementation adds the correction to J and repeats one of
the two mixed-response spin terms. Neither agreement of FFT and q-space
implementations nor those old large values validates the published method.

An independent spectral calculation on the certified six-electron spinor
reference verifies a consistent **full orbital-Hund extension** of Bruno's
inverse-susceptibility stiffness. After ligand relaxation it gives
0.540743855580540 meV, matching the certified full-density response to
1.10e-15 eV. Splitting-only diagonal Stoner renormalization yields zero on the
disconnected sectors. Thus no validated pure-Bruno recovery of the missing
Hund channel is claimed; explicit orbital Hund response is necessary.
See [collective-spin link](collective_spin_rotation.md) and the executable
certificate derivations/bruno_renormalization_link.py. This does not retroactively
diagnose the magnitude of old three-orbital results: reference/functionals differ.

## Linked Concepts

- [streamlit_2m1l_exchange_demo](streamlit_2m1l_exchange_demo.md)
- [hund_path_90deg_mft](hund_path_90deg_mft.md) - exact 90-degree Hund-path exchange, susceptibility form, and the MFT kernel requirement.
