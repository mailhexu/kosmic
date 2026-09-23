---
type: Domain Topic
id: abinit/usage/export-wavefunctions
domain: abinit
audience: usage
artifact_role: guideline
status: stable
summary: Export ABINIT wavefunction data for downstream projector and exchange workflows.
triggers: [export abinit wavefunctions, use abinit output with tb2j]
outcome: 
aliases: [wfk export]
requires_procedures: []
governed_by: []
uses_knowledge: []
supported_by: []
supersedes: []
observed_on: 
evidence: []
source_project: native
source_sha256: empty
---

# Export ABINIT wavefunctions

Confirm the downstream tool's supported ABINIT file type and version. Preserve the calculation's structure, spin, k-point, and band conventions with the exported wavefunction data. Record the exact ABINIT inputs and output identity in the consuming Project evidence rather than copying adapter-specific guesses into another domain.
