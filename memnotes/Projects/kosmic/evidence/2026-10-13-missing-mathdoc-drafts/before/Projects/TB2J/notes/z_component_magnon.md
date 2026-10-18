---
artifact_role: knowledge
audience: both
confidence: 0.9
created: 2026-05-29
last_validated: 2026-05-29T00:00:00
validation_procedure: |
  Ran `source /home/hexu/projects/myenvs/mydev/bin/activate && python TB2J/examples/magnon/ruo2_z_component_magnon.py --npoints 200` from the TB2J package. The default path is `GXSG`, i.e. Gamma-X-S-Gamma, with explicit `S=(0.5,0.5,0)`. Also ran `python TB2J/examples/magnon/ruo2_z_component_magnon.py --diagonal-only-j --npoints 200`. Verified the script with `python -m py_compile` and `ruff check`. Final full and diagonal-only metadata files each have 116 rows: 4 Jzz-only cases and 112 mixed z-transverse cases. JSON labels verify the path as Gamma, X, S, Gamma.
validation_test: null
successful_usage_count: 1
last_used_successfully: 2026-05-29T00:00:00
usage_stale: false
related_files:
  - TB2J/examples/magnon/ruo2_z_component_magnon.py
  - TB2J/examples/magnon/ruo2_z_component_outputs/metadata.csv
  - TB2J/examples/magnon/ruo2_z_component_outputs/figures/jzz_FM_overlay.png
  - TB2J/examples/magnon/ruo2_z_component_outputs/figures/jzz_AFM_overlay.png
  - TB2J/examples/magnon/ruo2_z_component_outputs/figures/mixed_deviation_FM.png
  - TB2J/examples/magnon/ruo2_z_component_outputs/figures/mixed_deviation_AFM.png
  - TB2J/examples/magnon/ruo2_z_component_outputs_diag/metadata.csv
  - TB2J/examples/magnon/ruo2_z_component_outputs_diag/figures/jzz_base_FM.png
  - TB2J/examples/magnon/ruo2_z_component_outputs_diag/figures/jzz_base_AFM.png
  - TB2J/examples/magnon/ruo2_z_component_outputs_diag/figures/jzz_FM_overlay.png
  - TB2J/examples/magnon/ruo2_z_component_outputs_diag/figures/jzz_AFM_overlay.png
  - Refs/SPRKKR_RuO2/RuO2.str
  - Refs/SPRKKR_RuO2/RuO2_JXC_Jij.dat
related_functions:
  - read_sprkkr_exchange
  - sprkkr_to_spinio
  - Magnon.load_from_io
  - Magnon.get_magnon_bands
tags:
  - magnon
  - RuO2
  - SPRKKR
  - exchange_tensor
  - Jzz
project: TB2J
status: stable
validated_by: automatic
validation_date: 2026-05-29T00:00:00
links_to:
  - jzz_magnon_energy_report
  - sprkkr_magnon_implementation
  - magnon_hamiltonian
  - magnon_Jq_transform
linked_from: []
type: Project Knowledge
---

# RuO2 Magnon Bands Under Z-Component Exchange Tensor Variations

## Summary

The numerical RuO2 experiment confirms the analytic result in [jzz_magnon_energy_report](jzz_magnon_energy_report.md). For z-aligned Ru moments, changing $J_{zz}$ changes the magnon band energies strongly. Adding $J_{xz}$, $J_{yz}$, $J_{zx}$, and $J_{zy}$ on top of a fixed $J_{zz}$ does not change the harmonic magnon bands produced by `Magnon.Hq()` for this z-collinear setup; all mixed-component cases had max band deviation 0.0 meV from their same-state, same-$J_{zz}$ baseline.

The mixed terms still matter physically as torque indicators. In this experiment, source-site mixed entries such as $J_{xz}$ and $J_{yz}$ produce a nonzero transverse torque proxy, even though they do not enter the strict z-collinear harmonic matrix. This matches the derivation: mixed longitudinal-transverse entries generate linear terms around a non-stationary reference state, not transverse hopping/pairing terms.

Many tested FM and low-$J_{zz}$ AFM cases are dynamically unstable in the current LSWT calculation, and TB2J emitted the existing warning that the system may be far from the magnetic ground state. These cases are still useful for controlled sensitivity testing, but their negative energies should not be read as physical stable magnon spectra.

## Inputs

- Structure: `Refs/SPRKKR_RuO2/RuO2.str`
- Exchange table: `Refs/SPRKKR_RuO2/RuO2_JXC_Jij.dat`
- Magnetic species: Ru
- Moment magnitude: $0.5674\ \mu_B$ from the SPRKKR reference note
- FM z state: `[0.5674, 0.5674]`
- AFM z state: `[0.5674, -0.5674]`
- K path: `GXSG`, i.e. Gamma-X-S-Gamma, with explicit `S=(0.5,0.5,0)`
- Final path points: 200
- No `shells.dat` was used or required.

## Method

The experiment driver is `TB2J/examples/magnon/ruo2_z_component_magnon.py`. It uses the existing SPRKKR path:

1. `read_sprkkr_exchange()` reads the RuO2 structure and exchange rows.
2. `sprkkr_to_spinio(..., tensor_policy="transverse-block")` builds a `SpinIO` object containing the SPRKKR transverse block.
3. The script mutates `SpinIO.Jani_dict` in memory.
4. `Magnon.load_from_io(spinio, Jiso=True, Jani=True, DMI=False, SIA=False)` constructs the magnon calculator.
5. `Magnon.get_magnon_bands(path="GXSG", npoints=200, special_points={"S": [0.5, 0.5, 0.0], ...})` computes bands along Gamma-X-S-Gamma.

The driver also supports `--diagonal-only-j`. This option keeps only `Jxx`, `Jyy`, and `Jzz` and zeros `Jxy`, `Jyx`, `Jxz`, `Jyz`, `Jzx`, and `Jzy` before constructing the magnon calculator. When this option is used without an explicit `--output-root`, the default output directory is `TB2J/examples/magnon/ruo2_z_component_outputs_diag` so the full-tensor experiment is not overwritten.

For every exchange row, the reference longitudinal value was

$$
J_{zz}^{\mathrm{base}} = \frac{J_{xx}+J_{yy}}{2}.
$$

The Jzz-only phase set

$$
J_{zz}=s J_{zz}^{\mathrm{base}},
$$

with $s \in \{0, 1\}$.

The mixed-component phase used the same $s \in \{0,1\}$ and added modes for $J_{xz}$, $J_{yz}$, $J_{zx}$, $J_{zy}$ with $\alpha \in \{0.25,0.5,1,-1\}$.

## How Jzz Enters the Magnon Hamiltonian

Consider a tensor exchange interaction between two spins,

$$
H_{ij}=-\mathbf{S}_i^T J_{ij}\mathbf{S}_j
=-\sum_{\alpha\beta}S_i^\alpha J_{ij}^{\alpha\beta}S_j^\beta,
$$

where the sign follows the TB2J convention used in the magnon implementation. For a collinear reference state with both moments along $+z$, introduce Holstein-Primakoff bosons to harmonic order,

$$
S_i^z=S_i-a_i^\dagger a_i,
\qquad
S_i^x=\sqrt{\frac{S_i}{2}}(a_i+a_i^\dagger),
\qquad
S_i^y=-i\sqrt{\frac{S_i}{2}}(a_i-a_i^\dagger).
$$

The longitudinal part of the pair Hamiltonian is therefore

$$
H_{ij}^{zz}
=-J_{ij}^{zz}(S_i-a_i^\dagger a_i)(S_j-a_j^\dagger a_j).
$$

Expanding by boson order gives

$$
H_{ij}^{zz}
=-J_{ij}^{zz}S_iS_j
+J_{ij}^{zz}S_j a_i^\dagger a_i
+J_{ij}^{zz}S_i a_j^\dagger a_j
-J_{ij}^{zz}a_i^\dagger a_i a_j^\dagger a_j.
$$

Linear spin-wave theory drops the quartic term. The remaining quadratic contribution is

$$
H_{ij}^{zz,(2)}
=J_{ij}^{zz}S_j n_i+J_{ij}^{zz}S_i n_j,
\qquad n_i=a_i^\dagger a_i.
$$

Thus $J_{zz}$ does not hop a magnon from $i$ to $j$. Instead, it changes the onsite magnon energy because a magnon reduces the longitudinal spin length at its site. In a lattice, summing over neighbors gives the diagonal number term

$$
H_{zz}^{(2)}
=\sum_i a_i^\dagger a_i\sum_j S_j J_{ij}^{zz},
$$

up to the global sign and pair-counting convention. After Fourier transformation this remains diagonal in sublattice/spin index and contributes through the $\mathbf{q}=0$ exchange sum, not through the phase-dependent hopping term:

$$
H_{zz}^{(2)}
=\sum_{\mathbf{q},i} a_{\mathbf{q}i}^\dagger a_{\mathbf{q}i}
\left(\sum_j S_j J_{ij}^{zz}(\mathbf{0})\right).
$$

The transverse block behaves differently. Terms with $J_{xx}$, $J_{xy}$, $J_{yx}$, and $J_{yy}$ contain products such as $a_i^\dagger a_j$, $a_i a_j^\dagger$, $a_i a_j$, and $a_i^\dagger a_j^\dagger$. These are the terms that carry the Bloch phase $e^{-i\mathbf{q}\cdot\mathbf{R}}$ and form the normal and anomalous intersite blocks of the magnon Hamiltonian. Therefore the schematic ferromagnetic result has the familiar structure

$$
\omega(\mathbf{q})\sim S\left[J^{zz}(\mathbf{0})-J^\perp(\mathbf{q})\right],
$$

where $J^{zz}(\mathbf{0})$ is the longitudinal onsite field and $J^\perp(\mathbf{q})$ comes from the transverse exchange block. Removing $J_{zz}$ removes the first term and changes the magnon band energies even though the transverse hopping matrix is unchanged.

This is exactly how the current TB2J implementation organizes the calculation. `Magnon.Hq()` forms local transverse and longitudinal vectors $U_i$ and $V_i$, then constructs the Bogoliubov matrix blocks schematically as

$$
A_{ij}(\mathbf{q})\propto U_i^T J_{ij}(\mathbf{q})U_j^*,
\qquad
B_{ij}(\mathbf{q})\propto U_i^T J_{ij}(-\mathbf{q})U_j,
$$

and the diagonal longitudinal field

$$
C_i=2\sum_l S_l V_i^T J_{il}(\mathbf{0})V_l.
$$

For a z-collinear state,

$$
V_i=(0,0,1),
$$

so

$$
V_i^T J_{il}(\mathbf{0})V_l=J_{il}^{zz}(\mathbf{0}).
$$

The transverse vectors $U_i$ have only $x$ and $y$ components, so the $A$ and $B$ blocks sample only the $xx$, $xy$, $yx$, and $yy$ entries for a strict z-collinear reference state. The mixed entries $J_{xz}$, $J_{yz}$, $J_{zx}$, and $J_{zy}$ do not enter these quadratic blocks; instead, at pair level they generate terms linear in $a_i$ or $a_i^\dagger$ when the reference direction is not torque-free. This is why the numerical experiment finds that changing $J_{zz}$ shifts the bands, while changing only the mixed z-transverse entries leaves the harmonic z-collinear band energies unchanged.

## Figures

Jzz-only overlays:

![FM Jzz overlay](../../../../TB2J/examples/magnon/ruo2_z_component_outputs/figures/jzz_FM_overlay.png)

![AFM Jzz overlay](../../../../TB2J/examples/magnon/ruo2_z_component_outputs/figures/jzz_AFM_overlay.png)

Mixed-component deviation plots:

![FM mixed deviation](../../../../TB2J/examples/magnon/ruo2_z_component_outputs/figures/mixed_deviation_FM.png)

![AFM mixed deviation](../../../../TB2J/examples/magnon/ruo2_z_component_outputs/figures/mixed_deviation_AFM.png)

Raw case data and summary metrics are in `TB2J/examples/magnon/ruo2_z_component_outputs/metadata.csv`. Per-case JSON files are under `jzz/FM`, `jzz/AFM`, `mixed/FM`, and `mixed/AFM` in the same output directory.

## Diagonal-Only J Figures

These figures use `--diagonal-only-j`, so only `Jxx`, `Jyy`, and `Jzz` are retained. The standalone baseline figures use $J_{zz}=(J_{xx}+J_{yy})/2$.

![FM diagonal-only baseline](../../../../TB2J/examples/magnon/ruo2_z_component_outputs_diag/figures/jzz_base_FM.png)

![AFM diagonal-only baseline](../../../../TB2J/examples/magnon/ruo2_z_component_outputs_diag/figures/jzz_base_AFM.png)

The next figures vary $J_{zz}$ while still keeping only diagonal tensor terms.

![FM diagonal-only Jzz sweep](../../../../TB2J/examples/magnon/ruo2_z_component_outputs_diag/figures/jzz_FM_overlay.png)

![AFM diagonal-only Jzz sweep](../../../../TB2J/examples/magnon/ruo2_z_component_outputs_diag/figures/jzz_AFM_overlay.png)

Diagonal-only raw case data and summary metrics are in `TB2J/examples/magnon/ruo2_z_component_outputs_diag/metadata.csv`.

## Jzz Results

The following table lists minimum band energy and the two Gamma energies in meV for the Jzz-only phase.

| State | $J_{zz}$ scale | Min energy | Gamma band 0 | Gamma band 1 | Warnings |
| ----- | -------------: | ---------: | -----------: | -----------: | -------: |
| FM    |            0.0 |   -222.929 |     -222.929 |      176.930 |        1 |
| FM    |            1.0 |   -409.547 |     -409.547 |      -15.476 |        1 |
| AFM   |            0.0 |   -222.553 |     -222.553 |      -46.370 |        1 |
| AFM   |            1.0 |    -50.198 |      -50.198 |      112.423 |        1 |

The trend is strong and state-dependent. In the FM setup, switching from $J_{zz}=0$ to $J_{zz}=(J_{xx}+J_{yy})/2$ lowers both Gamma bands in this sign convention and keeps the calculation unstable. In the AFM setup, the same switch raises the second Gamma band but the sampled path still has a negative minimum in the full tensor run.

## Diagonal-Only Jzz Results

The diagonal-only run keeps only `Jxx`, `Jyy`, and the varied `Jzz`. It still shows a strong $J_{zz}$ dependence, while the $J_{xy}/J_{yx}$ contribution is removed from the transverse block.

| State | $J_{zz}$ scale | Min energy | Gamma band 0 | Gamma band 1 | Warnings |
|---|---:|---:|---:|---:|---:|
| FM | 0.0 | -167.987 | -167.987 | 191.633 | 1 |
| FM | 1.0 | -358.951 | -358.951 | 0.001 | 1 |
| AFM | 0.0 | -167.971 | -167.971 | -146.070 | 1 |
| AFM | 1.0 | 0.599 | 0.599 | 0.599 | 0 |

For the AFM diagonal-only case, the baseline $J_{zz}=(J_{xx}+J_{yy})/2$ gives nearly degenerate positive Gamma energies around 0.599 meV and no stability warning. The FM diagonal-only baseline still triggers the unstable-ground-state warning.

## Mixed Z-Transverse Results

The mixed phase included 112 cases: 2 states, 2 $J_{zz}$ scales, 7 mixed modes, and 4 amplitudes. The maximum absolute band deviation from the same-state and same-$J_{zz}$ no-mixed baseline was:

| State | Mixed cases | Max band deviation | Max torque proxy |
|---|---:|---:|---:|
| FM | 56 | 0.0 meV | 40.572 meV |
| AFM | 56 | 0.0 meV | 40.572 meV |

The zero band deviation is expected from TB2J's z-collinear harmonic projection. For z-aligned spins, the transverse vectors select the $xx/xy/yx/yy$ block for hopping/pairing, and the longitudinal $V$ vector selects $zz$ for the diagonal term. The mixed entries are not sampled in these quadratic blocks.

The torque proxy used here is a simple row-sum diagnostic over source-site $xz/yz$ entries. It is not a full magnetic-force calculation, but it records that the artificially injected mixed entries can represent a non-stationary reference direction even when the harmonic band matrix is unchanged.

## Validation

- `python -m py_compile TB2J/examples/magnon/ruo2_z_component_magnon.py` passed in the configured Python environment.
- `ruff check TB2J/examples/magnon/ruo2_z_component_magnon.py` passed.
- The smoke run with 20 points completed and wrote the same output schema.
- A diagonal-only smoke run with `--diagonal-only-j --npoints 20` completed; all rows had `diagonal_only_j=True`, max mixed torque proxy 0.0 meV, and max mixed band deviation 0.0 meV.
- The final full run with 200 points completed on `GXSG` and wrote 116 rows to `metadata.csv`, 116 JSON files, and six figures.
- The final diagonal-only run with 200 points completed on `GXSG` and wrote 116 rows to `ruo2_z_component_outputs_diag/metadata.csv`, 116 JSON files, and six figures including standalone baseline bands plus Jzz-sweep overlays.
- Refreshed JSON labels verify the path ordering: Gamma at index 0, X at index 58, S at index 116, Gamma at index 199.
- Pyright diagnostics reported missing `matplotlib` imports because the LSP was not using the activated project environment; the actual environment successfully imported matplotlib and generated figures.

## Interpretation

This experiment supports using `transverse-block-jzz` instead of plain `transverse-block` when a longitudinal diagonal term is needed from SPRKKR transverse-only data. Plain `transverse-block` removes $J_{zz}$ and therefore changes the diagonal LSWT contribution.

The experiment also supports the analytic statement that $J_{xz}$, $J_{yz}$, $J_{zx}$, and $J_{zy}$ do not change the strict z-collinear harmonic magnon bands in TB2J. They are better interpreted as signs of transverse torque or non-stationarity of the chosen z reference state unless the total torque cancels after summing all neighbors.

## Email Example Directory

The compact email-friendly example is `examples/magnon/ruo2_email_example/` in the merged TB2J worktree. It contains `run_ruo2_magnon_compare.py`, a README, PNG band plots, JSON band data, and a CSV table. The script compares `tensor_policy="isotropic"`, which uses scalar $J=(J_{xx}+J_{yy})/2$, against `tensor_policy="transverse-block-jzz"`, which keeps $J_{xx}$, $J_{yy}$, $J_{xy}$, and $J_{yx}$ and sets $J_{zz}=(J_{xx}+J_{yy})/2$.

## Linked Concepts

- [jzz_magnon_energy_report](jzz_magnon_energy_report.md)
- [sprkkr_magnon_implementation](sprkkr_magnon_implementation.md)
- [magnon_hamiltonian](magnon_hamiltonian.md)
- [magnon_Jq_transform](magnon_Jq_transform.md)
