# Shared Domain Skill Library implementation record

## Scope

Implemented approved Stories 025–030 against the approved Shared Domain Skill Library PRD and Architecture: authoritative vault schema, generated catalog and indexes, deterministic resolver/loader, cross-project governance, atomic migration, one-router installation, and dogfood release.

## Behavioral evidence

- `python3 -m unittest tests.test_shared_library` initially failed for missing resolver, migration, install, and governance behavior, then passed after implementation and review fixes.
- The final full suite passed 283 tests.
- `generate-library` and `validate-library` produced and validated `memnotes/Skills/.kosmic/{catalog,manifest}.json` plus the ABINIT, TB2J, and Kosmic domain indexes.
- Explicit `--route abinit --role usage` produced a domain-only plan with `ordered_loads: [domain:abinit]`.
- Query `debug tb2j exchange parameters from abinit` selected `tb2j/development/debug-abinit-exchange` and loaded its declared ABINIT Usage dependencies first; no unrelated topic was loaded.
- A 100-byte request for that route failed closed with `BUDGET_EXCEEDED: bytes 3733/100`, emitting no Recipe Packet.
- The deterministic ambiguity fixture failed with `AMBIGUOUS` and emitted no Recipe Packet.
- The migrated Kosmic `cli-projection-commands` old/new bodies are byte-equal and retain identical source hash `9e5bcdc66e14fe39c028a3066d7d39ae4bd0e8ab6cafc58c10a312d6dd20813f`.
- The complete explicit Kosmic migration map was replayed idempotently; all migrated files retained source hashes and Evidence references.
- OpenCode, Claude Code, Codex, and OMP installations each byte- and identity-verified exactly one `memnotes-skills` router. Runtime inventory discovery remains unverified until each adapter starts a fresh session.

## Code provenance

- Review base: `0daf64e5711c14407b551f199832d8b16a2a1db1`
- Final pre-publication worktree tree: recorded in `MANIFEST.md`.
- Proposal fingerprint after Evidence-path coverage: `30d2d8021f4eee71d4f896545ee89f0ba171206b3ffad857dc90b941c931bd1a`.
