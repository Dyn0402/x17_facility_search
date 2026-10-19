#!/usr/bin/env python3
"""
nfs_fold.py -- gate 2 of PLAN_GANIL_NFS.md: the NFS neutron spectrum folded
against ³He(n,γ)⁴He, per neutron energy, for the baseline cell.

    python nfs_fold.py            # tables + figures into ganil_nfs/out/

What it computes, all at the NFS 0° direction:

* neutrons per second per MeV through the cell: Y(E_n) [n/µC/sr/MeV] × I × Ω.
  The cell (R = 50 mm) is wider than the collimated beam wherever we would
  sit (8 cm spot at 13.6 m), so the rate is set by the collimator's solid
  angle Ω and does not depend on the flight path;
* radiative captures: × n·L × σ_nγ(E_n) (ENDF/B in MX17_Full_Geant/data/He3.h5),
  with the cell's own attenuation;
* IPC pairs: × α_pair(E1, W), the Born pairs-per-photon at W = E*(E_n)
  (nTof_x17 ipc_born); fast capture is E1 (thermal capture is M1);
* the X17 kinematic edge θ_min(E_n) = 2 asin(m_X / E_X), and the ⁴He levels
  the capture runs through.

Also a deuteron-energy scan: the same d+Be model at lower E_d, with the
40 MeV data normalisation (×1.293) carried over.  That carry-over is a
model assumption -- only the 40 MeV spectrum has been measured.

Rates assume 50 µA (the NFS maximum).  What current survives at the low
repetition rate we need is question Q3 in ganil_nfs/README.md §10 (ask).
"""
from __future__ import annotations

import sys
from pathlib import Path

import h5py
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'ill'))
sys.path.insert(0, str(Path.home() / 'PycharmProjects/nTof_x17'))
import nfs_beam as nb                                            # noqa: E402

OUT = HERE / 'out'
H5 = Path.home() / 'CLionProjects/MX17_Full_Geant/data/He3.h5'

S_N = 20.577                 # MeV, ³He + n separation in ⁴He
M_N, M_HE3, M_HE4 = 939.56542, 2808.39161, 3727.379
M_X = 16.8
I_UA = 50.0                  # µA, NFS maximum (current at low rep rate: ask)
OMEGA = nb.SOLID_ANGLE_AT_740      # sr, measured beam solid angle (25.55 mm collimator)
# baseline cell, PLAN §4.4 build C
P_BAR, L_CM, T_K = 30.0, 40.0, 293.15
N_HE3 = P_BAR * 1e5 / (1.380649e-23 * T_K) * 1e-6      # /cm³
NL = N_HE3 * L_CM                                        # /cm²
DAY = 86400.0
# ILL reference: radiative captures/s with today's PF1B beam (ill/FEASIBILITY_SIM.md §13)
ILL_ABSORBED = 1.9e10
ILL_GAMMA_PER_ABS = 1.03e-8

# ⁴He levels above the n+³He threshold (Tilley, Weller & Hale, NPA 541 (1992) 1, Table 4.2):
# (E_x MeV, J^π; T, Γ MeV)
HE4_LEVELS = [(21.01, '0⁻', 0.84), (21.84, '2⁻', 2.01), (23.33, '2⁻ T=1', 5.01),
              (23.64, '1⁻ T=1', 6.20), (24.25, '1⁻', 6.10), (25.28, '0⁻ T=1', 7.97),
              (25.95, '1⁻ T=1', 12.66), (28.31, '1⁺', 9.89), (28.37, '1⁻', 3.92),
              (28.39, '2⁻', 8.75), (28.64, '0⁻', 4.89), (28.67, '2⁺', 3.78)]

WINDOWS = [(0.2, 1.0), (0.2, 2.0), (2.0, 5.0), (5.0, 10.0), (10.0, 20.0), (20.0, 40.0), (0.2, 40.0)]


def w_of_en(e_n):
    """⁴He* excitation W = √s − m(⁴He) for n + ³He at rest."""
    s = (M_N + M_HE3) ** 2 + 2 * M_HE3 * np.asarray(e_n)
    return np.sqrt(s) - M_HE4


def beta_cm(e_n):
    e_n = np.asarray(e_n)
    return np.sqrt(e_n * (e_n + 2 * M_N)) / (e_n + M_N + M_HE3)


def theta_min_deg(e_n, m_x=M_X):
    """X17 edge for the X17 emitted perpendicular to the beam (E_X at rest in the CM)."""
    w = w_of_en(e_n)
    e_x = (w ** 2 + m_x ** 2 + 2 * w * M_HE4) / (2 * (w + M_HE4))   # two-body, ⁴He* at rest
    return np.degrees(2 * np.arcsin(m_x / e_x))


def endf(mt):
    f = h5py.File(H5)['He3']
    e = f['energy/294K'][:] * 1e-6                        # MeV
    xs = f[f'reactions/reaction_{mt:03d}/294K/xs']
    th = xs.attrs.get('threshold_idx', 0)
    v = xs[:]
    return e[th:th + len(v)], v


def sigma(e_n, mt):
    """ENDF cross section, b.  Above 20 MeV (end of the evaluation) ∝ 1/E_n -- a stand-in."""
    e, v = endf(mt)
    s = np.interp(e_n, e, v, left=0.0, right=np.nan)
    hi = e_n > e[-1]
    s[hi] = v[-1] * e[-1] / e_n[hi]
    return s


def alpha_e1(w):
    from sept26_prelim_analysis import ipc_born
    return np.array([ipc_born.alpha_pair('E1', float(x)) for x in np.atleast_1d(w)])


def fold(e_n, e_d0=40.0, scale=None):
    """Per-MeV rates through the cell, /s/MeV."""
    if scale is None:
        scale = nb.absolute_scale(40.0)
    tot, comp = nb.thick_target_yield(e_n, e_d0=e_d0, components=True)
    y, y_lo = tot * scale, comp['compound'] * scale
    y_lo = np.where(e_n < 1.5, y_lo, y)            # unvalidated below 1.5 MeV: band down to compound only
    n_s = y * I_UA * OMEGA
    s_ng = sigma(e_n, 102) * 1e-24
    s_tot = (sigma(e_n, 2) + sigma(e_n, 103) + sigma(e_n, 104) + sigma(e_n, 102)) * 1e-24
    x = NL * s_tot
    att = (1 - np.exp(-x)) / np.where(x > 0, x, 1)
    cap = n_s * NL * s_ng * att
    return pd.DataFrame(dict(E_n=e_n, Y_n_uC_sr_MeV=y, Y_low=y_lo, n_per_s_MeV=n_s,
                             sigma_ng_ub=s_ng * 1e30, sigma_tot_b=s_tot * 1e24, att=att,
                             cap_per_s_MeV=cap, cap_low_per_s_MeV=cap * y_lo / y))


def main():
    OUT.mkdir(exist_ok=True)
    e_n = np.unique(np.concatenate([np.geomspace(0.1, 2, 80), np.linspace(2, 40, 153)]))
    d = fold(e_n)
    d.insert(1, 'W_MeV', w_of_en(e_n))
    d.insert(2, 'beta_cm', beta_cm(e_n))
    d.insert(3, 'theta_min_deg', theta_min_deg(e_n))
    a = alpha_e1(d.W_MeV.values)
    d['alpha_E1'] = a
    d['ipc_per_s_MeV'] = d.cap_per_s_MeV * a
    d['ipc_low_per_s_MeV'] = d.cap_low_per_s_MeV * a
    d.to_csv(OUT / 'fold_table.csv', index=False, float_format='%.5g')

    ill = ILL_ABSORBED * ILL_GAMMA_PER_ABS
    rows = []
    for lo, hi in WINDOWS:
        m = (d.E_n >= lo) & (d.E_n <= hi)
        g = lambda c: float(np.trapezoid(d[c][m], d.E_n[m]))           # noqa: E731
        rows.append(dict(window=f'{lo:g}-{hi:g}', neutrons_per_s=g('n_per_s_MeV'),
                         captures_per_s=g('cap_per_s_MeV'), captures_per_s_low=g('cap_low_per_s_MeV'),
                         ipc_per_day=g('ipc_per_s_MeV') * DAY, ipc_per_day_low=g('ipc_low_per_s_MeV') * DAY,
                         vs_ILL_captures=g('cap_per_s_MeV') / ill,
                         theta_min_range=f'{theta_min_deg(hi):.0f}-{theta_min_deg(lo):.0f}'))
    win = pd.DataFrame(rows)
    win.to_csv(OUT / 'fold_windows.csv', index=False, float_format='%.4g')

    # deuteron-energy scan, the 40 MeV data normalisation carried over
    sc = nb.absolute_scale(40.0)
    srows = []
    grid = np.linspace(0.2, 2.0, 37)
    for ed in (10, 15, 20, 25, 30, 35, 40):
        f = fold(np.unique(np.concatenate([grid, np.linspace(2, ed + 5, 80)])), e_d0=ed, scale=sc)
        m = f.E_n <= 2.0
        tot = float(np.trapezoid(f.n_per_s_MeV, f.E_n))
        low = float(np.trapezoid(f.n_per_s_MeV[m], f.E_n[m]))
        caplow = float(np.trapezoid(f.cap_per_s_MeV[m], f.E_n[m]))
        cap = float(np.trapezoid(f.cap_per_s_MeV, f.E_n))
        srows.append(dict(E_d_MeV=ed, beam_power_kW_at_50uA=ed * I_UA * 1e-3,
                          n_per_s_all=tot, n_per_s_0p2_2=low, frac_0p2_2=low / tot,
                          captures_per_s_0p2_2=caplow, captures_per_s_all=cap))
    scan = pd.DataFrame(srows)
    scan.to_csv(OUT / 'ed_scan.csv', index=False, float_format='%.4g')

    print(f'cell: {P_BAR:g} bar × {L_CM:g} cm, n·L = {NL:.3g} /cm²;  beam {I_UA:g} µA × Ω = {OMEGA:.3g} sr')
    print(f'ILL radiative captures/s (1.9e10 absorbed): {ill:.0f}')
    print(win.to_string(index=False))
    print(scan.to_string(index=False))
    figures(d, win, scan)


def figures(d, win, scan):
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use()

    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(6.8, 6.4), sharex=True,
                                  gridspec_kw=dict(height_ratios=[3, 2], hspace=0.08))
    ax.fill_between(d.E_n, d.cap_low_per_s_MeV * DAY, d.cap_per_s_MeV * DAY, color=fs.ACCENT, alpha=0.2, lw=0)
    ax.plot(d.E_n, d.cap_per_s_MeV * DAY, color=fs.ACCENT, lw=1.6, label='³He(n,γ) per day per MeV')
    ax.plot(d.E_n, d.ipc_per_s_MeV * DAY * 100, color=fs.COPPER, lw=1.2, ls='--',
            label='IPC e⁺e⁻ pairs per day per MeV × 100')
    ax.axvspan(0.1, 1.5, color=fs.BAND_DEAD, alpha=0.06, lw=0)
    ax.text(0.12, 1e7, 'spectrum\nunmeasured', color=fs.BAND_DEAD, fontsize=8)
    ax.set_yscale('log')
    ax.set_ylim(1e3, 3e7)
    ax.set_ylabel('per day per MeV')
    ax.legend(loc='lower left', fontsize=8, frameon=False, bbox_to_anchor=(0.25, 0.0))
    fs.title(ax, 'NFS d(40)+Be on a 30 bar × 40 cm ³He cell, 50 µA',
             'band below 1.5 MeV: total model down to its compound part')
    for ex, jp, _ in HE4_LEVELS[:2] + HE4_LEVELS[4:5]:
        en = (ex - S_N) / 0.75
        ax.axvline(en, color=fs.LINE, lw=0.7)
        ax.text(en, 2.5e7, jp, rotation=90, fontsize=7, color=fs.MUTED, ha='right', va='top')
    ax2.plot(d.E_n, d.theta_min_deg, color=fs.INK, lw=1.4)
    ax2.set_ylabel('X17 edge θ_min [°]')
    ax2.set_xlabel('neutron energy E_n [MeV]  (TOF-tagged per event)')
    ax2.set_xscale('log')
    ax2.set_xlim(0.1, 40)
    out = d[['E_n', 'W_MeV', 'theta_min_deg', 'cap_per_s_MeV', 'cap_low_per_s_MeV', 'ipc_per_s_MeV']]
    fs.save(fig, OUT / 'fold_vs_En', data=out)

    fig, ax = fs.figure()
    ax.plot(scan.E_d_MeV, scan.captures_per_s_0p2_2 * DAY, 'o-', color=fs.ACCENT, label='0.2–2 MeV')
    ax.plot(scan.E_d_MeV, scan.captures_per_s_all * DAY, 's-', color=fs.COPPER, label='all E_n')
    ax.set_yscale('log')
    ax.set_xlabel('deuteron energy E_d [MeV]  (thick Be, 50 µA)')
    ax.set_ylabel('³He(n,γ) per day')
    ax.legend(frameon=False)
    fs.title(ax, 'Lowering E_d does not buy sub-2 MeV neutrons',
             'model at every E_d, the 40 MeV data normalisation carried over')
    fs.save(fig, OUT / 'ed_scan', data=scan)


if __name__ == '__main__':
    main()
