---
type: Domain Topic
id: abinit/development/seeded-phonopy-force-oracle
domain: abinit
audience: development
artifact_role: guideline
status: draft
summary: Regenerate an ABINIT spinor Phonopy force oracle from matched central densities and audit force-energy and basin consistency.
triggers: [seeded force oracle, spinor phonopy oracle, force-energy inconsistency, matched central density]
aliases: [spinor force oracle]
outcome: 
requires_procedures: []
governed_by: []
uses_knowledge: []
supported_by: []
supersedes: []
evidence: []
source_project: abinit
source_sha256: 455ff5f3fdc1be8505353f320f7c68e8d96cf04268eaa53cc8568cf0546b2f05
---

# Seeded Phonopy Force Oracle

Use this procedure when a finite-displacement campaign shows force-energy inconsistency or independently initialized SCF legs.

1. Run one converged, undisplaced supercell SCF for each interaction state, for example U=0 and U-on.
2. Start every plus-delta and minus-delta leg from the central density of its state with `wfinit 1` and `getden 1`.
3. Set the generic-input root in the files file to the central output root; input and output roots must differ.
4. If one pair keeps a strict energy-symmetry failure, rerun that pair with `getwfk 1` from the central WFK; the matched central-density initialization stays intact.
5. Run at most three `mpirun -np 8` legs concurrently; set `OMP_NUM_THREADS=1` and `MKL_NUM_THREADS=1`.
6. Gate each pair: converged SCF, present final force block, plus/minus force antisymmetry, small pair mean, nonzero force signal, and pair-energy symmetry.
7. Check one saved pair against its central energy with `k_E = (E+ + E- - 2E0)/h^2` and `k_F = -u.(F+ - F-)/(2h)`.
8. Convert a displacement given in Angstrom with `1 eV/Angstrom^2 = 0.529177210903^2 / 27.211386245988 Ha/bohr^2`.
9. Rebuild Phonopy force constants only after recording every gate.
10. If Phonopy applied the eV/(Angstrom*bohr) frequency factor to eV/Angstrom^2 force constants, rescale the reported frequencies by `15.6333023 / 21.490680`.
11. Compare the regenerated spectra with the saved spectra before attributing a DFPT-FD discrepancy to basin selection.

Do not relax an energy-symmetry gate silently. If the spectrum is stable but one pair fails, report both facts and keep the qualification.
