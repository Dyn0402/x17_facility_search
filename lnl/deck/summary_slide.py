"""One-slide summary, "Possible measurement at LNL", for the end of the n_TOF talk (2026-10-14 draft).

All numbers come from lnl/talk/lnl_summary_figs.py:numbers() (reach_geant.csv days_3d / S3d_per_day,
acceptance_geant.csv pair_tag, trigger_scint/costs.py), the same function that writes the stand-alone
figures in lnl/out/talk/ for pasting into the talk. The scattering numbers are lnl/out/nd/smear_scan.csv.
"""
import math
import sys
from pathlib import Path

import pandas as pd

import slidedoc as sd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'talk'))
import lnl_summary_figs as LS  # noqa: E402

AB, BP = LS.AB, LS.BP


def fd(d):
    return f'{d:.0f}' if d >= 10 else f'{d:.1f}'


def _smear(O):
    """Days to 3σ vs the angular smearing (FEASIBILITY_SIM §15, lnl/sim/lnl_smear_nd.py)."""
    p = O / 'nd' / 'smear_scan.csv'
    return pd.read_csv(p)


def summary_slide(D, O):
    N = LS.numbers()
    C = N['cases']
    a, b = C[f'{AB}|1'], C[f'{BP}|1']
    a4, b4 = C[f'{AB}|4'], C[f'{BP}|4']
    tag_a, tag_b = N['pair_tag'][AB], N['pair_tag'][BP]
    ps, pvt = N['price_keur']['PS'], N['price_keur']['PVT']
    col = {AB: sd.ORANGE, BP: sd.PURPLE}

    # ---- left: the reaction ----
    left = sd.col(
        sd.p('<b>⁷Li(p,e⁺e⁻)⁸Be</b>: ATOMKI\'s own reaction', 27),
        sd.callout('<b>A proton beam on lithium, not neutrons on ³He.</b> DC protons at E_p = 1.04–1.10 MeV from the LNL Van de '
                   'Graaffs (AN2000 / CN) on a thin Li₂O film: the same reaction, energy and target thickness as ATOMKI 2016.', sd.BLUE, 22),
        sd.callout('<b>An exact re-measurement with an independent detector.</b> One E_p fixes E* = 18.15 MeV, so the X17 edge sits at '
                   '133–139°; the Micromegas tracks point each lepton back to the target and reject cosmics.', sd.BLUE, 22),
        sd.callout('<b>A cleaner problem than n_TOF.</b> No neutrons below E_p = 1.88 MeV; a 1.5 µm film instead of a 500 bar capsule '
                   '(σ68 4.6° instead of 14.5°).', sd.GREEN, 22),
        gap=12, w=560)

    # ---- middle: X17 per day and days to 3σ ----
    rows = [(f'{LS.LABEL[AB]}', a['x17_per_day'], col[AB],
             f"{LS.LABEL[AB]}, 1 µA: {a['x17_per_day']:.1f} X17/day in the θ × |y| × E_sum fit at R = 5.8×10⁻⁶ "
             f"({a4['x17_per_day']:.0f}/day at 4 µA on CN); background {a['bkg_per_day']:.0f}/day."),
            (f'{LS.LABEL[BP]}', b['x17_per_day'], col[BP],
             f"{LS.LABEL[BP]}, 1 µA: {b['x17_per_day']:.0f} X17/day ({b4['x17_per_day']:.0f}/day at 4 µA); "
             f"background {b['bkg_per_day']:.0f}/day.")]
    bars = sd.hbars(rows, 200, width=360, h=40, label_w=270, fmt=lambda v: f'{v:.0f} / day', size=22)

    P = sd.Plot(640, 330, x=(0.1, 100, 'log'), y=(0, 8), xlabel='days of beam (1 µA)', ylabel='significance',
                margin=(16, 20, 70, 76))
    P.xticks([(v, f'{v:g}') for v in (0.1, 1, 10, 100)]).yticks([(v, f'{v}') for v in (0, 3, 5, 8)])
    P.hline(3, sd.MUT, '6 6', 1.5, label='3σ')
    P.hline(5, sd.MUT, '6 6', 1.5, label='5σ')
    ts = [10 ** (k / 20) for k in range(-20, 41)]
    for hw, c in ((AB, a), (BP, b)):
        d3 = c['days_3sigma']
        zs = [3 * math.sqrt(t / d3) for t in ts]
        P.line([t for t, z in zip(ts, zs) if z <= 8], [z for z in zs if z <= 8], col[hw], 4, markers=False)
        P.points([d3], [3], col[hw], r=9, tips=[f'{LS.LABEL[hw]}: 3σ at the ATOMKI ratio in {d3:.2f} days at 1 µA '
                                                 f'(5σ in {c["days_5sigma"]:.1f} d); {fd(C[f"{hw}|4"]["days_3sigma"])} d at 4 µA.'])
        P.text(d3 * 1.15, 2.2, f'{fd(d3)} d', 24, col[hw], weight=700)
    mid = sd.col(sd.p('<b>X17 in acceptance per day</b> (1 µA, R = 5.8×10⁻⁶)', 23), bars,
                 sd.p('<b>Time to the ATOMKI sensitivity</b>', 23), P.svg('significance vs days'), gap=10, w=660)

    # ---- right: the hardware change and the open studies ----
    sm = _smear(O)
    sm = sm[(sm.hw == BP) & (sm.analysis == 'θ × |y| × E_sum')].sort_values('factor').head(3)
    smear_txt = (f'3σ goes {" → ".join(fd(d) for d in sm.days)} d as σ68 goes '
                 f'{" → ".join(f"{round(s * 2) / 2:g}°" for s in sm.x17_sigma68)}')
    right = sd.col(
        sd.callout(f'<b>Big plastics = more trigger acceptance, nothing else.</b> One 75×75×5 cm plate per arm replaces the two bars '
                   f'and the liquid: X17 pairs triggered {tag_a * 100:.1f} % → {tag_b * 100:.0f} % (×{N["trigger_gain"]:.0f}), '
                   f'X17/day ×{N["x17_gain"]:.0f}, days ÷{N["days_gain"]:.0f}.', sd.PURPLE, 21),
        sd.callout(f'<b>≈ €{ps["plates_keur"][1]:.0f}k</b> for four polystyrene plates (€{ps["plates_keur"][0]:.0f}–'
                   f'{ps["plates_keur"][2]:.0f}k), ~€{ps["all_in_keur"][1]:.0f}k with the SiPM readout. Budgetary, no labour or VAT.',
                   sd.GREY, 21),
        sd.p('<b>To study</b>', 23),
        sd.callout(f'<b>Scattering</b> in the beam pipe and target chamber smears the edge: {smear_txt}. Needs the real LNL beam-line drawings in Geant4.', sd.ORANGE, 20),
        sd.callout('<b>Calorimetry</b>: the 5 cm plates must measure E_sum and the energy split |y| to separate the 15.1 MeV γ₁ '
                   'IPC (2× the 18 MeV line) and test the background shape. Bench-test a plate.', sd.ORANGE, 20),
        gap=12, w=520)

    D.slide('lnl-summary', sd.title('Possible measurement at LNL',
                                    f'⁷Li(p,e⁺e⁻)⁸Be with the MX17 apparatus: 3σ at the ATOMKI ratio in ~{fd(b["days_3sigma"])} day with big '
                                    f'plastics, ~{fd(a["days_3sigma"])} days with the n_TOF stack. Geant4, hover for details.')
            + sd.row(left, mid, right, gap=34),
            f"""<p>Draft of the single closing slide for the n_TOF talk (15 Oct 2026). Stand-alone figures for pasting:
<code>lnl/out/talk/{{x17_per_day,significance_days,lnl_summary}}.{{png,pdf}}</code>, numbers in
<code>lnl/out/talk/numbers.json</code>; regenerate with <code>python lnl/talk/lnl_summary_figs.py</code>.</p>
<p>Scenario 'ATOMKI 2016 anomaly' (Li₂O 300 µg/cm², E_p = 1.10 MeV, 1 µA), X17 m = 16.7 MeV at R = Γ_X/Γ_γ = 5.8×10⁻⁶,
selection MM 15° + TOF. X17/day is the signal inside the θ × |y| × E_sum fit (E_sum {a['esum_window']} MeV as built,
{b['esum_window']} MeV big plastics), of ~{a['produced_per_day']:.0f} produced per day. Days are <code>reach_geant.csv</code>
<code>days_3d</code> (FEASIBILITY_SIM §14.5): calibrated n_TOF-anchored response, background normalisations and shape structure
free, DAQ live time included; significance vs time scales as √t (beyond ~a week the unmodelled shape errors need the wider fit of §17.3). The as-built stack needs a working liquid scintillator. Pair
trigger acceptance from <code>acceptance_geant.csv</code> (both arms tagged). Price from <code>trigger_scint/costs.py</code>:
4 × 78×80×5 cm polystyrene with two 3" PMTs each (PVT: €{pvt['plates_keur'][1]:.0f}k), + all 20 SiPM bars read and a
160-channel FERS DAQ. Scattering: <code>smear_scan.csv</code> (§15), each event's reco − truth angle scaled by a factor.</p>""",
            short='LNL summary')
