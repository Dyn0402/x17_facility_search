#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lnl_geant.py -- the LNL Geant4 runs (L1-L6, as built and with big plastics)
-> acceptance x efficiency, E_sum, cosmics, EPC, accidentals, DAQ load, reach.

    python lnl/sim/fetch_sel.sh             # copy the merged tables from EOS
    python lnl/sim/lnl_geant.py             # -> lnl/out/geant/*.csv, figures

Inputs: lnl/sim/sel/<run>_<sample>[_bigP]_sel.npz, one per Geant4 sample, made on
lxplus by lnl/sim/lxplus/lnl_reduce.py + lnl_merge.py.  Every row is an event
with >= 2 "ok" arms (trigger leg = SiPM bar AND plastic >= 0.5 MIP, plus a
Micromegas segment in the active area); the two arms with the most
scintillator energy form the pair.  Nothing here uses Monte Carlo truth to
select: the opening angle is the chord from the beam spot (0,0,0) to the two
Micromegas charge centroids (reco_c).

The physics weights (yields, direct/resonant split, IPC alpha) come from
lnl_rates.py (out/yields.csv, out/ipc_alpha.csv), so this file replaces only
the detector part of that estimate: the toy acceptance x EPS_REST, the gamma1
leak, and the cosmic rate.

Analysis levels (all on top of the two-arm trigger):
    E_sum      E1 + E2 > ecut (SiPM + plastic + LS of the two arms, MeV)
    MM 15°     both segments point back to the spot (direction smeared 15°,
               the measured MX17 chambers; DCA < D90 = 90 % signal per arm),
               and a 20° collinearity veto (one straight track through 2 arms)
    MM 3°      the same with 3° segments (the ILL "upgrade" scenario)
    + TOF      the SiPM-wall time-of-flight veto (σ_t = 0.3 ns per arm):
               a cosmic muon reaches the lower arm 1-2 ns after the upper
Reach: a counting window and a binned Asimov/Fisher template fit over
90-180° (free IPC and gamma1 normalisations), 3 sigma on R = X17/gamma0.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
LNL = HERE.parent
SEL = Path(__import__('os').environ.get('LNL_SEL', HERE / 'sel'))
OUT = LNL / 'out' / 'geant'
FIGS = OUT / 'figures'
sys.path.insert(0, str(LNL))
sys.path.insert(0, str(LNL.parent / 'ill'))
import lnl_rates as LR      # noqa: E402

HW = {'as built': '', 'as built, LS off': '', '20 SiPM bars': '_sipm20', 'big plastics': '_bigP'}
#: variants that read the as-built files but take E_sum without the liquid
#: scintillators (they did not work at n_TOF: pile-up)
NO_LS = {'as built, LS off'}
#: cosmic and γ-line runs were not repeated for the 20-bar readout: use as built
#: (4 more instrumented bars per wall: slightly more singles, small after cuts)
FALLBACK = {'20 SiPM bars': 'as built'}
MU_LIVE_S = 60.0 / (300.0 * 300.0)       # s of live time per generated μ (1 /cm²/min, 3x3 m plane)
R_MM_MM = 220.0                          # mm, beam spot -> middle of the drift gap
TWO_TAU_S = 20e-9                        # two-arm coincidence window (conservative)
DREAM_TAU_S = 298e-6                     # DREAM RAW, 20 samples (nTof_x17_DAQ report)
BINS = np.arange(90, 181, 2.0)
XC = 0.5 * (BINS[1:] + BINS[:-1])
#: γ-line runs: lines drawn with equal weight (submit_lnl.py GAMMA_LINES)
LINES = {'gam_8Be': (18.15, 17.64, 15.1, 14.6), 'gam_19F': (6.13, 6.92, 7.12), 'gam_7Li': (0.478,)}


#: analysis levels: seg = MM segment direction resolution [deg] for the pointing
#: cut (D set to keep 90 % of X17 segments per arm, calibrated on the as-built
#: X17 sample: scattering in the window and gas is included) and the 20°
#: collinearity veto; tof = per-arm time resolution [ns] of the SiPM wall for
#: the time-of-flight veto (a muon reaches the lower arm ~1-2 ns after the upper)
TOF_SIGMA_NS = 0.3
REF_LEVEL = 'MM 15° + TOF'      # the level the figures show
TOF_K = 2.0
LEVELS = {'trigger': dict(seg=None, tof=None),
          'MM 15°': dict(seg=15.0, tof=None),
          'MM 3°': dict(seg=3.0, tof=None),
          'MM 15° + TOF': dict(seg=15.0, tof=TOF_SIGMA_NS),
          'MM 3° + TOF': dict(seg=3.0, tof=TOF_SIGMA_NS)}
_D90: dict = {}


def seg_D(deg):
    """DCA cut [mm] keeping 90 % of X17 segments per arm at this resolution."""
    if deg not in _D90:
        z = load('L1', 'X17_m16.7')
        if z is None:
            _D90[deg] = R_MM_MM * np.tan(np.radians(2.146 * deg))
        else:
            rng = np.random.default_rng(99)
            d = []
            for k in ('1', '2'):
                c, dd = z['c_dom' + k], z['d_dom' + k]
                ok = np.isfinite(dd).all(1) & np.isfinite(c).all(1)
                d.append(dca0(c[ok], smear_dir(dd[ok], deg, rng)))
            _D90[deg] = float(np.percentile(np.concatenate(d), 90))
        print(f'  pointing cut at {deg:g}°: D = {_D90[deg]:.0f} mm (90 % of X17 segments)')
    return _D90[deg]
COLL_DEG = 20.0
REACH_SCENARIOS = ('ATOMKI 2016 anomaly', 'ATOMKI 2016, 18.15 res', 'LNL 2023-24, thick',
                   'MEG II-2026 normalisation', 'ATOMKI 2022 direct', 'Hanoi 2024')
#: E_sum windows (lo, hi) in MeV.  The upper edge matters: a muon through two
#: arms leaves 20-35 MeV (LS), an X17 pair has 17.1 MeV of kinetic energy.
ECUTS = tuple((lo, hi) for lo in (0, 6, 8, 9, 10, 11, 12, 13) for hi in (14, 15, 16, 17, 18, 20, 99)
              if hi >= lo + 3)
ECUTS_TABLE = ((0, 99), (13, 99), (11, 15), (12, 16), (13, 17), (9, 14))


def ewin(ec):
    return 'none' if ec == (0, 99) else (f'> {ec[0]}' if ec[1] >= 99 else f'{ec[0]}–{ec[1]}')


# --------------------------------------------------------------------------- #
_CACHE: dict = {}


def load(run, sample, hw='as built'):
    key = (run, sample, hw)
    if key not in _CACHE:
        _CACHE[key] = _load(run, sample, hw)
    return _CACHE[key]


#: high-statistics extensions, combined with the base sample when present
EXT = {('L3', 'gam_8Be', ''): '_x20', ('L3', 'gam_8Be', '_bigP'): '_bigP_x10'}


def _combine(zs):
    if len(zs) == 1:
        return zs[0]
    out = {}
    for k in zs[0]:
        if k == 'cnt_lines':
            out[k] = zs[0][k]
        elif k.startswith('cnt_'):
            out[k] = sum(np.asarray(z[k]) for z in zs)
        else:
            out[k] = np.concatenate([z[k] for z in zs])
    return out


def _load(run, sample, hw):
    suf = HW[hw]
    f = SEL / f'{run}_{sample}{suf}_sel.npz'
    if not f.exists() and run in ('L3', 'L4') and hw in FALLBACK:
        suf = HW[FALLBACK[hw]]
        f = SEL / f'{run}_{sample}{suf}_sel.npz'
    if not f.exists():
        return None
    files = [f]
    ext = EXT.get((run, sample, suf))
    if ext and (SEL / f'{run}_{sample}{ext}_sel.npz').exists():
        files.append(SEL / f'{run}_{sample}{ext}_sel.npz')
    z = _combine([dict(np.load(p, allow_pickle=True)) for p in files])
    z['ngen'] = int(z['cnt_n_generated'])
    z['name'] = '+'.join(p.stem for p in files) + ('|noLS' if hw in NO_LS else '')
    if hw in NO_LS:
        z['Esum'] = z['E_sipm2'] + z['E_plast2']
        if 'sg_E' in z:      # singles: no per-arm split kept, so LS stays in (small effect)
            pass
    else:
        z['Esum'] = z['E1'] + z['E2']
    return z


def smear_dir(d, deg, rng):
    if deg <= 0:
        return d
    d = d / np.linalg.norm(d, axis=-1, keepdims=True)
    a = np.where(np.abs(d[:, 0]) < 0.9, 1.0, 0.0)
    ref = np.stack([a, 1 - a, np.zeros_like(a)], 1)
    e1 = np.cross(d, ref)
    e1 /= np.linalg.norm(e1, axis=1, keepdims=True)
    e2 = np.cross(d, e1)
    th = np.radians(rng.normal(0, deg, len(d)))
    ph = rng.uniform(0, 2 * np.pi, len(d))
    return (np.cos(th)[:, None] * d + np.sin(th)[:, None]
            * (np.cos(ph)[:, None] * e1 + np.sin(ph)[:, None] * e2))


def dca0(c, d):
    """Distance of the line c + t d from the beam spot (origin)."""
    return np.linalg.norm(np.cross(c, d), axis=-1) / np.linalg.norm(d, axis=-1)


def line_angle(d1, d2):
    c = np.abs((d1 * d2).sum(-1)) / (np.linalg.norm(d1, axis=-1) * np.linalg.norm(d2, axis=-1))
    return np.degrees(np.arccos(np.clip(c, 0, 1)))


def pass_seg(c1, d1, c2, d2, level, seed):
    """Pointing for both arms + collinearity veto; True where the pair passes."""
    if level is None or level.get('seg') is None:
        return np.ones(len(c1), bool)
    deg = level['seg']
    D = seg_D(deg)
    rng = np.random.default_rng(seed)
    ok = np.isfinite(d1).all(1) & np.isfinite(d2).all(1)
    s1 = smear_dir(np.where(np.isfinite(d1), d1, 1.0), deg, rng)
    s2 = smear_dir(np.where(np.isfinite(d2), d2, 1.0), deg, rng)
    c1 = np.where(np.isfinite(c1), c1, 0.0)
    c2 = np.where(np.isfinite(c2), c2, 0.0)
    ok &= (dca0(c1, s1) < D) & (dca0(c2, s2) < D)
    ok &= line_angle(s1, s2) >= COLL_DEG
    return ok


_SEG: dict = {}


def select(z, level, ecut, seed=11):
    """two-arm events passing the analysis level and the E_sum window ecut = (lo, hi)."""
    if z is None or len(z['reco_c']) == 0:
        return np.zeros(0, bool)
    key = (z['name'], level, seed)
    if key not in _SEG:
        _SEG[key] = (pass_seg(z['c_dom1'], z['d_dom1'], z['c_dom2'], z['d_dom2'], LEVELS[level], seed)
                     & pass_tof(z, LEVELS[level], seed))
    return _SEG[key] & (z['Esum'] > ecut[0]) & (z['Esum'] < ecut[1])


def pass_tof(z, level, seed):
    """Time-of-flight veto.  Samples without arm times (most IPC runs) pass:
    their pairs come from the spot like the X17 and keep the same ~99 %."""
    n = len(z['reco_c'])
    if level.get('tof') is None or 't_sipm1' not in z:
        return np.ones(n, bool)
    rng = np.random.default_rng(seed + 7)
    sig = level['tof']
    t1 = z['t_sipm1'] + rng.normal(0, sig, n)
    t2 = z['t_sipm2'] + rng.normal(0, sig, n)
    z1, z2 = z['c_all1'][:, 2], z['c_all2'][:, 2]          # vertical = +z
    cut = TOF_K * np.sqrt(2) * sig
    dt_down = np.where(z1 > z2, t2 - t1, t1 - t2)          # lower minus upper arm
    level_arms = np.abs(z1 - z2) < 100.0
    ok = np.where(level_arms, np.abs(t1 - t2) < cut, dt_down < cut)
    return ok | ~np.isfinite(t1 - t2)


#: background templates are smoothed: the IPC samples leave only 10-200 MC
#: events per 10° above 90°, and empty 2° bins would fake infinite sensitivity
KDE_BW_DEG = 5.0


def kde_hist(x, bw=KDE_BW_DEG, w=None):
    """Gaussian KDE integrated over BINS (reflected at 180°), sum = sum of w."""
    from scipy.special import ndtr
    x = np.asarray(x, float)
    w = np.ones(len(x)) if w is None else np.asarray(w, float)
    if len(x) == 0:
        return np.zeros(len(XC))
    fine = np.arange(0, 180.01, 0.25)              # pre-bin: events -> 0.25° bins
    hf, _ = np.histogram(x, fine, weights=w)
    xf = 0.5 * (fine[1:] + fine[:-1])
    xx = np.r_[xf, 360.0 - xf]
    ww = np.r_[hf, hf]
    keep = ww > 0
    c = ndtr((BINS[None, :] - xx[keep, None]) / bw)
    return ((c[:, 1:] - c[:, :-1]) * ww[keep, None]).sum(0)


def hist(z, mask, weights=None, smooth=False):
    """reco opening angle, per generated event, in BINS."""
    if z is None:
        return np.zeros(len(XC))
    w = None if weights is None else weights[mask]
    if smooth:
        sel = mask & (z['reco_c'] > BINS[0] - 4 * KDE_BW_DEG)
        return kde_hist(z['reco_c'][sel], w=None if weights is None else weights[sel]) / z['ngen']
    h, _ = np.histogram(z['reco_c'][mask], BINS, weights=w)
    return h / z['ngen']


# --------------------------------------------------------------------------- #
# acceptance tables
# --------------------------------------------------------------------------- #
PAIR_SAMPLES = [('L1', 'X17_m16.6'), ('L1', 'X17_m16.7'), ('L1', 'X17_m16.8'), ('L1', 'X17_m17.0'),
                ('L2', 'M1_18.15'), ('L2', 'E1_18.15'), ('L2', 'M1_17.64'), ('L2', 'M1_15.1'),
                ('L2', 'E1_15.1'), ('L2', 'M1_14.6'), ('L2', 'E1_14.6')]
L5_SAMPLES = [(s, t) for s in ('X17_m16.7', 'M1_18.15') for t in ('', 'chAl0.5', 'chAl1', 'bkC20', 'bkCu25')]


def acceptance_table(windows=((125, 155), (130, 150), (120, 160))):
    rows = []
    for hw in HW:
        for run, s in PAIR_SAMPLES:
            z = load(run, s, hw)
            if z is None:
                continue
            n = z['ngen']
            base = dict(sample=s, hw=hw, n_gen=n,
                        mm_2arm=int(z['cnt_mm_2arm']) / n, mm_2arm_active=int(z['cnt_mm_2arm_active']) / n,
                        pair_tag=int(z['cnt_n_ok2']) / n)
            truth_ok = z['truth_arms'].astype(bool)
            for lev in LEVELS:
                for ec in ECUTS_TABLE:
                    m = select(z, lev, ec)
                    r = dict(base, level=lev, esum=ewin(ec), acc=m.sum() / n,
                             truth_arms=float(truth_ok[m].mean()) if m.any() else np.nan)
                    d = (z['reco_c'] - z['theta'])[m & truth_ok]
                    if len(d) > 30:
                        q = np.percentile(d, [16, 50, 84])
                        r.update(sigma68=0.5 * (q[2] - q[0]), bias=q[1])
                        df = (z['reco_first'] - z['theta'])[m & truth_ok]
                        qf = np.percentile(df, [16, 84])
                        r['sigma68_firsthit'] = 0.5 * (qf[1] - qf[0])
                    for lo, hi in windows:
                        w = (z['reco_c'] >= lo) & (z['reco_c'] < hi)
                        r[f'acc_{lo}_{hi}'] = (m & w).sum() / n
                    rows.append(r)
    return pd.DataFrame(rows)


def material_table():
    rows = []
    for s, tag in L5_SAMPLES:
        run = 'L5' if tag else ('L1' if s.startswith('X17') else 'L2')
        z = load(run, s + (f'_{tag}' if tag else ''))
        if z is None:
            continue
        truth_ok = z['truth_arms'].astype(bool)
        for lev in ('trigger', 'MM 15°', 'MM 3°'):
            m = select(z, lev, (0, 99))
            d = (z['reco_c'] - z['theta'])[m & truth_ok]
            q = np.percentile(d, [16, 50, 84]) if len(d) > 30 else [np.nan] * 3
            w = (z['reco_c'] >= 125) & (z['reco_c'] < 155)
            rows.append(dict(sample=s, variant=tag or 'baseline (CFRP 0.4, Al 10 µm)', level=lev,
                             n_gen=z['ngen'], acc=m.sum() / z['ngen'], acc_125_155=(m & w).sum() / z['ngen'],
                             sigma68=0.5 * (q[2] - q[0]), bias=q[1]))
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# backgrounds that are not IPC
# --------------------------------------------------------------------------- #
def cosmic_hists(hw):
    """Per live day: reco-θ histogram after each (level, ecut).  When nothing
    passes, 1 event is assumed (conservative); the shape then comes from the
    same level without the E_sum cut."""
    z = load('L4', 'cosmic', hw)
    if z is None:
        return None, None
    days = z['ngen'] * MU_LIVE_S / 86400
    out, rows = {}, []
    for lev in LEVELS:
        m0 = select(z, lev, (0, 99))
        h0 = kde_hist(z['reco_c'][m0 & (z['reco_c'] > 70)])
        for ec in ECUTS:
            m = select(z, lev, ec)
            n = int(((z['reco_c'] >= BINS[0]) & m).sum())
            h = kde_hist(z['reco_c'][m & (z['reco_c'] > 70)])
            if n < 5:
                h = h0 / max(h0.sum(), 1e-30) * max(n, 1)
            out[(lev, ec)] = h / days
            w = (z['reco_c'] >= 125) & (z['reco_c'] < 155)
            rows.append(dict(hw=hw, level=lev, esum=ewin(ec), live_days=days, n_pass=int(m.sum()),
                             n_pass_90_180=int(n), per_day_90_180=n / days,
                             per_day_125_155=(m & w).sum() / days, trig2_per_s=int(z['cnt_trig2']) / (days * 86400)))
    return out, pd.DataFrame(rows)


def epc_hists(hw):
    """EPC/Compton pairs from the 8Be γ lines: reco-θ histogram per γ of each line."""
    z = load('L3', 'gam_8Be', hw)
    if z is None:
        return None, None
    nline = z['ngen'] / len(LINES['gam_8Be'])
    out, rows = {}, []
    for L in LINES['gam_8Be']:
        lm = np.isclose(z['inv_mass'], L, atol=1e-3)
        for lev in LEVELS:
            for ec in ECUTS:
                m = select(z, lev, ec) & lm
                out[(L, lev, ec)] = kde_hist(z['reco_c'][m & (z['reco_c'] > 70)]) / nline
                w = (z['reco_c'] >= 125) & (z['reco_c'] < 155)
                rows.append(dict(hw=hw, line=L, level=lev, esum=ewin(ec), per_gamma=m.sum() / nline,
                                 per_gamma_125_155=(m & w).sum() / nline))
    return out, pd.DataFrame(rows)


def singles(hw):
    """Per-arm rates of 'ok' singles and of trigger legs, per γ of each line and
    per second of cosmics; plus the single tables for accidental pairing."""
    res = {}
    for samp, lines in LINES.items():
        z = load('L3', samp, hw)
        if z is None:
            continue
        nline = z['ngen'] / len(lines)
        cl = [round(float(x), 3) for x in np.atleast_1d(z.get('cnt_lines', []))]
        for L in lines:
            k = cl.index(round(L, 3)) if round(L, 3) in cl else None
            leg_arm = np.array(z['cnt_line_leg_arm'][k]) if k is not None else np.zeros(4)
            trig2 = int(z['cnt_line_trig2'][k]) if k is not None else 0
            sm = np.isclose(z['sg_line'], L, atol=1e-3)
            res[('gam', L)] = dict(norm=nline, leg_arm=leg_arm / nline, trig2=trig2 / nline,
                                   sg={k2: z[f'sg_{k2}'][sm] for k2 in ('arm', 'E', 'c_all', 'c_dom', 'd_dom')})
    z = load('L4', 'cosmic', hw)
    if z is not None:
        live = z['ngen'] * MU_LIVE_S
        res[('cosmic', 0)] = dict(norm=live, leg_arm=np.array(z['cnt_leg_arm']) / live,
                                  trig2=int(z['cnt_trig2']) / live,
                                  sg={k2: z[f'sg_{k2}'] for k2 in ('arm', 'E', 'c_all', 'c_dom', 'd_dom')})
    return res


def gamma_rates(y, I_uA):
    """γ/s per line at the target for one yields row (lnl_rates scenario)."""
    pps = I_uA * 1e-6 / LR.E_CHARGE
    g0, g1 = y.Y_g0 * pps, y.Y_g1 * pps
    f17 = y.frac_17_64
    return {18.15: g0 * (1 - f17), 17.64: g0 * f17, 15.1: g1 * (1 - f17), 14.6: g1 * f17}


def accidentals(sg, rates, level, ecut, n_pairs=400_000, seed=3):
    """Random two-arm pairs of 'ok' singles: per-second rate passing the level
    and E_sum cut, as a reco-θ histogram.  rates: {(kind, line): per norm unit
    rate} -- e.g. γ/s for a line, 1 for cosmics (norm already per second)."""
    rng = np.random.default_rng(seed)
    pools = {a: [] for a in range(4)}
    r_arm = np.zeros(4)
    for key, rate in rates.items():
        if key not in sg or rate <= 0:
            continue
        s = sg[key]
        per = rate / s['norm']               # singles/s per stored row
        for a in range(4):
            m = s['sg']['arm'] == a
            if m.any():
                pools[a].append((per * m.sum(), {k: v[m] for k, v in s['sg'].items()}))
                r_arm[a] += per * m.sum()
    h = np.zeros(len(XC))
    total = 0.0
    for a in range(4):
        for b in range(a + 1, 4):
            if r_arm[a] <= 0 or r_arm[b] <= 0:
                continue
            rate_ab = TWO_TAU_S * r_arm[a] * r_arm[b]
            total += rate_ab

            def draw(arm):
                ws = np.array([p[0] for p in pools[arm]])
                src = rng.choice(len(ws), n_pairs, p=ws / ws.sum())
                out = {k: np.empty((n_pairs,) + pools[arm][0][1][k].shape[1:], np.float32)
                       for k in pools[arm][0][1]}
                for i, (_, tab) in enumerate(pools[arm]):
                    m = src == i
                    j = rng.integers(0, len(tab['arm']), m.sum())
                    for k in out:
                        out[k][m] = tab[k][j]
                return out
            A, B = draw(a), draw(b)
            th = np.degrees(np.arccos(np.clip(
                (A['c_all'] * B['c_all']).sum(1) / (np.linalg.norm(A['c_all'], axis=1)
                                                   * np.linalg.norm(B['c_all'], axis=1)), -1, 1)))
            m = ((A['E'] + B['E']) > ecut[0]) & ((A['E'] + B['E']) < ecut[1])
            m &= pass_seg(A['c_dom'], A['d_dom'], B['c_dom'], B['d_dom'], LEVELS[level], seed + a * 4 + b)
            # (no TOF on accidentals: conservative, it would keep only ~2kσ/2τ of them)
            h += rate_ab * kde_hist(th[m & (th > 70)]) / n_pairs
    return h, r_arm, total


# --------------------------------------------------------------------------- #
# reach
# --------------------------------------------------------------------------- #
def fisher_sigma(s, comps, mu):
    """σ(R) from the Asimov Fisher matrix; s = dμ/dR, comps = free-norm templates."""
    ok = mu > 0
    D = [s[ok]] + [c[ok] for c in comps if c[ok].sum() > 0]
    F = np.array([[np.sum(a * b / mu[ok]) for b in D] for a in D])
    try:
        return float(np.sqrt(np.linalg.inv(F)[0, 0]))
    except np.linalg.LinAlgError:
        return np.nan


_TPL: dict = {}


def build_templates(hw, level, ecut, alpha, cos, epc, mass='16.7'):
    key = (hw, level, ecut)
    if key not in _TPL:
        _TPL[key] = _build_templates(hw, level, ecut, alpha, cos, epc, mass)
    return dict(_TPL[key])


def _build_templates(hw, level, ecut, alpha, cos, epc, mass='16.7'):
    """Per-γ0 templates (reco-θ histograms) at one (hw, level, ecut)."""
    H = {}
    for run, s in PAIR_SAMPLES:
        z = load(run, s, hw)
        H[s] = hist(z, select(z, level, ecut), smooth=not s.startswith('X17')) if z is not None else None
    a = alpha.set_index(['W_MeV', 'multipole']).alpha_pair
    t = dict(H=H, a=a, cos=None if cos is None else cos[(level, ecut)],
             epc={L: (None if epc is None else epc[(L, level, ecut)]) for L in LINES['gam_8Be']},
             sig=H.get(f'X17_m{mass}'))
    return t


def reach_one(y, t, I_uA=1.0, days=1.0, acc=None, window=(125, 155)):
    """3σ R reach (counting in window, and Fisher over 90-180°) for one yields row."""
    H, a = t['H'], t['a']
    if t['sig'] is None or H['M1_18.15'] is None or H['E1_18.15'] is None:
        return None
    f17, fr, fd = y.frac_17_64, y.frac_18_15_res, y.frac_direct
    b_ipc = (f17 * a[(17.64, 'M1')] * H['M1_17.64'] + fr * a[(18.15, 'M1')] * H['M1_18.15']
             + fd * a[(18.15, 'E1')] * H['E1_18.15'])
    g1r = y.Y_g1 / y.Y_g0
    b_g1 = g1r * ((1 - y.frac_g1_direct) * a[(15.1, 'M1')] * H['M1_15.1']
                  + y.frac_g1_direct * a[(15.1, 'E1')] * H['E1_15.1'])
    e = t['epc']
    b_epc = np.zeros(len(XC))
    if e[18.15] is not None:
        b_epc = (1 - f17) * e[18.15] + f17 * e[17.64] + g1r * ((1 - f17) * e[15.1] + f17 * e[14.6])
    sig = (1 - f17) * t['sig']
    ng0 = y.Y_g0 * I_uA * 1e-6 / LR.E_CHARGE * 86400 * days
    cos = (t['cos'] if t['cos'] is not None else np.zeros(len(XC))) * days
    accd = (acc if acc is not None else np.zeros(len(XC))) * 86400 * days
    mu = ng0 * (b_ipc + b_g1 + b_epc) + cos + accd
    s = ng0 * sig
    w = (XC >= window[0]) & (XC < window[1])
    B, S = mu[w].sum(), s[w].sum()
    b_m1 = f17 * a[(17.64, 'M1')] * H['M1_17.64'] + fr * a[(18.15, 'M1')] * H['M1_18.15']
    b_e1 = fd * a[(18.15, 'E1')] * H['E1_18.15']
    # M1 (resonances), E1 (direct capture) and γ1 normalisations all free: the
    # fit has to learn the M1/E1 mix (no interference in the Born shapes)
    sf = fisher_sigma(s, [ng0 * (b_m1 + b_epc), ng0 * b_e1, ng0 * b_g1], mu)
    sf1 = fisher_sigma(s, [ng0 * (b_ipc + b_epc), ng0 * b_g1], mu)
    # counting in the window that maximises S/sqrt(B) (2° grid, >= 10° wide)
    cs, cb = np.r_[0, np.cumsum(s)], np.r_[0, np.cumsum(mu)]
    best = (0.0, None)
    for i in range(len(XC)):
        for j in range(i + 5, len(XC) + 1):
            bb = cb[j] - cb[i]
            if bb > 0 and (cs[j] - cs[i]) / np.sqrt(bb) > best[0]:
                best = ((cs[j] - cs[i]) / np.sqrt(bb), (BINS[i], BINS[j]))
    zopt, wopt = best
    r3opt = 3 / zopt if zopt > 0 else np.nan
    return dict(N_g0=ng0, S_ATOMKI=S * LR.R_ATOMKI_2016, B_ipc=ng0 * b_ipc[w].sum(),
                win_opt=f'{wopt[0]:.0f}-{wopt[1]:.0f}' if wopt else '', R3_count_opt=r3opt,
                days_count_opt=days * (r3opt / LR.R_ATOMKI_2016) ** 2,
                days_fisher_1norm=days * (3 * sf1 / LR.R_ATOMKI_2016) ** 2,
                B_g1=ng0 * b_g1[w].sum(), B_epc=ng0 * b_epc[w].sum(), B_cos=cos[w].sum(),
                B_acc=accd[w].sum(), R3_count=3 * np.sqrt(B) / S if S > 0 else np.nan,
                R3_fisher=3 * sf, R3_fisher_1norm=3 * sf1,
                days_count=days * (3 * np.sqrt(B) / S / LR.R_ATOMKI_2016) ** 2 if S > 0 else np.nan,
                days_fisher=days * (3 * sf / LR.R_ATOMKI_2016) ** 2)


# --------------------------------------------------------------------------- #
# figures
# --------------------------------------------------------------------------- #
HW_COL = {'as built': '#0072B2', 'as built, LS off': '#56B4E9', '20 SiPM bars': '#009E73', 'big plastics': '#D55E00'}
LEV_LS = {'trigger': ':', 'MM 15°': '-', 'MM 3°': '--', 'MM 15° + TOF': '-.', 'MM 3° + TOF': (0, (1, 1))}


def figures(acc, reach, scan, alpha, best_ecut):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use()
    a = alpha.set_index(['W_MeV', 'multipole']).alpha_pair

    # 1. reco opening angle, per γ0 (ATOMKI 2016 anomaly mix), MM 15°, best cut
    y = pd.read_csv(LNL / 'out' / 'yields.csv').set_index('scenario').loc['ATOMKI 2016 anomaly']
    fig, axs = plt.subplots(1, 4, figsize=(12, 3.6), sharey=True)
    rows = []
    for ax, hw in zip(axs, HW):
        ec = best_ecut.get((hw, REF_LEVEL), (0, 99))
        H = {s: hist(load(r, s, hw), select(load(r, s, hw), REF_LEVEL, ec), smooth=not s.startswith('X17'))
             for r, s in PAIR_SAMPLES
             if load(r, s, hw) is not None}
        if 'M1_18.15' not in H or 'X17_m16.7' not in H:
            continue
        f17, fr, fd = y.frac_17_64, y.frac_18_15_res, y.frac_direct
        comp = {
            'IPC γ₀ (M1 res + E1 direct)': f17 * a[(17.64, 'M1')] * H['M1_17.64'] + fr * a[(18.15, 'M1')] * H['M1_18.15']
            + fd * a[(18.15, 'E1')] * H['E1_18.15'],
            'IPC γ₁ (15.1 MeV)': y.Y_g1 / y.Y_g0 * ((1 - y.frac_g1_direct) * a[(15.1, 'M1')] * H['M1_15.1']
                                                 + y.frac_g1_direct * a[(15.1, 'E1')] * H['E1_15.1']),
            'X17 at R = 5.8e-6 (m 16.7)': LR.R_ATOMKI_2016 * (1 - f17) * H['X17_m16.7'],
        }
        for (lab, h), c in zip(comp.items(), ('#0072B2', '#009E73', fs.ACCENT)):
            ax.step(XC, h, where='mid', color=c, label=lab)
            rows += [dict(hw=hw, esum=ewin(ec), component=lab, theta=x, per_gamma0=v) for x, v in zip(XC, h)]
        tot = sum(comp.values())
        ax.step(XC, tot, where='mid', color=fs.INK, lw=0.8, label='sum')
        ax.set_yscale('log')
        ax.set_xlabel('reconstructed opening angle [deg]')
        ax.set_title(f'{hw}\nE_sum {ewin(ec)} MeV, {REF_LEVEL}', fontsize=8)
    axs[0].set_ylabel('pairs per γ₀ per 2°')
    axs[0].legend(frameon=False, fontsize=7, loc='lower left')
    fs.fig_title(fig, 'What the arms see: IPC continuum and the X17 bump at ATOMKI strength',
                 'Geant4, Li₂O 300 µg/cm² at 1.10 MeV, per ground-state γ; chord from the beam spot to the MM centroids')
    fs.save(fig, FIGS / 'geant_theta', data=pd.DataFrame(rows))

    # 2. E_sum spectra: can the stack tell 18 from 15 MeV?
    fig, axs = plt.subplots(1, 4, figsize=(12, 3.6), sharey=True)
    rows = []
    eb = np.arange(0, 22.1, 0.5)
    for ax, hw in zip(axs, HW):
        for s, c in (('X17_m16.7', fs.ACCENT), ('M1_18.15', '#0072B2'), ('E1_18.15', '#56B4E9'),
                     ('M1_15.1', '#009E73'), ('E1_15.1', '#8FD175')):
            z = load('L1' if s.startswith('X17') else 'L2', s, hw)
            if z is None:
                continue
            m = select(z, 'trigger', (0, 99)) & (z['reco_c'] >= 120) & (z['reco_c'] < 160)
            h, _ = np.histogram(z['Esum'][m], eb)
            h = h / max(h.sum(), 1)
            ax.step(eb[:-1] + 0.25, h, where='mid', color=c, label=s.replace('_', ' '))
            rows += [dict(hw=hw, sample=s, E_lo=e, frac=v) for e, v in zip(eb[:-1], h)]
        ax.set_xlabel('E_sum, two arms [MeV]')
        ax.set_title(hw, fontsize=9)
    axs[0].set_ylabel('fraction / 0.5 MeV (pairs at 120–160°)')
    axs[0].legend(frameon=False, fontsize=7)
    fs.fig_title(fig, 'Energy sum: 18 vs 15 MeV transitions',
                 'Geant4, two-arm trigger, reconstructed angle 120–160°; E_sum = SiPM + plastic + LS of the two arms (LS off: SiPM + plastic)')
    fs.save(fig, FIGS / 'geant_esum', data=pd.DataFrame(rows))

    # 3. days to 3σ vs E_sum cut
    fig, ax = fs.figure()
    keep = []
    for (hw, lev), g in scan.groupby(['hw', 'level']):
        if (hw, lev) not in best_ecut or lev not in ('MM 3°', REF_LEVEL):
            continue
        g = g[g.e_hi == best_ecut[(hw, lev)][1]].sort_values('e_lo')
        keep.append(g)
        ax.plot(g.e_lo, g.days_fisher_1norm_live, linestyle=LEV_LS[lev], marker='o', ms=3, color=HW_COL[hw],
                label=f'{hw}, {lev} (E < {best_ecut[(hw, lev)][1]:g})')
    key = pd.concat(keep) if keep else scan
    ax.set_yscale('log')
    ax.axhline(30, color=fs.MUTED, lw=0.6)
    ax.set_xlabel('E_sum lower edge [MeV] (upper edge: best for each curve)')
    ax.set_ylabel('days at 1 µA for 3σ at R(ATOMKI)')
    ax.legend(frameon=False, fontsize=7, ncol=2)
    fs.title(ax, 'Days to see the ATOMKI X17 at 3σ', 'Geant4; Asimov template fit 90–180° (IPC norm and γ₁ free, M1/E1 mix fixed); DAQ live time included')
    fs.save(fig, FIGS / 'geant_days_vs_ecut', data=key)

    # 4. the acceptance chain for X17
    rows = []
    for hw in HW:
        z = load('L1', 'X17_m16.7', hw)
        if z is None:
            continue
        n = z['ngen']
        ec = best_ecut.get((hw, REF_LEVEL), (0, 99))
        w = (z['reco_c'] >= 125) & (z['reco_c'] < 155)
        rows += [dict(hw=hw, step='MM, 2 arms, active area', acc=int(z['cnt_mm_2arm_active']) / n),
                 dict(hw=hw, step='+ trigger legs in both', acc=int(z['cnt_n_ok2']) / n),
                 dict(hw=hw, step=f'+ E_sum {ewin(ec)} MeV', acc=select(z, 'trigger', ec).sum() / n),
                 dict(hw=hw, step=f'+ {REF_LEVEL}', acc=select(z, REF_LEVEL, ec).sum() / n),
                 dict(hw=hw, step='+ 125–155° window', acc=(select(z, REF_LEVEL, ec) & w).sum() / n)]
    ch = pd.DataFrame(rows)
    if len(ch):
        fig, ax = fs.figure()
        xs = np.arange(5)
        for i, hw in enumerate(HW):
            g = ch[ch.hw == hw]
            if g.empty:
                continue
            ax.bar(xs + (i - 1.5) * 0.2, g.acc * 100, 0.19, color=HW_COL[hw], label=hw)
            for x, v in zip(xs, g.acc):
                ax.text(x + (i - 1.5) * 0.2, v * 100 + 0.5, f'{v*100:.1f}', ha='center', fontsize=5)
        ax.set_xticks(xs, ['MM 2 arms', '+ trigger', '+ E_sum', '+ MM 15°\n+ TOF', '+ 125–155°'], fontsize=8)
        ax.set_ylabel('X17 (m 16.7) acceptance × ε [%]')
        ax.legend(frameon=False, fontsize=8)
        fs.title(ax, 'Where the X17 pairs go', 'Geant4, 10⁶ X17 at 18.15 MeV from the beam spot')
        fs.save(fig, FIGS / 'geant_chain', data=ch)


def daq_row(hw, y, I, sg):
    """Hardware two-arm trigger rate (legs only, no MM) and DREAM live time."""
    gr = gamma_rates(y, I)
    rates = {('gam', L): r for L, r in gr.items()}
    rates[('cosmic', 0)] = 1.0
    leg = np.zeros(4)
    corr = 0.0
    for k, r in rates.items():
        if k in sg:
            leg += sg[k]['leg_arm'] * r
            corr += sg[k]['trig2'] * r
    acc2 = TWO_TAU_S * sum(leg[i] * leg[j] for i in range(4) for j in range(i + 1, 4))
    f = corr + acc2
    return dict(gamma_per_s=sum(gr.values()), leg_per_s_arm=leg.round(2).tolist(), trig_corr=corr,
                trig_acc=acc2, trig_total=f, live=1 / (1 + f * DREAM_TAU_S), _rates=rates)


# --------------------------------------------------------------------------- #
def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    if '--figs' in sys.argv:            # figures only, from the CSVs of the last full run
        sm = json.loads((OUT / 'summary.json').read_text())
        be = {tuple(k.split('|')): tuple(v) for k, v in sm['best_ecut'].items()}
        figures(pd.read_csv(OUT / 'acceptance_geant.csv'), pd.read_csv(OUT / 'reach_geant.csv'),
                pd.read_csv(OUT / 'esum_scan.csv'), pd.read_csv(LNL / 'out' / 'ipc_alpha.csv'), be)
        return 0
    FIGS.mkdir(parents=True, exist_ok=True)
    ytab = pd.read_csv(LNL / 'out' / 'yields.csv')
    alpha = pd.read_csv(LNL / 'out' / 'ipc_alpha.csv')
    have = sorted(p.stem for p in SEL.glob('*_sel.npz'))
    print(f'{len(have)} merged samples in {SEL}')

    acc = acceptance_table()
    acc.to_csv(OUT / 'acceptance_geant.csv', index=False)
    mat = material_table()
    mat.to_csv(OUT / 'material_scan.csv', index=False)

    summary = {}
    ref = ytab[ytab.scenario == 'ATOMKI 2016 anomaly'].iloc[0]
    scan_rows, reach_rows, daq_rows = [], [], []
    best_ecut = {}
    for hw in HW:
        cos, cos_tab = cosmic_hists(hw)
        epc, epc_tab = epc_hists(hw)
        sg = singles(hw)
        tag = {'as built': '_asbuilt', 'as built, LS off': '_asbuilt_noLS'}.get(hw, HW[hw])
        if cos_tab is not None:
            cos_tab.to_csv(OUT / f'cosmics{tag}.csv', index=False)
        if epc_tab is not None:
            epc_tab.to_csv(OUT / f'epc{tag}.csv', index=False)

        def one(y, I, lev, ec, masses):
            d = daq_row(hw, y, I, sg)
            rates = d.pop('_rates')
            t = build_templates(hw, lev, ec, alpha, cos, epc)
            acch = accidentals(sg, rates, lev, ec, n_pairs=60_000)[0] if sg else None
            out = []
            for m in masses:
                t['sig'] = t['H'].get(f'X17_m{m}')
                r = reach_one(y, t, I, 1.0, acc=acch)
                if r is None:
                    continue
                live = d['live']
                out.append(dict(hw=hw, scenario=y.scenario, I_uA=I, level=lev, esum=ewin(ec),
                                e_lo=ec[0], e_hi=ec[1], mass=float(m), live=live, **r,
                                days_fisher_live=r['days_fisher'] / live,
                                days_fisher_1norm_live=r['days_fisher_1norm'] / live,
                                days_count_opt_live=r['days_count_opt'] / live,
                                days_count_live=r['days_count'] / live))
            return out, d

        # stage 1: the E_sum window, on the reference setting (ATOMKI 2016 anomaly, 1 µA, m 16.7)
        for lev in LEVELS:
            for ec in ECUTS:
                rows, _ = one(ref, 1.0, lev, ec, ('16.7',))
                scan_rows += rows
            sc = pd.DataFrame([r for r in scan_rows if r['hw'] == hw and r['level'] == lev])
            if len(sc) and sc.days_fisher_1norm_live.notna().any():
                bb = sc.loc[sc.days_fisher_1norm_live.idxmin()]
                best_ecut[(hw, lev)] = (bb.e_lo, bb.e_hi)
        # stage 2: every scenario, current and mass at the chosen window
        for _, y in ytab[ytab.scenario.isin(REACH_SCENARIOS)].iterrows():
            for I in (1.0, 4.0):
                d = None
                for lev in LEVELS:
                    if (hw, lev) not in best_ecut:
                        continue
                    rows, d = one(y, I, lev, best_ecut[(hw, lev)], ('16.6', '16.7', '16.8', '17.0'))
                    reach_rows += rows
                if d is not None:
                    daq_rows.append(dict(hw=hw, scenario=y.scenario, I_uA=I, **d))
    scan = pd.DataFrame(scan_rows)
    scan.to_csv(OUT / 'esum_scan.csv', index=False)
    reach = pd.DataFrame(reach_rows)
    reach.to_csv(OUT / 'reach_geant.csv', index=False)
    daq = pd.DataFrame(daq_rows)
    daq.to_csv(OUT / 'daq_load.csv', index=False)

    pd.set_option('display.width', 250)
    pd.set_option('display.max_columns', 40)
    if len(acc):
        print('\n== acceptance (no E_sum window) ==')
        print(acc[acc.esum == 'none'][['sample', 'hw', 'level', 'mm_2arm_active', 'pair_tag', 'acc', 'acc_125_155',
                                        'sigma68', 'bias', 'sigma68_firsthit']].to_string(index=False, float_format=lambda v: f'{v:.4g}'))
    if len(reach):
        best = reach[(reach.scenario == 'ATOMKI 2016 anomaly') & (reach.I_uA == 1.0) & (reach.mass == 16.7)]
        print('\n== best E_sum window per (hw, level), ATOMKI 2016 anomaly, 1 uA, m=16.7 ==')
        print(best[['hw', 'level', 'esum', 'S_ATOMKI', 'B_ipc', 'B_g1', 'B_epc', 'B_cos', 'B_acc', 'live',
                    'days_count_live', 'win_opt', 'days_count_opt_live', 'days_fisher_1norm_live',
                    'days_fisher_live']].to_string(index=False, float_format=lambda v: f'{v:.3g}'))
        print('\n== DAQ ==')
        print(daq[daq.I_uA == 1.0].to_string(index=False, float_format=lambda v: f'{v:.3g}'))
        summary['best'] = best.to_dict('records')
        summary['best_ecut'] = {f'{k[0]}|{k[1]}': list(v) for k, v in best_ecut.items()}
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=1, default=float))
    if len(reach):
        figures(acc, reach, scan, alpha, best_ecut)
    return 0


if __name__ == '__main__':
    sys.exit(main())
