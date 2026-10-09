#!/usr/bin/env python3
"""plastic_size.py -- why the big plastics win, and how big they need to be.

    python lnl/plastic_size.py          # -> lnl/out/plastics/*.csv + figures (~3 min)
    python lnl/plastic_size.py --figs   # figures only

A geometric toy of the trigger leg, calibrated on the Geant4 LNL runs, so the
plastic size and distance can be scanned without new Geant4:

  * pairs: X17 (m = 16.7 at W = 18.15 MeV) and Born M1/E1 IPC at 18.15 MeV, with
    the generator kinematics of MX17_Full_Geant X17PrimaryGenerator.cc (X17 and
    gamma* isotropic, the pair at theta* about it), from a sigma = 2 mm beam spot;
  * arms: the surveyed n_TOF arms (SimConfig.hh): faces at 204/204.5 mm, the
    pinwheel shifts, the MM active area 399.4 x 360 mm, the 50 x 50 cm SiPM
    wall (16 or 20 bars) and the plastics behind it, centred on the MM;
  * a leg: straight lepton from the spot, through the MM active area, kicked by
    Highland multiple scattering at the back of the MM (x/X0 = T_MM, fitted) and
    in the SiPM wall (1 % X0), must cross a read-out SiPM bar AND the plastic
    face, with kinetic energy > E_TH (fitted, stands for the ranging-out and the
    0.5 MIP thresholds);
  * the two free numbers are fitted to the Geant4 pair-tag of the X17 as built
    (2 x 20 x 30 cm, 16 bars) and with big plastics (75 x 75 cm, 20 bars).
    The IPC pair-tags, the MM-level acceptance and the 125-155 deg fractions are
    checks (calib.csv).

Days to 3 sigma (counting in 125-155 deg) scale as B/S^2 with S, B the accepted
X17 and IPC in the window; they are anchored to the Geant4 big-plastics value.
The E_sum, MM 15 deg and TOF efficiencies are held at their Geant4 big-plastics
values (5 cm plastic), so the curve is about geometry only.  AN ANALYTIC
STAND-IN for a Geant4 size scan, labelled as such.

Outputs (lnl/out/plastics/):
  calib.csv        toy vs Geant4 at the two calibration points and the checks
  chain.csv        the Geant4 X17 chain as built -> big plastics (the x15)
  footmap.csv      where the X17 leptons that cross an MM land on the plastic plane
  days_vs_size.csv days to 3 sigma against the side of a square plastic, per placement
  footprint.csv    the largest centred square per distance (neighbours collide)
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / 'out' / 'plastics'
GEANT = HERE / 'out' / 'geant'
ME = 0.51099895

# --- arm geometry (MX17_Full_Geant SimConfig.hh, lnl branch), mm ----------- #
DIST = np.array([204.0, 204.0, 204.5, 204.5])          # MM window face from the beam axis
SHIFT = np.array([15.5, 15.75, 16.35, 17.3])           # pinwheel shift along -u
W_HAT = np.array([[1, 0, 0], [-1, 0, 0], [0, 0, 1], [0, 0, -1]], float)
U_HAT = np.array([[0, 0, -1], [0, 0, 1], [1, 0, 0], [-1, 0, 0]], float)
MM_DW = 20.0            # measurement plane: 5 mm flange gap + mid drift
MM_BACK_DW = 45.0       # back of the MM module (drift 30, PCB 1.7, rohacell 5)
MM_HU, MM_HV = 199.7, 180.0
SIPM_DW = 127.5         # SiPM scintillator plane (11 cm + half the 3.5 cm container)
SIPM_HV = 250.0
PLASTIC_DW_ASBUILT = np.array([208.7, 204.7, 206.7, 204.7])   # SiPM back + measured gap + tape
SIPM_BACK_DW = 145.0
T_PLASTIC = 50.0        # big plastic thickness

# --- Geant4 calibration targets (lnl/out/geant/acceptance_geant.csv) -------- #
SIGMA_SPOT = 2.0


def iso(rng, n):
    c = rng.uniform(-1, 1, n)
    p = rng.uniform(0, 2 * np.pi, n)
    s = np.sqrt(1 - c * c)
    return np.stack([s * np.cos(p), s * np.sin(p), c], 1)


def boost(E, p, b):
    """Boost four-vectors (E, p[n,3]) by velocity b[n,3]."""
    b2 = (b * b).sum(1)
    g = 1 / np.sqrt(1 - b2)
    bp = (b * p).sum(1)
    g2 = np.where(b2 > 0, (g - 1) / np.where(b2 > 0, b2, 1), 0.0)
    p2 = p + (g2 * bp + g * E)[:, None] * b
    return g * (E + bp), p2


def gen_x17(rng, n, m=16.7, W=18.15):
    pX = math.sqrt(W * W - m * m)
    b = (pX / W) * iso(rng, n)
    Ee = m / 2
    pe = math.sqrt(Ee * Ee - ME * ME)
    d = iso(rng, n)
    E1, p1 = boost(np.full(n, Ee), -pe * d, b)
    E2, p2 = boost(np.full(n, Ee), pe * d, b)
    return E1 - ME, p1, E2 - ME, p2


def _born(kind, k, M, W, b2, c):
    if kind == 'M1':
        nT, nL = k * k, 0.0 * k
    else:  # E1
        nT, nL = 2 * W * W + 0 * k, M * M
    c2 = c * c
    sT = 2 * M * M * ((1 + c2) + (1 - b2) * (1 - c2))
    sL = 2 * M * M * (1 - b2 * c2)
    return nT * sT + nL * sL


def gen_ipc(rng, n, kind='M1', W=18.15):
    """Born multipole IPC, as X17PrimaryGenerator::GenerateIPC."""
    x = np.linspace(math.log(2 * ME * (1 + 1e-9)), math.log(W * (1 - 1e-12)), 20000)
    M = np.exp(x)
    k = np.sqrt(np.maximum(0, W * W - M * M))
    b2 = np.maximum(0, 1 - 4 * ME * ME / (M * M))
    nT = k * k if kind == 'M1' else 2 * W * W + 0 * k
    nL = 0 * k if kind == 'M1' else M * M
    iT = 2 * M * M * (8 / 3 + (1 - b2) * 4 / 3)
    iL = 2 * M * M * (2 - b2 * 2 / 3)
    f = (nT * iT + nL * iL) / M ** 4 * k * np.sqrt(b2) * 2 * M * M
    cdf = np.r_[0, np.cumsum(0.5 * (f[1:] + f[:-1]) * np.diff(x))]
    cdf /= cdf[-1]
    Ms = np.exp(np.interp(rng.uniform(0, 1, n), cdf, x))
    ks = np.sqrt(W * W - Ms * Ms)
    bs2 = 1 - 4 * ME * ME / (Ms * Ms)
    gmax = np.maximum(_born(kind, ks, Ms, W, bs2, 0.0), _born(kind, ks, Ms, W, bs2, 1.0))
    cs = np.empty(n)
    todo = np.arange(n)
    while len(todo):
        c = rng.uniform(-1, 1, len(todo))
        ok = rng.uniform(0, 1, len(todo)) * gmax[todo] <= _born(kind, ks[todo], Ms[todo], W, bs2[todo], c)
        cs[todo[ok]] = c[ok]
        todo = todo[~ok]
    kd = iso(rng, n)
    ref = np.where(np.abs(kd[:, 0:1]) < 0.9, [[1, 0, 0]], [[0, 1, 0]])
    e1 = np.cross(kd, ref)
    e1 /= np.linalg.norm(e1, axis=1, keepdims=True)
    e2 = np.cross(kd, e1)
    ph = rng.uniform(0, 2 * np.pi, n)
    sn = np.sqrt(1 - cs * cs)
    d = cs[:, None] * kd + sn[:, None] * (np.cos(ph)[:, None] * e1 + np.sin(ph)[:, None] * e2)
    Ee = Ms / 2
    pe = np.sqrt(np.maximum(0, Ee * Ee - ME * ME))
    b = (ks / W)[:, None] * kd
    E1, p1 = boost(Ee, -pe[:, None] * d, b)
    E2, p2 = boost(Ee, pe[:, None] * d, b)
    return E1 - ME, p1, E2 - ME, p2


def highland(ke, xx0):
    p = np.sqrt((ke + ME) ** 2 - ME * ME)
    beta = p / (ke + ME)
    return 13.6 / (beta * p) * math.sqrt(xx0) * (1 + 0.038 * math.log(xx0))


def kick(rng, d, th0):
    """Rotate unit vectors d by a space angle with plane-projected rms th0 [rad]."""
    ref = np.where(np.abs(d[:, 0:1]) < 0.9, [[1, 0, 0]], [[0, 1, 0]])
    e1 = np.cross(d, ref)
    e1 /= np.linalg.norm(e1, axis=1, keepdims=True)
    e2 = np.cross(d, e1)
    a, b = rng.normal(0, 1, (2, len(d))) * th0
    out = d + a[:, None] * e1 + b[:, None] * e2
    return out / np.linalg.norm(out, axis=1, keepdims=True)


class Leptons:
    """One lepton per row: the arm it enters, MM and downstream crossing points."""

    def __init__(self, rng, V, ke, p, t_mm, t_sipm=0.01):
        n = len(ke)
        d = p / np.linalg.norm(p, axis=1, keepdims=True)
        dw = d @ W_HAT.T                                   # (n, 4)
        arm = np.argmax(dw, 1)
        self.arm, self.ke = arm, ke
        w, u = W_HAT[arm], U_HAT[arm]
        cw = (d * w).sum(1)
        v0w = (V * w).sum(1)
        dist = DIST[arm]

        def at(P0, dd, depth):
            t = (dist + depth - (P0 * w).sum(1)) / (dd * w).sum(1)
            return P0 + t[:, None] * dd

        P = at(V, d, MM_DW)
        self.u_mm = (P * u).sum(1) + SHIFT[arm]
        self.v_mm = P[:, 1]
        self.mm = (cw > 0) & (np.abs(self.u_mm) < MM_HU) & (np.abs(self.v_mm) < MM_HV)
        ke_c = np.maximum(ke, 0.05)
        Pb = at(V, d, MM_BACK_DW)
        d1 = kick(rng, d, highland(ke_c, t_mm))
        Ps = at(Pb, d1, SIPM_DW)
        self.u_s = (Ps * u).sum(1)                         # structure frame (SiPM wall)
        self.v_s = Ps[:, 1]
        d2 = kick(rng, d1, highland(ke_c, t_sipm))
        self._Ps, self._d2, self._w, self._u, self._arm = Ps, d2, w, u, arm
        self._cache = {}

    def at_plastic(self, depth):
        """(u_mm, v) on a plane at `depth` (array per arm or scalar) behind the MM face."""
        key = tuple(np.atleast_1d(depth))
        if key not in self._cache:
            dep = np.broadcast_to(np.asarray(depth, float), (4,))[self._arm]
            t = (DIST[self._arm] + dep - (self._Ps * self._w).sum(1)) / (self._d2 * self._w).sum(1)
            P = self._Ps + t[:, None] * self._d2
            self._cache[key] = ((P * self._u).sum(1) + SHIFT[self._arm], P[:, 1])
        return self._cache[key]


class Sample:
    def __init__(self, kind, n, seed, t_mm):
        rng = np.random.default_rng(seed)
        if kind == 'X17':
            k1, p1, k2, p2 = gen_x17(rng, n)
        else:
            k1, p1, k2, p2 = gen_ipc(rng, n, kind)
        V = np.zeros((n, 3))
        V[:, 0] = rng.normal(0, SIGMA_SPOT, n)
        V[:, 2] = rng.normal(0, SIGMA_SPOT, n)
        self.n = n
        self.theta = np.degrees(np.arccos(np.clip((p1 * p2).sum(1) / (np.linalg.norm(p1, axis=1)
                                                                      * np.linalg.norm(p2, axis=1)), -1, 1)))
        self.L = (Leptons(rng, V, k1, p1, t_mm), Leptons(rng, V, k2, p2, t_mm))
        self.mm2 = self.L[0].mm & self.L[1].mm & (self.L[0].arm != self.L[1].arm)


def sipm_ok(L, nbars):
    lo, hi = (-250.0, 250.0) if nbars == 20 else (-225.0, 175.0)
    return (L.u_s > lo) & (L.u_s < hi) & (np.abs(L.v_s) < SIPM_HV)


def leg(L, e_th, plastic, depth, nbars=20):
    """plastic: ('square', S_mm) or ('asbuilt',) or ('none',) (SiPM alone)."""
    ok = L.mm & (L.ke > e_th)
    if nbars:
        ok &= sipm_ok(L, nbars)
    if plastic[0] == 'none':
        return ok
    u, v = L.at_plastic(depth)
    if plastic[0] == 'asbuilt':
        au = np.abs(u)
        return ok & (au > 1.5) & (au < 200.6) & (np.abs(v) < 150.2)
    h = plastic[1] / 2
    return ok & (np.abs(u) < h) & (np.abs(v) < h)


def pair_tag(s, e_th, plastic, depth, nbars=20):
    return s.mm2 & leg(s.L[0], e_th, plastic, depth, nbars) & leg(s.L[1], e_th, plastic, depth, nbars)


BIG_DEPTH = PLASTIC_DW_ASBUILT                 # the Geant4 big plastic sits where the bars were
GEANT_TAG = {('X17', 'as built'): 0.032565, ('X17', 'big plastics'): 0.231556,
             ('M1', 'as built'): 0.003080, ('M1', 'big plastics'): 0.023554,
             ('E1', 'as built'): 0.005431, ('E1', 'big plastics'): 0.037004}
GEANT_MM = {'X17': 0.38745, 'M1': 0.101377, 'E1': 0.124069}
#: fraction of pair-tagged events with truth theta in 125-155 (acceptance_geant.csv,
#: trigger, no E_sum: acc_125_155 / pair_tag, reco theta)
GEANT_WIN = {('X17', 'as built'): 0.020724 / 0.032565, ('X17', 'big plastics'): 0.180671 / 0.231556}
CONF = {'as built': (('asbuilt',), 16), 'big plastics': (('square', 750.0), 20)}


def calibrate(samples_by_t, e_grid):
    """Grid fit of (T_MM, E_TH) to the two X17 pair-tags (log ratio, least squares)."""
    best = None
    for t, S in samples_by_t.items():
        s = S['X17']
        for e in e_grid:
            r = [math.log(pair_tag(s, e, *CONF[h][:1], BIG_DEPTH, CONF[h][1]).mean() / GEANT_TAG[('X17', h)])
                 for h in CONF]
            chi = sum(x * x for x in r)
            if best is None or chi < best[0]:
                best = (chi, t, e)
    return best


def smear(theta, rng, s68=5.1):
    return theta + rng.normal(0, s68, len(theta))


def window_counts(s, mask, rng, lo=125, hi=155):
    th = smear(s.theta, rng)
    return ((th >= lo) & (th < hi) & mask).sum() / s.n


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    N = 600_000
    t_grid = (0.01, 0.02, 0.03, 0.045, 0.06, 0.08)
    e_grid = np.arange(0.5, 6.01, 0.25)
    samples = {t: {'X17': Sample('X17', N, 1, t)} for t in t_grid}
    chi, T_MM, E_TH = calibrate(samples, e_grid)
    print(f'calibrated: T_MM = {T_MM:.3f} X0, E_TH = {E_TH:.2f} MeV (chi = {chi:.3g})')

    N2 = 2_000_000
    S = {k: Sample(k, N2, 10 + i, T_MM) for i, k in enumerate(('X17', 'M1', 'E1'))}
    rng = np.random.default_rng(5)

    # ---- calibration and checks ---------------------------------------------- #
    rows = []
    for k, s in S.items():
        rows.append(dict(quantity='both leptons in MM active area, different arms', sample=k, hw='-',
                         toy=s.mm2.mean(), geant=GEANT_MM[k]))
        for h in CONF:
            m = pair_tag(s, E_TH, CONF[h][0], BIG_DEPTH, CONF[h][1])
            rows.append(dict(quantity='pair-tag', sample=k, hw=h, toy=m.mean(), geant=GEANT_TAG[(k, h)],
                             role='fit' if k == 'X17' else 'check'))
            if k == 'X17':
                rows.append(dict(quantity='fraction of pair-tags in 125-155 deg', sample=k, hw=h,
                                 toy=window_counts(s, m, rng) / m.mean(), geant=GEANT_WIN[(k, h)], role='check'))
    for h in CONF:
        m = pair_tag(S['X17'], E_TH, ('square', 750.0) if h == 'big plastics' else ('asbuilt',), BIG_DEPTH, 20)
        rows.append(dict(quantity='pair-tag, all 20 SiPM bars', sample='X17', hw=h, toy=m.mean(),
                         geant=0.0330 if h == 'as built' else GEANT_TAG[('X17', h)], role='check'))
    calib = pd.DataFrame(rows)
    calib['T_MM'] = T_MM
    calib['E_TH_MeV'] = E_TH
    calib.to_csv(OUT / 'calib.csv', index=False)
    print(calib.to_string(index=False, float_format=lambda v: f'{v:.4g}'))

    # ---- the Geant4 chain (the x15) ------------------------------------------- #
    reach = pd.read_csv(GEANT / 'reach_geant.csv')
    acc = pd.read_csv(GEANT / 'acceptance_geant.csv')
    rr = reach[(reach.scenario == 'ATOMKI 2016 anomaly') & (reach.I_uA == 1.0) & (reach.mass == 16.7)
               & (reach.level == 'MM 15° + TOF')].set_index('hw')
    a = acc[(acc['sample'] == 'X17_m16.7')].set_index(['hw', 'level', 'esum'])
    ch = []
    for h in ('as built', 'big plastics'):
        r0 = a.loc[(h, 'trigger', 'none')]
        esum = rr.loc[h].esum.replace('–', '–')
        try:
            r1 = a.loc[(h, 'trigger', esum)]
            r2 = a.loc[(h, 'MM 15° + TOF', esum)]
        except KeyError:
            r1 = a.loc[(h, 'trigger', '13–17')]
            r2 = a.loc[(h, 'MM 15° + TOF', '13–17')]
        ch.append(dict(hw=h, mm_2arm_active=r0.mm_2arm_active, pair_tag=r0.pair_tag, esum_window=r1.acc,
                       mm15_tof=r2.acc, window_125_155=r2.acc_125_155,
                       S_per_day=rr.loc[h].S_ATOMKI, B_ipc_per_day=rr.loc[h].B_ipc, B_g1_per_day=rr.loc[h].B_g1,
                       B_cos_per_day=rr.loc[h].B_cos, B_epc_per_day=rr.loc[h].B_epc,
                       days_count_125_155=rr.loc[h].days_count_live, days_count_opt=rr.loc[h].days_count_opt_live,
                       days_fit=rr.loc[h].days_fisher_1norm_live, esum=rr.loc[h].esum))
    pd.DataFrame(ch).to_csv(OUT / 'chain.csv', index=False)

    # ---- where the leptons land on the plastic plane -------------------------- #
    s = S['X17']
    rows = []
    for L, Lo in ((s.L[0], s.L[1]), (s.L[1], s.L[0])):
        m = s.mm2 & (L.ke > E_TH) & (Lo.ke > E_TH)
        u, v = L.at_plastic(BIG_DEPTH)
        rows.append(pd.DataFrame(dict(u=u[m], v=v[m], arm=L.arm[m],
                                      sipm16=sipm_ok(L, 16)[m], sipm20=sipm_ok(L, 20)[m])))
    fm = pd.concat(rows)
    e = np.arange(-500, 501, 25.0)
    H, _, _ = np.histogram2d(fm.u, fm.v, [e, e])
    H /= H.sum()
    fmap = pd.DataFrame([dict(u_lo=e[i], u_hi=e[i + 1], v_lo=e[j], v_hi=e[j + 1], frac=H[i, j])
                         for i in range(len(e) - 1) for j in range(len(e) - 1)])
    fmap.to_csv(OUT / 'footmap.csv', index=False)
    # fraction of MM-crossing leptons (above E_TH) inside each outline
    au, av = fm.u.abs(), fm.v.abs()
    inside = {'as-built bars (2 × 20×30 cm)': ((au > 1.5) & (au < 200.6) & (av < 150.2)).mean(),
              '16 SiPM bars': fm.sipm16.mean(), '20 SiPM bars': fm.sipm20.mean(),
              '75×75 cm': ((au < 375) & (av < 375)).mean(),
              '75×75 cm and 20 SiPM bars': ((au < 375) & (av < 375) & fm.sipm20).mean()}
    pd.Series(inside, name='frac_leptons').to_csv(OUT / 'footmap_inside.csv')
    print(pd.Series(inside))

    # ---- footprint: largest centred square per distance ----------------------- #
    # Plates of side S whose front faces sit at R from the beam axis: the
    # corner of one plate (at u = S/2 + pinwheel shift) reaches the neighbour's
    # front plane when S/2 + shift > R.  Keep 1 cm of clearance for wrapping.
    CLEAR = 10.0
    fp = pd.DataFrame(dict(R_mm=np.arange(250, 701, 10.0)))
    fp['S_max_mm'] = 2 * (fp.R_mm - SHIFT.max() - CLEAR)
    # MM shadow: the active area projected from the spot onto the plate plane
    fp['mm_shadow_u_mm'] = 2 * MM_HU * fp.R_mm / (DIST.mean() + MM_DW)
    fp['mm_shadow_v_mm'] = 2 * MM_HV * fp.R_mm / (DIST.mean() + MM_DW)
    fp.to_csv(OUT / 'footprint.csv', index=False)

    # ---- days against size ---------------------------------------------------- #
    yields = pd.read_csv(HERE / 'out' / 'yields.csv').set_index('scenario').loc['ATOMKI 2016 anomaly']
    alpha = pd.read_csv(HERE / 'out' / 'ipc_alpha.csv').set_index(['W_MeV', 'multipole']).alpha_pair
    w_m1 = (yields.frac_18_15_res + yields.frac_17_64) * alpha[(18.15, 'M1')]
    w_e1 = yields.frac_direct * alpha[(18.15, 'E1')]

    def sb(plastic, depth, nbars):
        r = np.random.default_rng(77)
        sx = window_counts(S['X17'], pair_tag(S['X17'], E_TH, plastic, depth, nbars), r)
        bm = window_counts(S['M1'], pair_tag(S['M1'], E_TH, plastic, depth, nbars), r)
        be = window_counts(S['E1'], pair_tag(S['E1'], E_TH, plastic, depth, nbars), r)
        return sx, w_m1 * bm + w_e1 * be

    s_ref, b_ref = sb(('square', 750.0), BIG_DEPTH, 20)
    anchor = rr.loc['big plastics']
    D_REF = anchor.days_count_opt_live
    R_REF = DIST.mean() + BIG_DEPTH.mean()
    rows = []
    placements = [
        ('where the bars are now (R = 41 cm), pushed back only if the plates collide', BIG_DEPTH.mean(), 20),
        ('right behind the SiPM wall (R = 35 cm)', SIPM_BACK_DW + 5.0, 20),
        ('SiPM wall removed, right behind the MM (R = 26 cm), plastic-only leg', MM_BACK_DW + 10.0, 0),
    ]
    sizes = np.arange(200, 1201, 25.0)
    for name, dw0, nb in placements:
        for S_mm in sizes:
            R_min = DIST.mean() + dw0
            R = max(R_min, S_mm / 2 + SHIFT.max() + CLEAR)
            dw = R - DIST
            sx, bx = sb(('square', S_mm), dw, nb)
            rows.append(dict(placement=name, sipm_bars=nb, S_mm=S_mm, R_front_mm=R, pushed_back=R > R_min + 0.1,
                             acc_x17_125_155=sx, b_rel=bx / b_ref, s_rel=sx / s_ref,
                             days=D_REF * (bx / b_ref) / (sx / s_ref) ** 2 if sx > 0 else np.nan,
                             plate_area_m2=4 * (S_mm / 1000) ** 2))
    dv = pd.DataFrame(rows)
    # the as-built point on the same scale (geometry only: as-built E_sum etc. not applied)
    sx, bx = sb(('asbuilt',), BIG_DEPTH, 16)
    dv = pd.concat([dv, pd.DataFrame([dict(placement='as-built bars (geometry only)', sipm_bars=16, S_mm=np.nan,
                                           R_front_mm=R_REF, pushed_back=False, acc_x17_125_155=sx,
                                           b_rel=bx / b_ref, s_rel=sx / s_ref,
                                           days=D_REF * (bx / b_ref) / (sx / s_ref) ** 2,
                                           plate_area_m2=4 * 0.4 * 0.3)])])
    dv['days_anchor'] = D_REF
    dv.to_csv(OUT / 'days_vs_size.csv', index=False)
    print(dv.groupby('placement').apply(lambda g: g.iloc[::4][['S_mm', 'R_front_mm', 's_rel', 'days']]).to_string())
    return 0


def figures():
    """lnl/out/plastics/figures/: the footprint map, the x15 chain, days against size."""
    import sys
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    sys.path.insert(0, str(HERE.parent / 'ill'))
    import figstyle as fs
    fs.use()
    F = OUT / 'figures'
    fm = pd.read_csv(OUT / 'footmap.csv')
    ch = pd.read_csv(OUT / 'chain.csv').set_index('hw')
    dv = pd.read_csv(OUT / 'days_vs_size.csv')
    ins = pd.read_csv(OUT / 'footmap_inside.csv', index_col=0).frac_leptons
    fig, axs = plt.subplots(1, 3, figsize=(14, 4.4), gridspec_kw=dict(width_ratios=[1, 1.1, 1.3]))
    ax = axs[0]
    e = np.unique(np.r_[fm.u_lo, fm.u_hi.max()])
    H = fm.pivot(index='v_lo', columns='u_lo', values='frac').values
    ax.pcolormesh(e / 10, e / 10, H, cmap='Greys', shading='flat')
    ax.add_patch(Rectangle((-20.06, -15.02), 19.91, 30.04, fill=False, ec='#D55E00', lw=2))
    ax.add_patch(Rectangle((0.15, -15.02), 19.91, 30.04, fill=False, ec='#D55E00', lw=2,
                           label=f'as-built bars: {ins.iloc[0] * 100:.0f} % of leptons'))
    ax.add_patch(Rectangle((-25 * 41.05 / 33.2, -25 * 41.05 / 33.2), 50 * 41.05 / 33.2, 50 * 41.05 / 33.2, fill=False,
                           ec='#0072B2', lw=1.5, ls='--', label=f'20-bar SiPM wall (shadow): {ins.iloc[2] * 100:.0f} %'))
    ax.add_patch(Rectangle((-37.5, -37.5), 75, 75, fill=False, ec='#009E73', lw=2,
                           label=f'75×75 cm: {ins.iloc[3] * 100:.0f} % ({ins.iloc[4] * 100:.0f} % with the wall)'))
    ax.set_aspect('equal')
    ax.set_xlim(-50, 50)
    ax.set_ylim(-50, 50)
    ax.set_xlabel('across the arm u [cm]')
    ax.set_ylabel('along the beam v [cm]')
    ax.legend(frameon=True, fontsize=7, loc='lower center')
    ax.set_title('X17 leptons through an MM, at the plastic (R 41 cm)', fontsize=8.5)
    ab, bp = ch.loc['as built'], ch.loc['big plastics']
    st = [('both legs tagged\n(pair-tag)', bp.pair_tag / ab.pair_tag),
          ('E_sum window\n(5 cm = calorimeter)', (bp.esum_window / bp.pair_tag) / (ab.esum_window / ab.pair_tag)),
          ('MM 15° + TOF', (bp.mm15_tof / bp.esum_window) / (ab.mm15_tof / ab.esum_window)),
          ('in 125–155°\n(less back-to-back bias)', (bp.window_125_155 / bp.mm15_tof) / (ab.window_125_155 / ab.mm15_tof))]
    S_r = bp.S_per_day / ab.S_per_day
    B_r = (bp.B_ipc_per_day + bp.B_g1_per_day + bp.B_cos_per_day + bp.B_epc_per_day) / (
        ab.B_ipc_per_day + ab.B_g1_per_day + ab.B_cos_per_day + ab.B_epc_per_day)
    ax = axs[1]
    cum = 1.0
    for i, (lab, f) in enumerate(st):
        ax.bar(i, np.log10(f), bottom=np.log10(cum), color=fs.ACCENT if i == 0 else '#b78bbb')
        ax.text(i, np.log10(cum * f) + 0.03, f'×{f:.2f}', ha='center', fontsize=8)
        cum *= f
    ax.bar(4, np.log10(S_r), color=fs.ACCENT)
    ax.text(4, np.log10(S_r) + 0.03, f'S ×{S_r:.1f}', ha='center', fontsize=8)
    ax.bar(5, np.log10(B_r), color='#0072B2')
    ax.text(5, np.log10(B_r) + 0.03, f'B ×{B_r:.1f}', ha='center', fontsize=8)
    ax.set_xticks(range(6), [x for x, _ in st] + ['X17 signal\nper day', 'IPC background\nper day'], fontsize=6.5, rotation=35, ha='right')
    ax.set_yticks(np.log10([1, 2, 5, 10, 20]), ['×1', '×2', '×5', '×10', '×20'])
    ax.set_title(f'Geant4: days ∝ B/S² → ×{S_r ** 2 / B_r:.0f} '
                 f'({ab.days_count_125_155:.0f} → {bp.days_count_125_155:.1f} d)', fontsize=8.5)
    ax = axs[2]
    cols = ['#0072B2', '#009E73', '#D55E00']
    for (pl, g), c in zip([(p, dv[dv.placement == p]) for p in dv.placement.unique() if not p.startswith('as-built')], cols):
        g = g.sort_values('S_mm')
        ax.plot(g.S_mm / 10, g.days, color=c, lw=1.8, label=pl)
        pb = g[g.pushed_back]
        ax.plot(pb.S_mm / 10, pb.days, color=c, lw=4, alpha=0.25)
    ab_ = dv[dv.placement.str.startswith('as-built')].iloc[0]
    ax.axhline(ab_.days, color=fs.MUTED, ls=':', lw=1)
    ax.text(21, ab_.days * 1.08, f'as-built bars, same cuts: {ab_.days:.0f} d', fontsize=7, color=fs.MUTED)
    ax.plot([75], [dv.days_anchor.iloc[0]], 'o', color='k', ms=5)
    ax.text(77, dv.days_anchor.iloc[0] * 0.8, 'Geant4 75×75', fontsize=7)
    ax.set_yscale('log')
    ax.set_ylim(0.5, 60)
    ax.set_xlim(20, 120)
    ax.set_xlabel('side of a square plastic, 5 cm thick [cm]')
    ax.set_ylabel('days to 3σ at R(ATOMKI), 1 µA')
    ax.legend(frameon=False, fontsize=6.3, loc='upper right')
    ax.set_title('Days vs plastic size (toy anchored to Geant4)\nthick line = plates pushed back to clear their neighbours', fontsize=8.5)
    fs.fig_title(fig, 'The big plastics win by acceptance: ×7 more pairs tagged, and the IPC rides along',
                 'Left/right: geometric toy calibrated on the Geant4 pair-tag (lnl/plastic_size.py, an analytic stand-in). '
                 'Middle: Geant4 X17 chain and per-day rates (reach_geant.csv)')
    fs.save(fig, F / 'plastics_size', data=dv)


if __name__ == '__main__':
    import sys as _s
    if '--figs' in _s.argv:
        figures()
        raise SystemExit(0)
    rc = main()
    figures()
    raise SystemExit(rc)
