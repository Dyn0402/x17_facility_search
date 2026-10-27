#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
opt_shell_material.py -- what the ogive of Pierfrancesco's sketch (§19, body A: wall 0.2, Ø50 × 63.2, tip R 3)
should be made of.  TARGET_OPTIONS.md §20.  Dylan (27 Oct): "is Be actually feasible?  machinable, affordable,
holds the vacuum, attaches to the beam pipe?"  Everything here is ESTIMATE (closed-form shell formulas and a 1D
fin), to be replaced by an FEA from the LNL mechanical office before anything is ordered.

    ~/PycharmProjects/nTof_x17/.venv/bin/python lnl/target/opt_shell_material.py

Writes to out/target/options/:
  shell_materials.csv   per material and wall: 1 bar stresses, buckling pressure, tip heat, thermal stress
  shell_thermal.csv     peak tip temperature rise vs current, h and spot size
  shell_trace.csv       x/X0 per leg and σ68 (the §17/§19 ray-trace, ESTIMATE) with the Mo liner included
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import opt_shapes as SH   # noqa: E402
import opt_sketch as SK   # noqa: E402

OUT = SH.OUT
P_ATM = 0.1013            # MPa
EP_MEV = 1.03             # beam energy: all of it ends up as heat in the shell (Li + liner + wall)
T_LI_MAX = 150.0          # °C, Li film limit used in §3 (melts at 180.5)
T_AIR = 25.0

# Room-temperature handbook values.  E GPa, sy = 0.2 % yield MPa, uts MPa, elong %, k W/m/K, alpha 1e-6/K.
# Be: Materion S-200FH datasheet (E 303, sy 296, 3 %; S-200F: 241 MPa, 2 %), ν 0.07 (Be is unusually low; 0.03–0.1
# in the literature).  AlBeMet AM162 (62 Be / 38 Al wt%): Materion.  Al 6061-T6, Al 1050-O, OFHC Cu (annealed and
# half-hard), Ti grade 2: ASM handbook.  X0 [mm] from opt_shapes.X0; AlBeMet by mass fractions (Be 65.19, Al 24.01
# g/cm², ρ 2.071).
MAT = {
    'Be S-200FH':   dict(E=303., nu=0.07, sy=296., uts=414., elong=3., k=216., alpha=11.4, X0=352.8, xmat='Be'),
    'AlBeMet 162':  dict(E=193., nu=0.17, sy=193., uts=262., elong=7., k=210., alpha=13.9, X0=190.8, xmat='AlBe'),
    'Al 6061-T6':   dict(E=69., nu=0.33, sy=276., uts=310., elong=12., k=167., alpha=23.6, X0=88.97, xmat='Al'),
    'Al 1050-O':    dict(E=69., nu=0.33, sy=28., uts=76., elong=39., k=229., alpha=24.0, X0=88.97, xmat='Al'),
    'Cu OFHC ann.': dict(E=115., nu=0.34, sy=69., uts=220., elong=45., k=391., alpha=17.0, X0=14.36, xmat='Cu'),
    'Ti grade 2':   dict(E=105., nu=0.37, sy=275., uts=345., elong=20., k=16.4, alpha=8.6, X0=35.6, xmat='Ti'),
}
SH.X0['AlBe'] = 190.8
K_MO, T_MO = 138., 8e-6   # the Mo liner (W/m/K, m)


# ---- the meridian of body A (inner surface), tip → base -------------------------------------------------
def meridian(n=1200):
    """s [mm] along the wall from the tip, r [mm], and the local half-angle α (wall to the beam axis)."""
    c, R = SK.TIP_C, SK.TIP_RI
    a0 = np.arcsin((SK.Y_CAP_I - c) / R)
    ang = np.linspace(np.pi / 2, a0, 80)                     # tip sphere, from the apex down to the flank
    r_cap, y_cap = R * np.cos(ang), c + R * np.sin(ang)
    y_fl = np.linspace(SK.Y_CAP_I, SK.Y_BASE, n)[1:]
    r_fl = SK.lemon_r(y_fl, SK.A_IN)
    r, y = np.r_[r_cap, r_fl], np.r_[y_cap, y_fl]
    s = np.r_[0, np.cumsum(np.hypot(np.diff(r), np.diff(y)))]
    alpha = np.arctan2(np.gradient(r), -np.gradient(y))      # 90° at the apex, 25° → 15° on the flank
    return s, r, alpha


# ---- 1 bar from outside: membrane stresses, the clamped base, buckling --------------------------------------
def pressure(m, t_mm, p=P_ATM):
    """Membrane hoop/meridional stress of a cone at the base (r 24.8, α 15°), the bending peak where the base is
    clamped into an adapter (√3 pR₂/(t√(1−ν²)), the clamped-cylinder edge), and the buckling pressure of the flank
    as a cone under external pressure (NASA SP-8019 equivalent cylinder of slant length L and radius ρ̄ = r̄/cos ᾱ,
    lateral-pressure formula of SP-8007, knockdown γ = 0.56).  The lemon's meridian bulges outwards, which
    stiffens it, so the cone value is conservative."""
    s, r, alpha = meridian()
    fl = r > 2.6
    rb, ab = r[-1], alpha[-1]
    R2 = rb / np.cos(ab)
    hoop = p * R2 / t_mm
    merid = p * R2 / (2 * t_mm)
    clamp = np.sqrt(3) * p * R2 / (t_mm * np.sqrt(1 - m['nu'] ** 2))
    L = s[fl][-1] - s[fl][0]
    abar = np.average(alpha[fl], weights=np.gradient(s[fl]))
    rho = 0.5 * (r[fl][0] + r[fl][-1]) / np.cos(abar)
    p_cl = 0.855 * m['E'] * 1e3 / (1 - m['nu'] ** 2) ** 0.75 * (t_mm / rho) ** 2.5 / (L / rho)
    return dict(hoop_MPa=hoop, merid_MPa=merid, clamp_MPa=clamp, buckle_classical_bar=10 * p_cl,
                buckle_bar=10 * 0.56 * p_cl, L_mm=L, rho_eq_mm=rho, alpha_mean_deg=np.degrees(abar))


# ---- heat: the wall as an axisymmetric fin along its meridian ----------------------------------------------
def tip_heat(kt, h, I_uA, sigma=2.0, T_base=0.0, n=1200):
    """d/ds(kt 2πr dT/ds) − h 2πr T + Q(s) = 0, T(base) = T_base (above the air), dT/ds = 0 at the apex.
    The beam (Gaussian, σ per axis [mm]) runs along the axis, so a proton at radius ρ lands where r(s) = ρ:
    the power landing between r and r + dr is P (r/σ²) exp(−r²/2σ²) dr.  Air on the outside only (the inside is
    vacuum); radiation is negligible below ~200 °C for these metals.  Returns s, r, T (K above the air)."""
    s, r, _ = meridian(n)
    S, Rm = s * 1e-3, np.maximum(r, 1e-4) * 1e-3
    P = EP_MEV * I_uA                                                            # W
    cdf = 1 - np.exp(-(r ** 2) / (2 * sigma ** 2))
    Q = P * np.diff(np.r_[0, 0.5 * (cdf[1:] + cdf[:-1]), 1.0])                  # W per node (sums to P)
    N = len(S)
    A = np.zeros((N, N))
    b = -Q.copy()
    for i in range(N - 1):
        ds = S[i + 1] - S[i]
        G = kt * 2 * np.pi * 0.5 * (Rm[i] + Rm[i + 1]) / ds                      # W/K
        A[i, i] -= G
        A[i, i + 1] += G
        A[i + 1, i + 1] -= G
        A[i + 1, i] += G
    dsn = np.gradient(S)
    A[np.arange(N), np.arange(N)] -= h * 2 * np.pi * Rm * dsn
    A[-1, :] = 0
    A[-1, -1], b[-1] = 1.0, T_base
    return s, r, np.linalg.solve(A, b)


def thermal_bending(m, t_mm, s, r, T):
    """Thermal stress in the hot tip (ESTIMATE).  A shell whose temperature varies along its meridian bends
    where the free radial growth α r T changes fastest: σ_b ≈ E α R₂ t |T″| / (2(1−ν²)) (thin cylinder with a
    slowly varying T(z), valid while the gradient length ≫ √(R₂t)).  Here the gradient length near the tip is
    ~3 mm and √(R₂t) ~ 0.8 mm, so read it to a factor ~2.  Returns MPa."""
    sm = s * 1e-3
    d2 = np.gradient(np.gradient(T, sm), sm)
    R2 = r * 1e-3 / np.cos(np.radians(20.0))
    sel = (r > 2.8) & (r < 20)
    sig = m['E'] * 1e9 * m['alpha'] * 1e-6 * R2 * t_mm * 1e-3 * np.abs(d2) / (2 * (1 - m['nu'] ** 2))
    return float(np.max(sig[sel]) / 1e6)


# ---- what the leptons see: the §19 trace with the liner included -------------------------------------------
class Scaled(SK.Ogive):
    """a layer of t_um on the 200 µm CAD wall, traced as the wall's path × t_um/200 (exact away from grazing)."""
    def __init__(self, mat, t_um):
        super().__init__(mat)
        self.f = t_um / 200.0

    def path(self, p, u):
        return self.f * SK.ogive_path(p, u)


def lepton_trace():
    V, U, T = SH.legs()
    tr = pd.read_csv(OUT / 'shapes_trace.csv')
    cal = tr[tr.kind.str.startswith('flat')]
    A = np.c_[np.ones(len(cal)), cal.sig_ms ** 2]
    (s2, k2), *_ = np.linalg.lstsq(A, cal.sigma68_g4 ** 2, rcond=None)
    cases = [('Cu', 200, 0), ('Be', 200, 8), ('Be', 300, 8), ('Be', 500, 8), ('AlBe', 300, 8),
             ('Al', 200, 8), ('Al', 300, 8), ('Al', 400, 8), ('Ti', 100, 0), ('Be', 200, 0), ('Al', 200, 0)]
    rows = []
    for mat, t, mo in cases:
        geo = [Scaled(mat, t)] + ([Scaled('Mo', mo)] if mo else [])
        r = SH.trace(geo, V, U, T, SK.on_ogive)
        rows.append(dict(config=f'{mat} {t} µm' + (f' + Mo {mo} µm' if mo else ''), x_med_pct=100 * r['x_med'],
                         f_pair_gt1pct=r['f_pair_gt1pct'], p_conv_18MeV=r['p_conv'],
                         sigma68_trace=float(np.sqrt(s2 + k2 * r['sig_ms'] ** 2))))
    g, n = SH.window(layers=(('Mo', 8), ('Dia', 200)), R=10.0, tilt_deg=45, ring_mm=0.5, ring_w=5.0, ring_mat='Ti',
                     tube='Al', tube_t=0.5)
    r = SH.trace(g, V, U, T, SH.on_plane(n))
    rows.append(dict(config='ref: our window Ø20, 45°, diamond 200, Ti rings, Al end 0.5', x_med_pct=100 * r['x_med'],
                     f_pair_gt1pct=r['f_pair_gt1pct'], p_conv_18MeV=r['p_conv'],
                     sigma68_trace=float(np.sqrt(s2 + k2 * r['sig_ms'] ** 2))))
    return pd.DataFrame(rows)


def main():
    pd.set_option('display.width', 250)
    rows, th = [], []
    walls = {'Be S-200FH': (0.2, 0.3, 0.5), 'AlBeMet 162': (0.3,), 'Al 6061-T6': (0.2, 0.3, 0.4),
             'Al 1050-O': (0.2, 0.3), 'Cu OFHC ann.': (0.2,), 'Ti grade 2': (0.1, 0.2)}
    for name, ts in walls.items():
        m = MAT[name]
        for t in ts:
            pr = pressure(m, t)
            kt = m['k'] * t * 1e-3 + K_MO * T_MO
            s, r, T4 = tip_heat(kt, 100, 4.0)
            # max current for the Li at 150 °C with the base held at the air (+10 K for the joint) and h = 100
            dT1 = tip_heat(kt, 100, 1.0)[2][0]
            row = dict(material=name, wall_mm=t, X0_pct_normal=100 * t / m['X0'], **pr,
                       SF_yield_clamp=m['sy'] / pr['clamp_MPa'], SF_buckle=pr['buckle_bar'] / 1.013,
                       dT_tip_4uA_h100=T4[0], I_max_uA=(T_LI_MAX - T_AIR - 10) / dT1,
                       sig_th_4uA_MPa=thermal_bending(m, t, s, r, T4))
            rows.append(row)
            for I in (0.5, 4.0, 10.0):
                for h in (30, 100, 300, 1000):
                    for sg in (2.0, 0.5):
                        th.append(dict(material=name, wall_mm=t, I_uA=I, h=h, sigma_mm=sg,
                                       dT_tip=tip_heat(kt, h, I, sigma=sg)[2][0]))
    df, tdf = pd.DataFrame(rows), pd.DataFrame(th)
    df.to_csv(OUT / 'shell_materials.csv', index=False)
    tdf.to_csv(OUT / 'shell_thermal.csv', index=False)
    print(df.to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    piv = tdf[(tdf.sigma_mm == 2.0) & (tdf.I_uA == 4.0)].pivot_table(index=['material', 'wall_mm'], columns='h',
                                                                        values='dT_tip')
    print('\npeak tip rise above the air [K], 4 µA (4.1 W), σ 2 mm, base at the air:\n', piv.round(0).to_string())
    piv = tdf[(tdf.sigma_mm == 0.5) & (tdf.I_uA == 4.0)].pivot_table(index=['material', 'wall_mm'], columns='h',
                                                                        values='dT_tip')
    print('\nsame, beam focused to σ 0.5 mm:\n', piv.round(0).to_string())
    lt = lepton_trace()
    lt.to_csv(OUT / 'shell_trace.csv', index=False)
    print('\n', lt.to_string(index=False, float_format=lambda v: f'{v:.3g}'))


if __name__ == '__main__':
    main()
