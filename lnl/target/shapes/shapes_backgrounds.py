#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
shapes_backgrounds.py -- everything the beam makes in the two LNL target designs besides ⁸Be, per proton
and per µA, at E_p = 1.03 and 1.10 MeV.  SHAPES_GEANT.md §3 (2026-10-27).

    ~/PycharmProjects/nTof_x17/.venv/bin/python lnl/target/shapes/shapes_backgrounds.py

Designs (the beam crosses the film along +y, then stops in the beam stop):
  dome     Li 20 µm (1068 µg/cm²) inside a 200 µm Cu hemisphere; the beam stops in the Cu
  window   Li 14 µm on the plane at 45° (19.8 µm along the beam), Mo 8 µm, diamond 200 µm; stops in the Mo
           (0°: Li 20 µm, the same along the beam)

Sources (each row of out/target/shapes/backgrounds_inventory.csv says which):
  ⁸Be γ₀, γ₁     target_model.layered_yield (Zahnow 1995 resonances + direct capture)
  ⁷Li(p,p′) 478   opt_backing.sigma_478_b (Bykov 2021 thick-target yield)
  ⁷Li(p,α)α       S(E) = 58 keV b + slope (NACRE; Spitaleri 2001 THM agrees): ESTIMATE ±20 %
  ⁶Li(p,γ)⁷Be     S ≈ 0.106 keV b (NACRE); ⁶Li(p,α)³He S ≈ 2.97 MeV b (NACRE)
  ¹⁹F(p,αγ), α_π  target_model.Fluorine (TUNL, Redigolo 2024)
  ¹¹B(p,γ₀)       target_model.sigma_b11_g0_ub (Breit-Wigner ESTIMATE, 17.23 MeV level)
  ¹⁵N(p,αγ) 897   ωγ = 362 eV, Γ = 1.57 keV (Marta et al., PRC 81 055807, 2010; 4.44 MeV γ)
  ¹⁴N(p,γ) 1058   ωγ = 0.353 eV, Γ = 3.8 keV (same; γ up to 8.3 MeV)
  ²³Na            bounding σ (PIGE-scale, see NA below): ESTIMATE, upper side
  PIXE            K-shell ionisation by binary-encounter scaling (σ U_K² universal in E/(λ U_K), ∝ ξ⁴ at
                  low ξ), anchored on σ_K(Cu, 1 MeV) = 70 b (ECPSSR scale, Lapicki 1989 compilation): ESTIMATE ×2–3
  α-induced n     ⁷Li(α,n)¹⁰B σ ≈ 0.2 b at 8–9 MeV, ¹³C(α,n) thick yield 1e-7 n/α (Po-C scale): ESTIMATE ×3
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent.parent))
import target_model as TM     # noqa: E402
import opt_backing as OB      # noqa: E402
import lnl_rates as LR        # noqa: E402

OUT = HERE.parent.parent / 'out' / 'target' / 'shapes'
P_PER_UA = 1e-6 / LR.E_CHARGE
N_A = LR.N_AVO
NLI_G = N_A / 6.941                  # Li atoms per gram
EPS = (1030.0, 1100.0)
DESIGNS = {
    'dome':   dict(label='Cu hemisphere, Li 20 µm / Cu 200 µm', li_ug=1068.0, stop='Cu'),
    'window': dict(label='diamond window 45°, Li 14 µm / Mo 8 / C 200 µm', li_ug=748.0 * np.sqrt(2), stop='Mo'),
}


# --------------------------------------------------------------------------- #
# cross sections (b, lab energy keV)
# --------------------------------------------------------------------------- #
def two_pi_eta(e_cm_kev, z1z2, mu_amu):
    return 31.29 * z1z2 * np.sqrt(mu_amu / e_cm_kev)


def s_factor_xs(ep_kev, A, z1z2, S_kevb):
    mu = A / (A + 1.0073) * 1.0073
    ecm = ep_kev * A / (A + 1.0073)
    return S_kevb / ecm * np.exp(-two_pi_eta(ecm, z1z2, mu))


def xs_li7_pa(ep):      # ⁷Li(p,α)α; S(E) ≈ 58 + 0.3·E_cm(keV) keV b up to 1 MeV (rising toward the 3 MeV bump)
    ecm = ep * 7 / 8
    return s_factor_xs(ep, 7.016, 3, 58.0 + 0.03 * ecm)


def xs_li6_pg(ep):
    return s_factor_xs(ep, 6.015, 3, 0.106)


def xs_li6_pa(ep):      # ⁶Li(p,α)³He, S ≈ 2.97 MeV b falling slowly
    return s_factor_xs(ep, 6.015, 3, 2970.0 * (1 - 0.3 * ep / 1000))


# narrow resonances in contaminants: (E_R lab keV, Γ_cm keV, ωγ eV, A, γ energy)
RES = {
    'N15_pag_897': (897.0, 1.57, 362.0, 15, 4.44),
    'N14_pg_1058': (1058.0, 3.8, 0.353, 14, 7.3),
}
F_N15 = 0.00366
# ²³Na: bounding effective σ over 0.8–1.1 MeV (the 440 keV (p,p′) line and the 1.63 MeV (p,αγ) line used in
# PIGE; capture γ to ²⁴Mg up to 12.7 MeV).  ESTIMATE: upper-side constants, not data.
NA = {'Na_pp_440': 30e-3, 'Na_pag_1634': 5e-3, 'Na_pg_12.7': 0.1e-3}


# --------------------------------------------------------------------------- #
# the film
# --------------------------------------------------------------------------- #
def film_trace(ep0, li_ug, step=0.25):
    """[(E_mid keV, dE keV, n_Li atoms/cm² in the step)] through pure Li."""
    e, m_left, out = ep0, li_ug * 1e-6, []
    while m_left > 0 and e > 30:
        s = float(TM.stopping({'Li': 1}, e / 1e3))        # MeV cm²/g
        dm = min(step / 1e3 / s, m_left)
        de = dm * s * 1e3
        out.append((e - de / 2, de, dm * NLI_G))
        e -= de
        m_left -= dm
    return out, e


def film_yields(ep0, li_ug):
    tr, e_out = film_trace(ep0, li_ug)
    y = dict(E_out=e_out)
    f7, f6 = LR.F_LI7_NAT, 1 - LR.F_LI7_NAT
    y['Li7_pa'] = sum(float(xs_li7_pa(em)) * n * f7 for em, de, n in tr) * 1e-24
    y['Li6_pg'] = sum(float(xs_li6_pg(em)) * n * f6 for em, de, n in tr) * 1e-24
    y['Li6_pa'] = sum(float(xs_li6_pa(em)) * n * f6 for em, de, n in tr) * 1e-24
    y['L478'] = sum(float(OB.sigma_478_b(em)[()]) * n for em, de, n in tr) * 1e-24
    # per unit contaminant fraction x (atoms per Li atom), uniform through the film
    y['F_gam_per_x'] = sum(float(TM.FL.gamma(em)) * 1e-3 * n for em, de, n in tr) * 1e-24
    y['F_api_per_x'] = sum(float(TM.FL.alpha_pi(em)) * 1e-3 * n for em, de, n in tr) * 1e-24
    y['B_g0_per_x'] = sum(float(TM.sigma_b11_g0_ub(em)) * 1e-6 * n * 0.801 for em, de, n in tr) * 1e-24
    for k, (er, g, wg, A, _) in RES.items():
        f = F_N15 if k.startswith('N15') else 1 - F_N15
        y[k + '_per_x'] = sum(OB.bw_int(em - de / 2, em + de / 2, er, g, wg, A) / de * n * f
                              for em, de, n in tr) * 1e-24
    for k, s in NA.items():
        y[k + '_per_x'] = sum(s * n for em, de, n in tr if em > 800) * 1e-24
    return y


# --------------------------------------------------------------------------- #
# PIXE in the beam stop (K x-rays), binary-encounter scaling
# --------------------------------------------------------------------------- #
U_K = {'Cu': 8.979, 'Mo': 20.000, 'Ti': 4.966}          # keV
OMEGA_K = {'Cu': 0.44, 'Mo': 0.765, 'Ti': 0.22}
E_KA = {'Cu': 8.05, 'Mo': 17.48, 'Ti': 4.51}
SIG_CU_1MEV = 70.0      # b, ECPSSR scale (ESTIMATE anchor)


def sigma_k(el, ep_kev):
    """σ_K ionisation (b): σ U² = f(ξ), ξ = E/(λ U), f ∝ ξ⁴ at low ξ (BEA); anchored on Cu at 1 MeV."""
    lam = 1836.15
    xi = ep_kev / (lam * U_K[el])
    xi0 = 1000.0 / (lam * U_K['Cu'])
    return SIG_CU_1MEV * (U_K['Cu'] / U_K[el]) ** 2 * (xi / xi0) ** 4


def pixe_yield(el, e_in, step=2.0):
    comp = {el: 1}
    A = {'Cu': 63.55, 'Mo': 95.95, 'Ti': 47.87}[el]
    n_g = N_A / A
    e, y = e_in, 0.0
    while e > 50:
        s = float(OB.S(comp, e / 1e3)) * 1e3            # keV cm²/g
        y += sigma_k(el, e - step / 2) * 1e-24 * n_g * step / s
        e -= step
    return y * OMEGA_K[el]


# --------------------------------------------------------------------------- #
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows, lev = [], []
    for d, D in DESIGNS.items():
        for ep in EPS:
            b = TM.layered_yield(ep, [TM.film('Li', D['li_ug'])])
            f = film_yields(ep, D['li_ug'])
            g0 = b['Y_g0']

            def add(src, rxn, eg, y, where, assume, effect):
                rows.append(dict(design=d, Ep_keV=ep, source=src, reaction=rxn, E_gamma_MeV=eg, yield_per_p=y,
                                 rate_per_uA=y * P_PER_UA, per_g0=y / g0, where=where, assumption=assume,
                                 effect=effect))
            add('⁸Be', '⁷Li(p,γ₀)⁸Be (18.15/17.64 + direct)', 17.9, g0, 'film', 'measured σ',
                f"signal; f17 {b['f17']:.3f}, direct {b['fdc']:.2f}, E_out {b['E_out_keV']:.0f} keV")
            add('⁸Be', '⁷Li(p,γ₁)⁸Be (to 3.03 MeV)', 15.0, b['Y_g1'], 'film', 'measured σ', 'γ₁ IPC background')
            add('⁷Li', "⁷Li(p,p′γ) 478 keV", 0.478, f['L478'], 'film', 'Bykov 2021 yield', 'singles, MM, pile-up')
            add('⁷Li', '⁷Li(p,α)α (8.7–9.3 MeV α, no γ)', 0.0, f['Li7_pa'], 'film', 'NACRE S-factor',
                'α stopped in Li/stop; feeds the α-induced rows')
            add('⁶Li', '⁶Li(p,γ)⁷Be (5.6 MeV γ; ⁷Be 53 d)', 5.6, f['Li6_pg'], 'film', 'NACRE S-factor',
                'negligible γ; ⁷Be activity')
            add('⁶Li', '⁶Li(p,α)³He (no γ)', 0.0, f['Li6_pa'], 'film', 'NACRE S-factor', 'charged, stopped')
            # α-induced neutrons: half the α go into the beam stop, half back out through the film
            n_li = f['Li7_pa'] * 2 * 0.2e-24 * (0.5 * D['li_ug'] * 1e-6 * NLI_G * LR.F_LI7_NAT)
            add('α-induced', '⁷Li(α,n)¹⁰B (α from ⁷Li(p,α)α, through the rest of the film)', 0.0, n_li, 'film',
                'σ ≈ 0.2 b, ESTIMATE ×3', 'fast neutrons (E_n ≲ 4 MeV)')
            if d == 'window':
                # α that cross 8 µm Mo enter the diamond at ≲ 5 MeV; ¹³C(α,n) thick yield ~1e-7 n/α
                add('α-induced', '¹³C(α,n)¹⁶O in the diamond', 0.0, f['Li7_pa'] * 2 * 0.5 * 1e-7, 'diamond',
                    '1e-7 n/α (Po-C scale), ESTIMATE ×3', 'neutrons, negligible')
            # PIXE in the stop (the beam leaves the film at E_out)
            el = D['stop']
            add('PIXE', f'{el} K x-rays ({E_KA[el]} keV)', E_KA[el] / 1e3, pixe_yield(el, f['E_out']), el,
                'BEA scaling, ESTIMATE ×2-3', 'MM occupancy if they escape (Geant4 gam_lib xray runs)')
            # a fluorine layer of 1 µg/cm² (PFPE pump oil, PTFE/Viton, fluoride cleaning): on the beam face (sees
            # E_p) or at the film/backing interface (sees the exit energy, averaged over ±10 keV of straggling)
            nF = 1e-6 / 18.998 * N_A
            for where, e_at in (('surface', ep), ('interface', f['E_out'])):
                sg = float(np.mean([TM.FL.gamma(e_at + de) for de in np.linspace(-10, 10, 41)]))
                sp = float(np.mean([TM.FL.alpha_pi(e_at + de) for de in np.linspace(-10, 10, 41)]))
                add('contaminant F layer', f'¹⁹F(p,αγ) 6.1–7.1, 1 µg/cm² F at the {where} ({e_at:.0f} keV)', 6.5,
                    sg * 1e-27 * nF, where, '1 µg/cm² F (≈ 5 nm PFPE)', f'singles/legs; α_π pairs {sp * 1e-27 * nF:.2g}/p')
            # contaminants, at a stated level
            levels = dict(F=1e-4, B=1e-5, N=1e-2, Na=1e-4)
            for k, (lab, eg, eff) in {
                    'F_gam': ('¹⁹F(p,αγ) 6.13/6.92/7.12', 6.5, 'singles/legs'),
                    'F_api': ('¹⁹F(p,α_π) 6.05 MeV E0 pairs', 6.05, 'pairs below the window'),
                    'B_g0': ('¹¹B(p,γ₀)¹²C 16.9 MeV (+ its IPC)', 16.9, 'IN the X17 window (the ATOMKI ¹²C case)'),
                    'N15_pag_897': ('¹⁵N(p,αγ)¹²C, 897 keV res.', 4.44, 'singles'),
                    'N14_pg_1058': ('¹⁴N(p,γ)¹⁵O, 1058 keV res.', 7.3, 'singles (1.10 MeV only)'),
                    'Na_pp_440': ('²³Na(p,p′γ) 440 keV', 0.44, 'singles'),
                    'Na_pag_1634': ('²³Na(p,αγ)²⁰Ne 1.63 MeV', 1.634, 'singles'),
                    'Na_pg_12.7': ('²³Na(p,γ)²⁴Mg ≤ 12.7 MeV', 12.7, 'legs; IPC below the window')}.items():
                el2 = k[:2].rstrip('_') if k[:2] != 'N1' else 'N'
                x = levels[el2]
                add(f'contaminant {el2}', lab, eg, f[k + '_per_x'] * x, 'film (uniform)',
                    f'{el2}/Li = {x:g} (atoms)', eff)
                lev.append(dict(design=d, Ep_keV=ep, element=el2, reaction=lab, yield_per_x=f[k + '_per_x'],
                                x_for_1pct_g0=0.01 * g0 / f[k + '_per_x'] if f[k + '_per_x'] > 0 else np.inf,
                                x_for_478_equal=f['L478'] / f[k + '_per_x'] if f[k + '_per_x'] > 0 else np.inf))
    r = pd.DataFrame(rows)
    r.to_csv(OUT / 'backgrounds_inventory.csv', index=False)
    L = pd.DataFrame(lev)
    L.to_csv(OUT / 'contaminant_levels.csv', index=False)
    pd.set_option('display.width', 250)
    pd.set_option('display.max_colwidth', 60)
    print(r[['design', 'Ep_keV', 'reaction', 'yield_per_p', 'rate_per_uA', 'per_g0', 'assumption']]
          .to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    print(L.to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
