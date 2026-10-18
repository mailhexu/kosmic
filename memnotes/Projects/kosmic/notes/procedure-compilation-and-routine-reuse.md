---
type: Project Knowledge
title: Procedure Compilation and Routine Reuse
description: Classify procedure mechanics, reuse canonical deterministic Python routines, and keep judgment in reviewed skill prose.
confidence: 0.9
created: '2026-09-07'
updated: '2026-10-18T17:20:40.811131Z'
skill_candidate: true
validation_procedure: "python3 -m unittest tests.test_kosmic_routines tests.test_shared_library tests.test_project_skills_cli"
project: kosmic
status: stable
audience: development
artifact_role: procedure
usage_stale: false
tags: [procedure-compilation, routines, task-p, governance]
outcome: Repeated deterministic mechanics resolve to one tested canonical routine while contextual judgment remains in skill prose.
evidence: [evidence/2026-09-07-procedure-compilation/session-record.md, evidence/2026-09-07-procedure-compilation/behavioral-validation.md]
---

# Procedure Compilation and Routine Reuse

## When to use

A Story or Quick Task introduces or materially changes repeatable procedure mechanics.

## Preconditions

The procedure role, owning domain, stable inputs, bounded outputs, expected failures, and behavioral evidence are known. Approved work and human gates remain authoritative.

## Procedure

1. Classify each procedure segment as judgment, deterministic routine, or mixed.
2. Query `.kosmic/routines.json` by exact ID, domain, module, symbol, owner, caller, procedure, or text before writing mechanics.
3. Reuse an exact routine; otherwise extend the owning module; create a routine only when no coherent implementation exists.
4. Declare static module-level `KOSMIC_ROUTINES`, typed IDs, callers, procedures, invariants, and determinism/offline properties.
5. Add focused behavioral tests and remove superseded handwritten mechanics in one clean cutover.
6. Record the governed Task P decision and declare `uses_routines` on every consuming procedure topic.
7. Regenerate and validate the Shared Library, then exercise the changed procedure packet.

## Decisions and branches

Keep interpretation, approval, risk, and context-dependent choices in prose. Compile only deterministic transformation, parsing, validation, hashing, publication, routing, migration, and reporting mechanics. Prefer reuse over extension and extension over creation.

## Verification

Static AST inspection must find the declaration without importing its module. Inventory, topic edges, source hashes, plan hashes, packet bytes, focused behavior, and rollback scenarios must all validate.

## Failure handling

Fail closed on dynamic declarations, duplicate IDs, missing modules or symbols, stale hashes, undeclared callers, broken reciprocal procedure edges, ambiguous queries, or partial publication. Atomic publication restores the previous complete tree after any mutation failure.

## References

- `skills/scripts/kosmic_routines.py`
- `skills/references/task_propose_skill.md`
- [Shared Domain Skill Library](./shared-domain-skill-library.md)
