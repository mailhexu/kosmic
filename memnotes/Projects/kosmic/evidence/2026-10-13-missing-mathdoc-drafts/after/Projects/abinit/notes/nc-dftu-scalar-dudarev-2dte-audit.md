---
artifact_role: knowledge
audience: both
type: Project Knowledge
status: draft
created: 2026-08-31
last_validated: 2026-08-31
confidence: 0.99
validation_procedure: "Activate /home/hexu/projects/myenvs/mydev and run python notes/nc-dftu-scalar-dudarev-2dte-audit.py; inspect the cited source lines and reproduce the Si Gamma U/U0 controls."
project: abinit
validated_by: SymPy exact identities, independent rational specialization, and current-source audit
tags: [nc-dftu, dfpt, dudarev, finite-q, sympy, ddb]
related_files:
  - notes/nc-dftu-scalar-dudarev-2dte-audit.py
  - abinit_dev_clean/shared/libpaw/src/m_hubbard_orbital.F90
  - abinit_dev_clean/src/66_nc_dftu/m_nc_dftu.F90
  - abinit_dev_clean/src/66_nc_dftu/m_nc_dftu_data.F90
  - abinit_dev_clean/src/72_response/m_dfpt_scfcv.F90
math_provenance: missing
math_provenance_reason: "nc-dftu-scalar-dudarev-2dte-audit.md display math requires one MathDoc marker per equation"
---

# Scalar Dudarev DFT+U 2DTE Audit

## Scope and conclusion

This note records an executable, scalar-collinear Dudarev DFT+U mixed-derivative audit for the NC PAO DFPT phonon path. It establishes two source facts:

1. The generic scalar response-energy contraction does not equal the Fréchet bilinear derivative of the scalar Dudarev functional for general nonsymmetric orbital response matrices.
2. The scalar finite-$q$ DDB completion builds several candidate classes but publishes only the mirrored `mixed - frozen` pair after the final overwrite.

These facts do **not** identify a safe production patch by themselves. The scalar contraction is not sufficient to change the final DDB because its accumulated classes are overwritten later, and the attempted exact mixed-occupation activation made the validated Si Gamma oracle worse. The next admissible implementation step is an independent PAO finite-difference oracle for the mixed occupation and for each final-row class.

The executable witness is [nc-dftu-scalar-dudarev-2dte-audit](nc-dftu-scalar-dudarev-2dte-audit.md). It is a standalone copy of the working-tree audit at `abinit_dev_clean/audit/.tmp_colldebug/derive_scalar_dudarev_2dte.py`.

## Functional and mixed derivative

Let $n$ be the correlated-subspace occupation matrix, and define $U_{\mathrm{eff}}=U-J$. The scalar Dudarev correction is

$$
E_U[n] = \frac{U_{\mathrm{eff}}}{2}\left(\operatorname{Tr}n-\operatorname{Tr}(n^2)\right).
$$

For two displacement parameters $\lambda$ and $\mu$,

$$
n=n_0+\lambda n_\lambda+\mu n_\mu+\lambda\mu n_{\lambda\mu},
$$

exact symbolic differentiation yields

$$
\frac{\partial^2 E_U}{\partial\lambda\,\partial\mu}
=
\frac{U_{\mathrm{eff}}}{2}
\left[
\operatorname{Tr}\left((I-2n_0)n_{\lambda\mu}\right)
-\operatorname{Tr}\left(n_\lambda n_\mu+n_\mu n_\lambda\right)
\right].
$$

For an occupation represented as $n=a a^\dagger$, the mixed product jet has four terms:

$$
n_{\lambda\mu}
=a_{\lambda\mu}a_0^\dagger
+a_0a_{\lambda\mu}^\dagger
+a_\lambda a_\mu^\dagger
+a_\mu a_\lambda^\dagger.
$$

The audit treats the dagger amplitudes as independent formal symbols. This avoids accidentally assuming a real-orbital or transpose-symmetric finite-$q$ response.

## Scalar contraction orientation

`shared/libpaw/src/m_hubbard_orbital.F90:193-201` implements the ground-state scalar potential convention

$$
V_{ij}=U_{\mathrm{eff}}\left(\frac12\delta_{ij}-n_{ji}\right).
$$

`m_hubbard_orbital.F90:442-448` consequently produces

$$
V^\lambda_{ij}=-U_{\mathrm{eff}}n^\lambda_{ji}.
$$

The functional derivative requires the bilinear response term

$$
-U_{\mathrm{eff}}\operatorname{Tr}(n_\lambda n_\mu)
=
\sum_{ij}V^\lambda_{ij}n^\mu_{ij}.
$$

Instead, `hubbard_response_energy` uses `potential_a(im,jm) * occ_b(jm,im)` at `m_hubbard_orbital.F90:521-529`. Exact $2\times2$ SymPy algebra gives its difference from the required Fréchet bilinear as

$$
-U_{\mathrm{eff}}
\left(n^\lambda_{12}-n^\lambda_{21}\right)
\left(n^\mu_{12}-n^\mu_{21}\right).
$$

The difference vanishes only if both orbital responses are transpose-symmetric. Finite-$q$ response has no such general guarantee.

The packed-spinor Dudarev path is different and internally consistent: `src/66_nc_dftu/m_nc_dftu_data.F90:789-840` defines $V^\lambda=-U_{\mathrm{eff}}n_\lambda$ and contracts it with reversed indices, yielding the desired trace.

## q/-q completion and final-row overwrite

For a real displacement, the paired mixed coefficient obeys $K_{-q}=K_q^*$. The DDB components must therefore be reconstructed as

$$
\Re K_q=\frac{\Re K_q+\Re K_{-q}}{2},
\qquad
\Im K_q=\frac{\Im K_q-\Im K_{-q}}{2}.
$$

`src/72_response/m_dfpt_scfcv.F90:2459-2624` first accumulates a `mixed - frozen` pair, RV1, missing-occupation-arm, and response-square contributions. At `2635-2638`, it unconditionally assigns the final bucket from only the mirrored `mixed - frozen` pair. The SymPy witness differentiates this published expression with respect to each prior RV1, missing-arm, and response-square symbol and obtains zero; those previously accumulated classes cannot reach `d2nl` through `2688-2693`.

The pairing identity is correct only if the computed $K_{-q}$ is the conjugate partner of the same complete physical coefficient. The source audit proves the final expression has the pairing form, but does not prove that `mixed - frozen` alone is a complete stationary DDB ledger. See [nc-dftu-mixed-perturbation-ddb-design](nc-dftu-mixed-perturbation-ddb-design.md) for the broader stationary-ledger constraint and why a standalone mixed-wavefunction occupation is not automatically a DDB acceptance oracle.

## Runtime controls and rejected directions

The current Si Gamma collinear NC DFT+U/U0 control has a U-channel acoustic row sum of approximately $+0.1472328$ and a finite-$U$ force-constant error of $0.1252776455$ against the matched phonopy reference. The matched U0 twin agrees with the reference at approximately $1.5\times10^{-5}$, so the comparison isolates the finite-$U$ channel.

The geometry hypothesis was rejected: an asymmetric-equivalent FCC Si representation preserved the U0 optical spectrum to $1.86\times10^{-5}\,\mathrm{cm}^{-1}$ while retaining the nearly isotropic finite-$U$ acoustic defect. MPI rank, explicit spin asymmetry, and correlated-site selection also did not remove it.

A gated exact-$n^{(2)}$ accumulator activation was rejected: it changed the row sum to approximately $-0.2282416$ and increased the force-constant error to $0.2013131984$. The mixed-occupation cache mapping therefore lacks the independent PAO oracle needed for production use.

A separate retained compatibility fix permits the Kramers scalar wavefunction-ket occupation cache to use one real component or two complex components; it is at `src/66_nc_dftu/m_nc_dftu.F90:593-627`. It unblocks `tim1rev=1` controls but does not cure the finite-$U$ DDB defect.

## Reproduction

Run from the MemNotes project with the required Python environment:

```bash
source /home/hexu/projects/myenvs/mydev/bin/activate
python notes/nc-dftu-scalar-dudarev-2dte-audit.py
```

Expected output includes all `PASS` lines and the nonzero mismatch
`-U*(nl12 - nl21)*(nm12 - nm21)`.

## Variables

| Symbol | Meaning | Units |
|---|---|---|
| $n$ | Correlated-subspace occupation matrix | electrons |
| $n_\lambda$, $n_\mu$ | First-order occupation response to the two perturbations | electrons per perturbation |
| $n_{\lambda\mu}$ | Mixed occupation response in the unconstrained product jet | electrons per perturbation pair |
| $U_{\mathrm{eff}}$ | Dudarev interaction $U-J$ | Ha |
| $V^\lambda$ | First-order Hubbard potential | Ha per perturbation |
| $K_q$ | Complex mixed DFT+U coefficient at phonon wavevector $q$ | DDB convention |

## Linked concepts

- [nc-dftu-mixed-perturbation-ddb-design](nc-dftu-mixed-perturbation-ddb-design.md) — stationary DDB ledger and mixed-response constraints.
- [nc-dftu-dfpt-implementation-report](nc-dftu-dfpt-implementation-report.md) — NC PAO response implementation path.
- [notation](notation.md) — project-wide notation.
