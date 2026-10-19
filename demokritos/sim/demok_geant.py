#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
demok_geant.py -- the Demokritos Geant4 campaign (D1-D3): acceptance, backgrounds
and reach for 3H(p,e+e-)4He with the MX17 apparatus around a Ti-T target.

    LNL_SEL=lnl/sim/sel_v3 DEMOK_SEL=demokritos/sim/sel \\
        ~/PycharmProjects/nTof_x17/.venv/bin/python demokritos/sim/demok_geant.py

Inputs: the merged two-arm tables (lnl_merge.py output) of D1 (X17), D2 (Born E1
IPC, generated above 70 deg) and D3 (the 20.49 MeV gamma line), fetched from EOS with
sim/fetch_sel.sh; the LNL L4 cosmics (same apparatus, 1.00 live day).

Everything after the tables is the LNL analysis (lnl/sim/lnl_geant.py):
  * the arm energies get the n_TOF-anchored 'LNL calibrated' response (lnl_calo);
  * levels 'trigger' and 'MM 15° + TOF' (pointing of both MM segments to the
    target within D(15°), 20° collinearity veto, 0.3 ns TOF veto);
  * the opening angle is the vertex-to-centroid chord, the vertex being the target
    position (0, y_T, 0) -- the merge assumed the origin, so it is recomputed here;
  * an E_sum window, scanned.
Weights per day at 1 uA come from ../out/yields.csv (demokritos_rates.py):
  X17 = N_gamma x B_x(ATOMKI); IPC = N_gamma x alpha_E1 with the gamma* anisotropy of
  E1 direct capture (W = 1 + a1 P1 + a2 P2 about the beam, a1 = 0.1, a2 = -0.9: nearly
  sin^2, a stand-in); EPC = N_gamma x the D3 per-gamma tables; cosmics per live day.

Reach: counting in the best (theta, E_sum) window, and Asimov/Fisher template fits
in theta and in theta x |y| (IPC and EPC norms free, cosmics fixed).  Statistics
only: see ESTIMATES.md section 3 on systematics at S/B ~ 1 %.
"""
from __future__ import annotations

import os
import sys
import zlib
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DEM = HERE.parent
ROOT = DEM.parent
OUT = DEM / 'out' / 'geant'
FIGS = OUT / 'figures'
os.environ.setdefault('LNL_SEL', str(ROOT / 'lnl' / 'sim' / 'sel_v3'))
SEL = Path(os.environ.get('DEMOK_SEL', HERE / 'sel'))
sys.path.insert(0, str(ROOT / 'lnl' / 'sim'))
sys.path.insert(0, str(ROOT / 'lnl'))
sys.path.insert(0, str(ROOT / 'ill'))
sys.path.insert(0, str(DEM))

import lnl_geant as G          # noqa: E402
import lnl_calo as LC          # noqa: E402
import lnl_rates as LR         # noqa: E402

W = 20.49
MASS = '16.94'
BX = 5.1e-6
SCENARIO = 'Demokritos Ti-T (2.1 mg/cm2), 900 keV'
CONFIGS = {'bare': 0.0, 'al25': 0.0, 'cu50': 0.0, 'cu1000': 0.0, 'cu1000_y120': 120.0}
CONFIG_LABEL = {'bare': 'no backing, no holder (bound)', 'al25': 'Al 25 µm', 'cu50': 'Cu 50 µm',
                'cu1000': 'Cu 1 mm (existing target)', 'cu1000_y120': 'Cu 1 mm, target +12 cm'}
HWS = {'as built': '', 'big plastics': '_bigP'}
RESP = 'LNL calibrated'
LEVEL = 'MM 15° + TOF'
ANISO_E1 = (0.1, -0.9)
BINS = np.arange(60, 181, 2.0)
XC = 0.5 * (BINS[1:] + BINS[:-1])
YB = np.array([0.0, 0.15, 0.3, 0.45, 0.6, 0.8, 1.0])
FIT_MIN = 80.0                  # D2 is generated above 70 deg: below ~80 deg reco it is short (f70 check)
FIT = XC >= FIT_MIN
ECUTS = [(lo, hi) for lo in (10, 12, 13, 14, 15, 16, 17) for hi in (19, 20, 21, 22, 23, 25, 99) if hi > lo + 2]
F70: dict = {}


# --------------------------------------------------------------------------- #
def born_f70(w=W):
    if w not in F70:
        ev = LR.ipc_vectors('E1', 2_000_000, w, seed=13)
        F70[w] = float(ev['w'][ev['theta'] > 70].sum() / ev['w'].sum())
    return F70[w]


def _file(run, sample, tag, hw):
    if run == 'L4':
        return Path(os.environ['LNL_SEL']) / f'L4_cosmic{HWS[hw]}_sel.npz'
    return SEL / f'{run}_{sample}_{tag}{HWS[hw]}_sel.npz'


_CACHE: dict = {}


def load(run, sample, tag, hw):
    """A merged table with the calibrated response and the opening angle about the target."""
    key = (run, sample, tag, hw)
    if key in _CACHE:
        return _CACHE[key]
    f = _file(run, sample, tag, hw)
    if not f.exists():
        _CACHE[key] = None
        return None
    z = dict(np.load(f, allow_pickle=True))
    z['ngen'] = int(z['cnt_n_generated'])
    z['name'] = f.stem
    z['Esum'] = z['E1'] + z['E2']
    z = LC.respond(z, hw, RESP, seed=zlib.crc32(f.stem.encode()))
    v = np.array([0.0, CONFIGS.get(tag, 0.0), 0.0])
    z['vtx'] = v
    a, b = z['c_all1'].astype(float) - v, z['c_all2'].astype(float) - v
    c = (a * b).sum(1) / (np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1))
    z['reco'] = np.degrees(np.arccos(np.clip(c, -1, 1)))
    E1, E2 = z['E1'], z['E2']
    z['absy'] = np.abs(E1 - E2) / np.maximum(E1 + E2, 1e-9)
    # legs that went downstream of the target (MM charge centroid beyond it along the beam):
    # they crossed the backing.  Measured, not truth.
    z['ndown'] = ((z['c_all1'][:, 1] > v[1]).astype(int) + (z['c_all2'][:, 1] > v[1]).astype(int))
    _CACHE[key] = z
    return z


def pass_level(z, level, seed=11):
    """LNL pointing + collinearity + TOF, with the pointing about the target vertex."""
    n = len(z['reco'])
    lv = G.LEVELS[level]
    ok = np.ones(n, bool)
    if lv.get('seg') is not None:
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


_SEL: dict = {}


def mask(z, level, ecut):
    if z is None:
        return None
    k = (z['name'], tuple(z['vtx']), level)
    if k not in _SEL:
        _SEL[k] = pass_level(z, level)
    return _SEL[k] & (z['Esum'] > ecut[0]) & (z['Esum'] < ecut[1])


def kcos(z):
    me = LR.M_E
    pm = np.sqrt(z['em_ke'] ** 2 + 2 * z['em_ke'] * me)[:, None] * z['em_p']
    pp = np.sqrt(z['ep_ke'] ** 2 + 2 * z['ep_ke'] * me)[:, None] * z['ep_p']
    k = pm + pp
    return k[:, 1] / np.maximum(np.linalg.norm(k, axis=1), 1e-9)


def rates_per_day(scenario=SCENARIO, I_uA=1.0):
    y = pd.read_csv(DEM / 'out' / 'yields.csv').set_index('scenario').loc[scenario]
    pps = I_uA * 1e-6 / LR.E_CHARGE * 86400
    return dict(gamma=y.Y_gamma * pps, ipc=y.Y_ipc_E1 * pps, x17=y.Y_gamma * pps * BX)


def weights(kind, z, R):
    """per-event weight -> events per day."""
    if kind == 'x17':
        return np.full(len(z['reco']), R['x17'] / z['ngen'])
    if kind == 'ipc':
        a1, a2 = ANISO_E1
        c = kcos(z) if 'em_p' in z else np.zeros(len(z['reco']))
        wa = 1 + a1 * c + a2 * 0.5 * (3 * c ** 2 - 1)
        return R['ipc'] * born_f70() / z['ngen'] * wa
    if kind == 'epc':
        return np.full(len(z['reco']), R['gamma'] / z['ngen'])
    if kind == 'cos':
        return np.full(len(z['reco']), 86400.0 / (z['ngen'] * G.MU_LIVE_S))
    raise KeyError(kind)


SAMPLES = {'x17': ('D1', f'X17_m{MASS}'), 'ipc': ('D2', f'E1_{W}'), 'epc': ('D3', 'gam_He4'),
           'cos': ('L4', 'cosmic')}


def sample(kind, tag, hw):
    """(table, extra factor).  D3 (EPC) ran as built only: for the big plastics its
    as-built tables are scaled by the IPC's big-plastics / as-built selected ratio."""
    run, s = SAMPLES[kind]
    z = load(run, s, tag, hw)
    if z is None and kind == 'epc' and hw != 'as built':
        return load(run, s, tag, 'as built'), 'scaled'
    return z, None


def kde(x, w, bins=BINS, bw=G.KDE_BW_DEG):
    from scipy.special import ndtr
    if len(x) == 0:
        return np.zeros(len(bins) - 1)
    xx = np.r_[x, 360.0 - x]
    ww = np.r_[w, w]
    c = ndtr((bins[None, :] - xx[:, None]) / bw)
    return ((c[:, 1:] - c[:, :-1]) * ww[:, None]).sum(0)


def _cat_hists(th, w, cat, ncat, smooth):
    out = []
    for c in range(ncat):
        m = cat == c
        out.append(kde(th[m], w[m]) if smooth else np.histogram(th[m], BINS, weights=w[m])[0])
    return np.stack(out)


def spectra(tag, hw, level, ecut, R, smooth_bkg=True):
    """per-day histograms in theta, theta x |y|, theta x n_down and theta x |y| x n_down."""
    H, H2 = {}, {}
    H3, H4 = {}, {}
    for kind in SAMPLES:
        z, flag = sample(kind, tag, hw)
        if z is None:
            H[kind] = np.zeros(len(XC))
            H2[kind] = np.zeros((len(YB) - 1, len(XC)))
            H3[kind] = np.zeros((3, len(XC)))
            H4[kind] = np.zeros((3 * (len(YB) - 1), len(XC)))
            H[kind + '_n'] = 0
            continue
        m = mask(z, level, ecut)
        w = weights(kind, z, R)
        if flag == 'scaled':
            zi, za = sample('ipc', tag, hw)[0], sample('ipc', tag, 'as built')[0]
            mi, ma = mask(zi, level, ecut), mask(za, level, ecut)
            w = w * (weights('ipc', zi, R)[mi].sum() / max(weights('ipc', za, R)[ma].sum(), 1e-30))
        th, ay = z['reco'][m], z['absy'][m]
        nd = z['ndown'][m]
        iy = np.clip(np.digitize(ay, YB) - 1, 0, len(YB) - 2)
        wm = w[m]
        sm = kind != 'x17' and smooth_bkg
        H3[kind] = _cat_hists(th, wm, nd, 3, sm)
        H4[kind] = _cat_hists(th, wm, iy * 3 + nd, 3 * (len(YB) - 1), sm)
        if kind != 'x17' and smooth_bkg and len(th) < 400_000:
            H[kind] = kde(th, wm)
            H2[kind] = np.stack([kde(th[(ay >= lo) & (ay < hi)], wm[(ay >= lo) & (ay < hi)])
                                 for lo, hi in zip(YB[:-1], YB[1:])])
        else:
            H[kind], _ = np.histogram(th, BINS, weights=wm)
            H2[kind] = np.stack([np.histogram(th[(ay >= lo) & (ay < hi)], BINS,
                                              weights=wm[(ay >= lo) & (ay < hi)])[0]
                                 for lo, hi in zip(YB[:-1], YB[1:])])
        H[kind + '_n'] = int(m.sum())
    H['H3'], H['H4'] = H3, H4
    return H, H2


def counting(H, lo_rng=(96, 130)):
    s, b = H['x17'], H['ipc'] + H['epc'] + H['cos']
    best = (np.nan, np.nan, 0.0)
    cs, cb = np.r_[0, np.cumsum(s)], np.r_[0, np.cumsum(b)]
    for i, lo in enumerate(BINS[:-1]):
        if not lo_rng[0] <= lo <= lo_rng[1]:
            continue
        for j in range(i + 3, len(BINS)):
            S, B = cs[j] - cs[i], cb[j] - cb[i]
            if B > 0 and S / np.sqrt(B) > best[2]:
                best = (lo, BINS[j], S / np.sqrt(B))
    lo, hi, z1 = best
    sel = (BINS[:-1] >= lo) & (BINS[:-1] < hi)
    return dict(win=f'{lo:g}-{hi:g}', S=float(s[sel].sum()), B_ipc=float(H['ipc'][sel].sum()),
                B_epc=float(H['epc'][sel].sum()), B_cos=float(H['cos'][sel].sum()),
                days=9 / z1 ** 2 if z1 > 0 else np.inf)


def fisher_days(s, comps, fixed):
    """days to 3 sigma at r = 1 (B_x ATOMKI) from the per-day templates, theta >= FIT_MIN."""
    s, comps, fixed = s[..., FIT].ravel(), [c[..., FIT].ravel() for c in comps], [f[..., FIT] for f in fixed]
    mu = s + sum(comps) + sum(f.ravel() for f in fixed)
    sig = G.fisher_sigma(s, comps, mu)           # sigma(r) in one day
    return 9 * sig ** 2


def reach(tag, hw, R):
    rows = []
    for ec in ECUTS:
        H, H2 = spectra(tag, hw, LEVEL, ec, R)
        c = counting(H)
        f1 = fisher_days(H['x17'], [H['ipc'], H['epc']], [H['cos']])
        f2 = fisher_days(H2['x17'], [H2['ipc'], H2['epc']], [H2['cos']])
        H3, H4 = H['H3'], H['H4']
        f3 = fisher_days(H3['x17'], [H3['ipc'], H3['epc']], [H3['cos']])
        f4 = fisher_days(H4['x17'], [H4['ipc'], H4['epc']], [H4['cos']])
        # the same, with only the both-upstream pairs (n_down = 0) counted
        up = {k: H3[k][0] for k in ('x17', 'ipc', 'epc', 'cos')}
        cu = counting(up)
        rows.append(dict(config=tag, hw=hw, ecut=f'{ec[0]}-{ec[1]}', **c,
                         S_tot=float(H['x17'].sum()), days_fit_theta=f1, days_fit_theta_y=f2,
                         days_fit_theta_ndown=f3, days_fit_theta_y_ndown=f4,
                         days_count_up=cu['days'], win_up=cu['win'], S_up=cu['S'],
                         B_up=cu['B_ipc'] + cu['B_epc'] + cu['B_cos'],
                         n_mc_x17=H['x17_n'], n_mc_ipc=H['ipc_n'], n_mc_epc=H['epc_n'],
                         n_mc_cos=H['cos_n']))
    return pd.DataFrame(rows)


def acceptance(tag, hw):
    rows = []
    for kind in ('x17', 'ipc', 'epc'):
        z, flag = sample(kind, tag, hw)
        if z is None or flag:
            continue
        ng = z['ngen']
        trig = len(z['reco']) / ng
        m = mask(z, LEVEL, (0, 99))
        row = dict(config=tag, hw=hw, sample=kind, ngen=ng, pair_tag=trig,
                   mm2arm=float(z['cnt_mm_2arm']) / ng if 'cnt_mm_2arm' in z else np.nan,
                   level_frac=float(m.sum()) / ng)
        if kind != 'epc':
            d = (z['reco'] - z['theta'])[m]
            d0 = (z['reco'] - z['theta'])[m & (z['ndown'] == 0)]
            row['sigma68_up_deg'] = float(np.diff(np.percentile(d0, [16, 84]))[0] / 2) if len(d0) > 50 else np.nan
            row['frac_up'] = float((z['ndown'][m] == 0).mean()) if m.any() else np.nan
            row['sigma68_deg'] = float(np.diff(np.percentile(d, [16, 84]))[0] / 2) if len(d) > 50 else np.nan
            row['bias_deg'] = float(np.median(d)) if len(d) > 50 else np.nan
            if kind == 'x17':
                opp = (z['a1'] // 2) == (z['a2'] // 2)
                row['frac_opposite_arms'] = float(opp[m].mean()) if m.any() else np.nan
        if kind == 'ipc':
            row['note'] = f'generated > 70 deg; Born f70 = {born_f70():.3f}'
        rows.append(row)
    return rows


def figures(spec, reach_best):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use()
    tags = [t for t in CONFIGS if any((t, hw) in spec for hw in HWS)]
    fig, axs = plt.subplots(len(tags), 2, figsize=(10, 3.2 * len(tags)), sharex=True, squeeze=False)
    rows = []
    for i, tag in enumerate(tags):
        for j, hw in enumerate(HWS):
            ax = axs[i, j]
            key = (tag, hw)
            if key not in spec:
                ax.set_visible(False)
                continue
            H, ec = spec[key]
            for k, c, lab in (('ipc', '#0072B2', 'E1 IPC'), ('epc', '#E69F00', 'EPC'),
                              ('cos', '#999999', 'cosmics'), ('x17', '#009E73', 'X17 at B_x')):
                ax.step(XC, np.clip(H[k], 1e-3, None), where='mid', color=c, label=lab)
                for x, v in zip(XC, H[k]):
                    rows.append(dict(config=tag, hw=hw, ecut=ec, theta=x, comp=k, per_day=v))
            ax.set_yscale('log')
            ax.axvspan(60, FIT_MIN, color='#999999', alpha=0.12, lw=0)
            ax.set_title(f'{CONFIG_LABEL[tag]}, {hw}, E_sum {ec}', fontsize=9)
            if i == len(tags) - 1:
                ax.set_xlabel('reconstructed opening angle [deg]')
            if j == 0:
                ax.set_ylabel('pairs / day / 2°')
            if i == 0 and j == 0:
                ax.legend(frameon=False, fontsize=7)
            ax.set_ylim(1e-2, 5e3)
    fs.fig_title(fig, 'Geant4: what MX17 sees around a Ti-T target, per day at 1 µA',
                 f'{LEVEL}, LNL-calibrated calorimetry, E_p = 900 keV, Demokritos Ti-T')
    fs.save(fig, FIGS / 'geant_theta', data=pd.DataFrame(rows))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    R = rates_per_day()
    print(f'per day at 1 uA: gamma {R["gamma"]:.3g}, IPC {R["ipc"]:.3g}, X17 {R["x17"]:.3g}; '
          f'Born f70 = {born_f70():.3f}')
    acc, allr, spec = [], [], {}
    for tag in CONFIGS:
        for hw in HWS:
            if sample('x17', tag, hw)[0] is None or sample('ipc', tag, hw)[0] is None:
                print(f'  {tag} {hw}: tables missing, skipped')
                continue
            acc += acceptance(tag, hw)
            r = reach(tag, hw, R)
            allr.append(r)
            b = r.loc[r.days_fit_theta_y_ndown.idxmin()]
            spec[(tag, hw)] = (spectra(tag, hw, LEVEL, tuple(int(v) for v in b.ecut.split('-')), R)[0], b.ecut)
    if not allr:
        print('no tables yet')
        return 1
    acc = pd.DataFrame(acc)
    reach_all = pd.concat(allr, ignore_index=True)
    best = (reach_all.sort_values('days_fit_theta_y_ndown').groupby(['config', 'hw'], sort=False).head(1)
            .sort_values(['config', 'hw']))
    best_c = (reach_all.sort_values('days').groupby(['config', 'hw'], sort=False).head(1)
              .sort_values(['config', 'hw']))
    acc.to_csv(OUT / 'acceptance_geant.csv', index=False)
    reach_all.to_csv(OUT / 'reach_scan.csv', index=False)
    best.to_csv(OUT / 'reach_geant.csv', index=False)
    pd.set_option('display.width', 250)
    pd.set_option('display.max_columns', 30)
    f = lambda v: f'{v:.3g}'                     # noqa: E731
    print('\n== acceptance ==\n', acc.to_string(index=False, float_format=f))
    print('\n== best by theta x |y| fit ==\n', best.to_string(index=False, float_format=f))
    print('\n== best by counting ==\n', best_c.to_string(index=False, float_format=f))
    figures(spec, best)
    return 0


if __name__ == '__main__':
    sys.exit(main())
