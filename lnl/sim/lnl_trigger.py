#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lnl_trigger.py -- the LNL trigger designed around single-arm triggers with a
prescale (FEASIBILITY_SIM.md §14.1, 2026-10-12).

    LNL_SEL=lnl/sim/sel_v3 python lnl/sim/lnl_trigger.py     # -> lnl/out/trigger/

Baseline from now on: every arm's leg (SiPM bar AND plastic >= 0.5 MIP) is a
trigger.  The logic has two outputs, ORed into DREAM:

  PAIR    >= 2 legs within 20 ns            never prescaled
  SINGLE  >= 1 leg, prescaled 1/P          P = 1 (take all) when the rate allows

plus a clock trigger for pedestals.  Each event carries the trigger word (which
legs, which output fired, the prescale counter), so the single-arm sample is
exactly normalised for any P.  DREAM is busy for τ = 298 µs per event (RAW,
20 samples, non-paralysable): live = 1 / (1 + f τ), the same for both outputs.

For hardware × beam current × P this gives the rates, the live fraction, the
data rate, and what the single-arm sample buys per hour:
  - cosmic MIPs per arm (the per-arm gain, lnl_calo.py: σ_g);
  - 8Be γ singles per arm (the high-energy end of the scale, event mixing).

The γ rates are the 8Be lines only (lnl_geant.singles); fluorine (¹⁹F(p,αγ),
6-7 MeV) on a LiF target or as contamination is not included (ask).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
LNL = HERE.parent
OUT = LNL / 'out' / 'trigger'
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(LNL.parent / 'ill'))
import lnl_geant as G      # noqa: E402

SCEN = ('ATOMKI 2016 anomaly', 'LNL 2023-24, thick')
CURRENTS = (0.5, 1.0, 2.0, 4.0, 8.0)
PRESCALES = (1, 2, 5, 10, 20, 50, 100)
CLOCK_HZ = 1.0
MB_PER_EVENT_FEU = 83.0 / 3350.0      # DREAM RAW 20 samples: 83 MB/s per FEU at 3.35 kHz
#: Landau MPV precision per MIP: σ(MPV)/MPV ≈ K_MPV / √N (Landau ⊗ Gauss with
#: σ/MPV ≈ 0.2, the n_TOF 2 cm bars; a fit to the peak region)
K_MPV = 0.35


def rows_for(hw, y, sg):
    gr = G.gamma_rates(y, 1.0)
    out = []
    for I in CURRENTS:
        leg_g = sum(sg[('gam', L)]['leg_arm'] * r * I for L, r in gr.items() if ('gam', L) in sg)
        leg_c = sg[('cosmic', 0)]['leg_arm'] if ('cosmic', 0) in sg else np.zeros(4)
        pair_g = sum(sg[('gam', L)]['trig2'] * r * I for L, r in gr.items() if ('gam', L) in sg)
        pair_c = sg[('cosmic', 0)]['trig2'] if ('cosmic', 0) in sg else 0.0
        leg = leg_g + leg_c
        acc = G.TWO_TAU_S * sum(leg[i] * leg[j] for i in range(4) for j in range(i + 1, 4))
        pair = pair_g + pair_c + acc
        single = leg.sum() - 2 * (pair_g + pair_c)        # events with exactly one leg (approx.)
        for P in PRESCALES:
            f = pair + single / P + CLOCK_HZ
            live = 1 / (1 + f * G.DREAM_TAU_S)
            mu_h = leg_c.min() / P * 3600 * live             # cosmic MIPs per hour, weakest arm
            out.append(dict(hw=hw, scenario=y.scenario, I_uA=I, prescale=P,
                            leg_per_s=leg.sum(), leg_cosmic_per_s=leg_c.sum(), leg_gamma_per_s=leg_g.sum(),
                            leg_per_arm=np.round(leg, 2).tolist(),
                            pair_per_s=pair, single_only_per_s=single, trig_per_s=f, live=live,
                            MB_per_s_per_FEU=f * MB_PER_EVENT_FEU,
                            TB_per_day_per_FEU=f * MB_PER_EVENT_FEU * 86400 / 1e6,
                            cosmic_mip_per_arm_per_h=mu_h,
                            gain_prec_1h=K_MPV / np.sqrt(max(mu_h, 1)),
                            gamma_singles_per_arm_per_h=leg_g.min() / P * 3600 * live))
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ytab = pd.read_csv(LNL / 'out' / 'yields.csv')
    rows = []
    for hw in ('as built', 'big plastics'):
        sg = G.singles(hw)
        for _, y in ytab[ytab.scenario.isin(SCEN)].iterrows():
            rows += rows_for(hw, y, sg)
    t = pd.DataFrame(rows)
    t.to_csv(OUT / 'prescale.csv', index=False)
    # the smallest prescale keeping DREAM live >= 95 % (and >= 98 %)
    best = []
    for (hw, sc, I), g in t.groupby(['hw', 'scenario', 'I_uA']):
        r = dict(hw=hw, scenario=sc, I_uA=I, leg_per_s=g.leg_per_s.iloc[0], pair_per_s=g.pair_per_s.iloc[0],
                 live_P1=g[g.prescale == 1].live.iloc[0])
        for tgt in (0.95, 0.98):
            ok = g[g.live >= tgt]
            r[f'P_for_{int(tgt * 100)}'] = int(ok.prescale.min()) if len(ok) else None
        p10 = g[g.prescale == 10].iloc[0]
        r.update(live_P10=p10.live, cosmic_mip_per_arm_per_h_P10=p10.cosmic_mip_per_arm_per_h,
                 gain_prec_1h_P10=p10.gain_prec_1h, TB_day_FEU_P1=g[g.prescale == 1].TB_per_day_per_FEU.iloc[0])
        best.append(r)
    best = pd.DataFrame(best)
    best.to_csv(OUT / 'prescale_choice.csv', index=False)
    with pd.option_context('display.width', 250, 'display.max_columns', 30):
        print(best.round(3).to_string())
    figure(t)


def figure(t):
    import matplotlib
    matplotlib.use('Agg')
    import figstyle as fs
    fs.use()
    fig, ax = fs.figure()
    d = t[t.scenario == 'ATOMKI 2016 anomaly']
    col = {'as built': '#D55E00', 'big plastics': '#0072B2'}
    for (hw, I), g in d[d.I_uA.isin((1.0, 4.0))].groupby(['hw', 'I_uA']):
        ax.plot(g.prescale, 100 * g.live, marker='o', lw=1.2, color=col[hw],
                ls='-' if I == 1.0 else '--', label=f'{hw}, {I:g} µA')
    ax.set_xscale('log')
    ax.axhline(95, color=fs.MUTED, lw=0.6, ls=':')
    ax.set_xlabel('single-arm prescale P (pairs never prescaled)')
    ax.set_ylabel('DREAM live fraction [%]')
    ax.legend(fontsize=7)
    fs.title(ax, 'Taking every single-arm trigger costs a few % of live time',
             'DREAM RAW τ = 298 µs; 8Be γ + cosmics (Geant4), Li₂O 1.04 MeV (ATOMKI 2016)')
    fs.save(fig, OUT / 'figures' / 'trigger_prescale', data=d)


if __name__ == '__main__':
    main()
