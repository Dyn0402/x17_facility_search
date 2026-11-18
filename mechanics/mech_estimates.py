"""Back-of-envelope gravity numbers for running MX17 with a horizontal beam.

At n_TOF EAR2 the beam is vertical (sim +Y = up), so every detector face stood
vertical and gravity acted in-plane.  With a horizontal beam the arm plane is
vertical: in the "plus" roll one arm looks down and one looks up; in the "X"
roll (45 deg) every arm is tilted by 45 deg.  This script sizes the loads that
change.  Everything here is an ESTIMATE (textbook plate/membrane formulas,
handbook material data); the numbers to ask the builders for are marked.

Usage:  python mechanics/mech_estimates.py   ->  mechanics/out/*.csv
"""
import csv
import math
import os

G = 9.81
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")

# normal component of gravity on a face, by roll and arm position
ORIENT = {"n_TOF (face vertical)": 0.0,
          "plus roll, top/bottom arm": 1.0,
          "X roll (45 deg), every arm": math.cos(math.radians(45))}


def cathode_sag():
    """Drift cathode: 50 um Kapton + 9 um Cu, 406 mm free span, gas on both sides,
    so its only out-of-plane loads are gravity and electrostatics.  Membrane under
    uniform tension T [N/m]: centre deflection ~ p R^2 / (4 T) (circular membrane,
    R = half the span; good to ~20 % for a square).  T is unknown (ask)."""
    areal = 1420 * 50e-6 + 8960 * 9e-6          # kg/m^2
    p_grav = areal * G                           # N/m^2
    # electrostatics, for comparison: drift field 233 V/cm -> eps0 E^2 / 2
    eps0 = 8.854e-12
    p_drift = 0.5 * eps0 * (233e2) ** 2
    # if the window (5 mm away) is grounded and the cathode sits at ~ -1.1 kV
    p_window_gap = 0.5 * eps0 * (1100 / 5e-3) ** 2
    R = 0.203
    rows = []
    for T in (5, 10, 20, 50, 100):
        for name, f in ORIENT.items():
            d = f * p_grav * R ** 2 / (4 * T) * 1e3
            rows.append(dict(tension_N_per_m=T, orientation=name,
                             sag_mm=round(d, 3), drift_gap_change_pct=round(100 * d / 30, 2)))
    return rows, dict(p_grav=p_grav, p_drift=p_drift, p_window_gap=p_window_gap)


def readout_plate():
    """Readout PCB, FR4 1.7 mm, 402 mm span inside the 8 mm Al ring (rohacell behind
    it ignored, so this is an upper bound).  Square plate, uniform load:
    w = alpha q a^4 / D, alpha = 0.00126 clamped, 0.00406 simply supported."""
    E, nu, t, rho, a = 20e9, 0.15, 1.7e-3, 1850, 0.402
    D = E * t ** 3 / (12 * (1 - nu ** 2))
    q_grav = rho * t * G
    rows = []
    for load, q in (("gravity, face horizontal", q_grav),
                    ("gas overpressure 1 mbar (ask the real value)", 100.0)):
        for edge, alpha in (("clamped", 0.00126), ("simply supported", 0.00406)):
            rows.append(dict(load=load, q_N_per_m2=round(q, 1), edge=edge,
                             deflection_mm=round(alpha * q * a ** 4 / D * 1e3, 3)))
    return rows


def sipm_bar_sag():
    """SiPM-wall bar, PVT 3 mm x 25 mm x 500 mm, held only at its two ends.
    At n_TOF the bars stood vertical (no bending).  Flat (top/bottom arm) it bends
    about its weak axis; on its edge (side arm) about the strong axis."""
    E, rho, L, b, h = 2.5e9, 1023, 0.50, 0.025, 0.003   # E of PVT ~2-3.4 GPa
    w = rho * G * b * h                                  # N/m
    rows = []
    for name, f in ORIENT.items():
        for edge, k in (("ends simply supported", 5 / 384), ("ends clamped", 1 / 384)):
            for axis, I in (("flat (weak axis)", b * h ** 3 / 12), ("on edge (strong axis)", h * b ** 3 / 12)):
                if f == 0:
                    continue
                d = k * f * w * L ** 4 / (E * I) * 1e3
                rows.append(dict(orientation=name, support=edge, bending=axis, sag_mm=round(d, 3)))
    sigma = (w * L ** 2 / 8) * (h / 2) / (b * h ** 3 / 12) / 1e6
    return rows, sigma


def masses():
    """Per-arm masses from the CAD dimensions (MX17_Geant design/GEOMETRY_FROM_CAD.md)
    and MX17_Full_Geant SimConfig.hh.  Electronics, enclosures and fixings: (ask)."""
    al, fr4, pvt, lab, cfrp = 2700, 1850, 1023, 860, 1600
    ring = lambda out, ap, t: (out ** 2 - ap ** 2) * t
    items = [
        ("MM gas frame (Al 440/410, 30 mm)", al * ring(0.44, 0.41, 0.030)),
        ("MM window flange (Al 440/400, 5 mm)", al * ring(0.44, 0.4002, 0.005)),
        ("MM backing plate (Al 470/402, 8 mm)", al * ring(0.47, 0.402, 0.008)),
        ("MM readout PCB (FR4 470 sq, 1.7 mm)", fr4 * 0.47 ** 2 * 1.7e-3),
        ("SiPM bars (20 x 500 x 25 x 3 mm PVT)", pvt * 20 * 0.5 * 0.025 * 0.003),
        ("trigger plastics (2 x 200 x 300 x 20 mm)", pvt * 2 * 0.2 * 0.3 * 0.02),
        ("LS liquid (LAB, 6.5 L)", lab * 6.5e-3),
        ("LS vessel (CFRP 2.6 mm, ~0.42 m^2)", cfrp * 0.42 * 2.6e-3),
        ("LS PMT + base (ESTIMATE)", 0.6),
        ("DREAM FEUs, cables, SiPM enclosure, fixings (ask)", float("nan")),
    ]
    big = pvt * 0.75 * 0.75 * 0.05
    return [dict(item=n, kg=round(m, 2)) for n, m in items], big


def envelope():
    """Radial envelope of one arm, from SimConfig.hh (ill branches), centre to back of the LS slab."""
    mm_face = 20.40
    sipm_front = mm_face + 11.0
    sipm_back = sipm_front + 3.5
    plastic_back = sipm_back + 6.3 + 2.0
    ls_back = sipm_back + 12.5 + 2.12 + 1.0     # +1 cm for the fill bulge (ESTIMATE)
    half_u = 25.0                               # SiPM wall half-width
    plus_low = ls_back
    x_low = (ls_back + half_u) * math.cos(math.radians(45))
    return dict(mm_face_cm=mm_face, sipm_back_cm=sipm_back, plastic_back_cm=round(plastic_back, 1),
                ls_back_cm=round(ls_back, 1), lowest_point_plus_cm=round(plus_low, 1),
                lowest_point_X_cm=round(x_low, 1))


def write(name, rows):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        wr.writeheader()
        wr.writerows(rows)


if __name__ == "__main__":
    rows, p = cathode_sag()
    write("cathode_sag.csv", rows)
    print(f"cathode: gravity {p['p_grav']:.2f} N/m2, drift-field pull {p['p_drift']:.1e}, "
          f"window-gap pull {p['p_window_gap']:.2f} (if the window is grounded)")
    for r in rows:
        if r["orientation"] != "n_TOF (face vertical)":
            print("  ", r)
    rows = readout_plate()
    write("readout_plate.csv", rows)
    for r in rows:
        print("  ", r)
    rows, sigma = sipm_bar_sag()
    write("sipm_bar_sag.csv", rows)
    for r in rows:
        print("  ", r)
    print(f"  bar bending stress, flat, simply supported: {sigma:.2f} MPa")
    rows, big = masses()
    write("arm_masses.csv", rows)
    tot = sum(r["kg"] for r in rows if r["kg"] == r["kg"])
    for r in rows:
        print("  ", r)
    print(f"  known per arm: {tot:.1f} kg; one 75 x 75 x 5 cm big plastic: {big:.1f} kg")
    env = envelope()
    write("envelope.csv", [env])
    print("  ", env)
