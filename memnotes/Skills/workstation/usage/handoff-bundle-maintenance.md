---
type: Domain Topic
id: workstation/usage/handoff-bundle-maintenance
domain: workstation
audience: usage
artifact_role: guideline
status: draft
summary: Assemble or refresh an offline handoff bundle of pinned git source archives plus example inputs and outputs, with verified SHA-256 checksums.
triggers: [handoff bundle, git archive, SHA256SUMS, source snapshot, offline handoff]
source_project: native
source_sha256: empty
aliases: [source handoff bundle]
---

# Maintain a source handoff bundle (git-archive based)

Use this topic to assemble or update a self-contained package of repo snapshots plus examples for an external user who must reproduce exact versions offline.

## Layout (created once)

```
BUNDLE/
├── README.md          # install order, per-workflow commands, exclusions
├── VERSIONS.txt       # repo:branch:commit line per pinned source
├── SHA256SUMS
├── source/            # one .tar.gz per repo, via `git archive`
│   └── <repo>.tar.gz  # prefix=<repo>/ so extraction gives src/<repo>
└── examples/<name>/   # inputs + small text outputs only
```

## Create or update a source archive

```bash
git -C <repo> archive --format=tar.gz --prefix=<repo>/ <commit> > BUNDLE/source/<repo>.tar.gz
```

- Pin by commit, never by branch name alone. Update the matching `VERSIONS.txt` line with `git rev-parse --short=7 <commit>`.
- Never archive the working tree: parallel sessions may have uncommitted changes. Run `git archive HEAD` only after your own surgical commit.
- If a parallel session switched the checkout to another branch, verify with `git branch --show-current` and pick commits from `git log <branch>` instead of assuming HEAD ancestry. Do not push branches that would publish in-flight parallel work; leave integration to the owner.

## Refresh checksums (exact recipe)

```bash
cd BUNDLE && {
  find source -type f -print0 | xargs -0 sha256sum
  sha256sum README.md VERSIONS.txt <each example file explicitly>
} > SHA256SUMS && sha256sum -c SHA256SUMS >/dev/null && echo OK
```

- Use `find source -type f`, not `source/*`: subdirectories (for example patch dirs) must be included, and bare `source/*` lists directories, which error.
- List example files explicitly, so accidentally added or removed artifacts surface as checksum failures, not silent drift.

## Keep README commands true

- Every CLI example in README must match the current pinned snapshot's flags. After any CLI rename or unification, grep the README for old command names and rerun `python -m ... --help` against the pinned tree.
- Regenerate reference outputs in `examples/` with the pinned code when possible. When the source data no longer satisfies current loader contracts (for example IBZ-only WFK under a full-BZ fail-closed guard), mark them LEGACY in the README instead of regenerating with different settings.

## Exclusions that keep the bundle small

- Drop wavefunctions, densities, and large binaries (WFK, DEN, CHGCAR, `vasprun.xml`, NetCDF over 1 MB) unless the receiver cannot regenerate them.
- Licensed files (VASP POTCAR) stay out; record a sha256 note instead.
- Freely distributable pseudopotentials (JTH) may be bundled; use relative paths in the input files.
