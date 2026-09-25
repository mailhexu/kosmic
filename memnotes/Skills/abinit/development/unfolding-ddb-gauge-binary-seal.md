---
type: Domain Topic
id: abinit/development/unfolding-ddb-gauge-binary-seal
domain: abinit
audience: development
artifact_role: guideline
status: draft
summary: Debug and certify ABINIT DDB or Phonopy phonon unfolding weights when pristine bands show fractional weights or only a Gamma sector.
triggers: [unfolding fractional weights, ddb unfolding gauge, gamma-only unfolding, binary weight seal]
aliases: [unfolding gauge certification]
outcome: 
requires_procedures: []
governed_by: []
uses_knowledge: []
supported_by: []
supersedes: []
evidence: []
source_project: abinit
source_sha256: e21883cf5d128889f36ff1b455847b929ad0905113ed2c84e2ec7efcd2677570
---

# DDB Gauge Binary Seal

Use this procedure when DDB or Phonopy unfolding weights show fractional values on pristine bands or only a Gamma sector.

## Diagnostic

1. Reproduce the exact DDB path and compute the legacy character-sum binary residual: `bres = max(min(abs(w), abs(w - 1)))`.
2. Inspect translation maps and eigenvector layout; ABINIT/anaddb and Phonopy use different gauge conventions.
3. Treat fractional weights on a mirror-symmetric pristine path as possible degenerate cosine mixtures, not atom-index errors.

## Robust projector

For each q-point, identify one home atom per translation orbit. With the eigenvector matrix `E` in `(component, branch)` layout, build

```python
A = sum(exp(-2j*pi*(k_target - q_carry) @ r) * E[idx_r][home, :]
        for r, idx_r in translations) / sqrt(N)
H = A.conj().T @ A
```

1. Diagonalize `H` inside near-degenerate frequency groups.
2. Assign sorted eigenvalues to the group's branches; pristine systems give binary weights.
3. Use `q_carry=q` with gauge `"fold"` for Phonopy vectors; use `q_carry=0` with gauge `"bloch"` for ABINIT anaddb DDB vectors.

## Acceptance seals

1. Synthetic mixed-gauge regression: the legacy path stays fractional; the robust path reaches a binary residual below tolerance.
2. Real Phonopy fixture: the robust fold gauge agrees with the legacy group sums.
3. Real `examples/Cu_fcc/out_DDB`: the robust Bloch gauge reaches a binary residual below 1e-6 with three weight-one modes per q.
4. Run the full test suite and regenerate the Cu figure.
