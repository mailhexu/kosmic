---
project_id: "kosmic"
subproject_id: "knowledge-first-notes-and-evidence-retirement"
status: done
record_kind: "story"
local_id: "005"
created: 2026-10-18
updated: 2026-10-18
linked_prd: "../prd.md"
linked_epic: "../epics/epic-001.md"
linked_architecture: "../architecture.md"
depends_on:
  - ../stories/story-001.md
  - ../stories/story-002.md
  - ../stories/story-003.md
  - ../stories/story-004.md
review_base: "139f91b"
review_round: 2
consumer_interface_change: true
proposal_required: false
related_notes:
  - notes/cli-projection-commands.md
  - notes/note-writing-style.md
  - notes/shared-domain-skill-library.md
completion_review:
  reviewer: "OMP/Main"
  axes:
    standards: {reviewer: "StandardsAxis005", decision: "approved"}
    spec: {reviewer: "SpecAxis005", decision: "approved"}
  decision: approved
  review_base: "139f91b"
  reviewed_revision: "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a"
  binding_scope: "Canonical source_revision binds the clean uncommitted delta; the full owned committed and formerly dirty source was independently reviewed against fixed base 139f91b and retained in commit 72e2d82. The user's manual Spec closure of Story 004 and its successful checked finish (receipt af0badba9f8fe6d3) are recorded separately and leave this binding and its scope unchanged."
  scope: ["worktree:skills/", "worktree:tests/", "worktree:docs/", "worktree:README.md", "worktree:CONTEXT.md", "worktree:memnotes/Skills/", "project:notes/", "project:skills/", "project:specs/skill-proposals/2026-09-24-day-delta-harvest-routine.md", "project:specs/skill-proposals/2026-10-11-migration-routine-decision.md", "project:subprojects/knowledge-first-notes-and-evidence-retirement/specs/", "project:.kosmic/work-receipts/", "project:log/kosmic-2026-10-18.md"]
  findings:
    - id: "05STD-01"
      disposition: "Blocking"
      status: "resolved"
      resolution: "Owned-topic reconciliation preserves unrelated actual-use IDs; the removal regression passes."
    - id: "05STD-02"
      disposition: "Blocking"
      status: "resolved"
      resolution: "All source-mapping paths enforce audience compatibility. Development-only sources cannot leak into Usage topics; both-audience sources serve both routes. Negative and positive real-consumer regressions pass."
    - id: "05SPEC-1"
      disposition: "Blocking"
      status: "resolved"
      resolution: "The prior library backup survives final published-tree validation; failure restores library, notes and pair to their call-entry state while preserving caller edits. Post-publication fault regression passes."
completion_observations:
  - criterion: |-
      Given a user invoking an obsolete evidence-pack mode after cutover (the `evidence_packs:` gate, sidecar-file acceptance inputs, stable-note `evidence:` path checks, and the forced pack-to-note distillation chain), when the command is run, then the invocation is rejected as unknown/unsupported — no no-op shim, alias, or replacement dossier under another name or hidden directory.
    observation: |-
      Focused retirement suite drives the retired pack inputs and gates directly and observes explicit unsupported rejection with no shim, alias or replacement dossier; `reject_retired_completion_inputs` runs before any new completion, `task_distill`/Task 9 is deleted without replacement, and completed originals are untouched.
    source: |-
      Writer-repo isolation run `20261018T151753Z-knowledge-first-isolatio-d6030fcb4465c9b7060cecb911c5e7c7` scratch `story005-retirement-15-green.log` (15/15 OK incl. unsupported-old-input cases); `tests/test_pack_retirement.py`.
  - criterion: |-
      Given the cutover CLI, when `--help` and current docs/templates are exercised once via a throwaway CLI/content smoke run, then they no longer name the retired modes; this is a one-time cutover smoke, not a permanent test of help text or source wording.
    observation: |-
      One-off content smoke in the managed whole-workflow run grepped `--help` / `work finish --help` and the exercised current docs/templates surfaces for retired-mode naming: 0 occurrences; the cutover removed the retired naming (Task 9 deleted, ADR 0002 references superseded); no permanent content-text test was added.
    source: |-
      Writer run `20261018T191012Z-smokewholeworkflow005-sy-db62268080b2ac6649343ec2e7d929bd` scratch `sw5-cycle2-report.md` (help grep 0); git diff 139f91b over skills/docs/templates.
  - criterion: |-
      Given the surviving commands (`work start/finish` identity/scope checks, `check-math`, MathDoc structural validation, derivation pairing, proposal gates, completion linkage, receipt validation), when invoked per their remaining duties, then the surviving invariants and gates are unchanged (including Story 003's changed completion proof contract — record-embedded observations and receipts, no sidecar inputs); only pack-specific duties were removed.
    observation: |-
      Surviving duties exercised green: `work start/finish` identity+scope (receipted finish scoped to `worktree:src/purefn.py`, project story record and `.kosmic`), `check-math`/MathDoc validation under Python 3.12.10/Sympy 1.14.0, source-bound proposal gate, receipt validation before and after finish (`completion gate passed`, rc=0); Story-003 record-embedded contract enforced (typed REVIEW_INVALID refusal while `completion_review` was absent; sidecar inputs no longer accepted on new records).
    source: |-
      Smoke run `sw5-cycle2-report.md` (exact argv/rc/order + receipts); `story005-retirement-15-green.log` (15/15 ALL PASS); `story005-final-publication-15-green.log` (15/15 ALL PASS).
  - criterion: |-
      Given an existing task record containing `impact.md` generation/publication ledger entries and a forced Task 9 note-writing step, when the cutover guidance applies within already-existing task records, then those entries/steps are retired in place without creating any replacement ledger, and finished records are never edited.
    observation: |-
      Ledger/step duties removed from current guidance with no replacement ledger or dossier; bounded current-record inventory found no unfinished task still carrying both an `impact.md` publication duty and a forced Task 9 step (remaining occurrences are immutable completed records/curated snapshots); the two actual draft proposal pack keys were retired in place and the five done proposals untouched; completed-record immutability test green.
    source: |-
      This record body sections "Implementation inventory and authority correction" and "Historical proposal readers and pending current work"; `story005-retirement-15-green.log` (completed-record immutability).
  - criterion: |-
      Given docs, references, templates, glossary, proposal inputs, and generated guidance that named Evidence Packs, when the cutover completes, then current consumers describe the knowledge-first workflow with `docs/adr/0002` superseded by a new ADR written at implementation ("knowledge-first notes; no separate evidence layer"); the new ADR supersedes by reference and the old file is preserved, not rewritten.
    observation: |-
      ADR 0004 written at implementation supersedes `docs/adr/0002` by reference with the old file preserved unrewritten; docs/references/templates/glossary/proposal-input guidance cut over (Task 9 chain deleted, no replacement dossier); the smoke consumed the new current templates end-to-end with retired-mode grep 0.
    source: |-
      `docs/adr/0004-knowledge-first-notes.md`; this record body "Implementation inventory and authority correction"; smoke run `sw5-cycle2-report.md`.
  - criterion: |-
      Given generated projections (STATUS.md and other generated topics/guidance), when any regeneration is needed, then it is produced only by the canonical publisher path (bounded per ADR-E) and never hand-edited; installation of any changed skill remains an unchanged separate approval boundary — this story refreshes and publishes nothing into the live skill set.
    observation: |-
      The smoke STATUS render went through the canonical publisher path only (planning-authority bounded path), producing the canonical STATUS row and terminal commit; generated topics were rebuilt only by the real `generate-library` publication (no hand-edited projections); the live vault/skill set was not refreshed or installed — installation remains a separate unchanged approval boundary.
    source: |-
      Smoke run `sw5-cycle2-report.md` (post-finish canonical STATUS row, commit 152188f); this record body "Current topic identity recovery".
  - criterion: |-
      Given old immutable curated inputs (historical proposal input snapshots, source pins referenced by completed records, completed historical doc records), when current readers and validators run, then they continue to support and validate those inputs against their original recorded bytes; nothing is repinned, re-blessed, refreshed to current bytes, or re-validated "live" in a way that revokes or blesses history; unresolved validity surfaces as pending/blocker per Story 003's rules.
    observation: |-
      Corrected per-proposal reader validated the five done proposals plus draft `2026-10-11-migration-routine-decision` against recorded historical pins with captured files byte-verified; nothing repinned or re-blessed; unresolved validity surfaces pending: draft `2026-09-24-day-delta-harvest-routine` stays explicitly blocked by its stale `notes/dream-reflection-workflow.md` pin (manifest stale, intentionally not repinned; continuing needs a separately governed fresh capture).
    source: |-
      This record body "Historical proposal readers and pending current work"; `story005-retirement-15-green.log` (history capture / draft freshness cases).
  - criterion: |-
      Given the completed QuickTask `restore-evidence-inventories-for-projection-hygiene`, which conflicts with this retirement, when supersession is recorded, then this Story — once user-approved and governing — records the supersession **by reference** (naming its record path/identity and the superseding rationale) within its own record; its pack-inventory rows are not executed post-cutover, and the completed historical record itself is byte-for-byte unmutated.
    observation: |-
      Supersession recorded by reference in this record's own "Implementation inventory and authority correction" section naming canonical path `specs/quick-tasks/restore-evidence-inventories-for-projection-hygiene.md` and captured SHA-256 `e66ee0a8…`; no restoration rows executed post-cutover and the QuickTask file is unmutated. Honest correction preserved: the inspected record is draft, not completed, with no completion receipt — changing no historical approval.
    source: |-
      This record body "Implementation inventory and authority correction"; `memnotes/Projects/kosmic/specs/quick-tasks/restore-evidence-inventories-for-projection-hygiene.md`.
  - criterion: |-
      Given a completed record predating the cutover, when its completion is later inspected, then its verdict, reviewer identities, `source_revision`/`review_base` binding, and receipt validity are intact — the cutover changed no recorded approval.
    observation: |-
      Completed-record immutability held: the five done proposals and legacy receipts validate against unchanged original recorded bytes; no recorded verdict, reviewer identity or `source_revision`/`review_base` binding was changed by the cutover (typed immutability and legacy-receipt validation cases green).
    source: |-
      `story005-retirement-15-green.log` (15/15 OK); `story004-final-40-green.log` (40/40 OK); this record body (five done proposals untouched).
  - criterion: |-
      TBUpy retracted Si interpretation (bounded copy): the correction presents the supported current conclusion first and labels the superseded retracted interpretation without erasing the failed approach; no recorded physics verdict changes.
    observation: |-
      Executed on bounded copy `demo1` in managed demo run `20261018T172001Z-knowledge-first-bounded-2c3d90264c3455cb6dd1d95ffe06147c`: retraction-first correction leads with the supported conclusion and labels the superseded interpretation, preserving settings/failed approach/negative findings; original note byte-identical after (SHA-256 `e2047fd2…`); content review approved by `ReviewLocality005` Round 2.
    source: |-
      This record body "Bounded demonstrations and content review" (paths + 10 original hashes); demo run scratch `demo1/transformed/formal_charge_campaign.retraction-first.md`.
  - criterion: |-
      TB2J `bruno-realspace-options` (bounded copy): the conflicting stable/draft metadata becomes one coherent note; differing physical settings, uncertainty, and negative results survive consolidation and existing links resolve.
    observation: |-
      Executed on bounded copy `demo2`: one active metadata header, dated inner draft stamp kept as provenance, B FFT/C local-approximate settings and limitations preserved, implementation claim bounded as pending verification, copied dependencies pointing at resolving source-vault targets; original byte-identical after (SHA-256 `30201c46…`); content review approved Round 2 including the corrected dependency link.
    source: |-
      This record body "Bounded demonstrations and content review"; demo run scratch `demo2/transformed/bruno-realspace-options.coherent.md`.
  - criterion: |-
      Kosmic `evidence/2026-10-15-completion-status-coherence` (bounded copy): unique/uncommitted snapshots are copied to durable recovery before any transformation; duplicated paperwork is classified disposable without touching the originals; no real data is destroyed.
    observation: |-
      All six pack files copied into a standalone recovery Git fixture at commit `7b48a499f0107c044482cb84efc593ccea40aeac` before classification (process transcript records the order; timestamps support but do not independently prove chronology); disposable-classified snapshots freshly compared byte-for-byte with tracked host files, unique JSON/manifest content retained; no original deleted; six originals byte-identical after, plus durable Git recovery at baseline commit `201438f…` on branch `kosmic-kf-baseline-d6030fcb`.
    source: |-
      This record body "Bounded demonstrations and content review" and "Current topic identity recovery"; demo run scratch `demo3`.
  - criterion: |-
      abinit NiO J₀² campaign (bounded copy): dataset-local metadata, units, run settings, schema, calibration, and single-dataset interpretation stay embedded or adjacent to the native data near its native store; only the independently reusable interpretation surfaces as a note with precise source links; no per-dataset duplicate note/pointer is manufactured and no numerical dataset is flattened into prose or lost.
    observation: |-
      Executed on bounded copy `demo4/dataset-adjacent-copy`: verbatim report and receipt documents retained adjacent to the copy; native archive `/STORAGE1/…/nio_j02` was available read-only and NOT copied (its `archive_manifest.json` stays native); the reusable note carries general response-gate pitfalls with precise native/source references; dielectric/elastic/phonon failures, non-isolated-J interpretation, open root cause, uncertified status and administrative blocker remain explicit; original report/archive-root bytes unchanged (`9e04ed85…`, `92515b6b…`).
    source: |-
      This record body "Bounded demonstrations and content review"; demo run scratch `demo4`.
  - criterion: |-
      Given the finite source→destination disposition map covering the audited legacy packs, when drafted, then it lives only in a future separately approved migration work record at execution time (never a universal registry, never authored in this story's runtime); every demonstration in this story operates on bounded copies only — no live-vault deletion, migration, or installation occurs.
    observation: |-
      No disposition map authored in this story and no universal registry created; all four demonstrations ran on bounded copies under the managed demo run; native/live/shared-vault originals never modified and no deletion, migration or installation occurred (all ten original SHA-256 values unchanged; honest no-native-terminal-proof item for the orphan old-original run preserved in the body).
    source: |-
      This record body "Bounded demonstrations and content review"; demo run `20261018T172001Z-knowledge-first-bounded-2c3d90264c3455cb6dd1d95ffe06147c`.
  - criterion: |-
      Given a note whose `skill_resources` actual-use list changes after approved publication or removal of a skill topic, when the sync updates the note's frontmatter, then the note's source bytes change while its semantic `updated` timestamp stays unchanged (bookkeeping write, not a semantic update).
    observation: |-
      Actual observation: the three current topics' notes carry their already-published stable IDs in `skill_resources` with semantic `updated` unchanged by bookkeeping; fresh source backups preceded the three staged backlink additions; the first publication attempt failed the 12288-byte Topic cap and its staged fields were restored before the consolidated canonical note published. Recorded as historical actual; final state: the focused publication suite is 15/15 ALL PASS after the compatibility fix (`story005-final-publication-15-green.log`) and the fresh real canonical CLI `generate-library` publication is GREEN across all six identities (final producer proof, next entries).
    source: |-
      This record body "Current topic identity recovery"; writer-repo isolation run `story005-final-publication-15-green.log` (15/15 ALL PASS; pre-fix 14/14 retained above as finding history).
  - criterion: |-
      Given that byte change, when the same approved publication/removal flow reconciles the affected current generated projections and library `source_sha256`/manifest entries against the note's final bytes, then the refreshed artifacts load coherently against the final source, preserving the exact reviewed scope — no stale-pin blessing, and installation remains a separate unchanged approval gate; historical curated snapshots and historical work-record pins are untouched (current-source consistency, not repinning history).
    observation: |-
      Publication reconciles only owned resource IDs and rebuilds the pair plus complete current topic bodies and raw source pins. All 15 publication regressions pass, including post-publish rollback, foreign-ID preservation, Development-only-to-Usage rejection and valid both-audience consumers. The real six-topic publisher and consumer pass with semantic `updated` unchanged by bookkeeping and old ledger bytes unchanged. Historical captures and pins remain untouched.
    source: |-
      `story005-final-publication-15-green.log` (15/15); `knowledge-first-final-cutover.log` (31 modules, 0 failed, 188.99 s); `dogfood-library-publication.log` (six final source identities/pins/resources and actual consumer); this record's Current topic identity recovery section.
  - criterion: |-
      Given `skill_resources` metadata, when written by any flow in this story, then it contains only stable topic IDs — no content hashes and no proposed/unapproved targets.
    observation: |-
      `skill_resources` written by the actual publication flow carries only already-published stable topic IDs (no content hashes, no proposed/unapproved targets); Round-1 finding 05STD-01 (out-of-scope actual-use IDs) fixed and covered by the focused publication suite (final: 15/15 ALL PASS, `story005-final-publication-15-green.log`).
    source: |-
      `story005-final-publication-15-green.log` (15/15 ALL PASS); this record body "Current topic identity recovery".
  - criterion: |-
      Given a genuine consumer holding a source pin whose recorded hash no longer matches the note's current bytes, when the approved refreshed flow runs, then the consumer loads against the coherent final source (behavior test on a real consumer; no wording/copy assertions). Existing source-pin primitives are the expected seam: `project_skills.py` lines 1273-1275, 1313-1315, 1648-1650; shared library lines 951-962 (source-byte hashes) — confirmed as implementation-time starting points, not a completed inventory.
    observation: |-
      The actual `resolve_library` → `load_recipe_packet` consumer loaded coherent final CLI guidance after three legacy source identities were recovered from verified prior-publication context. All six catalog pins match final raw note bytes and every current topic persists its stable source identity. Fifteen publication regressions and the real six-topic publication/load pass; no historical curated input was repinned.
    source: |-
      `story005-final-publication-15-green.log` (15/15); `dogfood-library-publication.log` (6/6 and actual consumer); `knowledge-first-final-cutover.log` (31 modules, 0 failed); this record's Current topic identity recovery section.
  - criterion: |-
      Given a real test-vault invocation of the full workflow (`work start` → edit → `work finish --scope`), when completed, then no `evidence/` tree, mandatory sidecar, or forced pack-to-note step is produced; embedded criterion observations and the two-axis independent review are still checked; receipted completion renders via the canonical publisher; and a session yielding no reusable finding manufactures no note.
    observation: |-
      Managed whole-workflow smoke cycle 2 on a real test vault: `work start` → real `src/purefn.py` change → FULL `check-completion` BEFORE finish (exact argv cited, rc=0 "completion gate passed") → receipted `work finish` (receipt `7dbd9da571c8807e.json`, payload record_sha256/proof `f548089d…`); no `evidence/` tree, sidecar or pack-to-note step produced; embedded observations + two-axis review enforced (typed REVIEW_INVALID refusal before `completion_review` embed; full gate also caught and fixed a `depends_on` path defect); post-finish `check-completion` passed, `work show` done, canonical STATUS row; pre-seeded note `mean-normalization.md` unchanged (sha256 `04fe9b90…`, zero notes diff) and the no_action finding manufactured no note. Cycle-1 gap (no pre-receipt full check) admitted and remediated on the new cycle-2 story; cycle-1 receipt `16d64c87ce5c446e.json` preserved historical.
    source: |-
      Writer run `20261018T191012Z-smokewholeworkflow005-sy-db62268080b2ac6649343ec2e7d929bd` scratch `sw5-cycle2-report.md` + `cycle2-verified-values.json` + receipts `7dbd9da571c8807e.json`/`16d64c87ce5c446e.json` under the smoke worktree `.kosmic/work-receipts/`.
  - criterion: |-
      Given the same smoke run, when math and proposal surfaces are exercised, then `check-math`, MathDoc structural validation, derivation pairing, completion linkage, and proposal/source binding still pass — verification was not weakened by locality (ADR-D(b)).
    observation: |-
      Same smoke exercised the math and proposal surfaces: `check-math` and MathDoc structural validation (derivation pairing included) passed under the run venv (Python 3.12.10/Sympy 1.14.0) on the real total-function change; the source-bound proposal validated as DRAFT no_action with `proposal_required` false and human approval left pending; completion linkage exercised by the receipted finish; focused suites (15/15 retirement, 15/15 publication including the positive both-audience case, 40/40 story-004) and the integrated release-verified suite (31 modules, 0 failed) confirm the verification surfaces were not weakened.
    source: |-
      Smoke run `sw5-cycle2-report.md` + `cycle2-verified-values.json`; `story005-retirement-15-green.log`; `story005-final-publication-15-green.log`; `story004-final-40-green.log`.
---

# Story 005: Coherent consumer cutover, legacy authority resolution, and bounded knowledge demonstrations

## User Story

As a kosmic maintainer,
I want every consumer of the retired evidence-pack machinery (CLI checks, docs, templates, generated guidance, proposal inputs, migration references) cut over consistently in one release, with legacy authority resolved by reference rather than mutation,
So that runtime and documentation never disagree, historical completed records and curated inputs stay verifiable as originally produced, and the four audited content transformations are demonstrated safely on bounded copies before any separately approved live-vault batch.

This story lands last (after [Story 001](story-001.md), [Story 002](story-002.md), [Story 003](story-003.md), [Story 004](story-004.md)) for a clean release cutover, not runtime mixed with stale guidance. It owns the cross-cutting retirement surface: obsolete CLI modes and Task 9 forced pack-to-note chain, `impact.md` ledger entries, ADR 0002 supersession, the conflicting completed inventory QuickTask, existing proposals and source pins, generated topics/guidance, and the legacy disposition authority boundary. It is the release integrator, not an excuse for earlier stories shipping mixed runtime/docs; each earlier story updates its own consumers, and this story reconciles what remains.

## Acceptance Criteria

### Retirement without shims (FR-008, ADR-D(a))

- [ ] Given a user invoking an obsolete evidence-pack mode after cutover (the `evidence_packs:` gate, sidecar-file acceptance inputs, stable-note `evidence:` path checks, and the forced pack-to-note distillation chain), when the command is run, then the invocation is rejected as unknown/unsupported — no no-op shim, alias, or replacement dossier under another name or hidden directory.
- [ ] Given the cutover CLI, when `--help` and current docs/templates are exercised once via a throwaway CLI/content smoke run, then they no longer name the retired modes; this is a one-time cutover smoke, not a permanent test of help text or source wording.
- [ ] Given the surviving commands (`work start/finish` identity/scope checks, `check-math`, MathDoc structural validation, derivation pairing, proposal gates, completion linkage, receipt validation), when invoked per their remaining duties, then the surviving invariants and gates are unchanged (including Story 003's changed completion proof contract — record-embedded observations and receipts, no sidecar inputs); only pack-specific duties were removed.
- [ ] Given an existing task record containing `impact.md` generation/publication ledger entries and a forced Task 9 note-writing step, when the cutover guidance applies within already-existing task records, then those entries/steps are retired in place without creating any replacement ledger, and finished records are never edited.

### Docs and generated surfaces (FR-008, FR-009)

- [ ] Given docs, references, templates, glossary, proposal inputs, and generated guidance that named Evidence Packs, when the cutover completes, then current consumers describe the knowledge-first workflow with `docs/adr/0002` superseded by a new ADR written at implementation ("knowledge-first notes; no separate evidence layer"); the new ADR supersedes by reference and the old file is preserved, not rewritten.
- [ ] Given generated projections (STATUS.md and other generated topics/guidance), when any regeneration is needed, then it is produced only by the canonical publisher path (bounded per ADR-E) and never hand-edited; installation of any changed skill remains an unchanged separate approval boundary — this story refreshes and publishes nothing into the live skill set.

### Legacy authority by reference (ADR-C/D, NFR-002)

- [ ] Given old immutable curated inputs (historical proposal input snapshots, source pins referenced by completed records, completed historical doc records), when current readers and validators run, then they continue to support and validate those inputs against their original recorded bytes; nothing is repinned, re-blessed, refreshed to current bytes, or re-validated "live" in a way that revokes or blesses history; unresolved validity surfaces as pending/blocker per Story 003's rules.
- [ ] Given the completed QuickTask `restore-evidence-inventories-for-projection-hygiene`, which conflicts with this retirement, when supersession is recorded, then this Story — once user-approved and governing — records the supersession **by reference** (naming its record path/identity and the superseding rationale) within its own record; its pack-inventory rows are not executed post-cutover, and the completed historical record itself is byte-for-byte unmutated.
- [ ] Given a completed record predating the cutover, when its completion is later inspected, then its verdict, reviewer identities, `source_revision`/`review_base` binding, and receipt validity are intact — the cutover changed no recorded approval.

### Bounded-copy demonstrations (ADR-D, NFR-002, PRD success criteria)

- [ ] TBUpy retracted Si interpretation (bounded copy): the correction presents the supported current conclusion first and labels the superseded retracted interpretation without erasing the failed approach; no recorded physics verdict changes.
- [ ] TB2J `bruno-realspace-options` (bounded copy): the conflicting stable/draft metadata becomes one coherent note; differing physical settings, uncertainty, and negative results survive consolidation and existing links resolve.
- [ ] Kosmic `evidence/2026-10-15-completion-status-coherence` (bounded copy): unique/uncommitted snapshots are copied to durable recovery before any transformation; duplicated paperwork is classified disposable without touching the originals; no real data is destroyed.
- [ ] abinit NiO J₀² campaign (bounded copy): dataset-local metadata, units, run settings, schema, calibration, and single-dataset interpretation stay embedded or adjacent to the native data near its native store; only the independently reusable interpretation surfaces as a note with precise source links; no per-dataset duplicate note/pointer is manufactured and no numerical dataset is flattened into prose or lost.
- [ ] Given the finite source→destination disposition map covering the audited legacy packs, when drafted, then it lives only in a future separately approved migration work record at execution time (never a universal registry, never authored in this story's runtime); every demonstration in this story operates on bounded copies only — no live-vault deletion, migration, or installation occurs.

### Source consistency after approved publication/removal (FR-010, ADR-F, current-source)

- [ ] Given a note whose `skill_resources` actual-use list changes after approved publication or removal of a skill topic, when the sync updates the note's frontmatter, then the note's source bytes change while its semantic `updated` timestamp stays unchanged (bookkeeping write, not a semantic update).
- [ ] Given that byte change, when the same approved publication/removal flow reconciles the affected current generated projections and library `source_sha256`/manifest entries against the note's final bytes, then the refreshed artifacts load coherently against the final source, preserving the exact reviewed scope — no stale-pin blessing, and installation remains a separate unchanged approval gate; historical curated snapshots and historical work-record pins are untouched (current-source consistency, not repinning history).
- [ ] Given `skill_resources` metadata, when written by any flow in this story, then it contains only stable topic IDs — no content hashes and no proposed/unapproved targets.
- [ ] Given a genuine consumer holding a source pin whose recorded hash no longer matches the note's current bytes, when the approved refreshed flow runs, then the consumer loads against the coherent final source (behavior test on a real consumer; no wording/copy assertions). Existing source-pin primitives are the expected seam: `project_skills.py` lines 1273-1275, 1313-1315, 1648-1650; shared library lines 951-962 (source-byte hashes) — confirmed as implementation-time starting points, not a completed inventory.

### Whole-system smoke (integration gap coverage)

- [ ] Given a real test-vault invocation of the full workflow (`work start` → edit → `work finish --scope`), when completed, then no `evidence/` tree, mandatory sidecar, or forced pack-to-note step is produced; embedded criterion observations and the two-axis independent review are still checked; receipted completion renders via the canonical publisher; and a session yielding no reusable finding manufactures no note.
- [ ] Given the same smoke run, when math and proposal surfaces are exercised, then `check-math`, MathDoc structural validation, derivation pairing, completion linkage, and proposal/source binding still pass — verification was not weakened by locality (ADR-D(b)).

## Tasks

### Phase 1: Research

- [ ] Inventory every current consumer of retired machinery: CLI modes/gate keys, templates, `task_distill.md`/Task 9 references, glossary, docs naming Evidence Packs, proposal inputs, generated-topic guidance, migration consumers naming `docs/adr/0002` — record exact file/mode list in Technical Notes.
- [ ] Confirm the ADR-E-bounded publisher path and which projections refresh at cutover; confirm no new subcommand modes are introduced.
- [ ] Locate the completed QuickTask record and the historical proposal/source-pin inputs; record their exact paths, hashes, and the reference fields the in-Story supersession entry must carry.
- [ ] Scope the four bounded-copy demonstration inputs and their copy/sandbox locations; verify original paths stay read-only throughout.
- [ ] Document findings and any human clarifications in Technical Notes.

### Phase 2: Tests (TDD — red first, only where machine-testable)

- [ ] TEST-001: invoking each retired pack mode is rejected as unknown/unsupported; no shim routes to a no-op (runtime behavior, not help/source text assertions).
- [ ] TEST-002: surviving commands' remaining duties pass unchanged (identity/scope, `check-math`, pairing, proposal/source binding, receipt validation vs unchanged original bytes — including legacy sidecar-byte receipts) under Story 003's record-embedded proof contract.
- [ ] TEST-003: completed-record immutability — cutover writes never touch finished records; the superseding section references, does not modify, the QuickTask.
- [ ] TEST-004: a real consumer loads regenerated guidance/metadata through the canonical publisher path (or, for the bounded derived STATUS output, the renderer authority path) and shows meaningful behavior — writes confined to the derived target, no source or live-skill mutation, `work finish` still refuses planning-phase records (Story 001 boundary holds in the integrated release). Help/docs/naming consistency stays in the throwaway Phase 4 content smoke, not a permanent content-text test.
- [ ] Content-review-only items (the four bounded-copy content demonstrations — checksum smoke that originals are byte-identical before/after, durable recovery existing before any copy is classified disposable; lifecycle prose quality; supersession rationale wording) are routed to the Phase 4 demonstration/review pass, not made permanent copy/source-text tests and not faked as machine tests.

### Phase 3: Implementation

- [ ] IMPL-001: remove obsolete CLI modes and the Task 9 forced pack-to-note chain; reuse only meaningful existing duties; delete rather than stub.
- [ ] IMPL-002: retire `impact.md` ledger entries and forced note gates within existing task-record guidance; no replacement ledger.
- [ ] IMPL-003: write the new superseding ADR; update docs/templates/references/glossary/proposal-input guidance; keep historical doc records labeled, untouched.
- [ ] IMPL-004: after this Story's own user approval, record in this governing work record (Story 005 itself) the supersession of the conflicting QuickTask by reference — no extra record is created.
- [ ] IMPL-005: regenerate affected projections via the canonical publisher only.
- [ ] IMPL-007: in the approved publication/removal flow, sync `skill_resources` (stable topic IDs only, no hashes/proposed targets) and reconcile affected current generated projections and library `source_sha256`/manifests against the note's final bytes, preserving exact reviewed scope — no stale-pin blessing, no automatic installation, historical snapshots/pins untouched.
- [ ] IMPL-006: execute the four bounded-copy demonstrations in a sandbox; record copy locations and pre/post checksums of originals in the work record.

### Phase 4: Review

- [ ] Real whole-CLI smoke in a test vault per the acceptance criteria above.
- [ ] Independent Standards review (both axes, named reviewers, fixed `review_base`) covering the cutover completeness and shim-absence.
- [ ] Independent Spec review covering FR-008/FR-009 traceability, ADR-D compliance, NFR-002 safety, and that no live-vault action or verdict change occurred. Destructive/live disposition and installation remain separate later approvals; no additional human gate is inserted before any disposition plan is drafted.

## Technical Notes

- Grounding: the seams below come from the approved Architecture (ADRs B–F) and files actually inspected while drafting (`docs/adr/0002-single-evidence-layer.md`; `skills/references/task_distill.md` (Task 9); `kosmic_project_skills.py` renderer (`generate_status`/`render_status`, bounded per ADR-E by Story 001); `impact.md` ledger entries inside existing task records; generated STATUS.md). Exact mode/gate keys and the full remaining-consumer inventory are Phase 1 research deliverables — this list is the bounded starting map, not a claim of completed verification.
- The new ADR is written **during implementation of this story**, per ADR-D(a). Supersession of the conflicting QuickTask is recorded in this Story's own record, effective once Story 005 is itself user-approved and governing; no extra superseding record is created, and the superseded historical record is never mutated.
- Legacy receipts remain verifiable against unchanged historical sidecar bytes (Story 003 contract); current readers keep supporting them until a separately approved migration establishes equivalent durable historical records. Missing/unresolved records surface pending/blocker; never re-pinned or re-blessed.
- The source→destination disposition map is **not** authored here. It lives in a future, separately approved migration work record at execution time. This story only demonstrates on bounded copies and honors the authority boundary.
- Demonstrations never change a recorded scientific verdict, destroy real data, or flatten a dataset into prose; originals are checksummed before and after.
- Assumption (implementation check, not fabricated verification): the canonical publisher refresh covers every generated surface naming packs; if research finds a generator outside the publisher path, surface it as a scope question before cutting over.

### Implementation inventory and authority correction

- Runtime retirement is concentrated in `skills/scripts/kosmic_project_skills.py` (pack constants and validators, stable-note path gate, proposal pack inputs, completion pack linkage, publication ledger) and `kosmic_dreams.py` (ledger and pack payload duties). There is no dedicated evidence-pack CLI subcommand to remove. New retired declarations must fail as unsupported; historical receipt and curated-input readers remain.
- Current guidance consumers are `skills/SKILL.md`, `skills/README.md`, Task 9 (`task_distill.md`), task implementation/quick-task/review/add-note/propose-skill/project-skills references, proposal templates, and the corresponding canonical knowledge notes. Scientific `artifact_role: evidence`, math/derivation checks, independent review, identity and output scope remain.
- [ADR 0004](../../../../../../../docs/adr/0004-knowledge-first-notes.md) supersedes ADR 0002 by reference. The old ADR remains unchanged.
- Superseded authority: `kosmic/quick-task/restore-evidence-inventories-for-projection-hygiene`, canonical path `specs/quick-tasks/restore-evidence-inventories-for-projection-hygiene.md`, captured SHA-256 `e66ee0a8393d4d9717cc3babb75824fe052721d55757440fd7c1b51ac6c2c8b4`. Contrary to this Story's planning assumption, the inspected record is **draft**, not completed, and has no completion receipt. This approved Story supersedes its pack-inventory restoration instruction because the knowledge-first workflow retires the mandatory pack layer. Do not execute those restoration rows post-cutover; do not edit or re-approve that original record. This factual correction changes no historical approval or physics verdict.
- Historical completed records, receipt originals, curated proposal snapshots and their recorded source pins are immutable. Current generated topics are a different authority class: their content and pins must be rebuilt from the final approved source, not merely rehashed.

### Bounded demonstrations and content review

Executed only on bounded copies under this writer's managed run `20261018T172001Z-knowledge-first-bounded-2c3d90264c3455cb6dd1d95ffe06147c`, scratch subdirectories `demo1` through `demo4`. These are temporary verification outputs, not a new permanent evidence layer or a live disposition map.

- TBUpy: `demo1/transformed/formal_charge_campaign.retraction-first.md` leads with the Si retraction and labels the old interpretation. Recorded physical settings, failed approach and negative findings remain.
- TB2J: `demo2/transformed/bruno-realspace-options.coherent.md` has one active metadata header, preserves the dated inner draft stamp as historical provenance, retains B FFT/C local-approximate settings and limitations, and bounds the implementation claim as pending verification. Copied dependencies point to resolving source-vault specification targets.
- Kosmic: all six pack files were copied into a standalone recovery Git fixture, commit `7b48a499f0107c044482cb84efc593ccea40aeac`, before copy classification. The process transcript records that order; commit/filesystem timestamps support but do not independently prove chronology. Both source snapshots classified disposable were freshly compared byte-for-byte with current Git-tracked host files; unique JSON/manifest content was retained. No original file was deleted.
- abinit: `demo4/dataset-adjacent-copy` retains verbatim report and receipt documents. The native archive `/STORAGE1/hexu/projects_bak/DFTU_NC_data/abinit_ncdftu_data/campaigns/nio_j02` was available read-only and was not copied; its `archive_manifest.json` remains native. The reusable note contains general response-gate pitfalls with precise native/source references, not a dataset pointer stub. Dielectric, elastic and phonon failures, non-isolated-J interpretation, open root cause, uncertified status and administrative validation blocker remain explicit.

Independent content reviewer `ReviewLocality005` requested three corrections: `DEMO005-1` receipt locations, `DEMO005-2` a copied dependency link, and `DEMO005-3` a nonexistent checksum citation. All three were corrected in bounded copies. Round 2 approved those fixes and the preserved scientific boundaries; this is content review, not the later whole-feature Standards/Spec approval. The reviewer inspected the recovery commit and source links, but did not independently rerun checksum computations.

Agent-observed fresh byte comparisons found all ten originals identical to the pre-transform pristine copies. Source roots below are the shared vault `/home/hexu/projects/memnotes/memnotes` for the first four rows and the original repository's `memnotes/Projects/kosmic/evidence/2026-10-15-completion-status-coherence/` for the last six.

| Original | Unchanged SHA-256 |
|----------|------------------|
| `Projects/TBUpy/notes/formal_charge_campaign.md` | `e2047fd2960c62ea009c60e6a1bbd157787f491e265a32e9c717b93a1685693c` |
| `Projects/TB2J_dev/notes/bruno-realspace-options.md` | `30201c467045c075c312b89969b6366c9f603b0e7cd6eb7707d8ad80627e0ead` |
| `Projects/abinit/evidence/2026-10-15-nio-j02-campaign/report.md` | `9e04ed8590107bd9652aa7a3e36bb1831cc092d61e6568b9725ba0a8f392eeb6` |
| `Projects/abinit/evidence/2026-10-15-nio-j02-campaign/archive-root.txt` | `92515b6b359be83f0278d5709ed3c8343a063f85f708a497026e0cd71e0f2919` |
| `MANIFEST.md` | `3bc1cb8006af923fad35523a084b94765a85b0f589d15839ee585067b7d00697` |
| `acceptance.json` | `155dea86dce63a4348947137a68cd2029a38dbaa17c9f6fce6d27d5127e17c5e` |
| `kosmic_completion.py` | `b0e93506188d44a509afad16dd113154f8c5382c03938b2c49578ea5ffc13d48` |
| `review.json` | `fef42a092112c497818fbe3f9f620fa57a249f60f8e2de334c96fc1fee3de231` |
| `smoke-before.json` | `107bd48beaf2a957f1dc628468d448c924e0d6f821760b33c9401b99d9bb0434` |
| `test_kosmic_work_records.py` | `cea56af3dffc902f427435c217d4a8a20ac6e1fb6ec4a03d2cf10a167c878311` |


### Current topic identity recovery

Three existing current topics still pin their 2026-09 adoption-time source versions, not the newer pair manifests. The already recorded `specs/shared-library-migration.json` assignments establish their topic IDs; raw Git blob reads independently matched each historical note byte-for-byte to its published `source_sha256`:

| Current topic | Historical source and exact published SHA-256 |
|---------------|-----------------------------------------------|
| `kosmic/development/cli-extension-conventions` | `9bdaf93:memnotes/Projects/kosmic/notes/cli-extension-conventions.md`; `12370f1ca4c1405e7062fa0338d3a80ea4661d19cb90676cad38cc2a94e3fc6d` |
| `kosmic/development/projection-audience-routing` | `9bdaf93:memnotes/Projects/kosmic/notes/projection-audience-routing.md`; `603b60733a105aac6b3c7c0025d6e52a1faaf2f3234b3db60ad5bbcb62b9a3d8` |
| `kosmic/usage/cli-projection-commands` | `0daf64e5:memnotes/Projects/kosmic/notes/cli-projection-commands.md`; `9e5bcdc66e14fe39c028a3066d7d39ae4bd0e8ab6cafc58c10a312d6dd20813f` |

Their source notes now carry those **already published** stable IDs in `skill_resources`, with semantic `updated` unchanged by bookkeeping. This is not nomination or a wish list. Fresh source backups preceded the three staged backlink additions; the first publication attempt failed the existing 12288-byte Topic limit and its staged fields were restored. The canonical CLI overview was then substantively consolidated without changing that limit, and the next canonical publication succeeded.

The real `generate-library` publication rebuilt all six current topic bodies from final note content, reconciled their complete raw source pins, and persisted `source: notes/...` identities. The actual `resolve_library` → `load_recipe_packet` consumer loaded the current STATUS and curation guidance; current pair and library validation passed. All six actual-use IDs and final raw source hashes matched, semantic `updated` values stayed unchanged by bookkeeping, and the old ledger bytes were unchanged. No generated topic was hand-edited to bless an old body, and no historical migration map, curated snapshot or old approval was changed. The old mapping establishes identity, not permission to rewrite historical pins.

The six original Kosmic pack files also have durable byte-identical recovery in the captured source baseline commit `201438f88bd077c68cda4f7b33438cb79752985f`, retained by branch `kosmic-kf-baseline-d6030fcb`; all six raw Git blob SHA-256 values were compared with the originals and matched. This durable Git recovery predates the bounded-copy classifications.

### Historical proposal readers and pending current work

After legitimate canonical-note evolution, the old reader rejected completed proposal `specs/skill-proposals/2026-09-07-atomic-publish-tree-reuse.md` because its captured source pin differed from the live note. The corrected reader treats completed proposals' canonical-note and routine pins as recorded historical facts, while still byte-verifying immutable captured files. Nonterminal proposals retain current-source freshness checks.

An actual per-proposal reader exercise validated all five completed proposals and draft `2026-10-11-migration-routine-decision.md`. Draft `2026-09-24-day-delta-harvest-routine.md` remains explicitly blocked by its old `notes/dream-reflection-workflow.md` pin. Neither that manifest nor any historical pin was refreshed or blessed. Continuing that proposal requires a separately governed fresh proposal input capture; this Story does not approve or complete it.

The bounded current-record inventory found no unfinished task containing both an `impact.md` publication duty and forced Task 9 step. Remaining such observations are immutable completed records or curated snapshots, not outstanding instructions to migrate. The two actual draft proposal pack keys were retired in place; the superseded inventory QuickTask remains unchanged.


## Assumptions & Verification

| Assumption | Verified? | Source |
|------------|-----------|--------|
| Obsolete pack modes are confined to the inventoried CLI surfaces | Yes | Implementation inventory and authority correction (`kosmic_project_skills.py` and `kosmic_dreams.py`; no dedicated subcommand); retirement suite 15/15 green |
| All generated projections flow through the ADR-E-bounded canonical publisher | Yes | Authorized STATUS renderer; real `generate-library` publication and `resolve_library` → `load_recipe_packet` consumer, six final source pins verified |
| QuickTask record path/identity and its current bytes are stable | Yes | Full captured SHA-256 in the supersession entry; unchanged draft record with no receipt, not a completed record |
| The four demonstration inputs exist at the audited paths | Yes | Bounded `demo1`–`demo4` exercise; ten original SHA-256 comparisons and durable recovery recorded above |

Verification scope (2026-10-18): the final cutover tree passed all 31 test modules (0 failed, 188.99 s, `knowledge-first-final-cutover.log`), all 15 publication regressions (23.481 s, `story005-final-publication-15-green.log`) and the real six-topic canonical publisher/consumer. The final generated-report heading was exercised through its CLI surface and the existing explicit-candidate behavior test. Round-2 Standards and Spec implementation reviews are approved; Story 004 still requires human Spec closure after its three-round cap. Stories 001–003 have actual successful receipts, imported byte-for-byte and terminal-validated here. This dependent Story remains `in_progress`, not completed.

## Definition of Done

- [ ] All acceptance criteria met; retired machinery absent with no shims; surviving invariants/gates unchanged under Story 003's record-embedded proof contract
- [ ] Historical records, curated inputs, pins, and receipts intact and still validatable as originally produced
- [ ] Bounded-copy demonstrations pass with originals unmodified; no live-vault deletion/migration/installation and no scheduler introduced
- [ ] New superseding ADR written; QuickTask supersession recorded by reference in this Story's own governing record; completed QuickTask unmutated
- [ ] Independent Standards + Spec review completed; all tests green; no regressions

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-10-18 | Created | Initial draft; approved - awaiting implementation |
| 2026-10-18 | Approved | User approved this story as part of the full five-story set; awaiting implementation |
| 2026-10-18 | Started | Work start accepted at setup commit 139f91b; implementation delegated |
| 2026-10-18 | Whole-CLI smoke completed | Managed run `20261018T191012Z-smokewholeworkflow005-sy-db62268080b2ac6649343ec2e7d929bd` cycle 2: pre-receipt FULL `check-completion` rc=0, receipted `work finish` (`7dbd9da571c8807e.json`), no `evidence/` tree or sidecars, pre-seeded note bytes unchanged, no_action finding manufactured no note; cycle-1 pre-receipt-check gap admitted and remediated. Feature completion not yet claimed |
| 2026-10-18 | Review and verification complete; dependency gate retained | Twenty exact criterion observations; latest 31-module suite green, 15 publication regressions green, real six-topic publisher/consumer green. StandardsAxis005 and SpecAxis005 approved Round 2. Stories 001–003 receipted and portable; superseded the same day when the user approved manual Spec closure of Story 004 (checked finish, receipt af0badba9f8fe6d3), removing this dependency |
| 2026-10-18 | User closure of Story 004 and Story 005 checked finish | User approved manual Spec closure of Story 004; its immutable done record and receipt af0badba9f8fe6d3.json were imported byte-intact into this Project. Full pre-finish checking then passed every gate for Story 005 (twenty exact criterion observations; Round-2 two-axis approval at fixed review base 139f91b), and the checked finish captured the final native receipt over these record bytes |
