#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
shapes_geant.py -- Geant4 run L10: the Cu hemisphere and the diamond window seen by MX17, as built and with
the big plastics, at E_p = 1.03 and 1.10 MeV.  SHAPES_GEANT.md §4-5 (2026-10-27).

    bash lnl/target/shapes/lxplus/fetch_l10.sh
    LNL_SEL=lnl/sim/sel_v3 ~/PycharmProjects/nTof_x17/.venv/bin/python lnl/target/shapes/shapes_geant.py

Same machinery as opt_geant.py (TARGET_OPTIONS §7): LNL-calibrated calorimetry, 'MM 15° + TOF', the
opening angle about the nominal vertex (0, 0, 0), Asimov/Fisher fit in θ × |y| × n_down with the M1, E1,
γ₁ and EPC norms free and cosmics fixed, the best E_sum window.  Differences:
  * every template comes from the configuration's own Geant4 run, γ₁ IPC (M1/E1 at 15.1) included;
  * the yields are those of the configuration's film at E_p (target_model.layered_yield): 20 µm Li for the
    dome and the 0° window, 14 µm at 45° (19.8 µm along the beam) for the tilted window;
  * the references are re-run the same way: the FEAS baseline (Li₂O 300 / Al 10 µm in the CFRP chamber) and
    the L9 flat design (Li 20 / Mo 8 / diamond 50 µm on a Cu ring, big plastics only).
Days are the raw fit (no anchoring to FEAS §14: the raw fit gives 1.02 d for the baseline, big plastics).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
TGT = HERE.parent
LNL = TGT.parent
sys.path.insert(0, str(TGT))
import opt_geant as OG          # noqa: E402
import target_model as TM       # noqa: E402
import opt_sketch as OS         # noqa: E402

OUT = LNL / 'out' / 'target' / 'shapes'
SSEL = Path(os.environ.get('L10_SEL', HERE / 'sel'))
LSEL = OG.LSEL
DETS = {'bigP': 'big plastics', 'asb': 'as built'}
# tag: (label, film); L10 (SHAPES_GEANT.md §4) and L11 (§10: the ogive, the light shells, the window's tube)
SHAPES = {
    'dome200':      ('Cu hemisphere 200 µm, R 11, rim, on the grey flange (reference)', 'Li'),
    'dome300':      ('Cu hemisphere 300 µm (CN paper), R 11, rim', 'Li'),
    'dome200glued': ('Cu hemisphere 200 µm, R 17.5, glued on the DN40 steel tube', 'Li'),
    'win45d200':    ('diamond window 45°, Ø20, 200 µm, Ti rings, Al end piece (reference)', 'Li45'),
    'win45d300':    ('diamond window 45°, Ø20, 300 µm', 'Li45'),
    'win0d200':     ('diamond window 0°, Ø20, 200 µm', 'Li'),
    'win0d300':     ('diamond window 0°, Ø20, 300 µm', 'Li'),
    # L11
    'ogCu200':      ('Cu ogive 200 µm (the 27 Oct CAD), Ø50 × 63, on an Al ring + DN40 line', 'LiOgive'),
    'ogBe200mo8':   ('Be ogive 200 µm + Mo 8 µm liner', 'LiOgive'),
    'ogAl200mo8':   ('Al ogive 200 µm + Mo 8 µm liner', 'LiOgive'),
    'ogBe300mo8':   ('Be ogive 300 µm + Mo 8 µm liner', 'LiOgive'),
    'ogAl300mo8':   ('Al ogive 300 µm + Mo 8 µm liner', 'LiOgive'),
    'domeBe200mo8': ('Be hemisphere 200 µm + Mo 8 µm liner, R 11, rim, grey flange', 'Li'),
    'win45be':      ('diamond window 45°, Ø20, 200 µm, Be 0.5 mm end piece', 'Li45'),
    'flat1mm':      ('flat Li 20 / Mo 8 / diamond 50 µm, Cu ring, in a buildable 1 mm × 300 mm CFRP chamber', 'Li'),
    'win45wide':    ('diamond window 45° on a wide adapter: 2 mm Al plate r 10-30 + 0.5 mm Al tube r 30', 'Li45'),
}
RUN = {t: ('L11' if t in ('ogCu200', 'ogBe200mo8', 'ogAl200mo8', 'ogBe300mo8', 'ogAl300mo8', 'domeBe200mo8', 'win45be', 'win45wide', 'flat1mm') else 'L10')
       for t in SHAPES}
# X17-only diagnostics (big plastics): acceptance and σ68 only
DIAG = {
    'diag_bare':        ('L10', 'window 45°: bare (no end piece, rings ~0, no line)'),
    'diag_noend':       ('L10', 'window 45°: no end piece (rings, line behind)'),
    'diag_cfrpend':     ('L10', 'window 45°: end piece CFRP 1 mm'),
    'diag_ogCu200bare': ('L11', 'Cu ogive, bare base (no mount, no line)'),
    'diag_epAl025':     ('L11', 'window 45°: end piece Al 0.25 mm'),
    'diag_epCfrp05':    ('L11', 'window 45°: end piece CFRP 0.5 mm'),
    'diag_ep16':        ('L11', 'window 45°: end piece Al 0.5 mm, 16 mm, straight on the grey flange'),
}
OG.FILM['Li45'] = TM.film('Li', 748.0 * np.sqrt(2))
# the same ogive runs with the Li masked to the tip sphere: the flat 20 µm yields (no flank path, no 441 keV), tag '<cfg>_tip'
TIP_ONLY = {'ogCu200', 'ogBe200mo8', 'ogBe300mo8', 'ogAl200mo8', 'ogAl300mo8'}
for _t in sorted(TIP_ONLY):
    SHAPES[_t + '_tip'] = (SHAPES[_t][0] + ', Li on the tip sphere only (flat-film yields)', 'Li')
    RUN[_t + '_tip'] = 'L11'
OG.FILM['LiOgive'] = None       # the ogive: the beam lands on the cap and the grazing flank (opt_sketch.ogive_yield_mix)
_g_film_yields = OG.film_yields
OS.spot()                       # load the beam-spot sample before setup() rebinds OG.CONFIGS
_OGIVE_FN = lambda t: TM.layered_yield(OG.EP, [TM.film('Li', t)])   # noqa: E731


def film_yields(film):
    if film == 'LiOgive':
        return OS.ogive_yield_mix(OG.EP, _OGIVE_FN, name='tm')
    return _g_film_yields(film)


OG.film_yields = film_yields
REFS = {'base': ('Li₂O 300 / Al 10 µm in the CFRP chamber (FEAS baseline)', 'Li2O'),
        'li20_mo8_dia50': ('flat Li 20 / Mo 8 / diamond 50 µm, Cu ring, CFRP chamber (L9 design)', 'Li')}
SAMPLE = {'x17': 'X17_m16.8', 'M1': 'M1_18.15', 'E1': 'E1_18.15', 'g1M1': 'M1_15.1', 'g1E1': 'E1_15.1',
          'epc': 'gam_8Be'}


def file_for(kind, tag, det):
    """tag is 'shape' or a reference; det 'bigP' / 'asb'."""
    sfx = '_bigP' if det == 'bigP' else ''
    if kind == 'cos':
        return LSEL / f'L4_cosmic{sfx}_sel.npz'
    if tag in SHAPES:
        return SSEL / f'{RUN[tag]}_{SAMPLE[kind]}_{tag.removesuffix("_tip")}_{det}_sel.npz'
    if tag in DIAG:
        return SSEL / f'{DIAG[tag][0]}_{SAMPLE[kind]}_{tag}_{det}_sel.npz' if kind == 'x17' else Path('/nonexistent')
    if tag == 'base':
        if kind == 'epc':
            return LSEL / ('L3_gam_8Be_bigP_x10_sel.npz' if det == 'bigP' else 'L3_gam_8Be_x20_sel.npz')
        run = 'L1' if kind == 'x17' else 'L2'
        return LSEL / f'{run}_{SAMPLE[kind]}{sfx}_sel.npz'
    if det != 'bigP':
        return Path('/nonexistent')
    if kind in ('g1M1', 'g1E1'):
        return LSEL / f'L2_{SAMPLE[kind]}_bigP_sel.npz'
    return OG.TSEL / f'L9_{SAMPLE[kind]}_{tag}_sel.npz'


def setup(det):
    """point opt_geant at one detector and register every configuration as '<tag>_<det>'."""
    OG.HW = DETS[det]
    OG.CONFIGS.clear()
    for t, (lab, film) in {**REFS, **SHAPES}.items():
        OG.CONFIGS[f'{t}_{det}'] = (lab, 0.0, film)
    if det == 'bigP':
        for t, (run, lab) in DIAG.items():
            OG.CONFIGS[f'{t}_{det}'] = (lab, 0.0, 'Li45')
    OG._file = lambda kind, tag: file_for(kind, tag.rsplit('_', 1)[0], tag.rsplit('_', 1)[1])
    OG.LINES = (18.15, 17.64, 15.1, 14.6)


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    acc, reach = [], []
    for det in DETS:
        setup(det)
        for tag in list(OG.CONFIGS):
            if OG.load('x17', tag) is None:
                print(f'{tag}: tables missing')
                continue
            for r in OG.acceptance(tag):
                acc.append(dict(det=det, **r))
            if tag.rsplit('_', 1)[0] in DIAG:
                continue
            for ep in (1030.0, 1100.0):
                OG.EP = ep
                best = None
                for ec in OG.ECUTS:
                    T = OG.templates(tag, ec)
                    if T is None:
                        break
                    d = OG.fisher_days(T)
                    B = sum(T[k].sum() for k in ('M1', 'E1', 'g1', 'epc', 'cos'))
                    row = dict(det=det, config=tag.rsplit('_', 1)[0], label=OG.CONFIGS[tag][0], Ep_keV=ep,
                               ecut=f'{ec[0]}-{ec[1]}', g0_per_day_1uA=T['ng0'], x17_sel_per_day=T['x17'].sum(),
                               B_sel_per_day=B, days_fit=d,
                               **{f'B_{k}_share': T[k].sum() / B for k in ('M1', 'E1', 'g1', 'epc', 'cos')},
                               n_mc_x17=T['x17_n'], n_mc_epc=T['epc_n'])
                    reach.append(row)
                    if best is None or d < best['days_fit']:
                        best = row
                if best is None:
                    print(f'{tag}: a template is missing, reach skipped')
                    continue
                print(f"{tag:22s} E_p {ep:.0f}: best E_sum {best['ecut']}: {best['days_fit']:.3g} d per µA")
            OG._CACHE.clear()
            OG._LEV.clear()
    a = pd.DataFrame(acc)
    r = pd.DataFrame(reach)
    a.to_csv(OUT / 'geant_acceptance.csv', index=False)
    r.to_csv(OUT / 'geant_reach_scan.csv', index=False)
    best = r.sort_values('days_fit').groupby(['det', 'config', 'Ep_keV'], sort=False).head(1)
    base = best[best.config == 'base'].set_index(['det', 'Ep_keV']).days_fit
    best = best.assign(ratio_to_base=[d / base.get((de, e), np.nan)
                                      for d, de, e in zip(best.days_fit, best.det, best.Ep_keV)])
    best = best.sort_values(['det', 'Ep_keV', 'days_fit'])
    best.to_csv(OUT / 'geant_reach.csv', index=False)
    pd.set_option('display.width', 250)
    pd.set_option('display.max_columns', 40)
    cols = ['det', 'config', 'sample', 'acc', 'acc_125_155', 'sigma68_deg', 'bias_deg', 'frac_any_down']
    print(a[[c for c in cols if c in a]].to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    print(best[['det', 'config', 'Ep_keV', 'ecut', 'x17_sel_per_day', 'B_sel_per_day', 'B_epc_share', 'days_fit',
                'ratio_to_base']].to_string(index=False, float_format=lambda v: f'{v:.3g}'))


if __name__ == '__main__':
    run()
