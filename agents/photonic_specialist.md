# Agent: Photonic Crystal Specialist

**Domain:** Photonic crystal cavity design for SnV at 619 nm in diamond.  
**Status:** Initialized but not yet active. Will be used when photonic simulation work begins.  
**When to use:** Questions about photonic bandgap, cavity mode design (Q/V), TE/TM gap requirements, legume GME simulation setup, or photonic crystal geometry choices for 619 nm.

---

## Target System

- **Emitter:** Tin vacancy (SnV) center in diamond
- **ZPL:** ~619 nm (vacuum)
- **Host material:** Diamond, n = 2.41 at 619 nm
- **Goal:** Photonic crystal cavity with high Purcell factor at 619 nm, co-designed with phononic shield

---

## Photonic Bandgap (Triangular Lattice, TE Modes)

For a triangular lattice of circular holes in a diamond slab, the TE photonic bandgap requires:

```
a / lambda ~ 0.25 to 0.38   (at d/a ~ 0.44, estimated)
```

For lambda = 619 nm:
```
a ~ 155 to 235 nm
```

This range is where the first TE bandgap opens. The exact bounds depend on r/a and d/a; a full photonic bandstructure sweep via legume is needed to map the gap precisely.

**Snowflake geometry** (Safavi-Naeini & Painter 2010) has a TE photonic bandgap at a/lambda ~ 0.42 (for Si at 1550 nm). The equivalent diamond/619 nm value needs to be computed.

---

## Figure of Merit

Purcell factor:
```
F_P = (3 / 4*pi^2) * (lambda/n)^3 * (Q/V)
```

where V is the mode volume in units of (lambda/n)^3.

For SnV cavity QED:
- Target Q ~ 10^5 to 10^6
- Target V ~ 1 (lambda/n)^3
- F_P ~ 10^4 to 10^5

Cooperativity: C = g^2 / (kappa * gamma), where g ~ sqrt(1/V), kappa ~ omega/Q, gamma = 1/tau_bulk.

---

## Simulation Tool: legume (GME)

The `pccsim` package (Documents/pccsim) uses legume for GME (Guided Mode Expansion) of 2D PCC slabs. It is the primary tool for photonic bandgap and cavity mode simulation.

**Key settings for 2D triangular lattice:**
- `gmax = 2` (truncation in reciprocal space; larger = more accurate but slower)
- `truncate_g = 'tbt'` (truncation type)
- k=0 only for cavity modes (heterostructure PCC)

See `Documents/pccsim/src/pccsim/` for the existing implementation.

---

## Photonic Simulation — Pending Tasks

1. Run photonic bandstructure for triangular lattice of holes in diamond at 619 nm via legume
2. Map TE/TM gap as function of (r/a, d/a) — specifically find a/lambda range for TE gap
3. Compare circular holes vs snowflake: does snowflake open a larger TE gap at the same fill fraction?
4. Determine cavity mode Q and V for a point-defect cavity in the triangular lattice
5. Feed photonic-compatible a range to the co-design mediator

---

## References

- Safavi-Naeini & Painter (2010) Opt. Express 18, 19659: snowflake crystal, photonic TE gap at 1550 nm in Si
- Johnson & Joannopoulos (2001) Opt. Express 8, 173: MPB photonic band structure
- legume documentation (github.com/fancompute/legume): GME for 2D PCC slabs
- `Documents/pccsim/`: existing legume-based simulation package for heterostructure PCCs
