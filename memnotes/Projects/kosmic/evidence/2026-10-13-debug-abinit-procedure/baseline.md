---
type: Skill Topic
id: tb2j/development/debug-abinit-exchange
domain: tb2j
audience: development
status: stable
summary: Diagnose TB2J exchange parameters generated from an ABINIT spin-orbit calculation.
triggers: [debug tb2j exchange parameters from abinit, incorrect abinit tb2j exchange]
aliases: [tb2j abinit debug]
requires: [abinit/usage/export-wavefunctions, abinit/usage/spin-orbit-conventions]
evidence: []
source_project: native
source_sha256: empty
---

# Debug TB2J exchange from ABINIT

Reproduce the smallest failing TB2J calculation. Verify the ABINIT wavefunction export and spin-orbit conventions first, then compare adapter inputs, orbital/projector selection, and exchange output. Change TB2J only after the boundary data are demonstrated correct or the adapter mismatch is isolated.
