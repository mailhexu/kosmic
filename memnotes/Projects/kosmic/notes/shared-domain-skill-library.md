---
type: Project Knowledge
title: Shared Domain Skill Library
description: How Kosmic stores, classifies, resolves, governs, migrates, and installs bounded cross-project Domain Topics.
confidence: 0.9
created: '2026-09-06'
updated: '2026-09-07'
validation_procedure: "python3 -m unittest tests.test_shared_library tests.test_project_skills_cli; kosmic_project_skills.py validate-library --vault {VAULT}"
project: kosmic
status: stable
audience: usage
artifact_role: knowledge
usage_stale: false
tags: [shared-library, routing, governance]
evidence: [evidence/2026-09-06-shared-domain-skill-library/session-record.md, evidence/2026-09-06-shared-domain-skill-library/review-findings.md, evidence/2026-09-07-semantic-artifact-roles/session-record.md, evidence/2026-09-07-semantic-artifact-roles/review-findings.md]
---

# Shared Domain Skill Library

## Overview

Kosmic keeps reusable software knowledge in one authoritative vault-level `Skills/` tree rather than installing one Usage/Development pair per Project. Exactly one `memnotes-skills` router is native-discoverable; compact Domain Skills and atomic Domain Topics load dynamically through deterministic, role-aware CLI plans.

## Invariants

- `Skills/SKILL.md` is the root router source; `Skills/{domain}/SKILL.md` owns domain identity, routing, and Maintainers.
- Every `Skills/{domain}/{usage|development}/{slug}.md` is a Domain Topic with an audience-independent `artifact_role`: knowledge informs, guidelines constrain, procedures direct, and dated evidence substantiates.
- Procedures alone are executable. They declare a bounded outcome and behavioral sections for trigger, preconditions, ordered actions, decisions, verification, failure handling, and references.
- Typed relationships are `requires_procedures`, `governed_by`, `uses_knowledge`, `supported_by`, and evidence-only `supersedes`; target roles, status, containment, dates, and cycles validate fail-closed.
- `resolve-library` deterministically infers or accepts `--intent do|check|understand|investigate`. Each intent selects only its corresponding primary role; `do` without a procedure returns `NO_EXECUTABLE_MATCH`.
- Recipe Packets label role and relation. Task packets load prerequisites, governing guidelines, and required knowledge before the primary procedure; evidence is opt-in for investigation rather than ordinary execution.
- `generate-library` derives catalogs, manifests, and domain indexes. `load-library` rechecks every source hash and exact framed UTF-8 byte total.
- Cross-project learning uses Task P only for procedures, with `library-skill://{domain}/{audience}/{slug}` and target-Maintainer approval.
- Migration requires explicit target, role, and typed relationships for every topic, preserves provenance, validates the complete staged graph, then swaps atomically.
- `install-library` installs and verifies one router before removing managed per-Project pairs. Unmanaged collisions and failures preserve the prior complete inventory.
- On-disk adapter verification is not runtime activation. Start a fresh session and inspect native skill inventory before claiming discovery.
