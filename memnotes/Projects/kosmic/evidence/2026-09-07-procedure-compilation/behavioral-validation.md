# Behavioral Validation

## Baseline

Kosmic had three separate publication implementations and no canonical executable-routine inventory. Reusable mechanics were only prose; procedure packets could not carry tested code references.

## Candidate

The implementation declares `kosmic/atomic-publish-tree` once in `kosmic_routines.py`. Project generation, migration, MathDocs, and Shared Library generation call that implementation. Static AST inspection inventories exact module/symbol/callers without importing source modules. Shared Library generation validates every procedure-to-routine edge in both directions and includes selected routine metadata in hash-pinned plans and packets.

## Observable scenarios

1. An injected failure after destination backup restores the prior complete tree.
2. Dynamic routine declarations fail closed without importing the source module.
3. A procedure declaring an unknown routine fails Shared Library generation.
4. A routine declaring an absent procedure edge fails reciprocal validation.
5. Exact-ID query returns one canonical record with inventory and manifest hashes.
6. A resolved procedure packet contains its routine record and routine source hash.

All six scenarios pass in focused unit tests and the full regression suite.
