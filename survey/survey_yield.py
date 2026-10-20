#!/usr/bin/env python3
"""
survey_yield.py -- the one curve every facility is compared on: ³He IPC pairs
per neutron that enters the cell, as a function of E_n; and the source spectra
the survey folds against it.

    python survey/survey_yield.py          # -> survey/out/yield_vs_En.{png,csv}

Pairs per entering neutron, cell of areal density n·L:

    P(E) = σ_nγ/σ_tot · (1 − exp(−n L σ_tot)) · α(W)

σ from ENDF/B (MX17_Full_Geant/data/He3.h5, via ganil_nfs/nfs_fold.py); α the
Born pairs per photon (nTof_x17 ipc_born, E1 at W = E*(E_n); the thermal
M1 + E0 value, 4.8e-11 per absorption, comes out the same to 3 %).  Elastic
scattering is counted as attenuation, not as a second chance: a lower bound
for a thick cell.

Why this curve decides the survey (SURVEY.md §2):
  * thermal: (n,p) is 5316 b and takes every neutron, so P = 4.8e-11;
  * 1-10 keV: direct E1 capture rises faster than 1/v, P ×10-80 per absorbed n;
  * 0.2-2 MeV: the cell is thin, P ≈ n L σ_nγ α ≈ 1e-8 for the 30 bar × 40 cm
    cell, ×200 the thermal value per neutron.
So a fast neutron is worth ~200 thermal ones, and the facility ranking is a
ranking in neutrons per second through the cell × P(E), up to the rate walls.
"""
from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
if not hasattr(np, 'trapezoid'):          # numpy < 2 on the Linux desktop
    np.trapezoid = np.trapz
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / 'out'
sys.path.insert(0, str(ROOT / 'ganil_nfs'))
sys.path.insert(0, str(ROOT / 'ill'))
sys.path.insert(0, str(Path.home() / 'PycharmProjects/nTof_x17'))
import nfs_fold as F                                         # noqa: E402

KB_T = 1.380649e-23
DAY = 86400.0

# cells: name -> (pressure bar, length cm, radius cm)
CELLS = {
    'NFS cell 30 bar × 40 cm': (30.0, 40.0, 5.0),        # PLAN_GANIL_NFS §4.4 build C (the NFS Geant4 cell)
    'n_TOF capsule 500 bar × 8 cm': (500.0, 8.0, 1.0),   # MX17_Full_Geant DetectorConstruction
    'ILL cell 1 bar × 8 cm': (1.0, 8.0, 4.0),            # ill G1 (R = 40 mm), for the thermal row
}
REF_CELL = 'NFS cell 30 bar × 40 cm'


def n_per_cm3(p_bar, t_k=293.15):
    return p_bar * 1e5 / (KB_T * t_k) * 1e-6


def sig(e_mev, mt):
    """ENDF/B ³He cross section in barn (nfs_fold.sigma; ∝1/E above 20 MeV)."""
    return F.sigma(np.atleast_1d(np.asarray(e_mev, float)), mt)


def sig_tot(e_mev):
    return sig(e_mev, 2) + sig(e_mev, 103) + sig(e_mev, 104) + sig(e_mev, 102)


@lru_cache(maxsize=None)
def _alpha_grid():
    w = np.linspace(20.55, 50.0, 60)
    return w, F.alpha_e1(w)


def alpha(e_mev):
    w, a = _alpha_grid()
    return np.interp(F.w_of_en(np.atleast_1d(e_mev)), w, a)


def pairs_per_neutron(e_mev, cell=REF_CELL):
    """IPC pairs per neutron entering the cell along its axis."""
    p, L, _ = CELLS[cell]
    nl = n_per_cm3(p) * L
    e = np.atleast_1d(np.asarray(e_mev, float))
    st = sig_tot(e) * 1e-24
    return sig(e, 102) * 1e-24 / st * (1 - np.exp(-nl * st)) * alpha(e)


def captures_per_neutron(e_mev, cell=REF_CELL):
    """³He(n,γ) per entering neutron (no α)."""
    return pairs_per_neutron(e_mev, cell) / alpha(e_mev)


# --------------------------------------------------------------------------- #
# Source spectra: normalised dN/dE [1/MeV] on an E grid [MeV].  Each is a stand-in
# for a published spectrum; SURVEY.md §3 gives the source and what it leaves out.

E_GRID = np.unique(np.concatenate([np.geomspace(1e-9, 1e-3, 120), np.geomspace(1e-3, 0.2, 120),
                                   np.linspace(0.2, 45.0, 600)]))


def _norm(e, f):
    f = np.clip(np.nan_to_num(f), 0, None)
    return f / np.trapezoid(f, e)


def watt(e=E_GRID, a=0.988, b=2.249):
    """²³⁵U thermal-fission Watt spectrum (ENDF a, b): MEDAPP/NECTAR converter."""
    return _norm(e, np.exp(-e / a) * np.sinh(np.sqrt(b * e)))


def li7pn_thick(e=E_GRID, e_max=0.85, e_min=0.05):
    """Thick ⁷Li(p,n) at 0°, E_p ≈ 2.6 MeV: a flat 0.05-0.85 MeV stand-in (Lee & Zhou 1999
    give mean/max 0.33/0.79 MeV at E_p = 2.5 MeV)."""
    return _norm(e, ((e > e_min) & (e < e_max)).astype(float))


def maxwell_flux(e=E_GRID, kt=0.025):
    """Flux-weighted Maxwellian (E·exp(−E/kT)): LiLiT/FRANZ near-threshold ⁷Li(p,n), kT ≈ 25-30 keV."""
    return _norm(e, e * np.exp(-e / kt))


def mono(e=E_GRID, e0=2.45, width=0.05):
    """A quasi-monoenergetic line (D-D 2.45 MeV, D-T 14.1 MeV)."""
    return _norm(e, np.exp(-0.5 * ((e - e0) / width) ** 2))


def per_decade(e=E_GRID, fr=None):
    """Lethargy-flat within each decade, with the given fraction per decade:
    fr = {(lo, hi) MeV: fraction}.  Used for the white spallation/photoneutron beams."""
    f = np.zeros_like(e)
    for (lo, hi), x in fr.items():
        m = (e >= lo) & (e < hi)
        f[m] = x / (np.log(hi / lo) * e[m])
    return _norm(e, f)


def epithermal(e=E_GRID, lo=0.5e-6, hi=10e-3):
    """1/E between 0.5 eV and 10 keV: the IAEA BNCT epithermal band."""
    return _norm(e, np.where((e > lo) & (e < hi), 1 / e, 0.0))


def nfs(e=E_GRID):
    """NFS d(40)+Be 0°, from the ganil_nfs fold (0.1-45 MeV)."""
    t = pd.read_csv(ROOT / 'ganil_nfs' / 'out' / 'fold_table.csv')
    return _norm(e, np.interp(e, t.E_n, t.n_per_s_MeV, left=0, right=0))


# Back-n ES#1 (CSNS), measured per-decade flux at 100 kW, small collimators (IHEP 2024 status slides,
# from NIM A 1060 (2024) 169045; refs/IHEP2024_BackN_status_p2_p5.pdf, slide 5): 0.1-1 eV 4.08e3, 1-10 eV 1.79e4,
# 10-100 eV 3.01e4, 0.1-1 keV 5.01e4, 1-10 keV 1.23e5, 10-100 keV 4.30e5, 0.1-1 MeV 2.98e6, 1-10 MeV 2.77e6,
# 10-200 MeV 6.21e5; total 7.03e6.  Shape assumed the same for the Φ50 mm large spot (Tang et al. 2021).
BACKN = {(1e-7, 1e-3): (4.08e3 + 1.79e4 + 3.01e4 + 5.01e4) / 7.03e6, (1e-3, 0.1): (1.23e5 + 4.30e5) / 7.03e6,
         (0.1, 1.0): 2.98e6 / 7.03e6, (1.0, 10.0): 2.77e6 / 7.03e6, (10.0, 45.0): 6.21e5 / 7.03e6}
# n_TOF EAR1/EAR2: close to isolethargic from 1 eV to ~100 MeV (we keep ≤ 45 MeV)
NTOF = {(1e-6, 1e-3): 0.375, (1e-3, 0.1): 0.25, (0.1, 1.0): 0.125, (1.0, 10.0): 0.125, (10.0, 45.0): 0.125}
# LANSCE WNR 30-degree ICE House: hard, 5e6 n/cm²/s above 1 MeV (LANL page); the split is an estimate
WNR = {(0.1, 1.0): 0.15, (1.0, 10.0): 0.35, (10.0, 45.0): 0.50}


def spectrum_mean_P(e, f, cell=REF_CELL):
    return float(np.trapezoid(f * pairs_per_neutron(e, cell), e))


def window_fraction(e, f, lo=0.2, hi=2.75):
    m = (e >= lo) & (e <= hi)
    return float(np.trapezoid(f[m], e[m]))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    e = np.geomspace(2.53e-8, 40.0, 400)
    tab = pd.DataFrame({'E_n_MeV': e, 'theta_min_deg': F.theta_min_deg(e), 'alpha': alpha(e),
                        'sigma_ng_ub': sig(e, 102) * 1e6, 'sigma_np_b': sig(e, 103)})
    for c in CELLS:
        tab[f'P [{c}]'] = pairs_per_neutron(e, c)
    p_th = float(pairs_per_neutron(2.53e-8, REF_CELL)[0])
    print(f'thermal: {p_th:.3g} pairs per neutron (thick cell; repo value 4.8e-11 per absorption)')

    spectra = {'thermal 25 meV': mono(e0=2.53e-8, width=1e-9), 'epithermal 1/E 0.5 eV-10 keV': epithermal(),
               'LiLiT kT 25 keV': maxwell_flux(), 'thick ⁷Li(p,n) 2.6 MeV': li7pn_thick(),
               'fission (Watt)': watt(), 'D-D 2.45 MeV': mono(),
               'Back-n ES#1': per_decade(fr=BACKN), 'n_TOF (isolethargic)': per_decade(fr=NTOF),
               'NFS d(40)+Be': nfs(), 'LANSCE WNR 30°': per_decade(fr=WNR), 'D-T 14.1 MeV': mono(e0=14.1, width=0.2)}
    rows = []
    for k, f in spectra.items():
        rows.append(dict(spectrum=k, P_mean=spectrum_mean_P(E_GRID, f), P_vs_thermal=spectrum_mean_P(E_GRID, f) / p_th,
                         frac_0p2_2p75=window_fraction(E_GRID, f), frac_below_2p75=window_fraction(E_GRID, f, 0, 2.75),
                         frac_above_8p5=window_fraction(E_GRID, f, 8.5, 99)))
    st = pd.DataFrame(rows)
    st.to_csv(OUT / 'spectra_summary.csv', index=False, float_format='%.4g')
    print(st.to_string(index=False))
    figure(tab, st)


def figure(tab, st):
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use()
    fig, ax = plt.subplots(figsize=fs.FIG)
    cols = [fs.ACCENT, fs.COPPER, fs.MUTED]
    for c, col in zip(CELLS, cols):
        ax.plot(tab.E_n_MeV, tab[f'P [{c}]'], color=col, lw=1.6, label=c)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(1e-8, 40)
    ax.set_ylim(1e-12, 1e-6)
    ax.axvspan(0.2, 2.75, color=fs.BAND_SIGNAL, alpha=0.08, lw=0)
    ax.text(0.25, 3e-7, 'ATOMKI-like E*\n(θ_min ≥ 99°)', color=fs.BAND_SIGNAL, fontsize=8)
    ax.set_xlabel('neutron energy [MeV]')
    ax.set_ylabel('IPC pairs per neutron entering the cell')
    ax.legend(loc='upper left', fontsize=8, frameon=False)
    fs.title(ax, 'A 1 MeV neutron is worth ~200 thermal ones',
             'thermal: (n,p) takes every neutron; above ~1 keV direct E1 capture grows faster than 1/v')
    fs.save(fig, OUT / 'yield_vs_En', data=tab)


if __name__ == '__main__':
    main()
