---
status: "approved"
created: "2026-09-06"
updated: "2026-09-06"
linked_prd: "prd.md"
linked_stories: ["stories/story-001-library-schema-catalog.md", "stories/story-002-deterministic-library-resolver.md", "stories/story-003-cross-project-domain-governance.md", "stories/story-004-shared-router-installation.md", "stories/story-005-shared-library-migration.md", "stories/story-006-shared-library-dogfood-release.md"]
project_id: "kosmic"
subproject_id: "shared-domain-skill-library"
record_kind: "architecture"
local_id: "architecture"
---

# Architecture: Shared Domain Skill Library

## System Overview

The feature replaces per-Project native Skill Pairs with one vault-level Shared Skill Library and one installed library router. `memnotes/Skills/` is authoritative. Its root `SKILL.md` is the library router; each immediate domain directory, such as `abinit/`, owns exactly one dynamically loaded `SKILL.md`; Usage and Development procedures below a domain remain ordinary atomic Markdown topics. The existing Kosmic workflow Orchestrator remains a separate global skill.

A deterministic Resolver Module accepts a Project, role, query or explicit route, and hard byte budget. It selects domain roots, topic notes, and declared cross-domain dependency closure from a generated catalog, returns a hash-pinned resolution plan, then loads that plan as one bounded Recipe Packet. Install Adapters expose only the root library router. Cross-project learning flows from source-Project Evidence Packs through a Skill Proposal reviewed by the target domain Maintainer.

```text
memnotes/
├── Projects/{project}/{notes,evidence,specs,log,...}
└── Skills/
    ├── SKILL.md
    ├── .kosmic/{catalog.json,manifest.json}
    ├── abinit/
    │   ├── SKILL.md
    │   ├── index.md
    │   ├── usage/*.md
    │   └── development/*.md
    └── tb2j/
        ├── SKILL.md
        ├── index.md
        ├── usage/*.md
        └── development/*.md
```

## Technical Decisions

### AD-SD1: Domain-root fracture seam

**Status**: Proposed

**Context**: A `SKILL.md` for every topic recreates discovery and maintenance overload; one monolithic skill loads too much. The stable ownership and routing seam is the maintained software domain.

**Decision**: only `Skills/SKILL.md` and each immediate Skill Domain directory have `SKILL.md`. A Domain Skill is a router and compact domain contract. Descendant Usage/Development files are ordinary Skill Topics, not native or nested Agent Skills. A Domain Skill may route to arbitrarily many topics through its generated `index.md`, but its own size is bounded.

**Consequences**: ABINIT and TB2J can be loaded independently or together without multiplying native skill inventory. Topic edits remain local and atomic. Domain routers require curated trigger and ownership metadata.

**Alternatives Considered**: one native skill per domain (rejected: inventory grows with domains); `SKILL.md` per topic (rejected: excessive discovery and shallow routers); only loose notes with no domain router (rejected: weak ownership and navigation).

### AD-SD2: Authoritative vault tree and generated indexes

**Status**: Proposed

**Context**: Generated projections must not become a second source of truth.

**Decision**: root/domain `SKILL.md` files and topic Markdown under `Skills/` are authoritative reviewed content. `Skills/.kosmic/catalog.json`, `manifest.json`, and each domain `index.md` are deterministic disposable indexes. Generation stages the complete index set, validates it against source bytes, and atomically replaces only generated artifacts. It never rewrites authoritative bodies.

`manifest.json` records schema/generator versions, library identity, working state, root hash, catalog hash, domain source hashes, and generation policy. Catalog entries are lexically sorted by stable ID.

**Consequences**: Obsidian and Git remain sufficient for authoring and review. Index drift is machine-detectable. Generated files can be deleted and rebuilt.

**Alternatives Considered**: copy Project notes into installed skills (rejected: duplicate authority); make JSON canonical (rejected: poor human review); mutate authoritative routers during generation (rejected: hidden authoring side effect).

### AD-SD3: Flat metadata contracts

**Status**: Proposed

**Context**: Kosmic's parser supports flat YAML and must remain stdlib-only.

**Decision**: the root router declares `type: Shared Skill Router`, `id: memnotes-skills`, `status`, `description`, and hard policy limits. A Domain Skill declares `type: Domain Skill`, unique lower-kebab `id`, `status`, `description`, `maintainers`, `triggers`, and optional `aliases`. A Skill Topic declares `type: Skill Topic`, globally unique `{domain}/{usage|development}/{slug}` ID, domain, audience, status, summary, triggers, aliases, `requires`, evidence paths, and optional freshness metadata. Lists remain flat scalar arrays.

Domain ownership is resolved from the target domain `SKILL.md`; topic files cannot override Maintainers. Topic dependency references use IDs, never filesystem traversal paths.

**Consequences**: one parser validates all library content. Stable IDs survive title or file-description changes. Maintainer authority is centralized at the domain root.

**Alternatives Considered**: nested YAML (rejected: parser and schema weight); infer metadata from prose (rejected: nondeterministic); repeat Maintainers on every topic (rejected: drift).

### AD-SD4: One deep resolver interface

**Status**: Proposed

**Context**: Agents need progressive navigation when they know the domain and query routing when they do not. These modes must not diverge semantically.

**Decision**: expose two operations through the Projection CLI:

```text
resolve-library --vault VAULT [--project PROJECT]
  (--query TEXT | --route ID)
  --role usage|development|auto
  --max-bytes N --max-domains N --max-topics N

load-library --vault VAULT --plan FILE
```

`resolve-library` emits canonical JSON `ResolutionPlan` containing normalized request, library manifest hash, selected domain roots, selected topics, dependency-first order, individual and total UTF-8 byte costs, source hashes, deterministic trace, exclusions, and `plan_sha256`. `load-library` accepts only a byte-identical plan whose self-hash, manifest, and selected source hashes still match; it emits the ordered Markdown Recipe Packet. It performs no new ranking.

The Resolver Module is the sole seam for eligibility, ranking, dependency closure, budget admission, and integrity. Adapters invoke it but do not implement its semantics.

**Consequences**: plans are auditable and loading is race-safe. The two command round trip is explicit. Callers learn one interface while complex routing remains local.

**Alternatives Considered**: have agents manually read arbitrary notes (rejected: inconsistent selection and budgets); one command that resolves and loads (rejected: weak audit/race seam); separate progressive and search implementations (rejected: divergent behavior).

### AD-SD5: Progressive-plus-query selection

**Status**: Proposed

**Context**: Pure menus add hops; pure lexical search can miss known routes.

**Decision**: explicit `--route` wins and resolves an exact domain or topic ID. Query mode applies NFKC normalization and case folding, then filters status/freshness/audience. Integer scoring prioritizes exact domain/ID, trigger and alias phrases, title, summary, and tags. Current Project identity is a deterministic domain boost, not an eligibility restriction. Equal top scores return an ambiguity result with at most five candidates instead of guessing. Lexical ID is the final ordering tie-break, never a hidden relevance decision.

After the primary topic set is chosen, declared dependencies determine all additional domains/topics. Selection trace records every match, score, boost, exclusion, and dependency edge.

**Consequences**: known routes are predictable, unfamiliar tasks remain searchable, and output is reproducible offline. Authors must maintain useful summaries and triggers.

**Alternatives Considered**: embeddings (deferred optional Adapter; rejected as required semantics); full-text unweighted search (rejected: noisy); LLM selection over the whole catalog (rejected: context and reproducibility failure).

### AD-SD6: Complete-packet budget admission

**Status**: Proposed

**Context**: A relevant packet can still overflow context, particularly across scientific domains.

**Decision**: account exact UTF-8 body bytes plus fixed generated framing. Defaults are root router 2 KiB, each Domain Skill 6 KiB, each topic 12 KiB, packet 32 KiB, four domains, and eight topics; Architecture constants are configurable downward by adapters but not silently upward beyond library policy. Compute transitive closure, deduplicate IDs, topologically order dependencies, then admit the complete packet. Any body or closure overrun yields `BUDGET_EXCEEDED` with required/available costs and no bodies. Never truncate, split automatically, or omit a prerequisite.

**Consequences**: admission is tokenizer-independent and safe. Conservative byte limits may reject packets that one model could fit; explicit authoring splits are required at independent procedural seams.

**Alternatives Considered**: model tokenizers (rejected: portability); greedy partial loading (rejected: invalid procedures); automatic paragraph chunking (rejected: destroys procedural invariants).

### AD-SD7: Typed dependency graph and cross-domain composition

**Status**: Proposed

**Context**: TB2J workflows may depend on ABINIT procedures, but copying those procedures creates drift.

**Decision**: `requires` contains exact Skill Topic IDs. Loading a topic also loads its owning Domain Skill and transitive topic dependencies. The catalog validator rejects unknown IDs, self-dependencies, cycles, audience-incompatible dependencies, and dependencies on ineligible content. Development may depend on Usage; Usage must not depend on Development. Cross-domain edges are first-class and reported in the plan trace.

**Consequences**: shared ABINIT procedures remain single-source while multi-domain packets are complete. Dependency curation becomes an explicit review responsibility.

**Alternatives Considered**: Markdown links as dependencies (rejected: ambiguous semantics); duplicate foreign instructions (rejected: drift); load entire dependent domain (rejected: context explosion).

### AD-SD8: Cross-project evidence and target-domain governance

**Status**: Proposed

**Context**: the Project that discovers a procedure and the Skill Domain that owns it may differ.

**Decision**: Evidence Packs remain under their source Project. Task P gains shared-library targets such as `library-skill://abinit/usage/export-wavefunctions`. A proposal records source Project, target domain/topic, target hash for updates, evidence references, proposer independence, `approved_by`, and the target Maintainer decision. Validation may resolve explicitly declared `Projects/.../evidence/...` references within the same vault while retaining containment. `approved_by` must exactly match one identifier in the target Domain Skill's flat `maintainers` list before approval or acceptance validates. The CLI validates this recorded policy claim; independent Task 7 review confirms the human authorization. Accepted content is authored under `Skills/{target-domain}/`; rejected fingerprints remain in the Impact Ledger.

No proposal may change both source-Project knowledge and target-domain library content atomically; those are separate reviewed artifacts linked by evidence.

**Consequences**: TB2J can teach ABINIT without taking ownership of ABINIT. Provenance points to where behavior was observed. Maintainer authorization is explicit and machine-checkable without pretending the CLI authenticates a human identity.

**Alternatives Considered**: direct cross-domain edits from a Project Story (rejected: weak ownership); copy evidence into the target domain (rejected: duplicate evidence); central Maintainer for every domain (rejected: bottleneck).

### AD-SD9: Single-router adapter cutover

**Status**: Proposed

**Context**: adapters currently expose two packages per Project.

**Decision**: generation produces one canonical installable router package whose `SKILL.md` points to the vault library and resolver command; it does not contain a domain catalog or bodies. Named Install Adapters atomically install this one package and remove every managed per-Project pair only after new-router byte/identity verification. Unmanaged colliding paths fail without deletion. `check-library-installation` verifies disk state; activation remains unverified until adapter reload and inventory observation.

The Kosmic workflow Orchestrator remains installed independently and routes authoring/governance work, not scientific recipes.

**Consequences**: shared-library discovery cost is constant. Installation requires reliable vault accessibility or command output. Clean cutover avoids aliases and duplicate routing.

**Alternatives Considered**: install every Domain Skill (rejected: growing inventory); retain pairs as deprecated aliases (rejected: duplicate discovery); embed all topics in the root (rejected: context overload).

### AD-SD10: Staged migration with behavioral equivalence

**Status**: Proposed

**Context**: current stable Project topics and their evidence/provenance must survive the authority change.

**Decision**: migration is explicit and staged: inventory every current pair source; propose a target domain and topic ID; preserve source/evidence metadata; author candidate domain routers/topics under a staging tree; generate and validate the catalog; compare representative old-router and new-resolver task outcomes; obtain Maintainer and Task 7 approval; publish `Skills/` atomically; install the root router; verify bytes; then remove managed old pairs. Migration aborts on collisions, unassigned topics, changed source hashes, behavioral regressions, or adapter failure.

Kosmic itself is the first dogfood domain. ABINIT and TB2J are the required cross-domain fixture before general migration.

**Consequences**: no topic silently disappears. Migration is heavier than a directory move but proves routing and provenance behavior before destructive cutover.

**Alternatives Considered**: migrate all Projects automatically by slug (rejected: domain ownership is semantic); dual-run indefinitely (rejected: duplicate authority); delete pairs before validation (rejected: unsafe).

## Data Models

```text
LibraryManifest
  schema_version
  generator_version
  library_id
  working_state
  root_sha256
  catalog_sha256
  policy
  domains[]

DomainEntry
  id
  path
  sha256
  description
  maintainers[]
  triggers[]
  aliases[]
  context_bytes

TopicEntry
  id
  domain
  audience
  path
  sha256
  title
  summary
  triggers[]
  aliases[]
  requires[]
  context_bytes
  source_refs[]

ResolutionPlan
  schema_version
  request
  manifest_sha256
  domains[]
  topics[]
  ordered_loads[]
  total_bytes
  trace[]
  exclusions[]
  plan_sha256
```

## Error Contract

- `NO_MATCH`: no eligible domain/topic; returns bounded candidates without bodies.
- `AMBIGUOUS`: equal qualifying routes; returns at most five candidates.
- `STALE_LIBRARY`: authoritative or generated hash drift; regenerate.
- `BROKEN_DEPENDENCY`: missing or ineligible required topic.
- `DEPENDENCY_CYCLE`: cycle with complete ID path.
- `BUDGET_EXCEEDED`: required and allowed byte/domain/topic counts.
- `INVALID_PLAN`: plan hash, manifest hash, request, or selected hashes differ.
- `OWNERSHIP_REQUIRED`: target-domain Maintainer approval absent.
- `INSTALLATION_COLLISION`: unmanaged destination would be replaced.

Every failure returns no Recipe bodies.

## Test Strategy

1. Parser and schema tests for root router, Domain Skill, and Skill Topic metadata.
2. Catalog tests for stable ordering, hashes, identity, stale/deprecated omission, link containment, and exact regeneration.
3. Resolver contract tests for explicit routes, query scoring, Project boost, ambiguity, audience filtering, and byte-identical plans.
4. Dependency tests for cross-domain closure, deduplication, topological order, unknown IDs, cycles, and Usage-to-Development rejection.
5. Budget boundary tests for exact fit, one-byte overflow, domain/topic caps, oversized leaves, and all-or-none output.
6. Plan loading tests for valid loads and every hash/race failure.
7. Governance tests for TB2J evidence targeting ABINIT, target Maintainer approval, rejection memory, and vault containment.
8. Atomic generation/install rollback tests and unmanaged collision tests.
9. Migration fixture preserving current source hashes/evidence/audience and rejecting unassigned topics.
10. Behavioral dogfood: Kosmic domain routing plus a TB2J-development query that loads ABINIT Usage dependencies and no unrelated topics.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Domain routers become large catalogs | High | Generated indexes hold topic listings; Domain `SKILL.md` has a hard size bound. |
| Lexical routing misses relevant topics | Medium | Reviewed triggers/aliases, explicit routes, ambiguity output, and trace-driven maintenance. |
| Cross-domain dependency growth exceeds context | High | Exact closure accounting, domain/topic caps, no partial loads, and narrower explicit recipes. |
| Maintainer ownership becomes unavailable | Medium | Fail closed; retain proposal and evidence pending another declared Maintainer. |
| Vault is inaccessible to an adapter | High | Resolver can emit the same verified packet; unsupported adapters cannot flatten the library. |
| Migration loses project-local nuance | High | No automatic slug-only migration; explicit domain assignment and behavioral comparison. |
| Root router and Kosmic Orchestrator appear duplicative | Medium | Router handles runtime recipe retrieval; Orchestrator handles authoring, specification, evidence, and governance. |

## Implementation Boundaries

The Projection CLI owns schemas, validation, catalog generation, resolution, plan loading, migration, and install verification. The Kosmic Orchestrator owns Task selection and governance. Domain Maintainers own domain routers and topic acceptance. Install Adapters own only host paths, pointers, and reload instructions. No adapter may rank topics, relax budgets, or reinterpret dependency semantics.
