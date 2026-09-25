---
type: Domain Topic
id: siesta/development/dftb-soc-dealloc-fix
domain: siesta
audience: development
artifact_role: guideline
status: draft
summary: Fix the SIGSEGV in SIESTA DFTB-branch SOC calculations caused by unconditional deallocation of the V_so_only pointer in nlefsm.f.
triggers: [siesta segv soc, exit 139, nlefsm crash, V_so_only]
source_project: native
source_sha256: empty
aliases: [soc dealloc fix]
---

# SIESTA DFTB SOC SIGSEGV Fix
## Symptom

The `siesta_DFTB` binary exits with SIGSEGV (code 139) in any
spin-orbit-coupling calculation, after k-grid setup.
## Root cause

In `Src/nlefsm.f`, subroutine `nlefsm_SO_off`:

- `V_so_only` is a Fortran pointer. The code allocates it only when
  `savehs_so = .true.`.
- The cleanup `deallocate(V_so_only)` runs unconditionally.
- When `savehs_so = .false.`, the code deallocates an uninitialized
  pointer. Heap corruption follows; `libc free()` raises SIGSEGV.
## Fix

1. Add `nullify(V_so_only)` before the conditional allocate.
2. Guard the cleanup: `if (savehs_so) deallocate(V_so_only)`.
## Rebuild

```bash
cd _build/build_fresh
cmake --build . --target SIESTA.siesta -j$(nproc)
```
## Verify

Run any SOC calculation (`Spin = spin-orbit`). The binary exits 0
instead of 139.
