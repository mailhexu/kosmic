---
project_id: "kosmic"
subproject_id: "command-owned-indexes-and-completion-review-context"
status: "approved"
record_kind: "epic"
local_id: "002"
linked_prd: "../prd.md"
linked_architecture: "../architecture.md"
created: "2026-10-23"
updated: "2026-10-23"
linked_stories: ["../stories/story-003.md"]
---

# Read-only completion fingerprints

## Description

Expose the exact existing review fingerprint through `work prepare-completion --worktree`, so completion drafting needs no inline Python imports or extra command. Keep preparation read-only and finish authoritative.

Requirements: PRD FR-005–007 and the fingerprint portion of FR-008. Technical decision: Architecture ADR-001 and its fingerprint/authority invariants.

## Scope

### In Scope

- Optional explicit `--worktree` on the existing preparation command. Without it, preserve current arguments, payload and behavior; never infer the writer from the current directory.
- With it, return top-level `source_revision` from the existing function alongside identity, canonical record path and preserved observation drafts.
- Preserve every authored observation field and blank unauthored criteria; fabricate no outcome, review decision, approval or evidence.
- Reuse live record resolution, nonterminal implementation admission, existing error precedence and the current fingerprint algorithm/exclusions, subject only to Architecture's user-approved exact canonical creation-lock amendment implemented during Story 002 integration. Story 003's completed receipt and historical reviewed pins remain unchanged.
- Leave both Project and writer unchanged on success/refusal. Add no clean/start/registration requirement, state repair, locks, logs, manifests, receipts or STATUS writes.
- Keep finish's live source/record/authority checks and revision-bound review intact. A preparation result remains a point-in-time observation, not cached permission.
- Replace the internal-import recipe and migrate relevant command references, canonical knowledge and generated guidance only after exercising the native command.

### Out of Scope

- New top-level fingerprint/review-context commands, `--write`, implicit source roots or a replacement hash.
- Automatic review pinning, approval/evidence generation, terminal/planning-record bypasses, or rewriting historical pins and receipts.
- Native index publication/recovery, owned by [Epic 001](epic-001.md).

## Planned Story Breakdown

Approved by the user. One cohesive Story covers **explicit-writer completion preparation and caller cutover**: optional argument/output, read-only and revision-binding behavior, regression coverage, actual CLI smoke, and removal of the obsolete internal-Python recipe together. No thin parser-only Story or temporary compatibility command. The Story requires its own approval before implementation.

The Story uses TDD and mandatory independent code review. Its implementation record will contain actual acceptance observations and review; no separate evidence sidecar.

[Story 003: Explicit-writer completion preparation and caller cutover](../stories/story-003.md) is user-approved and has no functional dependency on Epic 001's Stories.

## Success Criteria

- [ ] Existing preparation without `--worktree` preserves its current result and refusal behavior.
- [ ] Explicit-writer preparation returns the exact current `source_revision` with authored observations preserved field-for-field and unauthored criteria left blank.
- [ ] Real changed/untracked/deleted source and excluded metadata affect the value as the existing algorithm dictates, with only the approved same-root canonical creation-lock exception; unrelated `.kosmic/` data and an external Project's writer-local lock remain bound. Git HEAD is not substituted.
- [ ] A matching reviewed fingerprint passes the existing finish binding, while subsequent source drift is refused without automatic repinning or weaker safety gates.
- [ ] Project and writer bytes remain unchanged after success and refusal; existing record/ancestry/acceptance refusals and invalid-writer diagnostics remain.
- [ ] All affected callers use the supported CLI output; the obsolete internal-import recipe is removed and canonical projections are regenerated through the normal source path.
- [ ] Focused behavioral coverage and real CLI smoke pass; required independent review converges and the implemented Story has a successful native completion receipt.

## Verification

Extend existing preparation tests and finish binding scenarios through the CLI. Exercise both optional-argument paths, preserved adverse/extra observation fields, blank criteria, read-only filesystem snapshots and actual source drift. Tests compare consumer behavior and the authoritative binding, not source text or forwarding mocks.

Smoke the documented preparation → actual review binding → finish sequence on governed disposable fixtures, including stale-source refusal. Trust successful command results for their declared outputs rather than adding administrative confirmation commands.

Run the integrated affected suite once related implementation changes stabilize; preserve existing scientific/authority checks.

## Dependencies and Progress

- Requires the approved [PRD](../prd.md) and [Architecture](../architecture.md).
- No functional dependency on Epic 001. Coordinate shared CLI/guidance edits with its integration owner; combine the canonical projection refresh after related note edits.
- Receipt-backed status: [owning Story table](../INDEX.md#stories).
- Completion requires Story 003's native receipt; independent review approval alone is not completion.
