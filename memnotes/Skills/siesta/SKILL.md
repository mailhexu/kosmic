---
type: Domain Skill
id: siesta
status: draft
description: Run, patch, validate, and install the SIESTA perspin_DFTB spinor fork on this workstation and nic6.
maintainers: [hexu]
triggers: [siesta, perspin_DFTB, spin-orbit DFTB, density matrix]
aliases: []
---

# SIESTA

Use `development/` for source fixes, rotational-covariance validation, density-matrix seeding, fixture regeneration, and nic6 install cycles. Calculations run on the perspin_DFTB fork (`siesta_DFTB_dev/siesta_DFTB`). The fork stores spinor density matrices in an 8-real-column layout; check the column fold before interpreting any DM or Hamiltonian file. Ship fdf files to remote hosts as base64; plain transport mangles `%block` lines.
