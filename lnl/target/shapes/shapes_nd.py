#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
shapes_nd.py -- the FEAS §14.3 reference fit (θ × |y| × E_sum, Gaussian-process background structure, free
acceptance cubic, arm gains, ...; lnl/sim/lnl_nd.py) run on the L10/L11/L12 target-shape samples, with
Monte-Carlo-statistics diagnostics.  It checks the opt_geant-style numbers in out/target/shapes/geant_reach.csv
(θ × |y| × n_down, norms only, best of 16 E_sum windows).  2026-11-10.

    WORK_DATA=/media/ucla/work ~/PycharmProjects/nTof_x17/.venv/bin/python lnl/target/shapes/shapes_nd.py validate
    ... shapes_nd.py main      # -> out/target/shapes/nd_days.csv, nd_windows.csv
    ... shapes_nd.py mcstat    # -> out/target/shapes/nd_mcstat.csv, nd_counting.csv, nd_info.csv
    ... shapes_nd.py og        # -> out/target/shapes/nd_og_diag.csv (the geant_reach.csv fit itself, dissected)
    options: --extra-run L13 (combine a larger MC run with each configuration's own background tables), -j 8

How the event table is built (collect): lnl_nd.collect itself, with lnl_geant.load / lnl_syst.load_ipc /
lnl_syst.YIELDS / lnl_syst.LEVEL pointed at one configuration for the duration of the call:
  * signal X17 m16.8, IPC M1/E1 18.15 and 15.1, ⁸Be γ (EPC) from the configuration's own Geant4 run
    (shapes_geant.file_for), cosmics from L4; the response (lnl_calo.respond) seeded as opt_geant does;
  * yields from the configuration's film (shapes_geant.film_yields: target_model, the ogive / line-of-sight
    mixes) at E_p; fg (γ1 direct share) for the masked line-of-sight films from the unmasked one (the mix
    sums it with the Li-share weights, which do not add to 1 behind a mask);
  * the shape runs have no M1 17.64 and no 14.6 MeV tables: lnl_nd's 'M1_17.64' term gets the M1 18.15 table
    (its own coefficient f17·α(17.64) and anisotropy a1 = 0.1), the 14.6 terms the 15.1 tables (γ1 of the
    17.64 share on the 15.1 shape).  opt_geant does the same for 17.64 but splits γ1 50/50 M1/E1; here
    the split is fg / (1 − fg) as lnl_nd.  EPC tied to the M1 norm (lnl_nd), not free (opt_geant);
  * the opening angle is reco_c, the angle about (0, 0, 0) between the two MM charge centroids.  opt_geant's
    'reco' (rebuilt from c_all about the target position) is the same number for these targets, which all
    sit at y = 0 (checked: |reco − reco_c| < 1e-5°).  The ogive vertices lie at y = −9.5…0 mm (median
    −1.4); the nominal vertex at the tip is kept (see `vertex_check`).
  * the 'base' configuration is the FEAS baseline with lnl_nd's own inputs (L7 IPC incl. M1 17.64, L2 γ1 incl.
    14.6, L3 + x20 EPC); 'base_L2' is the baseline the way shapes_geant builds it (L2 IPC, x20 EPC only,
    the shape-run substitutions above).

MC tables: point a configuration at more statistics with RUNS / --extra-run (one line, see RUNS below).

READ BEFORE USING THE 'days' COLUMNS: on the as-built shape-run tables (~2-3 k IPC rows) the raw Fisher days are
meaningless (0.002-0.03 d; the information sits in KDE-tail bins with < 1 MC event of background; the FEAS
baseline on its own sparse L2 tables gives 0.016 d instead of 17 d).  Use 'days_floor1' (background floored at one
MC event-equivalent per bin, mu_floor_of; reproduces the dense baseline to 2 %) and the 'transplant' rows
(tp_table; +20-25 % conservative on the baseline).  nd_mcstat.csv holds the halves / subsample / bandwidth /
binning / information-location diagnostics, nd_counting.csv the S/√B cross-checks, nd_og_diag.csv the
opt_geant fit behind geant_reach.csv dissected the same way.  Resume parts: $WORK_DATA/x17_facility_search/
shapes_nd_parts (safe to delete).
"""
from __future__ import annotations

import argparse
import os
import sys

for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):   # one core per worker process
    os.environ.setdefault(_v, '1')
import time
import zlib
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
TGT = HERE.parent
LNL = TGT.parent
_W = Path(os.environ.get('WORK_DATA', '/media/ucla/work')) / 'x17_facility_search'
os.environ.setdefault('LNL_SEL', str(_W / 'sel_v3'))
os.environ.setdefault('L10_SEL', str(_W / 'lnl_sel'))
os.environ.setdefault('L9_SEL', str(_W / 'sel_l9'))
for _p in (LNL / 'sim', LNL, LNL.parent / 'ill', TGT, HERE):
    sys.path.insert(0, str(_p))

import lnl_nd as N            # noqa: E402
import opt_geant as OG        # noqa: E402
import shapes_geant as SG     # noqa: E402

G, S, C = N.G, N.S, N.C
OUT = LNL / 'out' / 'target' / 'shapes'
REF_LEVEL = S.LEVEL
REF_RESP, REF_STRUCT, REF_AN = N.REF_RESP, N.REF_STRUCT, N.REF_ANALYSIS

# --------------------------------------------------------------------------- #
# the MC tables.  RUN_DIR: where a run tag's merged tables live.  RUNS: the background runs combined per
# configuration (default: its own run, SG.RUN).  To use the larger as-built background MC, e.g.
#     RUNS['ogCu200'] = ['L11', 'L13']          (or --extra-run L13 for every configuration that has it)
# --------------------------------------------------------------------------- #
RUN_DIR = {'L10': SG.SSEL, 'L11': SG.SSEL, 'L12': SG.SSEL,
           'L13': Path(os.environ.get('L13_SEL', SG.SSEL))}
RUNS: dict = {}
EXTRA_RUNS: list = []
BKG_KINDS = ('M1', 'E1', 'g1M1', 'g1E1', 'epc')

MAIN = ['base', 'base_L2', 'ogCu200', 'ogCu200_los', 'ogCu200_tip', 'ogAl300cu12r8m4', 'ogAl300cu12r8m4_m6',
        'ogAl400cu12r8m4', 'win45d200', 'ogBe300mo8']
KEY_CFGS = ['base_L2', 'ogCu200', 'ogCu200_los', 'ogCu200_tip', 'ogAl300cu12r8m4', 'ogAl300cu12r8m4_m6']
RESPS = {'asb': ['LNL calibrated', 'n_TOF as is', 'LNL calibrated, LS off', 'ideal'],
         'bigP': ['LNL calibrated', 'big plates, poor']}
STRUCTS = ['none', 'S_θ 2 % + S_θy 1 %', 'S_θ 5 %, ℓ/2', 'S_m 5 %, ℓ/2', 'S_θy 5 %, ℓ/2']
ANS = [REF_AN, 'm_ee', 'θ, |y|<0.3']
EP_LIST = (1100.0, 1030.0)
WIN_GRID = [(lo, hi) for lo in (11, 12, 13, 14) for hi in (17, 18, 19, 20, 22)]
ERANGE = (7.0, 22.0)          # every window of WIN_GRID fits inside (lo − 4, hi)
N.load_windows()
for _d in (15.0, 3.0):        # the pointing cuts from the baseline X17 (before any rerouting)
    G.seg_D(_d)


def mc_tag(cfg):
    return 'base' if cfg.startswith('base') else cfg.removesuffix('_tip').removesuffix('_los').removesuffix('_m6')


def runs_for(cfg, kind):
    mc = mc_tag(cfg)
    own = SG.RUN.get(cfg)
    rr = RUNS.get(mc, [own])
    if kind in BKG_KINDS:
        rr = rr + [r for r in EXTRA_RUNS if r not in rr]
    return rr


def files(cfg, kind, det):
    """the merged tables of one configuration's sample (several runs are concatenated)."""
    mc = mc_tag(cfg)
    f0 = SG.file_for(kind, mc, det)
    if mc == 'base':
        return [f0]
    own = SG.RUN[cfg]
    out = []
    for r in runs_for(cfg, kind):
        f = RUN_DIR[r] / f0.name.replace(f'{own}_', f'{r}_', 1)
        if f.exists():
            out.append(f)
    return out


_TAB: dict = {}


def table(cfg, kind, det, resp):
    fl = files(cfg, kind, det)
    key = (tuple(map(str, fl)), resp, det)
    if key not in _TAB:
        if not fl:
            _TAB[key] = None
        else:
            z = G._combine([dict(np.load(f, allow_pickle=True)) for f in fl])
            z['ngen'] = int(z['cnt_n_generated'])
            z['name'] = '+'.join(f.stem for f in fl)
            z['Esum'] = z['E1'] + z['E2']
            _TAB[key] = C.respond(z, SG.DETS[det], resp, seed=zlib.crc32(fl[0].stem.encode()))
    return _TAB[key]


def film_yields_t(film, li_ug):
    """shapes_geant.film_yields with the Li film thickness li_ug (µg/cm², 1068 = 20 µm) instead of 20 µm:
    yields only (the Geant4 events stay those of the 20 µm run; leptons barely care)."""
    if film == 'LiOgive':
        return SG.OS.ogive_yield_mix(OG.EP, SG._OGIVE_FN, li_ug=li_ug, name='tm')
    if film.startswith('LiLos'):
        mask = {'LiLos': None, 'LiLos4': 4.0, 'LiLos6': 6.0}[film]
        return SG.CL.los_yield_mix(OG.EP, SG._OGIVE_FN, li_ug=li_ug, mask=mask, name='tm')
    if film in ('Li', 'Li45'):
        return SG.TM.layered_yield(OG.EP, [SG.TM.film('Li', li_ug * (np.sqrt(2) * 748 / 1068 if film == 'Li45' else 1))])
    raise ValueError(film)


def yields(cfg, ep, src='film', li_ug=None):
    """lnl_syst.YIELDS-style row for a configuration at E_p.  src 'syst': yields.csv (lnl_nd's own).
    li_ug: another Li film thickness (yields-only re-weighting, film_yields_t)."""
    if src == 'syst':
        scen = {1100.0: 'ATOMKI 2016 anomaly', 1030.0: 'ATOMKI 2016, 18.15 res'}[ep]
        return S.YIELDS.loc[scen].to_dict()
    OG.EP = ep
    film = 'Li2O' if mc_tag(cfg) == 'base' else SG.SHAPES[cfg][1]
    y = SG.film_yields(film) if li_ug is None else film_yields_t(film, li_ug)
    fg = y['frac_g1_direct']
    if film in ('LiLos4', 'LiLos6'):
        fg = (SG.film_yields('LiLos') if li_ug is None else film_yields_t('LiLos', li_ug))['frac_g1_direct']
    return dict(Y_g0=y['Y_g0'], Y_g1=y['Y_g1'], frac_17_64=y['f17'], frac_18_15_res=y['f18res'],
                frac_direct=y['fdc'], frac_g1_direct=fg)


# --------------------------------------------------------------------------- #
# 'transplant': the configuration's angular smearing, energy scale and per-component rates carried onto the
# dense FEAS-baseline MC (L1 X17, L7 IPC 18.15, L2 15.1; ~10× the shape runs' as-built statistics).  Each
# baseline event gets θ_reco = θ_true + Δ, Δ drawn from the configuration's own selected events of the same
# sample in the same (θ_true 10°, |y_true| < 0.3 / 0.6 / 1) cell; arm energies × κ (median E_sum ratio,
# configuration / baseline); the rate in the fit region matched to the configuration's MC.  EPC: the
# configuration's own table ('own') or the baseline EPC shape at the configuration's EPC rate ('base').
# An ESTIMATE of what larger shape-run MC would give, valid if the shell acts through smearing, energy loss and
# rates only (checked against the direct fit where the shape MC is dense: big plastics).
# --------------------------------------------------------------------------- #
_G_LOAD0, _S_IPC0 = G.load, S.load_ipc
BASE_DENSE = {'x17': ('L1', 'X17_m16.8'), 'M1': 'M1_18.15', 'E1': 'E1_18.15', 'g1M1': 'M1_15.1',
              'g1E1': 'E1_15.1', 'epc': ('L3', 'gam_8Be')}


def base_dense(kind, hw):
    """the dense baseline table of one kind.  IPC at 18.15: L7 (generated at θ > 70°, ×10 statistics) for
    θ_true ≥ 70° plus L2 (full range) below, with per-event weights '_wfac' (L2 events count
    ngen7 / (f70 · ngen2) L7 events): with the Cu ogive's smearing ~40 % of the selected M1 pairs have
    θ_true < 70°, which L7 alone would miss."""
    s = BASE_DENSE[kind]
    if isinstance(s, tuple):
        return _G_LOAD0(*s, hw)
    if not s.endswith('18.15'):
        return _S_IPC0(s, hw)[0]
    z7, z2 = _G_LOAD0('L7', s, hw), _G_LOAD0('L2', s, hw)
    f70 = S.born_f70(s[:2], 18.15)
    m7 = np.nan_to_num(z7['theta']) >= 70
    m2 = np.nan_to_num(z2['theta']) < 70
    n7 = len(z7['reco_c'])
    out = {}
    for k, v in z7.items():
        if isinstance(v, np.ndarray) and v.ndim >= 1 and len(v) == n7:
            if k in z2:                 # per-event keys only L7 has (arm times of E1) are dropped: TOF passes
                out[k] = np.concatenate([v[m7], z2[k][m2]])
        else:
            out[k] = v
    out['_wfac'] = np.r_[np.ones(m7.sum()), np.full(m2.sum(), z7['ngen'] / (f70 * z2['ngen']))]
    out['ngen'] = z7['ngen'] / f70           # full-range equivalent
    out['name'] = z7['name'] + '+L2lo'
    return out


def apply_wfac(ev, tabs):
    """multiply the weights of events that came from a table with per-event factors '_wfac' (matched on the
    table index and its E_sum, θ values)."""
    v0 = ev['v0']
    for zt in tabs:
        if zt is None or '_wfac' not in zt:
            continue
        n = len(zt['reco_c'])
        i = np.minimum(ev['idx'], n - 1)
        m = (ev['grp'] != 'sig') & (ev['grp'] != 'cos') & (ev['idx'] < n) \
            & (v0['E'] == zt['Esum'][i]) & (v0['th'] == np.asarray(zt['reco_c'], float)[i])
        f = np.where(m, zt['_wfac'][i], 1.0)
        ev['w'], ev['p1'], ev['p2'] = ev['w'] * f, ev['p1'] * f, ev['p2'] * f
    return ev


def _ytrue(z):
    return np.abs(z['em_ke'] - z['ep_ke']) / np.maximum(z['em_ke'] + z['ep_ke'], 1e-9)


def _region(z, level):
    return G.select(z, level, ERANGE) & (z['reco_c'] >= 90)


def tp_table(cfg, kind, det, resp, level, epc='own', seed=7):
    key = (cfg, kind, det, resp, level, epc, 'tp')
    if key in _TAB:
        return _TAB[key]
    hw = SG.DETS[det]
    zo = table(cfg, kind, det, resp)
    if kind == 'epc' and epc == 'own':
        _TAB[key] = zo
        return zo
    zb = base_dense(kind, hw)
    zz = dict(zb)
    if '_wfac' in zb:
        # the heavy L2 events below 70° (weight ×wfac): oversampled R = wfac times, each copy with its own Δ
        # and weight wfac / R, so a few heavy events do not land as lone spikes in the fit region
        n = len(zb['reco_c'])
        rep = np.clip(np.round(zb['_wfac']), 1, 12 if det == 'asb' else 3).astype(int)
        ir = np.repeat(np.arange(n), rep)
        for k, v in zb.items():
            if isinstance(v, np.ndarray) and v.ndim >= 1 and len(v) == n:
                zz[k] = v[ir]
        zz['_wfac'] = zb['_wfac'][ir] / rep[ir]
        zz['name'] = zb['name'] + '|rep'
        zb = zz
        zz = dict(zb)
    so, sb = _region(zo, level), _region(zb, level)
    if kind != 'epc':
        rng = np.random.default_rng(seed + zlib.crc32(f'{cfg}{kind}{det}'.encode()))
        lev_o = G.select(zo, level, ERANGE)
        d_o = (zo['reco_c'] - zo['theta'])[lev_o]
        it_o = np.clip((zo['theta'][lev_o] // 10).astype(int), 0, 17)
        iy_o = np.digitize(_ytrue(zo)[lev_o], [0.3, 0.6])
        it_b = np.clip((np.nan_to_num(zb['theta']) // 10).astype(int), 0, 17)
        iy_b = np.digitize(_ytrue(zb), [0.3, 0.6])
        dth = np.empty(len(zb['reco_c']))
        for i in range(18):
            for j in range(3):
                mb = (it_b == i) & (iy_b == j)
                if not mb.any():
                    continue
                pool = d_o[(it_o == i) & (iy_o == j)]
                if len(pool) < 10:
                    pool = d_o[it_o == i]
                if len(pool) < 10:
                    pool = d_o[np.abs(it_o - i) <= 2]
                if len(pool) < 10:
                    pool = d_o
                dth[mb] = rng.choice(pool, mb.sum())
        th = zb['theta'] + dth
        th = np.where(th > 180, 360 - th, th)
        zz['reco_c'] = np.abs(th)
    kap = float(np.median(zo['Esum'][so]) / np.median(zb['Esum'][sb]))
    for k in ('E1', 'E2', 'Esum', 'E1_ideal', 'E2_ideal', 'Esum_ideal'):
        if k in zb:
            zz[k] = zb[k] * kap
    zz['name'] = zb['name'] + f'|tp:{cfg}:{kind}:{level}:{epc}'
    sz = _region(zz, level)
    wf = zz.get('_wfac', np.ones(len(zz['reco_c'])))
    zz['ngen'] = wf[sz].sum() / max(so.sum() / zo['ngen'], 1e-30)
    zz['_tp'] = dict(kappa=kap, n_cfg=int(so.sum()), n_base=int(sz.sum()))
    if kind != 'epc':           # rows that land below 50° never reach an analysis bin (θ ≥ 90°, KDE from 70°)
        keep = zz['reco_c'] >= 50
        n = len(keep)
        nm = zz['name'] + '|ge50'
        zz = {k: (v[keep] if isinstance(v, np.ndarray) and v.ndim >= 1 and len(v) == n else v) for k, v in zz.items()}
        zz['name'] = nm
    _TAB[key] = zz
    return zz


IPC_KIND = {'M1_18.15': 'M1', 'M1_17.64': 'M1', 'E1_18.15': 'E1', 'M1_15.1': 'g1M1', 'M1_14.6': 'g1M1',
            'E1_15.1': 'g1E1', 'E1_14.6': 'g1E1'}


def window(det, resp):
    return C.BEST.get((SG.DETS[det], resp), S.HWS[SG.DETS[det]][0])


def collect(cfg, det, ep=1100.0, resp=REF_RESP, level=REF_LEVEL, I_uA=1.0, cos_scale=1.0, live=None,
            erange=ERANGE, mx='16.8', ysrc='film', transplant=False, tp_epc='own', li_ug=None):
    """lnl_nd's event table for one configuration.  level: lnl_geant.LEVELS key; cos_scale multiplies the
    cosmic rate; live: DAQ live fraction (default lnl_syst.HWS).  transplant: the configuration carried onto
    the dense baseline MC (tp_table; tp_epc 'own' / 'base')."""
    hw = SG.DETS[det]
    C.set_response(resp, sigma_g='auto')
    y = yields(cfg, ep, ysrc, li_ug)
    scen = f'__{cfg}@{ep:g}@{li_ug}'
    for k, v in y.items():
        S.YIELDS.loc[scen, k] = v
    g_load, s_ipc, lev0 = G.load, S.load_ipc, S.LEVEL
    S.LEVEL = level
    routed = cfg != 'base'
    used = []

    def tab(kind):
        z = tp_table(cfg, kind, det, resp, level, tp_epc) if transplant else table(cfg, kind, det, resp)
        used.append(z)
        return z
    if routed:
        def g_route(run, sample, hw_='as built'):
            if run == 'L1':
                return tab('x17')
            if run == 'L3':
                return tab('epc')
            return g_load(run, sample, hw_)

        def s_route(s, hw_):
            z = tab(IPC_KIND[s]) if s in IPC_KIND else None
            return (z, 1.0, 'cfg') if z is not None else (None, 1.0, None)
        G.load, S.load_ipc = g_route, s_route
    try:
        ev = N.collect(hw, scen, I_uA, erange=erange, mx=mx, live=live)
    finally:
        G.load, S.load_ipc, S.LEVEL = g_load, s_ipc, lev0
    apply_wfac(ev, {id(z): z for z in used if z is not None}.values())
    if cos_scale != 1.0:
        ev['w'] = np.where(ev['grp'] == 'cos', ev['w'] * cos_scale, ev['w'])
    # one id per MC event (the 17.64 / 14.6 terms reuse the 18.15 / 15.1 tables: same event twice)
    v0 = ev['v0']
    zepc = (tp_table(cfg, 'epc', det, resp, level, tp_epc) if transplant else table(cfg, 'epc', det, resp)) \
        if routed else G.load('L3', 'gam_8Be', hw)
    comp = ev['grp'].astype(object).copy()
    if zepc is not None:
        m = ev['grp'] == 'M1'
        i = np.minimum(ev['idx'], len(zepc['Esum']) - 1)
        isepc = m & (ev['idx'] < len(zepc['Esum'])) & np.isclose(v0['E'], zepc['Esum'][i], rtol=1e-6) \
            & np.isclose(v0['th'], zepc['reco_c'][i].astype(float), rtol=1e-6)
        comp[isepc] = 'epc'
    ev['comp'] = comp.astype(str)
    codes = pd.factorize(ev['comp'])[0]
    key = np.c_[codes, ev['idx'], np.round(v0['E'], 5), np.round(v0['th'], 5)]
    _, ev['uid'] = np.unique(key, axis=0, return_inverse=True)
    ev['uid'] = ev['uid'].ravel()
    ev['meta'] = dict(cfg=cfg, det=det, transplant=(tp_epc if transplant else 'no'), Ep_keV=ep, resp=resp, level=level, I_uA=I_uA, cos_scale=cos_scale,
                      g0_per_day=y['Y_g0'] * I_uA * 1e-6 / OG.LR.E_CHARGE * 86400, **{f'y_{k}': v for k, v in y.items()})
    return ev


# --------------------------------------------------------------------------- #
# fits
# --------------------------------------------------------------------------- #
def templates(ev, an, struct, sel=None):
    F, P, names, out = N.fisher_nd(ev, an, N.STRUCTS[struct], sigma_g=S.PRIOR_G, sel=sel, templates=True)
    return F, P, names, out


def days_from(out, names, keep=None, norms_only=False, mu_floor=None):
    """days from fisher_nd(templates=True) output; keep: bin mask; mu_floor: per-bin floor on the background
    μ in the denominator (mu_floor_of)."""
    g, mu, prior = out['g'], out['mu'], out['prior']
    if mu_floor is not None:
        mu = np.maximum(mu, mu_floor)
    ok = mu > mu.max() * 1e-9
    if keep is not None:
        ok = ok & keep
    rows = np.arange(len(names))
    if norms_only:
        rows = np.array([names.index(k) for k in ('r', 'M1', 'E1', 'g1')])
    gg = g[rows][:, ok]
    F = (gg / mu[ok]) @ gg.T
    P = np.diag([0.0 if prior[i] is None else 1 / prior[i] ** 2 for i in rows])
    return S.days_to(F, P)


def days_bb(out, names, var, norms_only=False, z=3.0):
    """days to zσ with the background-MC statistical error as a per-bin nuisance (Barlow-Beeston-lite,
    profiled at the Asimov point): per-day information g gᵀ / (μ + T σ²_MC), T the days.  var: σ²_MC per bin
    (per day², apply_var).  This is what the present MC can support; it tends to the plain Fisher result
    as the MC grows."""
    g, mu, prior = out['g'], out['mu'], out['prior']
    ok = mu > mu.max() * 1e-9
    rows = np.arange(len(names))
    if norms_only:
        rows = np.array([names.index(k) for k in ('r', 'M1', 'E1', 'g1')])
    gg = g[rows][:, ok]
    P = np.diag([0.0 if prior[i] is None else 1 / prior[i] ** 2 for i in rows])

    def zz(T):
        F = (gg / (mu[ok] + T * var[ok])) @ gg.T
        try:
            c = np.linalg.inv(T * F + P)[0, 0]
        except np.linalg.LinAlgError:
            return 0.0
        return 1 / np.sqrt(c) if c > 0 else 0.0
    if zz(1e6) < z:
        return np.inf
    lo, hi = 1e-4, 1e6
    for _ in range(80):
        mid = np.sqrt(lo * hi)
        lo, hi = (lo, mid) if zz(mid) >= z else (mid, hi)
    return hi


def bkg_var(ev, an):
    """σ²_MC of the background per analysis bin (KDE kernel squared), duplicated events merged."""
    return bkg_aggregate(ev, an, True)[1]


def mu_floor_of(ev, an, neq_min):
    """a floor on each bin's background at neq_min 'event-equivalents' of the local mean MC weight
    (w̄ = Σ K w² / Σ K w, the weight of the events whose kernels reach the bin): where the KDE has only a
    far event's Gaussian tail, the background is not known to be smaller than a fraction of one MC event.
    neq_min 0.1 ≈ half an event at a kernel's peak level in a 2° bin (5° KDE); 1 = one whole event."""
    bk = ev['grp'] != 'sig'
    u, first, inv = np.unique(ev['uid'][bk], return_index=True, return_inverse=True)
    wsum = np.bincount(inv, weights=ev['w'][bk])
    v = {k: ev['v0'][k][bk][first] for k in ('th', 'y', 'm', 'E')}
    b = N.Binner(an, v, True)
    hw, hk2 = b.apply(wsum), b.apply(wsum ** 2)
    wbar = np.where(hw > 0, hk2 / np.maximum(hw, 1e-300), 0.0)
    # categories with no background event at all: the category-average weight of the whole sample
    wbar = np.where(wbar > 0, wbar, np.average(wsum, weights=wsum) if len(wsum) else 0.0)
    return neq_min * wbar


def days_floor(ev, an, struct, neq_min, norms_only=False):
    _, _, names, out = templates(ev, an, struct)
    return days_from(out, names, norms_only=norms_only, mu_floor=mu_floor_of(ev, an, neq_min))


def days(ev, an, struct, sel=None):
    F, P, _, out = N.fisher_nd(ev, an, N.STRUCTS[struct], sigma_g=S.PRIOR_G, sel=sel)
    return S.days_to(F, P), out


def reweighted(ev, mult):
    """shallow copy of ev with every event weight (and the anisotropy rows) times mult."""
    e = dict(ev)
    e['w'], e['p1'], e['p2'] = ev['w'] * mult, ev['p1'] * mult, ev['p2'] * mult
    return e


def subsample_mult(ev, frac, seed, which='bkg'):
    u = np.random.default_rng(seed).random(ev['uid'].max() + 1)[ev['uid']]
    tgt = (ev['grp'] == 'sig') if which == 'sig' else (ev['grp'] != 'sig')
    return np.where(tgt, (u < frac) / frac, 1.0)


def an_variants(ec):
    ans = N.analyses(ec)
    lo, hi = ec
    ref = ans[REF_AN]
    out = {k: ans[k] for k in ANS}
    out['3D, |y| 3 bins'] = dict(axes=[ref['axes'][0], ('y', np.array([0, 0.3, 0.6, 1.0001])), ref['axes'][2]], E=ref['E'])
    out['3D, E_sum 2 bins'] = dict(axes=[ref['axes'][0], ref['axes'][1], ('E', np.array([lo - 4, lo, hi]))], E=ref['E'])
    out['3D, |y| 3 + E_sum 2 bins'] = dict(axes=[ref['axes'][0], ('y', np.array([0, 0.3, 0.6, 1.0001])),
                                                 ('E', np.array([lo - 4, lo, hi]))], E=ref['E'])
    return out


def bkg_aggregate(ev, an, smooth):
    """per-bin background Σw, Σw² (KDE-smoothed when smooth), with duplicated MC events merged first."""
    bk = ev['grp'] != 'sig'
    uid = ev['uid'][bk]
    u, first, inv = np.unique(uid, return_index=True, return_inverse=True)
    wsum = np.bincount(inv, weights=ev['w'][bk])
    v = {k: ev['v0'][k][bk][first] for k in ('th', 'y', 'm', 'E')}
    b = N.Binner(an, v, smooth)
    return b.apply(wsum), apply_var(b, wsum ** 2), b, wsum, ev['comp'][bk][first]


def apply_var(b, w2):
    """the MC variance of a Binner histogram: Σ_i K_i² w_i² (K the KDE kernel; plain bins: Σ w²)."""
    h = np.bincount(b.idx, weights=np.asarray(w2)[b.m], minlength=b.nsec * b.nf).reshape(b.nsec, b.nf)
    if b.K is not None:
        h = h @ (b.K ** 2)
    return h.ravel()


def info_split(ev, an, struct, out, names, thresholds=(1, 3, 10)):
    """where the information sits, per analysis bin of the background:
      neq  = (Σ K w)² / Σ K w²   the number of MC events' worth of KDE weight in the bin ('event-equivalents');
                                a lone event's Gaussian tail gives neq ≪ 1 far from it;
      neff = (Σ K w)² / Σ K² w²  the variance-based effective count (≥ 1 wherever any event contributes).
    Reported: the share of the signal-only information Σ s²/μ and of the signal in bins below N, and the
    full-fit days with those bins dropped."""
    bk = ev['grp'] != 'sig'
    u, first, inv = np.unique(ev['uid'][bk], return_index=True, return_inverse=True)
    wsum = np.bincount(inv, weights=ev['w'][bk])
    v = {k: ev['v0'][k][bk][first] for k in ('th', 'y', 'm', 'E')}
    b = N.Binner(an, v, True)
    hw, hk2, hv = b.apply(wsum), b.apply(wsum ** 2), apply_var(b, wsum ** 2)
    neq = np.where(hk2 > 0, hw ** 2 / np.maximum(hk2, 1e-300), 0.0)
    neff = np.where(hv > 0, hw ** 2 / np.maximum(hv, 1e-300), 0.0)
    s, mu = out['g'][0], out['mu']
    ok = mu > mu.max() * 1e-9
    i_s = np.where(ok, s ** 2 / np.where(ok, mu, 1), 0.0)
    r = dict(info_sig_only=i_s.sum(), sig_lost_mu0=float(s[~ok].sum() / max(s.sum(), 1e-30)),
             n_bins=int(len(s)), n_bins_sig=int((s > 0).sum()))
    for lab, arr in (('neq', neq), ('neff', neff)):
        for t in thresholds:
            low = arr < t
            r[f'infofrac_{lab}<{t}'] = float(i_s[low].sum() / max(i_s.sum(), 1e-30))
            r[f'sigfrac_{lab}<{t}'] = float(s[low].sum() / max(s.sum(), 1e-30))
            r[f'days_drop_{lab}<{t}'] = days_from(out, names, keep=~low)
    # the top 1 % of signal bins by s²/μ: their share of the information
    top = np.argsort(i_s)[::-1][:max(1, int(0.01 * len(s)))]
    r['infofrac_top1pc_bins'] = float(i_s[top].sum() / max(i_s.sum(), 1e-30))
    r['neq_median_top1pc'] = float(np.median(neq[top]))
    return r


def raw_counts(ev, an):
    """raw and effective MC counts per component inside the fit region (unsmoothed region, 90-180°)."""
    b = N.Binner(an, ev['v0'], False)
    r = {}
    for c in ('sig', 'M1', 'epc', 'E1', 'g1', 'cos'):
        m = b.m & (ev['comp'] == c)
        uid = ev['uid'][m]
        u, inv = np.unique(uid, return_inverse=True)
        w = np.bincount(inv, weights=ev['w'][m]) if len(u) else np.zeros(0)
        r[f'n_{c}'] = len(u)
        r[f'neff_{c}'] = float(w.sum() ** 2 / max((w ** 2).sum(), 1e-300)) if len(u) else 0.0
        r[f'rate_{c}'] = float(w.sum())
    return r


def counting(ev, ec, ycut=None):
    """best θ window [lo, hi) (lo 110-150°, ≥ 8° wide) inside the E_sum window, chosen on the KDE-smoothed B;
    S/√B days.  Reports the raw B too and the MC count behind it."""
    an = dict(axes=[('th', N.TH_B)], E=ec, ycut=ycut)
    sm = ev['grp'] == 'sig'
    bs = N.Binner(an, ev['v0'], False)
    sig = bs.apply(np.where(sm, ev['w'], 0))
    braw = bs.apply(np.where(sm, 0, ev['w']))
    bsm = N.Binner(an, ev['v0'], True).apply(np.where(sm, 0, ev['w']))
    # MC count per bin (merged duplicates)
    bk = (~sm) & bs.m
    _, first = np.unique(ev['uid'][bk], return_index=True)
    ib = np.clip(np.digitize(ev['v0']['th'][bk][first], N.TH_B) - 1, 0, len(N.TH_B) - 2)
    nmc = np.bincount(ib, minlength=len(N.TH_B) - 1)
    cs, cb, cr, cn = (np.r_[0, np.cumsum(a)] for a in (sig, bsm, braw, nmc))
    best = None
    for i in range(len(N.TH_B) - 1):
        if not 110 <= N.TH_B[i] <= 150:
            continue
        for j in range(i + 4, len(N.TH_B)):
            Sx, Bx = cs[j] - cs[i], cb[j] - cb[i]
            if Bx > 0 and (best is None or Sx / np.sqrt(Bx) > best[0]):
                best = (Sx / np.sqrt(Bx), i, j)
    _, i, j = best
    Sx, Bx, Br, nB = cs[j] - cs[i], cb[j] - cb[i], cr[j] - cr[i], cn[j] - cn[i]
    return dict(win=f'{N.TH_B[i]:g}-{N.TH_B[j]:g}', S=Sx, B_kde=Bx, B_raw=Br, n_mc_B=int(nB),
                days_kde=9 * Bx / Sx ** 2, days_raw=9 * Br / Sx ** 2 if Br > 0 else np.nan)


# --------------------------------------------------------------------------- #
# tasks
# --------------------------------------------------------------------------- #
def _row(ev, **kw):
    m = ev['meta']
    return dict(config=m['cfg'], det=m['det'], Ep_keV=m['Ep_keV'], resp=m['resp'],
                mc='direct' if m['transplant'] == 'no' else 'transplant', **kw)


TP_BIGP = ('base_L2', 'ogCu200', 'ogAl300cu12r8m4')


def MCS(cfg, det='asb'):
    """the MC variants run for a configuration: its own tables, and (shape runs) the transplant.  With the big
    plastics the shape MC is ~7× denser and the transplant is memory-heavy: only for TP_BIGP."""
    if cfg == 'base' or (det == 'bigP' and cfg not in TP_BIGP):
        return ['direct']
    return ['direct', 'transplant']


def task_main(args):
    """(cfg, det, resp): all structures × analyses at the per-response window, and the window grid for the
    reference fit, for both E_p."""
    cfg, det, resp = args
    rows, wrows = [], []
    ec0 = window(det, resp)
    for ep, mc in [(e, m) for e in EP_LIST for m in MCS(cfg, det)]:
        t0 = time.time()
        ev = collect(cfg, det, ep, resp, transplant=mc == 'transplant')
        ans = N.analyses(ec0)
        for a in ANS:
            for st in STRUCTS:
                d, o = days(ev, ans[a], st)
                rows.append(_row(ev, ecut=f'{ec0[0]:g}-{ec0[1]:g}', analysis=a, structure=st, days=d,
                                 days_floor1=days_floor(ev, ans[a], st, FLOOR),
                                 S_per_day=o['S'], B_per_day=o['B'], g0_per_day=ev['meta']['g0_per_day']))
        for ec in (WIN_GRID if not (det == 'bigP' and mc == 'transplant') else []):
            an = N.analyses(ec)[REF_AN]
            d, o = days(ev, an, REF_STRUCT)
            wrows.append(_row(ev, ecut=f'{ec[0]:g}-{ec[1]:g}', analysis=REF_AN, structure=REF_STRUCT, days=d,
                              days_floor1=days_floor(ev, an, REF_STRUCT, FLOOR), S_per_day=o['S'], B_per_day=o['B']))
        print(f'{cfg:20s} {det} {resp:24s} {ep:.0f} {mc:10s}: ref {rows[-len(ANS) * len(STRUCTS) + 1]["days"]:.3g} d '
              f'({time.time() - t0:.0f} s)', flush=True)
    return rows, wrows


SUB_FRACS = (0.5, 0.25, 0.125)
#: the background floor (mu_floor_of) used for the MC-safe numbers: 1 event-equivalent.  Calibrated on the
#: baseline: the sparse L2 as-built tables give 0.016 d raw, 12.3 d at 0.3 and 13.9 d at 1, against 13.6 d
#: from the dense L7 tables.
FLOOR = 1.0
SUB_SEEDS = (1, 2, 3, 4)


def task_mcstat(args):
    cfg, det, resp, eps, mc = args
    rows, crow, irow = [], [], []
    ec = window(det, resp)
    for ep in eps:
        t0 = time.time()
        ev = collect(cfg, det, ep, resp, transplant=mc == 'transplant')
        avs = an_variants(ec)
        an = avs[REF_AN]
        F, P, names, out = templates(ev, an, REF_STRUCT)
        d_ref = S.days_to(F, P)
        r = _row(ev, ecut=f'{ec[0]:g}-{ec[1]:g}', days_ref=d_ref)
        _, _, nn, on = templates(ev, an, 'none')
        r['days_none'] = days_from(on, nn)
        r['days_norms_only'] = days_from(on, nn, norms_only=True)
        r.update(raw_counts(ev, an))
        r['days_floor0.3'] = days_floor(ev, an, REF_STRUCT, 0.3)
        r['days_floor1'] = days_floor(ev, an, REF_STRUCT, FLOOR)
        r['days_floor1_none'] = days_floor(ev, an, 'none', FLOOR)
        r['days_floor1_norms_only'] = days_floor(ev, an, 'none', FLOOR, norms_only=True)
        # (b) the two random MC halves (signal and background together, as lnl_nd)
        half = np.random.default_rng(5).random(ev['uid'].max() + 1)[ev['uid']] < 0.5
        for lab, m in (('half_a', half), ('half_b', ~half)):
            r[lab] = days(ev, an, REF_STRUCT, sel=m)[0]
            r[lab + '_floor1'] = days_floor(reweighted(ev, np.where(m, 2.0, 0.0)), an, REF_STRUCT, FLOOR)
        # (c) background (and signal) MC subsamples, reweighted to the same rate
        for which in ('bkg', 'sig'):
            for f in SUB_FRACS:
                dd, dn = [], []
                dfl = []
                for sd in SUB_SEEDS:
                    e2 = reweighted(ev, subsample_mult(ev, f, 100 * sd + int(1 / f), which))
                    dd.append(days(e2, an, REF_STRUCT)[0])
                    if which == 'bkg':
                        _, _, n2, o2 = templates(e2, an, 'none')
                        dn.append(days_from(o2, n2, norms_only=True))
                        if f >= 0.25:
                            dfl.append(days_floor(e2, an, REF_STRUCT, FLOOR))
                if dfl:
                    r[f'sub_bkg_{f:g}_floor1'] = float(np.median(dfl))
                r[f'sub_{which}_{f:g}'] = float(np.median(dd))
                r[f'sub_{which}_{f:g}_lo'], r[f'sub_{which}_{f:g}_hi'] = float(np.min(dd)), float(np.max(dd))
                if dn:
                    r[f'sub_bkg_{f:g}_norms'] = float(np.median(dn))
        # extrapolation: 1/days linear in 1/f (noise-induced information ∝ MC variance)
        for tag, key in (('ref', 'sub_bkg_{}'), ('norms', 'sub_bkg_{}_norms')):
            base = d_ref if tag == 'ref' else r['days_norms_only']
            x = np.array([1.0, 2.0, 4.0])
            yv = 1 / np.array([base, r[key.format(0.5)], r[key.format(0.25)]])
            if np.all(np.isfinite(yv)):
                b1, b0 = np.polyfit(x, yv, 1)
                r[f'days_inf_{tag}'] = 1 / b0 if b0 > 0 else np.inf
                r[f'slope_{tag}'] = b1 / max(b0, 1e-30)
        # (d) KDE bandwidth and coarser binning
        bw0 = N.BW['th']
        for bw in (8.0, 12.0):
            N.BW['th'] = bw
            r[f'days_bw{bw:g}'] = days(ev, an, REF_STRUCT)[0]
        N.BW['th'] = bw0
        for k in ('3D, |y| 3 bins', '3D, E_sum 2 bins', '3D, |y| 3 + E_sum 2 bins'):
            r[f'days_{k}'] = days(ev, avs[k], REF_STRUCT)[0]
        # (f) where the information is
        r.update(info_split(ev, an, REF_STRUCT, out, names))
        rows.append(r)
        # (e) counting
        for yc in (None, 0.3):
            crow.append(_row(ev, ecut=f'{ec[0]:g}-{ec[1]:g}', ycut=yc if yc else 'none', **counting(ev, ec, yc)))
        print(f'mcstat {cfg:20s} {det} {resp:24s} {ep:.0f} {mc:10s}: ref {d_ref:.3g}, halves {r["half_a"]:.3g}/{r["half_b"]:.3g}, '
              f'bkg 1/2,1/4,1/8 {r["sub_bkg_0.5"]:.3g},{r["sub_bkg_0.25"]:.3g},{r["sub_bkg_0.125"]:.3g} '
              f'-> inf {r.get("days_inf_ref", np.nan):.3g} ({time.time() - t0:.0f} s)', flush=True)
    return rows, crow, irow


PARTS = Path(os.environ.get('SHAPES_ND_PARTS', _W / 'shapes_nd_parts'))


def run_pool(fn, tasks, nproc, tag):
    """runs fn over tasks with nproc workers (one task per worker life: memory is returned), saving each
    result under PARTS/<tag>/ as it arrives; tasks already saved are not rerun (resume)."""
    import multiprocessing as mp
    import pickle
    # the inputs are part of the key: a rerun with other MC tables never picks up stale parts
    tag = tag + (f"_x{'+'.join(EXTRA_RUNS)}" if EXTRA_RUNS else '') + (f'_r{zlib.crc32(repr(sorted(RUNS.items())).encode()):08x}' if RUNS else '')
    d = PARTS / tag
    d.mkdir(parents=True, exist_ok=True)
    fn_of = {t: d / (f'{zlib.crc32(repr(t).encode()):08x}.pkl') for t in tasks}
    todo = [t for t in tasks if not fn_of[t].exists()]
    print(f'{tag}: {len(tasks) - len(todo)} of {len(tasks)} tasks already done', flush=True)
    if nproc <= 1:
        for t in todo:
            fn_of[t].write_bytes(pickle.dumps(fn(t)))
    else:
        with mp.get_context('fork').Pool(nproc, maxtasksperchild=1) as p:
            for t, r in p.imap_unordered(_tagged(fn), todo, chunksize=1):
                fn_of[t].write_bytes(pickle.dumps(r))
    return [pickle.loads(fn_of[t].read_bytes()) for t in tasks]


class _tagged:
    def __init__(self, fn):
        self.fn = fn

    def __call__(self, t):
        return t, self.fn(t)


# --------------------------------------------------------------------------- #
# the opt_geant fit behind geant_reach.csv, dissected
# --------------------------------------------------------------------------- #
def og_setup(det):
    SG.setup(det)
    OG.RESP = REF_RESP
    OG._CACHE.clear()
    OG._LEV.clear()


def og_neff(tag, ec, T):
    """per-bin effective background MC count of opt_geant's templates (all background kinds)."""
    W, W2 = 0.0, 0.0
    y = OG.film_yields(OG.CONFIGS[tag][2])
    f17, g1r = y['f17'], y['Y_g1'] / y['Y_g0']
    for kind in ('M1', 'E1', 'g1M1', 'g1E1', 'epc', 'cos'):
        z = OG.load(kind, tag)
        m = OG.mask(z, ec)
        one = np.ones(len(z['reco']))
        if kind == 'epc':
            L = z['inv_mass']
            per = np.select([np.isclose(L, 18.15, atol=1e-3), np.isclose(L, 17.64, atol=1e-3),
                             np.isclose(L, 15.1, atol=1e-3), np.isclose(L, 14.6, atol=1e-3)],
                            [1 - f17, f17, g1r * (1 - f17), g1r * f17], 0.0)
            w = T['ng0'] * per / (z['ngen'] / 4)
        else:
            cnt = OG.hist4(z, m, one, True)
            w = one * (T[kind].sum() / max(cnt.sum(), 1e-30))
        W = W + OG.hist4(z, m, w, True)
        W2 = W2 + OG.hist4(z, m, w ** 2, True)
    return np.where(W2 > 0, W ** 2 / np.maximum(W2, 1e-300), 0.0)[:, OG.FIT].ravel()


def og_days_sub(T):
    s = T['x17'][:, OG.FIT].ravel()
    comps = [T[k][:, OG.FIT].ravel() for k in ('M1', 'E1', 'g1', 'epc')]
    b = sum(comps) + T['cos'][:, OG.FIT].ravel()
    return s, comps, b


def og_fisher(s, comps, b, keep=None):
    keep = np.ones(len(s), bool) if keep is None else keep
    sig = G.fisher_sigma(s[keep], [c[keep] for c in comps], (s + b)[keep])
    return 9 * sig ** 2


def og_task(args):
    cfg, det, ep = args
    og_setup(det)
    OG.EP = ep
    tag = f'{cfg}_{det}'
    best = None
    for ec in OG.ECUTS:
        T = OG.templates(tag, ec)
        d = OG.fisher_days(T)
        if best is None or d < best[0]:
            best = (d, ec, T)
    d0, ec, T = best
    all_w = sorted(OG.fisher_days(OG.templates(tag, e)) for e in OG.ECUTS)
    s, comps, b = og_days_sub(T)
    neff = og_neff(tag, ec, T)
    i_s = np.where(s + b > 0, s ** 2 / np.where(s + b > 0, s + b, 1), 0.0)
    r = dict(config=cfg, det=det, Ep_keV=ep, ecut=f'{ec[0]}-{ec[1]}', days_fit=d0, S=s.sum(), B=b.sum(),
             sig_in_empty_bkg=float(s[b <= 0].sum() / s.sum()), info_in_empty_bkg=float(i_s[b <= 0].sum() / i_s.sum()),
             days_no_empty=og_fisher(s, comps, b, b > 0), days_2nd_best_window=all_w[1],
             days_median_window=float(np.median(all_w)))
    for t in (1, 3, 10, 30):
        low = neff < t
        r[f'infofrac_neq<{t}'] = float(i_s[low].sum() / i_s.sum())
        r[f'sigfrac_neq<{t}'] = float(s[low].sum() / s.sum())
        r[f'days_drop_neq<{t}'] = og_fisher(s, comps, b, ~low)
    # the background templates from MC subsamples (reweighted), and signal subsamples
    orig_mask = OG.mask
    for which in ('bkg', 'sig'):
        for f in SUB_FRACS:
            dd = []
            for sd in SUB_SEEDS:
                def sub_mask(z, ec_, _f=f, _sd=sd):
                    m = orig_mask(z, ec_)
                    is_sig = 'X17' in z['name']
                    is_cos = 'cosmic' in z['name']
                    if is_cos or (is_sig != (which == 'sig')):
                        return m
                    u = np.random.default_rng(_sd * 1000 + zlib.crc32(z['name'].encode()) % 1000).random(len(m))
                    return m & (u < _f)
                OG.mask = sub_mask
                try:
                    T2 = OG.templates(tag, ec)
                finally:
                    OG.mask = orig_mask
                ks = ('x17',) if which == 'sig' else ('M1', 'E1', 'g1M1', 'g1E1', 'epc')
                for k in ks:
                    T2[k] = T2[k] / f
                T2['g1'] = T2['g1M1'] + T2['g1E1']
                dd.append(OG.fisher_days(T2))
            r[f'sub_{which}_{f:g}'] = float(np.median(dd))
            r[f'sub_{which}_{f:g}_lo'], r[f'sub_{which}_{f:g}_hi'] = float(np.min(dd)), float(np.max(dd))
    x = np.array([1.0, 2.0, 4.0])
    yv = 1 / np.array([d0, r['sub_bkg_0.5'], r['sub_bkg_0.25']])
    b1, b0 = np.polyfit(x, yv, 1)
    r['days_inf'] = 1 / b0 if b0 > 0 else np.inf
    # the fixed reference window of the baseline (no window optimisation)
    print(f"og {cfg:20s} {det} {ep:.0f}: {d0:.3g} d at {r['ecut']}; info in empty-bkg bins {r['info_in_empty_bkg']:.2f}, "
          f"without them {r['days_no_empty']:.3g}; bkg 1/2,1/4,1/8: {r['sub_bkg_0.5']:.3g}, {r['sub_bkg_0.25']:.3g}, "
          f"{r['sub_bkg_0.125']:.3g} -> inf {r['days_inf']:.3g}", flush=True)
    return r



# --------------------------------------------------------------------------- #
# stage 2 (2026-11-10): cosmic-rejection level × beam mode, and the other beam energies
# --------------------------------------------------------------------------- #
#: extra analysis levels, added to lnl_geant.LEVELS at run time (register_levels; the module source is untouched).
#: 'mu_seg': the cosmic sample's segment directions are smeared by mu_seg instead of seg before the pointing and
#: collinearity cuts; the pointing distance D (seg_D(seg)) and the beam samples' smearing stay those of seg.
EXTRA_LEVELS = {
    'MM 15° point, μ 3°': dict(seg=15.0, tof=None, mu_seg=3.0),
    'MM 15° point, μ 3° + TOF': dict(seg=15.0, tof=G.TOF_SIGMA_NS, mu_seg=3.0),
    'MM 15° + TOF 1 ns': dict(seg=15.0, tof=1.0),
    'MM 3° + TOF 1 ns': dict(seg=3.0, tof=1.0),
    'MM 15° point, μ 3° + TOF 1 ns': dict(seg=15.0, tof=1.0, mu_seg=3.0),
}
MODE_LEVELS = ['trigger', 'MM 15°', 'MM 3°', 'MM 15° + TOF', 'MM 3° + TOF', 'MM 15° point, μ 3°',
               'MM 15° point, μ 3° + TOF', 'MM 15° + TOF 1 ns', 'MM 3° + TOF 1 ns', 'MM 15° point, μ 3° + TOF 1 ns']
#: (label, I_uA, cos_scale)
MODES = [('cont 0.7', 0.7, 1.0), ('cont 1.0', 1.0, 1.0), ('cont 2.0', 2.0, 1.0), ('cont 4.0', 4.0, 1.0),
         ('pulsed 0.7, 6/333', 0.7, 6 / 333), ('pulsed 0.35, 6/333', 0.35, 6 / 333),
         ('pulsed 0.7, 20/333', 0.7, 20 / 333), ('pulsed 0.35, 20/333', 0.35, 20 / 333)]
#: cosmic-rate multipliers k for the break-even scan (cont 1.0 vs pulsed 0.7, 6/333, both with cosmics × k)
K_SCAN = (3.0, 10.0, 30.0, 100.0)
LIVE_S2 = 0.95
MODE_CFGS = ['ogCu200', 'ogCu200_los', 'ogAl300cu12r8m4']
MODE_RESPS = {'asb': ['n_TOF as is', 'LNL calibrated', 'LNL calibrated, LS off'], 'bigP': ['LNL calibrated']}
SIG_WIN = dict(th=(125.0, 160.0), y=0.6)     # the "signal window" for the per-row S, B numbers (E_sum: the fit window)
_G_SELECT0 = G.select


def _pass_seg_mu(z, lv, seed):
    """lnl_geant.pass_seg with D = seg_D(lv['seg']) but the directions smeared by lv['mu_seg'] (same rng use)."""
    c1, d1, c2, d2 = z['c_dom1'], z['d_dom1'], z['c_dom2'], z['d_dom2']
    D = G.seg_D(lv['seg'])
    rng = np.random.default_rng(seed)
    ok = np.isfinite(d1).all(1) & np.isfinite(d2).all(1)
    s1 = G.smear_dir(np.where(np.isfinite(d1), d1, 1.0), lv['mu_seg'], rng)
    s2 = G.smear_dir(np.where(np.isfinite(d2), d2, 1.0), lv['mu_seg'], rng)
    c1 = np.where(np.isfinite(c1), c1, 0.0)
    c2 = np.where(np.isfinite(c2), c2, 0.0)
    ok &= (G.dca0(c1, s1) < D) & (G.dca0(c2, s2) < D)
    ok &= G.line_angle(s1, s2) >= G.COLL_DEG
    return ok


def select_mu(z, level, ecut, seed=11):
    """lnl_geant.select, except that for levels with 'mu_seg' the cosmic tables use _pass_seg_mu."""
    lv = G.LEVELS[level]
    if lv.get('mu_seg') is None or z is None or len(z['reco_c']) == 0 or 'cosmic' not in str(z['name']):
        return _G_SELECT0(z, level, ecut, seed)
    key = (z['name'], level, seed)
    if key not in G._SEG:
        G._SEG[key] = _pass_seg_mu(z, lv, seed) & G.pass_tof(z, lv, seed)
    return G._SEG[key] & (z['Esum'] > ecut[0]) & (z['Esum'] < ecut[1])


def register_levels():
    for k, v in EXTRA_LEVELS.items():
        G.LEVELS.setdefault(k, v)
    G.select = select_mu


def _drop_tables():
    """memory: the event table is built; drop the per-sample tables (they are rebuilt per level anyway)."""
    import gc
    _TAB.clear()
    G._CACHE.clear()
    G._SEG.clear()
    gc.collect()


def _shrink(ev):
    """memory: the cached structure-mode values per event as float32 (they only weight histograms)."""
    for k in list(ev):
        if isinstance(k, tuple) and k[0] == '_sw':
            ev[k] = ev[k].astype(np.float32)


def mode_numbers(ev, ec):
    """S, beam B, cosmic B per day and the cosmic MC count, in the fit sample and in the signal window."""
    an = N.analyses(ec)[REF_AN]
    b = N.Binner(an, ev['v0'], False)
    v = ev['v0']
    win = b.m & (v['th'] >= SIG_WIN['th'][0]) & (v['th'] < SIG_WIN['th'][1]) & (v['y'] < SIG_WIN['y']) \
        & (v['E'] > ec[0]) & (v['E'] < ec[1])
    g = ev['grp']
    out = {}
    for lab, m in (('fit', b.m), ('win', win)):
        out[f'S_{lab}'] = float(ev['w'][m & (g == 'sig')].sum())
        out[f'Bbeam_{lab}'] = float(ev['w'][m & (g != 'sig') & (g != 'cos')].sum())
        out[f'Bcos_{lab}'] = float(ev['w'][m & (g == 'cos')].sum())
        out[f'n_mc_cos_{lab}'] = int(len(np.unique(ev['uid'][m & (g == 'cos')])))
    return out


def _fit_pair(ev, an):
    _, _, names, out = templates(ev, an, REF_STRUCT)
    return days_from(out, names), days_from(out, names, mu_floor=mu_floor_of(ev, an, FLOOR))


def task_modes(args):
    cfg, det, resp, mc = args
    register_levels()
    rows = []
    ecs = [window(det, resp)] + ([(11, 17)] if resp == 'LNL calibrated, LS off' else [])
    er = (min(e[0] for e in ecs) - 4, max(e[1] for e in ecs))   # memory: only the E range the windows need
    for level in MODE_LEVELS:
        t0 = time.time()
        ev = collect(cfg, det, 1100.0, resp, level=level, I_uA=1.0, cos_scale=1.0, live=LIVE_S2,
                     transplant=mc == 'transplant', erange=er)
        _drop_tables()
        templates(ev, N.analyses(ecs[0])[REF_AN], REF_STRUCT)        # fills the structure cache in ev
        _shrink(ev)
        g = ev['grp']
        for ec in ecs:
            an = N.analyses(ec)[REF_AN]
            modes = [(lab, I, c, 1.0) for lab, I, c in MODES]
            if det == 'asb':
                modes += [(f'{lab} cos×{k:g}', I, c * k, k) for k in K_SCAN for lab, I, c in
                          (('cont 1.0', 1.0, 1.0), ('pulsed 0.7, 6/333', 0.7, 6 / 333))]
            for lab, I, c, k in modes:
                e2 = reweighted(ev, np.where(g == 'cos', c, I))
                d_raw, d_fl = _fit_pair(e2, an)
                rows.append(dict(config=cfg, det=det, resp=resp, mc=mc, level=level, ecut=f'{ec[0]:g}-{ec[1]:g}',
                                 mode=lab, I_uA=I, cos_scale=c, cos_k=k, live=LIVE_S2, days_floor1=d_fl, days_raw=d_raw,
                                 **mode_numbers(e2, ec)))
        r = [x for x in rows if x['level'] == level and x['mode'] == 'cont 1.0' and x['ecut'] == f'{ecs[0][0]:g}-{ecs[0][1]:g}']
        print(f'modes {cfg:16s} {det} {resp:24s} {mc:10s} {level:30s}: cont 1.0 {r[0]["days_floor1"]:.3g} d, '
              f'cos/day {r[0]["Bcos_fit"]:.3g} ({r[0]["n_mc_cos_fit"]} MC) ({time.time() - t0:.0f} s)', flush=True)
        del ev
    return rows


ENERGIES = (441.0, 800.0, 1030.0, 1100.0, 1225.0)
THIN = ((800.0, 267.0), (800.0, 534.0), (1225.0, 267.0), (1225.0, 534.0))     # (E_p, Li µg/cm²): 5 and 10 µm
ENERGY_RESPS = {'asb': ['n_TOF as is', 'LNL calibrated'], 'bigP': ['LNL calibrated']}


def task_energies(args):
    cfg, det, resp, mc = args
    rows = []
    ec = window(det, resp)
    an = N.analyses(ec)[REF_AN]
    for ep, li in [(e, None) for e in ENERGIES] + list(THIN):
        ev = collect(cfg, det, ep, resp, level=REF_LEVEL, I_uA=1.0, live=LIVE_S2, transplant=mc == 'transplant', li_ug=li,
                     erange=(ec[0] - 4, ec[1]))
        m = ev['meta']
        d_raw, d_fl = (np.nan, np.nan) if ep < 500 else _fit_pair(ev, an)
        b = N.Binner(an, ev['v0'], False)
        g, comp = ev['grp'], ev['comp']
        r = dict(config=cfg, det=det, resp=resp, mc=mc, Ep_keV=ep, li_um=20.0 if li is None else li / 53.4,
                 ecut=f'{ec[0]:g}-{ec[1]:g}', days_floor1=d_fl, days_raw=d_raw, g0_per_day=m['g0_per_day'],
                 Y_g0=m['y_Y_g0'], f17=m['y_frac_17_64'], f18res=m['y_frac_18_15_res'], fdc=m['y_frac_direct'],
                 Y_g1=m['y_Y_g1'], x17_norm_per_day=m['g0_per_day'] * LIVE_S2 * (1 - m['y_frac_17_64']) * S.R_ATOMKI,
                 **{f'rate_{c}': float(ev['w'][b.m & (comp == c)].sum()) for c in ('sig', 'M1', 'E1', 'g1', 'epc', 'cos')},
                 pairs_beam_per_day=float(ev['w'][b.m & (g != 'sig') & (g != 'cos')].sum()),
                 **{k: v for k, v in mode_numbers(ev, ec).items()})
        rows.append(r)
        print(f'energies {cfg:16s} {det} {resp:16s} {mc:10s} {ep:.0f} {r["li_um"]:.0f} um: {d_fl:.3g} d, '
              f'beam pairs {r["pairs_beam_per_day"]:.3g}/d', flush=True)
    return rows


# --------------------------------------------------------------------------- #
def vertex_check():
    """σ68 of the X17 residual about (0,0,0) vs about the median vertex, as built, MM 15° + TOF."""
    rows = []
    for cfg in ('ogCu200', 'ogAl300cu12r8m4', 'win45d200'):
        for det in ('asb', 'bigP'):
            z = table(cfg, 'x17', det, 'ideal')
            m = G.select(z, REF_LEVEL, (-1e9, 1e9))
            vy = float(np.median(z['V'][:, 1]))
            for lab, v in (('origin', np.zeros(3)), ('median vertex', np.array([0, vy, 0]))):
                a, b = z['c_all1'] - v, z['c_all2'] - v
                c = (a * b).sum(1) / np.linalg.norm(a, axis=1) / np.linalg.norm(b, axis=1)
                d = (np.degrees(np.arccos(np.clip(c, -1, 1))) - z['theta'])[m]
                q = np.percentile(d, [16, 50, 84])
                rows.append(dict(config=cfg, det=det, vertex=lab, vy=vy if lab != 'origin' else 0.0,
                                 sigma68=0.5 * (q[2] - q[0]), bias=q[1]))
    return pd.DataFrame(rows)


def validate():
    rows = []
    t = time.time()
    for det in ('bigP', 'asb'):
        hw = SG.DETS[det]
        ec = window(det, REF_RESP)
        an = N.analyses(ec)[REF_AN]
        # V1: lnl_nd unmodified (scenario 'ATOMKI 2016 anomaly', m 16.7, its windows and erange)
        C.set_response(REF_RESP, sigma_g='auto')
        S.HWS[hw] = (ec, C.HWS0[hw][1])
        ev = N.collect(hw, erange=(ec[0] - 4, ec[1]))
        S.HWS[hw] = C.HWS0[hw]
        F, P, _, o = N.fisher_nd(ev, an, N.STRUCTS[REF_STRUCT], sigma_g=S.PRIOR_G)
        rows.append(dict(det=det, case='V1 lnl_nd as is (m 16.7, yields.csv, L7 IPC)', days=S.days_to(F, P),
                         S=o['S'], B=o['B']))
        cases = [('V2 shapes_nd base, m 16.7, yields.csv, lnl_nd erange', dict(cfg='base', mx='16.7', ysrc='syst', erange=(ec[0] - 4, ec[1]))),
                 ('V3 ... wide E range 7-22', dict(cfg='base', mx='16.7', ysrc='syst')),
                 ('V4 ... target_model yields', dict(cfg='base', mx='16.7')),
                 ('V5 ... X17 m 16.8 (= main-table base)', dict(cfg='base')),
                 ('V6 base_L2: shapes_geant inputs (L2 IPC, x20 EPC, 17.64/14.6 substituted)', dict(cfg='base_L2'))]
        for lab, kw in cases:
            cfg = kw.pop('cfg')
            ev = collect(cfg, det, 1100.0, REF_RESP, **kw)
            d, o = days(ev, an, REF_STRUCT)
            dn, _ = days(ev, an, 'none')
            _, _, nn, on = templates(ev, an, 'none')
            rows.append(dict(det=det, case=lab, days=d, days_none=dn, days_norms_only=days_from(on, nn, norms_only=True),
                             S=o['S'], B=o['B']))
        print(pd.DataFrame(rows).to_string(), f'({time.time() - t:.0f} s)', flush=True)
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('what', choices=['validate', 'main', 'mcstat', 'og', 'vertex', 'modes', 'energies', 'all'])
    ap.add_argument('-j', type=int, default=4)
    ap.add_argument('--extra-run', nargs='*', default=[])
    ap.add_argument('--configs', nargs='*', default=None)
    ap.add_argument('--suffix', default='')
    ap.add_argument('--det', nargs='*', default=['asb', 'bigP'])
    a = ap.parse_args()
    EXTRA_RUNS.extend(a.extra_run)
    OUT.mkdir(parents=True, exist_ok=True)
    sfx = a.suffix
    cfgs = a.configs or MAIN
    if a.what in ('vertex', 'all'):
        v = vertex_check()
        v.to_csv(OUT / f'nd_vertex{sfx}.csv', index=False)
        print(v.to_string())
    if a.what in ('validate', 'all'):
        validate().to_csv(OUT / f'nd_validate{sfx}.csv', index=False)
    if a.what in ('main', 'all'):
        tasks = [(c, det, r) for det in a.det for c in cfgs for r in RESPS[det]]
        res = run_pool(task_main, tasks, a.j, 'main' + sfx)
        pd.DataFrame([r for x in res for r in x[0]]).to_csv(OUT / f'nd_days{sfx}.csv', index=False)
        pd.DataFrame([r for x in res for r in x[1]]).to_csv(OUT / f'nd_windows{sfx}.csv', index=False)
    if a.what in ('mcstat', 'all'):
        tasks = [(c, 'asb', r, EP_LIST, mc) for c in cfgs for r in RESPS['asb'] for mc in MCS(c, 'asb')]
        tasks += [(c, 'bigP', r, (1100.0,), mc) for c in cfgs if c in ('base', 'ogCu200', 'ogAl300cu12r8m4')
                  for r in RESPS['bigP'] for mc in MCS(c, 'bigP')]
        tasks = [t for t in tasks if t[1] in a.det]
        tasks.sort(key=lambda t: t[4] != 'transplant')      # the slow ones first
        res = run_pool(task_mcstat, tasks, a.j, 'mcstat' + sfx)
        pd.DataFrame([r for x in res for r in x[0]]).to_csv(OUT / f'nd_mcstat{sfx}.csv', index=False)
        pd.DataFrame([r for x in res for r in x[1]]).to_csv(OUT / f'nd_counting{sfx}.csv', index=False)
    if a.what == 'modes':
        cf = a.configs or MODE_CFGS
        tasks = [(c, det, r, mc) for det in a.det for c in cf for r in MODE_RESPS[det] for mc in ('direct', 'transplant')]
        tasks.sort(key=lambda t: (t[1] != 'bigP', t[3] != 'transplant'))     # the slow ones first
        res = run_pool(task_modes, tasks, a.j, 'modes' + sfx)
        pd.DataFrame([r for x in res for r in x]).to_csv(OUT / f'nd_modes{sfx}.csv', index=False)
    if a.what == 'energies':
        cf = a.configs or MODE_CFGS
        tasks = [(c, det, r, mc) for det in a.det for c in cf for r in ENERGY_RESPS[det] for mc in ('direct', 'transplant')]
        tasks.sort(key=lambda t: (t[1] != 'bigP', t[3] != 'transplant'))
        res = run_pool(task_energies, tasks, a.j, 'energies' + sfx)
        pd.DataFrame([r for x in res for r in x]).to_csv(OUT / f'nd_energies{sfx}.csv', index=False)
    if a.what in ('og', 'all'):
        tasks = [(c, det, ep) for det in ('asb', 'bigP') for c in cfgs if c != 'base_L2' for ep in EP_LIST]
        res = run_pool(og_task, tasks, a.j, 'og' + sfx)
        pd.DataFrame(res).to_csv(OUT / f'nd_og_diag{sfx}.csv', index=False)


if __name__ == '__main__':
    main()
