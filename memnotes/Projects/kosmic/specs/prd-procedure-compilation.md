---
status: approved
created: 2026-09-07
updated: 2026-09-07
linked_research: []
linked_epics: [epics/epic-20-routine-registry-discovery.md, epics/epic-21-routine-governance.md, epics/epic-22-routine-publication-dogfood.md]
---

# Feature PRD: Procedure Compilation and Routine Reuse

## Problem Statement

Kosmic distinguishes executable procedures from guidelines, knowledge, and evidence, but a procedure is still represented primarily as prose. Repeated deterministic mechanics—parsing, validation, normalization, migration, hashing, publication, and reporting—can consequently be rewritten in multiple Domain Topics, task references, ad hoc scripts, or implementation stories. That duplication creates drift, makes behavior harder to test, and asks agents to reconstruct algorithms that Kosmic could execute reliably.

Kosmic needs a governed path by which repeated deterministic parts of procedures graduate into reusable Python routines. The path must preserve the authority of human-reviewed procedures: Python performs stable mechanics; Domain Topics retain intent, judgment, decisions, approval gates, and failure policy. Agents must discover and reuse an existing routine before writing equivalent code.

## Goals

- Turn commonly repeated, deterministic procedural mechanics into tested Python 3.11+ routines.
- Make existing reusable routines discoverable before an agent writes implementation from scratch.
- Keep one authoritative implementation for each compiled capability and remove superseded handwritten mechanics after cutover.
- Preserve human judgment, Maintainer approval, and Task 7 review outside automatic execution.
- Extend Task 9 and Task P with an auditable candidate-to-routine lifecycle.
- Validate the connection among procedure, routine contract, implementation, tests, and consumers.
- Preserve Kosmic's deterministic, offline, stdlib-only core and existing one-router architecture.

## Non-Goals

- Generate Python source from prose or LLM output automatically.
- Execute arbitrary Project scripts while generating or validating the Shared Skill Library.
- Replace Domain Topic procedures with undocumented commands.
- Compile judgment, scientific interpretation, architecture decisions, approval decisions, or context-dependent recovery policy.
- Add a dynamic plugin system, dependency injection framework, package manager, network registry, or second router.
- Treat repetition alone as sufficient evidence that a new abstraction is warranted.
- Rewrite existing routines merely to conform to a new wrapper when they already expose a suitable interface.

## Users and Responsibilities

| Role | Responsibility |
|---|---|
| Contributor | Searches the routine inventory, reuses an exact match, and records unmet capability needs. |
| Maintainer | Decides whether mechanics are stable enough to compile; every routine declares one owning domain and owning Maintainer, while interface changes require approval from Maintainers of consuming domains. |
| Distiller | Classifies captured procedure mechanics as judgment, deterministic routine, or mixed procedure and records whether a routine proposal is required. |
| Proposer | Recommends reuse, extension, creation, prose retention, or no action within the existing Task P proposal lifecycle. |
| Reviewer | Verifies contract depth, behavioral evidence, clean cutover, and absence of duplicate mechanics. |

## Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-PC01 | Task 9 must classify procedure mechanics as `judgment`, `deterministic-routine`, or `mixed-procedure` in the distillation record or linked Task P artifact; this classification is independent of `artifact_role`, applies only to procedure-role material, and remains a reasoned agent decision rather than CLI inference. Uncertain material follows the existing `no_action` path. | must |
| FR-PC02 | A routine candidate must identify repeated use, stable inputs and outputs, deterministic behavior, expected failures, side effects, and why one shared implementation improves locality or leverage. | must |
| FR-PC03 | Before proposing or implementing a routine, the workflow must search a canonical routine inventory and choose reuse or extension when an owning module already provides the required capability. | must |
| FR-PC04 | Task P retains its atomic `result: create|update|no_action` vocabulary and gains `target_kind: routine` plus `routine_action: reuse|extend|create|keep_as_prose|none`. `create` and `extend` map to proposal results `create` and `update`; `reuse`, `keep_as_prose`, and `none` map to `no_action` with a reason. One proposal targets either a routine or a procedure; work requiring both uses two explicitly linked proposals. | must |
| FR-PC05 | Every compiled routine must have a stable routine identifier, owning domain and Maintainer, owning Python module and symbol, concise contract, deterministic/offline declaration, side-effect declaration, behavioral test references, and consuming procedure references. | must |
| FR-PC06 | Creating or changing a shared or cross-domain routine requires the existing fresh-context proposer policy, recorded `proposer_mode`, target-Maintainer approval, and approval from Maintainers of domains whose procedures consume the changed interface. | must |
| FR-PC07 | The canonical routine inventory must be generated deterministically from authoritative source declarations, never maintained as an independent handwritten registry. | must |
| FR-PC08 | Kosmic validation must reject duplicate routine identifiers, missing modules or symbols, missing declared behavioral tests, invalid consumers, and inventory drift. | must |
| FR-PC09 | Domain Topic procedures must be able to declare the routines they invoke; validation must reject unknown routine identifiers and non-procedure consumers. | must |
| FR-PC10 | Routine implementation and tests must cross the same small module interface; callers must not need internal implementation details. | must |
| FR-PC11 | Accepted routine work must migrate every known caller, remove superseded duplicate code and algorithmic prose, and preserve the procedure's intent, decisions, verification, and failure policy. | must |
| FR-PC12 | Generated procedure packets must identify required routine IDs and exact invocation interfaces without embedding or executing Python source. | must |
| FR-PC13 | Create/extend proposals and implementation work must include baseline-versus-candidate behavioral evidence and pass Task 7 Standards and Spec review before publication. | must |
| FR-PC14 | New Story and Quick Task records must declare `routine_decision_required: true|false`; true requires exactly one valid `routine_proposal` path per routine target, while false forbids the path and records the reason in the body. The deterministic completion gate applies only from these declared fields, never prose inference. | must |
| FR-PC15 | Existing procedures and Python helpers without routine metadata remain valid during an explicit migration period; a procedure that newly declares or changes a routine invocation must set `routine_decision_required: true`. | must |
| FR-PC16 | The core implementation must remain Python 3.11+, stdlib-only, deterministic, and offline; routine discovery and validation must not import or execute declared routine modules. | must |
| FR-PC17 | The CLI must expose bounded commands to generate, validate, and query the routine inventory by ID, module, symbol, summary, owning domain, and consuming procedure. | must |
| FR-PC18 | Routine publication must be atomic and hash-pinned with the existing catalog/manifest lifecycle; failed generation must leave the prior inventory usable. | must |
| FR-PC19 | Completion gates must fail declared routine work when its proposal decision, required approvals, behavioral evidence, caller migration, or convergent review is missing. | must |
| FR-PC20 | The first release must compile the duplicated atomic directory-publication mechanics used by Project Skill Pair `generate` and Shared Skill Library `generate-library` into one reviewed routine, migrate both callers, and dogfood inventory query, success, injected-failure rollback, validation, and four-adapter publication behavior. | must |
| FR-PC21 | Routine proposal validation, completion checks, rejection fingerprints, templates, and Task P documentation must accept the routine fields without changing the meaning or validity of existing create/update/no-action proposals. | must |

## Non-Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| NFR-PC01 | Identical authoritative sources must produce byte-identical routine inventory, manifest, query JSON, and procedure references across repeated runs. | must |
| NFR-PC02 | Invalid declarations, symbols, tests, consumers, proposals, hashes, and gates must fail closed with stable typed errors naming the responsible routine or work item. | must |
| NFR-PC03 | Added routine metadata and packet framing must remain inside existing domain, topic, and byte-budget limits; overflow rejects the complete packet without truncation. | must |
| NFR-PC04 | Generation and validation must be offline, Python 3.11+ stdlib-only, and must not import or execute routine modules. | must |
| NFR-PC05 | Publication must use the existing atomic swap and rollback discipline; a failure at any injected stage preserves the complete prior inventory and generated library. | must |
| NFR-PC06 | Routine lookup must scan only the generated inventory and remain bounded by its size; it must not scan Project repositories or import source modules at query time. | must |
| NFR-PC07 | Untouched legacy procedures, proposals, fingerprints, and helpers must remain byte-valid during the declared migration period. | must |

## Routine Eligibility

A candidate is eligible only when all are true:

1. The mechanics have appeared in at least two credible call sites or Evidence Pack observations, or one implementation already has multiple callers.
2. Inputs, outputs, invariants, failures, and side effects can be stated without embedding task-specific judgment.
3. Behavioral correctness can be tested through one small module interface.
4. Reuse removes meaningful duplicated logic or prevents agents from reconstructing a correctness-sensitive algorithm.
5. The owning Maintainer accepts the interface and clean-cutover plan.

The repetition threshold may be waived for a correctness-critical deterministic operation—such as atomic publication or provenance hashing—when a second implementation would create unacceptable risk. The proposal must state that reason explicitly.

## User Workflow

1. Task 9 classifies mechanics in its distillation record and sets the work item's declared routine-decision gate.
2. The agent queries the routine inventory before proposing new code.
3. Task P emits one routine-target proposal using the existing result lifecycle and the mapped routine action.
4. Fresh-context and owning/consuming Maintainer approvals apply where the target is shared or cross-domain.
5. An approved Story or Quick Task adds failing behavioral tests, implements the routine, and migrates every caller.
6. Generation produces the canonical hash-pinned inventory.
7. Validation checks declarations, symbols, tests, consumers, hashes, and clean publication.
8. Task 7 reviews both code quality and conformance to the proposal and work item.
9. Only accepted routines and updated procedures are published.

## Success Criteria

- [ ] `generate` and `generate-library` both call one compiled atomic-publication routine and retain their current public behavior.
- [ ] Success and injected-failure tests prove atomic replacement, rollback, and cleanup through that routine's module interface.
- [ ] A bounded inventory query returns the atomic-publication routine by ID, symbol, owning domain, summary text, and each of its two consumers without reading source repositories.
- [ ] Duplicate IDs, missing symbols/tests/consumers, stale hashes, and stale inventory each fail with stable actionable errors.
- [ ] A reviewed mixed procedure retains judgment and approval branches in Markdown while invoking Python for deterministic publication mechanics.
- [ ] Baseline and compiled implementations produce equivalent observable behavior on representative success and failure cases.
- [ ] Shared Library resolution, Project projection, installation, completion gates, rejection memory, and all four adapter byte checks remain regression-free.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Abstraction from weak repetition | Shallow modules and needless indirection | Eligibility contract, inventory search, Maintainer approval, and deletion test. |
| Prose and code both remain authoritative | Drift and contradictory instructions | Clean cutover: procedures reference invocation and policy, not duplicate algorithms. |
| Validation executes untrusted modules | Side effects or compromised determinism | Static declarations and source inspection only; no import during generation or validation. |
| One giant utilities module | Poor ownership and hidden coupling | Each routine declares an owning module; extension must preserve a coherent deep interface. |
| Routine metadata becomes manual bureaucracy | Stale inventory and low adoption | Generate the inventory from declarations and keep the required contract compact. |
| Mechanical automation absorbs judgment | Unsafe behavior | Explicit three-way Task 9 classification and reviewer check of retained decisions and gates. |
| Compatibility lasts indefinitely | Two conventions remain | Time-bounded explicit migration with new-change enforcement and a later clean schema cutover. |

## Compatibility and Migration

The initial release is additive for untouched procedures, proposals, fingerprints, and helpers. New Story and Quick Task templates declare `routine_decision_required`; the CLI enforces only the declaration and linked proposal, never an inferred assessment of prose. A procedure that newly declares or changes a routine invocation must use the true path. Existing reusable Kosmic functions are inventoried and classified without wrapping them solely for metadata.

The first migration extracts atomic directory publication behind one deep module interface and moves both Project Skill Pair and Shared Skill Library callers in a clean cutover. After representative dogfood, a separately approved cutover may require routine references for all compiled procedure mechanics. No generated inventory alias, compatibility wrapper, or parallel handwritten registry becomes permanent.

## Open Questions

None. Architecture must choose the static source declaration format, inventory location, CLI seam, hashing boundary, and migration sequence while preserving the constraints above.
