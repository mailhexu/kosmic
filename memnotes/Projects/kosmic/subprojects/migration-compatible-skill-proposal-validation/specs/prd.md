---
project_id: "kosmic"
subproject_id: "migration-compatible-skill-proposal-validation"
status: "approved"
record_kind: "prd"
local_id: "prd"
created: "2026-10-12"
updated: "2026-10-12"
linked_research: []
linked_epics: []
---
# Migration-compatible Skill Proposal validation

## Problem Statement

After the approved flat-spec migration, the canonical Project catalog and all three migration Stories validate, but whole-Project `validate` reports failures in four historical Skill Proposals. One no-action proposal encodes empty target fields as YAML null and is rejected as the string `"None"`. One accepted proposal's immutable input manifest still identifies a feature Story by its former flat path, now owned at a new canonical path. Two older proposals pin a `notes/index.md` version whose current bytes differ.

The validator must distinguish a faithfully preserved historical input from an unresolved or altered source without rewriting curated manifests, silently refreshing hashes, or transferring an old proposal decision to a changed fingerprint. Otherwise a completed, receipt-backed migration can leave project-wide validation unusable, while aggressive repair would destroy the provenance that makes proposals auditable.

## Goals

- Make proposal validation represent the documented no-action empty-target contract consistently for YAML empty strings and null values.
- Preserve immutable proposal input manifests and curated snapshots byte-for-byte across record migrations.
- Define how historical proposal inputs that move through an approved migration are verified using authenticated migration provenance, without guessing path replacements.
- Keep genuine unreceipted source drift and changed proposal fingerprints visible; never infer approval for changed intervention content.
- Produce deterministic diagnostics that identify the proposal, manifest, input path and verified disposition.

## Non-Goals

- Rewriting, regenerating or approving existing proposal manifests or proposal decisions automatically.
- Relaxing SHA-256 checks for ordinary proposal inputs or ignoring stale input hashes without authenticated provenance.
- Changing Task P scope, proposer independence, behavioral evidence, Impact Ledger semantics or shared-skill publication gates.
- Re-running or rewriting the completed flat-spec migration.
- Editing curated snapshots, logs or historical evidence to make current validation pass.

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-001 | `no_action` target fields expressed as YAML null or empty string satisfy the existing empty-target contract; non-empty values remain rejected. | must |
| FR-002 | Proposal input manifests and curated snapshots remain byte-identical during validation and any supported migration reconciliation. | must |
| FR-003 | An input whose source record moved is considered migration-authentic only when a successful verified receipt maps its exact old path to the intended current path and authenticates the manifest's original SHA-256. No filename guessing or unrelated migration receipt is accepted. | must |
| FR-004 | A moved input with missing, mismatched or ambiguous receipt provenance remains invalid with an actionable diagnostic naming proposal, manifest and source. | must |
| FR-005 | Input hashes that are stale for non-moved or changed-in-place sources remain visible as stale; the validator never refreshes the manifest or proposal fingerprint automatically. | must |
| FR-006 | Historical proposal decisions are not treated as current approval for a changed proposal fingerprint or materially changed proposed intervention. | must |
| FR-007 | `validate-proposal` and whole-Project `validate` agree on proposal validity and report the same verified provenance disposition. | must |
| FR-008 | Validation remains deterministic, offline, Python standard-library-only, and read-only. | must |

## Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-001 | Provenance checks fail closed on malformed receipts, path traversal, project-identity mismatch, missing before-image hashes or digest mismatch. | must |
| NFR-002 | Existing accepted/rejected decisions, curated input bytes and migration receipts remain immutable. | must |
| NFR-003 | Ordinary non-migrated proposal validation retains its current hash-pinned behavior. | must |

## Success Criteria

- [ ] The historical no-action proposal with null target fields validates according to the empty-target contract without changing its bytes or fingerprint.
- [ ] A fixture with a moved proposal input validates only when the exact successful migration receipt authenticates the old path and source SHA-256.
- [ ] Missing, wrong-Project, mismatched-hash, changed-in-place and ambiguous migration provenance fail with specific diagnostics.
- [ ] The two proposals with stale `notes/index.md` hashes remain explicitly stale unless a valid authorized transition exists; no hash is silently refreshed.
- [ ] `validate-proposal` and whole-Project `validate` produce consistent results on valid-current, moved-with-receipt, stale-unmoved and tampered-receipt fixtures.
- [ ] Proposal/curated input bytes, decision fields and fingerprints remain unchanged throughout validation.

## Open Questions

- [ ] For completed proposals with stale non-moved inputs, should project-wide `validate` remain non-zero, or report historical staleness separately while only blocking proposals that can still authorize a mutation?
- [ ] Is a successful migration receipt's pinned `inputs` map sufficient evidence for historical proposal provenance, or must the verifier also check the retained transaction's before-image and final migration receipt?
- [ ] When a proposal's own fingerprint changes only because a linked identity was mechanically migrated, what exact evidence is sufficient to retain its historical accepted/rejected disposition without treating it as a new decision?

## Decision

The user approved this PRD on 2026-10-12. Architecture creation is the next planning gate. No implementation, manifest rewrite or existing-proposal edit is authorized by this approval.
