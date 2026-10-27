#!/usr/bin/env python3
"""
bham_targets.py -- which ³He target for the Birmingham HF-ADNeF beam (TARGET_GEANT.md §1, analytic).

    python birmingham/bham_targets.py         # -> birmingham/out/targets/target_trade.csv

At a broad, collimated fast-neutron beam the cell is thin (n L σ_tot ≪ 1 for every candidate), so the
capture rate is

    captures/s = N(³He in the beam) · φ · ⟨σ_nγ⟩,

N ∝ litres (STP) of ³He inside the beam.  Pressure does not enter except through the volume the same
gas needs.  A low-pressure target therefore needs a wider beam (more beam through the apparatus, a
vertex spread over more of the cell) for the same rate; a high-pressure one needs walls.  This script
lays out the candidates of the Geant4 run (submit_bham.py) on those axes:
  * ³He inventory (total, in the beam) and its cost (he4_bag: 2500 €/L(STP));
  * captures and IPC pairs per day, 2.8 MeV × 30 mA, cell centre 2 m from the Li (bham_beam.beam);
  * the radial material a 90° lepton crosses (x/X₀) and the Highland angle at 10 MeV/c;
  * the vertex spread along and across the beam the reconstruction has to live with;
  * the beam area (all beam-induced terms scale with it at fixed flux).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / 'out' / 'targets'
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'survey'))
import bham_beam as BB            # noqa: E402
import survey_yield as Y          # noqa: E402

EUR_PER_L = 2500.0                # he4_bag/he4_bag.py HE3_EUR_PER_L (market 2-5 k$)
L_STP = 22.414                    # L/mol at 0 °C, 1 atm
NA = 6.02214076e23
DAY = 86400.0
# radiation length [g/cm²] and density [g/cm³] (PDG; vessel_design/mylar_wrap_vessel.py)
X0 = {'He3': 70.7, 'Mylar': 39.95, 'Al': 24.01, 'CFRP': 42.70, 'Be': 65.19}
RHO = {'Mylar': 1.40, 'Al': 2.699, 'CFRP': 1.55, 'Be': 1.848}
ME = 0.51099895


def he3_g_cm3(p_bar, t_k=293.15):
    return p_bar * 1e5 * 3.016e-3 / (8.314 * t_k) * 1e-3


def highland(p_mev, x):
    beta = p_mev / np.hypot(p_mev, ME)
    return np.degrees(13.6 / (beta * p_mev) * np.sqrt(x) * (1 + 0.038 * np.log(x)))


# key: label, p [bar], gas R [cm], gas L [cm], radial walls [(mat, mm)], beam radius [cm]
TARGETS = {
    'cap500': ('n_TOF 500 bar capsule (as built)', 500.0, 1.0, 4.0, [('Al', 0.6), ('CFRP', 0.9)], 1.0),
    'c30': ('30 bar cell, R 5 × 40 cm, Be/CFRP (NFS build C)', 30.0, 5.0, 40.0, [('Be', 0.1), ('CFRP', 0.3)], 4.0),
    'c10': ('10 bar cell, R 5 × 40 cm, Al 25 µm + CFRP 0.3', 10.0, 5.0, 40.0, [('Al', 0.025), ('CFRP', 0.3)], 4.0),
    'bal5': ('1 bar mylar balloon, R 5 × 40 cm', 1.0, 5.0, 40.0, [('Mylar', 0.012), ('Al', 0.007)], 4.0),
    'bal10': ('1 bar mylar balloon, R 10 × 40 cm', 1.0, 10.0, 40.0, [('Mylar', 0.012), ('Al', 0.007)], 9.0),
}
CAPSULE_G_CM3 = 62.7e-3           # MX17_Full_Geant He3Gas_500bar (real-gas density at 500 bar)


def gas_volume(key):
    _, p, R, L, _, _ = TARGETS[key]
    if key == 'cap500':                                   # cylinder + two hemispherical ends
        return np.pi * R ** 2 * L + 4 / 3 * np.pi * R ** 3
    return np.pi * R ** 2 * L


def rows(ep=2.8, current=30e-3, dist_m=2.0):
    b, _ = BB.beam(ep, current, dist_m)
    phi = b['flux_at_cell']                               # n/cm²/s on axis (Ø8 cm spot)
    e = np.linspace(0.005, 1.3, 600)
    f = BB.spectrum_on_grid(ep, e)
    sig = np.trapezoid(f * Y.sig(e, 102), e) * 1e-24      # ⟨σ_nγ⟩ cm²
    alpha = float(np.trapezoid(f * Y.alpha(e), e))
    out = []
    for k, (lab, p, R, L, walls, rb) in TARGETS.items():
        rho = CAPSULE_G_CM3 if k == 'cap500' else he3_g_cm3(p)
        V = gas_volume(k)
        Vb = V if rb >= R else np.pi * rb ** 2 * L        # gas inside the beam
        litres = rho * V / 3.016 * L_STP
        litres_b = rho * Vb / 3.016 * L_STP
        cap = rho * Vb / 3.016 * NA * phi * sig
        x_gas = rho * R / X0['He3']
        x_wall = sum(RHO[m] * t / 10 / X0[m] for m, t in walls)
        x = x_gas + x_wall
        out.append(dict(key=k, target=lab, p_bar=p, R_cm=R, L_cm=L, beam_r_cm=rb, beam_area_cm2=np.pi * rb ** 2,
                        he3_L_STP=litres, he3_L_in_beam=litres_b, he3_cost_keur=litres * EUR_PER_L / 1e3,
                        captures_per_s=cap, ipc_pairs_per_day=cap * alpha * DAY,
                        x_over_X0_pct=100 * x, wall_pct=100 * x_wall, theta0_10MeV_deg=highland(10.0, x),
                        vtx_sigma_along_mm=10 * L / np.sqrt(12), vtx_sigma_across_mm=10 * rb / np.sqrt(2),
                        captures_per_beam_cm2=cap / (np.pi * rb ** 2)))
    t = pd.DataFrame(out)
    t['captures_vs_c30'] = t.captures_per_s / float(t.loc[t.key == 'c30', 'captures_per_s'].iloc[0])
    return t, dict(phi=phi, sigma_ub=sig * 1e30, alpha=alpha, n_cell=b['n_cell'])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    t, m = rows()
    t.to_csv(OUT / 'target_trade.csv', index=False, float_format='%.4g')
    pd.set_option('display.width', 250)
    print(f"φ = {m['phi']:.3g} n/cm²/s at 2 m (2.8 MeV, 30 mA); ⟨σ_nγ⟩ = {m['sigma_ub']:.1f} µb; ⟨α⟩ = {m['alpha']:.2e}")
    print(t.drop(columns='target').to_string(index=False, float_format=lambda v: f'{v:.3g}'))


if __name__ == '__main__':
    main()
