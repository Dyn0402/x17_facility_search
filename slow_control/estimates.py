#!/usr/bin/env python3
"""estimates.py -- back-of-envelope numbers behind SENSOR_OPTIONS.md §2 (water ingress, bottle condensation).

    python slow_control/estimates.py

Every input is an estimate or a literature value quoted in research/*.md; nothing here is measured on our set-up.
"""
import math

# ---- water ingress through tubing: measured points, scaled to our flows (ppm ∝ length / flow)
# CERN (arXiv:2202.12007): 6 mm Festo PU, +16 ppm/m at 3 L/h  -> 48 ppm·(L/h) per metre (lab humidity unknown)
# Belle (Lu & McDonald 2007): 1/4" polyolefin, Q = 2080 * l * R / F[cc/min]  -> at R = 0.5: 1040 ppm·cc/min/m = 62 ppm·L/h/m
TUBE = {"PU 6 mm (CERN)": 48.0, "polyolefin 1/4in, 50 %RH (Belle)": 2080 * 0.5 * 60 / 1000}

# ---- water through a drift window: WVTR of 60 µm PET, scaled from typical film data (estimate)
# PET ~ 20 g·25µm/(m²·d) at 38 °C/90 %RH  -> 60 µm: ~8 g/m²/d; at 22 °C/50 %RH ~ x0.1 (vapour-pressure drive x0.22,
# lower temperature ~x0.5) -> ~0.8 g/m²/d bare. Metallisation cuts WVTR 10-100x (good Al coat ~100x).
WINDOW_AREA = 0.40 * 0.36  # m², 40 x 36 cm
WVTR = {"bare PET 60 um": 0.8, "aluminised, poor (x10)": 0.08, "aluminised, good (x100)": 0.008}  # g/m²/day


def ppm_from_mass_rate(g_per_day, flow_l_h):
    ml_per_h = g_per_day / 18.015 * 22414 / 24  # mL(STP) of vapour per hour
    return 1e6 * ml_per_h / (flow_l_h * 1000)


# ---- isobutane vapour pressure (bar), standard values (NIST WebBook class), log-linear interpolation
PV = [(-20, 0.72), (-10, 1.08), (0, 1.57), (10, 2.20), (20, 3.02), (30, 4.05)]


def pvap(t):
    for (t0, p0), (t1, p1) in zip(PV, PV[1:]):
        if t0 <= t <= t1:
            f = (t - t0) / (t1 - t0)
            return math.exp(math.log(p0) + f * (math.log(p1) - math.log(p0)))
    raise ValueError(t)


def dew_temp(frac, p_bar):
    lo, hi = -20.0, 30.0
    target = frac * p_bar
    if target <= pvap(lo):
        return float("-inf")
    if target >= pvap(hi):
        return float("inf")
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if pvap(mid) < target else (lo, mid)
    return 0.5 * (lo + hi)


def main():
    print("Water ingress, ppm per metre of tube:")
    for name, k in TUBE.items():
        print(f"  {name:36s}" + "  ".join(f"{F:4.1f} L/h: {k/F:5.0f}" for F in (0.5, 1, 2.5, 5, 10)))
    print("Water through ONE 40x36 cm window, ppm at the chamber's flow:")
    for name, w in WVTR.items():
        g = w * WINDOW_AREA
        print(f"  {name:28s} {g*1000:6.1f} mg/day  " + "  ".join(f"{F:4.1f} L/h: {ppm_from_mass_rate(g, F):6.0f}" for F in (0.5, 1, 2.5, 5)))
    print("Isobutane dew point in the bottle (deg C) vs bottle pressure:")
    for frac in (0.05, 0.10):
        print(f"  {frac*100:.0f} % iC4H10: " + "  ".join(f"{p:3d} bar: {dew_temp(frac, p):6.1f}" for p in (10, 20, 30, 40, 50)))
    print("  (CERN store 95/5 50 L bottle holds 2.15 m³ -> ~43 bar full)")


if __name__ == "__main__":
    main()
