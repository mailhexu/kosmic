---
type: Domain Topic
id: siesta/development/covariance-debugging
domain: siesta
audience: development
artifact_role: guideline
status: draft
summary: Debug and validate spin-axis rotational covariance of constrained SCF in the perspin_DFTB fork: defect genealogy, SmN oracle, validation ladder, and method laws.
triggers: [x vs z asymmetry, soc mirror defect, FixDirection covariance, covariance audit]
source_project: native
source_sha256: empty
aliases: [axis covariance, fixdirection xz covariance]
---

# Constrained-Axis (Spin.FixDirection) Covariance Debugging

Use when a transverse-axis (x or y) SCF run behaves differently from a
z-axis run in the perspin_DFTB fork, or when validating MAE energies.
## Defect genealogy (found 2026-09; check status before re-hunting)
1. SEED: naive R x W is not S-unitary (TmFeO3 loses 9.7 e); orbital-sector
   rotation is unrepresentable; spin-only rotation is exact. The
   rotate_siestaDM W-dagger bug is FIXED.
2. SOLVER: stage-1 y-moment sign + anti-parallel skip — FIXED at
   acd0e50f3 (m_spin_conventions:spin_moment_vec8).
3. ROOT: off-site SOC mirror (nlefsm.f u rows + setup_hamiltonian
   fold) — proven; needs a conjugation-preserving rewrite.
## Oracle test system

2-atom primitive rocksalt SmN (one Sm site, cubic): C4 maps z to x with
identical ions, so E_x = E_y = E_z exactly; any failure is algorithmic.
Reproducer: converge z, spin-rotate the DM (Tr[D.S] invariant, Mulliken
rigid), 1-shot (MaxSCF 1, Mixer.Weight 1e-8), check stationarity; about
2 minutes on 8 ranks. Batteries: nic6 spinphon_native/smn2_*.
## Validation ladder
1. Isolated atom: all directions are symmetries; energies must match.
   Fresh-init meV gaps are branch selection.
2. Cubic solid: enumerate the 48 cubic operations before assigning
   per-axis InitSpin pairings.
3. Target crystal: x/z are physically distinct (MAE); test conditioning
   equivalence only. Delegate rungs to task subagents, not scouts.
## Method laws (do not re-violate)
- Covariance audits are valid only on the SO(3) subgroup (wigner-D);
  random unitaries give false defects for l >= 2.
- `spin spin-orbit` selects the off-site SOC path (calc_Vj_offsiteSO,
  nlefsm.f); spinorbit.f is dead code.
- Ship fdf to nic6 as base64 via rtk proxy scp; the DM col4 sign
  differs per module era.
## Certified conventions and decisive controls
- Fold (8-col): M11 = c1+ic5, M22 = c2+ic6, M_ud = c3-ic4, M_du = c7+ic8.
- Pure-SOC frozen-DM C4 image test is the smoking-gun control: strip U/B,
  FixDirection off, MaxSCF 1; compare E_z with the exact torus C4 image
  (gates: hermiticity 2e-15, Tr[D.S] exact, S-closure 3e-9). Generator:
  studies/soffsite_mirror/full_torus_seed/.
- The off-site SOC convention is a PAIR (u table + fold); never change
  one half alone. The C4-closing form is commit 439d83166 content.
  After a convention change, seeded gates are invalid; gate on
  cold-start z (Hund basin).
- Exonerated: on-site SOC, +U occupation channel, cdiag/diag3k, DM I/O,
  off-site kernel values, TB2J rotator (after fix), stage-1/2
  FixDirection; vec8 storage covariant; V_B spectra frame-invariant;
  init_user/SOC/+U/+B exonerated at <= 6 micro-eV.
