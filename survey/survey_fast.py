#!/usr/bin/env python3
"""
survey_fast.py -- the X17 reach of every fast-neutron source in the survey, by
re-weighting the GANIL/NFS Geant4 analysis (ganil_nfs/sim/nfs_reach.py) to the
source's spectrum, intensity and time structure.

    python survey/survey_fast.py               # -> survey/out/fast_reach.csv, fast_*.png
    python survey/survey_fast.py --check       # NFS row only, no occupancy/random-trigger terms

The NFS analysis gives, per E_n bin (0.2-25 MeV), Geant4 event lists with per-day
weights for X17, IPC (E1), correlated beam background, accidentals and cosmics,
for the 30 bar × 40 cm cell and the MX17 arms (as built / big plastics).  A
source f is the same apparatus with a different beam, so each class is scaled:

  X17, IPC     × cap_f,k / cap_NFS,k            (³He(n,γ) per bin, survey_yield P(E))
  accidentals  per bin, pairing rate 2δ Σ_a<b r_a r_b / (rep Δt_k) × the NFS
               pass fraction of that bin (vertex + E_sum); r_a = singles per arm
               from the NFS Geant4 singles-per-neutron vs E_n (N4 forced run)
  correlated   × (neutrons > 8.5 MeV)_f / (neutrons > 8.5 MeV)_NFS: every NFS
               correlated event came from E_n > 10 MeV
  cosmics      × the live fraction of each bin's TOF window (all of it for a DC beam)
  exposure     × DREAM live time (correlated + random two-arm triggers) × MM
               occupancy loss exp(−2·occ) (ILL convention), occ = singles per arm in 1 µs

The beam is throttled (s ≤ 1: collimator, current) to the best reach.  DC sources
have no E_n tag: their analysis is the θ fit summed over E_n ('θ, no TOF');
pulsed ones use m_ee | E_n.  Two signal conventions:
  all E*    X17/IPC constant at every E_n (the NFS 3.3e-3 convention);
  E* ≤ 22   X17 only from E_n ≤ 2.75 MeV (ATOMKI-like excitation; IPC everywhere).

What it cannot know (SURVEY.md §4.4): room and beam-dump background, γ from the
source (a crude extra-singles factor k_γ), the γ flash, singles from neutrons below
0.1 MeV (taken equal to 0.1-0.2 MeV), frame overlap.  It is a triage tool, scaled
from one Geant4 campaign, not a replacement for one.
"""
from __future__ import annotations

import argparse
import pickle
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
if not hasattr(np, 'trapezoid'):
    np.trapezoid = np.trapz
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'ganil_nfs' / 'sim'))
import survey_yield as Y                                     # noqa: E402
import nfs_reach as R                                        # noqa: E402

OUT = HERE / 'out'
CACHE = HERE / '.cache'
DAY = 86400.0
NB = len(R.NODES)                                   # 9 analysis bins, R.EDGES 0.2 … 25 MeV
PS_EDGES = np.array([0.1, 0.2] + R.EDGES[1:] + [45.0])   # singles-per-neutron bins (parent E_n)
PS_TO_K = np.array([0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 8])     # PS bin -> analysis bin
T_MM = 1e-6            # s, Micromegas memory (30 mm drift)
TAU_HW = 10e-9         # s, half-width of the hardware two-arm coincidence (random triggers)
SOFT = [0, 1, 2]       # bins with E_n ≤ 2.75 MeV: E* ≤ 22.1 MeV


# --------------------------------------------------------------------------- #
@dataclass
class Source:
    key: str
    label: str
    spectrum: np.ndarray            # dN/dE on Y.E_GRID, normalised
    n_cell: float                   # neutrons/s through the cell at full intensity, E ≥ e_min
    rep_hz: float | None = None     # None: DC/CW (no TOF); else pulses (or micro-pulses) per s
    flight_m: float = 0.0
    e_min: float = 0.0              # MeV; white pulsed beams: below this is gated off by TOF
    k_gamma: float = 0.0            # extra singles from source γ, as a fraction of the neutron singles
    macro_duty: float = 1.0         # pulsed: fraction of time inside macropulses (LANSCE); rep_hz is then the
                                    # micropulse rate inside them
    status: str = ''
    note: str = ''
    tof: bool = field(init=False)

    def __post_init__(self):
        self.tof = self.rep_hz is not None


def sources():
    g = Y.E_GRID
    n_nfs = nfs_n_per_s()
    ntof = Y.per_decade(fr=Y.NTOF)
    backn = Y.per_decade(fr=Y.BACKN)
    a50 = 50.0           # cm², a beam collimated to the 8 cm NFS spot (cell R = 50 mm)

    def above(f, e0):    # fraction of a spectrum above e0
        return Y.window_fraction(g, f, e0, 99.0)

    return [
        Source('nfs', 'GANIL NFS, d(40)+Be, 50 µA (Geant4 reference)', Y.nfs(), n_nfs, 440e3, 13.6,
               status='operating', note='the Geant4 campaign this model is scaled from'),
        Source('saraf2', 'SARAF-II, d(40) 5 mA CW on Li/Be, NFS-like spectrum', Y.nfs(), 100 * n_nfs, None,
               status='commissioning (first beam slipped past 2024)',
               note='×100 NFS current, same spectrum and solid angle; CW: no TOF'),
        Source('ear2', 'CERN n_TOF EAR2 (1e7 n/cm²/pulse, Ø5 cm)', _trunc(ntof, 0.1),
               1e7 * 19.6 * above(ntof, 0.1) * 19290 / DAY, 19290 / DAY, 20.0, 0.1,
               status='operating', note='2026 campaign site; 0.22 Hz average'),
        Source('ear1', 'CERN n_TOF EAR1 (8e5 n/cm²/pulse, Ø5 cm)', _trunc(ntof, 0.1),
               8e5 * 19.6 * above(ntof, 0.1) * 19290 / DAY, 19290 / DAY, 185.0, 0.1, status='operating'),
        Source('backn', 'CSNS Back-n ES#1, 185 kW, Φ50 mm', _trunc(backn, 0.1),
               1.8e7 * 1.85 * 19.6 * above(backn, 0.1), 25.0, 55.0, 0.1,
               status='operating (185 kW, Mar 2026)', note='1.8e7 n/cm²/s per 100 kW, Tang et al. 2021'),
        Source('backn2', 'CSNS-II Back-n ES#1, 500 kW, Φ50 mm', _trunc(backn, 0.1),
               1.8e7 * 5.0 * 19.6 * above(backn, 0.1), 25.0, 55.0, 0.1, status='upgrade under way, no date'),
        Source('wnr', 'LANSCE WNR 30° (ICE), 5e6 n/cm²/s >1 MeV, 50 cm²', Y.per_decade(fr=Y.WNR),
               5e6 / 0.85 * a50, 1 / 1.8e-6, 20.0, 0.1, macro_duty=14e3 * 1.8e-6, status='operating',
               note='~14 000 micropulses/s, 1.8 µs apart inside macropulses (duty 2.5 %); 0.2 MeV wraps'),
        Source('gelina', 'JRC GELINA, 2.5e13 n/s, 10 m (isotropic bound), 50 cm²', _trunc(ntof, 0.1),
               2.5e13 / (4 * np.pi * 1e6) * above(ntof, 0.1) * a50, 800.0, 10.0, 0.1, status='operating'),
        Source('nelbe', 'HZDR nELBE, 2.5e4 n/cm²/s, 7 cm²', Y.watt(), 2.5e4 * 7.0, 102e3, 6.0, status='operating'),
        Source('medapp', 'FRM II MEDAPP fission beam, 3.2e8 n/cm²/s, 50 cm²', Y.watt(), 3.2e8 * a50, None,
               k_gamma=1.0, status='reactor offline since 2020, restart date open',
               note='γ dose ~0.4 of n dose: k_γ = 1 (γ singles = n singles), a guess'),
        Source('bham1', 'Birmingham ⁷Li(p,n) 2.6 MeV, 30 mA, unmoderated, cell at 1 m', Y.li7pn_thick(),
               4.8e12 / 1e4 * a50, None, k_gamma=0.3, status='operating since Dec 2023 (BNCT/fusion)',
               note='optimistic: an unshielded 3e13 n/s target 1 m away; 0° ×2 the 4π average (est.)'),
        Source('bham2', 'Birmingham ⁷Li(p,n), shielded, cell at 2 m', Y.li7pn_thick(),
               4.8e12 / 4e4 * a50, None, k_gamma=0.3, status='operating since Dec 2023',
               note='the realistic geometry: target in its shield, collimated port, 2 m'),
        Source('dd', 'D-D generator 3e11 n/s (Phoenix-class), cell at 1 m', Y.mono(),
               3e11 / (4 * np.pi * 1e4) * a50, None, status='commercial',
               note='D(d,γ)⁴He 23.8 MeV γ at ~1e-7 of D(d,n): pairs in the source, 1 m away'),
        Source('dd2', 'D-D generator 3e11 n/s, shielded, cell at 2.5 m', Y.mono(),
               3e11 / (4 * np.pi * 2.5e2 ** 2) * a50, None, status='commercial',
               note='a 4π source needs ~1 m of shield around it: 2.5 m is the realistic distance'),
        Source('dt', 'D-T generator 4.6e13 n/s (SHINE record), cell at 1 m', Y.mono(e0=14.1, width=0.2),
               4.6e13 / (4 * np.pi * 1e4) * a50, None, k_gamma=0.3, status='commercial (isotope production)',
               note='E_n 14.1 MeV: E* 31 MeV, outside the ATOMKI window'),
        Source('bepn', 'Cyclotron ⁹Be(p,n), 30 MeV 1 mA, unmoderated, cell at 1 m (est.)',
               Y.per_decade(fr={(0.1, 1.0): 0.30, (1.0, 10.0): 0.55, (10.0, 28.0): 0.15}), 1e13 / 1e4 * a50, None,
               k_gamma=0.3, status='BNCT cyclotrons (NeuCure class) exist; unmoderated port: ask',
               note='Y(0°) ≈ 1e13 n/sr/s and the spectrum split are guesses: no thick-target table found'),
        Source('lilit', 'SARAF-I LiLiT, 1.9 MeV p, ~1.5 mA, keV n, cell at 0.5 m', Y.maxwell_flux(),
               1e10 / 2500 * a50, None, k_gamma=0.3, status='Phase-I target; Phase-II beam not yet',
               note='3e10 n/s into the 60° cone (est. 1e10 n/sr/s)'),
        Source('franz', 'FRANZ Frankfurt, 2.0 MeV p, 10 mA (design), keV n, 0.5 m', Y.maxwell_flux(),
               7e10 / 2500 * a50, None, k_gamma=0.3, status='RFQ at 10 mA (2025); 2 MeV stage not yet'),
    ]


def _trunc(f, e0):
    g = Y.E_GRID
    return Y._norm(g, np.where(g >= e0, f, 0.0))


def nfs_n_per_s():
    t = pd.read_csv(ROOT / 'ganil_nfs' / 'out' / 'fold_table.csv')
    return float(np.trapezoid(t.n_per_s_MeV, t.E_n))


# --------------------------------------------------------------------------- #
def nfs_model(hw):
    """NFS Geant4 inputs, cached: per-bin per-class histograms at NFS weights, singles per
    neutron vs E_n per arm, and the accidental pass fraction per bin."""
    CACHE.mkdir(exist_ok=True)
    p = CACHE / f'nfs_{hw.replace(" ", "_")}.pkl'
    if p.exists():
        return pickle.loads(p.read_bytes())
    R.BEAM_FACT = True                     # the headline (factorised correlated term)
    bins, E, beam = R.build(hw)
    hm = {}
    for kind in ('X17', 'IPC', 'beam', 'acc', 'cosmic'):
        hm[kind] = np.zeros((NB, len(R.M_BINS) - 1))
        ht = np.zeros((NB, len(R.TH_BINS) - 1))
        for k in range(NB):
            e = E[(E.kind == kind) & (E.bin == k)]
            hm[kind][k] = np.histogram(e.m, R.M_BINS, weights=e.w)[0]
            ht[k] = np.histogram(e.th, R.TH_BINS, weights=e.w)[0]
        hm[kind + '_th'] = ht

    zb = R.load('N4_beam_force' + R.HW[hw], R.SEL_BEAM)
    fold = pd.read_csv(ROOT / 'ganil_nfs' / 'out' / 'fold_table.csv')
    n_per_s = float(np.trapezoid(fold.n_per_s_MeV, fold.E_n))
    per_s = n_per_s / int(zb['cnt_n_generated'])
    w = zb['sg_w'] * per_s                                     # singles/s per MC single
    # singles per neutron, per arm, by parent E_n
    j = np.digitize(zb['sg_En'], PS_EDGES) - 1
    neut = np.array([np.trapezoid(fold.n_per_s_MeV[(fold.E_n >= a) & (fold.E_n <= b)],
                                  fold.E_n[(fold.E_n >= a) & (fold.E_n <= b)])
                     for a, b in zip(PS_EDGES[:-1], PS_EDGES[1:])])
    # prompt singles (within 100 ns of the neutron reaching the detector) arrive with their
    # neutron; delayed ones (captures, activation: ms-s) are spread uniformly in time
    prompt = zb['sg_t_sipm'].astype(float) - R.tof_s(zb['sg_En'], 1.2) * 1e9 < 100.0
    ps = np.zeros((2, 4, len(PS_EDGES) - 1))
    for i, sel in enumerate((prompt, ~prompt)):
        for a in range(4):
            for jj in range(len(PS_EDGES) - 1):
                ps[i, a, jj] = w[sel & (j == jj) & (zb['sg_arm'] == a)].sum() / max(neut[jj], 1e-30)
    ps_avg = np.array([[w[sel & (zb['sg_arm'] == a)].sum() / neut.sum() for a in range(4)]
                       for sel in (prompt, ~prompt)])
    model = dict(bins=bins, beam=beam, h=hm, ps=ps, ps_avg=ps_avg, cap_nfs=bins.captures_per_s.values,
                 n_hi_nfs=float(np.trapezoid(fold.n_per_s_MeV[fold.E_n > 8.5], fold.E_n[fold.E_n > 8.5])),
                 singles_nfs=float(w.sum()), cos_frac=np.array([(R.tof_s(b.lo) - R.tof_s(b.hi)) * R.REP_HZ
                                                                for b in bins.itertuples()]))
    p.write_bytes(pickle.dumps(model))
    return model


PS_MODE = 'geant'      # 'geant': singles per neutron vs E_n from N4; 'flat': the NFS spectrum average


def source_rates(src, M):
    """captures/s per analysis bin; prompt singles/s per arm per bin (by parent E_n);
    delayed singles/s per arm (uniform in time); neutrons/s above 8.5 MeV.

    PS_MODE 'flat' gives every neutron the NFS-average singles probability (4e-5, set
    by its > 10 MeV neutrons): a pessimistic bound for soft sources, whose own
    singles the N4 sample cannot measure (few MC neutrons below 4 MeV)."""
    g = Y.E_GRID
    f = src.spectrum
    cpn = Y.captures_per_neutron(g)
    cap = np.zeros(NB)
    edges = np.array([0.0] + R.EDGES[1:-1] + [99.0])              # <0.2 MeV into bin 0, >25 into bin 8
    for k in range(NB):
        m = (g >= edges[k]) & (g < edges[k + 1])
        cap[k] = src.n_cell * np.trapezoid(f[m] * cpn[m], g[m])
    ps_edges = np.concatenate([[0.0], PS_EDGES[1:-1], [99.0]])      # <0.1 MeV uses the 0.1-0.2 value
    neut = np.array([src.n_cell * np.trapezoid(f[(g >= a) & (g < b)], g[(g >= a) & (g < b)])
                     for a, b in zip(ps_edges[:-1], ps_edges[1:])])
    ps = M['ps']
    if PS_MODE == 'flat':
        ps = np.repeat(M['ps_avg'][:, :, None], ps.shape[2], 2)
    r_p = np.zeros((4, NB))
    for jj in range(len(neut)):
        r_p[:, PS_TO_K[jj]] += neut[jj] * ps[0, :, jj]
    r_d = (ps[1] * neut[None, :]).sum(1)
    g_ = 1 + src.k_gamma
    return cap, r_p * g_, r_d * g_, src.n_cell * Y.window_fraction(g, f, 8.5, 99.0)


def _pairs(r):
    return sum(r[a] * r[b] for a in range(4) for b in range(a + 1, 4))


def _windows(L):
    """arrival window [t0, t1] (s after the pulse) of each analysis bin over L metres."""
    return np.array([(R.tof_s(R.EDGES[k + 1], L), R.tof_s(R.EDGES[k], L)) for k in range(NB)])


def _profile(src, r_p, r_d, n=6000):
    """per-arm singles rate vs time within one period (wrap-around included).  Delayed
    singles (ms-s) are flat; prompt ones arrive with their neutron's bin window."""
    win = _windows(src.flight_m)
    per = 1.0 / src.rep_hz
    span = per if per < win[0, 1] else win[0, 1]                  # whole period if the slowest bin wraps
    t = (np.arange(n) + 0.5) * span / n
    rho = np.repeat(r_d[:, None], n, 1).astype(float)
    inwin = np.zeros((NB, n), bool)
    for k, (t0, t1) in enumerate(win):
        dt = t1 - t0
        if per < t1:                                              # wraps: fold the window into one period
            m = np.zeros(n, bool)
            for off in np.arange(np.floor(t0 / per), np.ceil(t1 / per) + 1) * per:
                m |= (t + off >= t0) & (t + off < t1)
        else:
            m = (t >= t0) & (t < t1)
        inwin[k] = m
        rho[:, m] += r_p[:, k:k + 1] / (src.rep_hz * dt)
    return t, span / n, rho, inwin, span


def _pairing(src, cap, r_p, r_d):
    """accidental pairing per analysis bin, per day, before cuts; the mean per-arm rate seen
    while each bin is open; and the fraction of time each bin is open."""
    if src.tof:
        md = src.macro_duty
        t, dt, rho, inwin, span = _profile(src, r_p / md, r_d)       # rates inside a macropulse
        pr = sum(rho[a] * rho[b] for a in range(4) for b in range(a + 1, 4))
        P = np.array([pr[inwin[k]].sum() * dt for k in range(NB)]) * src.rep_hz * md * 2 * R.COINC_NS * 1e-9 * DAY
        duty = np.array([inwin[k].sum() * dt for k in range(NB)]) * src.rep_hz * md
        r_inst = np.array([rho[:, inwin[k]].mean(1) if inwin[k].any() else r_d for k in range(NB)]).T
    else:
        duty = np.ones(NB)
        r_tot = r_p.sum(1) + r_d
        r_inst = np.repeat(r_tot[:, None], NB, 1)
        share = cap / (cap.sum() or 1.0)                            # DC: no E_n tag, split like the signal
        P = _pairs(r_tot) * 2 * R.COINC_NS * 1e-9 * DAY * share
    return P, r_inst, duty


def _random_triggers(src, r_p, r_d):
    """two-arm random hardware coincidences per second (time-averaged)."""
    if not src.tof:
        return _pairs(r_p.sum(1) + r_d) * 2 * TAU_HW
    md = src.macro_duty
    t, dt, rho, inwin, span = _profile(src, r_p / md, r_d)
    pr = sum(rho[a] * rho[b] for a in range(4) for b in range(a + 1, 4))
    return (pr.sum() * dt * src.rep_hz * md + _pairs(r_d) * max(0.0, 1 - span * src.rep_hz * md)) * 2 * TAU_HW


def calibrate(M):
    """The NFS row of this model: its pairing per bin (to calibrate the accidental pass
    fraction) and its prompt singles (to scale the correlated trigger rate)."""
    if 'P_nfs' not in M:
        src = sources()[0]
        cap, r_p, r_d, _ = source_rates(src, M)
        M['P_nfs'] = _pairing(src, cap, r_p, r_d)[0]
        M['prompt_nfs'] = float(r_p.sum())
    return M


def scaled(src, M, s, hw, extras=True):
    """Per-bin per-class weights (relative to NFS) and the exposure factor, at throttle s."""
    calibrate(M)
    cap, r_p, r_d, n_hi = source_rates(src, M)
    cap, r_p, r_d, n_hi = cap * s, r_p * s, r_d * s, n_hi * s
    with np.errstate(divide='ignore', invalid='ignore'):
        c_sig = np.where(M['cap_nfs'] > 0, cap / M['cap_nfs'], 0.0)
        P, r_inst, duty = _pairing(src, cap, r_p, r_d)
        c_acc = np.where(M['P_nfs'] > 0, P / M['P_nfs'], 0.0)       # × NFS pass fraction, bin by bin
    r_all = r_p.sum() + r_d.sum()
    corr = M['beam']['trig2_per_s'] * r_p.sum() / M['prompt_nfs']
    if src.tof:
        cos = duty / np.where(M['cos_frac'] > 0, M['cos_frac'], 1)
        if 1 / src.rep_hz < T_MM:                                    # bunch period inside the MM memory
            occ = np.full(NB, r_all / 4 * T_MM)
        else:
            occ = r_inst.mean(0) * T_MM
        rand = _random_triggers(src, r_p, r_d)
        if 1 / src.rep_hz > R.TAU_DAQ:                               # one readout per pulse at most
            live = 1 / (1 + (rand + corr) / src.rep_hz)
        else:
            live = 1 / (1 + (rand + corr) * R.TAU_DAQ)
    else:
        cos = (cap / (cap.sum() or 1.0)) / np.where(M['cos_frac'] > 0, M['cos_frac'], 1)
        occ = np.full(NB, r_all / 4 * T_MM)
        rand = _pairs(r_inst[:, 0]) * 2 * TAU_HW
        live = 1 / (1 + (rand + corr) * R.TAU_DAQ)
    if not extras:                                                   # the NFS analysis as published
        occ = np.zeros(NB)
        live = 1 / (1 + corr * R.TAU_DAQ)
    c_beam = n_hi / M['n_hi_nfs']
    expo = live * np.exp(-2 * occ)
    return dict(sig=c_sig, acc=c_acc, beam=np.full(NB, c_beam), cos=cos, expo=expo, live=live,
                occ=float(np.max(occ)), singles=float(r_all), cap=cap)


def z2(src, M, sc, rho, days, soft_only):
    h = M['h']
    sfx = '' if src.tof else '_th'
    mult_x = sc['sig'] * (np.isin(np.arange(NB), SOFT) if soft_only else 1.0)
    S = h['X17' + sfx] * (mult_x * rho / R.RHO_REF)[:, None]
    B = (h['IPC' + sfx] * sc['sig'][:, None] + h['acc' + sfx] * sc['acc'][:, None]
         + h['beam' + sfx] * sc['beam'][:, None] + h['cosmic' + sfx] * sc['cos'][:, None])
    ex = (sc['expo'] * days)[:, None]
    S, B = S * ex, B * ex
    if src.tof:
        return sum(R.z2_asimov(S[k], B[k]) for k in range(NB))
    return R.z2_asimov(S.sum(0), B.sum(0))


def rho3(src, M, sc, days, soft_only):
    lo, hi = 1e-7, 1e3
    if z2(src, M, sc, hi, days, soft_only) < 9:
        return np.inf
    for _ in range(60):
        mid = np.sqrt(lo * hi)
        lo, hi = (mid, hi) if z2(src, M, sc, mid, days, soft_only) < 9 else (lo, mid)
    return np.sqrt(lo * hi)


def best(src, M, hw, days, soft_only, extras=True, grid=np.geomspace(1e-6, 1.0, 49)):
    rows = []
    for s in grid:
        sc = scaled(src, M, s, hw, extras)
        rows.append((rho3(src, M, sc, days, soft_only), s, sc))
    r, s, sc = min(rows, key=lambda x: x[0])
    return r, s, sc, rows


def floor(src, M, hw, days, soft_only):
    """IPC + cosmics only, full intensity, no dead time or occupancy: the statistics floor."""
    sc = scaled(src, M, 1.0, hw, extras=False)
    sc['acc'] = np.zeros(NB)
    sc['beam'] = np.zeros(NB)
    sc['expo'] = np.ones(NB)
    return rho3(src, M, sc, days, soft_only)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true', help='NFS only, as published (no occupancy / random triggers)')
    ap.add_argument('--days', type=float, nargs='+', default=[14.0, 50.0])
    ap.add_argument('--figures', action='store_true', help='redraw the figures from the CSVs')
    ap.add_argument('--only', nargs='+', help='recompute these source keys and merge into the existing CSVs')
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    srcs = sources()
    all_srcs = srcs
    if a.only:
        srcs = [x for x in srcs if x.key in a.only]
    if a.figures:
        figure(pd.read_csv(OUT / 'fast_reach.csv'), pd.read_csv(OUT / 'fast_throttle_curves.csv'), srcs)
        return
    if a.check:
        for hw in R.HW:
            M = nfs_model(hw)
            src = srcs[0]
            sc = scaled(src, M, 1.0, hw, extras=False)
            print(hw, 'live', round(sc['live'], 4), 'ρ3σ 14 d: all E*', f"{rho3(src, M, sc, 14, False):.4g}",
                  ' E*≤22', f"{rho3(src, M, sc, 14, True):.4g}",
                  '(nfs_reach: big plastics 3.3e-3 / 0.031; as built 8.5e-3 / 0.16)')
        return
    global PS_MODE
    rows, curves = [], []
    for hw in R.HW:
        M = nfs_model(hw)
        for mode in ('geant', 'flat'):
            PS_MODE = mode
            for src in srcs:
                cap, r_p, r_d, _ = source_rates(src, M)
                for days in a.days:
                    for soft in (False, True):
                        r, s, sc, grid = best(src, M, hw, days, soft)
                        fl = floor(src, M, hw, days, soft) if mode == 'geant' else np.nan
                        ipc_k = cap * Y.alpha(np.array(R.NODES)) * DAY
                        rows.append(dict(key=src.key, source=src.label, hw=hw, days=days, singles_model=mode,
                                         signal='E* ≤ 22 MeV' if soft else 'all E*',
                                         analysis='m_ee | E_n' if src.tof else 'θ, no TOF',
                                         rho3=r, vs_ATOMKI=r / R.RHO_REF, throttle=s, rho3_floor=fl,
                                         n_cell_full=src.n_cell, ipc_per_day_full=float(ipc_k.sum()),
                                         ipc_soft_per_day_full=float(ipc_k[SOFT].sum()),
                                         singles_full=float(r_p.sum() + r_d.sum()), singles_at_best=sc['singles'],
                                         live=sc['live'], occ=sc['occ'], status=src.status, note=src.note))
                        if days == 50 and hw == 'big plastics':
                            curves += [dict(key=src.key, singles_model=mode, signal='E* ≤ 22' if soft else 'all E*',
                                            throttle=g[1], n_cell=src.n_cell * g[1], rho3=g[0]) for g in grid]
                print(f'{hw:13s} {mode:6s} {src.key:8s} done', flush=True)
    PS_MODE = 'geant'
    t, cv = pd.DataFrame(rows), pd.DataFrame(curves)
    if a.only:
        old = pd.read_csv(OUT / 'fast_reach.csv')
        oc = pd.read_csv(OUT / 'fast_throttle_curves.csv')
        t = pd.concat([old[~old.key.isin(a.only)], t], ignore_index=True)
        cv = pd.concat([oc[~oc.key.isin(a.only)], cv], ignore_index=True)
        order = {x.key: i for i, x in enumerate(all_srcs)}
        t = t.sort_values(['hw', 'singles_model', 'key'], key=lambda c: c.map(order) if c.name == 'key' else c,
                          kind='stable')
    t.to_csv(OUT / 'fast_reach.csv', index=False, float_format='%.4g')
    cv.to_csv(OUT / 'fast_throttle_curves.csv', index=False, float_format='%.4g')
    curves = cv
    pd.set_option('display.width', 250)
    pd.set_option('display.max_colwidth', 60)
    show = t[(t.hw == 'big plastics') & (t.days == 50)]
    print(show.pivot_table(index='key', columns=['singles_model', 'signal'], values='rho3', sort=False).to_string())
    figure(t, curves, all_srcs)


def figure(t, curves, srcs):
    import matplotlib.pyplot as plt
    sys.path.insert(0, str(ROOT / 'ill'))
    import figstyle as fs
    fs.use()
    short = dict(nfs='GANIL NFS (reference)', saraf2='SARAF-II d(40) 5 mA', ear2='n_TOF EAR2', ear1='n_TOF EAR1',
                 backn='CSNS Back-n 185 kW', backn2='CSNS-II Back-n 500 kW', wnr='LANSCE WNR 30°', gelina='JRC GELINA',
                 nelbe='HZDR nELBE', medapp='FRM II MEDAPP fission beam', bham1='Birmingham ⁷Li(p,n), 1 m',
                 bham2='Birmingham ⁷Li(p,n), shielded, 2 m', dd='D-D 3e11 n/s, 1 m', dd2='D-D 3e11 n/s, shielded, 2.5 m',
                 dt='D-T 4.6e13 n/s (no window signal)', bepn='Cyclotron ⁹Be(p,n) (est.)', lilit='SARAF-I LiLiT',
                 franz='FRANZ (design)')
    lab = {s.key: short.get(s.key, s.label) for s in srcs}
    d = t[(t.hw == 'big plastics') & (t.days == 50) & (t.signal == 'E* ≤ 22 MeV')]
    p = d.pivot_table(index='key', columns='singles_model', values='rho3', sort=False)
    p['floor'] = d[d.singles_model == 'geant'].set_index('key').rho3_floor
    p = p.sort_values('geant')
    fig, ax = plt.subplots(figsize=(8.4, 5.6))
    y = np.arange(len(p))
    big = 1.0
    for col, c, mk, lb in (('floor', fs.MUTED, '|', 'IPC + cosmics only (floor)'),
                           ('geant', fs.ACCENT, 'o', 'singles per n vs E_n (Geant4 N4)'),
                           ('flat', fs.COPPER, 's', 'singles per n = NFS average (pessimistic)')):
        v = np.clip(p[col].replace(np.inf, big).values, 1.2e-4, big)
        ax.scatter(v, y, color=c, marker=mk, s=36 if mk == '|' else 26, zorder=3, label=lb)
    for i, (lo, hi) in enumerate(zip(np.clip(p['geant'].replace(np.inf, big), 1.2e-4, big),
                                     np.clip(p['flat'].replace(np.inf, big), 1.2e-4, big))):
        ax.plot([lo, hi], [i, i], color=fs.LINE, lw=2.5, zorder=1)
    ax.set_yticks(y, [lab[k] for k in p.index], fontsize=8)
    ax.set_xscale('log')
    ax.set_xlim(1e-4, 1.2)
    ax.axvline(R.RHO_REF, color=fs.TRACK, lw=1.0)
    ax.text(R.RHO_REF * 1.08, len(p) - 0.6, 'ATOMKI ⁴He\n1.5e-3', color=fs.TRACK, fontsize=8, va='top')
    ax.set_xlabel('X17/IPC at 3σ, 50 d, E* ≤ 22 MeV, big plastics, best throttle (1 = none)')
    ax.legend(loc='lower right', fontsize=8, frameon=False)
    fs.title(ax, 'Fast sources scaled from the NFS Geant4 analysis',
             'X17/IPC reach at 3σ in 50 days; the beam is throttled to its best rate')
    fs.save(fig, OUT / 'fast_reach_fig', data=d)

    fig, ax = plt.subplots(figsize=fs.FIG)
    c = curves[(curves.signal == 'E* ≤ 22') & (curves.singles_model == 'geant')]
    for k, col in zip(['nfs', 'backn', 'medapp', 'bham1', 'dd', 'ear2'],
                      [fs.MUTED, fs.COPPER, fs.ACCENT, fs.TRACK, '#0072B2', '#009E73']):
        q = c[c.key == k]
        ax.plot(q.n_cell, np.clip(q.rho3.replace(np.inf, 10), 1e-4, 10), color=col, lw=1.5, label=lab[k])
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_ylim(5e-4, 5)
    ax.axhline(R.RHO_REF, color=fs.TRACK, lw=0.8, ls=':')
    ax.set_xlabel('neutrons/s through the cell (throttled)')
    ax.set_ylabel('X17/IPC at 3σ, 50 d (E* ≤ 22 MeV)')
    ax.legend(fontsize=8, frameon=False)
    fs.title(ax, 'Each source has a best rate', 'below it statistics, above it accidentals, occupancy and dead time')
    fs.save(fig, OUT / 'fast_throttle_fig', data=c)


if __name__ == '__main__':
    main()
