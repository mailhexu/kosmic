---
project_id: "kosmic"
subproject_id: "command-owned-indexes-and-completion-review-context"
status: "approved"
record_kind: "epic"
local_id: "001"
linked_prd: "../prd.md"
linked_architecture: "../architecture.md"
created: "2026-10-23"
updated: "2026-10-23"
linked_stories: ["../stories/story-001.md", "../stories/story-002.md"]
---

# Native indexed spec creation and recovery

## Description

Make successful `spec-create` own both its draft record and canonical owning-index row. Agents consume returned identities/paths instead of writing rows, discovering output locations or checking successful creation again.

Requirements: PRD FR-001–004 and the creation/index portion of FR-008. Technical decisions: Architecture ADR-002–004.

## Scope

### In Scope

- All five kinds: PRD, Architecture, Epic, Story and shared Quick Task; preserve existing immutable owner/parent identities and admission rules.
- Native rows in owner-local feature indexes or the Project index for Quick Tasks, in the table shape finish already updates. Preserve unrelated content; append a compatible table when needed rather than converting legacy sections.
- Extend the existing creation lock and operation records to every kind. Reserve identity/paths before publication; return success only after record and row publication.
- Resume incomplete publication with the same operation and identity. Preserve unrelated current index edits; refuse conflicting draft bytes, ambiguous/conflicting entries and unsafe targets without overwriting them.
- Expose non-null operation ID and explicit Project-relative `record_path`/`index_path`; retain existing result fields and historical `paths` representations.
- Serialize supported creation and finish index updates through the existing lock. Keep finish's gates, publication order and receipt semantics unchanged.
- Replace obsolete manual row-creation instructions and non-PRD resume caveats after exercising native behavior. Update canonical knowledge/generated guidance through their normal publication path.

### Out of Scope

- Bulk repair of historical bullet indexes, missing rows, operation history, receipts or review pins.
- A new transaction framework, journal, background process or cross-file atomicity claim.
- Automatic approval, implementation authority from draft creation, and guarantees against arbitrary concurrent editors ignoring the lock.
- The completion fingerprint interface, owned by [Epic 002](epic-002.md).

## Planned Story Breakdown

Approved by the user. The following slices define the Story breakdown; each Story requires its own approval before implementation.

1. [Story 001: Indexed creation and deterministic recovery](../stories/story-001.md) — draft; operation-backed record/row publication for all kinds, explicit returned paths and preservation/conflict/recovery coverage.
2. [Story 002: Finish coordination and workflow cutover](../stories/story-002.md) — draft; depends on Story 001, serializes index writers, proves actual finish transitions and migrates creation callers/guidance.

Both slices use TDD and mandatory independent code review. Shared CLI and guidance edits have one integration owner; independent investigation does not imply concurrent writes to those files.

## Success Criteria

- [ ] Each supported creation kind returns its actual record/index paths and produces one canonical row with correct title, kind, state and resolvable relative link.
- [ ] Interrupted publication resumes the original identity without duplicate rows or replacement of unrelated content; published-operation resume keeps its existing refusal.
- [ ] Conflicting record/row/unsafe-path cases refuse with operation/path context, preserve current bytes and never report successful partial publication.
- [ ] Supported interleaved creations and finish index updates retain all owned rows and status changes.
- [ ] A natively created implementation record completes through the actual finish path and its owning row becomes `done`, without weakened review/authority/receipt gates.
- [ ] All affected callers use native output/recovery; obsolete manual row-creation instructions are removed. Non-native research indexing and historical repair are not implicitly claimed.
- [ ] Behavioral regression coverage and the real CLI smoke pass; required independent review converges and implemented Stories have successful native completion receipts.

## Verification

Use the existing spec-creation/work-record/finish suites. Cover preservation, interruption boundaries, identity stability, unsafe targets and status transitions through public behavior, not exact template bytes or lock wiring.

Smoke the documented create → interrupted resume → consume returned paths → finish sequence in governed disposable fixtures. Successful administrative command outputs are authoritative; no additional listing, read-back or validation pass is required merely to confirm them.

The integrated affected suite runs after feature changes stabilize. Record actual observations and review in the eventual Stories, not in separate evidence files.

## Dependencies and Progress

- Requires the approved [PRD](../prd.md) and [Architecture](../architecture.md).
- No functional dependency on Epic 002; coordinate shared CLI/guidance files and combine the canonical projection refresh after related note edits.
- Stories: 0/2 done; both drafts await approval. Implementation: not started.
- Next gate: user approval of the linked draft Stories before implementation.
