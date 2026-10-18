---
type: reference
status: stable
audience: both
artifact_role: knowledge
---

# TB2J PAW Exchange: Term-by-Term Decomposition

## Overview

The TB2J projector Green-function exchange for PAW systems requires, per site,
three ingredients in the PAW projector basis $\tilde p_i$:

1. **Projector coefficients** $C^{\sigma}_{n,i}(k) = \langle\tilde p_i | \psi^{\sigma}_{nk}\rangle$
2. **Overlap metric** $s_{ij} = \langle\phi_i|\phi_j\rangle - \langle\tilde\phi_i|\tilde\phi_j\rangle$
3. **Spin-splitting operator** $\Delta_{ij} = H^{\uparrow}_{ij} - H^{\downarrow}_{ij}$

The spin-splitting operator $\Delta_{ij}$ has multiple physical contributions.
This note maps each term to its ABINIT storage location and output availability.

---

## The PAW on-site Hamiltonian Dij

The total PAW on-site Hamiltonian matrix is (`paw_ij%dij`):

$$
D_{ij}^{\sigma} = D_{ij}^{\text{KB}} + D_{ij}^{\text{Hartree}} + D_{ij}^{\text{XC},\sigma} + D_{ij}^{U,\sigma} + D_{ij}^{\text{SO},\sigma} + D_{ij}^{\text{hat}}
$$

ABINIT's `paw_ij` type stores each contribution as a separate array:

| Component | ABINIT field | Physical content | Spin-dep? |
|---|---|---|---|
| Total | `paw_ij%dij` | Sum of all terms below | ✅ |
| KB pseudopotential | (in `dij`, not separated) | Kleinman–Bylander $D^0_{ij}$ from PAW-XML | ❌ |
| Hartree | `paw_ij%dijhartree` | Coulomb $\langle\phi_i\phi_j - \tilde\phi_i\tilde\phi_j \;\vert\; 1/r \;\vert\; \rangle$ | ❌ |
| XC (AE) | `paw_ij%dijxc` | $\langle\phi \;\vert\; v_{xc}[n_1+n_c] \;\vert\; \phi\rangle$ | ✅ |
| XC (hat) | `paw_ij%dijxc_hat` | Compensation-charge XC $\int v_{xc} \sum_L Q_{ij}^L$ | ✅ |
| XC (val) | `paw_ij%dijxc_val` | Pseudo-only XC $\langle\tilde\phi \;\vert\; v_{xc}[\tilde n+\hat n+\tilde n_c] \;\vert\; \tilde\phi\rangle$ | ✅ |
| Hat (total) | `paw_ij%dijhat` | Full compensation-charge contribution to $V_{\text{trial}}$ | ✅ |
| DFT+U | `paw_ij%dijU` | Hubbard $V^{U,\sigma}_{m_1m_2}$ | ✅ |
| Spin-orbit | `paw_ij%dijso` | SOC contribution | ✅ |
| Exact exchange | `paw_ij%dijfock` | Hybrid Fock contribution | ✅ |

**For the exchange spin-splitting:**

$$
\Delta_{ij} = D_{ij}^{\text{XC},\uparrow} - D_{ij}^{\text{XC},\downarrow} + D_{ij}^{U,\uparrow} - D_{ij}^{U,\downarrow} + D_{ij}^{\text{SO},\uparrow} - D_{ij}^{\text{SO},\downarrow}
$$

(Hartree and KB are spin-independent → cancel in $\Delta$.)

---

## ABINIT output availability

### Without ABINIT modification (standard outputs)

| Output | What it contains | Format | Dij components? |
|---|---|---|---|
| `pawprt` (always) | Total Dij + Rhoij + noccmmp | **Text** (log file) | Total only |
| `prtvxc` (`*_VXC.nc`) | Smooth pseudo $V_{xc}(r)$ on FFT grid | NetCDF | Implicit in $V_{xc}$ |
| `prtpot` (`*_POT.nc`) | Total local $V_{\text{trial}} = V_{xc} + V_{psp} + V_{\text{Hartree}}$ | NetCDF | Local terms only (NO Hubbard, NO SOC) |
| WFK (`*_WFK.nc`) | Wavefunction coefficients + k-grid | NetCDF | Not directly; cprj recomputable |
| PAW-XML | PAW dataset ($\phi$, $\tilde\phi$, $\tilde p$, $s_{ij}$, $Q_{ij}^L$) | XML | Source for $s_{ij}$, $Q_{ij}^L$ |

**Key limitation:** No standard ABINIT output writes the individual Dij components (dijxc, dijU, dijso) to a binary file. The text `pawprt` output has the total Dij and the occupation matrix `noccmmp`.

### With ABINIT modification (`savetb2j` route)

| Output | What it contains | Format | Dij components? |
|---|---|---|---|
| `savetb2j` NetCDF | `delta_total`, `dijxc`, `dijU`, `dijso` separately | NetCDF | ✅ All separated |

The `savetb2j` route (`m_paw_savetb2j_netcdf.F90`) writes:
- `delta_total` = $D^{\uparrow}_{ij} - D^{\downarrow}_{ij}$ (complete spin-splitting)
- `dijxc` = `paw_ij%dijxc` spin-difference
- `dijU` = `paw_ij%dijU` spin-difference
- `dijso` = `paw_ij%dijso` spin-difference

---

## Recomputation strategies for the WFK+Vxc route (no ABINIT modification)

### XC spin-splitting

| Component | Source | Method |
|---|---|---|
| Smooth pseudo $\langle\tilde\phi \;\vert\; \Delta V_{xc}^{\text{FFT}} \;\vert\; \tilde\phi\rangle$ | `prtvxc` | Project onto PAW projectors from FFT grid (abinao existing method) |
| AE one-center $\langle\phi \;\vert\; v_{xc}[n_1+n_c] \;\vert\; \phi\rangle - \langle\tilde\phi \;\vert\; v_{xc}[\tilde n+\hat n+\tilde n_c] \;\vert\; \tilde\phi\rangle$ | PAW-XML + WFK | Reconstruct $n_1$ from $\rho_{ij}$ + cprj; evaluate $v_{xc}$ on radial sphere (Option B) |
| Hat XC $\int v_{xc} \sum_L Q_{ij}^L$ | PAW-XML | Compute from augmentation moments + smooth $v_{xc}$ |

### Hubbard (DFT+U) spin-splitting

| Component | Source | Method |
|---|---|---|
| $V^{U,\sigma}_{m_1m_2}$ | `pawprt` noccmmp + $U/J$ params | Recompute: $V^U_{m_1m_2} = \sum_{m_3m_4} U_{m_1m_2m_3m_4}\rho_{m_3m_4} - V_{dc}$ |

The occupation matrix `noccmmp` (density matrix in the $(l,m)$ basis) is printed by
`pawprt` at every SCF step. From it + the Hubbard $U$, $J$ parameters and the
Slater integrals $F^0, F^2, F^4, F^6$, the full Hubbard potential matrix can be
reconstructed using the Kanamori / rotationally-invariant DFT+U formulation
(`pawpupot` in ABINIT = `hubbard_potential` in the `m_hubbard_orbital` module).

### Spin-orbit contribution

| Component | Source | Method |
|---|---|---|
| $D^{\text{SO},\sigma}_{ij}$ | PAW-XML | Recompute from $\phi/\tilde\phi$ + $V_{\text{SO}}$ radial functions |

The SOC contribution requires the spin-orbit potential from the PAW-XML dataset
(`v_ps_so` in PSML, or the SOC radial functions in the PAW-XML file). For collinear
calculations without SOC (`nspden=2`, `nspinor=1`), this term is zero.

---

## Summary: what each exchange route provides

| Route | $\Delta^{\text{XC}}$ | $\Delta^{U}$ | $\Delta^{\text{SO}}$ | $s_{ij}$ | $C_{ni}(k)$ | Modification? |
|---|---|---|---|---|---|---|
| `savetb2j` | ✅ exact (`dijxc`) | ✅ exact (`dijU`) | ✅ exact (`dijso`) | ✅ from PAW-XML | ✅ direct | ABINIT source |
| GPAW exporter | ✅ full one-center | ❌ (GPAW DFT+U different) | ❌ | ✅ (`dO_ii`) | ✅ (`P_ani`) | No |
| WFK+Vxc Phase A | ⚠️ smooth only | ❌ | ❌ | ✅ (libpsp) | ✅ (WFK projection) | No |
| WFK+Vxc Phase B | ✅ full one-center | ❌ (recomputable from noccmmp) | ❌ | ✅ (libpsp) | ✅ (WFK projection) | No |
| WFK+Vxc + DFT+U | ✅ full one-center | ✅ (from noccmmp + U/J) | ❌ | ✅ (libpsp) | ✅ (WFK projection) | No |

---

## Priority assessment

For **pure PAW magnetic systems** (no DFT+U):
- Phase A (smooth XC only) is the fast cross-check
- Phase B (full one-center XC) matches GPAW

For **DFT+U PAW systems** (e.g., transition-metal oxides with $U$):
- The Hubbard spin-splitting often dominates $\Delta_{ij}$
- It can be recomputed from the occupation matrix + $U/J$ (available from `pawprt`)
- This makes DFT+U support feasible in the WFK+Vxc route without ABINIT modification

**Recommendation:** The WFK+Vxc PRD should include DFT+U recomputation as a Phase B
component, since the occupation matrix is already output by ABINIT and the Hubbard
potential is straightforward to recompute.
