# Incremental Curation Routine (curation-prepare / curation-finalize)

One curation job = three explicit stages; one outer agent (manual or externally
scheduled) orchestrates them. The Project CLI stages are deterministic and
never invoke a model. Review authority stays with the human-approved work
record; nomination is the strongest automated outcome. No new gate, daemon,
scheduler, queue, or report is introduced.

```text
python3 skills/scripts/kosmic_project_skills.py curation-prepare  \
    --project PROJECT --work-record REF --scope notes \
    [--from <UTC> | --baseline] [--note NOTE_PATH ...]

python3 skills/scripts/kosmic_project_skills.py curation-finalize \
    --project PROJECT --run RUN_HANDLE_FILE --work-record REF --scope notes
```

`[--from <UTC> | --baseline]` is OPTIONAL and FIRST-RUN-ONLY: a new scope
requires exactly one of the two (never both), while any scope that already
has a checkpoint derives its window from the persisted cursor and refuses a
provided bound typed.

## Scope

The default scope is `notes` (the whole recursive notes tree). A bounded
notes-subtree path narrows it: `notes/theory` and `notes/software` are two
independent scopes, each with its own checkpoint (`notes/theory` also accepts
the short form `theory`). Scope values must stay inside the notes tree:
absolute paths, `..`, and escaping components are rejected. Separate scopes
never read or advance each other's checkpoints.

## Stage 1 — prepare (deterministic; managed-run authority only)

Prepare freezes the cutoff `U` at run start (never a `--cutoff` flag). The
lower bound is FIRST-RUN-ONLY: a new scope requires exactly one explicit
bound — `--from <exact-UTC>` or `--baseline` (a deliberate zero-width first
window that scans nothing). After a scope has a checkpoint, prepare derives
its window from the persisted cursor alone and REFUSES any provided bound
(first bounds may never rewind or skip history). A bound-less prepare on a
scope without a checkpoint fails typed instead of sweeping history.

The semantic instant is frontmatter `updated`, falling back to `created` only
when the note was never updated; filesystem mtime is never consulted. The
snapshot records revision identities only (path, `updated`, content sha256,
`skill_candidate`, `skill_resources`) for **every** interval-eligible note —
including `skill_candidate: false` notes the reviewer may later skip — and
candidate-flagged and live-resource notes sort first. Note bytes are never
copied; nothing outside the Project notes tree is scanned.

Legacy date-only `updated`/`created` values certify the whole UTC day: a day
wholly inside `(L, U]` may be reviewed with recorded uncertainty, a day wholly
outside is skipped, and a day overlapping the boundary is recorded as
**ambiguous** — excluded from review, blocking full-scope advancement until a
bounded disposition resolves it. No historical times are invented. A note
with no usable timestamp fails closed (no all-history sweep). `index.md` is
the reserved bundle entry point and is never selected.

Prepare's ENTIRE coordination footprint is the managed run: the frozen window
and snapshot live inside the run workspace, and an active run for the same
project+scope (found through existing managed-run state and its snapshot)
makes a second prepare fail with a typed busy diagnostic. Terminal runs never
block; a grace-expired abandoned run is closed through the existing
`scratch fail` mechanism. Prepare writes NOTHING under the Project — no
checkpoint pointer, no lock file; the Project checkpoint appears only at
finalize.

## Stage 2 — semantic review (agent, not CLI)

The reviewing agent reads the selected notes in place and records outcomes
into the **existing** governing work record by adding a `curation_review`
frontmatter mapping (flow YAML, the same scalar semantics as every other
frontmatter field):

```yaml
curation_review:
  run_id: "<run_id returned by prepare>"
  reviewer: "<agent identity>"
  notes:
    - {path: "notes/example.md", revision: "<sha256 from prepare>", disposition: reviewed}
    - {path: "notes/other.md",   revision: "<sha256 from prepare>", disposition: no-action}
    - {path: "notes/legacy.md",  revision: "<sha256 from prepare>", disposition: skipped, reason: "creation-time-false candidate"}
```

Dispositions: `reviewed`, `no-action` (a successful outcome; no paperwork), or
`skipped` — skipping is valid ONLY for a note whose snapshot shows
`skill_candidate: false` AND empty `skill_resources`, with an explicit
`reason`. A candidate-flagged or live-resource note must be `reviewed` or
`no-action`. Nominations follow the existing proposal/review record concepts,
prefer updating the existing skill topic over creating a parallel one, and
never auto-approve, publish, or install.

## Stage 3 — finalize (deterministic; the only checkpoint writer)

Finalize verifies, in order: the `--run` handle names an active managed run
whose snapshot matches this project, scope, and governing record; the
`--work-record` is the currently governing `approved`/`in_progress` record
(and the SAME record the snapshot carries — a foreign record fails without
touching another run's lease); the work-record review mapping names the
reserved `run_id` and gives **every** prepared identity an explicit,
revision-exact disposition; and every prepared identity still matches current
instants and bytes. An in-window revision after prepare (drift) blocks
advancement; a revision saved after `U` simply belongs to the next window.
A full-scope window is also re-enumerated: notes that became eligible after
prepare block the cursor until they are prepared and reviewed.

Only after the managed run closes as `succeeded` does finalize publish the
per-scope checkpoint to exactly `U` — finalize alone (with the recorded
review) writes the checkpoint. Any missing/stale/wrong-run disposition,
ambiguity, drift, or failure releases nothing the checkpoint depends on: the
cursor stays where it was and the next window safely rescans. A `--note`
subset run validates the same way but **never** advances the checkpoint,
whatever its outcome. If the checkpoint write itself fails after the run
closed, the cursor stays old and the next prepare rescans — an unpublished
cursor is never consumed.

## Ground rules

- No model call, classifier, or semantic inference inside the CLI; review
  completion comes only from recorded dispositions, never from an exit
  status.
- No scheduler, daemon, queue, daily report, durable candidate list, or
  evidence pack; the only durable outputs are the managed-run metadata and
  the per-scope Project checkpoint that finalize publishes.
- Bookkeeping (linkage sync, check recording) does not bump the semantic
  `updated`; reassessment and candidacy flags do (Story 002 contract).
- Every stage requires an approved/in_progress work record, re-resolved at
  each invocation — prepare's managed scratch included.
