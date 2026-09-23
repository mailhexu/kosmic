---
type: Domain Topic
id: tb2j/development/debug-abinit-exchange
domain: tb2j
audience: development
artifact_role: procedure
status: stable
summary: Diagnose TB2J exchange parameters generated from an ABINIT spin-orbit calculation.
triggers: [debug tb2j exchange parameters from abinit, incorrect abinit tb2j exchange]
outcome: Diagnose the ABINIT-to-TB2J exchange boundary.
aliases: [tb2j abinit debug]
requires_procedures: []
governed_by: [abinit/usage/export-wavefunctions, abinit/usage/spin-orbit-conventions]
uses_knowledge: []
supported_by: []
supersedes: []
observed_on: 
evidence: []
source_project: native
source_sha256: empty
---
# Debug TB2J exchange from ABINIT

## When to use

Use when TB2J exchange parameters from an ABINIT spin-orbit calculation are incorrect.

## Preconditions

Retain the ABINIT inputs, wavefunction export, adapter inputs, and TB2J output.

## Procedure

1. Reproduce the smallest failing TB2J calculation.
2. Verify the ABINIT wavefunction export and spin-orbit conventions.
3. Compare adapter inputs and orbital/projector selection.
4. Change TB2J only after boundary data demonstrate an adapter or exchange defect.

## Decisions and branches

If ABINIT interface data are inconsistent, fix or regenerate them before changing TB2J. Otherwise isolate the smallest TB2J-side mismatch.

## Verification

Repeat the minimized calculation and confirm the exchange output changes for the demonstrated cause.

## Failure handling

Stop and record the first boundary whose identity or convention cannot be verified.

## References

Use the declared ABINIT export and spin-orbit guidelines.
