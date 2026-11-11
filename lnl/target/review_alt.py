"""Design review 2026-11-11 (TARGET_REVIEW.md): ray-trace of all-metal flat end caps against the diamond window.

ESTIMATE. Same method as opt_shapes.py (TARGET_OPTIONS §17): the accepted X17 pairs of Geant4 L9 are traced
through each geometry, a Highland toy gives the multiple-scattering spread of the opening angle, and the six
flat L9 configurations calibrate sigma68 = sqrt(sigma_int^2 + (k sigma_ms)^2).  The trace under-reads Geant4 for
the shells and the window (7.1-7.4 deg traced against 9.1-10.5 deg in Geant4), so read the rows relative to the
diamond-window reference row, not as absolute numbers.

Run:  L9_SEL=$WORK_DATA/x17_facility_search/sel_l9 LNL_SEL=$WORK_DATA/x17_facility_search/sel_v3 \
      ~/PycharmProjects/nTof_x17/.venv/bin/python review_alt.py
Output: ../out/target/options/review_alt_trace.csv
"""
import numpy as np
import pandas as pd

import opt_shapes as OS

OS.X0['Ta'] = 4.094   # mm
EPS = 1e-4            # "no ring": the window() rings shrunk to nothing (a one-piece machined cap)


def cap(layers, tilt, tube='Al', tube_t=0.5, R=10.0, rings=False):
    kw = dict(ring_mm=0.5, ring_mat='Ti') if rings else dict(ring_mm=EPS, glue_mm=EPS)
    return OS.window(layers=layers, R=R, tilt_deg=tilt, tube=tube, tube_t=tube_t, **kw)


def main():
    V, U, T = OS.legs()
    acc = pd.read_csv(OS.OUT / 'geant_acceptance.csv')
    reach = pd.read_csv(OS.OUT / 'geant_reach.csv').set_index('config')
    g4 = acc[acc['sample'] == 'x17'].set_index('config')
    calib = {'li20_mo8_dia50': OS.flat([('Mo', 8), ('Dia', 50)], 2), 'li20_dia50': OS.flat([('Dia', 50)], 2),
             'li20_cu25': OS.flat([('Cu', 25)], 2), 'li20_cu100': OS.flat([('Cu', 100)], 2),
             'li20_cu300': OS.flat([('Cu', 300)], 3), 'li20_cu1000': OS.flat([('Cu', 1000)], 3)}
    c = pd.DataFrame([dict(sig_ms=OS.trace(g, V, U, T, OS.on_film)['sig_ms'], s=g4.loc[t, 'sigma68_deg'],
                           d=reach.loc[t, 'days_ref_1uA']) for t, g in calib.items()])
    (s2, k2), *_ = np.linalg.lstsq(np.c_[np.ones(len(c)), c.sig_ms ** 2], c.s ** 2, rcond=None)
    sint, k = np.sqrt(max(s2, 0)), np.sqrt(max(k2, 0))

    cases = {
        'REF diamond window: Mo 8 / diamond 300, 45 deg, Ti rings 0.5 mm, Al end piece 0.5 mm':
            cap((('Mo', 8), ('Dia', 300)), 45, rings=True),
        'one-piece Al cap: Cu 12 / Al 300, 45 deg, Al end piece 0.5 mm': cap((('Cu', 12), ('Al', 300)), 45),
        'one-piece Al cap: Cu 12 / Al 400, 45 deg, Al end piece 0.5 mm': cap((('Cu', 12), ('Al', 400)), 45),
        'one-piece Al cap: Cu 12 / Al 500, 45 deg, Al end piece 0.5 mm': cap((('Cu', 12), ('Al', 500)), 45),
        'one-piece Al cap: Cu foil 25 / Al 300, 45 deg, Al end piece 0.5 mm': cap((('Cu', 25), ('Al', 300)), 45),
        'one-piece Al cap: Ta foil 10 / Al 300, 45 deg, Al end piece 0.5 mm': cap((('Ta', 10), ('Al', 300)), 45),
        'one-piece Al cap: Cu 12 / Al 300, 45 deg, Al end piece 0.3 mm': cap((('Cu', 12), ('Al', 300)), 45, tube_t=0.3),
        'Al cap Cu 12 / Al 300, 45 deg, on a CFRP tube 1 mm': cap((('Cu', 12), ('Al', 300)), 45, tube='CFRP', tube_t=1.0),
        'one-piece Al cap: Cu 12 / Al 300, 0 deg, Al end piece 0.5 mm': cap((('Cu', 12), ('Al', 300)), 0),
        'Cu foil 25 alone as window (not safe at 1 bar; for scale), 45 deg, Al end piece 0.5 mm': cap((('Cu', 25),), 45),
        'all-Cu cap 200 (his Cu, flat), 45 deg, Al end piece 0.5 mm': cap((('Cu', 200),), 45),
    }
    rows = []
    for lab, (geo, n) in cases.items():
        r = OS.trace(geo, V, U, T, OS.on_plane(n))
        r['sigma68_est'] = float(np.sqrt(sint ** 2 + (k * r['sig_ms']) ** 2))
        rows.append(dict(config=lab, **r))
    df = pd.DataFrame(rows)
    ref = df.sigma68_est.iloc[0]
    df['sigma68_minus_ref'] = df.sigma68_est - ref
    df.to_csv(OS.OUT / 'review_alt_trace.csv', index=False)
    pd.set_option('display.width', 250)
    print(f'calibration sigma_int {sint:.2f} deg, k {k:.2f}')
    print(df[['config', 'x_med', 'f_pair_gt1pct', 'p_conv', 'sigma68_est', 'sigma68_minus_ref']]
          .to_string(index=False, float_format=lambda v: f'{v:.3g}'))


if __name__ == '__main__':
    main()
