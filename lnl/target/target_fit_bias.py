#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
target_fit_bias.py -- if the target is not what the fit assumes, what X17 does
the fit report?  (lnl/target/TARGET_STUDY.md §8, 2026-10-22)

    LNL_SEL=lnl/sim/sel_v3 python lnl/target/target_fit_bias.py   # -> lnl/out/target/fit_bias.csv

The fit model is always the nominal target, Li₂O 300 µg/cm² at 1.10 MeV
(lnl_syst.SIG_RUN), with the reference 3D fit of lnl_nd (θ × |y| × E_sum,
S_θ 2 % + S_θy 1 %, LNL-calibrated response, big plastics).  The truth is a
degraded target from target_model.py:

  f17 = x       lithium has reached the depth where the beam crosses 441 keV
                (diffusion into the backing, a thick or stopping backing):
                a share x of γ₀ is the 17.64 MeV M1 line (nominal 0.6 %).
  hydration     Li₂O -> LiOH / Li₂CO₃ (heavier film: the beam samples lower
                energies, the direct-capture E1 share grows).
  carbon        a carbon layer on the front.
  boron         B/Li in the film: ¹¹B(p,γ₀) 16.9 MeV E1 IPC, a line the model
                does not have (L8 Geant4 sample E1_16.9, θ > 70° like L7).

For each, Δ = background(truth) − background(model) per day, and the Fisher
bias of the fitted parameters after T days is (T F + P)⁻¹ T b (lnl_nd.fisher_nd).
The signal is unchanged.  "fake_r" is the X17 the fit reports in units of the
ATOMKI ratio when there is none; "chi2_resid" is how hard the data reject the
mismodelling after the fit has absorbed what it can.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LNL = HERE.parent
os.environ.setdefault('LNL_SEL', str(LNL / 'sim' / 'sel_v3'))
sys.path.insert(0, str(LNL / 'sim'))
sys.path.insert(0, str(HERE))

import numpy as np          # noqa: E402
import pandas as pd         # noqa: E402

import lnl_geant as G       # noqa: E402
import lnl_syst as S        # noqa: E402
import lnl_calo as C        # noqa: E402
import lnl_nd as N          # noqa: E402
import target_model as TM   # noqa: E402

OUT = LNL / 'out' / 'target'
HW = 'big plastics'
DAYS = (1, 7, 30)
ANALYSES = ('θ × |y| × E_sum', 'θ', 'm_ee')


def yields_row(r, name):
    return pd.Series(dict(target=name, Y_g0=r['Y_g0'], Y_g1=r['Y_g1'], frac_17_64=r['f17'],
                          frac_18_15_res=r['f18res'], frac_direct=r['fdc'],
                          frac_g1_direct=r['frac_g1_direct'], mean_Estar_MeV=r['mean_Estar']), name=name)


def scenarios():
    """name -> (yields row, B/Li)."""
    al10 = TM.film('Al', 2700)
    ref = S.YIELDS.loc[S.SIG_RUN]
    out = {}
    nom = TM.layered_yield(1100, [TM.film('Li2O', 300), al10])
    out['nominal (model check)'] = (yields_row(nom, 'nominal'), 0.0)
    for x in (0.01, 0.02, 0.05, 0.10, 0.20):
        r = ref.copy()
        k = (1 - x) / (1 - ref.frac_17_64)
        r['frac_17_64'] = x
        r['frac_18_15_res'] = ref.frac_18_15_res * k
        r['frac_direct'] = ref.frac_direct * k
        r['Y_g0'] = ref.Y_g0 / k                 # the 18 MeV part unchanged, 17.64 added
        r['Y_g1'] = ref.Y_g1 / k                 # γ₁ of the 441 resonance grows with it (approx.)
        out[f'441 keV share of γ₀ = {x:.0%}'] = (r, 0.0)
    for lab, lay in (('hydrated: all LiOH', [(TM.FILMS['LiOH']['comp'], 300 * 47.9 / 29.9), al10]),
                     ('carbonated: all Li₂CO₃', [(TM.FILMS['Li2CO3']['comp'], 300 * 73.9 / 29.9), al10]),
                     ('carbon 100 µg/cm² on the front', [TM.film('C', 100), TM.film('Li2O', 300), al10])):
        out[lab] = (yields_row(TM.layered_yield(1100, lay), lab), 0.0)
    for b in (1e-3, 1e-2, 0.1, 0.24):
        out[f'boron B/Li = {b:g}'] = (ref.copy(), b)
    return out


def bkg_list(ev, sign=1.0):
    m = ev['grp'] != 'sig'
    v = {k: ev['v0'][k][m] for k in ('th', 'y', 'm', 'E')}
    return v, sign * ev['w'][m]


def boron_list(ec, b_per_li, live):
    """the ¹¹B(p,γ₀) 16.9 MeV E1 IPC per day for B/Li = b_per_li."""
    z, f, run = S.load_ipc('E1_16.9', HW)
    if z is None:
        return None
    y_ = S.YIELDS.loc[S.SIG_RUN]
    ng0 = y_.Y_g0 * 1e-6 / S.LR.E_CHARGE * 86400 * live
    yb = TM.layered_yield(1100, [TM.film('Li2O', 300), TM.film('Al', 2700)], b_per_li=b_per_li)['Y_B_g0']
    a = np.interp(16.9, [15.1, 17.64], [S.ALPHA[(15.1, 'E1')], S.ALPHA[(17.64, 'E1')]])
    w = np.full(len(z['reco_c']), ng0 * (yb / y_.Y_g0) * a * f / z['ngen'])
    m = G.select(z, S.LEVEL, (-1e9, 1e9)) & (z['Esum'] > ec[0] - 7) & (z['Esum'] < ec[1] + 3)
    E1, E2, Es = z['E1'].astype(float), z['E2'].astype(float), z['Esum'].astype(float)
    v = N.ev_vars(z, E1, E2, Es, N.kvary(z, 0))
    return {k: v[k][m] for k in ('th', 'y', 'm', 'E')}, w[m], yb / y_.Y_g0


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    N.load_windows()
    C.set_response(N.REF_RESP, sigma_g='auto')
    ec = C.BEST.get((HW, N.REF_RESP), S.HWS[HW][0])
    S.HWS[HW] = (ec, C.HWS0[HW][1])
    live = S.HWS[HW][1]
    er = (ec[0] - 4, ec[1])
    ans = N.analyses(ec)
    ev_ref = N.collect(HW, S.SIG_RUN, erange=er)
    rows = []
    for name, (yrow, b) in scenarios().items():
        if b:
            bl = boron_list(ec, b, live)
            if bl is None:
                print(f'skip {name}: no E1_16.9 template')
                continue
            dv, dw, ratio = bl
            extra = dict(B_g0_per_Li_g0=ratio)
        else:
            S.YIELDS.loc[name] = yrow
            ev_t = N.collect(HW, name, erange=er)
            vt, wt = bkg_list(ev_t)
            vr, wr = bkg_list(ev_ref, -1.0)
            dv = {k: np.concatenate([vt[k], vr[k]]) for k in vt}
            dw = np.concatenate([wt, wr])
            extra = dict(f17=yrow.frac_17_64, fdc=yrow.frac_direct, Y_g0_rel=yrow.Y_g0 / S.YIELDS.loc[S.SIG_RUN].Y_g0)
        for a in ANALYSES:
            for sname in ('none', N.REF_STRUCT):
                F, P, names, sb = N.fisher_nd(ev_ref, ans[a], N.STRUCTS[sname], sigma_g=S.PRIOR_G, delta=(dv, dw))
                for T in DAYS:
                    M = np.linalg.inv(T * F + P)
                    br = float((M @ (T * sb['b']))[0])
                    sr = float(np.sqrt(M[0, 0]))
                    chi2 = float(T * sb['dd'] - T ** 2 * sb['b'] @ M @ sb['b'])
                    rows.append(dict(scenario=name, analysis=a, structure=sname, days=T, fake_r=br, sigma_r=sr,
                                     fake_Z=br / sr, chi2_resid=chi2, delta_per_day=float(np.sum(dw)), **extra))
        r7 = [x for x in rows if x['scenario'] == name and x['days'] == 30 and x['structure'] == N.REF_STRUCT]
        print(f'{name:36s} ' + '  '.join(f"{x['analysis']}: r {x['fake_r']:+.3f} ({x['fake_Z']:+.1f}σ, χ² {x['chi2_resid']:.0f})"
                                         for x in r7) + '  [30 d]', flush=True)
    t = pd.DataFrame(rows)
    t.to_csv(OUT / 'fit_bias.csv', index=False)
    C.set_response('ideal')


if __name__ == '__main__':
    main()
