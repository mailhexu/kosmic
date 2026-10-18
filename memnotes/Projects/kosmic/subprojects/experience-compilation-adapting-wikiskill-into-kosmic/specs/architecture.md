---
status: "approved"
updated: "2026-09-02 (approved)"
linked_prd: "prd.md"
linked_epics: []
project_id: "kosmic"
subproject_id: "experience-compilation-adapting-wikiskill-into-kosmic"
record_kind: "architecture"
local_id: "architecture"
---

# Architecture — Experience Compilation

Implements [PRD](prd.md) (approved 2026-09-02). Bound by repo ADRs [0002](../../../../docs/adr/0002-single-evidence-layer.md) (single evidence layer) and [0003](../../../../docs/adr/0003-wrap-never-vendor-wikiskill.md) (wrap, never vendor).

## Vault layout (per Project)

```
{VAULT}/Projects/{TARGET}/
├── notes/                      # OKF bundle — unchanged, only projected layer
├── evidence/                   # NEW — excluded from OKF validation + projection
│   └── {YYYY-MM-DD}-{slug}/
│       ├── MANIFEST.md
│       └── *.md, *.jsonl       # immutable payloads
├── impact.md                   # NEW — flat append-only ledger, excluded from projection
├── specs/                      # specs (research/ absorbed per ADR-0002 → evidence/, FR-011)
└── log/                        # unchanged
```

## Components

### AD-1 Evidence storage and exclusion (FR-001, FR-002)

Evidence and `impact.md` live at Project root, **siblings of `notes/`**, not inside it. Consequence: exclusion is structural, not filtered — `validate_notes_bundle` (scripts/kosmic_project_skills.py:338) walks only `notes_dir`, and `collect_projection_plan` (:450) reads only `notes_dir`; neither ever sees them. The single code change is any directory-walk over the Project root (project discovery, `migrate`) tolerating the two new entries. No projection path is touched.

`MANIFEST.md` frontmatter: `kind: execution | research`, `produced_by`, `date`, `summary` (≤2 lines). Body: one line per payload file naming its role. No hashes — git is the hash layer.

### AD-2 `evidence:` note frontmatter (FR-004)

`parse_markdown` already exposes `document.metadata`; validation hooks into the existing per-note loop in `validate_notes_bundle` (:340-343): for **stable** notes only, every `evidence:` entry must resolve relative to the Project root. Drafts may dangle (pending packs). Additive and optional — existing notes without the key are unaffected.

### AD-3 Impact Ledger appends (FR-005, FR-006)

Two append points, both programmatic:

- **Publication**: at the end of `generate`, after atomic publication succeeds, append one entry per changed note: `date, kind: publication, targets: [note paths], refs: {old→new source hashes from Projection Provenance}, outcome: published, reason: ""`. Hashes come from the existing provenance pipeline — no new hashing.
- **Decision**: Task 7 review appends `date, kind: decision, targets: [note paths], refs: story id, outcome: accepted|rejected, reason: ≤1 line`. Appended by the reviewing agent per the task doc — the CLI *validates* but does not author decision entries (human-gate invariant).

`validate` parses `impact.md` when present: fixed 6 fields, known kinds/outcomes, ISO dates; malformed → failure (FR-006).

### AD-4 Completion gate (FR-007)

Extends `check_completion` (:1244) after the existing `consumer_interface_change` block, mirroring its shape: optional work-item frontmatter `evidence_packs: [slugs]`; absent → no gate (backward compatible); present → every slug must resolve to `evidence/{slug}/` and have ≥1 **draft or stable** note linking it via `evidence:`. Failure message names the orphaned slug.

### AD-5 Task 9 — Distill (FR-003)

Pure procedure doc, no code: `skills/references/task_distill.md`, catalogued in `SKILL.md`. Inputs: declared packs + existing notes. Procedure = Appendix E.2 analysis rules (root cause WHY, success-vs-failure, action patterns, exact commands, success + failure patterns, 10–30 lines, never-duplicate, index entry = problem+root-cause+fix). Outputs: draft notes / updates / deprecations via Task 2 conflict policy; promotion only through human review. Attribution header cites arXiv 2608.27454 and the pinned MIT repo revision. Executable by any agent reading the doc alone (NFR-004).

### AD-6 Retention flag (FR-008)

Task 4 doc gains one review item: list packs not referenced by any note's `evidence:` key and older than 3 months (pack date from directory name). Flag-only; no CLI enforcement, no deletion.

## Data flow

```
work item ──declares──> evidence pack ──Task 9 (Maintainer)──> draft note (evidence: links)
                                                                │ human review (Task 7)
                                                                v
                                            stable note ──generate──> Skill Pair + ledger entry
                                            rejected change ─────────> ledger decision entry
```

## Migration (FR-011)

One-time, this vault: move the two `specs/research/` memos to `evidence/2026-09-02-{slug}/MANIFEST.md + payload`, set `kind: research`; update PRD `linked_research` and specs INDEX links. Other vaults: no note edits required anywhere (all new keys optional).

## Test strategy

Extend `tests/test_project_skills_cli.py` (pytest, tmp-vault fixtures per existing convention): pack-manifest validation, `evidence:` resolution (stable dangling → fail; draft dangling → pass), ledger schema (malformed → fail), `check-completion` gate (orphan slug → fail; linked draft → pass; no declaration → pass), Project-root walk tolerance.

## Out of scope

Stage 2 wrappers (separate approval per ADR-0003); any projection/routing change; OKF modifications.
