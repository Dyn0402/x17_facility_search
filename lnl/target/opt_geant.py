#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
opt_geant.py -- Geant4 run L9: the LNL target options seen by MX17 (big plastics).
TARGET_OPTIONS.md §7.

    bash lnl/target/lxplus/fetch_l9.sh          # the merged L9 tables → lnl/target/sel/
    LNL_SEL=lnl/sim/sel_v3 ~/PycharmProjects/nTof_x17/.venv/bin/python lnl/target/opt_geant.py

Per configuration (film + backing + holder, target at y = 0 or moved +120 mm downstream):
  * X17 (m 16.8), Born M1 and E1 IPC at 18.15 MeV, and the ⁸Be γ lines (EPC), all with the
    LNL-calibrated big-plastic response (lnl_calo) and the 'MM 15° + TOF' level, the
    opening angle and the pointing taken about the target position (as demok_geant.py);
  * acceptance, σ68(Δθ), the fraction of pairs with a leg downstream of the target (it
    crossed the backing), EPC per γ;
  * a reach comparison: days to 3σ at R(ATOMKI) per µA, from an Asimov/Fisher fit in
    θ × |y| × n_down (M1, E1, γ₁ and EPC norms free, cosmics fixed), the best E_sum window.
    The film sets the yields (Li₂O 300 µg/cm² or 20 µm Li at E_p 1.10 MeV,
    target_model.layered_yield); γ₁ uses the baseline L2 15.1 MeV templates for every
    configuration.  This is a RELATIVE comparison: the reference 3D fit of FEAS §14
    (1.0 d at 1 µA for the baseline) is scaled by the ratio to the baseline row.
"""
from __future__ import annotations

import os
import sys
import zlib
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
LNL = HERE.parent
OUT = LNL / 'out' / 'target' / 'options'
os.environ.setdefault('LNL_SEL', str(LNL / 'sim' / 'sel_v3'))
LSEL = Path(os.environ['LNL_SEL'])
TSEL = Path(os.environ.get('L9_SEL', HERE / 'sel'))
sys.path.insert(0, str(LNL / 'sim'))
sys.path.insert(0, str(LNL))
sys.path.insert(0, str(LNL.parent / 'ill'))
sys.path.insert(0, str(HERE))

import lnl_geant as G          # noqa: E402
import lnl_calo as LC          # noqa: E402
import lnl_rates as LR         # noqa: E402
import target_model as TM      # noqa: E402

HW = 'big plastics'
RESP = 'LNL calibrated'
LEVEL = 'MM 15° + TOF'
EP = 1100.0
BINS = np.arange(70, 181, 2.0)
XC = 0.5 * (BINS[1:] + BINS[:-1])
YB = np.array([0.0, 0.15, 0.3, 0.45, 0.6, 0.8, 1.0])
FIT = XC >= 90.0
ECUTS = [(lo, hi) for lo in (11, 12, 13, 14) for hi in (17, 18, 19, 99)]
REF_DAYS = 1.0          # FEAS §14.3 reference 3D fit, baseline, big plastics, 1 µA

# tag: (label, y_target mm, film)
CONFIGS = {
    'base':            ('Li₂O 300 / Al 10 µm (FEAS baseline)', 0.0, 'Li2O'),
    'al10_y120':       ('Li₂O 300 / Al 10 µm, target +12 cm', 120.0, 'Li2O'),
    'dia50':           ('Li₂O 300 / diamond 50 µm, Cu ring', 0.0, 'Li2O'),
    'li20_dia50':      ('Li 20 µm / diamond 50 µm, Cu ring', 0.0, 'Li'),
    'li20_ta_dia300':  ('Li 20 µm / Ta 10 µm / diamond 300 µm', 0.0, 'Li'),
    'li20_dia1':       ('Li 20 µm / diamond 1 mm, Cu ring (centre)', 0.0, 'Li'),
    'li20_dia1_y120':  ('Li 20 µm / diamond 1 mm, target +12 cm', 120.0, 'Li'),
    'li20_mch_y120':   ('Li 20 µm / diamond micro-channel plate, +12 cm', 120.0, 'Li'),
    'cublock_y120':    ('Li₂O 300 / water-cooled Cu block, +12 cm', 120.0, 'Li2O'),
}
FILM = {'Li2O': TM.film('Li2O', 300), 'Li': TM.film('Li', 1068)}
ALPHA = pd.read_csv(LNL / 'out' / 'ipc_alpha.csv').set_index(['W_MeV', 'multipole']).alpha_pair
LINES = (18.15, 17.64, 15.1, 14.6)


def film_yields(film):
    y = TM.layered_yield(EP, [FILM[film]])
    return y


def _file(kind, tag):
    if kind == 'cos':
        return LSEL / 'L4_cosmic_bigP_sel.npz'
    if kind in ('g1M1', 'g1E1'):
        return LSEL / f'L2_{kind[2:]}_15.1_bigP_sel.npz'
    s = {'x17': 'X17_m16.8', 'M1': 'M1_18.15', 'E1': 'E1_18.15', 'epc': 'gam_8Be'}[kind]
    if tag == 'base' and kind != 'epc':
        return LSEL / f'L{1 if kind == "x17" else 2}_{s}_bigP_sel.npz'
    return TSEL / f'L9_{s}_{tag}_sel.npz'


_CACHE: dict = {}


def load(kind, tag):
    y_t = CONFIGS[tag][1]
    f = _file(kind, tag)
    key = (str(f), y_t)
    if key in _CACHE:
        return _CACHE[key]
    if not f.exists():
        _CACHE[key] = None
        return None
    z = dict(np.load(f, allow_pickle=True))
    z['ngen'] = int(z['cnt_n_generated'])
    z['name'] = f.stem
    z['Esum'] = z['E1'] + z['E2']
    z = LC.respond(z, HW, RESP, seed=zlib.crc32(f.stem.encode()))
    v = np.array([0.0, y_t, 0.0])
    z['vtx'] = v
    a, b = z['c_all1'].astype(float) - v, z['c_all2'].astype(float) - v
    c = (a * b).sum(1) / (np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1))
    z['reco'] = np.degrees(np.arccos(np.clip(c, -1, 1)))
    E1, E2 = z['E1'], z['E2']
    z['absy'] = np.abs(E1 - E2) / np.maximum(E1 + E2, 1e-9)
    z['ndown'] = (z['c_all1'][:, 1] > v[1]).astype(int) + (z['c_all2'][:, 1] > v[1]).astype(int)
    _CACHE[key] = z
    return z


def pass_level(z, seed=11):
    lv = G.LEVELS[LEVEL]
    deg = lv['seg']
    D = G.seg_D(deg)
    rng = np.random.default_rng(seed)
    d1, d2 = z['d_dom1'], z['d_dom2']
    good = np.isfinite(d1).all(1) & np.isfinite(d2).all(1)
    s1 = G.smear_dir(np.where(np.isfinite(d1), d1, 1.0), deg, rng)
    s2 = G.smear_dir(np.where(np.isfinite(d2), d2, 1.0), deg, rng)
    c1 = np.where(np.isfinite(z['c_dom1']), z['c_dom1'], 0.0) - z['vtx']
    c2 = np.where(np.isfinite(z['c_dom2']), z['c_dom2'], 0.0) - z['vtx']
    ok = good & (G.dca0(c1, s1) < D) & (G.dca0(c2, s2) < D) & (G.line_angle(s1, s2) >= G.COLL_DEG)
    return ok & G.pass_tof(z, lv, seed)


_LEV: dict = {}


def mask(z, ec):
    k = (z['name'], tuple(z['vtx']))
    if k not in _LEV:
        _LEV[k] = pass_level(z)
    return _LEV[k] & (z['Esum'] > ec[0]) & (z['Esum'] < ec[1])


def kde(x, w):
    from scipy.special import ndtr
    if len(x) == 0:
        return np.zeros(len(XC))
    xx, ww = np.r_[x, 360.0 - x], np.r_[w, w]
    c = ndtr((BINS[None, :] - xx[:, None]) / G.KDE_BW_DEG)
    return ((c[:, 1:] - c[:, :-1]) * ww[:, None]).sum(0)


def hist4(z, m, w, smooth):
    """θ × (|y| bin × n_down) per-day histogram, [ny*3, nθ]."""
    th, ay, nd, wm = z['reco'][m], z['absy'][m], z['ndown'][m], w[m]
    iy = np.clip(np.digitize(ay, YB) - 1, 0, len(YB) - 2)
    cat = iy * 3 + nd
    out = []
    for c in range(3 * (len(YB) - 1)):
        mm = cat == c
        out.append(kde(th[mm], wm[mm]) if smooth else np.histogram(th[mm], BINS, weights=wm[mm])[0])
    return np.stack(out)


def templates(tag, ec, I_uA=1.0):
    film = CONFIGS[tag][2]
    y = film_yields(film)
    ng0 = y['Y_g0'] * I_uA * 1e-6 / LR.E_CHARGE * 86400                 # γ0 per day
    f17, fr, fd = y['f17'], y['f18res'], y['fdc']
    g1r = y['Y_g1'] / y['Y_g0']
    T = {}
    for kind in ('x17', 'M1', 'E1', 'epc', 'g1M1', 'g1E1', 'cos'):
        z = load(kind, tag)
        if z is None:
            return None
        m = mask(z, ec)
        n = len(z['reco'])
        if kind == 'x17':
            w = np.full(n, ng0 * (1 - f17) * LR.R_ATOMKI_2016 / z['ngen'])
        elif kind == 'M1':     # the resonances: 18.15 (and the 17.64 share, with the 18.15 shape)
            w = np.full(n, ng0 * (fr * ALPHA[(18.15, 'M1')] + f17 * ALPHA[(17.64, 'M1')]) / z['ngen'])
        elif kind == 'E1':
            w = np.full(n, ng0 * fd * ALPHA[(18.15, 'E1')] / z['ngen'])
        elif kind == 'g1M1':
            w = np.full(n, ng0 * g1r * 0.5 * ALPHA[(15.1, 'M1')] / z['ngen'])
        elif kind == 'g1E1':
            w = np.full(n, ng0 * g1r * 0.5 * ALPHA[(15.1, 'E1')] / z['ngen'])
        elif kind == 'epc':    # four equal lines in the sample: γ0 (18.15/17.64) and γ1 (15.1/14.6)
            nline = z['ngen'] / len(LINES)
            L = z['inv_mass']
            per = np.select([np.isclose(L, 18.15, atol=1e-3), np.isclose(L, 17.64, atol=1e-3),
                             np.isclose(L, 15.1, atol=1e-3), np.isclose(L, 14.6, atol=1e-3)],
                            [1 - f17, f17, g1r * (1 - f17), g1r * f17], 0.0)
            w = ng0 * per / nline
        else:
            w = np.full(n, 86400.0 / (z['ngen'] * G.MU_LIVE_S))
        T[kind] = hist4(z, m, w, smooth=kind != 'x17')
        T[kind + '_n'] = int(m.sum())
    T['g1'] = T['g1M1'] + T['g1E1']
    T['ng0'] = ng0
    return T


def fisher_days(T):
    s = T['x17'][:, FIT].ravel()
    comps = [T[k][:, FIT].ravel() for k in ('M1', 'E1', 'g1', 'epc')]
    mu = s + sum(comps) + T['cos'][:, FIT].ravel()
    sig = G.fisher_sigma(s, comps, mu)          # σ(r) in one day, r in units of R_ATOMKI
    return 9 * sig ** 2


def counting_days(T):
    s = T['x17'].sum(0)
    b = sum(T[k].sum(0) for k in ('M1', 'E1', 'g1', 'epc', 'cos'))
    cs, cb = np.r_[0, np.cumsum(s)], np.r_[0, np.cumsum(b)]
    best = (0.0, '')
    for i in range(len(XC)):
        if not 110 <= BINS[i] <= 140:
            continue
        for j in range(i + 4, len(BINS)):
            S, B = cs[j] - cs[i], cb[j] - cb[i]
            if B > 0 and S / np.sqrt(B) > best[0]:
                best = (S / np.sqrt(B), f'{BINS[i]:g}-{BINS[j]:g}')
    return (9 / best[0] ** 2 if best[0] > 0 else np.inf), best[1]


def acceptance(tag):
    rows = []
    for kind in ('x17', 'M1', 'E1'):
        z = load(kind, tag)
        if z is None:
            continue
        m = mask(z, (0, 99))
        d = (z['reco'] - z['theta'])[m]
        d0 = (z['reco'] - z['theta'])[m & (z['ndown'] == 0)]
        q = np.percentile(d, [16, 50, 84]) if len(d) > 50 else [np.nan] * 3
        w = (z['reco'] >= 125) & (z['reco'] < 155)
        rows.append(dict(config=tag, label=CONFIGS[tag][0], sample=kind, ngen=z['ngen'],
                         acc=m.sum() / z['ngen'], acc_125_155=(m & w).sum() / z['ngen'],
                         sigma68_deg=0.5 * (q[2] - q[0]), bias_deg=q[1],
                         sigma68_up_deg=(0.5 * np.diff(np.percentile(d0, [16, 84]))[0]) if len(d0) > 50 else np.nan,
                         frac_any_down=float((z['ndown'][m] > 0).mean()) if m.any() else np.nan))
    z = load('epc', tag)
    if z is not None:
        nline = z['ngen'] / len(LINES)
        for ec in ((0, 99), (13, 18)):
            m = mask(z, ec)
            w = (z['reco'] >= 125) & (z['reco'] < 155)
            for L in LINES[:1]:
                lm = np.isclose(z['inv_mass'], L, atol=1e-3)
                rows.append(dict(config=tag, label=CONFIGS[tag][0], sample=f'EPC {L} γ, E_sum {ec}',
                                 ngen=int(nline), acc=(m & lm).sum() / nline,
                                 acc_125_155=(m & lm & w).sum() / nline))
    return rows


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    acc, reach = [], []
    for tag in CONFIGS:
        if load('x17', tag) is None:
            print(f'{tag}: tables missing')
            continue
        acc += acceptance(tag)
        best = None
        for ec in ECUTS:
            T = templates(tag, ec)
            if T is None:
                break
            d = fisher_days(T)
            dc, win = counting_days(T)
            row = dict(config=tag, label=CONFIGS[tag][0], film=CONFIGS[tag][2], ecut=f'{ec[0]}-{ec[1]}',
                       g0_per_day_1uA=T['ng0'], x17_sel_per_day=T['x17'].sum(), days_fit=d,
                       days_count=dc, win_count=win,
                       B_epc_share=T['epc'].sum() / sum(T[k].sum() for k in ('M1', 'E1', 'g1', 'epc', 'cos')),
                       n_mc_x17=T['x17_n'], n_mc_M1=T['M1_n'], n_mc_E1=T['E1_n'], n_mc_epc=T['epc_n'])
            reach.append(row)
            if best is None or d < best['days_fit']:
                best = row
        print(f"{tag:16s} best E_sum {best['ecut']}: fit {best['days_fit']:.3g} d, count {best['days_count']:.3g} d")
    acc = pd.DataFrame(acc)
    r = pd.DataFrame(reach)
    acc.to_csv(OUT / 'geant_acceptance.csv', index=False)
    r.to_csv(OUT / 'geant_reach_scan.csv', index=False)
    best = r.sort_values('days_fit').groupby('config', sort=False).head(1).set_index('config')
    base = best.loc['base', 'days_fit'] if 'base' in best.index else np.nan
    best['ratio_to_base_per_uA'] = best.days_fit / base
    best['days_ref_1uA'] = REF_DAYS * best.ratio_to_base_per_uA
    # same X17 rate as the baseline at 1 µA: the current a thicker film needs
    best['uA_for_baseline_rate'] = best.loc['base', 'g0_per_day_1uA'] / best.g0_per_day_1uA if 'base' in best.index else np.nan
    best = best.reindex([t for t in CONFIGS if t in best.index]).reset_index()
    best.to_csv(OUT / 'geant_reach.csv', index=False)
    pd.set_option('display.width', 250)
    pd.set_option('display.max_columns', 30)
    print(acc.to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    print(best.to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
