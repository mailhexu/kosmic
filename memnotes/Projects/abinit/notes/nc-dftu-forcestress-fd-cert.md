---
type: Project Knowledge
title: NC DFT+U Spinor Forces/Stress FD Certification
description: Certify packed-spinor NC DFT+U forces/stress against serial FD on the develop tree; fixture validation, inversion-broken bases, v10 pin, MPI equality close.
created: '2026-09-25'
updated: '2026-09-25'
project: abinit
status: draft
audience: development
artifact_role: guideline
tags: [abinit, dftu, spinor, finite-differences, v10, mpi]
---

# NC DFT+U Spinor Forces/Stress FD Certification

Certify analytic packed-spinor NC DFT+U force and stress channels against serial central
finite differences (FD) on the develop tree; pin v10 coverage; close with an MPI equality
check.
## Protocol
1. **Fixture selection is the first experiment.** Demand a fixture that reaches tolvrs
   1e-8 in tens of SCF steps with no limit cycle (deltaE wiggle < 1e-8 Ha). A 4-atom PBE
   cell proved fixture-intrinsic unstable; a 2-atom t212-class cell converged at step
   14/80 and certified. Validate the fixture before the campaign: one SCF plus an h=0.001
   displaced pair; watch the vres2 trajectory.
2. **Deck conventions** (story-550b, `gen_decks2.py`): nsppol 1, nspinor 2, nspden 4;
   occopt 0 fixed occupations; ixc 1 + ixcrot 3; tolsym 1e-12; nsym 1 (kills
   symmetry-driven noise in FD pairs); kptopt 3; istwfk *1; ecut 8. Multi-k is mandatory
   (2x2x2 shifted): Gamma-only hides the variable-npw stride-bug class. U-delta isolation:
   U-on (dftu_u nonzero) vs U=0 with usedftu_nc=1; that zero control must be bitwise equal
   to usedftu_nc=0.
3. **Channels**: 6 displaced forces (a1x..a3z) and 6 strain stresses (e1..e6) as U-on/U=0
   central differences; h-convergence pairs (h=0.01, 0.005) with Richardson
   `(4*FD(0.005) - FD(0.01)) / 3`. An inversion-symmetric base makes U-delta forces vanish
   (vacuous channels). Add displaced-base decks (a1x +/- 0.01) to break inversion so force
   channels carry signal.
4. **Exit gates** (story-547 precedent): forces <= 0.5% of FD; stress <= 6e-7 Ha/bohr^3 on
   shears; volume trace <= 1%.
5. **Failure adjudication, fixture vs analytic**: all-channels-over plus (a) bitwise zero
   control, (b) probe matrix showing an SCF floor independent of mixer, occupancy, and
   DFT+U (vres2 floors even at usedftu_nc=0 means a limit cycle), (c) strained cells on
   bad branches ~3.6e-2 Ha high (raw-DFT stress FD off its own print by ~800% is a
   strain-branch signature), (d) U-delta forces still physics-consistent vs scalar
   precedent. Then the fixture is the cause. Retain the failed campaign tree as evidence;
   re-run on the convergent fixture. Story-550: campaign 1 all-over (residuals
   1.3e-5..4.5e-4); campaign 2 force <= 4.7e-7 (0.135%), stress <= 1.34e-8.
6. **Pin v10**: copy the certified base deck to tests/v10/Input (max_nprocs 1).
   Trial-run from a scratch directory; an absolute-path input writes outputs next to the
   input, never run from Input/ or the build root. Pin the .abo into Refs. Register in
   tests/v10/__init__.py. Run `python runtests.py "v10[N]" -b build-l0`. Re-read the
   CURRENT __init__.py tail first; the sibling lane actively claims numbers (t236
   collision 2026-09-18; recovery: `git checkout` the tracked deck, re-home to the next
   free number). t237 = spinor forces+stress.
7. **MPI close (C1d)**: same deck at `mpirun -np 2/4`. etotal and hartree stress must be
   bitwise; forces to ~4e-13 equal band-group reduction reassociation, a 1-ulp class: PASS.
   Parse note: the .abo hartree stress header is `Cartesian components of stress tensor
   (hartree/bohr^3)` (not "of the total"); the GPa block follows with a `-` comment prefix.
## Deployed state (2026-09-18)
develop bcecb8b = v10[237]. C1a oracle paper 13fbbfb. C1b pre-exists in m_nc_dftu_forces:
forstrnps_dftu per-spinor dphi harvest, conjugate arms (dPhi)L + Phi(dL) with no factor 2,
strain dS chain. Evidence: scratch/story550, story550b, t237pin.
