#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
costs.py -- budgetary cost model for the trigger-scintillator options.

    python trigger_scint/costs.py       # prints the tables; used by analyze.py

Every price is a BUDGETARY estimate in EUR (2026, before VAT, no labour), with
a (low, central, high) range.  None of these vendors publish list prices for
this class of item (Eljen / Luxium / Nuvia, Hamamatsu / ET Enterprises, CAEN,
PETsys all quote on request), so the central values come from the public
reference points below and from typical quotes; get real quotes before
committing.

Reference points (public):
  * EJ-200-equivalent PVT, polished, 300 x 150 x 5 mm: $369
    (epic-scintillator.com) -> ~1.6 $/cm^3 for a SMALL polished piece.
  * EJ-200, 1/4" x 10" x 10" rough cut: $74-131 per piece (cosmic.lbl.gov
    parts list) -> 0.18-0.32 $/cm^3 as-cast.
  * Hamamatsu R9779 (2" fast timing PMT) budgetary $850-1050 at qty 180
    (Rutgers MUSE quote, 2013) -- small quantities and today's prices are
    ~2x that.
Large cast sheets with diamond-milled edges sit between the two scintillator
points; 0.6 EUR/cm^3 is the central value, 0.35-1.0 the range.
"""
from __future__ import annotations

# (low, central, high) EUR
PVT_PER_CM3 = (0.35, 0.60, 1.00)        # cast PVT (EJ-200 / BC-408 class), edges finished
PS_PER_CM3 = (0.15, 0.25, 0.40)         # polystyrene-based (cast/extruded, ~70 % light)
PMT = {                                 # tube + divider (+ mu-metal), EUR
    '2"': (1600, 2200, 3000),           # fast 2" (R13089 / ET 9214B class)
    '3"': (2300, 3300, 4300),           # R6091 / ET 9305 class
    '5"': (3500, 4600, 6500),           # R877 / R1250 / ET 9390 class
}
GUIDE_SMALL = (400, 800, 1500)          # PMMA fishtail / trapezoid, end face <= ~60 cm wide
GUIDE_LARGE = (800, 1500, 2500)         # wider ends (twisted strips or long fishtail)
WRAP_MECH_PER_SLAB = {2: (800, 1500, 2500), 5: (1500, 3000, 5000), 10: (2500, 5000, 8000)}
HV_PER_CH = (0, 600, 1000)              # 0 if the n_TOF plastic HV (8 ch) comes along
DIGI_PER_PMT_CH = (500, 800, 1200)      # share of a 16-ch 500 MS/s-1 GS/s digitizer

# LS revival: new PMTs + bases on the four funnels, fresh optical coupling,
# possibly a LAB refill/degassing; the n_TOF problem was rate/pile-up, which a
# hardware fix does not cure.
LS_REVIVAL = (2000, 6000, 12000)

# DAQ for the SiPM walls (4 walls x 20 bars x 2 ends = 160 channels)
DAQ = {
    "ganged sums (n_TOF style, 8 ch/wall = 32 ch) on 1x V1742 (DRS4)": (10000, 14000, 18000),
    "160 ch: FERS-5200 (A5202/A5204, Citiroc/Radioroc, bias incl.) x3 + DT5215": (12000, 18000, 25000),
    "160 ch: PETsys TOFPET2 (256-ch system)": (15000, 22000, 32000),
    "160 ch: 5x V1742 DRS4 5 GS/s + VME crate/bridge": (55000, 75000, 90000),
    "160 ch: 3x VX2745 (125 MS/s, 64 ch) + crate": (50000, 65000, 80000),
}
# bringing the 4 un-instrumented bars per wall online and un-ganging the
# preamp boards (SiPMs + preamps for 32 bar-ends, board respin)
SIPM_COMPLETION = (5000, 10000, 18000)


def slab_cost(W_cm, L_cm, T_cm, pmt='3"', n_pmt=2, material="PVT", k=1):
    """One slab, k = 0/1/2 for low/central/high."""
    vol = W_cm * L_cm * T_cm
    sc = vol * (PVT_PER_CM3 if material == "PVT" else PS_PER_CM3)[k]
    guide = (GUIDE_LARGE if W_cm > 60 else GUIDE_SMALL)[k] * n_pmt
    tkey = min(WRAP_MECH_PER_SLAB, key=lambda t: abs(t - T_cm))
    mech = WRAP_MECH_PER_SLAB[tkey][k]
    pm = PMT[pmt][k] * n_pmt
    elec = (HV_PER_CH[k] + DIGI_PER_PMT_CH[k]) * n_pmt
    return dict(scint=sc, guides=guide, mech=mech, pmts=pm, elec=elec,
                total=sc + guide + mech + pm + elec)


def four_slabs(W_cm, L_cm, T_cm, pmt='3"', n_pmt=2, material="PVT"):
    return tuple(4 * slab_cost(W_cm, L_cm, T_cm, pmt, n_pmt, material, k)["total"] for k in range(3))


def main():
    for args in [(70, 80, 2), (78, 80, 2), (60, 60, 2), (78, 80, 5), (78, 80, 10)]:
        for pmt in ('2"', '3"', '5"'):
            lo, c, hi = four_slabs(*args, pmt=pmt)
            print(f"4 x {args} cm, 2 x {pmt:3s} each: {c/1e3:5.1f} kEUR  ({lo/1e3:.1f}-{hi/1e3:.1f})")
    print("PS instead of PVT, 78x80x5, 3\":",
          [round(x / 1e3, 1) for x in four_slabs(78, 80, 5, material="PS")])


if __name__ == "__main__":
    main()
