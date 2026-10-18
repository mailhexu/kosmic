---
project_id: "kosmic"
subproject_id: "deterministic-flat-spec-migration"
record_kind: "architecture"
local_id: "architecture"
status: "approved"
created: "2026-10-11"
updated: "2026-10-11"
linked_prd: "prd.md"
linked_epics: ["epics/epic-001.md"]
---

# Deterministic Flat Spec Migration Architecture

## Contract

Implement the approved [PRD](prd.md) with offline Python 3.11+ standard-library commands. Reuse `kosmic_specs.migration_plan`, descriptor-safe file access, `_creation_lock`, `SpecCatalog.validate`, live shared Quick Task authorization, and existing STATUS rendering. No model invocation, prose-based owner inference, automatic approval, or adapter installation.

## AD-M01 — One planner, one executor

Keep `migrate-subprojects-plan` as the read-only entry point. Add `--output PATH` for saving its JSON without shell redirection; the explicit output is a bounded planning artifact and must not overwrite an existing file. Preserve stdout mode.

Add `migrate-subprojects-apply --project ROOT --plan PLAN --approve-digest SHA256 --work-record REF`. The digest acknowledges the exact reviewed plan; the work record supplies current Project-scoped authority. Both are mandatory. The apply command resolves the shared Quick Task using the existing flat bootstrap path rather than requiring the catalog it establishes. Accept only currently approved or in-progress shared Quick Tasks belonging to ROOT. Do not change task status.

Put transaction mechanics in `skills/scripts/kosmic_migration.py`; keep owner derivation and rewriting in the existing planner. The CLI handles argument parsing and delegates. Add `migrate-subprojects-recover --project ROOT --plan PLAN --approve-digest SHA256 --work-record REF` for interrupted application. Recovery is restricted to the exact pinned transaction; it is not general filesystem cleanup.

## AD-M02 — Complete, reproducible plan

Version the apply-capable plan schema explicitly. Save assignments and all inputs necessary to recompute the plan; include the complete legacy inventory, existing owner identities, ProjectEntry hash, active inbound-reference hashes, target preconditions, candidate output hashes and approved scope. The digest covers every field except itself.

At apply time, validate schema, canonical paths, approved digest and actual content hashes. Recompute candidate bytes with the same canonical planner and proposal fingerprint function, using saved assignments. Require the recomputed mapping and bytes to agree with the reviewed plan. Reject extra, missing, altered or newly introduced records and occupied targets before mutation. Reject traversal, external writes, symlink components, non-regular files and unsupported reference forms with an exact path and remedy. Do not accept arbitrary supplied document bytes merely because their digest matches.

Deterministic owner allocation uses declared ancestry and explicit assignments. Existing subprojects retain their identities and contents. Multiple architectures mapped onto the same owner are a collision, not permission to overwrite.

## AD-M03 — Live links and historical authority

Extend the existing rewrite pass rather than create a second mapper. Cover record frontmatter ancestry and dependency fields, Markdown links, reference-style links and images outside code fences, and Project/owner indexes. Inventory live inbound references in active specs, ProjectEntry, notes and existing subproject entries/specs; rewrite only their path-bearing fields and links. Leave unrelated bytes unchanged. An unsupported live reference blocks application rather than silently breaking it.

Logs and evidence payloads remain byte-identical historical artifacts. Preserve existing lifecycle statuses, approval decisions and review evidence. Emit old-to-new paths and qualified identities in the migration receipt. Do not rewrite old acceptance or review payloads to make them validate for a new identity. Without a compatible current completion receipt, migrated terminal work stays pending under the existing completion rules; the migration receipt is not a completion receipt.

Shared tasks/proposals remain under Project `specs/`. Preserve already valid canonical local IDs; only legacy records lacking identity metadata receive deterministic canonical metadata. Preserve proposal decisions and record old/new fingerprints; non-mechanical changes require explicit review and must not inherit fingerprint-bound approval silently.

## AD-M04 — Staging and validation

Use a managed run for disposable candidate data. Stage the minimum complete validation view: ProjectEntry, shared specs, existing and new owner entries/specs, and referenced metadata needed by catalog validation. Retain original Project-relative reference semantics. Do not copy unrelated repositories, installed skills or large evidence payloads.

Generate every candidate output before authoritative mutation. Run `SpecCatalog.validate` against the staged view and verify live links against the candidate path inventory. Build owner indexes and a Project navigation index from the candidate catalog. Render bound STATUS using the same catalog and existing renderer, ensuring links use final Project paths rather than staging paths. An unbound STATUS is an explicit report, not a new binding.

## AD-M05 — Recoverable per-path cutover

Hold the existing Project creation lock across final preflight, application and receipt publication. Retain the Project root and `.kosmic` inode: replacing the entire Project would detach the held lock and could discard unrelated concurrent work. Do not use `publish_tree` as though its managed-path mode supported deletions or complete crash recovery; its current contract requires every managed staged path to exist and its recovery interface is whole-tree-only.

Persist a bounded transaction under `.kosmic/migrations/{DIGEST}/`. Before the first mutation, store the immutable plan, affected-path before bytes and hashes, candidate bytes and hashes, and an ordered operation manifest. Record each operation's intent durably before mutation, then its result. Use descriptor-safe atomic writes, checked deletion of obsolete feature files, and directory fsync. Before replacing or deleting a path, verify its expected current state. Never replace unrelated directory trees.

Ordinary exceptions restore all affected paths to their before state in reverse order, but only when current bytes match a recorded transaction state. Concurrent external changes are conflicts and must not be overwritten during rollback. Interrupted application leaves the transaction available to the explicit recovery command, which reconciles hashes and rolls back an incomplete transaction. A complete validated output set without its final receipt may be verified and finalized. Receipt publication is last.

The operation manifest includes a bound external STATUS target when present. Validate that target through the existing binding contract and back it up alongside Project outputs. Project locking excludes supported creation/migration writers; raw editors remain a compliance boundary, not claimed filesystem isolation. A second transaction refuses to start while an incomplete migration exists.

## AD-M06 — Receipt and idempotence

A successful migration receipt records schema, Project identity, approved plan digest, work-record identity, mapping, input/output hashes, proposal recheck requirements and STATUS disposition. Retain the pinned before images for explicit rollback/recovery provenance; do not delete them as disposable scratch.

Repeating apply with the same plan checks its existing receipt and final managed output hashes before attempting source-inventory validation, because old sources no longer exist. Return the verified existing result without new writes. If outputs have changed since completion, report drift rather than reapply or undo later work. Never create duplicate owners or receipts.

## Failure Contract

Typed errors distinguish approval/authority failure, ambiguity, plan mismatch, input drift, target collision, unsafe path, invalid candidate, transaction conflict, interrupted transaction and completed-output drift. Failures name the affected path and the next safe action. No catch-and-continue migration, warning suppression or fallback approval.

## Verification

Exercise actual plan/apply/recover CLI calls on temporary multi-feature Projects. Prove local and cross-owner dependencies, shared tasks, existing canonical local IDs, live inbound links, immutable history, receipt-aware terminal status and bound/unbound STATUS. Compare candidate/output bytes and resolve intended record identities through the real catalog.

Regression tests cover ambiguity, inventory drift, tampering, collisions, symlink/traversal attempts, no approval, lost authority, publication failure rollback, process interruption at intent/publication boundaries, external edits during recovery and repeated completed application. Run the existing bounded suite after integration. Tests must assert consumer-visible state, not source-text wiring.

## Requirement Coverage

| PRD requirements | Decisions |
|---|---|
| FR-M01–M03 | AD-M01, AD-M02 |
| FR-M04 | AD-M02, AD-M05 |
| FR-M05–M06 | AD-M03, AD-M04 |
| FR-M07 | AD-M04, AD-M05 |
| FR-M08 | AD-M05, AD-M06 |
| FR-M09 | AD-M03, AD-M04, AD-M06 |

## Approval Boundary

The user approved this Architecture on 2026-10-11. The epic breakdown and implementation stories retain their required approval gates. No live Project migration is approved by this decision. No source implementation changes or live moves occur in this planning step.
