---
type: reference
status: stable
audience: both
artifact_role: knowledge
---

# PAW Projector Snapshot Contract

---
confidence: 0.95
created: 2026-08-11
last_validated: 2026-08-11
validation_procedure: "Run TB2J/tests/tests/test_paw_projector.py together with projector Green and ABINIT PAW regression tests."
project: TB2J_dev
status: validated
validated_by: automatic
tags: [paw, projector-green, validation, exchange]
---

## Overview

A PAW projector producer must build an immutable `PawProjectorSnapshot` and validate it before constructing `ProjectorGreenData`. This separates source-specific collection from the exchange kernel and preserves the existing dual-projector PAW convention with `overlap_k=None`.

## Principles

- The physical site layout is authoritative: source-site identity, contiguous global projector slices, atomic species, PAW setup hashes, and ordered channels all travel together.
- Local PAW spin-difference components enter in Hartree and convert exactly once at the snapshot-to-Green boundary. Spectral ingredients are already in the eV convention accepted by `ProjectorGreenData`.
- Operator composition is inclusion-once. A producer either selects an authoritative `total` component or composes explicit non-total components; it cannot compose `total` with any part of that total.
- Snapshot arrays and provenance are owned read-only copies. A producer cannot mutate a validated object after construction.

## Details

`TB2J.paw_projector` validates finite spectral arrays, normalized k-point weights, site/projector layout coverage, local-block Hermiticity, unit and basis consistency, selection policy, and required provenance. It fails before Green construction so source errors cannot silently enter the LKAG trace.

For selected PAW components $a$, the builder publishes the complete local exchange splitting in eV:

$$
\Delta_i^{\mathrm{eV}} = 27.211386245988 \sum_{a \in \mathcal{S}} \Delta_{i,a}^{\mathrm{Ha}}.
$$

The resulting `ProjectorGreenData` preserves source-site numbering, padded site-local blocks, the dual-projector coefficient interpretation, and a provenance payload recording the selected components and policy.

## Variables

| Symbol | Description | Units |
|--------|-------------|-------|
| $\Delta_i$ | PAW local spin-difference operator at site $i$ | Hartree at input; eV in Green data |
| $\mathcal{S}$ | Inclusion-once selected operator-component set | dimensionless |
| $i$ | Source-site index; never renumbered by magnetic-site selection | dimensionless |

## Conventions

- `authoritative_total` selects only `total`; every other supplied component declares that it is included in that total.
- `compose` never selects `total` or a component already declared included in it.
- All supplied components share one native PAW projector Hamiltonian basis identifier.

## Linked Concepts

- [[abinit-paw-wfk-vxc-exchange]]: ABINIT PAW WFK and `pawprt` data source.
- [[gpaw-dftu-paw-operator]]: GPAW producer rule for a complete Hubbard-inclusive spin difference.
- [[notation]]: Standard exchange notation.
