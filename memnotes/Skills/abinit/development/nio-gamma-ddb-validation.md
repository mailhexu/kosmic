---
type: Domain Topic
id: abinit/development/nio-gamma-ddb-validation
domain: abinit
audience: development
artifact_role: evidence
status: stable
summary: Runtime and source-review evidence that the packed-spinor NiO Gamma phonon path writes the ordinary ABINIT DDB layout.
triggers: [investigate NiO gamma DDB, NiO spinor validation, gamma phonon failure]
aliases: [NiO gamma validation]
outcome: 
requires_procedures: []
governed_by: []
uses_knowledge: []
supported_by: []
supersedes: []
observed_on: 2026-08-12
evidence: []
source_project: abinit
source_sha256: 7be78a2f6aa3fb3b13912e8d9487f0bf6d3a3aec1556f2df8b5107a97a683a14
---

# Packed-Spinor Gamma Phonon DDB Validation

On 2026-08-12, runtime fixtures and source review confirmed that the enabled static NC PAO DFT+U spinor phonon route uses ABINIT's ordinary Gamma DDB array and scheduler. The spinor-specific work remained in packed occupation, potential, source, response-pair, and frozen-projector contractions; native DDB indexing received the contracted scalar result.

The validation ran temporary U-on and U=0 two-atom NiO Gamma fixtures with eight MPI ranks and checked the resulting spinor DDB. This is dated evidence, not current implementation guidance; use it to investigate a matching regression and revalidate against the current source before drawing a present-tense conclusion.
