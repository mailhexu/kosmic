# Kosmic Project Knowledge

Kosmic maintains authoritative knowledge for a software project and presents audience-specific agent guidance derived from that knowledge.

## Language

**Project**:
A software product or package whose contributor and consumer knowledge is managed as one named boundary.
_Avoid_: Target, workspace

**Project Identifier**:
An immutable, explicitly assigned, globally unique slug from which a Project's Skill Projection names are derived.
_Avoid_: Target, directory basename, display name

**Project Knowledge**:
The authoritative body of durable knowledge about a Project, shared as the source for its audience-specific guidance.
_Avoid_: Skill content, generated documentation

**Development Skill**:
A per-Project agent skill containing Contributor-only guidance; it refers to the paired Usage Skill for consumer and shared guidance rather than repeating it.
_Avoid_: Developer docs, internal skill

**Usage Skill**:
The single per-Project agent skill containing Consumer and shared guidance across all of the Project's Consumer Interfaces.
_Avoid_: User docs, quick-start skill, operations skill

**Skill Projection**:
An audience-specific agent skill package derived from Project Knowledge, with a concise Skill Router and topic references rather than an independently maintained or monolithic source.
_Avoid_: Generated copy, standalone skill

**Skill Pair**:
The exactly one Development Skill and one Usage Skill derived for a Project and delivered as one indivisible unit.
_Avoid_: Two skills, project skills

**Kosmic Orchestrator**:
The global skill that governs knowledge and development workflows and loads a Project's Development Skill when project-specific Contributor guidance is needed.
_Avoid_: Development Skill, project skill

**Install Adapter**:
An agent-specific mechanism that exposes a canonical vault-hosted Skill Pair through that agent's skill system.
_Avoid_: Skill Projection, installer

**Projection CLI**:
The deterministic Kosmic tool that validates, generates, drift-checks, and installs a Project's atomic Skill Pair.
_Avoid_: Agent procedure, skill generator

**Shared Skill Library**:
The authoritative vault-level `Skills/` tree containing maintained Domain Skills and atomic Skill Topics, exposed through one native Shared Skill Router.
_Avoid_: Project Skill Pair, global wiki

**Domain Skill**:
One maintained software-domain boundary, such as ABINIT or TB2J, represented by a compact dynamically loaded `SKILL.md` that owns routing and Maintainers.
_Avoid_: Every recipe, installed skill

**Skill Topic**:
One atomic Usage or Development procedure stored as ordinary Markdown beneath a Domain Skill.
_Avoid_: Subskill, `SKILL.md` per recipe

**Recipe Packet**:
A complete, dependency-closed, byte-bounded, hash-verified set of Domain Skills and Skill Topics loaded for one task.
_Avoid_: Whole library, partial context

**Shared Skill Router**:
The sole native Agent Skill entry point for the Shared Skill Library; it delegates deterministic selection and loading to the Projection CLI.
_Avoid_: Domain Skill, Kosmic workflow Orchestrator

**Projection Provenance**:
The source-note identity and content hash carried by a projected topic reference so drift can be detected without treating generated content as authoritative.
_Avoid_: Source link, generated metadata

**Audience Scope**:
The classification of Project Knowledge as relevant to Contributors, Consumers, or both.
_Avoid_: Category, skill type

**Projection-Eligible Knowledge**:
Validated Project Knowledge whose Audience Scope and applicability to the Working State permit it to appear in a Skill Projection.
_Avoid_: Publishable note, generated source

**Unscoped Knowledge**:
Legacy Project Knowledge without an explicit Audience Scope; it is treated as Contributor-only until reviewed.
_Avoid_: Shared knowledge, inferred usage knowledge

**Skill Router**:
The concise entry point of a Skill Projection that selects only the topic references needed for the current task.
_Avoid_: Skill summary, table of contents

**Working State**:
The checked-out state of a Project that both members of its Skill Pair describe, including validated unreleased behavior.
_Avoid_: Supported release, published version

**Consumer Interface**:
A supported surface through which Consumers use a Project, such as a command-line interface, programming API, or hosted service.
_Avoid_: Usage Skill, project

**Contributor**:
An agent or person changing the Project's implementation or development infrastructure.
_Avoid_: Developer, maintainer

**Consumer**:
An agent or person using the Project through its supported interfaces without changing its implementation.
_Avoid_: User, operator

**Evidence Pack**:
The immutable, append-only record of one work item or investigation that motivates knowledge; it never projects into a Skill Pair. Research discovery and execution outcome are two kinds of the same concept.
_Avoid_: Research memo, raw trace, wiki page

**Distillation**:
The gated post-work procedure in which a Maintainer analyzes Evidence Packs into root-cause knowledge expressed as draft atomic notes, updates, or deprecations.
_Avoid_: Wiki maintenance, note extraction, summarization

**Maintainer**:
The agent executing Distillation over Evidence Packs; a role within contribution, not a separate audience.
_Avoid_: Contributor (the audience), Wiki Maintainer agent

**Pattern**:
The role of an atomic note distilled from evidence: what happens, why (root cause), and the fix, stated so relevance is judgeable from its index entry alone.
_Avoid_: Wiki pattern page, separate artifact from an atomic note

**Impact Ledger**:
The machine-appended, append-only record of knowledge-state transitions — publications and accept/reject decisions — kept separate from session narrative.
_Avoid_: Session log, review ledger, skill-impact tracker
