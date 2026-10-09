"""
app.py  --  Local Streamlit UI for phononic crystal parameter setup and results viewing.

Run with:
    streamlit run app.py

Dependencies (local Mac only):
    pip install streamlit matplotlib numpy
"""

import time
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

RESULTS_DIR = Path(__file__).parent / 'results'

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title='Phononic Crystal',
    layout='wide',
    initial_sidebar_state='expanded',
)
st.title('Phononic Crystal — Diamond Slab')

# ── Sidebar: parameters ───────────────────────────────────────────────────────

with st.sidebar:
    st.header('Geometry')
    a_nm = st.number_input('a  Lattice constant (nm)', 100, 3000, 500, step=10)
    da   = st.slider('d/a  Slab thickness',  0.20, 0.60, 0.44, 0.01)
    ra   = st.slider('r/a  Hole radius',     0.10, 0.48, 0.35, 0.01,
                     help='Holes touch at r/a = 0.5; keep ≤ 0.48')

    d_nm      = da * a_nm
    r_nm      = ra * a_nm
    fill_pct  = 2 * np.pi * ra**2 / np.sqrt(3) * 100   # % of slab area that is air
    st.caption(f'd = {d_nm:.0f} nm  ·  r = {r_nm:.0f} nm  ·  fill = {fill_pct:.1f}%')

    st.divider()
    st.header('Simulation')
    n_seg         = st.slider('k-points per segment',   5,  40, 15)
    n_modes       = st.slider('Modes per k-point',      5,  40, 20)
    eig_shift_GHz = st.slider('Eigenfreq shift (GHz)', 0.0, 30.0, 3.0, 0.5,
                              help='Eigenfrequency solver search center')

    st.divider()
    st.header('Material — Diamond')
    st.markdown('E = 1050 GPa  \nν = 0.07  \nρ = 3500 kg/m³  \nv_LA ≈ 17 500 m/s')
    f_est = 17500.0 / (a_nm * 1e-9) / 1e9
    st.metric('Band center estimate', f'{f_est:.1f} GHz', help='v_LA / a')

# ── Main columns ──────────────────────────────────────────────────────────────

col_cell, col_band = st.columns([1, 2])

# ── Unit cell visualization ───────────────────────────────────────────────────

with col_cell:
    st.subheader('Unit cell')

    Lx = float(a_nm)
    Ly = float(a_nm) * np.sqrt(3)
    rp = float(r_nm)

    fig_uc, ax_uc = plt.subplots(figsize=(3.2, 3.2 * np.sqrt(3)))
    ax_uc.set_aspect('equal')
    ax_uc.set_xlim(0, Lx)
    ax_uc.set_ylim(0, Ly)

    # Diamond slab background
    ax_uc.add_patch(mpatches.Rectangle((0, 0), Lx, Ly, color='#b8c9e0', zorder=0))

    # Holes — interior + 4 corners (clipped to axes boundary)
    for hx, hy in [(Lx/2, Ly/2), (0, 0), (Lx, 0), (0, Ly), (Lx, Ly)]:
        ax_uc.add_patch(mpatches.Circle((hx, hy), rp, color='white', zorder=1, clip_on=True))

    # Radius annotation on interior hole
    ax_uc.annotate(
        '', xy=(Lx/2 + rp, Ly/2), xytext=(Lx/2, Ly/2),
        arrowprops=dict(arrowstyle='<->', color='#c0392b', lw=1.2),
    )
    ax_uc.text(Lx/2 + rp/2, Ly/2 + Ly*0.025, f'r = {rp:.0f} nm',
               ha='center', va='bottom', fontsize=8, color='#c0392b')

    for sp in ax_uc.spines.values():
        sp.set_linewidth(1.5)
        sp.set_edgecolor('#2c3e50')
    ax_uc.set_xlabel('x  (nm)', fontsize=9)
    ax_uc.set_ylabel('y  (nm)', fontsize=9)
    ax_uc.set_title(
        f'a = {Lx:.0f} nm   d = {d_nm:.0f} nm\n'
        f'r/a = {ra:.2f}   d/a = {da:.2f}   fill = {fill_pct:.1f}%',
        fontsize=9,
    )
    ax_uc.tick_params(labelsize=8)
    plt.tight_layout()
    st.pyplot(fig_uc)
    plt.close(fig_uc)

    # BZ path diagram
    st.caption('k-path: Γ → X → S → Y → Γ  (rectangular BZ)')
    fig_bz, ax_bz = plt.subplots(figsize=(3.0, 1.8))
    kx_max = 1.0
    ky_max = 1.0 / np.sqrt(3)
    pts_bz = {'G': (0, 0), 'X': (kx_max, 0), 'S': (kx_max, ky_max), 'Y': (0, ky_max)}
    labels  = {'G': 'Γ', 'X': 'X', 'S': 'S', 'Y': 'Y'}
    path_bz = ['G', 'X', 'S', 'Y', 'G']
    xs_bz   = [pts_bz[k][0] for k in path_bz]
    ys_bz   = [pts_bz[k][1] for k in path_bz]
    ax_bz.fill([0, kx_max, kx_max, 0], [0, 0, ky_max, ky_max], color='#eaf0fb', zorder=0)
    ax_bz.plot(xs_bz, ys_bz, 'o-', color='#2c3e50', lw=1.5, ms=5, zorder=2)
    offsets = {'G': (-0.12, 0.03), 'X': (0.04, 0.03), 'S': (0.04, 0.03), 'Y': (-0.14, 0.03)}
    for k, (px, py) in pts_bz.items():
        ox, oy = offsets[k]
        ax_bz.text(px + ox, py + oy, labels[k], fontsize=9, color='#2c3e50')
    ax_bz.set_aspect('equal')
    ax_bz.set_xlim(-0.2, 1.35)
    ax_bz.set_ylim(-0.15, 0.85)
    ax_bz.set_xlabel('kx  (π/a)', fontsize=8)
    ax_bz.set_ylabel('ky  (π/a√3)', fontsize=8)
    ax_bz.tick_params(labelsize=7)
    ax_bz.set_title('Brillouin zone', fontsize=9)
    plt.tight_layout()
    st.pyplot(fig_bz)
    plt.close(fig_bz)

# ── Band structure viewer ─────────────────────────────────────────────────────

with col_band:
    st.subheader('Band structure')

    hdr_col, btn_col = st.columns([5, 1])
    with btn_col:
        if st.button('↺ Refresh'):
            st.rerun()

    npz_files = (
        sorted(RESULTS_DIR.glob('phononic_band_*.npz'),
               key=lambda p: p.stat().st_mtime, reverse=True)
        if RESULTS_DIR.exists() else []
    )

    if not npz_files:
        st.info('No results yet — pull .npz files into results/ and hit Refresh.')
    else:
        with hdr_col:
            chosen = st.selectbox('Result file', [p.name for p in npz_files],
                                  label_visibility='collapsed')
        chosen_path = RESULTS_DIR / chosen
        data        = np.load(chosen_path, allow_pickle=True)

        freqs    = data['freqs_GHz']
        k_dist   = data['k_dist']
        tick_idx = data['tick_idx']
        tick_lbl = [str(s).replace('G', 'Γ') for s in data['tick_lbl']]
        tick_x   = k_dist[tick_idx]

        # Detect complete bandgaps
        gaps = []
        for b in range(freqs.shape[1] - 1):
            f_top = np.nanmax(freqs[:, b])
            f_bot = np.nanmin(freqs[:, b + 1])
            if f_bot > f_top:
                fc    = 0.5 * (f_top + f_bot)
                gfrac = (f_bot - f_top) / fc
                if gfrac > 0.02:
                    gaps.append((f_top, f_bot, gfrac))

        fig_bs, ax_bs = plt.subplots(figsize=(6.5, 5))
        for mi in range(freqs.shape[1]):
            ax_bs.plot(k_dist, freqs[:, mi], color='steelblue', lw=0.9, alpha=0.8)
        for fl, fu, _ in gaps:
            ax_bs.axhspan(fl, fu, color='tomato', alpha=0.18)
        for xv in tick_x:
            ax_bs.axvline(xv, color='gray', lw=0.5, ls='--')
        ax_bs.set_xticks(tick_x)
        ax_bs.set_xticklabels(tick_lbl, fontsize=11)
        ax_bs.set_xlabel('Wavevector', fontsize=11)
        ax_bs.set_ylabel('Frequency (GHz)', fontsize=11)
        ax_bs.set_xlim(k_dist[0], k_dist[-1])
        ax_bs.set_ylim(0)
        ax_bs.grid(alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig_bs)
        plt.close(fig_bs)

        if gaps:
            st.markdown('**Complete bandgaps:**')
            for fl, fu, gf in gaps:
                st.markdown(
                    f'- {fl:.3f}–{fu:.3f} GHz &nbsp;·&nbsp; '
                    f'center {0.5*(fl+fu):.3f} GHz &nbsp;·&nbsp; '
                    f'gap/midgap {gf*100:.1f}%'
                )
        else:
            st.caption('No complete bandgap (gap/midgap > 2%) found.')

        mtime = chosen_path.stat().st_mtime
        st.caption(f'{chosen}  ·  {time.strftime("%Y-%m-%d %H:%M", time.localtime(mtime))}')

# ── Run configuration ─────────────────────────────────────────────────────────

with st.expander('Run configuration'):
    st.markdown('Paste into the **PARAMETERS** block of `scripts/phononic_band.py`:')
    st.code(
        f'a  = {a_nm}e-9    # lattice constant [m]\n'
        f'd  = {d_nm:.1f}e-9    # slab thickness [m]  (d/a = {da:.2f})\n'
        f'r  = {r_nm:.1f}e-9    # hole radius [m]     (r/a = {ra:.2f})\n'
        f'\n'
        f'n_seg         = {n_seg}\n'
        f'n_modes       = {n_modes}\n'
        f'eig_shift_GHz = {eig_shift_GHz}',
        language='python',
    )
    st.markdown('Run command (from project root, after filling in SSH details):')
    st.code('python scripts/remote_runner.py scripts/phononic_band.py', language='bash')
