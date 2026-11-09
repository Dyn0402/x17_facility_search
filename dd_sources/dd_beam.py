#!/usr/bin/env python3
"""
dd_beam.py -- intense D-D neutron sources for the X17 study (dd_sources/FACILITY.md, FEASIBILITY.md).

    python dd_sources/dd_beam.py --check       # reproduce bham_26_2m_pb5 with the shared engine
    python dd_sources/dd_beam.py               # beam model + reach -> dd_sources/out/dd_*.csv, .png

Source model (ESTIMATE unless marked):
  sigma        Bosch & Hale 1992 D(d,n)3He S-factor (published fit, valid to E_cm ~ 4.9 MeV).
  stopping     D in D per atom, velocity-scaled Andersen-Ziegler form for H (ESTIMATE, +/-15 %).
  yield        thick windowless D2 gas: Y(E_d) = int sigma/eps dE. Anchored to the only measured
               high-yield number: Phoenix 3e11 n/s at 300 kV (current not public, implied ~35 mA).
               Solid Ti-D target: ×0.07 of gas, from FNG (1 mA, 300 keV, 5.7e8 n/s measured).
  angle        CM W(c) = 1 + A c^2 (ESTIMATE; A rises with E_d).
Geometry: the cell (30 bar, R 5, L 40 cm) sits on its axis upstream of the arms; the source is a point
  (or a short line) at distance d from the front window. G = (1/L) int_V dV / (4 pi r^2): the parallel-
  beam-equivalent fraction of source neutrons, replacing the engine's "n through the Ø8 cm spot".
Background: the engine (N5, G5/G6 re-weighted) for the beam through the cell, plus two ESTIMATE terms
  N5 does not contain: direct flux from the 4pi source onto the arms through a shadow shield, and the
  room return.
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
OUT.mkdir(exist_ok=True)
sys.path.insert(0, str(ROOT / 'survey' / 'soft_sim'))
sys.path.insert(0, str(ROOT / 'ill'))

E_CHARGE = 1.602176634e-19
D_PER_MA = 1e-3 / E_CHARGE
M_D, M_N, M_HE3 = 2.01410, 1.00866, 3.01603
Q_DD = 3.269                        # MeV
SOLID_FACTOR = 0.07                 # ESTIMATE: FNG 5.7e8 n/s at 1 mA, 300 keV, vs the gas model (TiD)
PHOENIX_Y = 3e11                    # measured (IPAC 2018 TUYGBF2)
CELL_R, CELL_L = 5.0, 40.0          # cm, the 30 bar cell
ARM_FACE, ARM_X, ARM_Z = 20.4, 20.0, 18.0   # cm: face distance, half-widths of the MM active area
TVL_PE = 12.0                       # cm, ESTIMATE: 2.45 MeV n in borated PE (uncollided 8 cm; broad beam ~12-15)
EPS_LEG = 1.6e-3                    # ESTIMATE: legs per 2.45 MeV n striking an arm (N5 legs / scatter-to-arm ~1.7e-2)
EPS_OK = 3e-6                       # ESTIMATE: ok singles per n striking an arm (N5, 5 MC events; ±×3)
P_ROOM_LEG = 1e-7                   # ESTIMATE: legs per arm per source neutron from the room (S ~ 150 m²)
ROOM_OK_FRAC = 0.05                 # ok singles / legs of the room return (Birmingham/FRANZ-like)
REF_N = 1e9


def sigma_mb(e_cm_kev):
    e = np.asarray(e_cm_kev, float)
    bg = 31.3970
    s = 5.3701e4 + e * (3.3027e2 + e * (-1.2706e-1 + e * (2.9327e-5 + e * (-2.5151e-9))))
    with np.errstate(divide='ignore', invalid='ignore'):
        return np.where(e > 0.5, s / (e * np.exp(bg / np.sqrt(e))), 0.0)


def eps_ev(ed_kev):
    """stopping of D in D [1e-15 eV cm²/atom]; velocity scaling of H in H (Andersen-Ziegler form)."""
    e = np.maximum(ed_kev / 2.0, 1e-3)
    lo = 1.44 * e ** 0.45
    hi = (242.6 / e) * np.log(1 + 1.2e4 / e + 0.1159 * e)
    return 1 / (1 / lo + 1 / hi)


GRID = np.linspace(2.0, 3000.0, 3000)                     # keV deuteron energy


def thick_y_per_d(ed_kev):
    e = GRID[GRID <= ed_kev]
    # sigma [mb → cm²], eps [1e-15 eV cm²/atom], dE in eV:
    return float(np.trapezoid(sigma_mb(e / 2.0) * 1e-27 / (eps_ev(e) * 1e-15) * 1e3, e))


A_PHOENIX_MA = PHOENIX_Y / (thick_y_per_d(300.0) * D_PER_MA)     # implied mA at 300 kV, gas (no molecular-ion correction)


def yield_n_s(ed_kev, i_ma, solid=False):
    return thick_y_per_d(ed_kev) * D_PER_MA * i_ma * (SOLID_FACTOR if solid else 1.0)


def aniso(ed_kev):
    return 0.3 + 1.2 * np.minimum(np.asarray(ed_kev, float) / 1000.0, 1.5)    # ESTIMATE


def kin(ed_mev, cos_cm):
    """lab E_n and cos(lab) for CM cosine."""
    m = M_D + M_D
    e_cm_f = Q_DD + ed_mev * M_D / m
    mu = M_N * M_HE3 / (M_N + M_HE3)
    vn_cm = np.sqrt(2 * mu * e_cm_f) / M_N
    v_c = np.sqrt(2 * ed_mev / M_D) * M_D / m
    vz = vn_cm * cos_cm + v_c
    vx = vn_cm * np.sqrt(1 - cos_cm ** 2)
    v2 = vx ** 2 + vz ** 2
    return 0.5 * M_N * v2, vz / np.sqrt(v2)


def spectrum(ed_kev, theta_deg, half=15.0, n=400_000, seed=4):
    """thick-target spectrum at lab angle θ±half: dY/dΩ [n/deuteron/sr], E grid, mean E, fraction of 4π."""
    rng = np.random.default_rng(seed)
    ed = rng.uniform(2.0, ed_kev, n)
    w = sigma_mb(ed / 2.0) * 1e-27 / (eps_ev(ed) * 1e-15) * 1e3 * (ed_kev - 2.0) / n
    c = rng.uniform(-1, 1, n)
    A = aniso(ed)
    w = w * (1 + A * c ** 2) / (1 + A / 3)
    en, cl = kin(ed / 1000.0, c)
    tl = np.degrees(np.arccos(cl))
    sel = np.abs(tl - theta_deg) < half
    th0, th1 = np.radians(max(theta_deg - half, 0)), np.radians(min(theta_deg + half, 180))
    dom = 2 * np.pi * (np.cos(th0) - np.cos(th1))
    return en[sel], w[sel] / dom, float(w.sum())


def spectrum_on_grid(ed_kev, theta, e_grid, smooth=0.0):
    en, w, _ = spectrum(ed_kev, theta)
    h, ed = np.histogram(en, 400, range=(0.0, 12.0), weights=w)
    x = 0.5 * (ed[1:] + ed[:-1])
    if smooth > 0:
        y = np.zeros_like(e_grid)
        for xi, hi in zip(x[h > 0], h[h > 0]):
            y += hi * np.exp(-0.5 * ((e_grid - xi) / (smooth * xi)) ** 2) / (smooth * xi)
    else:
        y = np.interp(e_grid, x, h, left=0, right=0)
    return y / np.trapezoid(y, e_grid)


def geom_factor(d, line=0.0, n=400_000, seed=7):
    """G = (1/L) int_V dV/(4π r²): parallel-beam-equivalent fraction of source n.  Point on the cell axis
    at distance d from the front (or a transverse line of full length `line`), arbitrary d."""
    rng = np.random.default_rng(seed)
    z = rng.uniform(0, CELL_L, n)
    r = CELL_R * np.sqrt(rng.uniform(0, 1, n))
    ph = rng.uniform(0, 2 * np.pi, n)
    xs = rng.uniform(-line / 2, line / 2, n) if line else 0.0
    r2 = (r * np.cos(ph) - xs) ** 2 + (r * np.sin(ph)) ** 2 + (z + d) ** 2
    vol = np.pi * CELL_R ** 2 * CELL_L
    return float((1 / (4 * np.pi * r2)).mean() * vol / CELL_L)


def arm_transmission(d, tvl=TVL_PE, shield=True, n=200_000, seed=9, r_in=8.0):
    """direct flux on one arm per source neutron, with a shadow shield. Point source on the axis at
    z_s = -(CELL_L/2 + d); arm face at r=ARM_FACE, |x|<ARM_X, |z|<ARM_Z.  Shield = BPE filling every
    ray from r_in out to the arm, except the cone that subtends the cell front (open bore)."""
    rng = np.random.default_rng(seed)
    zs = -(CELL_L / 2 + d)
    x = rng.uniform(-ARM_X, ARM_X, n)
    z = rng.uniform(-ARM_Z, ARM_Z, n)
    dx, dy, dz = x, np.full(n, ARM_FACE), z - zs
    r = np.sqrt(dx * dx + dy * dy + dz * dz)
    cos_i = dy / r
    frac = (ARM_X * ARM_Z * 4) * (cos_i / (4 * np.pi * r * r)).mean()
    if not shield:
        return dict(frac_unshielded=float(frac), T=1.0, mean_t_cm=0.0, frac=float(frac))
    # Keep-out: tracks need the region between the cell and the arms clear, so shielding is only allowed
    # upstream of the cell's front plane (z < -CELL_L/2). Ray length with z below that plane, minus the source shroud.
    frac_up = np.clip((-CELL_L / 2 - zs) / np.maximum(z - zs, 1e-9), 0.0, 1.0)
    t = np.maximum(frac_up * r - r_in - 3.0, 0.0)
    T = 10.0 ** (-t / tvl)
    f = (ARM_X * ARM_Z * 4) * (cos_i / (4 * np.pi * r * r) * T).mean()
    return dict(frac_unshielded=float(frac), T=float(f / frac), mean_t_cm=float(t.mean()), frac=float(f))


# ---------------------------------------------------------------- reach
def ang_factor(ed_kev, theta):
    """dY/dOmega at this lab angle / 4pi average: the anisotropy the point-source G does not include."""
    _, w, tot = spectrum(ed_kev, theta)
    return float(w.sum() * 4 * np.pi / tot)


def make_source(SR, key, ed_kev, theta, g=0.0):
    fn_true = spectrum_on_grid(ed_kev, theta, SR.E_GRID)
    fn_smooth = spectrum_on_grid(ed_kev, theta, SR.E_GRID, smooth=0.12)
    s = SR.Soft(key, key, fn_true, REF_N, np.zeros_like(SR.E_GRID), 0.0, 'dd')
    b = SR.Soft(key, key, fn_smooth, REF_N, np.zeros_like(SR.E_GRID), 0.0, 'dd')
    return s, b


def add_direct(C, ok_ref, leg_ref):
    """engine components + a direct arm load per unit k (same k scaling as the engine)."""
    o0 = C['ok_arm'].sum()
    ok = C['ok_arm'] + ok_ref
    leg = C['leg_arm'] + leg_ref
    return dict(C, ok_arm=ok, leg_arm=leg, acc_th=C['acc_th'] * (ok.sum() / max(o0, 1e-30)) ** 2)


CONFIGS = [
    # name, E_d keV, theta, I mA, solid, line, what
    ('adelphi_1e10', 150.0, 90.0, None, True, 0.0, 'Adelphi DD-110 class, rated 1e10 n/s, compact Ti target'),
    ('astral_mk2_1e10', 150.0, 90.0, None, True, 0.0, 'Astral Mk2 (vendor claim 1e10 D-D, not independent)'),
    ('phoenix_3e11', 300.0, 90.0, 35.0, False, 40.0, 'Phoenix 300 kV gas, measured 3e11, cell at 90°'),
    ('phoenix_0deg', 300.0, 0.0, 35.0, False, 40.0, 'same at 0° (E_n ~3.2 MeV: out of the window)'),
    ('phoenix_135', 300.0, 135.0, 35.0, False, 40.0, 'Phoenix 300 kV gas, measured 3e11, cell at 135°'),
    ('need_1e12', 300.0, 90.0, 117.0, False, 40.0, 'hypothetical 1e12 D-D'),
    ('need_3e12', 300.0, 90.0, 350.0, False, 40.0, 'hypothetical 3e12 D-D (catalogue "need")'),
    ('need_1e13', 300.0, 90.0, 1170.0, False, 40.0, 'hypothetical 1e13 D-D'),
    ('dacc_0p75_5mA', 750.0, 90.0, 5.0, False, 10.0, 'deuteron accelerator 0.75 MeV, 5 mA, gas cell, 90°'),
    ('dacc_1p5_5mA', 1500.0, 90.0, 5.0, False, 10.0, 'deuteron 1.5 MeV, 5 mA (SPIRAL2-RFQ class), 90°'),
    ('dacc_1p5_5mA_135', 1500.0, 135.0, 5.0, False, 10.0, 'deuteron 1.5 MeV, 5 mA, 135°'),
    ('dacc_2p0_10mA', 2000.0, 90.0, 10.0, False, 10.0, 'deuteron 2 MeV, 10 mA, gas cell, 90°'),
    ('dacc_2p0_10mA_135', 2000.0, 135.0, 10.0, False, 10.0, 'deuteron 2 MeV, 10 mA, 135°'),
]
YIELD_OVERRIDE = {'adelphi_1e10': 1e10, 'astral_mk2_1e10': 1e10, 'phoenix_3e11': 3e11, 'phoenix_0deg': 3e11, 'phoenix_135': 3e11,
                  'need_1e12': 1e12, 'need_3e12': 3e12, 'need_1e13': 1e13}
DIST = (15.0, 25.0, 35.0, 50.0, 75.0, 100.0, 250.0)
SHIELD_MODES = ('none', 'shadow')


def run(days=(14.0, 50.0), check=False):
    import soft_reach as SR
    SF, R, Y = SR.SF, SR.R, SR.Y
    if check:
        srcs = [s for s in SR.sources() if s.key == 'bham_26_2m_pb5']
        for hw in R.HW:
            M = SF.nfs_model(hw); runs = SR.load_runs(hw)
            C = SR.components(srcs[0], runs, hw, M); cap = SR.captures(srcs[0])
            for d in days:
                res = [(SR.rho3(M, SR.at_throttle(srcs[0], C, M, cap, s), d, True), s) for s in np.geomspace(1e-4, 1, 41)]
                print(f'{hw:13s} {d:4.0f} d rho3 = {min(res)[0]:.4g}')
        return
    rows, comps = [], []
    grid = np.geomspace(1e-3, 1.0, 31)
    for hw in R.HW:
        M = SF.nfs_model(hw); runs = SR.load_runs(hw)
        cache = {}
        for name, ed, th, ima, solid, line, what in CONFIGS:
            ck = (ed, th)
            if ck not in cache:
                st, bs = make_source(SR, f'{ed:.0f}_{th:.0f}', ed, th)
                C = SR.components(bs, runs, hw, M)
                cache[ck] = (st, C, SR.captures(st))
                print(f'{hw:13s} {ck} ok/arm {C["ok_arm"].mean():.3g} legs/arm {C["leg_arm"].mean():.3g}'
                      f' corr {C["corr_fact"]:.3g}/d ({C["corr_n_mc"]} MC) per 1e9 n', flush=True)
            st, C, cap = cache[ck]
            Y0 = YIELD_OVERRIDE.get(name) or yield_n_s(ed, ima, solid)
            for d in DIST:
                G = geom_factor(d, line) * ang_factor(ed, th)
                for mode in SHIELD_MODES:
                    arm = arm_transmission(d, shield=(mode == 'shadow'))
                    k = Y0 * G / REF_N
                    leg_dir = Y0 * arm['frac'] * EPS_LEG
                    ok_dir = Y0 * arm['frac'] * EPS_OK
                    leg_room = Y0 * P_ROOM_LEG
                    C2 = add_direct(C, np.full(4, (ok_dir + leg_room * ROOM_OK_FRAC) / k),
                                    np.full(4, (leg_dir + leg_room) / k))
                    C_beam_only = C
                    comps.append(dict(key=name, hw=hw, d_cm=d, shield=mode, Y=Y0, G=G, n_cell_eff=Y0 * G,
                                      naive_spot_8cm=Y0 * 50.0 / (4 * np.pi * (d + CELL_L / 2) ** 2),
                                      legs_arm_beam=C['leg_arm'].mean() * k, legs_arm_direct=leg_dir, legs_arm_room=leg_room,
                                      ok_arm_beam=C['ok_arm'].mean() * k, ok_arm_direct=ok_dir, ok_arm_room=leg_room * ROOM_OK_FRAC,
                                      T_shield=arm['T'], frac_arm_unsh=arm['frac_unshielded']))
                    for ver, CC in (('full', C2), ('beam_only', C_beam_only)):
                        for dd in days:
                            res = []
                            for s in grid:
                                st1 = SR.at_throttle(st, CC, M, cap, s * k)
                                res.append((SR.rho3(M, st1, dd, True), SR.rho3(M, st1, dd, False), s, st1))
                            r, ra, s, st1 = min(res, key=lambda x: x[0])
                            ra_best = min(x[1] for x in res)
                            st0 = SR.at_throttle(st, dict(C, acc_th=C['acc_th'] * 0, corr_th=C['corr_th'] * 0,
                                                          ok_arm=C['ok_arm'] * 0, leg_arm=C['leg_arm'] * 0, corr_trig=0.0),
                                                 M, cap, k)
                            rows.append(dict(key=f'{name}_{d:.0f}cm_{mode}_{ver}', source=name, what=what, Y=Y0, E_d_keV=ed,
                                             theta=th, d_cm=d, shield=mode, model=ver, hw=hw, days=dd,
                                             rho3=r, rho3_all=ra_best, rho3_floor=SR.rho3(M, st0, dd, True),
                                             vs_ATOMKI=r / R.RHO_REF, throttle=s, live=st1['live'], occ=st1['occ'],
                                             days_to_atomki=50 * (r / R.RHO_REF) ** 2 if dd == 50 else np.nan,
                                             signal='E* ≤ 22 MeV', **SR.window_counts(st1, M, True)))
    t = pd.DataFrame(rows)
    t.to_csv(OUT / 'dd_reach.csv', index=False, float_format='%.4g')
    pd.DataFrame(comps).to_csv(OUT / 'dd_components.csv', index=False, float_format='%.4g')
    return t


def tables():
    rows = []
    for ed in (100, 150, 300, 500, 750, 1000, 1500, 2000):
        y = thick_y_per_d(float(ed))
        for th in (0.0, 45.0, 90.0, 135.0):
            en, w, _ = spectrum(float(ed), th)
            sw = w.sum()
            rows.append(dict(E_d_keV=ed, theta=th, Y_per_d=y, Y_n_s_per_mA_gas=y * D_PER_MA,
                             mean_En=float((en * w).sum() / sw), emin=float(en.min()), emax=float(en.max()),
                             f_in_window=float(w[en <= 2.75].sum() / sw), rel_yield_sr=float(sw * 4 * np.pi / (y if y else 1))))
    a = pd.DataFrame(rows)
    a.to_csv(OUT / 'dd_kinematics.csv', index=False, float_format='%.4g')
    g = pd.DataFrame([dict(d_cm=d, G_point=geom_factor(d), G_line40=geom_factor(d, 40.0),
                           G_over_naive_frontface=geom_factor(d) / (50 / (4 * np.pi * d ** 2)),
                           G_over_naive_center=geom_factor(d) / (50 / (4 * np.pi * (d + 20) ** 2)),
                           arm_frac_unsh=arm_transmission(d, shield=False)['frac'],
                           arm_T_shadow=arm_transmission(d)['T'],
                           mean_t_cm=arm_transmission(d)['mean_t_cm'],
                           arm_T_tvl_8=arm_transmission(d, tvl=8.0)['T'], arm_T_tvl_20=arm_transmission(d, tvl=20.0)['T'])
                      for d in (5, 10, 15, 25, 35, 50, 75, 100, 150, 250)])
    g.to_csv(OUT / 'dd_geometry.csv', index=False, float_format='%.4g')
    return a, g


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    if a.check:
        run(check=True); sys.exit()
    print(f'implied Phoenix current {A_PHOENIX_MA:.0f} mA; check FNG-model {yield_n_s(300.0, 1.0, True):.3g} (5.7e8)')
    pd.set_option('display.width', 250)
    x, y = tables()
    print(x.to_string(index=False)); print(y.to_string(index=False))
    run()
