"""The NPI Řež TR-24 cartoon for the ⁹Be(p,n) slide note (top view, not to scale).  Solid: what exists;
dashed green: what the X17 set-up would add (a port through the vault wall, collimator, flight tube, dump)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'survey' / 'soft_sim'))
import deck_common as C  # noqa: E402
from deck_common import sd  # noqa: E402

PROP = sd.GREEN


def beamline(w=1664, h=500, n_cell='4.8×10⁹/s'):
    o = []
    y = 270
    # TR-24 vault
    o.append(f'<rect x="0" y="40" width="860" height="440" rx="14" fill="#f4f1ea" stroke="{sd.INK}" stroke-width="2.5"'
             f'{sd.tipattr("TR-24 vault (built 2012-14, MCNPX-designed shielding); size: ask")}/>')
    o.append(sd.T(18, 72, 'TR-24 vault (size: ask)', 22, sd.INK, 'start', 600))
    o.append(f'<circle cx="150" cy="{y}" r="105" fill="#e7eef7" stroke="{sd.BLUE}" stroke-width="2.5"'
             f'{sd.tipattr("ACSI TR-24: H⁻ cyclotron, 18-24 MeV (stripping-foil radius), 300 µA, two simultaneous beams; commissioned Oct 2015")}/>')
    o.append(sd.T(150, y - 6, 'TR-24', 26, sd.BLUE, 'middle', 600))
    o.append(sd.T(150, y + 24, '18–24 MeV, 0.3 mA', 19, sd.BLUE))
    o.append(sd.arrow(255, y, 330, y, sd.RED, 5, 12))
    o.append(C.box(330, y - 34, 70, 68, 'B', '#efe3d2', sd.ORANGE, 24,
                   tip='output 2: beamline with focusing and a switching magnet to three target positions'))
    o.append(sd.arrow(400, y, 560, y, sd.RED, 6, 16))
    o.append(sd.T(480, y - 16, 'p, 18 MeV', 21, sd.RED))
    # Be converter
    o.append(f'<rect x="560" y="{y - 70}" width="90" height="140" rx="10" fill="#c9c3b8" stroke="{sd.MUT}" stroke-width="2"'
             f'{sd.tipattr("target chamber + local shielding; submerged-jet water cooling (7.2 kW)")}/>')
    o.append(f'<rect x="600" y="{y - 26}" width="12" height="52" fill="{sd.RED}"'
             f'{sd.tipattr("static Be disk, 4 mm × Ø40 mm, open in the forward direction: 2.3×10¹³ n/s at 18 MeV, 0.3 mA")}/>')
    o.append(sd.T(605, y + 100, 'Be converter', 21, sd.INK, 'middle', 600))
    o.append(sd.T(605, y - 86, 'samples sit here (20 mm)', 19, sd.MUT))
    for r in (80, 140, 200):
        o.append(f'<path d="M {606 + r * 0.6:.0f} {y - r * 0.8:.0f} A {r} {r} 0 0 1 {606 + r * 0.6:.0f} {y + r * 0.8:.0f}" '
                 f'fill="none" stroke="{sd.BLUE}" stroke-width="2" stroke-dasharray="4 6" opacity="0.6"/>')
    o.append(sd.T(760, 448, '4π field, mean 4.9 MeV', 19, sd.BLUE))
    # the vault wall with a proposed port
    o.append(f'<rect x="860" y="40" width="130" height="440" fill="#d9d4ca" stroke="{sd.INK}" stroke-width="2.5"'
             f'{sd.tipattr("vault wall: the fast field needs ~1-2 m concrete-equivalent between the Be and the arms (estimate)")}/>')
    o.append(f'<rect x="860" y="{y - 20}" width="130" height="40" fill="#fbf9f4" stroke="{PROP}" stroke-width="2.5" stroke-dasharray="8 5"'
             f'{sd.tipattr("proposed collimated port, Ø8 cm (U-120M has one: movable shielding doors, Ø3-25 cm)")}/>')
    o.append(sd.T(925, 30, 'wall + port (ask)', 20, PROP, 'middle', 600))
    # experimental area
    o.append(f'<rect x="990" y="40" width="674" height="440" rx="14" fill="#fbf9f4" stroke="{sd.INK}" stroke-width="2.5"'
             f'{sd.tipattr("an area beyond the wall: exists at U-120M (adjacent hall, 15 m flight path); at TR-24: ask")}/>')
    o.append(sd.T(1010, 72, 'experimental area (ask)', 22, sd.INK, 'start', 600))
    o.append(f'<rect x="990" y="{y - 14}" width="200" height="28" fill="none" stroke="{PROP}" stroke-width="2.5" stroke-dasharray="8 6"'
             f'{sd.tipattr("evacuated flight tube to the cell window")}/>')
    o.append(C.arms(1290, y, 1.15))
    o.append(sd.T(1290, y + 150, 'MX17, cell 2 m from the Be', 22, sd.PURPLE, 'middle', 600))
    o.append(f'<rect x="1370" y="{y - 14}" width="140" height="28" fill="none" stroke="{PROP}" stroke-width="2.5" stroke-dasharray="8 6"/>')
    o.append(C.box(1530, y - 70, 70, 140, '', '#e3efe6', PROP, tip='proposed beam dump'))
    o.append(sd.T(1565, y + 100, 'dump', 20, PROP))
    o.append(C.beam_arrow(620, 1525, y, sd.BLUE, 5))
    o.append(sd.T(1090, y + 44, f'n, {n_cell}', 20, sd.BLUE))
    return sd.svg(w, h, ''.join(o), 'NPI Řež TR-24: cyclotron, Be converter and the proposed X17 station beyond the wall')
