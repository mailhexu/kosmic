---
type: Project Knowledge
title: ABINIT Procedure-Skill Calibration
description: Evidence-based criteria for promoting ABINIT development guidance into bounded shared procedures and routing their recipe packets.
confidence: 0.9
created: '2026-09-08'
updated: '2026-10-18T17:20:40.811131Z'
skill_candidate: false
validation_procedure: "Re-read the named ABINIT source guidance and run representative resolve-library queries after an approved migration."
project: kosmic
status: draft
audience: development
artifact_role: knowledge
usage_stale: false
tags: [abinit, procedures, skill-proposals, routing]
evidence: []
---

# ABINIT Procedure-Skill Calibration

## Overview

The existing ABINIT development projection exposes more than sixty references in one flat list. The shared ABINIT Domain Skill currently has three topics and no development procedure. The gap is not a need for a native `SKILL.md` per recipe. It is a need to admit a small number of evidenced, bounded procedures as `abinit/development/*` Domain Topics, then load them through the existing single `memnotes-skills` router.

## Admission Rule

Promote material only when it has a repeatable trigger, one bounded outcome, ordered actions, meaningful branches, verification, failure handling, and evidence of at least one successful execution. The resulting topic must be smaller and more decisive than the source note; otherwise retain the material as knowledge, a guideline, or evidence.

A candidate needs an explicit target and trigger vocabulary. It is not sufficient that the title contains an imperative verb. Legacy notes without `artifact_role: procedure` and the behavioral section contract must first be brought to that shape at their source; they cannot directly seed a shared-procedure proposal.

## Extracted Rules

1. **A task record is not a procedure.** Keep guidance in a task specification or its evidence when its predicate, repository, reference era, or success criterion is unique to that investigation. A reusable procedure must survive replacement of those particulars by explicit inputs.
2. **Knowledge is not automatically executable guidance.** Preserve a derivation, oracle ladder, or diagnostic model as knowledge or dated evidence when its primary value is interpretation. Promote it only after repeated work reveals a bounded operational seam with a repeatable outcome.
3. **One procedural seam per outcome.** Do not create a generic “add a file” procedure. Scaffold a routine, register a source, change a libPAW file, wire an input variable, and add a regression test have different invariants and verification.
4. **Evidence must be current and two-sided.** Admission requires a successful current execution and one meaningful failure or recovery path. Historical incidents may motivate a candidate but cannot be copied as its supported workflow.
5. **Refresh before promotion.** When a candidate contains an obsolete incident or workaround, remove it, re-derive the supported path against the current source tree, and regenerate evidence before Task P.
6. **Route narrowly and fail closed.** A `do` request selects one procedure by explicit route or reviewed triggers. Specialist physics knowledge and optional setup do not enter a task packet unless the task explicitly requires them.
7. **Keep one authority.** Migrate an existing mature skill by behavioral comparison and clean cutover; never publish an overlapping second authority.
8. **A Domain must earn its root.** A separate domain needs more than one durable procedure or knowledge topic with shared ownership. A single private-documentation workflow remains a named skill or project material.
9. **Repeated failures are a proposal signal, not automatic promotion.** A recurring failure becomes a procedure candidate when the remedy generalizes across independent cases, its root cause can be stated as an invariant, and a reproducer plus verification matrix demonstrate the repair. Preserve a single unexplained incident as evidence until that threshold is met.

## Candidate Assessment

| Candidate | Evidence | Decision | Required repair before Task P |
| --- | --- | --- | --- |
| Build ABINIT from a git checkout with CMake | Existing `abinit-git-cmake-build` has prerequisites, two known failures and fixes, build/install steps, and a smoke-plus-regression verification. | First migration candidate. Do not duplicate the current named skill: move one reviewed authority to `abinit/development/build-from-git-cmake` after behavioral comparison. | Pin source ownership and the target-maintainer decision; compare the current named skill with the proposed recipe packet. |
| Register a new Fortran source in an existing ABINIT CMake directory | `adding-source-files-abinit.md` identifies the required `CMakeLists.txt` and `abinit.src` updates and their alphabetical-order invariant. | Incubate, not yet a procedure candidate. | The note records `successful_usage_count: 0`, lacks failure handling, and conflates CMake registration with legacy build-system behavior. Execute it successfully, narrow it to CMake directories, and document a failure/repair path. |
| Add a normal ABINIT regression test | `abinit-add-test-case.md` records one successful usage and a generic ten-step workflow with a single-test verification. | Candidate; needs atomic-note consolidation at its source first. | Split generic ABINIT regression-test creation from Multibinit model-specific fixture guidance, then add explicit failure handling for unstable references and test-registration errors. |
| Add a Multibinit input variable | `adding-input-variables-multibinit.md` records one successful use and the declaration/default/parser/output sequence. | Candidate after revalidation. | Revalidate against the current input-variable/documentation wiring and exercise a focused input test; retain it as a separate procedure from source registration. |
| Add a libPAW file | `libpaw-coding-rules.txt` is a libPAW-only coding rule, while developer scripts scaffold F90 routines/modules. | Guideline/reference, not a general “add an ABINIT file” procedure. | Gather an executed libPAW addition with registration, tests, and portability-check evidence before proposing a scoped procedure. |

## Routing Model

The ABINIT Domain Skill remains the ownership and vocabulary router. For `intent: do`, the resolver selects exactly one procedure by an explicit route or reviewed trigger/alias, then loads only its declared closure:

1. the `abinit` Domain Skill;
2. prerequisite procedures, only when they are genuinely required;
3. the selected procedure;
4. governing guidelines and essential knowledge.

Do not make build setup an unconditional dependency of source registration or test creation. A developer with an already configured tree needs only the changed-path procedure; a missing or broken git build is an explicit `build ABINIT from git` route. The resolver should return `NO_EXECUTABLE_MATCH` rather than use a wide explanatory note as task instructions.

Recommended initial triggers are:

| Topic ID | Triggers | Dependencies |
| --- | --- | --- |
| `abinit/development/build-from-git-cmake` | `build abinit from git`, `cmake build abinit`, `configure abinit git checkout` | none |
| `abinit/development/register-fortran-source` | `register ABINIT Fortran source`, `add source file to ABINIT CMake`, `update abinit.src` | none until its evidence exists |
| `abinit/development/add-regression-test` | `add ABINIT regression test`, `create ABINIT test case`, `add TEST_INFO` | none; build setup is a user-selected prerequisite |
| `abinit/development/add-multibinit-input-variable` | `add Multibinit input variable`, `wire multibinit parser variable` | none |

## MPI Procedure Packet Candidate

The MPI distribution material should not become one large “ABINIT MPI skill.” It already separates naturally into a procedure, a correctness guideline, and explanatory knowledge. That gives a contributor the smallest complete packet for the change being made.

| Role | Proposed topic | When it loads | Content boundary |
| --- | --- | --- | --- |
| Procedure | `abinit/development/implement-cg-mpi-reduction` | Add or change an ABINIT quantity accumulated from `cg` across k-point, band, FFT, or spinor parallelization. | Local G-vector accumulation, the required reduction order, owned-band filtering, final communicator reductions, and a topology matrix for verification. The existing `abinit_mpi_cg_loop_template.md` is strong source evidence because it documents the invariants, common failures, and agreement across `paral_kgb`, `npkpt`, `npband`, and `npfft` modes. |
| Guideline | `abinit/development/mpi-distribution-invariants` | The procedure above, or a future MPI-sensitive implementation procedure, needs correctness constraints. | Local versus global extents, ownership versus storage, communicator selection, reduction-before-filtering, and the prohibition on changing offsets with logical band ownership. It turns recurring mistakes into reviewable rules. |
| Knowledge | `abinit/development/mpi-topology-model` | A contributor asks to understand MPI distribution or must select a communicator. | The `MPI_type` communicator hierarchy, Cartesian dimensions, `proc_distrb`, and local-to-global mappings. It informs; it is not task instruction by itself. |
| Knowledge | `abinit/development/fft-distribution-model` | An MPI change touches `fourwf`, `fourdp`, local FFT planes, or transpose behavior. | Cyclic wavefunction and block density/potential distributions, ownership maps, and FFT communication costs. |
| Future procedure | `abinit/development/diagnose-mpi-topology-dependent-result` | A result differs between serial and a specific MPI topology, or only fails for `paral_kgb=1`, `npband>1`, or `npfft>1`. | Create only after repeated failures establish a stable diagnosis sequence. It must start from a minimized topology matrix, identify the first violated ownership/reduction invariant, and prove the repair over the affected topologies. |

The proposed `implement-cg-mpi-reduction` packet should load the ABINIT Domain Skill, the primary procedure, its MPI correctness guideline, and only the two knowledge topics required by the code path. It must not load generic build, test, or unrelated physics guidance.

## Failure-Derived Proposal Rule

Repeated failure is high-value discovery evidence because it identifies the missing invariant that a future contributor needs before writing code. Record the initial symptom, incorrect plausible approaches, the root cause, the repaired rule, and a verification matrix. Promote the result when the same rule prevents or repairs independent failures; otherwise retain the incident as evidence.

## MPI Proposal Intake Prerequisite

The current Kosmic vault contains the `abinit` Domain Skill but no `Projects/abinit/` source Project. The candidate evidence is in a separate vault and its legacy note has neither `artifact_role: procedure` nor verified procedure evidence at its source. Task P therefore cannot lawfully create a shared-procedure proposal from that material yet.

The user selected a **scoped MPI source Project** rather than full external-Project adoption. `Projects/abinit/` will own only the historical provenance and future fresh evidence for the MPI CG-reduction packet. It must declare that boundary, retain historical validation as evidence rather than current execution proof, and not compete with the external full ABINIT Project for unrelated knowledge. Typed draft notes may then be captured at their source, followed by a fresh-context Task P proposal. Do not copy the external note directly into the shared library.

## Additional Potential Topics

These are prospective topics, not Task P artifacts. Each would require its own verified procedure evidence, fresh-context proposal, approval, behavioral comparison, and review.

| Priority | Potential topic | Trigger | Admission status | Scope decision |
| --- | --- | --- | --- | --- |
| — | `abinit/development/bisect-v10-regression` | `bisect ABINIT v10 regression`, `find ABINIT regression commit` | Rejected as a library candidate. This is a task-specific investigation whose predicate, repository, and reference era are part of its task record. | Preserve it in the relevant task specification and evidence rather than promote it into reusable ABINIT routing. |
| — | `abinit/development/adjudicate-finite-u-dfpt` | `validate finite-U ABINIT DFPT`, `compare NC DFT+U phonons to finite difference` | Reclassify as physics knowledge plus dated validation evidence, not a general procedure. | Retain its oracle details as inspectable domain knowledge; create an executable procedure only if a future repeated task proves a stable operational seam. |
| 1 | `abinit/development/scaffold-fortran-routine` | `create ABINIT Fortran routine`, `create ABINIT Fortran module` | Selected for evidence gathering. Developer scripts identify `mkroutine.sh`, `mkmodule.sh`, and `abirules.pl`. | Keep scaffolding separate from build registration. Capture one successful invocation, resulting source shape, checker result, and recovery for an invalid invocation. |
| 2 | `abinit/development/check-libpaw-change` | `check libPAW change`, `validate libPAW portability` | Selected for evidence gathering. The libPAW rules define a checker command and portability constraints. | Scope it to `src/??_libpaw`; record a build plus `check-libpaw.py` result and one meaningful failure diagnostic. |
| 3 | `abinit/development/rebuild-after-fortran-interface-change` | `ABINIT stale module files`, `rebuild after Fortran type change` | Selected only after content refresh. The user reports that the `66_ncpao` incident is obsolete. | Delete the historical directory-order workaround from the candidate. Re-derive and exercise the current supported cleanup/reconfigure/rebuild path after an interface change, with its actual failure signatures. |
| 6 | `abinit-docs/development/build-gitlab-migration-pdf` | `build ABINIT GitLab migration PDF`, `validate migration guide screenshots` | Defer. The existing `abinit-gitlab-migration-docs` procedure is mature, but it operates in a private documentation repository rather than the ABINIT engine. | Create a distinct `abinit-docs` Domain only if a second durable documentation procedure appears. Until then, retain the existing named skill to avoid a shallow one-topic domain. |

## Explicit Non-Candidates

- Output-file variable mapping is an important local source invariant, but one in-source reminder does not constitute a standalone workflow.
- The historical same-level directory-order workaround is not a skill: it is version-sensitive evidence of a design defect, not a stable supported procedure.
- A generic “add an ABINIT file” skill would hide materially different contracts for ordinary source registration, routine scaffolding, libPAW, input variables, tests, and output files. It must remain split.

## Proposal Sequence

1. Use the already mature CMake build procedure as the first shared-procedure migration and compare old named-skill behavior with the recipe packet.
2. Capture and execute the three development candidates independently. Each produces its own verified procedure evidence and Task P artifact; do not batch unrelated procedures.
3. Promote only candidates that pass Task P’s fresh-context proposal, target-Maintainer approval, behavioral comparison, and Task 7 review.
4. Use resolver traces from representative ABINIT requests to refine triggers and aliases. Change routing metadata only when a trace demonstrates a false match, ambiguity, or unnecessary dependency.

## Implication for Kosmic

Kosmic already contains the required structural mechanisms: artifact roles, Task P, fresh-context review, typed recipe-packet closure, intent routing, byte budgets, and single-router installation. The missing operational discipline is an explicit admission pass before authors assume that a how-to belongs in a skill. This ABINIT calibration supplies that pass: evidence first, one procedural seam, one target, one behavioral comparison, and trace-driven routing maintenance.

## References

- [Shared Domain Skill Library](./shared-domain-skill-library.md)
- [Procedure Compilation and Routine Reuse](./procedure-compilation-and-routine-reuse.md)
