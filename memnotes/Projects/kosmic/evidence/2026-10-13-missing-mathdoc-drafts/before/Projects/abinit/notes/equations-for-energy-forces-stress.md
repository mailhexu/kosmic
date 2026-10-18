---
artifact_role: knowledge
audience: both
confidence: 0.9
created: 2026-03-07
last_validated: 2026-03-07T19:30:00
validation_procedure: |
  Extracted equations from m_effective_potential.F90 (effective_potential_evaluate subroutine).
  Cross-referenced with m_harmonics_terms.F90 and m_anharmonics_terms.F90.
  Verified against Taylor expansion formalism for effective potentials.
  Formatted in LaTeX for clarity and documentation.
successful_usage_count: 1
last_used_successfully: 2026-03-07T19:30:00
usage_stale: false
related_files:
  - "abinit/src/78_effpot/m_effective_potential.F90"
  - "abinit/src/78_effpot/m_harmonics_terms.F90"
  - "abinit/src/78_effpot/m_anharmonics_terms.F90"
  - "abinit/src/78_effpot/m_polynomial_coeff.F90"
related_functions:
  - "effective_potential_evaluate"
  - "harmonics_terms_evaluateIFC"
  - "harmonics_terms_evaluateElastic"
  - "anharmonics_terms_evaluateElastic"
  - "polynomial_coeff_evaluate"
tags:
  - "equations"
  - "energy"
  - "forces"
  - "stress"
  - "effective-potential"
  - "latex"
project: abinit
status: stable
validated_by: automatic
validation_date: 2026-03-07T19:30:00
links_to:
  - "energy-forces-stress-evaluation"
  - "effective-potential-data-structure"
  - "dipole-dipole-interaction"
linked_from: []
type: Project Knowledge
---

# Equations for Energy, Forces, and Stress Evaluation

## Overview
The effective potential method uses a **Taylor expansion** of the potential energy surface (PES) around a reference structure. This note documents all equations in LaTeX format.

## Notation

| Symbol | Meaning |
|--------|---------|
| $E$ | Total energy |
| $E_0$ | Reference energy |
| $\mathbf{u}_i$ | Displacement of atom $i$: $\mathbf{u}_i = \mathbf{r}_i - \mathbf{r}_i^0$ |
| $\boldsymbol{\varepsilon}$ | Strain tensor (Voigt: 6 components) |
| $\Phi_{ij}^{\alpha\beta}$ | Interatomic force constants (IFCs) |
| $C_{\alpha\beta}$ | Elastic constants (2nd order) |
| $Z^*_{i,\alpha\beta}$ | Born effective charge tensor |
| $\epsilon_{\infty,\alpha\beta}$ | High-frequency dielectric tensor |
| $V_0$ | Reference volume |
| $N_{cell}$ | Number of unit cells in supercell |

**Index conventions:**
- $i,j,k$: atom indices
- $\alpha,\beta,\gamma \in \{x,y,z\}$: Cartesian directions
- Greek indices: strain components (Voigt: 1-6)
- Repeated indices: Einstein summation convention

---

## Total Energy

### General Form

The total energy is a sum of contributions:

$$
E_{\text{total}} = E_{\text{ref}} + E_{\text{IFC}} + E_{\text{elastic}} + E_{\text{anh,elastic}} + E_{\text{anh,IFC}} + E_{\text{confine}} + E_{\text{field}}
$$

---

## 1. Reference Energy

### Equation

$$
E_{\text{ref}} = N_{\text{cell}} \cdot E_0
$$

Where:
- $E_0$: Reference energy of primitive cell (Hartree)
- $N_{\text{cell}} = n_1 \times n_2 \times n_3$: Number of cells in supercell

### Forces and Stress

$$
\mathbf{F}_{\text{ref}} = 0, \quad \boldsymbol{\sigma}_{\text{ref}} = 0
$$

---

## 2. Harmonic IFC Energy

### Energy

$$
E_{\text{IFC}} = \frac{1}{2} \sum_{i,j} \sum_{\alpha,\beta} \Phi_{ij}^{\alpha\beta} \, u_i^\alpha \, u_j^\beta
$$

Or in matrix notation:

$$
E_{\text{IFC}} = \frac{1}{2} \, \mathbf{u}^T \cdot \mathbf{\Phi} \cdot \mathbf{u}
$$

Where:
- $\Phi_{ij}^{\alpha\beta} = \frac{\partial^2 E}{\partial u_i^\alpha \partial u_j^\beta}$: IFC matrix
- $\mathbf{u}$: displacement vector (3N components)
- $\mathbf{\Phi}$: dynamical matrix (3N × 3N)

### Forces

$$
F_i^\alpha = -\frac{\partial E_{\text{IFC}}}{\partial u_i^\alpha} = -\sum_{j,\beta} \Phi_{ij}^{\alpha\beta} \, u_j^\beta
$$

In matrix form:

$$
\mathbf{F} = -\mathbf{\Phi} \cdot \mathbf{u}
$$

### Stress

No direct stress contribution from IFCs (couples to strain via elastic terms).

---

## 3. Elastic Energy (2nd Order)

### Energy

$$
E_{\text{elastic}} = \frac{1}{2} V_0 \sum_{\alpha,\beta=1}^6 C_{\alpha\beta} \, \varepsilon_\alpha \, \varepsilon_\beta + \sum_{i,\alpha,\gamma} \lambda_i^{\alpha\gamma} \, u_i^\alpha \, \varepsilon_\gamma
$$

Where:
- $C_{\alpha\beta}$: 2nd order elastic constants (6×6, Voigt notation)
- $\lambda_i^{\alpha\gamma}$: strain-displacement coupling (6×N×3)
- $\varepsilon_\alpha$: strain (Voigt: $\varepsilon_1=\varepsilon_{xx}$, $\varepsilon_4=2\varepsilon_{yz}$, etc.)

### Forces

$$
F_i^\alpha = -\frac{\partial E_{\text{elastic}}}{\partial u_i^\alpha} = -\sum_{\gamma} \lambda_i^{\alpha\gamma} \, \varepsilon_\gamma
$$

### Stress

$$
\sigma_\alpha = \frac{1}{V_0} \frac{\partial E_{\text{elastic}}}{\partial \varepsilon_\alpha} = \sum_{\beta} C_{\alpha\beta} \, \varepsilon_\beta + \frac{1}{V_0} \sum_{i,\gamma} \lambda_i^{\alpha\gamma} \, u_i^\gamma
$$

In matrix notation:

$$
\boldsymbol{\sigma} = \mathbf{C} \cdot \boldsymbol{\varepsilon} + \frac{1}{V_0} \mathbf{\lambda}^T \cdot \mathbf{u}
$$

---

## 4. Anharmonic Elastic Energy

### 3rd Order Elastic

$$
E_{\text{3rd,elastic}} = \frac{1}{6} \sum_{\alpha,\beta,\gamma=1}^6 C_{\alpha\beta\gamma} \, \varepsilon_\alpha \, \varepsilon_\beta \, \varepsilon_\gamma
$$

**Forces:**

$$
\mathbf{F} = 0 \quad \text{(no displacement dependence)}
$$

**Stress:**

$$
\sigma_\alpha = \frac{1}{2} \sum_{\beta,\gamma} C_{\alpha\beta\gamma} \, \varepsilon_\beta \, \varepsilon_\gamma
$$

### 4th Order Elastic

$$
E_{\text{4th,elastic}} = \frac{1}{24} \sum_{\alpha,\beta,\gamma,\delta=1}^6 C_{\alpha\beta\gamma\delta} \, \varepsilon_\alpha \, \varepsilon_\beta \, \varepsilon_\gamma \, \varepsilon_\delta
$$

**Stress:**

$$
\sigma_\alpha = \frac{1}{6} \sum_{\beta,\gamma,\delta} C_{\alpha\beta\gamma\delta} \, \varepsilon_\beta \, \varepsilon_\gamma \, \varepsilon_\delta
$$

### Elastic-Displacement Coupling

$$
E_{\text{elast-displ}} = \frac{1}{2} \sum_{i,\alpha,\beta,\gamma} D_i^{\alpha\beta\gamma} \, u_i^\alpha \, \varepsilon_\beta \, \varepsilon_\gamma
$$

**Forces:**

$$
F_i^\alpha = -\frac{\partial E_{\text{elast-displ}}}{\partial u_i^\alpha} = -\frac{1}{2} \sum_{\beta,\gamma} D_i^{\alpha\beta\gamma} \, \varepsilon_\beta \, \varepsilon_\gamma
$$

**Stress:**

$$
\sigma_\alpha = \sum_{i,\beta} D_i^{\beta\alpha\gamma} \, u_i^\beta \, \varepsilon_\gamma
$$

---

## 5. Strain-Phonon Coupling

### Energy

$$
E_{\text{strain-phonon}} = \frac{1}{2} \sum_{i,j,\alpha,\beta,\gamma} \Lambda_{ij}^{\alpha\beta\gamma} \, u_i^\alpha \, u_j^\beta \, \varepsilon_\gamma
$$

Where $\Lambda_{ij}^{\alpha\beta\gamma}$ is the strain-phonon coupling tensor.

### Forces

$$
F_i^\alpha = -\frac{\partial E_{\text{strain-phonon}}}{\partial u_i^\alpha} = -\sum_{j,\beta,\gamma} \Lambda_{ij}^{\alpha\beta\gamma} \, u_j^\beta \, \varepsilon_\gamma
$$

### Stress

$$
\sigma_\gamma = \frac{1}{2 V_0} \sum_{i,j,\alpha,\beta} \Lambda_{ij}^{\alpha\beta\gamma} \, u_i^\alpha \, u_j^\beta
$$

---

## 6. Anharmonic IFC (Polynomial Coefficients)

### General Form

$$
E_{\text{anh}} = \sum_k c_k \prod_{i,\alpha} \left(u_i^\alpha\right)^{n_{k,i,\alpha}}
$$

Where:
- $k$: term index
- $c_k$: coefficient for term $k$
- $n_{k,i,\alpha}$: power for atom $i$, direction $\alpha$ in term $k$

### Example Terms

**On-site anharmonicity:**

$$
E_{\text{on-site}} = c \cdot (u_x)^4
$$

**Bond anharmonicity:**

$$
E_{\text{bond}} = c \cdot (\mathbf{u}_i \cdot \mathbf{u}_j)^2
$$

**Multi-atom:**

$$
E_{\text{multi}} = c \cdot u_i^x \, u_j^y \, u_k^z
$$

### Forces

For a general term:

$$
F_i^\alpha = -\frac{\partial E_{\text{anh}}}{\partial u_i^\alpha} = -\sum_k c_k \, n_{k,i,\alpha} \, (u_i^\alpha)^{n_{k,i,\alpha}-1} \prod_{(j,\beta) \neq (i,\alpha)} (u_j^\beta)^{n_{k,j,\beta}}
$$

### Stress

Typically no direct stress contribution (depends on implementation).

---

## 7. Confinement Potential

### Energy

$$
E_{\text{confine}} = f_{\text{disp}} \sum_i \Theta(|\mathbf{u}_i| - u_c) \left(|\mathbf{u}_i| - u_c\right)^{p_{\text{disp}}} + f_{\text{strain}} \sum_\alpha \Theta(|\varepsilon_\alpha| - \varepsilon_c) \left(|\varepsilon_\alpha| - \varepsilon_c\right)^{p_{\text{strain}}}
$$

Where:
- $\Theta(x)$: Heaviside step function (1 if $x>0$, 0 otherwise)
- $u_c$: cutoff displacement
- $\varepsilon_c$: cutoff strain
- $f_{\text{disp}}, f_{\text{strain}}$: force/stress factors
- $p_{\text{disp}}, p_{\text{strain}}$: powers (typically 2 or 4)

### Forces

$$
F_i^\alpha = -\frac{\partial E_{\text{confine}}}{\partial u_i^\alpha} = -f_{\text{disp}} \, p_{\text{disp}} \, \Theta(|\mathbf{u}_i| - u_c) \left(|\mathbf{u}_i| - u_c\right)^{p_{\text{disp}}-1} \frac{u_i^\alpha}{|\mathbf{u}_i|}
$$

### Stress

$$
\sigma_\alpha = \frac{1}{V_0} \frac{\partial E_{\text{confine}}}{\partial \varepsilon_\alpha} = \frac{f_{\text{strain}}}{V_0} \, p_{\text{strain}} \, \Theta(|\varepsilon_\alpha| - \varepsilon_c) \left(|\varepsilon_\alpha| - \varepsilon_c\right)^{p_{\text{strain}}-1} \cdot \text{sgn}(\varepsilon_\alpha)
$$

---

## 8. External Electric Field

### Energy

$$
E_{\text{field}} = -\sum_i q_i \, \mathbf{E}(t) \cdot \mathbf{r}_i
$$

Where:
- $q_i$: charge of atom $i$ (from Born effective charges)
- $\mathbf{E}(t)$: time-dependent electric field

### Field Types

**Static field:**

$$
\mathbf{E}(t) = \mathbf{E}_0
$$

**Oscillating field:**

$$
\mathbf{E}(t) = \mathbf{E}_0 \cos(\omega t + \phi)
$$

**Gaussian pulse:**

$$
\mathbf{E}(t) = \mathbf{E}_0 \, \exp\left(-\frac{(t-t_0)^2}{2\sigma^2}\right) \cos(\omega t)
$$

### Forces

$$
\mathbf{F}_i = -\frac{\partial E_{\text{field}}}{\partial \mathbf{r}_i} = q_i \, \mathbf{E}(t)
$$

### Stress

No direct contribution (couples to polarization).

---

## 9. Dipole-Dipole Interaction

### Real-Space Interaction

$$
V_{dd}(\mathbf{r}) = \frac{1}{r^3} \left[ \boldsymbol{\mu}_i \cdot \boldsymbol{\mu}_j - 3 \frac{(\boldsymbol{\mu}_i \cdot \mathbf{r})(\boldsymbol{\mu}_j \cdot \mathbf{r})}{r^2} \right]
$$

Where:
- $\boldsymbol{\mu}_i = \mathbf{Z}^*_i \cdot \mathbf{u}_i$: induced dipole
- $\mathbf{r} = \mathbf{r}_j - \mathbf{r}_i$: separation vector

### Reciprocal Space (q→0 limit)

$$
\lim_{\mathbf{q} \to 0} \Phi_{\alpha\beta}^{dd}(\mathbf{q}) = \sum_{i,j,\gamma,\delta} Z^*_{i,\alpha\gamma} \, \frac{q_\gamma q_\delta}{|\mathbf{q}|^2 \, \epsilon_{\infty,\gamma\delta}} \, Z^*_{j,\beta\delta}
$$

This gives the **non-analytical term correction (NAC)** for LO-TO splitting.

### Ewald Summation

The full dipole-dipole IFC is:

$$
\Phi_{ij}^{\alpha\beta} = \Phi_{ij}^{\alpha\beta,\text{real}} + \Phi_{ij}^{\alpha\beta,\text{recip}} + \Phi_{ij}^{\alpha\beta,\text{self}} + \Phi_{ij}^{\alpha\beta,\text{surface}}
$$

Where each term converges exponentially:
- **Real space**: $\sum_{\mathbf{R}} \text{erfc}(\alpha|\mathbf{r}_{ij}+\mathbf{R}|)$
- **Reciprocal space**: $\sum_{\mathbf{G}} \frac{1}{|\mathbf{G}|^2} \exp(-|\mathbf{G}|^2/4\alpha^2)$
- **Self**: $-\frac{2\alpha}{\sqrt{\pi}}$ correction
- **Surface**: depends on boundary conditions

See [dipole-dipole-interaction](dipole-dipole-interaction.md) for implementation details.

---

## Summary Tables

### Energy Contributions

| Term | Equation | Scaling |
|------|----------|---------|
| Reference | $E_{\text{ref}} = N_{\text{cell}} E_0$ | O(1) |
| IFC | $E_{\text{IFC}} = \frac{1}{2} \mathbf{u}^T \mathbf{\Phi} \mathbf{u}$ | O(N²) |
| Elastic | $E_{\text{elast}} = \frac{1}{2} V_0 \boldsymbol{\varepsilon}^T \mathbf{C} \boldsymbol{\varepsilon}$ | O(1) |
| Anharm. IFC | $E_{\text{anh}} = \sum_k c_k \prod (u_i^\alpha)^{n_k}$ | O(N_terms) |
| Confinement | $E_{\text{conf}} = f \sum (|u|-u_c)^p$ | O(N) |

### Force Contributions

| Term | Equation |
|------|----------|
| IFC | $\mathbf{F} = -\mathbf{\Phi} \mathbf{u}$ |
| Elastic | $\mathbf{F} = -\mathbf{\lambda} \boldsymbol{\varepsilon}$ |
| Anharm. IFC | $F_i^\alpha = -\frac{\partial E_{\text{anh}}}{\partial u_i^\alpha}$ |
| Confinement | $\mathbf{F} = -f p (|u|-u_c)^{p-1} \hat{u}$ |
| Field | $\mathbf{F}_i = q_i \mathbf{E}$ |

### Stress Contributions

| Term | Equation |
|------|----------|
| Elastic | $\boldsymbol{\sigma} = \mathbf{C} \boldsymbol{\varepsilon} + \frac{1}{V_0}\mathbf{\lambda}^T \mathbf{u}$ |
| 3rd Elastic | $\sigma_\alpha = \frac{1}{2} C_{\alpha\beta\gamma} \varepsilon_\beta \varepsilon_\gamma$ |
| El-Di Coupling | $\sigma_\alpha = D_{\alpha\beta\gamma} u^\beta \varepsilon^\gamma$ |
| Strain-Phonon | $\sigma_\gamma = \frac{1}{2V_0} \Lambda_{ij}^{\alpha\beta\gamma} u_i^\alpha u_j^\beta$ |

---

## Units

All equations use **atomic units**:
- Energy: Hartree ($E_h$)
- Length: Bohr ($a_0$)
- Force: $E_h/a_0$
- Stress: $E_h/a_0^3$

**Conversions:**
- 1 $E_h$ = 27.2114 eV
- 1 $a_0$ = 0.529177 Å
- 1 $E_h/a_0$ = 51.422 eV/Å
- 1 $E_h/a_0^3$ = 29421 GPa

---

## Acoustic Sum Rule (ASR)

### Condition

Translational invariance requires:

$$
\sum_j \Phi_{ij}^{\alpha\beta} = 0 \quad \forall i, \alpha, \beta
$$

### Correction

Applied to IFCs:

$$
\Phi_{ii}^{\alpha\beta} \leftarrow \Phi_{ii}^{\alpha\beta} - \sum_{j \neq i} \Phi_{ij}^{\alpha\beta}
$$

Ensures $\mathbf{F} = 0$ for uniform translation ($\mathbf{u}_i = \mathbf{u}_0$).

---

## Linked Concepts

- [energy-forces-stress-evaluation](energy-forces-stress-evaluation.md) - Implementation details
- [effective-potential-data-structure](effective-potential-data-structure.md) - Data structures
- [dipole-dipole-interaction](dipole-dipole-interaction.md) - Long-range treatment
