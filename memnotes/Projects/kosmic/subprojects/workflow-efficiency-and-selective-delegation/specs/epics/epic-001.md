---
project_id: "kosmic"
subproject_id: "workflow-efficiency-and-selective-delegation"
status: "approved"
record_kind: "epic"
local_id: "001"
linked_prd: "../prd.md"
linked_architecture: "../architecture.md"
linked_stories:
  - "../stories/story-001.md"
  - "../stories/story-002.md"
---

# Safe Single-Invocation Completion

## Description

One ordinary nonterminal `work finish` runs every currently required
completion gate — eliminating manual precheck choreography — and read-only
criterion prefill removes manual exact copying, without relaxing any guard.
This Epic owns FR-003, FR-004 and FR-005, the FR-002 fresh re-derivation
guards those invocations exercise, and the FR-012 runtime docs/examples/
consumer-contract cutover for this behavior. Requirements and accepted design:
[prd.md](../prd.md), [architecture.md](../architecture.md); ADR-B, ADR-C and
ADR-D are binding, and ADR-A authority semantics are consumed as given —
authority handling is not redesigned here.

## Scope

### In Scope

- Unified finish (FR-003, ADR-B): public `finish_work` signature and
  `work finish` CLI receipt schema unchanged; one invocation runs proof
  validation → primary scope check (`SCOPE_DENIED` precedence over review
  validation) → reviewed scope/`source_revision`/fixed-base review → the
  complete shared read-only domain precheck via the established deferred
  import → affected freshness rechecks immediately before writes → the
  existing publication order (record → indexes → log → receipt → STATUS).
- Guards retained (FR-002/FR-003): dependency, math/proposal/routine,
  consumer related-note, projection, STATUS and authority checks all remain;
  precheck domain errors surface as `COMPLETION_PRECHECK_FAILED` with the
  original diagnostic; Project-config failures are not swallowed; no auto
  repair, repin, or pin refresh inside the precheck; standalone
  `check-completion` stays diagnostic/fail-fast on the same shared helper.
- Terminal route first (FR-004, ADR-C): a valid receipt verifies immutable
  record/legacy originals plus the declared formal contracts — no mutable
  note/data rehash, no current dirty-source review rehash, no pin refresh;
  an absent receipt falls through to full-path recovery; an unreadable or
  inconsistent receipt is rejected, never re-blessed; a valid retry returns
  the receipt and completion log unchanged and repairs only derived STATUS.
- Prefill (FR-005, ADR-D): read-only `work prepare-completion` returns the
  exact criteria in canonical record order, preserving authored and adverse
  entries field-for-field; unauthored criteria come back blank yet remain
  invalid at finish; missing or duplicate/ambiguous criteria and unknown,
  duplicate or malformed authored mappings are rejected; no writes, sidecar,
  outcome, reviewer or approval claims; completed records refused.
- Cutover (FR-012): current docs, CLI guidance, examples and consumer
  contracts updated coherently with the landed behavior; historical bytes
  untouched.

### Out of Scope

- No workflow-policy redesign: no reviewer-count reduction, light pass, new
  preflight framework, prepared-completion token, or completion dossier.
- No installs, live/global vault changes, or historical record/receipt/pin
  byte edits.
- No measurement ownership: the FR-011 three-case assessment and packet-
  sizing policy (ADR-E/F) belong to Epic 002 and may proceed independently;
  its integrated assessment uses the mechanics this Epic lands.

## Stories

- [Story 001: Unified Safe Completion and Immutable Retry](../stories/story-001.md) — done; successful receipt.
- [Story 002: Read-Only Criterion Prefill](../stories/story-002.md) — done; successful receipt.

These Stories have no semantic dependency; overlapping runtime/docs edits need
one integration owner rather than concurrent blind writes.

## Success Criteria

- [x] A feature Story finishes through one `work finish` invocation exercising every applicable completion gate before done/receipt publication.
- [x] Injected invalid dependency, authority, scientific-math, proposal or projection state blocks finish with no receipt. Domain precheck failures retain their diagnostic through `COMPLETION_PRECHECK_FAILED`; existing authority/scope/proof/review codes remain unchanged, and missing/unreadable Project config is reported, not swallowed.
- [x] Mis-scoped finish claims fail with `SCOPE_DENIED` before review validation is consulted.
- [x] Changed record bytes, a changed `source_revision` binding, or stale mid-episode authority reject the invocation.
- [x] Ordinary linked-note/data evolution and review-base aging leave a valid receipt valid, while tampered record bytes, missing/changed immutable originals, or failing declared formal math/proposal/routine checks reject the retry.
- [x] A valid retry returns the receipt and completion log unchanged and repairs only derived STATUS; an unreadable/inconsistent receipt is rejected without re-blessing or repinning; an absent-receipt interrupted finish recovers by rerunning every gate.
- [x] `prepare-completion` preserves authored/adverse entries verbatim in canonical order, leaves unauthored criteria blank while such drafts still fail finish, rejects missing/ambiguous criteria and unknown/duplicate/malformed authored mappings, refuses completed records, and provably writes nothing.
- [x] Implementing Stories verify behavior at the CLI level (no source-text, import, or call-count assertions) and complete only after mandatory pinned two-axis review on the fixed base; docs/examples/consumer contracts match shipped behavior at cutover.

## Progress

- Stories: 2/2 receipted done; the approved planning record is retained without inventing a separate Epic completion receipt.
- Evidence: child observations, actual CLI exercises and independent Round 2 review. Final integrated assessment belongs to Story 004.
