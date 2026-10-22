---
project: kosmic
created: 2026-09-02
updated: 2026-10-22
---

# Specs Index: kosmic

This index is navigational only. It does not replace PRD, Architecture, Story, Quick Task, or code review gates.

## Overview

- PRD: [PRD](../subprojects/experience-compilation-adapting-wikiskill-into-kosmic/specs/prd.md) (approved 2026-09-02)
- Architecture: [Architecture](../subprojects/experience-compilation-adapting-wikiskill-into-kosmic/specs/architecture.md) (approved 2026-09-02)
- Current focus: vault-level Shared Domain Skill Library with one native router, dynamically loaded domain `SKILL.md` files, and cross-project learning

## Active Specs

| Type | Link | Status | Notes |
|------|------|--------|-------|
| PRD | [PRD](../subprojects/experience-compilation-adapting-wikiskill-into-kosmic/specs/prd.md) | approved | Experience Compilation: single evidence layer, Task 9 distillation, impact ledger, completion gate |
| Architecture | [Architecture](../subprojects/experience-compilation-adapting-wikiskill-into-kosmic/specs/architecture.md) | approved | Evidence layer, Task 9 distillation, impact ledger, completion gate — grounded in ADRs 0002-0003 |
| Feature PRD | [Math Derivation Layer](../subprojects/prd-math-derivation-layer-mathdocs/specs/prd.md) | approved 2026-09-05 | Seven Task 7 findings resolved; ready for Architecture |
| Feature Architecture | [Math Derivation Layer](../subprojects/prd-math-derivation-layer-mathdocs/specs/architecture.md) | approved 2026-09-05 | AD-M1..M8: registry, protocol, markers, atomic updates, validation, completion linkage |
| Feature PRD | [Skill Proposal Loop](../subprojects/skill-proposal-loop/specs/prd.md) | approved 2026-09-06 | Task P, fresh-context proposer policy, behavioral gate, activation diagnostics |
| Feature Architecture | [Skill Proposal Loop](../subprojects/skill-proposal-loop/specs/architecture.md) | approved 2026-09-06 | AD-P1..P8: proposer role, artifact, gates, behavior, rejection memory, activation |
| Feature PRD | [Shared Domain Skill Library](../subprojects/shared-domain-skill-library/specs/prd.md) | approved 2026-09-06 | One library router; domain-root subskills; ordinary topic notes; cross-domain resolution and Maintainer governance |
| Feature Architecture | [Shared Domain Skill Library](../subprojects/shared-domain-skill-library/specs/architecture.md) | approved 2026-09-06 | AD-SD1..SD10: domain-root fracture, deterministic resolver, bounded cross-domain packets, governed migration |
| Feature PRD | [Deterministic Flat Spec Migration](../subprojects/deterministic-flat-spec-migration/specs/prd.md) | approved 2026-10-11 | Reuse the existing planner and add a safe, approved-plan executor so migration needs no agent for mechanical changes. |
| Feature Architecture | [Deterministic Flat Spec Migration](../subprojects/deterministic-flat-spec-migration/specs/architecture.md) | approved 2026-10-11 | Define pinned-plan validation, staged catalog checks, recoverable per-path cutover and idempotent receipts without changing work authority. |
| Feature Epic | [Script-driven flat-spec migration](../subprojects/deterministic-flat-spec-migration/specs/epics/epic-001.md) | approved 2026-10-11 | All three Stories have checked completion receipts; separately approved live migration applied successfully. |
| Feature PRD | [Migration-compatible Skill Proposal validation](../subprojects/migration-compatible-skill-proposal-validation/specs/prd.md) | approved 2026-10-12 | Preserve immutable proposal inputs while validating historical paths and no-action null fields after record migration. Architecture is the next gate. |
| Feature PRD | [Knowledge-first notes and evidence retirement](../subprojects/knowledge-first-notes-and-evidence-retirement/specs/prd.md) | approved 2026-10-17 | Locality, skill-resource metadata and timestamp-bounded curation requirements accepted. |
| Feature Architecture | [Knowledge-first notes and evidence retirement](../subprojects/knowledge-first-notes-and-evidence-retirement/specs/architecture.md) | approved 2026-10-17 | Note lifecycle, compact completion and incremental curation design accepted. |
| Feature Epic | [Knowledge-first workflow and incremental skill curation](../subprojects/knowledge-first-notes-and-evidence-retirement/specs/epics/epic-001.md) | approved 2026-10-18 | Five Story records drafted; individual Story approval required before implementation. |
| Feature Stories | [Knowledge-first workflow: five Story drafts](../subprojects/knowledge-first-notes-and-evidence-retirement/specs/INDEX.md#draft-stories) | draft | STATUS authorization; notes/metadata; completion/receipts; incremental curation; coherent consumer cutover. |
| Feature PRD | [Review convergence and optional historical validation](../subprojects/review-convergence-and-optional-historical-validation/specs/prd.md) | approved 2026-10-21 | Worker-response barrier, complete bounded re-review handoff, and optional inspectable historical-integrity policy. |
| Feature Architecture | [Review convergence and optional historical validation](../subprojects/review-convergence-and-optional-historical-validation/specs/architecture.md) | approved 2026-10-21 | Accepted exact-path history inspection/audit seam and coordinator-ledger review barrier; four Story drafts await approval. |
| Feature Epic | [Optional historical validation](../subprojects/review-convergence-and-optional-historical-validation/specs/epics/epic-001.md) | approved 2026-10-22 | Two Story drafts; scoped historical reporting/audit with strict active integrity. |
| Feature Epic | [Complete review handoffs](../subprojects/review-convergence-and-optional-historical-validation/specs/epics/epic-002.md) | approved 2026-10-22 | Two Story drafts; compatible finding annotations and bounded coordinator handoffs. |
| Feature Stories | [Review convergence and historical validation: four Story drafts](../subprojects/review-convergence-and-optional-historical-validation/specs/INDEX.md#draft-stories) | draft | History/reporting → read-only audit; finding annotations → coordinator handoff. Individual Story approval required. |

## Research Memos

| Research | Status | Linked PRD | Linked Architecture | Recommendation |
|----------|--------|------------|---------------------|----------------|
| [2026-09-02 route-graph skill projection](../evidence/2026-09-02-route-graph-skill-projection/memo.md) | done | [Archived PRD](archive/2026-09-02-prd-route-graph.md) | [Archived Architecture](archive/2026-09-02-architecture-route-graph.md) | Option B: keep pair, shared route graph — direction abandoned by user |
| [2026-09-02 WikiSkill experience compilation](../evidence/2026-09-02-wikiskill-experience-compilation/memo.md) | done | [PRD](../subprojects/experience-compilation-adapting-wikiskill-into-kosmic/specs/prd.md) | [Architecture](../subprojects/experience-compilation-adapting-wikiskill-into-kosmic/specs/architecture.md) | Posture B staged: adapt WikiSkill engine writing into Kosmic substrate |

## Quick Tasks

| Quick Task | Status | Scope | Verification |
|------------|--------|-------|--------------|
| [Projected link rewriting](quick-tasks/2026-09-02-projected-link-rewriting.md) | done | demote unshipped links in projected references | 95/95 tests; gate passed; pair regenerated |
| [Manifest code provenance](quick-tasks/2026-09-03-manifest-code-provenance.md) | done | optional git_head/worktree_tree in MANIFEST + provenance command | 142/142 tests; validate exit 0 |
| [Plan flat-spec migration bootstrap](quick-tasks/plan-flat-spec-migration-bootstrap.md) | draft | Inventory legacy feature records and prepare an owner-aware migration plan without moving or approving them. | Awaiting explicit approval for planning; migration execution needs a separate gate. |
| [Malformed completion-review refusal](quick-tasks/repair-malformed-completion-review-gate-precedence.md) | done | preserve proof/scope/review refusal order for malformed review metadata | Red-before/green-after CLI regression; 28 focused tests; both independent review axes approved |
| [Executable CLI and observable verification](quick-tasks/restore-cli-executable-release-and-observable-verification-guida.md) | done | restore committed executable mode and remove the permanent-test-per-criterion mandate | Actual direct/Python help and policy handoff exercised; both independent review axes approved |
| [Publish release and install OMP](quick-tasks/publish-reviewed-kosmic-release-and-install-omp-orchestrator.md) | done | fast-forward origin/main and install the exact reviewed kosmic package into OMP | Remote release SHA observed; 64-file hash/mode match; installed CLI smoke passed |

## Epics

| Epic | Status | Stories | Notes |
|------|--------|---------|-------|
| [Epic 1 Evidence substrate](../subprojects/experience-compilation-adapting-wikiskill-into-kosmic/specs/epics/epic-001-evidence-substrate.md) | done | 3 | Layer, manifest validation, memo migration |
| [Epic 2 Note linkage](../subprojects/experience-compilation-adapting-wikiskill-into-kosmic/specs/epics/epic-002-note-linkage.md) | done | 1 | `evidence:` frontmatter validation |
| [Epic 3 Impact ledger](../subprojects/experience-compilation-adapting-wikiskill-into-kosmic/specs/epics/epic-003-impact-ledger.md) | done | 2 | Schema validation + generate appends |
| [Epic 4 Completion gate](../subprojects/experience-compilation-adapting-wikiskill-into-kosmic/specs/epics/epic-004-completion-gate.md) | done | 1 | check-completion evidence_packs enforcement |
| [Epic 5 Distillation docs](../subprojects/experience-compilation-adapting-wikiskill-into-kosmic/specs/epics/epic-005-distillation-docs.md) | done | 2 | Task 9 doc, retention flag, docs |
| [Epic 6 Mathdocs substrate](../subprojects/prd-math-derivation-layer-mathdocs/specs/epics/epic-001-mathdocs-substrate.md) | done | 2 | Structure, registry, metadata, source hash |
| [Epic 7 Math execution](../subprojects/prd-math-derivation-layer-mathdocs/specs/epics/epic-002-math-execution-verification.md) | done | 2 | Protocol verification and atomic update |
| [Epic 8 Math linkage gates](../subprojects/prd-math-derivation-layer-mathdocs/specs/epics/epic-003-math-linkage-gates.md) | done | 2 | Note markers and implementation references |
| [Epic 9 Math workflow/release](../subprojects/prd-math-derivation-layer-mathdocs/specs/epics/epic-004-math-workflow-release.md) | done | 2 | Task M, templates, reviewed dogfood, v4.0.0 distribution |
| [Epic 10 Proposer contract](../subprojects/skill-proposal-loop/specs/epics/epic-001-proposer-contract.md) | done | 2 | Task P, artifact template, deterministic validation |
| [Epic 11 Proposal governance](../subprojects/skill-proposal-loop/specs/epics/epic-002-proposal-governance.md) | done | 2 | Completion gate, lifecycle, fingerprints, rejection memory |
| [Epic 12 Proposal behavior](../subprojects/skill-proposal-loop/specs/epics/epic-003-proposal-behavior.md) | done | 1 | Baseline/candidate evidence and review |
| [Epic 13 Activation/release](../subprojects/skill-proposal-loop/specs/epics/epic-004-proposal-activation-release.md) | done | 2 | Installation diagnostics, dogfood, distribution |
| [Epic 14 Shared library foundation](../subprojects/shared-domain-skill-library/specs/epics/epic-001-shared-library-foundation.md) | draft | 2 | Domain/topic schemas, catalog, deterministic resolver |
| [Epic 15 Shared library governance](../subprojects/shared-domain-skill-library/specs/epics/epic-002-shared-library-governance.md) | draft | 2 | Cross-project evidence, domain ownership, single-router install |
| [Epic 16 Shared library migration/release](../subprojects/shared-domain-skill-library/specs/epics/epic-003-shared-library-migration-release.md) | draft | 2 | Explicit migration, cross-domain dogfood, clean cutover |

## Stories

| Story | Status | Epic | Notes |
|-------|--------|------|-------|
| [story-001 evidence tolerance](../subprojects/experience-compilation-adapting-wikiskill-into-kosmic/specs/stories/story-001-evidence-tolerance.md) | done | 1 | Root-walk tolerance |
| [story-002 manifest validation](../subprojects/experience-compilation-adapting-wikiskill-into-kosmic/specs/stories/story-002-manifest-validation.md) | done | 1 | MANIFEST schema |
| [story-003 migrate memos](../subprojects/experience-compilation-adapting-wikiskill-into-kosmic/specs/stories/story-003-migrate-research-memos.md) | done | 1 | research/ → packs |
| [story-004 evidence frontmatter](../subprojects/experience-compilation-adapting-wikiskill-into-kosmic/specs/stories/story-004-evidence-frontmatter.md) | done | 2 | Stable resolve, draft dangle |
| [story-005 ledger validation](../subprojects/experience-compilation-adapting-wikiskill-into-kosmic/specs/stories/story-005-ledger-validation.md) | done | 3 | 6-field schema |
| [story-006 publication entries](../subprojects/experience-compilation-adapting-wikiskill-into-kosmic/specs/stories/story-006-generate-publication-entries.md) | done | 3 | generate appends |
| [story-007 completion gate](../subprojects/experience-compilation-adapting-wikiskill-into-kosmic/specs/stories/story-007-completion-gate.md) | done | 4 | evidence_packs enforcement |
| [story-008 Task 9 doc](../subprojects/experience-compilation-adapting-wikiskill-into-kosmic/specs/stories/story-008-task9-distill-doc.md) | done | 5 | E.2 procedure, attribution |
| [story-009 docs + retention](../subprojects/experience-compilation-adapting-wikiskill-into-kosmic/specs/stories/story-009-docs-retention.md) | done | 5 | Task docs, README, flag |
| [story-010 mathdocs registry](../subprojects/prd-math-derivation-layer-mathdocs/specs/stories/story-001-mathdocs-structure-registry.md) | done | 6 | Structure, pairing, reserved index |
| [story-011 metadata/hash](../subprojects/prd-math-derivation-layer-mathdocs/specs/stories/story-002-mathdocs-metadata-hash.md) | done | 6 | Source/environment currency |
| [story-012 check-math protocol](../subprojects/prd-math-derivation-layer-mathdocs/specs/stories/story-003-check-math-protocol.md) | done | 7 | Deterministic execution and exact verification |
| [story-013 atomic update](../subprojects/prd-math-derivation-layer-mathdocs/specs/stories/story-004-check-math-atomic-update.md) | done | 7 | Generated block + all-or-none publication |
| [story-014 equation markers](../subprojects/prd-math-derivation-layer-mathdocs/specs/stories/story-005-equation-marker-validation.md) | done | 8 | Regular-note result/exposition validation |
| [story-015 implementation gate](../subprojects/prd-math-derivation-layer-mathdocs/specs/stories/story-006-math-implementation-gate.md) | done | 8 | Source-root MathDoc traceability |
| [story-016 Task M](../subprojects/prd-math-derivation-layer-mathdocs/specs/stories/story-007-task-math-note-workflow.md) | done | 9 | Procedures, templates, routing |
| [story-017 dogfood/release](../subprojects/prd-math-derivation-layer-mathdocs/specs/stories/story-008-mathdocs-dogfood-release.md) | done | 9 | Real SymPy proof, review, gates, install, push |
| [story-018 Task P](../subprojects/skill-proposal-loop/specs/stories/story-001-task-p-procedure.md) | done | 10 | Fresh-context procedure and template |
| [story-019 proposal validation](../subprojects/skill-proposal-loop/specs/stories/story-002-proposal-validation.md) | done | 10 | Deep SkillProposal loader and CLI |
| [story-020 proposal completion](../subprojects/skill-proposal-loop/specs/stories/story-003-proposal-completion-gate.md) | done | 11 | Additive work-item gate |
| [story-021 rejection memory](../subprojects/skill-proposal-loop/specs/stories/story-004-rejection-memory.md) | done | 11 | Fingerprint, reconsideration, ledger |
| [story-022 behavioral gate](../subprojects/skill-proposal-loop/specs/stories/story-005-proposal-behavioral-gate.md) | done | 12 | Isolated baseline/candidate evidence |
| [story-023 activation diagnostics](../subprojects/skill-proposal-loop/specs/stories/story-006-installation-activation-diagnostics.md) | done | 13 | Descriptions, installed bytes, honest discovery |
| [story-024 dogfood/release](../subprojects/skill-proposal-loop/specs/stories/story-007-proposer-dogfood-release.md) | done | 13 | Real proposal, review, release |
| [story-025 library schema/catalog](../subprojects/shared-domain-skill-library/specs/stories/story-001-library-schema-catalog.md) | done | 14 | Authoritative documents, generated indexes, dependency validation |
| [story-026 deterministic resolver](../subprojects/shared-domain-skill-library/specs/stories/story-002-deterministic-library-resolver.md) | done | 14 | Route/query plans, closure, budgets, verified load |
| [story-027 cross-project governance](../subprojects/shared-domain-skill-library/specs/stories/story-003-cross-project-domain-governance.md) | done | 15 | Source evidence, target-domain Maintainer approval |
| [story-028 shared router install](../subprojects/shared-domain-skill-library/specs/stories/story-004-shared-router-installation.md) | done | 15 | One native router, adapter cutover and rollback |
| [story-029 shared library migration](../subprojects/shared-domain-skill-library/specs/stories/story-005-shared-library-migration.md) | done | 16 | Explicit assignments, provenance preservation, atomic publication |
| [story-030 dogfood/release](../subprojects/shared-domain-skill-library/specs/stories/story-006-shared-library-dogfood-release.md) | done | 16 | Kosmic and TB2J→ABINIT behavior, review, release |

## Completed or Archived

| Item | Completed | Notes |
|------|-----------|-------|
| [Route-Graph PRD](archive/2026-09-02-prd-route-graph.md) | 2026-09-02 (abandoned) | Direction abandoned by user before stories; superseded by WikiSkill adaptation PRD |
| [Route-Graph Architecture](archive/2026-09-02-architecture-route-graph.md) | 2026-09-02 (abandoned) | ADRs 0002-0006 never approved or implemented; retained for reference |
| [Experience Compilation (PRD + Architecture + 5 epics + 9 stories)](../subprojects/experience-compilation-adapting-wikiskill-into-kosmic/specs/prd.md) | 2026-09-02 | Implemented, reviewed (self-review round 1, disclosed), 67/67 tests; first Skill Pair published; ledger live |
| [Math Derivation Layer (PRD + Architecture + 4 epics + 8 stories)](../subprojects/prd-math-derivation-layer-mathdocs/specs/prd.md) | 2026-09-05 | Implemented, independently reviewed, 205 tests; real SymPy dogfood; v4.0.0 pushed and installed |
| [Shared Domain Skill Library (PRD + Architecture + 3 epics + 6 stories)](../subprojects/shared-domain-skill-library/specs/prd.md) | 2026-09-06 | Implemented, independently reviewed, 283 tests; explicit Kosmic migration; four-adapter `memnotes-skills` install verified |

## Maintenance Notes

- Update this index when creating or changing PRD, Architecture, Research, Quick Task, Epic, or Story files.
- Keep statuses aligned with the artifact frontmatter.
- Link durable knowledge through notes rather than storing it only in this index.
- Project Skill Pair published 2026-09-02 (first stable usage note: cli-projection-commands).
<!-- kosmic:migration-owners:start -->

## Migrated Subprojects

- [Dream Reflection](../subprojects/dream-reflection/specs/INDEX.md) — approved
- [Experience Compilation: adapting WikiSkill into Kosmic](../subprojects/experience-compilation-adapting-wikiskill-into-kosmic/specs/INDEX.md) — approved
- [Feature PRD: Managed Run Workspaces](../subprojects/feature-prd-managed-run-workspaces/specs/INDEX.md) — approved
- [Feature PRD: Procedure Compilation and Routine Reuse](../subprojects/feature-prd-procedure-compilation-and-routine-reuse/specs/INDEX.md) — approved
- [PRD: Math Derivation Layer (mathdocs)](../subprojects/prd-math-derivation-layer-mathdocs/specs/INDEX.md) — approved
- [Project Status File](../subprojects/project-status-file/specs/INDEX.md) — approved
- [Semantic Artifact Roles](../subprojects/semantic-artifact-roles/specs/INDEX.md) — approved
- [Shared Domain Skill Library](../subprojects/shared-domain-skill-library/specs/INDEX.md) — approved
- [Skill Proposal Loop](../subprojects/skill-proposal-loop/specs/INDEX.md) — approved
<!-- kosmic:migration-owners:end -->
