---
type: Project Knowledge
title: Projection CLI experience commands
description: What the Projection CLI validates and enforces for evidence packs, note evidence links, the impact ledger, and work-item completion.
confidence: 0.9
created: '2026-09-02'
updated: '2026-09-02'
validation_procedure: "python3 -m unittest tests/test_project_skills_cli; kosmic_project_skills.py validate --project {VAULT}/Projects/{TARGET}"
project: kosmic
status: stable
audience: usage
usage_stale: false
tags: []
evidence: [evidence/2026-09-02-experience-compilation-impl/session-record.md]
---

# Projection CLI experience commands

## Overview
How the Projection CLI treats the Experience layer: evidence packs, per-note evidence links, the impact ledger, and the work-item completion gate. All commands remain deterministic, offline, and stdlib-only.

## Principles
- Projected references are package-consistent: a link whose target is not in the same package (drafts, other-audience notes) is demoted to bold plain text; `generate` warns on stderr naming each demoted link. Code fences, external URLs, and non-Markdown targets are untouched.
- Notes may declare `evidence: [paths]` (Project-root-relative). `validate` fails a **stable** note whose paths do not resolve; drafts may reference pending packs.
- `impact.md` at the Project root is an append-only ledger of six-field entries (`date, kind, targets, refs, outcome, reason`). `generate` appends publication entries automatically after each atomic publication to the canonical root; review decisions are appended procedurally. `validate` rejects malformed entries.
- Work items may declare `evidence_packs: [slugs]`; `check-completion` fails naming any declared pack that lacks a draft-or-stable note linking it via `evidence:`.

## Details
- `validate` checks packs and the ledger before pair validation; a vault with neither is unaffected (all keys optional).
- A pack with files missing from its manifest body — or listing files absent on disk — fails validation; packs are expected flat (one directory of payload files).
- Deprecated notes never satisfy evidence linkage; drafts do.

## Linked Concepts
- [Projection audience routing](./projection-audience-routing.md): how validated notes project into the Skill Pair.
- [Projection CLI extension conventions](./cli-extension-conventions.md): contributor-side conventions for extending this CLI.
- [Notation](./notation.md): standard symbols.
