#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lnl_nd_maps.py -- the θ × |y| × E_sum reference fit drawn as 2D maps, and the
"impostor" test: can a mismodelled background fake an X17?  (FEASIBILITY_SIM.md
§16, 2026-10-14)

    LNL_SEL=$PWD/lnl/sim/sel_v3 python lnl/sim/lnl_nd_maps.py      # -> lnl/out/nd/maps/

Same event list as lnl_nd (calibrated response, MM 15° + TOF, the per-response
E_sum window).  Writes:

  maps.csv     per (E_sum slice, θ, |y|) cell, per day: X17 at R_ATOMKI, the
               background (and its M1 / E1 / γ₁ / cosmic parts), and the two
               impostors.  Fine cells (3° × 0.05) and coarse ones (6° × 0.1).
  proj.csv     1D projections (θ in the window; |y| and E_sum at 125–155°).
  bias.csv     the fake X17 each fit reports when the background model is
               wrong by an impostor, after T days: bias in r = R/R_ATOMKI,
               its σ, the fake significance, and the χ² the fit is left with
               (Asimov: the mismodelling that the free parameters cannot absorb).

The impostors are background errors built to copy the X17 exactly in the 1D
opening-angle spectrum (all |y|, E_sum window): each X17 event keeps its
reconstructed angle but takes |y| and E_sum from a background event at the
same angle (±1.5°, 30 draws).  So in the angle alone the impostor is the
signal, by construction; it differs only in how it shares the energy.
  A 'acceptance'  applied at every |y| and every E_sum: a geometry, material
                  or efficiency error, which does not know the lepton energies.
  B 'window'      applied at every |y| but only inside the E_sum window: an
                  error in the 18 MeV IPC physics (or a γ₁ leak) that the 15 MeV
                  side band does not share.
An error that copies the X17 in θ, in |y| *and* in E_sum is a signal-shaped
background; no fit separates it.  That is what the 441 keV run and the E_p
scan (the X17 edge moves, an acceptance error does not) are for.

Bias: with the model wrong by Δ, the Asimov fit moves by (T F + P)⁻¹ T b,
b = Σ g Δ/μ (lnl_nd.fisher_nd delta_w).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lnl_nd as N      # noqa: E402
import lnl_calo as C    # noqa: E402
import lnl_syst as S    # noqa: E402

OUT = N.OUT / 'maps'
GRIDS = {'fine': (np.arange(90, 180.001, 3.0), np.arange(0, 1.0001, 0.05)),
         'coarse': (np.arange(90, 180.001, 6.0), np.arange(0, 1.0001, 0.1))}
WIN = (125.0, 155.0)            # the angle window of the 1D |y| and E_sum projections
ANALYSES = ('θ', 'm_ee', 'θ × |y|', 'θ × |y| × E_sum')
DAYS = (1.0, 7.0, 30.0)


NREP = 30                       # background partners drawn per X17 event


def hist2(v, w, E, tb, yb, smooth=True):
    """per-day (θ, |y|) histogram of event weights w, E_sum in E; θ KDE-smoothed
    as in the fit (Binner) for backgrounds, plain for signal-like lists."""
    an = dict(axes=[('th', tb), ('y', yb)], E=E)
    return N.Binner(an, v, smooth).apply(w).reshape(len(yb) - 1, len(tb) - 1)   # (y, θ)


def impostors(ev, ec, seed=11):
    """two event lists (v, w) that copy the X17 angle spectrum in the E_sum window
    exactly, with |y| and E_sum taken from background events at the same angle
    (±1.5°): A from the whole fitted E_sum range, B from the window only."""
    rng = np.random.default_rng(seed)
    v, w, grp = ev['v0'], ev['w'], ev['grp']
    sg = (grp == 'sig') & (v['E'] > ec[0]) & (v['E'] < ec[1])
    bk = grp != 'sig'
    inw = (v['E'] > ec[0]) & (v['E'] < ec[1])
    th_s, w_s = v['th'][sg], w[sg]
    out = {}
    for k, pool in (('A', bk), ('B', bk & inw)):
        ib = np.nonzero(pool)[0]
        tb = v['th'][ib]
        th, ww, src = [], [], []
        for t0 in np.arange(np.floor(th_s.min()), 181.0, 1.0):
            js = np.nonzero((th_s >= t0) & (th_s < t0 + 1))[0]
            if not len(js):
                continue
            near = ib[np.abs(tb - (t0 + 0.5)) < 1.5]
            if not len(near):
                continue
            pw = w[near] / w[near].sum()
            # A: only the in-window share of the partners is seen in the 1D window spectrum
            boost = 1.0 if k == 'B' else w[near].sum() / max(w[near][inw[near]].sum(), 1e-30)
            pick = rng.choice(near, size=(len(js), NREP), p=pw)
            th.append(np.repeat(th_s[js], NREP))
            ww.append(np.repeat(w_s[js] * boost / NREP, NREP))
            src.append(pick.ravel())
        th, ww, src = np.concatenate(th), np.concatenate(ww), np.concatenate(src)
        y, E = v['y'][src], v['E'][src]
        out[k] = (dict(th=th, y=y, m=N.mass(y, th), E=E), ww)
    return out


def run(hw):
    C.set_response(N.REF_RESP, sigma_g='auto')
    ec = C.BEST.get((hw, N.REF_RESP), S.HWS[hw][0])
    S.HWS[hw] = (ec, C.HWS0[hw][1])
    ev = N.collect(hw, erange=(ec[0] - 4, ec[1]))
    imp = impostors(ev, ec)
    grp, w = ev['grp'], ev['w']
    sg, bk = grp == 'sig', grp != 'sig'
    slices = {'window': ec, 'side band': (ec[0] - 4, ec[0])}

    # ---- maps --------------------------------------------------------------- #
    rows = []
    for gname, (tb, yb) in GRIDS.items():
        for sl, E in slices.items():
            v0 = ev['v0']
            h = dict(X17=hist2(v0, np.where(sg, w, 0), E, tb, yb, smooth=False), bkg=hist2(v0, np.where(bk, w, 0), E, tb, yb))
            for gg in ('M1', 'E1', 'g1', 'cos'):
                h[gg] = hist2(v0, np.where(grp == gg, w, 0), E, tb, yb)
            for k, (vi, wi) in imp.items():
                h[f'imp{k}'] = hist2(vi, wi, E, tb, yb, smooth=False)
            for iy in range(len(yb) - 1):
                for it in range(len(tb) - 1):
                    rows.append(dict(hw=hw, grid=gname, slice=sl, E_lo=E[0], E_hi=E[1],
                                     theta_lo=tb[it], theta_hi=tb[it + 1], y_lo=yb[iy], y_hi=yb[iy + 1],
                                     **{k: v[iy, it] for k, v in h.items()}))
    maps = pd.DataFrame(rows)

    # ---- 1D projections ------------------------------------------------------ #
    v = ev['v0']
    prj = []
    an = N.analyses(ec)['θ']
    lists = (('X17', v, np.where(sg, w, 0), False), ('bkg', v, np.where(bk, w, 0), True),
             ('impA', *imp['A'], False), ('impB', *imp['B'], False))
    yb = np.arange(0, 1.0001, 0.05)
    eb = np.arange(ec[0] - 6, ec[1] + 3.001, 0.5)
    for comp, vv, ww, smooth in lists:
        hh = N.Binner(an, vv, smooth).apply(ww)
        prj += [dict(hw=hw, var='theta', lo=a, hi=b, comp=comp, per_day=x) for a, b, x in zip(N.TH_B[:-1], N.TH_B[1:], hh)]
        inw = (vv['th'] > WIN[0]) & (vv['th'] < WIN[1])
        inE = (vv['E'] > ec[0]) & (vv['E'] < ec[1])
        hy, _ = np.histogram(vv['y'][inw & inE], yb, weights=ww[inw & inE])
        prj += [dict(hw=hw, var='y', lo=a, hi=b, comp=comp, per_day=x) for a, b, x in zip(yb[:-1], yb[1:], hy)]
        he, _ = np.histogram(vv['E'][inw], eb, weights=ww[inw])
        prj += [dict(hw=hw, var='Esum', lo=a, hi=b, comp=comp, per_day=x) for a, b, x in zip(eb[:-1], eb[1:], he)]
    prj = pd.DataFrame(prj)

    # ---- the fake X17 each fit reports --------------------------------------- #
    ans = N.analyses(ec)
    bias = []
    for a in ANALYSES:
        for sname in ('none', N.REF_STRUCT):
            for k, d in imp.items():
                F, P, names, sb = N.fisher_nd(ev, ans[a], N.STRUCTS[sname], sigma_g=S.PRIOR_G, delta=d)
                for T in DAYS:
                    M = np.linalg.inv(T * F + P)
                    br = float((M @ (T * sb['b']))[0])
                    sr = float(np.sqrt(M[0, 0]))
                    # χ² left after the fit has absorbed what it can: how hard the data reject the impostor
                    chi2 = float(T * sb['dd'] - T ** 2 * sb['b'] @ M @ sb['b'])
                    bias.append(dict(hw=hw, analysis=a, structure=sname, impostor=k, days=T,
                                     fake_r=br, sigma_r=sr, fake_Z=br / sr, true_Z=1 / sr, chi2_resid=chi2))
                r7 = [x for x in bias if x['analysis'] == a and x['structure'] == sname and x['impostor'] == k and x['days'] == 7][0]
                print(f'{hw:13s} {a:16s} {sname:20s} imp {k}: fake r {r7["fake_r"]:+.3f} '
                      f'(σ {r7["sigma_r"]:.3f}, fake Z {r7["fake_Z"]:+.1f}, true X17 Z {r7["true_Z"]:.1f}, χ² left {r7["chi2_resid"]:.1f} at 7 d)', flush=True)
    S.HWS[hw] = C.HWS0[hw]
    C.set_response('ideal')
    return maps, prj, pd.DataFrame(bias)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    N.load_windows()
    res = [run(hw) for hw in ('big plastics', 'as built')]
    for i, name in enumerate(('maps', 'proj', 'bias')):
        pd.concat([r[i] for r in res]).to_csv(OUT / f'{name}.csv', index=False)
    b = pd.concat([r[2] for r in res])
    with pd.option_context('display.width', 220):
        print(b[b.days == 7].pivot_table(index=['hw', 'impostor', 'structure'], columns='analysis', values='fake_r', sort=False).round(3))


if __name__ == '__main__':
    main()
