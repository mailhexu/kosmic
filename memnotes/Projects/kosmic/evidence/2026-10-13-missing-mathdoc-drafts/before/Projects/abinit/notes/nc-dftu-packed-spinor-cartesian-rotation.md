---
artifact_role: knowledge
audience: both
type: validated-procedure
status: stable
title: "NC DFT+U packed-spinor Cartesian symmetry rotation"
created: 2026-09-09
project: abinit
tags:
  - nc-dftu
  - symmetry
  - spinor
  - pao
---

# NC DFT+U packed-spinor Cartesian symmetry rotation

## Scope

Use when changing or reviewing `symmetrize_nc_occmatrix_spinor`, `symrec_cart`, packed spin densities `(uu, dd, ud, du)`, or an NC DFT+U spinor symmetry path. This is Cartesian-spin transport, not the separate PAO real-harmonic `zarot` gauge problem.

## Locked convention

For ABINIT direct-lattice `rprimd`, reciprocal-lattice `gprimd`, and reciprocal-space symmetry `symrec`, use

$$
R_{\mathrm{spin}} = gprimd\; symrec\; rprimd^{T}.
$$

Do **not** use the inherited inverse-looking expression

$$
rprimd\; symrec^{T}\; gprimd.
$$

The locked form matches the PAW Cartesian spin convention. The rejected form is wrong for non-involutory operations and can be non-orthogonal in skew cells.

## Why this is easy to miss

Identity, mirrors, symmetric lattice matrices, and energy-only tests can hide the error. For a skew hexagonal C3 operation, the rejected form produced

$$
\left\|R^{T}R-I\right\|_F = 4.320\times10^{-1}
$$

and a packed-spinor star-average error of $5.77\times10^{-1}$. The PAW form gives orthogonality and the direct star average to machine precision.

The PAO generic-C3 real-harmonic relation

$$
zarot = Q D(R_{\mathrm{cart}})^{T} Q
$$

is a different basis-gauge conversion. Do not copy its $Q$ factors into the Cartesian packed-spin transform.

## Mandatory discharge gate

1. Use both a skew/non-orthogonal hexagonal C3 geometry and a cubic C3 control.
2. Assert $\|R_{\mathrm{spin}}^{T}R_{\mathrm{spin}}-I\|$ is at floating-point noise for every exercised operation.
3. Apply the operation to an explicit packed spinor density and compare the code-faithful star average with a direct SU(2)/Pauli construction.
4. Include time reversal and a pure $+y$ control. For packed channels,

$$
M_y=i(\rho_{ud}-\rho_{du}).
$$

5. Retain the rejected transform as a mutation control. A new formula is not certified unless the old one fails decisively.
6. Trace the actual `symrec` producer plus the local `rprimd`/`gprimd` definitions before transplanting this formula between PAO, spinor, and real-space code paths.

## Evidence and implementation

ABINIT Wave 3 commit `5ab4bca3cd` changed `m_nc_dftu_gs.F90` to the locked convention. Strict SymPy validation reported:

| Check | Residual |
|---|---:|
| Spinor covariance | $7.29\times10^{-17}$ |
| PAW-form orthogonality | $3.38\times10^{-16}$ |
| PAW-form direct Cartesian rotation | $2.22\times10^{-16}$ |
| PAW-form star average | $5.43\times10^{-16}$ |
| Time-reversal spin algebra | $9.18\times10^{-17}$ |

See [ABINIT lattice/matrix convention pitfalls](abinit-lattice-matrix-convention-pitfalls.md) for broader frame and matrix traps, and [the Wave-3 migration record](../specs/research/2026-09-07-port-inventory-migration-plan.md) for port scope and validation history.
