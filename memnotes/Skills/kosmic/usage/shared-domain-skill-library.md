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
source_sha256: f510ad15f2eac794baf95c3a96448834d35c11e29e2972e8445b84159e4bc940
artifact_role: knowledge
requires_procedures: []
governed_by: []
uses_knowledge: []
supported_by: []
supersedes: []
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
