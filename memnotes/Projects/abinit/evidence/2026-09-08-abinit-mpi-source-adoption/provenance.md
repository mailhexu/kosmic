# Historical MPI CG-Reduction Provenance

## External Source

- Source Project: external full ABINIT Project (outside this vault)
- Source note: `notes/abinit_mpi_cg_loop_template.md`
- Source SHA-256: `4adcd872ff345bb9b4793dd4bda2f1cf395c7bdda385566542bb177f03345fba`
- Source validation date: 2026-03-04
- Source validation: `tests/NiO_NC_DFTU` over `paral_kgb=0` with `npkpt=2,4` and `paral_kgb=1` with `npband=2`, `npfft=2`, and the documented k-point/band/FFT combinations through eight ranks; reported agreement below `5e-6 Ha`.

## Extracted Invariants

1. `npwarr(ikpt)` is a local extent in `paral_kgb=1`.
2. `nband_k` remains global, including the `icg` increment.
3. Reduce G-vector partial sums on `comm_bandspinorfft` before applying logical band ownership.
4. Reduce the result over `comm_kpt`, then `comm_band` when band groups are split.
5. Advance `icg` by `npw_k * my_nspinor * nband_k`.

## Limits

This pack preserves historical provenance only. The source run predates this Project adoption and has not been re-executed against a current ABINIT tree. It must not support a Task P procedure proposal. A future execution pack must reproduce a relevant topology matrix and capture at least one meaningful failure/recovery path before Task 9 distills a procedure candidate.
