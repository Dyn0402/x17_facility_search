#!/usr/bin/env python3
"""
survey_absorbed.py -- cold, thermal and epithermal beams: the ILL Geant4 rate walls
carried to every facility whose neutrons are absorbed in the ³He.

    python survey/survey_absorbed.py        # -> survey/out/absorbed_reach.{csv,png}

The ILL campaign (ill/FEASIBILITY_SIM.md §13) gives the 50-day reach vs the absorbed
rate R, with every class split out (walls_tubeMy_e14.csv: He flight tube, mylar
window, panel, E_sum > 14).  Two facts carry the whole thermal class:

  1. The yield per absorbed neutron does not depend on the facility (1/v, survey_yield).
  2. The best reach sits at R ≈ 6e10 n/s (MM occupancy + DREAM), which PF1B already
     exceeds (1.2e11 with a Ø5 cm spot).
So a facility with capture flux Φ reaches the ILL curve at R ≤ R_max = 1.2e11 Φ/Φ_PF1B,
and can never do better than PF1B with this apparatus.

Epithermal (BNCT) beams: a neutron of 1 eV-10 keV gives k = P_epi/P_th ≈ 3.6× the
pairs (survey_yield, 1/E spectrum, the 30 bar × 40 cm cell it needs).  At the same
entering rate the backgrounds are taken from the ILL table unchanged (they come from
neutrons scattered and captured around the cell, which an epithermal beam also does:
an assumption), and

    ρ' = ρ · sqrt((k·IPC + ACC + COS + WALL) / (IPC + ACC + COS + WALL)) / k

(Fisher counting scaling; the X17 and IPC scale with k, the rest does not).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
if not hasattr(np, 'trapezoid'):
    np.trapezoid = np.trapz
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import survey_yield as Y                                     # noqa: E402

OUT = HERE / 'out'
WALLS = ROOT / 'ill' / 'sim' / 'analysis_v3' / 'cons' / 'walls_tubeMy_e14.csv'
HW = 'nTOF 5 ns + veto, per-arm coinc (strict)'
PHI_PF1B = 2.2e10            # n/cm²/s capture flux at the guide exit (Petoukhov 2023)
R_PF1B = 1.2e11              # absorbed n/s PF1B delivers into a Ø5 cm spot (ill/out/beam_spot.csv)
REF_8BE = 1.64e-3            # ILL convention: X17/IPC(M1) at ATOMKI's ⁸Be strength
REF_4HE = 1.5e-3             # ATOMKI ⁴He (the NFS convention)

# (key, label, capture flux n/cm²/s [or epithermal flux], kind, status, source)
FACILITIES = [
    ('pf1b', 'ILL PF1B (cold)', 2.2e10, 'cold', 'operating to 2033', 'Petoukhov et al. 2023; ill/FACILITY.md'),
    ('mephisto', 'FRM II MEPHISTO (cold)', 2.0e10, 'cold', 'reactor offline since 2020',
     'expected ≈ PF1B (Soldner et al., ANNI paper, arXiv:1811.11692)'),
    ('anni', 'ESS ANNI (cold, pulsed long-pulse)', 2.5e10, 'cold', 'proposed; E5 port shared with HIBEAM',
     'simulated at 5 MW, arXiv:1811.11692'),
    ('ngc', 'NIST NCNR NG-C (cold)', 8.1e9, 'cold', 'reactor restarted 2026, users late 2026',
     'aCORN, arXiv:2012.14379 (before the 2023 cold-source upgrade)'),
    ('fnpb', 'ORNL SNS FnPB (cold, pulsed)', 1.0e9, 'cold', 'operating',
     '~1e9 n/cm²/s, 10 × 12 cm² (ORNL BL13 flyer, polarised)'),
    ('carr', 'CIAE CARR cold guide', 1.0e9, 'cold', 'operating', '> 1e9 at the guide exit (design study)'),
    ('fipps', 'ILL FIPPS (thermal, collimated)', 1.8e8 / R_PF1B * PHI_PF1B, 'thermal', 'operating',
     '1.8e8 n/s into the n_TOF capsule (ill/FACILITY.md); entered as the PF1B-equivalent flux'),
    ('bnct1', 'BNCT epithermal beam, 1e9 n/cm²/s (IAEA floor)', 1.0e9, 'epithermal',
     'reactor (KUR, LVR-15, THOR, RA-6) and accelerator BNCT', 'IAEA-TECDOC-1223; DawonMedax ≥ 1e9'),
    ('bnct5', 'BNCT epithermal beam, 5e9 n/cm²/s (best case)', 5.0e9, 'epithermal',
     'best reactor beams (MIT FCB class)', 'upper bound'),
]


def walls():
    d = pd.read_csv(WALLS)
    return {sc: d[(d.hw == HW) & (d.scenario == 'as is') & (d.knobs == sc)].sort_values('R')
            for sc in ('MM occ + DREAM', 'MM occ ÷10, DAQ 10 µs')}


def reach_curve(w, k):
    ipc = w.M1 + w.E0
    other = w.ACC + w.COS + w.WALL + w.G
    return w.reach3 * np.sqrt((k * ipc + other) / (ipc + other)) / k


def main():
    OUT.mkdir(exist_ok=True)
    W = walls()
    p_th = float(Y.pairs_per_neutron(2.53e-8)[0])
    k_epi = Y.spectrum_mean_P(Y.E_GRID, Y.epithermal()) / p_th
    rows, curves = [], []
    for key, label, phi, kind, status, src in FACILITIES:
        if kind == 'epithermal':
            r_max = phi * np.pi * 5.0 ** 2           # the 30 bar × 40 cm cell, R = 50 mm
            k = k_epi
        else:
            r_max = R_PF1B * phi / PHI_PF1B
            k = 1.0
        for sc, w in W.items():
            rr = reach_curve(w, k).values
            ok = w.R.values <= r_max * 1.0001
            if not ok.any():
                i = 0
                best_r = float(rr[0] * np.sqrt(w.R.values[0] / r_max))   # below the grid: ∝ 1/√R
                best_R = r_max
            else:
                i = int(np.argmin(np.where(ok, rr, np.inf)))
                best_r, best_R = float(rr[i]), float(w.R.values[i])
            rows.append(dict(key=key, facility=label, kind=kind, phi=phi, R_max=r_max, k_pairs=k, scenario=sc,
                             R_best=best_R, rho3_50d=best_r, vs_8Be=best_r / REF_8BE, vs_4He=best_r / REF_4HE,
                             status=status, source=src))
            curves += [dict(key=key, scenario=sc, R=R_, rho3=r_, allowed=bool(o))
                       for R_, r_, o in zip(w.R.values, rr, ok)]
    t = pd.DataFrame(rows)
    t.to_csv(OUT / 'absorbed_reach.csv', index=False, float_format='%.4g')
    pd.set_option('display.width', 220)
    print(f'k(epithermal 1/E, 30 bar × 40 cm) = {k_epi:.2f}')
    print(t[['key', 'scenario', 'R_max', 'R_best', 'rho3_50d', 'vs_8Be']].to_string(index=False))
    figure(t, pd.DataFrame(curves))


def figure(t, c):
    import matplotlib.pyplot as plt
    sys.path.insert(0, str(ROOT / 'ill'))
    import figstyle as fs
    fs.use()
    fig, ax = plt.subplots(figsize=fs.FIG)
    sc = 'MM occ + DREAM'
    for key, col, lab in (('pf1b', fs.MUTED, 'thermal/cold: ILL curve (k = 1)'),
                          ('bnct1', fs.ACCENT, 'epithermal 1/E (k = 3.6)')):
        q = c[(c.key == key) & (c.scenario == sc)]
        ax.plot(q.R, q.rho3, color=col, lw=1.6, label=lab)
    d = t[t.scenario == sc]
    for (R_, r_), g in d.groupby(['R_best', 'rho3_50d']):
        ax.plot(R_, r_, 'o', ms=4, color=fs.COPPER if (g.kind == 'epithermal').all() else fs.INK)
        ax.annotate(', '.join(g.key), (R_, r_), fontsize=7, xytext=(3, -10 if (g.kind == 'epithermal').all() else 4),
                    textcoords='offset points')
    ax.axhline(REF_8BE, color=fs.TRACK, lw=0.8, ls=':')
    ax.text(1.2e9, REF_8BE * 1.1, 'ATOMKI (⁸Be level)', color=fs.TRACK, fontsize=8)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(1e8, 2e12)
    ax.set_xlabel('absorbed (entering) neutrons/s')
    ax.set_ylabel('X17/IPC at 3σ, 50 d')
    ax.legend(fontsize=8, frameon=False, loc='upper right')
    fs.title(ax, 'No thermal facility beats PF1B; epithermal gains ≤ ×2',
             'ILL Geant4 rate walls (He tube, mylar window, panel, E_sum > 14), as-is MM and DREAM')
    fs.save(fig, OUT / 'absorbed_reach_fig', data=d)


if __name__ == '__main__':
    main()
