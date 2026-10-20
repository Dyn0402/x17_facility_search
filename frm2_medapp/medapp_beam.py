#!/usr/bin/env python3
"""
medapp_beam.py -- the FRM II SR10 fission-neutron beam (MEDAPP / NECTAR) for the X17 study
(frm2_medapp/FACILITY.md, FEASIBILITY.md).

    python frm2_medapp/medapp_beam.py         # -> frm2_medapp/out/medapp_spectra.{csv,png}, medapp_beam.csv

Neutrons: ²³⁵U thermal-fission Watt spectrum (ENDF a = 0.988 MeV, b = 2.249 /MeV; mean 1.98 MeV),
plus an "intermediate" 1/E part between 1 keV and 0.5 MeV.  Breitkreutz et al. (NIM A 593 (2008) 466;
Wagner, ÖMPG 2011 slide "Watt spectrum plus intermediate neutrons") measured the spectrum by foil
activation; the intermediate fraction behind the standard B4C filter is not public: 5 % here
(stand-in, (ask)).  Standard filters (1 cm B4C-epoxy + 3.5 cm Pb): 3.2×10⁸ n/cm²/s free in air at
the MEDAPP reference position (SSD 592 cm, effective source 15 × 15 cm²); up to 7×10⁸ without
the Pb (more γ).

γ: mean energy 2.4 MeV behind 3.5 cm Pb (Wagner 2011).  The dose ratio n:γ is 3:1 (0.54 vs
0.20 Gy/min at 2 cm in water); with fluence-to-dose factors (2.4 MeV γ: ~1.0×10⁻¹¹ Gy cm²; fission
neutrons in tissue: ~2.9×10⁻¹¹ Gy cm²) this is ≈ 1 photon per neutron, the survey's k_γ = 1.
The spectrum shape is a stand-in: exp(−E/2.45 MeV) on 0.1-10 MeV (prompt fission + capture γ
hardened by the Pb), which has mean 2.4 MeV.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
if not hasattr(np, 'trapezoid'):
    np.trapezoid = np.trapz

HERE = Path(__file__).resolve().parent
OUT = HERE / 'out'
FLUX_STD = 3.2e8          # n/cm²/s, standard filters, free in air (MLZ 2025 poster; FRM II web page)
FLUX_MAX = 7e8            # n/cm²/s, "depending on filter used" (MLZ JLSRF 2015, Wagner 2007)
GAMMA_PER_N = 1.0         # photons per neutron at the beam (from the 3:1 dose ratio; see the docstring)
INTERMEDIATE = 0.05       # fraction of neutrons in the 1/E part, 1 keV-0.5 MeV (stand-in)
AREA = 50.0               # cm², the beam collimated to the Ø8 cm cell spot (MLC 1.5 cm leaves)


def watt(e, a=0.988, b=2.249):
    return np.exp(-e / a) * np.sinh(np.sqrt(b * e))


def neutron_spectrum(e, inter=INTERMEDIATE):
    """normalised dN/dE on the grid e (MeV)."""
    w = watt(e)
    w = w / np.trapezoid(w, e)
    m = (e > 1e-3) & (e < 0.5)
    i = np.where(m, 1 / np.maximum(e, 1e-12), 0.0)
    i = i / np.trapezoid(i, e)
    return (1 - inter) * w + inter * i


def gamma_spectrum(e, e0=2.45):
    f = np.where((e > 0.1) & (e < 10.0), np.exp(-e / e0), 0.0)
    return f / np.trapezoid(f, e)


def beam(flux=FLUX_STD, area=AREA):
    return dict(flux=flux, n_cell=flux * area, gamma_cell=GAMMA_PER_N * flux * area)


def main():
    OUT.mkdir(exist_ok=True)
    e = np.geomspace(1e-3, 20, 2000)
    fn, fg = neutron_spectrum(e), gamma_spectrum(e)
    d = pd.DataFrame(dict(E=e, dNdE_n=fn, dNdE_gamma=fg))
    win = (e >= 0.2) & (e <= 2.75)
    rows = [dict(case=c, flux=f, n_cell=f * AREA, gamma_cell=GAMMA_PER_N * f * AREA,
                 mean_En=float(np.trapezoid(e * fn, e)), frac_window=float(np.trapezoid(fn[win], e[win])),
                 frac_above_2p75=float(np.trapezoid(fn[e > 2.75], e[e > 2.75])),
                 mean_Eg=float(np.trapezoid(e * fg, e)))
            for c, f in (('standard filters', FLUX_STD), ('no Pb (max)', FLUX_MAX))]
    t = pd.DataFrame(rows)
    t.to_csv(OUT / 'medapp_beam.csv', index=False, float_format='%.4g')
    print(t.to_string(index=False))
    sys.path.insert(0, str(HERE.parent / 'ill'))
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use()
    fig, ax = fs.figure()
    ax.plot(e, e * fn, color=fs.ACCENT, lw=1.6, label='neutrons (Watt + 5 % 1/E)')
    ax.plot(e, e * fg, color=fs.COPPER, lw=1.4, ls='--', label='γ (stand-in, mean 2.4 MeV)')
    ax.axvspan(0.2, 2.75, color=fs.BAND_SIGNAL, alpha=0.08, lw=0)
    ax.set_xscale('log')
    ax.set_xlabel('E [MeV]')
    ax.set_ylabel('E dN/dE (normalised)')
    ax.legend(frameon=False, fontsize=8)
    fs.title(ax, 'MEDAPP: a fission spectrum, 70 % of it in the ATOMKI-like window',
             'shaded: E_n 0.2-2.75 MeV (E* ≤ 22.1 MeV); 3.2×10⁸ n/cm²/s with the standard filters')
    fs.save(fig, OUT / 'medapp_spectra', data=d)


if __name__ == '__main__':
    main()
