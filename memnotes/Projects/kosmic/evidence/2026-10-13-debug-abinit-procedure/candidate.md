---
type: Domain Topic
id: tb2j/development/debug-abinit-exchange
domain: tb2j
audience: development
status: stable
artifact_role: procedure
summary: Diagnose TB2J exchange parameters generated from an ABINIT spin-orbit calculation.
outcome: A localized cause for wrong TB2J exchange parameters from an ABINIT spin-orbit calculation, attributed to wavefunction export, spin-orbit conventions, adapter boundary handling, or TB2J itself.
triggers: [debug tb2j exchange parameters from abinit, incorrect abinit tb2j exchange]
aliases: [tb2j abinit debug]
governed_by: [abinit/usage/export-wavefunctions, abinit/usage/spin-orbit-conventions]
requires_procedures: []
uses_knowledge: []
supported_by: []
supersedes: []
evidence: []
source_project: native
source_sha256: empty
---

# Debug TB2J exchange from ABINIT

## When to use

Use when TB2J exchange parameters computed from an ABINIT spin-orbit calculation are reported as wrong (magnitudes, signs, missing neighbors, or other discrepancies) and the cause is not yet localized.

## Preconditions

- A reproducible ABINIT spin-orbit run and the TB2J adapter invocation that consumes its output.
- Awareness of the ABINIT wavefunction export guidance (`abinit/usage/export-wavefunctions`) and the ABINIT spin-orbit convention guidance (`abinit/usage/spin-orbit-conventions`); both are typed as guidelines governing this procedure.

## Procedure

Reproduce the smallest failing TB2J calculation. Verify the ABINIT wavefunction export and spin-orbit conventions first, then compare adapter inputs, orbital/projector selection, and exchange output. Change TB2J only after the boundary data are demonstrated correct or the adapter mismatch is isolated.

If no reduced case is found, work with the original failing calculation and record that no smaller reproducer was identified.

## Decisions and branches

- Boundary data incorrect or unverifiable → stop; repair the ABINIT export or convention handling first (follow the two governing guidelines); do not modify TB2J.
- Boundary data correct, adapter mismatch isolated → fix or report the adapter boundary handling; re-run the smallest failing case to confirm.
- Boundary data and adapter boundary consistent but exchange still wrong → only then investigate or change TB2J itself.

## Verification

After a fix, exercise the same original or reduced failing case and inspect the corrected exchange output. Record which boundary input, export setting, or adapter handling changed and how the observed exchange output differs.

## Failure handling

- If ABINIT output identity (inputs, version, file type) cannot be established, stop and record the gap instead of guessing adapter conventions.
- If the defect cannot be reproduced in a smaller case, work with the original failing calculation and record that no reduced reproducer was found.

## References

- `abinit/usage/export-wavefunctions` (guideline)
- `abinit/usage/spin-orbit-conventions` (guideline)
