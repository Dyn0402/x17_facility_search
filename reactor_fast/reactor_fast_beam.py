#!/usr/bin/env python3
"""
reactor_fast_beam.py -- operating reactor fast and epithermal beams for the X17 search, as alternatives to
the FRM II MEDAPP fission beam (reactor_fast/FACILITY.md, FEASIBILITY.md).

    python reactor_fast/reactor_fast_beam.py              # beam tables + reach -> reactor_fast/out/
    python reactor_fast/reactor_fast_beam.py --beam-only  # the beam model only

The reach uses the shared engine survey/soft_sim/soft_reach.py (Geant4 runs N5/G5/G6 re-weighted).
Engine check: this script reproduces medapp_std and bham_28_2m_pb5 of survey/soft_sim/out/soft_reach.csv
(rho3 to 4 digits, all hardware), written to out/rf_engine_check.csv.

Treatment of neutrons below the N5 edge (1 keV), which is 60-90 % of an epithermal beam:
    N5 starts at 1 keV, so the Geant4 tables say nothing about them.  Three variants:
      'n5only'   drop everything below 1 keV (signal and background)
      'subkev'   HEADLINE: sub-keV neutrons make pairs at the ENDF yield of the cell (captures below), and
                 each counts in the background as a neutron at 1-3 keV (N5's lowest, quietest bin).  ESTIMATE.
      'subkev10' same but ×10 background weight, the sensitivity for capture γ in cell walls and dump.
    Pairs below 1 keV are put in the first analysis bin (E_n < 0.75 MeV), so their θ distribution is that of
    E* = 20.95 MeV, slightly narrower than the true 20.6 MeV.

Fast group of the BNCT beams: published dose per fast neutron (>10 keV) sets the cutoff E_c of a 1/E·exp(−E/E_c)
shape through a tissue-kerma table (ESTIMATE, ±30 %).  γ: fluence = dose / 1.0e-11 Gy cm² (the MEDAPP
conversion, 2.4 MeV), spectrum exp(−E/2.45 MeV) on 0.1-10 MeV (the MEDAPP stand-in).  Both are stand-ins.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
if not hasattr(np, 'trapezoid'):
    np.trapezoid = np.trapz

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / 'out'
sys.path.insert(0, str(ROOT / 'survey' / 'soft_sim'))

AREA = 50.0                    # cm², the Ø8 cm cell spot of the engine
GAMMA_K = 1.0e-11              # Gy cm² per photon (MEDAPP conversion at 2.4 MeV; ESTIMATE)
E_FULL = np.geomspace(1e-9, 20.0, 12000)   # MeV: full range, thermal to fission tail
EPI_LO, EPI_HI = 0.4e-6, 1e-2  # MeV, the BNCT definition of "epithermal" (0.4 eV-10 keV)
KERMA = (np.array([1e-3, 1e-2, 1e-1, 3e-1, 1.0, 2.0, 5.0, 14.0]),       # MeV
         np.array([1.1e-13, 1.0e-12, 6.6e-12, 1.0e-11, 2.5e-11, 3.0e-11, 4.5e-11, 6.5e-11]))
# Tissue kerma per fluence, Gy cm²: approximate ICRU-style values (ESTIMATE, ±30 %).
MU_PB_N = 0.20                 # /cm, uncollided n in Pb (the engine's value; a lower bound on transmission for the
                               # forward-scattered part)
MU_PB_G = (np.array([0.1, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 20.0]),         # MeV
           np.array([60.0, 1.8, 0.77, 0.51, 0.47, 0.49, 0.56, 0.62]))     # /cm (NIST XCOM, rounded; Bi within 10 %)

# TAPIRO (ENEA Casaccia): Rosa et al. IGORR 2009; Osipenko et al. arXiv:1505.06314 (MCNP, checked with diamond).
TAPIRO_S = 3.0e14              # n/s integrated core source at 5 kW (Rosa 2009, calculated)
TAPIRO_R_FACE = 2.15e2         # cm: outer face of the shield (Cu to r = 40 cm + 175 cm borated concrete)
TAPIRO_CELL_STANDOFF = 55.0    # cm: exit face to the middle of the 40 cm cell (ESTIMATE)
TAPIRO_MEAN_INNER = 0.586      # MeV, mean energy in the inner Cu reflector (Osipenko: MCNP)
TAPIRO_MEAN_OUTER = 0.166      # MeV, mean energy at the outer Cu edge (Osipenko: MCNP)
TAPIRO_GT135_CORE = 0.20       # fraction > 1.35 MeV at core centre (Rosa 2009)
TAPIRO_GT135_COL = 4e7 / 1.5e10   # fraction > 1.35 MeV at the thermal column entrance (Rosa 2009)


def watt(e, a=0.988, b=2.249):
    return np.exp(-e / a) * np.sinh(np.sqrt(b * np.maximum(e, 0)))


def _norm(f, e):
    i = np.trapezoid(f, e)
    return f / i if i > 0 else f


def tapiro_shape(a, ec=1.5, e=E_FULL):
    """a × Watt + (1−a) × 1/E·exp(−E/E_c) on [1 keV, 20 MeV]: a fission spectrum softened in the Cu (E_c = 1.5 MeV
    for the inner reflector / direct core view, 0.5 MeV for the outer edge; ESTIMATE)."""
    w = _norm(np.where(e > 1e-3, watt(e), 0.0), e)
    s = _norm(np.where(e > 1e-3, np.exp(-e / ec) / e, 0.0), e)
    return a * w + (1 - a) * s


def _mean(f, e=E_FULL):
    return float(np.trapezoid(e * f, e) / np.trapezoid(f, e))


def _frac(f, lo, hi, e=E_FULL):
    m = (e >= lo) & (e < hi)
    return float(np.trapezoid(f[m], e[m]) / np.trapezoid(f, e))


def tapiro_fit_a(target_mean, ec=1.5):
    x = np.linspace(0, 1, 1001)
    m = np.array([_mean(tapiro_shape(v, ec)) for v in x])
    return float(np.interp(target_mean, m, x))


A_INNER = tapiro_fit_a(TAPIRO_MEAN_INNER)
A_OUTER = tapiro_fit_a(TAPIRO_MEAN_OUTER, ec=0.5)


def bnct_shape(phi_th, phi_epi, phi_fast, ec_mev):
    """absolute dΦ/dE [1/cm²/s/MeV] on E_FULL: Maxwellian thermal + 1/E epithermal + 1/E·exp(−E/E_c) fast."""
    e = E_FULL
    kt = 2.53e-8
    th = np.where(e < EPI_LO, e / kt ** 2 * np.exp(-e / kt), 0.0)
    ep = np.where((e >= EPI_LO) & (e < EPI_HI), 1 / e, 0.0)
    fa = np.where(e >= EPI_HI, np.exp(-e / ec_mev) / e, 0.0)
    return phi_th * _norm(th, e) + phi_epi * _norm(ep, e) + phi_fast * _norm(fa, e)


def kerma_of_fast(ec_mev):
    """mean tissue kerma per neutron [Gy cm²] of the fast group (>10 keV) with cutoff E_c."""
    e = E_FULL[(E_FULL >= EPI_HI)]
    f = np.exp(-e / ec_mev) / e
    k = np.exp(np.interp(np.log(e), np.log(KERMA[0]), np.log(KERMA[1])))
    return float(np.trapezoid(k * f, e) / np.trapezoid(f, e))


def ec_from_dose(dose_per_fast):
    x = np.geomspace(0.02, 20.0, 400)
    k = np.array([kerma_of_fast(v) for v in x])
    return float(np.interp(dose_per_fast, k, x)) if k.min() < dose_per_fast < k.max() else (0.02 if dose_per_fast <= k.min() else 20.0)


def fast_from_dose(d_fast_gy_s, ec=0.3):
    return d_fast_gy_s / kerma_of_fast(ec)


def gamma_shape(e, e0=2.45):
    return _norm(np.where((e > 0.1) & (e < 10.0), np.exp(-e / e0), 0.0), e)


def pb_transmission(t_cm, e):
    mu = np.interp(np.log(np.maximum(e, 1e-3)), np.log(MU_PB_G[0]), MU_PB_G[1])
    return np.exp(-mu * t_cm)


# --------------------------------------------------------------------------- #
def bnct_cases():
    """the operating (or historically measured) epithermal beams; numbers from FACILITY.md.
    phi at the exit; standoff factor: the cell cannot sit at the exit (arms ± the wall), so a fraction
    of the exit flux reaches the Ø8 cm spot; LVR-15 measured ×2.5 down at 20 cm (Physiol. Res. 46, 1997)."""
    STOFF = 0.25                                  # flux kept at ~35 cm from a BNCT exit (ESTIMATE from LVR-15's 2.5× at 20 cm)
    out = {}
    # LVR-15: Burian et al. 2003 (measured free beam, 10 MW), fast dose fit from Physiol. Res. 1997 Table 1
    ec_lvr = ec_from_dose(1.3e-12 / 0.15)        # Table 1: D_f = 1.3e-12 per epi, fast/epi = 0.15 → 8.7e-12 per fast n
    out['lvr15'] = dict(what='LVR-15 BNCT beam, 10 MW, measured free beam (2003)', st='measured',
                        phi_th=0.23 * 7.13e8, phi_epi=7.13e8, phi_fast=6.1e7, ec=ec_lvr, dg=1.98 / 3600, stoff=STOFF)
    # MITR FCB: OSTI 20804769, in air at the patient position; fast dose ⇒ phi_fast
    ec = ec_lvr
    pf = fast_from_dose(3.9e-2 / 60, ec)
    out['mitr'] = dict(what='MITR fission converter beam, measured in air (historical; FC being converted)', st='historical',
                       phi_th=0.02 * 8.4e9, phi_epi=8.4e9, phi_fast=pf, ec=ec, dg=11.8e-2 / 60, stoff=STOFF)
    # THOR: 2004 design study (Nucl. Technol.), values per MW
    pf = fast_from_dose(4.7e-4, ec)
    out['thor_1mw'] = dict(what='THOR 1 MW (design values)', st='design', phi_th=0.02 * 1.7e9, phi_epi=1.7e9, phi_fast=pf, ec=ec,
                           dg=2.1e-4, stoff=STOFF)
    out['thor_2mw'] = dict(what='THOR 2 MW (design ×2, if licensed for the beam)', st='design',
                           phi_th=0.02 * 3.4e9, phi_epi=3.4e9, phi_fast=2 * pf, ec=ec, dg=4.2e-4, stoff=STOFF)
    # TAPIRO epithermal column: Burn/Casalini/Nava 2003, calculated (window + AlF3 + Ni), standard free beam
    d = 8.0e8
    out['tapiro_epi'] = dict(what='TAPIRO epithermal column, 5 kW (calculated, 2003)', st='calculated',
                             phi_th=0.01 * d, phi_epi=d, phi_fast=fast_from_dose(4.1e-13 * d, ec), ec=ec,
                             dg=3.5e-13 * d, stoff=STOFF)
    # RA-6: 1999 design (0.5 MW, 1.1e9); doses per epi neutron from the same table
    d = 1.1e9
    out['ra6'] = dict(what='RA-6 epithermal design (0.5 MW, 1999)', st='design', phi_th=0.03 * d, phi_epi=d,
                      phi_fast=fast_from_dose(7.5e-13 * d, ec), ec=ec, dg=3.0e-13 * d, stoff=STOFF)
    return out


def tapiro_open_cases():
    """TAPIRO opened as a fast beam (a concept, not a facility): a straight channel through the thermal-column
    region (or a removed Cu sector) that views the core.  Flux at the cell = S·f_view /(4π L²)."""
    L = TAPIRO_R_FACE + TAPIRO_CELL_STANDOFF
    base = TAPIRO_S / (4 * np.pi * L ** 2)
    return {
        'tapiro_open_core': dict(what='TAPIRO open channel, direct core view (Cu sector removed; concept)', flux=0.5 * base,
                                 a=None, frac=TAPIRO_GT135_CORE, gk=1.0),
        'tapiro_open_refl': dict(what='TAPIRO open channel, reflector view (mean 0.17 MeV; concept)', flux=1.0 * base,
                                 a=A_OUTER, frac=None, gk=1.0),
    }


def tapiro_core_a():
    """Watt weight that gives the Rosa 2009 >1.35 MeV core-centre fraction."""
    x = np.linspace(0, 1, 1001)
    f = np.array([_frac(tapiro_shape(v), 1.35, 20.0) for v in x])
    return float(np.interp(TAPIRO_GT135_CORE, f, x))


# --------------------------------------------------------------------------- #
class Spec:
    """a spectrum at the cell: dPhi/dE on E_FULL, with a γ fluence (per cm²/s) and its shape."""
    def __init__(self, key, what, flux_e, gflux, st='', pb=0.0):
        self.key, self.what, self.st, self.pb = key, what, st, pb
        self.flux_e = flux_e * np.exp(-MU_PB_N * pb) if pb else flux_e
        g = gamma_shape(E_FULL)
        if pb:
            t = pb_transmission(pb, E_FULL)
            g = g * t
            gflux = gflux * np.trapezoid(g, E_FULL) / np.trapezoid(gamma_shape(E_FULL), E_FULL)
            g = _norm(g, E_FULL)
        self.gflux, self.gs = gflux, g

    def summary(self):
        e = E_FULL
        tot = np.trapezoid(self.flux_e, e)
        return dict(key=self.key, what=self.what, status=self.st, pb_cm=self.pb, flux_total=tot,
                    flux_lt1keV=tot * _frac(self.flux_e, 0, 1e-3), flux_ge1keV=tot * _frac(self.flux_e, 1e-3, 21),
                    frac_window=_frac(self.flux_e, 0.2, 2.75), frac_gt2p75=_frac(self.flux_e, 2.75, 21),
                    mean_En_MeV=_mean(self.flux_e), gflux=self.gflux, g_per_n=self.gflux / max(tot, 1e-300),
                    n_spot=tot * AREA, g_spot=self.gflux * AREA)


def spec_bnct(key, c, stoff=None, pb=0.0):
    f = bnct_shape(c['phi_th'], c['phi_epi'], c['phi_fast'], c['ec'])
    s = (c['stoff'] if stoff is None else stoff)
    return Spec(key, c['what'], f * s, c['dg'] / GAMMA_K * s, c['st'], pb)


def spec_open(key, c, a, gk, pb=0.0, ec=1.5):
    f = tapiro_shape(a, ec) * c['flux']
    return Spec(key, c['what'], f, gk * c['flux'], 'concept (ESTIMATE)', pb)


def spec_watt(key, what, flux, gk, inter=0.05, pb=0.0):
    w = _norm(watt(E_FULL), E_FULL)
    m = (E_FULL > 1e-3) & (E_FULL < 0.5)
    i = _norm(np.where(m, 1 / E_FULL, 0.0), E_FULL)
    return Spec(key, what, ((1 - inter) * w + inter * i) * flux, gk * flux, 'generic', pb)


# --------------------------------------------------------------------------- #
def to_source(SR, sp, variant):
    """the engine Soft source + the captures array for a spectrum, with the sub-keV treatment of the variant."""
    from scipy.interpolate import interp1d
    Y, R, NB = SR.Y, SR.R, SR.NB
    e = E_FULL
    above = e >= 1e-3
    f_above = sp.flux_e * above
    n_above = np.trapezoid(f_above, e)
    n_sub = np.trapezoid(sp.flux_e * (~above), e)
    # captures per entering neutron over the full range
    cpn = Y.captures_per_neutron(e)
    edges = np.array([0.0] + R.EDGES[1:-1] + [99.0])
    cap = np.zeros(NB)
    for k in range(NB):
        mk = (e >= edges[k]) & (e < edges[k + 1])
        cap[k] = AREA * np.trapezoid((sp.flux_e * cpn)[mk], e[mk])
    if variant == 'n5only':
        mk = (e >= edges[0]) & (e < edges[1]) & above
        cap[0] = AREA * np.trapezoid((sp.flux_e * cpn)[mk], e[mk])
        fn_e = f_above
        n_bg = n_above
    else:                                         # sub-keV counted as the 1-3 keV bin in the background
        w_sub = 1.0 if variant == 'subkev' else 10.0
        m13 = (e >= 1e-3) & (e < 3e-3)
        bump = np.where(m13, 1.0 / e, 0.0)
        bump = _norm(bump, e)
        fn_e = f_above + w_sub * n_sub * bump
        n_bg = np.trapezoid(fn_e, e)
    fn = interp1d(e, _norm(fn_e, e), bounds_error=False, fill_value=0.0)(SR.E_GRID)
    fn = _norm(fn, SR.E_GRID)
    fg = interp1d(e, sp.gs, bounds_error=False, fill_value=0.0)(SR.E_GRID)
    fg = _norm(fg, SR.E_GRID)
    src = SR.Soft(sp.key, sp.what, fn, n_bg * AREA, fg, sp.gflux * AREA, 'reactor_fast')
    return src, cap


def throttled(SR, src, C, M, cap, days, soft):
    grid = np.geomspace(1e-4, 1.0, 41)
    out = []
    for s in grid:
        st = SR.at_throttle(src, C, M, cap, s)
        out.append((SR.rho3(M, st, days, soft), s, st))
    return min(out, key=lambda x: x[0])


def wall(r, floor, s, live, occ, acc_frac):
    if s < 0.9:
        return f'DREAM / accidentals (throttle {s:.2f})'
    if r / floor < 1.2:
        return 'statistics floor (IPC + cosmics)'
    return f'accidentals {acc_frac:.0%} of the window background' if acc_frac > 0.2 else 'statistics (IPC + cosmics, DREAM live %.2f)' % live


def score(SR, sp, hw, M, runs, variant, days=(50.0, 14.0), cap_mult=1.0):
    src, cap = to_source(SR, sp, variant)
    cap = cap * cap_mult
    C = SR.components(src, runs, hw, M)
    rows = []
    for d in days:
        for soft in (True, False):
            r, s, st = throttled(SR, src, C, M, cap, d, soft)
            floor_C = dict(C, acc_th=C['acc_th'] * 0, corr_th=C['corr_th'] * 0, ok_arm=C['ok_arm'] * 0,
                           leg_arm=C['leg_arm'] * 0, corr_trig=0.0)
            st0 = SR.at_throttle(src, floor_C, M, cap, 1.0)
            fl = SR.rho3(M, st0, d, soft)
            wc = SR.window_counts(st, M, soft)
            bg = sum(wc[f'{k}_win_per_day'] for k in ('IPC', 'cosmic', 'acc', 'corr'))
            rows.append(dict(key=sp.key, variant=variant, hw=hw, days=d, signal='E* ≤ 22 MeV' if soft else 'all E*', rho3=r,
                             rho3_floor=fl, vs_ATOMKI=r / SR.R.RHO_REF, throttle=s, live=st['live'], occ=st['occ'],
                             days_to_atomki=50 * (r / SR.R.RHO_REF) ** 2 if d == 50 else np.nan,
                             acc_frac_window=wc['acc_win_per_day'] / max(bg, 1e-30),
                             wall=wall(r, fl, s, st['live'], st['occ'], wc['acc_win_per_day'] / max(bg, 1e-30)),
                             legs_per_arm=float(C['leg_arm'].mean()), ok_per_arm=float(C['ok_arm'].mean()),
                             n_bg_spot=src.n_cell, g_spot=src.g_cell, **wc, ok_g_frac=C['ok_g_frac'],
                             cap_per_s_total=float(cap.sum())))
    return rows


def spectra():
    """every spectrum that goes through the engine: name -> Spec."""
    out = {}
    c = bnct_cases()
    for k in ('lvr15', 'mitr', 'thor_1mw', 'thor_2mw', 'tapiro_epi', 'ra6'):
        out[k] = spec_bnct(k, c[k])
    # LVR-15: stand-off scan and Pb in the beam
    for so, tag in ((1.0, 'at_exit'), (0.5, 'd20'), (0.25, 'd35')):
        out[f'lvr15_{tag}'] = spec_bnct(f'lvr15_{tag}', c['lvr15'], stoff=so)
    for pb in (5.0, 10.0):
        out[f'lvr15_pb{pb:.0f}'] = spec_bnct(f'lvr15_pb{pb:.0f}', c['lvr15'], pb=pb)
    # TAPIRO, open channel (concept)
    op = tapiro_open_cases()
    a_core = tapiro_core_a()
    out['tapiro_open'] = spec_open('tapiro_open', op['tapiro_open_core'], a_core, 1.0)
    for gk in (0.3, 3.0):
        out[f'tapiro_open_g{gk:g}'] = spec_open(f'tapiro_open_g{gk:g}', op['tapiro_open_core'], a_core, gk)
    for pb in (5.0, 10.0):
        out[f'tapiro_open_pb{pb:.0f}'] = spec_open(f'tapiro_open_pb{pb:.0f}', op['tapiro_open_core'], a_core, 1.0, pb=pb)
        out[f'tapiro_open_g3_pb{pb:.0f}'] = spec_open(f'tapiro_open_g3_pb{pb:.0f}', op['tapiro_open_core'], a_core, 3.0, pb=pb)
    out['tapiro_open_f015_pb5'] = spec_open('tapiro_open_f015_pb5', dict(op['tapiro_open_core'], flux=0.3 * op['tapiro_open_core']['flux']), a_core, 1.0, pb=5.0)
    out['lvr15_ec0p3'] = spec_bnct('lvr15_ec0p3', dict(c['lvr15'], ec=0.3))
    out['tapiro_refl'] = spec_open('tapiro_refl', op['tapiro_open_refl'], A_OUTER, 1.0, ec=0.5)
    return out


def flux_grid():
    """the engine as a map: reach against fast flux at the cell and γ/n, Watt spectrum (what the MEDAPP-like beam
    needs to be, facility-independent)."""
    out = {}
    for fx in (1e6, 3e6, 1e7, 3e7, 1e8, 3e8, 1e9, 3e9):
        for gk in (0.3, 1.0, 3.0, 10.0):
            k = f'grid_watt_{fx:.0e}_g{gk:g}'
            out[k] = spec_watt(k, f'Watt, {fx:.0e} n/cm²/s, γ/n {gk:g}', fx, gk)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--beam-only', action='store_true')
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    pd.set_option('display.width', 250, 'display.max_columns', 40, 'display.float_format', '{:.3g}'.format)
    S = spectra()
    bt = pd.DataFrame([s.summary() for s in S.values()])
    bt['A_outer'] = A_OUTER
    bt.to_csv(OUT / 'rf_beam.csv', index=False, float_format='%.4g')
    print(bt[['key', 'flux_total', 'flux_lt1keV', 'flux_ge1keV', 'frac_window', 'frac_gt2p75', 'mean_En_MeV', 'gflux', 'g_per_n']].to_string(index=False))
    print('fits: a_inner', A_INNER, 'a_outer', A_OUTER, 'a_core', tapiro_core_a(), 'Ec_LVR', ec_from_dose(1.3e-12 / 0.15))
    if a.beam_only:
        return
    import soft_reach as SR
    SF, R = SR.SF, SR.R
    # engine check
    ref = pd.read_csv(ROOT / 'survey/soft_sim/out/soft_reach.csv')
    srcs = {s.key: s for s in SR.sources()}
    chk = []
    for hw in R.HW:
        M = SF.nfs_model(hw)
        runs = SR.load_runs(hw)
        for k in ('medapp_std', 'bham_28_2m_pb5'):
            s = srcs[k]
            C = SR.components(s, runs, hw, M)
            cap = SR.captures(s)
            r, t, _ = throttled(SR, s, C, M, cap, 50.0, True)
            q = ref[(ref.key == k) & (ref.hw == hw) & (ref.days == 50) & (ref.signal == 'E* ≤ 22 MeV')].iloc[0]
            chk.append(dict(key=k, hw=hw, mine=r, published=q.rho3, ratio=r / q.rho3, throttle=t))
    chk = pd.DataFrame(chk)
    chk.to_csv(OUT / 'rf_engine_check.csv', index=False, float_format='%.5g')
    print(chk.to_string(index=False))
    # the reach
    G = flux_grid()
    rows, grows = [], []
    for hw in R.HW:
        M = SF.nfs_model(hw)
        runs = SR.load_runs(hw)
        for k, sp in S.items():
            for variant in ('subkev', 'n5only', 'subkev10'):
                rows += score(SR, sp, hw, M, runs, variant)
        for k, sp in G.items():
            grows += score(SR, sp, hw, M, runs, 'subkev', days=(50.0,))
    t = pd.DataFrame(rows)
    t.to_csv(OUT / 'rf_reach.csv', index=False, float_format='%.4g')
    g = pd.DataFrame(grows)
    g.to_csv(OUT / 'rf_flux_grid.csv', index=False, float_format='%.4g')
    q = t[(t.days == 50) & (t.hw == 'big plastics') & (t.signal == 'E* ≤ 22 MeV')]
    print(q.pivot_table(index='key', columns='variant', values='rho3', sort=False).to_string())
    print(g[(g.days == 50) & (g.hw == 'big plastics') & (g.signal == 'E* ≤ 22 MeV')].pivot_table(
        index='key', values=['rho3', 'throttle', 'days_to_atomki'], sort=False).to_string())


if __name__ == '__main__':
    main()
