"""The FRANZ cartoon for the slide note (top view, not to scale).  Solid: what exists or is being
commissioned; dashed green: what the X17 set-up would add (thin-Li target chamber shield, flight tube,
dump)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'survey' / 'soft_sim'))
import deck_common as C  # noqa: E402
from deck_common import sd  # noqa: E402

PROP = sd.GREEN


def beamline(w=1664, h=500):
    o = []
    y = 270
    o.append(f'<rect x="0" y="40" width="{w}" height="440" rx="14" fill="#fbf9f4" stroke="{sd.INK}" stroke-width="3"'
             f'{sd.tipattr("FRANZ experimental hall, physics building, Riedberg campus; layout and size (ask)")}/>')
    o.append(sd.T(20, 72, 'FRANZ hall, Goethe University (layout: ask)', 22, sd.INK, 'start', 600))
    o.append(C.box(30, y - 50, 120, 100, 'CHORDIS', '#fff', sd.INK, 20, sub='35+25 kV',
                   tip='CHORDIS volume ion source (from GSI) + electrostatic post-accelerator to 60 keV; 0.5-1 ms at 10 Hz today'))
    o.append(sd.arrow(150, y, 180, y, sd.RED, 5, 12))
    o.append(f'<rect x="180" y="{y - 30}" width="200" height="60" rx="30" fill="#eef1f4" stroke="{sd.MUT}" stroke-width="2"'
             f'{sd.tipattr("LEBT: solenoids, diagnostics, H₂⁺/H₃⁺ removal")}/>')
    o.append(sd.T(280, y + 8, 'LEBT', 22, sd.MUT))
    o.append(sd.arrow(380, y, 410, y, sd.RED, 5, 12))
    o.append(f'<rect x="410" y="{y - 55}" width="250" height="110" rx="20" fill="#e7eef7" stroke="{sd.BLUE}" stroke-width="2.5"'
             f'{sd.tipattr("175 MHz 4-rod RFQ to 700 keV: commissioned end 2023 with up to 11 mA (7.1 mA matched, 92.7 %)")}/>')
    o.append(sd.T(535, y + 8, 'RFQ 0.7 MeV', 22, sd.BLUE, 'middle', 600))
    o.append(f'<rect x="660" y="{y - 55}" width="150" height="110" rx="20" fill="#e7eef7" stroke="{sd.BLUE}" stroke-width="2.5" '
             f'stroke-dasharray="7 5"{sd.tipattr("1.3 MV IH-DTL coupled to the RFQ: conditioned standalone to 10 kW CW; coupled 2 MeV beam planned end of 2025 (not confirmed)")}/>')
    o.append(sd.T(735, y + 8, 'IH → 2 MeV', 22, sd.BLUE, 'middle', 600))
    o.append(sd.T(610, y + 90, 'coupled RFQ-IH-DTL, one 250 kW amplifier', 19, sd.MUT))
    o.append(sd.arrow(810, y, 900, y, sd.RED, 6, 16))
    o.append(sd.T(855, y - 16, 'p', 22, sd.RED))
    # target + proposed shield
    o.append(f'<rect x="900" y="{y - 140}" width="190" height="280" rx="10" fill="#e3efe6" stroke="{PROP}" stroke-width="2.5" '
             f'stroke-dasharray="9 6"{sd.tipattr("proposed: ~20-30 cm borated PE (+ Pb) around the target chamber, Ø8 cm hole on the 0° axis")}/>')
    o.append(sd.T(995, y - 152, 'BPE shield (proposed)', 20, PROP, 'middle', 600))
    o.append(f'<rect x="960" y="{y - 50}" width="40" height="100" rx="6" fill="#e6e8ec" stroke="{sd.INK}" stroke-width="2.5"'
             f'{sd.tipattr("target chamber")}/>')
    o.append(f'<rect x="992" y="{y - 40}" width="8" height="80" fill="{sd.RED}"'
             f'{sd.tipattr("thin Li (~10 µm) on Cu: protons leave the Li at the (p,n) threshold and never reach the ⁸Be resonances")}/>')
    o.append(sd.T(980, y + 80, 'thin Li', 20, sd.INK))
    o.append(f'<rect x="1000" y="{y - 14}" width="90" height="28" fill="#fbf9f4" stroke="{PROP}" stroke-width="2"/>')
    # forward cone
    o.append(f'<path d="M 1000 {y} L 1420 {y - 200} M 1000 {y} L 1420 {y + 200}" stroke="{sd.BLUE}" stroke-width="2" '
             f'stroke-dasharray="4 6" opacity="0.7"{sd.tipattr("kinematic collimation: at 1.912 MeV every neutron is within 64°; at 2.0 MeV 0° gets ×3.6 the 4π average")}/>')
    o.append(f'<rect x="1090" y="{y - 14}" width="70" height="28" fill="none" stroke="{PROP}" stroke-width="2.5" stroke-dasharray="8 6"/>')
    o.append(C.arms(1270, y, 1.0))
    o.append(sd.T(1270, y + 135, 'MX17, cell 0.5 m from the Li', 22, sd.PURPLE, 'middle', 600))
    o.append(f'<rect x="1340" y="{y - 14}" width="150" height="28" fill="none" stroke="{PROP}" stroke-width="2.5" stroke-dasharray="8 6"/>')
    o.append(C.box(1500, y - 70, 60, 140, '', '#e3efe6', PROP, tip='proposed beam dump (borated PE)'))
    o.append(sd.T(1530, y + 100, 'dump', 20, PROP))
    o.append(C.beam_arrow(1000, 1495, y, sd.BLUE, 5))
    o.append(sd.T(1145, y + 40, 'n ≤ 0.23 MeV', 18, sd.BLUE))
    return sd.svg(w, h, ''.join(o), 'FRANZ: ion source, RFQ-IH-DTL, thin Li target, and the proposed X17 station')
