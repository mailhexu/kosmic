---
type: Domain Topic
id: workstation/usage/locate-upf-pseudopotentials
domain: workstation
audience: usage
artifact_role: guideline
status: draft
summary: Find existing scalar or full-relativistic ONCVPSP UPF pseudopotentials on this workstation with locate, and verify pair compatibility before use.
triggers: [UPF pseudopotential, ONCVPSP, SG15, PseudoDojo, locate upf]
source_project: native
source_sha256: empty
aliases: [find pseudopotentials]
---

# Locate UPF pseudopotentials on this workstation

Search for existing UPF-format pseudopotentials with `locate`. Do not build ONCVPSP from source: the local oncvpsp tree at `/home/hexu/projects/oncvpsp` has macOS `make.inc` paths and does not compile on this machine.

## Search

```bash
locate -i '*.upf' | grep -iE 'cl|chlor'   # filter by element
locate -i '*Li*.upf'
```

## Known-good collections

- SG15 scalar ONCVPSP PBE, v1.0 and v1.1: `/home/hexu/.local/pp/sg15/sg15_oncv_upf_2015-10-07/`. A mirror for ABACUS lives under `/home/hexu/.local/pp/abacus/psp/SG15_ONCV_v1.0_upf/`. SG15 has only `-1.0` for Li; `-1.1` files exist for Cl.
- PseudoDojo full-relativistic ONCVPSP PBE (PDv0.3 and PDv0.4): `/STORAGE2/Xibu4T/document/bak_hexu/.local/pp/abinit/dojo/pseudo_dojo/pseudo_dojo/pseudos/ONCVPSP-PBE-FR-PDv{0.3,0.4}/<Sym>/`.

## Verify compatibility

Check the header of each candidate:

```bash
grep -m4 -E 'relativistic|pseudo_type|z_valence|element|functional' <file>.upf
```

A matched pair needs: the same `pseudo_type="NC"`, the same XC functional (PBE), and matching `relativistic="scalar"` (scalar relativistic, SR) or `relativistic="full"` (full relativistic, FR) for both species.

## Verified example pairs (LiCl)

- SR: `Li_ONCV_PBE-1.0.upf` plus `Cl_ONCV_PBE-1.1.upf` (SG15).
- FR: `ONCVPSP-PBE-FR-PDv0.4/Li/Li-s_r.upf` plus `.../Cl/Cl_r.upf` (PseudoDojo).

## Traps

- Naming differs: PseudoDojo uses `_r` suffixes for relativistic sets; SG15 uses `ONCV_PBE-<version>` suffixes.
- Do not attempt to build the local oncvpsp checkout.
