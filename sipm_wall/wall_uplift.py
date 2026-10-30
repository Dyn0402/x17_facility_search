#!/usr/bin/env python3
"""
wall_uplift.py -- what reading the SiPM wall bar by bar (or SiPM by SiPM) buys over
the n_TOF ganged groups, measured on the LNL Geant4 samples.

Inputs (sim/sel/, gitignored; fetch with sim/fetch_wall.sh):
    L1_X17_m16.7{,_bigP}_wall.npz   X17 pairs, as built / big plastics
    L4_cosmic{,_bigP}_wall.npz      one live day of cosmic muons each
made on lxplus by sim/lxplus/wall_reduce.py (+ wall_merge.py): the lnl_merge
two-arm selection, plus every SiPM-wall bar hit in the two pair arms.

The handle studied: the wall gives each arm a second space point behind the
Micromegas.  The line MM centroid -> wall point
  * points back to the beam spot for a lepton from the target, not for a cosmic
    muon (pointing cut, DCA to the spot);
  * is the same straight line in both arms for a muon crossing two arms
    (collinearity veto: distance of each wall point from the MM1-MM2 line, transverse
    to the beam, where only the bar index matters);
  * gives a lepton direction without the poor MM segment angle.
And the wall time gives the arm-to-arm time of flight.

Readout scenarios (`READOUT`): u from the hit bar (or 4-bar group) centre; v (along
the bar) from the top/bottom time difference, Gaussian sigma_v; the arm time is the
earliest truth time + Gaussian sigma_t (mean-timer: propagation cancels).

Outputs: out/*.csv and out/figures/*.png (each figure with its .csv).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SEL = HERE / 'sim' / 'sel'
OUT = HERE / 'out'
FIG = OUT / 'figures'
sys.path.insert(0, str(HERE.parent / 'ill'))

PIN_MM = np.array([15.5, 15.75, 16.35, 17.3])     # local-u offset of the wall structure (SimConfig pinwheel)
UHAT = np.array([[0, 0, -1], [0, 0, 1], [1, 0, 0], [-1, 0, 0]], float)   # DetectorConstruction armDefs
VHAT = np.array([0, 1, 0], float)
BAR_W = 25.0
BAR_THR_MEV = 0.10            # a bar (or group) counts as hit above this deposit (~0.2 MIP of 3 mm)
MU_LIVE_S = 60.0 / (300.0 * 300.0)      # live s per generated muon (lnl_geant.py)
WINDOW = (125.0, 155.0)
ECUT = {'as built': (13.0, 17.0), 'big plastics': (13.0, 17.0)}       # lnl/FEASIBILITY_SIM.md §3-4
SAMPLES = {'as built': ('L1_X17_m16.7', 'L4_cosmic'), 'big plastics': ('L1_X17_m16.7_bigP', 'L4_cosmic_bigP')}
#: IPC per day in 125-155° at 1 µA after MM 15° + TOF + E_sum (FEASIBILITY_SIM §4, §7), the reference level here:
IPC_PER_DAY = {'as built': 110.0, 'big plastics': 1480.0}

#: readout scenarios.  group = bars per channel; sig_v [mm] along the bar; sig_t [ns] per arm.
#: Ganged: sigma_y 10-13 cm and ~0.4 ns measured at n_TOF (nTof_x17 mx_july_beam_qa
#: vertical_slides; ntof_scint_recovery control).  Per bar / per SiPM: ESTIMATES (see README §3).
READOUT = {
    'ganged 4 bars (n_TOF)': dict(group=4, sig_v=115.0, sig_t=0.45),
    'per bar end (160 ch)': dict(group=1, sig_v=40.0, sig_t=0.25),
    'per SiPM (320 ch)': dict(group=1, sig_v=30.0, sig_t=0.20),
}
COLL_LOSS = 3.0             # % of X17 pairs the wall collinearity veto may lose
SIG_V_SCAN = (10.0, 20.0, 30.0, 40.0, 60.0, 80.0, 115.0, 150.0)
SIG_T_SCAN = (0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.7, 1.0)


def load(stem):
    f = SEL / f'{stem}_wall.npz'
    if not f.exists():
        raise SystemExit(f'missing {f}: run sim/fetch_wall.sh')
    return dict(np.load(f))


def arm_origin(z):
    """Per arm, O such that global = O + u uHat + v vHat + w wHat (fitted on the stored hits)."""
    arms = np.where(z['w_slot'] == 0, z['a1'][z['w_row']], z['a2'][z['w_row']]).astype(int)
    O = np.zeros((4, 3))
    WH = np.zeros((4, 3))
    for a in range(4):
        m = arms == a
        if not m.any():
            continue
        # wHat = outward normal: uHat x vHat or its negative; fit both and keep the better
        best = None
        for s in (1, -1):
            wh = s * np.cross(UHAT[a], VHAT)
            o = z['w_g'][m] - (z['w_u'][m, None] * UHAT[a] + z['w_v'][m, None] * VHAT + z['w_w'][m, None] * wh)
            sp = o.std(0).sum()
            if best is None or sp < best[0]:
                best = (sp, o.mean(0), wh)
        O[a], WH[a] = best[1], best[2]
        assert best[0] < 1.0, f'arm {a}: local->global fit spread {best[0]:.2f} mm'
    return O, WH


def wall_points(z, group, sig_v, sig_t, rng, O, WH, bars_lit=None):
    """Measured wall point (global, mm) and time (ns) for both pair arms, NaN if no bar/group fires.

    group: 1 = every bar its own channel; 4 = ganged groups of 4 (n_TOF windows: as built
    bars 1-16 -> groups 1-4, 5-8, ...; 20 bars -> 0-3, 4-7, ...).
    """
    n = len(z['reco_c'])
    row, slot, bar = z['w_row'].astype(int), z['w_slot'].astype(int), z['w_bar'].astype(int)
    E, t, v, w = z['w_E'].astype(float), z['w_t'].astype(float), z['w_v'].astype(float), z['w_w'].astype(float)
    if bars_lit is not None:
        k = (bar >= bars_lit[0]) & (bar <= bars_lit[1])
        row, slot, bar, E, t, v, w = row[k], slot[k], bar[k], E[k], t[k], v[k], w[k]
    lo = 1 if (bar.size and bar.min() >= 1 and bar.max() <= 16) else 0       # as built: bars 1..16
    ch = (bar - lo) // group
    key = (row * 2 + slot) * 32 + ch
    uk, inv = np.unique(key, return_inverse=True)
    Ech = np.bincount(inv, E)
    vch = np.bincount(inv, E * v) / np.maximum(Ech, 1e-12)
    wch = np.bincount(inv, E * w) / np.maximum(Ech, 1e-12)
    tch = np.full(len(uk), np.inf)
    np.minimum.at(tch, inv, t)
    hit = Ech > BAR_THR_MEV
    uk, Ech, vch, wch, tch = uk[hit], Ech[hit], vch[hit], wch[hit], tch[hit]
    rs = uk // 32
    # the channel with the most energy per (row, slot)
    o = np.lexsort((-Ech, rs))
    first = np.ones(len(o), bool)
    first[1:] = rs[o][1:] != rs[o][:-1]
    pick = o[first]
    P = np.full((n, 2, 3), np.nan)
    T = np.full((n, 2), np.nan)
    tmin = np.full(n * 2, np.inf)                      # earliest fired channel per arm (the trigger time)
    np.minimum.at(tmin, rs, tch)
    r, s = rs[pick] // 2, rs[pick] % 2
    c = uk[pick] % 32
    arm = np.where(s == 0, z['a1'][r], z['a2'][r]).astype(int)
    u_c = ((c * group + lo) + 0.5 * group - 0.5 - 9.5) * BAR_W + PIN_MM[arm]
    v_m = vch[pick] + rng.normal(0, sig_v, len(pick))
    v_m = np.clip(v_m, -250.0, 250.0)
    w_m = wch[pick]
    P[r, s] = O[arm] + u_c[:, None] * UHAT[arm] + v_m[:, None] * VHAT + w_m[:, None] * WH[arm]
    tt = tmin.reshape(n, 2)
    T[:] = np.where(np.isfinite(tt), tt + rng.normal(0, sig_t, tt.shape), np.nan)
    return P, T


def dca0(c, d):
    return np.linalg.norm(np.cross(c, d), axis=-1) / np.linalg.norm(d, axis=-1)


def dist_to_line(p, a, b):
    d = b - a
    return np.linalg.norm(np.cross(p - a, d), axis=-1) / np.linalg.norm(d, axis=-1)


def smear_dir(d, deg, rng):
    d = d / np.linalg.norm(d, axis=-1, keepdims=True)
    a = np.where(np.abs(d[:, 0]) < 0.9, 1.0, 0.0)
    ref = np.stack([a, 1 - a, np.zeros_like(a)], 1)
    e1 = np.cross(d, ref)
    e1 /= np.linalg.norm(e1, axis=1, keepdims=True)
    e2 = np.cross(d, e1)
    th = np.radians(rng.normal(0, deg, len(d)))
    ph = rng.uniform(0, 2 * np.pi, len(d))
    return np.cos(th)[:, None] * d + np.sin(th)[:, None] * (np.cos(ph)[:, None] * e1 + np.sin(ph)[:, None] * e2)


def angle(a, b):
    c = (a * b).sum(-1) / (np.linalg.norm(a, axis=-1) * np.linalg.norm(b, axis=-1))
    return np.degrees(np.arccos(np.clip(c, -1, 1)))


class Sample:
    def __init__(self, stem, rng):
        self.z = load(stem)
        tp = SEL / f'{stem}_tplast.npz'           # earliest plastic time per pair arm (lnl sel_v3, same rows)
        if tp.exists():
            t = np.load(tp)
            self.t_plast = np.stack([t['t_plast1'], t['t_plast2']], 1).astype(float)
        self.O, self.WH = arm_origin(self.z)
        z = self.z
        self.c1, self.c2 = z['c_dom1'].astype(float), z['c_dom2'].astype(float)
        self.ca1, self.ca2 = z['c_all1'].astype(float), z['c_all2'].astype(float)
        self.d1, self.d2 = z['d_dom1'].astype(float), z['d_dom2'].astype(float)
        self.Esum = (z['E1'] + z['E2']).astype(float)
        self.ang = z['reco_c'].astype(float)
        self.n = len(self.ang)
        self.rng = rng

    def wall(self, group, sig_v, sig_t, seed=5):
        return wall_points(self.z, group, sig_v, sig_t, np.random.default_rng(seed), self.O, self.WH)

    def base(self, ecut):
        return (self.ang >= WINDOW[0]) & (self.ang < WINDOW[1]) & (self.Esum > ecut[0]) & (self.Esum < ecut[1])

    # --- cuts ------------------------------------------------------------- #
    def wall_dca(self, P):
        D = np.full((self.n, 2), np.inf)
        for k, c in ((0, self.c1), (1, self.c2)):
            ok = np.isfinite(P[:, k]).all(1) & np.isfinite(c).all(1)
            D[ok, k] = dca0(c[ok], P[ok, k] - c[ok])
        return D

    def wall_coll(self, P):
        """max distance of the two wall points from the MM1-MM2 line, in the plane transverse to the beam
        (the bar index alone; v along the bar is too coarse).  A muon crossing two arms is straight: ~mm."""
        d = np.full(self.n, np.inf)
        Q, a, b = P.copy(), self.c1.copy(), self.c2.copy()
        for x in (Q, a, b):
            x[..., 1] = 0.0                       # drop the beam coordinate (y)
        ok = np.isfinite(Q).all((1, 2)) & np.isfinite(a).all(1) & np.isfinite(b).all(1)
        d[ok] = np.maximum(dist_to_line(Q[ok, 0], a[ok], b[ok]), dist_to_line(Q[ok, 1], a[ok], b[ok]))
        return d

    def mm_dca(self, deg, seed=11):
        rng = np.random.default_rng(seed)
        D = np.full((self.n, 2), np.inf)
        S = []
        for k, (c, d) in enumerate(((self.c1, self.d1), (self.c2, self.d2))):
            ok = np.isfinite(d).all(1) & np.isfinite(c).all(1)
            s = np.full_like(d, np.nan)
            s[ok] = smear_dir(d[ok], deg, rng)
            D[ok, k] = dca0(c[ok], s[ok])
            S.append(s)
        return D, S

    def tof_ok(self, T, sig_t, k=2.0):
        """lnl_geant.pass_tof: veto if the lower arm fires > k√2σ after the upper one."""
        t1, t2 = T[:, 0], T[:, 1]
        z1, z2 = self.ca1[:, 2], self.ca2[:, 2]
        cut = k * np.sqrt(2) * sig_t
        dt_down = np.where(z1 > z2, t2 - t1, t1 - t2)
        level = np.abs(z1 - z2) < 100.0
        ok = np.where(level, np.abs(t1 - t2) < cut, dt_down < cut)
        return ok | ~np.isfinite(t1 - t2)


def cut90(D):
    """per-arm DCA cut keeping 90 % of X17 arms (both arms pooled)."""
    x = D[np.isfinite(D)]
    return float(np.percentile(x, 90))


def run_hw(hw, rows, scan_rows, res_rows):
    rng = np.random.default_rng(1)
    xs, cs = (Sample(s, rng) for s in SAMPLES[hw])
    ecut = ECUT[hw]
    bx, bc = xs.base(ecut), cs.base(ecut)
    live_s = cs.z['n_generated'].sum() * MU_LIVE_S
    per_day = 86400.0 / live_s
    print(f'\n== {hw}: X17 in window {bx.sum()}, cosmics in window {bc.sum()} ({bc.sum() * per_day:.0f}/day), '
          f'cosmic live {live_s / 86400:.2f} d')

    def add(level, mx, mc, note=''):
        ex = (mx & bx).sum() / max(bx.sum(), 1)
        nc = (mc & bc).sum() * per_day
        rows.append(dict(hardware=hw, level=level, x17_eff=round(ex, 4), cosmics_per_day=round(nc, 1),
                         cosmics_mc=int((mc & bc).sum()), note=note))
        print(f'  {level:58s} X17 {ex:6.3f}  cosmics/day {nc:9.1f}  (MC {int((mc & bc).sum())})')

    tx = np.ones(xs.n, bool)
    tc = np.ones(cs.n, bool)
    add('trigger + E_sum + window', tx, tc)
    # MM segments as in lnl_geant (15° measured chambers, 3° upgrade) + 20° collinearity
    for deg in (15.0, 3.0):
        Dx, Sx = xs.mm_dca(deg)
        Dc, Sc = cs.mm_dca(deg)
        D = cut90(Dx)
        lx, lc = angle(Sx[0], Sx[1]), angle(Sc[0], Sc[1])
        mx = (Dx < D).all(1) & (np.minimum(lx, 180 - lx) >= 20)      # lnl_geant COLL_DEG veto
        mc = (Dc < D).all(1) & (np.minimum(lc, 180 - lc) >= 20)
        add(f'MM {deg:g}° (D = {D:.0f} mm)', mx, mc)
        if deg == 15.0:
            mm15x, mm15c = mx, mc
    for name, R in READOUT.items():
        Px, Tx = xs.wall(R['group'], R['sig_v'], R['sig_t'])
        Pc, Tc = cs.wall(R['group'], R['sig_v'], R['sig_t'])
        Wx, Wc = xs.wall_dca(Px), cs.wall_dca(Pc)
        D = cut90(Wx)
        Cx, Cc = xs.wall_coll(Px), cs.wall_coll(Pc)
        C = float(np.percentile(Cx[np.isfinite(Cx)], COLL_LOSS))   # collinearity veto losing 3 % of X17
        px, pc = (Wx < D).all(1), (Wc < D).all(1)
        kx, kc = Cx > C, Cc > C
        tofx, tofc = xs.tof_ok(Tx, R['sig_t']), cs.tof_ok(Tc, R['sig_t'])
        add(f'{name}: wall pointing (D = {D:.0f} mm)', px, pc)
        add(f'{name}: wall collinearity (> {C:.0f} mm)', kx, kc)
        add(f'{name}: TOF (σ_t {R["sig_t"]} ns)', tofx, tofc)
        add(f'{name}: MM 15° + TOF', mm15x & tofx, mm15c & tofc, 'the lnl_geant reference level with this σ_t')
        add(f'{name}: wall collinearity + TOF', kx & tofx, kc & tofc)
        add(f'{name}: MM 15° + wall collinearity + TOF', mm15x & kx & tofx, mm15c & kc & tofc)
        # direction resolution of the MM -> wall line for X17 leptons (truth: em_P / ep_P at the MM)
        res_rows.extend(direction_resolution(xs, Px, hw, name))
    # scans of sigma_v (pointing) and sigma_t (TOF), per-bar granularity vs ganged
    for group in (1, 4):
        for sv in SIG_V_SCAN:
            Px, _ = xs.wall(group, sv, 0.3)
            Pc, _ = cs.wall(group, sv, 0.3)
            Wx, Wc = xs.wall_dca(Px), cs.wall_dca(Pc)
            D = cut90(Wx)
            Cx, Cc = xs.wall_coll(Px), cs.wall_coll(Pc)
            C = float(np.percentile(Cx[np.isfinite(Cx)], COLL_LOSS))
            mx, mc = (Wx < D).all(1) & (Cx > C), (Wc < D).all(1) & (Cc > C)
            scan_rows.append(dict(hardware=hw, scan='sigma_v', group=group, value=sv, x17_eff=(mx & bx).sum() / bx.sum(),
                                  cosmics_per_day=(mc & bc).sum() * per_day, D90_mm=D))
    # the same TOF veto on the plastic (PMT) time instead of the wall's: no un-ganging needed
    if hasattr(xs, 't_plast') and hasattr(cs, 't_plast'):
        for st in SIG_T_SCAN:
            r1, r2 = np.random.default_rng(21), np.random.default_rng(22)
            Tx = xs.t_plast + r1.normal(0, st, xs.t_plast.shape)
            Tc = cs.t_plast + r2.normal(0, st, cs.t_plast.shape)
            mx, mc = xs.tof_ok(Tx, st), cs.tof_ok(Tc, st)
            scan_rows.append(dict(hardware=hw, scan='sigma_t_plastic', group=0, value=st, x17_eff=(mx & bx).sum() / bx.sum(),
                                  cosmics_per_day=(mc & bc).sum() * per_day, D90_mm=np.nan))
            if st in (0.25, 0.45):
                add(f'plastic PMT time: TOF (σ_t {st} ns)', mx, mc, 'MM-position-corrected plastic time assumed')
    for st in SIG_T_SCAN:
        _, Tx = xs.wall(1, 40.0, st)
        _, Tc = cs.wall(1, 40.0, st)
        mx, mc = xs.tof_ok(Tx, st), cs.tof_ok(Tc, st)
        scan_rows.append(dict(hardware=hw, scan='sigma_t', group=1, value=st, x17_eff=(mx & bx).sum() / bx.sum(),
                              cosmics_per_day=(mc & bc).sum() * per_day, D90_mm=np.nan))


def direction_resolution(xs, P, hw, name):
    z = xs.z
    out = []
    if 'em_P' not in z:
        return out
    for k, c in ((0, xs.c1), (1, xs.c2)):
        arm = z['a1'] if k == 0 else z['a2']
        # truth momentum of the lepton that went into this arm
        tp = np.where((z['em_arm'] == arm)[:, None], z['em_P'], np.where((z['ep_arm'] == arm)[:, None], z['ep_P'], np.nan))
        ok = np.isfinite(P[:, k]).all(1) & np.isfinite(tp).all(1) & np.isfinite(c).all(1)
        a = angle(P[ok, k] - c[ok], tp[ok])
        b = angle(c[ok], tp[ok])          # the spot -> MM chord (what the analysis uses)
        out.append(dict(hardware=hw, readout=name, arm_slot=k + 1, n=int(ok.sum()),
                        mm_to_wall_sigma68_deg=float(np.percentile(a, 68)),
                        spot_to_mm_sigma68_deg=float(np.percentile(b, 68))))
    return out


MM_AREA_MM2 = 399.4 * 359.9          # MM active area (CLAUDE.md)


def road_table(hw):
    """The MM road a wall hit defines: the line spot -> wall point, crossed with the MM; the X17 lepton's
    MM centroid lies within (du, dv) of it for 95 % of arms.  The road area over the MM active area is the
    chance that an unrelated MM cluster (a neutron recoil, pile-up) falls inside the road."""
    xs = Sample(SAMPLES[hw][0], np.random.default_rng(3))
    out = []
    for name, R in READOUT.items():
        P, _ = xs.wall(R['group'], R['sig_v'], R['sig_t'])
        res_u, res_v = [], []
        for k, (c, a) in enumerate(((xs.c1, xs.z['a1']), (xs.c2, xs.z['a2']))):
            ok = np.isfinite(P[:, k]).all(1) & np.isfinite(c).all(1)
            w = P[ok, k]
            pred = w * (np.linalg.norm(c[ok], axis=1) / np.linalg.norm(w, axis=1))[:, None]
            d = c[ok] - pred
            res_u.append(np.abs((d * UHAT[a[ok].astype(int)]).sum(1)))
            res_v.append(np.abs(d[:, 1]))
        u95, v95 = (float(np.percentile(np.concatenate(r), 97.5)) for r in (res_u, res_v))
        frac = min(1.0, (2 * u95) * (2 * v95) / MM_AREA_MM2)
        out.append(dict(hardware=hw, readout=name, road_half_u_mm=round(u95), road_half_v_mm=round(v95),
                        road_fraction_of_MM=round(frac, 3),
                        p_stray_in_road_at_0p6_per_arm=round(1 - np.exp(-0.6 * frac), 3)))
    return out


def figures(scan):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import figstyle as fs           # ill/figstyle.py house style
    fs.use()
    FIG.mkdir(parents=True, exist_ok=True)
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.2))
    for hw, ls in (('as built', '-'), ('big plastics', '--')):
        for group, col in ((1, 'C0'), (4, 'C3')):
            s = scan[(scan.hardware == hw) & (scan.scan == 'sigma_v') & (scan.group == group)]
            if len(s):
                axs[0].plot(s.value / 10, s.cosmics_per_day, ls, color=col, marker='o', ms=3,
                            label=f'{hw}, {"per bar" if group == 1 else "ganged 4"}')
        s = scan[(scan.hardware == hw) & (scan.scan == 'sigma_t')]
        if len(s):
            axs[1].plot(s.value, s.cosmics_per_day, ls, color='C0', marker='o', ms=3, label=f'{hw}, wall time')
        s = scan[(scan.hardware == hw) & (scan.scan == 'sigma_t_plastic')]
        if len(s):
            axs[1].plot(s.value, s.cosmics_per_day, ls, color='C2', marker='s', ms=3, label=f'{hw}, plastic time')
    axs[0].set_xlabel('σ_v along the bar [cm]')
    axs[0].set_ylabel('cosmics / day in 125–155° (E_sum 13–17)')
    axs[0].set_yscale('symlog', linthresh=1)
    axs[0].set_title('wall pointing + collinearity', fontsize=10)
    axs[0].axvspan(10, 13, color='0.85', zorder=0)
    axs[0].text(11.5, axs[0].get_ylim()[1] * 0.5, 'n_TOF\nganged', ha='center', va='top', fontsize=8)
    axs[0].legend(fontsize=8)
    axs[1].set_xlabel('σ_t per arm [ns]')
    axs[1].set_ylabel('cosmics / day in 125–155° (E_sum 13–17)')
    axs[1].set_yscale('symlog', linthresh=1)
    axs[1].set_title('TOF veto alone: wall or plastic time', fontsize=10)
    for name, R in READOUT.items():
        axs[1].axvline(R['sig_t'], color='0.6', lw=0.8, ls=':')
        axs[1].text(R['sig_t'], 0.97, name.split(' (')[0], rotation=90, fontsize=7, va='top', ha='right',
                    transform=axs[1].get_xaxis_transform())
    axs[1].legend(fontsize=8)
    fs.save(fig, FIG / 'cosmics_vs_resolution.png', data=scan)
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows, scan_rows, res_rows = [], [], []
    for hw in SAMPLES:
        if not all((SEL / f'{st}_wall.npz').exists() for st in SAMPLES[hw]):
            print(f'skipping {hw}: tables missing (sim/fetch_wall.sh)')
            continue
        run_hw(hw, rows, scan_rows, res_rows)
    road = pd.DataFrame([r for hw in SAMPLES if (SEL / f'{SAMPLES[hw][0]}_wall.npz').exists() for r in road_table(hw)])
    road.to_csv(OUT / 'mm_road.csv', index=False)
    print(road.to_string(index=False))
    cr = pd.DataFrame(rows)
    cr['days_rel'] = np.nan
    for hw, g in cr.groupby('hardware'):
        ref = g[g.level == 'ganged 4 bars (n_TOF): MM 15° + TOF'].iloc[0]
        # IPC comes from the spot like the X17 and passes the same cuts (lnl_geant.pass_tof note)
        B = IPC_PER_DAY[hw] * g.x17_eff / ref.x17_eff + g.cosmics_per_day
        d = B / g.x17_eff ** 2
        cr.loc[g.index, 'days_rel'] = (d / d[ref.name]).round(3)
    cr.to_csv(OUT / 'cosmic_rejection.csv', index=False)
    print(cr[['hardware', 'level', 'x17_eff', 'cosmics_per_day', 'days_rel']].to_string(index=False))
    scan = pd.DataFrame(scan_rows)
    scan.to_csv(OUT / 'resolution_scan.csv', index=False)
    pd.DataFrame(res_rows).to_csv(OUT / 'direction_resolution.csv', index=False)
    print(pd.DataFrame(res_rows).to_string(index=False))
    figures(scan)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
