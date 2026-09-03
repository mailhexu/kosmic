---
status: done
created: 2026-09-02
updated: 2026-09-02
linked_prd: ../prd.md
linked_architecture: ../architecture.md
open_questions: []
---

# Research: WikiSkill-style experience compilation for Kosmic

## Question

Which mechanisms from WikiSkill (arXiv 2608.27454v1, Tang et al., Google Research, 27 Aug 2026) should Kosmic adopt to make its knowledge system compound from experience instead of relying on discretionary note-taking?

## Context

PRD "Route-Graph Project Skill Pair" (approved) and Architecture (draft, in review) cover the *projection shape*. WikiSkill addresses the orthogonal *knowledge acquisition loop*: how execution experience becomes persistent knowledge that later changes build on.

## Sources

- WikiSkill paper: three-layer workspace (raw/ immutable traces, wiki/ persistent patterns + logs.md + skill-impact.md, skills/ with SKILL.md + PURPOSE.md); four-role loop (Inference Agent, Wiki Maintainer, Skill Proposer, Gating and Rollback); skills roll back on validation regression, wiki never rolls back.
- Key results: persistent wiki access for the proposer +15.0 avg points; wiki access for the inference agent during training −2.8 (knowledge leak makes trajectories less informative); 39-58% of accepted skill updates occur early, refinement continues late; general procedures transfer across models while model-specific workarounds can negatively transfer; unbounded wiki growth (no pruning) is a stated limitation.

## Availability (verified 2026-09-02)

- **No official code release** from the authors (Google Research); paper + appendix prompts only.
- **Third-party MIT implementation**: `github.com/ashutoshsinghpr7/wikiskill` (PyPI `wikiskill`, Python ≥3.10, 73★). Verified real: Algorithm 1 loop on live agent backends (Hermes reference; Claude Code, Codex, GitHub Copilot CLI adapters with isolated per-workspace profiles), raw/wiki/skills layer layout, Wiki Maintainer + Skill Proposer as installable SKILL.md using the paper's verbatim Appendix E prompts, strict `R_val > R_best` gating with git rollback, skill-impact.md with rejected proposals embedded, cross-workspace `transfer`.
- **Honest caveat from its own docs**: no live *accepted* proposal yet on the bundled bench (all gates rejected or `no_action`); requires auto-gradable task packs (`exact`/`contains`/`json_field`/`code_stdout` graders). It is benchmark machinery, not a project-knowledge system.
- **Format compatibility**: its wiki layer is plain markdown (patterns/*.md, index.md, log.md, skill-impact.md) — structurally close to, but not conformant with, Kosmic's OKF v0.2 bundle (no line-1 frontmatter contract, status lifecycle, audience scope, provenance hashes, or atomic publication).

## Findings

Kosmic already implements half of WikiSkill, with different (deterministic, human-gated) mechanisms:

| WikiSkill mechanism | Kosmic counterpart | Verdict |
|---|---|---|
| Skills Layer with PURPOSE.md mapping skill → motivating patterns | Projection manifests: source path + SHA-256 per reference | Kosmic stronger on content provenance; weaker on *motivation* provenance |
| Gating and Rollback: validation-score gate; skills roll back, wiki persists | Approval gates + code review (Task 7), atomic publication, drift validation; notes never rolled back | Equivalent in spirit, human-gated instead of score-gated |
| Wiki access restricted during task execution | Routers load only needed projected references, not the vault | Already present; paper's −2.8 ablation corroborates progressive disclosure |
| Wiki pruning | `stale_after`, `usage_stale`, `status: deprecated`, Task 4 review | Kosmic ahead; WikiSkill lists pruning as an open limitation |
| Raw Layer: immutable execution traces feeding consolidation | **Gap.** `log/` holds curated session summaries, not raw evidence | Missing |
| Wiki Maintainer: dedicated root-cause consolidation pass over traces | **Partial gap.** Task 2 triggers exist but consolidation is discretionary; Task 4 extracts from logs weakly | Under-specified |
| skill-impact.md: programmatic append-only ledger of proposals (diff, score, accept/reject) so rejected changes are never re-proposed | **Gap.** Manifests are point-in-time; no chronological record of what was published/rejected and why | Missing |
| Evidence → pattern linkage (traces motivate wiki updates) | **Gap.** Notes have `validation_procedure` but no links to motivating evidence | Missing |

What NOT to import: LLM-driven autonomous skill-proposer loops and validation-score gating. Kosmic's contract is deterministic generation with human approval gates; the paper's loop optimizes benchmark scores, not trustworthy project knowledge.

## Options Considered (revised after availability check)

### Posture A: Use `ashutoshsinghpr7/wikiskill` standalone, alongside Kosmic

Run the pip package on auto-gradable task packs (its graders: exact/contains/json_field/code_stdout) where such packs exist; manually distill accepted patterns into Kosmic notes.

**Pros**: zero integration work; real loop machinery today (isolated agent profiles, transcript normalization, Appendix E prompts, gating harness).

**Cons**: does not touch Kosmic's gaps — capture/distillation for real dev work stays discretionary; its wiki is not OKF-conformant; its own logs show zero accepted proposals so far (weak evidence the full loop pays off outside paper-scale benchmarks); two knowledge bases drift apart.

### Posture B: Adapt the repo as Kosmic's experience-compilation engine (write into the substrate)

Borrow its commodity pieces — backend adapters (Codex/Claude transcript capture), trace normalization, verbatim Appendix E Maintainer prompt (MIT) — and make Kosmic's structures the targets: traces → `evidence/`, maintainer output → draft notes with `evidence:` links (never auto-stable), gate outcomes + publications → `impact.md` ledger. Its benchmark scoring/evolution loop is dropped: in Kosmic the "proposer" is the normal story/quick-task flow and the gate is Task 7 review plus the test suite (TDD), which is the grader that actually exists for project knowledge.

**Pros**: closes all three gaps; activation becomes mechanical (post-story/post-debug distillation driven by captured evidence) instead of discretionary — directly addresses the "skills not often written/updated" complaint; single substrate, OKF invariants intact; human gates preserved.

**Cons**: integration surface (transcript capture varies per agent backend); new vault convention; medium-size follow-up feature.

### Posture C: Concepts only, no dependency

Implement evidence layer + distillation duty + ledger purely in Kosmic task docs and CLI, borrowing the paper's ideas without the repo.

**Pros**: no external dependency; smallest surface.

**Cons**: re-implements transcript capture eventually anyway; forfeits MIT-licensed prompts/adapters that are already written and tested.

## Recommendation (revised)

**Posture B, staged**: 

1. **Stage 1 (concepts, no dependency)** — the three structural pieces land in Kosmic: `evidence/` convention, Wiki-Maintainer distillation step in Task 2/4 (root-cause pattern extraction, `evidence:` frontmatter links, additive and optional), `impact.md` programmatic ledger appended by `generate`. Human review promotes draft notes to stable; nothing auto-publishes.
2. **Stage 2 (optional adoption)** — where transcript capture is wanted, vendor or wrap the repo's MIT backend adapters and Appendix E Maintainer prompt with attribution; evaluation only until an accepted-proposal track record exists.

Scope relative to route-graph work: separate follow-up PRD ("Experience Compilation") is still the lean — the pieces are orthogonal to projection shape; combining only if the user wants one release.

## Open Questions

- [ ] Should `evidence:` links participate in route-graph `requires`-style validation, or stay informational? (Lean: resolvable-path check only.)
- [ ] Ledger granularity: per `generate` publication or per accepted note change? (Lean: per publication; manifests carry per-note detail.)

## Architecture Impact

- Current draft architecture: no change required; `evidence:` is additive metadata of the same family as `domains`/`intents`/`requires` (ADR-0002 pattern) if combined later.
- If combined now: extend ADR-0002 vocabulary validation with `evidence` resolvable-path check and add ledger append to ADR-0006 generation contract.

## Notes to Capture

- The mapping table above is durable design knowledge; promote to an atomic note once the direction is user-confirmed.
