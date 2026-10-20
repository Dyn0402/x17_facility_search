#!/usr/bin/env python3
"""
soft_reach.py -- X17 reach of the continuous soft-neutron sources (FRM II MEDAPP, Birmingham
HF-ADNeF) with their own Geant4 beam background, re-weighted from two broad-band runs.

    python survey/soft_sim/soft_reach.py            # -> survey/soft_sim/out/soft_reach.csv, soft_*.csv
    python survey/soft_sim/soft_reach.py --only medapp_std bham_26_2m_pb5

Geant4 inputs (MX17_Full_Geant branch `soft`, the NFS cell and arms, sel tables in sel/):
  N5_beam_soft[_bigP]     log-flat neutrons 1 keV-20 MeV, forced first collision + roulette
  G5_beam_gamma[_bigP]    log-flat photons 0.1-20 MeV (--beam-particle gamma), roulette
Both: Ø8 cm disc 1 m upstream of the cell window, vacuum flight tube (Vac:55, Al 1 mm wall,
0.5 mm window), the 30 bar × 40 cm NFS cell (Be 3 mm window, Be/CFRP skin, Al 4 mm end cap).

A source = (neutron spectrum, n/s through the Ø8 cm spot) + (γ spectrum, γ/s through it).  Every
Geant4 row (single, leg, trigger, correlated two-arm event) is re-weighted by
rate · f(E)/g(E) / N_generated, with g the log-flat generation density.  Then, per day:

  X17, IPC    the NFS signal tables (survey_fast.nfs_model: θ histograms per E_n bin, NFS cuts)
              × captures per bin of this source / NFS captures per bin
  accidental  pairs of this source's own "ok" singles (leg + MM segment) in different arms,
              |Δt| < 5 ns, importance-sampled ∝ rate, through the NFS reconstruction and cuts
              (beam-axis vertex DCA < 60 mm, E_sum > W/2 with W at E_n = 0.5 MeV)
  correlated  this source's same-event two-arm "ok" pairs, same cuts (200 response draws each)
  cosmics     the LNL L4 tables, all day (DC beam), shared among the bins like the signal
  exposure    DREAM live time 1/(1 + (random + correlated two-arm triggers)·298 µs) ×
              exp(−2·occ), occ = ok singles per arm in 1 µs (survey_fast convention); random
              triggers from all legs, 2τ = 20 ns

DC beam: no E_n tag, so the fit is the θ histogram summed over E_n ('θ, no TOF').  The beam is
throttled (s ≤ 1) to the best 3σ reach.  Not in the model: the room, the beam dump downstream
(the beam leaves through the world volume), shielding leakage from the source itself, and air
in front of the cell (the tube is evacuated up to the window).
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
if not hasattr(np, 'trapezoid'):
    np.trapezoid = np.trapz

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / 'survey'))
sys.path.insert(0, str(ROOT / 'ganil_nfs' / 'sim'))
sys.path.insert(0, str(ROOT / 'frm2_medapp'))
sys.path.insert(0, str(ROOT / 'birmingham'))
import survey_fast as SF                                      # noqa: E402
import survey_yield as Y                                      # noqa: E402
import nfs_reach as R                                         # noqa: E402

SEL = HERE / 'sel'
OUT = HERE / 'out'
DAY = 86400.0
NB = SF.NB
SOFT = SF.SOFT
GEN = {'n': (1e-3, 20.0), 'g': (0.1, 20.0), 'h': (14.0, 19.0)}   # generation ranges [MeV]
FLAT = {'h'}                                                  # flat in E; the others log-flat
RUN = {'n': 'N5_beam_soft', 'g': 'G5_beam_gamma', 'h': 'G6_beam_gamma'}
PART = {'n': 'n', 'g': 'g', 'h': 'g'}                         # which spectrum a run samples
OPTIONAL = {'h'}                                              # G6 (14-19 MeV γ) replaces G5 there when present
W_DC = float(R.F.w_of_en(0.5))                                # W for the DC E_sum cut and m_ee
K_SMEAR = 200
CORR_MODE = 'fact'            # 'fact' (headline) or 'direct' (--corr direct)
MAX_ACC = 400_000
E_GRID = np.geomspace(1e-3, 20.0, 3000)


# --------------------------------------------------------------------------- #
@dataclass
class Soft:
    key: str
    label: str
    fn: np.ndarray                  # normalised neutron dN/dE on E_GRID
    n_cell: float                   # n/s through the Ø8 cm spot
    fg: np.ndarray                  # normalised γ dN/dE on E_GRID
    g_cell: float                   # γ/s through the spot
    site: str = ''
    note: str = ''


def _lines(lines, width=0.01):
    """normalised sum of narrow Gaussians: [(E MeV, weight), ...], σ = width·E."""
    f = np.zeros_like(E_GRID)
    for e0, w in lines:
        f += w * np.exp(-0.5 * ((E_GRID - e0) / (width * e0)) ** 2) / (width * e0)
    return f / np.trapezoid(f, E_GRID)


def _mix(parts):
    """[(normalised pdf, rate), ...] -> (normalised pdf, total rate)"""
    tot = sum(r for _, r in parts)
    if tot <= 0:
        return np.zeros_like(E_GRID), 0.0
    return sum(f * r for f, r in parts) / tot, tot


MU_PB = {'n': 0.20, 'g478': 1.76, 'g15': 0.57}               # /cm, Pb: uncollided n (σ ≈ 6 b, 0.3-1 MeV),
                                                             # γ 478 keV, γ 15-18 MeV (NIST XCOM)


def sources():
    import medapp_beam as MB
    import bham_beam as BB
    S = []
    fn = MB.neutron_spectrum(E_GRID)
    fg = MB.gamma_spectrum(E_GRID)
    for key, flux, kg, lab in (('medapp_std', MB.FLUX_STD, 1.0, 'standard filters (B4C + 3.5 cm Pb), γ/n = 1'),
                               ('medapp_g3', MB.FLUX_STD, 3.0, 'standard filters, γ/n = 3 (pessimistic)'),
                               ('medapp_nopb', MB.FLUX_MAX, 3.0, 'no Pb filter: 7e8 n/cm²/s, γ/n = 3 (guess)')):
        S.append(Soft(key, f'MEDAPP {lab}', fn, flux * MB.AREA, fg, kg * flux * MB.AREA, 'medapp'))
    # Birmingham: target γ — 478 keV (⁷Li(p,p'γ) ~6e-5/p thick at 2.5 MeV, Taskaev 2006; plus ⁷Be decay,
    # 6 TBq × 10.4 %), and the ⁸Be lines (1e-7/p; γ0:γ1 = 1:2, the 441 and 1030 keV resonances 0.6:0.4)
    hi = [(17.64, 0.6 / 3), (18.15, 0.4 / 3), (14.64, 1.2 / 3), (15.15, 0.8 / 3)]
    for ep in (2.6, 2.8):
        fn_b = BB.spectrum_on_grid(ep, E_GRID)
        for d in (1.0, 2.0):
            for pb in (0.0, 5.0, 10.0):
                b, _ = BB.beam(ep, 30e-3, d)
                om = 50.0 / (d * 100) ** 2 / (4 * np.pi)
                p_s = 30e-3 / BB.E_CHARGE
                g478 = (6e-5 * p_s + 6e11 * 0.104) * om * np.exp(-MU_PB['g478'] * pb)
                g15 = BB.GAMMA_PER_P * p_s * om * np.exp(-MU_PB['g15'] * pb)
                fg_b, g_tot = _mix([(_lines([(0.478, 1.0)]), g478), (_lines(hi), g15)])
                key = f'bham_{ep * 10:.0f}_{d:.0f}m_pb{pb:.0f}'
                S.append(Soft(key, f'Birmingham E_p {ep} MeV, 30 mA, cell at {d:.0f} m, {pb:.0f} cm Pb in the beam',
                              fn_b, b['n_cell'] * np.exp(-MU_PB['n'] * pb), fg_b, g_tot, 'bham',
                              note=f'γ 478 keV {g478:.2g}/s, 15-18 MeV {g15:.2g}/s through the spot'))
    return S


# --------------------------------------------------------------------------- #
def load_runs(hw):
    out = {}
    for p, nm in RUN.items():
        z = R.load(nm + R.HW[hw], SEL)
        if z is None:
            if p in OPTIONAL:
                continue
            sys.exit(f'missing {SEL}/{nm + R.HW[hw]}_sel.npz (survey/soft_sim/fetch_sel.sh)')
        out[p] = z
    return out


def gen_density(p, e, runs=None):
    """generation density of run p at E; zero where another run of the same particle takes over
    (G5 above 14 MeV when G6 is loaded), so each energy is counted once."""
    lo, hi = GEN[p]
    e = np.asarray(e, float)
    if p in FLAT:
        g = np.where((e >= lo) & (e <= hi), 1.0 / (hi - lo), 0.0)
    else:
        g = np.where((e >= lo) & (e <= hi), 1.0 / (e * np.log(hi / lo)), 0.0)
    if runs is not None and p == 'g' and 'h' in runs:
        g = np.where((e >= GEN['h'][0]) & (e <= GEN['h'][1]), 0.0, g)
    return g


def row_rate(z, p, e_key, w_key, f, rate, runs=None):
    """per-row rate [1/s] for the source: rate · f(E)/g(E) · w / N_gen."""
    e = np.asarray(z[e_key], float)
    fe = np.interp(e, E_GRID, f, left=0.0, right=0.0)
    g = gen_density(p, e, runs)
    w = np.asarray(z[w_key], float) if w_key in z else np.ones(len(e))
    with np.errstate(divide='ignore', invalid='ignore'):
        return np.where(g > 0, rate * fe / g * w / float(z['cnt_n_generated']), 0.0)


def _two_arm(z, rr, hw, idx, draws=K_SMEAR):
    """events() of same-event pairs idx (rows of the pair table), weight rr per row, K response draws."""
    if not len(idx):
        return pd.DataFrame(columns=['th', 'm', 'Es', 'ok', 'w'])
    keys = ['c_all1', 'c_all2', 'c_dom1', 'd_dom1', 'c_dom2', 'd_dom2', 'E_sipm_a', 'E_plast_a', 'E_ls_a', 'V']
    zz = {k: z[k][idx] for k in keys}
    d = pd.concat([R.events(zz, hw, W_DC, seed=300 + r) for r in range(draws)], ignore_index=True)
    d['w'] = np.tile(rr[idx], draws) / draws
    return d


def _acc_pairs(sg, rr, hw, seed=5):
    """accidental pairs of singles from different events: per arm pair, importance-sampled ∝ rate;
    returned weights are pairs/s before the 2δ factor."""
    rng = np.random.default_rng(seed)
    out = []
    arm = sg['sg_arm']
    for a in range(4):
        for b in range(a + 1, 4):
            i = np.nonzero((arm == a) & (rr > 0))[0]
            j = np.nonzero((arm == b) & (rr > 0))[0]
            if not len(i) or not len(j):
                continue
            ra, rb = rr[i].sum(), rr[j].sum()
            I = rng.choice(i, MAX_ACC, p=rr[i] / ra)
            J = rng.choice(j, MAX_ACC, p=rr[j] / rb)
            keep = sg['sg_ev'][I] != sg['sg_ev'][J]
            I, J = I[keep], J[keep]
            zz = {'c_all1': sg['sg_c_all'][I], 'c_all2': sg['sg_c_all'][J],
                  'c_dom1': sg['sg_c_dom'][I], 'd_dom1': sg['sg_d_dom'][I],
                  'c_dom2': sg['sg_c_dom'][J], 'd_dom2': sg['sg_d_dom'][J],
                  'E_sipm_a': np.stack([sg['sg_E_sipm'][I], sg['sg_E_sipm'][J]], 1),
                  'E_plast_a': np.stack([sg['sg_E_plast'][I], sg['sg_E_plast'][J]], 1),
                  'E_ls_a': np.stack([sg['sg_E_ls'][I], sg['sg_E_ls'][J]], 1), 'V': np.zeros((len(I), 3))}
            d = R.events(zz, hw, W_DC, seed=seed + 10 * a + b)
            d['w'] = ra * rb / MAX_ACC
            out.append(d)
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame(columns=['th', 'm', 'Es', 'ok', 'w'])


def _concat_sg(runs, rates):
    """the ok-singles tables of both runs, with per-row rates for this source."""
    keys = ['sg_arm', 'sg_ev', 'sg_c_all', 'sg_c_dom', 'sg_d_dom', 'sg_E_sipm', 'sg_E_plast', 'sg_E_ls', 'sg_E']
    ps = list(runs)
    sg = {k: np.concatenate([np.asarray(runs[p][k]) if k != 'sg_ev' else
                             np.asarray(runs[p][k]) + i * 10 ** 15 for i, p in enumerate(ps)])
          for k in keys}
    return sg, np.concatenate([rates[f'{p}_sg'] for p in ps])


def components(src, runs, hw, M):
    """everything at full intensity (s = 1): per-arm rates, trigger rates, and θ histograms per day
    (accidentals before the 2δ factor and the s² scaling)."""
    rt = {}
    for p in runs:
        f, rate = (src.fn, src.n_cell) if PART[p] == 'n' else (src.fg, src.g_cell)
        z = runs[p]
        rt[f'{p}_sg'] = row_rate(z, p, 'sg_En', 'sg_w', f, rate, runs)
        rt[f'{p}_lg'] = row_rate(z, p, 'lg_En', 'lg_w', f, rate, runs)
        rt[f'{p}_tr'] = row_rate(z, p, 'tr_En', 'tr_w', f, rate, runs)
        rt[f'{p}_pr'] = row_rate(z, p, 'En', 'w', f, rate, runs)
    ok_arm = np.zeros(4)
    leg_arm = np.zeros(4)
    for p in runs:
        ok_arm += np.bincount(runs[p]['sg_arm'], rt[f'{p}_sg'], minlength=4)
        leg_arm += np.bincount(runs[p]['lg_arm'], rt[f'{p}_lg'], minlength=4)
    corr_trig = sum(rt[f'{p}_tr'].sum() for p in runs)
    # correlated two-arm ok pairs: direct (cuts per event, K response draws) and factorised
    # (every two-arm ok event at its own θ × the pooled vertex and E_sum pass fractions, per
    # particle; the NFS headline convention), because a handful of MC events pass all cuts
    dc, fact = [], []
    for p in runs:
        z = runs[p]
        idx = np.nonzero(rt[f'{p}_pr'] > 0)[0]
        d = _two_arm(z, rt[f'{p}_pr'], hw, idx)
        d['src'] = PART[p]
        dc.append(d)
        if len(d) and d.w.sum() > 0:
            sw = d.w.sum()
            fv, fe = d.w[d.ok].sum() / sw, d.w[d.Es > 0.5 * W_DC].sum() / sw
            f2 = d.copy()
            f2['w'] = f2.w * fv * fe
            fact.append(f2)
    dc = pd.concat(dc, ignore_index=True)
    fact = pd.concat(fact, ignore_index=True) if fact else dc.iloc[:0]
    sel_c = dc[dc.ok & (dc.Es > 0.5 * W_DC)]
    CORR_DIRECT = CORR_MODE == 'direct'
    sel_use = sel_c if CORR_DIRECT else fact
    sg, rr = _concat_sg(runs, rt)
    da = _acc_pairs(sg, rr, hw)
    sel_a = da[da.ok & (da.Es > 0.5 * W_DC)] if len(da) else da
    acc_raw = float(da.w.sum()) if len(da) else 0.0               # = Σ_{a<b} r_a r_b
    th = lambda d: np.histogram(d.th, R.TH_BINS, weights=d.w)[0] if len(d) else np.zeros(len(R.TH_BINS) - 1)  # noqa: E731
    return dict(ok_arm=ok_arm, leg_arm=leg_arm, corr_trig=corr_trig,
                corr_th=th(sel_use) * DAY, corr_raw=float(dc.w.sum()) * DAY, corr_sel=float(sel_c.w.sum()) * DAY,
                corr_fact=float(fact.w.sum()) * DAY,
                corr_n_mc=int(len(sel_c) // K_SMEAR) if len(sel_c) else 0,
                acc_th=th(sel_a) * 2 * R.COINC_NS * 1e-9 * DAY, acc_pass=float(sel_a.w.sum()) / max(acc_raw, 1e-300),
                acc_raw=acc_raw * 2 * R.COINC_NS * 1e-9 * DAY, acc_n_mc=int(len(sel_a)),
                ok_g_frac=float(sum(rt[f'{p}_sg'].sum() for p in runs if PART[p] == 'g') / max(rr.sum(), 1e-300)),
                corr_g_frac=float(dc[dc.src == 'g'].w.sum() / max(dc.w.sum(), 1e-300)) if len(dc) else 0.0)


def captures(src):
    cpn = Y.captures_per_neutron(E_GRID)
    edges = np.array([0.0] + R.EDGES[1:-1] + [99.0])
    return np.array([src.n_cell * np.trapezoid((src.fn * cpn)[(E_GRID >= edges[k]) & (E_GRID < edges[k + 1])],
                                               E_GRID[(E_GRID >= edges[k]) & (E_GRID < edges[k + 1])])
                     for k in range(NB)])


def at_throttle(src, C, M, cap, s):
    h = M['h']
    c_sig = np.where(M['cap_nfs'] > 0, cap * s / M['cap_nfs'], 0.0)
    share = cap / (cap.sum() or 1.0)
    cos = share / np.where(M['cos_frac'] > 0, M['cos_frac'], 1)
    occ = C['ok_arm'].sum() * s / 4 * SF.T_MM
    L = C['leg_arm'] * s
    rand = sum(L[a] * L[b] for a in range(4) for b in range(a + 1, 4)) * 2 * SF.TAU_HW
    live = 1 / (1 + (rand + C['corr_trig'] * s) * R.TAU_DAQ)
    expo = live * np.exp(-2 * occ)
    B = dict(IPC=(h['IPC_th'] * c_sig[:, None]).sum(0), cosmic=(h['cosmic_th'] * cos[:, None]).sum(0),
             acc=C['acc_th'] * s ** 2, corr=C['corr_th'] * s)
    return dict(c_sig=c_sig, B=B, live=live, occ=occ, rand=rand, expo=expo)


def rho3(M, st, days, soft_only):
    h = M['h']
    mult = st['c_sig'] * (np.isin(np.arange(NB), SOFT) if soft_only else 1.0)
    S1 = (h['X17_th'] * mult[:, None]).sum(0) / R.RHO_REF * st['expo'] * days
    Bt = sum(st['B'].values()) * st['expo'] * days

    def z2(rho):
        return R.z2_asimov(S1 * rho, Bt)
    lo, hi = 1e-7, 1e3
    if z2(hi) < 9:
        return np.inf
    for _ in range(60):
        mid = np.sqrt(lo * hi)
        lo, hi = (mid, hi) if z2(mid) < 9 else (lo, mid)
    return np.sqrt(lo * hi)


def window_counts(st, M, soft_only, lo=100.0, hi=150.0):
    """per day in the X17 θ window (100-150°), at ρ = ATOMKI, for the tables."""
    m = (R.TH_BINS[:-1] >= lo) & (R.TH_BINS[1:] <= hi)
    h = M['h']
    mult = st['c_sig'] * (np.isin(np.arange(NB), SOFT) if soft_only else 1.0)
    out = {f'{k}_win_per_day': float(v[m].sum() * st['expo']) for k, v in st['B'].items()}
    out['X17_win_per_day'] = float((h['X17_th'] * mult[:, None]).sum(0)[m].sum() * st['expo'])
    return out


def singles_table(hws=tuple(R.HW)):
    """ok singles and legs per arm per incident particle vs its energy (log bins), N5/G5, with the
    survey's N4 table and its flat (NFS-average) bound for comparison -> out/singles_vs_E.csv."""
    rows = []
    for hw in hws:
        runs = load_runs(hw)
        for p in runs:
            lo, hi = GEN[p]
            z = runs[p]
            if p in FLAT:
                e = np.linspace(lo, hi, 6)
                frac = np.diff(e) / (hi - lo)
            else:
                e = np.geomspace(lo, hi, 4 * int(round(np.log10(hi / lo))) + 1)
                frac = np.log(e[1:] / e[:-1]) / np.log(hi / lo)
            N = float(z['cnt_n_generated'])
            for nm, ek, wk in (('ok', 'sg_En', 'sg_w'), ('leg', 'lg_En', 'lg_w')):
                h = np.histogram(z[ek], e, weights=z[wk])[0] / (N * frac) / 4
                n = np.histogram(z[ek], e)[0]
                rows += [dict(hw=hw, particle='neutron' if p == 'n' else 'gamma', run=RUN[p], kind=nm, lo=a, hi=b,
                              E=np.sqrt(a * b), per_arm=v, n_mc=int(k)) for a, b, v, k in zip(e[:-1], e[1:], h, n)]
        M = SF.nfs_model(hw)
        ps = M['ps'].sum(0).mean(0)                                    # prompt + delayed, mean over arms
        for a, b, v in zip(SF.PS_EDGES[:-1], SF.PS_EDGES[1:], ps):
            rows.append(dict(hw=hw, particle='neutron', kind='survey N4', lo=a, hi=b, E=np.sqrt(a * b), per_arm=v, n_mc=-1))
        rows.append(dict(hw=hw, particle='neutron', kind='survey flat', lo=0.1, hi=45, E=np.nan,
                         per_arm=float(M['ps_avg'].sum(0).mean()), n_mc=-1))
    t = pd.DataFrame(rows)
    t.to_csv(OUT / 'singles_vs_E.csv', index=False, float_format='%.4g')
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--days', type=float, nargs='+', default=[14.0, 50.0])
    ap.add_argument('--only', nargs='+')
    ap.add_argument('--hw', choices=list(R.HW), help='one hardware set only (testing)')
    ap.add_argument('--corr', choices=('fact', 'direct'), default='fact', help='correlated beam term')
    ap.add_argument('--tag', default='', help='suffix for the output files')
    a = ap.parse_args()
    global CORR_MODE, OUT
    CORR_MODE = a.corr
    if a.tag:
        OUT = OUT.parent / f'out_{a.tag}'
    hws = [a.hw] if a.hw else list(R.HW)
    OUT.mkdir(exist_ok=True)
    print(singles_table(hws).query('kind != "leg"').to_string(index=False))
    srcs = sources()
    if a.only:
        srcs = [s for s in srcs if s.key in a.only]
    rows, curves, comps = [], [], []
    grid = np.geomspace(1e-4, 1.0, 41)
    for hw in hws:
        M = SF.nfs_model(hw)
        runs = load_runs(hw)
        for src in srcs:
            C = components(src, runs, hw, M)
            cap = captures(src)
            ipc_day = cap * Y.alpha(np.array(R.NODES)) * DAY
            comps.append(dict(key=src.key, hw=hw, n_cell=src.n_cell, g_cell=src.g_cell,
                              ok_singles_per_arm=C['ok_arm'].mean(), legs_per_arm=C['leg_arm'].mean(),
                              ok_singles_gamma_frac=C['ok_g_frac'], corr_trig_per_s=C['corr_trig'],
                              corr_ok2_per_day=C['corr_raw'], corr_sel_per_day=C['corr_sel'], corr_sel_mc=C['corr_n_mc'],
                              corr_fact_per_day=C['corr_fact'],
                              corr_gamma_frac=C['corr_g_frac'], acc_raw_per_day=C['acc_raw'], acc_pass=C['acc_pass'],
                              acc_sel_mc=C['acc_n_mc'], ipc_per_day=float(ipc_day.sum()),
                              ipc_soft_per_day=float(ipc_day[SOFT].sum()), note=src.note))
            for days in a.days:
                for soft in (True, False):
                    res = []
                    for s in grid:
                        st = at_throttle(src, C, M, cap, s)
                        res.append((rho3(M, st, days, soft), s, st))
                        if days == 50 and hw == 'big plastics':
                            curves.append(dict(key=src.key, signal='E* ≤ 22' if soft else 'all E*', throttle=s,
                                               n_cell=src.n_cell * s, rho3=res[-1][0]))
                    r, s, st = min(res, key=lambda x: x[0])
                    st0 = at_throttle(src, dict(C, acc_th=C['acc_th'] * 0, corr_th=C['corr_th'] * 0,
                                                ok_arm=C['ok_arm'] * 0, leg_arm=C['leg_arm'] * 0, corr_trig=0.0),
                                      M, cap, 1.0)
                    rows.append(dict(key=src.key, site=src.site, source=src.label, hw=hw, days=days,
                                     signal='E* ≤ 22 MeV' if soft else 'all E*', rho3=r, vs_ATOMKI=r / R.RHO_REF,
                                     throttle=s, rho3_floor=rho3(M, st0, days, soft), live=st['live'], occ=st['occ'],
                                     rand_trig_per_s=st['rand'], **window_counts(st, M, soft)))
            print(f'{hw:13s} {src.key:22s} ok/arm {C["ok_arm"].mean():.3g}/s  legs/arm {C["leg_arm"].mean():.3g}/s  '
                  f'corr sel {C["corr_sel"]:.3g}/d ({C["corr_n_mc"]} MC)  acc pass {C["acc_pass"]:.2g} ({C["acc_n_mc"]} MC)',
                  flush=True)
    t, cv, cp = pd.DataFrame(rows), pd.DataFrame(curves), pd.DataFrame(comps)
    if a.only and (OUT / 'soft_reach.csv').exists():
        t = pd.concat([pd.read_csv(OUT / 'soft_reach.csv').query('key not in @a.only'), t], ignore_index=True)
        cv = pd.concat([pd.read_csv(OUT / 'soft_throttle.csv').query('key not in @a.only'), cv], ignore_index=True)
        cp = pd.concat([pd.read_csv(OUT / 'soft_components.csv').query('key not in @a.only'), cp], ignore_index=True)
    t.to_csv(OUT / 'soft_reach.csv', index=False, float_format='%.4g')
    cv.to_csv(OUT / 'soft_throttle.csv', index=False, float_format='%.4g')
    cp.to_csv(OUT / 'soft_components.csv', index=False, float_format='%.4g')
    pd.set_option('display.width', 250)
    print(cp.drop(columns='note').to_string(index=False))
    print(t[t.days == 50].pivot_table(index='key', columns=['hw', 'signal'], values='rho3', sort=False).to_string())


if __name__ == '__main__':
    main()
