---
type: reference
status: draft
audience: both
artifact_role: knowledge
math_provenance: missing
math_provenance_reason: "mixed_radius_solution_options.md display math requires one MathDoc marker per equation"
---

# Mixed-Radius Solution Options

## Overview
The current limitation comes from three coupled assumptions:
- one cutoff radius defines the primitive truncated-Bessel basis
- one cutoff radius fixes the primitive-space dimension under energy cutoff
- one cutoff radius is written into the exported ABACUS orbital file and shared mesh

This note proposes practical ways to work around or solve those limitations.

## Option 1. Keep ABACUS as-is and optimize over global `rcut`

### Idea
Do not try to put mixed radii inside one ABACUS basis file.
Instead, keep one global `rcut` per basis and optimize/rank bases across a sweep of candidate `rcut` values.

### Objective
Use

$$
J = \mathrm{spillage} + \lambda V
$$

with a global-radius volume model such as

$$
V = \sum_l n_\zeta^{(l)} \frac{4\pi}{3} r_c^3
$$

### Pros
- smallest code change
- fully compatible with ABACUS
- no file-format changes
- easy to benchmark

### Cons
- does not give different radii per channel
- only gives basis selection, not true mixed-radius construction

### Best use
- near-term ABACUS workflow
- first implementation of compactness-penalized spillage

## Option 2. Two-level optimization in ABACUS-CSW-NAO

### Idea
Keep the current inner spillage optimization over coefficients for a fixed `rcut`, and add an outer search over a small number of radius patterns.

Examples:
- global `rcut` sweep
- manual per-channel candidate patterns such as `(r_s, r_p, r_d)` for internal experiments

### Structure

For each radius pattern `R`:

$$
\mathbf{c}^*(R) = \arg\min_{\mathbf{c}} \mathrm{spillage}(\mathbf{c}; R)
$$

then rank the result by

$$
J(R) = \mathrm{spillage}(\mathbf{c}^*(R); R) + \lambda V(R)
$$

### Pros
- conceptually clean separation between coefficient optimization and compactness selection
- avoids differentiating with respect to radius
- can be implemented with grid search or Bayesian search

### Cons
- still limited by ABACUS output constraints if `R` includes mixed radii
- practical only if the basis export and consumer code support the radius pattern

### Best use
- radius-selection logic
- research prototype before deeper refactor

## Option 3. Shared outer grid with effective per-channel cutoffs

### Idea
Represent all radial functions on one common mesh up to

$$
r_{\max} = \max_l r_c^{(l)}
$$

and enforce

$$
\chi_{lz}(r) = 0 \quad \text{for } r > r_c^{(l)}
$$

### What this solves
- all channels can be stored on arrays of the same length
- internal code can carry different effective supports

### What it does not solve
- ABACUS file/header semantics may still assume one physical cutoff
- current coefficient-generation logic still needs per-channel primitive spaces

### Pros
- mathematically clean internal representation
- natural for codes that accept sampled radial functions on a common grid

### Cons
- not enough by itself for ABACUS
- still requires nontrivial refactor of basis construction

### Best use
- internal data model for a future mixed-radius implementation
- plausible route for SIESTA-like workflows

## Option 4. Per-channel primitive bases

### Idea
Define a separate primitive basis for each angular momentum channel:

$$
f_{lq}(r; r_c^{(l)}) =
\begin{cases}
j_l\!\left(\dfrac{z_{lq}}{r_c^{(l)}} r\right), & r \le r_c^{(l)} \\
0, & r > r_c^{(l)}
\end{cases}
$$

with channel-dependent basis size

$$
n_{\mathrm{bes}}^{(l)} = \#\left\{ q : \left(\frac{z_{lq}}{r_c^{(l)}}\right)^2 < E_{\mathrm{cut}} \right\}
$$

### What changes
- coefficient tensors become channel-dependent in size by construction
- reduced-basis transforms become channel-dependent
- initialization and projection routines must be generalized

### Pros
- mathematically consistent way to do mixed radii
- closest to the real physics motivation

### Cons
- substantial refactor
- incompatible with present ABACUS export assumptions

### Best use
- proper mixed-radius implementation in a code that supports it
- likely better aligned with a SIESTA-based path than an ABACUS one

## Option 5. Switch the mixed-radius target code to SIESTA

### Idea
If mixed cutoff radii are a hard requirement, move that part of the project to a code that already supports more flexible numerical atomic orbitals.

### Strategy
- keep ABACUS-CSW-NAO for current ABACUS-compatible basis workflows
- design a parallel SIESTA-oriented basis generator or exporter
- reuse the compactness-penalized objective idea there

### Pros
- avoids fighting ABACUS format limitations
- aligns implementation with target code capability

### Cons
- requires understanding SIESTA basis format and generation workflow
- duplicates some infrastructure unless abstracted cleanly

### Best use
- true mixed-radius NAO development

## Option 6. Use ABINIT as the reference engine for spillage

### Idea
Separate two roles that are coupled in the current workflow:
- reference-state generation
- localized-basis construction

Use ABINIT to generate planewave reference wavefunctions, then compute spillage of a candidate localized basis against those reference states.

### Conceptual objective

$$
J = \mathrm{spillage}_{\mathrm{ABINIT\ ref}} + \lambda V
$$

### Pros
- decouples reference quality from ABACUS-specific workflow
- may allow a cleaner cross-code benchmark of basis quality
- useful even if the final target code is not ABINIT itself

### Cons
- requires wavefunction/projection data interoperability
- more infrastructure work before it becomes useful

### Best use
- cross-code scientific benchmarking
- code-agnostic basis optimization research

## Option 7. Use penalty only for basis ranking, not inner optimization

### Idea
Do not modify the optimizer at first.
Keep current coefficient optimization exactly as-is, then after each candidate basis is generated, rank it by

$$
J = \mathrm{spillage} + \lambda V
$$

### Pros
- almost zero algorithmic risk
- no change to gradients or minimizer internals
- easiest validation path

### Cons
- penalty does not directly influence the coefficient search
- only affects model selection, not the fitted basis itself

### Best use
- first experimental stage
- useful baseline before integrating penalty directly into the loss

## Option 8. Penalize radial extent directly instead of cutoff radius

### Idea
Instead of penalizing nominal cutoff radius, penalize actual orbital extent measured from the generated radial functions.

Examples:

$$
V_{\mathrm{eff}} \propto \sum_{lz} \int r^2 |\chi_{lz}(r)|^2 w(r) \, dr
$$

or tail-sensitive measures such as

$$
T_{\mathrm{tail}} = \sum_{lz} \int_{r_0}^{\infty} r^2 |\chi_{lz}(r)|^2 \, dr
$$

### Pros
- penalizes actual diffuseness, not just nominal radius
- may be more physically meaningful

### Cons
- more expensive to evaluate
- less directly tied to code/runtime cost than simple `r_c^3`

### Best use
- later-stage refinement after a simpler penalty works

## Recommended Order

### Near-term
1. Implement Option 7 first: keep optimization unchanged and rank bases by $\mathrm{spillage} + \lambda V$
2. Then implement Option 1: use the same objective for global-`rcut` selection in ABACUS
3. If needed, move to direct loss integration for ABACUS-compatible workflows

### Medium-term
4. Investigate Option 5 for true mixed-radius basis support in SIESTA
5. Investigate Option 6 for ABINIT-based cross-code spillage evaluation

### Long-term
6. If mixed-radius basis generation is still a major target, build Option 4 with an internal shared-grid representation from Option 3

## Recommended Practical Split

- **ABACUS track:** compactness-penalized spillage with one global `rcut`
- **SIESTA track:** true mixed-radius basis representation
- **ABINIT track:** external reference-wavefunction engine for spillage benchmarking

This split matches the real constraints of the codes better than trying to force all goals into the current ABACUS orbital-file model.
