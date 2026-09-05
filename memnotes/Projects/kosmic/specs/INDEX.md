---
project: kosmic
created: 2026-09-02
updated: 2026-09-05
---

# Specs Index: kosmic

This index is navigational only. It does not replace PRD, Architecture, Story, Quick Task, or code review gates.

## Overview

- PRD: [PRD](prd.md) (approved 2026-09-02)
- Architecture: [Architecture](architecture.md) (approved 2026-09-02)
- Current focus: designing the Math Derivation Layer (`mathdocs/`) for SymPy-backed, reproducible equations

## Active Specs

| Type | Link | Status | Notes |
|------|------|--------|-------|
| PRD | [PRD](prd.md) | approved | Experience Compilation: single evidence layer, Task 9 distillation, impact ledger, completion gate |
| Architecture | [Architecture](architecture.md) | approved | Evidence layer, Task 9 distillation, impact ledger, completion gate — grounded in ADRs 0002-0003 |
| Feature PRD | [Math Derivation Layer](prd-math-derivation-layer.md) | approved 2026-09-05 | Seven Task 7 findings resolved; ready for Architecture |
| Feature Architecture | [Math Derivation Layer](architecture-math-derivation-layer.md) | approved 2026-09-05 | AD-M1..M8: registry, protocol, markers, atomic updates, validation, completion linkage |

## Research Memos

| Research | Status | Linked PRD | Linked Architecture | Recommendation |
|----------|--------|------------|---------------------|----------------|
| [2026-09-02 route-graph skill projection](../evidence/2026-09-02-route-graph-skill-projection/memo.md) | done | [Archived PRD](archive/2026-09-02-prd-route-graph.md) | [Archived Architecture](archive/2026-09-02-architecture-route-graph.md) | Option B: keep pair, shared route graph — direction abandoned by user |
| [2026-09-02 WikiSkill experience compilation](../evidence/2026-09-02-wikiskill-experience-compilation/memo.md) | done | [PRD](prd.md) | [Architecture](architecture.md) | Posture B staged: adapt WikiSkill engine writing into Kosmic substrate |

## Quick Tasks

| Quick Task | Status | Scope | Verification |
|------------|--------|-------|--------------|
| [Projected link rewriting](quick-tasks/2026-09-02-projected-link-rewriting.md) | done | demote unshipped links in projected references | 95/95 tests; gate passed; pair regenerated |
| [Manifest code provenance](quick-tasks/2026-09-03-manifest-code-provenance.md) | done | optional git_head/worktree_tree in MANIFEST + provenance command | 142/142 tests; validate exit 0 |

## Epics

| Epic | Status | Stories | Notes |
|------|--------|---------|-------|
| [Epic 1 Evidence substrate](epics/epic-1-evidence-substrate.md) | done | 3 | Layer, manifest validation, memo migration |
| [Epic 2 Note linkage](epics/epic-2-note-linkage.md) | done | 1 | `evidence:` frontmatter validation |
| [Epic 3 Impact ledger](epics/epic-3-impact-ledger.md) | done | 2 | Schema validation + generate appends |
| [Epic 4 Completion gate](epics/epic-4-completion-gate.md) | done | 1 | check-completion evidence_packs enforcement |
| [Epic 5 Distillation docs](epics/epic-5-distillation-docs.md) | done | 2 | Task 9 doc, retention flag, docs |
| [Epic 6 Mathdocs substrate](epics/epic-6-mathdocs-substrate.md) | done | 2 | Structure, registry, metadata, source hash |
| [Epic 7 Math execution](epics/epic-7-math-execution-verification.md) | done | 2 | Protocol verification and atomic update |
| [Epic 8 Math linkage gates](epics/epic-8-math-linkage-gates.md) | done | 2 | Note markers and implementation references |
| [Epic 9 Math workflow/release](epics/epic-9-math-workflow-release.md) | done | 2 | Task M, templates, reviewed dogfood, v4.0.0 distribution |

## Stories

| Story | Status | Epic | Notes |
|-------|--------|------|-------|
| [story-001 evidence tolerance](stories/story-001-evidence-tolerance.md) | done | 1 | Root-walk tolerance |
| [story-002 manifest validation](stories/story-002-manifest-validation.md) | done | 1 | MANIFEST schema |
| [story-003 migrate memos](stories/story-003-migrate-research-memos.md) | done | 1 | research/ → packs |
| [story-004 evidence frontmatter](stories/story-004-evidence-frontmatter.md) | done | 2 | Stable resolve, draft dangle |
| [story-005 ledger validation](stories/story-005-ledger-validation.md) | done | 3 | 6-field schema |
| [story-006 publication entries](stories/story-006-generate-publication-entries.md) | done | 3 | generate appends |
| [story-007 completion gate](stories/story-007-completion-gate.md) | done | 4 | evidence_packs enforcement |
| [story-008 Task 9 doc](stories/story-008-task9-distill-doc.md) | done | 5 | E.2 procedure, attribution |
| [story-009 docs + retention](stories/story-009-docs-retention.md) | done | 5 | Task docs, README, flag |
| [story-010 mathdocs registry](stories/story-010-mathdocs-structure-registry.md) | done | 6 | Structure, pairing, reserved index |
| [story-011 metadata/hash](stories/story-011-mathdocs-metadata-hash.md) | done | 6 | Source/environment currency |
| [story-012 check-math protocol](stories/story-012-check-math-protocol.md) | done | 7 | Deterministic execution and exact verification |
| [story-013 atomic update](stories/story-013-check-math-atomic-update.md) | done | 7 | Generated block + all-or-none publication |
| [story-014 equation markers](stories/story-014-equation-marker-validation.md) | done | 8 | Regular-note result/exposition validation |
| [story-015 implementation gate](stories/story-015-math-implementation-gate.md) | done | 8 | Source-root MathDoc traceability |
| [story-016 Task M](stories/story-016-task-math-note-workflow.md) | done | 9 | Procedures, templates, routing |
| [story-017 dogfood/release](stories/story-017-mathdocs-dogfood-release.md) | done | 9 | Real SymPy proof, review, gates, install, push |

## Completed or Archived

| Item | Completed | Notes |
|------|-----------|-------|
| [Route-Graph PRD](archive/2026-09-02-prd-route-graph.md) | 2026-09-02 (abandoned) | Direction abandoned by user before stories; superseded by WikiSkill adaptation PRD |
| [Route-Graph Architecture](archive/2026-09-02-architecture-route-graph.md) | 2026-09-02 (abandoned) | ADRs 0002-0006 never approved or implemented; retained for reference |
| [Experience Compilation (PRD + Architecture + 5 epics + 9 stories)](prd.md) | 2026-09-02 | Implemented, reviewed (self-review round 1, disclosed), 67/67 tests; first Skill Pair published; ledger live |
| [Math Derivation Layer (PRD + Architecture + 4 epics + 8 stories)](prd-math-derivation-layer.md) | 2026-09-05 | Implemented, independently reviewed, 205 tests; real SymPy dogfood; v4.0.0 pushed and installed |

## Maintenance Notes

- Update this index when creating or changing PRD, Architecture, Research, Quick Task, Epic, or Story files.
- Keep statuses aligned with the artifact frontmatter.
- Link durable knowledge through notes rather than storing it only in this index.
- Project Skill Pair published 2026-09-02 (first stable usage note: cli-projection-commands).
