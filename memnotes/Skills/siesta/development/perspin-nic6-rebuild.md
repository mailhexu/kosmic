---
type: Domain Topic
id: siesta/development/perspin-nic6-rebuild
domain: siesta
audience: development
artifact_role: guideline
status: draft
summary: Rebuild the SIESTA perspin_DFTB branch tip on nic6 as dev@sha-gcc, verify, deprecate the previous install, and update swmgr records.
triggers: [perspin rebuild, nic6 siesta install, deprecate dev module, swmgr siesta record]
source_project: native
source_sha256: empty
aliases: [perspin nic6 update, siesta install cycle]
---

# Update a perspin_DFTB Dev Install on nic6

Trigger: `/home/hexu/projects/siesta_git/siesta_DFTB_dev/siesta_DFTB`
(perspin_DFTB) has new commits. Build the tip on nic6 from the local
tree; deprecate the previous module.
## 0. Source the new tip
- `git log --oneline <prev>..HEAD`; tree must be clean. If dirty, commit
  first or scp changed Src files over the staged tree (stage exports
  HEAD, not the working tree). Verify the stage with md5 against
  `git show <sha>:Src/file`; a mismatch means the label lies.
- The gitlab.com origin is STALE and SSH keys fail; compare with
  `git ls-remote https://gitlab.com/mailhexu/siesta.git perspin_DFTB`
  (HTTPS token). Never downgrade. Short sha: 9 chars.
## 1. Build (via SLURM; control machine = local box)
```bash
STAGE_ROOT=/tmp/stage_<sha> sh stage_submodules.sh
rsync -a --delete /tmp/stage_<sha>/ nic6:~/src/siesta_perspin@<sha>/
ssh nic6 'bash ~/bin/nic6-siesta-configure.sh siesta_perspin@<sha> ~/src/siesta_perspin@<sha> ~/sw/siesta/dev@<sha>-gcc'
ssh nic6 'cd /scratch/hexu/build/siesta_perspin@<sha> && sbatch ~/bin/nic6-siesta-build.sh siesta_perspin@<sha> ~/sw/siesta/dev@<sha>-gcc siesta_DFTB'
```
Build job (about 2.5 minutes) = build + install + serial H2 smoke.
Invariant: `FreeEng = -30.542591 eV`, `SMOKE_DONE`, 0 `error:` lines.
## 2. Modulefile and deprecation
Copy the pattern from `~/privatemodules/siesta/dev@<prev>-gcc`: prefix
`~/sw/siesta/dev@<sha>-gcc`, `conflict siesta`, loads GCC/14.3.0,
OpenMPI/5.0.8, FlexiBLAS/3.4.5, ScaLAPACK/2.2.2, libxc/7.0.0,
netCDF-Fortran/4.6.2, PATH + SIESTA_ROOT. Deprecate: move the old
modulefile to `<prefix>/modulefile.deprecated`; prepend a DEPRECATED
line to its README. Never delete prefixes (running jobs) or touch the
user's separate variant modules (e.g. dev@<sha>-fdm-gcc).
## 3. Feature verification (pick by the diff)
Fixtures under `/scratch/hexu/siesta-tests/`: `op-mpi-account/`
(1-vs-4-rank FreeEng to 1e-6 eV), `fixdir-check/` (spin pinned to 0.05
deg), `op-sign-check/` (trace/func agreement). ALWAYS copy
`Sm.1.psml N.2.psml Sm.1.ion N.2.ion` into a new fixture dir; siesta
aborts without them. Runner: sbatch, `srun --mpi=pmix_v5 -n1 siesta <
siesta.fdf`. 60-step unconstrained runs are NOT converged.
## 4. swmgr vault records
Vault: `/home/hexu/projects/software_installation_manager`. Order:
lockfile `locks/siesta-dev@<sha>-gcc-nic6.lock` (rebuild commands, pins,
verification numbers) -> install record -> TOC row + old row flip ->
`machines/nic6.md` + `software/siesta.md` -> published page (new + old
deprecation header + `_index.md`) -> `hugo` -> commit as
`hexu <mailhexu@gmail.com>` -> memnotes log `.../siesta/log/
siesta-<date>.md` -> README in the new prefix (both shas + date).
## Known pitfalls
