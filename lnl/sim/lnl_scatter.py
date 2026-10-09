#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lnl_scatter.py -- how much the target region widens the X17 peak at LNL.

    python lnl/sim/lnl_scatter.py        # -> lnl/out/scatter/*.csv, figures

The LNL counterpart of the n_TOF capsule "dilution" figure
(MX17_Full_Geant docs/angular_resolution: truth vs smeared opening angle).
Here the beam is in vacuum: the leptons cross a 0.4 mm CFRP chamber tube
(r = 25 mm), not a 500 bar ³He capsule.

  widen.csv     X17 (m = 16.7, 18.15 MeV) opening angle, normalised, for the SAME
                selected events: Geant4 truth (no scattering, perfect detector)
                against the reconstructed chord (beam spot -> MM centroid) with
                the CFRP 0.4 mm chamber (Geant4 L1, big plastics, the reference
                selection), with Al 0.5 / 1.0 mm tubes (Geant4 L5, as built,
                trigger level), plus two Gaussian illustrations: the no-wall
                floor of the appendix model and the n_TOF capsule's 14.5°.
  stacked.csv   per day at 1 µA, big plastics, the reference selection: IPC (γ₀ +
                γ₁) and the X17 at R(ATOMKI), in truth and reconstructed angle.
  cost.csv      what the smearing costs: counting days in the best window,
                truth against reconstructed (same S, B normalisation).
  budget.csv    Highland budget, layer by layer, along one lepton's path: θ₀ at
                8.6 MeV, the lever (L − r)/L that turns a kink into a chord-angle
                error, and the contribution to σ68 with the k of the appendix model
                (fitted to the Geant4 L5 walls).  n_TOF capsule row for scale.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
LNL = HERE.parent
sys.path.insert(0, str(HERE))
import lnl_geant as LG          # noqa: E402

OUT = LNL / 'out' / 'scatter'
FIGS = OUT / 'figures'
REF_EC = None                   # filled from reach_geant.csv (big plastics, reference level)
B1 = np.arange(90, 181, 1.0)
B2 = np.arange(90, 181, 2.0)
RES: dict = {}
S68_NTOF = 14.5                 # n_TOF capsule, CLAUDE.md / angular_resolution_note.md


def ref_ecut(hw):
    r = pd.read_csv(LNL / 'out' / 'geant' / 'reach_geant.csv')
    r = r[(r.scenario == 'ATOMKI 2016 anomaly') & (r.I_uA == 1.0) & (r.mass == 16.7) & (r.hw == hw)
          & (r.level == LG.REF_LEVEL)].iloc[0]
    return (int(r.e_lo), int(r.e_hi)), r


def s68(d):
    q = np.percentile(d, [16, 50, 84])
    return 0.5 * (q[2] - q[0]), q[1]


def widen():
    rng = np.random.default_rng(4)
    ec, _ = ref_ecut('big plastics')
    rows, stats = [], []

    def add(label, x, kind):
        h, _ = np.histogram(x, B1)
        h = h / max(h.sum(), 1)
        rows.extend(dict(curve=label, kind=kind, theta_lo=B1[i], frac_per_deg=h[i]) for i in range(len(h)))

    z = LG.load('L1', 'X17_m16.7', 'big plastics')
    m = LG.select(z, LG.REF_LEVEL, ec) & z['truth_arms'].astype(bool)
    th, rc = z['theta'][m], z['reco_c'][m]
    add('truth (no scattering)', th, 'geant')
    add('CFRP 0.4 mm chamber (baseline)', rc, 'geant')
    sg, bias = s68(rc - th)
    stats.append(dict(curve='CFRP 0.4 mm chamber (baseline)', source=f'Geant4 L1 big plastics, {LG.REF_LEVEL}, E_sum {LG.ewin(ec)}',
                      n=int(m.sum()), sigma68=sg, bias=bias))
    hl = pd.read_csv(LNL / 'out' / 'appendix' / 'highland.csv')
    floor = hl.s0_deg.iloc[0]
    RES['no wall (model floor)'] = floor
    RES['n_TOF ³He capsule (σ68 14.5°)'] = S68_NTOF
    add('no wall (model floor)', th + rng.normal(0, floor, len(th)), 'model')
    stats.append(dict(curve='no wall (model floor)', source='appendix Highland model s0, Gaussian', n=int(m.sum()),
                      sigma68=floor, bias=0.0))
    add('n_TOF ³He capsule (σ68 14.5°)', th + rng.normal(0, S68_NTOF, len(th)), 'model')
    stats.append(dict(curve='n_TOF ³He capsule (σ68 14.5°)', source='n_TOF σ68, Gaussian on the LNL truth', n=int(m.sum()),
                      sigma68=S68_NTOF, bias=0.0))
    # Al tubes: the Geant4 L5 residuals (reco - truth, as built, trigger level) applied
    # to the same big-plastic events, so the selection does not change the shape
    for tag, lab in (('chAl0.5', 'Al 0.5 mm chamber'), ('chAl1', 'Al 1.0 mm chamber')):
        z = LG.load('L5', f'X17_m16.7_{tag}')
        m5 = LG.select(z, 'trigger', (0, 99)) & z['truth_arms'].astype(bool)
        res = (z['reco_c'] - z['theta'])[m5]
        x = th + rng.choice(res, len(th))
        x = np.where(x > 180, 360 - x, x)
        add(lab, x, 'geant residuals')
        sg, bias = s68(res)
        stats.append(dict(curve=lab, source='Geant4 L5 residuals (as built, trigger) on the same events', n=int(m5.sum()),
                          sigma68=sg, bias=bias))
        RES[lab] = res
    w = pd.DataFrame(rows)
    st = pd.DataFrame(stats)
    # share of the X17 inside 125-155 and the sharpest 10° (peak height)
    for c in w.curve.unique():
        g = w[w.curve == c]
        x = g.theta_lo.values
        f = g.frac_per_deg.values
        st.loc[st.curve == c, 'frac_125_155'] = f[(x >= 125) & (x < 155)].sum()
        st.loc[st.curve == c, 'peak_frac_per_deg'] = np.convolve(f, np.ones(3) / 3, 'same').max()
    t = w[w.curve == 'truth (no scattering)']
    st = pd.concat([pd.DataFrame([dict(curve='truth (no scattering)', source='Geant4 truth, same events', n=st.n.iloc[0],
                                       sigma68=0.0, bias=0.0,
                                       frac_125_155=t[(t.theta_lo >= 125) & (t.theta_lo < 155)].frac_per_deg.sum(),
                                       peak_frac_per_deg=np.convolve(t.frac_per_deg, np.ones(3) / 3, 'same').max())]), st])
    return w, st


def stacked():
    """Per day, big plastics, reference selection: truth and reco spectra."""
    ec, rr = ref_ecut('big plastics')
    y = pd.read_csv(LNL / 'out' / 'yields.csv').set_index('scenario').loc['ATOMKI 2016 anomaly']
    a = pd.read_csv(LNL / 'out' / 'ipc_alpha.csv').set_index(['W_MeV', 'multipole']).alpha_pair
    ng0 = rr.N_g0          # γ₀ per day at 1 µA
    f17, fr, fd = y.frac_17_64, y.frac_18_15_res, y.frac_direct
    g1r = y.Y_g1 / y.Y_g0
    wts = {('L2', 'M1_17.64'): f17 * a[(17.64, 'M1')], ('L2', 'M1_18.15'): fr * a[(18.15, 'M1')],
           ('L2', 'E1_18.15'): fd * a[(18.15, 'E1')],
           ('L2', 'M1_15.1'): g1r * (1 - y.frac_g1_direct) * a[(15.1, 'M1')],
           ('L2', 'E1_15.1'): g1r * y.frac_g1_direct * a[(15.1, 'E1')]}
    out = {}
    for var in ('theta', 'reco_c'):
        b = np.zeros(len(B2) - 1)
        for (run, s), wt in wts.items():
            z = LG.load(run, s, 'big plastics')
            m = LG.select(z, LG.REF_LEVEL, ec)
            h, _ = np.histogram(z[var][m], B2)
            b += ng0 * wt * h / z['ngen']
        z = LG.load('L1', 'X17_m16.7', 'big plastics')
        m = LG.select(z, LG.REF_LEVEL, ec)
        h, _ = np.histogram(z[var][m], B2)
        s = ng0 * LG.LR.R_ATOMKI_2016 * (1 - f17) * h / z['ngen']
        out[var] = (b, s)
    # the same truth events smeared by each wall's residuals (Gaussian for the model rows)
    rng = np.random.default_rng(8)
    for lab, r in RES.items():
        def sm(x):
            d = rng.normal(0, r, len(x)) if np.isscalar(r) else rng.choice(r, len(x))
            y_ = x + d
            return np.where(y_ > 180, 360 - y_, y_)
        b = np.zeros(len(B2) - 1)
        for (run, s_), wt in wts.items():
            z = LG.load(run, s_, 'big plastics')
            m = LG.select(z, LG.REF_LEVEL, ec)
            h, _ = np.histogram(sm(z['theta'][m]), B2)
            b += ng0 * wt * h / z['ngen']
        z = LG.load('L1', 'X17_m16.7', 'big plastics')
        m = LG.select(z, LG.REF_LEVEL, ec)
        h, _ = np.histogram(sm(z['theta'][m]), B2)
        out[lab] = (b, ng0 * LG.LR.R_ATOMKI_2016 * (1 - f17) * h / z['ngen'])
    rows = [dict(theta_lo=B2[i], ipc_truth=out['theta'][0][i], x17_truth=out['theta'][1][i],
                 ipc_reco=out['reco_c'][0][i], x17_reco=out['reco_c'][1][i]) for i in range(len(B2) - 1)]
    st = pd.DataFrame(rows)
    # counting cost: best window (>= 10° wide), days ∝ B/S², same normalisation
    cost = []
    cases = [('truth (no scattering)', out['theta']), ('CFRP 0.4 mm chamber, Geant4 reco', out['reco_c'])]
    cases += [(k + (' (Gaussian)' if np.isscalar(RES[k]) else ' (L5 residuals)'), out[k]) for k in RES]
    for lab, (b, s) in cases:
        cs, cb = np.r_[0, np.cumsum(s)], np.r_[0, np.cumsum(b)]
        best = (0, None)
        for i in range(len(s)):
            for j in range(i + 5, len(s) + 1):
                bb = cb[j] - cb[i]
                if bb > 0 and (cs[j] - cs[i]) / math.sqrt(bb) > best[0]:
                    best = ((cs[j] - cs[i]) / math.sqrt(bb), (B2[i], B2[j]))
        z1 = best[0]                         # significance in one day
        cost.append(dict(case=lab, window=f'{best[1][0]:.0f}-{best[1][1]:.0f}', z_1day=z1, days_3sigma=9 / z1 ** 2))
    cost = pd.DataFrame(cost)
    cost['ratio_to_truth'] = cost.days_3sigma / cost.days_3sigma.iloc[0]
    cost['days_anchored'] = cost.ratio_to_truth / cost.ratio_to_truth.iloc[1] * rr.days_count_opt_live
    cost['note'] = (f'big plastics, {LG.REF_LEVEL}, E_sum {LG.ewin(ec)}; IPC γ₀+γ₁ only (cosmics, EPC < 1 %); '
                    'counting, best window on 2° bins; Geant4 MC statistics, no KDE')
    return st, cost


def budget():
    """Highland per layer for one 8.6 MeV lepton leaving at 90° to the beam."""
    hl = pd.read_csv(LNL / 'out' / 'appendix' / 'highland.csv')
    k = hl.k.iloc[0]
    L = 215.0                                         # appendix_calc.L_MM (the model's calibration)
    P = 8.6
    x0 = {'CFRP': 42.7 / 1.55, 'Al': 8.897, 'Mylar': 28.54, 'Kapton': 28.57, 'Cu': 1.436,
          'air': 30390.0, 'Ar/iC4H10': 11760.0 * 1.0}
    layers = [('Al backing, 10 µm (only for backward leptons, oblique)', 'Al', 0.010 * 2, 0.0),
              ('CFRP chamber tube, 0.4 mm', 'CFRP', 0.4, 25.0),
              ('air, chamber to MM window (179 mm)', 'air', 179.0, 114.5),
              ('MM window, 60 µm aluminised mylar', 'Mylar', 0.060, 204.0),
              ('MM cathode, 50 µm Kapton + 9 µm Cu', None, None, 209.0),
              ('drift gas to mid-gap (15 mm)', 'Ar/iC4H10', 15.0, 212.0)]
    rows = []
    for name, mat, t_mm, r in layers:
        if mat is None:
            xx = 0.050 / 10 / x0['Kapton'] + 0.009 / 10 / x0['Cu']
        else:
            xx = t_mm / 10 / x0[mat]
        th = math.degrees(13.6 / P * math.sqrt(xx) * (1 + 0.038 * math.log(xx)))
        if name.startswith('air'):
            # distributed scatterer: rms lever over r in [25, 204]
            rs = np.linspace(25, 204, 400)
            lever = float(np.sqrt(np.mean(((L - rs) / L) ** 2)))
        else:
            lever = (L - r) / L
        rows.append(dict(layer=name, x_over_X0=xx, theta0_deg=th, lever=lever, chord_deg=th * lever,
                         sigma68_term_deg=k * th * lever))
    # n_TOF for scale: 0.6 mm Al + 0.9 mm CFRP at r ~ 11 mm (angular_resolution_note.md)
    xx = 0.06 / x0['Al'] + 0.09 / x0['CFRP']
    th = math.degrees(13.6 / P * math.sqrt(xx) * (1 + 0.038 * math.log(xx)))
    rows.append(dict(layer='n_TOF: ³He capsule wall, 0.6 mm Al + 0.9 mm CFRP (for scale)', x_over_X0=xx, theta0_deg=th,
                     lever=(L - 11) / L, chord_deg=th * (L - 11) / L, sigma68_term_deg=k * th * (L - 11) / L))
    b = pd.DataFrame(rows)
    b['k_model'] = k
    b['s0_floor_deg'] = hl.s0_deg.iloc[0]
    return b


def figures(w, st, sk, cost, bud):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    sys.path.insert(0, str(LNL.parent / 'ill'))
    import figstyle as fs
    fs.use()
    sty = {'truth (no scattering)': ('#009E73', '-', 2.0),
           'no wall (model floor)': ('#56B4E9', ':', 1.6),
           'CFRP 0.4 mm chamber (baseline)': (fs.ACCENT, '-', 2.0),
           'Al 0.5 mm chamber': ('#E69F00', '--', 1.4),
           'Al 1.0 mm chamber': ('#D55E00', '--', 1.4),
           'n_TOF ³He capsule (σ68 14.5°)': (fs.MUTED, '-.', 1.4)}
    fig, axs = plt.subplots(1, 3, figsize=(13.5, 4.0))
    ax = axs[0]
    for c, (col, ls, lw) in sty.items():
        g = w[w.curve == c]
        s = st[st.curve == c].iloc[0]
        lab = c if c.startswith(('truth', 'n_TOF')) else f'{c}: σ68 {s.sigma68:.1f}°'
        ax.step(g.theta_lo + 0.5, g.frac_per_deg, where='mid', color=col, ls=ls, lw=lw, label=lab)
    ax.set_xlim(100, 180)
    ax.set_xlabel('e⁺e⁻ opening angle [deg]')
    ax.set_ylabel('X17 pairs, normalised / 1°')
    ax.legend(frameon=False, fontsize=7, loc='upper left')
    ax.set_title('X17 alone (m 16.7): truth vs measured', fontsize=9)
    x = sk.theta_lo + 1
    for ax, kind, ttl in ((axs[1], 'truth', 'stacked on IPC, truth angle'), (axs[2], 'reco', 'stacked on IPC, as measured (CFRP)')):
        ax.bar(x, sk[f'ipc_{kind}'], width=2, color='#a7bfd6', label='IPC (γ₀ + γ₁)')
        ax.bar(x, sk[f'x17_{kind}'], width=2, bottom=sk[f'ipc_{kind}'], color='#d64545', label='X17 at R(ATOMKI)')
        ax.step(x, sk[f'ipc_{kind}'] + sk[f'x17_{kind}'], where='mid', color=fs.INK, lw=0.7)
        ax.set_xlim(90, 180)
        ax.set_xlabel('e⁺e⁻ opening angle [deg]')
        ax.set_title(ttl, fontsize=9)
        ax.legend(frameon=False, fontsize=7)
    axs[1].set_ylabel('pairs per day / 2° (1 µA, big plastics)')
    fs.fig_title(fig, f'At LNL the target region barely widens the X17 edge: σ68 {st.sigma68.iloc[1]:.1f}° against 14.5° for the n_TOF capsule',
                 f'Geant4 truth and reconstructed chord for the same events; CFRP 0.4 mm chamber; counting days '
                 f'truth {cost.days_3sigma.iloc[0]:.2f} → measured {cost.days_3sigma.iloc[1]:.2f} d. '
                 'Al: Geant4 L5 residuals on the same events; dotted / dash-dot: Gaussian illustrations')
    fs.save(fig, FIGS / 'scatter_widen', data=w)
    fig, ax = fs.figure()
    bb = bud.iloc[::-1]
    ax.barh(bb.layer, bb.sigma68_term_deg, color=[fs.MUTED if l.startswith('n_TOF') else fs.ACCENT for l in bb.layer])
    ax.set_xlabel('contribution to the X17 σ68 [deg] (k·θ₀·lever)')
    fs.title(ax, 'Where the scattering is: the chamber wall, then the air',
             f'Highland at 8.6 MeV, lever (L−r)/L with L = 215 mm, k = {bud.k_model.iloc[0]:.2f} fitted to Geant4 L5; floor s₀ {bud.s0_floor_deg.iloc[0]:.1f}°')
    fs.save(fig, FIGS / 'scatter_budget', data=bud)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    w, st = widen()
    sk, cost = stacked()
    bud = budget()
    w.to_csv(OUT / 'widen.csv', index=False)
    st.to_csv(OUT / 'widen_stats.csv', index=False)
    sk.to_csv(OUT / 'stacked.csv', index=False)
    cost.to_csv(OUT / 'cost.csv', index=False)
    bud.to_csv(OUT / 'budget.csv', index=False)
    print(st.to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    print(cost.to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    print(bud.to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    figures(w, st, sk, cost, bud)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
