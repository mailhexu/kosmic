---
type: reference
status: stable
audience: both
artifact_role: knowledge
---

# Chiral Domain Multiplicity and Enantiomers

---
confidence: 0.95
created: 2026-02-23
last_validated: 2026-02-23
validation_procedure: "Standard crystallographic group-subgroup relationship formulas."
project: symphon
status: validated
validated_by: automatic
tags: [domains, phase-transitions, symmetry]
---

## Overview
This note describes how structural domains (twins) and enantiomeric (chiral) domains are counted and classified during a displacive phase transition from a parent to a chiral daughter space group in `chiral_transitions.py`.

## Principles
When a crystal undergoes a phase transition to a lower symmetry group, the lost symmetry operations become twin operations that map the resulting structure into equivalent domain variants.

## Variables
The following variables are used in this note (see [[notation]] for full definitions):

| Symbol | Description | Units |
|--------|-------------|-------|
| $n_{d}$ | Number of distinct structural domains | dimensionless |
| $|G_{p}|$ | Order of the point group of the parent space group | dimensionless |
| $|G_{d}|$ | Order of the point group of the daughter space group | dimensionless |
| $V_{ratio}$ | Volume ratio between the primitive daughter cell and primitive parent cell | dimensionless |

## Equations
The fundamental equation for counting total structural domains is the index of the daughter group in the parent group:

$$
n_{d} = \frac{|G_{p}|}{|G_{d}|} \times V_{ratio}
$$

In the implementation (`domain_multiplicity`), we use the order of the primitive cell operations (rotations) for both parent and daughter to compute the rotational index, and multiply by the supercell expansion factor `$V_{ratio}$` derived from the $q$-point.

## Enantiomeric Domains
A chiral phase transition starting from an achiral parent creates structural domains. Since the daughter must be a Sohncke group (containing only proper rotations), the transition *must* lose all improper operations present in the parent.

An **enantiomeric twin pair** (left-handed vs right-handed domain) is formed if the transition loses an operation that changes handedness. These include:
- Inversion (`i`)
- Mirror plane (`m`)
- Glide plane (`g`)

In `_count_enantiomeric_domains`, the algorithm inspects the list of `LostOperation`s. If any inversion, mirror, or glide is present in the parent but absent in the daughter, the structure forms enantiomeric domain variants (count = 1 pair).

## Linked Concepts
- [[sohncke_space_groups]]: Enantiomorphous space group pairs.
- [[chiral_transition_enumeration]]: Finding the symmetry breaking transitions that generate these domains.
