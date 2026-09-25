---
type: Domain Topic
id: tb2j/development/tensor-symmetrizer-audit
domain: tb2j
audience: development
artifact_role: guideline
status: draft
summary: Audit exchange-tensor symmetrization engines with an independent spglib invariance checker, per-orbit stabilizer averaging, and synthetic fixtures.
triggers: [symmetrize_J audit, exchange tensor symmetrization, DMI symmetrizer bug, Jani invariance check]
aliases: [symmetrizer audit]
outcome: 
requires_procedures: []
governed_by: []
uses_knowledge: []
supported_by: []
supersedes: []
evidence: []
source_project: tb2j
source_sha256: 3580ed8e1bfb5b5340739a14c8478ab28c985b801df8dae78834a485aa728410
---

# Tensor Symmetrizer Audit

Review or debug code that symmetrizes exchange tensors over space-group (SG) or magnetic-space-group (MSG) operations: TB2J `symmetrize_J.py`, HamiltonIO, downfolding.

## Independent checker

Build the checker as a throwaway script in `/tmp`; never put it in the repository; never reuse engine internals.
- Get operations from spglib: `get_symmetry_dataset((cell, xfrac, numbers), symprec)`; build `W_c = cell @ W @ inv(cell)`.
- Map sites by `W x + t (mod 1)` to the nearest atom within symprec; the map must be bijective.
- Map bond images: `d = x_j + R − x_i; d' = W d; R' = round(d' − (x_j' − x_i'))`; check the integer residual.

Run in order:
1. Decomposition round trip: `Γ == (tr/3)I + Jani + A(D)` with `A^{αβ} = ε^{αβγ}D^γ`; Jani is symmetric.
2. Reversal: `Γ[(-R),j,i] == Γ[(R),i,j].T`.
3. Full invariance: for every operation and every stored key with a present target, `Γ[target] == W_c Γ W_c^T` to about 1e-14. Residuals at input-noise scale (about 1e-3) mean biased averaging; exact zeros on wrong components mean wrong site maps.
4. Zero-snap hygiene: no component stays in `(0, zero_tol)` after symmetrization.
5. Disk round trip (`write_all` then `load_pickle`); synthetic SpinIO objects need a `distance_dict` (copy `_distance_dict` from `TB2J/tests/test_symmetrize_J.py`) plus positional `charges` and `index_spin`.

## Averaging semantics

Define orbits as connected components of the key-to-present-image graph over all operations (union-find or BFS; skip absent targets for edges only). Average each orbit under its set-wise stabilizer: operations `g` with `gO ⊆ O`. The stabilizer is always a group, so the orbit mean is exactly invariant.
Wrong design 1: global dataset closure drops sublattice-exchanging operations that are the only link between the (0,1) and (1,0) nearest-neighbor sublattices (bcc Im-3m case).
Wrong design 2: a flat mean that skips absent images per (key, operation) gives unequal weights and breaks invariance at noise scale.

## Synthetic fixture traps

- Seed `(1,0,R)` only together with `(0,1,−R)`; seeding both directions over an (0,1)-direction R list creates bonds longer than the cutoff and breaks operation closure.
- Cut on bond distance `|x_j + R − x_i| <= dcut`, never on `|R|`; with basis offsets, symmetry images keep bond length but change `|R|`. Enumerate each direction over its own box.
- `A@(0,0,0) + B@(½,½,z)` (2 atoms, tetragonal) is P4/nmm #129; its mirrors and site-exchanging operations forbid all DMI. For a genuine C4-only (P4) test, place B on a general-position 4-site orbit. Always print the spglib-detected group before asserting physics.
- Never hardcode per-group zero expectations; a site-exchanging mirror perpendicular to the bond kills only D parallel to the bond (D in-plane survives), and a C2 perpendicular to the bond kills only D parallel to the axis. Compute the symbolic orbit average instead (`docs/sympy/04_spacegroup_symmetrization.py`, 88 checks).

## Environment and proof standard

Source `/home/hexu/projects/myenvs/mydev/bin/activate` and run from the TB2J repo root, so `import TB2J` resolves to the repo. spglib 2.7 supports `get_magnetic_symmetry_dataset`; primed MSG operations act identically on all even-spin terms (bilinear Γ, rank-2 K) and only enlarge site-map orbits.
Green engine tests are not evidence. The independent operation-by-key invariance scan (every operation, every key, exact to about 1e-14) is the evidence.
