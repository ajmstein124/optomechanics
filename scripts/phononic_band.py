"""
phononic_band.py

Phononic band structure of a 2D cross-unit-cell slab via COMSOL 6.x (mph).

Geometry
--------
Square lattice (period ca), free-standing slab (thickness t).
Unit cell: diamond slab with a cross-shaped hole.
  Cross hole = union of two bars:
    horizontal bar: ch*ca  x  ct*ca  x  1.1*t
    vertical   bar: ct*ca  x  ch*ca  x  1.1*t
  Both centered at origin.

With ch < 1 (here 0.85), the hole does NOT reach the unit-cell edges,
so all 4 lateral faces are solid rectangles -- clean Bloch BC surfaces.

Band-structure path:  Gamma -> X -> M -> Gamma  (2D square BZ)

Material
--------
Diamond, isotropic approximation:
  E = 1050 GPa,  nu = 0.07,  rho = 3500 kg/m^3
(Upgrade to cubic anisotropy later if needed.)

Usage
-----
  py -3.12 phononic_band.py

Dependencies
------------
  pip install mph matplotlib numpy
  COMSOL 6.x must be installed locally (this script starts a COMSOL server).
"""

import sys
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')        # non-interactive -- safe for SSH / headless
import matplotlib.pyplot as plt
import mph

# =============================================================================
# PARAMETERS
# =============================================================================

# --- Geometry ---
ca  = 1.0e-6     # lattice constant [m]  <-- main knob; shifts gap frequency
t   = 0.22e-6    # slab thickness [m]
ct  = 0.25       # cross arm width fraction  (arm_width = ct * ca)
ch  = 0.85       # cross hole span fraction  (hole_span = ch * ca)

# --- Material: diamond isotropic ---
E_d   = 1050e9   # Young's modulus [Pa]
nu_d  = 0.07     # Poisson's ratio
rho_d = 3500.0   # density [kg/m^3]

# --- Simulation ---
n_seg   = 15     # k-points per BZ segment (total = 3*n_seg + 1)
n_modes = 20     # eigenfrequencies to extract at each k-point
eig_shift_GHz = 1.0  # eigenfrequency search shift [GHz]; raise if modes missed

# --- Output ---
save_dir = r'C:\Users\hopel\Documents\Abby\optomechanics'
tag      = f'ca{int(ca*1e9)}nm_t{int(t*1e9)}nm_ct{ct}_ch{ch}'

# =============================================================================
# K-PATH: Gamma - X - M - Gamma
# =============================================================================

kmax = np.pi / ca  # BZ boundary [rad/m]

seg_GX = np.c_[np.linspace(0,    kmax, n_seg, endpoint=False), np.zeros(n_seg)]
seg_XM = np.c_[np.full(n_seg, kmax), np.linspace(0, kmax, n_seg, endpoint=False)]
seg_MG = np.c_[np.linspace(kmax, 0, n_seg+1), np.linspace(kmax, 0, n_seg+1)]
k_path = np.vstack([seg_GX, seg_XM, seg_MG])   # shape (3*n_seg+1, 2), [rad/m]

dk     = np.linalg.norm(np.diff(k_path, axis=0), axis=1)
k_dist = np.r_[0, np.cumsum(dk)]       # arc-length coordinate for plotting

tick_idx = [0, n_seg, 2*n_seg, 3*n_seg]
tick_x   = k_dist[tick_idx]
tick_lbl = ['G', 'X', 'M', 'G']       # ASCII only (Windows cp1252 safe)

# =============================================================================
# BUILD COMSOL MODEL
# =============================================================================

print('Starting COMSOL server...')
client = mph.start(cores=4)
model  = client.create('phononic_diamond')
m      = model.java          # direct Java API handle

print('Building model...')

# --- Global parameters -------------------------------------------------------
p = m.param()
p.set('ca',  str(ca),   'Lattice constant [m]')
p.set('t',   str(t),    'Slab thickness [m]')
p.set('ct',  str(ct),   'Cross arm fraction')
p.set('ch',  str(ch),   'Cross hole span fraction')
p.set('kx',  '0',       'Bloch kx [rad/m]')
p.set('ky',  '0',       'Bloch ky [rad/m]')

# --- Component ---------------------------------------------------------------
comp = m.component().create('comp1', True)

# --- Geometry ----------------------------------------------------------------
geom = comp.geom().create('geom1', 3)
geom.lengthUnit('m')

# Unit cell slab
blk = geom.create('blk1', 'Block')
blk.set('size', ['ca', 'ca', 't'])
blk.set('base', 'center')

# Cross hole: horizontal bar (ch*ca x ct*ca x 1.1*t)
barh = geom.create('barh', 'Block')
barh.set('size', ['ch*ca', 'ct*ca', '1.1*t'])
barh.set('base', 'center')

# Cross hole: vertical bar (ct*ca x ch*ca x 1.1*t)
barv = geom.create('barv', 'Block')
barv.set('size', ['ct*ca', 'ch*ca', '1.1*t'])
barv.set('base', 'center')

# Union of the two bars = full cross hole
uni = geom.create('uni1', 'Union')
uni.selection('input').set(['barh', 'barv'])
uni.set('keepSubdomains', 'off')

# Subtract cross hole from slab
dif = geom.create('dif1', 'Difference')
dif.selection('input').set(['blk1'])
dif.selection('input2').set(['uni1'])

geom.run('fin')
print('  Geometry built.')

# --- Component-level Box Selections for lateral faces -----------------------
# Used to apply Floquet BCs to exactly the right faces.
# Tolerance 'ca*1e-4' is much smaller than the geometry features.

def box_face_sel(comp_node, name, axis, sign_str):
    """
    Create a Box Selection for the face perpendicular to 'axis' at sign*ca/2.
    sign_str: '-0.5' or '+0.5'
    """
    s = comp_node.selection().create(name, 'Box')
    s.set('entitydim', 2)                  # 2 = boundary (face)
    s.set('condition', 'allvertices')
    tol = 'ca*1e-4'
    ctr = f'({sign_str})*ca'              # = ±ca/2 since sign_str is '±0.5'
    for ax in ('x', 'y', 'z'):
        if ax == axis:
            s.set(f'{ax}min', f'{ctr}-{tol}')
            s.set(f'{ax}max', f'{ctr}+{tol}')
        else:
            # Span the full unit cell + margin so we catch slanted/partial faces
            s.set(f'{ax}min', '-2*ca')
            s.set(f'{ax}max',  '2*ca')
    return s

box_face_sel(comp, 'sel_xm', 'x', '-0.5')   # x = -ca/2
box_face_sel(comp, 'sel_xp', 'x',  '0.5')   # x = +ca/2
box_face_sel(comp, 'sel_ym', 'y', '-0.5')   # y = -ca/2
box_face_sel(comp, 'sel_yp', 'y',  '0.5')   # y = +ca/2

# --- Material ----------------------------------------------------------------
mat = comp.material().create('mat1', 'Common')
mat.label('Diamond')
mat.propertyGroup('def').set('density',       str(rho_d))
mat.propertyGroup('def').set('youngsmodulus', str(E_d))
mat.propertyGroup('def').set('poissonsratio', str(nu_d))

# --- Physics: Solid Mechanics ------------------------------------------------
solid = comp.physics().create('solid', 'SolidMechanics', 'geom1')

# Two Floquet periodic BCs (x-pair and y-pair).
# Source face + Destination sub-feature explicitly pair opposite faces.
def add_floquet_bc(solid_node, name, src_sel, dst_sel):
    """
    Add one Floquet (Bloch) periodic condition pairing src_sel -> dst_sel.
    k-vector is [kx, ky, 0] referencing the global parameters.
    """
    pc = solid_node.create(name, 'PeriodicCondition', 2)
    pc.label(f'Floquet {name}')
    pc.set('PeriodicType', 'Floquet')
    pc.set('kFloquet', ['kx', 'ky', '0'])
    pc.selection().named(src_sel)
    dest = pc.create('dest', 'Destination', 2)
    dest.selection().named(dst_sel)
    return pc

add_floquet_bc(solid, 'pc_x', 'comp1_sel_xm', 'comp1_sel_xp')
add_floquet_bc(solid, 'pc_y', 'comp1_sel_ym', 'comp1_sel_yp')
# Top and bottom faces: free (COMSOL default for Solid Mechanics)

# --- Mesh --------------------------------------------------------------------
mesh = comp.mesh().create('mesh1')
mesh.create('ftet1', 'FreeTet')
sz = mesh.create('size1', 'Size')
sz.set('hauto', 5)          # 1=finest ... 9=coarsest; 5=normal; 4=fine

# --- Study: Eigenfrequency ---------------------------------------------------
std = m.study().create('std1')
eig = std.create('eig1', 'Eigenfrequency')
eig.set('neigsactive', 'on')
eig.set('neigs',  str(n_modes))
eig.set('shift',  f'{eig_shift_GHz}[GHz]')   # search near this frequency

# Global evaluation node for eigenfrequency extraction
ev = m.result().numerical().create('ev1', 'EvalGlobal')
ev.set('data', 'dset1')
ev.setIndex('expr',  'freq', 0)
ev.setIndex('unit',  'GHz',  0)
ev.setIndex('descr', 'Eigenfrequency', 0)

print('Model ready. Beginning k-point sweep...')

# =============================================================================
# SOLVE LOOP
# =============================================================================

os.makedirs(save_dir, exist_ok=True)

freqs_GHz = np.full((len(k_path), n_modes), np.nan)

for i, (kxi, kyi) in enumerate(k_path):
    m.param().set('kx', repr(kxi))
    m.param().set('ky', repr(kyi))

    m.study('std1').run()

    # getData() returns list-of-lists: outer index = parameter (eigenmode),
    # inner index = expression (here: freq). Flatten to 1-D array.
    try:
        raw = ev.getData()
        row = np.array([float(r[0]) for r in raw], dtype=float)
    except Exception as e:
        print(f'  WARNING: getData() failed at k={i}: {e}')
        row = np.full(n_modes, np.nan)

    n = min(len(row), n_modes)
    freqs_GHz[i, :n] = row[:n]

    if i % 5 == 0 or i == len(k_path) - 1:
        f_lo = np.nanmin(row[:n]) if n > 0 else float('nan')
        f_hi = np.nanmax(row[:n]) if n > 0 else float('nan')
        print(f'  k={i+1:3d}/{len(k_path)}'
              f'  kx={kxi:.3e}  ky={kyi:.3e}'
              f'  f=[{f_lo:.3f}, {f_hi:.3f}] GHz')

# =============================================================================
# BANDGAP ANALYSIS
# =============================================================================

def find_bandgaps(freqs, k_dist, tol_frac=0.02):
    """
    Find complete bandgaps in the band structure.
    A gap exists between band n and n+1 if max(band_n) < min(band_{n+1})
    across all k-points (with a small tolerance tol_frac * center_freq).

    Returns list of (f_lower, f_upper, gap_frac) tuples.
    """
    n_k, n_b = freqs.shape
    gaps = []
    for b in range(n_b - 1):
        f_top    = np.nanmax(freqs[:, b])        # top of band b
        f_bottom = np.nanmin(freqs[:, b+1])      # bottom of band b+1
        if f_bottom > f_top:
            f_center  = 0.5 * (f_top + f_bottom)
            gap_frac  = (f_bottom - f_top) / f_center
            if gap_frac > tol_frac:              # ignore tiny numerical gaps
                gaps.append((f_top, f_bottom, gap_frac))
    return gaps

gaps = find_bandgaps(freqs_GHz, k_dist)

print('\nBandgap summary:')
if gaps:
    for (fl, fu, gf) in gaps:
        print(f'  gap: {fl:.3f} - {fu:.3f} GHz'
              f'  (center={0.5*(fl+fu):.3f} GHz, {gf*100:.1f}% gap/midgap)')
else:
    print('  No complete bandgap found.')
    print('  Try increasing ca (shifts gap to lower frequency)')
    print('  or adjusting ct/ch to widen the gap.')

# =============================================================================
# SAVE DATA
# =============================================================================

data_path = os.path.join(save_dir, f'phononic_band_{tag}.npz')
np.savez(data_path,
         freqs_GHz=freqs_GHz,
         k_path_radpm=k_path,
         k_dist=k_dist,
         ca=ca, t=t, ct=ct, ch=ch)
print(f'\nData saved: {data_path}')

# =============================================================================
# PLOT
# =============================================================================

fig, ax = plt.subplots(figsize=(5.5, 5))

for mi in range(n_modes):
    ax.plot(k_dist, freqs_GHz[:, mi], 'b-', lw=0.9, alpha=0.75)

# Shade bandgaps
for (fl, fu, _) in gaps:
    ax.axhspan(fl, fu, color='red', alpha=0.15, label=f'gap {fl:.2f}-{fu:.2f} GHz')

# Zone boundary lines
for xv in tick_x:
    ax.axvline(xv, color='gray', lw=0.5, ls='--')

ax.set_xticks(tick_x)
ax.set_xticklabels(tick_lbl, fontsize=11)
ax.set_xlabel('Wavevector', fontsize=11)
ax.set_ylabel('Frequency (GHz)', fontsize=11)
ax.set_title(f'Diamond phononic crystal band structure\n'
             f'ca={ca*1e9:.0f}nm  t={t*1e9:.0f}nm  '
             f'ct={ct}  ch={ch}', fontsize=10)
ax.set_xlim([k_dist[0], k_dist[-1]])
ax.set_ylim([0, None])
ax.grid(alpha=0.3)
if gaps:
    ax.legend(fontsize=8, loc='upper right')

plt.tight_layout()
fig_path = os.path.join(save_dir, f'phononic_band_{tag}.png')
fig.savefig(fig_path, dpi=150)
print(f'Figure saved: {fig_path}')

client.clear()
print('Done.')
