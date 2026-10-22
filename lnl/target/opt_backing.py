"""
opt_backing.py — what the film and the backing emit under 0–1.2 MeV protons, for the
LNL target options (TARGET_OPTIONS.md §4–§6).

Per stack (film + interlayer + backing, from the beam side) it steps the proton down
through every layer (PSTAR stopping, Bragg additivity) and integrates:

  * ⁷Li(p,γ)⁸Be γ₀ / γ₁ and the 441-keV share (target_model.layered_yield);
  * ⁷Li(p,p′γ)⁷Li 478 keV: σ from the thick-Li yield of Bykov et al., ARI 175 (2021)
    109821 (4.9×10⁶ /µC at 1.0 MeV, 5.8×10⁷ at 1.67 MeV; a power law between, ±15 %);
  * ¹²C(p,γ)¹³N 2.37 MeV (457 keV resonance, Γ 34 keV cm, ωγ 0.6 eV) and
    ¹³C(p,γ)¹⁴N 8.06 MeV (556 keV resonance, Γ 34.9 keV cm, Γγ₀ 9.1 eV, Γγ 11.8 eV,
    ω = 3/4; Skowronski et al., PRC 111 064611 (2025), arXiv:2512.17288 Table I);
    ¹³C natural 1.07 %, or 0.01 % for ¹²C-enriched CVD diamond;
  * ²⁷Al(p,γ)²⁸Si: the 632 / 773 / 992 keV resonances (ωγ 0.26 / 0.13 / 1.9 eV; ESTIMATE
    for the first two) and ²⁷Al(p,p′γ) 843 keV above 0.876 MeV (2 mb, ESTIMATE ×3);
  * heavy backings (Ta, Mo, W, Cu, Pd): Coulomb excitation only (≤ 1.1 MeV lines; ESTIMATE),
    (p,γ) and (p,n) are below 10⁻¹² per proton (Coulomb barrier 7–13 MeV);
  * the hydrogen dose where the beam stops, and the time to the blister thresholds;
  * residual-gas chemistry on metallic Li (it is a getter).

    python lnl/target/opt_backing.py   → out/target/options/{lines,stacks,hydrogen,li_chemistry}.csv
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import target_model as TM

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'out' / 'target' / 'options'
E_CH = 1.602176634e-19
N_A = 6.02214076e23
HBARC = 197.327         # MeV fm
AMU = 931.494           # MeV

# --------------------------------------------------------------------------- #
# materials for the stepping: composition (atoms) and density
# --------------------------------------------------------------------------- #
MATS = {
    'Li':      dict(comp={'Li': 1}, rho=0.534),
    'Li2O':    dict(comp={'Li': 2, 'O': 1}, rho=2.013),
    'LiF':     dict(comp={'Li': 1, 'F': 1}, rho=2.635),
    'Diamond': dict(comp={'C': 1}, rho=3.515),
    'Graphite': dict(comp={'C': 1}, rho=1.0),
    'Al':      dict(comp={'Al': 1}, rho=2.70),
    'Cu':      dict(comp={'Cu': 1}, rho=8.96),
    'Ta':      dict(comp={'Ta': 1}, rho=16.65),
    'Mo':      dict(comp={'Mo': 1}, rho=10.22),
    'Pd':      dict(comp={'Pd': 1}, rho=12.02),
}
AW = {'Li': 6.941, 'O': 15.999, 'F': 18.998, 'C': 12.011, 'Al': 26.982, 'Cu': 63.546,
      'Ta': 180.95, 'Mo': 95.95, 'Pd': 106.42}
STP_AS = {'Ta': 'W', 'Pd': 'Ag'}          # PSTAR stand-ins


def S(comp, e_mev):
    """MeV cm²/g, Bragg."""
    mt = sum(AW[e] * n for e, n in comp.items())
    tot = 0.0
    for e, n in comp.items():
        el = STP_AS.get(e, e)
        se = float(TM.STP.element(el, e_mev))
        tot += AW[e] * n / mt * se
    return tot


def n_atoms(comp, el):
    """atoms of el per gram."""
    mt = sum(AW[e] * n for e, n in comp.items())
    return comp.get(el, 0) * N_A / mt


# --------------------------------------------------------------------------- #
# cross sections
# --------------------------------------------------------------------------- #
def bw(ep_kev, er_lab_kev, gam_cm_kev, wg_ev, A_t):
    """Breit-Wigner (Γp ≈ Γ) in barns: π ƛ² ωγ Γ / ((E − E_R)² + Γ²/4), cm energies."""
    mu = A_t / (A_t + 1.0)
    e_cm = np.asarray(ep_kev, float) * mu
    er_cm = er_lab_kev * mu
    lam2 = HBARC ** 2 / (2 * mu * AMU * e_cm / 1e3) * 1e-2        # fm² → b  (1 b = 100 fm²)
    return np.pi * lam2 * (wg_ev * 1e-3) * gam_cm_kev / ((e_cm - er_cm) ** 2 + gam_cm_kev ** 2 / 4)


def bw_int(e_lo, e_hi, er_lab_kev, gam_cm_kev, wg_ev, A_t):
    """∫σ dE_lab over [e_lo, e_hi] (b·keV), analytic in the Lorentzian with ƛ² at the midpoint,
    so narrow resonances are not under-sampled by the step.  Over the whole resonance
    it gives the thick-target result (λ²/2) ωγ / μ."""
    mu = A_t / (A_t + 1.0)
    em = 0.5 * (e_lo + e_hi) * mu
    lam2 = HBARC ** 2 / (2 * mu * AMU * max(em, 1.0) / 1e3) * 1e-2
    er = er_lab_kev * mu
    g = gam_cm_kev
    lor = (2 / g) * (np.arctan(2 * (e_hi * mu - er) / g) - np.arctan(2 * (e_lo * mu - er) / g))
    return np.pi * lam2 * (wg_ev * 1e-3) * g * lor / mu


# ¹³C(p,γ) 556 keV: Γγ = 11.8 eV, γ₀ 9.1 eV (8.06 MeV); ω = 3/4 (Skowronski 2025 / [31])
C13_RES = dict(er=556.4, gam=34.9, wg=0.75 * 11.8, f_g0=9.1 / 11.8)
C12_RES = dict(er=456.8, gam=34.0, wg=0.60)        # 2.37 MeV
AL_RES = [dict(er=632.2, gam=0.005, wg=0.26), dict(er=773.7, gam=0.005, wg=0.13),
          dict(er=991.9, gam=0.1, wg=1.91)]          # 10.76 MeV (992) etc.; narrow (ESTIMATE for 632/773)


def sigma_478_b(ep_kev):
    """⁷Li(p,p′γ) 478 keV σ (b, per natural-Li atom) from Bykov 2021's thick-Li yield Y = 4.9e6 (E/1 MeV)^4.6 /µC
    (fit through 1.0 and 1.67 MeV); σ = (dY/dE) S_Li / n_Li per proton; 0 below 0.55 MeV."""
    e = np.asarray(ep_kev, float) / 1e3
    dYdE = 4.9e6 * 4.6 * e ** 3.6 / (1e-6 / E_CH)            # per proton per MeV
    s_li = np.array([float(TM.STP.element('Li', x)) for x in np.atleast_1d(e)])
    n_li = N_A / 6.941
    return np.where(e > 0.55, dYdE * s_li / n_li * 1e24, 0.0)


# --------------------------------------------------------------------------- #
# stepping
# --------------------------------------------------------------------------- #
def run_stack(ep_kev, layers, f13=0.0107, step_kev=0.5):
    """layers: [(mat, µm)].  Per-proton yields of the lines and the depth where the beam
    stops (which layer)."""
    e = float(ep_kev)
    y = dict(L478=0.0, C12_237=0.0, C13_806=0.0, C13_other=0.0, Al_res=0.0, Al_843=0.0)
    stop_layer = 'dump'
    dep = {}
    for name, t_um in layers:
        comp, rho = MATS[name]['comp'], MATS[name]['rho']
        m_left = rho * t_um * 1e-4                            # g/cm²
        e_in = e
        while m_left > 0 and e > 20:
            s = S(comp, e / 1e3)
            dm = min(step_kev / 1e3 / s, m_left)
            de = dm * s * 1e3
            em = e - de / 2
            if 'Li' in comp:
                y['L478'] += float(sigma_478_b(em)[()]) * n_atoms(comp, 'Li') * dm * 1e-24
            if 'C' in comp:
                nC = n_atoms(comp, 'C') / (s * 1e3) * 1e-24          # atoms/g per (keV per g/cm²) → per keV
                y['C12_237'] += bw_int(e - de, e, C12_RES['er'], C12_RES['gam'], C12_RES['wg'], 12) * (1 - f13) * nC
                c13 = bw_int(e - de, e, C13_RES['er'], C13_RES['gam'], C13_RES['wg'], 13) * f13 * nC
                y['C13_806'] += c13 * C13_RES['f_g0']
                y['C13_other'] += c13 * (1 - C13_RES['f_g0'])
            if 'Al' in comp:
                nA = n_atoms(comp, 'Al') / (s * 1e3) * 1e-24
                y['Al_res'] += sum(bw_int(e - de, e, r['er'], r['gam'], r['wg'], 27) for r in AL_RES) * nA
                if em > 876:
                    y['Al_843'] += 2e-3 * n_atoms(comp, 'Al') * dm * 1e-24
            e -= de
            m_left -= dm
        dep[name] = e_in - max(e, 0)
        if e <= 20 and stop_layer == 'dump':
            stop_layer = name
            e = 0.0
    return y, stop_layer, max(e, 0.0), dep


# film for layered_yield (target_model's FILMS)
FILM_TM = {'Li': 'Li', 'Li2O': 'Li2O', 'LiF': 'LiF'}
UM_TO_UG = {'Li': 0.534e2, 'Li2O': 2.013e2, 'LiF': 2.635e2}     # µg/cm² per µm

STACKS = {
    # key: (E_p keV, layers, f13, note)
    'Li2O 300 / Al 10 µm (FEAS baseline)': (1100, [('Li2O', 1.49), ('Al', 10)], 0.0107, ''),
    'Li2O 300 / diamond 50 µm': (1100, [('Li2O', 1.49), ('Diamond', 50)], 0.0107, ''),
    'Li2O 300 / Ta 10 / diamond': (1100, [('Li2O', 1.49), ('Ta', 10), ('Diamond', 300)], 0.0107, ''),
    'Li2O 300 / Cu 1 mm': (1100, [('Li2O', 1.49), ('Cu', 1000)], 0.0107, ''),
    'Li 20 µm / diamond 1 mm (Pierfrancesco)': (1100, [('Li', 20), ('Diamond', 1000)], 0.0107, ''),
    'Li 20 µm / ¹²C diamond 1 mm (99.99 %)': (1100, [('Li', 20), ('Diamond', 1000)], 1e-4, ''),
    'Li 20 µm / Ta 10 µm / diamond 1 mm': (1100, [('Li', 20), ('Ta', 10), ('Diamond', 1000)], 0.0107, ''),
    'Li 20 µm / Cu 1 mm (BNCT-style)': (1100, [('Li', 20), ('Cu', 1000)], 0.0107, ''),
    'Li 20 µm / Al 10 µm': (1100, [('Li', 20), ('Al', 10)], 0.0107, ''),
    'Li 10 µm / diamond 1 mm': (1100, [('Li', 10), ('Diamond', 1000)], 0.0107, ''),
    'Li 40 µm / diamond 1 mm': (1100, [('Li', 40), ('Diamond', 1000)], 0.0107, ''),
    'Li 20 µm / diamond, E_p 1.20 MeV': (1200, [('Li', 20), ('Diamond', 1000)], 0.0107, ''),
}


def stack_table():
    rows, lines = [], []
    for key, (ep, layers, f13, _) in STACKS.items():
        film, t_um = layers[0]
        be = TM.layered_yield(ep, [TM.film(FILM_TM[film], t_um * UM_TO_UG[film])])
        y, stop, e_out, dep = run_stack(ep, layers, f13)
        g0 = be['Y_g0']
        row = dict(stack=key, Ep_keV=ep, film=film, film_um=t_um,
                   E_after_film_keV=be['E_out_keV'], beam_stops_in=stop,
                   Y_g0_per_p=g0, Y_g0g1_per_p=g0 + be['Y_g1'], f441=be['f17'], f18res=be['f18res'],
                   g0_per_uC=g0 / E_CH * 1e-6, rel_g0_vs_baseline=np.nan)
        for k, v in y.items():
            row[f'Y_{k}_per_p'] = v
            row[f'{k}_per_g0'] = v / g0
        rows.append(row)
        for k, eg in (('L478', 0.478), ('C12_237', 2.37), ('C13_806', 8.06), ('Al_res', 10.76), ('Al_843', 0.843)):
            if y[k] > 0:
                lines.append(dict(stack=key, line=k, E_MeV=eg, per_p=y[k], per_uC=y[k] / E_CH * 1e-6,
                                  per_8Be_g0=y[k] / g0))
    t = pd.DataFrame(rows)
    base = t.loc[t['stack'].str.startswith('Li2O 300 / Al'), 'Y_g0_per_p'].iloc[0]
    t['rel_g0_vs_baseline'] = t.Y_g0_per_p / base
    return t, pd.DataFrame(lines)


# --------------------------------------------------------------------------- #
# hydrogen where the beam stops
# --------------------------------------------------------------------------- #
BLISTER = {   # onset fluence /cm², source
    'Cu': (1.0e19, 'Budker INP, 2 MeV p, 263 °C: blisters from 1e19, dense at 3e19 (RSI 2017)'),
    'Ta': (3.4e19, 'no change up to 3.4e19 (RSI 2017); ≥ 6.7e20 claimed (Metals 7, 558)'),
    'Al': (1.0e18, 'low-energy literature, ×10 uncertain'),
    'Diamond': (np.nan, 'unknown at MeV / 20–150 °C (ask): H is immobile in diamond; '
                        '1.2e17 /cm² at 350 keV blisters only after a >1400 °C anneal'),
    'Li': (np.inf, 'LiH forms; no blistering mechanism in a soft metal'),
}


def hydrogen_table():
    rows = []
    for I in (0.25, 0.5, 1, 4):
        for sig in (2.0, 3.0):
            peak = I * 1e-6 / E_CH / (2 * np.pi * (sig / 10) ** 2)       # /cm²/s at the centre
            for mat, (thr, src) in BLISTER.items():
                days = thr / (peak * 86400) if np.isfinite(thr) else (np.inf if thr == np.inf else np.nan)
                rows.append(dict(I_uA=I, sigma_mm=sig, peak_fluence_per_day=peak * 86400, stop_material=mat,
                                 blister_onset=thr, days_to_onset=days, source=src))
    # a wobbler / larger spot: σ 2 mm swept over a ±6 mm square spreads the dose ×~(1 + (12/(2.5σ))²) ≈ ×6
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# metallic Li as a getter: how fast the residual gas converts the film
# --------------------------------------------------------------------------- #
def li_chemistry():
    """Hertz–Knudsen flux × sticking (s ≈ 1 for H₂O, O₂ and CO₂ on fresh Li; ~10⁻³ for N₂ at RT
    and none for H₂, CH₄; ESTIMATES).  Each molecule takes 2 Li (H₂O → LiOH + ½H₂ or Li₂O;
    O₂ → 4 Li; N₂ → 6 Li).  Li metal 4.63×10²² /cm³."""
    kT = 1.380649e-23 * 293
    rows = []
    gases = {'H2O': (18, 1.0, 2), 'O2': (32, 1.0, 4), 'CO2': (44, 0.5, 2), 'N2': (28, 1e-3, 6)}
    n_li = 4.63e22
    for p_mbar in (1e-6, 1e-7, 1e-8):
        for g, (M, s, nli) in gases.items():
            flux = p_mbar * 100 / np.sqrt(2 * np.pi * M * 1.6605e-27 * kT) * 1e-4      # /cm²/s
            li_per_s = flux * s * nli
            um_per_day = li_per_s * 86400 / n_li * 1e4
            rows.append(dict(p_partial_mbar=p_mbar, gas=g, flux_cm2_s=flux, sticking=s,
                             Li_consumed_um_per_day=um_per_day, days_to_eat_20um=20 / um_per_day))
    return pd.DataFrame(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    t, lines = stack_table()
    t.to_csv(OUT / 'stacks.csv', index=False)
    lines.to_csv(OUT / 'lines.csv', index=False)
    pd.set_option('display.width', 250)
    print(t[['stack', 'E_after_film_keV', 'beam_stops_in', 'Y_g0_per_p', 'rel_g0_vs_baseline', 'f441',
             'L478_per_g0', 'C12_237_per_g0', 'C13_806_per_g0', 'Al_res_per_g0']].to_string(index=False))
    h = hydrogen_table()
    h.to_csv(OUT / 'hydrogen.csv', index=False)
    print(h[(h.sigma_mm == 2.0)].pivot(index='stop_material', columns='I_uA', values='days_to_onset').round(2))
    c = li_chemistry()
    c.to_csv(OUT / 'li_chemistry.csv', index=False)
    print(c.to_string(index=False))


if __name__ == '__main__':
    main()
