---
status: approved
created: 2026-09-22
updated: 2026-09-23
linked_research: []
linked_epics: [epics/epic-26-dream-reflection-initial-release.md]
---

# Dream Reflection

## Problem Statement

Kosmic accumulates a day of work across projects—log sessions, knowledge notes,
story transitions, evidence packs, and impact entries—but does not read that
work back as a whole. The next session therefore starts without one trustworthy
view of what finished, what remains active or blocked, which knowledge changed,
or which repeated mechanics and ideas deserve follow-up. Task Review performs
interactive knowledge hygiene; Kosmic lacks a whole-vault, backward-looking
reflection workflow over the previous day's observable history.

## Goals

- A user-facing Task D (`dream`) reflects on the target day (calendar yesterday
  by default) across all projects and produces one vault-level record.
- Deterministic CLI mechanics harvest the target-day delta, current open work,
  and bounded knowledge/candidate evidence; agent judgment produces the digest.
- `memnotes/dreams/` holds one record per date, a reverse-chronological index,
  and a cumulative idea backlog.
- Every record states source coverage and answers: what finished, what remains
  in flight (including blockers), what knowledge changed or needs attention,
  and what skills or experiments may be worth pursuing.
- Skill candidates remain advisory and enter Task 9 → Task P → Maintainer
  governance only through a later explicit action.

## Non-Goals

- Automatic modification of canonical skills, Project Knowledge, specs, logs,
  evidence, or status fields outside `memnotes/dreams/`.
- Auto-created Task P proposals or `[Extracted]` markers.
- Per-project dream files; project detail is grouped inside the vault record.
- Scheduled or daemon execution.
- Claiming exact edit-time history when neither Git nor maintained frontmatter
  records it; the dream must disclose such coverage limits.
- Weekly rollups and configurable idea aging in the initial release.

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-D1 | Task D is the user-facing `dream` workflow. It accepts `{VAULT}`, optional `--date YYYY-MM-DD`, optional `--timezone IANA_NAME`, and optional `--project {TARGET}`. Effective timezone resolves as explicit `--timezone`, otherwise the host's resolvable IANA timezone, otherwise fail closed; omitted date means the preceding calendar date in that timezone. Deterministic CLI subcommands provide harvest and publication; the CLI does not impersonate agent judgment. | must |
| FR-D2 | Harvest computes the union of (a) files changed by target-window commits under tracked vault surfaces, (b) files whose frontmatter `created` or `updated` equals the target date, and (c) relevant dirty files. It records exact source commits, timezone, origin per file, dirty state, and coverage limitations. | must |
| FR-D3 | Harvest emits versioned, typed JSON inside a managed run. It includes changed files, log sessions, story transitions, evidence packs, impact entries, a current `open_work` snapshot, deterministic knowledge checks, an explicit reflection `read_set`, and skill-candidate evidence. | must |
| FR-D4 | Dream records live at `memnotes/dreams/{YYYY-MM-DD}.md` with versioned frontmatter `schema: kosmic.dream.record/1`, `type: dream`, `date`, `projects`, `source_commits`, `timezone`, `produced_by`, `generated_content_sha256`, and `status: draft`; required sections are Done, In Flight, Notes Digest, Knowledge Flags, Skill Candidates, Ideas, and Today. | must |
| FR-D5 | Deterministic Knowledge Flags are operationally defined: `unextracted-log` means a selected log item lacks `[Extracted]`; `uncited-draft` means a changed draft note has no Markdown backlink in the harvested link index; `declared-stale` means `stale_after` is past or `usage_stale: true`; `evidence-order` compares MANIFEST `date` with citing-note `updated`. `possible-contradiction` is an agent judgment and must cite both notes. | must |
| FR-D6 | Skill Candidates are listed only in-record. Each candidate cites at least two evidence references from the target-day delta, prior dream candidate sections, or routine-query results, and includes a proposed Task P scope. | must |
| FR-D7 | `dreams/index.md` is deterministically rebuilt with exactly one reverse-chronological row per dream. `dreams/ideas.md` is cumulative; idea IDs are `{date}-{slug}`, exact IDs are unique, and optional `merges:` links near-duplicates identified during reflection. | must |
| FR-D8 | A vault-level `validate-dreams --vault {VAULT}` command validates allowed paths, dream frontmatter/sections, filename-date equality, index uniqueness/order, idea IDs, and links. `dream-publish` invokes it against the staged tree and fails closed. | must |
| FR-D9 | Publication stages a complete candidate `dreams/` tree and atomically promotes it through the existing `publish_tree` path with a base-tree digest precondition. No unrelated vault path changes. | must |
| FR-D10 | Same-date reruns compare the canonical record against its persisted `generated_content_sha256`, which `dream-publish` alone computes after merge/redaction from canonical persisted bytes. Unchanged generated records are replaceable idempotently; manual divergence requires explicit `--replace`. `--project` filters evidence but still produces the single canonical date record and records the filter. Whole-tree base-digest drift always fails and cannot be bypassed by `--replace`. | must |
| FR-D11 | Cross-project repetition detection is judgment-phase, advisory-only: harvest supplies prior candidate/routine evidence, and Task D may surface a Shared Skill Library candidate without modifying library or proposal files. | should |
| FR-D12 | A later release may add `dream --week` and configurable idea aging after at least two real daily dream records exist. | could |

## Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-D1 | For identical vault state, target date, timezone, and project filter, harvest JSON is deterministic and offline. Reflection is explicitly judgmental and is not claimed deterministic. | must |
| NFR-D2 | Reflection reads only the harvest plus paths and immutable hashes in its `read_set`; it writes only the staged `memnotes/dreams/` tree. | must |
| NFR-D3 | Harvest may make one metadata pass and one link-only content pass over Markdown in the authoritative vault surfaces. Other full-content reads are bounded to the target delta, open-work records, deterministic flag evidence, prior dream candidate sections, and routine-query results. | must |
| NFR-D4 | Before publication, existing Kosmic redaction rules remove known token/handle fields and scratch paths; permanent records may contain public run IDs only. Validation rejects `.tmp/kosmic/` paths and known secret-bearing field labels. | must |
| NFR-D5 | Dream records are Obsidian-readable, use relative Markdown links, and conform to the declared dream schema. | must |

## Success Criteria

- [ ] A dream over a real prior workday includes every observable changed memnote, states any coverage gap, and matches completed/in-flight story ground truth including work begun before that day.
- [ ] A seeded uncommitted target-date note is harvested via frontmatter and tagged with its origin.
- [ ] Each deterministic Knowledge Flag passes its operational oracle; a seeded contradiction links both notes and is labeled judgmental.
- [ ] A genuine repeated mechanic appears as an evidence-backed Skill Candidate without creating a proposal file.
- [ ] Two dates and a same-date rerun produce a unique reverse-chronological index and duplicate-free ideas backlog; manual divergence requires `--replace`.
- [ ] `validate-dreams` passes valid staged/canonical trees and fails closed on malformed records, secrets, scratch paths, duplicate dates, and index drift.
- [ ] Full suite, completion gates, and adapter byte checks remain green after delivery.

## Resolved Questions

- Weekly rollup and configurable aging are deferred beyond the initial release.
- Idea identity is deterministic `{date}-{slug}`; near-duplicate merging remains agent judgment with explicit links.
- Knowledge Flags are read-only findings; remediation is prose guidance and never mutates source records.
- Task D owns judgment; the CLI owns deterministic harvest, validation, and publication.
