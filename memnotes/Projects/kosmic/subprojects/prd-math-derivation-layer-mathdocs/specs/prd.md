---
status: "approved"
created: "2026-09-05"
updated: "2026-09-05"
linked_architecture: "architecture.md"
project_id: "kosmic"
subproject_id: "prd-math-derivation-layer-mathdocs"
record_kind: "prd"
local_id: "prd"
---

# PRD: Math Derivation Layer (mathdocs)

## Problem

Projects contain many mathematical equations. Today the LLM re-derives or
recalls them during development and debugging, which is inconsistent and
unreproducible: the same expression can drift between sessions, notes, and
code. Nothing forces the implementation to agree with a checkable derivation,
and when a discrepancy surfaces there is no rule saying which side is wrong.

Clarification on the transcription rule below: it governs **stated results**,
not exposition. A note may include intermediate explanatory steps (walking
through *why* the derivation takes the form it does, trivial arithmetic, prose
motivation); only the final results — the expressions other notes and code
rely on — must be transcribed from execution output. Display math (`$$…$$`)
carrying a relied-upon result requires the `derivation:` linkage in FR-004.

## Goal

Every equation used in a Kosmic project is defined, computed, and corrected in
one authoritative place: an executable SymPy file. The LLM never authors
equations freehand; it transcribes results from a derivation that a machine
can re-run. Discrepancies are resolved derivation-first.

All FR-001 through FR-008 are **Must** requirements for the first release;
none is optional.

## Vault layout and migration (FR-001)

Every Project contains a `mathdocs/` directory, peer of `notes/` and
`evidence/`:

```
{VAULT}/Projects/{TARGET}/mathdocs/
  index.md          # reserved derivation index
  {slug}.py         # executable SymPy derivation (stdlib + sympy only)
  {slug}.md         # derivation note, one per .py, same slug
```

Task 1 initialization creates the directory and an empty reserved `index.md`.
Task 8 migration creates missing structure idempotently and never overwrites
existing mathdocs content. This migration is required for existing Projects,
not deferred until the first derivation. `mathdocs/` is never projected into
the Skill Pair; conceptual notes link to it by Project-root-relative path.

## Pairing and index (FR-002)

- Every `{slug}.py` has a matching `{slug}.md` and vice versa; `validate`
  fails on unpaired files, listing them.
- `index.md` contains exactly one table row per non-deprecated derivation with
  columns `Derivation | Status | Result summary`; `Derivation` is the relative
  link `{slug}.md`, `Status` matches the note frontmatter, and the summary is
  one non-empty line. `validate` fails on missing, duplicate, stale-status, or
  unknown rows.

## Derivation and verified-result contract (FR-003)

Math note frontmatter:

```yaml
type: Math Derivation
status: draft | stable | deprecated
derivation: {slug}.py
source_sha256: {64-lowercase-hex}
python_version: {major.minor.patch}
sympy_version: {installed-version}
verified_at: {ISO-8601-UTC}
verified_host: {hostname}
verified_directory: {absolute-source-directory}
```

Each script supports a Kosmic machine-output mode and emits a versioned,
UTF-8 JSON object containing uniquely named results with canonical SymPy
representation (`srepr`) and rendered LaTeX. Results are sorted by name.

The paired note contains one machine-delimited Verified Results block. Each
result in that block is identified as `{project_id}/{slug}#{result-name}` and
contains the exact emitted LaTeX. `check-math` compares script output, every
named result, the block contents, and `source_sha256`; process success alone
never counts as verification. The note may explain assumptions, units, and
intermediate reasoning outside the block. Every correction appends its date,
error, and resolution under `## Corrections`.

## Stable-note equation gate (FR-004)

A regular note containing authoritative mathematical results declares all
source derivations:

```yaml
derivations: [mathdocs/{slug}.py, ...]
```

Every relied-upon final result is display math immediately preceded by a
`MathDoc: {project_id}/{slug}#{result-name}` marker. `check-math` compares that
equation to the named script result. Intermediate explanatory display math may
use `MathDoc-Exposition: {project_id}/{slug}`; it must resolve to a declared
derivation but is not asserted as a named final result. Inline math is limited
to notation, trivial arithmetic, and exposition; an inline expression used as
an implementation requirement must be promoted to a marked display result.

`validate` fails a stable note containing display math without non-empty,
resolvable `derivations:` and a valid adjacent result/exposition marker.
Drafts may reference pending derivations. Code fences are excluded from math
detection.

## Work-item and implementation linkage (FR-005)

Work items implementing mathematical functionality declare:

```yaml
derivations: [{slug}, ...]
math_implementation_files: [src/path/to/file.py, ...]
```

The completion command accepts `--source-root` (default: current directory);
implementation paths resolve beneath that root. Equation-derived source code
contains an adjacent comment or docstring with the stable identifier
`MathDoc: {project_id}/{slug}` (optionally `#result-name`).
`check-completion` fails unless every declared derivation exists, its note is
stable and currently verified, every declared slug appears in at least one
implementation file, and every listed implementation file references at
least one declared slug. Paths escaping `--source-root` are rejected. Absent
`derivations` means no math gate; declaring either math field requires both.

## check-math command (FR-006)

```bash
python3 {KOSMIC_SKILL_DIR}/scripts/kosmic_project_skills.py check-math \
  --project "{VAULT}/Projects/{TARGET}" [--slug {slug}] \
  [--source-root "{REPO}"] [--update]
```

- Executes each selected `.py` in machine-output mode and reports per-file
  pass/fail plus a summary.
- Default mode is read-only verification: compare machine output, paired-note
  result block, source hash, and recorded Python/SymPy versions.
- `--update` atomically refreshes only the paired note's generated Verified
  Results block and verification metadata, and only after a successful run;
  explanatory prose and `## Corrections` are never rewritten.
- A missing SymPy import, malformed result protocol, timeout, nonzero child
  exit, output mismatch, or stale metadata produces a nonzero command exit
  with a specific remedy. Structural `validate` remains host-independent.

## Debugging rule — inspect the derivation first (FR-007)

For an equation-level defect (wrong value, units, sign, domain, or functional
form), inspect the referenced derivation before editing implementation code.
Review its assumptions, symbol domains, units, conventions, and named output.
If it is wrong, fix the `.py`, run `check-math --update`, append the correction
record, then update dependent notes and code. Code is never patched around a
known-broken derivation.

Execution alone does not make a derivation correct. If review cannot identify
whether the derivation, requirements, or implementation is wrong, block the
code change and record the unresolved discrepancy; never choose a side merely
because one artifact executes.

## Skill integration (FR-008)

- `SKILL.md`: add `mathdocs/` to Project paths, a Mandatory Checkpoint
  (“equation-level defect → inspect derivation first”), and Task M: Math Note.
- New `references/task_math_note.md`: create/update scripts and paired notes,
  run `check-math`, and maintain the reserved index.
- `task_init.md` and migration: create/backfill `mathdocs/index.md`
  idempotently.
- `task_add_note.md`: equation-bearing stable notes require plural
  `derivations:` and adjacent result/exposition markers.
- `task_implement_story.md`: Phase-1 research locates relevant derivations;
  math stories declare both derivations and implementation files.
- `task_review.md`: check equation markers and derivation currency; flag
  derivations unused past the configured cutoff.
- `notation.md`: define `{slug}`, Math Derivation, MathDoc identifiers,
  verified results, and derivation-first debugging.

## Non-goals

- Projecting math notes into the Skill Pair.
- Executing derivations inside `validate` (host-dependent; `check-math` owns
  execution).
- Numeric validation harnesses, plotting, or benchmark data — derivations
  only.

## Non-functional requirements

- **NFR-001 Determinism**: process derivation slugs and result names in lexical
  order; use UTF-8 and LF output; compare verified output after LF
  normalization only. Set deterministic child locale and hash seed.
- **NFR-002 Offline**: validation and execution require no network access.
  Derivation scripts may import only the standard library and SymPy.
- **NFR-003 Bounded execution**: invoke Python with an argument vector (never a
  shell), controlled cwd at the Project `mathdocs/` directory, captured
  stdout/stderr, and a default 30-second timeout per derivation. An explicit
  positive `--timeout` may override it.
- **NFR-004 Mutation safety**: `validate` and default `check-math` are
  read-only. `check-math --update` stages every selected note update and
  publishes them atomically only after every selected derivation succeeds;
  failure preserves all prior notes.
- **NFR-005 Trust boundary**: derivation scripts are trusted Project code.
  Kosmic provides process isolation and timeout, not an OS sandbox; the
  command must state this before executing third-party or unreviewed scripts.
- **NFR-006 Compatibility**: the Projection CLI remains Python 3.11+
  standard-library-only. SymPy is required only in the child environment used
  by `check-math`; all other commands remain usable without it.
- **NFR-007 Path containment**: mathdoc and implementation paths resolve
  beneath their declared roots; traversal and symlink escape are rejected.

## Open questions

None blocking. Architecture will fix the exact versioned JSON schema, marker
syntax, atomic-update staging mechanism, and parser seams without weakening
the observable contracts above.

## Acceptance

1. Initialization and migration create the reserved `mathdocs/index.md`
   structure idempotently without overwriting existing content.
2. `validate` rejects unpaired files, invalid/stale index rows, invalid
   derivation metadata, missing or stale source hashes, unresolved plural
   derivations, and unmarked display math in stable notes; each error names
   the file and violated field.
3. `check-math` deterministically compares machine output, named result
   markers, source hash, and recorded Python/SymPy versions; tests cover clean,
   mismatch, malformed protocol, missing dependency, timeout, and all-or-none
   update behavior.
4. `check-completion --source-root` verifies stable/current derivations and
   `MathDoc:` identifiers in every declared implementation file, including
   containment and missing-reference failures.
5. Dogfood: at least one real derivation, paired note, linked conceptual note,
   and referenced implementation in the kosmic Project; `validate`,
   `check-math`, and `check-completion` all pass.
6. Skill docs and templates are updated in one pass; the new skill version is
   installed and diff-verified in all configured homes.

## PRD Review

**Decision**: Approved
**Reviewer**: AI (Task 7 PRD re-review)
**Date**: 2026-09-05
**Approval basis**: User approved the direction; re-review verified every
Blocking finding below is resolved in the normative requirements.

### Finding resolution

| ID | Resolution | Status |
|----|------------|--------|
| PRD-001 | FR-003/006 require versioned named machine output, a delimited Verified Results block, source-hash and exact result comparison; process exit alone is insufficient. | resolved |
| PRD-002 | FR-005 requires adjacent `MathDoc:` identifiers in declared implementation files and completion-time source-root verification. | resolved |
| PRD-003 | FR-001 requires idempotent `mathdocs/index.md` creation during both initialization and migration. | resolved |
| PRD-004 | FR-003 records and validates source SHA-256, Python/SymPy versions, UTC verification time, host, and directory; `--update` refreshes them only after successful execution. | resolved |
| PRD-005 | FR-007 requires assumption/domain/unit review and blocks unresolved discrepancies; execution no longer chooses the authoritative side. | resolved |
| PRD-006 | FR-004 supports plural derivations, named final-result markers, exposition markers, and an explicit inline-math boundary. | resolved |
| PRD-007 | NFR-001..007 specify determinism, offline operation, bounded no-shell execution, atomic/read-only behavior, trust, compatibility, and path containment. | resolved |

### Checklist

- Problem: clear and evidence-linked to equation drift.
- Goals: machine-verifiable through named outputs, hashes, markers, and gates.
- Non-goals: projection, numerical harnesses, plots, and benchmarks excluded.
- Requirements: FR-001..008 all explicitly Must; NFR-001..007 measurable.
- Success criteria: six observable acceptance criteria cover structure,
  execution, implementation linkage, dogfood, and distribution.
- Open questions: no blockers; wire-format/parser details correctly deferred
  to Architecture without relaxing behavior.
