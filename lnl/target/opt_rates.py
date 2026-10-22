"""
opt_rates.py — the film and backing γ lines (opt_backing.py) in MX17 with big plastics:
trigger legs per arm, Micromegas hits per arm and their occupancy (TARGET_OPTIONS.md §7.3).

Input: the Geant4 L9 `gam_7Li_bklines` singles library (lxplus/target_singles.py over
$E/L9/gam_7Li_bklines, baseline target geometry, big plastics): isotropic lines at 0.136,
0.478, 0.843, 1.369, 2.37, 4.44, 5.6, 8.06 and 10.76 MeV from the beam spot, equal weights.

    python lnl/target/opt_rates.py   → out/target/options/{line_response,rates_options}.csv
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'out' / 'target' / 'options'
LIB = HERE / 'sel' / 'L9_gam_7Li_bklines_singles.npz'
E_CH = 1.602176634e-19
LINES = (0.136, 0.478, 0.843, 1.369, 2.37, 4.44, 5.6, 8.06, 10.76)
MM_WIN = 1.2e-6            # DREAM RAW window, 20 × 60 ns
COSMIC_LEGS = 15.0         # legs / s / arm (FEAS §4)
# yields column in stacks.csv → line energy in the library
COLS = {'Y_L478_per_p': 0.478, 'Y_Al_843_per_p': 0.843, 'Y_C12_237_per_p': 2.37,
        'Y_C13_806_per_p': 8.06, 'Y_Al_res_per_p': 10.76}


def response():
    z = np.load(LIB)
    n = int(z['n_generated'][0])
    nline = n / len(LINES)
    legs = z['legs'].astype(int)
    rows = []
    for L in LINES:
        m = np.isclose(z['inv_mass'], L, atol=1e-3)
        e = (z['E_sipm'] + z['E_plast'])[m]
        lg = legs[m]
        mm = z['seg_e'][m]
        p_leg = np.mean([((lg >> a) & 1).sum() / nline for a in range(4)])
        p_mm = np.mean([(mm[:, a] > 0).sum() / nline for a in range(4)])
        p_sc = np.mean([(e[:, a] > 0.1).sum() / nline for a in range(4)])
        rows.append(dict(E_MeV=L, p_leg_per_arm=p_leg, p_mm_per_arm=p_mm, p_scint_100keV_per_arm=p_sc))
    return pd.DataFrame(rows).set_index('E_MeV')


def rates(resp):
    st = pd.read_csv(OUT / 'stacks.csv')
    rows = []
    for _, s in st.iterrows():
        for I in (0.125, 0.5, 1.0, 4.0):
            pps = I * 1e-6 / E_CH
            legs = mm = 0.0
            per_line = {}
            for col, L in COLS.items():
                r = s[col] * pps
                legs += r * resp.loc[L, 'p_leg_per_arm']
                mm += r * resp.loc[L, 'p_mm_per_arm']
                per_line[f'mm_{L}'] = r * resp.loc[L, 'p_mm_per_arm']
            g0 = s['Y_g0_per_p'] * pps
            rows.append(dict(stack=s['stack'], I_uA=I, g0_per_s=g0, legs_per_arm_s=legs,
                             legs_vs_cosmics=legs / COSMIC_LEGS, mm_hits_per_arm_s=mm,
                             mm_occupancy=mm * MM_WIN, **per_line))
    return pd.DataFrame(rows)


def main():
    resp = response()
    resp.to_csv(OUT / 'line_response.csv')
    pd.set_option('display.width', 250)
    print(resp.to_string(float_format=lambda v: f'{v:.3g}'))
    r = rates(resp)
    r.to_csv(OUT / 'rates_options.csv', index=False)
    print(r[['stack', 'I_uA', 'g0_per_s', 'legs_per_arm_s', 'mm_hits_per_arm_s', 'mm_occupancy']]
          .to_string(index=False, float_format=lambda v: f'{v:.3g}'))


if __name__ == '__main__':
    main()
