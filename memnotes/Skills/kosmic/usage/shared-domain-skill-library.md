---
type: Domain Topic
id: kosmic/usage/shared-domain-skill-library
domain: kosmic
audience: usage
status: stable
summary: Maintain and use Kosmic's bounded Shared Domain Skill Library.
triggers: [shared skill library, resolve library, install shared router, cross-project procedure]
aliases: [memnotes skills, domain skill]
evidence: [evidence/2026-09-06-shared-domain-skill-library/session-record.md, evidence/2026-09-06-shared-domain-skill-library/review-findings.md]
source_project: kosmic
source_sha256: 9ce1f5d0d7334d945b57561e8d8e9266e55aa893ae30496e100abfdd6e98dbdc
artifact_role: knowledge
requires_procedures: []
governed_by: []
uses_knowledge: []
supported_by: []
supersedes: []
source: notes/shared-domain-skill-library.md
---

# Shared Domain Skill Library

## Overview

Kosmic keeps reusable software procedures in one authoritative vault-level `Skills/` tree rather than installing one Usage/Development pair per Project. Exactly one `memnotes-skills` router is native-discoverable; compact Domain Skills and atomic topic Markdown load dynamically through deterministic CLI plans.

## Invariants

- `Skills/SKILL.md` is the root router source; `Skills/{domain}/SKILL.md` owns domain identity, routing, and Maintainers.
- Detailed procedures are ordinary `Skills/{domain}/{usage|development}/{slug}.md` files. They never require their own native `SKILL.md`.
- `generate-library` derives catalogs, manifests, and domain indexes. Generated files are disposable and never hand-edited.
- `resolve-library` accepts exactly one explicit route or query and returns one canonical hash-pinned plan. Domain routes load only the domain router; topic routes and queries close declared dependencies.
- `load-library` rechecks the plan, manifest, every source hash, and the exact framed UTF-8 byte total before emitting a Recipe Packet.
- Draft/deprecated topics and invalid dependency or audience edges fail closed. Ambiguity and any byte/domain/topic overflow emit no recipe body.
- Cross-project learning uses Task P with `library-skill://{domain}/{audience}/{slug}`. Evidence stays in its source Project; a target Domain Maintainer approves publication.
- Migration requires one explicit assignment for every old projected reference, preserves source hash, source Project, audience, and Evidence, stages generated artifacts, then swaps the complete library atomically.
- `install-library` installs and verifies one router before removing managed per-Project pairs. Unmanaged collisions and failures preserve the prior complete inventory.
- On-disk adapter verification is not runtime activation. Start a fresh session and inspect native skill inventory before claiming discovery.

## Source-linked topics (FR-010)

The existing `generate-library` flow, run under the Project's own approved work record, syncs each note's `skill_resources` to stable topic IDs that actually use it; that sync is bookkeeping and never bumps the note's semantic `updated`. From the note's final bytes it rederives the current topic body, the full raw source-byte hash for every linked topic, and the affected current Project pair and library manifests; current topics persist `source: notes/…` stable identities so a pair-first regeneration never loses the mapping. Failures restore the prior metadata and publications. Direct source-backed topic IDs are the current existing model — a source link, not a hash wish list — and nothing scans all vault data. Historical curated snapshots and old work-record pins stay untouched, there is no per-note queue and no new report, and the flow never auto-approves or installs anything.

Reconciliation changes only IDs owned by the current or prior publication; unrelated actual-use IDs survive. A source note must permit its topic's audience (`both` permits Usage and Development); incompatible remapping fails closed. Retain the prior library backup through validation of the published tree, and roll back the library, note metadata and pair together to their call-entry state without discarding pre-existing caller edits.
