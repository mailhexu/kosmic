---
artifact_role: knowledge
audience: both
type: note
status: stable
created: 2026-10-03
last_validated: 2026-10-03
stale_after: 2027-10-03
tags: [abinit, hgg, dftu, paw, conventions]
project: abinit
related_notes: [hgg-reconstruction-conventions]
---

# Where the DFT+U (Hubbard) term lives in the HGG factored export

Learned implementing story 605. The headline: **no dedicated Hubbard factors are needed**
— the +U operator already rides inside the ordinary KB coupling factor.

## Data flow

$$
\texttt{dijU} \;\longrightarrow\; \texttt{paw\_ij\%dij} \;\longrightarrow\;
\texttt{ham\%ekb} \;\longrightarrow\; \texttt{nonlop} \;\longrightarrow\; \texttt{getghc}
$$

| Step | Location |
|------|----------|
| `dijU` computed by `pawdiju_euijkl` | `src/65_paw/m_paw_denpot.F90:1006-1008` |
| merged into `paw_ij%dij` | `src/65_paw/m_paw_denpot.F90:2490-2492` |
| `gs_ham%init` packs `dij` into `ham%ekb` via `pawdij2ekb` | `src/66_nonlocal/m_hamiltonian.F90:1012-1014`, `:2134` |
| applied by `nonlop` | `src/66_wfs/m_getghc.F90:1092` |

The merge happens **before** `gs_ham%init`, so by the time the HGG writer reads `gs_hamk%ekb`
the Hubbard contribution is already inside it and is exported as
`hgg_nonlocal_coupling_matrix`. The story-605 guard was purely over-restrictive.

There is **no +U hook in `getghc`** — grep for `usepawu|dijU|nc_dftu` in `src/66_wfs` and
`src/66_nonlocal` returns nothing.

## Scope correction: NC DFT+U does not exist in ABINIT 10.9.3

Verified absent from this tree: the `usedftu_nc` input variable, `m_nc_dftu_hamiltonian.F90`,
`apply_dftu_hamiltonian_nc`, and the `nc_dftu` symbol. The only Hubbard term is PAW+U
(`usepawu`). Stories written against the NC+U (pymatgen/FLL) feature must be re-scoped
before implementation.

## Proving a term is present, not just self-consistent

The in-run certificate compares the reconstructed operator against the *in-memory* one. If a
term were dropped on **both** sides, the residual would still be `0.000E+00` and the test
would pass while the export were wrong. Always pair it with a control that switches the term
off and shows the exported factors actually differ:

```
usepawu 1 vs usepawu 0:  max|d ekb| = 2.457  (|ekb| = 3.295), eigenvalues shift by 2.919 Ha
hgg_sij identical        -> the Hubbard term enters dij/ekb, not the PAW overlap
```

## Guarded variants

`usepawu > 1` selects FLL double counting and `natvshift` formulations, and `usedmft` selects
the DFT+DMFT Hamiltonian. These are separate operators, not covered by the `usepawu 1`
certificate, so they stay guarded.