#!/usr/bin/env python3
"""sens.py -- robustness of the D-D reach: the N5 correlated-term bound, the ESTIMATE terms (shield TVL, arm
response, room return), the accidental hardness, and the n_TOF capsule (out/dd_sens.csv, out/dd_capsule.csv)."""
import sys
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dd_beam as D
import soft_reach as SR
SF, R, Y = SR.SF, SR.R, SR.Y
hw = 'big plastics'
M = SF.nfs_model(hw); runs = SR.load_runs(hw)
grid = np.geomspace(1e-3, 1, 31)
CASES = [('phoenix 90deg', 300., 90., 3e11, 40.), ('phoenix 135deg', 300., 135., 3e11, 40.),
         ('1e12 90deg', 300., 90., 1e12, 40.), ('d 1.5 MeV 5 mA 135deg (gas, hypothetical)', 1500., 135., None, 10.)]

# correlated term: N5 has no selected pair near 2.45 MeV. Bound it from the MC exposure.
z = runs['n']; N = float(z['cnt_n_generated'])
e = np.asarray(z['En'], float)
print('N5 two-arm rows, big plastics:', [(lo, hi, int(((e >= lo) & (e < hi)).sum())) for lo, hi in ((1.5, 3.1), (3.1, 5), (5, 10), (10, 20))])
st, bs = D.make_source(SR, 'x', 300., 90.)
rr = SR.row_rate(z, 'n', 'En', 'w', bs.fn, D.REF_N)
pos = rr[rr > 0]
print('rows with weight:', len(pos), 'sum /d', rr.sum() * 86400, 'mean row rate /d', (pos.mean() * 86400 if len(pos) else 0))
ewin = (np.asarray(z['sg_En'], float) > 1.9) & (np.asarray(z['sg_En'], float) < 3.1)
g0 = SR.gen_density('n', np.array([2.45]))[0]
w_typ = float(np.median(np.asarray(z['sg_w'], float)[ewin])) if ewin.any() else 1.0
f0 = np.interp(2.45, SR.E_GRID, bs.fn)
per_event_day = D.REF_N * f0 / g0 * w_typ / N * 86400
bound = 2.3 * per_event_day
print(f'per MC event: {per_event_day:.3g} /d per 1e9 n; 90% bound on two-arm ok pairs before cuts: {bound:.3g} /d')
pd.DataFrame([dict(per_event_per_day_at_1e9=per_event_day, bound_90cl_per_day_at_1e9=bound)]).to_csv(HERE/'out'/'dd_corr_bound.csv', index=False, float_format='%.4g')

def reach(case, d, tvl=D.TVL_PE, eps_leg=D.EPS_LEG, eps_ok=D.EPS_OK, proom=D.P_ROOM_LEG, acc_mult=1.0, corr_day=0.0, roomok=D.ROOM_OK_FRAC, days=50.):
    nm, ed, th, Y0, line = case
    Y0 = Y0 or D.yield_n_s(ed, 5.0, False)
    st, bs = D.make_source(SR, 'x', ed, th)
    C = SR.components(bs, runs, hw, M); cap = SR.captures(st)
    G = D.geom_factor(d, line) * D.ang_factor(ed, th)
    arm = D.arm_transmission(d, tvl=tvl)
    k = Y0 * G / D.REF_N
    legdir, okdir, legroom = Y0 * arm['frac'] * eps_leg, Y0 * arm['frac'] * eps_ok, Y0 * proom
    C2 = D.add_direct(C, np.full(4, (okdir + legroom * roomok) / k), np.full(4, (legdir + legroom) / k))
    C2 = dict(C2, acc_th=C2['acc_th'] * acc_mult)
    if corr_day:                                                # flat in θ at the bound, per unit k
        C2['corr_th'] = np.ones(len(R.TH_BINS) - 1) * corr_day / (len(R.TH_BINS) - 1)
    res = [(SR.rho3(M, SR.at_throttle(st, C2, M, cap, s * k), days, True), s) for s in grid]
    r, s = min(res)
    stt = SR.at_throttle(st, C2, M, cap, s * k)
    return dict(rho3=r, throttle=s, live=stt['live'], occ=stt['occ'], T=arm['T'], k=k)

rows = []
var = [('nominal', {}), ('TVL 8 cm', dict(tvl=8.)), ('TVL 20 cm', dict(tvl=20.)), ('arm response ×3', dict(eps_leg=D.EPS_LEG * 3, eps_ok=D.EPS_OK * 3)),
       ('arm response ÷3', dict(eps_leg=D.EPS_LEG / 3, eps_ok=D.EPS_OK / 3)), ('room ×3', dict(proom=D.P_ROOM_LEG * 3)), ('room ×10', dict(proom=D.P_ROOM_LEG * 10)),
       ('room ÷3', dict(proom=D.P_ROOM_LEG / 3)), ('accidentals ×100 (hard capture γ)', dict(acc_mult=100.)),
       ('correlated at the N5 90% bound', dict(corr_day=bound)), ('corr bound & room ×3 & acc ×100', dict(corr_day=bound, proom=D.P_ROOM_LEG * 3, acc_mult=100.))]
for case in CASES:
    for d in (35., 50., 75., 100.):
        for nm, kw in var:
            rows.append(dict(case=case[0], d_cm=d, variant=nm, **reach(case, d, **kw)))
            print(rows[-1], flush=True)
pd.DataFrame(rows).to_csv(HERE/'out'/'dd_sens.csv', index=False, float_format='%.4g')

# capsule: 500 bar, R 1, L 4 (Birmingham's cap500), centred on the arms; same source position; reach ∝ 1/sqrt(captures) (stats limited)
out = []
c30 = 30. * np.pi * 25 * 40
c500 = 500. * np.pi * 1 * 4
for d in (25., 35., 50., 75.):
    zs = D.CELL_L / 2 + d
    flux_cell = D.geom_factor(d) / (np.pi * 25)          # mean flux per source n over the cell (per cm²)
    flux_cap = 1 / (4 * np.pi * zs ** 2)
    ratio = (c500 * flux_cap) / (c30 * flux_cell)
    out.append(dict(d_cm=d, captures_capsule_over_cell=ratio, reach_factor_stats=1 / np.sqrt(ratio)))
pd.DataFrame(out).to_csv(HERE/'out'/'dd_capsule.csv', index=False, float_format='%.4g')
print(pd.DataFrame(out).to_string())
