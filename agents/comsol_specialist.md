# Agent: COMSOL Specialist

**Domain:** COMSOL 6.x simulation setup via the mph Python library.  
**When to use:** Any question about COMSOL model construction, Floquet BCs, eigenfrequency solver settings, geometry operations, mesh, or troubleshooting COMSOL/mph errors.

---

## mph Workflow

```python
import mph
client = mph.start(cores=4)
model  = client.create('name')
m      = model.java          # COMSOL Java API
```

- Build the model once; update parameters and re-run geometry/mesh/study per sweep combo.
- `m.param().set('name', 'value', 'description')` — set global parameters.
- `m.study('std1').run()` — run all study steps.
- `client.clear()` when done (releases COMSOL server resources).

---

## Floquet Periodic Boundary Conditions

**Mathematical form** (from COMSOL blog "Modeling Phononic Band Gap Materials and Structures"):

```
u_dest = exp(-i * k_F . (r_dest - r_src)) * u_src
```

where `k_F = (kx, ky, 0)` is the Bloch wavevector, `r` is the position vector, `u` is the displacement field.

**COMSOL setup:**
```python
pc = solid_node.create(name, 'PeriodicCondition', 2)
pc.set('PeriodicType', 'Floquet')
pc.set('kFloquet', ['kx', 'ky', '0'])   # kx, ky are global parameters
pc.selection().named(src_sel)
dest = pc.create('dest', 'Destination', 2)
dest.selection().named(dst_sel)
```

Two conditions needed for rectangular supercell:
- `pc_x`: x=0 face → x=a face (sel_x0 → sel_xa)
- `pc_y`: y=0 face → y=a*sqrt(3) face (sel_y0 → sel_ya)
- Top/bottom (z faces): free/traction-free by default.

**Complex eigensolver note:** For k != 0, the phase factor is complex, so COMSOL invokes a complex eigensolver automatically. Eigenvalues (omega^2) remain real for an undamped system. `getData()` returns real frequencies — this is correct behavior.

**k=Gamma special case:** At kx=ky=0, matrices are real and zero-frequency rigid-body modes appear. Use `eig_shift_GHz > 0` to skip them.

---

## Box Face Selections

Used to select faces on a specific plane for periodic BC assignment:

```python
s = comp.selection().create(name, 'Box')
s.set('entitydim', 2)
s.set('condition', 'allvertices')   # face selected only if ALL vertices are in the box
s.set('xmin', f'({coord})-{tol}')
s.set('xmax', f'({coord})+{tol}')
s.set('ymin', '-a_lat*0.1'); s.set('ymax', 'a_lat*2.0')  # wide in non-axis directions
s.set('zmin', '-d_slab');    s.set('zmax', 'd_slab')
```

Tolerance `tol = 'a_lat*1e-4'` is tight enough to avoid picking up internal faces.  
Four selections needed: `sel_x0` (x=0), `sel_xa` (x=a), `sel_y0` (y=0), `sel_ya` (y=a*sqrt(3)).

---

## Eigenfrequency Study

```python
std = m.study().create('std1')
eig = std.create('eig1', 'Eigenfrequency')
eig.set('neigsactive', 'on')
eig.set('neigs', str(n_modes))       # number of eigenfrequencies to find
eig.set('shift', f'{shift_GHz}[GHz]')  # shift-invert center
```

**Shift rule:** Set shift to 30-70% of the expected gap center. Shift must be below the gap. If modes are missing, lower the shift. If DC modes clutter the plot, raise the shift.

**Extracting results:**
```python
ev = m.result().numerical().create('ev1', 'EvalGlobal')
ev.set('data', 'dset1')
ev.setIndex('expr', 'freq', 0)
ev.setIndex('unit', 'GHz', 0)
# after study.run():
raw = ev.getData()   # list of lists: outer=eigenmode, inner=expression
freqs = np.array([float(entry[0]) for entry in raw])
```

---

## Geometry: Triangular Lattice of Circular Holes (current geometry)

**Supercell:** Lx=a, Ly=a*sqrt(3), Lz=d (rectangular 2-atom cell of the hexagonal lattice).

**Holes:**
- 1 interior hole at (a/2, a*sqrt(3)/2) — fully inside cell
- 4 corner holes at (0,0), (a,0), (0,a*sqrt(3)), (a,a*sqrt(3)) — each a quarter-atom

```python
cyl = geom.create(name, 'Cylinder')
cyl.set('r', 'r_hole')
cyl.set('h', '1.1*d_slab')           # taller than slab so Boolean Difference clips it cleanly
cyl.set('pos', [x0_expr, y0_expr, '-0.55*d_slab'])
```

Union all holes, then Difference from slab block. Run `geom.run('fin')` to finalize.

**For parameter sweeps (updating geometry in-loop):**
```python
m.param().set('a_lat', str(a))
m.param().set('d_slab', str(d))
m.param().set('r_hole', str(r))
m.component('comp1').geom('geom1').run('fin')   # rebuild geometry
m.component('comp1').mesh('mesh1').run()         # re-mesh
```

Box face selections are parametric so they update automatically when `a_lat` changes.

---

## Upgrade Path: Snowflake Geometry

When upgrading from circles to snowflake (Safavi-Naeini & Painter 2010), replace the Cylinder objects with 6 rotated arm shapes per hole site. The supercell, k-path, BCs, and eigenfrequency study remain unchanged.

---

## Known Issues / Gotchas

- **Windows encoding:** Never use Unicode in `print()` statements. Windows SSH uses cp1252; box-drawing characters cause `UnicodeEncodeError`.
- **Scripts must be on local Windows drive:** Network/cloud-synced paths (OneDrive, etc.) cause COMSOL to behave incorrectly.
- **getData() returns empty:** Check that `study.run()` completed without error. Check `eig_shift` is in range.
- **Box selections miss faces:** Increase `tol` slightly (try `a_lat*5e-4`). Verify face count with `len(solid_node.selection('geom1_...').entities(2))`.
