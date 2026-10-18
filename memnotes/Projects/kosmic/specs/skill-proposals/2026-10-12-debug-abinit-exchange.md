---
project_id: kosmic
subproject_id: null
record_kind: proposal
local_id: debug-abinit-exchange
status: done
created: 2026-10-12
updated: 2026-10-13
result: update
scope: shared-procedure
artifact_role: procedure
target: tb2j/development/debug-abinit-exchange
target_ref: library-skill://tb2j/development/debug-abinit-exchange
target_sha256: 4f3c942063cce6e4d8e9e0eed218cfc09d636df75ea119b9139b6a94b47af72f
proposer_mode: subagent
proposer_ref: agent://ProcedureRepairProposal
proposer_reason: Fresh-context shared-procedure proposer.
input_manifest: [specs/skill-proposals/inputs/2026-10-12-debug-abinit-exchange.md]
related_notes: []
evidence_packs: [2026-10-13-debug-abinit-procedure]
behavioral_evidence: [evidence/2026-10-13-debug-abinit-procedure/behavior.json]
decision: accepted
approved_by: hexu
fingerprint: d181ddf6c4b8e7f024fd496c988072b265a063ba46f8f98c60b9c0f80ffaac4a
reconsiders: ""
approval_note: Owner approved the exact candidate hash with "OK. next" on 2026-10-13.
---

# Repair existing ABINIT exchange diagnostic procedure

## Problem

The approved procedure classification cannot validate its legacy single-paragraph source: outcome and required sections are missing, and two ABINIT guideline dependencies still use obsolete requires.

## Evidence

Real ten-topic recovery smoke rejected unclassified dependencies. No TB2J scientific calculation was run for this formatting/relationship repair.

## Proposed Change

Use [the exact candidate](candidates/2026-10-12-debug-abinit-exchange.md), SHA-256 `3615d248a82f34eeb5f033c4ce561e2edc6963658dd61e245df8be842a79d0d2`. Declare both existing ABINIT guidelines in governed_by, add truthful outcome and required sections, preserve Topic ID, native provenance and original diagnostic paragraph.

## Applicability

Existing ABINIT-to-TB2J boundary diagnosis only. Mechanics: judgment. Routine action: keep_as_prose; no deterministic routine creation.

## Behavioral Validation

Candidate paths: [specs/skill-proposals/candidates/2026-10-12-debug-abinit-exchange.md]

Baseline fails strict typed-role validation. Candidate must validate with other nine approved classifications; do-resolution must include both guidelines. This retrieval check does not certify scientific exchange correctness. Publication waits for exact candidate approval and independent review.

## Risks

Do not weaken validators or erase prerequisites. No installed skill edits; original failing calculation remains usable when no reduced reproducer is available.
