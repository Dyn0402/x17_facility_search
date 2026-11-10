#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bham_nd.py -- Monte-Carlo-statistics checks of the Birmingham reach (bham_geant.py, TARGET_GEANT.md §4) and the
same reach with a floating background shape (the LNL reference fit, lnl/sim/lnl_nd.py, FEASIBILITY_SIM.md §14.3).
2026-11-10.

    WORK_DATA=/media/ucla/work ~/PycharmProjects/nTof_x17/.venv/bin/python birmingham/geant/bham_nd.py all
    ... bham_nd.py repro | mcstat | nd | resp        # -> birmingham/out/geant/combo/nd_*.csv

Reads the tables from $BHAM_SEL (default $WORK_DATA/x17_facility_search/bham_sel) and the L4 cosmics from
$BHAM_LSEL (default .../lnl_sel_v3), the 'combo' wall (Pb + BPE exit, the headline), and the DAQ exposure from
out/geant/combo/daq_live.csv.  bham_geant.py and bham_common.py are used unmodified: this script sets their
module paths at run time and swaps bham_geant.recon for recon2 (the same code, same random streams, plus the
arm energies, arms and true θ that the nuisances need; `repro` checks that the days are unchanged).

How each template is built in bham_geant (and here):
  x17    B1 X17 rows passing pointing + collinearity + TOF and the E_sum window; plain 2° histogram
  E1/M1  B1 IPC rows, same cuts; KDE (5°) in θ per (|y|, n_down) category; norm free (E1)
  cos    L4 cosmics (LNL run, same arms), same cuts; KDE; fixed
  beam   every two-arm row of B2/B3 (cell), R3 room rows (c30 run, scaled by beam area) and R2 wall rows, at its own
         θ, |y|, n_down, with NO cut applied to it: weight × (pooled fraction passing pointing + TOF) × (pooled
         fraction in the E_sum window), pooled over the five targets per source; KDE; norm free
Fit: Asimov/Fisher, μ = s + b, bins θ ≥ 90° (2°) × |y| (6) × n_down (3).

The floating-shape fit (fisher): r, E1 norm, beam norm free; cosmics fixed; θ-resolution scale k ±10 % (IPC rows,
which carry the true θ); E_sum scale ±2 % and per-arm gains (σ_g of the response) on the rows that carry arm
energies (IPC, cosmics); acceptance cubic in θ (free) and |y| tilt (P1, P2, ±5 %) on all background; GP structure
(lnl_nd.struct_weights, unit priors) on all background.  Optional E_sum axis: 4 bins [lo−4, lo−2, lo, lo+3, hi].
MC safety: background floored at FLOOR MC event-equivalents per bin (as lnl/target/shapes/shapes_nd.mu_floor_of).
"""
from __future__ import annotations

import os
import sys

for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bham_common as C        # noqa: E402

_W = Path(os.environ.get('WORK_DATA', '/media/ucla/work')) / 'x17_facility_search'
C.SEL = Path(os.environ.get('BHAM_SEL', _W / 'bham_sel'))
C.LSEL = Path(os.environ.get('BHAM_LSEL', _W / 'lnl_sel_v3'))
C.WALL = 'combo'
C.OUT = C.OUT / 'combo'        # read only here (daq_live.csv); every output of this script is nd_*.csv
OUTD = C.OUT

import bham_geant as BG        # noqa: E402
import lnl_nd as N             # noqa: E402

G, LC, S = BG.G, BG.LC, N.S
FLOOR = 1.0
TH_B = np.arange(90, 181, 2.0)
YB = np.r_[BG.YB[:-1], 1.0001]
NDB = np.array([-0.5, 0.5, 1.5, 2.5])
E_FINE = np.r_[np.arange(0, 31, 1.0), 99.0]
K_STEP, E_STEP, G_STEP = 0.15, 0.03, 0.03
PRIOR = dict(k=0.10, e=0.02, yt1=0.05, yt2=0.05)
STRUCTS = dict(N.STRUCTS)
STRUCTS['S_θ 5 % + S_θy 5 %, ℓ/2'] = [('S_θ', 0.05, 0.5), ('S_θy', 0.05, 0.5)]
STRUCTS['S_θE 5 %, ℓ/2'] = [('S_θE', 0.05, 0.5)]
ST_LIST = ['none', 'S_θ 2 %', 'S_θy 2 %', 'S_θ 2 % + S_θy 1 %', 'S_θE 2 %', 'S_θ 5 %, ℓ/2', 'S_θy 5 %, ℓ/2',
           'S_θE 5 %, ℓ/2', 'S_θ 5 % + S_θy 5 %, ℓ/2']


# --------------------------------------------------------------------------- #
# bham_geant.recon with the extra per-row outputs (identical random streams)
# --------------------------------------------------------------------------- #
def recon2(z, hw, target, D=None, seed=0, tof=True):
    rng = np.random.default_rng(seed)
    z = LC.respond(dict(z, Esum=z['E1'] + z['E2'], name=z.get('name', 'x')), hw, BG.RESP, seed=seed)
    det = 'bigP' if hw == 'big plastics' else 'asb'
    if BG.PILEUP.get((target, det)):
        E = BG.add_pileup(np.stack([z['E1'], z['E2']], 1).astype(float), BG.PILEUP[(target, det)], rng)
        z = dict(z, E1=E[:, 0], E2=E[:, 1])
    d1, d2 = z['d_dom1'].astype(float), z['d_dom2'].astype(float)
    good = np.isfinite(d1).all(1) & np.isfinite(d2).all(1)
    s1 = G.smear_dir(np.where(np.isfinite(d1), d1, 1.0), BG.SEG_DEG, rng)
    s2 = G.smear_dir(np.where(np.isfinite(d2), d2, 1.0), BG.SEG_DEG, rng)
    c1 = np.where(np.isfinite(z['c_dom1']), z['c_dom1'], 0.0).astype(float)
    c2 = np.where(np.isfinite(z['c_dom2']), z['c_dom2'], 0.0).astype(float)
    y1, r1 = BG.axis_point(c1, s1)
    y2, r2 = BG.axis_point(c2, s2)
    lo, hi = C.GAS_Y.get(target, (-200.0, 200.0))
    yv = np.clip(np.nan_to_num(0.5 * (y1 + y2)), lo, hi)
    v = np.zeros((len(yv), 3))
    v[:, 1] = yv
    a, b = z['c_all1'].astype(float) - v, z['c_all2'].astype(float) - v
    cs = (a * b).sum(1) / (np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1))
    th = np.degrees(np.arccos(np.clip(cs, -1, 1)))
    rr = np.maximum(np.nan_to_num(r1, nan=1e9), np.nan_to_num(r2, nan=1e9))
    ok = good & (G.line_angle(s1, s2) >= G.COLL_DEG)
    ok_pt = ok.copy()
    if D is not None:
        ok &= rr < D
    ok_ptg = ok.copy()
    if tof:
        ok &= G.pass_tof(z, G.LEVELS['MM 15° + TOF'], seed)
    E1, E2 = z['E1'], z['E2']
    nd = (z['c_all1'][:, 1] > yv).astype(int) + (z['c_all2'][:, 1] > yv).astype(int)
    n = len(yv)
    return dict(th=th, absy=np.abs(E1 - E2) / np.maximum(E1 + E2, 1e-9), ndown=nd, Es=E1 + E2, ok=ok, rr=rr,
                yv=yv, ytrue=z['V'][:, 1] if 'V' in z else np.zeros(n),
                E1=np.asarray(E1, float), E2=np.asarray(E2, float),
                a1=np.asarray(z['a1'], int) if 'a1' in z else np.full(n, -1),
                a2=np.asarray(z['a2'], int) if 'a2' in z else np.full(n, -1),
                theta=np.asarray(z['theta'], float) if 'theta' in z else np.full(n, np.nan),
                ok_coll=ok_pt, ok_point=ok_ptg, rid=np.arange(n))


BG.recon = recon2
_PU: dict = {}


def setup(det, resp='LNL calibrated', ls_pileup=True):
    """bham_geant's per-target components of one detector set (all five targets: the beam term is pooled)."""
    BG.RESP = resp
    for t in C.TARGETS:
        if (t, det) not in _PU:
            _PU[(t, det)] = BG.pileup_model(t, det)
        m = _PU[(t, det)]
        BG.PILEUP[(t, det)] = m if (ls_pileup or det == 'bigP') else m[:2]
    comps = {t: BG.per_day(t, det) for t in C.TARGETS}
    BG.pool_beam(list(comps.values()), det)
    rs = [c['beam'][0] for c in comps.values() if c is not None and 'beam' in c]
    pool = {}
    src = np.concatenate([r['src'] for r in rs])
    ok = np.concatenate([r['ok'] for r in rs])
    es = np.concatenate([r['Es'] for r in rs])
    for k in np.unique(src):
        m = src == k
        h = np.histogram(es[m], E_FINE)[0] / m.sum()
        pool[k] = dict(f_ok=ok[m].mean(), n=int(m.sum()), n_ok=int(ok[m].sum()), fE=h)
    return comps, pool


def exposure(t, det):
    d = pd.read_csv(OUTD / 'daq_live.csv')
    return float(d[(d.target == t) & (d.det == det)].exposure.iloc[0])


def best_window(comp, det, expo):
    best = None
    for ec in BG.ECUTS:
        d = BG.fisher_days(BG.templates(comp, ec, expo, det))
        if best is None or d < best[0]:
            best = (d, ec)
    return best


# --------------------------------------------------------------------------- #
# the event table
# --------------------------------------------------------------------------- #
def events(comp, pool, det, expo, erange, beam_scale=1.0, beam_fok=None, beam_mode='own', resp='LNL calibrated'):
    """every row with its per-day weight.  beam rows are replicated over the E_FINE bins with the pooled
    E fractions (bham_geant's factorisation).  beam_fok: {src: f_ok} overrides of the pooled pass fractions
    (e.g. an upper limit where 0 of n MC rows pass).  Keys: grp, w, wfull (the weight of the whole MC row, for the
    event-equivalent count), uid, and the variable sets v0, k±, e±, g{j}±."""
    P = []
    nid = 0
    for k in ('x17', 'E1', 'M1', 'cos'):
        r, w = comp[k]
        lo, hi = erange[0] - 3, erange[1] + 3
        m = r['ok'] & (r['Es'] > lo) & (r['Es'] < hi)
        ww = (w * (1.0 if k == 'cos' else expo))[m]
        d = dict(grp=np.full(m.sum(), {'x17': 'sig'}.get(k, k)), w=ww, wfull=ww,
                 uid=nid + np.arange(m.sum()), th=r['th'][m], y=r['absy'][m], nd=r['ndown'][m], E=r['Es'][m],
                 E1=r['E1'][m], E2=r['E2'][m], a1=r['a1'][m], a2=r['a2'][m], theta=r['theta'][m],
                 beam=np.zeros(m.sum(), bool))
        nid += m.sum()
        P.append(d)
    if 'beam' in comp:
        r, w = comp['beam']
        n = len(w)
        ec = np.arange(len(E_FINE) - 1)
        f = np.zeros((n, len(ec)))
        for src, pl in pool.items():
            fo = pl['f_ok'] if beam_fok is None or src not in beam_fok else beam_fok[src]
            f[r['src'] == src] = fo * pl['fE'][None, :]
        W = (w * expo * beam_scale)[:, None] * f
        Ec = 0.5 * (E_FINE[1:] + E_FINE[:-1])
        th, y, nd = r['th'], r['absy'], r['ndown']
        if beam_mode != 'own':
            th, y, nd = beam_mode(r)
        keep = W > 0
        ii, jj = np.nonzero(keep)
        d = dict(grp=np.full(len(ii), 'beam'), w=W[ii, jj], wfull=W.sum(1)[ii], uid=nid + ii, th=th[ii], y=y[ii],
                 nd=nd[ii], E=Ec[jj], E1=np.full(len(ii), np.nan), E2=np.full(len(ii), np.nan),
                 a1=np.full(len(ii), -1), a2=np.full(len(ii), -1), theta=np.full(len(ii), np.nan),
                 beam=np.ones(len(ii), bool))
        P.append(d)
    ev = {k: np.concatenate([p[k] for p in P]) for k in P[0]}
    ev['src_n'] = int(len(comp['beam'][1])) if 'beam' in comp else 0
    # variable sets
    th, y, E = ev['th'], ev['y'], ev['E']

    def vs(th_, y_, E_):
        return dict(th=th_, y=y_, E=E_, nd=ev['nd'], m=np.zeros_like(th_))
    ev['v0'] = vs(th, y, E)
    t = ev['theta']
    has_t = np.isfinite(t) & (ev['grp'] != 'sig')
    for sg, k in (('k+', K_STEP), ('k-', -K_STEP)):
        tk = np.where(has_t, t + (1 + k) * (th - t), th)
        tk = np.abs(np.where(tk > 180, 360 - tk, tk))
        ev[sg] = vs(tk, y, E)
    nb = ~ev['beam']
    for sg, e in (('e+', E_STEP), ('e-', -E_STEP)):
        ev[sg] = vs(th, y, np.where(nb, E * (1 + e), E))
    for j in range(4):
        for sg, g in (('+', G_STEP), ('-', -G_STEP)):
            E1 = np.where(nb, ev['E1'] * (1 + g * (ev['a1'] == j)), 0)
            E2 = np.where(nb, ev['E2'] * (1 + g * (ev['a2'] == j)), 0)
            yy = np.where(nb, np.abs(E1 - E2) / np.maximum(E1 + E2, 1e-9), y)
            ev[f'g{j}{sg}'] = vs(th, yy, np.where(nb, E1 + E2, E))
    ev['sigma_g'] = LC.RESP[resp]['sigma_g']
    return ev


def analysis(ec, esum_axis=False, ndown=True, yaxis=True):
    lo, hi = ec
    axes = [('th', TH_B)]
    if yaxis:
        axes.append(('y', YB))
    if ndown:
        axes.append(('nd', NDB))
    if esum_axis:
        eb = np.array([lo - 4, lo - 2, lo, lo + 3, hi], float)
        axes.append(('E', eb))
        return dict(axes=axes, E=(eb[0], eb[-1]))
    return dict(axes=axes, E=(lo, hi))


# --------------------------------------------------------------------------- #
# Fisher
# --------------------------------------------------------------------------- #
def isbkg(grp):
    """the background of the fit: IPC(E1), cosmics, beam (the M1 rows are only an alternative IPC shape)."""
    return (grp == 'E1') | (grp == 'cos') | (grp == 'beam')


def legendre(x, n):
    return [np.ones_like(x), x, 0.5 * (3 * x ** 2 - 1), 0.5 * (5 * x ** 3 - 3 * x)][n]


def fisher(ev, an, struct='none', nuis=True, sel=None, wmult=None, m1=False):
    """the per-day parameter rows g (signal first), the background b and priors.  nuis False: the bham_geant fit
    (r, E1, beam norms only)."""
    w = ev['w'] if wmult is None else ev['w'] * wmult
    if sel is not None:
        w = np.where(sel, w, 0.0)
    grp = ev['grp']
    sm, bk = grp == 'sig', isbkg(grp)
    cache = {}

    def H(key, ww, m, smooth=True):
        ck = (key, smooth)
        if ck not in cache:
            cache[ck] = N.Binner(an, ev[key], smooth)
        return cache[ck].apply(np.where(m, ww, 0.0))
    b = H('v0', w, bk)
    s = H('v0', w, sm, smooth=False)
    rows, names, prior = [s, H('v0', w, grp == 'E1'), H('v0', w, grp == 'beam')], ['r', 'E1', 'beam'], [None] * 3
    if m1:
        rows.append(H('v0', w, grp == 'M1')); names.append('M1'); prior.append(None)
    if nuis:
        def fd(kp, km, st):
            return (H(kp, w, bk) - H(km, w, bk)) / (2 * st)
        rows.append(fd('k+', 'k-', K_STEP)); names.append('k'); prior.append(PRIOR['k'])
        rows.append(fd('e+', 'e-', E_STEP)); names.append('e'); prior.append(PRIOR['e'])
        for j in range(4):
            rows.append(fd(f'g{j}+', f'g{j}-', G_STEP)); names.append(f'gain{j}'); prior.append(ev['sigma_g'])
        v0 = ev['v0']
        xt = (v0['th'] - 135.0) / 45.0
        for n in (1, 2, 3):
            rows.append(H('v0', w * legendre(xt, n), bk)); names.append(f'acc{n}'); prior.append(None)
        xy = 2 * v0['y'] - 1
        for n in (1, 2):
            rows.append(H('v0', w * legendre(xy, n), bk)); names.append(f'yt{n}'); prior.append(PRIOR[f'yt{n}'])
        for st in STRUCTS[struct]:
            kind, delta, ls = (tuple(st) + (1.0,))[:3]
            ck = ('_sw', kind, delta, ls)
            if ck not in ev:
                ev[ck] = N.struct_weights(kind, v0, delta, ls)
            for j, Wm in enumerate(ev[ck]):
                rows.append(H('v0', w * Wm, bk)); names.append(f'{kind}{j}'); prior.append(1.0)
    return dict(g=np.array(rows), b=b, s=s, names=names, prior=prior)


def days_of(f, floor=None, keep=None, beam_free=True):
    g, b, s = f['g'], f['b'], f['s']
    if floor is not None:
        b = np.maximum(b, floor)
    mu = s + b
    ok = mu > mu.max() * 1e-12
    if keep is not None:
        ok &= keep
    rows = [i for i, n in enumerate(f['names']) if beam_free or n != 'beam']
    rows = [i for i in rows if g[i][ok].any() or i == 0]
    gg = g[rows][:, ok]
    F = (gg / mu[ok]) @ gg.T
    pr = [f['prior'][i] for i in rows]
    if all(p is None for p in pr):
        try:
            return 9 * float(np.linalg.inv(F)[0, 0])
        except np.linalg.LinAlgError:
            return np.nan
    P = np.diag([0.0 if p is None else 1 / p ** 2 for p in pr])
    return S.days_to(F, P)


def neq_wbar(ev, an, wmult=None):
    """per bin: background event-equivalents neq = Σ K w / w̄ and the local mean MC-row weight
    w̄ = Σ K w·w_full / Σ K w (w_full: the weight of the whole MC row; beam replicates carry a share of it)."""
    w = ev['w'] if wmult is None else ev['w'] * wmult
    wf = ev['wfull'] if wmult is None else ev['wfull'] * wmult
    bk = isbkg(ev['grp'])
    bn = N.Binner(an, ev['v0'], True)
    hw = bn.apply(np.where(bk, w, 0))
    hk = bn.apply(np.where(bk, w * wf, 0))
    wbar = np.where(hw > 0, hk / np.maximum(hw, 1e-300), 0.0)
    m = bk & (w > 0)
    glob = np.average(wf[m], weights=w[m]) if m.any() else 0.0
    neq = np.where(wbar > 0, hw / np.maximum(wbar, 1e-300), 0.0)
    return neq, np.where(wbar > 0, wbar, glob)


def floor_of(ev, an, nmin=FLOOR, wmult=None):
    return nmin * neq_wbar(ev, an, wmult)[1]


def days_floor(ev, an, struct='none', nuis=False, nmin=FLOOR, wmult=None, sel=None, m1=False):
    wm = wmult
    if sel is not None:
        wm = (np.ones(len(ev['w'])) if wm is None else wm) * sel
    f = fisher(ev, an, struct, nuis, wmult=wm, m1=m1)
    return days_of(f, floor_of(ev, an, nmin, wm))


def info_split(ev, an, f, thresholds=(1, 3, 10)):
    neq, _ = neq_wbar(ev, an)
    s, mu = f['s'], f['s'] + f['b']
    ok = mu > 0
    i_s = np.where(ok, s ** 2 / np.where(ok, mu, 1), 0.0)
    r = {}
    for t in thresholds:
        low = neq < t
        r[f'infofrac_neq<{t}'] = float(i_s[low].sum() / i_s.sum())
        r[f'sigfrac_neq<{t}'] = float(s[low].sum() / s.sum())
        r[f'days_drop_neq<{t}'] = days_of(f, keep=~low)
    return r


def raw_counts(ev, an):
    bn = N.Binner(an, ev['v0'], False)
    r = {}
    for c in ('sig', 'E1', 'cos', 'beam'):
        m = bn.m & (ev['grp'] == c)
        u, inv = np.unique(ev['uid'][m], return_inverse=True)
        w = np.bincount(inv, weights=ev['w'][m]) if len(u) else np.zeros(0)
        r[f'n_{c}'] = len(u)
        r[f'neff_{c}'] = float(w.sum() ** 2 / max((w ** 2).sum(), 1e-300)) if len(u) else 0.0
        r[f'rate_{c}'] = float(w.sum())
    return r


def subsample(ev, frac, seed, which='bkg'):
    u = np.random.default_rng(seed).random(ev['uid'].max() + 1)[ev['uid']]
    tgt = (ev['grp'] == 'sig') if which == 'sig' else isbkg(ev['grp'])
    return np.where(tgt, (u < frac) / frac, 1.0)


def counting(ev, ec):
    an = dict(axes=[('th', TH_B)], E=ec)
    sm = ev['grp'] == 'sig'
    bs = N.Binner(an, ev['v0'], False)
    bkm = isbkg(ev['grp'])
    sig = bs.apply(np.where(sm, ev['w'], 0))
    braw = bs.apply(np.where(bkm, ev['w'], 0))
    bsm = N.Binner(an, ev['v0'], True).apply(np.where(bkm, ev['w'], 0))
    bk = bkm & bs.m
    _, first = np.unique(ev['uid'][bk], return_index=True)
    ib = np.clip(np.digitize(ev['v0']['th'][bk][first], TH_B) - 1, 0, len(TH_B) - 2)
    nmc = np.bincount(ib, minlength=len(TH_B) - 1)
    cs, cb, cr, cn = (np.r_[0, np.cumsum(a)] for a in (sig, bsm, braw, nmc))
    best = None
    for i in range(len(TH_B) - 1):
        if not 100 <= TH_B[i] <= 150:
            continue
        for j in range(i + 4, len(TH_B)):
            Sx, Bx = cs[j] - cs[i], cb[j] - cb[i]
            if Bx > 0 and (best is None or Sx / np.sqrt(Bx) > best[0]):
                best = (Sx / np.sqrt(Bx), i, j)
    _, i, j = best
    Sx, Bx, Br, nB = cs[j] - cs[i], cb[j] - cb[i], cr[j] - cr[i], cn[j] - cn[i]
    return dict(win=f'{TH_B[i]:g}-{TH_B[j]:g}', S=Sx, B_kde=Bx, B_raw=Br, n_mc_B=int(nB),
                days_kde=9 * Bx / Sx ** 2, days_raw=9 * Br / Sx ** 2)


PER_ROW = ('grp', 'w', 'wfull', 'uid', 'th', 'y', 'nd', 'E', 'E1', 'E2', 'a1', 'a2', 'theta', 'beam')
VSETS = ('v0', 'k+', 'k-', 'e+', 'e-') + tuple(f'g{j}{s}' for j in range(4) for s in '+-')


def replace_beam(ev, shape, total, ec, seed=4):
    """a copy of ev whose beam rows are replaced by a smooth stand-in with `total` per day inside the E_sum window
    ec: shape 'cos' (the cosmic rows), 'E1' (the IPC rows: then degenerate with the IPC norm; fit it with
    beam_free=False), 'uniform' (20 000 synthetic rows flat in θ 70-180°, |y| 0-1, n_down 0-2, E inside ec)."""
    keep = np.nonzero(~ev['beam'])[0]
    out = {k: ev[k][keep] for k in PER_ROW}
    vs = {k: {q: ev[k][q][keep] for q in ev[k]} for k in VSETS}
    nid = ev['uid'].max() + 1
    if shape in ('cos', 'E1'):
        ii = np.nonzero(ev['grp'] == shape)[0]
        inw = (ev['E'][ii] > ec[0]) & (ev['E'][ii] < ec[1])
        sc = total / max(ev['w'][ii][inw].sum(), 1e-300)
        add = {k: ev[k][ii] for k in PER_ROW}
        add['w'] = add['w'] * sc
        add['wfull'] = add['wfull'] * sc
        add['uid'] = nid + np.arange(len(ii))
        addv = {k: {q: ev['v0'][q][ii] for q in ev['v0']} for k in VSETS}
    else:
        rng = np.random.default_rng(seed)
        n = 20000
        th = rng.uniform(70, 180, n)
        y = rng.uniform(0, 1, n)
        nd = rng.integers(0, 3, n)
        E = np.full(n, 0.5 * (ec[0] + min(ec[1], 30.0)))
        add = dict(grp=np.full(n, 'beam'), w=np.full(n, total / n * 110 / 90), uid=nid + np.arange(n), th=th, y=y,
                   nd=nd, E=E, E1=np.full(n, np.nan), E2=np.full(n, np.nan), a1=np.full(n, -1), a2=np.full(n, -1),
                   theta=np.full(n, np.nan))
        add['wfull'] = add['w']
        addv = {k: dict(th=th, y=y, E=E, nd=nd, m=np.zeros(n)) for k in VSETS}
    add['grp'] = np.full(len(add['w']), 'beam')
    add['beam'] = np.ones(len(add['w']), bool)
    e2 = dict(ev)
    for k in PER_ROW:
        e2[k] = np.concatenate([out[k], add[k]])
    for k in VSETS:
        e2[k] = {q: np.concatenate([vs[k][q], addv[k][q]]) for q in vs[k]}
    for k in list(e2):
        if isinstance(k, tuple):
            del e2[k]
    return e2


def mc_var(ev, an, wmult=None):
    """σ²_MC of the background per analysis bin: Σ K² w² with the rows of one MC event in one fine bin merged."""
    w = ev['w'] if wmult is None else ev['w'] * wmult
    bk = isbkg(ev['grp'])
    b = N.Binner(an, ev['v0'], True)
    m = b.m & bk
    sel = m[b.m]
    idx = b.idx[sel]
    uid = ev['uid'][m]
    key = uid.astype(np.int64) * (b.nsec * b.nf) + idx
    u, inv = np.unique(key, return_inverse=True)
    ws = np.bincount(inv, weights=w[m])
    h = np.bincount(u % (b.nsec * b.nf), weights=ws ** 2, minlength=b.nsec * b.nf).reshape(b.nsec, b.nf)
    return (h @ (b.K ** 2)).ravel()


def days_bb(f, var, beam_free=True, z=3.0):
    """days to zσ with the background-MC error as a per-bin nuisance (Barlow-Beeston-lite at the Asimov point):
    per-day information g gᵀ / (μ + T σ²_MC) (shapes_nd.days_bb)."""
    g, mu = f['g'], f['s'] + f['b']
    ok = mu > mu.max() * 1e-12
    rows = [i for i, n in enumerate(f['names']) if (beam_free or n != 'beam') and (g[i][ok].any() or i == 0)]
    gg = g[rows][:, ok]
    P = np.diag([0.0 if f['prior'][i] is None else 1 / f['prior'][i] ** 2 for i in rows])

    def zz(T):
        F = (gg / (mu[ok] + T * var[ok])) @ gg.T
        try:
            c = np.linalg.inv(T * F + P)[0, 0]
        except np.linalg.LinAlgError:
            return 0.0
        return 1 / np.sqrt(c) if c > 0 else 0.0
    if zz(1e7) < z:
        return np.inf
    lo, hi = 1e-3, 1e7
    for _ in range(80):
        mid = np.sqrt(lo * hi)
        lo, hi = (lo, mid) if zz(mid) >= z else (mid, hi)
    return hi


# --------------------------------------------------------------------------- #
# tasks
# --------------------------------------------------------------------------- #
CASES =[('c30', 'asb'), ('c30', 'bigP'), ('cap500', 'asb')]
SEEDS = (1, 2, 3, 4, 5, 6)


def repro(resps=('LNL calibrated',)):
    rows = []
    for det in C.DETS:
        for resp in resps:
            comps, pool = setup(det, resp)
            for t in C.TARGETS:
                expo = exposure(t, det)
                d, ec = best_window(comps[t], det, expo)
                ev = events(comps[t], pool, det, expo, ec)
                dn = days_of(fisher(ev, analysis(ec), nuis=False))
                rows.append(dict(target=t, det=det, resp=resp, esum=f'{ec[0]}-{ec[1]}', days_bham_geant=d,
                                 days_event_table=dn))
                print(rows[-1], flush=True)
    return pd.DataFrame(rows)


def beam_report(comps, pool, det, t, expo):
    """the beam rows of target t by source: MC rows, rate before cuts [/day], pooled pass fraction (n_ok / n)."""
    r, w = comps[t]['beam']
    out = []
    for src in np.unique(r['src']):
        m = r['src'] == src
        pl = pool[src]
        out.append(dict(target=t, det=det, src=src, rows_target=int(m.sum()), rate_2arm_per_day=float(w[m].sum() * expo),
                        pooled_rows=pl['n'], pooled_pass=pl['n_ok'], f_ok=pl['f_ok'],
                        f_ok_90UL=2.303 / pl['n'] if pl['n_ok'] == 0 else np.nan,
                        rows_target_pass=int(r['ok'][m].sum()),
                        rows_target_coll=int(r['ok_coll'][m].sum()), rows_target_point=int(r['ok_point'][m].sum())))
    return out


def smooth_beam_flat(r):
    """beam rows spread flat in θ (90-180°), |y| and n_down kept (each row keeps its category)."""
    rng = np.random.default_rng(3)
    return rng.uniform(90, 180, len(r['th'])), r['absy'], r['ndown']


def mcstat(cases=CASES):
    rows, crow, brow = [], [], []
    for det in sorted({d for _, d in cases}):
        comps, pool = setup(det)
        for t, d_ in cases:
            if d_ != det:
                continue
            t0 = time.time()
            expo = exposure(t, det)
            d0, ec = best_window(comps[t], det, expo)
            brow += beam_report(comps, pool, det, t, expo)
            ev = events(comps[t], pool, det, expo, ec)
            an = analysis(ec)
            f = fisher(ev, an, nuis=False)
            r = dict(target=t, det=det, esum=f'{ec[0]}-{ec[1]}', days_bham_geant=d0, days=days_of(f))
            r['days_floor0.3'] = days_of(f, floor_of(ev, an, 0.3))
            r['days_floor1'] = days_of(f, floor_of(ev, an, 1.0))
            r['days_floor3'] = days_of(f, floor_of(ev, an, 3.0))
            r['S_per_day'], r['B_per_day'] = float(f['s'].sum()), float(f['b'].sum())
            r.update(raw_counts(ev, an))
            r.update(info_split(ev, an, f))
            # halves
            half = np.random.default_rng(5).random(ev['uid'].max() + 1)[ev['uid']] < 0.5
            for lab, m in (('half_a', half), ('half_b', ~half)):
                wm = np.where(m, 2.0, 0.0)
                fh = fisher(ev, an, nuis=False, wmult=wm)
                r[lab] = days_of(fh)
                r[lab + '_floor1'] = days_of(fh, floor_of(ev, an, 1.0, wm))
            # subsamples of the background MC
            for fr in (0.5, 0.25, 0.125):
                dd, dfl = [], []
                for sd in SEEDS:
                    wm = subsample(ev, fr, 100 * sd + int(1 / fr))
                    fs = fisher(ev, an, nuis=False, wmult=wm)
                    dd.append(days_of(fs))
                    dfl.append(days_of(fs, floor_of(ev, an, 1.0, wm)))
                r[f'sub_{fr:g}'] = float(np.median(dd))
                r[f'sub_{fr:g}_lo'], r[f'sub_{fr:g}_hi'] = float(np.min(dd)), float(np.max(dd))
                r[f'sub_{fr:g}_floor1'] = float(np.median(dfl))
                r[f'sub_{fr:g}_floor1_lo'], r[f'sub_{fr:g}_floor1_hi'] = float(np.min(dfl)), float(np.max(dfl))
            x = np.array([1.0, 2.0, 4.0, 8.0])
            for tag, key in (('', 'sub_{}'), ('_floor1', 'sub_{}_floor1')):
                base = r['days' if not tag else 'days_floor1']
                yv = 1 / np.array([base] + [r[key.format(g)] for g in (0.5, 0.25, 0.125)])
                b1, b0 = np.polyfit(x, yv, 1)
                r[f'days_inf{tag}'] = 1 / b0 if b0 > 0 else np.inf
            # the beam term
            for lab, kw in (('beam_x0.5', dict(beam_scale=0.5)), ('beam_x2', dict(beam_scale=2.0)),
                            ('beam_x10', dict(beam_scale=10.0)),
                            ('beam_flat_theta', dict(beam_mode=smooth_beam_flat)),
                            ('beam_none', dict(beam_scale=0.0))):
                e2 = events(comps[t], pool, det, expo, ec, **kw)
                f2 = fisher(e2, an, nuis=False)
                r[f'days_{lab}'] = days_of(f2)
                r[f'days_{lab}_floor1'] = days_of(f2, floor_of(e2, an, 1.0))
                r[f'beamrate_{lab}'] = float(f2['g'][2].sum())
            # zero-pass sources at their 90 % upper-limit pass fraction (2.3 / n_rows pooled)
            ul = {src: 2.303 / pl['n'] for src, pl in pool.items() if pl['n_ok'] == 0}
            if ul:
                e2 = events(comps[t], pool, det, expo, ec, beam_fok=ul)
                f2 = fisher(e2, an, nuis=False)
                r['days_beam_UL'] = days_of(f2)
                r['days_beam_UL_floor1'] = days_of(f2, floor_of(e2, an, 1.0))
                r['beamrate_UL'] = float(f2['g'][2].sum())
                e3 = events(comps[t], pool, det, expo, ec, beam_fok=ul, beam_mode=smooth_beam_flat)
                f3 = fisher(e3, an, nuis=False)
                r['days_beam_UL_flat_floor1'] = days_of(f3, floor_of(e3, an, 1.0))
                r['UL_sources'] = '+'.join(f'{k}:{v:.3g}' for k, v in ul.items())
            r['beamrate'] = float(f['g'][2].sum())
            # the MC error as a per-bin nuisance
            r['days_bb'] = days_bb(f, mc_var(ev, an))
            # KDE bandwidth and coarser categories
            bw0 = N.BW['th']
            for bw in (8.0, 12.0):
                N.BW['th'] = bw
                fb = fisher(ev, an, nuis=False)
                r[f'days_bw{bw:g}'] = days_of(fb)
                r[f'days_bw{bw:g}_floor1'] = days_of(fb, floor_of(ev, an, 1.0))
            N.BW['th'] = bw0
            for lab, a2 in (('y3', dict(axes=[('th', TH_B), ('y', np.array([0, 0.3, 0.6, 1.0001])), ('nd', NDB)], E=ec)),
                            ('y6_nonD', analysis(ec, ndown=False)), ('theta_only', analysis(ec, ndown=False, yaxis=False))):
                fb = fisher(ev, a2, nuis=False)
                r[f'days_{lab}'] = days_of(fb)
                r[f'days_{lab}_floor1'] = days_of(fb, floor_of(ev, a2, 1.0))
            # a smooth correlated background at a given level (× the IPC rate in the window), free norm
            ipc = float(fisher(ev, an, nuis=False)['g'][1].sum())
            r['ipc_rate'] = ipc
            for shape in ('cos', 'uniform', 'E1'):
                for lev in (0.03, 0.1, 0.3, 1.0, 3.0, 10.0):
                    e2 = replace_beam(ev, shape, lev * ipc, ec)
                    f2 = fisher(e2, an, nuis=False)
                    r[f'days_smooth_{shape}_{lev:g}xIPC_floor1'] = days_of(f2, floor_of(e2, an, 1.0),
                                                                           beam_free=shape != 'E1')
            rows.append(r)
            crow.append(dict(target=t, det=det, esum=f'{ec[0]}-{ec[1]}', **counting(ev, ec)))
            print(f"mcstat {t} {det}: {d0:.3g} d (bham_geant) {r['days']:.3g} (table), floor1 {r['days_floor1']:.3g}, "
                  f"halves {r['half_a']:.3g}/{r['half_b']:.3g}, sub ½ ¼ ⅛ {r['sub_0.5']:.3g} {r['sub_0.25']:.3g} "
                  f"{r['sub_0.125']:.3g} -> inf {r['days_inf']:.3g}; info neq<1 {r['infofrac_neq<1']:.2f} "
                  f"({time.time() - t0:.0f} s)", flush=True)
    return pd.DataFrame(rows), pd.DataFrame(crow), pd.DataFrame(brow)


def nd(cases=CASES, structs=ST_LIST, resp='LNL calibrated', tag=''):
    rows = []
    for det in sorted({d for _, d in cases}):
        comps, pool = setup(det, resp)
        for t, d_ in cases:
            if d_ != det:
                continue
            t0 = time.time()
            expo = exposure(t, det)
            d0, ec = best_window(comps[t], det, expo)
            ev = events(comps[t], pool, det, expo, (ec[0] - 4, ec[1]), resp=resp)
            ans = {'θ×|y|×n_down (bham_geant)': analysis(ec), 'θ×|y|×n_down×E_sum': analysis(ec, esum_axis=True),
                   'θ×|y|': analysis(ec, ndown=False), 'θ': analysis(ec, ndown=False, yaxis=False)}
            for aname, an in ans.items():
                fl = floor_of(ev, an, FLOOR)
                for st in structs:
                    for m1 in ((False, True) if st in ('none', 'S_θ 2 % + S_θy 1 %') else (False,)):
                        f = fisher(ev, an, st, nuis=st != 'norms', m1=m1)
                        r = dict(target=t, det=det, resp=resp, esum=f'{ec[0]}-{ec[1]}', analysis=aname,
                                 structure=st + (' + M1 free' if m1 else ''), days=days_of(f),
                                 days_floor1=days_of(f, fl), days_floor1_beam_fixed=days_of(f, fl, beam_free=False))
                        rows.append(r)
                fn = fisher(ev, an, nuis=False)
                rows.append(dict(target=t, det=det, resp=resp, esum=f'{ec[0]}-{ec[1]}', analysis=aname,
                                 structure='norms only', days=days_of(fn), days_floor1=days_of(fn, fl),
                                 days_floor1_beam_fixed=days_of(fn, fl, beam_free=False)))
                # halves for the reference structure
                half = np.random.default_rng(5).random(ev['uid'].max() + 1)[ev['uid']] < 0.5
                for lab, m in (('half_a', half), ('half_b', ~half)):
                    wm = np.where(m, 2.0, 0.0)
                    fh = fisher(ev, an, 'S_θ 2 % + S_θy 1 %', wmult=wm)
                    rows.append(dict(target=t, det=det, resp=resp, esum=f'{ec[0]}-{ec[1]}', analysis=aname,
                                     structure=f'S_θ 2 % + S_θy 1 % [{lab}]', days=days_of(fh),
                                     days_floor1=days_of(fh, floor_of(ev, an, FLOOR, wm))))
                print(f'nd {t} {det} {resp} {aname}: ' + ', '.join(
                    f"{x['structure']} {x['days_floor1']:.3g}" for x in rows if x['analysis'] == aname
                    and x['target'] == t and x['det'] == det and x['resp'] == resp) + f' ({time.time() - t0:.0f} s)',
                    flush=True)
    return pd.DataFrame(rows)


def resp_variants():
    rows = []
    for resp, lsp in (('LNL calibrated', True), ('n_TOF as is', True), ('LNL calibrated, LS off', True),
                      ('LNL calibrated, LS off', False)):
        comps, pool = setup('asb', resp, ls_pileup=lsp)
        t = 'c30'
        expo = exposure(t, 'asb')
        d0, ec = best_window(comps[t], 'asb', expo)
        ev = events(comps[t], pool, 'asb', expo, (ec[0] - 4, ec[1]), resp=resp)
        r = dict(target=t, det='asb', resp=resp, ls_pileup=lsp, esum=f'{ec[0]}-{ec[1]}', days_bham_geant=d0)
        for aname, an in (('3D', analysis(ec)), ('4D', analysis(ec, esum_axis=True))):
            fl = floor_of(ev, an, FLOOR)
            fn = fisher(ev, an, nuis=False)
            r[f'{aname}_norms_floor1'] = days_of(fn, fl)
            r[f'{aname}_ref_floor1'] = days_of(fisher(ev, an, 'S_θ 2 % + S_θy 1 %'), fl)
            r[f'{aname}_stress_floor1'] = days_of(fisher(ev, an, 'S_θ 5 % + S_θy 5 %, ℓ/2'), fl)
        f = fisher(ev, analysis(ec), nuis=False)
        r['S_per_day'], r['B_per_day'] = float(f['s'].sum()), float(f['b'].sum())
        r.update(info_split(ev, analysis(ec), f, thresholds=(1,)))
        rows.append(r)
        print(r, flush=True)
    return pd.DataFrame(rows)


NGROUPS = {'k': ('k',), 'e': ('e',), 'gains': ('gain',), 'acc cubic': ('acc',), 'y tilt': ('yt',),
           'S_θ': ('S_θ',), 'S_θy': ('S_θy',)}


def _grp_of(n):
    if n in ('r', 'E1', 'beam', 'M1'):
        return 'norm'
    for g, ps in NGROUPS.items():
        if g == 'S_θ' and n.startswith('S_θy'):
            continue
        if any(n.startswith(p) for p in ps):
            return g
    return '?'


def _sub(f, keep):
    idx = [i for i, n in enumerate(f['names']) if keep(n)]
    return dict(g=f['g'][idx], b=f['b'], s=f['s'], names=[f['names'][i] for i in idx],
                prior=[f['prior'][i] for i in idx])


def breakdown(struct='S_θ 2 % + S_θy 1 %'):
    """which nuisance group costs what in the reference fit (c30, floor 1): norms + one group, all − one group."""
    rows = []
    for det in ('asb', 'bigP'):
        comps, pool = setup(det)
        t = 'c30'
        expo = exposure(t, det)
        _, ec = best_window(comps[t], det, expo)
        ev = events(comps[t], pool, det, expo, (ec[0] - 4, ec[1]))
        for aname, an in (('3D', analysis(ec)), ('4D', analysis(ec, esum_axis=True))):
            fl = floor_of(ev, an)
            f = fisher(ev, an, struct)
            r = dict(det=det, analysis=aname, structure=struct, all=days_of(f, fl),
                     norms=days_of(_sub(f, lambda n: _grp_of(n) == 'norm'), fl))
            for g in NGROUPS:
                r[f'norms+{g}'] = days_of(_sub(f, lambda n, g=g: _grp_of(n) in ('norm', g)), fl)
                r[f'all-{g}'] = days_of(_sub(f, lambda n, g=g: _grp_of(n) != g), fl)
            rows.append(r)
            print(r, flush=True)
    return pd.DataFrame(rows)


def refsub(structs=('norms only', 'S_θ 2 % + S_θy 1 %', 'S_θ 5 % + S_θy 5 %, ℓ/2'), fracs=(1.0, 0.5, 0.25),
           seeds=(1, 2, 3, 4)):
    """background-MC subsamples of the floating-shape fits (c30, floor 1): do the MC-safe days still move?"""
    rows = []
    for det in ('asb', 'bigP'):
        comps, pool = setup(det)
        t = 'c30'
        expo = exposure(t, det)
        _, ec = best_window(comps[t], det, expo)
        ev = events(comps[t], pool, det, expo, (ec[0] - 4, ec[1]))
        for aname, an in (('3D', analysis(ec)), ('4D', analysis(ec, esum_axis=True))):
            for st in structs:
                for fr in fracs:
                    for sd in (seeds if fr < 1 else (0,)):
                        wm = None if fr == 1 else subsample(ev, fr, 100 * sd + int(1 / fr))
                        f = fisher(ev, an, 'none' if st == 'norms only' else st, nuis=st != 'norms only', wmult=wm)
                        rows.append(dict(det=det, analysis=aname, structure=st, frac=fr, seed=sd,
                                         days=days_of(f), days_floor1=days_of(f, floor_of(ev, an, FLOOR, wm))))
                d = pd.DataFrame([r for r in rows if r['det'] == det and r['analysis'] == aname and r['structure'] == st])
                print(det, aname, st, d.groupby('frac').days_floor1.median().round(1).to_dict(), flush=True)
    return pd.DataFrame(rows)


if __name__ == '__main__':
    what = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if what in ('refsub', 'all'):
        refsub().to_csv(OUTD / 'nd_refsub.csv', index=False, float_format='%.4g')
    if what in ('breakdown', 'all'):
        breakdown().to_csv(OUTD / 'nd_breakdown.csv', index=False, float_format='%.4g')
    if what in ('repro', 'all'):
        repro().to_csv(OUTD / 'nd_repro.csv', index=False, float_format='%.5g')
    if what in ('mcstat', 'all'):
        a, b, c = mcstat()
        a.to_csv(OUTD / 'nd_mcstat.csv', index=False, float_format='%.4g')
        b.to_csv(OUTD / 'nd_counting.csv', index=False, float_format='%.4g')
        c.to_csv(OUTD / 'nd_beam_rows.csv', index=False, float_format='%.4g')
    if what in ('nd', 'all'):
        nd().to_csv(OUTD / 'nd_days.csv', index=False, float_format='%.4g')
    if what in ('resp', 'all'):
        resp_variants().to_csv(OUTD / 'nd_resp.csv', index=False, float_format='%.4g')
