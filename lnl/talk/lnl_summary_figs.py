#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figures and numbers for the one-slide "Possible measurement at LNL" summary that closes the
n_TOF talk (15 Oct 2026). The same slide is drafted in the LNL deck (lnl/deck/summary_slide.py),
which takes its numbers from :func:`numbers` here, so the two cannot drift apart.

    python lnl/talk/lnl_summary_figs.py          # -> lnl/out/talk/

Writes (each .png with its .csv; .pdf too, for pasting into a slide):
    x17_per_day         X17 per day selected at the ATOMKI ratio, n_TOF stack vs big plastics, 1 and 4 µA
    significance_days   expected significance vs beam days, both stacks, 1 µA (4 µA dashed)
    lnl_summary         the two panels side by side
    numbers.json        every number the slide quotes, with its source

Sources (no number is typed in by hand):
  * lnl/out/geant/reach_geant.csv, the reference rows (FEASIBILITY_SIM §14.5): scenario
    'ATOMKI 2016 anomaly' (Li₂O 300 µg/cm², E_p = 1.10 MeV, ATOMKI's 2016 conditions), m = 16.7,
    level 'MM 15° + TOF'. S3d_per_day = X17 per day inside the θ × |y| × E_sum fit at R = 5.8×10⁻⁶;
    days_3d = beam days to 3σ at that R (calibrated response, S_θ 2 % + S_θy 1 % free background
    structure, DAQ live time included).
  * lnl/out/geant/acceptance_geant.csv: pair_tag = X17 pairs with a trigger hit in both arms.
  * trigger_scint/costs.py: four 78×80×5 cm plates with two 3" PMTs each, + SiPM completion + FERS DAQ.

Significance vs time is Z(t) = 3·sqrt(t / days_3d): the Fisher information of the reference fit is
linear in exposure (the deck's 30-day reach uses the same scaling).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
LNL = HERE.parent
REPO = LNL.parent
O = LNL / 'out'
OUT = O / 'talk'

R_ATOMKI = 5.8e-6
A16 = 'ATOMKI 2016 anomaly'
REF = 'MM 15° + TOF'
AB, BP = 'as built', 'big plastics'
LABEL = {AB: 'n_TOF stack as built', BP: 'big plastics'}
ATOMKI_ACC = 0.025          # ESTIMATES.md §2: 5-telescope ATOMKI pair acceptance


def numbers(mass=16.7):
    G = pd.read_csv(O / 'geant' / 'reach_geant.csv')
    A = pd.read_csv(O / 'geant' / 'acceptance_geant.csv')
    y = pd.read_csv(O / 'yields.csv').set_index('scenario').loc[A16]
    sys.path.insert(0, str(REPO / 'trigger_scint'))
    import costs as CO

    def row(hw, I):
        r = G[(G.scenario == A16) & (G.hw == hw) & (G.level == REF) & (G.I_uA == I) & (G.mass == mass)]
        return r.iloc[0]

    def tag(hw):
        return float(A[(A['sample'] == f'X17_m{mass:g}') & (A.hw == hw)].pair_tag.iloc[0])

    cases = {}
    for hw in (AB, BP):
        for I in (1.0, 4.0):
            r = row(hw, I)
            cases[f'{hw}|{I:g}'] = dict(hw=hw, I_uA=I, x17_per_day=float(r.S3d_per_day), bkg_per_day=float(r.B3d_per_day),
                                         days_3sigma=float(r.days_3d), days_5sigma=float(r.days_3d) * 25 / 9,
                                         esum_window=r.esum_3d, live=float(r.live),
                                         produced_per_day=float(r.N_g0) * R_ATOMKI * (1 - y.frac_17_64))
    fers = CO.DAQ[[k for k in CO.DAQ if k.startswith('160 ch: FERS')][0]]
    price = {}
    for m in ('PS', 'PVT'):
        plates = [4 * CO.slab_cost(78, 80, 5, '3"', 2, m, k)['total'] for k in range(3)]
        price[m] = dict(plates_keur=[p / 1e3 for p in plates],
                        all_in_keur=[(plates[k] + CO.SIPM_COMPLETION[k] + fers[k]) / 1e3 for k in range(3)])
    t_ab, t_bp = tag(AB), tag(BP)
    a1, b1 = cases[f'{AB}|1'], cases[f'{BP}|1']
    return dict(
        scenario=A16, mass=mass, R_ATOMKI=R_ATOMKI, level=REF, cases=cases,
        pair_tag={AB: t_ab, BP: t_bp}, trigger_gain=t_bp / t_ab,
        x17_gain=b1['x17_per_day'] / a1['x17_per_day'], days_gain=a1['days_3sigma'] / b1['days_3sigma'],
        atomki_pair_acc=ATOMKI_ACC, price_keur=price,
        sources=dict(reach='lnl/out/geant/reach_geant.csv (days_3d, S3d_per_day, B3d_per_day)',
                     trigger='lnl/out/geant/acceptance_geant.csv (pair_tag)', price='trigger_scint/costs.py'),
        notes='range = [low, central, high]; days to 3σ/5σ at R(ATOMKI) = 5.8e-6; 5σ = 3σ × 25/9')


def figures(N):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    sys.path.insert(0, str(REPO / 'ill'))
    import figstyle as fs
    fs.use()
    OUT.mkdir(parents=True, exist_ok=True)
    col = {AB: fs.COPPER, BP: fs.ACCENT}
    C = N['cases']

    def bars(ax):
        rows = []
        hws = (AB, BP)
        for j, I in enumerate((1.0, 4.0)):
            for i, hw in enumerate(hws):
                c = C[f'{hw}|{I:g}']
                x = i + (j - 0.5) * 0.38
                ax.bar(x, c['x17_per_day'], 0.36, color=col[hw], alpha=1.0 if I == 1 else 0.45,
                       edgecolor=col[hw], linewidth=1)
                ax.text(x, c['x17_per_day'] * 1.12, f"{c['x17_per_day']:.0f}", ha='center', va='bottom',
                        fontsize=10, color=fs.INK, weight='bold' if I == 1 else 'normal')
                ax.text(x, 1.5, f'{I:g} µA', ha='center', va='bottom', fontsize=8.5,
                        color='white' if I == 1 else fs.INK)
                rows.append(dict(hw=hw, I_uA=I, x17_per_day=c['x17_per_day'], bkg_per_day=c['bkg_per_day'],
                                 produced_per_day=c['produced_per_day']))
        ax.set_yscale('log')
        ax.set_ylim(1, 2000)
        ax.set_xticks(range(len(hws)), [LABEL[h] for h in hws])
        ax.set_ylabel('X17 per day selected  (R = 5.8×10⁻⁶)')
        ax.grid(axis='x', visible=False)
        g = N['x17_gain']
        ax.text(0.5, 1100, f'×{g:.1f} at the same current', fontsize=10.5, color=fs.MUTED, ha='center', va='center')
        fs.title(ax, 'X17 in acceptance per day', f"of ~{C[f'{AB}|1']['produced_per_day']:.0f} produced per day at 1 µA")
        return pd.DataFrame(rows)

    def signif(ax):
        rows = []
        t = [10 ** (k / 50) for k in range(-100, 101)]      # 0.01 .. 100 d
        for hw in (AB, BP):
            for I, ls in ((1.0, '-'), (4.0, '--')):
                d3 = C[f'{hw}|{I:g}']['days_3sigma']
                z = [3 * math.sqrt(x / d3) for x in t]
                ax.plot(t, z, ls, color=col[hw], lw=2.0 if I == 1 else 1.2,
                        label=f'{LABEL[hw]}, {I:g} µA')
                rows += [dict(hw=hw, I_uA=I, days=x, Z=v) for x, v in zip(t, z)]
                if I == 1:
                    ax.plot([d3], [3], 'o', color=col[hw], ms=6, zorder=5)
                    ax.annotate(f'{d3:.1f} d' if d3 < 10 else f'{d3:.0f} d', (d3, 3), textcoords='offset points',
                                xytext=(6, -14), fontsize=10, color=col[hw], weight='bold')
        for z, lab in ((3, '3σ'), (5, '5σ')):
            ax.axhline(z, color=fs.MUTED, lw=0.8, ls=':')
            ax.text(0.011, z + 0.15, lab, color=fs.MUTED, fontsize=9)
        ax.axvspan(7, 14, color=fs.GRID, alpha=0.6, lw=0)
        ax.text(9.8, 0.35, '1–2\nweeks', ha='center', fontsize=8.5, color=fs.MUTED)
        ax.set_xscale('log')
        ax.set_xlim(0.01, 100)
        ax.set_ylim(0, 10)
        ax.set_xticks([0.01, 0.1, 1, 10, 100], ['0.01', '0.1', '1', '10', '100'])
        ax.set_xlabel('days of beam')
        ax.set_ylabel('expected significance at the ATOMKI ratio')
        ax.legend(loc='upper left', fontsize=8.5, frameon=False)
        fs.title(ax, 'Time to the ATOMKI sensitivity', f'Geant4, θ × |y| × E_sum fit, background shape free')
        return pd.DataFrame(rows)

    def save(fig, name, df):
        fig.savefig(OUT / f'{name}.pdf')        # vector copy for the slide
        fs.save(fig, OUT / name, data=df)

    fig, ax = fs.figure(figsize=(4.6, 3.6))
    df1 = bars(ax)
    save(fig, 'x17_per_day', df1)
    fig, ax = fs.figure(figsize=(5.2, 3.6))
    df2 = signif(ax)
    save(fig, 'significance_days', df2)
    fig, (a1, a2) = fs.figure(figsize=(9.8, 3.8), ncols=2, gridspec_kw=dict(width_ratios=[1, 1.25]))
    bars(a1)
    signif(a2)
    fig.tight_layout()
    save(fig, 'lnl_summary', pd.concat([df1.assign(panel='x17_per_day'), df2.assign(panel='significance')]))
    plt.close('all')


def main():
    N = numbers()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'numbers.json').write_text(json.dumps(N, indent=1, ensure_ascii=False, default=str))
    figures(N)
    a, b = N['cases'][f'{AB}|1'], N['cases'][f'{BP}|1']
    print(f"X17/day selected, 1 µA: {a['x17_per_day']:.1f} (as built) → {b['x17_per_day']:.0f} (big plastics), ×{N['x17_gain']:.1f}")
    print(f"days to 3σ at R(ATOMKI): {a['days_3sigma']:.1f} → {b['days_3sigma']:.2f}")
    print(f"pair tag: {N['pair_tag'][AB] * 100:.1f} % → {N['pair_tag'][BP] * 100:.1f} %  (×{N['trigger_gain']:.1f})")
    print(f"price PS plates {N['price_keur']['PS']['plates_keur']}, all in {N['price_keur']['PS']['all_in_keur']} k€")
    print(f'wrote {OUT}')


if __name__ == '__main__':
    main()
