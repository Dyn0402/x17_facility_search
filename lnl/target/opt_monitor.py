"""
opt_monitor.py — watching the target during the run, carbon build-up, and the
"thicker Al window" question (TARGET_OPTIONS.md §8–§10).

  * PIGE: the 478 keV ⁷Li(p,p′γ) line in a HPGe or LaBr₃ outside the chamber: counts per
    second, the time to 1 % on the Li content, and how the line responds to Li loss and
    to carbon (opt_backing σ₄₇₈, thick-Li yield of Bykov 2021);
  * carbon: Peterson & Laubert (PAC 1977) measured ~1 C atom retained per proton
    (~2 µg/cm²/h) in a diffusion-pumped chamber, ~×10 less with a cold shield or a
    150 °C target; "not measurable" with a LN₂ trap at 10⁻⁷ mbar (Redigolo 2024).
    For each film: the beam-energy shift per day and what it does to the γ₀ yield and
    the 441-keV share;
  * the Micromegas window: attenuation of 0.478 and 17.6 MeV γ in Al, and the pair
    conversion probability a thicker window adds.

    python lnl/target/opt_monitor.py   → out/target/options/{pige,carbon_shift,al_window}.csv
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import target_model as TM
import opt_backing as OB

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'out' / 'target' / 'options'
E_CH = 1.602176634e-19

# full-energy-peak efficiency at 478 keV at 10 cm, point source (ESTIMATES ±30 %):
# ~60 % relative-efficiency coaxial HPGe ≈ 4×10⁻³; 3″×3″ LaBr₃ ≈ 6×10⁻³ (but 3 % FWHM)
DETS = {'HPGe 60 %': (4e-3, 0.0025), 'LaBr3 3x3"': (6e-3, 0.030)}   # (ε at 10 cm, FWHM/E)

FILMS = {'Li₂O 300 µg/cm² at 1.10 MeV': [('Li2O', 1.49)],
         'Li 20 µm at 1.10 MeV': [('Li', 20.0)]}


def y478(layers, ep=1100.0):
    y, _, _, _ = OB.run_stack(ep, layers + [('Ta', 10)])
    return y['L478']


def pige_table():
    rows = []
    for name, layers in FILMS.items():
        yp = y478(layers)
        for I in (0.25, 1.0, 4.0):
            n = yp * I * 1e-6 / E_CH                       # 478 keV γ/s into 4π
            for det, (e10, fw) in DETS.items():
                for d_cm in (25, 50, 100):
                    eff = e10 * (10 / d_cm) ** 2
                    peak = n * eff
                    # everything else hitting the crystal: the 478 Compton continuum and the
                    # high-energy γ (≈ ×4 the peak, ESTIMATE)
                    tot = 4 * peak / 0.25 if peak > 0 else 0
                    rows.append(dict(film=name, I_uA=I, det=det, d_cm=d_cm, Y478_per_p=yp, gam478_per_s=n,
                                     peak_cps=peak, total_cps_est=tot, s_to_1pct=1e4 / peak,
                                     ok_rate=tot < (3e4 if det.startswith('HPGe') else 3e5)))
    return pd.DataFrame(rows)


def pige_sensitivity():
    """d ln Y478 / d(thickness) and per keV of carbon in front: can PIGE tell them apart?"""
    rows = []
    for name, layers in FILMS.items():
        y0 = y478(layers)
        mat, t = layers[0]
        y_thin = y478([(mat, 0.9 * t)])
        # carbon in front: 10 µg/cm² (≈ 2.3 keV at 1.1 MeV)
        dE = 10e-6 * float(TM.STP.element('C', 1.1)) * 1e3
        y_c = y478(layers, 1100.0 - dE)
        rows.append(dict(film=name, Y478=y0, dlnY_per_10pct_Li_loss=(y_thin - y0) / y0,
                         dlnY_per_10ug_C=(y_c - y0) / y0, C_10ug_keV=dE))
    return pd.DataFrame(rows)


def carbon_shift():
    """Days of running at 1 µA vs carbon on the front (three vacuum classes), and what the
    γ₀ yield and the 441-keV share do for the thin and the thick film."""
    rate_atoms_per_p = {'diffusion pumps, no trap (1977)': 1.0, 'cold shield or hot target': 0.1,
                        'LN₂ trap, 10⁻⁷ mbar (Redigolo 2024)': 0.01}
    spot_cm2 = 2 * np.pi * 0.2 ** 2
    rows = []
    for vac, k in rate_atoms_per_p.items():
        for I in (0.25, 1.0, 4.0):
            ug_per_day = k * I * 1e-6 / E_CH * 86400 / spot_cm2 * 12.011 / 6.022e23 * 1e6
            for days in (1, 7, 14):
                c_ug = ug_per_day * days
                for name, layers in FILMS.items():
                    mat, t = layers[0]
                    ug = t * OB.UM_TO_UG[mat]
                    y0 = TM.layered_yield(1100.0, [TM.film(mat, ug)])
                    yc = TM.layered_yield(1100.0, [({'C': 1}, c_ug), TM.film(mat, ug)])
                    rows.append(dict(vacuum=vac, C_per_p=k, I_uA=I, days=days, C_ug_cm2=c_ug,
                                     dE_keV=c_ug * float(TM.STP.element('C', 1.1)) * 1e-3, film=name,
                                     g0_rel=yc['Y_g0'] / y0['Y_g0'], f441=yc['f17'], f441_0=y0['f17']))
    return pd.DataFrame(rows)


def al_window():
    """NIST XCOM-level numbers for Al: μ/ρ(0.478 MeV) = 0.0838 cm²/g, μ/ρ(17.6 MeV, pair-
    dominated) = 0.0227 cm²/g; X₀ = 8.897 cm.  Pair production ≈ (7/9) t/X₀ at 18 MeV."""
    rows = []
    for t_mm in (0.0, 0.06, 0.5, 1.0, 2.0, 5.0, 10.0):
        x = 2.699 * t_mm / 10
        rows.append(dict(Al_mm=t_mm, att_478=1 - np.exp(-0.0838 * x), att_17p6=1 - np.exp(-0.0227 * x),
                         pair_conv_18MeV=7 / 9 * t_mm / 88.97,
                         highland_theta0_deg_8MeV=np.degrees(13.6 / 8.6 * np.sqrt(max(t_mm, 1e-9) / 88.97)
                                                             * (1 + 0.038 * np.log(max(t_mm, 1e-9) / 88.97)))
                         if t_mm > 0 else 0.0))
    return pd.DataFrame(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pd.set_option('display.width', 250)
    p = pige_table()
    p.to_csv(OUT / 'pige.csv', index=False)
    print(p[(p.I_uA == 1.0)].to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    s = pige_sensitivity()
    s.to_csv(OUT / 'pige_sensitivity.csv', index=False)
    print(s.to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    c = carbon_shift()
    c.to_csv(OUT / 'carbon_shift.csv', index=False)
    print(c[(c.I_uA == 1.0)].to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    a = al_window()
    a.to_csv(OUT / 'al_window.csv', index=False)
    print(a.to_string(index=False, float_format=lambda v: f'{v:.3g}'))


if __name__ == '__main__':
    main()
