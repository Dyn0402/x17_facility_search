#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lnl_week.py -- one week of beam, as measured: can the smeared X17 be seen?

    python lnl/sim/lnl_week.py        # -> lnl/out/scatter/week*.csv, figures/scatter_week.png

Reads lnl/out/scatter/stacked.csv (lnl_scatter.py: per day at 1 µA, big plastics,
MM 15° + TOF, IPC γ₀ + γ₁ and X17 at R(ATOMKI), truth and reco angle) and the
reach rows of lnl/out/geant/reach_geant.csv. No Geant4 tables needed.

  week.csv     4° bins, 7 live-corrected days: IPC expectation (5° Gaussian
               smoothing of the MC, as the reach templates; KDE_BW_DEG in
               lnl_geant.py), X17 truth and measured, one Poisson pseudo-experiment.
  week_z.csv   significance against time for the three reach methods (Asimov,
               Z ∝ √t), and the counting Z when the IPC shape under the window
               is uncertain by ε (relative to the sidebands): Z = S/√(B + ε²B²).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
LNL = HERE.parent
OUT = LNL / 'out' / 'scatter'
FIGS = OUT / 'figures'
DAYS = 7.0
BW = 5.0                        # lnl_geant.KDE_BW_DEG
SEED = 17


def smooth(x, y, bw=BW):
    """Gaussian smoothing of a binned spectrum, reflected at 180° (sum kept)."""
    xx = np.r_[x, 360 - x]
    yy = np.r_[y, y]
    k = np.exp(-0.5 * ((x[:, None] - xx[None, :]) / bw) ** 2)
    k /= k.sum(1, keepdims=True)
    s = k @ yy
    return s * y.sum() / s.sum()


def main():
    sk = pd.read_csv(OUT / 'stacked.csv')
    r = pd.read_csv(LNL / 'out' / 'geant' / 'reach_geant.csv')
    r = r[(r.scenario == 'ATOMKI 2016 anomaly') & (r.I_uA == 1.0) & (r.mass == 16.7) & (r.hw == 'big plastics')
          & (r.level == 'MM 15° + TOF')].iloc[0]
    live = r.live
    x2 = sk.theta_lo.values + 1.0
    ipc = smooth(x2, sk.ipc_reco.values)
    # 2° -> 4° bins
    e4 = np.arange(90, 181, 4.0)
    def rb(v):
        return np.array([v[(sk.theta_lo >= a) & (sk.theta_lo < a + 4)].sum() for a in e4[:-1]])
    f = DAYS * live
    B, St, Sr = f * rb(ipc), f * rb(sk.x17_truth.values), f * rb(sk.x17_reco.values)
    Braw = f * rb(sk.ipc_reco.values)
    rng = np.random.default_rng(SEED)
    N = rng.poisson(B + Sr)
    wk = pd.DataFrame(dict(theta_lo=e4[:-1], theta_hi=e4[1:], ipc_exp=B, ipc_mc_unsmoothed=Braw, x17_truth=St,
                           x17_reco=Sr, pseudo_data=N, resid=N - B, resid_err=np.sqrt(np.maximum(N, 1))))
    wk['note'] = (f'{DAYS:.0f} days x live {live:.3f}, 1 µA, Li2O 300 µg/cm2 at 1.10 MeV, big plastics, MM 15° + TOF, '
                  f'E_sum {r.esum}; IPC γ0+γ1 smoothed {BW:.0f}° (MC noise); one Poisson toy, seed {SEED}')
    wk.to_csv(OUT / 'week.csv', index=False)

    # the counting window of the reach (win_opt) on the 2° stacked bins
    lo, hi = (float(v) for v in r.win_opt.split('-'))
    w2 = (sk.theta_lo >= lo) & (sk.theta_lo < hi)
    s1 = live * sk.x17_reco[w2].sum()
    b1 = live * ipc[w2.values].sum()
    in_w = (e4[:-1] >= lo) & (e4[:-1] < hi)
    z_toy = (N[in_w].sum() - B[in_w].sum()) / np.sqrt(B[in_w].sum())
    rows = []
    for t in (1, 3, 7, 14):
        row = dict(days=t,
                   z_count_known_B=3 * np.sqrt(t / r.days_count_opt_live),
                   z_fit_ipc_norm_free=3 * np.sqrt(t / r.days_fisher_1norm_live),
                   z_fit_m1_e1_g1_free=3 * np.sqrt(t / r.days_fisher_live))
        for eps in (0.01, 0.02, 0.05):
            S, Bt = t * s1, t * b1
            row[f'z_count_shape_{eps * 100:.0f}pct'] = S / np.sqrt(Bt + (eps * Bt) ** 2)
        rows.append(row)
    z = pd.DataFrame(rows)
    z['S_per_day'] = s1
    z['B_per_day'] = b1
    z['window'] = r.win_opt
    z['z_toy_week'] = z_toy
    z['days_count'] = r.days_count_opt_live
    z['days_fit_1norm'] = r.days_fisher_1norm_live
    z['days_fit_free'] = r.days_fisher_live
    z.to_csv(OUT / 'week_z.csv', index=False)
    print(wk.drop(columns='note').to_string(index=False, float_format=lambda v: f'{v:.1f}'))
    print(z.to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    figure(wk, z)
    return 0


def figure(wk, z):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    sys.path.insert(0, str(LNL.parent / 'ill'))
    import figstyle as fs
    fs.use()
    fig, (a, b) = plt.subplots(2, 1, figsize=(7.0, 6.0), sharex=True, gridspec_kw=dict(height_ratios=[2, 1.3]))
    x = 0.5 * (wk.theta_lo + wk.theta_hi)
    a.step(x, wk.ipc_exp, where='mid', color=fs.MUTED, lw=1.4, label='IPC expectation (γ₀ + γ₁)')
    a.step(x, wk.ipc_exp + wk.x17_reco, where='mid', color='#d64545', lw=1.4, label='IPC + X17 at R(ATOMKI), measured')
    a.errorbar(x, wk.pseudo_data, yerr=np.sqrt(wk.pseudo_data), fmt='o', ms=3, color=fs.INK, label='one pseudo-experiment')
    a.set_ylabel('pairs per week / 4°')
    a.legend(frameon=False, fontsize=7)
    b.axhline(0, color=fs.MUTED, lw=0.8)
    b.step(x, wk.x17_truth, where='mid', color='#009E73', lw=1.2, ls='--', label='X17, truth angle')
    b.step(x, wk.x17_reco, where='mid', color='#d64545', lw=1.6, label='X17, measured (CFRP chamber)')
    b.errorbar(x, wk.resid, yerr=wk.resid_err, fmt='o', ms=3, color=fs.INK, label='pseudo-data − IPC')
    b.set_xlabel('e⁺e⁻ opening angle [deg]')
    b.set_ylabel('per week / 4°')
    b.set_xlim(90, 180)
    b.legend(frameon=False, fontsize=7)
    zz = z.set_index('days')
    fs.fig_title(fig, 'One week at 1 µA, as measured: the smeared X17 on the IPC',
                 f'Big plastics, MM 15° + TOF. Counting Z in {z.window.iloc[0]}°: '
                 f'{zz.z_count_known_B[7]:.1f}σ (Asimov, B known), toy {z.z_toy_week.iloc[0]:.1f}σ; '
                 f'fit with M1/E1/γ₁ free {zz.z_fit_m1_e1_g1_free[7]:.1f}σ')
    fs.save(fig, FIGS / 'scatter_week', data=wk)


if __name__ == '__main__':
    raise SystemExit(main())
