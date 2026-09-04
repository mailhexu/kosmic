# Math Derivation Layer implementation record

## Scope

Implemented approved PRD `prd-math-derivation-layer.md`, Architecture `architecture-math-derivation-layer.md`, Epics 6-9, and Stories 010-017.

## Delivered behavior

- Vault-only `mathdocs/` registry with same-slug executable SymPy scripts and derivation notes.
- Stable metadata and SHA-256 currency validation.
- Versioned JSON `check-math` protocol, lexical execution, bounded timeout, controlled locale/hash seed, per-file PASS/FAIL, and summary.
- Copy-on-write `check-math --update` publication of paired metadata and generated result regions.
- Stable regular-note result/exposition markers with exact result comparison and code-fence exclusion.
- Work-item completion linkage to finite, contained source files carrying `MathDoc:` identifiers.
- Task M workflow, templates, initialization/migration hooks, search/review/story integration, and v4.0.0 documentation.

## Dogfood

`mathdocs/atomic-publication-state.py` uses SymPy polynomial reduction modulo the binary constraint `s²-s` to prove mutually exclusive old/new visibility and exactly one visible canonical tree. Its stable paired note records four named results, assumptions, units, environment, source hash, and correction history. `notes/atomic-skill-publication.md` consumes exact result markers plus an exposition marker. `scripts/kosmic_project_skills.py::publish_directory` carries the adjacent source identifier.

## Verification

- `python3 -m unittest tests.test_project_skills_cli`: 205 tests passed.
- Real derivation: `uv run --with sympy python skills/scripts/kosmic_project_skills.py check-math --project memnotes/Projects/kosmic --slug atomic-publication-state --source-root .`: PASS under Python 3.12.10 / SymPy 1.14.0.
- `generate`, `validate`, and `review` passed on the Kosmic Project before final evidence linkage; final gates were rerun after publication.
- Stories 010-017 passed `check-completion --source-root .`; Stories 013 and 017 exercised derivation/source linkage.

## Code state

Code state: /home/hexu/projects/myagentskills/kosmic (local) — git 6ee55e565525567e97667f79c61b88a4b639779e, tree 9fd68956e35f2dff747b9545e2e9665056f308b1, jj qlukzopluzoo.
