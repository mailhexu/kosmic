---
status: approved
archived: 2026-09-02
archived_reason: "User abandoned the route-graph direction in favor of adapting WikiSkill (arXiv 2608.27454) into Kosmic; see ../prd.md"
created: 2026-09-02
updated: 2026-09-02
linked_research: [../../evidence/2026-09-02-route-graph-skill-projection/memo.md]
linked_epics: []
---

# Route-Graph Project Skill Pair

## Problem Statement

The v3.0.0 Projection CLI flattens Project Knowledge into two independently routed skill packages whose `SKILL.md` files are flat topic indexes. Three effects fragment generated guidance:

1. **Shared-knowledge indirection.** `audience: both` notes project into Usage only; the Development router must tell contributors to load the Usage companion to reach shared facts (`collect_projection_plan`, `skills/scripts/kosmic_project_skills.py:439-500`).
2. **Discretionary routing.** Each router lists topics without order, prerequisites, or stopping rules, so agents must infer which references matter for a task.
3. **No coverage contract.** Nothing checks that each declared Consumer Interface has configure/invoke/troubleshoot coverage or that Contributor routes include validation guidance.

The system stays deterministic, but its output is a pile of topics rather than task-shaped guidance.

## Goals

- Make shared Project Knowledge directly reachable from Development routes without the Usage-companion indirection.
- Replace flat topic lists with generated, ordered route manifests keyed by task intent.
- Introduce one controlled routing taxonomy (domains and intents) shared by Usage and Development projections.
- Add deterministic coverage and integrity checks to `validate` and `review`.
- Preserve the existing public contract: pair names, adapter installation paths, AGENTS integration fields, and the `generate → validate → install` lifecycle.

## Non-Goals

- Renaming or collapsing `{PROJECT_ID}-usage` / `{PROJECT_ID}-development` (Design A rejected).
- Task-oriented capability catalog projection (Design C deferred).
- Projecting specs or logs directly; distillation into stable notes remains the only path.
- Changing the OKF v0.2 notes bundle format beyond additive optional frontmatter.
- Deduplicating physical reference copies across the two packages (each package stays self-contained; layout is an implementation detail).

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-001 | Additive optional note frontmatter: `domains: [list]`, `intents: [list]`, `requires: [note-list]`; values validated against the controlled vocabularies; `requires` must resolve to existing notes | must |
| FR-002 | Controlled vocabularies defined once in the CLI: domains `interfaces, configuration, operations, architecture, testing, release`; intents `configure, invoke, integrate, troubleshoot, change, test, review, release` | must |
| FR-003 | Development plan includes stable `audience: both` notes alongside `development` notes; Usage plan continues to receive `usage` and `both` notes | must |
| FR-004 | Generated routers present intent-keyed routes: each route lists ordered references with prerequisites and a stopping rule, plus provenance-bearing topic references as today | must |
| FR-005 | Stable notes without route metadata still project under an explicit "General topics" fallback route (backward compatibility) | must |
| FR-006 | `validate` fails on: unknown vocabulary values, unresolvable `requires`, routes referencing excluded notes, missing Development→Usage companion declaration | must |
| FR-007 | `review` reports unrouted stable notes (no domains/intents), unscoped notes, and per-intent coverage gaps; per-Consumer-Interface coverage deferred until an interface registry exists (ADR-0005) | must |
| FR-008 | Unscoped notes remain Development-only and never enter consumer routes | must |
| FR-009 | Existing projects regenerate without note edits; only router content and manifests change | must |
| FR-010 | Pair manifest records per-package route inventory and source provenance sufficient for drift detection | must |
| FR-011 | `check-completion` continues to enforce the Consumer Interface gate against stable `usage`/`both` notes | must |
| FR-012 | Update `SKILL.md`, `README.md`, `references/task_project_skills.md`, `references/task_add_note.md`, and `docs/` to document route metadata and router semantics | should |

## Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-001 | Determinism: identical notes produce byte-identical projections; regeneration comparison in `validate` unchanged in spirit | must |
| NFR-002 | Standard library only; Python 3.11+ | must |
| NFR-003 | Atomic publication and installation with rollback preserved; generated-marker and provenance invariants preserved | must |
| NFR-004 | Router SKILL.md stays under ~150 lines even with many notes (progressive disclosure via references) | should |

## Success Criteria

- [ ] A project with `both`, `usage`, `development`, and unscoped notes generates a pair where Development routes include the `both` notes directly and unscoped notes stay Development-only.
- [ ] An existing v3.0.0 project regenerates with no note edits and passes `validate` (FR-009).
- [ ] `validate` rejects a note with an unknown domain, an unresolvable `requires`, or a route pointing at an excluded note.
- [ ] `review` lists unrouted stable notes and per-intent coverage gaps.
- [ ] Full `tests/` suite passes with new coverage for FR-001..FR-011.

## Open Questions

- [x] Should `requires` edges be validated acyclic (DAG check) in `validate`, or only resolvable? — **Resolved (ADR-0004)**: resolvable only; ordering is deterministic `(domain index, title)`.
- [x] Should the fallback "General topics" route be split per audience or shared? — **Resolved (ADR-0005)**: per package, matching FR-003 routing.
- [x] Is a `--strict-routing` mode (fail `generate` on unrouted stable notes) wanted now or deferred? — **Resolved (ADR-0005)**: defer; `review` reporting suffices.
