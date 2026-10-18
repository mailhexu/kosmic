---
type: Skill Topic
id: abinit/usage/spin-orbit-conventions
domain: abinit
audience: usage
status: stable
summary: Preserve ABINIT spinor and spin-orbit conventions across downstream interfaces.
triggers: [abinit spin orbit conventions, abinit soc spinor]
aliases: [abinit soc]
requires: []
evidence: []
source_project: native
source_sha256: empty
---

# ABINIT spin-orbit conventions

Treat spinor ordering, noncollinear magnetization, symmetry reduction, and wavefunction normalization as interface data. Verify them against the ABINIT run and the consuming adapter before interpreting magnetic exchange results. Do not infer conventions from a filename alone.
