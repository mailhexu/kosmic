---
type: Domain Topic
id: siesta/development/axis-constrained-scf-ladder
domain: siesta
audience: development
artifact_role: guideline
status: draft
summary: Run the theta-ladder constrained-SCF axis scan and the x/z axis-equivalence ladder for Spin.FixDirection runs on the perspin_DFTB fork.
triggers: [theta ladder, axis constrained SCF, FixDirection scan, MAE workflow]
source_project: native
source_sha256: empty
aliases: [axis ladder, spin-axis continuation]
---

# Axis-Constrained SCF Ladder

Run axis-continuation (theta-ladder) constrained SCF and x/z
axis-equivalence validation for perspin_DFTB `Spin.FixDirection` runs
on TmFeO3-class systems.
## Seed correctness (validated 2026-09-18)
- Use spin-only DM rotations as seeds only: D' = (I x W) D (I x W+).
  The rotation is S-unitary (S = S_orb x I2), charge-exact, in-pattern.
- Verify gates first: Tr[D.S] unchanged, write/read roundtrip exact,
  Mulliken moment = R(dTheta) m to 1e-5 deg, plus a dTheta = 0 self-test.
- Never use orbital co-rotation (R_l x W) of a solid DM: the Loewdin
  sandwich is dense, pattern truncation is non-PSD (cdiag crash), and the
  f-shell m-frame is lattice-pinned, so the seed is an excited state.
- Re-verify the TB2J rotate_siestaDM pipeline after updates (past W+
  double-conjugation bug); a y-rotation must preserve Tr[D.S].
  real_sh_rotation_90 tables rotate orbital multipoles with opposite
  chirality to the spin W; use R_l^T to restore rigidity.
## Validation ladder (order matters)
1. Isolated atom: all directions are exact symmetries; per-iteration
   Eharris/E_KS and Mulliken must match to micro-eV for file-fed chains.
   Fresh-init gaps of about 6 meV are eigensolver branch selection in
   SOC-split quasi-degenerate manifolds, not potential defects.
2. Cubic solid (SmN/CeN): enumerate the 48 cubic operations BEFORE
   assigning per-axis InitSpin pairings; naive pairings compare basins
   about 350 meV apart.
3. Target crystal: run the theta-ladder. Never compare one-shot energies
   across binaries; slot bookkeeping drifts and OP/LCap transients reach
   100-1000 eV.
## Theta-ladder protocol (validated on TmFeO3 B=0.35)
- Anchor on a converged z run. Each rung seeds from the previous rung's
  converged DM by the incremental angle about +y; update DM.InitSpin
  thetas (+ atoms theta, - atoms 180 - theta); MaxSCF 150-500,
  MustConverge, SCF.Mix.Spin all.
- Retry: Mixer.Weight 0.05, halve the increment (floor about 1 degree),
  record the best energy, probe past the break with jump-probes.
- Adjudicate per rung: convergence, E_KS, transverse fraction (holds
  to 3e-7 when healthy), net moment components.
- The constraint does not fail in practice; breaks are electronic
  sublattice reorganization. Levers: reorganize the sublattice pattern
  in the seed, 500+ iterations, DM-mixing regularization, force-theorem.
## Audit gates and ops
- Covariance audits are valid only on the SO(3) subgroup; use
  wigner_D_real rotations. Random unitaries give false defects for l >= 2.
- nic6: rtk proxy ssh/scp only; ship fdf as base64; atom fixtures serial
  only (MPI SOC segfault at np >= 2), 32 ranks for solids; modules
  dev@153d5ba01-gcc and dev@ccbb20e66-gcc (OP.DoubleCountingMean OFF);
  ladder workdirs are resumable (queue.txt + rung.json).
