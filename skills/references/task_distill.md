---
type: Task Reference
title: Task 9 - Distill
---

# Task 9: Distill

**When**: After a work item (story or quick task) that declared `evidence_packs`, before `check-completion` can pass; or whenever the Maintainer is asked to consolidate captured experience.

**Reference**: this document is self-sufficient — no hidden prompt state is required.

## Purpose

A Maintainer (any capable coding agent executing this task) analyzes Evidence Packs into root-cause knowledge expressed as draft atomic notes, updates to existing notes, or deprecations. Distillation output is **always `draft`** — promotion to stable happens only through human review (Task 7 or Task 4).

> Procedure adapted from the WikiSkill Wiki Maintainer (arXiv 2608.27454, Appendix E.2; third-party implementation `github.com/ashutoshsinghpr7/wikiskill`, MIT, pinned revision `02fac2c804fe156e43b12c691e4ae527614d63a1`). The upstream JSON output contract and wholesale index-rewrite rules are intentionally dropped: output is OKF notes edited in place; the notes index is maintained per Task 2.

## Inputs

1. The declared Evidence Packs: `{VAULT}/Projects/{TARGET}/evidence/{slug}/` — read `MANIFEST.md` first, then each payload file by its listed role.
2. The existing Project Knowledge notes (`notes/`), to honor the never-duplicate rule.

## Procedure (analysis rules — all mandatory)

1. **Read the manifest, then the payloads.** Evidence is immutable — never modify pack contents.
2. **Deep analysis, not symptoms.** For execution evidence: read what was actually done (commands, edits, tool output); compare successful vs. failed attempts; extract **action patterns** (what to do or avoid), never bare error messages. Identify **why** each failure happened — root cause, not what happened.
3. **Both directions.** Capture failure patterns (what went wrong, how to avoid it) and success patterns (strategies that consistently worked).
4. **Exact sequences.** Notes distilled from evidence must carry exact commands, file paths, and API calls from the evidence — concrete, not paraphrased.
5. **Never duplicate.** Before creating a note, search `notes/` for existing coverage. If found: update that note with the new evidence (append or refine), do not create a second note. Conflicting findings follow Task 2's conflict policy (a `## Conflict` section or `{TOPIC}_conflict.md`).
6. **Concise.** Distilled notes are 10–30 lines. Only meaningful, generalizable observations become notes — one-off noise stays in the pack.
7. **Link evidence.** Every distilled or updated note gains `evidence: [paths]` frontmatter (Project-root-relative paths into the pack), so `check-completion` and `validate` can verify linkage.
8. **Environment anchoring.** When distilled findings depend on exact code or machine state, carry a Code state line (see `notation.md`) into the distilled note or the pack's session record; the MANIFEST provenance keys (`git_head`/`worktree_tree`) remain the authoritative record for packs.
9. **Index entry quality.** Each new note's entry in `notes/index.md` states problem + root cause + fix in one or two sentences, specific enough to judge relevance without opening the note.
10. **Deprecation.** When evidence contradicts a stable note, do not delete it: add a draft update and flag the contradiction for review; deprecation is a human-gated outcome.
11. **Classify reusable Patterns.** If Distillation creates or materially updates a reusable Pattern with a repeatable trigger, stable inputs, ordered actions, decision points, expected output, and failure handling, set the work item's `proposal_required: true` and run Task P. Project facts, vocabulary, and one-off observations stay `proposal_required: false`; Task P records `no_action` when classification remains uncertain.

## Output

- New draft notes, updates to existing notes (with new evidence appended), or deprecations flagged for review — all following Task 2's atomic-note rules.
- Every touched note: `status: draft` until reviewed, `evidence:` paths set.
- Log entry in `log/` pointing at the packs consumed.

## Completion

Run the Projection CLI `check-completion` for the work item (it fails if any declared pack lacks a linking note). Then request review.

## Explicitly out of scope

- Editing evidence pack contents (immutable).
- Promoting notes to stable (human gate).
- Touching the Skill Pair (generated; `generate` owns it).
