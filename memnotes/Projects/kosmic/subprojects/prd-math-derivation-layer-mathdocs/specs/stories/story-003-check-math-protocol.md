---
status: "done"
created: "2026-09-05"
updated: "2026-09-05"
linked_epic: "../epics/epic-002-math-execution-verification.md"
linked_architecture: "../architecture.md"
linked_prd: "../prd.md"
related_notes: ["cli-projection-commands.md"]
consumer_interface_change: true
evidence_packs: ["2026-09-05-math-derivation-layer-impl"]
review_base: ""
review_round: 0
project_id: "kosmic"
subproject_id: "prd-math-derivation-layer-mathdocs"
record_kind: "story"
local_id: "003"
---

# Story 012: check-math Protocol and Verification

## User Story

As a developer, I want one deterministic command to execute and compare SymPy
results, so that successful execution cannot hide stale equations.

## Acceptance Criteria

- [x] `check-math` runs selected slugs lexically with no shell, controlled cwd/environment, UTF-8 capture, and configurable default-30-second timeout.
- [x] Version-1 JSON requires exact schema, sorted unique result names, non-empty srepr/LaTeX, and no extra stdout.
- [x] Default mode is read-only and compares protocol versions/results, paired generated block, source hash, and recorded Python/SymPy versions.
- [x] Missing SymPy, malformed JSON, nonzero exit, timeout, output mismatch, and stale environment fail with slug/layer/remedy.
- [x] Trusted-code warning is emitted without claiming a sandbox.

## Tasks

### Phase 1: Research
- [x] Verify subprocess/error/parser conventions and CLI exit codes

### Phase 2: Tests (TDD)
- [x] TEST-012A: valid fake protocol and lexical ordering
- [x] TEST-012B: every protocol/process failure mode
- [x] TEST-012C: read-only filesystem proof and selected-slug behavior

### Phase 3: Implementation
- [x] IMPL-012A: add parser/dispatch and deterministic child runner
- [x] IMPL-012B: parse protocol into typed named results
- [x] IMPL-012C: compare against registry and render diagnostics

### Phase 4: Review
- [x] Focused/full tests and CLI smoke check pass
- [x] Task 7 review approved

## Definition of Done

- [x] All acceptance criteria met
- [x] Consumer command documentation stable
- [x] Code reviewed; related usage note updated before completion
