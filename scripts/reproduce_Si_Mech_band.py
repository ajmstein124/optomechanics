"""
Reproduce Si snowflake mechanical band structure -- validation run.
Uses original Si parameters from unit_cell_3.mph. Single parameter point, N_ks=13.
Expected: phononic bandgap near 7 GHz.

Run via:
    python scripts/remote_runner.py scripts/reproduce_Si_Mech_band.py
"""

import sys
import numpy as np
import scipy.io
import matplotlib.pyplot as plt
from pathlib import Path
from comsol_utils import start_client, mphglobal, make_bz_path, bz_ticks, BZ_LABELS

SAVE_FOLDER = Path('simu_data') / 'reproduce_Si'
SAVE_FOLDER.mkdir(parents=True, exist_ok=True)

client, model = start_client('unit_cell_3.mph')
m = model.java

# Original Si parameters
scaling = 1.067
a  = 448e-9 * scaling   # 478 nm
d  = 182e-9
w  = 99e-9
t  = 220e-9
N_freqs = 10
f0 = 7e9

for name, val in [('a', a), ('d', d), ('w', w), ('f_r', 25e-9),
                   ('t', t), ('N_mode', N_freqs), ('f_mech', f0)]:
    m.param().set(name, str(val))

N_ks = 13
ks = make_bz_path(a, N_ks)
n_kpts = ks.shape[1]
freqs = np.zeros((n_kpts, 2*N_freqs), dtype=complex)

solid = m.component('comp1').physics('solid')

for ii in range(n_kpts):
    print(f'k-point {ii+1}/{n_kpts}  kx={ks[0,ii]:.3e}  ky={ks[1,ii]:.3e}')
    sys.stdout.flush()
    m.param().set('kFx', str(ks[0, ii]))
    m.param().set('kFy', str(ks[1, ii]))

    # Symmetric modes
    solid.feature('as1').active(False)
    solid.feature('sym1').active(True)
    m.sol('sol1').runAll()
    sym_f = mphglobal(m, 'solid.freq', 'dset1')
    freqs[ii, :N_freqs] = sym_f[:N_freqs]

    # Antisymmetric modes
    solid.feature('sym1').active(False)
    solid.feature('as1').active(True)
    m.sol('sol1').runAll()
    asym_f = mphglobal(m, 'solid.freq', 'dset1')
    freqs[ii, N_freqs:] = asym_f[:N_freqs]

    scipy.io.savemat(
        str(SAVE_FOLDER / f'Si_Mech_bands_nominal_ii_{ii+1}.mat'),
        {'freqs': freqs, 'ks': ks, 'a': a, 'd': d,
         'w': w, 't': t, 'f0': f0, 'N_ks': N_ks}
    )

# Final save
fname = str(SAVE_FOLDER / 'Si_Mech_bands_nominal.mat')
scipy.io.savemat(fname, {'freqs': freqs, 'ks': ks, 'a': a, 'd': d,
                          'w': w, 't': t, 'f0': f0, 'N_ks': N_ks})
print(f'Saved: {fname}')

# Plot
fig, ax = plt.subplots(figsize=(8, 6))
for jj in range(n_kpts):
    ax.plot(np.full(N_freqs, jj+1), 1e-9*np.real(freqs[jj, :N_freqs]),  'b.', markersize=8)
    ax.plot(np.full(N_freqs, jj+1), 1e-9*np.real(freqs[jj, N_freqs:]), 'r.', markersize=8)
ax.set_ylabel('Frequency (GHz)')
ax.set_xlabel('k-point')
ax.set_xticks(bz_ticks(N_ks))
ax.set_xticklabels(BZ_LABELS)
ax.set_xlim([1, 3*N_ks-2])
ax.set_ylim([0, 20])
ax.legend(['Symmetric', 'Antisymmetric'], loc='upper left')
ax.set_title('Si snowflake -- mechanical bands (reproduction)')
ax.tick_params(labelsize=12)
plt.tight_layout()
plt.savefig(str(SAVE_FOLDER / 'Si_Mech_bands_nominal.jpg'), dpi=150)
print('Done.')

client.clear()
