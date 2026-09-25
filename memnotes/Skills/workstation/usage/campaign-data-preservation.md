---
type: Domain Topic
id: workstation/usage/campaign-data-preservation
domain: workstation
audience: usage
artifact_role: guideline
status: draft
summary: Promote disposable campaign runs into a paper data tree: per-leg inputs, outputs, and scripts; verify real output directory names; flag disputed numbers.
triggers: [campaign data, preserve runs, paper data tree, TB2J_results, DISPUTED]
source_project: native
source_sha256: empty
aliases: [data preservation]
---

# Preserve disposable campaign runs into a paper data tree

When promoting scratch runs (`.tmp/<campaign>/`) into a committed paper `data/` tree, follow this checklist. Learned from the CrI3 tri-code SOC campaign (TB2J_projector paper).

## Per-leg preservation

For each run leg, copy:

- Inputs: decks (INCAR/KPOINTS/POSCAR/POTCAR, ABINIT `.in`, GPAW runner `.py`).
- The final exchange output (`exchange.out`). VERIFY the actual output directory name first. TB2J's VASP native CLI writes `TB2J_results/`; older flows used `TB2J_results_vasp/`; abinao writes `TB2J_results_<tag>/`. A `[ -f ... ] && cp` guard fails SILENTLY when the assumed directory name is wrong — `ls` the scratch dir and confirm the copy landed before declaring success.
- The extraction and parsing scripts the numbers depend on.
- Small state files that prove completion (`campaign_done.txt`, summaries, `leg_export.json`).

Never copy giant binaries (WFK/VXC over 100 MB, full `.gpw`). Projector NetCDFs (about 7-60 MB) are the right reproducibility artifact for the ABINIT and GPAW projector paths.

## Run scripts

Commit the exact runner and exporter scripts per code into `data/<campaign>/<CODE>/scripts/` (or per leg). The user requires full workflow reproducibility: SCF launcher, exporter, extraction, summary. Document in the tree README per code:

- Launch command (mpirun rankfile / OMP threads).
- Environment pinning (for example `PYTHONPATH` to the branch worktree that has the exporter).
- Required deck flags (for example VASP `SYMPREC=1e-2`, explicit `GGA=PE`).

## Status honesty

If a code's numbers contradict cross-code references, mark rows `DISPUTED` in `comparison.csv` and write the discrepancy plus diagnostic plan in the README. Run the discriminating leg (for example collinear on the identical deck) before quoting. Never silently reconcile.

## Commit

The paper repo is its own git root. Commit with a scoped `git add data/<campaign>`; keep the user's unrelated dirty files out.
