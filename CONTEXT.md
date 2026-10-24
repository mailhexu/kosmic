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

**Project Idea**:
A tentative proposal, possibility, or open question captured for later consideration within a Project; neither verified Project Knowledge nor an approved Work Record.
_Avoid_: Approved task, established knowledge, skill nomination

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

**Domain Topic**:
An authoritative Shared Library document classified independently by audience and semantic role.
_Avoid_: Skill Topic, executable reference

**Procedure**:
Executable guidance with a recognizable trigger, bounded outcome, ordered actions, decisions, verification, and failure handling.
_Avoid_: Any stable note, topic

**Guideline**:
Normative constraints that govern procedures and review without becoming an executable task.
_Avoid_: Procedure, recommendation

**Knowledge**:
Informational facts, models, conventions, and implementation explanation used for understanding.
_Avoid_: Procedure, evidence

**Evidence**:
A dated historical observation that substantiates or challenges claims but never silently becomes current guidance.
_Avoid_: Procedure, current truth

**Work Record**:
The single governing record of one work item or investigation: embedded per-criterion observations, the independent two-axis review, and its completion receipt. There is no separate evidence layer.
_Avoid_: Evidence pack, sidecar, manifest dossier

**Completion Receipt**:
The machine receipt a successful `work finish` publishes, bound to the completed record's exact bytes; it is the completion marker, so unreceipted `done` is pending.
_Avoid_: Approval checkbox, acceptance sidecar

**Maintainer**:
A contributing agent role within a Project audience, not a separate audience.
_Avoid_: Contributor (the audience), Wiki Maintainer agent

**Pattern (note)**:
An atomic note capturing what happens, why (root cause), and the fix, stated so relevance is judgeable from its index entry alone. A note gains nothing by being a separate artifact from its concept.
_Avoid_: Wiki pattern page, evidence-derived duplicate

**Deterministic Routine**:
A tested Python function that implements stable, reusable procedure mechanics and is discovered from a static declaration without importing its source module.
_Avoid_: Skill prose, plugin, generated code

**Routine Inventory**:
The generated, hash-pinned catalog of deterministic routines, ownership, callers, procedure edges, and behavioral-test references used for reuse-first selection.
_Avoid_: Handwritten registry, runtime plugin list

**RoutineRecord**:
A normalized entry in `.kosmic/routines.json` containing a routine’s identity, source module and symbol, owning Maintainer, constraints, callers, procedure edges, test references, and provenance hashes.
_Avoid_: runtime plugin object, handwritten registry row

**Procedure Compilation**:
The governed Task P transition that moves repeated deterministic mechanics from verified procedure notes into a canonical routine while retaining judgment, risk, and approval in reviewed skill prose.
_Avoid_: Automatic code generation, compiling Markdown

**Subproject**:
A named feature scope within one Project. A Subproject owns its specifications and shares the Project's knowledge.
_Avoid_: Separate Project, private knowledge bundle

**Work Record**:
The specification or Quick Task that states the purpose, scope, and acceptance criteria of an action. Implementation requires an approved Story or Quick Task.
_Avoid_: Session summary, chat task list

**Work Context**:
The explicit association of an agent's work with a Project, optional Subproject, Work Record, working directory, and allowed change scope.
_Avoid_: Project-wide active task, implicit current feature
