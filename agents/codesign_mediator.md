# Agent: Co-design Mediator (Phoxonic Specialist)

**Domain:** Simultaneous photonic + phononic crystal co-design ("phoxonic") for SnV cavity QED.  
**Role:** Coordinates the phononic and photonic specialists. Surfaces conflicts, proposes resolution strategies, and tracks the overall co-design research question.

---

## The Co-design Problem

We need a single 2D photonic crystal slab geometry that simultaneously has:

1. **Photonic TE bandgap** containing a cavity mode at 619 nm (SnV ZPL)
2. **Phononic bandgap** at the target mechanical frequency (goal: 5 GHz, or whatever is achievable in diamond at 619 nm)

Both constraints act on the same parameter `a` (lattice constant), creating a fundamental tension.

---

## The Photonic-Phononic Conflict

**Phononic gap center** (Bragg scaling, diamond):
```
f_gap = 0.5 * v_LA / a = 0.5 * 17450 / a   [a in meters, f in Hz]
```

**Photonic TE gap** (triangular lattice, diamond, d/a ~ 0.44):
```
a_phot ~ 0.25*lambda to 0.38*lambda = 155 to 235 nm  (at lambda=619 nm)
```

**At the photonic a:**
```
f_phon = 0.5 * 17450 / (155e-9 to 235e-9)  ~  37 to 56 GHz
```

**To reach 5 GHz phononic gap:**
```
a ~ 0.5 * 17450 / 5e9 = 1750 nm
a/lambda = 1750/619 ~ 2.8  (far outside photonic TE gap range)
```

**Conclusion:** At 619 nm in diamond, the natural photonic lattice constant gives a phononic gap of ~37-56 GHz, not 5 GHz. The 5 GHz target is currently incompatible with photonic co-design at this wavelength.

---

## Resolution Strategies

### Strategy 1 (Current): Validate pipeline at a=500 nm
Use a=500 nm as a test point regardless of photonic compatibility. Expected phononic gap ~17 GHz. The goal is to confirm the COMSOL simulation pipeline works and produces correct bandstructure results. Photonic co-design comes after.

### Strategy 2: Accept the ~50 GHz natural phononic gap
If we accept that the phononic gap falls at ~37-56 GHz at the photonically-compatible lattice constant, we can target a high-frequency mechanical mode. This may be relevant for SnV spin-orbit coupling (splitting ~850 GHz) or phonon-mediated interactions. The phononic shield still reduces phonon bath coupling even if not at 5 GHz.

### Strategy 3: Snowflake geometry (primary research path)
Safavi-Naeini & Painter (2010) demonstrated that the snowflake geometry achieves simultaneous phononic + photonic bandgaps in Si at a=500 nm. The phononic gap is at ~9.5 GHz and the photonic gap is at ~1550 nm (a/lambda~0.32 for Si snowflake). This works because the snowflake unit cell is designed to have strong scattering in both the acoustic and optical frequency ranges.

For diamond at 619 nm, the equivalent snowflake design would need:
- Photonic constraint: a/lambda ~ 0.25-0.42 → a ~ 155-260 nm (estimate)
- At a=200 nm: f_phon ~ 0.5*17450/200e-9 ~ 44 GHz
- The snowflake geometry may allow a wider phononic gap at smaller a/lambda, potentially pushing the phononic gap to lower fractional frequency

**This is the primary research question**: Can a snowflake geometry in diamond achieve a simultaneous photonic TE gap at 619 nm AND a phononic gap at a "useful" mechanical frequency? What is that frequency?

### Strategy 4: Superlattice / quasi-periodic design
Decouple the phononic and photonic lattice constants using a superlattice or a geometry with two different periodicities. Higher complexity, less studied.

---

## Current Status

| Domain | Task | Status |
|--------|------|--------|
| Phononic | Pipeline validation (circles, a=500 nm) | In progress (awaiting SSH credentials) |
| Phononic | Snowflake geometry implementation | Pending (after circles validated) |
| Photonic | Bandstructure at 619 nm, triangular lattice | Not started |
| Co-design | Simultaneous phoxonic gap in diamond | Research target |

---

## Next Decision Points

1. After phononic pipeline is validated with circles at a=500 nm:
   - Implement snowflake geometry in phononic_band.py
   - Run photonic bandstructure via legume (photonic specialist)
   - Map photonic a-window and compare with phononic frequency at that a

2. Once both photonic a-window and phononic f(a) are known:
   - Determine if any a achieves simultaneous gaps
   - If yes: optimize jointly for Q/V (photonic) and gap fraction (phononic)
   - If no: evaluate Strategy 2 (accept high-frequency phononic gap) or Strategy 4 (superlattice)

---

## Key References

- Safavi-Naeini & Painter (2010) Opt. Express 18, 19659: simultaneous phoxonic bandgap in Si snowflake — the primary blueprint
- Chan thesis (Caltech 2012) Ch. 4: co-design strategy for optomechanical crystal
- Maldovan & Thomas (2006) Nature Materials 5, 667: phoxonic crystals — theoretical framework
