# CLAUDE.md — Optomechanics Project Driver

This is the top-level agent context file. All sub-agent files are registered here and deferred to for their respective domains.

---

## Project Overview

**Project:** Co-designed photonic/phononic crystal structures for SnV cavity QED  
**Owner:** ajmstein  
**Created:** 2026-10-08  

Build and simulate diamond photonic crystal structures for cavity QED with the tin vacancy (SnV) center. The project has three sequential stages with increasing complexity.

**Physical system**
- Emitter: Tin vacancy (SnV) center in diamond
  - Zero-phonon line (ZPL): ~619 nm
  - Debye-Waller factor: ~57%
  - Excited-state lifetime (bulk): ~4.5 ns
  - Spin-orbit splitting: ~850 GHz
- Host: Diamond thin film (free-standing slab)
  - Refractive index: n = 2.41 at 619 nm

---

## Project Stages

### Stage 1 — Phononic bandgap pipeline (CURRENT)
**Goal:** Get COMSOL working. Simulate phononic band structure of a 2D diamond slab and confirm a bandgap exists.  
**No photonic constraints.** Geometry, lattice constant, and frequency are free parameters chosen for simulation convenience.  
**Success criterion:** COMSOL runs, band structure looks reasonable, bandgap detected and plotted.  
**Current geometry:** Triangular lattice of circular holes, a=500 nm, d/a=0.44, r/a=0.35. Expected phononic gap ~17 GHz.

### Stage 2 — Phononic bandgap in a photonic crystal structure
**Goal:** Co-design a structure that is simultaneously:
- A **photonic crystal cavity** at 619 nm (SnV ZPL), AND
- A **phononic crystal** with a bandgap at a target frequency (~5 GHz goal)

The phononic bandgap suppresses coupling of the SnV to the phonon bath — it is a **gap**, not a localized mechanical mode. The emitter sits in a region of phononic forbidden frequencies, reducing decoherence.  
**This is where the photonic/phononic lattice constant conflict matters** (see co-design mediator).

### Stage 3 — Full optomechanical crystal cavity
**Goal:** Extend Stage 2 so the structure also has a **localized mechanical mode** at a target frequency within the phononic gap — forming a full optomechanical crystal.  
**Adds:** mechanical cavity design (defect engineering), optomechanical coupling rate g_0, mechanical Q.  
**This is the full phoxonic co-design problem** (photonic cavity + phononic bandgap + mechanical cavity mode, all in one structure).

---

## Key figures of merit (by stage)

- Stage 1: fractional phononic gap width (f_bot - f_top) / f_center
- Stage 2: phononic gap at target frequency + photonic Q/V at 619 nm
- Stage 3: Purcell factor F_P = (3/4pi^2)(lambda/n)^3(Q/V); cooperativity C = g^2/(kappa*gamma); mechanical Q

---

## Current State

**Stage 1 (active):**
- [x] Phononic band structure scripts: `scripts/phononic_band.py` (single run) + `scripts/phononic_sweep.py` (parameter sweep)
- [x] Remote execution: `scripts/remote_runner.py` (SSH to Windows COMSOL machine)
- [x] Local Streamlit UI: `app.py` (parameter setup, unit cell preview, results visualization, Starting Point tab)
- [ ] SSH credentials filled in (pending — user to provide)
- [ ] First COMSOL run validated

**Stage 2 (not started):**
- [ ] Photonic bandgap simulation set up (legume or COMSOL)
- [ ] Phononic/photonic lattice constant conflict resolved (see co-design mediator)
- [ ] Simultaneous bandgap demonstrated in a single structure

**Stage 3 (not started):**
- [ ] Mechanical cavity mode design
- [ ] Optomechanical coupling rate computed

---

## Repository Structure

```
optomechanics/
├── CLAUDE.md                        <- this file (top-level driver)
├── app.py                           <- Streamlit UI (run: streamlit run app.py)
├── agents/                          <- sub-agent context files (one per domain)
│   ├── comsol_specialist.md
│   ├── phononic_specialist.md
│   ├── photonic_specialist.md
│   └── codesign_mediator.md
├── docs/
│   └── generate_param_reference.py  <- generates parameter_reference.pdf
├── configs/                         <- sweep configs (written by app.py UI)
│   └── sweep_config.json
├── results/                         <- pulled back from Windows (gitignored)
├── scripts/
│   ├── phononic_band.py             <- COMSOL single-run band structure
│   ├── phononic_sweep.py            <- COMSOL parameter sweep (a, d/a, r/a grid)
│   └── remote_runner.py             <- SSH runner: copy + execute on Windows COMSOL machine
└── notebooks/
```

**Execution model**:
1. Set parameters in app.py UI (localhost:8501)
2. Click "Write sweep config" to write `configs/sweep_config.json`
3. Run: `python scripts/remote_runner.py scripts/phononic_sweep.py`
4. Results pulled back to `results/` and displayed in app.py

Remote machine: `USERNAME@HOST` (placeholder — fill in SSH details)  
Remote path: `C:\Users\USERNAME\Documents\optomechanics` (fill in username)  
Python on Windows: `py -3.12`

---

## Sub-Agents

Sub-agent files live in `agents/`. Each handles a specific domain.

| File | Domain | Status |
|------|--------|--------|
| `agents/comsol_specialist.md` | COMSOL/mph simulation setup, Floquet BCs, eigensolvers | Active |
| `agents/phononic_specialist.md` | Phononic crystal design, gap analysis, parameter space | Active |
| `agents/photonic_specialist.md` | Photonic crystal design, SnV at 619 nm, legume GME | Initialized (not yet used) |
| `agents/codesign_mediator.md` | Phoxonic co-design, photonic/phononic conflict resolution | Active |

---

## Key Parameters and Constants

```python
# Optical
lambda_ZPL      = 619e-9     # SnV zero-phonon line [m]
n_diamond       = 2.41       # refractive index at 619 nm
DWF             = 0.57       # Debye-Waller factor
tau_bulk        = 4.5e-9     # bulk excited-state lifetime [s]

# Mechanical (diamond isotropic approximation)
E_d    = 1050e9    # Young's modulus [Pa]   (from c11=1076, c12=125, c44=578 GPa)
nu_d   = 0.07      # Poisson's ratio
rho_d  = 3500.0    # density [kg/m^3]
v_LA   = 17450     # longitudinal acoustic velocity [m/s] (sqrt(E(1-nu)/(rho(1+nu)(1-2nu))))
v_TA   = 8440      # transverse acoustic velocity [m/s]

# Frequency scaling (Bragg mechanism, calibrated to Safavi-Naeini & Painter 2010)
# f_gap ~ 0.5 * v_LA / a   (alpha=0.5 from Si snowflake at a=500nm, f~9.5 GHz)
# Diamond at a=500nm: f_gap ~ 17 GHz
# For 5 GHz: a ~ 1750 nm (incompatible with photonics at 619 nm -- see co-design notes)
# Photonic TE gap at 619 nm requires a ~ 155-235 nm -> f_phon ~ 37-56 GHz

# Default simulation parameters
a_default    = 500e-9    # lattice constant [m]
da_default   = 0.44      # d/a slab thickness ratio (Safavi-Naeini & Painter value)
ra_default   = 0.35      # r/a hole radius ratio
n_seg        = 15        # k-points per BZ segment (total = 4*n_seg+1)
n_modes      = 20        # eigenfrequencies per k-point
eig_shift    = 3.0       # GHz -- shift-invert center; set < gap center to skip DC modes
```

---

## Background Reading

- **Jasper Chan PhD thesis** (Caltech 2012, Painter group): Ground-state cooling of a 3.7 GHz mechanical mode in a Si nanobeam optomechanical crystal. Key reference for:
  - Phononic Bloch state theory (Ch. 3.1.4): f ~ v/a frequency scaling
  - COMSOL Floquet periodic BC setup for mechanical band structure (App. F)
  - Cavity design via smooth defect modulation (well function)
  - Optomechanical coupling rate (moving boundary + photoelastic effect)

- **Safavi-Naeini & Painter (2010)** Opt. Express 18, 19659: Snowflake crystal with simultaneous phononic + photonic bandgap in a Si slab. Key reference for:
  - Snowflake unit cell geometry (hexagonal lattice, d/a=0.44, r/a~0.35)
  - Rectangular 2-atom supercell for COMSOL with orthogonal Floquet BCs
  - Simultaneous phoxonic gap: phononic ~9.5 GHz + photonic TE at ~1550 nm
  - Starting point for diamond upgrade

- **COMSOL Blog** "Modeling Phononic Band Gap Materials and Structures":
  - Floquet BC formulation: u_dest = exp(-i k_F . (r_dest - r_src)) * u_src
  - Complex eigensolver required for k != 0 (eigenvalues remain real)
  - IBZ path: Gamma->X->M->Gamma (square lattice); our path Gamma->X->S->Y->Gamma (rectangular supercell of hex lattice)
  - Gap verification via harmonic response simulation (future validation step)

- **Grimsditch & Ramdas (1975)** Phys. Rev. B 11, 3139: Diamond elastic constants (c11=1076, c12=125, c44=578 GPa).

---

## Design Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-10-08 | Project created | Starting point for SnV phoxonic cavity design |
| 2026-10-08 | 2D slab PCC geometry (not 1D nanobeam) | User decision |
| 2026-10-08 | Cross unit cell script (superseded) | Initial starting point from Chan thesis |
| 2026-10-09 | **Switched from snowflake to circular holes** | Circles as a simpler pipeline-validation geometry first; upgrade to snowflake once COMSOL pipeline is validated. Circles may produce narrow/partial phononic gap but will confirm model setup. |
| 2026-10-09 | Rectangular 2-atom supercell | Lx=a, Ly=a*sqrt(3): allows orthogonal Floquet BCs in COMSOL. k-path Gamma->X->S->Y->Gamma. S = M point of hexagonal BZ. |
| 2026-10-09 | Default a=500 nm for pipeline test | Expected phononic gap ~17 GHz in diamond. Not photonically compatible at 619 nm (a/lambda=0.81, outside TE gap range), but validates the simulation pipeline before tackling co-design. |
| 2026-10-09 | Phononic/photonic conflict surfaced | Photonic TE gap at 619 nm requires a~155-235 nm -> phononic gap ~37-56 GHz. 5 GHz target requires a~1750 nm, incompatible. Research question: find a that achieves simultaneous gaps, likely requires snowflake geometry. |
| 2026-10-09 | eig_shift=3 GHz at a=500 nm | Intentionally below expected ~17 GHz gap to capture all acoustic branches. Raise to ~8 GHz if low-frequency modes clutter the plot. |
