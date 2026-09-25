---
type: Domain Topic
id: abinit/development/pymultibinit-phonon-band-comparison
domain: abinit
audience: development
artifact_role: guideline
status: draft
summary: Compute finite-displacement phonon bands with fitted pymultibinit models and overlay an ML reference such as MACE on identical q-paths.
triggers: [pymultibinit phonon bands, MACE overlay, frozen phonon calculator, seekpath band path]
aliases: [phonon band comparison]
outcome: 
requires_procedures: []
governed_by: []
uses_knowledge: []
supported_by: []
supersedes: []
evidence: []
source_project: abinit
source_sha256: ba4bf91534439acbd2e864c7afe0e0a9be4a139cc8bdc6dc6abf59de340953dd
---

# pymultibinit Phonon Band Comparison

Compute finite-displacement (FD) phonon bands at arbitrary structures with a fitted pymultibinit effective potential, and overlay a machine-learning (ML) reference such as MACE on identical q-paths.

## Recipe

1. Build the calculator: `MultibinitCalculator.from_pyeffpot(ddb_file=model.ddb, xml_file=fitted.nc, ncell=(2,2,2)*?, match_tolerance=0.35)`. Raise the tolerance for any structure displaced more than about 0.1 Å from the model reference; metastable distortions fail at 0.1.
2. Compute FD phonons: `atomchain.phonon.frozenphonon.calculate_phonon(atoms, calc=calc, ndim=np.eye(3)*2, phonon_save_dir=cache, parallel=False)`. The call evaluates the 2×2×2 supercell, which must match the model ncell atom count; the cache dir lets reruns resume from force pickles.
3. Build the band path: `get_band_qpoints_by_seekpath(ph.primitive, npoints=41)` returns `(qpoints, labels, path_connections)` in this order; labels are per-segment endpoint pairs.
4. Draw: `ph.run_band_structure(bands, path_connections=connections)`. Do not pass the pair list as labels (phonopy raises UFuncNoLoopError). Draw ticks yourself: the start symbol of the first pair, then the end symbol of each pair at the cumulative segment distance.
5. Overlay: plot `bd['frequencies']` versus `bd['distances']` per segment (reset x to the cumulative length) for both models.

## Environment

- torch/MACE in mydev needs `LD_LIBRARY_PATH=/home/hexu/projects/myenvs/mydev/lib/python3.11/site-packages/nvidia/cu13/lib` (libnvrtc-builtins.so.13.0), or TorchScript fails.
- pymultibinit resolves to the repo source through the editable install; atomchain likewise.

## Limitations

- Non-diagonal supercells (for example M2 `[[2,1,0],[0,1,0],[0,0,1]]`) cannot be represented by the model (diagonal ncell only); those phases are FD-only through atomchain.
- Sheared or compressed cells can still fail atom matching even at tolerance 0.35 (wrong sublattice, about 1.9 Å mismatch): a structural failure, not a tolerance issue.

Reference implementation: `atomchain/.tmp/phonon_metastable/run_phonons.py`; example outputs in `atomchain/examples/08_training_set_strategies_batio3/batio3_rattle_fw_s0.25/report_phonon.md`.
