#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
target_model.py -- what can go wrong with a thin lithium target in a ⁸Be X17
run, in numbers.  (lnl/target/TARGET_STUDY.md, 2026-10-22)

    python lnl/target/target_model.py          # -> lnl/out/target/*.csv, figures

Everything is analytic or a 1D/2D numerical model, anchored to published data
where they exist.  The ⁸Be cross sections and stopping powers are those of
lnl_rates.py (Zahnow 1995, PSTAR); this file adds:

  layered targets   a proton slowing down through an arbitrary stack (carbon
                    on the front, the film, lithium that has diffused into the
                    backing, the backing) -> the ⁸Be capture mix (17.64 M1 from
                    the 441 keV resonance, 18.15 M1, direct E1) per layer.
  ¹⁹F               ¹⁹F(p,α_π)¹⁶O* -> the 6.05 MeV E0 pair line, from
                    Redigolo et al. J. Phys. G 51 (2024) 075106 (Figs 6, 8,
                    digitised, data/f19/); ¹⁹F(p,αγ) 6.13/6.92/7.12 MeV γ from the
                    TUNL compilation (2021PH03 dσ/dΩ(90°) 0.84-1.52 MeV;
                    1991HE16 below 0.9 MeV).
  ¹¹B               ¹¹B(p,γ₀)¹²C, 16.9 MeV at E_p ≈ 1.05 MeV, from the 17.23 MeV
                    1⁻ level (Γ = 1.15 MeV, (2J+1)Γγ₀ ≥ 115 eV, Kelley 2017
                    A = 12): an ESTIMATE (Breit-Wigner, Γp/Γ = 0.5 assumed).
  heat              steady-state temperature of the backing foil under the beam
                    spot: an axisymmetric clamped disk or a strip held at one
                    end, conduction plus radiation from both faces.
  diffusion         Li in Al, D = 4.5 exp(-139 kJ/mol / RT) cm²/s (Costas 1963,
                    Al-LiAl couples).
  evaporation       Hertz-Knudsen from the vapour pressure: Li (CRC: 1 Pa at
                    797 K, 100 Pa at 995 K); LiF (ΔH_sub ≈ 256 kJ/mol, 1 Pa at
                    ~1050 K: an ESTIMATE good to ×3).
  blistering        H fluence where the beam stops, against 10¹⁸ (Cu, low E)
                    to 2-3×10¹⁹ /cm² (Cu, 2 MeV; Budker/OIST).
  carbon build-up   a parametric layer 0-100 µg/cm² (rates in the literature
                    span 10¹⁴ C/cm²/µC to "none seen" with a cold trap).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
LNL = HERE.parent
sys.path.insert(0, str(LNL))
sys.path.insert(0, str(LNL.parent / 'ill'))
import lnl_rates as LR      # noqa: E402

DATA = LNL / 'data'
OUT = LNL / 'out' / 'target'

E_CH = LR.E_CHARGE
N_A = LR.N_AVO
SIGMA_SB = 5.670374e-8
R_GAS = 8.314462
AW = {'Li': 6.941, 'F': 18.998, 'O': 15.999, 'C': 12.011, 'H': 1.008, 'Al': 26.982,
      'Cu': 63.546, 'B': 10.81, 'N': 14.007, 'P': 30.974}

XS = LR.CrossSection()
STP = LR.Stopping()

#: the films.  comp in atoms per formula unit; rho bulk g/cm³.
FILMS = {
    'LiF': dict(comp={'Li': 1, 'F': 1}, rho=2.635),
    'Li2O': dict(comp={'Li': 2, 'O': 1}, rho=2.013),
    'LiOH': dict(comp={'Li': 1, 'O': 1, 'H': 1}, rho=1.46),
    'Li2CO3': dict(comp={'Li': 2, 'C': 1, 'O': 3}, rho=2.11),
    'Li': dict(comp={'Li': 1}, rho=0.534),
    # LiPON as MEG II: Li2.9 PO3.3 N0.46 (stopping: P ~ Al by Bragg, N ~ O)
    'LiPON': dict(comp={'Li': 2.9, 'P': 1, 'O': 3.3, 'N': 0.46}, rho=2.4),
    'C': dict(comp={'C': 1}, rho=2.0),
    'Al': dict(comp={'Al': 1}, rho=2.70),
    'Cu': dict(comp={'Cu': 1}, rho=8.96),
}


def stopping(comp, e_mev):
    """MeV cm²/g; P and N borrow Al and O (Bragg; ~10 % for the minor elements)."""
    c = {}
    for el, n in comp.items():
        el2 = {'P': 'Al', 'N': 'O', 'B': 'C'}.get(el, el)
        c[el2] = c.get(el2, 0) + n * AW[el] / AW[el2]
    return STP.compound(c, e_mev)


def per_gram(comp, el):
    m = sum(AW[e] * n for e, n in comp.items())
    return comp.get(el, 0) * N_A / m


# --------------------------------------------------------------------------- #
# ¹⁹F and ¹¹B cross sections
# --------------------------------------------------------------------------- #
def _tunl(name):
    d = pd.read_csv(DATA / 'f19' / name, skiprows=6)
    return d.iloc[:, 0].astype(float).values, d.iloc[:, 1].astype(float).values


class Fluorine:
    """σ(¹⁹F(p,α_π)) and σ(¹⁹F(p,αγ), all three lines) in mb, lab E_p in keV."""

    R_67 = 0.6     # (6.92 + 7.12 MeV) / 6.13 MeV above 0.9 MeV: ESTIMATE (x2), see TARGET_STUDY §3

    def __init__(self):
        a = pd.read_csv(DATA / 'f19' / 'redigolo2024_alpha_pi_digitised.csv', comment='#')
        a = a.sort_values('Ecm_MeV')
        self.api_ep = a.Ecm_MeV.values / 0.9497 * 1e3
        self.api = a.sigma_mb.values
        self.g613_ep, s = _tunl('tunl_2021PH03_6p13_dsdo90.csv')
        self.g613 = 4 * np.pi * s                          # isotropic: ±30 %
        lo = {}
        for i in (2, 3, 4):
            x, y = _tunl(f'tunl_1991HE16_g{i}.csv')
            lo[i] = (x, 4 * np.pi * y * 1e3)              # b/sr at 45° -> mb
        self.lo = lo

    def alpha_pi(self, ep):
        ep = np.asarray(ep, float)
        x, y = self.api_ep, self.api
        # below the data: constant S-factor (Coulomb barrier scaling) -- upper-side ESTIMATE
        s0 = y[0] / LR.s_to_sigma_mb(1.0, ep * 0 + x[0]) if False else None   # noqa: F841
        tpe = lambda e: 31.29 * 9 * np.sqrt(0.9497 * 1.0073 / (e * 0.9497))   # 2πη, p + ¹⁹F
        below = y[0] * (x[0] / ep) * np.exp(-(tpe(ep) - tpe(x[0])))
        return np.where(ep < x[0], below, np.interp(ep, x, y))

    def gamma(self, ep):
        ep = np.asarray(ep, float)
        hi = np.interp(ep, self.g613_ep, self.g613) * (1 + self.R_67)
        lo = sum(np.interp(ep, x, y, left=0, right=0) for x, y in self.lo.values())
        return np.where(ep >= self.g613_ep[0], hi, lo)


FL = Fluorine()


def sigma_b11_g0_ub(ep_kev, gg0_ev=38.0, gp_frac=0.5):
    """¹¹B(p,γ₀)¹²C via the 17.23 MeV 1⁻ level (E_p = 1388 keV, Γ = 1.15 MeV):
    single-level Breit-Wigner, s-wave Γp scaled by exp(-2πη).  Γγ₀ ≥ 38 eV
    (Kelley 2017: (2J+1)Γγ₀ ≥ 115 eV); Γp/Γ = 0.5 at the peak is assumed.  ESTIMATE."""
    ep = np.asarray(ep_kev, float)
    mu = 11.0093 * 1.00728 / (11.0093 + 1.00728)
    ecm = ep * 11.0093 / (11.0093 + 1.00728) / 1e3
    er, gam = 1.388 * 11.0093 / (11.0093 + 1.00728), 1.15
    tpe = lambda e: 31.29 * 5 * np.sqrt(mu / (e * 1e3))
    gp = gp_frac * gam * np.exp(-(tpe(ecm) - tpe(er)))
    k = np.sqrt(2 * mu * LR.U_MEV * ecm) / 197.327
    lam2_b = (1 / k) ** 2 / 100
    om = 3 / 8
    return 1e6 * np.pi * lam2_b * om * gp * gg0_ev * 1e-6 / ((ecm - er) ** 2 + gam ** 2 / 4)


# --------------------------------------------------------------------------- #
# a proton through a layered target
# --------------------------------------------------------------------------- #
def layered_yield(ep0_kev, layers, f7=LR.F_LI7_NAT, step_kev=0.25, b_per_li=0.0):
    """layers: list of (comp, µg/cm²) from the beam side.  comp may hold Li, F,
    O, C, H, Al, ... as atom fractions.  Returns per-proton yields:
    γ₀ split by origin (17.64 res, 18.15 res, direct), γ₁, ¹⁹F α_π pairs and
    αγ γ, ¹¹B γ₀ (b_per_li = B atoms per Li atom in the Li-bearing layers),
    and the energy deposited per layer (keV)."""
    e = float(ep0_kev)
    acc = dict(g0_17=0.0, g0_18=0.0, g0_dc=0.0, g1=0.0, g1_res=0.0, f_api=0.0, f_gam=0.0, b_g0=0.0,
               w_estar=0.0)
    dep = []
    for comp, t in layers:
        m_left = t * 1e-6
        n7 = per_gram(comp, 'Li') * f7
        nf = per_gram(comp, 'F')
        e_in = e
        while m_left > 0 and e > 30:
            s = float(stopping(comp, e / 1e3))
            dm = min(step_kev / 1e3 / s, m_left)
            de = dm * s * 1e3
            em = e - de / 2
            if n7:
                k = n7 * dm * 1e-30
                r17 = float(XS.res(em, '17.64')) * k
                r18 = float(XS.res(em, '18.15')) * k
                dc = float(XS.direct(em)) * k
                acc['g0_17'] += r17
                acc['g0_18'] += r18
                acc['g0_dc'] += dc
                g01 = float(XS.total(em, 'g01')) * k
                acc['g1'] += g01 - r17 - r18 - dc
                acc['g1_res'] += sum(float(XS.res(em, rr, 'g1')) for rr in LR.RES) * k
                acc['w_estar'] += (r17 + r18 + dc) * float(LR.e_star(em))
                if b_per_li:
                    acc['b_g0'] += float(sigma_b11_g0_ub(em)) * k / f7 * b_per_li * 0.801
            if nf:
                kf = nf * dm * 1e-27
                acc['f_api'] += float(FL.alpha_pi(em)) * kf
                acc['f_gam'] += float(FL.gamma(em)) * kf
            e -= de
            m_left -= dm
        dep.append(e_in - e)
    g0 = acc['g0_17'] + acc['g0_18'] + acc['g0_dc']
    out = dict(E_out_keV=e, Y_g0=g0, Y_g1=acc['g1'],
               f17=acc['g0_17'] / g0 if g0 else np.nan,
               f18res=acc['g0_18'] / g0 if g0 else np.nan,
               fdc=acc['g0_dc'] / g0 if g0 else np.nan,
               mean_Estar=acc['w_estar'] / g0 if g0 else np.nan,
               frac_g1_direct=(acc['g1'] - acc['g1_res']) / acc['g1'] if acc['g1'] else np.nan,
               Y_F_pairs=acc['f_api'], Y_F_gamma=acc['f_gam'], Y_B_g0=acc['b_g0'])
    out['dep_keV'] = dep
    return out


def film(name, t_ug):
    return (FILMS[name]['comp'], t_ug)


def al_with_li(t_um, li_ug_cm2, depth_um, n=20):
    """Al backing t_um thick into which li_ug_cm2 of Li has diffused with a
    half-Gaussian profile of width depth_um (√(4Dt)), as n slabs."""
    rho = FILMS['Al']['rho']
    z = np.linspace(0, t_um, n + 1)
    zc = 0.5 * (z[1:] + z[:-1])
    prof = np.exp(-(zc / max(depth_um, 1e-6)) ** 2)
    prof = prof / prof.sum() * li_ug_cm2
    out = []
    for dz, li in zip(np.diff(z), prof):
        al = rho * dz * 1e-4 * 1e6                       # µg/cm²
        x = (li / AW['Li']) / (al / AW['Al'])            # Li per Al atom
        out.append(({'Al': 1.0, 'Li': x}, al + li))
    return out


# --------------------------------------------------------------------------- #
# scenarios
# --------------------------------------------------------------------------- #
def scenario_table() -> pd.DataFrame:
    """The ⁸Be capture mix and the other nuclei for the targets people have used
    and for the ways they degrade."""
    al10 = film('Al', 2.70 * 10 * 100)                    # 10 µm Al = 2700 µg/cm²
    rows = []

    def add(name, group, ep, layers, note='', b=0.0):
        r = layered_yield(ep, layers, b_per_li=b)
        dep = r.pop('dep_keV')
        rows.append(dict(scenario=name, group=group, Ep_keV=ep, note=note, dE_total_keV=sum(dep),
                         **r, F_pairs_per_8Be_pair=r['Y_F_pairs'] / (3.5e-3 * (r['Y_g0'] + r['Y_g1']))
                         if r['Y_g0'] else np.nan,
                         F_gamma_per_8Be_gamma=r['Y_F_gamma'] / (r['Y_g0'] + r['Y_g1']) if r['Y_g0'] else np.nan))

    # what each group used
    add('ATOMKI 2016/2022, LiF 30 on-res', 'used', 450, [film('LiF', 30), al10])
    add('ATOMKI 2022, Li2O 300 off-res 1.10', 'used', 1100, [film('Li2O', 300), al10])
    add('Hanoi 2024, LiF 30 at 0.80', 'used', 800, [film('LiF', 30), al10])
    add('Hanoi 2024, Li2O (0.44 mg/cm² measured) at 1.225', 'used', 1225, [film('Li2O', 440), film('Al', 0.89 * 100)])
    add('MEG II 2023, LiPON 7 µm on Cu 1.08', 'used', 1080, [film('LiPON', 2.4 * 7 * 100), film('Cu', 8.96 * 25 * 100)])
    add('LNL 2023-24, LiF 34 at 1.03', 'used', 1034, [film('LiF', 34), al10], 'backing (ask)')
    add('LNL 2023-24, LiF 935, 1.03 at centre', 'used', 1124, [film('LiF', 935), al10], 'backing (ask)')
    add('LNL 2023-24, LiF 34 at 441', 'used', 446, [film('LiF', 34), al10], 'backing (ask)')
    # our candidates
    for f, t, ep in (('Li2O', 100, 1050), ('Li2O', 300, 1070), ('LiF', 100, 1050), ('Li', 53, 1050),
                     ('LiPON', 240, 1070)):
        add(f'MX17 candidate: {f} {t} at {ep}', 'candidate', ep, [film(f, t), al10])
    # degradation of Li2O 300 at 1.07 MeV
    base = [film('Li2O', 300)]
    add('Li2O 300 + C 10 µg/cm²', 'carbon', 1070, [film('C', 10)] + base + [al10])
    add('Li2O 300 + C 50 µg/cm²', 'carbon', 1070, [film('C', 50)] + base + [al10])
    add('Li2O 300 + C 200 µg/cm²', 'carbon', 1070, [film('C', 200)] + base + [al10])
    add('Li2O 300 -> LiOH (×1.6 mass)', 'hydration', 1070, [(FILMS['LiOH']['comp'], 300 * 47.9 / 29.9)] + [al10])
    add('Li2O 300 -> Li2CO3 (×2.47 mass)', 'hydration', 1070, [(FILMS['Li2CO3']['comp'], 300 * 73.9 / 29.9)] + [al10])
    # metallic Li diffusing into Al (the ATOMKI 2016 mishap), at 1.04 MeV; Li 53 µg/cm² (1 µm)
    for frac, d in ((0.0, 1), (0.1, 2), (0.3, 5), (0.5, 10), (1.0, 10), (1.0, 30)):
        lay = ([film('Li', 53 * (1 - frac))] if frac < 1 else []) + al_with_li(10, 53 * frac, d)
        add(f'Li 53 at 1.04, {frac:.0%} diffused to {d} µm in 10 µm Al', 'diffusion', 1040, lay)
    # and on a thick backing (the beam stops: diffused Li sees all energies down to 0)
    for frac, d in ((0.1, 2), (0.5, 10), (1.0, 30)):
        lay = ([film('Li', 53 * (1 - frac))] if frac < 1 else []) + al_with_li(30, 53 * frac, d)
        add(f'Li 53 at 1.04, {frac:.0%} diffused to {d} µm, thick Al', 'diffusion', 1040, lay)
    # LiF that loses F (radiolysis) and its Li then diffuses
    for frac in (0.1, 0.3):
        lay = [film('LiF', 100 * (1 - frac))] + al_with_li(10, 100 * frac * 6.94 / 25.94, 5)
        add(f'LiF 100 at 1.05, {frac:.0%} of Li freed and diffused 5 µm', 'diffusion', 1050, lay)
    # boron contamination (B atoms per Li atom)
    for b in (1e-4, 1e-3, 1e-2, 0.24):
        add(f'Li2O 300 at 1.07, B/Li = {b:g}', 'boron', 1070, base + [al10], b=b)
    return pd.DataFrame(rows)


def fluorine_scan() -> pd.DataFrame:
    """LiF thickness × beam energy: pairs and γ from ¹⁹F per ⁸Be pair."""
    rows = []
    for t in (30, 100, 300, 935):
        for ep in np.arange(450, 1301, 25):
            r = layered_yield(ep, [film('LiF', t)])
            r.pop('dep_keV')
            ipc = 3.5e-3 * (r['Y_g0'] + r['Y_g1'])
            rows.append(dict(t_ug_cm2=t, Ep_keV=ep, Y_g0=r['Y_g0'], Y_g1=r['Y_g1'], Y_8Be_pairs=ipc,
                             Y_F_pairs=r['Y_F_pairs'], Y_F_gamma=r['Y_F_gamma'],
                             F_pairs_per_8Be_pair=r['Y_F_pairs'] / ipc, F_gamma_per_8Be_gamma=r['Y_F_gamma'] / (r['Y_g0'] + r['Y_g1'])))
    return pd.DataFrame(rows)


def xs_table() -> pd.DataFrame:
    ep = np.arange(300, 1500.1, 5)
    return pd.DataFrame(dict(Ep_keV=ep, Li7_g0_ub=XS.total(ep), Li7_g01_ub=XS.total(ep, 'g01'),
                             F19_alpha_pi_mb=FL.alpha_pi(ep), F19_gamma_mb=FL.gamma(ep),
                             B11_g0_ub_est=sigma_b11_g0_ub(ep)))


# --------------------------------------------------------------------------- #
# heat
# --------------------------------------------------------------------------- #
MAT_TH = {   # k [W/m/K], emissivity (both faces; a film on top changes it little in the IR)
    'Al': (237.0, 0.08), 'Cu': (400.0, 0.05), 'Ni': (90.0, 0.15),
    'C glassy': (6.0, 0.85), 'C graphite foil': (300.0, 0.85), 'Ta': (57.0, 0.15),
}


def foil_power(ep_kev, mat, t_um, film_dep_kev=10.0):
    """W per µA deposited in the film + foil (the rest leaves with the beam)."""
    comp = {'Al': {'Al': 1}, 'Cu': {'Cu': 1}, 'Ni': {'Cu': 1}, 'Ta': {'Cu': 1},
            'C glassy': {'C': 1}, 'C graphite foil': {'C': 1}}[mat]
    rho = {'Al': 2.70, 'Cu': 8.96, 'Ni': 8.9, 'Ta': 16.6, 'C glassy': 1.5, 'C graphite foil': 1.0}[mat]
    m = rho * t_um * 1e-4
    e = ep_kev - film_dep_kev
    while m > 0 and e > 5:
        s = float(stopping(comp, e / 1e3))
        dm = min(1.0 / 1e3 / s, m)
        e -= dm * s * 1e3
        m -= dm
    return (ep_kev - max(e, 0)) / 1e3          # MeV -> W/µA


def temp_disk(P_W, mat, t_um, R_mm=10.0, sig_mm=1.5, T0=300.0, n=200):
    """axisymmetric foil clamped at radius R, Gaussian beam σ: T(r) with conduction
    and two-face radiation, by Newton iteration on the finite-volume system."""
    k, eps = MAT_TH[mat]
    t = t_um * 1e-6
    r = np.linspace(0, R_mm * 1e-3, n + 1)
    rc = 0.5 * (r[1:] + r[:-1])
    dr = r[1] - r[0]
    q = np.exp(-0.5 * (rc / (sig_mm * 1e-3)) ** 2)
    area = 2 * np.pi * rc * dr
    q = P_W * q / (q * area).sum()                         # W/m²
    T = np.full(n, T0 + 10.0)
    for _ in range(200):
        # conduction conductances between cells i and i+1, and to the clamp at R
        G = k * t * 2 * np.pi * r[1:-1] / dr
        Gb = k * t * 2 * np.pi * r[-1] / (dr / 2)
        F = q * area - 2 * eps * SIGMA_SB * (T ** 4 - T0 ** 4) * area
        J = np.zeros((n, n))
        F[:-1] -= G * (T[:-1] - T[1:])
        F[1:] -= G * (T[1:] - T[:-1])
        F[-1] -= Gb * (T[-1] - T0)
        idx = np.arange(n - 1)
        J[idx, idx] -= G
        J[idx, idx + 1] += G
        J[idx + 1, idx + 1] -= G
        J[idx + 1, idx] += G
        J[-1, -1] -= Gb
        J[np.arange(n), np.arange(n)] -= 8 * eps * SIGMA_SB * T ** 3 * area
        dT = np.linalg.solve(J, -F)
        T = T + np.clip(dT, -500, 500)
        T = np.maximum(T, T0)
        if np.abs(dT).max() < 1e-3:
            break
    return float(T[0])


def temp_strip(P_W, mat, t_um, w_mm=5.0, L_mm=50.0, x0_mm=25.0, sig_mm=1.5, T0=300.0, n=400,
               ends=('fixed', 'fixed')):
    """a strip w wide and L long, its ends either held at T0 by a cooled rod
    ('fixed') or insulated ('free': a Plexiglas rod, k = 0.2 W/m/K), beam centred
    at x0: 1D fin with radiation from both faces.  The ATOMKI strip is 10 µm ×
    5 mm × 50 mm Al between two rods 25 mm either side of the beam (Gulyás 2016)."""
    k, eps = MAT_TH[mat]
    t, w = t_um * 1e-6, w_mm * 1e-3
    x = np.linspace(0, L_mm * 1e-3, n + 1)
    xc = 0.5 * (x[1:] + x[:-1])
    dx = x[1] - x[0]
    q = np.exp(-0.5 * ((xc - x0_mm * 1e-3) / (sig_mm * 1e-3)) ** 2)
    q = P_W * q / q.sum()                                  # W per cell
    area = 2 * w * dx
    G = k * t * w / dx
    Gb = k * t * w / (dx / 2)
    T = np.full(n, T0 + 10.0)
    for _ in range(300):
        F = q - eps * SIGMA_SB * (T ** 4 - T0 ** 4) * area
        F[:-1] -= G * (T[:-1] - T[1:])
        F[1:] -= G * (T[1:] - T[:-1])
        J = np.zeros((n, n))
        idx = np.arange(n - 1)
        J[idx, idx] -= G
        J[idx, idx + 1] += G
        J[idx + 1, idx + 1] -= G
        J[idx + 1, idx] += G
        for i, e in ((0, ends[0]), (n - 1, ends[1])):
            if e == 'fixed':
                F[i] -= Gb * (T[i] - T0)
                J[i, i] -= Gb
        J[np.arange(n), np.arange(n)] -= 4 * eps * SIGMA_SB * T ** 3 * area
        dT = np.linalg.solve(J, -F)
        T = np.maximum(T + np.clip(dT, -500, 500), T0)
        if np.abs(dT).max() < 1e-3:
            break
    return float(T.max())


HOLDERS = {
    # name: (geometry, mat, t_um, kwargs)
    'ATOMKI 2016: 10 µm Al strip, Plexiglas rods': ('strip', 'Al', 10, dict(ends=('free', 'free'))),
    'ATOMKI 2022: 10 µm Al strip, Al rods': ('strip', 'Al', 10, {}),
    '10 µm Al disk, clamped at r = 10 mm': ('disk', 'Al', 10, {}),
    '1 µm Ni disk, clamped at r = 10 mm (Hanoi Li2O)': ('disk', 'Ni', 1, {}),
    '20 µm glassy C disk, r = 10 mm': ('disk', 'C glassy', 20, {}),
    '25 µm graphite foil disk, r = 10 mm': ('disk', 'C graphite foil', 25, {}),
    '25 µm Cu disk, clamped at r = 10 mm (MEG II-like)': ('disk', 'Cu', 25, {}),
}


def thermal_table() -> pd.DataFrame:
    rows = []
    for name, (geo, mat, t, kw) in HOLDERS.items():
        for ep in (450, 800, 1050, 1100):
            ppa = foil_power(ep, mat, t)
            for I in (0.1, 0.2, 0.5, 0.8, 1.0, 1.5, 2.0, 4.0):
                P = ppa * I
                T = temp_strip(P, mat, t, **kw) if geo == 'strip' else temp_disk(P, mat, t, **kw)
                rows.append(dict(holder=name, Ep_keV=ep, I_uA=I, P_W=P, W_per_uA=ppa, T_max_K=T, T_max_C=T - 273.15))
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# materials limits: diffusion, evaporation
# --------------------------------------------------------------------------- #
def D_li_al(T):
    """cm²/s, Costas 1963 (Al-LiAl couples)."""
    return 4.5 * np.exp(-139e3 / (R_GAS * T))


def p_li(T):
    return 10 ** (10.05 - 8010.0 / T)        # Pa (CRC: 1 Pa 797 K, 100 Pa 995 K)


def p_lif(T):
    return 10 ** (12.73 - 13370.0 / T)       # Pa, ESTIMATE (ΔH_sub 256 kJ/mol, 1 Pa at 1050 K)


def evap_ug_cm2_per_h(p, M_g):
    """Hertz-Knudsen, unit sticking: mass flux in µg/cm²/h."""
    def f(T):
        return p(T) * np.sqrt(M_g * 1e-3 / (2 * np.pi * R_GAS * T)) * 1e5 * 3600   # kg/m²/s -> µg/cm²/h
    return f


def limits_table() -> pd.DataFrame:
    T = np.arange(300, 1001, 10.0)
    li_ev = evap_ug_cm2_per_h(p_li, 6.94)(T)
    lif_ev = evap_ug_cm2_per_h(p_lif, 25.94)(T)
    return pd.DataFrame(dict(T_K=T, T_C=T - 273.15, D_LiAl_cm2_s=D_li_al(T),
                             diff_len_1d_um=np.sqrt(4 * D_li_al(T) * 86400) * 1e4,
                             diff_len_1wk_um=np.sqrt(4 * D_li_al(T) * 7 * 86400) * 1e4,
                             Li_evap_ug_cm2_h=li_ev, LiF_evap_ug_cm2_h=lif_ev))


def threshold_T(tab, col, value):
    """first temperature where tab[col] passes value (monotone rising)."""
    i = np.argmax(tab[col].values >= value)
    return float(tab.T_K.values[i]) if tab[col].values[i] >= value else np.nan


# --------------------------------------------------------------------------- #
# dose
# --------------------------------------------------------------------------- #
def fluence_table() -> pd.DataFrame:
    rows = []
    for I in (0.5, 1.0, 4.0):
        for sig in (1.0, 2.0, 3.0):
            area = 2 * np.pi * (sig * 0.1) ** 2          # cm², Gaussian effective area
            for days in (1, 7, 30):
                n = I * 1e-6 * days * 86400 / E_CH
                rows.append(dict(I_uA=I, spot_sigma_mm=sig, days=days, protons=n, fluence_cm2=n / area,
                                 over_1e18=n / area / 1e18, over_2e19=n / area / 2e19))
    return pd.DataFrame(rows)


def carbon_table() -> pd.DataFrame:
    """beam-energy shift from a carbon overlayer, and what it does to the
    441 keV calibration on a thin LiF target and to the 1.07 MeV running."""
    rows = []
    for tc in (0, 2, 5, 10, 20, 50, 100):
        for ep, f, t in ((446, 'LiF', 30), (1070, 'Li2O', 300)):
            r = layered_yield(ep, [film('C', tc), film(f, t)] if tc else [film(f, t)])
            dep = r.pop('dep_keV')
            rows.append(dict(t_C_ug_cm2=tc, Ep_keV=ep, target=f'{f} {t}', shift_keV=dep[0] if tc else 0.0,
                             Y_g0=r['Y_g0'], f17=r['f17'], mean_Estar=r['mean_Estar']))
    d = pd.DataFrame(rows)
    for (ep, tg), g in d.groupby(['Ep_keV', 'target']):
        d.loc[g.index, 'Y_rel'] = g.Y_g0 / g.Y_g0.iloc[0]
    return d


# --------------------------------------------------------------------------- #
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    xs = xs_table()
    xs.to_csv(OUT / 'cross_sections.csv', index=False)
    i = np.argmin(np.abs(xs.Ep_keV - 1050))
    print(f"CHECK σ at 1.05 MeV: ⁷Li γ₀ {xs.Li7_g0_ub[i]:.1f} µb, γ₀+γ₁ {xs.Li7_g01_ub[i]:.1f} µb;"
          f" ¹⁹F α_π {xs.F19_alpha_pi_mb[i]:.2f} mb, αγ {xs.F19_gamma_mb[i]:.2f} mb; ¹¹B γ₀ {xs.B11_g0_ub_est[i]:.1f} µb (est.)")
    sc = scenario_table()
    sc.to_csv(OUT / 'scenarios.csv', index=False)
    with pd.option_context('display.width', 250, 'display.max_columns', 30, 'display.max_colwidth', 60):
        print(sc[['scenario', 'Ep_keV', 'dE_total_keV', 'E_out_keV', 'Y_g0', 'f17', 'fdc', 'Y_F_pairs',
                  'F_pairs_per_8Be_pair', 'F_gamma_per_8Be_gamma', 'Y_B_g0']].to_string(float_format=lambda v: f'{v:.3g}'))
    fs = fluorine_scan()
    fs.to_csv(OUT / 'fluorine_scan.csv', index=False)
    th = thermal_table()
    th.to_csv(OUT / 'thermal.csv', index=False)
    with pd.option_context('display.width', 250):
        print(th[th.Ep_keV.isin([800, 1050])].pivot_table(index=['holder', 'Ep_keV'], columns='I_uA',
                                                           values='T_max_C', sort=False).round(0).to_string())
    lim = limits_table()
    lim.to_csv(OUT / 'limits.csv', index=False)
    for lab, col, v in (('Li through 10 µm Al in a day', 'diff_len_1d_um', 10),
                        ('Li through 10 µm Al in a week', 'diff_len_1wk_um', 10),
                        ('Li 1 µm (53 µg/cm²) evaporates in 10 h', 'Li_evap_ug_cm2_h', 5.3),
                        ('LiF 300 µg/cm² evaporates in a week', 'LiF_evap_ug_cm2_h', 300 / 168)):
        T = threshold_T(lim, col, v)
        print(f"LIMIT {lab}: T ≥ {T:.0f} K ({T - 273.15:.0f} °C)")
    fluence_table().to_csv(OUT / 'fluence.csv', index=False)
    ct = carbon_table()
    ct.to_csv(OUT / 'carbon.csv', index=False)
    print(ct.round(4).to_string())


if __name__ == '__main__':
    main()
