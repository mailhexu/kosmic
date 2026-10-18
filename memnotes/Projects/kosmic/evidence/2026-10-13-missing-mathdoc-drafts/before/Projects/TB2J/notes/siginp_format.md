---
artifact_role: knowledge
audience: both
confidence: 0.95
created: 2026-03-19
last_validated: 2026-03-19
validation_procedure: "Parse LaMnO3 sig.inp and verify values"
project: TB2J
status: stable
validated_by: implementation
tags: [format, input, dmft]
type: Project Knowledge
---

# sig.inp File Format


## Overview
The sig.inp file contains the DMFT self-energy Σ(iωₙ) in text format. This format is commonly used by TRIQS, EDMFTF, and custom DMFT solvers. The file consists of a header section with metadata and a data section with frequency-dependent self-energy values.

## File Structure

```
[Header lines starting with #]
[Empty line]
[Data lines: frequency + self-energy values]
```

## Header Section

### Line 1: Orbital Counts
```
# nom,ncor_orb= 4774 10
```
- nom: Number of Matsubara frequencies (positive integer)
- ncor_orb: Number of correlated orbitals (positive integer)

### Line 2: Temperature
```
# T=  0.010000000000000
```
- T: Temperature in electron volts (eV)
- Note: T[eV] = T[K] × k_B where k_B = 8.617×10⁻⁵ eV/K
- Example: T = 0.01 eV ≈ 116 K

### Line 3: Σ(∞) - Vdc (Optional)
```
# s_oo-Vdc=  2.595...  3.291...  ... (10 values)
```
- One value per correlated orbital
- s_oo: High-frequency limit of self-energy Σ(∞)
- Vdc: Double-counting potential
- If using total self-energy, add this to Σ(iωₙ) - Σ(∞)

### Line 4: Σ(∞) Values (Optional)
```
# s_oo= [23.112..., 23.808..., ... (10 values)]
```
- High-frequency limit Σ(∞) for each orbital
- Used with --total-sigma flag

### Line 5: Vdc Values (Optional)
```
# Vdc= [20.517..., ... (10 values)]
```
- Double-counting potential for each orbital
- Relation: s_oo - Vdc = Σ(∞) - Vdc

## Data Section

### Format
Each line contains 1 + 2×ncor_orb columns:

```
ωₙ    Re(Σ₁)  Im(Σ₁)  Re(Σ₂)  Im(Σ₂)  ...  Re(Σₙ)  Im(Σₙ)
```

### Column Description

| Column | Content | Units |
|--------|---------|-------|
| 1 | Matsubara frequency ωₙ | eV |
| 2,3 | Real, Imaginary parts of Σ₁ | eV |
| 4,5 | Real, Imaginary parts of Σ₂ | eV |
| ... | ... | eV |
| 2n,2n+1 | Real, Imaginary parts of Σₙ | eV |

### Example Data Line
```
0.0314159265358979  -0.123456  0.067890  -0.234567  0.089012  ...
```

### Matsubara Frequency Convention

Fermionic Matsubara frequencies are defined as:

$$
\omega_n = \frac{(2n+1)\pi}{\beta}
$$

where:
- n = 0, 1, 2, ... (frequency index)
- β = 1/T (inverse temperature in eV⁻¹)
- ω₀ = π/β (first frequency)

### Self-Energy Convention

The file contains: Σ(iωₙ) - Σ(∞)

To get total self-energy:
- Use --total-sigma flag
- Total Σ = (Σ(iωₙ) - Σ(∞)) + Σ(∞) = Σ(iωₙ)

## Spin Convention for Collinear Calculations

For collinear spin with ncor_orb = 10 (e.g., 5 d-orbitals × 2 spins):

| Orbital Index | Spin | Orbital |
|--------------|------|---------|
| 1-5 | Up (↑) | d₁-d₅ |
| 6-10 | Down (↓) | d₁-d₅ |

The dmft_params.dat file maps these indices to specific atoms.

## Validation Rules

1. **Frequency monotonicity**: ωₙ must be strictly increasing
2. **Positive frequencies**: All ωₙ > 0
3. **Equal spacing**: Δω = 2π/β (constant)
4. **Column count**: Must be 1 + 2×ncor_orb

## Python Parsing Example

```python
# Parse header
with open('sig.inp', 'r') as f:
    for line in f:
        if line.startswith('# nom,ncor_orb='):
            nom, ncor_orb = map(int, line.split('=')[1].split())
        elif line.startswith('# T='):
            temperature = float(line.split('=')[1])
        elif not line.startswith('#'):
            break  # End of header

# Parse data
data = np.loadtxt('sig.inp', comments='#')
mesh = data[:, 0]  # Matsubara frequencies
sigma_diag = data[:, 1::2] + 1j * data[:, 2::2]  # Complex self-energy
```

## Variables

| Variable | Description | Units |
|----------|-------------|-------|
| nom | Number of Matsubara frequencies | - |
| ncor_orb | Number of correlated orbitals | - |
| T | Temperature | eV |
| ωₙ | n-th Matsubara frequency | eV |
| Σₖ(iωₙ) | Self-energy for orbital k | eV |
| Σ(∞) | High-frequency limit | eV |
| Vdc | Double-counting potential | eV |

## Linked Concepts
- [dmft_params_format](dmft_params_format.md): Maps orbital indices to atoms
- [matsubara_frequencies](matsubara_frequencies.md): Frequency mesh theory
- [dmft_tb2j_workflow](dmft_tb2j_workflow.md): Complete workflow
