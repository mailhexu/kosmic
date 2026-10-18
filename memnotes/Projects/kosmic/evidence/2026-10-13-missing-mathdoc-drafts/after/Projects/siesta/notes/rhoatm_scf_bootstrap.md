---
artifact_role: knowledge
audience: both
confidence: 0.98
created: 2026-07-20
last_validated: 2026-07-23T00:00:00
validation_procedure: |
  Build siesta/_build/build/Src/siesta, run the focused CTest cases
  fe_spin_bootstrap_rhoatm and save_dm with SIESTA_TESTS_VERIFY=1, including
  their semantic output checks, and run the one-step Ni external-basis
  Vna.Source pseudopotential probe recorded below.
related_files:
  - "siesta/Src/dhscf.F"
  - "siesta/Src/m_handle_sparse.F90"
  - "siesta/Src/m_new_dm.F90"
  - "siesta/Src/read_options.F90"
  - "siesta/Src/setup_hamiltonian.F"
  - "siesta/Src/siesta_forces.F90"
  - "siesta/Src/siesta_options.F90"
  - "siesta/Tests/CMakeLists.txt"
  - "siesta/Tests/02.SpinPolarization/fe_spin_bootstrap_rhoatm.fdf"
  - "siesta/Tests/14.FileIO/save_dm.fdf"
  - "siesta/Tests/check_bootstrap_rhoatm.py"
related_functions:
  - "dhscf"
  - "new_DM"
  - "setup_hamiltonian"
  - "siesta_forces"
tags: ["scf", "rhoatm", "density-bootstrap", "spin-polarization", "vna"]
project: siesta
status: draft
validated_by: automatic
validation_date: 2026-07-23T00:00:00
links_to: ["external_basis_dm_initialization", "vna_pp_harris_consistency"]
linked_from: []
type: Project Knowledge
math_provenance: missing
math_provenance_reason: "rhoatm_scf_bootstrap.md display math requires one MathDoc marker per equation"
---

# Fresh-SCF bootstrap from rhoatm

`SCF.Bootstrap.Rhoatm` defaults to enabled for a fresh calculation containing an external `.orb` basis when the FDF option is omitted; it remains default-false for native-only generated bases. The default uses the broadcast `species%is_external_basis` flag, so every MPI rank resolves it identically in either Vna mode. An explicit `T` or `F` is authoritative. After `setup_H0` has made `m_dhscf%rhoatm`, SIESTA builds one Hamiltonian from that in-memory total density, diagonalizes it normally into an AO-representable density matrix, and then enters the unchanged ordinary SCF loop at `iscf=1`. It does not fit a density matrix to a grid and does not write or read a density-grid file.

## Initialization precedence

`m_new_dm` records the final initialization method. Method zero means the ordinary atomic DM was used; nonzero values mean a compatible `.DM`/`.TSDE` read, an in-memory reused/extrapolated DM, or a `DM.Init.Bulk` overlay. The bootstrap runs only for method zero. Restart/reuse methods emit a skip diagnostic before compatibility guards are evaluated.

`bulk_expand` reports whether at least one `%block DM.Init.Bulk` segment was successfully applied. `new_DM` records that provenance as `last_dm_init_method=4`, preventing the later rhoatm bootstrap from silently replacing the overlaid density matrix. Its local `init_method` remains unchanged so existing first-step mixing and TranSiesta branches retain their prior behavior. A present but empty block does not claim bulk provenance.

The bootstrap does not modify `mix_scf_first` or mixer history. The pre-step is `setup_hamiltonian(0, rhoatm_bootstrap=.true.)` followed by `compute_DM(0)`. The ordinary first iteration and its normal `SCF.Mix.First` behavior follow unchanged.

## Spin-density construction

`dhscf` first evaluates the ordinary atomic DM on the grid as physical up/down channels. At each point, negative numerical values are clipped before forming the bounded local polarization:

$$
p(\mathbf r)=\frac{\max(\rho_\uparrow,0)-\max(\rho_\downarrow,0)}
{\max(\rho_\uparrow,0)+\max(\rho_\downarrow,0)}.
$$

Zero-density points use $p=0$. The retained atomic density is made nonnegative and normalized to the target electron charge:

$$
\rho_0(\mathbf r)=\max(\rho_{\mathrm{atm}}(\mathbf r),0)
\frac{Q_{\mathrm{tot}}}{\int \max(\rho_{\mathrm{atm}},0)d\mathbf r}.
$$

The bootstrap channels are then

$$
\rho_{\uparrow,\downarrow}^{\mathrm{boot}}(\mathbf r)=
\frac{\rho_0(\mathbf r)}{2}\left(1\pm p(\mathbf r)\right).
$$

They are pointwise nonnegative, sum to the normalized `rhoatm`, and carry the ordinary atomic DM's local collinear polarization seed. Because `rhoatm` is the retained output of `rhooda`, this automatically includes `species%rhoatm_pp` when `Vna.Source pseudopotential` is active; `rhooda`, Vna construction, and `rhoatm_pp` storage remain unchanged.

`ntpl` is rank-local under MPI. The implementation therefore all-reduces the raw `rhoatm` integral before calculating the normalization scale, then all-reduces the resulting charge and spin diagnostics. It aborts if the globally seeded charge differs from `Qtot`.

## V1 compatibility guards

For a fresh atomic DM, activation requires collinear `spin%Grid==2`, an explicit `%block DM.InitSpin`, density-matrix mixing, diagonalization, no Harris functional, no DFT+U, no TranSiesta mode, no charge-grid input, and `DM.Init.RandomStates=0`. Unsupported configurations stop with a specific `SCF.Bootstrap.Rhoatm` message.

## Validation

Release build and focused regression:

```text
cmake --build siesta/_build/build --target SIESTA.siesta -j 4
SIESTA_TESTS_VERIFY=1 ctest --test-dir siesta/_build/build \
  -R '(fe_spin_bootstrap_rhoatm|save_dm|bulk_dm_bootstrap)' --output-on-failure
```

The focused run passes nine tests: execution, semantic output checking, and numeric comparison for each of three cases. The Fe3 MPI checker requires activation before `stepf` and `scf: 1`, unchanged `SCF.Mix.First = T`, finite charge normalization to the reported target, and nonzero bootstrap spin. Its output reports globally reduced charge `24.00001191 -> 24.00000000` and bootstrap spin `7.50235117`. The FileIO checkers require `restart/reuse skip (method 1 has precedence)` for a saved DM and `method 4 has precedence` after an observed `DM.Init.Bulk` overlay; both forbid the active diagnostic.

A one-step Ni external `.orb` probe used `basis_matrix/abacus_v2_pseudodojo/pbe_sr/psml/Ni.psml`, `Refs/Ni_gga_7au_100Ry_4s2p2d1f.orb`, and `Vna.Source pseudopotential`. It reported PP Vna/rhooda consistency, charge `17.99986171 -> 18.00000000`, bootstrap spin `2.30691478`, and then ordinary `iscf=1`.

The complete configured Release execution suite passed 264/264 tests. The environment has no Fortran LSP, so GNU compiler diagnostics from the CMake build are the source-level diagnostic gate.

## Linked concepts

- [external_basis_dm_initialization](external_basis_dm_initialization.md) explains why a grid density must be diagonalized rather than fitted directly to an AO DM.
- [vna_pp_harris_consistency](vna_pp_harris_consistency.md) defines why the retained `rhoatm` must stay consistent with Vna.
