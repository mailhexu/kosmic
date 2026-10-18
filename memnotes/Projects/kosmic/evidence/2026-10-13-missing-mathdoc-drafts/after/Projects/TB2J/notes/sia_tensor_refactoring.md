---
artifact_role: knowledge
audience: both
confidence: 0.9
created: 2026-04-02
last_validated: 2026-04-02T10:00:00
validation_procedure: |
  Read and verified all modified files:
  - TB2J/io_exchange/io_exchange.py: SpinIO class, sia_tensor, get_sia_energy()
  - TB2J/io_exchange/edit.py: set_anisotropy(), set_sia_tensor(), remove_sia_tensor()
  - TB2J/io_exchange/io_multibinit.py: XML output with spin_sia_tensor_list
  - TB2J/io_exchange/io_vampire.py: _sia_tensor_to_k1_k1dir() helper
  - TB2J/io_exchange/io_tomsasd.py: _sia_tensor_to_k1_k1dir() helper
  - TB2J/io_exchange/io_txt.py: removed legacy k1/k1dir section
  - TB2J/symmetrize_J.py: fixed pre-existing bug in Jonly path
project: TB2J
status: draft
validated_by: automatic
tags: [sia, anisotropy, tensor, refactoring, spinio]
type: Project Knowledge
math_provenance: missing
math_provenance_reason: "sia_tensor_refactoring.md display math requires one MathDoc marker per equation"
---

# Single-Ion Anisotropy Tensor Refactoring

## Overview

Refactored the `SpinIO` class to represent single-ion anisotropy (SIA) exclusively as a full 3×3 anisotropic tensor (`sia_tensor`) rather than the legacy scalar+direction pair (`k1`, `k1dir`).

## Energy Convention

The SIA energy is computed as:

$$
E_{\text{SIA}} = -\sum_i \mathbf{S}_i^T \mathbf{A}_i \mathbf{S}_i
$$

where $\mathbf{A}_i$ is the 3×3 SIA tensor for atom $i$, and $\mathbf{S}_i$ is the spin vector.

For uniaxial input with amplitude $k_1$ and direction $\hat{e}$, the tensor is built as:

$$
\mathbf{A} = k_1 \, (\hat{e} \otimes \hat{e})
$$

## Key Changes

### SpinIO (`io_exchange/io_exchange.py`)

- Removed legacy `self.k1`, `self.k1dir`, `self.has_uniaxial_anistropy` instance attributes
- `has_uniaxial_anistropy` is now a read-only property returning `self.has_sia_tensor`
- Added `get_sia_energy(spinat=None)` method to compute SIA energy from tensor
- `sia_tensor` is a dict mapping spin index to 3×3 numpy array

### Edit API (`io_exchange/edit.py`)

- `set_anisotropy(spinio, species, k1=None, k1dir=None, tensor=None)`:
  - Primary interface: `tensor=` (full 3×3)
  - Convenience interface: `k1` + `k1dir` (builds A = k1·(ê⊗ê))
  - Mixing both raises `ValueError`
- `set_sia_tensor(spinio, species, tensor)`: sets tensor directly
- `remove_sia_tensor(spinio, species=None)`: removes for species or all

### Output Writers

- **Multibinit** (`io_multibinit.py`): Uses `spin_sia_tensor_list` / `spin_sia_tensor_term` (9 elements flattened)
- **VAMPIRE** (`io_vampire.py`): Added `_sia_tensor_to_k1_k1dir()` to extract effective k1/k1dir from tensor
- **TomASD** (`io_tomsasd.py`): Same tensor→k1/k1dir fallback
- **TXT** (`io_txt.py`): Removed redundant k1/k1dir sub-section (tensor already written by `write_sia_section()`)

### Other Fixes

- **symmetrize_J.py**: Fixed pre-existing bug where `self.k1 = None` etc. were set on the `TB2JSymmetrizer` instance instead of `self.new_exc` (the SpinIO copy)
- **TB2J_edit.py CLI**: Updated `cmd_show` to display `sia_tensor` matrix instead of k1

## Design Decisions

1. **No backward compatibility**: Old pickle files with `k1`/`k1dir` don't exist, so no migration code needed
2. **Tensor-first API**: `tensor=` is the primary interface; k1/k1dir is convenience only
3. **Legacy format support**: VAMPIRE and TomASD only support uniaxial anisotropy, so a tensor→k1/k1dir conversion helper extracts the dominant eigenvalue/eigenvector
4. **Separate from SpinHamiltonian**: `SpinHamiltonian` and `SpinXmlParser` have their own independent `k1`/`k1dir` — these were NOT changed

## Linked Concepts

- [magnon_hamiltonian](magnon_hamiltonian.md): SIA contributes to the Hamiltonian diagonal blocks
- [notation](notation.md): Variable conventions for anisotropy
