---
project_id: "kosmic"
subproject_id: "knowledge-first-notes-and-evidence-retirement"
status: done
record_kind: "story"
local_id: "003"
created: 2026-10-18
updated: 2026-10-18
linked_prd: "../prd.md"
linked_epic: "../epics/epic-001.md"
linked_architecture: "../architecture.md"
related_notes: ["notes/cli-projection-commands.md", "notes/note-writing-style.md"]
consumer_interface_change: true
review_base: "09ca28c"
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
review_round: 3
completion_review:
  reviewer: "OMP/Main"
  axes:
    standards: {decision: "approved", reviewer: "Story003StandardsReviewer"}
    spec: {decision: "approved", reviewer: "OpenAI Codex Spec"}
  decision: "approved"
  review_base: "09ca28c"
  reviewed_revision: "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a"
  findings:
    - id: "03STD-01"
      disposition: "Blocking"
      status: "resolved"
      resolution: "Empty reviewed scope self-blocked record-only finishes: the coverage recheck ran even when the computed changed-path set was empty. Resolved by skipping coverage only for an empty changed set (source commits 3005e3a, ac486ac), with the record-only success regression and the meaningful uncovered-work refusal regression."
    - id: "03STD-02"
      disposition: "Blocking"
      status: "resolved"
      resolution: "The plain --work-item terminal entry skipped the current math contract after a receipt. Resolved by factoring the math contract group into the shared gate helper wired into the plain terminal path, proven by the math-source-drift regression (specific source_sha256 refusal, direct receipt still valid; source commit ac486ac)."
    - id: "03STD-03"
      disposition: "Blocking"
      status: "resolved"
      resolution: "The plain terminal entry still ran the full record-content validator, revoking valid receipts when a declared note was later deprecated or merged. Resolved by deriving only the declared formal MathDoc registry on the terminal path (load_math_registry only_slugs), proven by the declared-note deprecation regression (source commits e7990dc5, d1559017)."
    - id: "03SPEC-1"
      disposition: "Blocking"
      status: "resolved"
      resolution: "Same plain-entry early return left current proposal/routine contracts unverified after a receipt. Resolved by the same shared factored helper covering proposal and routine gates on the plain terminal path, with the record-only and math regressions exercising the shared wiring."
    - id: "03SPEC-2"
      disposition: "Blocking"
      status: "resolved"
      resolution: "The plain --work-item terminal receipt path revalidated the record's declared linked notes after the receipt (the full record-content validator rejected a later deprecated/merged note), revoking a valid completion. Resolved together with 03STD-03 by deriving only the declared formal MathDoc registry on the terminal path (load_math_registry only_slugs) so no related-note or knowledge-currentness check runs after the receipt, proven by the declared-note deprecation regression (source commits e7990dc5, d1559017). AC11 bounded carry-over was demonstrated separately under the approved scope and is recorded in the completion observations, not as a review finding."
  scope: ["worktree:skills/scripts/", "worktree:skills/references/", "worktree:tests/", "project:skills/", "project:impact.md", "project:subprojects/knowledge-first-notes-and-evidence-retirement/specs/stories/story-003.md"]
completion_observations:
  - criterion: "Given an ordinary code fix in an approved implementation record, when `work finish` runs with criterion observations and the review decision embedded in that record, then completion succeeds with no `evidence/` directory, no acceptance/review sidecar JSONs, no manifest, and no manufactured note, and the published receipt's proof binds exactly the completed record (`{record_path: sha256 of record bytes at finish}`)."
    observation: "Toy-two real CLI finish (managed run two) succeeded with no evidence/ directory, no sidecar JSONs, no manifest and no manufactured note; the published receipt proof was exactly {record_path: sha256 of finished record bytes}. The parent-observed 64-test pass includes the receipt-binding unit coverage."
    source: "Managed run 20261018T171855Z-story003-completion-smoke-two (work finish --scope worktree:src/ --scope project:specs/); receipt captured in this record's Technical Notes."
  - criterion: "Given observations that omit any acceptance criterion or mismatch the exact criterion checkbox text, when `work finish` validates, then it fails deterministically and publishes no receipt — a structural coverage check only: no keyword/NLP parsing of free-text observation content and no new mandatory outcome field or classifier."
    observation: "Missing, partial, mismatched and repeated criteria each refuse deterministically without a receipt; the validator contains no outcome field and no text parsing."
    source: "Coverage regressions in tests/test_record_scoped_completion.py within the parent-observed 64-test pass."
  - criterion: "Given observations documenting an actual adverse scientific/verification finding, when finish runs, then observation sufficiency is assessed by the real independent reviewer, not by machine parsing: the structured `completion_review` decision must be non-approved (e.g. `changes-requested`), and finish deterministically refuses to publish a receipt while that decision is not approved."
    observation: "A changes-requested review decision refuses publication deterministically; sufficiency judgment stays with the recorded reviewer."
    source: "test_changes_requested_review_blocks_receipt in the parent-observed pass."
  - criterion: "Given source changed after the recorded review, when `work finish` re-derives `source_revision`, then the `reviewed_revision` mismatch fails completion; binding keeps the unchanged `source_revision`, including its `specs/`/`evidence/`/`log/`/record/`.tmp`/STATUS/`.git/` exclusion set un-widened."
    observation: "A stale reviewed_revision fails as REVIEW_INVALID; the source_revision algorithm and exclusion set were read-verified unchanged and behaved identically across both toy runs."
    source: "test_stale_embedded_reviewed_revision_denies_completion; kosmic_completion.source_revision read verification."
  - criterion: "Given either review axis lacks an approved decision with a named reviewer identity, when completion is validated, then it fails; standards and spec approvals remain mandatory and independent (existing identity/base/round checks preserved in embedded form)."
    observation: "A non-approved nested axis and an empty reviewer identity each refuse; standards and spec stay independent named decisions under review.axes."
    source: "test_missing_axis_approval_refuses and test_missing_reviewer_identity_refuses in the parent-observed pass."
  - criterion: "Given a blocking finding neither resolved nor explicitly risk-accepted by a named human with a reason, when completion is validated, then it fails; finding ids, dispositions, and risk-acceptance notes survive approval."
    observation: "Unresolved Blocking disposition refuses; disposition Blocking with status risk-accepted plus named risk_accepted_by and risk_acceptance_note finishes."
    source: "test_unresolved_blocking_finding_refuses and test_risk_accepted_blocking_finding_finishes."
  - criterion: "Given `work finish --scope` claims, then scope diff checking behavior is unchanged, and record status changes only through finish publication: a hand-edited `done` without a receipt stays surfaced as receipt-pending, never counted as completed."
    observation: "Out-of-scope source still refuses with SCOPE_DENIED and an unreceipted done stays receipt-pending; toy-two's STATUS_STALE precheck refusal demonstrated the live precheck gate (toy-one's failed preflight was gate evidence, never counted as closure)."
    source: "test_out_of_scope_diff_is_not_completed and test_unreceipted_done_remains_pending_and_finish_converges; toy-two precheck transcript."
  - criterion: "Given a newly completed record, when its receipt is validated later, then validation checks schema, qualified identity, canonical `record_path`, successful status, and `record_sha256`/proof against the unchanged completed record bytes only — no recursive rehashing of linked notes, data docs, or artifacts."
    observation: "Both check-completion entry modes validate the completed toy-two record against its unchanged bytes only; no note or data-doc rehashing occurs."
    source: "Toy-two live post-finish both entry modes; test_receipt_survives_note_evolution_but_not_record_edit."
  - criterion: "Given historical completion, when related notes are later refined, merged, split, or deprecated, or dataset-local docs change, then the receipt stays valid with no retroactive drift; when the completed work record itself is edited after its receipt, then the receipt breaks by design (drift detection, not adversarial authentication — reviewer attribution and the trusted publication path remain required)."
    observation: "A dataset-doc edit left both entry modes green; a post-receipt record edit was rejected by both entry modes with COMPLETION_PENDING; byte-exact restore plus retry returned the byte-identical receipt."
    source: "Toy-two live post-finish exercises (run two transcript)."
  - criterion: "Given a legacy receipt recorded against sidecar files, when validated, then it checks those originals' unchanged historical bytes without rehashing evolving linked content; absent or unrecoverable originals surface as explicit pending/blocker and no legacy receipt is repinned, blanket-blessed, or refreshed against current bytes."
    observation: "Legacy sidecar receipts validate recorded originals only; a missing original surfaces pending, a changed original surfaces drift, recorded artifact churn never revokes, and an empty proof stays pending."
    source: "test_legacy_sidecar_receipts_stay_terminal_without_repin segments (a)-(g) in the parent-observed pass."
  - criterion: "Given migration of existing proof payloads to the record-bound shape, when a record is carried over, then no recorded fact is dropped (criteria, outcomes, artifacts, reviewer identities, findings, revisions are preserved or explicitly mapped in the approved migration record)."
    observation: "Bounded carry-over demonstrated (AC11): a synthetic legacy fixture (done record + acceptance/review sidecars + artifact + legacy receipt) was carried through the official legacy reader in managed run 20261018T180846Z-story003-legacy-carryove; the field-by-field inventory (criteria, outcomes, observations, artifact references and digests, reviewer identities and decisions, findings, review base/round/reviewed revision, record binding, proof digests) was identical before and after the reader pass, all original bytes unchanged, receipt never repinned. Live migration of the real vault remains a future separately approved activity with the documented field-by-field mapping rule."
    source: "Managed run 20261018T180846Z-story003-legacy-carryove (scratch carryover/): before/after inventory comparison through kosmic_completion.check_terminal_receipt; inventory JSON in the Story003 smoke transcript."
  - criterion: "Given an interrupted finish, when it is retried, then the receipt-first repair keeps the valid receipt and regenerates only derived STATUS, preserving the publish order record → indexes → completion log → receipt → STATUS."
    observation: "Interrupted-publication repair keeps the receipt and regenerates only derived reports; the toy-two byte-restore retry returned the byte-identical receipt."
    source: "Interrupted-repair tests in the parent-observed pass; toy-two retry receipt_immutable=yes."
  - criterion: "Given the cutover, then the math gate (`validate_math_implementation`) and the skill-proposal and routine gates in `_check_existing_completion` behave unchanged, and no replacement dossier, manifest, or hidden directory is introduced."
    observation: "Math and proposal/routine suites passed untouched within the parent-observed run; the toy finishes introduced no evidence packs, manifests or hidden directories."
    source: "Parent-observed 64-test pass (math/proposal suites untouched); toy-two finish transcript."
depends_on: []
---

# Story 003: Compact completion and durable historical receipts

## User Story

As a kosmic developer finishing a Story or QuickTask,
I want criterion observations and the independent review decision embedded in the work record, with the receipt bound to the completed record's bytes,
So that an ordinary code fix completes without an Evidence Pack, manifest, or acceptance/review sidecars, and historical completions stay valid regardless of later note or data-doc evolution.

## Dependencies

None — Epic slice 3 is independently designable. [Story 005](story-005.md) later reconciles the
whole-release doc cutover; this story owns only its bounded doc set below.

## Acceptance Criteria

- [ ] Given an ordinary code fix in an approved implementation record, when `work finish` runs with criterion observations and the review decision embedded in that record, then completion succeeds with no `evidence/` directory, no acceptance/review sidecar JSONs, no manifest, and no manufactured note, and the published receipt's proof binds exactly the completed record (`{record_path: sha256 of record bytes at finish}`).
- [ ] Given observations that omit any acceptance criterion or mismatch the exact criterion checkbox text, when `work finish` validates, then it fails deterministically and publishes no receipt — a structural coverage check only: no keyword/NLP parsing of free-text observation content and no new mandatory outcome field or classifier.
- [ ] Given observations documenting an actual adverse scientific/verification finding, when finish runs, then observation sufficiency is assessed by the real independent reviewer, not by machine parsing: the structured `completion_review` decision must be non-approved (e.g. `changes-requested`), and finish deterministically refuses to publish a receipt while that decision is not approved.
- [ ] Given source changed after the recorded review, when `work finish` re-derives `source_revision`, then the `reviewed_revision` mismatch fails completion; binding keeps the unchanged `source_revision`, including its `specs/`/`evidence/`/`log/`/record/`.tmp`/STATUS/`.git/` exclusion set un-widened.
- [ ] Given either review axis lacks an approved decision with a named reviewer identity, when completion is validated, then it fails; standards and spec approvals remain mandatory and independent (existing identity/base/round checks preserved in embedded form).
- [ ] Given a blocking finding neither resolved nor explicitly risk-accepted by a named human with a reason, when completion is validated, then it fails; finding ids, dispositions, and risk-acceptance notes survive approval.
- [ ] Given `work finish --scope` claims, then scope diff checking behavior is unchanged, and record status changes only through finish publication: a hand-edited `done` without a receipt stays surfaced as receipt-pending, never counted as completed.
- [ ] Given a newly completed record, when its receipt is validated later, then validation checks schema, qualified identity, canonical `record_path`, successful status, and `record_sha256`/proof against the unchanged completed record bytes only — no recursive rehashing of linked notes, data docs, or artifacts.
- [ ] Given historical completion, when related notes are later refined, merged, split, or deprecated, or dataset-local docs change, then the receipt stays valid with no retroactive drift; when the completed work record itself is edited after its receipt, then the receipt breaks by design (drift detection, not adversarial authentication — reviewer attribution and the trusted publication path remain required).
- [ ] Given a legacy receipt recorded against sidecar files, when validated, then it checks those originals' unchanged historical bytes without rehashing evolving linked content; absent or unrecoverable originals surface as explicit pending/blocker and no legacy receipt is repinned, blanket-blessed, or refreshed against current bytes.
- [ ] Given migration of existing proof payloads to the record-bound shape, when a record is carried over, then no recorded fact is dropped (criteria, outcomes, artifacts, reviewer identities, findings, revisions are preserved or explicitly mapped in the approved migration record).
- [ ] Given an interrupted finish, when it is retried, then the receipt-first repair keeps the valid receipt and regenerates only derived STATUS, preserving the publish order record → indexes → completion log → receipt → STATUS.
- [ ] Given the cutover, then the math gate (`validate_math_implementation`) and the skill-proposal and routine gates in `_check_existing_completion` behave unchanged, and no replacement dossier, manifest, or hidden directory is introduced.

## Non-Goals

- No new dossier/manifest format, hidden directory, or new subcommand mode (NFR-003).
- No change to `source_revision` semantics beyond where embedded review reads it; no widening of its exclusion list.
- No live-vault migration, evidence-archive recreation, or deletion of existing `evidence/` content ([Story 005](story-005.md)).
- No math-gate semantics change; mathdocs remain formal derivation records.
- No renderer authorization change ([Story 001](story-001.md)), note metadata/curation ([Stories 002](story-002.md)/[004](story-004.md)), or ADR-0002 supersession ([Story 005](story-005.md)).
- No automatic re-blessing of legacy receipts and no machine validator replacing semantic review.

## Tasks

### Phase 1: Research

- [ ] Map the exact completion paths: `validate_completion_proof`, `source_revision`, `_checked_review`, `validate_receipt_payload`, `check_terminal_receipt`, `finish_work`, `check_completion_gates` in `skills/scripts/kosmic_completion.py`; gates and pending-receipt rendering in `skills/scripts/kosmic_project_skills.py`; scope checks in `skills/scripts/kosmic_work.py`.
- [ ] Inventory existing receipts under `.kosmic/work-receipts/` and their sidecar/proof shapes; identify which records would need the legacy pending path.
- [ ] Verify current test coverage for completion behavior under `tests/` and pick red/green targets.
- [ ] Confirm the bounded doc set (`skills/references/work_completion.md`); defer all other pack-doc cutover to [Story 005](story-005.md).
- [ ] Document findings in Technical Notes; record open points in the assumption table.

### Phase 2: Tests (focused deterministic red/green where machine-testable)

- [ ] TEST-001: missing/partial/mismatched criterion coverage fails deterministically before any receipt write; and a non-approved structured `completion_review` decision (e.g. `changes-requested`) blocks receipt publication — asserted via the structured decision field, never via free-text observation wording such as 'failed' triggering parser rejection.
- [ ] TEST-002: source drift since review (`reviewed_revision` ≠ recomputed `source_revision`) fails.
- [ ] TEST-003: missing standards or spec axis approval, or missing reviewer identity, fails.
- [ ] TEST-004: unresolved blocking finding fails; named-human risk acceptance passes with the note retained.
- [ ] TEST-005: new-shape receipt validates against unchanged record bytes; stays valid across later note edits; breaks when the completed record is edited.
- [ ] TEST-006: legacy sidecar receipt validates against unchanged historical originals; absent originals surface pending/blocker, not forged success.
- [ ] TEST-007: retry after interruption keeps the receipt and repairs only STATUS; publish order preserved.
- [ ] TEST-008: existing math/proposal gate tests stay green untouched.

### Phase 3: Implementation

- [ ] IMPL-001: add embedded `completion_observations`/`completion_review` validation (full exact-text criterion coverage, both independent axes, fixed `review_base` + `reviewed_revision`, findings ledger) replacing sidecar-file validation in `work finish`.
- [ ] IMPL-002: narrow receipt proof to the completed record binding; keep all other receipt fields and the publish order intact.
- [ ] IMPL-003: add the legacy validation branch (unchanged historical bytes → valid; missing/unrecoverable → explicit pending/blocker) without repinning or new subcommands.
- [ ] IMPL-004: remove the retired gates (`evidence_packs` requirement, forced `note_links_evidence_pack` chain, sidecar inputs) while keeping identity/scope/math/proposal duties; update `skills/references/work_completion.md` to match runtime.

### Phase 4: Real CLI smoke

- [ ] On bounded scratch records: complete a fix with no `evidence/`, no sidecars, no note; probe each negative boundary; exercise a legacy-shaped receipt and an interrupted-then-retried finish via the real CLI. As one-off planning-package verification, confirm records still resolve through the `SpecCatalog` public seam (`skills/scripts/kosmic_specs.py`) — no standing wiring test.

### Phase 5: Independent review

- [ ] Real independent Standards + Spec review with named per-axis reviewers, fixed review base, and a findings ledger embedded in this record per the new shape; blocking findings resolved or explicitly human-risk-accepted.

## Routine Decision

Project-internal `work finish`/receipt validation mechanics change (completion
evidence moves from sidecar files into the owning work record and the receipt
binds the record itself), but no Shared Skill Library routine or edge artifact
is introduced or modified; therefore no separate routine proposal is required
by this Story.

## Technical Notes

Real compact-completion smoke (2026-10-18, managed run
`20261018T164901Z-story003-completion-smok-c01e35f16be01edf9841ba77c19d6eb9`,
handle `.tmp/kosmic/handles/61541b0151e3f421d2662db918279aa6`, toy repo
`.tmp/kosmic/runs/<run>/scratch/toy-vault`, project `Projects/toy`,
project_id `synthetic-sandbox`):

- Canonical record `synthetic-sandbox/quick-task/fix-double-behavior`
  (`specs/quick-tasks/fix-double-behavior.md`, project-level per the
  supported model; toy registry rebuilt via official `workdir-register`,
  entry `wd-3344ce8f92bbdf52`, bootstrap QC
  `synthetic-sandbox/quick-task/bootstrap-working-directory-registration-synthetic-sandbox`).
- `review_base` `f72528153245da9696f1b16b9e3a66ba23409f0d`; two real
  independent approvals (Toy003Standards, Toy003Spec) recorded in the nested
  ADR-B `completion_review` with `reviewed_revision`
  `4d7ad892a582f48923d25c7f6cda58571eedd9f42415a4f77f1b7b24b4880bb5`, scope
  `["worktree:src/", "project:specs/"]`.
- Real program behavior: baseline printed `3` for input 3 (defect), `0`;
  after the one-line fix `6` and `0`; exactly one dirty path `src/double.py`.
- Real CLI `work finish --scope worktree:src/ --scope project:specs/` →
  successful receipt, proof exactly `{"specs/quick-tasks/fix-double-behavior.md":
  "<record sha256>"}`; no `evidence/`, no packs, no manufactured notes;
  STATUS derived from the receipt.
- Post-finish: both `check-completion` entry modes pass; a later
  dataset-doc edit did not revoke; a post-receipt record edit was rejected
  by both entry modes with `COMPLETION_PENDING`; after byte-exact restore
  the finish retry returned the byte-identical receipt (receipt-first
  repair); the src fix stayed uncommitted throughout.

Research verification (2026-10-18, writer d6030fcb, baseline 09ca28c tree):

Run-two canonical-order smoke (2026-10-18, managed run
`20261018T171855Z-story003-completion-smoke-two-faba22c2407dce25d45eea18f45db80c`,
handle `.tmp/kosmic/handles/ad3bbdccb5bf5ba3b18aee175f925ab4`, toy repo
`.../scratch/toy2-vault`, project `Projects/toy-two`, project_id `toy-two`):

- Canonical order live: fixture baseline commit → official `workdir-register`
  (entry `wd-cf37e6d34a6e4b18`) → `review_base 53788a871312cda1c6b550a1a25d2ae95330fcff`
  pinned (C3) → `work start` accepted BEFORE edits → baseline defect `2→2`,
  `0→0` → one-line fix → `2→6`, `0→0`, exactly one dirty path → real
  observations embedded → `generate-status` under the approved QC BEFORE
  precheck → item-only precheck GREEN.
- Real independent two-axis review recorded exactly as returned:
  standards `Toy003Standards` approved, spec `ToyTwoSpec` approved, no
  findings, reviewed_revision `201e9b7101afab7a9c1cafc0a6c4ebcf25f6eb0f26ddfd9eefe981d09491541b`,
  scope `["worktree:src/", "project:specs/"]`.
- Full `--work-record` check-completion GREEN from the toy worktree (source
  root must be the worktree; running from an unrelated cwd binds the wrong
  delta), then real `work finish` → successful receipt, proof exactly
  `{"specs/quick-tasks/fix-triple-behavior.md": "<record sha256>"}`.
- Post-finish: both entry modes pass; dataset-doc edit did not revoke;
  post-receipt record edit rejected by both entry modes (`COMPLETION_PENDING`);
  byte-exact restore + retry returned the byte-identical receipt; src fix
  uncommitted throughout.
- Smoke-driven source fix (separate commit, UNREVIEWED, flagged for parent):
  fresh-finish primary scope check now always exempts the canonical
  publication candidates (STATUS/INDEX/log) — without it the mandated
  generate-status-before-finish order self-blocks on the derived STATUS.md;
  first observed as `SCOPE_DENIED: STATUS.md`.

- Runtime seams confirmed by direct read: `validate_completion_proof` (:101),
  `source_revision` (:171, exclusion set `specs/`, `evidence/`, `log/`, the record
  itself, `.tmp`, `STATUS.md`, `.git/`, nested-project prefix), `validate_receipt_payload`
  (:199), `check_terminal_receipt` (:211), `_checked_review` (:217), `finish_work`
  (:312, publish order record → indexes → completion log → receipt → STATUS,
  receipt-first repair), `check_completion_gates` (:390).
- Receipts live at `Project/.kosmic/work-receipts/<receipt_name(qualified_id)>`;
  `receipt_name` = `sha256(qualified_id)[:16].json` (`kosmic_dreams.py:443`).
  `kosmic_dreams._successful_receipt` delegates catalog identities to
  `validate_receipt_payload` (so pending semantics ride the rewritten validator);
  flat `specs/`-prefixed bootstrap identities keep the minimal identity/status
  format by design.
- Staged-catalog root receipt validation (`kosmic_project_skills.py` STATUS rows)
  also flows through `pending_terminal_receipts` → `_successful_receipt`, so the
  rewritten record-bound/legacy validator covers the STATUS pending surface with
  no extra consumers to change.
- `evidence_packs` completion gate sat at `kosmic_project_skills.py:3661-3668`
  with `note_links_evidence_pack` (:2643) as its only runtime caller — both
  retired in the cutover; Skill Proposal metadata handling and the full
  `validate` command's `validate_evidence_packs` audit are separate concerns and
  stay untouched (Story 005 owns whole-release doc cutover).
- Test conventions: CLI-driven consumer tests via `tests/scoped_completion_support.py`
  (`ScopedProjectCase` fixture: flat approved quick-task `fixture-task`, one
  criterion, git repo at fixture root, `.tmp/` ignored); direct-API completion
  tests via `tests/test_kosmic_work_records.py` (subproject story fixture from
  `test_kosmic_navigation.build_two_feature_project`). `kosmic_yaml` renders and
  parses JSON-compatible flow collections, so nested embedded completion fields
  live in record frontmatter directly (round-trip verified).
- The empty-changed-set `source_revision` payload hashes to
  `sha256("{}") = 44136fa3…aff8a`; fixture project prefixes exclude every
  project-relative path, so embedded `reviewed_revision` is stable across record
  rewrites in tests.

Current runtime (pre-cutover seams, verified during research):

- `skills/scripts/kosmic_completion.py` — `RECEIPT_SCHEMA = "kosmic.work-receipt/1"`,
  receipts under `.kosmic/work-receipts` (:31-32). `validate_completion_proof` (:101)
  requires an `acceptance_evidence` sidecar per criterion group, re-hashes declared
  artifact `{path, sha256}` entries against live bytes, demands full exact-checkbox
  criterion coverage, and validates the `review_record` sidecar (`review_base` match,
  round 1..3, per-axis standards/spec approvals with reviewer identities, blocking
  findings resolved or user-accepted). `source_revision` (:171) hashes changed
  worktree paths excluding `specs/`, `evidence/`, `log/`, the record itself, `.tmp`,
  `STATUS.md`, `.git/` — this set must not widen (dataset-local placement, ADR-A).
  `_checked_review` (:217) fails when `reviewed_revision` ≠ recomputed
  `source_revision`. `validate_receipt_payload` (:199) demands `record_sha256` equal
  to the hash of current record bytes and `proof` equal to a fresh recompute, raising
  `COMPLETION_PENDING` / `COMPLETION_DRIFT` — the retroactive-revocation behavior
  ADR-C replaces. `finish_work` (:312) publishes record → indexes → completion log →
  receipt → derived STATUS and repairs interrupted publication receipt-first without
  rewriting the receipt or duplicating the log; `check_completion_gates` (:390)
  routes done records to ancestry + terminal-receipt checks and implementation
  records to proof + reviewed-revision checks.
- `skills/scripts/kosmic_project_skills.py` — `_check_existing_completion` (:3618)
  enforces done dependencies, STATUS freshness, `consumer_interface_change`, the
  math gate, the `evidence_packs` + `note_links_evidence_pack` forced pack-to-note
  chain (retired here), and `proposal_required`/`routine` gates (unchanged here).
  Unreceipted `done` renders as receipt-pending (:3820, :3913); root receipt
  validation hashes original record bytes and fail-closes byte-drifted candidates
  (:3886).
- `skills/scripts/kosmic_work.py` — `check_record_changes` (:537) implements
  `--scope` diff claims; `IMPLEMENTATION_KINDS` (:59).

Approved design (ADR-B — field names are proposed, absent from runtime today):
`completion_observations` entries carry `criterion` (exact checkbox text),
`observation`, `source` — the accepted shape has no required outcome field, and
deterministic finish reads only structural criterion coverage: observation
sufficiency, including adverse scientific/verification findings, is assessed by
the real independent reviewer through the structured `completion_review` decision
— never by a new text classifier or outcome field. An implementation may add an
explicit outcome flag only by preserving this accepted
field contract and requiring no unapproved API. `completion_review` carries
reviewer identity, both standards/spec axes with per-axis reviewer and
decision, overall decision
(`approved | changes-requested | user-accepted` with `approved_by`), fixed
`review_base`, `reviewed_revision`, and a stable findings ledger (`Blocking |
Non-blocking`; blocking findings resolved or explicitly risk-accepted by a named
human). `work finish` validates these embedded fields instead of the two sidecar
JSONs; the receipt payload keeps its existing field names and shapes, with proof
exactly `{"<canonical record_path>": "<sha256 of completed record bytes at finish>"}`.

Approved design (ADR-C): a completed work record is immutable after its receipt;
terminal validation hashes only those unchanged record bytes, so later note
refinement/merge/split/deprecation and dataset-doc edits never revoke completion,
while a post-completion work-record edit breaks the receipt by design. These hashes
detect drift, not adversarial fabrication: reviewer attribution and the trusted
publication path remain required. Legacy receipts recorded against sidecar files
validate against those originals' unchanged historical bytes until an approved
migration establishes an equivalent durable historical record; unresolved validity
is surfaced as pending or an explicit blocker, never repinned or re-blessed against
current bytes. No new subcommand modes.

## Assumptions & Verification

| Assumption | Verified? | Source |
|------------|-----------|--------|
| `completion_observations`/`completion_review` do not exist in runtime today | ⬜ verify in Research | `skills/scripts/kosmic_completion.py` |
| Existing receipts under `.kosmic/work-receipts/` are sidecar-shaped with artifact-path proof maps | ⬜ verify in Research | `.kosmic/work-receipts/` |
| Completion behavior has machine-testable coverage under `tests/` | ⬜ verify in Research | `tests/` |
| `skills/references/work_completion.md` is the only consumer doc this story must cut over | ⬜ verify in Research | `skills/references/work_completion.md` |

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Focused tests red → green; existing math/proposal gate tests stay green untouched
- [ ] Real CLI smoke on bounded scratch records (positive, negative, legacy, retry)
- [ ] Independent two-axis review approved and embedded per the new shape
- [ ] `skills/references/work_completion.md` matches runtime; no regressions introduced

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-10-18 | Created | Initial draft; approved - awaiting implementation |
| 2026-10-18 | Approved | User approved this story as part of the full five-story set; awaiting implementation |
| 2026-10-18 | Started | Work start accepted at setup commit 09ca28c; implementation delegated |
