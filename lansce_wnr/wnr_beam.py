#!/usr/bin/env python3
"""
wnr_beam.py -- LANSCE WNR Target 4 as an X17 source: the beam per flight-path angle, its time
structure, and the X17 reach with time of flight, re-weighted from the NFS and soft-beam Geant4 runs.

    python lansce_wnr/wnr_beam.py               # -> lansce_wnr/out/wnr_*.csv/png
    python lansce_wnr/wnr_beam.py --check       # the engine on the NFS beam (must match survey_fast's NFS row)

The beam (FACILITY.md §2):
  Y(E, angle)   n/proton/MeV/sr from the bare W target, digitised from Nowicki, Wender & Mocko,
                Physics Procedia 90 (2017) 374, Fig. 2 (15/30/60/90°, 0.1-800 MeV); below 0.1 MeV
                Y ∝ √E (an assumption: only wrap-around and singles use it).
  time          40 macropulses/s × 625 µs (duty 2.5 %), 7×10⁸ p per micropulse, micropulses 1.8 µs
                apart (13 889/s, 1.56 µA); 3.6 and 7.2 µs on request (fewer protons, same per pulse).
                The 100 Hz upgrade option multiplies the macropulse rate by 2.5.
  the cell      the NFS geometry (30 bar × 40 cm, Ø8 cm spot = 50 cm²) at L metres from the target.

The apparatus response (all per neutron entering the Ø8 cm spot, per arm, vs E_n):
  ok singles, legs, two-arm triggers, two-arm "ok" pairs (correlated)
      E_n < 8.5 MeV: the N5 soft run (log-flat 1 keV-20 MeV, forced, survey/soft_sim/sel);
      8.5-45 MeV:    the N4 forced NFS run (survey_fast.nfs_model's table; ganil_nfs/sim/sel_beam);
      > 45 MeV:      the 25-45 MeV value × K_HI (no Geant4 above 45 MeV: an assumption, varied).
  prompt / delayed: a single within 100 ns of the neutron's arrival travels with it in time;
      later ones (captures, activation) are spread uniformly over all time.

Per configuration (angle, L, micropulse spacing T, macropulse rate), everything is folded
into one micropulse period u ∈ [L/c, L/c + T):
  bins        the NFS E_n bins (0.2-25 MeV) as time windows; a bin is cut at the next γ flash
              (u = T + L/c): below E_wrap the neutrons belong to the next frame. Their captures
              stay as IPC-like background in the bin they fold into; their X17 is lost.
  X17, IPC    the NFS signal tables per bin × captures here / captures at NFS
  accidental  the pairing integral ∫ Σ_{a<b} ρ_a ρ_b du over each bin's window (ρ = ok singles
              rate inside a macropulse, prompt folded + delayed flat), × micropulses/s × 2δ,
              divided by the same integral for NFS's own beam: × the NFS histogram of that bin
              (the NFS vertex + E_sum pass fraction per bin)
  correlated  two-arm ok pairs per neutron × the NFS pooled vertex and E_sum pass fractions
              (the factorised NFS headline), placed in the bin their neutron's arrival folds into;
              the m_ee shape of that bin from NFS
  cosmics     × (bin window × micropulses/s) / NFS's open fraction of that bin
  trigger     a time-of-flight gate: only two-arm triggers inside the analysed windows read out
  DAQ         non-paralysable τ = 298 µs, but triggers come only during macropulses: the live
              fraction is the renewal count in one 625 µs macropulse at the in-macropulse rate
  occupancy   Micromegas: ok singles per arm in the 1 µs before each instant, averaged over a bin
              window; exposure × exp(−2·occ) (the survey convention)

Analysis: m_ee | E_n (Asimov, summed over bins); "E* ≤ 22": X17 only from E_n ≤ 2.75 MeV, the
trigger gated to those windows; "all E*": X17/IPC constant, the gate covers 0.2-25 MeV.
Throttle s ≤ 1 (collimator/current) scanned for the best reach.  Not modelled: the γ flash
(gated, but its Micromegas occupancy is not), room and beam-dump return, the source γ.
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
ROOT = HERE.parent
OUT = HERE / 'out'
sys.path.insert(0, str(ROOT / 'survey'))
sys.path.insert(0, str(ROOT / 'ganil_nfs' / 'sim'))
sys.path.insert(0, str(ROOT / 'ill'))
import survey_fast as SF                                      # noqa: E402
import survey_yield as Y                                      # noqa: E402
import nfs_reach as R                                         # noqa: E402

DAY = 86400.0
C_M_NS = 0.299792458
NB = SF.NB
SOFT = SF.SOFT
SOFT_SEL = ROOT / 'survey' / 'soft_sim' / 'sel'
N5_GEN = (1e-3, 20.0)
K_HI = 1.0                      # singles/pairs per neutron above 45 MeV, × the 25-45 MeV value
COS_VETO = 1.0                  # cosmics left after a veto (1 = none, the headline)
E_FINE = np.geomspace(1e-3, 800.0, 8000)
AREA = 50.0                     # cm², the Ø8 cm NFS spot
P_PER_UP = 7e8                  # protons per micropulse (LANL time-of-flight page)
MACRO_S = 625e-6
MACRO_HZ = 40.0
DU_NS = 2.0                     # time-profile resolution

# Nowicki, Wender & Mocko 2017, Fig. 2: Y [n/p/MeV/sr] read at these energies (MeV)
Y_E = [0.1, 0.2, 0.3, 0.5, 1, 2, 3, 5, 10, 20, 30, 50, 100, 200, 300, 400, 500, 600, 700, 780]
Y_TAB = {
    15: [0.125, 0.135, 0.14, 0.14, 0.115, 0.075, 0.045, 0.022, 0.009, 0.0021, 0.0013, 0.00095, 6e-4, 4e-4,
         3e-4, 2e-4, 1e-4, 1.4e-4, 1e-4, 1.5e-5],
    30: [0.175, 0.185, 0.19, 0.185, 0.15, 0.09, 0.06, 0.027, 0.010, 0.0022, 0.0014, 0.0010, 6e-4, 3.5e-4,
         1.7e-4, 1e-4, 8e-5, 2.2e-5, 0, 0],
    60: [0.245, 0.255, 0.26, 0.25, 0.19, 0.105, 0.07, 0.030, 0.011, 0.0022, 0.0013, 0.0009, 5e-4, 1.5e-4,
         4e-5, 0, 0, 0, 0, 0],
    90: [0.27, 0.27, 0.27, 0.25, 0.20, 0.11, 0.075, 0.030, 0.011, 0.0020, 0.0011, 0.0005, 2.2e-4, 3e-5,
         0, 0, 0, 0, 0, 0],
}
# the 60° curve ends at ~380 MeV, 90° at ~230 MeV, 30° at ~650 MeV (Fig. 2)
Y_END = {15: 780.0, 30: 650.0, 60: 380.0, 90: 230.0}


def yield_per_p(e, ang):
    """n / proton / MeV / sr at angle ang (log-log interpolation of Fig. 2)."""
    e = np.asarray(e, float)
    xs, ys = np.log(Y_E), np.array(Y_TAB[ang], float)
    good = ys > 0
    last = float(np.max(np.array(Y_E)[good]))
    lx = np.log(np.clip(e, Y_E[0], None))
    y = np.exp(np.interp(lx, xs[good], np.log(ys[good])))
    # fall from the last tabulated point to 1e-5 at the curve's end
    tail = (e > last) & (e < Y_END[ang])
    with np.errstate(divide='ignore', invalid='ignore'):
        y = np.where(tail, ys[good][-1] * (1e-5 / ys[good][-1]) ** ((np.log(e) - np.log(last)) /
                                                                   (np.log(Y_END[ang]) - np.log(last))), y)
    y = np.where(e >= Y_END[ang], 0.0, y)
    return np.where(e < Y_E[0], Y_TAB[ang][0] * np.sqrt(np.clip(e, 0, None) / Y_E[0]), y)


# --------------------------------------------------------------------------- #
@dataclass
class Config:
    key: str
    ang: int
    L: float                       # m, target to cell centre
    T_us: float = 1.8              # micropulse spacing
    macro_hz: float = MACRO_HZ
    area: float = AREA
    label: str = ''

    @property
    def up_per_s(self):
        return self.macro_hz * MACRO_S / (self.T_us * 1e-6)

    @property
    def duty(self):
        return self.macro_hz * MACRO_S

    @property
    def p_per_s(self):
        return self.up_per_s * P_PER_UP

    def n_spec(self, e=E_FINE):
        """neutrons/s/MeV through the spot (time-averaged)."""
        return yield_per_p(e, self.ang) * self.p_per_s * self.area / (self.L * 100.0) ** 2


def tof_ns(e, L):
    return R.tof_s(np.asarray(e, float), L) * 1e9


def e_of_tof(t_ns, L):
    """kinetic energy [MeV] for a time of flight t over L (relativistic)."""
    b = L / (np.asarray(t_ns, float) * C_M_NS)
    b = np.clip(b, 0, 0.999999)
    return 939.565 * (1 / np.sqrt(1 - b ** 2) - 1)


# --------------------------------------------------------------------------- #
# response per neutron vs E_n, per arm
def _n5(hw):
    z = R.load('N5_beam_soft' + R.HW[hw], SOFT_SEL)
    if z is None:
        sys.exit(f'missing {SOFT_SEL}/N5_beam_soft{R.HW[hw]}_sel.npz (survey/soft_sim/fetch_sel.sh)')
    return z


def response(hw, M):
    """dict of per-neutron tables on common edges: ok prompt/delayed, legs prompt/delayed [4, nb],
    trig2 and correlated-selected [nb] (per neutron entering the spot)."""
    z = _n5(hw)
    e5 = np.concatenate([np.geomspace(1e-3, 0.2, 7), [0.75, 1.5, 2.75, 4.25, 6.0, 8.5]])
    e4 = np.array(SF.PS_EDGES[7:])                                   # 8.5 12 17 25 45
    edges = np.concatenate([e5, e4[1:], [1000.0]])
    nb5, nb = len(e5) - 1, len(edges) - 1
    ngen = float(z['cnt_n_generated'])
    lnr = np.log(N5_GEN[1] / N5_GEN[0])
    n5 = ngen * np.log(e5[1:] / e5[:-1]) / lnr                       # neutrons generated per bin

    def per_n(e, w, arm=None, t=None):
        j = np.digitize(e, e5) - 1
        ok = (j >= 0) & (j < nb5)
        if arm is None:
            return np.bincount(j[ok], w[ok], nb5) / n5
        out = np.zeros((2, 4, nb5))
        pr = (t - tof_ns(e, 1.2)) < 100.0
        for i, sel in enumerate((pr, ~pr)):
            for a in range(4):
                m = ok & sel & (arm == a)
                out[i, a] = np.bincount(j[m], w[m], nb5) / n5
        return out

    ok5 = per_n(z['sg_En'], z['sg_w'], z['sg_arm'], z['sg_t_sipm'])
    lg5 = per_n(z['lg_En'], z['lg_w'], z['lg_arm'], z['lg_t'])
    tr5 = per_n(z['tr_En'], z['tr_w'])
    pr5 = per_n(z['En'], z['w'])
    # N4 above 8.5 MeV (NFS forced run, the survey's table)
    ok4 = M['ps'][:, :, 7:]                                          # bins 8.5-12, 12-17, 17-25, 25-45
    zb = R.load('N4_beam_force' + R.HW[hw], R.SEL_BEAM)
    fold = pd.read_csv(ROOT / 'ganil_nfs' / 'out' / 'fold_table.csv')
    nps = float(np.trapezoid(fold.n_per_s_MeV, fold.E_n))
    frac4 = np.array([np.trapezoid(fold.n_per_s_MeV[(fold.E_n >= a) & (fold.E_n <= b)],
                                   fold.E_n[(fold.E_n >= a) & (fold.E_n <= b)]) for a, b in zip(e4[:-1], e4[1:])]) / nps
    n4 = float(zb['cnt_n_generated']) * frac4
    pr4 = np.histogram(zb['En'], e4, weights=zb['w'])[0] / n4
    # legs and triggers above 8.5 MeV: N5's 4.25-8.5 MeV ratio to ok singles (N4 has no per-E table)
    r_lg = lg5[:, :, -1].sum() / max(ok5[:, :, -1].sum(), 1e-30)
    ok4_tot = ok4.sum((0, 1))
    tr4 = M['beam']['trig2_per_s'] / M['beam']['ok2_per_s'] * pr4      # NFS: triggers per ok pair
    hi = lambda x: x[..., -1:] * K_HI                                  # noqa: E731  > 45 MeV
    ok = np.concatenate([ok5, ok4, hi(ok4)], axis=2)
    lg = np.concatenate([lg5, ok4 * r_lg, hi(ok4 * r_lg)], axis=2)
    tr = np.concatenate([tr5, tr4, hi(tr4)])
    pr = np.concatenate([pr5, pr4, hi(pr4)])
    fvfe = M['beam']['f_vertex'] * M['beam']['f_esum']
    # per-row tables with their own delays (correlated pairs and triggers): (E, per-neutron weight
    # in its edges-bin, delay after the neutron reaches the detector [ns], edges-bin index)
    jb = lambda e: np.clip(np.digitize(e, edges) - 1, 0, nb - 1)    # noqa: E731

    def rows(e, w, t, src):
        e, w, t = (np.asarray(x, float) for x in (e, w, t))
        d = t - tof_ns(e, 1.2)
        j = jb(e)
        if src == 5:
            m = e < 8.5
            norm = n5[np.clip(np.digitize(e, e5) - 1, 0, nb5 - 1)]
        else:
            m = (e >= 8.5) & (e < 45.0)
            norm = n4[np.clip(np.digitize(e, e4) - 1, 0, len(n4) - 1)]
        out = [e[m], w[m] / norm[m], d[m], j[m]]
        if src == 4:                                                   # > 45 MeV: the 25-45 MeV rows
            h = (e >= 25.0) & (e < 45.0)
            out = [np.concatenate([out[0], np.full(h.sum(), 100.0)]),
                   np.concatenate([out[1], w[h] / norm[h] * K_HI]),
                   np.concatenate([out[2], d[h]]), np.concatenate([out[3], np.full(h.sum(), nb - 1)])]
        return out

    t4 = np.fmin(zb['t_sipm1'], zb['t_sipm2'])
    c5 = rows(z['En'], z['w'], np.fmin(z['t_sipm1'], z['t_sipm2']), 5)
    c4 = rows(zb['En'], zb['w'], t4, 4)
    corr_rows = [np.concatenate([a, b]) for a, b in zip(c5, c4)]
    corr_rows[1] = corr_rows[1] * fvfe
    g5 = rows(z['tr_En'], z['tr_w'], z['tr_t'], 5)
    g4 = rows(zb['En'], zb['w'] * M['beam']['trig2_per_s'] / M['beam']['ok2_per_s'], t4, 4)
    trig_rows = [np.concatenate([a, b]) for a, b in zip(g5, g4)]
    return dict(edges=edges, ok=ok, lg=lg, trig=tr, corr=pr * fvfe, ok4_tot=ok4_tot, nb=nb,
                corr_rows=corr_rows, trig_rows=trig_rows)


def response_nfs(M):
    """the survey's own NFS response (N4 singles table), for the calibration run."""
    edges = np.append(SF.PS_EDGES[:-1], 1000.0)
    edges[0] = 1e-3
    ok = M['ps']
    zero = np.zeros(ok.shape[2])
    return dict(edges=edges, ok=ok, lg=ok * 0, trig=zero, corr=zero, nb=ok.shape[2])


def per_fine(tab, e=E_FINE):
    j = np.clip(np.digitize(e, tab['edges']) - 1, 0, tab['nb'] - 1)
    return {k: (v[..., j] if k in ('ok', 'lg', 'trig', 'corr') else v) for k, v in tab.items()
            if not k.endswith('_rows')}


# --------------------------------------------------------------------------- #
@dataclass
class Beam:
    """a configuration folded into one micropulse period."""
    e: np.ndarray
    n: np.ndarray               # neutrons/s in each fine-E cell (time-averaged)
    L: float
    T_ns: float
    up_per_s: float
    duty: float


def beam_of(cfg):
    e = E_FINE
    de = np.gradient(e)
    return Beam(e, cfg.n_spec(e) * de, cfg.L, cfg.T_us * 1e3, cfg.up_per_s, cfg.duty)


def beam_nfs():
    e = E_FINE
    fold = pd.read_csv(ROOT / 'ganil_nfs' / 'out' / 'fold_table.csv')
    f = np.interp(e, fold.E_n, fold.n_per_s_MeV, left=0, right=0)
    return Beam(e, f * np.gradient(e), R.FLIGHT_M, 1e9 / R.REP_HZ, R.REP_HZ, 1.0)


def windows(b):
    """per analysis bin: [u0, u1] in ns within the period representation [L/c, L/c+T)."""
    tg = b.L / C_M_NS
    u_end = tg + b.T_ns
    w = []
    for k in range(NB):
        t0 = tof_ns(R.EDGES[k + 1], b.L)
        t1 = min(tof_ns(R.EDGES[k], b.L), u_end)
        w.append((t0, t1) if t1 > t0 else (np.nan, np.nan))
    return np.array(w)


def fold(b, t_ns):
    tg = b.L / C_M_NS
    return tg + np.mod(np.asarray(t_ns) - tg, b.T_ns)


def analyse(cfg_beam, tab, M, hw, s=1.0, gate_bins=None, extras=True):
    """per-bin weights relative to the NFS tables, the exposure, and diagnostics, at throttle s."""
    b = cfg_beam
    rf = per_fine(tab, b.e)
    n = b.n * s
    tg = b.L / C_M_NS
    u_edges = tg + np.arange(0, b.T_ns + DU_NS, DU_NS)
    nu = len(u_edges) - 1
    t = tof_ns(b.e, b.L)
    u = fold(b, t)
    iu = np.clip(np.digitize(u, u_edges) - 1, 0, nu - 1)
    du_s = DU_NS * 1e-9
    W = windows(b)
    uc = 0.5 * (u_edges[1:] + u_edges[:-1])
    inwin = np.array([(uc >= w0) & (uc < w1) if np.isfinite(w0) else np.zeros(nu, bool) for w0, w1 in W])
    if gate_bins is None:
        gate_bins = list(range(NB))
    gate = inwin[gate_bins].any(0)

    def profile(per_n):          # per-arm in-macropulse rate [1/s] vs u, from prompt rates
        out = np.zeros((4, nu))
        for a in range(4):
            out[a] = np.bincount(iu, n * per_n[a], nu) / b.up_per_s / du_s
        return out
    rho = profile(rf['ok'][0]) + (n * rf['ok'][1]).sum(1)[:, None]            # delayed flat (time-avg)
    rho_l = profile(rf['lg'][0]) + (n * rf['lg'][1]).sum(1)[:, None]
    pair = sum(rho[a] * rho[c] for a in range(4) for c in range(a + 1, 4))
    pair_l = sum(rho_l[a] * rho_l[c] for a in range(4) for c in range(a + 1, 4))
    P = np.array([pair[inwin[k]].sum() * du_s for k in range(NB)]) * b.up_per_s * 2 * R.COINC_NS * 1e-9 * DAY
    # captures: the bin of each fine-E cell by its folded time; X17 only where it is not wrapped
    cpn = Y.captures_per_neutron(b.e)
    cap = n * cpn
    kb = np.full(len(b.e), -1)
    for k, (w0, w1) in enumerate(W):
        if np.isfinite(w0):
            kb[(u >= w0) & (u < w1)] = k
    own = (t < tg + b.T_ns) & (b.e >= R.EDGES[0])
    cap_x = np.array([cap[(kb == k) & own].sum() for k in range(NB)])
    cap_i = np.array([cap[kb == k].sum() for k in range(NB)])
    dur = np.array([(w1 - w0) * 1e-9 if np.isfinite(w0) else 0.0 for w0, w1 in W])
    if 'corr_rows' in tab:
        # neutrons/s in each response bin, then every Geant4 row at its own arrival time
        jn = np.clip(np.digitize(b.e, tab['edges']) - 1, 0, tab['nb'] - 1)
        n_bin = np.bincount(jn, n, tab['nb'])

        def place(rws):
            e_r, w_r, d_r, j_r = rws
            r = n_bin[j_r] * w_r
            late = d_r > 2e4                                       # > 20 µs: flat in time
            ur = fold(b, tof_ns(e_r, b.L) + np.where(late, 0.0, d_r))
            per_bin = np.array([r[~late & (ur >= w0) & (ur < w1)].sum() if np.isfinite(w0) else 0.0
                                for w0, w1 in W]) + r[late].sum() * dur * b.up_per_s
            ing = gate[np.clip(np.digitize(ur, u_edges) - 1, 0, nu - 1)]
            in_gate = r[~late & ing].sum() + r[late].sum() * gate.sum() * du_s * b.up_per_s
            return per_bin, in_gate
        corr, _ = place(tab['corr_rows'])
        corr = corr * DAY
        _, trig_corr = place(tab['trig_rows'])
    else:
        corr = np.array([(n * rf['corr'])[kb == k].sum() for k in range(NB)]) * DAY
        trig_corr = (n * rf['trig'])[gate[iu]].sum()
    trig_rand = pair_l[gate].sum() * du_s * b.up_per_s * 2 * SF.TAU_HW
    trig = trig_corr + trig_rand
    # DAQ: renewal count per macropulse at the in-macropulse rate
    r_in = trig / b.duty if b.duty < 1 else trig
    if b.duty < 1 and r_in > 0:
        tm = MACRO_S
        live = min(1.0, (tm + R.TAU_DAQ) / (R.TAU_DAQ + 1 / r_in) / (r_in * tm))
    else:
        live = 1 / (1 + trig * R.TAU_DAQ)
    # Micromegas occupancy: ok singles per arm in the preceding 1 µs, inside a macropulse
    nmem = int(round(SF.T_MM * 1e9 / DU_NS))
    tot = rho.mean(0)
    ext = np.concatenate([tot, tot])                     # periodic within a macropulse
    cs = np.concatenate([[0], np.cumsum(ext)])
    ii = nu + np.arange(nu) + 1
    occ_u = (cs[ii] - cs[np.maximum(ii - nmem, 0)]) * du_s
    occ = np.array([occ_u[inwin[k]].mean() if inwin[k].any() else 0.0 for k in range(NB)])
    cos = dur * b.up_per_s / M['cos_frac']
    if not extras:
        occ = np.zeros(NB)
        live = 1 / (1 + M['beam']['trig2_per_s'] * s * R.TAU_DAQ)
    expo = live * np.exp(-2 * occ)
    return dict(cap_x=cap_x, cap_i=cap_i, P=P, corr=corr, cos=cos, expo=expo, live=live, occ=occ,
                trig_corr=trig_corr, trig_rand=trig_rand, W=W, uc=uc, rho=rho, gate=gate,
                ok_per_arm=float(rho.mean(0).mean() * b.duty), n_cell=float(n.sum()))


def beam_shapes(M):
    """NFS correlated m_ee shape per bin (the nearest bin with events where a bin has none)."""
    h = M['h']['beam']
    tot = h.sum(1)
    sh = np.zeros_like(h)
    good = np.nonzero(tot > 0)[0]
    for k in range(NB):
        j = good[np.argmin(np.abs(good - k))]
        sh[k] = h[j] / tot[j]
    return sh


def calib(M):
    if 'P_wnr_nfs' not in M:
        a = analyse(beam_nfs(), response_nfs(M), M, None)
        M['P_wnr_nfs'] = a['P']
    return M


def components(a, M, soft_only):
    """S (at ρ = RHO_REF) and B histograms per bin, per day of beam, exposure included."""
    h = M['h']
    with np.errstate(divide='ignore', invalid='ignore'):
        cx = np.where(M['cap_nfs'] > 0, a['cap_x'] / M['cap_nfs'], 0)
        ci = np.where(M['cap_nfs'] > 0, a['cap_i'] / M['cap_nfs'], 0)
        ca = np.where(M['P_wnr_nfs'] > 0, a['P'] / M['P_wnr_nfs'], 0)
    if soft_only:
        cx = cx * np.isin(np.arange(NB), SOFT)
    sh = beam_shapes(M)
    ex = a['expo'][:, None]
    S = h['X17'] * cx[:, None] * ex
    B = dict(IPC=h['IPC'] * ci[:, None] * ex, acc=h['acc'] * ca[:, None] * ex,
             corr=sh * a['corr'][:, None] * ex, cosmic=h['cosmic'] * a['cos'][:, None] * ex * COS_VETO)
    return S, B


def rho3(S, B, days, bins=range(NB), delta=0.0):
    Bt = sum(B.values())

    def z2(rho):
        return sum(R.z2_asimov(S[k] * rho / R.RHO_REF * days, Bt[k] * days, delta) for k in bins)
    lo, hi = 1e-7, 1e3
    if z2(hi) < 9:
        return np.inf
    for _ in range(60):
        mid = np.sqrt(lo * hi)
        lo, hi = (mid, hi) if z2(mid) < 9 else (lo, mid)
    return np.sqrt(lo * hi)


GATES = {'0.2-2.75': SOFT, '0.2-6': list(range(5)), '0.2-12': list(range(7)), '0.2-25': list(range(NB))}


def best(cfg, tab, M, hw, days, soft_only, grid=np.geomspace(1e-3, 1.0, 31)):
    """best throttle (and, for 'all E*', best trigger gate: the soft gate keeps the DAQ alive)."""
    b = beam_of(cfg)
    gates = {'0.2-2.75': SOFT} if soft_only else GATES
    rows = []
    for gname, gate in gates.items():
        for s in grid:
            a = analyse(b, tab, M, hw, s, gate)
            a['gate_name'] = gname
            S, B = components(a, M, soft_only)
            rows.append((rho3(S, B, days, gate), s, a, S, B))
    b_ = min(rows, key=lambda x: x[0])
    g = b_[2]['gate_name']
    return b_, [r for r in rows if r[2]['gate_name'] == g]


def floor(cfg, tab, M, hw, days, soft_only):
    gate = SOFT if soft_only else list(range(NB))
    a = analyse(beam_of(cfg), tab, M, hw, 1.0, gate)
    a['expo'] = np.ones(NB)
    S, B = components(a, M, soft_only)
    B = dict(IPC=B['IPC'], cosmic=B['cosmic'])
    return rho3(S, B, days, gate)


# --------------------------------------------------------------------------- #
def configs():
    C = []
    # the real flight paths (FACILITY.md §3): 90L 7-15 m, 30R ICE-II ~12 m, 30L ICE House ~20 m,
    # 15L CoGNAC 22 m, 60R (length: ask; 15 m taken)
    for L in (7.0, 8.0, 10.0, 12.0, 15.0):
        C.append(Config(f'90L_{L:g}m', 90, L, label=f'4FP90L, {L:g} m'))
    C.append(Config('90L_8m_3p6', 90, 8.0, 3.6, label='4FP90L, 8 m, 3.6 µs'))
    C.append(Config('90L_15m_3p6', 90, 15.0, 3.6, label='4FP90L, 15 m, 3.6 µs'))
    C.append(Config('90L_10m_100Hz', 90, 10.0, macro_hz=100.0, label='4FP90L, 10 m, 100 Hz (×2.5 current)'))
    C.append(Config('60R_15m', 60, 15.0, label='4FP60R, 15 m (length: ask)'))
    C.append(Config('30R_10m', 30, 10.0, label='4FP30R ICE-II, ~10 m'))
    C.append(Config('30L_20m', 30, 20.0, label='4FP30L ICE House, ~20 m'))
    C.append(Config('30L_20m_3p6', 30, 20.0, 3.6, label='4FP30L ICE House, ~20 m, 3.6 µs'))
    C.append(Config('15L_22m', 15, 22.0, label='4FP15L, 22 m'))
    C.append(Config('15L_22m_3p6', 15, 22.0, 3.6, label='4FP15L, 22 m, 3.6 µs'))
    return C


HEADLINE = '90L_10m'


def scan_L(tab, M, hw, days=50.0):
    """reach vs L for each angle and spacing (E* ≤ 22 and all E*)."""
    rows = []
    for ang in (15, 30, 60, 90):
        for T in (1.8, 3.6, 7.2):
            for L in (5.0, 6.0, 7.0, 8.0, 10.0, 12.0, 15.0, 20.0, 25.0, 30.0):
                cfg = Config(f'scan_{ang}_{L:g}_{T}', ang, L, T)
                for soft in (True, False):
                    (r, s, a, S, B), _ = best(cfg, tab, M, hw, days, soft, grid=np.geomspace(1e-2, 1.0, 13))
                    rows.append(dict(hw=hw, angle=ang, L=L, T_us=T, signal='E* ≤ 22' if soft else 'all E*', gate=a['gate_name'],
                                     rho3=r, throttle=s, live=a['live'], occ=float(a['occ'][SOFT].max()),
                                     e_wrap=float(e_of_tof(T * 1e3 + L / C_M_NS, L))))
    return pd.DataFrame(rows)


def main():
    global K_HI, COS_VETO
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--no-scan', action='store_true')
    ap.add_argument('--days', type=float, nargs='+', default=[14.0, 50.0])
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    if a.check:
        for hw in R.HW:
            M = calib(SF.nfs_model(hw))
            x = analyse(beam_nfs(), response(hw, M), M, hw, 1.0, list(range(NB)), extras=False)
            x['P'] = M['P_wnr_nfs']                    # NFS singles: accidentals × 1 by construction
            print(hw, 'captures / NFS', np.round(x['cap_x'] / M['cap_nfs'], 3), 'cosmics / NFS', np.round(x['cos'], 3))
            print(hw, 'correlated per day: this model', np.round(x['corr']), 'NFS', np.round(M['h']['beam'].sum(1)))
            for soft in (False, True):
                S, B = components(x, M, soft)
                B0 = dict(B, corr=M['h']['beam'] * x['expo'][:, None])
                print(hw, 'E*≤22' if soft else 'all  ', '14 d: correlated as here', f'{rho3(S, B, 14):.4g}',
                      ' NFS correlated', f'{rho3(S, B0, 14):.4g}',
                      '(nfs_reach: big plastics 3.3e-3 / 0.031; as built 8.5e-3 / 0.16)')
        return
    spec_figure()
    rows, comp, curves = [], [], []
    for hw in R.HW:
        M = calib(SF.nfs_model(hw))
        tab = response(hw, M)
        for cfg in configs():
            for days in a.days:
                for soft in (True, False):
                    (r, s, x, S, B), grid = best(cfg, tab, M, hw, days, soft)
                    fl = floor(cfg, tab, M, hw, days, soft)
                    gate = GATES[x['gate_name']]
                    rows.append(dict(key=cfg.key, gate=x['gate_name'], label=cfg.label, hw=hw, days=days,
                                     signal='E* ≤ 22 MeV' if soft else 'all E*', rho3=r, vs_ATOMKI=r / R.RHO_REF,
                                     days_to_atomki=days * (r / R.RHO_REF) ** 2 if np.isfinite(r) else np.inf,
                                     throttle=s, rho3_floor=fl, live=x['live'], occ_max=float(x['occ'][gate].max()),
                                     trig_corr=x['trig_corr'], trig_rand=x['trig_rand'], n_cell=x['n_cell'],
                                     ok_singles_per_arm=x['ok_per_arm'],
                                     e_wrap=float(e_of_tof(cfg.T_us * 1e3 + cfg.L / C_M_NS, cfg.L)),
                                     **{f'{k}_per_day': float(v[gate].sum()) for k, v in B.items()},
                                     X17_per_day=float(S[gate].sum())))
                    if days == 50 and hw == 'big plastics':
                        curves += [dict(key=cfg.key, signal='E* ≤ 22' if soft else 'all E*', throttle=g[1],
                                        n_cell=g[2]['n_cell'], rho3=g[0], live=g[2]['live'],
                                        occ=float(g[2]['occ'][GATES[g[2]['gate_name']]].max())) for g in grid]
                        if soft:
                            for k in range(NB):
                                comp.append(dict(key=cfg.key, bin=k, E_lo=R.EDGES[k], E_hi=R.EDGES[k + 1],
                                                 u0_ns=x['W'][k, 0], u1_ns=x['W'][k, 1], X17=S[k].sum(),
                                                 **{kk: v[k].sum() for kk, v in B.items()}, occ=x['occ'][k],
                                                 expo=x['expo'][k]))
            print(f'{hw:13s} {cfg.key:14s} done', flush=True)
    t = pd.DataFrame(rows)
    t.to_csv(OUT / 'wnr_reach.csv', index=False, float_format='%.4g')
    pd.DataFrame(comp).to_csv(OUT / 'wnr_components.csv', index=False, float_format='%.4g')
    pd.DataFrame(curves).to_csv(OUT / 'wnr_throttle.csv', index=False, float_format='%.4g')
    # sensitivity to the > 45 MeV response (no Geant4 there)
    sens = []
    for k_hi in (0.0, 1.0, 3.0, 10.0):
        K_HI = k_hi
        for hw in R.HW:
            M = calib(SF.nfs_model(hw))
            tab = response(hw, M)
            for key in (HEADLINE, '90L_7m', '30L_20m', '15L_22m'):
                cfg = [c for c in configs() if c.key == key][0]
                for soft in (True, False):
                    (r, s, x, S, B), _ = best(cfg, tab, M, hw, 50.0, soft)
                    sens.append(dict(K_HI=k_hi, hw=hw, key=key, signal='E* ≤ 22' if soft else 'all E*', rho3=r))
    K_HI = 1.0
    for veto in (0.3, 0.1):
        COS_VETO = veto
        for hw in R.HW:
            M = calib(SF.nfs_model(hw))
            tab = response(hw, M)
            for key in (HEADLINE, '90L_10m_100Hz'):
                cfg = [c for c in configs() if c.key == key][0]
                for soft in (True, False):
                    (r, s, x, S, B), _ = best(cfg, tab, M, hw, 50.0, soft)
                    sens.append(dict(K_HI=f'veto {veto}', hw=hw, key=key, signal='E* ≤ 22' if soft else 'all E*', rho3=r))
    COS_VETO = 1.0
    for hw in R.HW:                     # an uncorrelated background-shape uncertainty per m_ee bin
        M = calib(SF.nfs_model(hw))
        tab = response(hw, M)
        cfg = [c for c in configs() if c.key == HEADLINE][0]
        (r, s, x, S, B), _ = best(cfg, tab, M, hw, 50.0, True)
        for dl in (0.005, 0.01, 0.02):
            sens.append(dict(K_HI=f'delta {dl}', hw=hw, key=HEADLINE, signal='E* ≤ 22',
                             rho3=rho3(S, B, 50.0, SOFT, dl)))
    pd.DataFrame(sens).to_csv(OUT / 'wnr_khi_sensitivity.csv', index=False, float_format='%.4g')
    pd.set_option('display.width', 250)
    show = t[t.days == 50]
    print(show.pivot_table(index='key', columns=['hw', 'signal'], values='rho3', sort=False).to_string())
    print(pd.DataFrame(sens).astype({'K_HI': str}).pivot_table(index=['key', 'hw', 'signal'], columns='K_HI', values='rho3').to_string())
    if not a.no_scan:
        sc = pd.concat([scan_L(response(hw, calib(SF.nfs_model(hw))), calib(SF.nfs_model(hw)), hw)
                        for hw in R.HW], ignore_index=True)
        sc.to_csv(OUT / 'wnr_scan.csv', index=False, float_format='%.4g')
    figures()


# --------------------------------------------------------------------------- #
def spec_figure():
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use()
    e = np.geomspace(0.1, 800, 400)
    rows = []
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=fs.WIDE)
    cols = {15: fs.TRACK, 30: fs.COPPER, 60: '#0072B2', 90: fs.ACCENT}
    for ang, c in cols.items():
        y = yield_per_p(e, ang)
        ax.plot(e, np.where(y > 0, y, np.nan), color=c, lw=1.5, label=f'{ang}°')
        # neutrons/s through the Ø8 cm spot per lethargy at 10 m, 1.56 µA
        cfg = Config('x', ang, 10.0)
        ax2.plot(e, np.where(y > 0, cfg.n_spec(e) * e, np.nan), color=c, lw=1.5, label=f'{ang}°')
        rows += [dict(angle=ang, E=x, Y=v, n_per_s_lethargy_10m=cfg.n_spec(np.array([x]))[0] * x)
                 for x, v in zip(e, y)]
    ax.axvspan(0.2, 2.75, color=fs.BAND_SIGNAL, alpha=0.07, lw=0)
    ax2.axvspan(0.2, 2.75, color=fs.BAND_SIGNAL, alpha=0.07, lw=0)
    for a_ in (ax, ax2):
        a_.set_xscale('log')
        a_.set_yscale('log')
        a_.set_xlabel('E_n [MeV]')
        a_.legend(frameon=False, fontsize=8)
    ax.set_ylim(1e-5, 1)
    ax.set_ylabel('Y [n / proton / MeV / sr]')
    ax2.set_ylabel('E·dN/dE through Ø8 cm at 10 m [n/s]')
    ax2.set_ylim(1e5, 3e8)
    fs.title(ax, 'WNR Target 4: softer at wide angles', 'Nowicki et al. 2017 Fig. 2, digitised')
    fs.title(ax2, 'At the cell, 1.56 µA', 'the ATOMKI-like window 0.2-2.75 MeV shaded')
    fig.tight_layout()
    fs.save(fig, OUT / 'wnr_spectra', data=pd.DataFrame(rows))
    t = pd.DataFrame([dict(angle=ang, frac_0p2_2p75=float(np.trapezoid(yield_per_p(E_FINE, ang) * ((E_FINE > 0.2) & (E_FINE < 2.75)), E_FINE)
                                                          / np.trapezoid(yield_per_p(E_FINE, ang) * (E_FINE > 0.1), E_FINE)),
                           frac_above_8p5=float(np.trapezoid(yield_per_p(E_FINE, ang) * (E_FINE > 8.5), E_FINE)
                                                / np.trapezoid(yield_per_p(E_FINE, ang) * (E_FINE > 0.1), E_FINE)),
                           frac_above_45=float(np.trapezoid(yield_per_p(E_FINE, ang) * (E_FINE > 45), E_FINE)
                                               / np.trapezoid(yield_per_p(E_FINE, ang) * (E_FINE > 0.1), E_FINE)),
                           n_per_sr_per_p_above_0p1=float(np.trapezoid(yield_per_p(E_FINE, ang) * (E_FINE > 0.1), E_FINE)),
                           flux_above_1p5_at_20m_1p56uA=float(np.trapezoid(Config('x', ang, 20.0).n_spec(E_FINE) * (E_FINE > 1.5), E_FINE)) / AREA,
                           flux_above_1p5_at_12m_1p56uA=float(np.trapezoid(Config('x', ang, 12.0).n_spec(E_FINE) * (E_FINE > 1.5), E_FINE)) / AREA)
                      for ang in (15, 30, 60, 90)])
    t.to_csv(OUT / 'wnr_spectra_summary.csv', index=False, float_format='%.4g')
    print(t.to_string(index=False))


def figures():
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use()
    # reach vs L
    p = OUT / 'wnr_scan.csv'
    if p.exists():
        sc = pd.read_csv(p)
        d = sc[(sc.hw == 'big plastics') & (sc.signal == 'E* ≤ 22')]
        fig, ax = plt.subplots(figsize=fs.FIG)
        cols = {15: fs.TRACK, 30: fs.COPPER, 60: '#0072B2', 90: fs.ACCENT}
        for (ang, T), q in d.groupby(['angle', 'T_us']):
            ls = {1.8: '-', 3.6: '--', 7.2: ':'}[T]
            ax.plot(q.L, np.clip(q.rho3.replace(np.inf, 1), 1e-4, 1), ls, color=cols[ang], lw=1.4,
                    label=f'{ang}°, {T:g} µs')
        ax.axhline(R.RHO_REF, color=fs.MUTED, lw=0.8)
        ax.text(5.1, R.RHO_REF * 1.1, 'ATOMKI ⁴He 1.5e-3', color=fs.MUTED, fontsize=8)
        ax.set_yscale('log')
        ax.set_xlabel('target → cell distance L [m]')
        ax.set_ylabel('X17/IPC at 3σ, 50 d, E* ≤ 22 MeV')
        ax.legend(frameon=False, fontsize=7, ncol=2)
        fs.title(ax, 'Distance decides, the angle much less: best at ~10 m, 1.8 µs',
                 'big plastics, best throttle; the window is cut at the next γ flash; closer than 10 m DREAM dead time sets in')
        fs.save(fig, OUT / 'wnr_reach_vs_L', data=d)
    # time profile of the headline configuration
    hw = 'big plastics'
    M = calib(SF.nfs_model(hw))
    tab = response(hw, M)
    cfg = [c for c in configs() if c.key == HEADLINE][0]
    a = analyse(beam_of(cfg), tab, M, hw, 1.0, SOFT)
    fig, ax = plt.subplots(figsize=fs.FIG)
    ax.plot(a['uc'] / 1e3, a['rho'].mean(0), color=fs.ACCENT, lw=1.2, label='ok singles per arm (in a macropulse)')
    for k in range(NB):
        w0, w1 = a['W'][k]
        if np.isfinite(w0):
            ax.axvspan(w0 / 1e3, w1 / 1e3, color=fs.BAND_SIGNAL if k in SOFT else fs.BAND_CONTROL,
                       alpha=0.12 if k in SOFT else 0.05, lw=0)
            ax.text(0.5 * (w0 + w1) / 1e3, a['rho'].mean(0).max() * 1.3, f'{R.EDGES[k]:g}', fontsize=6,
                    ha='center', color=fs.MUTED)
    ax.set_yscale('log')
    ax.set_xlabel('time after the micropulse [µs] (one 1.8 µs period, folded)')
    ax.set_ylabel('singles/s per arm')
    fs.title(ax, f'{cfg.label}: where the singles fall', 'bin lower edges in MeV; shaded purple: 0.2-2.75 MeV')
    fs.save(fig, OUT / 'wnr_time_profile', data=pd.DataFrame(dict(u_ns=a['uc'], rho_mean=a['rho'].mean(0),
                                                                     gate=a['gate'])))
    # throttle curves
    cv = pd.read_csv(OUT / 'wnr_throttle.csv')
    fig, ax = plt.subplots(figsize=fs.FIG)
    for key, c in ((HEADLINE, fs.ACCENT), ('90L_7m', fs.MUTED), ('30L_20m', fs.COPPER), ('15L_22m', fs.TRACK), ('90L_10m_100Hz', '#0072B2')):
        q = cv[(cv.key == key) & (cv.signal == 'E* ≤ 22')]
        ax.plot(q.n_cell, np.clip(q.rho3.replace(np.inf, 1), 1e-4, 1), color=c, lw=1.4, label=key)
    ax.axhline(R.RHO_REF, color=fs.MUTED, lw=0.8)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('neutrons/s through the Ø8 cm spot (time-averaged, throttled)')
    ax.set_ylabel('X17/IPC at 3σ, 50 d, E* ≤ 22')
    ax.legend(frameon=False, fontsize=8)
    fs.title(ax, 'Full beam is best from ~10 m out; closer, DREAM dead time sets in', 'the 2.5 % macropulse duty keeps the rate walls far away')
    fs.save(fig, OUT / 'wnr_throttle_fig', data=cv)


if __name__ == '__main__':
    main()
