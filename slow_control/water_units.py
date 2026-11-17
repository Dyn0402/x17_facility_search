#!/usr/bin/env python3
"""water_units.py -- ppmv of water in the chamber gas <-> partial pressure, RH, dew/frost point.

    python slow_control/water_units.py          # prints the table, writes out/water_units.csv

Decides what a humidity chip in a flow cell can resolve. Saturation pressure: Magnus (Sonntag 1990 constants) over
water above 0 C and over ice below. Gas pressure 1013 hPa (the chambers run at ~1 bar).
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

P_GAS = 1013.25  # hPa


def es_water(t):     # hPa, Sonntag 1990
    return 6.112 * math.exp(17.62 * t / (243.12 + t))


def es_ice(t):
    return 6.112 * math.exp(22.46 * t / (272.62 + t))


def dew_frost(pw):
    """Dew point (over water) if > 0 C, else frost point (over ice), in C."""
    x = math.log(pw / 6.112)
    td = 243.12 * x / (17.62 - x)
    if td >= 0:
        return td
    return 272.62 * x / (22.46 - x)


def main():
    rows = []
    for ppm in (10, 30, 100, 300, 1000, 2000, 5000, 10000, 15000, 20000):
        pw = ppm * 1e-6 * P_GAS
        r = dict(ppmv=ppm, pw_hPa=round(pw, 4), dew_frost_C=round(dew_frost(pw), 1))
        for t in (20, 25):
            r[f"RH_{t}C_pct"] = round(100 * pw / es_water(t), 3)
        rows.append(r)
    # what +-1 %RH (SHT45-class absolute) and 0.01 %RH (resolution/repeatability class) mean in ppm at 20/25 C
    sens = {t: es_water(t) / P_GAS * 1e4 for t in (20, 25)}   # ppmv per %RH
    out = Path(__file__).with_name("out")
    out.mkdir(exist_ok=True)
    with open(out / "water_units.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{'ppmv':>7} {'p_w hPa':>9} {'Td/Tf C':>8} {'RH@20':>8} {'RH@25':>8}")
    for r in rows:
        print(f"{r['ppmv']:>7} {r['pw_hPa']:>9.3f} {r['dew_frost_C']:>8.1f} {r['RH_20C_pct']:>8.3f} {r['RH_25C_pct']:>8.3f}")
    for t, s in sens.items():
        print(f"at {t} C: 1 %RH = {s:.0f} ppmv; 0.01 %RH = {s/100:.1f} ppmv")
    # sensitivity of RH reading to cell temperature at fixed water: dRH/RH = -d ln es/dT ~ -6 %/K
    t = 22.0
    d = (math.log(es_water(t + 0.5)) - math.log(es_water(t - 0.5)))
    print(f"RH at fixed ppm changes by {-100*d:.1f} % of reading per K of cell temperature (so the chip's own T matters)")


if __name__ == "__main__":
    main()
