# Task M: Math Note

Create or correct one executable SymPy derivation and its paired Math Derivation note. The executable file is the authority; prose records assumptions, units, interpretation, and correction history. Write the human-owned prose in the Simplified Technical English subset defined by [Note writing style](note-writing-style.md); the machine-owned region is exempt.

Persistent derivation/script/note changes require a compatible approved Story or standalone Quick Task and declared shared mathdocs/note scope. Read-only math checks remain record-free. Pass `--work-record REF` to `check-math --update`; script success never supplies approval or acceptance sufficiency by itself.

## When to Use

- A formula or symbolic result will be reused by notes or implementation.
- A mathematical discrepancy appears in a note, derivation, or source file.
- A work item declares `derivations` and `math_implementation_files`.

Do not use this task for inline notation, arithmetic, plots, or numerical benchmarks.

## Invariants

1. `{PROJECT}/mathdocs/{slug}.py` and `{slug}.md` are a same-slug pair.
2. `mathdocs/index.md` has one row for every non-deprecated pair.
3. The script supports `--kosmic-json` and writes only the version-1 JSON protocol to stdout. Diagnostics use stderr.
4. The paired note's generated region is machine-owned. Assumptions, units, explanations, and `## Corrections` remain human-owned.
5. A stable note must carry the current source hash and verification environment.
6. If an equation is wrong, correct the derivation first. Never patch prose or implementation around a broken derivation.

## Workflow

### 1. Search

Read `mathdocs/index.md`, then search `notes/index.md` and the relevant specs. Update an existing derivation rather than creating a second authority for the same result.

### 2. Create the pair

Copy:

- `references/templates/template-math-derivation.py` to `mathdocs/{slug}.py`
- `references/templates/template-math-derivation.md` to `mathdocs/{slug}.md`

Use a lowercase hyphenated slug. Define symbols, domains, assumptions, and units explicitly. Return named results in lexical order. Add the pair to `mathdocs/index.md` as `draft`.

### 3. Execute and review

Run:

```bash
python3 ${KOSMIC_SKILL_DIR}/scripts/kosmic_project_skills.py check-math \
  --project "${VAULT}/Projects/${TARGET}" --slug "${SLUG}" --update \
  --source-root "${SOURCE_ROOT}"
```

`--update` executes trusted Project code without an OS sandbox. Inspect the derivation, assumptions, exact `srepr`, rendered LaTeX, and generated note region. Confirm physical dimensions and conventions manually; successful execution does not prove the model is correct.

Append corrections under `## Corrections` with date, error, and resolution. Never edit the generated region manually.

### 4. Link dependent knowledge

A stable regular note declares:

```yaml
derivations: [mathdocs/{slug}.py]
```

Place one marker immediately before each relied-upon display equation:

```markdown
<!-- MathDoc: {project_id}/{slug}#{result-name} -->
$$
<exact verified LaTeX>
$$
```

Use `<!-- MathDoc-Exposition: {project_id}/{slug} -->` for explanatory display equations. Exposition is not an authoritative result.

### 5. Link implementation

The approved work item declares:

```yaml
derivations: [{slug}]
math_implementation_files: [relative/source/path.py]
```

Each listed source file carries an adjacent comment or docstring containing `MathDoc: {project_id}/{slug}` or `MathDoc: {project_id}/{slug}#{result-name}`.

### 6. Verify and promote

Run `validate`, default read-only `check-math`, and `check-completion --source-root`. Review the assumptions and source-marker adjacency through Task 7. Only then promote the paired note and index row from `draft` to `stable`, rerun all three commands, and update the Project log.

## Debugging Rule

Equation-level defect → inspect and run the derivation first → correct the paired note through `check-math --update` → update dependent regular notes → fix implementation → rerun completion. An unresolved discrepancy blocks code changes; do not choose a convenient side.