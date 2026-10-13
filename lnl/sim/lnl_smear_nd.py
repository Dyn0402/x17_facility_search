#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lnl_smear_nd.py -- how much does more scattering in the target region (a thicker
chamber or beam pipe) cost each fit?  (FEASIBILITY_SIM.md §15, 2026-10-13)

    LNL_SEL=$PWD/lnl/sim/sel_v3 python lnl/sim/lnl_smear_nd.py    # -> lnl/out/nd/smear_scan.csv

Every event's reconstructed angle is moved away from its Geant4 truth by a
factor f: θ' = θ_true + f (θ_reco − θ_true).  The baseline (f = 1) is the CFRP
0.4 mm chamber, X17 σ68 ≈ 4.6° (big plastics, §10).  f scales the whole
residual, so the tails grow with it: a stand-in for a thicker wall, not a
Geant4 run of one.  Cosmics (no truth angle) are left as they are.

    f = 1.0   CFRP 0.4 mm (baseline)
    f = 2.0   ~9°, Geant4's Al 0.5 mm chamber (§10)
    f = 3.1   ~14°, the n_TOF capsule (14.5° there)
    f = 6.0   ~27°, a 1 mm stainless pipe (Highland: x/X0 5.7 % against Al 1 mm's 1.1 % at 12.2°)

Fits as lnl_nd (calibrated response, S_θ 2 % + S_θy 1 %, gains, free
acceptance cubic, θ-resolution scale ±10 %).
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

FACTORS = {1.0: 'CFRP 0.4 mm (baseline)', 2.0: '~Al 0.5 mm', 3.1: 'n_TOF capsule', 6.0: '~1 mm stainless'}
ANALYSES = ('θ', 'm_ee', 'θ × |y|', 'θ × |y| × E_sum')
_kvary = N.kvary


def main():
    N.load_windows()
    rows = []
    for hw in ('big plastics', 'as built'):
        C.set_response(N.REF_RESP, sigma_g='auto')
        ec = C.BEST.get((hw, N.REF_RESP), S.HWS[hw][0])
        S.HWS[hw] = (ec, C.HWS0[hw][1])
        ans = N.analyses(ec)
        z = N.G.load('L1', 'X17_m16.7', hw)
        sel = N.G.select(z, S.LEVEL, ec)
        dth = (z['reco_c'] - z['theta'])[sel]
        for f, lab in FACTORS.items():
            N.kvary = (lambda zz, k, f=f: _kvary(zz, (1 + k) * f - 1))
            q16, q84 = np.percentile(f * dth, [16, 84])
            s68 = float(0.5 * (q84 - q16))      # as lnl_scatter: half the 16-84 % interval
            ev = N.collect(hw, erange=(ec[0] - 4, ec[1]))
            for a in ANALYSES:
                F, P, _, sb = N.fisher_nd(ev, ans[a], N.STRUCTS[N.REF_STRUCT], sigma_g=S.PRIOR_G)
                d = S.days_to(F, P)
                rows.append(dict(hw=hw, factor=f, case=lab, x17_sigma68=s68, analysis=a, days=d))
                print(f'{hw:13s} f {f:3.1f} ({lab:24s}) σ68 {s68:5.1f}°  {a:16s} {d:8.2f} d', flush=True)
        N.kvary = _kvary
        S.HWS[hw] = C.HWS0[hw]
    C.set_response('ideal')
    t = pd.DataFrame(rows)
    t.to_csv(N.OUT / 'smear_scan.csv', index=False)
    with pd.option_context('display.width', 200):
        print(t.pivot_table(index=['hw', 'analysis'], columns='factor', values='days', sort=False).round(2))


if __name__ == '__main__':
    main()
