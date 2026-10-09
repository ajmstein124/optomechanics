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
- [x] Physical model defined (SnV in diamond, target phoxonic co-design)
- [x] Cavity geometry chosen: **2D slab photonic crystal cavity** (not 1D nanobeam)
- [ ] Photonic bandgap simulation set up (legume or COMSOL)
- [x] Phononic bandgap simulation set up (scripts/phononic_band.py)
- [ ] Co-design optimization strategy defined
- [ ] Analysis pipeline set up

---

## Repository Structure

```
optomechanics/
├── CLAUDE.md                       ← this file (top-level driver)
├── agents/                         ← sub-agent context files (one per domain)
├── skills/                         ← reusable skill/tool definitions
├── data/                           ← simulation outputs (gitignored)
├── results/                        ← pulled back from Windows (gitignored)
├── scripts/
│   ├── phononic_band.py            ← COMSOL phononic band structure (cross unit cell)
│   └── remote_runner.py            ← SSH runner: copy + execute on Windows COMSOL machine
└── notebooks/
```

**Execution model**: scripts run on Windows (`jvlab@100.68.160.53`) via SSH.
Trigger with: `python scripts/remote_runner.py scripts/phononic_band.py`
Results saved to `C:\Users\hopel\Documents\Abby\optomechanics\` and pulled back to `results/`.

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

## Background Reading

- **Jasper Chan PhD thesis** (Caltech 2012, Painter group): Ground-state cooling of a 3.7 GHz mechanical mode in a Si nanobeam optomechanical crystal. Key reference for:
  - Phononic Bloch state theory (Ch. 3.1.4)
  - Cross unit cell phononic shield design (Fig 3.9): params ca, ct, ch, t
  - COMSOL Floquet periodic BC setup for mechanical band structure (App. F)
  - Cavity design via smooth defect modulation (well function)
  - Optomechanical coupling rate (moving boundary + photoelastic effect)

## Design Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-10-08 | Project created | Starting point for SnV phoxonic cavity design |
| 2026-10-08 | 2D slab PCC geometry (not 1D nanobeam) | User decision: 2D cavities |
| 2026-10-08 | Cross unit cell script (superseded) | Initial starting point from Chan thesis; has phononic bandgap but NO photonic bandgap for TE modes |
| 2026-10-09 | **Switched to snowflake crystal** | Safavi-Naeini & Painter 2010 snowflake (hexagonal lattice) has simultaneous phononic + photonic bandgap — required for phoxonic co-design. Cross is unsuitable. |
| 2026-10-09 | Rectangular 2-atom supercell for snowflake | Allows orthogonal Floquet BCs in COMSOL (Lx=a, Ly=a√3); k-path Γ→X→S→Y→Γ |
| 2026-10-08 | Diamond isotropic elasticity in first script | Simpler; can upgrade to cubic (c11=1076, c12=125, c44=578 GPa) once geometry is validated |
