---
status: done
created: 2026-09-02
updated: 2026-09-02
linked_prd: ../archive/2026-09-02-prd-route-graph.md
linked_architecture: ../archive/2026-09-02-architecture-route-graph.md
open_questions: []
---

# Research: Systematizing generated Project skills

## Question

Generated Project guidance feels fractioned. Which projection architecture makes it systematic while preserving Kosmic's invariants?

## Context

Three read-only scouts mapped the v3.0.0 projection model (`skills/scripts/kosmic_project_skills.py`), workflow docs, and design alternatives on 2026-09-02. Key evidence: `collect_projection_plan` routes `usage`/`both` → Usage and `development` → Development; `router_text` emits flat topic lists plus a Development→Usage companion instruction; adapters install exactly two packages atomically.

## Sources

- `skills/scripts/kosmic_project_skills.py` — `collect_projection_plan` (439-500), `router_text` (530-600), `build_projection_root` (628-680), `validate_projection_root` (685-755), adapters (1098-1230)
- `skills/references/task_project_skills.md` — projection invariants
- `CONTEXT.md` — domain language (Skill Pair, Skill Router, Audience Scope)
- `docs/adr/0001-required-matt-pocock-procedure-skills.md`, `docs/research/matt-pocock-skills-for-kosmic.md`

## Findings

- Fragmentation is not skill count (exactly two per Project); it is (1) `both` notes absent from Development, (2) flat discretionary routers, (3) stranded specs/logs, (4) layered source/canonical/installed lifecycles, (5) eligibility filters that silently omit knowledge.
- Docs contradictions: named-skill-only support claim vs pointer adapter; dependency lists differ from `REQUIRED_PROCEDURE_SKILLS`.
- Codex adapter root `~/.agents/skills` mismatches this runtime's `~/.codex/skills` (observed 2026-08-20).

## Options Considered

### Option A: Single composition-root skill

**Pros**:
- One caller entry point; shared facts stored once; simplest invocation.

**Cons**:
- Removes the Consumer/Contributor contract; root risks becoming a shallow decision document; breaks installed pair callers.

### Option B: Keep the pair; shared route graph + bounded route manifests

**Pros**:
- Preserves names, adapters, AGENTS fields — smallest compatible migration.
- Makes shared knowledge first-class in Development routes.
- Deepest module: small stable interface (two names + intent) hiding routing, ordering, and coverage complexity.

**Cons**:
- Projection/validation grow richer (routes, vocabularies, coverage rules).
- Two entry points remain.

### Option C: Task-oriented capability catalog

**Pros**:
- Matches task-shaped requests best; explicit prerequisites and escalation.

**Cons**:
- Highest authoring/validation cost; taxonomy becomes its own discovery problem; premature for sparse notes.

## Recommendation

**Option B**, approved by the user on 2026-09-02. Capability catalog (C) may be revisited once several Projects show stable recurring task families.

## Open Questions

(None blocking; PRD open questions cover `requires` acyclicity, fallback routing, and strict mode.)

## Architecture Impact

Architecture must add ADRs for: route metadata schema and controlled vocabularies; router generation contract (ordering, prerequisites, stopping rules); coverage/integrity validation rules; backward-compatible migration for existing projections.

## Notes to Capture

- [Projection audience routing](../../notes/projection-audience-routing.md) — captured.
