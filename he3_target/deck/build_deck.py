"""Build the ³He target engineering slide note (he3_target/FEASIBILITY_PLAN.md).

    ~/PycharmProjects/nTof_x17/.venv/bin/python he3_target/deck/build_deck.py
    python3 ~/PycharmProjects/dylan-cern-site/scripts/add-note.py he3_target/out/he3-target-engineering.html \\
        --slug he3-target-engineering --force --deploy

Reads he3_target/out/designs.csv and calibration.csv (he3_target.py).
"""
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.expanduser(os.environ.get('SLIDEDOC_DIR', '~/PycharmProjects/dylan-cern-site/scripts')))
import slidedoc as sd  # noqa: E402
from slidedoc import T, line, sci  # noqa: E402

HERE = Path(__file__).resolve().parent
H = HERE.parent
O = H / 'out'
t = pd.read_csv(O / 'designs.csv').set_index('key')
cal = pd.read_csv(O / 'calibration.csv').iloc[0]

FAM = {'anchor': sd.BLUE, 'balloon': sd.GREY, 'copv': sd.GREEN, 'mono-Be': sd.GOLD, 'mono-Al': sd.ORANGE}
FAMN = {'anchor': 'Geant4 target (as simulated)', 'balloon': '1 bar balloon (Geant4)', 'copv': 'Al-lined CFRP, code-sized',
        'mono-Be': 'monolithic Be tube', 'mono-Al': 'monolithic Al tube'}
SHORT = {'cap500': 'n_TOF capsule', 'c30': 'build C (30 bar)', 'c10': '10 bar cell', 'bal5': 'balloon R 5',
         'bal10': 'balloon R 10', 'c30-copv': 'build C, code-sized', 'c30m-copv': 'baseline: 30 bar R 4',
         'c30-be': '30 bar Be tube', 'c30-al': '30 bar Al tube', 'c10m-copv': 'fallback: 10 bar R 4',
         'c60m-copv': '60 bar R 4', 'c100m-copv': '100 bar R 4', 't200-r2': '200 bar R 2', 't500-r1': '500 bar R 1 × 40'}
BASE, FALL, ALT = t.loc['c30m-copv'], t.loc['c10m-copv'], t.loc['t200-r2']
K, SV, KK = cal.K_anchor, cal.sigma_v_deg, cal.k


def tipd(k):
    r = t.loc[k]
    return (f'{r.design}\n{r.p_bar:g} bar, gas R {r.R_cm:g} cm × {r.L_cm:g} cm, beam R {r.beam_r_cm:g} cm\n'
            f'walls {r.walls} mm → {r.total_x_over_X0_pct:.2f} % X₀, σ68 {r.sigma68_deg:.1f}°\n'
            f'³He {r.he3_L_STP:.0f} L STP ({r.he3_L_in_beam:.0f} in the beam), {r.he3_keur:.0f} k€\n'
            f'{r.days_ATOMKI:.1f} d to ATOMKI ({r.days_source})\nPS·V {r.PSV_barL:.0f} bar·L → {r.ped}')


def fd(x):
    return f'{x:.1f} d' if x < 10 else f'{x:.0f} d'


D = sd.Deck('The ³He target: build it, fill it, get it approved, empty it',
            'Engineering feasibility of the ³He target for MX17 at a fast-neutron beam (Birmingham HF-ADNeF): code-sized '
            'vessels, the legal class, a closed gas fill/recovery loop, ³He supply, tritium, what to simulate. 29 Oct 2026.')

# ------------------------------------------------------------------ cover
D.slide('cover', sd.kicker('MX17 at Birmingham · the ³He target as an engineering project · 29 Oct 2026')
        + '<h1 style="font-size:58px;font-weight:600;line-height:1.1;letter-spacing:-1.2px">'
          'The ³He target is not a physics blocker. It is a year of procurement and engineering with known technology: '
          'buy litres inside the beam, put them in a code-sized 30 bar cell, run a closed gas loop.</h1>'
        + sd.row(
            sd.bignum(f'{BASE.he3_L_STP:.0f} L', '³He for the baseline cell', sd.DGREEN,
                      f'30 bar, R 4 cm × 40 cm, Al-lined CFRP; {BASE.he3_keur:.0f} k€ at 2.5 k€/L',
                      tip=tipd('c30m-copv')),
            sd.bignum(f'~{BASE.days_ATOMKI:.0f} d', 'of beam to the ATOMKI strength', sd.DBLUE,
                      'estimate from the Geant4 rows; build C as drawn: 6.7 d', tip='days ≈ K·σ68/L_beam, K fitted on the 30 bar cell'),
            sd.bignum('≲ 0.2 %', '³He lost per campaign', sd.DGREY, 'cryopump fill and recovery, dump tank on the relief',
                      tip='residual after recovery < 0.01 L, leaks 0.005 L, regeneration < 0.1 L (FEASIBILITY_PLAN §4.2)'),
            gap=40),
        dark=True, short='cover')

# ------------------------------------------------------------------ setup schematic
def setup_svg():
    W, Hh = 1664, 600
    cy = 270
    o = []
    # shield wall
    for x0, w_, c, lab in ((40, 60, '#cfe3c9', 'BPE'), (100, 160, '#d9d4c9', 'concrete'), (260, 20, '#9aa1ad', 'Pb')):
        o.append(f'<rect x="{x0}" y="40" width="{w_}" height="460" fill="{c}" stroke="{sd.RULE}"/>')
        o.append(T(x0 + w_ / 2, 525, lab, 18))
    o.append(f'<rect x="40" y="{cy - 40}" width="240" height="80" fill="#fff" stroke="{sd.MUT}" stroke-dasharray="4 4"/>')
    o.append(T(160, 25, 'shield wall + Ø8 cm bore', 20, sd.INK))
    o.append(T(20, cy + 8, 'Li', 22, sd.RED, weight=600, tip='the ⁷Li(p,n) source, 2.8 MeV × 30 mA, 3.7×10¹³ n/s, 2 m upstream of the cell centre'))
    # beam band
    o.append(f'<rect x="280" y="{cy - 40}" width="1210" height="80" fill="{sd.ORANGE}" fill-opacity="0.13"'
             f'{sd.tipattr("the Ø8 cm collimated beam: 1.4×10⁸ n/cm²/s on axis, E_n ≤ 1.1 MeV")}/>')
    o.append(T(380, cy - 52, 'beam Ø8 cm (n, E ≤ 1.1 MeV)', 20, sd.ORANGE, 'start'))
    # 4He bag
    o.append(f'<rect x="560" y="{cy - 85}" width="520" height="170" rx="60" fill="none" stroke="{sd.PURPLE}" '
             f'stroke-width="2" stroke-dasharray="8 6"{sd.tipattr("⁴He bag at 1.01 bar: catches slow leaks, sniffed for mass 3 by a leak detector")}/>')
    o.append(T(820, cy - 95, '⁴He bag, sniffed for mass 3', 19, sd.PURPLE))
    # cell: 400 mm long → 400 px, R 40 mm, domes
    x0, x1, r = 620, 1020, 40
    o.append(f'<path d="M{x0},{cy - r} L{x1},{cy - r} A{r},{r} 0 0 1 {x1},{cy + r} L{x0},{cy + r} A{r},{r} 0 0 1 {x0},{cy - r} Z" '
             f'fill="#e8f3ee" stroke="{sd.GREEN}" stroke-width="5"{sd.tipattr(tipd("c30m-copv"))}/>')
    o.append(T(820, cy + 8, '³He, 30 bar, R 4 × 40 cm', 22, sd.INK, weight=600))
    o.append(T(820, cy + 120, '0.2 mm Al liner + 0.36 mm wound CFRP, domed ends', 19, sd.GREEN))
    # boss, valve, line
    o.append(f'<rect x="{x1 + r - 4}" y="{cy - 8}" width="22" height="16" fill="{sd.MUT}"/>')
    o.append(line(x1 + r + 18, cy, x1 + r + 70, cy, sd.INK, 3) + line(x1 + r + 70, cy, x1 + r + 70, 560, sd.INK, 3))
    o.append(f'<circle cx="{x1 + r + 70}" cy="{cy + 140}" r="9" fill="{sd.CARD}" stroke="{sd.INK}" stroke-width="3"'
             f'{sd.tipattr("first valve: ≤ 1 cm³ dead volume between it and the cell")}/>')
    o.append(T(x1 + r + 86, cy + 146, 'valve + fill line, outside the acceptance', 18, sd.INK, 'start'))
    o.append(f'<rect x="1150" y="530" width="300" height="56" rx="10" fill="{sd.CARD}" stroke="{sd.INK}" stroke-width="2"/>')
    o.append(T(1300, 566, 'gas panel (next slides)', 20, sd.INK))
    o.append(line(x1 + r + 70, 560, 1150, 560, sd.INK, 3))
    # arms (side view: two of four)
    for y in (cy - 204 - 30, cy + 204):
        o.append(f'<rect x="620" y="{y}" width="400" height="30" fill="#dfe8f4" stroke="{sd.BLUE}" stroke-width="2"'
                 f'{sd.tipattr("Micromegas TPC, 399 × 360 mm active, 30 mm drift, face at ±204 mm")}/>')
    for y in (cy - 204 - 30 - 46, cy + 204 + 30 + 16):
        o.append(f'<rect x="600" y="{y}" width="440" height="30" fill="#efe6d6" stroke="{sd.GOLD}" stroke-width="2"/>')
    o.append(T(1060, cy - 204 - 8, 'Micromegas', 19, sd.BLUE, 'start'))
    o.append(T(1060, cy - 204 - 52, 'SiPM wall + plastics', 19, sd.GOLD, 'start'))
    # acceptance
    o.append(line(620, 40, 620, 500, sd.MUT, 1, '3 5') + line(1020, 40, 1020, 500, sd.MUT, 1, '3 5'))
    # dump
    o.append(f'<rect x="1490" y="{cy - 70}" width="110" height="140" fill="#cfe3c9" stroke="{sd.RULE}"/>')
    o.append(T(1545, cy + 95, 'dump', 19))
    return sd.svg(W, Hh, ''.join(o), 'the cell in the Birmingham beam')


D.slide('setup', sd.title('What has to be built: a pressurised ³He cell in the beam, between the four arms, with a way to fill and empty it',
                          'side view to scale along the beam (1 px = 1 mm near the cell); hover the dotted terms and the parts')
        + setup_svg(),
        notes='The Birmingham Geant4 study (birmingham/TARGET_GEANT.md) chose the target by physics only: the 30 bar Be/CFRP '
              '"build C" cell, R 5 × 40 cm, 87 L of ³He, 6.7 days to the ATOMKI strength. It did not ask whether the cell can be '
              'built to a pressure code, how the gas gets in and out, who supplies the ³He, or what the beam does to the gas. '
              'This note does. The drawing shows the baseline that comes out of it: R 4 cm matched to the Ø8 cm beam, an Al-lined '
              'CFRP vessel with domed ends, the valve and fill line leaving sideways outside the Micromegas acceptance, the cell '
              'inside a ⁴He bag. Hover anything with a dotted underline or the drawn parts for numbers.',
        short='setup')

# ------------------------------------------------------------------ days vs litres
P = sd.Plot(1100, 690, x=(1, 300, 'log'), y=(1, 400, 'log'), xlabel='³He inside the beam [L STP]',
            ylabel='days of beam to the ATOMKI strength (3σ)')
P.xticks([(1, '1'), (3, '3'), (10, '10'), (30, '30'), (100, '100'), (300, '300')])
P.yticks([(1, '1'), (3, '3'), (10, '10'), (30, '30'), (100, '100'), (300, '300')])
lx = np.geomspace(1, 300, 40)
P.line(lx, K * 11.4 / lx, sd.MUT, w=2, dash='6 6', markers=False,
       tip=f'days = K·σ68/L with K = {K:.1f} and σ68 = 11.4° (the 30 bar cell)')
for k, r in t.iterrows():
    c = FAM[r.family]
    P.line([r.he3_L_in_beam], [r.days_ATOMKI], c, w=0, r=10, marker='open' if r.geant4 else 'circle', tips=[tipd(k)])
LBL = {'cap500': (8, 14), 'bal5': (8, 14), 'bal10': (8, -14), 'c10': (12, -16), 't500-r1': (-12, -14),
       't200-r2': (14, 8), 'c60m-copv': (14, 8), 'c100m-copv': (14, 22)}
for k, (dx, dy) in LBL.items():
    r = t.loc[k]
    P.raw(T(P.X(r.he3_L_in_beam) + dx, P.Y(r.days_ATOMKI) + dy, SHORT[k], 19, sd.INK, 'start' if dx > 0 else 'end'))
P.raw(T(P.X(55) + 16, P.Y(8.3) - 20, '30 bar variants: 6.7–9.4 d', 19, sd.INK, 'start'))
P.text(1.25, 2.0, 'the gas moves the days; the walls barely do', 25, sd.INK, weight=600)
leg = sd.legend([(FAMN[f], c, 'open' if f in ('anchor', 'balloon') else 'dot') for f, c in FAM.items()], size=21)
D.slide('days', sd.title('Days follow the litres of ³He inside the beam, whatever the pressure or the wall',
                         'Geant4 rows (open) and designs interpolated from them (filled); big plastics, 30 mA, Pb + PE wall exit')
        + sd.row(P.svg('days vs litres'),
                 sd.col(leg, sd.callout(f'days ≈ {K:.0f} · σ68 / L<sub>beam</sub>', sd.BLUE, 30),
                        sd.p('Fitted on the five simulated targets. The other Geant4 rows give K = 32–37 (42 for the 2 L '
                             'balloon, where cosmics start to count).', 23, sd.MUT), w=460, gap=28), gap=40),
        notes=f'σ68² = {SV:.2f}² + ({KK:.2f}·θ₀)², θ₀ the Highland angle at 10 MeV/c through the radial material, reproduces '
              'the balloon (10.8°), the cells (11.3–11.4°) and the capsule (14.4°). The ~11° floor is the Micromegas segment '
              'direction, not the target. Days = K·σ68/L_beam with K from the 30 bar cell. Not in it: the beam-induced '
              'background scaling with the beam area (about 10 % of the 30 bar cell\'s background), so small-beam designs are '
              'probably a little better than drawn and need Geant4. he3_target.py → out/designs.csv, out/calibration.csv.',
        short='days vs ³He')

# ------------------------------------------------------------------ walls
keys = ['c30', 'c30m-copv', 'c30-copv', 'c30-be', 'c30-al']
rows = []
for k in keys:
    r = t.loc[k]
    rows.append((SHORT[k], r.days_ATOMKI, FAM[r.family], tipd(k), f'{r.walls} mm · {r.total_x_over_X0_pct:.2f} % X₀ · σ68 {r.sigma68_deg:.1f}°'))
P2 = sd.Plot(640, 560, x=(0, 1.7), y=(10, 17), xlabel='radial x/X₀ [%]', ylabel='σ68 [°]')
P2.xticks([(0, '0'), (0.5, '0.5'), (1.0, '1.0'), (1.5, '1.5')]).yticks([(v, str(v)) for v in (10, 12, 14, 16)])
xx = np.linspace(0.005, 1.65, 60)
th = [sd_th for sd_th in []]
from math import log, sqrt  # noqa: E402


def hl(x):
    x = x / 100
    b = 10 / np.hypot(10, 0.511)
    return np.degrees(13.6 / (b * 10) * sqrt(x) * (1 + 0.038 * log(x)))


P2.line(xx, [np.hypot(SV, KK * hl(v)) for v in xx], sd.MUT, w=2, dash='6 6', markers=False, tip='σ68² = σv² + (k θ₀)² fit')
for k, r in t.iterrows():
    if r.family == 'balloon' and k == 'bal10':
        continue
    P2.line([r.total_x_over_X0_pct], [r.sigma68_deg], FAM[r.family], w=0, r=9, marker='open' if r.geant4 else 'circle',
            tips=[tipd(k)])
P2.text(0.05, 16.3, 'Micromegas floor ≈ 11°', 21, sd.INK, weight=600)
D.slide('walls', sd.title('Build C cannot be built as drawn, and the honest version costs only ~8 % in days',
                          '30 bar, 55 L in the beam: days by wall build (left); σ68 against the radial material, Geant4 (open) and the fit (right)')
        + sd.row(sd.col(sd.hbars(rows, 10, width=380, label_w=330, fmt=fd, size=23),
                        sd.p('Build C: 0.3 mm CFRP is under the code thickness (0.45 mm at R 5, burst factor 3), and a 0.1 mm '
                             'Be liner is not a product. A plain Al tube costs ×1.4.', 23, sd.MUT), w=980, gap=28),
                 P2.svg('sigma68 vs material'), gap=40),
        notes='Sizing rules (he3_target.py): filament-wound CFRP by netting analysis, t = 1.5·P·R/σ with σ = 500 MPa '
              '(1500 MPa lamina strength, burst factor 3), ≥ 0.3 mm, on a non-structural metal liner; monolithic Be or Al at '
              'min(UTS/4, YS/1.5): Be 86 MPa (Materion I-70-H minimums), Al 2219-T851 114 MPa. The rule reproduces the n_TOF '
              'capsule as built (500 bar at R 10 mm needs 1.5 mm; it has 0.6 Al + 0.9 CFRP). Be tubes are gun-drilled and turned '
              'from block; thin-wall practice is ~0.4 mm at small diameter (ask Materion for Ø80–100 × 400 mm).',
        short='walls')

# ------------------------------------------------------------------ legal class map
P3 = sd.Plot(1060, 700, x=(0.005, 60, 'log'), y=(0.5, 2000, 'log'), xlabel='vessel volume V [L]',
             ylabel='design pressure PS [bar]')
P3.xticks([(0.01, '0.01'), (0.1, '0.1'), (1, '1'), (10, '10'), (50, '50')])
P3.yticks([(1, '1'), (10, '10'), (100, '100'), (1000, '1000')])
sep = [(0.005, 1000), (1, 1000), (1, 50), (60, 50 / 60)]
P3.raw(f'<polygon points="{" ".join(f"{P3.X(a):.1f},{P3.Y(b):.1f}" for a, b in sep + [(60, 0.5), (0.005, 0.5)])}" '
       f'fill="{sd.GREEN}" fill-opacity="0.10"/>', back=True)
P3.line([a for a, b in sep], [b for a, b in sep], sd.GREEN, w=3, markers=False,
        tip='below this line: Art 4(3), sound engineering practice, no conformity marking (V ≤ 1 L at PS ≤ 1000 bar, or PS·V ≤ 50 bar·L)')
for lim, lab in ((200, 'Cat I | II  (PS·V = 200)'), (1000, 'Cat II | III  (1000)')):
    vs = np.geomspace(1, 60, 20)
    P3.line(vs, lim / vs, sd.MUT, w=2, dash='6 5', markers=False, tip=f'PS·V = {lim} bar·L (boundary from secondary sources)')
    P3.raw(T(P3.X(55), P3.Y(lim / 55) + 26, lab, 18, sd.MUT, 'end'))
P3.raw(T(P3.X(0.007), P3.Y(1.2), 'sound engineering practice (no category)', 20, sd.GREEN, 'start', 600))
P3.raw(T(P3.X(20), P3.Y(7), 'Cat I: maker self-certifies', 20, sd.INK, 'middle', 600))
for k, r in t.iterrows():
    if r.p_bar < 2:
        continue
    P3.line([r.V_L], [r.PS_bar], FAM[r.family], w=0, r=9, marker='open' if r.geant4 else 'circle', tips=[tipd(k)])
for k, dx, dy in (('c30m-copv', -14, -14), ('c10m-copv', -14, 24), ('t200-r2', -14, -12), ('t500-r1', 14, 6),
                  ('cap500', 14, -12), ('c100m-copv', 14, 6), ('c30', 14, 22)):
    r = t.loc[k]
    P3.raw(T(P3.X(r.V_L) + dx, P3.Y(r.PS_bar) + dy, SHORT[k], 18, sd.INK, 'start' if dx > 0 else 'end'))
D.slide('legal', sd.title('Every candidate is either below the pressure-equipment threshold or in Category I',
                          'UK Pressure Equipment (Safety) Regulations 2016 = PED Annex II Table 2 (vessels, group 2 gases); PS = 1.1 × fill')
        + sd.row(P3.svg('PED class map'),
                 sd.col(sd.callout('Under 1 L, even 500 bar needs no category: the capsule, the 200 bar tube.', sd.GREEN, 25),
                        sd.callout('The 30 bar cells are Category I (module A).', sd.INK, 25),
                        sd.callout('In service the whole system falls under PSSR 2000: a written scheme of examination.', sd.ORANGE, 25),
                        w=520, gap=24), gap=40),
        notes='Thresholds: SI 2016/1105 reg. 6 (as the PED Art 4): group 2 gas vessels are in scope above V = 1 L with '
              'PS·V > 50 bar·L, or PS > 1000 bar. Category I up to 200 bar·L; the higher boundaries come from secondary '
              'sources and need checking. PSSR 2000 applies to any system above 0.5 bar gauge with a relevant fluid: the cell, '
              'the gas panel and the storage cylinder need a written scheme of examination by a competent person, whatever the '
              'class. Birmingham\'s own pressure-systems procedure applies on top (ask). A custom vessel is not an ADR/TPED '
              'receptacle: it travels empty and is filled on site (ask a dangerous-goods adviser).',
        short='legal class')


# ------------------------------------------------------------------ gas panel P&ID
def box(x, y, w, h, lab, sub='', c=sd.INK, tip=None, fill=sd.CARD):
    s = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" stroke="{c}" stroke-width="2.5"'
         f'{sd.tipattr(tip)}/>' + T(x + w / 2, y + (h / 2 + 8 if not sub else h / 2 - 4), lab, 22, sd.INK, weight=600))
    if sub:
        s += T(x + w / 2, y + h / 2 + 24, sub, 17, sd.MUT)
    return s


def pid_svg():
    W, Hh = 1664, 640
    o = []
    pipe = lambda *pts: ''.join(line(*pts[i], *pts[i + 1], sd.INK, 3.5) for i in range(len(pts) - 1))  # noqa: E731
    o.append(box(20, 60, 230, 90, '³He cylinder', 'supplier\'s, TPED/DOT', tip='the approved storage receptacle; the gas lives here between runs'))
    o.append(box(330, 60, 230, 90, 'getter purifier', '+ LN₂ trap', sd.PURPLE, tip='Zr getter: removes H₂, H₂O, O₂, N₂ and tritium (HT/T₂); the LN₂ trap holds condensables'))
    o.append(box(1240, 30, 400, 170, '', c=sd.GREEN, fill='#e8f3ee', tip=tipd('c30m-copv')))
    o.append(T(1440, 105, 'CELL, 30 bar', 26, sd.INK, weight=600) + T(1440, 140, 'in the ⁴He bag, sniffed for mass 3', 18, sd.PURPLE))
    o.append(box(330, 300, 300, 110, 'CRYOPUMP', 'charcoal at 4–10 K (GM cooler or LHe)', sd.BLUE,
                 tip='fill: adsorb the cylinder cold, then warm into the closed cell (thermal compression to 30 bar). '
                     'Recovery: cold charcoal pumps the cell to < 10⁻³ mbar, then warms into the cylinder.'))
    o.append(box(780, 470, 330, 110, 'DUMP TANK', '≥ 120 L, evacuated', sd.RED,
                 tip='62 L STP into 120 L ends at 0.5 bar: a relief event loses nothing'))
    o.append(box(20, 470, 300, 110, 'turbo + dry scroll', 'evacuation only', sd.MUT,
                 tip='exhausts to air, so it is closed off whenever ³He is in the lines'))
    o.append(pipe((250, 105), (330, 105)) + pipe((560, 105), (1240, 105)))
    o.append(pipe((445, 150), (445, 300)))
    o.append(pipe((170, 470), (170, 355), (330, 355)))
    o.append(pipe((1440, 200), (1440, 525), (1110, 525)))
    o.append(pipe((630, 355), (945, 355), (945, 470)))
    for x, y, lab in ((290, 105, 'V1'), (900, 105, 'V3'), (445, 230, 'V4'), (250, 355, 'V5'), (945, 420, 'V6')):
        o.append(f'<circle cx="{x}" cy="{y}" r="11" fill="{sd.CARD}" stroke="{sd.INK}" stroke-width="3"/>' + T(x + 16, y - 14, lab, 17, anchor='start'))
    o.append(f'<rect x="1424" y="300" width="32" height="44" fill="{sd.RED}"'
             f'{sd.tipattr("relief valve at 33 bar with a burst disc ahead of it (no seat leak), venting into the dump tank")}/>')
    o.append(T(1470, 330, 'burst disc + relief (33 bar)', 19, sd.RED, 'start'))
    o.append(f'<circle cx="760" cy="105" r="16" fill="{sd.CARD}" stroke="{sd.BLUE}" stroke-width="3"'
             f'{sd.tipattr("P1: 0–100 bar transducer on the cell side; P2: 0–1000 mbar capacitance gauge meters the inventory")}/>')
    o.append(T(760, 75, 'P1, P2', 18, sd.BLUE))
    o.append(T(1440, 600, 'all-metal: VCR/CF joints, bellows valves', 19, sd.MUT))
    return sd.svg(W, Hh, ''.join(o), 'gas panel')


D.slide('panel', sd.title('Gas in and out: a closed loop where nothing vents and the cryopump does both jobs',
                          'schematic of the gas panel for the baseline cell; hover each part')
        + pid_svg(),
        notes='<ol><li><b>Fill.</b> Evacuate and bake the cell and lines, leak-check the panel. Expand the cylinder into the cryopump '
              'at 4–10 K (charcoal adsorbs helium). Close it off, open it to the cell, warm the charcoal: the gas compresses into the '
              'cell with no moving parts in the ³He. Top up in steps; meter the inventory on P2 before every warm-up.</li>'
              '<li><b>Recover.</b> Cool the cryopump, open it to the cell: charcoal at 4 K pumps to &lt; 10⁻³ mbar. Warm into the '
              'cylinder (through a compressor if the cylinder sits above what thermal compression reaches). 1 mbar left in 2.3 L is '
              '2×10⁻³ L STP.</li>'
              '<li><b>Losses per campaign:</b> residual &lt; 0.01 L, leaks at 10⁻⁶ mbar·L/s for 60 days 0.005 L, a relief event 0, '
              'regeneration &lt; 0.1 L: ≲ 0.2 % of 62 L.</li>'
              '<li><b>200 bar and above:</b> a small all-metal diaphragm compressor (³He/tritium compatibility is a vendor question) '
              'is the extra cost of the t200 option.</li>'
              '<li><b>Precedent and help:</b> the ILL ³He group (Tyrex fills and recovers cells daily), ISIS, PSI, the detector makers '
              '(tubes at 10–40 atm). The JLab tritium/³He target (40 cm Al 2219 cells, 20 bar ³He, welded, valves outside the '
              'acceptance, evacuated chamber as secondary containment, safety factor ≥ 5; arXiv:1306.6000) is the closest '
              'nuclear-physics precedent. Borrowing a working panel, or its people, is quicker than building one.</li></ol>',
        short='gas panel')

# ------------------------------------------------------------------ not consumed
n_atoms = BASE.he3_L_STP / 22.414 * 6.022e23
trit = BASE.tritons_per_s_fast * 50 * 86400
caps = BASE.captures_per_s * 50 * 86400
rows = [('³He atoms in the cell', n_atoms, sd.GREEN, f'{BASE.he3_L_STP:.0f} L STP'),
        ('lost per campaign (0.2 %)', n_atoms * 2e-3, sd.ORANGE, 'gas loop, §4.2'),
        ('turned into tritium, 50 d', trit, sd.RED, f'{BASE.tritons_per_s_fast:.2g} ³He(n,p)t per s'),
        ('radiative captures, 50 d', caps, sd.BLUE, f'{BASE.captures_per_s:.0f} per s: the signal')]
D.slide('supply', sd.title('The measurement does not use up its ³He, so borrow it before buying it',
                           f'baseline cell, 50 days at 30 mA; atoms on a log scale')
        + sd.hbars([(a, b, c, None, d) for a, b, c, d in rows], 1e25, width=760, log=True, vmin=1e9, label_w=380,
                   fmt=lambda v: sci(v, 1), size=25)
        + sd.flow([dict(label='1. Loan', sub='ISIS (UK: no export licence), ILL, PSI, JCNS, ESS', color=sd.GREEN),
                   dict(label='2. Buy, then resell', sub='DOE Isotope Program, Chemgas, Linde, Air Liquide (ask)', color=sd.BLUE),
                   dict(label='Export licence', sub='³He is dual-use 1C232 (US, EU, UK lists): months, both ways',
                        color=sd.ORANGE),
                   dict(label='Return', sub='getter pass and an analysis: purity and tritium stated', color=sd.PURPLE)],
                  size=23),
        notes='Price: ~2–2.5 k$/L for bulk gas is the most-cited figure (DOE Isotope Program 2024–25, secondary sources); purified '
              'grades are quoted to ~10 k$/L, and there is no transparent spot price. Demand is rising (dilution refrigerators); '
              'the DOE has signed forward purchases of lunar ³He for 2029. Treat 2.5 k€/L as optimistic. Quantities: baseline 62 L, '
              'fallback 21 L, 200 bar tube 90 L, plus ~5 % for lines and the cylinder heel.',
        short='³He supply')

# ------------------------------------------------------------------ tritium
P4 = sd.Plot(1000, 600, x=(0, 6), y=(0.01, 3000, 'log'), xlabel='', ylabel='tritium after 50 days [MBq]')
P4.yticks([(0.01, '0.01'), (0.1, '0.1'), (1, '1'), (10, '10'), (100, '100'), (1000, '1000')])
tk = ['cap500', 'c10m-copv', 'c30m-copv', 'c30', 't200-r2']
P4.xticks([(i + 0.5, SHORT[k].replace('baseline: ', '').replace('fallback: ', '')) for i, k in enumerate(tk)])
for i, k in enumerate(tk):
    r = t.loc[k]
    f_, th_ = r.tritium_MBq_50d_fast, r.tritium_MBq_50d_th1e4
    P4.vbar(i + 0.35, f_, 60, sd.RED, tip=f'{SHORT[k]}: {f_:.2f} MBq from the beam\'s fast neutrons ({r.tritons_per_s_fast:.2g} /s)')
    P4.vbar(i + 0.65, th_, 60, sd.GOLD, tip=f'{SHORT[k]}: {th_:.2f} MBq per 10⁴ n/cm²/s of thermal neutrons on the whole cell')
P4.hline(1000, sd.GREEN, label='UK exemption: 10⁹ Bq per premises (H-3)', tip='EPR 2016 Sch. 23 Table 5')
P4.text(0.15, 200, 'three orders of magnitude below the exemption', 23, sd.INK, weight=600)
D.slide('tritium', sd.title('The beam turns some ³He into tritium: about 1 MBq per run, far below the exemption',
                            '³He(n,p)t: σ = 1.02 b against σ_nγ = 53 µb over the Birmingham spectrum (1.9×10⁴ tritons per capture)')
        + sd.row(P4.svg('tritium'),
                 sd.col(sd.legend([('beam fast neutrons (Geant4 rate)', sd.RED, 'box'),
                                   ('room-return thermal, per 10⁴ n/cm²/s (not simulated)', sd.GOLD, 'box')], size=22),
                        sd.callout('~1.5×10⁵ Bq per g of gas: under the 10⁶ Bq/g exemption, over 100 Bq/g, so it is radioactive '
                                   'material under an exemption. The RPA has to agree it.', sd.ORANGE, 24),
                        sd.callout('The getter takes the tritium out before the gas goes back.', sd.PURPLE, 24),
                        w=600, gap=28), gap=40),
        notes='Thermal ³He(n,p) is 5316 b, so a modest moderated flux from the room (borated PE, concrete, the dump) can match the beam '
              'term; Geant4 can score it in the existing R2/R3 runs. Levels: UK EPR 2016 Schedule 23 Table 5 (10⁹ Bq, 10⁶ Bq/g for '
              'H-3) and Table 2 (100 Bq/g). The vessel itself gets only short-lived activation (²⁸Al).',
        short='tritium')

# ------------------------------------------------------------------ safety
sk = ['cap500', 'c10m-copv', 'c30m-copv', 'c30', 't500-r1', 't200-r2', 'c60m-copv', 'c100m-copv']
rows = [(SHORT[k], t.loc[k].tnt_g, FAM[t.loc[k].family], f'{t.loc[k].stored_kJ:.1f} kJ: isentropic expansion to 1 atm') for k in sk]
D.slide('safety', sd.title('Stored energy is grams of TNT: the safety case is a burst test, a relief path and a catch bag',
                           'TNT equivalent of the gas expanding to 1 atm, per design')
        + sd.row(sd.hbars(rows, 7.5, width=640, label_w=330, fmt=lambda v: f'{v:.2g} g', size=24),
                 sd.col(sd.callout('Burst test a prototype at ≥ 3 PS; proof test the flight vessel at 1.43 PS.', sd.GREEN, 24),
                        sd.callout('Over-charging the cryopump is the realistic overpressure: meter the inventory, burst disc + '
                                   'relief into the dump tank, interlock on P1.', sd.RED, 24),
                        sd.callout('Wound CFRP normally leaks before it breaks; the bag and the frame catch fragments.',
                                   sd.PURPLE, 24), w=560, gap=24), gap=40),
        notes='<table><tr><th>hazard</th><th>control</th></tr>'
              '<tr><td>stored energy (baseline 7.6 kJ)</td><td>burst ≥ 3 PS, proof 1.43 PS, exclusion zone while filling</td></tr>'
              '<tr><td>overpressure (cryopump warm-up into the cell)</td><td>inventory metered on P2; relief + burst disc into the dump tank; interlock</td></tr>'
              '<tr><td>loss of ³He (155 k€)</td><td>dump tank, the bag, leak monitoring (1 % at 30 bar = 0.3 bar)</td></tr>'
              '<tr><td>tritium ≤ 2 MBq</td><td>all-metal panel, getter as the sink, exhaust never sees ³He</td></tr>'
              '<tr><td>beryllium</td><td>none in the baseline (Al liner)</td></tr>'
              '<tr><td>liner buckling during evacuation</td><td>design check; 0.2 mm Al bonded to CFRP at 1 bar external</td></tr></table>',
        short='safety')

# ------------------------------------------------------------------ simulation
D.slide('sim', sd.title('What to simulate next, in the order the answers matter',
                        'MX17_Full_Geant runs that turn the estimates into numbers')
        + sd.row(
            sd.card(sd.p('<b>1 · The cell we would build</b>', 28, sd.GREEN)
                    + sd.p('30 bar, R 4 and 4.5 cm, Al 0.2 + CFRP 0.36–0.5, domes, bosses, valve and side-going fill line, '
                           'the ⁴He bag. Pairs, beam n and γ, room.', 23)
                    + sd.p(f'Decides: the {BASE.days_ATOMKI:.1f} d estimate; whether the beam edge at the wall costs background. '
                           'Needs domes and bosses in --target cell.', 22, sd.MUT)),
            sd.card(sd.p('<b>2 · 200 bar, R 2 cm, Ø4 cm beam</b>', 28, sd.BLUE)
                    + sd.p(f'{ALT.he3_L_in_beam:.0f} L in the beam at {ALT.total_x_over_X0_pct:.1f} % X₀, {ALT.days_ATOMKI:.1f} d (est).', 23)
                    + sd.p('Decides: does a 4× smaller beam cut the room return, DREAM dead time and slab pile-up? If yes, the '
                           'small high-pressure tube wins.', 22, sd.MUT)),
            sd.card(sd.p('<b>3 · ³He(n,p) in the gas</b>', 28, sd.GOLD)
                    + sd.p('Count it in the existing room and wall runs (R2, R3): a re-reduction, not a new run.', 23)
                    + sd.p('Decides: the tritium and the thermal flux at the target.', 22, sd.MUT)),
            sd.card(sd.p('<b>4 · Capsule gas density</b>', 28, sd.RED)
                    + sd.p('He3Gas_500bar = 62.7 mg/cm³ is the ideal-gas value; real ³He at 500 bar, 20 °C is ~50 '
                           '(Z ≈ 1.24).', 23)
                    + sd.p('Decides: the capsule rows are ~25 % high unless n_TOF filled above 500 bar (ask). Also in the '
                           'n_TOF analyses.', 22, sd.MUT)),
            gap=28),
        notes='Nice to have: the monolithic Al 2219 tube (no composites, 9.4 d est) and the 60 bar R 4 cell (3.8 d est) to anchor '
              'the high-pressure end of the interpolation. No new runs for the balloons or the old capsule: they are out.',
        short='simulate')


# ------------------------------------------------------------------ timeline
def gantt():
    W, Hh = 1664, 470
    x0, mw = 420, 92                     # 13 months
    items = [('asks out; Geant4 1–3; choose 30 vs 200 bar', 0, 2, sd.BLUE),
             ('³He request + export licence', 0.5, 9, sd.ORANGE),
             ('vessel design; order 2 prototypes + 1 flight', 2, 6, sd.GREEN),
             ('gas panel: specify, build or borrow', 2, 8, sd.PURPLE),
             ('burst, proof, leak and cycle tests (⁴He)', 6, 9, sd.GREEN),
             ('written scheme; ⁴He dry run at Birmingham', 9, 11.5, sd.RED),
             ('³He fill, beam', 12, 13, sd.INK)]
    o = []
    for m in range(14):
        x = x0 + m * mw
        o.append(line(x, 20, x, Hh - 40, sd.RULE, 1) + T(x, Hh - 12, str(m), 19))
    o.append(T(x0 + 6.5 * mw, 14, 'months from go-ahead', 20, sd.INK))
    for i, (lab, a, b, c) in enumerate(items):
        y = 40 + i * 56
        o.append(T(x0 - 16, y + 27, lab, 21, sd.INK, 'end'))
        o.append(f'<rect x="{x0 + a * mw:.0f}" y="{y + 6}" width="{(b - a) * mw:.0f}" height="34" rx="8" fill="{c}" fill-opacity="0.8"/>')
    return sd.svg(W, Hh, ''.join(o), 'timeline')


D.slide('plan', sd.title('About a year from go-ahead to ³He in the beam; the ³He licence and the vessel tests set the pace',
                         'phases of FEASIBILITY_PLAN §9.2 (estimate)')
        + gantt()
        + sd.table(['budget line (ESTIMATE)', 'k€'],
                   [['³He, 62 L (bought; a loan costs much less)', '155'], ['vessel: design, 2 prototypes, 1 flight + tests', '35–95'],
                    ['gas panel, cryopump, turbo + scroll', '45–135'], ['diaphragm compressor (200 bar option only)', '50–150']],
                   size=21),
        notes='Asks to send now: Birmingham (pressure-systems procedure, room for a gas panel and dump tank, RPA on tritiated ³He, '
              'LHe/LN₂ on site); n_TOF (the 500 bar capsule\'s maker, code, liner, laminate, who filled it and to what pressure); '
              'ISIS / ILL ³He group / PSI (a 60–100 L loan for ~3 months, a panel or a fill service, return conditions); a COPV '
              'shop (Al-lined CFRP Ø80 × 400 mm at 30 bar, Ø40 at 200 bar); Materion only if Be stays in play; ³He suppliers '
              '(price, lead time, buy-back, licensing).',
        short='plan')

# ------------------------------------------------------------------ close
D.slide('close', sd.kicker('what this does not settle')
        + '<h1 style="font-size:52px;font-weight:600;line-height:1.15">Open: whether ³He can be had in time, what Birmingham\'s '
          'rules add, and whether the smaller beam of a high-pressure tube helps the room loads.</h1>'
        + sd.row(
            sd.col(sd.p('<b>Not settled here</b>', 30, sd.DINK),
                   sd.p('Days for unsimulated designs are interpolations (±15 %), without the beam-area dependence of the '
                        'background.', 24, sd.DMUT),
                   sd.p('PED boundaries above 200 bar·L, ADR transport and the ³He price come from secondary sources.', 24, sd.DMUT),
                   sd.p('The room and the shield wall remain the larger risk for the measurement (TARGET_GEANT).', 24, sd.DMUT)),
            sd.col(sd.p('<b>Decisions</b>', 30, sd.DINK),
                   sd.p(f'Baseline 30 bar R 4 ({BASE.he3_L_STP:.0f} L) or the 200 bar R 2 tube ({ALT.he3_L_STP:.0f} L): after '
                        'Geant4 item 2.', 24, sd.DMUT),
                   sd.p(f'Fallback 10 bar ({FALL.he3_L_STP:.0f} L, ~{FALL.days_ATOMKI:.0f} d) if ³He is short.', 24, sd.DMUT),
                   sd.p('Loan before purchase: ask ISIS first.', 24, sd.DMUT)),
            gap=60),
        dark=True, short='open')

OUTF = O / 'he3-target-engineering.html'
D.write(OUTF, note_meta=dict(title='The ³He target: build it, fill it, approve it, empty it',
                             summary='Engineering feasibility of the MX17 ³He target at Birmingham: code-sized vessels, legal class, '
                                     'a closed cryopump gas loop, ³He supply and tritium, and what to simulate next.',
                             date='2026-10-29'))
print(OUTF)
