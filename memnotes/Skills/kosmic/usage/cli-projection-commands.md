---
type: Domain Topic
id: kosmic/usage/cli-projection-commands
domain: kosmic
audience: usage
status: stable
summary: Projection CLI experience commands
triggers: [Projection CLI experience commands]
aliases: []
evidence: [evidence/2026-09-02-experience-compilation-impl/session-record.md, evidence/2026-09-05-math-derivation-layer-impl/session-record.md, evidence/2026-09-06-skill-proposal-loop-impl/session-record.md]
source_project: kosmic
source_sha256: 457c086686948f175a7cf2ab385325a76cb7719944cc1c747ae7534e879a0823
artifact_role: guideline
requires_procedures: []
governed_by: []
uses_knowledge: []
supported_by: []
supersedes: []
source: notes/cli-projection-commands.md
---

# Projection CLI experience commands

## Overview
How the Projection CLI treats executable MathDocs, Skill Proposals, projections, installation, derived STATUS, and record-embedded completion. Structural commands are deterministic, offline, and stdlib-only; `check-math` executes trusted Project Python and therefore requires the Project derivation environment. The command reference `skills/references/cli-projection-commands.md` owns flags and step-by-step procedures; this note carries the durable invariants.

## Principles
- Projected references are package-consistent: a link whose target is outside the rendering package (drafts, other-audience notes) is demoted to bold plain text and `generate` warns on stderr naming each demoted link; code fences, external URLs, and non-Markdown targets are untouched.
- Notes carry no `evidence:` gate: a stable note is never rejected for missing or unresolved evidence paths, and legacy `evidence:` frontmatter values remain valid historical metadata that current commands neither require nor bless (knowledge-first notes, `docs/adr/0004-knowledge-first-notes.md`). Reproducibility uses plain `sources:` links in the note body.
- Completion is record-embedded: criterion observations, the independent two-axis review, and scope claims live in the work record; `work finish` publishes a receipt bound to the completed record's bytes. There is no `impact.md` ledger and no `evidence_packs:` frontmatter — legacy packs and ledger entries stay untouched historical bytes.
- Every Project has a vault-only `mathdocs/` registry: stable Math Derivations carry the current script SHA-256, Python/SymPy versions, verification time, host, and source directory; stable regular notes mark each display equation with a resolvable `MathDoc` result or exposition identifier.
- Task P proposal artifacts use `draft -> approved -> done` status and `pending -> accepted|rejected` decisions; `validate-proposal` enforces the SHA-pinned curated input manifest, scope/independence policy, immutable fingerprints, behavioral evidence, and project-relative candidate isolation, and `check-completion` enforces the proposal gate before its Consumer Interface early return.

## Details
- `validate` checks notes, MathDocs, proposals, and projections; retired pack and ledger inputs are neither required nor audited, and legacy pack/ledger bytes stay untouched.
- `check-math` runs active derivations in lexical order with a bounded timeout, comparing their versioned JSON protocol, environment, source hash, and named results against the paired notes; execution is trusted, not sandboxed. `check-math --update --source-root` publishes the complete `mathdocs/` tree or nothing; dependents update from the published canonical results before rerunning `validate` and completion.
- Math-derived work items declare `derivations` plus a finite `math_implementation_files` list; `check-completion --source-root` requires each listed file to stay under that root and carry an adjacent `MathDoc: project/slug[#result]` identifier.
- Completion is record-local: `related_notes`, the record's `derivations`, and those notes' declared derivations form the checked closure; unrelated legacy defects do not block it, while declared missing, malformed, deprecated, or stale dependencies do. Identity, ancestry, acceptance, review, containment, and receipt gates are unchanged, and non-mathematical records need no unrelated mathdocs registry.
- Consumer completion checks whole Skill Pair integrity and the current source or routed reference for each declared Consumer note; `validate`, projection generation, and unscoped `check-math` remain strict global audits.
- `check-installation` byte-compares both named-adapter packages and Project identity against the canonical pair; success proves on-disk installation only — reload the adapter and inspect its skill inventory before claiming active-session discovery.

### Existing library role recovery
`migrate-library` accepts the existing `kosmic.semantic-role-classification/v1` map for in-place legacy Topic metadata recovery: each source names its unchanged library-relative identity, an explicit role, and typed relationships, and an optional `source_project` pin must match existing provenance. Unclassified legacy dependencies and symlink sources or generated outputs are rejected; recovery preserves body bytes, validates the staged library, and publishes atomically. It cannot turn an incomplete paragraph into a valid procedure — a separately approved and reviewed content proposal must supply that repair.

## Flat-spec migration
`migrate-subprojects-plan` saves an exclusive, hash-pinned JSON plan deriving feature owners from declared ancestry and explicit assignments; it never approves work or moves records. `migrate-subprojects-apply` requires the exact reviewed plan digest and a currently approved or in_progress Quick Task in that Project, recomputes the plan, rejects drift and occupied or unsafe targets, validates a staged catalog, and publishes checked per-path changes with durable before images; `migrate-subprojects-recover` reconciles an interrupted transaction, and unknown external edits are conflicts, not permission to overwrite. Application requires a Git worktree with its managed `.tmp/` scratch root ignored; migration execution and adapter installation retain separate approvals, and a migration receipt is not a work-completion receipt.

Planning audits every authoritative Markdown file, including root documents, specs, notes, and MathDocs. Proposal input manifests and curated snapshots under `specs/skill-proposals/inputs/` are protected evidence — pinned, audited, never rewritten; evidence, logs, and generated skills are likewise pinned and never rewritten. A broken reference is repaired only when its filename or stem has exactly one authoritative target; ambiguous matches block application, and `link_corrections` and `link_problems` record every outcome. Frontmatter parsing supports nested mappings and sequences, flow collections, and literal/folded block scalars without third-party YAML; duplicate keys, anchors, aliases, merge keys, complex keys, and tab indentation are rejected. For `linked_*` metadata a document-relative destination takes precedence over a Project-root namesake, so an existing owner's link keeps resolving when a root-level namesake is also migrated; staged catalog validation verifies owner ancestry before publication even when the plan reports no ownership ambiguity.

## Derived STATUS authority
`generate-status --work-record REF` regenerates the derived `STATUS.md` in the Project's bound status root; the only written path is that STATUS file — records, receipts, and sources are never written, and hand edits are regenerated over. Implementation records keep their exact legacy grants: an approved or in_progress story or quick-task authorizes the refresh unchanged, including project-level quick-task authority against a fixed-subproject bound directory. Bounded planning records additionally authorize this one derived refresh: an approved PRD or Architecture, or a draft PRD, Architecture, Epic, or Story whose own hierarchy governs the bound output path — with a Project-wide status root, or a registered directory fixed to the record's own subproject; a draft story additionally requires its approved ancestry. Everything else is refused `WORK_PHASE_DENIED` and nothing is written. A draft never narrows the Project-wide rendered view, planning grants no source mutation or `work finish` capability, and the status-root binding is never created, replaced, or dropped by a refresh.

## Optional knowledge curation
An optional three-stage curation routine — `curation-prepare` (deterministic selection) → agent semantic review recorded in the governing work record → `curation-finalize` (deterministic verification) — nominates skill-material candidates between manual or externally scheduled runs. Prepare freezes the cutoff `U` at run start, takes the first lower bound explicitly (`--from <exact-UTC>` or `--baseline`), and selects notes with `L < changed_at <= U` by semantic `updated` (created fallback); the reserved `index.md` is never selected. The persisted per-scope checkpoint advances to exactly `U` only after a full-scope successful finalize; subset runs and failures never advance it. Review is agent work, not CLI: nominations follow the existing proposal/review records, and the routine never auto-approves, publishes, installs, or schedules anything. Interface and details: `skills/references/curation_routine.md`.

## Linked Concepts
- [Projection audience routing](../development/projection-audience-routing.md): how validated notes project into the Skill Pair.
- [Projection CLI extension conventions](../development/cli-extension-conventions.md): contributor-side conventions for extending this CLI.
- [Notation](notation.md): standard symbols.
