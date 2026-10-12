#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lnl_nd.py -- does a fit in two or three kinematic variables protect the LNL
X17 search against an imprecise background shape?  (FEASIBILITY_SIM.md §14.3,
2026-10-12)

    LNL_SEL=lnl/sim/sel_v3 python lnl/sim/lnl_nd.py [--resp 'LNL calibrated']   # -> lnl/out/nd/

lnl_syst.py puts the "unknown structure" (a Gaussian process, relative
amplitude δ, length ℓ) on the fitted variable itself.  So a θ fit and an m_ee
fit were never compared under the same background uncertainty: the m_ee
numbers assumed structure in m_ee.  Here the uncertainty lives on the
events, as a weight 1 + Σ c_j φ_j(event) on every background event, defined
in physical variables, and each analysis sees it through its own binning:

  S_θ    structure in the reconstructed opening angle, common to all y and
         E_sum: acceptance, the MM geometry, material.  ℓ = 10°.
  S_m    structure in m_ee (the §13 assumption).  ℓ = 0.55 MeV.
  S_θy   structure local in the (θ, |y|) plane: a background-physics shape
         error (IPC multipoles, the γ* anisotropy, E1/M1 mix).  ℓ = 10°, 0.15.
  S_θE   structure local in (θ, E_sum): the energy response, γ1 leakage.

The analyses (all at the reference level, MM 15° + TOF):

  θ                 θ_reco, 2° bins, all |y|, in the E_sum window
  θ, |y|<0.3        the §12 cut, no control
  m_ee              the §13 fit
  θ × |y|           6 |y| bins: the X17 is a curve θ_X(y), acceptance
                    structure is vertical bands
  m_ee × |y|        6 |y| bins
  m_ee × E_sum      E_sum from the γ1 side band to the window top
  θ × |y| × E_sum   both

Fit parameters as lnl_syst: r = R/R_ATOMKI; M1, E1, γ1 norms free (EPC tied
to M1, cosmics fixed); θ-resolution scale k ±10 %; E_sum scale e ±2 %;
γ* anisotropy a1 ±0.3, a2 ±0.15; acceptance cubic in θ (free); a |y| tilt
(linear + quadratic, ±5 %); per-arm gains (σ_g, lnl_calo); the |y| resolution
scale ±10 % when a response is applied; and the structure modes (unit
priors).  Asimov / Fisher, days to 3σ at R_ATOMKI.

MC statistics: background templates are KDE-smoothed along their first axis
(5° or 0.27 MeV, as lnl_syst); finer axes are plain bins.  A fine grid on a
few thousand IPC events fakes information (the n_TOF C3 lesson), so each
result is repeated on the two halves of the MC (columns half_a, half_b).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import ndtr

HERE = Path(__file__).resolve().parent
LNL = HERE.parent
OUT = LNL / 'out' / 'nd'
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(LNL.parent / 'ill'))
import lnl_geant as G      # noqa: E402
import lnl_syst as S       # noqa: E402
import lnl_calo as C       # noqa: E402

W_TR = S.W_TR
K_STEP, E_STEP, G_STEP, Y_STEP = 0.15, 0.03, 0.03, 0.15
PRIOR = dict(k=0.10, e=0.02, an1=S.PRIOR_AN1, an2=S.PRIOR_AN2, yt1=0.05, yt2=0.05, ky=0.10)
YB6 = np.array([0, 0.1, 0.2, 0.3, 0.45, 0.6, 1.0001])


# --------------------------------------------------------------------------- #
# the event list: every background and signal event with its per-day weight
# --------------------------------------------------------------------------- #
def mass(y, th):
    return W_TR * np.sqrt(np.clip((1 - y ** 2) * (1 - np.cos(np.radians(th))) / 2, 0, None))


def kvary(z, k):
    th = z['reco_c'].astype(float)
    if k:
        t = z['theta']
        th = np.where(np.isfinite(t), t + (1 + k) * (th - t), th)
        th = np.where(th > 180, 360 - th, th)
    return th


def ev_vars(z, E1, E2, Esum, th):
    y = np.abs(E1 - E2) / np.maximum(E1 + E2, 1e-9)
    return dict(th=th, y=y, m=mass(y, th), E=Esum)


def collect(hw, scen=S.SIG_RUN, I_uA=1.0, erange=(0, 99)):
    """event table for one hardware/response: variables, variations, weights."""
    y_ = S.YIELDS.loc[scen]
    live = S.HWS[hw][1]
    ng0 = y_.Y_g0 * I_uA * 1e-6 / S.LR.E_CHARGE * 86400 * live
    a = S.ALPHA
    f17, fr, fd, fg = y_.frac_17_64, y_.frac_18_15_res, y_.frac_direct, y_.frac_g1_direct
    g1r = y_.Y_g1 / y_.Y_g0
    coef = {'M1_17.64': ('M1', f17 * a[(17.64, 'M1')]), 'M1_18.15': ('M1', fr * a[(18.15, 'M1')]),
            'E1_18.15': ('E1', fd * a[(18.15, 'E1')]),
            'M1_15.1': ('g1', g1r * (1 - f17) * (1 - fg) * a[(15.1, 'M1')]),
            'E1_15.1': ('g1', g1r * (1 - f17) * fg * a[(15.1, 'E1')]),
            'M1_14.6': ('g1', g1r * f17 * (1 - fg) * a[(14.6, 'M1')]),
            'E1_14.6': ('g1', g1r * f17 * fg * a[(14.6, 'E1')])}
    parts = []

    def add(z, m, w, grp, p1=None, p2=None):
        if not m.any():
            return
        d = dict(grp=np.full(m.sum(), grp), w=w[m] if np.ndim(w) else np.full(m.sum(), w),
                 p1=(p1[m] if p1 is not None else np.zeros(m.sum())),
                 p2=(p2[m] if p2 is not None else np.zeros(m.sum())),
                 idx=np.nonzero(m)[0])
        E1, E2, Es = z['E1'].astype(float), z['E2'].astype(float), z['Esum'].astype(float)
        th0 = kvary(z, 0)
        d['v0'] = {k: v[m] for k, v in ev_vars(z, E1, E2, Es, th0).items()}
        for sg, k in (('k+', K_STEP), ('k-', -K_STEP)):
            d[sg] = {k_: v[m] for k_, v in ev_vars(z, E1, E2, Es, kvary(z, k)).items()}
        for sg, e in (('e+', E_STEP), ('e-', -E_STEP)):
            d[sg] = {k_: v[m] for k_, v in ev_vars(z, E1, E2, Es * (1 + e), th0).items()}
        for j in range(4):
            for sg, g in (('+', G_STEP), ('-', -G_STEP)):
                zz = S.gain_var(z, j, g)
                d[f'g{j}{sg}'] = {k_: v[m] for k_, v in ev_vars(z, zz['E1'], zz['E2'], zz['Esum'], th0).items()}
        if 'E1_ideal' in z:          # |y| resolution scale: residual from the ideal deposits
            yi = np.abs(z['E1_ideal'] - z['E2_ideal']) / np.maximum(z['E1_ideal'] + z['E2_ideal'], 1e-9)
            y0 = np.abs(E1 - E2) / np.maximum(E1 + E2, 1e-9)
            for sg, s_ in (('y+', Y_STEP), ('y-', -Y_STEP)):
                yy = np.clip(yi + (1 + s_) * (y0 - yi), 0, 1)
                d[sg] = dict(th=th0[m], y=yy[m], m=mass(yy, th0)[m], E=Es[m])
        parts.append(d)

    def base_mask(z):
        return G.select(z, S.LEVEL, (-1e9, 1e9)) & (z['Esum'] > erange[0] - 3) & (z['Esum'] < erange[1] + 3)

    # signal
    z = G.load('L1', 'X17_m16.7', hw)
    add(z, base_mask(z), ng0 * (1 - f17) * S.R_ATOMKI / z['ngen'], 'sig')
    # IPC
    for s, (grp, c) in coef.items():
        z, f, _ = S.load_ipc(s, hw)
        if z is None:
            continue
        w = np.full(len(z['reco_c']), ng0 * c * f / z['ngen'])
        p1 = p2 = None
        if s in S.ANISO and 'em_p' in z:
            cc = S.kcos(z)
            P1, P2 = cc, 0.5 * (3 * cc ** 2 - 1)
            a1, a2 = S.ANISO[s]
            w0 = 1 + a1 * P1 + a2 * P2
            p1, p2 = w * P1, w * P2
            w = w * w0
        add(z, base_mask(z), w, grp, p1, p2)
    # EPC (tied to M1)
    z = G.load('L3', 'gam_8Be', hw)
    if z is not None:
        nline = z['ngen'] / len(G.LINES['gam_8Be'])
        cl = {18.15: 1 - f17, 17.64: f17, 15.1: g1r * (1 - f17), 14.6: g1r * f17}
        w = np.zeros(len(z['reco_c']))
        for L, c in cl.items():
            w[np.isclose(z['inv_mass'], L, atol=1e-3)] = ng0 * c / nline
        add(z, base_mask(z) & (w > 0), w, 'M1')
    # cosmics (fixed)
    z = G.load('L4', 'cosmic', hw)
    if z is not None:
        days = z['ngen'] * G.MU_LIVE_S / 86400
        add(z, base_mask(z), live / days, 'cos')
    keys = [k for k in parts[0] if k not in ('grp', 'w', 'p1', 'p2', 'idx')]
    ev = dict(grp=np.concatenate([p['grp'] for p in parts]), w=np.concatenate([p['w'] for p in parts]),
              p1=np.concatenate([p['p1'] for p in parts]), p2=np.concatenate([p['p2'] for p in parts]),
              idx=np.concatenate([p['idx'] for p in parts]))
    for k in keys:
        if all(k in p for p in parts):
            ev[k] = {v: np.concatenate([p[k][v] for p in parts]) for v in ('th', 'y', 'm', 'E')}
    return ev


# --------------------------------------------------------------------------- #
# analyses: axes (variable, edges); the first is KDE-smoothed for backgrounds
# --------------------------------------------------------------------------- #
TH_B = np.arange(90, 181, 2.0)
M_B = np.arange(8.0, 20.0001, 0.25)
BW = {'th': G.KDE_BW_DEG, 'm': 0.27}
LO = {'th': 70.0, 'm': 4.0}


def analyses(ec):
    lo, hi = ec
    eb = np.array([lo - 4, lo - 2, lo, 0.5 * (lo + hi), hi])
    return {
        'θ': dict(axes=[('th', TH_B)], E=(lo, hi)),
        'θ, |y|<0.3': dict(axes=[('th', TH_B)], E=(lo, hi), ycut=0.3),
        'm_ee': dict(axes=[('m', M_B)], E=(lo, hi)),
        'θ × |y|': dict(axes=[('th', TH_B), ('y', YB6)], E=(lo, hi)),
        'm_ee × |y|': dict(axes=[('m', M_B), ('y', YB6)], E=(lo, hi)),
        'm_ee × E_sum': dict(axes=[('m', M_B), ('E', eb)], E=(eb[0], eb[-1])),
        'θ × |y| × E_sum': dict(axes=[('th', TH_B), ('y', YB6), ('E', eb)], E=(eb[0], eb[-1])),
    }


class Binner:
    """the analysis binning for one set of event variables: each event's
    (secondary bin, fine bin of the first axis), and the KDE matrix that turns
    the fine histogram into the analysis bins.  apply(w) -> flattened histogram."""

    def __init__(self, an, v, smooth):
        (k0, b0), rest = an['axes'][0], an['axes'][1:]
        m = (v['E'] > an['E'][0]) & (v['E'] < an['E'][1])
        if an.get('ycut') is not None:
            m &= v['y'] < an['ycut']
        sec = np.zeros(len(m), int)
        nsec = 1
        for k, b in rest:
            i = np.digitize(v[k], b) - 1
            m &= (i >= 0) & (i < len(b) - 1)
            sec = sec * (len(b) - 1) + np.clip(i, 0, len(b) - 2)
            nsec *= len(b) - 1
        x = v[k0]
        self.nsec, self.nb = nsec, len(b0) - 1
        if smooth:
            bw = BW[k0]
            step = (b0[1] - b0[0]) / 8
            fine = np.arange(LO[k0], b0[-1] + 1e-9 + 4 * bw, step)
            xf = 0.5 * (fine[1:] + fine[:-1])
            c = ndtr((b0[None, :] - xf[:, None]) / bw)
            K = c[:, 1:] - c[:, :-1]
            if k0 == 'th':                  # reflected at 180°
                c2 = ndtr((b0[None, :] - (360.0 - xf)[:, None]) / bw)
                K = K + (c2[:, 1:] - c2[:, :-1])
            m &= (x > fine[0]) & (x < fine[-1])
            fi = np.clip(np.digitize(x, fine) - 1, 0, len(xf) - 1)
            self.nf, self.K = len(xf), K
        else:
            m &= (x >= b0[0]) & (x < b0[-1])
            fi = np.clip(np.digitize(x, b0) - 1, 0, self.nb - 1)
            self.nf, self.K = self.nb, None
        self.m = m
        self.idx = (sec * self.nf + fi)[m]

    def apply(self, w):
        h = np.bincount(self.idx, weights=np.asarray(w)[self.m], minlength=self.nsec * self.nf)
        h = h.reshape(self.nsec, self.nf)
        if self.K is not None:
            h = h @ self.K
        return h.ravel()


# --------------------------------------------------------------------------- #
# structure bases: GP eigenmodes on a node grid, interpolated to each event
# --------------------------------------------------------------------------- #
def gp_basis(nodes, ells, delta):
    """nodes: (n, d) grid; returns (modes (M, n), scaled so coefficients have unit priors)."""
    d2 = sum(((nodes[:, None, i] - nodes[None, :, i]) / ells[i]) ** 2 for i in range(nodes.shape[1]))
    Cm = delta ** 2 * np.exp(-0.5 * d2)
    w, v = np.linalg.eigh(Cm)
    keep = w > 1e-4 * w.max()
    return (v[:, keep] * np.sqrt(w[keep])).T


def struct_weights(kind, v, delta, lscale=1.0):
    """per-event mode values (M, n_events) for structure model `kind`;
    lscale multiplies the correlation lengths (0.5: edge-like structure)."""
    if kind == 'S_θ':
        g = np.arange(70, 181, 2.0)
        B = gp_basis(g[:, None], [10.0 * lscale], delta)
        return np.array([np.interp(v['th'], g, b) for b in B])
    if kind == 'S_m':
        g = np.arange(4, 20.01, 0.125)
        B = gp_basis(g[:, None], [0.55 * lscale], delta)
        return np.array([np.interp(v['m'], g, b) for b in B])
    if kind in ('S_θy', 'S_θE'):
        gt = np.arange(70, 181, 3.0)
        if kind == 'S_θy':
            g2, l2, x2 = np.arange(0, 1.0001, 0.05), 0.15, v['y']
        else:
            g2, l2, x2 = np.arange(4, 26.01, 1.0), 2.0, v['E']
        T, Y = np.meshgrid(gt, g2, indexing='ij')
        B = gp_basis(np.c_[T.ravel(), Y.ravel()], [10.0 * lscale, l2 * lscale], delta)
        # bilinear interpolation of each mode at the events
        it = np.clip(np.searchsorted(gt, v['th']) - 1, 0, len(gt) - 2)
        iy = np.clip(np.searchsorted(g2, x2) - 1, 0, len(g2) - 2)
        ft = np.clip((v['th'] - gt[it]) / (gt[1] - gt[0]), 0, 1)
        fy = np.clip((x2 - g2[iy]) / (g2[1] - g2[0]), 0, 1)
        n2 = len(g2)
        out = np.empty((len(B), len(x2)))
        for j, b in enumerate(B):
            bb = b.reshape(len(gt), n2)
            out[j] = ((1 - ft) * (1 - fy) * bb[it, iy] + ft * (1 - fy) * bb[it + 1, iy]
                      + (1 - ft) * fy * bb[it, iy + 1] + ft * fy * bb[it + 1, iy + 1])
        return out
    raise ValueError(kind)


# --------------------------------------------------------------------------- #
# Fisher
# --------------------------------------------------------------------------- #
def legendre(x, n):
    return [np.ones_like(x), x, 0.5 * (3 * x ** 2 - 1), 0.5 * (5 * x ** 3 - 3 * x)][n]


def fisher_nd(ev, an, structs, sigma_g=None, sel=None):
    """F (data, per day) and P (priors) for one analysis.  structs: list of
    (kind, δ).  sel: boolean mask on events (MC half)."""
    if sel is None:
        sel = np.ones(len(ev['w']), bool)
    grp = ev['grp']
    sm = sel & (grp == 'sig')
    bk = sel & (grp != 'sig')
    fac = 1.0 / max(sel.mean(), 1e-9)       # a half carries half the events: rescale
    v0 = ev['v0']
    _b = {}

    def H(v, w, m, smooth=True):
        key = (id(v), smooth)
        if key not in _b:
            _b[key] = Binner(an, v, smooth)
        return fac * _b[key].apply(np.where(m, w, 0.0))

    mu = H(v0, ev['w'], bk)
    sig = H(v0, ev['w'], sm, smooth=False)
    rows, names, prior = [sig], ['r'], [None]
    for gname in ('M1', 'E1', 'g1'):
        rows.append(H(v0, ev['w'], bk & (grp == gname)))
        names.append(gname)
        prior.append(None)
    # anisotropy (already in w through w0; derivatives are w·P / w0 → stored as p1, p2)
    for p, key in (('an1', 'p1'), ('an2', 'p2')):
        rows.append(H(v0, ev[key], bk))
        names.append(p)
        prior.append(PRIOR[p])

    def fd(kp, km, step):
        return (H(ev[kp], ev['w'], bk) - H(ev[km], ev['w'], bk)) / (2 * step)
    rows.append(fd('k+', 'k-', K_STEP)); names.append('k'); prior.append(PRIOR['k'])
    rows.append(fd('e+', 'e-', E_STEP)); names.append('e'); prior.append(PRIOR['e'])
    if sigma_g:
        for j in range(4):
            rows.append(fd(f'g{j}+', f'g{j}-', G_STEP)); names.append(f'gain{j}'); prior.append(sigma_g)
    if 'y+' in ev:
        rows.append(fd('y+', 'y-', Y_STEP)); names.append('ky'); prior.append(PRIOR['ky'])
    # acceptance cubic in θ (free) and a |y| tilt (±5 %)
    xt = (v0['th'] - 135.0) / 45.0
    for n in (1, 2, 3):
        rows.append(H(v0, ev['w'] * legendre(xt, n), bk)); names.append(f'acc{n}'); prior.append(None)
    xy = 2 * v0['y'] - 1
    for n in (1, 2):
        rows.append(H(v0, ev['w'] * legendre(xy, n), bk)); names.append(f'yt{n}'); prior.append(PRIOR[f'yt{n}'])
    for st in structs:
        kind, delta, ls = (tuple(st) + (1.0,))[:3]
        ck = ('_sw', kind, delta, ls)
        if ck not in ev:
            ev[ck] = struct_weights(kind, v0, delta, ls)
        Wm = ev[ck]
        for j in range(len(Wm)):
            rows.append(H(v0, ev['w'] * Wm[j], bk)); names.append(f'{kind}{j}'); prior.append(1.0)
    g = np.array(rows)
    ok = mu > mu.max() * 1e-9
    F = (g[:, ok] / mu[ok]) @ g[:, ok].T
    P = np.diag([0.0 if p is None else 1 / p ** 2 for p in prior])
    return F, P, names, dict(S=sig.sum(), B=mu.sum())


STRUCTS = {
    'none': [],
    'S_θ 2 %': [('S_θ', 0.02)],
    'S_m 2 %': [('S_m', 0.02)],
    'S_θy 2 %': [('S_θy', 0.02)],
    'S_θE 2 %': [('S_θE', 0.02)],
    'S_θ 2 % + S_θy 1 %': [('S_θ', 0.02), ('S_θy', 0.01)],
    # stress tests: larger, and edge-like (half the correlation lengths)
    'S_θ 5 %, ℓ/2': [('S_θ', 0.05, 0.5)],
    'S_m 5 %, ℓ/2': [('S_m', 0.05, 0.5)],
    'S_θy 5 %, ℓ/2': [('S_θy', 0.05, 0.5)],
}


def run(hw, resp, sigma_g, halves=True):
    C.set_response(resp, sigma_g=sigma_g)
    ec = C.BEST.get((hw, resp), S.HWS[hw][0])
    S.HWS[hw] = (ec, C.HWS0[hw][1])
    ans = analyses(ec)
    ev = collect(hw, erange=(ec[0] - 4, ec[1]))
    rng = np.random.default_rng(5)
    half = rng.random(len(ev['w'])) < 0.5
    rows = []
    for aname, an in ans.items():
        for sname, st in STRUCTS.items():
            F, P, names, sb = fisher_nd(ev, an, st, sigma_g=S.PRIOR_G)
            r = dict(hw=hw, resp=resp, ecut=f'{ec[0]}-{ec[1]}', analysis=aname, structure=sname,
                     days=S.days_to(F, P), S_per_day=sb['S'], B_per_day=sb['B'])
            if halves and sname in ('none', 'S_θ 2 % + S_θy 1 %'):
                for lab, m in (('half_a', half), ('half_b', ~half)):
                    Fh, Ph, _, _ = fisher_nd(ev, an, st, sigma_g=S.PRIOR_G, sel=m)
                    r[lab] = S.days_to(Fh, Ph)
            rows.append(r)
            print(f"{hw:13s} {resp:16s} {aname:16s} {sname:20s} {r['days']:8.2f} d"
                  + (f"  halves {r['half_a']:.2f} / {r['half_b']:.2f}" if 'half_a' in r else ''))
    S.HWS[hw] = C.HWS0[hw]
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--resp', nargs='*', default=['ideal', 'LNL calibrated'])
    ap.add_argument('--hw', nargs='*', default=['big plastics', 'as built'])
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    win = OUT.parent / 'calo' / 'resolution.csv'
    if win.exists():          # the per-response E_sum windows from lnl_calo
        for _, r in pd.read_csv(win).iterrows():
            lo, hi = (float(x) for x in str(r.ecut).split('-'))
            C.BEST[(r.hw, r.resp)] = (lo, hi)
    rows = []
    for hw in a.hw:
        for resp in a.resp:
            rows += run(hw, resp, 'auto')
    t = pd.DataFrame(rows)
    tag = '_'.join(x.replace(' ', '').replace(',', '') for x in a.hw + a.resp)
    t.to_csv(OUT / f'nd_days_{tag}.csv', index=False)
    piv = t.pivot_table(index=['hw', 'resp', 'analysis'], columns='structure', values='days', sort=False)
    with pd.option_context('display.width', 250, 'display.max_columns', 30):
        print(piv.round(2).to_string())


if __name__ == '__main__':
    main()
