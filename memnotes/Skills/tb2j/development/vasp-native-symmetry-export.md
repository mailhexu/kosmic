---
type: Domain Topic
id: tb2j/development/vasp-native-symmetry-export
domain: tb2j
audience: development
artifact_role: guideline
status: draft
summary: Implement a VASP symmetry-reduced k-point projector export for TB2J with consumer-side symmetry expansion.
triggers: [VASP IBZ projector export, tb2j_export.F, KPOINTS_FULL action matrix, native PAW export]
aliases: [VASP symmetry export]
outcome: 
requires_procedures: []
governed_by: []
uses_knowledge: []
supported_by: []
supersedes: []
evidence: []
source_project: tb2j
source_sha256: e046acd7de556594acb4cdefd4450f2998a501e81a3cfe9576bedea8742de5e0
---

# VASP Native Symmetry Export

Build a VASP-to-TB2J (or similar projector-based exchange) pipeline that exports irreducible Brillouin zone (IBZ) projector coefficients and expands them with symmetry on the consumer side.

## Implementation steps

1. Force KPOINTS_FULL allocation at export time:
```fortran
IF (.NOT. ASSOCIATED(KPOINTS_FULL) .AND. SYMM%ISYM >= 0) THEN
   LFULL_KPOINTS = .TRUE.
   CALL SETUP_FULL_KPOINTS(KPOINTS, LATT_CUR, T_INFO%NIOND, &
        SYMM%ROTMAP, SYMM%MAGROT, SYMM%ISYM, &
        .NOT.WDES%LNONCOLLINEAR, IO%IU6, IO%IU0)
ENDIF
```
2. Build action matrices from SL plus ROTMAP, with no Bloch phase correction:
   - Call `SETUP_SYM_LL(MMAX, LDIM, KPOINTS_FULL%ISYMOP(:,:,NK_BZ), SL, A, B)`.
   - For each atom NI, read the source atom `NIP = KPOINTS_FULL%ROTMAP(NI, NK_BZ)`.
   - Fill a block-diagonal action from SL for each l-channel.
   - Do NOT apply `exp(-2πi(k_target·τ_NI − k_parent·τ_NIP))`; it breaks results.
3. Use `nproj_physical = sum(ion_nproj)` for action dimensions, not NPROD (the stream stride carries padding).
4. Cast CDIJ to COMPLEX*16 before writing; OVERLAP may be REAL*8.
5. Validate the mesh in Python with tolerance-based grouping (tol = 1e-6) instead of exact unique for the Cartesian-product check; this handles 1/7 meshes.

## Modules needed in tb2j_export.F

- `USE full_kpoints` — KPOINTS_FULL pointer.
- `USE mkpoints_struct_def` — skpoints_full type, rotation_handle.
- `USE asa` — SETUP_SYM_LL.

## Binary format (v6)

After type metadata and before spectral arrays, write in this order:
`kpoint_storage_mode` (int, = 1); `nkpt_bz` (int); `vkpt_bz` (3×nkpt_bz doubles, Fortran order); `parent_ibz` (nkpt_bz ints, zero-based); `source_spin` (nspin×nkpt_bz ints); `conjugate` (nspin×nkpt_bz ints, from LINV); `projector_action` (nproj_phys²×nspin×nkpt_bz complex128); `symmetry_operation` (nkpt_bz ints); `spinflip` (nkpt_bz ints).
