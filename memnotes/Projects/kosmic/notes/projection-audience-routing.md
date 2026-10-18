---
type: Project Knowledge
title: Projection audience routing
status: stable
audience: development
tags: [projection, audience, routing]
created: '2026-09-02'
updated: '2026-09-02' # promoted
validation_procedure: "Read collect_projection_plan and router_text in skills/scripts/kosmic_project_skills.py; cross-check references/task_project_skills.md invariants"
project: kosmic
---

# Projection audience routing

## Behavior (v3.0.0)

`collect_projection_plan` in `skills/scripts/kosmic_project_skills.py` admits only stable, non-expired, non-`usage_stale` notes and routes them by Audience Scope:

- `audience: usage` and `audience: both` → Usage package only.
- `audience: development` → Development package only.
- Missing `audience` → unscoped; Development-only until reviewed.

Consequence: a `both` note is **not** copied into the Development package. The Development router instead carries a textual instruction to load the Usage companion for consumer and shared behavior (`router_text`; codified in `references/task_project_skills.md` invariant: "Development projects stable `audience: development` notes and requires Usage for consumer and shared behavior").

## Change direction

The route-graph redesign (project `both` notes into Development routes, intent-keyed routers) was drafted and then **abandoned on 2026-09-02** before implementation; see the archived [PRD](../specs/archive/2026-09-02-prd-route-graph.md) and [Architecture](../specs/archive/2026-09-02-architecture-route-graph.md). The routing behavior described above therefore remains current. The active improvement direction is WikiSkill-style experience compilation (see [PRD](../subprojects/experience-compilation-adapting-wikiskill-into-kosmic/specs/prd.md)).


## Related

- [Notation](notation.md) — Audience Scope vocabulary.
