---
status: approved
created: 2026-09-07
updated: 2026-09-07
linked_research: []
linked_epics: [epics/epic-17-semantic-role-schema.md, epics/epic-18-role-aware-resolution.md, epics/epic-19-classification-migration-release.md]
---

# Semantic Artifact Roles

## Problem Statement

Kosmic currently classifies maintained material primarily by audience (`usage`, `development`, or `both`) and represents every shared-library descendant as a `Skill Topic`. This conflates four different uses of durable material: a repeatable procedure that directs action, a guideline that constrains judgment, knowledge that explains the system, and evidence that records an observation or prior result.

The defect is visible in the ABINIT projection. Its Development Skill exposes 63 references uniformly as topics even though only a small subset are repeatable procedures. Data-structure descriptions, equations, implementation reports, debugging status, validation snapshots, and task instructions consequently appear to have equivalent operational authority. An agent can mistake historical evidence for current guidance or descriptive knowledge for an approved procedure.

Kosmic needs a semantic classification independent of audience, deterministic routing that respects each role's authority, and a migration path that preserves useful material without promoting every stable note into executable skill guidance.

## Goals

- Distinguish procedures, guidelines, knowledge, and evidence as explicit semantic roles independent of audience.
- Ensure only procedures directly instruct an agent to perform a task.
- Preserve guidelines as normative constraints, knowledge as reference, and evidence as dated support rather than default operational guidance.
- Select a procedure first for actionable requests, then load only its typed prerequisite procedures, governing guidelines, required knowledge, and requested evidence.
- Support reference-only resolution for understanding questions without falsely claiming an executable skill match.
- Replace misleading `Skill Topic` terminology with role-neutral `Domain Topic` terminology.
- Make Task 9 Distill and Task P classify durable outputs before proposing procedural skill changes.
- Migrate ABINIT first as the representative fixture, without losing source hashes, audience, evidence links, or Maintainer ownership.
- Preserve the one-installed-router architecture, deterministic offline operation, byte budgets, hash-pinned plans, atomic publication, and target-domain governance.

## Non-Goals

- Install one native Agent Skill per procedure or Domain Topic.
- Delete knowledge, guidelines, or historical evidence merely because they are not procedures.
- Infer semantic roles or typed dependencies from prose during canonical generation.
- Use an LLM, embeddings, or network service for required classification or routing.
- Treat every numbered list, workflow diagram, implementation report, or validation record as a procedure.
- Rewrite all mixed ABINIT notes into procedures during schema migration.
- Authenticate Maintainer identity beyond the existing recorded-approval contract.
- Change adapter installation paths or replace the existing Shared Skill Router seam.

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-SR01 | Every active shared-library descendant must declare exactly one `artifact_role`: `procedure`, `guideline`, `knowledge`, or `evidence`; audience remains a separate field. | must |
| FR-SR02 | Generated catalogs, manifests, domain indexes, resolution plans, and Recipe Packets must use the role-neutral term `Domain Topic`; `Skill Topic` must not remain as a canonical schema type or generated label after migration. | must |
| FR-SR03 | A `procedure` must declare a recognizable trigger and bounded outcome and contain required behavioral sections for preconditions, ordered procedure, decisions or branches, verification, and failure handling. | must |
| FR-SR04 | A `guideline` may constrain a procedure or review but must not be selected as the executable task body. | must |
| FR-SR05 | `knowledge` must be loadable as informational reference and must not directly authorize or require actions. | must |
| FR-SR06 | `evidence` must record observation or provenance metadata, must be excluded from ordinary actionable packets by default, and must not be presented as current procedure. | must |
| FR-SR07 | Domain Topics must use typed relationships: `requires_procedures`, `governed_by`, `uses_knowledge`, and `supported_by`; validation must enforce compatible target roles for every relationship. | must |
| FR-SR08 | Resolver requests must distinguish `do`, `check`, `understand`, and `investigate` intent, whether explicitly supplied or deterministically inferred. | must |
| FR-SR09 | A `do` result must select one eligible procedure before dependency closure; if no procedure matches, the resolver must fail or return an explicitly reference-only result without claiming executable guidance. | must |
| FR-SR10 | A `check` result must prioritize applicable guidelines and may include a governing procedure; an `understand` result must prioritize knowledge; an `investigate` result may include knowledge and evidence with freshness information. | must |
| FR-SR11 | Actionable Recipe Packets must order content as selected procedure, prerequisite procedures, governing guidelines, required knowledge, then explicitly requested evidence, while preserving dependency-first requirements where necessary. | must |
| FR-SR12 | Resolution plans and traces must expose each loaded topic's artifact role, relationship to the selected procedure, and reason for inclusion. | must |
| FR-SR13 | Evidence topics must declare an observation date; optional supersession links must be validated, cycle-free, and used to exclude superseded evidence from default investigation results. | should |
| FR-SR14 | Task 9 Distill must explicitly classify each durable result before projection and must require Task P consideration only when the result is or materially changes a reusable procedure. | must |
| FR-SR15 | Task P must reject procedural proposals that lack a repeatable trigger, bounded outcome, meaningful action sequence, verification contract, or evidence of at least one successful execution. | must |
| FR-SR16 | Migration must inventory every existing shared Domain Topic, require an explicit role assignment, preserve provenance and audience, and abort atomically on unassigned, incompatible, stale, or colliding records. | must |
| FR-SR17 | ABINIT must be the first complete migration fixture: clear task procedures must be distinguished from guidelines, durable knowledge, evidence/history, and mixed documents retained conservatively as knowledge until separately distilled. | must |
| FR-SR18 | Existing cross-domain procedure composition, Maintainer approval, byte budgets, source-hash verification, catalog determinism, and single-router installation must continue to work. | must |
| FR-SR19 | Project Knowledge notes created or materially updated through Kosmic must declare the same artifact role vocabulary so that later shared-library proposals preserve semantics rather than reclassifying blindly. | must |
| FR-SR20 | Validation errors must name the topic, invalid role or relationship, expected role, and remediation; no invalid packet body may be emitted. | must |

## Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-SR01 | Classification, validation, catalog generation, routing, plan loading, and migration must remain deterministic, offline, and Python 3.11+ standard-library-only. | must |
| NFR-SR02 | The same library snapshot, normalized request, intent, and budget must produce byte-identical plans and Recipe Packets. | must |
| NFR-SR03 | Role classification and typed relationships must be authoritative Markdown metadata; generated JSON remains disposable index state. | must |
| NFR-SR04 | Migration and generation must stage and validate the complete result before one atomic publication; failure must preserve the prior valid library. | must |
| NFR-SR05 | Role-aware routing must not increase native-discovery inventory beyond the one installed Shared Skill Router. | must |
| NFR-SR06 | Ordinary `do` packets should become smaller or equal in size for representative ABINIT tasks because unrelated knowledge and evidence are excluded. | should |
| NFR-SR07 | Existing evidence paths, source hashes, source Project identity, audience, Maintainers, and proposal history must remain traceable after migration. | must |
| NFR-SR08 | Errors must remain typed and fail closed for missing role, incompatible relationship, no executable match, ambiguity, stale content, supersession cycle, and budget overflow. | must |

## Success Criteria

- [ ] Catalog validation rejects a Domain Topic with a missing/unknown role or a typed relationship pointing to an incompatible role.
- [ ] A `do` query for adding an ABINIT regression test selects the test procedure and only its declared procedural, guideline, and knowledge closure; unrelated validation reports are absent.
- [ ] An `understand` query for ABINIT wavefunction storage returns a reference-only knowledge result and does not claim an executable procedure.
- [ ] An `investigate` query for a NiO electric-response discrepancy can load dated, non-superseded validation evidence and labels it as evidence.
- [ ] A guideline such as ABINIT lattice/matrix convention checks can govern multiple procedures without becoming the selected task body.
- [ ] Procedure validation rejects a report that has numbered historical steps but lacks trigger, outcome, decisions, current verification, or failure handling.
- [ ] An explicit ABINIT migration assignment classifies every existing topic and preserves its source SHA-256, evidence references, audience, and ownership.
- [ ] Migration leaves mixed documents as knowledge unless a separately reviewed procedure is distilled from them.
- [ ] Equivalent runs produce byte-identical role-aware plans and packets; invalid or over-budget runs emit no packet body.
- [ ] Task 9 and Task P documentation and templates enforce classification before procedural proposal.
- [ ] The root router remains the only installed shared-library skill and all supported adapter byte checks still pass.
- [ ] Existing project validation, Evidence Pack, MathDoc, proposal, governance, and completion tests remain green.

## Open Questions

- [x] Is audience sufficient to distinguish operational authority? No; audience and artifact role are independent.
- [x] Which roles exist? Procedure, guideline, knowledge, and evidence.
- [x] What is executable? Only a procedure; guidelines constrain and knowledge/evidence inform.
- [x] Should every procedure become a native skill? No; the single router dynamically loads ordinary Domain Topics.
- [x] How are dependencies represented? Typed relationships with target-role validation.
- [x] How should mixed legacy documents migrate? Conservatively as knowledge until separately distilled.
- [x] Which domain proves the migration? ABINIT, because its current projection contains representative procedures, guidelines, knowledge, and historical evidence.
- [x] Must role-aware intent always be explicit on the CLI? No. Deterministically infer it by default and permit an explicit `--intent` override.
- [x] Is evidence supersession mandatory? No. It is optional, but every declared supersession edge must be validated for role, containment, and cycles.
