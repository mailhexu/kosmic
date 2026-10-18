---
type: Domain Topic
id: kosmic/development/atomic-skill-publication
domain: kosmic
audience: development
status: stable
summary: Atomic Skill Publication
triggers: [Atomic Skill Publication]
aliases: []
evidence: [evidence/2026-09-05-math-derivation-layer-impl/session-record.md]
source_project: kosmic
source_sha256: 7d4391e80866b489a28e77cc4748b60e2ab7228f673fc30b817c42f78762e165
artifact_role: knowledge
requires_procedures: []
governed_by: []
uses_knowledge: []
supported_by: []
supersedes: []
source: notes/atomic-skill-publication.md
---

# Atomic Skill Publication

Kosmic builds a Project Skill Pair in temporary storage, validates it there, and only then replaces the canonical pair. If replacement fails, the previous valid pair is restored.

## State invariant

Let the binary outcome indicator `s` be one on commit and zero on rollback. The visible-tree indicators are:

<!-- MathDoc: kosmic/atomic-publication-state#commit_indicator -->
$$
s
$$

<!-- MathDoc: kosmic/atomic-publication-state#rollback_indicator -->
$$
1 - s
$$

The binary constraint underlying the transition is explanatory rather than a separately asserted output:

<!-- MathDoc-Exposition: kosmic/atomic-publication-state -->
$$
s^{2} = s
$$

Reduction modulo that constraint proves that the old and new trees are never simultaneously visible:

<!-- MathDoc: kosmic/atomic-publication-state#mixed_visibility -->
$$
0
$$

and that exactly one canonical tree remains visible:

<!-- MathDoc: kosmic/atomic-publication-state#visible_count -->
$$
1
$$

These results prove the publication state transition, not the semantic correctness of generated skill content. Content validity is established before replacement by bundle, provenance, and source-link checks.

## Implementation consequence

All generated files must be written and validated under the temporary root. Canonical paths are mutation targets only inside the replacement transaction; no caller may update a projected file in place.

## Related concepts

- [CLI extension conventions](cli-extension-conventions.md)
- [CLI projection commands](../usage/cli-projection-commands.md)
