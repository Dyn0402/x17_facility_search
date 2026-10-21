"""The WNR cartoons for the LANSCE slide note: Target 4 with its six flight paths and the proposed X17 station
on 4FP90L (top view, not to scale), and the beam's time structure (macropulses, micropulses, the window).
Solid: what exists; dashed green: what the X17 set-up would add."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'survey' / 'soft_sim'))
import deck_common as C  # noqa: E402
from deck_common import sd  # noqa: E402

PROP = sd.GREEN

PATHS = [  # name, angle (deg, + = left of the proton beam), length label, what, tip
    ('15L', 15, '22 / 90 m', 'Chi-Nu, CoGNAC', '4FP15L: 22 m and 90 m stations, 2 m pit; Chi-Nu, detector development'),
    ('15R', -15, '', 'LENZ', '4FP15R: the hardest spectrum, up to 800 MeV; LENZ charged-particle reactions'),
    ('30L', 30, '~20 m', 'ICE House', '4FP30L ICE House: electronics testing, 1.5×10⁶ n/cm²/s > 1.5 MeV, Ø2.5-8 cm'),
    ('30R', -30, '~10 m', 'ICE-II', '4FP30R ICE-II: 4.7×10⁶ n/cm²/s > 1.5 MeV, Ø2.5-6.4 cm'),
    ('60R', -60, '', 'radiography', '4FP60R: neutron radiography and CT, field 30 × 20 cm to Ø2.5 cm'),
    ('90L', 90, '7-15 m', 'fission', '4FP90L: the softest spectrum, 7-15 m; fission chambers and the NIFFTE TPC'),
]


def beamline(w=1664, h=560, L=10.0):
    """protons go up the page; flight paths fan out from the target; 4FP90L runs left, horizontally."""
    c = 0.299792458

    def tof(e):
        g = 1 + e / 939.565
        return L / (c * math.sqrt(1 - 1 / g ** 2))
    o = []
    tx, ty = 1000, 420
    o.append(sd.arrow(tx, h, tx, ty + 70, sd.RED, 6, 16))
    o.append(sd.T(tx + 14, h - 12, '800 MeV p from the LANSCE linac, ~1.5 µA', 21, sd.RED, 'start',
                  tip='40 macropulses/s of 625 µs; micropulses every 1.8 µs, 7×10⁸ p each'))
    o.append(f'<circle cx="{tx}" cy="{ty}" r="70" fill="#d7d2c8" stroke="{sd.MUT}" stroke-width="2"'
             f'{sd.tipattr("Target 4 shielding; each flight path leaves through its own collimator")}/>')
    o.append(f'<rect x="{tx - 8}" y="{ty - 20}" width="16" height="40" rx="3" fill="{sd.INK}"'
             f'{sd.tipattr("bare W target: 7.5 cm long, Ø3 cm, 4 mm water jacket; no moderator")}/>')
    o.append(sd.T(tx + 84, ty + 52, 'Target 4 (bare W)', 21, sd.INK, 'start', 600))
    for name, ang, ln, what, tip in PATHS:
        if name == '90L':
            continue
        a = math.radians(abs(ang))
        sx = -1 if ang > 0 else 1
        dx, dy = sx * math.sin(a), -math.cos(a)
        r1 = {15: 340, 30: 280}.get(abs(ang), 250)
        o.append(f'<line x1="{tx + 70 * dx:.0f}" y1="{ty + 70 * dy:.0f}" x2="{tx + r1 * dx:.0f}" y2="{ty + r1 * dy:.0f}" '
                 f'stroke="{sd.GREY}" stroke-width="5" stroke-linecap="round"{sd.tipattr(tip)}/>')
        lab = f'{name} · {what}' + (f' ({ln})' if ln else '')
        o.append(sd.T(tx + (r1 + 12) * dx, ty + (r1 + 12) * dy - 6, lab, 19, sd.MUT, 'end' if dx < 0 else 'start', tip=tip))
    # 4FP90L to the left, with the X17 station
    y = ty
    o.append(f'<line x1="{tx - 70}" y1="{y}" x2="130" y2="{y}" stroke="{sd.PURPLE}" stroke-width="8" stroke-linecap="round"'
             f'{sd.tipattr(PATHS[-1][4])}/>')
    o.append(sd.T(690, y - 50, '4FP90L: softest, 7-15 m', 22, sd.PURPLE, 'middle', 600))
    o.append(f'<rect x="780" y="{y - 26}" width="60" height="52" fill="#e3efe6" stroke="{PROP}" stroke-width="2.5" '
             f'stroke-dasharray="8 6"{sd.tipattr("collimator to a Ø8 cm spot at the cell (the fission TPC has one: size ask)")}/>')
    o.append(sd.T(810, y + 54, 'collimator → Ø8 cm', 19, PROP))
    ax = 500
    o.append(f'<g transform="rotate(180 {ax} {y})">{C.arms(ax, y, 1.1)}</g>')
    o.append(sd.T(ax, y - 112, f'MX17, cell {L:g} m from the W', 22, sd.PURPLE, 'middle', 600))
    o.append(C.box(150, y - 60, 50, 120, '', '#e3efe6', PROP, tip='beam dump behind the station (what 90L has: ask)'))
    o.append(sd.T(175, y + 90, 'dump', 19, PROP))
    o.append(sd.T(500, y + 135, 'n: 0.1-230 MeV, 3.7×10⁸/s through Ø8 cm', 20, sd.BLUE))
    # trigger gate + proposal boxes
    o.append(C.box(40, 20, 560, 120, 'ToF trigger gate', '#f3eefa', sd.PURPLE, 24,
                   sub=f'two-arm triggers only {tof(2.75) / 1e3:.2f}-{tof(0.2) / 1e3:.2f} µs after each micropulse',
                   tip='LANSCE distributes the micropulse timing: accept triggers only for 0.2-2.75 MeV arrivals'))
    o.append(sd.line(320, 140, ax - 40, y - 130, sd.PURPLE, 2, '6 6'))
    o.append(C.box(1320, 400, 330, 120, 'LANSCE user call', '#eef5ef', PROP, 22, sub='nuclear science, Feb deadline',
                   tip='90L has very limited beam time (2026 call): talk to the instrument scientist first'))
    return sd.svg(w, h, ''.join(o), 'WNR Target 4 with its six flight paths and the proposed X17 station on 4FP90L')


def timing(w=1600, h=330, L=8.0, T_us=1.8):
    """three micropulse periods: the γ flash, the fast neutrons, the 0.2-2.75 MeV window at L metres."""
    import numpy as np
    c = 0.299792458

    def tof(e):
        g = 1 + e / 939.565
        return L / (c * math.sqrt(1 - 1 / g ** 2))           # ns
    x0, x1 = 60, w - 40
    span = 3 * T_us * 1e3 + 300
    X = lambda t: x0 + (x1 - x0) * t / span                  # noqa: E731
    o = [sd.line(x0, 230, x1, 230, sd.INK, 2)]
    for k in range(3):
        t0 = k * T_us * 1e3
        tg = t0 + L / c
        o.append(sd.line(X(t0), 120, X(t0), 230, sd.RED, 4))
        o.append(sd.T(X(t0), 112, 'p' if k else 'micropulse', 19, sd.RED))
        o.append(f'<rect x="{X(tg) - 2:.1f}" y="140" width="5" height="90" fill="{sd.ORANGE}"'
                 f'{sd.tipattr(f"γ flash at {L / c:.0f} ns: gated off")}/>')
        a, b = tof(25.0) + t0, tof(2.75) + t0
        o.append(f'<rect x="{X(a):.1f}" y="170" width="{X(b) - X(a):.1f}" height="60" fill="{sd.GREY}" opacity="0.35"'
                 f'{sd.tipattr("2.75-25 MeV neutrons: fast, outside the gate")}/>')
        a, b = tof(2.75) + t0, tof(0.2) + t0
        o.append(f'<rect x="{X(a):.1f}" y="150" width="{X(b) - X(a):.1f}" height="80" fill="{sd.PURPLE}" opacity="0.35"'
                 f'{sd.tipattr(f"0.2-2.75 MeV neutrons arrive {tof(2.75):.0f}-{tof(0.2):.0f} ns: the gate")}/>')
        if k == 0:
            o.append(sd.T((X(a) + X(b)) / 2, 142, 'gate: 0.2-2.75 MeV', 20, sd.PURPLE, 'middle', 600))
    for t in range(0, int(span) + 1, 500):
        o.append(sd.line(X(t), 230, X(t), 238, sd.INK, 1.5))
        o.append(sd.T(X(t), 262, f'{t / 1e3:g}', 18, sd.MUT))
    o.append(sd.T((x0 + x1) / 2, 300, f'µs after a micropulse (cell at {L:g} m; micropulses every {T_us:g} µs, '
                  f'348 per 625 µs macropulse, 40 macropulses/s)', 20, sd.MUT))
    o.append(sd.T(x0, 40, f'0.2 MeV neutrons arrive at {tof(0.2) / 1e3:.2f} µs, before the next γ flash at '
                  f'{(T_us * 1e3 + L / c) / 1e3:.2f} µs: no frame overlap in the window', 22, sd.INK, 'start', 600))
    return sd.svg(w, h, ''.join(o), 'WNR micropulse timing at the cell')
