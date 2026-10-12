#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lnl_syst.py -- how robust is the LNL X17 reach once the background shape is
not assumed perfectly known?  (FEASIBILITY_SIM.md §12, 2026-10-12)

    python lnl/sim/lnl_syst.py            # -> lnl/out/syst/*.csv, figures

Four parts:

1. atomki_repro(): ATOMKI 2016 at truth level.  Born IPC (M1, E1) and X17
   pairs from 8Be* at rest (lnl_rates generators), ATOMKI's cuts (|y| <= 0.5,
   both leptons above threshold, E_sum = the full 18 MeV), Gaussian angular
   smearing, acceptance-corrected (4π).  Does R = 5.8e-6 give their visible
   bump (data / no-boson curve 1.26-1.35 at 135-145°, PRL 116 042501 Fig. 4)?  And how
   much of the gap to our S/B comes from the E1 fraction, the y cut and the
   resolution?
2. The symmetric-pair cut on the Geant4 tables: |y| = |E1 - E2| / (E1 + E2)
   with the measured arm energies (no charge sign needed).
3. reach with shape nuisances: an Asimov/Fisher fit (background-only Asimov,
   σ(R) from the inverse Fisher matrix) with
     - free M1, E1 and γ1 normalisations (EPC tied to M1, cosmics fixed);
     - the angular-resolution scale k (reco - truth scaled by 1 + k);
     - the E_sum scale e;
     - a multiplicative acceptance polynomial 1 + Σ a_n P_n(x), x = θ over
       90-180° mapped to [-1, 1], shared by every sample (the detector);
     - per-category "transfer" polynomials with prior ε: how well a control
       sample's acceptance shape carries over to the signal category.
   The time T enters the data term only, so priors set a ceiling Z_max.
4. control samples: the asymmetric pairs and the γ1 E_sum sideband of the
   same run, and a run on the 441 keV (17.64 MeV) resonance, where ATOMKI saw
   no anomaly in 2016.  They share the detector nuisances with the signal
   category, so they measure the shape.

Inputs: lnl/sim/sel (lnl_geant.py), lnl/out/yields.csv, ipc_alpha.csv.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
LNL = HERE.parent
OUT = LNL / 'out' / 'syst'
sys.path.insert(0, str(HERE))
import lnl_geant as G       # noqa: E402
LR = G.LR

R_ATOMKI = LR.R_ATOMKI_2016
#: ATOMKI 2016 Fig. 4 (E_p = 1.10 MeV, -0.5 <= y <= 0.5, E_sum = 18 MeV), read
#: off the published figure: data and the no-boson (M1 + 23 % E1) curve
ATOMKI_FIG4 = pd.DataFrame(dict(theta=[85, 95, 105, 115, 125, 135, 145, 155, 165],
                                data=[0.0461, 0.0373, 0.0275, 0.0219, 0.0200, 0.0216, 0.0206, 0.0162, 0.0136],
                                ipc=[0.0461, 0.0373, 0.0277, 0.0224, 0.0198, 0.0172, 0.0153, 0.0134, 0.0121]))
#: (digitised at 300 dpi from arXiv:1504.01527 p. 4; ±3 % reading error.  The
#: dashed curve is the IPC-only simulation; above 120° it departs from the data)


# --------------------------------------------------------------------------- #
# 1. ATOMKI at truth level
# --------------------------------------------------------------------------- #
def atomki_repro(n=2_000_000):
    a = pd.read_csv(LNL / 'out' / 'ipc_alpha.csv').set_index(['W_MeV', 'multipole']).alpha_pair
    W = 18.15
    ev = {k: LR.ipc_vectors(k, n, W, seed=s) for k, s in (('M1', 1), ('E1', 2))}
    ev['X17'] = LR.x17_vectors(n, W, 16.7, seed=3)
    for e in ev.values():
        e['w'] = e['w'] / e['w'].sum()            # pairs: per pair of that kind
        e['y'] = np.abs(e['ke1'] - e['ke2']) / (e['ke1'] + e['ke2'])
    edges = np.arange(40, 181, 10.0)
    xc = 0.5 * (edges[1:] + edges[:-1])
    rows = []
    rng = np.random.default_rng(5)

    def h(e, ycut, ke_min, sig):
        m = (e['ke1'] > ke_min) & (e['ke2'] > ke_min)
        if ycut is not None:
            m &= (e['y'] <= ycut) if ycut > 0 else (e['y'] > -ycut)
        th = e['theta'] + rng.normal(0, sig, len(e['theta'])) if sig > 0 else e['theta']
        th = np.where(th > 180, 360 - th, th)
        # acceptance-corrected: per unit solid angle of the pair opening (ATOMKI "IPCC")
        hh, _ = np.histogram(th[m], edges, weights=e['w'][m])
        return hh

    cases = [  # label, E1 share of the γ0 intensity, y cut, KE threshold, σ_θ
        ('ATOMKI 2016 as published: M1 + 23 % E1, |y| ≤ 0.5, σ 3°', 0.23, 0.5, 2.0, 3.0),
        ('… σ 6°', 0.23, 0.5, 2.0, 6.0),
        ('… no y cut', 0.23, None, 2.0, 3.0),
        ('our mix: 52 % E1 (direct capture), |y| ≤ 0.5, σ 3°', 0.52, 0.5, 2.0, 3.0),
        ('our mix, no y cut, σ 5° (≈ our Geant4 selection)', 0.52, None, 2.0, 5.0),
        ('pure M1, |y| ≤ 0.5, σ 3°', 0.0, 0.5, 2.0, 3.0),
    ]
    for lab, fE1, yc, kmin, sig in cases:
        hm, he, hx = (h(ev[k], yc, kmin, sig) for k in ('M1', 'E1', 'X17'))
        # per γ0: IPC = Σ (γ share x α_pair x shape);  X17 = R x (all γ0)
        b = (1 - fE1) * a[(W, 'M1')] * hm + fE1 * a[(W, 'E1')] * he
        s = R_ATOMKI * hx
        for x, bb, ss in zip(xc, b, s):
            rows.append(dict(case=lab, E1_share=fE1, ycut=yc, sigma_deg=sig, theta=x, ipc=bb, x17=ss,
                             ratio=(bb + ss) / bb if bb > 0 else np.nan))
    d = pd.DataFrame(rows)
    # what R would give ATOMKI's own bump (data/IPC at 135-145°) in the as-published case
    c0 = d[(d.case == cases[0][0]) & (d.theta == 145)].iloc[0]
    fig4 = ATOMKI_FIG4.set_index('theta')
    want = fig4.loc[145, 'data'] / fig4.loc[145, 'ipc'] - 1
    r_needed = R_ATOMKI * want / (c0.x17 / c0.ipc)
    return d, dict(atomki_fig4_excess_145=float(want), ours_at_R_atomki_145=float(c0.x17 / c0.ipc),
                   R_needed_for_fig4=float(r_needed))


# --------------------------------------------------------------------------- #
# 2. Geant4 templates with an asymmetry category and nuisance variations
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# The fitted variable.  'theta': the reconstructed opening angle, 90-180° in 2°.
# 'mass': m_ee = W √((1 − y²)(1 − cos θ)/2) with W = 18.15 MeV (the pair's total
# energy is the transition energy; y from the arm energies is a ratio, so the
# containment scale drops out), 8-20 MeV in 0.25 MeV.  use_var() switches every
# global below; the GP length ℓ and the KDE width are scaled so that 10° ≈ 0.55 MeV
# and 5° ≈ 0.27 MeV (dm/dθ at the 134° edge).
# --------------------------------------------------------------------------- #
W_TR = 18.15
VAR = 'theta'
XC, BINS = G.XC, G.BINS
KBW, KLO = G.KDE_BW_DEG, 70.0        # KDE width, lowest value kept before smoothing
UNIT = 1.0                            # variable units per degree near the edge
WIN = (130, 160)                      # the "window" used in the tables
XN = (XC - 135.0) / 45.0
LEG = []


def use_var(var):
    global VAR, XC, BINS, KBW, KLO, UNIT, WIN, XN, LEG
    VAR = var
    if var == 'theta':
        BINS = G.BINS
        KBW, KLO, UNIT, WIN = G.KDE_BW_DEG, 70.0, 1.0, (130, 160)
    else:
        BINS = np.arange(8.0, 20.0001, 0.25)
        KBW, KLO, UNIT, WIN = 0.27, 4.0, 0.055, (16.0, 17.25)
    XC = 0.5 * (BINS[1:] + BINS[:-1])
    XN = 2 * (XC - BINS[0]) / (BINS[-1] - BINS[0]) - 1
    LEG = [np.ones_like(XN), XN, 0.5 * (3 * XN ** 2 - 1), 0.5 * (5 * XN ** 3 - 3 * XN),
           0.125 * (35 * XN ** 4 - 30 * XN ** 2 + 3)]
    globals().setdefault("_T", {}).clear()


def kde(x, w=None):
    """Gaussian KDE integrated over BINS (reflected at the top edge for θ), sum = sum of w."""
    from scipy.special import ndtr
    x = np.asarray(x, float)
    w = np.ones(len(x)) if w is None else np.asarray(w, float)
    if len(x) == 0:
        return np.zeros(len(XC))
    step = (BINS[1] - BINS[0]) / 8
    fine = np.arange(KLO, BINS[-1] + 1e-9 + 4 * KBW, step)
    hf, _ = np.histogram(x, fine, weights=w)
    xf = 0.5 * (fine[1:] + fine[:-1])
    if VAR == 'theta':
        xx, ww = np.r_[xf, 360.0 - xf], np.r_[hf, hf]
    else:
        xx, ww = xf, hf
    keep = ww != 0
    c = ndtr((BINS[None, :] - xx[keep, None]) / KBW)
    return ((c[:, 1:] - c[:, :-1]) * ww[keep, None]).sum(0)


def var_of(z, k=0.0):
    """the fitted variable per event; k scales the angular residual (reco − truth)."""
    th = z['reco_c']
    if k:
        t = z['theta']
        th = np.where(np.isfinite(t), t + (1 + k) * (th - t), th)
        th = np.where(th > 180, 360 - th, th)
    if VAR == 'theta':
        return th
    y = asym(z)
    return W_TR * np.sqrt(np.clip((1 - y ** 2) * (1 - np.cos(np.radians(th))) / 2, 0, None))


use_var('theta')
K_STEP, E_STEP = 0.15, 0.03                  # finite-difference steps (res scale, E scale)
_T: dict = {}


def asym(z):
    return np.abs(z['E1'] - z['E2']) / np.maximum(z['E1'] + z['E2'], 1e-9)


def cat_mask(z, level, ecut, ycat, e=0.0):
    """level (MM pointing, TOF) & E_sum window (scaled by 1 + e) & y category.
    ycat: 'all', 'y<c' (symmetric) or 'y>c' (the asymmetric complement)."""
    m = G.select(z, level, (-1e9, 1e9))
    es = z['Esum'] * (1 + e)
    m = m & (es > ecut[0]) & (es < ecut[1])
    if ycat != 'all':
        c = float(ycat[2:])
        m = m & ((asym(z) < c) if ycat[1] == '<' else (asym(z) >= c))
    return m


def thist(z, mask, k=0.0, smooth=True, w=None):
    """reco-θ histogram per generated event, with the residual scaled by 1 + k
    and optional event weights w (the γ* anisotropy)."""
    th = var_of(z, k)
    if smooth:
        sel = mask & (th > KLO)
        return kde(th[sel], w=None if w is None else w[sel]) / z['ngen']
    h, _ = np.histogram(th[mask], BINS, weights=None if w is None else w[mask])
    return h / z['ngen']


# --------------------------------------------------------------------------- #
# γ* anisotropy about the beam: W = 1 + a1 P1(cos θ_k) + a2 P2(cos θ_k)
#   a1: the E1-M1 interference.  Zahnow 1995 σ(0°)/σ(150°) = 7.6 ± 1.3 for γ0 at
#       1100 keV gives a1 ≈ 1.0 (with a2 below); 1.23 at 440 keV gives a1 ≈ 0.1.
#       For arms symmetric about 90° to the beam it cancels (Hayes et al. 2021,
#       arXiv:2106.06834), which the Geant4 tables confirm (<P1> ≈ 0).
#   a2: Hayes et al. R-matrix 4πσ(90°)/σ_int = 1 - a2/2 = 0.82 → a2 = 0.36;
#       physical range 0-0.5 (pure 3P1 M1 gives 0.5).
# Applied to the γ0 IPC (real-photon anisotropy carried by the virtual photon);
# not to γ1, EPC or the X17.  Needs the truth momenta (em_p, ep_p: sel_v2, L7).
# --------------------------------------------------------------------------- #
ANISO = {'M1_18.15': (1.0, 0.36), 'E1_18.15': (1.0, 0.36), 'M1_17.64': (0.1, 0.36)}
PRIOR_AN1, PRIOR_AN2 = 0.3, 0.15
ME = 0.51099895


def kcos(z):
    """cos(γ*, beam) per event from the truth lepton momenta; beam = +Y."""
    pm = np.sqrt(z['em_ke'] ** 2 + 2 * z['em_ke'] * ME)[:, None] * z['em_p']
    pp = np.sqrt(z['ep_ke'] ** 2 + 2 * z['ep_ke'] * ME)[:, None] * z['ep_p']
    k = pm + pp
    return k[:, 1] / np.maximum(np.linalg.norm(k, axis=1), 1e-9)


# --------------------------------------------------------------------------- #
# IPC samples: L7 (generated above 70°, ×10-20 statistics) when present, else L2
# --------------------------------------------------------------------------- #
IPC_RUNS = ('L7', 'L2')
_F70: dict = {}


def born_f70(kind, W):
    """Born fraction of pairs with θ > 70° (the L7 generator cut)."""
    if (kind, W) not in _F70:
        ev = LR.ipc_vectors(kind, 2_000_000, W, seed=13)
        _F70[(kind, W)] = float(ev['w'][ev['theta'] > 70].sum() / ev['w'].sum())
    return _F70[(kind, W)]


def load_ipc(s, hw):
    """(table, per-generated-pair factor, run) for an IPC sample."""
    for run in IPC_RUNS:
        z = G.load(run, s, hw)
        if z is not None:
            f = born_f70(s[:2], float(s[3:])) if run == 'L7' else 1.0
            return z, f, run
    return None, 1.0, None


SAMPLES = ('X17_m16.7', 'M1_18.15', 'E1_18.15', 'M1_17.64', 'M1_15.1', 'E1_15.1', 'M1_14.6', 'E1_14.6')


def templates(hw, level, ecut, ycat):
    """{sample: {variation: hist}} per generated pair, variations
    '0', 'k+', 'k-', 'e+', 'e-'; EPC per γ of each 8Be line; cosmics per live day."""
    key = (hw, level, ecut, ycat)
    if key in _T:
        return _T[key]
    out = {'src': {}}
    for s in SAMPLES:
        if s.startswith('X17'):
            z, f, run = G.load('L1', s, hw), 1.0, 'L1'
        else:
            z, f, run = load_ipc(s, hw)
        if z is None:
            out[s] = None
            continue
        out['src'][s] = run
        sm = not s.startswith('X17')
        w0 = wp1 = wp2 = None
        if s in ANISO and 'em_p' in z:
            c = kcos(z)
            p1, p2 = c, 0.5 * (3 * c ** 2 - 1)
            a1, a2 = ANISO[s]
            w0, wp1, wp2 = 1 + a1 * p1 + a2 * p2, p1, p2
        m0 = cat_mask(z, level, ecut, ycat)
        out[s] = {'0': f * thist(z, m0, 0, sm, w0),
                  'k+': f * thist(z, m0, K_STEP, sm, w0), 'k-': f * thist(z, m0, -K_STEP, sm, w0),
                  'e+': f * thist(z, cat_mask(z, level, ecut, ycat, E_STEP), 0, sm, w0),
                  'e-': f * thist(z, cat_mask(z, level, ecut, ycat, -E_STEP), 0, sm, w0)}
        if s in ANISO:
            zero = np.zeros(len(XC))
            out[s]['p1'] = f * thist(z, m0, 0, sm, wp1) if wp1 is not None else zero
            out[s]['p2'] = f * thist(z, m0, 0, sm, wp2) if wp2 is not None else zero
            out[s]['iso'] = f * thist(z, m0, 0, sm)
    z = G.load('L3', 'gam_8Be', hw)
    epc = {}
    if z is not None:
        nline = z['ngen'] / len(G.LINES['gam_8Be'])
        for L in G.LINES['gam_8Be']:
            m = cat_mask(z, level, ecut, ycat) & np.isclose(z['inv_mass'], L, atol=1e-3)
            v = var_of(z)
            epc[L] = kde(v[m & (v > KLO)]) / nline
    out['epc'] = epc
    z = G.load('L4', 'cosmic', hw)
    cos = np.zeros(len(XC))
    if z is not None:
        days = z['ngen'] * G.MU_LIVE_S / 86400
        m = cat_mask(z, level, ecut, ycat)
        v = var_of(z)
        n = int((m & (v >= BINS[0])).sum())
        h = kde(v[m & (v > KLO)])
        if n < 5:      # as lnl_geant: shape from the level without E_sum, at least 1 event
            m0 = G.select(z, level, (0, 99))
            h0 = kde(v[m0 & (v > KLO)])
            h = h0 / max(h0.sum(), 1e-30) * max(n, 1)
        cos = h / days
    out['cos'] = cos
    _T[key] = out
    return out


ALPHA = pd.read_csv(LNL / 'out' / 'ipc_alpha.csv').set_index(['W_MeV', 'multipole']).alpha_pair
YIELDS = pd.read_csv(LNL / 'out' / 'yields.csv').set_index('scenario')
SIG_RUN, CTRL_RUN = 'ATOMKI 2016 anomaly', 'ATOMKI 2022, on 17.64'


def physics(y, t, var='0', run='18'):
    """per-γ0 components for one yields row: M1 (+EPC, tied), E1, γ1, and the X17
    shape.  run '18': the 1.10 MeV run; '17': the 441 keV run (no X17 assumed)."""
    a = ALPHA
    zero = np.zeros(len(XC))
    H = {s: (None if t[s] is None else t[s].get(var, zero)) for s in SAMPLES}
    f17, fr, fd = y.frac_17_64, y.frac_18_15_res, y.frac_direct
    g1r = y.Y_g1 / y.Y_g0
    e = t['epc']
    epc = 0
    if e and var not in ('p1', 'p2', 'iso'):
        epc = (1 - f17) * e[18.15] + f17 * e[17.64] + g1r * ((1 - f17) * e[15.1] + f17 * e[14.6])
    m1 = f17 * a[(17.64, 'M1')] * H['M1_17.64'] + fr * a[(18.15, 'M1')] * H['M1_18.15'] + epc
    e1 = fd * a[(18.15, 'E1')] * H['E1_18.15']
    fg = y.frac_g1_direct
    g1 = g1r * ((1 - f17) * ((1 - fg) * a[(15.1, 'M1')] * H['M1_15.1'] + fg * a[(15.1, 'E1')] * H['E1_15.1'])
                + f17 * ((1 - fg) * a[(14.6, 'M1')] * H['M1_14.6'] + fg * a[(14.6, 'E1')] * H['E1_14.6']))
    sig = (1 - f17) * H['X17_m16.7'] if run == '18' else np.zeros(len(XC))
    return dict(M1=m1, E1=e1, g1=g1), sig


# --------------------------------------------------------------------------- #
# 3. Fisher fit with nuisances, several datasets
# --------------------------------------------------------------------------- #
def dataset(name, hw, level, ecut, ycat, scen, run, tfrac, live, I_uA=1.0):
    """One histogram the fit sees: per-day expectation and its derivatives."""
    y = YIELDS.loc[scen]
    t = templates(hw, level, ecut, ycat)
    ng0 = y.Y_g0 * I_uA * 1e-6 / LR.E_CHARGE * 86400 * live           # γ0 per (live-corrected) day
    comp, sig = physics(y, t, '0', run)
    cp = {v: physics(y, t, v, run)[0] for v in ('k+', 'k-', 'e+', 'e-', 'p1', 'p2')}

    def tot(c):
        return sum(c.values())
    mu = ng0 * tot(comp) + t['cos'] * live
    return dict(name=name, run=run, tfrac=tfrac, mu=mu, sig=ng0 * sig * R_ATOMKI,
                norms={f'{run}:{k}': ng0 * v for k, v in comp.items()},
                dk=ng0 * (tot(cp['k+']) - tot(cp['k-'])) / (2 * K_STEP),
                de=ng0 * (tot(cp['e+']) - tot(cp['e-'])) / (2 * E_STEP),
                dp1=ng0 * tot(cp['p1']), dp2=ng0 * tot(cp['p2']))


def gp_modes(delta, ell):
    """Unknown local structure as a Gaussian process on the 2° bins: relative
    amplitude delta, squared-exponential correlation length ell [deg].  Returns
    basis rows (each × μ is dμ/dc for a unit-prior coefficient c)."""
    ell = ell * UNIT                      # ℓ is given in degrees-equivalent
    C = delta ** 2 * np.exp(-0.5 * ((XC[:, None] - XC[None, :]) / ell) ** 2)
    w, v = np.linalg.eigh(C)
    keep = w > 1e-6 * w.max()
    return (v[:, keep] * np.sqrt(w[keep])).T


def fisher(dsets, npoly=3, prior_k=0.10, prior_e=0.02, prior_a='free', gp_shared=None, gp_ind=None,
           one_norm=False, k_e=True, prior_cat=0.05, aniso=True):
    """Fisher matrix per signal-run day (data part F) and the prior part P.
    Parameters: r = R / R_ATOMKI; physics norms per run (or one IPC norm + γ1
    per run); resolution scale k and E scale e; a shared acceptance polynomial
    a1..a_npoly (prior_a: σ per coefficient, or 'free'); unknown local structure
    as Gaussian-process modes, gp_shared = (δ, ℓ) common to every dataset (the
    detector) and gp_ind = (δ, ℓ) independent per dataset (sample-specific
    effects: how well a control carries over).  GP coefficients have unit priors.
    With several datasets each also gets a normalisation nuisance (prior_cat):
    the MC split of a run's pairs between the categories is not exact.
    aniso: the γ* anisotropy coefficients a1, a2 per run (priors PRIOR_AN1/2)."""
    names = ['r']
    for d in dsets:
        keys = ([f"{d['run']}:IPC", f"{d['run']}:g1"] if one_norm else list(d['norms']))
        names += [k for k in keys if k not in names]
    if k_e:
        names += ['k', 'e']
    if aniso:
        names += [f"{p}|{r}" for r in dict.fromkeys(d['run'] for d in dsets) for p in ('an1', 'an2')]
    names += [f'a{n}' for n in range(1, npoly + 1)]
    gs = gp_modes(*gp_shared) if gp_shared else np.zeros((0, len(XC)))
    gi = gp_modes(*gp_ind) if gp_ind else np.zeros((0, len(XC)))
    names += [f'gs{j}' for j in range(len(gs))]
    names += [f"gi{j}|{d['name']}" for d in dsets for j in range(len(gi))]
    multi = len(dsets) > 1
    if multi:
        names += [f"n|{d['name']}" for d in dsets]
    ix = {n: i for i, n in enumerate(names)}
    F = np.zeros((len(names), len(names)))
    for d in dsets:
        ok = d['mu'] > 0
        g = np.zeros((len(names), len(XC)))
        g[0] = d['sig']
        for k, v in d['norms'].items():
            kk = (f"{d['run']}:g1" if k.endswith(':g1') else f"{d['run']}:IPC") if one_norm else k
            g[ix[kk]] += v
        if k_e:
            g[ix['k']], g[ix['e']] = d['dk'], d['de']
        if aniso:
            g[ix[f"an1|{d['run']}"]], g[ix[f"an2|{d['run']}"]] = d['dp1'], d['dp2']
        for n in range(1, npoly + 1):
            g[ix[f'a{n}']] = d['mu'] * LEG[n]
        for j in range(len(gs)):
            g[ix[f'gs{j}']] = d['mu'] * gs[j]
        for j in range(len(gi)):
            g[ix[f"gi{j}|{d['name']}"]] = d['mu'] * gi[j]
        if multi:
            g[ix[f"n|{d['name']}"]] = d['mu']
        F += d['tfrac'] * (g[:, ok] / d['mu'][ok]) @ g[:, ok].T
    P = np.zeros_like(F)
    for n, i in ix.items():
        s = {'k': prior_k, 'e': prior_e}.get(n)
        if n[0] == 'a' and n[1:].isdigit():
            s = prior_a
        if n.startswith('g'):
            s = 1.0
        if n.startswith('n|'):
            s = prior_cat
        if n.startswith('an1|'):
            s = PRIOR_AN1
        if n.startswith('an2|'):
            s = PRIOR_AN2
        if s is not None and s != 'free':
            P[i, i] = 1 / s ** 2
    return F, P, names


def sigma_r(F, P, T):
    M = T * F + P
    try:
        c = np.linalg.inv(M)[0, 0]
    except np.linalg.LinAlgError:
        return np.inf
    return float(np.sqrt(c)) if c > 0 else np.inf


def z_at(F, P, T):
    return 1 / sigma_r(F, P, T)


def days_to(F, P, z=3.0):
    """signal-run days for z σ at R_ATOMKI (r = 1); inf if the priors cap Z below z."""
    if z_at(F, P, 1e8) < z:
        return np.inf
    lo, hi = 1e-4, 1e8
    for _ in range(100):
        mid = np.sqrt(lo * hi)
        lo, hi = (lo, mid) if z_at(F, P, mid) >= z else (mid, hi)
    return hi


def counting(d):
    """S/√B in the best window (≥ 10°), B exact: days to 3σ."""
    cs, cb = np.r_[0, np.cumsum(d['sig'])], np.r_[0, np.cumsum(d['mu'])]
    best, win = 0.0, None
    nmin = 5 if VAR == 'theta' else 4          # ≥ 10° or ≥ 1 MeV
    for i in range(len(XC)):
        for j in range(i + nmin, len(XC) + 1):
            b = cb[j] - cb[i]
            if b > 0 and (cs[j] - cs[i]) / np.sqrt(b) > best:
                best, win = (cs[j] - cs[i]) / np.sqrt(b), (BINS[i], BINS[j])
    i, j = np.searchsorted(BINS, win[0]), np.searchsorted(BINS, win[1])
    return 9 / best ** 2, win, (cs[j] - cs[i]) / (cb[j] - cb[i])


# --------------------------------------------------------------------------- #
# the study
# --------------------------------------------------------------------------- #
LEVEL = 'MM 15° + TOF'          # the reference level (lnl_geant REF_LEVEL)
HWS = {'big plastics': ((13, 18), 0.99), 'as built': ((13, 17), 0.999)}   # best E_sum window, DAQ live
YOPP = {'all': None, 'y<0.5': 'y>0.5', 'y<0.3': 'y>0.3', 'y<0.2': 'y>0.2'}
ELL = 10.0                      # GP correlation length [deg], ~ the X17 peak width
T_441 = 0.25                    # 441 keV run time / 1.10 MeV run time


def sets(hw, ycat):
    ec, live = HWS[hw]
    sig = dataset('sig', hw, LEVEL, ec, ycat, SIG_RUN, '18', 1.0, live)
    inrun = []
    if YOPP[ycat]:
        inrun.append(dataset('asym', hw, LEVEL, ec, YOPP[ycat], SIG_RUN, '18', 1.0, live))
    inrun.append(dataset('g1side', hw, LEVEL, (ec[0] - 4, ec[0]), 'all', SIG_RUN, '18', 1.0, live))
    c441 = dataset('441', hw, LEVEL, ec, ycat, CTRL_RUN, '17', T_441, live)
    return sig, inrun, c441


def rungs(sig, inrun, c441):
    """The ladder of assumptions: (label, short, (F, P), beam days per signal-run day)."""
    det = dict(npoly=3, prior_a='free')
    return [
        ('counting in the best window, B exact', 'count', None, 1.0),
        ('template fit, shapes exact (one IPC norm + γ₁)', 'fit 1 norm',
         fisher([sig], npoly=0, one_norm=True, k_e=False, aniso=False)[:2], 1.0),
        ('+ M1, E1, γ₁ norms free', 'M1/E1 free', fisher([sig], npoly=0, k_e=False, aniso=False)[:2], 1.0),
        ('+ γ* anisotropy about the beam (a₁ ± 0.3, a₂ ± 0.15)', 'anisotropy',
         fisher([sig], npoly=0, k_e=False)[:2], 1.0),
        ('+ resolution ±10 %, E scale ±2 %, acceptance cubic ±2 % (calibrated detector)', 'detector ±2 %',
         fisher([sig], npoly=3, prior_a=0.02)[:2], 1.0),
        ('+ acceptance cubic free', 'acc. free', fisher([sig], **det)[:2], 1.0),
        ('+ unknown structure 1 % (ℓ 10°)', 'struct 1 %', fisher([sig], gp_shared=(0.01, ELL), **det)[:2], 1.0),
        ('+ unknown structure 2 % (ℓ 10°)', 'struct 2 %', fisher([sig], gp_shared=(0.02, ELL), **det)[:2], 1.0),
        ('… 2 % with ℓ 5° (edge-like)', 'struct 2 %, ℓ 5°',
         fisher([sig], gp_shared=(0.02, 5.0), **det)[:2], 1.0),
        ('2 % shared + in-run controls (asym. pairs, γ₁ side-band), 1 % transfer, ±5 % category norm',
         '+ in-run ctrl',
         fisher([sig] + inrun, gp_shared=(0.02, ELL), gp_ind=(0.01, ELL), **det)[:2], 1.0),
        ('… + 441 keV run (¼ of the time)', '+ 441 keV',
         fisher([sig] + inrun + [c441], gp_shared=(0.02, ELL), gp_ind=(0.01, ELL), **det)[:2], 1 + T_441),
    ]


def ladder():
    rows = []
    for hw in HWS:
        for ycat in ('all', 'y<0.5', 'y<0.3'):
            sig, inrun, c441 = sets(hw, ycat)
            cd, win, sb = counting(sig)
            for i, (lab, short, FP, tpt) in enumerate(rungs(sig, inrun, c441)):
                if FP is None:
                    d, z30 = cd, 3 * np.sqrt(30 / cd)
                else:
                    d = days_to(*FP) * tpt
                    z30 = z_at(*FP, 30 / tpt)
                rows.append(dict(hw=hw, ycat=ycat, step=i, rung=lab, short=short, days_3sigma=d, Z_30d=z30,
                                 S_per_day=sig['sig'].sum(), B_per_day=sig['mu'].sum(),
                                 win=f'{win[0]:g}-{win[1]:g}', SB_win=sb))
    return pd.DataFrame(rows)


def delta_scan():
    rows = []
    det = dict(npoly=3, prior_a='free')
    for hw in HWS:
        for ycat in ('all', 'y<0.3'):
            sig, inrun, c441 = sets(hw, ycat)
            for dl in (0.0025, 0.005, 0.01, 0.015, 0.02, 0.03, 0.05):
                a = fisher([sig], gp_shared=(dl, ELL), **det)[:2]
                b = fisher([sig] + inrun, gp_shared=(dl, ELL), gp_ind=(dl / 2, ELL), **det)[:2]
                rows.append(dict(hw=hw, ycat=ycat, delta=dl, days_sig_only=days_to(*a),
                                 days_inrun_ctrl=days_to(*b), Z30_sig_only=z_at(*a, 30), Z30_inrun=z_at(*b, 30)))
    return pd.DataFrame(rows)


YB = np.arange(0, 1.0001, 0.05)
TB = np.arange(90, 181, 5.0)


def coefs(y):
    """per-γ0 weight of each pair sample (as physics(), without EPC/cosmics: ≤ 1 %)."""
    a = ALPHA
    f17, fr, fd, fg = y.frac_17_64, y.frac_18_15_res, y.frac_direct, y.frac_g1_direct
    g1r = y.Y_g1 / y.Y_g0
    return {'M1_17.64': f17 * a[(17.64, 'M1')], 'M1_18.15': fr * a[(18.15, 'M1')], 'E1_18.15': fd * a[(18.15, 'E1')],
            'M1_15.1': g1r * (1 - f17) * (1 - fg) * a[(15.1, 'M1')], 'E1_15.1': g1r * (1 - f17) * fg * a[(15.1, 'E1')],
            'M1_14.6': g1r * f17 * (1 - fg) * a[(14.6, 'M1')], 'E1_14.6': g1r * f17 * fg * a[(14.6, 'E1')],
            'X17_m16.7': (1 - f17) * R_ATOMKI}


def y_explain():
    """Where signal and background sit in (θ, |y|), per day at 1 µA, and the |y| cut scan."""
    y = YIELDS.loc[SIG_RUN]
    cf = coefs(y)
    rows2, rows1, scan = [], [], []
    for hw, (ec, live) in HWS.items():
        ng0 = y.Y_g0 * 1e-6 / LR.E_CHARGE * 86400 * live
        H = {'X17': np.zeros((len(TB) - 1, len(YB) - 1)), 'IPC': np.zeros((len(TB) - 1, len(YB) - 1))}
        for smp, c in cf.items():
            if smp.startswith('X17'):
                z, f = G.load('L1', smp, hw), 1.0
            else:
                z, f, _ = load_ipc(smp, hw)
            if z is None:
                continue
            m = cat_mask(z, LEVEL, ec, 'all')
            w = np.full(len(m), f / z['ngen'])
            if smp in ANISO and 'em_p' in z:
                cc = kcos(z)
                w = w * (1 + ANISO[smp][0] * cc + ANISO[smp][1] * 0.5 * (3 * cc ** 2 - 1))
            h, _, _ = np.histogram2d(z['reco_c'][m], asym(z)[m], [TB, YB], weights=w[m])
            H['X17' if smp.startswith('X17') else 'IPC'] += ng0 * c * h
        for comp, h in H.items():
            for i in range(len(TB) - 1):
                for j in range(len(YB) - 1):
                    rows2.append(dict(hw=hw, comp=comp, theta_lo=TB[i], y_lo=YB[j], per_day=h[i, j]))
            win = h[(TB[:-1] >= 130) & (TB[:-1] < 160)].sum(0)
            rows1 += [dict(hw=hw, comp=comp, y_lo=YB[j], per_day=win[j]) for j in range(len(YB) - 1)]
        for yc in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0):
            ycat = 'all' if yc >= 1 else f'y<{yc:g}'
            sig = dataset('sig', hw, LEVEL, ec, ycat, SIG_RUN, '18', 1.0, live)
            dc, win, sb = counting(sig)
            det = dict(npoly=3, prior_a='free')
            f2 = fisher([sig], gp_shared=(0.02, ELL), **det)[:2]
            inrun = [dataset('g1side', hw, LEVEL, (ec[0] - 4, ec[0]), 'all', SIG_RUN, '18', 1.0, live)]
            if ycat != 'all':
                inrun.append(dataset('asym', hw, LEVEL, ec, f'y>{yc:g}', SIG_RUN, '18', 1.0, live))
            fc = fisher([sig] + inrun, gp_shared=(0.02, ELL), gp_ind=(0.01, ELL), **det)[:2]
            w = (XC >= WIN[0]) & (XC < WIN[1])
            scan.append(dict(hw=hw, ycut=yc, S_130_160=sig['sig'][w].sum(), B_130_160=sig['mu'][w].sum(),
                             SB_best=sb, best_win=f'{win[0]:g}-{win[1]:g}', days_count=dc,
                             days_struct2=days_to(*f2), days_ctrl=days_to(*fc)))
    return pd.DataFrame(rows2), pd.DataFrame(rows1), pd.DataFrame(scan)


def ycut_table():
    rows = []
    for hw, (ec, live) in HWS.items():
        for ycat in ('all', 'y<0.5', 'y<0.3', 'y<0.2'):
            sig = dataset('sig', hw, LEVEL, ec, ycat, SIG_RUN, '18', 1.0, live)
            d, win, sb = counting(sig)
            w = (XC >= WIN[0]) & (XC < WIN[1])
            rows.append(dict(hw=hw, ycat=ycat, S_130_160=sig['sig'][w].sum(), B_130_160=sig['mu'][w].sum(),
                             SB_130_160=sig['sig'][w].sum() / sig['mu'][w].sum(), best_win=f'{win[0]:g}-{win[1]:g}',
                             SB_best=sb, days_count=d))
    t = pd.DataFrame(rows)
    for hw in HWS:
        ref = t[(t.hw == hw) & (t.ycat == 'all')].iloc[0]
        m = t.hw == hw
        t.loc[m, 'eff_X17'] = t.loc[m, 'S_130_160'] / ref.S_130_160
        t.loc[m, 'eff_B'] = t.loc[m, 'B_130_160'] / ref.B_130_160
    return t


def spectra():
    """expected counts per 2° in 10 beam days, IPC and X17, all vs y<0.3 (big plastics)."""
    rows = []
    for hw in HWS:
        for ycat in ('all', 'y<0.3'):
            sig = sets(hw, ycat)[0]
            for x, b, s in zip(XC, sig['mu'], sig['sig']):
                rows.append(dict(hw=hw, ycat=ycat, theta=x, B_10d=10 * b, S_10d=10 * s))
    return pd.DataFrame(rows)


def figures(atk, lad, scan, sp):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    sys.path.insert(0, str(LNL.parent / 'ill'))
    import figstyle as fs
    fs.use()
    FIG = OUT / 'figures'
    FIG.mkdir(parents=True, exist_ok=True)

    # 1. ATOMKI at truth level vs their Fig. 4
    fig, ax = fs.figure()
    cols = ['#0072B2', '#56B4E9', '#999999', '#D55E00', '#E69F00', '#009E73']
    for (case, g), c in zip(atk.groupby('case', sort=False), cols):
        g = g[g.theta >= 85]
        ax.plot(g.theta, (g.ratio - 1) * 100, color=c, marker='o', ms=3, label=case)
    f4 = ATOMKI_FIG4
    ax.plot(f4.theta, (f4.data / f4.ipc - 1) * 100, 'ks', ms=5, label='ATOMKI 2016 Fig. 4 (data / no-boson curve)')
    ax.axhline(0, color=fs.MUTED, lw=0.6)
    ax.set_xlabel('opening angle [deg] (10° bins)')
    ax.set_ylabel('X17 excess over IPC [%]')
    ax.legend(frameon=False, fontsize=6.5, loc='upper left')
    fs.title(ax, 'The ATOMKI bump is a 25–35 % excess, not a peak',
             'Truth-level Born IPC + X17 (m 16.7) at R = 5.8e-6, 18.15 MeV, acceptance-corrected; ATOMKI read off PRL 116 042501')
    fs.save(fig, FIG / 'atomki_repro', data=atk)

    # 2. the ladder
    fig, axs = plt.subplots(1, 2, figsize=fs.WIDE, sharey=True)
    ycol = {'all': '#0072B2', 'y<0.5': '#E69F00', 'y<0.3': fs.ACCENT}
    for ax, hw in zip(axs, HWS):
        g0 = lad[lad.hw == hw]
        steps = g0.step.unique()
        for k, (ycat, g) in enumerate(g0.groupby('ycat', sort=False)):
            v = np.minimum(g.days_3sigma.values, 3e4)
            ax.barh(steps + (k - 1) * 0.27, v, 0.26, color=ycol[ycat], label=f'{ycat} pairs' if ycat != 'all' else 'all pairs')
        ax.set_xscale('log')
        ax.set_yticks(steps, g0[g0.ycat == 'all'].short)
        ax.invert_yaxis()
        ax.axvline(30, color=fs.MUTED, lw=0.6, ls='--')
        ax.set_xlabel('beam days at 1 µA for 3σ at R(ATOMKI)')
        ax.set_title(hw, fontsize=9)
    axs[0].legend(frameon=False, fontsize=7, loc='lower right')
    fs.fig_title(fig, 'What the reach costs once the background shape is not known exactly',
                 'Geant4, MM 15° + TOF, Li₂O 300 µg/cm² at 1.10 MeV; each row adds freedom to the fit; dashed: 30 days')
    fs.save(fig, FIG / 'syst_ladder', data=lad)

    # 3. days vs δ
    fig, ax = fs.figure()
    for (hw, ycat), g in scan.groupby(['hw', 'ycat'], sort=False):
        c = '#D55E00' if hw == 'big plastics' else '#0072B2'
        ls = '-' if ycat == 'y<0.3' else ':'
        ax.plot(g.delta * 100, g.days_sig_only, color=c, ls=ls, marker='o', ms=3, label=f'{hw}, {ycat}: signal run only')
        ax.plot(g.delta * 100, g.days_inrun_ctrl, color=c, ls=ls, marker='s', ms=3, mfc='white',
                label=f'{hw}, {ycat}: + in-run controls')
    ax.set_yscale('log')
    ax.set_ylim(0.5, 3e4)
    ax.axhline(30, color=fs.MUTED, lw=0.6, ls='--')
    ax.set_xlabel('unknown structure δ in the background shape [%] (ℓ = 10°)')
    ax.set_ylabel('beam days for 3σ at R(ATOMKI)')
    ax.legend(frameon=False, fontsize=6.5, ncol=1)
    fs.title(ax, 'How well the background shape must be known',
             'Asimov/Fisher, M1/E1/γ₁ free, detector nuisances; controls share the structure, transfer δ/2')
    fs.save(fig, FIG / 'syst_delta', data=scan)

    # 4. what 10 days look like: all vs y<0.3, big plastics
    fig, axs = plt.subplots(1, 2, figsize=fs.WIDE)
    rng = np.random.default_rng(4)
    for ax, ycat in zip(axs, ('all', 'y<0.3')):
        g = sp[(sp.hw == 'big plastics') & (sp.ycat == ycat)]
        b, s = g.B_10d.values, g.S_10d.values
        # 10° bins as ATOMKI
        e10 = np.arange(90, 181, 10)
        bb = np.add.reduceat(b, np.arange(0, len(b), 5))
        ss = np.add.reduceat(s, np.arange(0, len(s), 5))
        xc = e10[:-1] + 5
        obs = rng.poisson(bb + ss)
        ax.step(xc, bb, where='mid', color='#0072B2', label='IPC + EPC + cosmics')
        ax.step(xc, bb + ss, where='mid', color=fs.ACCENT, label='+ X17 at R(ATOMKI)')
        ax.errorbar(xc, obs, yerr=np.sqrt(obs), fmt='ko', ms=3, label='one pseudo-experiment')
        ax.set_yscale('log')
        ax.set_xlabel('reconstructed opening angle [deg]')
        sb = ss[(xc > 130) & (xc < 160)].sum() / bb[(xc > 130) & (xc < 160)].sum()
        ax.set_title(f'{"all pairs" if ycat == "all" else "|y| < 0.3"}: S/B {sb*100:.0f} % in 130–160°', fontsize=9)
    axs[0].set_ylabel('pairs per 10° in 10 days at 1 µA')
    axs[0].legend(frameon=False, fontsize=7)
    fs.fig_title(fig, 'Big plastics, 10 days: the symmetric cut makes the bump visible',
                 'Geant4, MM 15° + TOF, E_sum 13–18 MeV; |y| = |E₁ − E₂| / (E₁ + E₂) from the arm energies')
    fs.save(fig, FIG / 'syst_spectra', data=sp)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pd.set_option('display.width', 250)
    pd.set_option('display.max_columns', 30)
    atk, s = atomki_repro()
    atk.to_csv(OUT / 'atomki_repro.csv', index=False)
    print(atk[atk.theta >= 115].pivot_table(index='case', columns='theta', values='ratio', sort=False).round(3).to_string())
    print(s)
    y2, y1, ys = y_explain()
    y2.to_csv(OUT / 'y_theta_map.csv', index=False)
    y1.to_csv(OUT / 'y_window.csv', index=False)
    ys.to_csv(OUT / 'y_scan.csv', index=False)
    print(ys.round(3).to_string(index=False))
    yt = ycut_table()
    yt.to_csv(OUT / 'ycut.csv', index=False)
    print(yt.to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    lad = ladder()
    lad.to_csv(OUT / 'ladder.csv', index=False)
    print(lad.pivot_table(index=['step', 'short'], columns=['hw', 'ycat'], values='days_3sigma', sort=False)
          .round(2).to_string())
    print(lad.pivot_table(index=['step', 'short'], columns=['hw', 'ycat'], values='Z_30d', sort=False)
          .round(2).to_string())
    scan = delta_scan()
    scan.to_csv(OUT / 'delta_scan.csv', index=False)
    print(scan.round(3).to_string(index=False))
    sp = spectra()
    sp.to_csv(OUT / 'spectra_10d.csv', index=False)
    # the same ladder, scan and spectra fitted in the reconstructed mass m_ee
    use_var('mass')
    lad_m = ladder()
    lad_m.to_csv(OUT / 'ladder_mass.csv', index=False)
    print('== fitted in m_ee ==')
    print(lad_m.pivot_table(index=['step', 'short'], columns=['hw', 'ycat'], values='days_3sigma', sort=False)
          .round(2).to_string())
    print(lad_m.pivot_table(index=['step', 'short'], columns=['hw', 'ycat'], values='Z_30d', sort=False)
          .round(2).to_string())
    scan_m = delta_scan()
    scan_m.to_csv(OUT / 'delta_scan_mass.csv', index=False)
    print(scan_m.round(3).to_string(index=False))
    sp_m = spectra()
    sp_m.to_csv(OUT / 'spectra_10d_mass.csv', index=False)
    use_var('theta')
    summ = dict(atomki=s, ladder=lad.to_dict('records'), ycut=yt.to_dict('records'))
    (OUT / 'summary.json').write_text(json.dumps(summ, indent=1, default=float))
    figures(atk, lad, scan, sp)
    return 0


if __name__ == '__main__':
    sys.exit(main())
