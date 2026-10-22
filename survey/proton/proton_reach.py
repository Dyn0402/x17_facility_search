#!/usr/bin/env python3
"""
proton_reach.py -- the reach model for the proton survey: what a proton machine of a given energy range
and DC current gives the MX17 apparatus, scaled from the two Geant4 anchors.

    PY=~/PycharmProjects/nTof_x17/.venv/bin/python
    $PY survey/proton/proton_reach.py          # -> survey/proton/out/current_scan.{csv,png}

Imported by proton_catalogue.py.  PROTON_SURVEY.md §1-2 explains every number.

The figure of merit is the one the LNL and Demokritos studies quote: **beam days to 3σ at the ATOMKI
strength** (statistics, the calibrated 3D/θ×|y| fits), on one of the three ATOMKI claims:

  be8  ⁷Li(p,e⁺e⁻)⁸Be at 1.03-1.10 MeV (18.15 MeV state), R = 5.8e-6   Geant4: lnl/FEASIBILITY_SIM.md §15
  he4  ³H(p,e⁺e⁻)⁴He at 0.5-0.9 MeV on Ti-T, B_x = 5.1e-6                Geant4: demokritos/ESTIMATES.md §6.2
  c12  ¹¹B(p,e⁺e⁻)¹²C at 1.5-2.5 MeV, B_x = 3.4e-6                       ESTIMATE scaled from be8 (§1.3)

Days fall as 1/(I · live) at fixed S/B (Fisher, background-dominated).  Two things stop that:
  * the target: a thin film on a thin backing takes ~4 µA (lnl/target/TARGET_STUDY.md §5); a water-cooled
    thick backing moved downstream (Demokritos' trick, ×1.06 in days) takes more.  How much more is an
    ESTIMATE: CAP below, nominal 20 µA (Li₂O, B), 10 µA (Ti-T);
  * DREAM: live = 1/(1 + f τ), with the LNL §14.1 trigger rates (pairs never prescaled, singles prescaled
    to ≤ 20 /s).  Not a limit below ~1 mA.
So every machine above ~20 µA gives the same days: the apparatus, not the accelerator, sets the reach.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / 'out'

# ---- the three ATOMKI claims ------------------------------------------------------------------------
# days: days to 3σ at the ATOMKI strength at 1 µA, statistics only (big plastics, as built)
# x17_day: X17 produced per day per µA into 4π at the ATOMKI strength (no acceptance), for the crude headline
# window: the incident proton energies a machine must reach for the claim [MeV] (⁸Be: both ATOMKI 2016 energies;
# ⁴He: the 0.9 MeV anchor point; ¹²C: ATOMKI's 11σ point at 1.88 MeV); tritium: needs a Ti-T target
REACTIONS = {
    'be8': dict(label='⁷Li(p,e⁺e⁻)⁸Be, 18.15 MeV', short='⁸Be', window=(1.03, 1.10), tritium=False,
                days=dict(big=1.00, built=17.0), x17_day=920., strength='R = 5.8×10⁻⁶ (ATOMKI 2016)',
                status='Geant4', src='lnl/FEASIBILITY_SIM.md §15 (3D fit, calibrated response, MM 15° + TOF, m 16.7); '
                                     'X17/day lnl/ESTIMATES.md §1 (Li₂O 300 µg/cm², 1.10 MeV)'),
    'he4': dict(label='³H(p,e⁺e⁻)⁴He, 20.5-20.8 MeV', short='⁴He', window=(0.90, 0.90), tritium=True,
                days=dict(big=3.6, built=35.), x17_day=2.0e3, strength='B_x = 5.1×10⁻⁶ (ATOMKI 2021)',
                status='Geant4', src='demokritos/ESTIMATES.md §6.2 (Ti-T on 1 mm Cu at +12 cm, θ × |y| fit; S/B ≈ 1 %, '
                                     'systematics open); X17/day §1 (2.1 mg/cm² Ti-T, 0.9 MeV)'),
    'c12': dict(label='¹¹B(p,e⁺e⁻)¹²C, 17.23 MeV', short='¹²C', window=(1.88, 1.88), tritium=False,
                days=None, x17_day=None, strength='B_x = 3.4×10⁻⁶ (ATOMKI 2022)',
                status='ESTIMATE', src='scaled from be8 (PROTON_SURVEY.md §1.3): ATOMKI 2 mg/cm² ¹¹B, Γγ0 = 44 eV'),
}

# ---- ¹²C, scaled from ⁸Be (ESTIMATE until Geant4) ----------------------------------------------------
# σ(p,γ0) at the 17.23 MeV 1⁻ resonance (E_p = 1.388, Γ = 1.15 MeV, Γp = 1 MeV, Γγ0 = 44 eV, NNDC 11b_p_g_res):
# Breit-Wigner peak 4π ƛ² g Γp Γγ0 / Γ², g = 3/8, ƛ = 4.22 fm at E_cm 1.272 MeV -> 28 µb; 25 µb averaged over
# ATOMKI's 300 keV-thick 2 mg/cm² target.
SIG_C12 = 25e-30                     # cm²
NB_C12 = 2e-3 / 11.009 * 6.022e23        # atoms/cm² in ATOMKI's 2 mg/cm² ¹¹B (enriched)
P_PER_UA = 6.2415e12
G0_C12 = SIG_C12 * NB_C12 * P_PER_UA      # γ0/s per µA  (~1.7e4)
G0_BE8 = 1.85e3                      # γ0/s per µA, Li₂O 300 µg/cm² at 1.10 MeV (lnl/ESTIMATES.md §1)
R_BE8, R_C12 = 5.8e-6, 3.4e-6
KAPPA_C12 = 2.0                      # acceptance × E1-IPC shape penalty vs ⁸Be at 150-160°: ESTIMATE, range 1-4
C12_SCALE = (G0_BE8 / G0_C12) * (R_BE8 / R_C12) ** 2 * KAPPA_C12
REACTIONS['c12']['days'] = {k: v * C12_SCALE for k, v in REACTIONS['be8']['days'].items()}
REACTIONS['c12']['x17_day'] = G0_C12 * R_C12 * 86400

# ---- the apparatus ---------------------------------------------------------------------------------
TAU = 298e-6                         # DREAM RAW busy per event [s]
# LNL §14.1 (Geant4 ⁸Be γ + cosmics, Li₂O 300 at 1.04 MeV): arm legs/s and pair triggers/s = a + b·I[µA]
DAQ = dict(big=dict(legs=(88., 64.9), pairs=(21.7, 0.29)),
           built=dict(legs=(36., 22.3), pairs=(3.47, 0.03)))
SINGLES_MAX = 20.                    # prescaled single-arm triggers kept per second
I_THIN = 4.0                         # µA a thin film on a thin cooled backing takes (TARGET_STUDY §5)
CAP = dict(be8=20., c12=20., he4=10.)   # µA with a water-cooled thick backing downstream: ESTIMATE (§2.2)
OFFSET = 3.6 / 3.4                   # days cost of the thick backing moved downstream (demokritos §6.2, big plastics)


def live(i_ua, hw='big'):
    """DREAM live fraction at i_ua µA: pairs never prescaled, singles prescaled to ≤ SINGLES_MAX/s."""
    (la, lb), (pa, pb) = DAQ[hw]['legs'], DAQ[hw]['pairs']
    legs, pairs = la + lb * i_ua, pa + pb * i_ua
    f = pairs + min(legs, SINGLES_MAX)
    return 1.0 / (1.0 + f * TAU)


def days(reaction, i_ua, hw='big', cap=True):
    """Beam days to 3σ at the ATOMKI strength at i_ua µA of machine current (capped by the target)."""
    r = REACTIONS[reaction]
    i_use = min(i_ua, CAP[reaction]) if cap else i_ua
    d = r['days'][hw] * live(1.0, hw) / (i_use * live(i_use, hw))
    return d * (OFFSET if i_use > I_THIN else 1.0)


def covers(reaction, e_lo, e_hi, tritium):
    """Can a machine of proton range [e_lo, e_hi] MeV (and tritium licence 'yes'/'ask'/'no') test this claim?"""
    lo, hi = REACTIONS[reaction]['window']
    if REACTIONS[reaction]['tritium'] and tritium == 'no':
        return False
    return e_lo <= lo + 1e-9 and e_hi >= hi - 1e-9


def main():
    sys.path.insert(0, str(HERE.parent.parent / 'ill'))
    import figstyle as fs
    import matplotlib.pyplot as plt
    import pandas as pd
    fs.use()
    I = np.logspace(-1, 3.3, 200)
    rows = []
    for rk in REACTIONS:
        for hw in ('big', 'built'):
            for i in I:
                rows.append(dict(reaction=rk, hw=hw, i_ua=i, live=live(min(i, CAP[rk]), hw), days=days(rk, i, hw),
                                 days_uncapped=days(rk, i, hw, cap=False)))
    df = pd.DataFrame(rows)
    fig, ax = fs.figure()
    col = dict(be8='#0072B2', he4='#D55E00', c12='#009E73')
    for rk, r in REACTIONS.items():
        for hw, ls in (('big', '-'), ('built', '--')):
            d = df[(df.reaction == rk) & (df.hw == hw)]
            ax.plot(d.i_ua, d.days, ls, color=col[rk], lw=1.6,
                    label=f"{r['short']} ({'big plastics' if hw == 'big' else 'as built'}{', est.' if r['status'] != 'Geant4' else ''})")
    for x, t in ((1, 'LNL AN2000'), (4, 'LNL CN / thin-target limit'), (20, 'cooled-target cap (est.)')):
        ax.axvline(x, color='0.6', lw=0.8, ls=':')
        ax.text(x * 1.06, 120, t, rotation=90, va='top', fontsize=8, color='0.35')
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlabel('DC proton current the machine delivers at the reaction energy [µA]')
    ax.set_ylabel('beam days to 3σ at the ATOMKI strength')
    ax.set_ylim(0.01, 200)
    ax.legend(fontsize=8, ncol=2, frameon=False, loc='lower left')
    fs.title(ax, 'Above ~20 µA every proton machine is the same', 'statistics only; the target and DREAM, not the beam, set the floor')
    OUT.mkdir(exist_ok=True)
    fs.save(fig, OUT / 'current_scan', data=df)
    print(f"c12 scale vs be8: {C12_SCALE:.3f} (γ0/s/µA {G0_C12:.3g} vs {G0_BE8:.3g}); "
          f"c12 X17/day/µA {REACTIONS['c12']['x17_day']:.3g}")
    for rk in REACTIONS:
        print(rk, {i: (round(days(rk, i, 'big'), 3), round(days(rk, i, 'built'), 2)) for i in (1, 4, 20, 1000)})


if __name__ == '__main__':
    main()
