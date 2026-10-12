#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lnl_mixing.py -- can event mixing measure the pair acceptance against θ?
(FEASIBILITY_SIM.md §13, 2026-10-12)

    LNL_SEL=<dir with *_sel.npz> python lnl/sim/lnl_mixing.py    # -> lnl/out/mixing/

ATOMKI take the acceptance against opening angle from "uncorrelated e+e- pairs
of different single electron events".  Tested here on Geant4, at trigger level
(two arms with a leg; no E_sum, no MM pointing) so it is the geometric part:

  true acceptance  A(θ) = selected / generated in truth θ.  "Generated" is
                   the Born θ distribution of that multipole (lnl_rates, the
                   generator's formula) × n_generated; for L7 (generated only
                   above 70°) the Born distribution conditioned on θ > 70°.
  mixed estimate   A_mix = M(θ) / sinθ, M = opening angles of hits from two
                   different events in two different arms, chord from the spot.
    singles mixing   the hits are single-arm events (Compton / conversion
                     electrons of the 8Be γ lines, L3 singles tables): what a
                     prescaled single-arm trigger would record.
    pair-leg mixing  the hits are the two legs of selected IPC pairs, swapped
                     between events of the same arm pair: what a pair trigger
                     alone gives.

Two selections: all pairs, and truth |y| < 0.3 (both leptons hard, so the
per-lepton efficiency hardly depends on energy).  Figure of merit: χ²/ndf of
A/A_mix against a constant over 125-175° with MC statistical errors, and the
rms deviation.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lnl_geant as G     # noqa: E402
import lnl_syst as S      # noqa: E402
LR = G.LR
OUT = HERE.parent / 'out' / 'mixing'
EDGES = np.arange(90, 181, 5.0)
XC = 0.5 * (EDGES[1:] + EDGES[:-1])
FIT = (XC >= 125) & (XC < 175)
LEVEL = 'trigger'
SAMPLES = (('M1_18.15', 'M1', 18.15), ('E1_18.15', 'E1', 18.15), ('M1_17.64', 'M1', 17.64))
_BORN: dict = {}


def born(kind, W, ycut=None, n=4_000_000):
    """Born θ histogram per generated pair (EDGES), optionally truth |y| < ycut; and f(θ > 70°)."""
    key = (kind, W, ycut)
    if key not in _BORN:
        ev = LR.ipc_vectors(kind, n, W, seed=11)
        w = ev['w'] / ev['w'].sum()
        m = np.ones(len(w), bool)
        if ycut is not None:
            m = np.abs(ev['ke1'] - ev['ke2']) / (ev['ke1'] + ev['ke2']) < ycut
        h, _ = np.histogram(ev['theta'][m], EDGES, weights=w[m])
        _BORN[key] = (h, w[ev['theta'] > 70].sum())
    return _BORN[key]


def chord(c1, c2):
    c = (c1 * c2).sum(1) / (np.linalg.norm(c1, axis=1) * np.linalg.norm(c2, axis=1))
    return np.degrees(np.arccos(np.clip(c, -1, 1)))


def singles_mix(hw, rng, nmax=200_000, rep=5):
    g = G.load('L3', 'gam_8Be', hw)
    arm, c = g['sg_arm'].astype(int), g['sg_c_all']
    ok = np.isfinite(c).all(1)
    M = np.zeros(len(XC))
    for a in range(4):
        for b in range(a + 1, 4):
            ia, ib = np.nonzero((arm == a) & ok)[0], np.nonzero((arm == b) & ok)[0]
            n = min(len(ia), len(ib), nmax)
            for _ in range(rep):
                M += np.histogram(chord(c[rng.choice(ia, n)], c[rng.choice(ib, n)]), EDGES)[0] * (len(ia) * len(ib) / n)
    return M / np.sin(np.radians(XC))


def pairleg_mix(z, m, rng, rep=20):
    a1, a2 = z['a1'][m].astype(int), z['a2'][m].astype(int)
    c1, c2 = z['c_all1'][m], z['c_all2'][m]
    sw = a1 > a2
    lo, hi = np.where(sw[:, None], c2, c1), np.where(sw[:, None], c1, c2)
    key = np.minimum(a1, a2) * 4 + np.maximum(a1, a2)
    M = np.zeros(len(XC))
    for k in np.unique(key):
        i = np.nonzero(key == k)[0]
        for _ in range(rep):
            j = rng.permutation(i)
            M += np.histogram(chord(lo[i[j != i]], hi[j[j != i]]), EDGES)[0]
    return M / np.sin(np.radians(XC))


def compare(A, Aerr, Amix):
    r = A / np.where(Amix > 0, Amix, np.nan)
    norm = np.nansum(r[FIT] / (Aerr[FIT] / A[FIT]) ** 2) / np.nansum(1 / (Aerr[FIT] / A[FIT]) ** 2)
    r, e = r / norm, (r / norm) * Aerr / np.maximum(A, 1e-30)
    ok = FIT & np.isfinite(r) & (e > 0)
    chi2 = float(np.sum(((r[ok] - 1) / e[ok]) ** 2))
    return r, e, chi2, int(ok.sum() - 1), 100 * float(np.sqrt(np.mean((r[ok] - 1) ** 2))), 100 * float(np.mean(e[ok]))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(7)
    rows, curves = [], []
    for hw in S.HWS:
        Asg = singles_mix(hw, rng)
        for run in ('L2', 'L7'):
            for samp, kind, W in SAMPLES:
                z = G.load(run, samp, hw)
                if z is None:
                    continue
                for ycat, yc in (('all', None), ('y<0.3 (truth)', 0.3)):
                    hb, f70 = born(kind, W, yc)
                    gen = hb * z['ngen'] / (f70 if run == 'L7' else 1.0)
                    m = G.select(z, LEVEL, (-1e9, 1e9))
                    if yc is not None:
                        m = m & (np.abs(z['em_ke'] - z['ep_ke']) / (z['em_ke'] + z['ep_ke']) < yc)
                    ht, _ = np.histogram(z['theta'][m], EDGES)
                    A = ht / np.maximum(gen, 1e-30)
                    Aerr = np.sqrt(np.maximum(ht, 1)) / np.maximum(gen, 1e-30)
                    for meth, Am in (('singles', Asg), ('pair legs', pairleg_mix(z, m, rng))):
                        r, e, chi2, ndf, rms, stat = compare(A, Aerr, Am)
                        rows.append(dict(hw=hw, run=run, sample=samp, ycat=ycat, method=meth, n_125_175=int(ht[FIT].sum()),
                                         chi2=chi2, ndf=ndf, rms_pct=rms, mc_stat_per_bin_pct=stat))
                        curves += [dict(hw=hw, run=run, sample=samp, ycat=ycat, method=meth, theta=x, ratio=a, err=b)
                                   for x, a, b in zip(XC, r, e)]
    t, c = pd.DataFrame(rows), pd.DataFrame(curves)
    t.to_csv(OUT / 'mixing_summary.csv', index=False)
    c.to_csv(OUT / 'mixing_curves.csv', index=False)
    pd.set_option('display.width', 220)
    print(t.round(2).to_string(index=False))
    figure(c, t)
    return 0


def figure(c, t):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    sys.path.insert(0, str(HERE.parent.parent / 'ill'))
    import figstyle as fs
    fs.use()
    run = 'L7' if (c.run == 'L7').any() else 'L2'
    fig, axs = plt.subplots(1, 2, figsize=fs.WIDE, sharey=True)
    cols = {'M1_18.15': '#0072B2', 'E1_18.15': '#D55E00', 'M1_17.64': '#009E73'}
    for ax, meth in zip(axs, ('pair legs', 'singles')):
        g0 = c[(c.hw == 'big plastics') & (c.run == run) & (c.method == meth)]
        for (samp, ycat), g in g0.groupby(['sample', 'ycat']):
            if samp == 'M1_17.64':
                continue
            tt = t[(t.hw == 'big plastics') & (t.run == run) & (t.method == meth) & (t['sample'] == samp) & (t.ycat == ycat)].iloc[0]
            ax.errorbar(g.theta + (1.2 if ycat != 'all' else 0), g.ratio, yerr=g.err, color=cols[samp],
                        ls='-' if ycat == 'all' else '--', marker='o', ms=3, lw=1.1, capsize=0,
                        label=f'{samp}, {ycat}: χ²/ndf {tt.chi2:.0f}/{tt.ndf}')
        ax.axhspan(0.98, 1.02, color=fs.MUTED, alpha=0.18, lw=0)
        ax.axhline(1, color=fs.MUTED, lw=0.6)
        ax.set_ylim(0.4, 1.6)
        ax.set_xlabel('opening angle [deg]')
        ax.set_title(f'mixing {meth}' + (' (what a pair trigger gives)' if meth == 'pair legs' else ' (a single-arm trigger)'), fontsize=9)
        ax.legend(frameon=False, fontsize=6.5)
    axs[0].set_ylabel('true acceptance / mixing estimate\n(normalised over 125–175°)')
    fs.fig_title(fig, 'Event mixing measures the pair acceptance only from single-arm events',
                 f'Geant4 {run} IPC, big plastics, two-arm trigger level; band ±2 %; errors = MC statistics')
    fs.save(fig, OUT / 'figures' / 'mixing_ratio', data=c)


if __name__ == '__main__':
    sys.exit(main())
