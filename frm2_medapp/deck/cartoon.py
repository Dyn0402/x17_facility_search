"""The SR10 beamline cartoon for the MEDAPP slide note (side view, not to scale except where labelled)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'survey' / 'soft_sim'))
import deck_common as C  # noqa: E402
from deck_common import sd  # noqa: E402


def beamline(w=1664, h=560):
    o = []
    y = 250                                   # beam axis
    # reactor pool + D2O tank + core
    o.append(f'<rect x="0" y="20" width="430" height="470" rx="18" fill="#dcebf7" stroke="{sd.BLUE}" stroke-width="2"'
             f'{sd.tipattr("reactor pool (light water)")}/>')
    o.append(sd.T(18, 52, 'reactor pool (H₂O)', 21, sd.BLUE, 'start'))
    o.append(f'<circle cx="170" cy="{y}" r="150" fill="#bcd7ef" stroke="{sd.BLUE}" stroke-width="2"'
             f'{sd.tipattr("D₂O moderator tank, 2.5 m diameter")}/>')
    o.append(sd.T(170, y + 125, 'D₂O tank', 21, sd.BLUE))
    o.append(f'<rect x="140" y="{y - 40}" width="60" height="80" rx="6" fill="#f2b56b" stroke="{sd.ORANGE}" stroke-width="2.5"'
             f'{sd.tipattr("compact HEU core: 8.1 kg ²³⁵U, 20 MW, 8×10¹⁴ n/cm²/s thermal")}/>')
    o.append(sd.T(170, y + 7, 'core', 20, sd.INK))
    # converter plates at the tank edge, ~1 m from the core
    for dx in (0, 14):
        o.append(f'<rect x="{292 + dx}" y="{y - 46}" width="8" height="92" fill="{sd.RED}"'
                 f'{sd.tipattr("converter: 2 U₃Si₂-Al plates, 540 g of 93 % ²³⁵U, 80 kW of fission; lowered into the D₂O tank next to the SR10 nose")}/>')
    o.append(sd.T(300, y - 64, 'U converter', 21, sd.RED))
    o.append(sd.T(232, y + 72, '~1 m', 19, sd.MUT))
    o.append(sd.line(200, y + 54, 292, y + 54, sd.MUT, 1.5))
    # beam tube with shutters through the pool wall
    o.append(f'<rect x="318" y="{y - 30}" width="300" height="60" fill="#f4f1ea" stroke="{sd.INK}" stroke-width="2"'
             f'{sd.tipattr("beam tube SR10, 4 shutter drums (redundant: therapy requirement)")}/>')
    for i in range(4):
        o.append(f'<circle cx="{450 + 40 * i}" cy="{y}" r="22" fill="#d8d3c8" stroke="{sd.MUT}" stroke-width="2"/>')
    o.append(f'<rect x="430" y="20" width="30" height="470" fill="#bbb4a6"{sd.tipattr("pool wall / biological shield")}/>')
    o.append(sd.T(540, y - 44, 'SR10 + 4 shutters', 21, sd.INK))
    # filters + MLC
    o.append(C.box(628, y - 60, 46, 120, '', '#e9e4f5', sd.PURPLE,
                   tip='standard filters: 1 cm B4C-epoxy (thermal) + 3.5 cm Pb (γ); pneumatic, others possible'))
    o.append(sd.T(651, y - 74, 'filters', 21, sd.PURPLE))
    o.append(C.box(684, y - 80, 60, 160, '', '#d8d3c8', sd.INK,
                   tip='multi-leaf collimator: leaves 1.5 cm wide, 60 cm deep (Fe/PE/Pb), field up to 27 × 19 cm'))
    o.append(sd.T(714, y + 110, 'MLC', 21, sd.INK))
    # MEDAPP room
    o.append(f'<rect x="760" y="40" width="520" height="430" rx="10" fill="#fbf9f4" stroke="{sd.INK}" stroke-width="3"'
             f'{sd.tipattr("MEDAPP irradiation room (therapy, short experiments); sample space 40 × 30 cm in the field")}/>')
    o.append(sd.T(780, 72, 'MEDAPP room', 24, sd.INK, 'start', 600))
    # proposed: vacuum tube + MX17 + dump tube
    o.append(f'<rect x="760" y="{y - 14}" width="250" height="28" fill="none" stroke="{sd.GREEN}" stroke-width="2.5" stroke-dasharray="8 6"'
             f'{sd.tipattr("proposed: evacuated flight tube MLC → cell window (in air ~1 %/m of the beam scatters)")}/>')
    o.append(C.arms(1150, y, 1.15))
    o.append(sd.T(1150, y + 150, 'MX17 (proposed)', 22, sd.PURPLE, 'middle', 600))
    o.append(f'<rect x="1190" y="{y - 14}" width="90" height="28" fill="none" stroke="{sd.GREEN}" stroke-width="2.5" stroke-dasharray="8 6"/>')
    o.append(sd.T(1150, 112, 'SSD 5.9 m from the source', 20, sd.MUT))
    # NECTAR room + beam stop
    o.append(f'<rect x="1300" y="40" width="364" height="430" rx="10" fill="#fbf9f4" stroke="{sd.INK}" stroke-width="3"'
             f'{sd.tipattr("NECTAR: radiography/tomography, permanent set-ups up to 80 × 80 × 80 cm, 500 kg; 0.9-47 ×10⁶ n/cm²/s")}/>')
    o.append(sd.T(1320, 72, 'NECTAR room', 24, sd.INK, 'start', 600))
    o.append(C.box(1580, y - 70, 50, 140, '', '#bbb4a6', sd.INK, tip='beam stop'))
    o.append(sd.T(1605, y + 100, 'beam stop', 20, sd.INK))
    o.append(C.beam_arrow(305, 1570, y, sd.BLUE, 5))
    o.append(sd.T(1010, y + 40, 'fission n 3.2×10⁸ /cm²/s, γ ≈ n', 20, sd.BLUE, 'end'))
    return sd.svg(w, h, ''.join(o), 'SR10 fission beam: converter, tube, filters, MLC, MEDAPP and NECTAR rooms')
