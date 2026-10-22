---
type: Domain Topic
id: kosmic/development/projection-audience-routing
domain: kosmic
audience: development
status: stable
summary: Projection audience routing
triggers: [Projection audience routing]
aliases: []
evidence: []
source_project: kosmic
source_sha256: 18b70850c29c248cfdd88e2cee38bd2deaa4ec50998570f8dd4c4bb57d10d8d1
artifact_role: knowledge
requires_procedures: []
governed_by: []
uses_knowledge: []
supported_by: []
supersedes: []
source: notes/projection-audience-routing.md
---

# Projection audience routing

## Behavior (v3.0.0)

`collect_projection_plan` in `skills/scripts/kosmic_project_skills.py` admits only stable, non-expired, non-`usage_stale` notes and routes them by Audience Scope:

- `audience: usage` and `audience: both` → Usage package only.
- `audience: development` → Development package only.
- Missing `audience` → unscoped; Development-only until reviewed.

Consequence: a `both` note is **not** copied into the Development package. The Development router instead carries a textual instruction to load the Usage companion for consumer and shared behavior (`router_text`; codified in `references/task_project_skills.md` invariant: "Development projects stable `audience: development` notes and requires Usage for consumer and shared behavior").

## Change direction

The route-graph redesign (project `both` notes into Development routes, intent-keyed routers) was drafted and then **abandoned on 2026-09-02** before implementation; see the archived [PRD](/home/hexu/projects/myagentskills/kosmic/memnotes/Projects/kosmic/specs/archive/2026-09-02-prd-route-graph.md) and [Architecture](/home/hexu/projects/myagentskills/kosmic/memnotes/Projects/kosmic/specs/archive/2026-09-02-architecture-route-graph.md). The routing behavior described above therefore remains current. The active improvement direction is WikiSkill-style experience compilation (see [PRD](/home/hexu/projects/myagentskills/kosmic/memnotes/Projects/kosmic/subprojects/experience-compilation-adapting-wikiskill-into-kosmic/specs/prd.md)).


## Related

- [Notation](../usage/notation.md) — Audience Scope vocabulary.
