#!/usr/bin/env python3
"""
rf_scans.py -- follow-up scans on reactor_fast_beam.py results (reactor_fast/FEASIBILITY.md):

    python reactor_fast/rf_scans.py                # -> out/rf_cells.csv, out/rf_budget.csv
    python reactor_fast/rf_scans.py --refresh KEY ...   # re-score those keys and merge them into out/rf_reach.csv

Cell scan: the yield of a different cell is applied by scaling the captures only (ESTIMATE: the Geant4 backgrounds are for the
30 bar × 40 cm NFS cell).  n_TOF capsule: 500 bar × 8 cm, Ø2 cm face, so ×(3.14/50) of the Ø8 cm spot flux; 10 bar × 40 cm: he3_target fallback.
Budget: the pairs of each beam by energy region, in units where MEDAPP (standard filters, throttle 1) = 1.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / 'survey' / 'soft_sim'))
import reactor_fast_beam as B                                  # noqa: E402
import soft_reach as SR                                        # noqa: E402

OUT = HERE / 'out'
Y, R, SF = SR.Y, SR.R, SR.SF
CELLS = {'NFS 30 bar × 40 cm': 1.0,
         '10 bar × 40 cm (he3_target fallback)': None,           # computed from yields
         'n_TOF capsule 500 bar × 8 cm, Ø2 cm': None}


def cap_ratio(sp, cell, area_frac):
    """(captures in cell × area fraction) / (captures in the reference cell), for this spectrum."""
    e = B.E_FULL
    a = np.trapezoid(sp.flux_e * Y.captures_per_neutron(e, cell) * area_frac, e)
    b = np.trapezoid(sp.flux_e * Y.captures_per_neutron(e), e)
    return float(a / b)


def custom_10bar():
    Y.CELLS['10 bar × 40 cm'] = (10.0, 40.0, 5.0)
    return '10 bar × 40 cm'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--refresh', nargs='+')
    a = ap.parse_args()
    S = B.spectra()
    if a.refresh:
        p = OUT / 'rf_reach.csv'
        t = pd.read_csv(p)
        t = t[~t.key.isin(a.refresh)]
        rows = []
        for hw in R.HW:
            M = SF.nfs_model(hw)
            runs = SR.load_runs(hw)
            for k in a.refresh:
                for v in ('subkev', 'n5only', 'subkev10'):
                    rows += B.score(SR, S[k], hw, M, runs, v)
        pd.concat([t, pd.DataFrame(rows)], ignore_index=True).to_csv(p, index=False, float_format='%.4g')
        print('refreshed', a.refresh)
        return
    # energy-budget table
    medapp = {s.key: s for s in SR.sources()}['medapp_std']
    cap_med = float(SR.captures(medapp).sum())
    rows = []
    e = B.E_FULL
    cpn = Y.captures_per_neutron(e)
    regs = [('thermal <0.4 eV', 0, 4e-7), ('0.4 eV-1 keV', 4e-7, 1e-3), ('1 keV-10 keV', 1e-3, 1e-2), ('10 keV-0.2 MeV', 1e-2, 0.2),
            ('0.2-2.75 MeV', 0.2, 2.75), ('>2.75 MeV', 2.75, 21.0)]
    for k, sp in S.items():
        d = dict(key=k)
        for nm, lo, hi in regs:
            m = (e >= lo) & (e < hi)
            d[f'cap_{nm}'] = B.AREA * np.trapezoid((sp.flux_e * cpn)[m], e[m])
        d['cap_total'] = sum(v for x, v in d.items() if x.startswith('cap_'))
        d['ratio_medapp_fullbeam'] = d['cap_total'] / cap_med
        d['ratio_medapp_throttled'] = d['cap_total'] / (0.3162 * cap_med)
        rows.append(d)
    pd.DataFrame(rows).to_csv(OUT / 'rf_budget.csv', index=False, float_format='%.4g')
    # cell scan on the best sources
    rows = []
    best = [k for k in ('tapiro_open', 'tapiro_open_g3_pb5', 'lvr15') if k in S]
    c10 = custom_10bar()
    for hw in R.HW:
        M = SF.nfs_model(hw)
        runs = SR.load_runs(hw)
        for k in best:
            sp = S[k]
            for cell, area, nm in ((None, 1.0, 'NFS 30 bar × 40 cm'), (c10, 1.0, '10 bar × 40 cm (he3_target fallback)'),
                                   ('n_TOF capsule 500 bar × 8 cm', np.pi / B.AREA, 'n_TOF capsule, Ø2 cm (no focusing)')):
                f = 1.0 if cell is None else cap_ratio(sp, cell, area)
                r = B.score(SR, sp, hw, M, runs, 'subkev', days=(50.0,), cap_mult=f)
                q = [x for x in r if x['signal'] == 'E* ≤ 22 MeV'][0]
                rows.append(dict(key=k, hw=hw, cell=nm, cap_mult=f, rho3=q['rho3'], days_to_atomki=q['days_to_atomki'], throttle=q['throttle'],
                                 floor=q['rho3_floor']))
    t = pd.DataFrame(rows)
    t.to_csv(OUT / 'rf_cells.csv', index=False, float_format='%.4g')
    pd.set_option('display.width', 200)
    print(t.to_string(index=False))


def fig_spectra():
    sys.path.insert(0, str(HERE.parent / 'ill'))
    import figstyle as fs
    S = B.spectra()
    fs.use()
    fig, ax = fs.figure()
    e = B.E_FULL
    d = pd.DataFrame(dict(E=e))
    for k, col, lab in (('tapiro_open_pb5', fs.ACCENT, 'TAPIRO open channel + 5 cm Pb (concept)'),
                        ('lvr15_at_exit', fs.COPPER, 'LVR-15 BNCT beam at the exit'),
                        ('mitr', fs.MUTED, 'MITR FCB (historical)'), ('thor_1mw', fs.TRACK, 'THOR 1 MW (design)')):
        f = S[k].flux_e
        d[k] = f
        m = e > 1e-8
        ax.plot(e[m], (e * f)[m], color=col, lw=1.5, label=lab)
    ax.axvspan(0.2, 2.75, color=fs.BAND_SIGNAL, alpha=0.08, lw=0)
    ax.axvline(1e-3, color='k', lw=0.7, ls=':')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_ylim(1e4, 3e9)
    ax.set_xlabel('E_n [MeV]')
    ax.set_ylabel('E dΦ/dE [n/cm²/s]')
    ax.legend(frameon=False, fontsize=8)
    fs.title(ax, 'Reactor beams at the cell', 'dotted: N5 lower edge (1 keV); shaded: E_n 0.2-2.75 MeV')
    fs.save(fig, OUT / 'rf_spectra', data=d)


if __name__ == '__main__':
    fig_spectra()
    main()
