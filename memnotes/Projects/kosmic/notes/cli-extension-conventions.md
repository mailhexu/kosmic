---
type: Project Knowledge
title: Projection CLI extension conventions
description: Where new vault-layer features hook into the Projection CLI and the failure modes observed extending it.
confidence: 0.8
created: '2026-09-02'
updated: '2026-10-22T07:14:50.506Z'
skill_candidate: true
validation_procedure: "python3 -m unittest tests.test_project_skills_cli; kosmic_project_skills.py validate --project {VAULT}/Projects/{TARGET}"
project: kosmic
status: stable
audience: development
artifact_role: guideline
usage_stale: false
tags: []
evidence: [evidence/2026-09-02-experience-compilation-impl/session-record.md]
skill_resources: [kosmic/development/cli-extension-conventions]
---

# Projection CLI extension conventions

## Overview
Conventions learned while extending `scripts/kosmic_project_skills.py` with gated validation surfaces (mathdocs, proposals, completion), and the failure modes that recurred.

## Principles
- **Structural exclusion beats filtering.** Anything that must never project (specs, logs, `evidence/`) lives as a sibling of `notes/`, not inside it: `validate_notes_bundle` and `collect_projection_plan` walk only `notes_dir`, so exclusion costs zero code and cannot regress.
- **Gates run before early returns.** Any completion gate sits *before* the `if not affects_interface: return` — otherwise non-interface work items silently skip it. Any new gate must be pinned by a test that exercises the early-return path.
- **Derived state writes only after success.** Generated artifacts (indexes, projections, manifests) are written strictly after `publish_directory` succeeds and only when publishing to the canonical root; a failed generate leaves them untouched (`KOSMIC_FAIL_STAGE` injection tests this).
- **Optional frontmatter is absent-compatible.** New keys (`skill_candidate:`, `skill_resources:`) must make absent ≡ no-op so existing vaults regenerate with zero note edits; retired keys (`evidence:`, `evidence_packs:`) likewise read as absent ≡ no-op.

## Details
- Projection-affecting note edits pair with regeneration in the same atomic publication; a stable note plus a stale projection fails validation loudly (by design).
- Line-anchored edits on a file that your own edits keep renumbering misfire: re-read the target region immediately before every anchor. Three misfires this session, all from stale line numbers.
- Historical inspection uses structural reporting facts, not weakened operational loaders; invocation-only audit state never enters generators or mutation gates. Keep the [consumer history contract](./cli-projection-commands.md) coherent when extending this seam.

## Linked Concepts
- [Projection audience routing](./projection-audience-routing.md): what the projection pipeline does with the notes bundle this note's conventions extend around.
- [Notation](./notation.md): standard symbols.
