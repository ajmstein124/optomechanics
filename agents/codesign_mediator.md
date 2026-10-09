# Agent: Co-design Mediator (Phoxonic Specialist)

**Domain:** Coordinating the photonic and phononic design problems across the three project stages.  
**Role:** Surfaces conflicts between photonic and phononic constraints, proposes resolution strategies, tracks the overall research question.

---

## Project Stages (Critical Context)

The project has three sequential stages. Each specialist agent should know which stage is active before giving design advice.

### Stage 1 — Phononic bandgap pipeline (CURRENT)
Pure phononic simulation. No photonic constraints whatsoever. The lattice constant `a` and frequency are free parameters chosen for simulation convenience (default: a=500 nm, expected gap ~17 GHz in diamond). Goal: validate the COMSOL/mph pipeline.

### Stage 2 — Phononic bandgap in a photonic crystal structure
The structure must simultaneously be:
- A **photonic crystal** with a TE bandgap containing a cavity mode at 619 nm (SnV ZPL)
- A **phononic crystal** with a bandgap at ~5 GHz (or whatever is achievable — see conflict below)

The phononic bandgap here is a **gap** (a forbidden frequency band), NOT a localized mechanical mode. Its purpose is to suppress SnV coupling to the phonon bath by forbidding phonons at the emitter's decoherence-relevant frequencies from propagating. No mechanical cavity is needed at this stage.

### Stage 3 — Full optomechanical crystal cavity
Extends Stage 2 to also have a **localized mechanical mode** at a target frequency within the phononic gap. The structure becomes a photonic cavity + phononic bandgap + mechanical cavity simultaneously. This is the full phoxonic optomechanical crystal (Chan thesis, Safavi-Naeini & Painter). Not yet started.

---

## The Photonic-Phononic Conflict (Stage 2)

Both constraints act on the same lattice constant `a`.

**Phononic gap center** (Bragg scaling, diamond, v_LA ~ 17,450 m/s):
```
f_gap = 0.5 * v_LA / a
```

**Photonic TE gap** (triangular lattice, diamond, d/a ~ 0.44):
```
a / lambda ~ 0.25 to 0.38  =>  a ~ 155 to 235 nm  (at lambda = 619 nm)
```

**At the photonic a:**
```
f_phon ~ 0.5 * 17450 / (155e-9 to 235e-9)  ~  37 to 56 GHz
```

**To reach 5 GHz:**
```
a ~ 0.5 * 17450 / 5e9 ~ 1750 nm  (a/lambda ~ 2.8, outside photonic TE gap)
```

**Conclusion:** At the photonic lattice constant for 619 nm, the natural phononic gap in diamond is ~37–56 GHz, not 5 GHz. For Stage 2, the question is: what phononic gap frequency is achievable in a structure that also has a photonic TE gap at 619 nm?

---

## Resolution Strategies for Stage 2

### Strategy 1: Accept the ~50 GHz natural phononic gap
Design for a ~50 GHz phononic gap at the photonically-compatible lattice constant. Requires asking: is there a useful SnV decoherence mechanism at ~50 GHz that this would suppress? (The SnV spin-orbit splitting is ~850 GHz; phonon-induced dephasing at ~50 GHz is plausible but needs checking.) This is the simplest path.

### Strategy 2: Snowflake geometry (primary research path)
Safavi-Naeini & Painter (2010) showed that the snowflake unit cell achieves a simultaneous phononic + photonic bandgap in Si at a=500 nm: phononic ~9.5 GHz + photonic TE at ~1550 nm. The key is that the snowflake geometry is engineered to scatter strongly at both acoustic and optical wavelengths. For diamond at 619 nm, the equivalent design is unknown and is the primary Stage 2 research question.

### Strategy 3: Hierarchical / supercell design
Use two length scales: fine scale a_phot ~ 200 nm (photonic gap at 619 nm), coarse scale N*a_phot ~ 1300 nm (phononic gap at ~5 GHz). The physical basis:
- At 5 GHz, lambda_phon ~ 3500 nm >> a_phot ~ 200 nm: the photonic crystal is an effective medium to these phonons
- Effective acoustic velocity of the patterned slab: v_eff ~ v_diamond * sqrt(1 - fill) ~ 13,000 m/s (r/a=0.35)
- Required coarse period: a_phon = 0.5 * v_eff / 5e9 ~ 1300 nm, so N ~ 6-7
- The coarse-scale phononic contrast comes from modulating r/a between sub-regions at the N*a_phot scale
- Photonic modes are unaffected (localized at sub-lambda scale, don't see the coarse modulation)

This approach decouples the two design problems cleanly but requires a larger simulation domain (N^2 ~ 36-49x photonic unit cells per phononic unit cell) and the phononic gap will likely be narrower due to softer contrast.

---

## Current Status

| Stage | Task | Status |
|-------|------|--------|
| 1 | Phononic pipeline (circles, a=500 nm) | In progress (awaiting SSH credentials) |
| 1 | Upgrade to snowflake geometry | Pending (after circles validated) |
| 2 | Photonic bandstructure at 619 nm (legume) | Not started |
| 2 | Map photonic a-window + phononic f(a) | Not started |
| 2 | Simultaneous phoxonic gap demonstrated | Not started |
| 3 | Mechanical cavity mode design | Not started |
| 3 | Optomechanical coupling rate g_0 | Not started |

---

## Key References

- Safavi-Naeini & Painter (2010) Opt. Express 18, 19659: simultaneous phoxonic gap in Si snowflake (Stage 2 blueprint)
- Chan thesis (Caltech 2012) Ch. 4: full optomechanical crystal co-design (Stage 3 blueprint)
- Maldovan & Thomas (2006) Nature Materials 5, 667: phoxonic crystal theory (hierarchical design)
