---
type: Project Knowledge
title: Finite-U NC DFT+U Oracle Adjudication
description: Validate finite-U NC DFT+U DFPT observables against independent finite-field, finite-displacement, and energy oracles.
created: '2026-09-25'
updated: '2026-09-25'
project: abinit
status: draft
audience: development
artifact_role: guideline
tags: [abinit, dftu, dfpt, phonons, oracle, phonopy]
---

# Finite-U NC DFT+U Oracle Adjudication

Use this note when a DDB (derivative database) or response result needs an oracle
independent of the port and reference implementations.
## Phonon oracle procedure
1. Match the electronic sampling of the DDB fixture before selecting a supercell. A
   Gamma-only 2x2x2 supercell samples an eight-point primitive mesh; it is not equivalent
   to a primitive calculation at one shifted k-point.
2. Use symmetric energy displacements, normally +/-0.01 bohr, and strict SCF
   (tolvrs=1e-12). Every U-on set needs a same-mesh U=0 twin.
3. Parse the final ABINIT Cartesian forces. Require equilibrium residual force below
   7e-8 eV/A before trusting a force FD dataset.
4. Check force conservativity before using force constants. The Hessian transpose
   asymmetry must be small. Central force curvature must agree with energy curvature for
   every displaced column. If either check fails, force-based FC is not a physical oracle.
5. When force FD is nonconservative, build the exact symmetric energy Hessian from central
   energy curvatures and validated cross columns. Enforce the acoustic sum rule only on
   that symmetric energy Hessian. Pass this FC to Phonopy and diagonalize it
   independently. Assert the spectra agree.
6. Compare invariant Gamma frequencies or q-resolved dynamical spectra, not raw DDB
   blocks. DDB entries may represent supercell-folded image sums.
## NiO Wave-6 fixture lesson
The two-atom FM-seed NiO Gamma fixture uses one primitive k-point
`kpt=(1/2,1/2,1/2)`, nsym=1. Its matched FD oracle is a primitive 1x1x1 Phonopy object,
not a Gamma-only 2x2x2 supercell. Both the current and archived U-on DDBs for this
fixture carried a sign-flipped Ni self force-constant block, about -2.8 Ha/bohr^2 against
the energy oracle +0.0614 Ha/bohr^2. Archive agreement is a port-regression check, not a
physical certification. Direct spinor-force FD was nonconservative even at U=0; the
energy-Hessian Phonopy result is therefore the certified oracle.
## Units and settings
- 0.01 bohr = 0.00529177 A. Use Phonopy 3.0.0 in the project-approved Python environment.
- For anaddb DDB spectra, use identical `asr=0`, `chneut=0`, `dipdip=0` before comparison.
- Treat negative modes in a constrained or under-sampled fixture as fixture physics,
  unless the energy-Hessian oracle and the DDB disagree. Do not infer stability from the
  DDB alone.
