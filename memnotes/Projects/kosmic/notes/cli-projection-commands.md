---
type: Project Knowledge
title: Projection CLI experience commands
description: What the Projection CLI validates and enforces for evidence packs, executable MathDocs, Skill Proposals, projections, installation, and work-item completion.
confidence: 0.9
created: '2026-09-02'
updated: '2026-09-06'
validation_procedure: "python3 -m unittest tests/test_project_skills_cli; kosmic_project_skills.py validate --project {VAULT}/Projects/{TARGET}"
project: kosmic
status: stable
audience: usage
usage_stale: false
tags: []
evidence: [evidence/2026-09-02-experience-compilation-impl/session-record.md, evidence/2026-09-05-math-derivation-layer-impl/session-record.md, evidence/2026-09-06-skill-proposal-loop-impl/session-record.md]
---

# Projection CLI experience commands

## Overview
How the Projection CLI treats Project evidence, executable MathDocs, Skill Proposals, projections, installation, and work-item completion. Structural commands are deterministic, offline, and stdlib-only; `check-math` executes trusted Project Python and therefore requires the Project derivation environment.

## Principles
- Projected references are package-consistent: a link whose target is not in the same package (drafts, other-audience notes) is demoted to bold plain text; `generate` warns on stderr naming each demoted link. Code fences, external URLs, and non-Markdown targets are untouched.
- Notes may declare `evidence: [paths]` (Project-root-relative). `validate` fails a **stable** note whose paths do not resolve; drafts may reference pending packs.
- `impact.md` at the Project root is an append-only ledger of six-field entries (`date, kind, targets, refs, outcome, reason`). `generate` appends publication entries automatically after each atomic publication to the canonical root; review decisions are appended procedurally. `validate` rejects malformed entries.
- Work items may declare `evidence_packs: [slugs]`; `check-completion` fails naming any declared pack that lacks a draft-or-stable note linking it via `evidence:`.
- Every Project has a vault-only `mathdocs/` registry. Stable Math Derivations carry the current script SHA-256, Python/SymPy versions, verification time, host, and source directory. Stable regular notes mark each display equation with a resolvable `MathDoc` result or exposition identifier.
- Task P proposal artifacts use `draft -> approved -> done` status and `pending -> accepted|rejected` decisions. `validate-proposal` checks a SHA-pinned curated input manifest, scope/independence policy, immutable fingerprints, execution-pack behavioral evidence, and project-relative candidate isolation. `check-completion` enforces the proposal gate before its Consumer Interface early return.

## Details
- `validate` checks packs and the ledger before pair validation; a vault with neither is unaffected (all keys optional).
- A pack with files missing from its manifest body — or listing files absent on disk — fails validation; packs are expected flat (one directory of payload files).
- Deprecated notes never satisfy evidence linkage; drafts do.
- `check-math --project PROJECT [--slug SLUG]` executes active derivations in lexical order with a bounded timeout, reports every selected file as PASS or FAIL plus a summary, and compares their versioned JSON protocol, environment, source hash, and named results against the paired notes. It warns that execution is trusted and not sandboxed.
- After reviewing changed symbolic output, `check-math --update --source-root REPO` stages all selected paired-note metadata and generated result regions, then publishes the complete `mathdocs/` tree or nothing. Update dependent regular notes and implementation from those published canonical results before rerunning `validate` and completion.
- Math-derived work items declare both `derivations` and a finite `math_implementation_files` list. `check-completion --source-root REPO` requires each source file to stay under that root and carry an adjacent `MathDoc: project/slug[#result]` identifier.
- `check-installation` byte-compares both named-adapter packages and their Project identity against the canonical pair. Success proves on-disk installation only; reload the adapter and inspect its skill inventory before claiming active-session discovery.

## Linked Concepts
- [Projection audience routing](./projection-audience-routing.md): how validated notes project into the Skill Pair.
- [Projection CLI extension conventions](./cli-extension-conventions.md): contributor-side conventions for extending this CLI.
- [Notation](./notation.md): standard symbols.
