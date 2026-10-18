---
status: "approved"
updated: "2026-09-02 (approved)"
linked_research: ["../../../evidence/2026-09-02-wikiskill-experience-compilation/memo.md", "../../../evidence/2026-09-02-route-graph-skill-projection/memo.md"]
linked_epics: ["epics/epic-001-evidence-substrate.md", "epics/epic-002-note-linkage.md", "epics/epic-003-impact-ledger.md", "epics/epic-004-completion-gate.md", "epics/epic-005-distillation-docs.md"]
project_id: "kosmic"
subproject_id: "experience-compilation-adapting-wikiskill-into-kosmic"
record_kind: "prd"
local_id: "prd"
---

# Experience Compilation: adapting WikiSkill into Kosmic

## Problem Statement

Kosmic's knowledge system captures Project Knowledge only when the agent discretionally decides to (Task 2 triggers exist but nothing enforces them), keeps no raw material behind notes, and has no memory of which knowledge changes were published or rejected across sessions. The result is the observed behavior: notes and skills are rarely written or updated, and rejected ideas get re-litigated.

WikiSkill (arXiv 2608.27454) validates the fix experimentally: a persistent knowledge layer that compounds from execution experience, separated from the skills built on it, improved skill evolution by +15.0 average points; its absence is the dominant ablation. Its loop machinery now exists as MIT-licensed, third-party code (`github.com/ashutoshsinghpr7/wikiskill`), but that implementation is benchmark machinery (auto-graded task packs, score gating, plain-markdown wiki) — not an Obsidian/OKF-conformant project-knowledge system with human gates.

## Decisions (settled in grilling session 2026-09-02, ADRs 0002–0003)

- **One evidence layer** (ADR-0002): research discovery and execution outcome are two kinds of the same concept — the Evidence Pack. `specs/research/` is absorbed.
- **Vocabulary imported as roles**: Pattern (the role of a distilled note), Maintainer (the agent executing Distillation), Impact Ledger (mirrors `skill-impact.md`). `vault`/`notes/` untouched; task names stay verb-first.
- **Task 9: Distill** is the only *gated* extraction (Task 2 stays opportunistic, Task 4 periodic).
- **Enforcement is mechanical**, not discretionary: a CLI gate, not a checklist.
- **Stage 2 posture pinned** (ADR-0003): wrap the pip package on demand; never vendor.

## Goals

- Make knowledge capture **mechanical, not discretionary**: distillation runs as a defined post-work step driven by captured evidence, enforced by the existing completion gate pattern.
- Add the three missing WikiSkill mechanisms to the Kosmic vault, OKF-conformant: Evidence Packs, Distillation (Task 9), and the Impact Ledger.
- Reuse the verified Appendix E.2 Maintainer analysis procedure with attribution.
- Preserve every Kosmic invariant: authoritative OKF notes bundle, deterministic stdlib CLI, human approval gates, atomic publication, projection pipeline untouched.

## Non-Goals

- Benchmark scoring loops, validation-score gating, or autonomous skill-proposer agents (the grader is the test suite + Task 7 review; the gate is human).
- Changing the projection/audience/routing model (route-graph direction abandoned 2026-09-02; archived under `specs/archive/`).
- Auto-stable notes or auto-publication: Distillation output is always `draft` until human review.
- Projecting Evidence Packs or the Impact Ledger into generated skills.
- Vendoring third-party code into this repository.

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-001 | Evidence layer: `{VAULT}/Projects/{TARGET}/evidence/{YYYY-MM-DD}-{slug}/` — one pack per work item (story, quick task, or standalone investigation); immutable and append-only; `MANIFEST.md` with frontmatter `kind: execution \| research`, `produced_by`, `date`, `summary` (≤2 lines) and a body file list with a one-line role per file; no per-file hashes (git is the hash layer) | must |
| FR-002 | Evidence is excluded from OKF bundle validation and projection exactly like `log/`; the Projection CLI ignores it | must |
| FR-003 | Task 9 (Distill): a Maintainer agent analyzes declared Evidence Packs plus existing notes. Procedure adopts the Appendix E.2 analysis rules wholesale — root cause (WHY, not WHAT), success-vs-failure comparison, action patterns not error messages, exact command sequences, both success and failure patterns, 10–30-line notes, never-duplicate (update existing notes with new evidence), index entry states problem + root cause + fix. Dropped from upstream: the JSON output contract and wholesale index rewrite (the OKF index is maintained per Task 2). Outputs: draft notes, updates, or deprecations; conflicts follow Task 2's conflict policy; deprecation stays human-gated | must |
| FR-004 | Additive optional note frontmatter `evidence: [paths]` (relative to Project root); CLI validates entries resolve for stable notes; drafts may reference pending evidence | must |
| FR-005 | Impact Ledger `{VAULT}/Projects/{TARGET}/impact.md`: flat, append-only; entry = 6 fixed fields (date, kind `publication\|decision`, targets, refs, outcome, reason ≤1 line); no prose. `generate` appends publication entries (changed note paths, old→new source hashes); Task 7 review appends decision entries for knowledge changes | must |
| FR-006 | Ledger is excluded from projection; `validate` fails on malformed ledger entries | must |
| FR-007 | Completion gate: work items declare `evidence_packs: [slugs]` in frontmatter (optional; absent = no gate); `check-completion` fails when any declared pack lacks a draft-or-stable note linking it via `evidence:` — mirrors the `consumer_interface_change` gate pattern | must |
| FR-008 | Task 4 review flags unreferenced Evidence Packs older than 3 months; nothing is ever auto-deleted or auto-archived | must |
| FR-009 | Attribution: prompt/procedure text adapted from WikiSkill carries attribution to arXiv 2608.27454 and the MIT repo, with the pinned upstream revision recorded in the Kosmic release | must |
| FR-010 | Stage 2 (optional, separately approved): transcript-capture adapters wrapped on demand from the installed `wikiskill` pip package (ADR-0003); no vendoring | could |
| FR-011 | Migration: existing `specs/research/` memos become `kind: research` Evidence Packs; specs INDEX and spec frontmatter links updated | must |
| FR-012 | Docs updated: `SKILL.md` task catalogue (Task 9), `README.md`, `references/task_add_note.md`, `references/task_implement_story.md`, `references/task_quick_task.md`, `references/task_review.md` (retention flag), `docs/` | must |

## Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-001 | Stage 1 uses only the Python 3.11+ standard library; no runtime dependency on the third-party repo | must |
| NFR-002 | All CLI checks remain deterministic and offline | must |
| NFR-003 | Evidence Packs are plain files (Markdown + JSONL), git-friendly, Obsidian-browsable outside `notes/` | should |
| NFR-004 | Distillation must be executable by any capable coding agent reading the task doc alone — no hidden prompt state | must |

## Success Criteria

- [ ] A real story produces an Evidence Pack; Distillation yields a draft note with valid `evidence:` links; review promotes it to stable; `validate` passes.
- [ ] A work item with `evidence_packs:` declared but no linking note fails `check-completion`; adding the draft note passes it.
- [ ] `generate` publication and a Task 7 reject decision each append correct 6-field ledger entries; malformed entries fail `validate`.
- [ ] A stable note with an unresolvable `evidence:` path fails `validate`.
- [ ] `kind: research` pack (migrated memo) is accepted by the same validation as `kind: execution`.
- [ ] Full `tests/` suite passes with new coverage for FR-002, FR-004, FR-005, FR-006, FR-007.
- [ ] Attribution + pinned revision recorded for every adapted text.

## Open Questions

- [ ] None blocking. Ledger split cadence (flat vs per-year) revisited if `impact.md` grows unwieldy; Stage-2 wrapper interface sketched at architecture time.
