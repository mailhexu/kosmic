---
status: approved
created: 2026-09-06
updated: 2026-09-06
linked_research: []
linked_epics: [epics/epic-14-shared-library-foundation.md, epics/epic-15-shared-library-governance.md, epics/epic-16-shared-library-migration-release.md]
---

# Shared Domain Skill Library

## Problem Statement

Kosmic currently projects each Project into one installed Usage Skill and one installed Development Skill. Topic bodies are already separated into references, but the number of discoverable native skills grows as two times the number of Projects, while each Project router accumulates a flat topic list. Multi-project scientific work also exposes an ownership gap: work in TB2J may produce reusable ABINIT operating knowledge, yet the fixed per-Project pair has no shared domain destination or governed cross-project contribution path.

Kosmic needs one vault-level library that keeps native skill discovery constant, loads only task-relevant domain guidance, and permits evidence from one Project to improve another maintained domain without duplicating procedures or bypassing the target Maintainer.

## Goals

- Keep native agent discovery bounded to one installed Shared Skill Router regardless of Project or domain count.
- Organize reusable guidance by maintained software domain, with one dynamically loaded `SKILL.md` at each domain root and ordinary Usage/Development topic notes beneath it.
- Resolve tasks through progressive domain navigation plus deterministic query routing, loading a bounded packet rather than an entire library.
- Keep shared-library native discovery bounded to one installed Shared Skill Router regardless of Project or domain count; the existing Kosmic workflow Orchestrator remains a separate global skill.
- Let evidence produced by any Project propose changes to the owning Skill Domain under target-domain Maintainer approval.
- Preserve authoritative Markdown, deterministic offline validation, provenance, atomic publication, and adapter-independent installation.

## Non-Goals

- Make every subtopic or recipe a native or nested Agent Skill with its own `SKILL.md`.
- Inject every domain, topic description, or recipe into always-visible context.
- Infer dependencies or ownership from recipe prose using an LLM.
- Use embeddings, network services, or model-specific tokenizers for required routing behavior.
- Allow a source Project to directly publish accepted guidance into another domain without target-domain review.
- Retain the current per-Project Usage/Development Skill Pair as a compatibility alias after cutover.

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-SD01 | The vault must contain one authoritative `Skills/` tree beside `Projects/`; shared procedural guidance must not be stored as generated content inside a Project. | must |
| FR-SD02 | `Skills/SKILL.md` must project to the sole native Agent Skill entry point for the Shared Skill Library and must route without embedding domain topic bodies or an unbounded domain catalog; it does not replace the Kosmic workflow Orchestrator. | must |
| FR-SD03 | Every Skill Domain must have exactly one root `{domain}/SKILL.md` containing domain identity, trigger description, Maintainer ownership, routing rules, and links to its Usage and Development topics. | must |
| FR-SD04 | Detailed Usage and Development topics must remain ordinary atomic Markdown notes; subtopics must not require `SKILL.md`. | must |
| FR-SD05 | The resolver must support both explicit progressive routes and deterministic query-based domain/topic selection through one interface. | must |
| FR-SD06 | A resolution result must include the selected domain roots, selected topic notes, transitive declared dependencies, byte cost, source hashes, and a deterministic selection trace. | must |
| FR-SD07 | Topics may declare dependencies on other Skill Domains and their topics; the resolver must load cross-domain dependencies once, in dependency-first order, and reject missing dependencies or cycles. | must |
| FR-SD08 | Resolution must enforce configurable limits for total UTF-8 bytes, loaded domains, and loaded topics; it must reject overflow without truncating a topic or omitting a required dependency. | must |
| FR-SD09 | Generation must build a canonical catalog from reviewed domain and topic metadata, validate paths, identities, hashes, ownership, dependency closure, and budget metadata, then publish atomically. | must |
| FR-SD10 | Draft, deprecated, stale, invalid, or unreviewed topics must not be loadable; source or catalog drift must fail closed with regeneration guidance. | must |
| FR-SD11 | Evidence produced in one Project may support a Skill Proposal targeting another Skill Domain; acceptance must require the target domain's Maintainer review and preserve source-Project evidence provenance. | must |
| FR-SD12 | The same task may load multiple domain roots, such as TB2J plus ABINIT, without copying ABINIT procedures into TB2J topics. | must |
| FR-SD13 | Install Adapters must expose only the Shared Skill Router through native discovery; domain `SKILL.md` files and topic notes must be loaded dynamically from the vault or emitted by the resolver. | must |
| FR-SD14 | Installation checks must verify router identity and bytes separately from active-session discovery, preserving the existing honest activation boundary. | must |
| FR-SD15 | Migration must convert eligible current Project Skill Pair topics into domain topics with source/evidence provenance, validate behavioral equivalence, switch all adapters atomically, and remove the old installed pairs in one clean cutover. | must |
| FR-SD16 | The library must expose deterministic commands to validate the library, resolve a task, load a pinned resolution plan, generate its catalog/router, install it, and check installed bytes. | must |

## Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-SD01 | All required generation, validation, routing, hashing, and budget behavior must remain deterministic, offline, and Python 3.11+ standard-library-only. | must |
| NFR-SD02 | Shared-library native discovery cost must remain constant as Projects, Skill Domains, and topics are added. | must |
| NFR-SD03 | The same library snapshot, normalized request, and budget must produce byte-identical resolution plans and Recipe Packets. | must |
| NFR-SD04 | Paths must be vault-contained and traversal-safe; dynamic loading must verify catalog and content hashes before returning bodies. | must |
| NFR-SD05 | Resolver failures must be typed and actionable, including no match, ambiguity, stale catalog, broken dependency, dependency cycle, and budget overflow. | must |
| NFR-SD06 | Routers and topics must remain human-readable Markdown and Obsidian-compatible; generated JSON is disposable indexing state, not authority. | must |
| NFR-SD07 | A failed generation, migration, or installation must leave the prior complete valid state available and must never expose a partial tree. | must |
| NFR-SD08 | Adapter-specific paths and reload instructions must remain behind the existing Install Adapter seam; adapters must not own routing semantics. | must |
## Success Criteria

- [ ] Adding a tenth Skill Domain does not add another native-discovery skill or enlarge the installed root router beyond its configured bound.
- [ ] A TB2J development query using ABINIT selects both domain roots and only the declared TB2J and ABINIT topics needed for the task.
- [ ] A cross-project ABINIT proposal backed by TB2J evidence cannot publish until the ABINIT Maintainer accepts it.
- [ ] A missing dependency, dependency cycle, stale source hash, or undersized budget returns a deterministic failure and no partial packet.
- [ ] Progressive routing and equivalent query routing select the same topic closure for a pinned fixture.
- [ ] OpenCode, Claude Code, and Codex installations contain one discoverable Shared Skill Router and byte-verify against the canonical vault copy.
- [ ] Current Kosmic Project topics migrate without lost source hashes, evidence references, or Usage/Development classification.
- [ ] Existing projection, evidence, MathDoc, proposal, and completion behavior remains valid until the approved clean cutover.

## Open Questions

- [x] Where does shared skill knowledge live? In vault-level `Skills/`, beside `Projects/`.
- [x] What receives a `SKILL.md`? The global router and each root Skill Domain; detailed topics remain ordinary Markdown.
- [x] How is material selected? Progressive routing plus deterministic query resolution.
- [x] Can a task load multiple domains? Yes; explicit cross-domain dependencies are first-class.
- [x] Who governs cross-project learning? The target Skill Domain Maintainer approves proposals backed by source-Project evidence.
- [x] Are all domain skills installed natively? No; only the global router is native-discoverable.
