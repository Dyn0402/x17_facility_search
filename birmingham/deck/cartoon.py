"""The HF-ADNeF cartoon for the Birmingham slide note (top view, not to scale).  Solid: what exists;
dashed green: what the X17 set-up would add (shield wall + collimator + γ filter, flight tube, dump)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'survey' / 'soft_sim'))
import deck_common as C  # noqa: E402
from deck_common import sd  # noqa: E402

PROP = sd.GREEN


def beamline(w=1664, h=560):
    o = []
    y = 300
    # accelerator bunker
    o.append(f'<rect x="0" y="150" width="560" height="300" rx="14" fill="#f4f1ea" stroke="{sd.INK}" stroke-width="2.5"'
             f'{sd.tipattr("accelerator bunker extension (underground)")}/>')
    o.append(sd.T(18, 180, 'accelerator bunker', 22, sd.INK, 'start', 600))
    o.append(C.box(24, y - 40, 90, 80, 'ECR', '#fff', sd.INK, 21, tip='ECR ion source (protons; deuterons planned)'))
    o.append(f'<rect x="130" y="{y - 60}" width="300" height="120" rx="60" fill="#e7eef7" stroke="{sd.BLUE}" stroke-width="2.5"'
             f'{sd.tipattr("Neutron Therapeutics hyperion-type electrostatic accelerator: 14 HV stages, 0.4-2.6 MeV (2.8 max), < 50 mA DC")}/>')
    for i in range(14):
        o.append(sd.line(160 + 17 * i, y - 48, 160 + 17 * i, y + 48, sd.BLUE, 1.2))
    o.append(sd.T(280, y + 90, '2.6-2.8 MeV, 30 mA DC', 22, sd.BLUE))
    o.append(C.box(450, y - 36, 70, 72, 'B', '#efe3d2', sd.ORANGE, 24,
                   tip='dipole switching magnet (beam switching area lined with borated PE)'))
    o.append(sd.arrow(114, y, 130, y, sd.RED, 5, 12))
    o.append(sd.arrow(430, y, 450, y, sd.RED, 5, 12))
    o.append(sd.arrow(520, y, 640, y, sd.RED, 6, 16))
    o.append(sd.T(580, y - 16, 'p', 22, sd.RED))
    # target room
    o.append(f'<rect x="580" y="30" width="1084" height="460" rx="14" fill="#fbf9f4" stroke="{sd.INK}" stroke-width="3"'
             f'{sd.tipattr("neutron target room, walls lined with borated PE; dimensions (ask)")}/>')
    o.append(sd.T(600, 62, 'target room (size: ask)', 22, sd.INK, 'start', 600))
    # Ti vessel with the Li wheel (seen edge-on), Pb around
    o.append(f'<rect x="630" y="{y - 150}" width="120" height="300" rx="10" fill="#c9c3b8" stroke="{sd.MUT}" stroke-width="2"'
             f'{sd.tipattr("lead shielding around the target (⁷Be: up to 6 TBq per target)")}/>')
    o.append(f'<rect x="660" y="{y - 130}" width="60" height="260" rx="8" fill="#e6e8ec" stroke="{sd.INK}" stroke-width="2.5"'
             f'{sd.tipattr("titanium vacuum vessel (4-6 mm Ti exit wall)")}/>')
    o.append(f'<rect x="684" y="{y - 120}" width="12" height="240" fill="{sd.RED}"'
             f'{sd.tipattr("rotating Li wheel, 1 m, 16 Cu petals with ~0.3 mm Li, 600 rpm, ~100 kW; >3×10¹³ n/s at 30 mA")}/>')
    o.append(sd.T(690, y + 180, 'Li wheel + Ti vessel + Pb', 20, sd.INK))
    o.append(sd.T(690, y - 162, 'users mount rigs here', 20, sd.MUT))
    # 4π field
    for r in (90, 150, 210):
        o.append(f'<path d="M {690 + r * 0.6:.0f} {y - r * 0.8:.0f} A {r} {r} 0 0 1 {690 + r * 0.6:.0f} {y + r * 0.8:.0f}" '
                 f'fill="none" stroke="{sd.BLUE}" stroke-width="2" stroke-dasharray="4 6" opacity="0.6"/>')
    # proposed shield wall + collimator + filter
    o.append(f'<rect x="900" y="80" width="150" height="400" fill="#e3efe6" stroke="{PROP}" stroke-width="2.5" stroke-dasharray="9 6"'
             f'{sd.tipattr("proposed shield wall: borated PE + Pb, ~0.5-1 m, with a Ø8 cm collimator on the 0° axis")}/>')
    o.append(f'<rect x="900" y="{y - 20}" width="150" height="40" fill="#fbf9f4" stroke="{PROP}" stroke-width="2"/>')
    o.append(f'<rect x="960" y="{y - 20}" width="40" height="40" fill="#8f8a80"'
             f'{sd.tipattr("Pb γ filter in the collimator (5 cm: 478 keV γ ×1.5×10⁻⁴, 15-18 MeV γ ×0.06, neutrons ×0.37 uncollided)")}/>')
    o.append(sd.T(975, 108, 'shield + collimator', 20, PROP, 'middle', 600))
    o.append(sd.T(975, y + 52, 'Pb filter', 19, sd.INK))
    o.append(f'<rect x="1050" y="{y - 14}" width="220" height="28" fill="none" stroke="{PROP}" stroke-width="2.5" stroke-dasharray="8 6"/>')
    o.append(C.arms(1350, y, 1.15))
    o.append(sd.T(1350, y + 150, 'MX17, cell 2 m from the Li', 22, sd.PURPLE, 'middle', 600))
    o.append(f'<rect x="1430" y="{y - 14}" width="120" height="28" fill="none" stroke="{PROP}" stroke-width="2.5" stroke-dasharray="8 6"/>')
    o.append(C.box(1560, y - 70, 60, 140, '', '#e3efe6', PROP, tip='proposed beam dump (borated PE)'))
    o.append(sd.T(1590, y + 100, 'dump', 20, PROP))
    o.append(C.beam_arrow(700, 1555, y, sd.BLUE, 5))
    o.append(sd.T(1160, y + 44, 'n ≤ 1.1 MeV, 7×10⁹/s', 20, sd.BLUE))
    return sd.svg(w, h, ''.join(o), 'HF-ADNeF: accelerator, Li target, and the proposed shielded X17 station')
