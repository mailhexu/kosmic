---
status: done
created: 2026-09-07
updated: 2026-09-07
linked_epic: ../epics/epic-18-role-aware-resolution.md
linked_architecture: ../architecture-semantic-artifact-roles.md
linked_prd: ../prd-semantic-artifact-roles.md
related_notes: [shared-domain-skill-library.md]
evidence_packs: [2026-09-07-semantic-artifact-roles]
consumer_interface_change: true
proposal_required: false
review_base: ""
review_round: 2
---

# Story 033: Intent and Role-Aware Primary Selection

## User Story

As an agent using the shared router, I want actionable and reference requests resolved differently, so that only approved procedures direct work while knowledge and evidence remain clearly informational.

## Acceptance Criteria

- [x] Resolver and CLI accept an optional `do|check|understand|investigate` intent override.
- [x] Without an override, a versioned deterministic classifier infers intent; ties fail with `AMBIGUOUS_INTENT`.
- [x] `do` scores stable audience-eligible procedures only and fails `NO_EXECUTABLE_MATCH` rather than falling back.
- [x] `check`, `understand`, and `investigate` follow AD-SR6 primary-role and fallback rules and label reference mode.
- [x] Investigation excludes transitively superseded evidence unless explicitly routed.
- [x] The plan hash covers intent, origin, mode, primary topic, trace, and exclusions.

## Tasks

- [x] Pin inference, override, ambiguity, role filtering, route, and failure contracts with red tests.
- [x] Implement intent classification and primary eligibility within `resolve_library`.
- [x] Expose CLI arguments and actionable output.
- [x] Run focused and full regression suites.
- [x] Run mandatory Standards and Spec review.

## Definition of Done

- [x] Equivalent explicit and inferred requests produce byte-identical semantic selections.
- [x] No actionable result is sourced from knowledge, guideline, or evidence.
- [x] Code review converges with no blocking findings.
