---
project_id: "kosmic"
subproject_id: "knowledge-first-notes-and-evidence-retirement"
status: "in_progress"
record_kind: "story"
local_id: "004"
created: 2026-10-18
updated: 2026-10-18
linked_prd: "../prd.md"
linked_epic: "../epics/epic-001.md"
linked_architecture: "../architecture.md"
depends_on:
  - ../stories/story-002.md
related_notes:
  - notes/note-writing-style.md
consumer_interface_change: true
review_base: "22559de"
review_round: 3
completion_review:
  reviewer: "OMP/Main"
  axes:
    standards:
      reviewer: "OpenAI Codex"
      decision: approved
    spec:
      reviewer: "OMP Story 004 independent code reviewer"
      decision: changes_requested
  decision: changes_requested
  review_base: "22559de"
  reviewed_revision: "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a"
  binding_scope: "Canonical source_revision binds the clean uncommitted delta only; reviewed commits are retained against fixed base 22559de. The final 04SPEC-5 predicate fix still awaits human review closure."
  scope: ["worktree:skills/scripts/kosmic_curation.py", "worktree:skills/scripts/kosmic_project_skills.py", "worktree:skills/references/curation_routine.md", "worktree:skills/README.md", "worktree:tests/test_kosmic_curation_prepare.py", "worktree:tests/test_kosmic_curation_stages.py", "project:subprojects/knowledge-first-notes-and-evidence-retirement/specs/stories/story-004.md"]
  findings: [{"id":"04STD-001","disposition":"Blocking","status":"resolved","resolution":"Cursor selection and first-bound checks run inside the scope transaction."},{"id":"04STD-002","disposition":"Blocking","status":"resolved","resolution":"Native manifest identifies active leases independently of snapshot readability."},{"id":"04STD-003","disposition":"Blocking","status":"resolved","resolution":"Finalizing, partial and unresolvable native states fail closed."},{"id":"04STD-004","disposition":"Blocking","status":"resolved","resolution":"Failed snapshot publication closes its new run or keeps its unresolved lease busy."},{"id":"04STD-005","disposition":"Blocking","status":"resolved","resolution":"Note reads and enumeration use verified no-follow directory descriptors."},{"id":"04STD-006","disposition":"Blocking","status":"resolved","resolution":"Checkpoint parents and publication use no-follow descriptor-relative operations."},{"id":"04STD-007","disposition":"Blocking","status":"resolved","resolution":"Foreign and unopenable handles produce typed refusals before mutation."},{"id":"04STD-008","disposition":"Blocking","status":"resolved","resolution":"Synopsis makes first-run bounds optional after initialization."},{"id":"04STD-1","disposition":"Blocking","status":"resolved","resolution":"Prepare uses native scratch authority and writes no Project checkpoint."},{"id":"04SPEC-1","disposition":"Blocking","status":"resolved","resolution":"Checkpoint selection and first-bound validation occur inside the transaction."},{"id":"04SPEC-2","disposition":"Blocking","status":"resolved","resolution":"Candidate and live-resource notes cannot be deliberately skipped."},{"id":"04SPEC-3","disposition":"Blocking","status":"resolved","resolution":"Bounded subtree scopes retain independent selections and checkpoints."},{"id":"04SPEC-4","disposition":"Blocking","status":"resolved","resolution":"A concurrent finalize cannot be bypassed by a stale first-run baseline."},{"id":"04SPEC-5","disposition":"Blocking","status":"resolved","resolution":"Exact native purpose comparison isolates missing snapshots to their own scope; regression passes. Code fixed after Round 3; Spec approval and human closure remain pending."}]
completion_observations:
  - criterion: "AC1 — Window selection: given checkpoint `L` and frozen cutoff `U`, prepare records transient revision-identity metadata for **every** interval-eligible note in the memnotes `notes/` scope whose semantic instant satisfies `L < changed_at <= U` — including `skill_candidate: false` notes — with candidate-flagged and live-resource notes listed first for review priority. Values equal to `L` are excluded, values equal to `U` are included; the semantic instant is frontmatter `updated` (creation-date fallback only when never updated, real UTC precision, never filesystem mtime). The review agent may deliberately skip creation-time-false candidates inside the window, but every eligible identity must receive an explicit disposition; no note outside the window is semantically reviewed."
    observation: "Bounds verified L-exclusive/U-inclusive with created-fallback and mtime independence; candidate-first ordering exercised; the real two-window smoke selected exactly the two eligible first-window notes (candidate flagged first) and only the genuine intervening note in the second window."
    source: "test_window_bounds_follow_l_exclusive_u_inclusive; test_created_fallback_selects_never_updated_notes; test_filesystem_mtime_is_never_consulted; test_explicit_skip_with_reason_is_a_valid_disposition; test_second_full_prepare_uses_the_persisted_cursor; actual smoke (story004-fresh-backend run, U1 2026-10-18T18:19:22.869602Z)"
  - criterion: "AC2 — Post-cutoff edits: a note saved after `U` is outside this run's snapshot and is reviewed on the next run; run metadata must not round such timestamps back into `[L, U]`."
    observation: "A post-cutoff revision on a prepared note defers without blocking; a brand-new post-cutoff note is never selected and the checkpoint still advances to exactly U."
    source: "test_post_cutoff_revision_defers_to_the_next_window; test_post_cutoff_note_defers_without_blocking_the_cursor"
  - criterion: "AC3 — Checkpoint advance: finalize advances the shared per-scope checkpoint to exactly `U` only after (a) the referenced work record is the currently governing record in `approved` or `in_progress` status, (b) its recorded review outcomes — from an independent semantic review, never inferred from the collector's exit status — give every prepared eligible identity an explicit disposition (reviewed, deliberately skipped, or no-action), and (c) the prepared revision identities revalidate against current instants. An absent disposition, an unprocessed in-window revision (drift), a failed proposal creation, or a missing/invalid work record leaves the checkpoint unchanged. An explicit no-action outcome is a successful full-scope result and advances the checkpoint."
    observation: "Missing/stale dispositions, in-window drift, and foreign records each leave the cursor unchanged; real no-action reviews advanced exactly to U1 then U2 in the smoke."
    source: "test_missing_disposition_leaves_checkpoint_unchanged; test_stale_revision_disposition_is_rejected; test_in_window_revision_after_prepare_blocks_advancement; test_foreign_work_record_finalize_never_touches_the_lease; smoke finalizes (checkpoint 2026-10-18T18:19:22.869602Z then 2026-10-18T19:12:17.352055Z)"
  - criterion: "AC4 — Targeted subset: a `--note` subset run uses the same window logic over that subset but never advances the full-scope checkpoint, whatever its outcome."
    observation: "Subset runs validate identically and never advance; out-of-window subset entries are rejected typed."
    source: "test_subset_run_never_advances_the_checkpoint; test_subset_entry_outside_window_is_rejected"
  - criterion: "AC5 — Serialization: two runs over the same scope serialize (single writer via the run handle); the second observes the first's checkpoint outcome rather than racing it."
    observation: "Active same-scope runs refuse busy; unresolved status/report states fail closed as busy without retiring the lease; terminal predecessors never block."
    source: "test_second_prepare_observes_active_run_as_busy; test_unresolved_run_status_is_never_retired_by_guessing; test_unresolvable_abandon_keeps_the_scope_busy; test_terminal_predecessor_never_blocks_a_fresh_run; smoke busy rejection (rc 2)"
  - criterion: "AC6 — Scope isolation: separate scopes keep independent checkpoints; a run over scope A neither reads nor advances scope B's checkpoint, and no note outside the declared scope's `notes/` tree (and never any external data store) is selected."
    observation: "Bounded subtree scopes keep independent checkpoints (including Round-2 snapshot-loss cross-scope isolation); scope paths are component-verified against escape."
    source: "test_scoped_subtrees_keep_independent_checkpoints; test_snapshot_loss_is_scoped_to_its_own_scope; test_scope_paths_are_bounded"
  - criterion: "AC7 — First run: prepare without `--from`/`--baseline` fails with a typed diagnostic instead of inventing a prior checkpoint or sweeping all history."
    observation: "Typed first-bound refusal before any selection; simultaneous --from and --baseline also refused (exactly one first bound)."
    source: "test_unbounded_prepare_requires_the_typed_first_bound; test_simultaneous_bounds_are_rejected; smoke bound-less prepare only ran after a persisted cursor existed"
  - criterion: "AC8 — Legacy date-only values: a date-only `updated`/`created` overlapping the boundary cannot establish an exact instant; the run records the ambiguity, excludes the note from semantic review this run, and blocks checkpoint advancement until a bounded disposition resolves it. No historical times are invented; no ambiguous note is silently dropped."
    observation: "Wholly-inside legacy days are reviewed with recorded uncertainty; boundary-overlapping days block advancement typed."
    source: "test_date_only_day_wholly_inside_is_reviewed_with_uncertainty; test_date_only_day_overlapping_boundary_blocks_advancement"
  - criterion: "AC9 — Bookkeeping does not self-requeue: syncing `skill_resources` linkage or recording a check does not bump the note's semantic `updated`, so it does not re-enter the next window; setting `skill_candidate` false→true (or intentional reassessment) is a semantic change and does bump `updated` (Story 002 metadata contract)."
    observation: "Story 002 validated readers are reused verbatim (never reimplemented); selection keys only on the `updated` frontmatter value, exercised by the drift/deferral pair."
    source: "test_in_window_revision_after_prepare_blocks_advancement; test_post_cutoff_revision_defers_to_the_next_window"
  - criterion: "AC10 — Selection vs review boundary: prepare may inspect scope-wide frontmatter to build the window, but semantic review covers only interval-eligible notes; a `skill_candidate: false` note outside the window is never promoted into review, and no out-of-window note is reviewed for any reason."
    observation: "Dispositions covering non-prepared notes are rejected typed before any mutation."
    source: "test_disposition_for_out_of_snapshot_note_is_rejected"
  - criterion: "AC11 — Live-resource staleness: non-empty `skill_resources` notes are checked for stale guidance only when they themselves fall in `(L, U]`; source context links may be consulted to understand a selected note, but linked context is never fresh-reviewed as a candidate."
    observation: "Live-resource notes participate only via their own window membership; enumeration never follows linked context."
    source: "test_skipping_a_live_resource_note_is_structurally_invalid; scope enumeration is per-note window logic (_classify) with no link traversal"
  - criterion: "AC12 — Nomination only: the review agent may nominate a candidate (existing proposal/review record concepts, as Dream's proposal flow does) but never auto-approves, publishes, installs, or triggers any model call from the CLI; no daily report artifact, durable candidate queue, evidence pack, or scheduler is introduced. An explicit no-action outcome requires neither a proposal nor extra paperwork."
    observation: "No model/queue/scheduler/report code paths exist in the module; nominations are recorded dispositions only. A real bounded nomination exercise on copied published kosmic material (existing-topic update nomination over parallel create, no auto-publish) was executed under managed scratch — see Progress Log."
    source: "static module read; AC14 nomination exercise (story004-ac14-nomination-demo run)"
  - criterion: "AC13 — Source links retained: run metadata and the work record reference notes by existing paths plus snapshot revision identities; neither copies note or dataset bytes into sidecar artifacts."
    observation: "Snapshot schema stores path/updated/revision (sha256 hexdigest)/skill_candidate/skill_resources only — identity field is the snapshot's `revision`; dispositions must quote it exactly."
    source: "test_disposition_for_out_of_snapshot_note_is_rejected; test_stale_revision_disposition_is_rejected"
  - criterion: "AC14 — Topic update preference: when review finds changed guidance affecting an existing skill topic, the nominated action is \"update the existing topic\" over creating a parallel one, and publication remains behind the existing human approval gate."
    observation: "Real bounded exercise: copied published kosmic note (usage topic cli-projection-commands pair) semantically changed under managed scratch; fresh independent review read the selected note plus the copied topic context and nominated updating the existing topic over parallel creation; no auto-approve/publish/install occurred."
    source: "story004-ac14-nomination-demo run; Curate004Semantic review recorded in the synthetic QC work record"
  - criterion: "AC15 — Work-record authority: the work record referenced by `--work-record` — an existing Story/QuickTask record in `approved` or `in_progress` status under existing completion governance — authorizes the review stage's writes to itself, any note-frontmatter writes this routine performs, and the checkpoint advance; prepare mutates only managed scratch under the existing managed-run/scratch authority and carries the same `--work-record`. The deterministic CLI stages alone never mutate the checkpoint or the vault, and no metadata artifact is created beyond the managed-run scratch metadata and the existing work record."
    observation: "Prepare creates no Project state (no .kosmic); foreign records are refused without touching another lease; the checkpoint appeared only at finalize and published exactly U1 then U2 through the verified component chain."
    source: "test_prepare_writes_no_project_checkpoint; test_foreign_work_record_finalize_never_touches_the_lease; test_symlinked_checkpoint_dir_is_refused_without_external_touch; actual smoke checkpoints (U1 2026-10-18T18:19:22.869602Z, U2 2026-10-18T19:12:17.352055Z)"
---

# Story 004: Incremental manual and scheduled curation routine

## User Story

As a memnotes maintainer,
I want one manual (or externally scheduled) agent routine that reviews only notes semantically
changed since the last successful full-scope check — deterministic CLI selection first, real
semantic review second, checkpoint finalization gated on an approved work record —
So that stale skill-material candidacy and in-use resource guidance are caught incrementally
without rescanning all history, without any promotion automaton, and without new queues or reports.

## Approved design (implemented)

One job invocation = three explicit stages; the Project CLI stages are deterministic and never
invoke a model:

1. **Prepare (deterministic CLI)** — `curation-prepare --work-record REF` freezes cutoff `U`
   internally at run start, selects eligible notes (`L < changed_at <= U`, candidate-flagged and
   live-resource notes first) and records transient revision-identity metadata for **every**
   interval-eligible note — including `skill_candidate: false` notes the reviewer may skip —
   into the existing managed-run workspace under its scratch authority. No checkpoint advance,
   no vault note mutation, no note/data byte copies — note references and revision identities
   only.
2. **Semantic review (agent, not CLI)** — the reviewing agent reads the selected notes in place
   and records outcomes (no-action, or nominations reusing existing proposal/review record
   concepts) in the **existing work record** opened for this curation run, including each
   reviewed note's reference and its snapshot revision identity. No model call is faked inside
   the CLI; the CLI has no review authority.
3. **Finalize (deterministic CLI)** — `curation-finalize --work-record REF` verifies the
   referenced work record is the currently governing record in `approved` or `in_progress`
   status, that the recorded review outcomes (semantic review performed independently — never
   inferred from the collector's exit status) cover the entire prepared eligible snapshot with
   an explicit disposition per note — reviewed, deliberately skipped (e.g. creation-time-false
   candidate), or no-action — then revalidates the prepared revision identities against current
   instants and advances the checkpoint to exactly `U`. Any absent/unaccounted eligible note,
   unprocessed in-window revision (drift), missing/invalid work record, or failed review
   outcome leaves the checkpoint unchanged. Post-`U` updates remain next-run by contract.

Prefer existing managed-run support (`skills/scripts/kosmic_runs.py` scratch/lease model) for
the transient run handle and snapshot metadata. There is no standalone `kosmic` binary: all
examples invoke `python3 skills/scripts/kosmic_project_skills.py <subcommand>`; all names below
are proposed.

```
python3 skills/scripts/kosmic_project_skills.py curation-prepare
    --project PROJECT --work-record REF
    [--scope notes]                # defaults to the memnotes notes/ scope
    [--from <UTC> | --baseline]    # first-run lower bound or intentional baseline
    [--note NOTE_SLUG ...]         # targeted subset; never advances the checkpoint

python3 skills/scripts/kosmic_project_skills.py curation-finalize
    --project PROJECT --run RUN_REF --work-record REF
```

No `--cutoff` date flag: `U` is frozen internally by prepare and carried in the run metadata
(kept inspectable so tests can pin the frozen `U`); the review stage needs no CLI at all.
The checkpoint store (proposed) is one small per-scope JSON in the project's `.kosmic/` area
holding the last-successful UTC instant plus run identity — no queue, no report files, and no
metadata artifact beyond the managed scratch metadata and the existing work record.

## Acceptance Criteria

- [ ] AC1 — Window selection: given checkpoint `L` and frozen cutoff `U`, prepare records transient revision-identity metadata for **every** interval-eligible note in the memnotes `notes/` scope whose semantic instant satisfies `L < changed_at <= U` — including `skill_candidate: false` notes — with candidate-flagged and live-resource notes listed first for review priority. Values equal to `L` are excluded, values equal to `U` are included; the semantic instant is frontmatter `updated` (creation-date fallback only when never updated, real UTC precision, never filesystem mtime). The review agent may deliberately skip creation-time-false candidates inside the window, but every eligible identity must receive an explicit disposition; no note outside the window is semantically reviewed.
- [ ] AC2 — Post-cutoff edits: a note saved after `U` is outside this run's snapshot and is reviewed on the next run; run metadata must not round such timestamps back into `[L, U]`.
- [ ] AC3 — Checkpoint advance: finalize advances the shared per-scope checkpoint to exactly `U` only after (a) the referenced work record is the currently governing record in `approved` or `in_progress` status, (b) its recorded review outcomes — from an independent semantic review, never inferred from the collector's exit status — give every prepared eligible identity an explicit disposition (reviewed, deliberately skipped, or no-action), and (c) the prepared revision identities revalidate against current instants. An absent disposition, an unprocessed in-window revision (drift), a failed proposal creation, or a missing/invalid work record leaves the checkpoint unchanged. An explicit no-action outcome is a successful full-scope result and advances the checkpoint.
- [ ] AC4 — Targeted subset: a `--note` subset run uses the same window logic over that subset but never advances the full-scope checkpoint, whatever its outcome.
- [ ] AC5 — Serialization: two runs over the same scope serialize (single writer via the run handle); the second observes the first's checkpoint outcome rather than racing it.
- [ ] AC6 — Scope isolation: separate scopes keep independent checkpoints; a run over scope A neither reads nor advances scope B's checkpoint, and no note outside the declared scope's `notes/` tree (and never any external data store) is selected.
- [ ] AC7 — First run: prepare without `--from`/`--baseline` fails with a typed diagnostic instead of inventing a prior checkpoint or sweeping all history.
- [ ] AC8 — Legacy date-only values: a date-only `updated`/`created` overlapping the boundary cannot establish an exact instant; the run records the ambiguity, excludes the note from semantic review this run, and blocks checkpoint advancement until a bounded disposition resolves it. No historical times are invented; no ambiguous note is silently dropped.
- [ ] AC9 — Bookkeeping does not self-requeue: syncing `skill_resources` linkage or recording a check does not bump the note's semantic `updated`, so it does not re-enter the next window; setting `skill_candidate` false→true (or intentional reassessment) is a semantic change and does bump `updated` (Story 002 metadata contract).
- [ ] AC10 — Selection vs review boundary: prepare may inspect scope-wide frontmatter to build the window, but semantic review covers only interval-eligible notes; a `skill_candidate: false` note outside the window is never promoted into review, and no out-of-window note is reviewed for any reason.
- [ ] AC11 — Live-resource staleness: non-empty `skill_resources` notes are checked for stale guidance only when they themselves fall in `(L, U]`; source context links may be consulted to understand a selected note, but linked context is never fresh-reviewed as a candidate.
- [ ] AC12 — Nomination only: the review agent may nominate a candidate (existing proposal/review record concepts, as Dream's proposal flow does) but never auto-approves, publishes, installs, or triggers any model call from the CLI; no daily report artifact, durable candidate queue, evidence pack, or scheduler is introduced. An explicit no-action outcome requires neither a proposal nor extra paperwork.
- [ ] AC13 — Source links retained: run metadata and the work record reference notes by existing paths plus snapshot revision identities; neither copies note or dataset bytes into sidecar artifacts.
- [ ] AC14 — Topic update preference: when review finds changed guidance affecting an existing skill topic, the nominated action is "update the existing topic" over creating a parallel one, and publication remains behind the existing human approval gate.
- [ ] AC15 — Work-record authority: the work record referenced by `--work-record` — an existing Story/QuickTask record in `approved` or `in_progress` status under existing completion governance — authorizes the review stage's writes to itself, any note-frontmatter writes this routine performs, and the checkpoint advance; prepare mutates only managed scratch under the existing managed-run/scratch authority and carries the same `--work-record`. The deterministic CLI stages alone never mutate the checkpoint or the vault, and no metadata artifact is created beyond the managed-run scratch metadata and the existing work record.

## Completion Observations

Per-criterion observations live in the frontmatter `completion_observations` list; each
`criterion` value quotes the normalized single-line Acceptance Criterion verbatim and carries
only evidence actually exercised. Story status remains `in_progress` — these observations are
not a completion claim; final Round-3 re-review and global integration are pending.

Provenance of smoke timestamps: every frontmatter `updated` stamp in the synthetic smoke
fixture (17:20/17:40 first window, 18:41 intervening) is a CONTROLLED SYNTHETIC STAMP chosen
to place notes inside specific windows — none is a captured creation instant (note bytes were
written at real run time, 19:12 for the intervening note). The smoke proves the window
CONTRACT under controlled stamps; no real-capture claim is made. Review identity integrity:
both finalize rounds validated the reviewer's transcribed revisions byte-exactly against the
prepared snapshots before advancing.

## Dependencies

- Depends on [Story 002](story-002.md): the `skill_candidate` / `skill_resources` metadata
  fields, the semantic-`updated` bump rules, and the legacy-default reading this story selects
  and reviews on.
- [Story 005](story-005.md) reconciles this story's consumer docs into the release cutover.

## Non-Goals

- No scheduler, daemon, cron installation, or automatic daily output: exactly one callable job;
  external scheduling (if ever wanted) invokes the same routine, nothing is installed here.
- No model invocation inside the Project CLI, no auto-promotion, keyword-only promotion,
  auto-publication, or auto-installation; approval/publication/installation gates are unchanged.
- No new durable candidate queue, confidence scores, per-dataset pointer notes, or evidence
  packs; no forced Dream reports (Dream's day-only collector cannot express this window and is
  not modified).
- No scan of external data repositories; scope stays within memnotes `notes/`.
- No retroactive re-review of already-checked history and no rewrite of historical completion
  receipts; curation snapshots current notes, never historical hashes.

## Tasks

### Phase 1: Research

- [x] Verify the Story 002 metadata contract as drafted (field names, bump rules, legacy
  defaults) and record any interface assumptions in Technical Notes.
- [x] Verify the existing subcommand/flag conventions and typed-error style in
  `skills/scripts/kosmic_project_skills.py` (subcommand registry around :4226) and the
  managed-run lease/snapshot support in `skills/scripts/kosmic_runs.py` to be reused.
- [x] Verify how an existing work record in `approved` or `in_progress` status authorizes
  mutations today (`kosmic_work.py` finish/scope handling and managed-run scratch authority)
  so prepare's and finalize's authority checks reuse the existing mechanisms.
- [x] Verify the Dream proposal/review record concepts reusable for nominations, and confirm
  no existing checkpoint artifact exists to collide with.
- [x] Confirm scope authority: which paths constitute the memnotes `notes/` scope and where a
  per-scope checkpoint file may live.

### Phase 2: Tests (TDD — write first, red then green)

- [ ] TEST-001: window boundary — notes at `updated == L` excluded, `== U` included, strictly
  between included, after `U` excluded (fixed clock, test vault).
- [ ] TEST-002: created-fallback for a never-updated note; fs mtime never consulted.
- [ ] TEST-003: finalize with a valid governing work record and a no-action outcome advances
  the checkpoint to `U`; failed/missing review dispositions, in-window snapshot drift, and a
  missing or unauthorized work record each leave it unchanged.
- [ ] TEST-003b: prepare snapshots revision identities for every interval-eligible note
  including `skill_candidate: false`; finalize rejects a work record whose dispositions omit
  any prepared identity, accepts an explicit "skipped — creation-time-false" disposition, and
  never infers completion from the collector/prepare exit status.
- [ ] TEST-004: `--note` subset run leaves the checkpoint unchanged; separate scopes do not
  leak; same-scope second run serializes after the first.
- [ ] TEST-005: prepare without `--from`/`--baseline` fails with a typed diagnostic.
- [ ] TEST-006: date-only value overlapping the boundary blocks advancement and is reported,
  not dropped or invented.
- [ ] TEST-007: bookkeeping-only linkage write does not re-enter the window;
  `skill_candidate` false→true does; out-of-window `candidate: false` is not reviewed.
- [ ] TEST-008: candidate-first ordering and in-window live-resource staleness selection;
  out-of-window linked context is never added as a review candidate.
- [ ] TEST-009: finalize without `--work-record` (or pointing at a record that is not the
  governing `approved`/`in_progress` record) is rejected and mutates nothing.

### Phase 3: Implementation

- [ ] IMPL-001: semantic-instant parsing and window selection over the declared scope.
- [ ] IMPL-002: per-scope checkpoint store with read/advance semantics; transient
  revision-identity run metadata in the existing managed-run workspace, written under its
  scratch authority with prepare carrying `--work-record`.
- [ ] IMPL-003: `curation-prepare` and `curation-finalize` subcommands with the flags above,
  including the governing work-record authority check (`approved`/`in_progress`), per-identity
  disposition coverage validation, and snapshot revalidation before any checkpoint publication.
- [ ] IMPL-004: review-outcome recording in the existing work record (reviewed note refs,
  revision identities, outcomes; nominations via existing proposal/review record concepts with
  update-existing-topic preference), no new artifacts beyond the checkpoint and run handle.

### Phase 4: Routine smoke and review

- [ ] Smoke: on a test vault with a fixed clock, run the full routine end to end — prepare,
  agent semantic review into the work record, finalize — covering first-run baseline, no-action
  advance, candidate nomination, subset non-advance, unauthorized finalize rejection, and a
  post-cutoff edit landing next run.
- [ ] Independent Standards review and independent Spec review, recorded per the current
  review contract.

## Routine Decision

No reusable deterministic procedure mechanics are introduced or materially changed beyond the
proposed `curation-prepare`/`curation-finalize` interfaces, their checkpoint store, and the
review handoff; promotion remains human-gated and review authority stays with the work record.

## Technical Notes

- Window contract and metadata names come from ADR-F (approved design, unimplemented); the
  PRD requirement is FR-011 and the ACs mirror its curation success-criteria bullet.
- Reused seams (verified present today): the single CLI entry with subparsers in
  `skills/scripts/kosmic_project_skills.py` (offline, stdlib-only, typed failures); managed-run
  lease/snapshot support in `kosmic_runs.py`; work-record authority from the existing
  `kosmic_work.py` governance. `curation-prepare`, `curation-finalize`, and the checkpoint
  store do not exist yet.
- The routine is one job invocation, not one subcommand: deterministic CLI stages bracket an
  agent semantic-review stage. The CLI never performs or simulates review; finalize consumes
  the work record's recorded dispositions and the frozen `U` from run metadata. Prepare's
  snapshot covers every interval-eligible revision identity — `skill_candidate: false` notes
  included — so finalize's coverage check has no silent absent notes; deliberate skips are
  recorded dispositions, and snapshot metadata holds identities only, never note bytes.
- The semantic instant is frontmatter `updated` with `created` fallback (Story 002 schema);
  UTC microseconds, e.g. `2026-10-17T09:30:00.123456Z`. Date-only legacy values are ambiguous
  at boundaries by design (AC8) — resolution is a bounded human disposition, not a heuristic.
- Snapshot revalidation before advancing catches the race "note changed in-window while the
  run was reviewing": finalize re-reads the selected notes' instants and refuses to advance
  the checkpoint on drift (AC3).
- Nominations reuse Dream's proposal/review record concepts without forcing Dream's day-based
  reports (ADR-F boundary); "update existing topic first" (AC14) follows the FR-004 refine/
  merge preference applied to skill material.

### Implemented research decisions (2026-10-18, implementation)

- **Module seam**: deterministic stages live in a new `skills/scripts/kosmic_curation.py`
  (`prepare_curation` / `finalize_curation` / `run_cli`), wired as two CLI subcommands in the
  existing `build_parser`/`run()` dispatch. The module imports `kosmic_runs` and `kosmic_work`
  with the established dual relative/absolute import pattern and pulls the Story 002 readers
  (`note_skill_candidate`, `note_skill_resources`, `validated_note_updated`), `parse_markdown`,
  and `load_project` from `kosmic_project_skills`, which imports the curation module lazily in
  its dispatch — no import cycle.
- **Serialization (mandatory chosen strategy)**: per-scope control JSON
  `<project>/.kosmic/curation/<scope>.json` holds `last_successful` plus the `active_run`
  reservation (run id, handle file, snapshot file, governing record, mode, window). A
  scope-specific NOFOLLOW flock guards each in-process transaction only; cross-CLI
  serialization is the reservation, never a pretend-persistent flock. Prepare: busy on a live
  reservation (`CURATION_BUSY`, exit 2); a terminal/out-of-grace predecessor is retired via
  the existing `finish_run(handle, "failed")` mechanism without touching
  `last_successful`. Unresolved orphans stay busy (fail closed); recovery is the existing
  managed-run gc/extend tooling, no new recovery command.
- **Authority**: every stage re-resolves the `--work-record` through
  `kosmic_work.resolve_work_record` (implementation kinds, `approved`/`in_progress`); prepare's
  managed run carries `record_run_provenance` provenance like `scratch begin` does; scratch
  authority follows the existing `gate_scratch_mutation` root semantics (Git-toplevel rooted
  managed-run root, no workdir-registration prerequisite). Finalize requires the SAME
  qualified record the reservation carries; a foreign record fails
  (`CURATION_RECORD_MISMATCH`) without touching the other run's lease — `finish_run` is only
  ever called on OUR reserved handle.
- **Window semantics**: `--from` accepts exact UTC instants only (`--from >= U` rejected);
  `--baseline` is the explicit zero-width first-run lower bound (empty window by design; prior
  notes neither swept nor rejected). Exactly one lower bound is required, else typed
  `CURATION_LOWER_BOUND_REQUIRED` (AC7). Legacy date-only `updated`/`created` certify the
  whole UTC day: wholly inside `(L, U]` → snapshot with `uncertain: true` (review allowed);
  wholly outside → skipped; boundary overlap → recorded `ambiguous`, excluded from review,
  blocks full-scope advancement until a bounded disposition (AC8, no invented times). Missing
  timestamp (no `updated`, no `created`) fails closed `CURATION_TIMESTAMP_UNKNOWN` — no
  history sweep, no per-note database.
- **Identities**: one consistent read per note — path (relative, reserved `index.md` excluded
  via the existing enumeration pattern), raw `updated`, sha256 revision identity, candidate
  flag, resources. Symlinked notes or parent components are rejected (bounded regular files,
  no follow). Sorted candidate/live-resource first (review priority). No note bytes copied.
- **Run metadata**: snapshot JSON lives under the reserved run's managed workspace
  (`<run>/output/curation-snapshot.json`), written atomically after the reservation is
  recorded; a lost snapshot fails finalize closed and releases the scope.
- **Review schema** (documented in `skills/references/curation_routine.md`): a
  `curation_review` frontmatter mapping in the EXISTING work record — `run_id` (must equal
  the reserved run), `reviewer`, `notes: [{path, revision, disposition, reason?}]` with
  disposition `reviewed | no-action | skipped` (`skipped` requires a reason). Finalize parses
  it structurally: wrong `run_id`, missing/stale revision, extra non-prepared disposition, or
  absent disposition each fail closed and release the reservation without advancing. An
  explicit no-action across full scope is a successful advance to exactly `U`.
- **Post-U drift**: revalidation flags only revisions whose current semantic instant is
  `<= U`; a revision after `U` defers to the next window and does not block (AC2/AC3).
- **Subset runs**: `--note` entries are normalized to bounded `notes/<relative>` paths; an
  entry outside the window is rejected; subset runs validate identically but never advance
  the checkpoint (AC4).
- **Focused regression suites**: parent ran `tests.test_kosmic_curation_prepare` and
  `tests.test_kosmic_curation_stages` after correcting the duplicate `work_record` test helper
  argument and the CLI exception-namespace catch; 22 tests passed. The full project suite and
  Standards/Spec reviews remain pending.
- **Synthetic end-to-end smoke (2026-10-18)**: under the governed Story004 scratch run, the
  actual CLI prepared only `notes/candidate.md` (`skill_candidate: true`) and
  `notes/noncandidate.md` (`skill_candidate: false`) from a throwaway Project; both identities
  had exact independent semantic no-action dispositions recorded by `Curate004Semantic` in
  the synthetic Quick Task. Actual `curation-finalize` returned `advanced: true`,
  `reviewed: 2`, `run_state: succeeded`, and checkpoint exactly
  `2026-10-18T17:18:38.625567Z`. No real Project notes or Shared Skill Library material were
  accessed; no nomination, proposal, publication, or installation was warranted.
  The synthetic outer managed run also terminalized as `succeeded`.

## Assumptions & Verification

| Assumption | Verified? | Source |
|------------|-----------|--------|
| Single CLI entry + subparser conventions reusable | ✅ | `skills/scripts/kosmic_project_skills.py:4226+` |
| ADR-F field names `skill_candidate`/`skill_resources` | ✅ (design, approved) | `../architecture.md` ADR-F |
| Managed-run lease/snapshot support fits the transient handle | ⬜ | Phase 1 research (`kosmic_runs.py`) |
| Existing work-record governance reusable for finalize authority | ⬜ | Phase 1 research (`kosmic_work.py`) |
| Dream proposal/review record concepts reusable for nominations | ⬜ | Phase 1 research |
| Story 002 metadata/bump contract as assumed | ⬜ | `../stories/story-002.md` |

## Definition of Done

- [ ] All acceptance criteria met
- [ ] All tests pass (TEST-001..009, including 003b)
- [ ] Real end-to-end routine smoke on a fixed-clock test vault (prepare → review → finalize)
- [ ] Independent Standards and Spec reviews recorded
- [ ] No scheduler, queue, daily report, CLI model call, or live-vault mutation outside an
  authorized work record

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-10-18 | Created | Initial draft; depends on Story 002; no implementation |
| 2026-10-18 | Approved | User approved this story as part of the full five-story set; awaiting implementation |
| 2026-10-18 | Revised | Review corrections: prepare/finalize handoff with work-record authority; python3 script invocation; in-window-only resource review; no cutoff/dry-run flags |
| 2026-10-18 | Started | Work start accepted at setup commit 22559de; implementation delegated |
| 2026-10-18 | Implemented | Phase 1 research verified; deterministic stages + CLI wiring + consumer docs; parent reports 22 focused regressions pass; independent two-note synthetic no-action prepare/review/finalize smoke advanced exactly to frozen U; full suite and Standards/Spec reviews pending |
| 2026-10-18 | Verified | Parent 40/40 GREEN (story004-final-40-green.log) after Round-2 authority/race/concurrency fixes; Standards Round-3 approved code scope; Spec Round-3 changes_requested with sole 04SPEC-5 code-fixed awaiting human closure |
| 2026-10-18 | Observed | Record metadata migrated (frontmatter completion_observations ×15 exact criteria, review_round 3, completion_review changes_requested, source_revision sha256 of kosmic_curation.py); real bounded AC14 nomination exercise under managed scratch: copied published kosmic pair cli-projection-commands byte-exact, baseline U0 2026-10-18T19:37:44.476493Z, genuine note change updated 2026-10-18T19:38:35Z, Curate004Semantic reviewed the selected revision and NOMINATED UPDATE EXISTING TOPIC kosmic/usage/cli-projection-commands (no parallel create, no auto-publish); finalize advanced exactly to U2 2026-10-18T19:38:35.561864Z with the nomination verbatim in the synthetic QC record — proposal production remains a separate follow-up gate |
