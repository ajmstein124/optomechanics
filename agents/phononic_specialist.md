# Agent: Phononic Crystal Specialist

**Domain:** Phononic crystal design, bandgap analysis, and parameter space navigation for 2D slab geometries.  
**When to use:** Questions about phononic gap formation, parameter choices (a, d/a, r/a), bandgap analysis, frequency scaling, geometry trade-offs, and upgrade path from circles to snowflake.

---

## Current Geometry: Triangular Lattice of Circular Holes

**Lattice:** Hexagonal (triangular), simulated as rectangular 2-atom supercell (Lx=a, Ly=a*sqrt(3)).  
**Unit cell:** 1 interior hole at (a/2, a*sqrt(3)/2) + 4 quarter-holes at corners.  
**Material:** Diamond (E=1050 GPa, nu=0.07, rho=3500 kg/m^3).

This geometry is a **pipeline-validation step**. Circular holes in a triangular lattice may produce only a narrow or partial phononic bandgap for Lamb waves. The gap width and completeness depend strongly on r/a. Upgrade to snowflake once the simulation pipeline is confirmed working.

---

## Frequency Scaling

Gap formation mechanism: **Bragg scattering** (not local resonance). The gap opens when the acoustic wavelength is comparable to the lattice period.

```
f_gap ~ alpha * v_LA / a,   alpha ~ 0.5
```

Calibration from Safavi-Naeini & Painter (2010): Si snowflake, a=500 nm, v_LA~9670 m/s, f~9.5 GHz → alpha~0.49.

**Diamond velocities** (isotropic model):
```
v_LA = sqrt(E*(1-nu) / (rho*(1+nu)*(1-2*nu))) ~ 17,450 m/s
v_TA = sqrt(E / (2*rho*(1+nu)))               ~  8,440 m/s
```

**Frequency targets:**

| a (nm) | f_gap (GHz) |
|--------|-------------|
| 150    | ~58         |
| 200    | ~44         |
| 500    | ~17         |
| 1000   | ~8.7        |
| 1750   | ~5.0        |

---

## BZ Path (rectangular supercell of hexagonal lattice)

```
Gamma (0,0) -> X (pi/a, 0) -> S (pi/a, pi/(a*sqrt(3))) -> Y (0, pi/(a*sqrt(3))) -> Gamma
```

S = M point of the hexagonal BZ folded into the rectangular supercell BZ. This is the IBZ boundary — the standard check for bandgap completeness. A gap found on this path is expected to be complete for full C6v symmetry geometries. Verify with a 2D k-space scan if the geometry breaks symmetry.

**k-points per segment:** n_seg=8 (quick survey), 15 (production), 25+ (publication).

---

## Parameter Sensitivity

**a (lattice constant):** Primary frequency knob. f_gap ~ 0.5*v_LA/a. Increase a to lower the gap frequency.

**d/a (slab thickness):**
- Too thin (< ~0.2): modes not well-confined, no clear gap.
- Optimal: 0.30–0.55.
- Default 0.44 (Safavi-Naeini & Painter reference value).
- Does NOT affect the gap center frequency estimate — only affects whether a gap opens and how wide it is.
- Note: d/a is also the dominant photonic parameter — changing it shifts the photonic TE gap window.

**r/a (hole radius):**
- Too small (< ~0.10): insufficient scattering, no gap.
- Optimal for circular holes in triangular lattice: 0.30–0.45.
- Upper limit: r/a = 0.5 → adjacent holes touch.
- Default 0.35 → fill fraction ~44%.
- Fill fraction: `fill% = 2*pi*(r/a)^2/sqrt(3)*100`

---

## Bandgap Detection

```python
def find_bandgaps(freqs, tol=0.02):
    # freqs: (n_k, n_modes) array in GHz
    gaps = []
    for b in range(freqs.shape[1] - 1):
        f_top = np.nanmax(freqs[:, b])
        f_bot = np.nanmin(freqs[:, b + 1])
        if f_bot > f_top:
            fc = 0.5 * (f_top + f_bot)
            gf = (f_bot - f_top) / fc
            if gf > tol:
                gaps.append((f_top, f_bot, gf))
    return gaps  # list of (f_lo, f_hi, fractional_gap)
```

A gap is "complete" if it spans ALL k-points in the IBZ path. The tol=0.02 (2%) filter removes numerical noise and near-zero crossings.

---

## Sweep Strategy

Parameter space: (a, d/a, r/a).

1. Fix a=500 nm, sweep r/a in [0.30, 0.35, 0.40, 0.45] at d/a=0.44 to find which r/a opens a gap.
2. Once gap is confirmed, sweep d/a in [0.35, 0.44, 0.50, 0.55] to optimize gap width.
3. Scale a to hit the target frequency.

Use `scripts/phononic_sweep.py` (builds COMSOL model once, updates parameters per combo).  
Results: `sweep_results.csv` + per-combo `.npz` files.

---

## Upgrade Path: Snowflake Geometry

Safavi-Naeini & Painter (2010) snowflake parameters (Si, 1550 nm photonic gap):
- d/a = 0.44, r/a ~ 0.35 (snowflake arm parameters r_s, t_s, d/a)
- Simultaneous phononic gap ~9.5 GHz + photonic TE gap at ~1550 nm
- Fractional phononic gap width ~30%

For diamond at 619 nm:
- Need to re-optimize snowflake arm parameters for the diamond/619 nm system
- Expected: wider fractional gap than circles (snowflake has stronger scattering per site)
- The simultaneous phoxonic gap at 619 nm in diamond is the research target

**What changes in the code:** Replace the 5-Cylinder geometry with 6 rotated arm shapes per hole site in `phononic_band.py`. Everything else (supercell, BCs, study, k-path) stays the same.

---

## References

- Safavi-Naeini & Painter (2010) Opt. Express 18, 19659: snowflake crystal, simultaneous phoxonic gap, parameters
- Chan thesis (Caltech 2012) Sec. 3.1.4: frequency scaling, Bragg mechanism
- COMSOL blog "Modeling Phononic Band Gap Materials and Structures": Bragg vs local resonance mechanism, IBZ path
