---
type: Domain Topic
id: kosmic/development/atomic-skill-publication
domain: kosmic
audience: development
artifact_role: procedure
status: stable
summary: Publish a staged artifact tree atomically with rollback
triggers: [publish staged tree, atomic directory publication, rollback generated artifacts]
outcome: Destination contains the complete validated staged tree or remains byte-for-byte unchanged.
aliases: []
requires_procedures: []
governed_by: []
uses_knowledge: []
supported_by: []
supersedes: []
observed_on:
evidence: []
uses_routines: [kosmic/atomic-publish-tree]
source_project: native
source_sha256: empty
---
# Atomic Skill Publication

## When to use

Use when replacing a generated tree or a bounded set of generated paths after the complete staged output has validated.

## Preconditions

The staged tree is complete, on the destination filesystem, and validated. The caller owns the destination or explicit managed paths.

## Procedure

1. Prepare and validate the full staged output without mutating the destination.
2. Call `publish_tree(staged, destination)` for a whole-tree swap, or pass validated relative `managed_paths` for a bounded update.
3. Verify the published bytes through the consumer-facing validator.

## Decisions and branches

Use whole-tree mode only when Kosmic owns the complete destination. Use managed mode where user-maintained siblings must survive. Approval and validation remain caller policy; the routine owns only publication mechanics.

## Verification

Run the owning generator's validator and compare installed bytes where an adapter is involved. An injected mutation-boundary failure must leave the prior destination unchanged.

## Failure handling

Treat any publication exception as a failed transaction. Confirm rollback restored prior bytes; do not retry from a partially consumed staging tree.

## References

Routine inventory ID: `kosmic/atomic-publish-tree`. The owning Task P proposal and evidence pack record behavioral equivalence and approvals.
