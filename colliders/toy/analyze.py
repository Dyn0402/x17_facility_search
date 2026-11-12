#!/usr/bin/env python3
"""Collider X17 toy: acceptance, mass resolution, backgrounds and reach (2026-11-12).

Reads colliders/out/pairs/*.json|csv from run.py (campaign.sh) and writes
figures + CSVs to colliders/out/ and the results table colliders/out/reach.csv.

Reach: 3 sigma on BR(P -> gamma X17) x BR(X17 -> ee) in a mass window around
the reconstructed peak, statistics only (and with a 0.1 % background-shape
systematic), against pi0 and eta Dalitz pairs and pi0-photon conversions in the
beam pipe / first silicon layer that survive a vertex-compatibility (chi2) cut.
Not included: combinatorial pairs, hadron mis-ID, electron-ID efficiency (BR
reach scales as 1/eps_pair), pile-up.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2 as chi2dist

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'ill'))
import kinematics as kin  # noqa: E402
from detectors import DETECTORS  # noqa: E402
import figstyle as fs  # noqa: E402

PAIRS = HERE.parent / 'out' / 'pairs'
OUT = HERE.parent / 'out'
P_CUT = 1e-3          # per-leg chi2 p-value cut (primary-vertex compatibility) and conversion-veto threshold
SYST = 1e-3           # background-shape systematic for the 'with syst' reach

# Benchmark datasets: minimum-bias events and dN/dy of pi0 at mid-rapidity.  (ask) = not a published number.
DATASETS = {
    'auau200': dict(label='Au+Au 200 GeV MB', n_ev=1e10, dndy_pi0=85.0,
                    note='1e10 MB events (ask: STAR Run 23+25, sPHENIX 2025 streaming); pi0 dN/dy ~ 0.5 dNch/deta, dNch/deta(MB) ~ 170'),
    'pp13600': dict(label='pp 13.6 TeV MB', n_ev=1e12, dndy_pi0=3.2,
                    note='1e12 MB events (ask: ALICE Run 3 continuous readout); dNch/deta ~ 7'),
    'pbpb5360': dict(label='Pb-Pb 5.36 TeV MB', n_ev=1.2e10, dndy_pi0=200.0,
                     note='1.2e10 MB events (ask: ALICE 2023-24); dNch/deta(MB) ~ 450; pp acceptance used'),
    'alice3': dict(label='pp 14 TeV, Runs 5-6', n_ev=1e14, dndy_pi0=3.2, note='(ask) order of magnitude'),
}
# BR(pi0 -> gamma X17) ceiling from NA48/2 (eps < 8e-4 at 90 % CL, as used by Feng et al. 2016)
BR_PI0_NA48 = 2 * (8e-4) ** 2 * (1 - (kin.M_X17 / kin.MPI0) ** 2) ** 3 * kin.BR_GG['pi0']
BR_ETA_ILLUS = 1e-5

DET_ORDER = ['star', 'star_lowB', 'sphenix_tpc', 'sphenix_si', 'sphenix_tpc_q', 'sphenix_si_q',
             'alice_tpc_0p5T', 'alice_tpc_0p2T', 'alice_its_0p5T', 'alice_its_0p2T', 'alice3_2T', 'alice3_0p5T']
SYSTEM = {k: ('auau200' if k.startswith(('star', 'sphenix')) else 'pp13600') for k in DET_ORDER}
COL = {'star': '#0072B2', 'star_lowB': '#56B4E9', 'sphenix_tpc': '#D55E00', 'sphenix_si': '#E69F00',
       'sphenix_tpc_q': '#D55E00', 'sphenix_si_q': '#E69F00', 'alice_tpc_0p5T': '#009E73',
       'alice_tpc_0p2T': '#66c2a5', 'alice_its_0p5T': '#CC79A7', 'alice_its_0p2T': '#8a3f8f',
       'alice3_2T': '#444444', 'alice3_0p5T': '#999999'}
LS = {k: ('--' if k.endswith('_q') or k.endswith('lowB') or k.endswith('0p5T') and k.startswith('alice3') else '-')
      for k in DET_ORDER}


def load(det, source):
    tag = f'{det}__{source.replace(":", "")}__{SYSTEM[det]}'
    js = PAIRS / f'{tag}.json'
    if not js.exists():
        return None, None
    s = json.loads(js.read_text())
    try:
        d = pd.read_csv(PAIRS / f'{tag}.csv')
    except pd.errors.EmptyDataError:
        d = pd.DataFrame()
    if len(d):
        d['m'] = d.mreco * 1e3
        pa = chi2dist.sf(d.chi2_ep, np.maximum(d.ndf_ep, 1))
        pb = chi2dist.sf(d.chi2_em, np.maximum(d.ndf_em, 1))
        d['pass'] = (pa > P_CUT) & (pb > P_CUT)
        if 'chi2_conv' in d:
            # pair-level conversion veto: compatible with a zero-opening pair from the pipe / first layer
            d['conv_like'] = chi2dist.sf(d.chi2_conv, np.maximum(d.ndf_conv, 1)) > P_CUT
            d['pass'] &= ~d['conv_like']
    return s, d


def per_dy(s):
    return s['n_thrown'] / (2 * kin.Y_GEN)


def wmedian(x, w):
    o = np.argsort(x)
    c = np.cumsum(w[o])
    return float(x[o][np.searchsorted(c, 0.5 * c[-1])])


def robust_sigma(x):
    x = np.asarray(x)
    return float(1.4826 * np.median(np.abs(x - np.median(x)))) if len(x) else np.nan


def analyse_det(det):
    sysk = SYSTEM[det]
    ds = DATASETS['alice3' if det.startswith('alice3') else sysk]
    eta_pi0 = kin.eta_over_pi0(sysk)
    res = dict(det=det, label=DETECTORS[det].label, system=ds['label'], n_ev=ds['n_ev'],
               dndy_pi0=ds['dndy_pi0'], eta_over_pi0=eta_pi0)
    bg = {}
    for src in ('dal_pi0', 'dal_eta', 'conv'):
        s, d = load(det, src)
        bg[src] = (s, d)
    for sig in ('x17_pi0', 'x17_eta'):
        s, d = load(det, sig)
        if s is None or not len(d):
            continue
        A = s['w_accepted'] / per_dy(s)
        dp = d[d['pass']]
        eps_chi2 = dp.w.sum() / d.w.sum()
        c = wmedian(dp.m.values, dp.w.values)
        sig_r = robust_sigma(dp.m.values)
        best = None
        for hw in np.arange(0.2, 6.01, 0.1):
            f = dp.w[(dp.m - c).abs() < hw].sum() / d.w.sum()
            B = 0.0
            bparts = {}
            for src, (sb, db) in bg.items():
                if sb is None or not len(db):
                    bparts[src] = 0.0
                    continue
                dbp = db[db['pass']]
                b = dbp.w[(dbp.m - c).abs() < hw].sum() / per_dy(sb)
                mult = ds['dndy_pi0'] * (eta_pi0 if src == 'dal_eta' else 1.0)
                bparts[src] = b * mult * ds['n_ev']
                B += bparts[src]
            npar = ds['n_ev'] * ds['dndy_pi0'] * (eta_pi0 if sig == 'x17_eta' else 1.0)
            if f <= 0 or B <= 0:
                continue
            br3 = 3 * np.sqrt(B) / (npar * A * f)
            br3s = 3 * np.sqrt(B + (SYST * B) ** 2) / (npar * A * f)
            br3s4 = 3 * np.sqrt(B + (1e-4 * B) ** 2) / (npar * A * f)
            if best is None or br3 < best['br3']:
                best = dict(hw=hw, f=f, B=B, br3=br3, br3s=br3s, br3s4=br3s4, parts=bparts, npar=npar)
        k = sig.split('_')[1]
        res.update({f'A_dy_{k}': A, f'eps_chi2_{k}': eps_chi2, f'mpeak_{k}': c, f'sigM_{k}': sig_r})
        if best:
            res.update({f'win_{k}': best['hw'], f'f_win_{k}': best['f'], f'B_{k}': best['B'],
                        f'BR3_{k}': best['br3'], f'BR3syst_{k}': best['br3s'], f'BR3syst4_{k}': best['br3s4'],
                        f'SoverB_at_BR3_{k}': best['br3'] * best['npar'] * A * best['f'] / best['B'],
                        f'Bfrac_dal_pi0_{k}': best['parts']['dal_pi0'] / best['B'],
                        f'Bfrac_dal_eta_{k}': best['parts']['dal_eta'] / best['B'],
                        f'Bfrac_conv_{k}': best['parts']['conv'] / best['B'],
                        f'N_sig_per_BR_{k}': best['npar'] * A * best['f']})
    # conversion rejection by the chi2 cut, and where the surviving / all conversions sit
    sc, dc = bg['conv']
    if sc is not None and len(dc):
        res['conv_acc_per_pi0_dy'] = sc['w_accepted'] / per_dy(sc)
        res['conv_chi2_eff'] = dc.w[dc['pass']].sum() / dc.w.sum()
        res['conv_mass_median_all'] = wmedian(dc.m.values, dc.w.values)
    return res


def fig_scan():
    ps = [0.0, 0.025, 0.05, 0.1, 0.2, 0.4, 0.8, 1.6]
    rows = []
    for det in DET_ORDER:
        for p in ps:
            s, d = load(det, f'scan:{p}')
            if s is None:
                continue
            acc = s['n_accepted'] / s['n_thrown']
            dp = d[d['pass']] if len(d) else d
            rows.append(dict(det=det, label=DETECTORS[det].label, p_X=p, pair_acceptance=acc,
                             sigma_M_MeV=robust_sigma(dp.m) if len(dp) >= 20 else np.nan,
                             peak_MeV=float(np.median(dp.m)) if len(dp) >= 20 else np.nan,
                             n_fit=len(dp)))
    df = pd.DataFrame(rows)
    fig, axs = fs.figure(figsize=(9.6, 4.0), ncols=2)
    for det in DET_ORDER:
        g = df[df.det == det]
        if not len(g):
            continue
        x = np.where(g.p_X == 0, 0.012, g.p_X)
        axs[0].plot(x, g.pair_acceptance, ls=LS[det], color=COL[det], marker='o', label=DETECTORS[det].label)
        axs[1].plot(x, g.sigma_M_MeV, ls=LS[det], color=COL[det], marker='o')
    for ax in axs:
        ax.set_xscale('log')
        ax.set_xlabel('X17 momentum  [GeV]   (leftmost point: at rest)')
    axs[0].set_ylabel('both leptons tracked  (|η_X| < 0.5)')
    axs[1].set_ylabel('σ(m_ee), robust  [MeV]')
    axs[1].set_ylim(0, 3.2)
    h, l = axs[0].get_legend_handles_labels()
    axs[1].legend(h, l, fontsize=6.8, loc='upper left', ncol=2, columnspacing=0.8)
    fs.title(axs[0], 'Pair acceptance vs X17 momentum', 'outbound arc only; per-detector hit requirements')
    fs.title(axs[1], 'Mass resolution vs X17 momentum', 'broken-line fit, MS + brems, χ² cut')
    fs.save(fig, OUT / 'fig_scan_acceptance_resolution', data=df)
    return df


def fig_ms():
    """Analytic: sigma_M from scattering in material t before the first measurement, for symmetric boosted pairs."""
    t = np.logspace(-3.5, -1.3, 200)
    sig = np.sqrt(2) * 13.6 * np.sqrt(t) * (1 + 0.038 * np.log(t))
    pts = []
    for det in DET_ORDER:
        D = DETECTORS[det]
        first = min(i for i, L in enumerate(D.layers) if L.meas)
        tb = sum(L.t for L in D.layers[:first])
        if tb <= 0:
            continue  # ALICE 3: first layer in the beam vacuum
        pts.append(dict(det=det, label=D.label, t_before_first_hit=tb,
                        sigM_analytic=np.sqrt(2) * 13.6 * np.sqrt(tb) * (1 + 0.038 * np.log(tb))))
    pdf = pd.DataFrame(pts)
    fig, ax = fs.figure(figsize=(6.8, 4.2))
    ax.plot(t * 100, sig, color=fs.INK)
    LAB = {'star': ('STAR: pipe + IFC + gas before row 1', (8, -12)),
           'sphenix_tpc': ('sPHENIX design (Be 0.76 mm)', (8, -14)),
           'sphenix_tpc_q': ('sPHENIX as quoted (pipe 1.8 %)', (8, -12)),
           'alice_tpc_0p5T': ('ALICE Run 3', (-10, 10))}
    for r in pts:
        if r['det'] not in LAB:
            continue
        lab, off = LAB[r['det']]
        ax.plot(r['t_before_first_hit'] * 100, r['sigM_analytic'], 'o', color=COL[r['det']])
        ax.annotate(lab, (r['t_before_first_hit'] * 100, r['sigM_analytic']), textcoords='offset points',
                    xytext=off, fontsize=8, color=COL[r['det']], ha='right' if off[0] < 0 else 'left')
    ax.axhline(16.8 * 0.05, color=fs.MUTED, lw=0.8, ls=':')
    ax.text(0.04, 16.8 * 0.05 * 1.05, '5 % of m_X', color=fs.MUTED, fontsize=8)
    ax.set_xscale('log')
    ax.set_xlabel('material before the first measurement, x/X₀  [%]')
    ax.set_ylabel('σ(m_ee) from scattering  [MeV]')
    fs.title(ax, 'Scattering smears a boosted pair mass by ≈ 19 MeV·√(x/X₀)',
             'symmetric pair, θ_open ≈ 2m/E: independent of the X17 momentum and mass (no vertex constraint)')
    fs.save(fig, OUT / 'fig_ms_mass_floor', data={'curve': pd.DataFrame(dict(t=t, sigM=sig)), 'detectors': pdf})
    return pdf


def fig_lepton_pt():
    rng = np.random.default_rng(5)
    rows = {}
    fig, ax = fs.figure(figsize=(6.8, 4.0))
    bins = np.logspace(np.log10(0.003), np.log10(3), 61)
    for src, col, sysk in (('x17_pi0', '#0072B2', 'auau200'), ('x17_eta', '#D55E00', 'auau200')):
        g = kin.gen_pairs(rng, 400000, src, sysk)
        V = g['ep'] + g['em']
        yV = 0.5 * np.log((V[:, 0] + V[:, 3]) / (V[:, 0] - V[:, 3]))
        m = np.abs(yV) < 1
        ptmin = np.minimum(np.hypot(g['ep'][m, 1], g['ep'][m, 2]), np.hypot(g['em'][m, 1], g['em'][m, 2]))
        h, _ = np.histogram(ptmin, bins)
        h = h / h.sum()
        ax.stairs(h, bins * 1e3, color=col, label=f'X17 from {"π⁰" if "pi0" in src else "η"} (softer lepton)')
        rows[src] = h
    for thr, c in ((59, COL['star']), (104, COL['sphenix_tpc']), (21, COL['sphenix_si']), (8.4, fs.MUTED)):
        ax.axvline(thr, color=c, lw=1.0, ls='--')
    ax.set_xscale('log')
    ax.set_xlabel('pT of the softer lepton  [MeV]')
    ax.set_ylabel('fraction per bin  (|y_X| < 1)')
    ax.legend(fontsize=8, loc='upper right')
    ymax = max(v.max() for v in rows.values())
    for thr, lab, c in ((59, 'STAR', COL['star']), (104, 'sPHENIX TPC', COL['sphenix_tpc']),
                        (21, 'sPHENIX Si', COL['sphenix_si']), (8.4, 'at rest', fs.MUTED)):
        ax.text(thr * 1.05, ymax * 0.55, lab, color=c, fontsize=8, rotation=90, va='bottom')
    fs.title(ax, 'The soft lepton sets the acceptance', 'Au+Au 200 GeV meson spectra (mT scaling); dashed: tracking thresholds at η = 0')
    df = pd.DataFrame(dict(pt_lo_MeV=bins[:-1] * 1e3, pt_hi_MeV=bins[1:] * 1e3, **rows))
    fs.save(fig, OUT / 'fig_lepton_pt', data=df)


def fig_spectra(results):
    dets = ['star', 'sphenix_tpc', 'sphenix_si', 'alice_its_0p2T']
    fig, axs = fs.figure(figsize=(9.6, 6.4), nrows=2, ncols=2)
    axs = axs.ravel()
    bins = np.arange(8, 30.01, 0.5)
    tabs = {}
    for ax, det in zip(axs, dets):
        sysk = SYSTEM[det]
        ds = DATASETS[sysk]
        e = kin.eta_over_pi0(sysk)
        tab = dict(m_lo=bins[:-1], m_hi=bins[1:])
        for src, lab, col, mult in (('dal_pi0', 'π⁰ Dalitz', '#0072B2', 1.0), ('dal_eta', 'η Dalitz', '#009E73', e),
                                    ('conv', 'conversions after veto (few MC events)', '#D55E00', 1.0)):
            s, d = load(det, src)
            if s is None or not len(d):
                continue
            dp = d[d['pass']]
            h, _ = np.histogram(dp.m, bins, weights=dp.w)
            h = h / per_dy(s) * mult * ds['n_ev'] * ds['dndy_pi0']
            ax.stairs(h, bins, color=col, label=lab)
            tab[src] = h
        for src, br, lab, col, mult in (('x17_pi0', BR_PI0_NA48, f'X17 from π⁰, BR {BR_PI0_NA48:.1e}', fs.ACCENT, 1.0),
                                        ('x17_eta', BR_ETA_ILLUS, f'X17 from η, BR {BR_ETA_ILLUS:.0e}', fs.TRACK, e)):
            s, d = load(det, src)
            if s is None or not len(d):
                continue
            dp = d[d['pass']]
            h, _ = np.histogram(dp.m, bins, weights=dp.w)
            h = h / per_dy(s) * mult * ds['n_ev'] * ds['dndy_pi0'] * br
            ax.stairs(h, bins, color=col, lw=1.8, label=lab)
            tab[src] = h
        ax.set_yscale('log')
        ax.set_ylim(bottom=max(1.0, ax.get_ylim()[0]))
        ax.set_xlabel('reconstructed m_ee  [MeV]')
        ax.set_ylabel(f'pairs / 0.5 MeV  ({ds["n_ev"]:.0e} ev)')
        fs.title(ax, DETECTORS[det].label, ds['label'])
        tabs[det] = pd.DataFrame(tab)
    axs[1].legend(fontsize=7, loc='lower right')
    fig.subplots_adjust(hspace=0.55, wspace=0.28)
    fs.save(fig, OUT / 'fig_mass_spectra', data=tabs)


def fig_reach(res):
    df = pd.DataFrame(res)
    df = df[df.det.isin(DET_ORDER)].set_index('det').loc[[d for d in DET_ORDER if d in set(df.det)]].reset_index()
    fig, ax = fs.figure(figsize=(8.4, 4.8))
    y = np.arange(len(df))
    for k, off, col, lab in (('pi0', -0.18, '#0072B2', 'π⁰ → γX17'), ('eta', 0.18, '#D55E00', 'η → γX17')):
        v = df.get(f'BR3_{k}')
        vs = df.get(f'BR3syst_{k}')
        if v is None:
            continue
        ax.barh(y + off, v, height=0.34, color=col, alpha=0.85, label=f'{lab}, stat. only')
        ax.plot(df.get(f'BR3syst4_{k}'), y + off, '|', color=fs.MUTED, ms=9, mew=1.4)
        ax.plot(vs, y + off, '|', color=fs.INK, ms=9, mew=1.4)
    ax.plot([], [], '|', color=fs.MUTED, ms=9, mew=1.4, label='with 0.01 % background-shape syst.')
    ax.plot([], [], '|', color=fs.INK, ms=9, mew=1.4, label=f'with {SYST:.1%} background-shape syst.')
    ax.axvspan(2.6e-5, 9e-5, color='#D55E00', alpha=0.10, zorder=0)
    ax.text(2.8e-5, -0.75, 'η: protophobic vector (est.)', color='#D55E00', fontsize=7.5)
    ax.axvline(BR_PI0_NA48, color='#0072B2', ls='--', lw=1)
    ax.text(BR_PI0_NA48 * 0.92, -0.75, 'NA48/2 π⁰ ceiling', color='#0072B2', fontsize=7.5, ha='right')
    ax.set_ylim(len(df) - 0.4, -1.1)
    ax.set_yticks(y)
    ax.set_yticklabels([f'{r.label}  [{r.system.split(" MB")[0]}]' for r in df.itertuples()], fontsize=7.6)
    ax.set_xscale('log')
    ax.set_xlabel('3σ reach on BR(P → γX17) × BR(X17 → e⁺e⁻)')
    ax.legend(fontsize=7.6, loc='upper center', bbox_to_anchor=(0.5, -0.13), ncol=2, frameon=False)
    fs.title(ax, 'Reach in meson decays, benchmark datasets',
             'Dalitz + conversions only (no combinatorics, no e-ID loss); 1e10 Au+Au / 1e12 pp / 1e14 pp (ALICE 3)')
    cols = ['det', 'label', 'system', 'n_ev'] + [c for c in df.columns if c.startswith(('BR3', 'A_dy', 'sigM', 'win', 'B_'))]
    fs.save(fig, OUT / 'fig_reach', data=df[cols])


def main():
    fs.use()
    OUT.mkdir(exist_ok=True)
    res = [analyse_det(d) for d in DET_ORDER]
    df = pd.DataFrame(res)
    df.to_csv(OUT / 'reach.csv', index=False)
    pd.set_option('display.width', 250)
    pd.set_option('display.max_columns', 40)
    show = ['det', 'A_dy_pi0', 'sigM_pi0', 'eps_chi2_pi0', 'win_pi0', 'BR3_pi0', 'BR3syst4_pi0', 'BR3syst_pi0', 'SoverB_at_BR3_pi0',
            'Bfrac_conv_pi0', 'A_dy_eta', 'sigM_eta', 'BR3_eta', 'BR3syst4_eta', 'BR3syst_eta', 'SoverB_at_BR3_eta',
            'conv_chi2_eff', 'conv_mass_median_all']
    print(df[[c for c in show if c in df.columns]].to_string(float_format=lambda v: f'{v:.3g}'))
    fig_ms()
    fig_lepton_pt()
    scan = fig_scan()
    print(scan.pivot(index='p_X', columns='det', values='pair_acceptance').round(3).to_string())
    print(scan.pivot(index='p_X', columns='det', values='sigma_M_MeV').round(2).to_string())
    fig_spectra(res)
    fig_reach(res)


if __name__ == '__main__':
    main()
