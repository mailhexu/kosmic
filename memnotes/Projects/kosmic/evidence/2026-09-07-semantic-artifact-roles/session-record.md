# Semantic Artifact Roles implementation record

## Scope

Implemented approved Stories 031–036: role-neutral Domain Topic schema, strict procedure contracts, typed dependency closure, deterministic intent inference and primary selection, role-aware Recipe Packets, Distillation/Task P classification gates, and explicit ABINIT-first migration followed by Kosmic and TB2J.

## Behavioral evidence

- `python3 -m unittest tests.test_project_skills_cli tests.test_shared_library` passed 288 tests after implementation.
- `generate-library --vault memnotes` and `validate-library --vault memnotes` passed for the role-aware catalog.
- `validate --project memnotes/Projects/kosmic` passed after publishing the classified stable note.
- `validate-proposal` passed for the existing dogfood proposal under the role-aware fingerprint contract.
- Resolver dogfood exercised `do`, `check`, `understand`, and `investigate`: procedures are executable only for `do`; guidelines and knowledge route by intent; absence of eligible evidence fails closed with `NO_MATCH`.
- `install-library` and `check-library-installation` byte- and identity-verified the single `memnotes-skills` router for OpenCode, Claude Code, Codex, and OMP. Runtime discovery remains unverified until each adapter starts a fresh session.

## Migration evidence

`specs/migrations/2026-09-07-semantic-role-classification.json` explicitly assigns all nine pre-cutover Shared Library topics across ABINIT, Kosmic, and TB2J. Every assignment includes target ID, artifact role, and all five typed relationship fields. Generation validated the complete staged graph before atomic replacement. Source hashes, audience, source Project, and existing evidence metadata were preserved.

## Code provenance

- `git_head`: `c52ab6a15b2dab0df9cbd450a76fcdc386612cdb`
- `worktree_tree`: `c7578c82c4b05643482bbb67dc6ddf9fb5b863e3`

The worktree hash was captured after implementation and before this Evidence Pack was added.
