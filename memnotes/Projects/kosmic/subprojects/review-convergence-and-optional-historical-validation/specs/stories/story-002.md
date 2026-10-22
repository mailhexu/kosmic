---
project_id: "kosmic"
subproject_id: "review-convergence-and-optional-historical-validation"
status: "approved"
record_kind: "story"
local_id: "002"
created: 2026-10-22
updated: 2026-10-22
linked_prd: "../prd.md"
linked_epic: "../epics/epic-001.md"
linked_architecture: "../architecture.md"
related_notes: [notes/cli-projection-commands.md]
consumer_interface_change: true
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
review_round: 0
completion_observations: []
completion_review: {}
depends_on: [kosmic/review-convergence-and-optional-historical-validation/story/001]
---

# Story 2: Read-only strict-audit override and compatibility cutover

## User Story

As a Project maintainer,
I want a single read-only `validate --history-audit` override that forces retrospective strict auditing of exactly my configured history scope for that one invocation — with an empty-scope refusal, immutable history/STATUS bytes, and zero new flags on any active command,
So that I can fail loudly on real historical mismatches on demand while every operational surface and the canonical view stay exactly as Story 001 defined them.

## Scope

### In Scope
- Adding `--history-audit` to the existing `validate` subcommand only: read-only forced strict audit of the configured non-empty scope, refusing clearly when no/empty scope is configured; existing validate exit conventions retained.
- Compatibility cutover sweep: every operational command/loader (work finish/check-completion, validate-proposal, migration, math, library, workdir, proposal/routine readers) accepts history configuration with unchanged behavior and gains no flag; audit state never reaches operational paths.
- Immutability guarantees: the audit renders no alternate canonical STATUS, writes no history, and diagnostics never claim "all history verified".
- Consumer docs/knowledge coherence in the same episode: `skills/references/cli-projection-commands.md` command reference, `notes/cli-projection-commands.md` durable invariant, `notes/cli-extension-conventions.md` contributor guidance (body link), plus native projection refresh of the published note; real end-to-end smoke.

### Out of Scope
- New history selectors/flags beyond `validate --history-audit`; any mutation, backfill, auto-repin, lifecycle rewrite, or authority grant from audit results; changes to warn-mode behavior delivered by Story 001; upstream code-review skill edits; permanent prose/call-count/wiring tests; changes to the separate review-convergence Epic.

### Owned Files
- `skills/scripts/kosmic_project_skills.py` (validate parser/dispatch), `skills/scripts/kosmic_history.py` (audit override param wiring), `skills/references/cli-projection-commands.md`, `notes/cli-projection-commands.md`, `notes/cli-extension-conventions.md`. Shared publication (`kosmic_completion.py`) and CLI knowledge/generated outputs are reconciled by the parent integration owner against one baseline — one writer per shared path, no blind whole-file edits; Story 001 must be resolved with its native receipt before this Story's edits begin.

## Acceptance Criteria

- [ ] AC1: Given a configured non-empty `history_integrity` scope, when `kosmic_project_skills.py validate --history-audit --project …` runs, then it forces retrospective strict audit of exactly the configured records for that invocation and fails under existing validate exit conventions on actual missing/mismatched integrity with integrity-specific diagnostics, regardless of whether configured mode is warn or strict.
- [ ] AC2: Given no or an empty configured history scope, when `validate --history-audit` runs, then it is refused as a clear configuration/usage error (nonzero exit, explicit message) rather than reporting an audit of nothing.
- [ ] AC3: Given a warn-mode Project, when `validate` runs without the flag, then behavior is exactly the Story 001 contract and the flag is the only strict override; canonical generation before and after the read-only audit uses the same configured view with identical bytes, the audit never renders an alternate canonical STATUS nor writes history, and the audit flag is neither accepted by nor passed to the generator.
- [ ] AC4: Given the audit or normal validate on a history-configured Project, when before/after byte hashes are compared, then configured records, receipts, pins and bound `STATUS.md` are identical, warn-path diagnostics say `unverified`/`not audited` (never "verified"), and audit success states only that configured records passed invocation-time integrity — granting no completion proof or authority.
- [ ] AC5: Given an active stale/tampered in-scope artifact, when `validate --history-audit` or strict-configured validate runs, then existing strict freshness/identity/ancestry/pin failures still refuse it — the history override never bypasses an active dependency and never grants mutation authority.
- [ ] AC6: Across `work finish`, `check-completion`, `validate-proposal`, migration, math, library, workdir and operational loaders on a history-configured Project, when each command runs, then behavior and exit codes match the no-policy baseline and no command except `validate` gains any history flag (verified against `--help` surfaces).
- [ ] AC7: Given a faithful disposable copy of the kosmic Project under managed scratch with the three representative records selected in that copy's `history_integrity`, when the real CLI runs warn `validate`, `validate --history-audit` and `generate-status` on the copy, then warn validation follows the Story 001 success path with unverified warnings, the audit fails on the old done record's missing receipt, generation bytes are identical before and after the audit, every record/receipt/pin/STATUS byte in the copy is unchanged, and the live Project's ProjectEntry and history bytes are untouched.

## Tasks

### Phase 1: Research
- [ ] **Activation task (mandatory, before any edit):** the implementation owner pins `review_base` in this record to the real clean-writer baseline (current `git rev-parse HEAD` of a clean tree, taken after Story 001 landed). The draft deliberately omits `review_base` — no placeholder value is written now.
- [ ] Known facts: validate parser `kosmic_project_skills.py:4185-4188` and STATUS_STALE dispatch ~`:4831-4848`; Story 001's `inspect_history(structure, policy, strict_audit=False)` is the accepted extension point (ADR-002); ADR-001 fixes the only new flag as read-only `validate --history-audit` with empty-scope refusal and kept exit conventions; command reference `skills/references/cli-projection-commands.md` owns flags/procedures while `notes/cli-projection-commands.md` owns durable invariants (Usage/published; regeneration required) and `notes/cli-extension-conventions.md` is Development guidance (body link, not related_notes).
- [ ] Bounded activation checks (read-only): confirm Story 001 is resolved with a native receipt; confirm `--history-audit` does not exist yet; capture baseline bytes/hashes for the three representative records and bound `STATUS.md`; list current `--help` surfaces to diff for the no-flag cutover sweep.

### Phase 2: Tests first (new/changed runtime behavior at the CLI seam; extend `tests/test_project_skills_cli.py`; reuse existing passing guards, never forced red)
- [ ] TEST-001: audit failure on a selected missing-receipt fixture under warn and strict configurations (integrity-specific diagnostic, validate exit convention).
- [ ] TEST-002: empty/absent scope refusal for `--history-audit` (explicit message, nonzero exit, no audit report).
- [ ] TEST-003: no-flag cutover — operational command parsers/behavior identical with history config present; `--help` diff shows no new flags off `validate`.
- [ ] TEST-004: audit read-only byte-immutability on a disposable copy (records, receipts, pins, STATUS.md unchanged).
- [ ] TEST-005: warn parity without the flag — outputs identical to Story 001 behavior; no alternate STATUS render path exists.
- [ ] TEST-006: public CLI regressions cover invalid-scope hard errors under the audit flag and audit byte-immutability on a disposable copy; no permanent call-count/wiring/prose tests.

### Phase 3: Implementation
- [ ] IMPL-001: add `--history-audit` to the validate subparser only; dispatch forces strict audit of the configured scope through `inspect_history` without constructing an operational catalog, refuses empty scope clearly, keeps exit conventions, and never renders or writes an alternate canonical STATUS.
- [ ] IMPL-002: compatibility cutover sweep — assert by construction that no other command/parser/operational loader receives history state; any accidental leak found is removed, not gated.
- [ ] IMPL-003: docs/knowledge in the same episode — `skills/references/cli-projection-commands.md` documents the `--history-audit` flag and procedure, `notes/cli-projection-commands.md` carries the updated durable invariant, `notes/cli-extension-conventions.md` stays coherent via a body link (not misleading related_notes), then the published note's native projection is regenerated and validates clean.

### Phase 4: Real end-to-end smoke
- [ ] Real CLI smoke on a faithful disposable copy of the kosmic Project under the managed scratch workspace with representative existing record bytes and the three PRD representative records selected only in the copy's `history_integrity`: warn validate follows the Story 001 success path with warnings; `validate --history-audit` fails on the old done record's missing receipt; hashes before/after are identical; the stale-active representative (published/executed artifact with a stale pin) still refuses under audit; the live ProjectEntry and history bytes are never edited and all disposables are removed.

### Phase 5: Independent fixed-base review and native completion
- [ ] One independent Standards + Spec review pair against the pinned `review_base` on one held snapshot with the stable full findings ledger, changed targets and affected checks; one complete pair is one round; repairs/partial callbacks consume no round; maximum three rounds then an explicit human decision packet; reviewer-only closure (`status: resolved`, optionally `resolution: fixed|refuted`); completion only via native receipt (`work finish` for this record) after convergence.

## Routine Decision

No reusable deterministic routine mechanics are introduced or materially changed: this Story adds caller guidance and a read-only audit surface for this private Project's own validation — ordinary Project validation/reporting, not registered routine compilation or `uses_routines` edges. If implementation actually changes routine edges or reusable registered mechanics, that scope must be updated and re-approved rather than silently expanded.
