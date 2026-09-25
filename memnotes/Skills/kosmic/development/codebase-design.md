---
type: Domain Topic
id: kosmic/development/codebase-design
domain: kosmic
audience: development
artifact_role: guideline
status: draft
summary: Shared vocabulary and principles for designing deep modules, seams, and testable interfaces.
triggers: [deep module, module interface design, seam placement, shallow module, deletion test]
source_project: native
source_sha256: empty
aliases: [deep modules, codebase design]
---

# Codebase Design

Design deep modules: much behavior behind a small interface, placed at a
clean seam, testable through that interface. Use this vocabulary exactly.
Do not substitute "component", "service", or "boundary".

## Glossary

- **Module**: anything with an interface and an implementation. The term
  is scale-agnostic: a function, class, package, or tier-spanning slice.
- **Interface**: everything a caller must know to use the module
  correctly: the type signature plus invariants, ordering constraints,
  error modes, and performance characteristics.
- **Implementation**: the code inside the module.
- **Depth**: leverage at the interface: behavior exercised per unit of
  interface learned. Deep hides much behavior behind a small interface;
  shallow means the interface nearly matches the implementation.
- **Seam**: the place where the interface lives; a spot where behavior can
  change without editing that spot. Do not say "boundary".
- **Adapter**: a concrete thing that satisfies an interface at a seam; the
  word describes the role, not the contents.
- **Leverage**: what callers gain from depth.
- **Locality**: what maintainers gain; change concentrates in one place.

## Principles

- Depth is a property of the interface, not of the implementation. A deep
  module may contain small swappable parts; they stay out of the
  interface. A module may hold internal seams for its own tests.
- Apply the deletion test. If deleting the module makes complexity vanish,
  it was a pass-through. If complexity reappears in N callers, the module
  earned its place.
- The interface is the test surface. A test that must go past the
  interface signals the wrong module shape.
- One adapter means a hypothetical seam. Two adapters mean a real one. Do
  not introduce a seam until something varies across it.

## Designing for testability

1. Accept dependencies; do not create them inside the module.
2. Return results; do not produce side effects.
3. Keep the surface small: fewer methods and parameters give fewer and
   simpler tests.

When designing an interface, ask: can I remove methods, simplify
parameters, or hide more complexity? Compare radically different designs
on depth, locality, and seam placement.
