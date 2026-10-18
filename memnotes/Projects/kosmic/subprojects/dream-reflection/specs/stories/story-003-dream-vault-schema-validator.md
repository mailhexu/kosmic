---
status: "done"
created: "2026-09-23"
updated: "2026-09-23"
linked_epic: "../epics/epic-001-dream-reflection-initial-release.md"
linked_architecture: "../architecture.md"
linked_prd: "../prd.md"
related_notes: ["../../../../notes/dream-reflection-workflow.md"]
consumer_interface_change: true
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
depends_on: []
review_base: ""
review_round: 0
project_id: "kosmic"
subproject_id: "dream-reflection"
record_kind: "story"
local_id: "003"
---

# Story 059: Dream Vault Schema and Validator

## User Story

As a vault maintainer,
I want first-class validated dream records,
So that reflection history remains linkable, safe, and structurally trustworthy.

## Acceptance Criteria

- [x] `validate-dreams --vault` accepts only dated records, `index.md`, and `ideas.md` under the dream root and enforces `kosmic.dream.record/1` types, enums, headings, filename/date equality, and relative links.
- [x] The validator enforces one reverse-chronological index row per dated record and unique, well-formed idea IDs/merge targets.
- [x] Composite link checks validate staged internal targets plus hash-pinned external targets and fail on drift.
- [x] Canonical record serialization and `generated_content_sha256` generation/verification follow AD-DR6 byte-for-byte.
- [x] Scratch paths and known private handle/token field labels fail validation; valid public run provenance passes.
- [x] Separate candidate-record and idea-input schemas enumerate agent-writable fields; reject generated digests, target identity/date, provenance/run identity, index rows, and other publisher-owned fields.

## Tasks

### Phase 1: Research

- [x] Reuse evidence, index, OKF, canonical scalar/list, digest, and redaction conventions.
- [x] Specify the exact record/index/ideas grammars in Technical Notes.

### Phase 2: Tests (TDD - Write First!)

- [x] TEST-059-1: Valid and malformed record/frontmatter/section/path fixtures.
- [x] TEST-059-2: Index ordering/uniqueness and idea collision/merge fixtures.
- [x] TEST-059-3: Canonical hash, external-link drift, scratch, and secret-label fixtures.

### Phase 3: Implementation

- [x] IMPL-059-1: Add dream record/index/ideas parsers, serializer, and validators.
- [x] IMPL-059-2: Add `validate-dreams` CLI and staged composite-view validation.
- [x] IMPL-059-3: Add redaction and generated-content digest helpers used by publication.

### Phase 4: Review

- [x] All tests pass
- [x] Consumer-interface completion gate passes with stable usage knowledge
- [x] Standards and Spec review completed

## Routine Decision

Dream validation is tied to Kosmic vault schemas and remains project-local CLI
infrastructure; no Shared Routine edge is introduced.

## Technical Notes

The validator is vault-scoped, not an extension of project-scoped `validate`. It defines both untrusted agent-input schemas and final canonical schemas; `dream-publish` must call the same implementation and derive every publisher-owned field itself.

## Assumptions & Verification

| Assumption | Verified? | Source |
|------------|-----------|--------|
| Existing parser can express the fixed YAML types | ⬜ | Projection CLI parser |
| Existing redaction policy is callable before serialization | ⬜ | Managed-run implementation |

## Definition of Done

- [x] All acceptance criteria met
- [x] Focused and full tests pass
- [x] Code reviewed and approved
- [x] Stable usage note exists and is projected
- [x] No regressions introduced

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-09-23 | Created | Initial draft |

| 2026-09-23 | Done | Implemented and verified; dogfood evidence in evidence/2026-09-23-dream-reflection-release |
