# Skill Proposal Loop session record

## Scope

Implemented approved Stories 018-024: Task P procedure and template, flat proposal schema and validator, completion gate, rejection memory, behavioral-evidence contract, deterministic installation verification, activation diagnostics, and real Kosmic dogfood.

## Dogfood

A dedicated fresh-context proposer received only the SHA-pinned curated manifest at `specs/skill-proposals/inputs/kosmic-proposer-dogfood.md`. It emitted `specs/skill-proposals/2026-09-06-kosmic-proposer-dogfood.md` with `result: no_action`: the existing generated Development topic already exposes the observed Projection CLI Pattern, so a separate procedural skill would duplicate it. Human approval accepted that result. The decision and fingerprint were appended to `impact.md`.

## Verification

- `python3 -m unittest tests.test_project_skills_cli`: 260 tests passed before final documentation and release updates.
- `validate-proposal` accepted the completed dogfood artifact and reproduced fingerprint `89bcc7de7c82648874b87a27942b90135bf8fa4a6546bbcc9dbba454c01f0b73`.
- Code provenance before evidence publication: git head `ce222de21653f23539c02e80cf7646b1562874a2`; worktree tree `b54abe9fd9d55287f7a445d0d8788ff68e783422`.
- Generated the canonical Skill Pair with generator version 4 and installed it through the OpenCode, Claude Code, and Codex named adapters.
- `check-installation` byte- and identity-verified both packages at `/home/hexu/.config/opencode/skill`, `/home/hexu/.claude/skills`, and `/home/hexu/.agents/skills`.

## Activation boundary

Named-adapter installation reports on-disk byte and Project-identity verification. Runtime inventory inspection remains required after adapter reload; absence of that observation is recorded as unverified, never as successful activation.
