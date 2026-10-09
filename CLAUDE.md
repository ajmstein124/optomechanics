# CLAUDE.md — Optomechanics Project Driver

This is the top-level agent context file. All sub-agent files and skill files are registered here and deferred to for their respective domains.

---

## Project Overview

**Project:** Co-designed photonic/phononic crystal cavities for SnV cavity QED  
**Owner:** ajmstein  
**Created:** 2026-10-08  

Design and simulate co-designed photonic crystal cavity (PCC) / phononic crystal cavity structures in diamond thin films for cavity quantum electrodynamics with the tin vacancy (SnV) center. The goal is simultaneous photonic and phononic bandgap engineering ("phoxonic" design) to achieve high Purcell enhancement at the SnV zero-phonon line while mechanically isolating the emitter from the phonon bath.

**Physical system**
- Emitter: Tin vacancy (SnV) center in diamond
  - Zero-phonon line (ZPL): ~619 nm
  - Debye-Waller factor: ~57%
  - Excited-state lifetime (bulk): ~4.5 ns
  - Spin-orbit splitting: ~850 GHz
- Host: Diamond thin film (free-standing slab or on SiO2)
  - Refractive index: n = 2.41 at 619 nm
- Target: co-designed structure with simultaneous photonic + phononic bandgaps

**Key figures of merit**
- Purcell factor: F_P = (3/4pi^2) * (lambda/n)^3 * (Q/V)
- Cooperativity: C = g^2 / (kappa * gamma)
- Photonic: maximize Q/V at 619 nm
- Phononic: bandgap spanning SnV-relevant mechanical frequencies (GHz range)

---

## Current State

- [x] Project initialized
- [ ] Physical model defined
- [ ] Cavity geometry chosen (nanobeam vs. 2D slab vs. heterostructure)
- [ ] Photonic bandgap simulation set up
- [ ] Phononic bandgap simulation set up
- [ ] Co-design optimization strategy defined
- [ ] Analysis pipeline set up

---

## Repository Structure

```
optomechanics/
├── CLAUDE.md               ← this file (top-level driver)
├── agents/                 ← sub-agent context files (one per domain)
├── skills/                 ← reusable skill/tool definitions
├── data/                   ← simulation outputs (gitignored)
├── scripts/                ← simulation and analysis scripts
└── notebooks/              ← exploratory notebooks
```

---

## Sub-Agents

Sub-agent files live in `agents/`. Each handles a specific domain. Register them here as they are created.

| File | Domain | Status |
|------|--------|--------|
| _(none yet)_ | | |

---

## Skills

Skill files live in `skills/`. Each encodes a reusable procedure or workflow.

| File | Purpose | Status |
|------|---------|--------|
| _(none yet)_ | | |

---

## Key Parameters and Constants

```
# Optical
lambda_ZPL      = 619e-9     # SnV zero-phonon line [m]
n_diamond       = 2.41       # refractive index at 619 nm
DWF             = 0.57       # Debye-Waller factor
tau_bulk        = 4.5e-9     # bulk excited-state lifetime [s]

# Mechanical (TBD — fill in as model is refined)
# omega_m       = ?          # target phononic bandgap center frequency
# Q_m           = ?          # target mechanical Q

# Fabrication constraints (TBD)
# slab_thickness = ?         # diamond film thickness [m]
# min_feature    = ?         # minimum lithographic feature [m]
```

---

## Design Decisions Log

_[Log non-obvious choices, constraints, and context that won't be obvious from the code]_

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-10-08 | Project created | Starting point for SnV phoxonic cavity design |
