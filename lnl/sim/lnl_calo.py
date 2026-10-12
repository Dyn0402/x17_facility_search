#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lnl_calo.py -- does the LNL reach survive a realistic calorimeter?
(FEASIBILITY_SIM.md §14, 2026-10-12)

    LNL_SEL=lnl/sim/sel_v3 python lnl/sim/lnl_calo.py      # -> lnl/out/calo/

Until now every LNL energy was a Geant4 deposit: no light yield, no
non-uniformity, no threshold, no gain error.  The headline (m_ee fit, §13) uses
the arm energies three times: the E_sum window (13-17/18 MeV, removes γ1 and
cosmics), |y| = |E1 - E2|/(E1 + E2), and m_ee = W √((1 - y²)(1 - cos θ)/2).

This applies a per-layer response to the per-arm deposits (sel_v3 tables keep
E_sipm, E_plast, E_ls per arm), anchored on what n_TOF measured
(nTof_x17/ntof_calorimetry, C1 and C4, 2026-10-08):

  plastic 2 cm bars   MIP (3.41 MeV) Landau ⊗ Gauss, Gauss σ/MPV 0.13-0.24 per
                      bar (mean ~0.19) on cosmics over the whole face.  The
                      scint-stack per-cell medians (gain_map, plas_full,
                      all_late) spread 4-5 % rms on A, C, D and 9.5 % on B: the
                      face term c = 5 % (2 % after an MM-position map), the rest
                      photostatistics, a = 0.32 √MeV.  Per-bar
                      scale known to 4-7 % (MIP fit), and the source line was off
                      by 3-24 %: the n_TOF calibration is good to ~10 %.
                      Linear in path to 1.45 MIP.  Threshold ~0.3 MeV (ZS).
  SiPM wall 3 mm      MIP ~0.6 MeV; run-to-run 2-2.5 %; groups up to 35 % low
                      before correction.  a = 0.19 √MeV (25 % at the MIP).
  liquid (as built)   MIP σ/MPV 0.46; 6-9 mV/MeV against the 16-18 mV ZS, i.e.
                      a 1.8-2.8 MeV threshold; MIP efficiency 14-56 % and only
                      near the PMT (A, D) or falling away from it (C).  The
                      n_TOF model: threshold 2.3 MeV, a = 0.78 √MeV, and a
                      per-hit light-collection factor, log-normal σ = 0.5.
  big plastics 5 cm   no data.  Scaled from the 2 cm bar (one PMT, ~10 pe/MeV
                      if a = 0.32 is all photostatistics): 4 PMTs on a 75 × 75
                      plate give a = 0.20-0.35 √MeV; the face term with an MM
                      position map from cosmics 5 %, without 10-15 %.

The response scenarios (RESP) and the per-arm gain prior σ_g that goes into
the fit (lnl_syst.PRIOR_G) are:

  ideal               Geant4 deposits (the §13 numbers), σ_g 0
  n_TOF as is         the response above, uncorrected face terms, σ_g 10 %
  LNL calibrated      MM-position face maps, the liquid repaired (threshold
                      0.5 MeV, a = 0.5, c = 15 %), σ_g 2 % from the single-arm
                      cosmic MIPs (the single-arm trigger, §14.1)
  LNL calibrated, LS off   as above without the liquid (as built only)
  big plates, poor    a = 0.35, c = 15 %, σ_g 5 % (big plastics only)

Outputs (lnl/out/calo/):
  resolution.csv   per scenario: E_sum of γ0 and γ1 pairs, |y| and m_ee of the
                   X17 (position, width), the |y| residual
  days.csv         robust days (m_ee fit and the θ fit at |y| < 0.3, 2 %
                   structure + in-run controls) per scenario and σ_g
  figures/         calo_esum, calo_mass, calo_gain
"""
from __future__ import annotations

import sys
import zlib
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
LNL = HERE.parent
OUT = LNL / 'out' / 'calo'
FIG = OUT / 'figures'
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(LNL.parent / 'ill'))
import lnl_geant as G      # noqa: E402
import lnl_syst as S       # noqa: E402

# --------------------------------------------------------------------------- #
# response scenarios: per layer (a [√MeV], c, threshold [MeV]); the liquid may
# carry a log-normal light-collection factor 'logn'; sigma_g is the fit prior
# --------------------------------------------------------------------------- #
SIPM = dict(a=0.19, c=0.08, thr=0.10)
SIPM_CAL = dict(a=0.19, c=0.04, thr=0.10)
PL2 = dict(a=0.32, c=0.05, thr=0.30)
PL2_CAL = dict(a=0.32, c=0.02, thr=0.30)
LS_NTOF = dict(a=0.78, c=0.0, thr=2.3, logn=0.5)
LS_FIX = dict(a=0.50, c=0.15, thr=0.5)
BIG = dict(a=0.25, c=0.10, thr=0.30)
BIG_CAL = dict(a=0.20, c=0.05, thr=0.30)
BIG_POOR = dict(a=0.35, c=0.15, thr=0.30)

RESP = {
    'ideal': None,
    'n_TOF as is': dict(sipm=SIPM, plast=PL2, ls=LS_NTOF, big=BIG, sigma_g=0.10),
    'LNL calibrated': dict(sipm=SIPM_CAL, plast=PL2_CAL, ls=LS_FIX, big=BIG_CAL, sigma_g=0.02),
    'LNL calibrated, LS off': dict(sipm=SIPM_CAL, plast=PL2_CAL, ls=None, big=BIG_CAL, sigma_g=0.02),
    'big plates, poor': dict(sipm=SIPM_CAL, plast=PL2_CAL, ls=LS_FIX, big=BIG_POOR, sigma_g=0.05),
}
#: which scenarios make sense for which hardware
HW_RESP = {'as built': ('ideal', 'n_TOF as is', 'LNL calibrated', 'LNL calibrated, LS off'),
           'big plastics': ('ideal', 'n_TOF as is', 'LNL calibrated', 'big plates, poor')}

_STATE = {'resp': 'ideal', 'approx': set()}


def _layer(e, p, rng):
    """measured energy of one layer: E (1 + c N) + a √E N', zero below threshold."""
    if p is None:
        return np.zeros_like(e)
    e = np.asarray(e, float)
    m = e * (1 + p['c'] * rng.standard_normal(e.shape))
    if p.get('logn'):
        s = p['logn']
        m = m * np.exp(s * rng.standard_normal(e.shape) - 0.5 * s * s)
    m = m + p['a'] * np.sqrt(np.clip(e, 0, None)) * rng.standard_normal(e.shape)
    m = np.clip(m, 0, None)
    return np.where(m > p['thr'], m, 0.0)


def arm_layers(z):
    """per-arm (n, 2) deposits (sipm, plastic, liquid).  Tables merged before
    sel_v3 only keep the two-arm sums: split them in the ratio of the arm totals
    (flagged; the liquid split is then wrong for the hard leg)."""
    if 'E_plast_a' in z:
        return z['E_sipm_a'].astype(float), z['E_plast_a'].astype(float), z['E_ls_a'].astype(float)
    _STATE['approx'].add(z.get('name', '?'))
    E = np.stack([z['E1'], z['E2']], 1).astype(float)
    f = E / np.maximum(E.sum(1, keepdims=True), 1e-9)
    return f * z['E_sipm2'][:, None], f * z['E_plast2'][:, None], f * z['E_ls2'][:, None]


def respond(z, hw, name, seed=0):
    """copy of z with E1, E2, Esum replaced by the measured arm energies."""
    r = RESP[name]
    if r is None or z is None or len(z['E1']) == 0:
        return z
    rng = np.random.default_rng(seed)
    es, ep, el = arm_layers(z)
    big = hw == 'big plastics'
    m = _layer(es, r['sipm'], rng) + _layer(ep, r['big'] if big else r['plast'], rng)
    if not big:
        m = m + _layer(el, r['ls'], rng)
    zz = dict(z)
    zz['E1_ideal'], zz['E2_ideal'], zz['Esum_ideal'] = z['E1'], z['E2'], z['Esum']
    zz['E1'], zz['E2'] = m[:, 0], m[:, 1]
    zz['Esum'] = m.sum(1)
    zz['name'] = z['name'] + f'|{name}'
    return zz


_orig_load = G._load


def _load_resp(run, sample, hw):
    z = _orig_load(run, sample, hw)
    name = _STATE['resp']
    if z is None or name == 'ideal':
        return z
    seed = zlib.crc32(f'{run}|{sample}|{hw}|{name}'.encode())
    return respond(z, hw, name, seed)


G._load = _load_resp


def set_response(name, sigma_g='auto'):
    """switch the response; clears the caches.  sigma_g: the fit's per-arm gain
    prior ('auto': the scenario's own; None: no gain nuisance)."""
    _STATE['resp'] = name
    G._CACHE.clear()
    S._T.clear()
    r = RESP[name]
    S.PRIOR_G = (None if r is None else r['sigma_g']) if sigma_g == 'auto' else sigma_g


# --------------------------------------------------------------------------- #
# resolution numbers
# --------------------------------------------------------------------------- #
def q(x, p):
    return float(np.quantile(x, p)) if len(x) else np.nan


def resolution(hw, name):
    ec = S.HWS[hw][0]
    rows = {}
    zx = G.load('L1', 'X17_m16.7', hw)
    m = G.select(zx, S.LEVEL, (-1e9, 1e9))
    w = m & (zx['reco_c'] > 125) & (zx['reco_c'] < 165)
    es = zx['Esum'][w]
    rows.update(x17_Esum_med=q(es, .5), x17_Esum_w68=0.5 * (q(es, .84) - q(es, .16)),
                x17_in_window=float(((es > ec[0]) & (es < ec[1])).mean()))
    y = S.asym(zx)
    win = w & (zx['Esum'] > ec[0]) & (zx['Esum'] < ec[1])
    if 'E1_ideal' in zx:
        y0 = np.abs(zx['E1_ideal'] - zx['E2_ideal']) / np.maximum(zx['E1_ideal'] + zx['E2_ideal'], 1e-9)
        rows['y_resid_w68'] = 0.5 * (q((y - y0)[win], .84) - q((y - y0)[win], .16))
    yt = np.abs(zx['em_ke'] - zx['ep_ke']) / (zx['em_ke'] + zx['ep_ke'])
    rows['x17_ycut03'] = float((y[win] < 0.3).mean())
    rows['corr_y_ytrue'] = float(np.corrcoef(y[win], yt[win])[0, 1])
    S.use_var('mass')
    mm = S.var_of(zx)[win]
    S.use_var('theta')
    rows.update(x17_mass_med=q(mm, .5), x17_mass_w68=0.5 * (q(mm, .84) - q(mm, .16)))
    for smp, lab in (('M1_18.15', 'g0'), ('M1_15.1', 'g1')):
        z, _, _ = S.load_ipc(smp, hw)
        mk = G.select(z, S.LEVEL, (-1e9, 1e9)) & (z['reco_c'] > 125) & (z['reco_c'] < 165)
        e = z['Esum'][mk]
        rows[f'{lab}_Esum_med'] = q(e, .5)
        rows[f'{lab}_Esum_w68'] = 0.5 * (q(e, .84) - q(e, .16))
        rows[f'{lab}_in_window'] = float(((e > ec[0]) & (e < ec[1])).mean())
    rows['g1_g0_sep'] = (rows['g0_Esum_med'] - rows['g1_Esum_med']) / np.hypot(rows['g0_Esum_w68'],
                                                                               rows['g1_Esum_w68'])
    return rows


def spectra(hw):
    """E_sum (γ0, γ1, X17) and m_ee (X17, γ0 IPC) for the figures."""
    eb = np.arange(0, 30.01, 0.5)
    mb = np.arange(8, 20.01, 0.25)
    out = []
    for name in HW_RESP[hw]:
        set_response(name)
        for smp, lab in (('X17_m16.7', 'X17'), ('M1_18.15', 'γ0 IPC (M1)'), ('M1_15.1', 'γ1 IPC (M1)')):
            z = G.load('L1', smp, hw) if lab == 'X17' else S.load_ipc(smp, hw)[0]
            mk = G.select(z, S.LEVEL, (-1e9, 1e9)) & (z['reco_c'] > 125) & (z['reco_c'] < 165)
            h, _ = np.histogram(z['Esum'][mk], eb)
            for x, v in zip(0.5 * (eb[1:] + eb[:-1]), h / max(h.sum(), 1)):
                out.append(dict(hw=hw, resp=name, sample=lab, var='Esum', x=x, frac=v))
            ec = BEST.get((hw, name), HWS0[hw][0])
            mw = mk & (z['Esum'] > ec[0]) & (z['Esum'] < ec[1])
            S.use_var('mass')
            mm = S.var_of(z)[mw]
            S.use_var('theta')
            h, _ = np.histogram(mm, mb)
            for x, v in zip(0.5 * (mb[1:] + mb[:-1]), h / max(h.sum(), 1)):
                out.append(dict(hw=hw, resp=name, sample=lab, var='m_ee', x=x, frac=v))
    return out


# --------------------------------------------------------------------------- #
# robust days: lnl_syst's "2 % shared + in-run controls" rung, with the gain
# nuisance, for the m_ee fit and the θ fit at |y| < 0.3
# --------------------------------------------------------------------------- #
def robust_days(hw, var, ycat):
    S.use_var(var)
    sig, inrun, _ = S.sets(hw, ycat)
    det = dict(npoly=3, prior_a='free')
    F, P, _ = S.fisher([sig] + inrun, gp_shared=(0.02, S.ELL), gp_ind=(0.01, S.ELL), **det)
    d_rob = S.days_to(F, P)
    F0, P0, _ = S.fisher([sig], npoly=0, k_e=False, aniso=False)
    d_stat = S.days_to(F0, P0)
    S.use_var('theta')
    return d_stat, d_rob


ECUT_LO = (7, 8, 9, 10, 11, 12, 13, 14)
ECUT_HI = (14, 15, 16, 17, 18, 19, 20, 22)
HWS0 = dict(S.HWS)


def best_window(hw):
    """E_sum window minimising the robust m_ee days for the current response
    (the §13 windows were tuned on ideal deposits).  Sets S.HWS[hw]."""
    live = HWS0[hw][1]
    best = (np.inf, HWS0[hw][0])
    pg, S.PRIOR_G = S.PRIOR_G, None          # the window hardly depends on the gain prior; faster
    rows = []
    for lo in ECUT_LO:
        for hi in ECUT_HI:
            if hi < lo + 3:
                continue
            S.HWS[hw] = ((lo, hi), live)
            d = robust_days(hw, 'mass', 'all')[1]
            rows.append(dict(lo=lo, hi=hi, days=d))
            if d < best[0]:
                best = (d, (lo, hi))
    S.HWS[hw] = (best[1], live)
    S.PRIOR_G = pg
    S._T.clear()
    BEST[(hw, _STATE['resp'])] = best[1]
    return best[1], rows


BEST: dict = {}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    print(f'tables: {G.SEL}')
    res, days, wins = [], [], []
    for hw in ('as built', 'big plastics'):
        for name in HW_RESP[hw]:
            set_response(name)
            ec, scan = best_window(hw)
            wins.extend(dict(hw=hw, resp=name, **w) for w in scan)
            r = resolution(hw, name)
            res.append(dict(hw=hw, resp=name, sigma_g=S.PRIOR_G or 0.0, ecut=f'{ec[0]}-{ec[1]}', **r))
            for var, ycat, lab in (('mass', 'all', 'm_ee fit'), ('theta', 'y<0.3', 'θ fit, |y|<0.3')):
                ds, dr = robust_days(hw, var, ycat)
                days.append(dict(hw=hw, resp=name, fit=lab, sigma_g=S.PRIOR_G or 0.0,
                                 ecut=f'{ec[0]}-{ec[1]}', days_stat=ds, days_robust=dr))
                print(f'{hw:13s} {name:24s} {lab:16s} σ_g {S.PRIOR_G or 0:.2f}: stat {ds:6.2f} d,'
                      f' robust {dr:6.2f} d')
        # the gain prior alone, on the calibrated response
        set_response('LNL calibrated')
        best_window(hw)
        for sg in (0.0, 0.01, 0.02, 0.05, 0.10, 0.20):
            set_response('LNL calibrated', sigma_g=sg if sg > 0 else None)
            for var, ycat, lab in (('mass', 'all', 'm_ee fit'), ('theta', 'y<0.3', 'θ fit, |y|<0.3')):
                ds, dr = robust_days(hw, var, ycat)
                days.append(dict(hw=hw, resp='LNL calibrated (σ_g scan)', fit=lab, sigma_g=sg,
                                 days_stat=ds, days_robust=dr))
                print(f'{hw:13s} σ_g scan {sg:.2f} {lab:16s}: robust {dr:6.2f} d')
        S.HWS[hw] = HWS0[hw]
    pd.DataFrame(wins).to_csv(OUT / 'windows.csv', index=False)
    res = pd.DataFrame(res)
    days = pd.DataFrame(days)
    res.to_csv(OUT / 'resolution.csv', index=False)
    days.to_csv(OUT / 'days.csv', index=False)
    sp = pd.DataFrame(spectra('as built') + spectra('big plastics'))
    sp.to_csv(OUT / 'spectra.csv', index=False)
    set_response('ideal')
    if _STATE['approx']:
        print('APPROXIMATE per-arm layer split (pre-sel_v3 tables):', sorted(_STATE['approx'])[:5], '...')
    with pd.option_context('display.width', 250, 'display.max_columns', 30):
        print(res.round(3).to_string())
    figures(res, days, sp)


def figs_only():
    figures(pd.read_csv(OUT / 'resolution.csv'), pd.read_csv(OUT / 'days.csv'), pd.read_csv(OUT / 'spectra.csv'))


def figures(res, days, sp):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use()
    col = {'ideal': fs.MUTED, 'n_TOF as is': '#D55E00', 'LNL calibrated': '#0072B2',
           'LNL calibrated, LS off': '#009E73', 'big plates, poor': '#CC79A7'}
    for var, xl, fn, xlim in (('Esum', 'E_sum of the two arms [MeV]', 'calo_esum', (0, 26)),
                              ('m_ee', 'pair mass m_ee [MeV]', 'calo_mass', (10, 20))):
        fig, axs = plt.subplots(1, 2, figsize=fs.WIDE, sharey=False)
        for ax, hw in zip(axs, ('as built', 'big plastics')):
            for name in HW_RESP[hw]:
                # E_sum: the γ0 IPC has the X17's E_sum, so show X17 vs γ1; m_ee: X17 vs γ0
                smps = (('X17', '-'), ('γ1 IPC (M1)', ':')) if var == 'Esum' else (('X17', '-'), ('γ0 IPC (M1)', '--'))
                for smp, ls in smps:
                    d = sp[(sp.hw == hw) & (sp.resp == name) & (sp['sample'] == smp) & (sp['var'] == var)]
                    ax.plot(d.x, d.frac, ls=ls, color=col[name], lw=1.3, label=f'{name}: {smp}')
            ax.set_xlim(*xlim)
            ax.set_xlabel(xl)
            ax.set_title(hw, fontsize=9)
        axs[0].set_ylabel('fraction per bin (θ 125–165°)')
        for ax in axs:
            ax.legend(fontsize=6, ncol=1, loc='upper left')
        ttl = ('What a real response does to E_sum' if var == 'Esum'
               else 'What a real response does to the X17 mass peak')
        fs.fig_title(fig, ttl, 'Geant4 deposits with the n_TOF-anchored response (lnl_calo.py)')
        fs.save(fig, FIG / fn, data=sp[sp['var'] == var])
    # gain prior scan
    fig, ax = fs.figure()
    d = days[days.resp == 'LNL calibrated (σ_g scan)']
    for (hw, fit), g in d.groupby(['hw', 'fit']):
        ax.plot(100 * g.sigma_g, g.days_robust, marker='o', lw=1.2,
                color='#0072B2' if hw == 'big plastics' else '#D55E00',
                ls='-' if fit == 'm_ee fit' else '--', label=f'{hw}, {fit}')
    ax.set_yscale('log')
    ax.set_xlabel('per-arm gain prior σ_g [%]')
    ax.set_ylabel('days to 3σ at R_ATOMKI (robust)')
    ax.legend(fontsize=7)
    fs.title(ax, 'How well must each arm be calibrated?',
             'LNL-calibrated response, 2 % structure + in-run controls, gain nuisance per arm')
    fs.save(fig, FIG / 'calo_gain', data=d)


if __name__ == '__main__':
    figs_only() if '--figs' in sys.argv else main()
