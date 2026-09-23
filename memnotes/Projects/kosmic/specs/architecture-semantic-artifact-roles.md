---
status: approved
created: 2026-09-07
updated: 2026-09-07
linked_prd: prd-semantic-artifact-roles.md
linked_research: []
linked_epics: [epics/epic-17-semantic-role-schema.md, epics/epic-18-role-aware-resolution.md, epics/epic-19-classification-migration-release.md]
---

# Architecture: Semantic Artifact Roles

## Overview

This feature deepens the existing Shared Library Resolver Module rather than adding another router or adapter seam. Authoritative Project notes and shared Domain Topics gain the same four-value semantic vocabulary: `procedure`, `guideline`, `knowledge`, and `evidence`. Audience continues to control consumer/contributor visibility; artifact role controls operational authority.

The existing root Shared Skill Router and Domain Skills remain routing documents. Descendant `Skill Topic` documents become role-neutral `Domain Topic` documents. For actionable requests, the Resolver selects exactly one procedure and closes four typed relationship sets. Reference requests may return knowledge, guidelines, or evidence without pretending to produce executable guidance.

```text
request + audience + optional intent override
                     │
                     v
              Intent Classifier
          do | check | understand | investigate
                     │
                     v
             Primary Role Selector
                     │
          ┌──────────┴───────────┐
          │                      │
     task result          reference-only result
   one procedure          knowledge/guideline/evidence
          │
          v
 typed closure + role validation
          │
          v
 hash-pinned bounded Recipe Packet
```

No optional Research branch is needed: the ABINIT audit and current implementation expose the relevant data shapes and seams, while the product decisions are resolved in the approved PRD.

## Architectural Decisions

### AD-SR1: Artifact role is orthogonal to audience

**Context**: `audience` answers whether a topic serves Usage or Development. It does not say whether the topic directs action, constrains judgment, explains facts, or records a prior observation.

**Decision**: every active Domain Topic declares exactly one `artifact_role` from `procedure`, `guideline`, `knowledge`, or `evidence`. Project notes use the same field. The catalog stores both `audience` and `artifact_role`; neither is inferred from the other, the file path, headings, or prose.

**Consequences**: one knowledge topic can serve Development without becoming a procedure. Classification becomes explicit Maintainer work. Existing content requires migration.

**Alternatives considered**: encode role in `type` only (rejected: weak querying and migration); derive role from audience (rejected: repeats the defect); infer from prose (rejected: nondeterministic and unsafe).

### AD-SR2: Domain Topic replaces Skill Topic

**Context**: `Skill Topic` assigns skill semantics to every descendant even though many are reference or evidence documents.

**Decision**: canonical descendant metadata uses `type: Domain Topic`. Root `type: Shared Skill Router` and domain-root `type: Domain Skill` remain unchanged because those documents genuinely route agent behavior. Schema and generator versions advance together; generated catalogs, indexes, plans, packets, validation errors, templates, and documentation use Domain Topic terminology.

**Consequences**: the library retains its existing filesystem layout and installed router. The schema cutover is intentionally incompatible; there is no permanent alias for `Skill Topic`.

**Alternatives considered**: retain the name and add role (rejected: continued semantic ambiguity); create four filesystem trees (rejected: role moves would churn paths and IDs).

### AD-SR3: Procedures satisfy a behavioral body contract

**Context**: numbered steps also appear in reports and explanatory notes. Metadata alone cannot prevent a historical sequence from being mislabeled as an executable procedure.

**Decision**: stable procedures require non-empty `triggers` and `outcome` metadata plus exactly discoverable level-two sections: `When to use`, `Preconditions`, `Procedure`, `Decisions and branches`, `Verification`, `Failure handling`, and `References`. Validation checks structural presence and non-empty content, not the prose's truth. Other roles do not require these sections.

**Consequences**: procedural authority is reviewable and mechanically bounded. Existing mixed documents remain knowledge until deliberately distilled. The validator does not become a semantic LLM.

**Alternatives considered**: frontmatter-only procedure fields (rejected: awkward long instructions and poor readability); free-form procedure prose (rejected: reports can pass accidentally); require a separate file extension (rejected: no semantic gain).

### AD-SR4: One typed relationship interface replaces `requires`

**Context**: the current `requires` graph only expresses loading order. It cannot distinguish prerequisite execution, normative governance, informational context, or empirical support.

**Decision**: Domain Topics expose four list fields:

```yaml
requires_procedures: []
governed_by: []
uses_knowledge: []
supported_by: []
```

Target roles are exact:

| Edge | Allowed target |
|---|---|
| `requires_procedures` | `procedure` |
| `governed_by` | `guideline` |
| `uses_knowledge` | `knowledge` |
| `supported_by` | `evidence` |

All edges use canonical topic IDs. Unknown targets, self-edges, role mismatches, cycles, and Usage-to-Development dependencies fail validation. Cycle detection traverses the union graph; packet ordering additionally preserves prerequisite-procedure order.

**Consequences**: dependency meaning appears in plans and review. `requires` is removed after explicit migration rather than retained as an alias.

**Alternatives considered**: retain one edge plus target-role inspection (rejected: callers still cannot know why content loaded); typed Markdown links (rejected: prose links are not dependency declarations).

### AD-SR5: Intent classifier is deterministic with explicit override

**Context**: the user approved convenient inference plus a deterministic correction path.

**Decision**: `resolve_library` accepts `intent: str | None`; CLI accepts `--intent {do,check,understand,investigate}`. An explicit value wins. Otherwise a pure `_infer_intent(normalized_query)` function uses a versioned ordered vocabulary stored as module constants. Exact action verbs select `do`; review/compliance verbs select `check`; diagnostic/cause/evidence verbs select `investigate`; explanatory/default queries select `understand`. The chosen intent and `explicit|inferred` origin enter the request and plan hash.

If inference produces tied categories, fail with `AMBIGUOUS_INTENT` and request `--intent`; do not guess.

**Consequences**: normal agent requests remain concise; tests can pin behavior; changing vocabulary requires a schema/generator review.

**Alternatives considered**: always require intent (rejected by PRD decision); inference without override (rejected: no correction interface); model classification (rejected: offline nondeterminism).

### AD-SR6: Primary selection is role-aware

**Context**: the current `_score` ranks every stable topic together. A highly matching report can beat the actual task procedure.

**Decision**: audience/status eligibility runs first, then intent selects the primary role set:

| Intent | Primary eligibility |
|---|---|
| `do` | procedure only |
| `check` | guideline first; procedure permitted only when no guideline matches and labeled supporting procedure |
| `understand` | knowledge first; guideline permitted only as a labeled reference fallback |
| `investigate` | non-superseded evidence first, then knowledge fallback |

Explicit topic routes remain valid for every role and set result mode from the routed role. Domain-only routes continue to load only the Domain Skill. Query scoring remains deterministic within the eligible role set.

A `do` query with no procedure emits `NO_EXECUTABLE_MATCH`; it never falls back to knowledge. Other non-action intents may return `mode: reference`. The plan records `intent`, `mode`, `primary_topic`, and every exclusion reason.

**Consequences**: operational authority is fail-closed. Reference discovery remains available. Existing score weights can be reused after role filtering.

**Alternatives considered**: score role as another weight (rejected: enough textual overlap can still let evidence win); return knowledge as a do fallback (rejected: misleading authority).

### AD-SR7: Resolver computes a labeled relationship closure

**Context**: flat `ordered_loads` cannot explain whether a topic is executable, governing, informational, or evidentiary.

**Decision**: the Resolver Module computes closure from the primary topic and emits topic plan rows with `artifact_role`, `relation`, and `included_by`. Relations are `primary`, `prerequisite`, `governing`, `knowledge`, and `evidence`. A topic reached through multiple edges is loaded once and records a sorted set of reasons.

Actionable packet presentation order is:

1. owning Domain Skills;
2. prerequisite procedures in dependency-first order;
3. primary procedure;
4. governing guidelines;
5. required knowledge;
6. evidence only for explicit routes, `investigate`, or an explicit include-evidence option.

`load_recipe_packet` verifies the plan hash, manifest hash, source hashes, byte sizes, role, and relation before emission. Packet framing labels role and relation.

**Consequences**: callers receive a bounded task packet rather than a bag of related documents. Domain Skills still precede topics because they carry ownership and routing context.

**Alternatives considered**: procedure first before prerequisites (rejected: violates dependency-first execution); preserve existing flat dependency order (rejected: semantics stay hidden).

### AD-SR8: Evidence freshness is optional but validated

**Context**: evidence snapshots may conflict or age. The user rejected mandatory subject chains because Kosmic has no stable subject-identity model.

**Decision**: evidence requires ISO `observed_on`. It may declare `supersedes: [evidence-topic-id]`. Each target must be evidence, exist, be older by observation date, and remain audience-compatible. The supersession graph must be acyclic. Investigation queries exclude transitively superseded evidence from primary candidates unless explicitly routed; plans record the exclusion reason. No same-subject inference occurs.

**Consequences**: Maintainers can express known replacement without fabricating relationships between independent observations. Dates remain visible even when no edge exists.

**Alternatives considered**: mandatory supersession per subject (rejected: needs a subject schema); date-only latest-wins (rejected: unrelated evidence can share dates/topics); no freshness model (rejected: stale status can appear current).

### AD-SR9: Project notes share classification, not shared-library procedure structure

**Context**: Task 9 outputs Project Knowledge first; later Task P proposals may promote reusable procedures. Role must survive this transition, but ordinary Project notes should not all satisfy the strict shared-procedure body contract.

**Decision**: Project notes created or materially updated through Kosmic require `artifact_role`. `validate_notes_bundle` validates the vocabulary. A Project note labeled `procedure` uses the same behavioral section contract because it can already project into a Project Skill Pair. Existing untouched notes remain accepted during a bounded migration phase but are reported as unclassified and cannot seed a new shared-library proposal.

Task 9 first chooses the artifact role. Task P is required for new/materially changed procedure notes only. Proposal manifests and fingerprints include `artifact_role`; project-knowledge/no-action paths remain available for other roles.

**Consequences**: classification begins at knowledge capture rather than being guessed during migration. Legacy vaults do not fail immediately, but unclassified notes cannot silently become shared procedures.

**Alternatives considered**: classify only shared topics (rejected: semantics are lost upstream); require immediate edits to every historical Project note (rejected: excessive migration blast radius).

### AD-SR10: Explicit staged migration with ABINIT as fixture

**Context**: current shared topics use `type: Skill Topic`, `requires`, and no semantic role. ABINIT has enough variety to prove classification and routing behavior.

**Decision**: migration assignments expand from `source -> target ID` to records containing `target`, `artifact_role`, and typed relationships. No role is inferred. Generation stages rewritten Domain Topics and generated artifacts, validates the complete graph and representative requests, then swaps once.

ABINIT migration uses four explicit buckets:

- clear procedures: initially the six approved in the PRD audit;
- guidelines: Fortran design rules and lattice/matrix convention checks;
- durable explanatory material: knowledge;
- reports, statuses, audits, and validation snapshots: evidence when an observation date is defensible, otherwise knowledge pending evidence curation.

Mixed implementation documents default to knowledge. Converting one later requires Task 9 distillation, Task P where applicable, Maintainer approval, behavioral evidence, and normal publication.

**Consequences**: migration preserves content and provenance while reducing false operational authority. The fixture supports before/after routing comparisons and packet-size checks.

**Alternatives considered**: bulk default every topic to knowledge (rejected: hides unreviewed assignments); automatically classify by title (rejected: nondeterministic semantics); migrate every domain simultaneously (rejected: unnecessarily large failure surface).

## Module Changes

### Shared Library Resolver Module

`skills/scripts/kosmic_shared_library.py` remains the sole implementation module for shared-library parsing, cataloging, graph validation, resolution, plan loading, migration, and router publication.

New or replaced internal interfaces:

```python
ARTIFACT_ROLES = {"procedure", "guideline", "knowledge", "evidence"}
INTENTS = {"do", "check", "understand", "investigate"}
RELATION_FIELDS = {
    "requires_procedures": "procedure",
    "governed_by": "guideline",
    "uses_knowledge": "knowledge",
    "supported_by": "evidence",
}

def _infer_intent(query: str) -> str: ...
def _validate_topic_body(document: Document, role: str, path: Path) -> None: ...
def _relationship_order(primary: str, by_id: dict[str, dict[str, Any]], *, include_evidence: bool) -> list[dict[str, Any]]: ...

def resolve_library(..., intent: str | None = None, include_evidence: bool = False) -> dict[str, Any]: ...
```

These are internal seams. The external CLI remains `generate-library`, `validate-library`, `resolve-library`, `load-library`, `migrate-library`, `install-library`, and `check-library-installation` with additive resolver options and an intentionally versioned catalog/assignment schema.

### Project Projection Module

`skills/scripts/kosmic_project_skills.py` adds the shared artifact-role vocabulary to note validation, migration reporting, Task P proposal fingerprints, and templates. Project Skill Pair generation labels projected references by role and prevents non-procedure references from being presented as executable task guidance. The pair remains a compatibility/project-local projection mechanism; the Shared Library remains the cross-project authority.

### Documentation and templates

Update:

- Kosmic `SKILL.md` terminology and Task Selection behavior;
- `task_distill.md` classification step;
- `task_propose_skill.md` procedure eligibility gate;
- note, proposal, and shared-topic templates;
- Shared Library authoring/installation documentation;
- Kosmic glossary and stable shared-domain note.

## Data Flow

```text
Evidence Pack
    │
    v
Task 9 Distill ──classify──> Project note
                              role: procedure|guideline|knowledge|evidence
                                      │
                         procedure only: Task P decision
                                      │
                                      v
                         governed Domain Topic proposal
                                      │ Maintainer approval
                                      v
                         explicit role/relationship publication
                                      │
                                      v
                       generated catalog + manifest
                                      │
                   request ──> intent/role selection
                                      │
                                      v
                        typed, bounded Recipe Packet
```

## Migration and Compatibility

1. Advance shared-library schema and generator versions.
2. Generate an inventory report for every current Domain Topic.
3. Require explicit role and typed relationship assignments.
4. Migrate ABINIT in staging and run representative `do`, `understand`, and `investigate` requests.
5. Migrate Kosmic and TB2J after the ABINIT contract passes.
6. Publish the complete `Skills/` tree atomically.
7. Regenerate the installed router only if its bytes change; domain topics remain dynamically loaded.
8. Remove `Skill Topic`, untyped `requires`, and old assignment schema support in the same release.

Existing Project notes without `artifact_role` remain valid but are reported as unclassified during the migration window. Newly created or materially updated notes must carry a role. A later separately approved cleanup may make the field universally mandatory after vault inventories are complete.

## Test Strategy

### Schema and graph

- Accept each artifact role and reject missing/unknown roles.
- Enforce procedure metadata and required body sections.
- Enforce every relationship's target role, existence, audience compatibility, and acyclicity.
- Validate evidence dates and optional supersession edges.
- Reject old canonical `Skill Topic` and `requires` fields after cutover.

### Resolver behavior

- Explicit and inferred intent produce identical plans when semantically equivalent.
- Ambiguous inference fails with `AMBIGUOUS_INTENT`.
- `do` selects procedures only and returns `NO_EXECUTABLE_MATCH` rather than knowledge fallback.
- `understand` returns reference mode with knowledge.
- `investigate` prefers non-superseded evidence and labels dates.
- Explicit routes preserve the routed role and mode.
- Typed closure order, deduplication, trace, hashes, and byte accounting are exact.

### Migration

- Assignment must cover every source and include a role.
- Source hashes, source Project, evidence, audience, and ownership survive.
- Mixed ABINIT documents remain knowledge unless explicitly assigned otherwise.
- Failure before swap preserves the previous complete library.
- Representative old/new ABINIT queries record expected semantic differences rather than false byte equivalence.

### Regression and release

- Existing Evidence Pack, MathDoc, Task P, completion, governance, resolver budget, atomic generation, and adapter tests pass.
- Real ABINIT queries verify procedure, knowledge, guideline, and evidence behavior.
- All four adapters byte-check the one installed root router; active-session discovery remains explicitly separate.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Maintainers misclassify reports as procedures | High | Strict procedure contract, explicit review, behavior evidence, fail-closed Task P gate |
| Intent vocabulary routes an action as reference | High | Ordered deterministic rules, ambiguity failure, explicit `--intent` override |
| Evidence dominates normal tasks | High | Exclude evidence from `do` packets unless explicitly included; role-aware primary selection |
| Migration silently demotes useful procedures | Medium | Explicit per-topic assignment and representative ABINIT behavioral comparison |
| Strict procedure sections encourage boilerplate | Medium | Validate a small fixed contract and allow concise sections; no additional nested schema |
| Typed graph increases authoring cost | Medium | Four stable fields, generated inventory, exact errors, templates, and validation before publication |
| Legacy Project notes remain semantically unknown | Medium | Report unclassified notes; block them from seeding shared proposals; classify on touch |
| Schema cutover breaks stale plans | Low | Intentional version bump and hash-pinned fail-closed regeneration guidance |

## Out of Scope

- Semantic truth checking of note bodies.
- Automatic subject identity or conflict resolution across independent evidence.
- Model-based intent or role classification.
- Paragraph-level loading or partial topic truncation.
- Reclassifying every historical Project note in every vault during this feature.
- Creating native Agent Skills for individual procedures.
