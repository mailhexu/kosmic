---
type: Project Knowledge
title: Projection CLI extension conventions
description: Where new vault-layer features hook into the Projection CLI and the failure modes observed extending it.
confidence: 0.8
created: '2026-09-02'
updated: 2026-09-02
validation_procedure: "python3 -m unittest tests.test_project_skills_cli; kosmic_project_skills.py validate --project {VAULT}/Projects/{TARGET}"
project: kosmic
status: stable
audience: development
usage_stale: false
tags: []
evidence: [evidence/2026-09-02-experience-compilation-impl/session-record.md]
---

# Projection CLI extension conventions

## Overview
Conventions learned while adding the Experience layer (evidence packs, note linkage, impact ledger, completion gate) to `scripts/kosmic_project_skills.py`, and the failure modes that recurred.

## Principles
- **Structural exclusion beats filtering.** Anything that must never project (evidence packs, `impact.md`) lives as a sibling of `notes/`, not inside it: `validate_notes_bundle` and `collect_projection_plan` walk only `notes_dir`, so exclusion costs zero code and cannot regress.
- **Gates run before early returns.** `check_completion`'s evidence gate sits *before* the `if not affects_interface: return` — otherwise non-interface work items silently skip it. Any new gate must be pinned by a test that exercises the early-return path.
- **Append-only state appends only after success.** The ledger is written strictly after `publish_directory` succeeds and only when publishing to the canonical root; a failed generate leaves it untouched (`KOSMIC_FAIL_STAGE` injection tests this).
- **Optional frontmatter is absent-compatible.** New keys (`evidence:`, `evidence_packs:`) must make absent ≡ no-op so existing vaults regenerate with zero note edits.

## Details
- Stable-note `evidence:` paths are Project-root-relative because packs live outside `notes/`; note-relative paths would need `../` everywhere. Drafts may dangle.
- Ledger entries are single Markdown bullets with six fixed fields separated by ` | `; a reason containing ` | ` fails validation loudly (by design).
- Line-anchored edits on a file that your own edits keep renumbering misfire: re-read the target region immediately before every anchor. Three misfires this session, all from stale line numbers.

## Linked Concepts
- [Projection audience routing](./projection-audience-routing.md): what the projection pipeline does with the notes bundle this note's conventions extend around.
- [Notation](./notation.md): standard symbols.
