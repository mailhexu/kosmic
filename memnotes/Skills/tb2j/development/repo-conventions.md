---
type: Domain Topic
id: tb2j/development/repo-conventions
domain: tb2j
audience: development
artifact_role: guideline
status: draft
summary: Branch discipline, mydev environment, pre-commit, tests and docs layout, sympy derivations, and VASP interface facts for the TB2J repository.
triggers: [TB2J repo conventions, TB2J branch discipline, TB2J pre-commit, TB2J docs build]
aliases: [TB2J development conventions]
outcome: 
requires_procedures: []
governed_by: []
uses_knowledge: []
supported_by: []
supersedes: []
evidence: []
source_project: tb2j
source_sha256: 69695f67ae8da81adaf8725057f1cb39e1c22e598b9ac09056073eb1334441fe
---

# TB2J Repo Conventions

The repository lives at `/home/hexu/projects/TB2J_dev/TB2J` and carries many long-lived user branches.

## Branch discipline

1. Run `git branch --show-current` before every commit and confirm the placement.
2. Repair a commit on the wrong branch by cherry-pick plus a reset of the user's branch.
3. Do not mix unrelated commits into `RISB`; the user owns that in-progress quasi-particle interface (story S1).
4. The `symmetrize` branch holds the rewritten symmetrizer: exact space-group/magnetic-space-group (SG/MSG) orbit projection, per-orbit stabilizer averaging, `zero_tol`, docs, and a sympy derivation; it is pushed.

## Environment, tests, docs

Source `/home/hexu/projects/myenvs/mydev/bin/activate` (Python 3.11, sympy, spglib 2.7, sisl). From the repo root, `import TB2J` resolves to the repo package, and `python -m pytest TB2J/tests -q` runs the suite in under 30 s. Sphinx parses MyST markdown in `docs/src/`; the toctree lives in `docs/index.rst`; verify with `python -m sphinx -b dummy docs /tmp/out -q`. `.rst` links inside markdown pages produce house-style warnings (recommonmark).

Pre-commit runs ruff and ruff-format. ruff-format rewrites files and fails the commit; re-run `git add` on the reformatted files and commit again.

## Sympy derivations

Put each new derivation in `docs/sympy/NN_topic.py` (runnable, assertion-checked, mydev environment) plus a companion `.md` report in the style of 01/02/03/04. The sphinx build excludes `docs/sympy`.

## VASP native interface

A patched VASP writes `tb2j_native.bin` (format v4-v6) automatically after SCF; no INCAR switch exists. Conditions: LSTOP, ISPIN <= 2, NCDIJ <= 2, default ISYM. `TB2J/scripts/vasp_native2J.py` consumes the file; the Wannier90 route uses `LWANNIER90`. The patch lives in `~/projects/TB2J_dev/ABINIT_VASP_FeO_package/source/VASP_TB2J_patch/`.

## Symmetrizer semantics (if extending)

For a pair tensor `Γ = J_iso·I + Jani + A(D)` with `A^{αβ} = ε^{αβγ}D^γ`:
- Reversal: `Γ_ji(-R) = Γ_ij(R)^T`; operation action: `Γ' = W_c Γ W_c^T` with `W_c = cell·W·cell^{-1}`.
- D is axial: `D' = det(W_c) W_c D`; primed MSG operations cancel spin flips in bilinear and rank-2 terms and only enlarge site-map orbits.
- With truncated data, orbits are connected components of the key-to-image graph; average each orbit under its own set-wise stabilizer. Never flat-average over partially defined operations.
- Moriya rules for site-exchanging operations (mirror or C2 perpendicular to the bond): exactly one D component dies per operation, not all of D; `docs/sympy/04` verifies this.
