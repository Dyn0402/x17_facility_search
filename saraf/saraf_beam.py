#!/usr/bin/env python3
"""
saraf_beam.py -- SARAF (Soreq, Yavne): the LiLiT keV-neutron source and the Phase II linac for the X17 study
(saraf/FACILITY.md, FEASIBILITY.md), with the reach from the shared Geant4 soft-beam background.

    python saraf/saraf_beam.py --check         # reproduce published rows (Birmingham, FRANZ) with the shared engine
    python saraf/saraf_beam.py                 # beam tables + reach -> saraf/out/saraf_*.{csv,png}
    python saraf/saraf_beam.py --beam-only     # the beam model only (no Geant4 tables needed)
    python saraf/saraf_beam.py --post          # shield estimate + summary figure from the reach tables

Three source families, every yield tied to a published number where one exists:

LiLiT family (thick liquid Li, ⁷Li(p,n)): slowing-down MC as in franz_beam.py / bham_beam.py, σ(E_p) table extended
  above 3 MeV (ESTIMATE: flat at ~250 mb, ⁷Li(p,n₁) channel not modelled), CM-isotropic.  The absolute scale is set by
  the MEASURED LiLiT yield, 2.5×10¹⁰ n/s/mA at 1.925 MeV (3-5×10¹⁰ n/s at 1-2 mA: Tessler et al. PLB 751 (2015),
  arXiv:1511.04701; Mardor et al. EPJA 54 (2018) 91, "~2×10¹⁰ n/s/mA").
  The ⁸Be γ: MEASURED at LiLiT, 3×10⁸ (17.6 MeV) + 4×10⁸ (14.6 MeV) γ/s/mA (Tessler 2015), i.e. 1.1×10⁻⁷ γ/p,
  which confirms the Birmingham / FRANZ thick-target stand-in of 1×10⁻⁷.  LiLiT is a 1.5 mm stopping jet: every proton
  crosses the 441 and 1030 keV resonances, so there is no thin-target option without building a different target.

p + Be family (⁹Be(p,n), solid Be): bepn_cyclotron/bepn_beam.py (ENDF/B-VIII.0 LA150, verified there at 16-30 MeV only).
  Below 8 MeV it is an evaluation extrapolation: ESTIMATE.

d + Be family (⁹Be(d,n)): ganil_nfs/nfs_beam.py (Serber + Watt, Morrell & Bernstein, anchored to the measured NFS flux at
  40 MeV).  At E_d ≲ 15 MeV the stripping model is an extrapolation: the 5 MeV row is an ESTIMATE of order of magnitude.
  γ: stand-in, 1 γ per neutron at 0.7-3.4 MeV lines (ESTIMATE).

Reach: the survey/soft_sim engine (N5/G5/G6, + N4 above 20 MeV through bepn_reach).  Beam-only: Ø8 cm spot, vacuum tube,
no room, no shield, no target chamber scatter.  CW: no TOF tag.
"""
from __future__ import annotations

import argparse
import functools
import sys
from pathlib import Path

import numpy as np
import pandas as pd
if not hasattr(np, 'trapezoid'):
    np.trapezoid = np.trapz

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / 'out'
for p in ('birmingham', 'franz', 'bepn_cyclotron', 'ganil_nfs', 'survey/soft_sim', 'ill'):
    sys.path.insert(0, str(ROOT / p))
import bham_beam as BB                                        # noqa: E402

E_CHARGE = BB.E_CHARGE
E_TH = BB.E_TH
P_PER_MA = 1e-3 / E_CHARGE
Y_LILIT = 2.5e10                                              # n/s/mA at 1.925 MeV, measured (3-5e10 n/s at 1-2 mA)
E_LILIT = 1.925
Y_BHAM = 1e12                                                 # n/s/mA at 2.6 MeV (Birmingham facility number; cross-check)
GAMMA_8BE = 7e8                                               # γ/s/mA, 17.6 + 14.6 MeV, measured at LiLiT (Tessler 2015)
LINES_8BE = [(17.64, 3 / 7), (14.64, 4 / 7)]                  # measured 3:4
S_LI = 0.19                                                   # MeV cm²/mg, p in Li at ~2 MeV (estimate, as franz)
N_LI7 = 0.925 * 6.022e23 / 6.94 * 1e-3                        # ⁷Li per mg natural Li
G478_25 = 6e-5                                                # 478 keV γ/p at 2.5 MeV thick (Taskaev 2006)
AREA = 50.0                                                   # cm², the Ø8 cm cell spot
MU_PB = {'n_kev': 0.36, 'n': 0.20, 'g478': 1.76, 'g15': 0.57}  # /cm Pb (as FRANZ / soft_reach)
SIG_EXT = np.array([[3.5, 245.0], [4.0, 240.0], [4.5, 240.0]])  # mb, ESTIMATE (Liskien & Paulsen trend, n0 only)
SIG = np.vstack([BB.SIG_TAB, SIG_EXT])
E_BINS = np.concatenate([np.arange(0, 0.7, 0.002), np.arange(0.7, 3.5, 0.02)])
EPS = (1.925, 2.2, 2.6, 2.8, 3.0, 3.5, 4.0)                   # LiLiT family proton energies, MeV
PBE = (3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 14.0, 18.0)             # p+Be, MeV
DBE = (5.0, 10.0, 15.0, 20.0, 30.0, 40.0)                     # d+Be, MeV


# --------------------------------------------------------------------------- #
def sigma_mb(ep):
    return np.interp(ep, SIG[:, 0], SIG[:, 1])


@functools.lru_cache(maxsize=None)
def mc(ep0, n=4_000_000, seed=3):
    """thick-Li slowing-down MC, 1.881 MeV ... ep0: (E_n, cosθ_lab, w) with w in n/p (absolute σ/S)."""
    rng = np.random.default_rng(seed)
    lo = E_TH + 1e-5
    ep = rng.uniform(lo, ep0, n)
    s = S_LI * (ep / 2.0) ** -0.8
    w = N_LI7 * sigma_mb(ep) * 1e-27 / s * (ep0 - lo) / n
    e_cm_f = ep * BB.M_LI / (BB.M_P + BB.M_LI) + BB.Q
    ok = e_cm_f > 0
    mu_f = BB.M_N * BB.M_BE / (BB.M_N + BB.M_BE)
    v_n_cm = np.sqrt(2 * mu_f * np.clip(e_cm_f, 0, None)) / BB.M_N
    v_cm = np.sqrt(2 * ep / BB.M_P) * BB.M_P / (BB.M_P + BB.M_LI)
    cth = rng.uniform(-1, 1, n)
    vx = v_n_cm * np.sqrt(1 - cth ** 2)
    vz = v_n_cm * cth + v_cm
    v2 = vx ** 2 + vz ** 2
    return 0.5 * BB.M_N * v2[ok], (vz / np.sqrt(v2))[ok], w[ok]


def model_yield_per_ma(ep0):
    return mc(ep0)[2].sum() * P_PER_MA


NORM = Y_LILIT / model_yield_per_ma(E_LILIT)                  # applied to every E_p (measured-LiLiT scale)


@functools.lru_cache(maxsize=None)
def spectra(ep0):
    """0° spectrum (cosθ > 0.99), per sr per mA; 4π yield; angular info."""
    e, c, w = mc(ep0)
    w = w * P_PER_MA * NORM
    sel = c > 0.99
    dom = 2 * np.pi * 0.01
    h0, _ = np.histogram(e[sel], E_BINS, weights=w[sel])
    dyde0 = h0 / dom / np.diff(E_BINS)
    x = 0.5 * (E_BINS[1:] + E_BINS[:-1])
    return dict(x=x, dyde0=dyde0, y0=float(h0.sum() / dom), ytot=float(w.sum()), mean0=float((h0 * x).sum() / max(h0.sum(), 1e-30)),
                emax0=float(e[sel].max()), cmin=float(c.min()), f_below_1keV=float(w[sel & (e < 1e-3)].sum() / max(w[sel].sum(), 1e-300)))


def spectrum_on_grid(ep0, grid):
    s = spectra(ep0)
    f = np.interp(grid, s['x'], s['dyde0'], left=0.0, right=0.0)
    return f / np.trapezoid(f, grid)


def lilit_source(SR, ep, pb):
    """1 mA, 1 m reference: LiLiT-class thick Li."""
    s = spectra(ep)
    om = AREA / 100 ** 2
    p_s = P_PER_MA
    g478 = G478_25 * max(0.0, (ep - 0.55) / 1.95) ** 2 * p_s + s['ytot'] * 0.104        # + saturated ⁷Be
    mun = MU_PB['n_kev'] if ep < 2.2 else MU_PB['n']
    n_cell = s['y0'] * om * np.exp(-mun * pb)
    gl = g478 * om / (4 * np.pi) * np.exp(-MU_PB['g478'] * pb)
    gh = GAMMA_8BE * om / (4 * np.pi) * np.exp(-MU_PB['g15'] * pb)
    fg, g_tot = SR._mix([(SR._lines([(0.478, 1.0)]), gl), (SR._lines(LINES_8BE), gh)])
    src = SR.Soft(f'lilit_{ep * 1000:.0f}_pb{pb:.0f}', f'LiLiT-class thick Li, E_p {ep} MeV, {pb:.0f} cm Pb; 1 mA, 1 m',
                  spectrum_on_grid(ep, SR.E_GRID), n_cell, fg, g_tot, 'saraf',
                  note=f'per mA at 1 m: γ 478 {gl:.2g}/s, 15-18 MeV {gh:.2g}/s; mean E_n(0°) {s["mean0"] * 1e3:.0f} keV')
    src.family, src.e0, src.pb, src.th = 'lilit', ep, pb, 0.0
    return src


def pbe_source(SR, ep, th):
    import bepn_beam as BP
    b = BP.beam(ep, 1e-3, th, 1.0)
    src = SR.Soft(f'pbe_{ep:.0f}_{th:.0f}', f'p + thick Be, E_p {ep} MeV, θ {th:.0f}°; 1 mA, 1 m',
                  BP.spectrum_on_grid(ep, th, SR.E_GRID), b['n_cell'], BP.gamma_on_grid(ep, SR.E_GRID), b['g_cell'], 'saraf',
                  note=f'mean E_n {b["mean_En"]:.2f} MeV; <2.75 MeV {b["f_below_2p75"]:.2f}; Y {b["n_tot"]:.3g} n/s/mA')
    src.family, src.e0, src.pb, src.th = 'pbe', ep, 0.0, th
    return src


def _dbe_shape(ed, th, e):
    import nfs_beam as NB
    y = NB.thick_target_yield(e, theta=np.radians(th), e_d0=ed)
    return np.asarray(y) * NB.absolute_scale(e_d0=40.0)


def dbe_total(ed):
    """n/s/mA total from the model, integrated over θ (rad grid)."""
    ths = np.radians(np.array([1, 5, 10, 20, 30, 45, 60, 90, 120, 150, 178.0]))
    e = np.linspace(0.05, 55.0, 700)
    ys = np.array([np.trapezoid(_dbe_shape(ed, np.degrees(t), e), e) for t in ths])
    return float(2 * np.pi * np.trapezoid(ys * np.sin(ths), ths)) * 1e3                 # /µC → per mA


def dbe_source(SR, ed, th):
    e = SR.E_GRID
    y = _dbe_shape(ed, th, e)
    y = np.where(e < 0.05, 0.0, y)
    om = AREA / 100 ** 2
    y_tot = np.trapezoid(y, e) * 1e3                                                     # n/s/mA/sr at θ
    fn = y / max(np.trapezoid(y, e), 1e-300)
    gl = dbe_total(ed) * om / (4 * np.pi)                                                # 1 γ per n, isotropic, ESTIMATE
    fg = SR._lines([(0.718, 0.3), (1.74, 0.1), (2.15, 0.1), (3.37, 0.5)])
    src = SR.Soft(f'dbe_{ed:.0f}_{th:.0f}', f'd + thick Be, E_d {ed} MeV, θ {th:.0f}°; 1 mA, 1 m',
                  fn, y_tot * om, fg, gl, 'saraf', note=f'n/s/mA/sr {y_tot:.3g}; model; <2.75 MeV frac'
                  f' {np.trapezoid(y[e <= 2.75], e[e <= 2.75]) / max(np.trapezoid(y, e), 1e-300):.2f}')
    src.family, src.e0, src.pb, src.th = 'dbe', ed, 0.0, th
    return src


# --------------------------------------------------------------------------- #
# Scenarios: current (mA) as a function of (family, energy); None = not applicable.
def phase1_current(e):
    """Phase I linac as operated: CW, ~2 mA at 2 MeV, ~1 mA at 4 MeV (M. Paul, CERN n_TOF talk 2021; 4 kW)."""
    return min(2.0, 4.0 / e)


def scenarios(family, e0):
    if family == 'lilit':
        d = {'phaseI': (phase1_current(e0), 'Phase I linac as operated (≤ 4 kW)')}
        if e0 == E_LILIT:
            d['as_ran'] = (1.5, 'LiLiT as ran 2014-18 (~1.5 mA, 2.9 kW)')
        d['phaseII'] = (5.0, 'Phase II 5 mA on a LiLiT-class jet (≥ 10 kW, not demonstrated)')
        return d
    if family == 'pbe':
        d = {}
        if e0 <= 4.0:
            d['phaseI'] = (phase1_current(e0), 'Phase I linac as operated (≤ 4 kW), needs a solid Be target')
        d['phaseII'] = (5.0, f'Phase II 5 mA, {5 * e0:.0f} kW on Be (target not planned)')
        return d
    if family == 'dbe':
        d = {}
        if e0 <= 5.0:
            d['phaseI'] = (1.0, 'Phase I deuterons ~1 mA, ≤ 5 MeV (commissioned to < 50 % duty in CW)')
        d['phaseII'] = (5.0, f'Phase II 5 mA d, {5 * e0:.0f} kW')
        return d
    raise ValueError(family)


DISTS = {'lilit': (0.3, 0.5, 1.0, 2.0), 'pbe': (0.5, 1.0, 2.0), 'dbe': (0.5, 1.0, 2.0)}


def sources(SR):
    S = []
    for ep in EPS:
        for pb in (0.0, 5.0):
            S.append(lilit_source(SR, ep, pb))
    for ep in PBE:
        for th in (0.0, 130.0):
            S.append(pbe_source(SR, ep, th))
    for ed in DBE:
        for th in (0.0, 130.0):
            S.append(dbe_source(SR, ed, th))
    return S


def reach(days=(14.0, 50.0), only=None):
    import bepn_reach as BR                                  # noqa: F401  (patches the engine: grid + N4 above 20 MeV)
    SR = BR.SR
    SR.E_GRID = np.unique(np.concatenate([np.geomspace(1e-3, 20.0, 3000), np.linspace(20.0, 40.0, 401)]))
    srcs = sources(SR)
    if only:
        srcs = [s for s in srcs if any(o in s.key for o in only)]
    rows, comps = [], []
    grid = np.geomspace(1e-4, 1.0, 41)
    SF, R, Y = SR.SF, SR.R, SR.Y
    for hw in R.HW:
        M = SF.nfs_model(hw)
        runs, _ = BR.load_runs(hw)
        for src in srcs:
            C = SR.components(src, runs, hw, M)
            cap = SR.captures(src)
            ipc_day = float((cap * Y.alpha(np.array(R.NODES))).sum() * SR.DAY)
            print(f'{hw:13s} {src.key:18s} per mA at 1 m: n_cell {src.n_cell:.3g}/s  ok/arm {C["ok_arm"].mean():.3g}  '
                  f'legs/arm {C["leg_arm"].mean():.3g}  γ share ok {C["ok_g_frac"]:.2f}  corr {C["corr_fact"]:.3g}/d', flush=True)
            for scen, (i_ma, what) in scenarios(src.family, src.e0).items():
                for d in DISTS[src.family]:
                    k = i_ma * (1.0 / d) ** 2
                    comps.append(dict(key=src.key, family=src.family, e0=src.e0, theta=src.th, pb_cm=src.pb, scen=scen, dist_m=d, hw=hw,
                                      i_mA=i_ma, power_kW=i_ma * src.e0, n_cell=src.n_cell * k, g_cell=src.g_cell * k,
                                      ok_singles_per_arm=C['ok_arm'].mean() * k, legs_per_arm=C['leg_arm'].mean() * k,
                                      ok_gamma_frac=C['ok_g_frac'], corr_trig_per_s=C['corr_trig'] * k, corr_fact_per_day=C['corr_fact'] * k,
                                      corr_mc=C['corr_n_mc'], ipc_per_day=ipc_day * k, note=src.note, what=what))
                    for dd in days:
                        for soft in (True, False):
                            res = []
                            for s in grid:
                                st = SR.at_throttle(src, C, M, cap, s * k)
                                res.append((SR.rho3(M, st, dd, soft), s, st))
                            r, s, st = min(res, key=lambda x: x[0])
                            st0 = SR.at_throttle(src, dict(C, acc_th=C['acc_th'] * 0, corr_th=C['corr_th'] * 0,
                                                           ok_arm=C['ok_arm'] * 0, leg_arm=C['leg_arm'] * 0, corr_trig=0.0), M, cap, k)
                            rows.append(dict(key=src.key, family=src.family, e0=src.e0, theta=src.th, pb_cm=src.pb, scen=scen, dist_m=d,
                                             i_mA=i_ma, hw=hw, days=dd, signal='E* ≤ 22 MeV' if soft else 'all E*', rho3=r,
                                             vs_ATOMKI=r / R.RHO_REF, throttle=s, rho3_floor=SR.rho3(M, st0, dd, soft),
                                             days_to_atomki=50 * (r / R.RHO_REF) ** 2 if dd == 50 else np.nan,
                                             live=st['live'], occ=st['occ'], **SR.window_counts(st, M, soft)))
    t, cp = pd.DataFrame(rows), pd.DataFrame(comps)
    t.to_csv(OUT / 'saraf_reach.csv', index=False, float_format='%.4g')
    cp.to_csv(OUT / 'saraf_components.csv', index=False, float_format='%.4g')
    return t, cp


# --------------------------------------------------------------------------- #
def check():
    """reproduce published rows with the shared engine (default grid, no extension): Birmingham (soft_reach.csv) and
    FRANZ design, thin Li, 0.5 m (franz_reach.csv)."""
    import soft_reach as SR
    import franz_beam as FB
    R, SF = SR.R, SR.SF
    hw = 'big plastics'
    M = SF.nfs_model(hw)
    runs = SR.load_runs(hw)
    out = []
    grid = np.geomspace(1e-4, 1.0, 41)
    src = [s for s in SR.sources() if s.key == 'bham_28_2m_pb5'][0]
    C, cap = SR.components(src, runs, hw, M), SR.captures(src)
    ref = pd.read_csv(ROOT / 'survey/soft_sim/out/soft_reach.csv')
    r = min(SR.rho3(M, SR.at_throttle(src, C, M, cap, s), 50.0, True) for s in grid)
    v = float(ref[(ref.key == src.key) & (ref.hw == hw) & (ref.days == 50) & (ref.signal == 'E* ≤ 22 MeV')].rho3.iloc[0])
    out.append(dict(row='Birmingham bham_28_2m_pb5, big plastics, 50 d', reproduced=r, published=v, ratio=r / v))
    src = [s for s in FB.sources() if s.key == 'franz_2000_thin_pb0'][0]
    C, cap = SR.components(src, runs, hw, M), SR.captures(src)
    k = 20.0 * (1.0 / 0.5) ** 2
    r = min(SR.rho3(M, SR.at_throttle(src, C, M, cap, s * k), 50.0, True) for s in np.geomspace(1e-3, 1.0, 31))
    q = pd.read_csv(ROOT / 'franz/out/franz_reach.csv')
    v = float(q[(q.key == src.key) & (q.scen == 'design') & (q.dist_m == 0.5) & (q.hw == hw) & (q.days == 50)].rho3.iloc[0])
    out.append(dict(row='FRANZ design 2.0 MeV thin Li 0.5 m, big plastics, 50 d', reproduced=r, published=v, ratio=r / v))
    t = pd.DataFrame(out)
    print(t.to_string(index=False))
    t.to_csv(OUT / 'saraf_engine_check.csv', index=False, float_format='%.4g')


# --------------------------------------------------------------------------- #
def beam_tables():
    import bepn_beam as BP
    rows, sp = [], []
    om1 = AREA / 100 ** 2
    for ep in EPS:
        s = spectra(ep)
        rows.append(dict(family='lilit', e0=ep, per_mA_total_n=s['ytot'], per_mA_0deg_sr=s['y0'], mean_En_0deg_MeV=s['mean0'],
                         max_En_0deg_MeV=s['emax0'], f_below_2p75=1.0, gamma_hi_per_mA=GAMMA_8BE, n_cell_1mA_1m=s['y0'] * om1, cos_min=s['cmin']))
        sp += [dict(source=f'LiLiT {ep} MeV', E_n=xi, per_mA_sr_MeV=v) for xi, v in zip(s['x'], s['dyde0']) if v > 0]
    for ep in PBE:
        b = BP.beam(ep, 1e-3, 0.0, 1.0)
        rows.append(dict(family='pbe', e0=ep, per_mA_total_n=b['n_tot'], per_mA_0deg_sr=b['n_per_sr'], mean_En_0deg_MeV=b['mean_En'], max_En_0deg_MeV=b['E_max'],
                         f_below_2p75=b['f_below_2p75'], gamma_hi_per_mA=b['g_tot'], n_cell_1mA_1m=b['n_cell'], cos_min=np.nan))
        e = BP.EBINS
        v = BP.at_angle(ep, 0.0) * P_PER_MA
        sp += [dict(source=f'p+Be {ep:.0f} MeV', E_n=xi, per_mA_sr_MeV=y) for xi, y in zip(0.5 * (e[1:] + e[:-1]), v) if y > 0]
    e = np.linspace(0.05, 55.0, 700)
    for ed in DBE:
        y = _dbe_shape(ed, 0.0, e) * 1e3
        frac = np.trapezoid(y[e <= 2.75], e[e <= 2.75]) / np.trapezoid(y, e)
        rows.append(dict(family='dbe', e0=ed, per_mA_total_n=dbe_total(ed), per_mA_0deg_sr=np.trapezoid(y, e), mean_En_0deg_MeV=np.trapezoid(y * e, e) / np.trapezoid(y, e),
                         max_En_0deg_MeV=float(e[y > 1e-3 * y.max()].max()), f_below_2p75=frac, gamma_hi_per_mA=dbe_total(ed), n_cell_1mA_1m=np.trapezoid(y, e) * om1, cos_min=np.nan))
        sp += [dict(source=f'd+Be {ed:.0f} MeV', E_n=xi, per_mA_sr_MeV=v) for xi, v in zip(e, y) if v > 0]
    t = pd.DataFrame(rows)
    t.to_csv(OUT / 'saraf_beam.csv', index=False, float_format='%.4g')
    chk = dict(model_abs_per_mA_1p925=model_yield_per_ma(E_LILIT), model_abs_per_mA_2p6=model_yield_per_ma(2.6), norm_applied=NORM,
               lilit_scale_per_mA_2p6=model_yield_per_ma(2.6) * NORM, bham_anchor_per_mA_2p6=Y_BHAM, ratio_to_bham=model_yield_per_ma(2.6) * NORM / Y_BHAM,
               gamma_per_p_measured=GAMMA_8BE / P_PER_MA)
    print({k: f'{v:.3g}' for k, v in chk.items()})
    pd.Series(chk).to_csv(OUT / 'saraf_yield_check.csv', header=['value'], float_format='%.4g')
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use()
    d = pd.DataFrame(sp)
    fig, ax = plt.subplots(figsize=(9, 4.4))
    show = [('LiLiT 1.925 MeV', fs.MUTED), ('LiLiT 2.6 MeV', fs.COPPER), ('LiLiT 4.0 MeV', fs.TRACK), ('p+Be 4 MeV', fs.ACCENT),
            ('p+Be 8 MeV', 'C4'), ('d+Be 5 MeV', 'C3'), ('d+Be 40 MeV', 'k')]
    for name, col in show:
        q = d[d.source == name]
        ax.plot(q.E_n, q.per_mA_sr_MeV, color=col, lw=1.6, label=name)
    ax.axvline(2.75, color='0.5', ls=':', lw=1)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(0.01, 50)
    ax.set_ylim(1e7, 3e13)
    ax.set_xlabel('E_n [MeV]')
    ax.set_ylabel('0° dY/dE dΩ [n / (s mA sr MeV)]')
    ax.legend(frameon=False, fontsize=8, ncol=2)
    fs.fig_title(fig, 'SARAF source candidates at 0°: the X17 window is E_n ≤ 2.75 MeV',
                 'LiLiT family: measured scale at 1.925 MeV; p+Be ENDF extrapolation; d+Be Serber model (5 MeV ESTIMATE)')
    fs.save(fig, OUT / 'saraf_spectra', data=d)
    return t


def post():
    """from out/saraf_reach.csv: the shield estimate (not Geant4) and the summary figure."""
    r, cp = pd.read_csv(OUT / 'saraf_reach.csv'), pd.read_csv(OUT / 'saraf_components.csv')
    b = pd.read_csv(OUT / 'saraf_beam.csv')
    q = r[(r.days == 50) & (r.signal == 'E* ≤ 22 MeV') & (r.hw == 'big plastics')]
    rows = []
    for key, scen, d in (('lilit_4000_pb0', 'phaseI', 1.0), ('lilit_4000_pb0', 'phaseI', 0.5), ('lilit_4000_pb0', 'phaseII', 1.0),
                         ('lilit_1925_pb0', 'as_ran', 0.5), ('pbe_4_0', 'phaseII', 1.0)):
        c = cp[(cp.key == key) & (cp.scen == scen) & (cp.dist_m == d) & (cp.hw == 'big plastics')].iloc[0]
        fam = c.family
        bb = b[(b.family == fam) & (b.e0 == c.e0)].iloc[0]
        n_sr = bb.per_mA_0deg_sr * c.i_mA
        n_arm = n_sr / (d * 100) ** 2 * 75 ** 2
        tvl = 5.0 if c.e0 < 2 else 10.0                               # borated PE, keV / ~MeV (stand-in)
        for eps in (1e-5, 1e-4):
            T = 0.1 * c.ok_singles_per_arm / (n_arm * eps)
            rows.append(dict(key=key, scen=scen, dist_m=d, i_mA=c.i_mA, tvl_cm=tvl, n_arm_unshielded=n_arm, ok_arm=c.ok_singles_per_arm, eps=eps,
                             T_needed=T, bpe_cm=max(0.0, -tvl * np.log10(T))))
    s = pd.DataFrame(rows)
    s.to_csv(OUT / 'saraf_shield.csv', index=False, float_format='%.4g')
    print(s.to_string(index=False))
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use()
    fig, ax = plt.subplots(figsize=(9.5, 4.6))
    z = q[(q.family == 'lilit') & (q.pb_cm == 0) & (q.dist_m == 1.0)]
    for scen, col, lab in (('phaseI', fs.TRACK, 'thick Li, ≤ 4 kW (Phase I class), 1 m'), ('phaseII', fs.ACCENT, 'thick Li, 5 mA (not demonstrated), 1 m')):
        y = z[z.scen == scen].sort_values('e0')
        ax.plot(y.e0, y.rho3, '-o', color=col, label=lab)
    y = q[(q.key.str.startswith('pbe')) & (q.theta == 0) & (q.scen == 'phaseII') & (q.dist_m == 1.0)].sort_values('e0')
    ax.plot(y.e0, y.rho3, '-s', color='C4', label='p + Be, 0°, 5 mA, 1 m (ENDF; < 8 MeV ESTIMATE)')
    y = q[(q.key.str.startswith('pbe')) & (q.theta == 130) & (q.scen == 'phaseII') & (q.dist_m == 1.0)].sort_values('e0')
    ax.plot(y.e0, y.rho3, '--s', color='C4', alpha=.6, label='p + Be, 130°, 5 mA, 1 m')
    y = q[(q.key.str.startswith('dbe')) & (q.theta == 0) & (q.scen == 'phaseII') & (q.dist_m == 1.0)].sort_values('e0')
    ax.plot(y.e0, y.rho3, '-^', color='k', label='d + Be, 0°, 5 mA, 1 m (Serber; 5 MeV ESTIMATE)')
    ax.axhline(1.5e-3, color=fs.COPPER, ls='--', lw=1.2)
    ax.text(30, 1.65e-3, 'ATOMKI ⁴He 1.5×10⁻³', color=fs.COPPER, fontsize=8, ha='right')
    ax.axhline(3.3e-4, color='0.5', ls=':', lw=1)
    ax.text(30, 3.6e-4, 'Birmingham 3.3×10⁻⁴ (engine)', color='0.4', fontsize=8, ha='right')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(1.8, 45)
    ax.set_xlabel('beam energy [MeV]')
    ax.set_ylabel('X17/IPC at 3σ in 50 days')
    ax.legend(frameon=False, fontsize=8)
    fs.fig_title(fig, 'SARAF options, E* ≤ 22 MeV, big plastics: low energy wins, the 40 MeV beam does not',
                 'engine: beam only, Ø8 cm, no room; the throttle hides the extra current of hard spectra')
    fs.save(fig, OUT / 'saraf_reach_fig', data=q[q.dist_m == 1.0][['key', 'family', 'e0', 'theta', 'pb_cm', 'scen', 'dist_m', 'rho3', 'throttle', 'live']])
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--beam-only', action='store_true')
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--post', action='store_true')
    ap.add_argument('--only', nargs='+')
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    pd.set_option('display.width', 250)
    if a.post:
        post()
        return
    if a.check:
        check()
        return
    t = beam_tables()
    print(t.to_string(index=False))
    if a.beam_only:
        return
    r, cp = reach(only=a.only)
    q = r[(r.days == 50) & (r.signal == 'E* ≤ 22 MeV') & (r.hw == 'big plastics')]
    print(q.sort_values('rho3').head(25)[['key', 'scen', 'dist_m', 'i_mA', 'rho3', 'throttle', 'days_to_atomki', 'live', 'occ']].to_string(index=False))


if __name__ == '__main__':
    main()
