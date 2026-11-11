"""Build the slide note for the Geant4 study of the two LNL target designs (lnl/target/SHAPES_GEANT.md).

Revised 11 Nov 2026 for the buildability review (lnl/target/TARGET_REVIEW.md, read through review_data.py): a dated
"where this stands" slide, the cover / x-ray / risk / closing slides reworded (the 45° geometry kept, the diamond and
the Mo dropped, the proposal is the same geometry as a one-piece Al cap), the Mo K occupancy corrected (×2, 4 Nov).

Reads lnl/out/target/shapes/ (shapes_geant.py, shapes_backgrounds.py, shapes_rates.py), writes
lnl/out/target/lnl-target-shapes.html:

    ~/PycharmProjects/nTof_x17/.venv/bin/python lnl/target/shapes/deck/build_shapes_deck.py
    python3 ~/PycharmProjects/dylan-cern-site/scripts/add-note.py \\
        lnl/out/target/lnl-target-shapes.html --slug lnl-target-shapes --force --deploy
"""
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.expanduser(os.environ.get(
    'SLIDEDOC_DIR', '~/PycharmProjects/dylan-cern-site/scripts')))
import slidedoc as sd  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import nd_reach_io as nd  # noqa: E402
sys.path.insert(0, str(HERE.parents[1]))
import review_data as RV  # noqa: E402  (the 11 Nov 2026 buildability review: verdicts, the proposed cap)
O = HERE.parents[2] / 'out' / 'target' / 'shapes'
OUTF = HERE.parents[2] / 'out' / 'target' / 'lnl-target-shapes.html'


def rd(name):
    f = O / name
    return pd.read_csv(f) if f.exists() else None


GR, GA, BI, CL = rd('geant_reach.csv'), rd('geant_acceptance.csv'), rd('backgrounds_inventory.csv'), rd('contaminant_levels.csv')
RS, RL, RC, DQ, DV = rd('rates_summary.csv'), rd('rates_by_line.csv'), rd('rates_channels.csv'), rd('daq_live.csv'), \
    rd('days_vs_current.csv')
CU, DIA, MO, TI, LI, AL, PVC, SS = sd.GOLD, sd.PURPLE, sd.GREY, '#8a8f98', sd.BLUE, sd.ORANGE, '#9aa0a6', '#5f6368'
LAB = {'dome200': 'Cu dome 200 µm', 'dome300': 'Cu dome 300 µm', 'dome200glued': 'Cu dome 200, glued on steel',
       'win45d200': 'window 45°, 200 µm', 'win45d300': 'window 45°, 300 µm', 'win0d200': 'window 0°, 200 µm',
       'win0d300': 'window 0°, 300 µm', 'base': 'FEAS baseline (Li₂O 300 / Al 10)',
       'li20_mo8_dia50': 'flat Li 20 / Mo 8 / C 50 (L9)'}
ORDER = ['win45d200', 'win45d300', 'win0d200', 'win0d300', 'dome200', 'dome300', 'dome200glued', 'li20_mo8_dia50', 'base']


def g(det, cfg, ep, col='days_fit'):
    """days come from nd_reach_io (reference fit, shape floating); other columns from geant_reach.csv"""
    if col == 'days_fit':
        return nd.best(cfg, det, ep, nd.CAL)
    if GR is None:
        return np.nan
    q = GR[(GR.det == det) & (GR.config == cfg) & (GR.Ep_keV == ep)]
    return float(q[col].iloc[0]) if len(q) else np.nan


def acc(det, cfg, col='sigma68_deg', sample='x17'):
    if GA is None:
        return np.nan
    q = GA[(GA.det == det) & (GA.config == f'{cfg}_{det}') & (GA['sample'] == sample)]
    return float(q[col].iloc[0]) if len(q) else np.nan


def f2(v, d=2):
    return '—' if not np.isfinite(v) else f'{v:.{d}g}'


D = sd.Deck('LNL target designs in Geant4',
            'Pierfrancesco’s Cu hemisphere and the flat diamond window, simulated with the MX17 arms as built and with the '
            'big plastics, at 1.03 and 1.10 MeV: reach, backgrounds, contamination, trigger and DREAM, scintillator load.')

# --------------------------------------------------------------------------- #
# geometry drawing: both designs in the (y, r) plane, 7 px/mm
def drawing():
    W, H, s = 1664, 470, 5.2
    out = []

    def P(cx, cy, y, r):
        return cx + y * s, cy - r * s

    def ring(cx, cy, y0, y1, r0, r1, color, tip, op=.8):     # both signs of r
        for sg in (1, -1):
            x0, ya = P(cx, cy, y0, sg * r1 if sg > 0 else -r0)
            out.append(f'<rect x="{x0:.1f}" y="{ya:.1f}" width="{(y1 - y0) * s:.1f}" height="{(r1 - r0) * s:.1f}" '
                       f'fill="{color}" opacity="{op}"{sd.tipattr(tip)}/>')

    # dome, left
    cx, cy = 600, 250
    R = 11.0
    ths = np.linspace(-np.pi / 2, np.pi / 2, 80)
    xo = [P(cx, cy, -R + (R + 1.6) * np.cos(a), (R + 1.6) * np.sin(a)) for a in ths]   # wall drawn ×8 thick
    xi = [P(cx, cy, -R + R * np.cos(a), R * np.sin(a)) for a in ths[::-1]]
    pts = ' '.join(f'{x:.1f},{y:.1f}' for x, y in xo + xi)
    out.append(f'<polygon points="{pts}" fill="{CU}" opacity=".9"{sd.tipattr("Cu hemisphere, R 11 mm, 200 µm (drawn ×8 thick); the beam stops in it")}/>')
    li = [P(cx, cy, -R + (R - 0.5) * np.cos(a), (R - 0.5) * np.sin(a)) for a in np.linspace(-0.6, 0.6, 20)]
    out.append(sd.poly([x for x, _ in li], [y for _, y in li], LI, w=6, tip='Li 20 µm on the inside, where the spot lands'))
    ring(cx, cy, -R - 5, -R, R, R + 4, CU, 'Cu rim 4 × 5 mm at the equator (photo)', .9)
    ring(cx, cy, -27, -16, 15, 33, PVC, 'grey flange r 15–33 mm (PVC assumed: ask)', .7)
    ring(cx, cy, -75, -27, 21, 24, PVC, 'grey tube r 21–24 mm, to −165 mm', .7)
    out.append(sd.arrow(P(cx, cy, -75, 0)[0], cy, P(cx, cy, -2, 0)[0], cy, sd.INK, 4, 14))
    out.append(sd.T(cx - 190, 34, 'Cu hemisphere (Pierfrancesco)', 26, sd.INK, weight=600))
    out.append(sd.T(cx - 190, 62, 'Li 20 µm inside 200 µm Cu, on the grey flange', 21, sd.MUT))
    # window, right
    cx, cy = 1360, 250
    th = np.radians(45)

    def seg(z0, z1, r0, r1, color, tip):
        for sg in (1, -1):
            q = []
            for z, rr in ((z0, r0), (z1, r0), (z1, r1), (z0, r1)):
                y = (z - rr * sg * np.sin(th)) / np.cos(th)
                q.append(P(cx, cy, y, rr * sg))
            out.append(f'<polygon points="{" ".join(f"{x:.1f},{yy:.1f}" for x, yy in q)}" fill="{color}" opacity=".9"{sd.tipattr(tip)}/>')
    seg(-0.8, 0, 0, 10, LI, 'Li 14 µm (drawn ×60)')
    seg(0, 0.5, 0, 15, MO, 'Mo 8 µm: the beam stop (drawn ×60)')
    seg(0.5, 2.3, 0, 15, DIA, 'CVD diamond 200 µm (drawn ×9): the vacuum wall')
    seg(-1.6, -0.8, 10, 15, TI, 'Ti ring 0.5 × 5 mm + 0.1 mm epoxy (drawn ×1.6)')
    seg(2.3, 3.1, 10, 15, TI, 'Ti ring 0.5 × 5 mm')
    for sg in (1, -1):
        y_cut = (-1.6 - 10.5 * sg * np.sin(th)) / np.cos(th)
        x0, _ = P(cx, cy, -55, 0)
        x1, _ = P(cx, cy, y_cut, 0)
        _, ya = P(cx, cy, 0, sg * 11.3 if sg > 0 else -10)
        out.append(f'<rect x="{x0:.1f}" y="{ya:.1f}" width="{x1 - x0:.1f}" height="{1.3 * s:.1f}" fill="{AL}" opacity=".85"'
                   f'{sd.tipattr("Al end piece 0.5 mm (drawn ×2.6), 55 mm long, cut on the window plane")}/>')
    ring(cx, cy, -66, -55, 15, 33, PVC, 'the same grey flange, 39 mm further back', .7)
    out.append(sd.arrow(P(cx, cy, -75, 0)[0], cy, P(cx, cy, -1, 0)[0], cy, sd.INK, 4, 14))
    out.append(sd.T(cx - 150, 34, 'Diamond window (flat, 45°)', 26, sd.INK, weight=600))
    out.append(sd.T(cx - 150, 62, 'Li 14 / Mo 8 / diamond 200 µm, Ø20 in Ti rings, on an Al end piece', 21, sd.MUT))
    out.append(sd.T(60, 455, 'beam: p 1.03–1.10 MeV, σ 2 mm, along +y', 21, sd.MUT, anchor='start'))
    return sd.svg(W, H, ''.join(out), 'the two target designs')


# --------------------------------------------------------------------------- #
# cover
def dl0(det, des, I, P):
    q = DQ[(DQ.det == det) & (DQ.design == des) & (DQ.Ep_keV == 1100.0) & DQ.contam & np.isclose(DQ.I_uA, I) & (DQ.prescale == P)]
    return float(q.live.iloc[0]) if len(q) else np.nan


dw, dd = g('bigP', 'win45d200', 1100.0), g('bigP', 'dome200', 1100.0)
dwa, dda = nd.asb_pair('win45d200', 1100.0), nd.asb_pair('dome200', 1100.0)
XDOME = int(dd / dw)   # 10.5 at 1.10 MeV, 10.6 at 1.03: quoted as ×10
cover = (sd.kicker('MX17 at LNL · target designs in Geant4 · 27 Oct 2026')
         + '<h1 style="font-size:52px;font-weight:600;line-height:1.12;letter-spacing:-1.2px">'
           f'The 45° geometry beats the Cu hemisphere by ×{XDOME:.0f} in days with the big plastics. Its diamond and Mo stop were dropped on 11 Nov: '
           'the proposal is the same geometry as a one-piece aluminium cap. DREAM and the scintillators cope if the single-arm trigger is prescaled.</h1>'
         + sd.p('Geant4 run L10: both designs with the photographed beam line, the arms as built and with the big plastics, '
                'X17, M1/E1 IPC (γ₀ and γ₁), EPC, and γ-line libraries for the singles. Nuclear yields from measured data. '
                f'Days: {nd.LABEL} (corrected 10 Nov 2026; FEASIBILITY_SIM.md §19).',
                26, sd.DMUT)
         + sd.row(
             sd.bignum(f'{f2(dw)} d', 'per µA to 3σ at ATOMKI: window 45°, big plastics', sd.DGREEN,
                       f'as built {dwa} d (liquid repaired / as at n_TOF)¹ · 1.10 MeV'),
             sd.bignum(f'{f2(dd)} d', 'per µA: Cu hemisphere 200 µm, big plastics', '#f0a35e',
                       f'as built {dda} d¹ · 1.10 MeV'),
             sd.bignum(f"{dl0('bigP', 'window', 1.0, 10):.0%}", 'DREAM live at 1 µA, prescale 10, window, big plastics', sd.DBLUE, f"{dl0('bigP', 'window', 1.0, 1):.0%} with no prescale"),
             gap=48)
         + sd.p('¹ ' + nd.ASB_NOTE, 18, sd.DMUT))
D.slide('cover', cover, '<p>Dylan, 27 Oct: a full Geant4 study of the two designs, anything that could go wrong, the trigger rate against DREAM, and the γ load on the scintillators. Write-up <code>lnl/target/SHAPES_GEANT.md</code>; Geant4 branch <code>lnl_shapes</code>, run L10.</p>', dark=True, short='cover')

# --------------------------------------------------------------------------- #
# where this stands (the 11 Nov review)
CD = RV.cap_days()
EST = '' if CD['g4'] else '*'


def vrow(tag, name, days=None):
    v = RV.verdict(tag)
    d3 = days or [nd.fmt(x) for x in RV.days3(tag)]
    col = {'propose': sd.GREEN, 'ok': sd.BLUE, 'later': sd.GOLD, 'drop': sd.RED}[v['level']]
    return [name, f'<b style="color:{col}">{v["label"]}</b>', *d3, v['short']]


def ratio(a, b):
    r = [nd.best(x, 'asb', 1100, rs) / nd.best(y, 'asb', 1100, rs) for x in a for y in b for rs in (nd.CAL, nd.AS_NTOF)]
    r = [x for x in r if np.isfinite(x)]
    return min(r), max(r)


OG_LO, OG_HI = ratio(('ogCu200', 'ogCu200_los'), ('ogAl300cu12r8m4', 'ogAl400cu12r8m4'))
srows = [vrow('cap45al400cu', 'Flat Al end cap at 45° (the proposal)', [nd.fmt(CD['big']) + EST, nd.fmt(CD['asb']) + EST, nd.fmt(CD['asb_ntof']) + EST]),
         vrow('dome300', 'Cu hemisphere 300 µm (the cup that exists)'),
         vrow('dome200', 'Cu hemisphere 200 µm'),
         vrow('ogCu200', 'Cu ogive (his CAD sketch, L11)'),
         vrow('win45d200', 'Diamond window 45°, 200 µm'),
         vrow('win45d300', 'Diamond window 45°, 300 µm'),
         vrow('win0d200', 'Diamond window 0°, 200 µm')]
D.slide('status', sd.title('Where this stands (11 Nov 2026): keep the 45° geometry, in aluminium. The diamond and its Mo stop are dropped',
                           'The buildability review checked every design against how lithium targets are really made. Days to 3σ at '
                           'the ATOMKI strength, 1 µA, 1.10 MeV')
        + sd.table(['design', 'verdict', 'big plastics', 'as built, liquid repaired', 'as built, liquid as at n_TOF', 'why'],
                   srows, size=20, align=['left', 'left', 'right', 'right', 'right', 'left'], widths=[470, 270, 150, 170, 180, 420])
        + sd.row(sd.callout('<b>Proposed:</b> ' + RV.CAP['stack'] + '. Same geometry as the 45° window, so the Geant4 result of this '
                            'deck carries over. ' + ('* Days: an estimate from the 45° diamond window, Geant4 run L14 is running. '
                                                     if not CD['g4'] else 'Days: Geant4 run L14. ')
                            + 'All designs side by side: <a href="lnl-target-compare.html" style="color:inherit">lnl-target-compare</a>.',
                            sd.GREEN, 20),
                 sd.callout(f'<b>The Cu shells, as built:</b> with today’s detector the Cu ogive is within ×{OG_LO:.1f}–{OG_HI:.1f} of the '
                            'light Al ogives. The ×10 of this deck is a big-plastics number. The Mo K x-rays are ×2 higher than '
                            'shown on 27 Oct (slide "Micromegas"). The review is a proposal, not yet discussed with Pierfrancesco.',
                            sd.ORANGE, 20), gap=36),
        '<p>Verdicts from <code>lnl/target/TARGET_REVIEW.md</code> (11 Nov 2026) via <code>review_data.py</code>; days from '
        '<code>nd_reach.csv</code> (reference fit, background shape floating). ' + RV.verdict('win45d200')['why'] + ' '
        + RV.verdict('dome300')['why'] + ' ' + nd.ASB_NOTE + '</p>', short='where this stands')

D.slide('designs', sd.title('The two designs as simulated: both are the end of the beam pipe, air outside',
                            'Hover the parts. Sizes from the photos (±20 %) and the 26 Oct decisions.')
        + drawing()
        + sd.table(['', 'Cu hemisphere', 'diamond window'], [
            ['film', 'Li 20 µm lining the inside', 'Li 14 µm at 45° (19.8 µm along the beam); 20 µm at 0°'],
            ['beam stop', 'Cu (range 5.8 µm at 0.87 MeV)', 'Mo 8 µm (range 5.3 µm at 0.87 MeV; 7.5 µm at 1.10 MeV)'],
            ['in the leptons’ path', '200 µm Cu shell, tangent near 90°; Cu rim; grey flange', 'diamond 200 µm, Ti rings, Al end piece'],
            ['variants run', '300 µm; R 17.5 glued on the DN40 steel tube', '0° and 45°; 200 and 300 µm'],
        ], size=21, align=['left', 'left', 'left'], widths=[260, 680, 720]),
        '<p>Geant4 branch <code>lnl_shapes</code> of MX17_Full_Geant: <code>--shape dome|window</code>, the beam line as coaxial '
        'tubes (<code>--line</code>). Vertices are drawn where the σ = 2 mm spot lands on the film, uniform in depth.</p>',
        short='designs')

# --------------------------------------------------------------------------- #
# reach table
if GR is not None:
    rows = []
    for cfg in ORDER:
        r = [LAB[cfg], f2(acc('bigP', cfg), 3) + '°']
        for ep in (1030.0, 1100.0):
            r.append(nd.fmt(g('bigP', cfg, ep)))
        r.append(f2(acc('asb', cfg), 3) + '°')
        for ep in (1030.0, 1100.0):
            r.append(nd.asb_pair(cfg, ep) if np.isfinite(nd.best(cfg, 'asb', ep)) else '–')
        rows.append(r)
    xw = g('bigP', 'win45d200', 1100.0) / g('bigP', 'li20_mo8_dia50', 1100.0)
    D.slide('reach', sd.title(f'Geant4: the 45° window is within ×{xw:.1f} of the flat design (and matches it without its end piece); the Cu hemisphere is ×{XDOME:.0f} slower',
                              f'Geant4 L10: σ68 of the X17 opening angle and days per µA to 3σ at R(ATOMKI), 1 µA, {nd.LABEL}')
            + sd.table(['configuration', 'σ68 big P', 'big P 1.03', 'big P 1.10', 'σ68 as built', 'as built 1.03¹', 'as built 1.10¹'],
                       rows, size=21, align=['left'] + ['right'] * 6, widths=[500, 160, 150, 150, 180, 220, 220])
            + sd.p('As built: liquid scintillator repaired / liquid as it ran at n_TOF. ¹ ' + nd.ASB_NOTE, 18, sd.MUT),
            '<p>Every lepton crosses the Cu shell; near 90° from the apex it runs nearly tangent (~30 % X₀), and the shell converts the ⁸Be γ: EPC is 46 % of the background against 5 % for the window. 0° costs ×1.3 against 45° (rings and end piece in the 90° plane). 1.03 MeV costs +20 % (more direct capture). '
            'Days from <code>nd_reach.csv</code> (<code>shapes_nd.py reach</code>, FEASIBILITY_SIM.md §19): the reference fit, θ × |y| × E_sum, background shape floating, made safe against thin Monte Carlo. '
            'The statistics-only days of 27 Oct (<code>geant_reach.csv</code>) were optimistic by ×1.1–1.4 with big plastics; as built they were an artefact.</p>', short='reach')


D.slide('endpiece', sd.title('The window itself is better than the flat design; its Ø20 Al end piece costs the 3 degrees',
                             'Diagnostic Geant4 runs, X17, big plastics: σ68 of the reconstructed opening angle')
        + sd.hbars([('as designed: Ti rings + 55 mm Al end piece', 9.13, sd.ORANGE, 'acceptance 0.152', '9.1°'),
                    ('Ti rings ~0', 8.73, sd.ORANGE, 'acceptance 0.155', '8.7°'),
                    ('end piece 1 mm CFRP', 8.34, sd.ORANGE, 'acceptance 0.151', '8.3°'),
                    ('flat L9 design, CFRP chamber', 6.64, sd.GREY, 'acceptance 0.131', '6.6°'),
                    ('no end piece', 6.24, sd.GREEN, 'acceptance 0.154', '6.2° (≈ 0.24 d/µA, scaled)'),
                    ('bare window (no end piece, no rings)', 5.70, sd.GREEN, 'acceptance 0.158', '5.7°')],
                   vmax=10, width=700, h=44, label_w=560)
        + sd.callout('Leptons at 90–140° cross the Ø20 tube wall at grazing incidence. A wide adapter was tried in L11 and is no '
                     'better: the wall subtends the same solid angle at any radius. Only a thinner or lighter wall helps, so the '
                     'proposed Al cap keeps the Ø20 tube and has a 0.3 mm end piece as its lever (11 Nov).', sd.GREEN, 23),
        '<p>Runs <code>X17_m16.8_diag_*</code> in L10 (5 × 10⁵ each). SHAPES_GEANT.md §4.1.</p>', short='end piece')

# --------------------------------------------------------------------------- #
# backgrounds inventory
def inv(design, ep, key):
    q = BI[(BI.design == design) & (BI.Ep_keV == ep) & BI.reaction.str.contains(key, regex=False)]
    return float(q.rate_per_uA.iloc[0]) if len(q) else np.nan


rows = []
for key, lab, note in (('γ₀)⁸Be', '⁷Li(p,γ₀)⁸Be, the signal line', 'direct share 71 % (1.03) / 61 % (1.10)'),
                       ('γ₁)⁸Be', '⁷Li(p,γ₁)⁸Be, 15.1/14.6 MeV', 'γ₁ IPC; most trigger legs'),
                       ('478', '⁷Li(p,p′γ) 478 keV', '×330 γ₀: singles, PMT current, MM hits'),
                       ('(p,α)α', '⁷Li(p,α)α', 'α stopped; no γ'),
                       ('⁶Li(p,γ)', '⁶Li(p,γ)⁷Be 5.6 MeV', 'negligible'),
                       ('(α,n)¹⁰B', 'α-induced neutrons', 'ESTIMATE; nothing at the arms'),
                       ('Mo K', 'PIXE: Mo Kα 17.5 keV (window)', 'escapes into the Micromegas'),
                       ('at the interface', '¹⁹F layer 1 µg/cm² at the Li/stop interface', '1.10 MeV: on the 872 keV resonance')):
    v03, v10 = inv('window', 1030.0, key), inv('window', 1100.0, key)
    rows.append([lab, sd.sci(v03, 1) if np.isfinite(v03) else '—', sd.sci(v10, 1) if np.isfinite(v10) else '—', note])
D.slide('bg', sd.title('The film makes 330 soft γ per signal γ, and the stop makes x-rays; no neutrons, nothing in the window',
                       'Per µA (6.24 × 10¹² p/s), window 45°; the dome is the same within 2 % (same Li along the beam)')
        + sd.table(['reaction', '/s at 1.03 MeV', '/s at 1.10 MeV', 'what it does'], rows, size=21,
                   align=['left', 'right', 'right', 'left'], widths=[560, 220, 220, 660])
        + sd.callout('No beam neutrons: ⁷Li(p,n) opens at 1.881 MeV, ⁶⁵Cu(p,n) at 2.17, ¹³C(p,n) at 3.2. Cu/Mo (p,γ) and '
                     'Coulomb excitation < 10⁻¹⁰ per proton.', sd.GREEN, 23),
        '<p>Yields: ⁸Be from Zahnow 1995 (target_model), 478 keV from Bykov 2021, NACRE S-factors for ⁷Li(p,α) and ⁶Li, '
        'TUNL/Redigolo for ¹⁹F, Marta 2010 for the N resonances. PIXE is a binary-encounter scaling anchored on σ_K(Cu, 1 MeV) '
        '≈ 70 b: ESTIMATE ×2–3. Interface fluorine: the beam leaves 20 µm Li at 872 keV at E_p = 1.10 MeV, which is the '
        'strongest ¹⁹F(p,αγ) resonance.</p>', short='backgrounds')

# contamination
crow = [['¹⁹F uniform', '6.1–7.1 MeV γ; 6.05 E0 pairs', 'F/Li 3 × 10⁻⁵', 'trigger legs only'],
        ['¹⁹F layer at the interface', '6–7 MeV γ', '1 µg/cm² → 60 % of γ₀ at 1.10; 1.5 % at 1.03', 'avoid fluoride etch, PFPE oil'],
        ['¹⁹F layer on the face', '6–7 MeV γ', '1 µg/cm² → 3–4 %', 'singles'],
        ['¹⁵N (Li₃N from air)', '4.44 MeV γ, 897 keV res.', 'N/Li 0.8 %', 'harmless, visible'],
        ['²³Na (in Li metal)', '440 keV, 1.63, ≤ 12.7 MeV', 'Na/Li 10⁻⁵ (440); 0.26 % (12.7)', 'singles; IPC below window'],
        ['¹¹B (BN crucibles)', '16.9 MeV γ₀ in the window', 'B/Li 5 %', 'harmless at ppm'],
        ['C build-up', '—', '2.6 keV per 10 µg/cm²', 'harmless']]
D.slide('contam', sd.title('No contaminant can fake the signal; fluorine at the Li/stop interface can double the trigger rate at 1.10 MeV',
                           'Level at which each line reaches 1 % of the ⁸Be γ₀ rate (uniform in the film unless stated)')
        + sd.table(['contaminant', 'line', 'level for 1 % of γ₀', 'verdict'], crow, size=21,
                   align=['left'] * 4, widths=[380, 420, 520, 340]),
        '<p>Boron is the only contaminant whose line lies inside the 13–18 MeV window (the ATOMKI ¹²C case), and it needs '
        'percent levels. The interface fluorine comes from the way the stop is cleaned before the Li goes on, or from '
        'perfluorinated pump oil in the evaporator; one short run at 1.10 MeV with a look at the 6.13 MeV line checks it.</p>',
        short='contamination')

# scintillators
def ch(det, des, c, t, col='rate_per_uA'):
    q = RC[(RC.det == det) & (RC.design == des) & (RC.Ep_keV == 1100.0) & (RC.ch == c) & np.isclose(RC.thr_MeV, t)]
    return float(q[col].iloc[0]) if len(q) else np.nan


srow = []
for det, lab in (('bigP', 'big slab 75×75×5'), ('asb', 'plastic 20×30×2 (as built)')):
    srow.append([lab, sd.sci(ch(det, 'window', 20, 0.05), 1), f"{ch(det, 'window', 20, 1.675):.0f}",
                 sd.sci(ch(det, 'window', 20, 0.05, 'MeV_per_s_uA'), 1)])
srow.append(['LS cell (as built)', sd.sci(ch('asb', 'window', 22, 0.05), 1), f"{ch('asb', 'window', 22, 0.5):.0f} (> 0.5 MeV)",
             sd.sci(ch('asb', 'window', 22, 0.05, 'MeV_per_s_uA'), 1)])
srow.append(['SiPM bar 3 mm (busiest)', sd.sci(RC[(RC.det == 'bigP') & (RC.design == 'window') & (RC.Ep_keV == 1100.0) & (RC.ch < 20) & np.isclose(RC.thr_MeV, 0.05)].rate_per_uA.max(), 1),
             f"{RC[(RC.det == 'bigP') & (RC.design == 'window') & (RC.Ep_keV == 1100.0) & (RC.ch < 20) & np.isclose(RC.thr_MeV, 0.2376)].rate_per_uA.max():.0f} (> 0.24)", '~2 × 10²'])
D.slide('scint', sd.title('Even the big plastics do not saturate: 478 keV makes 3 × 10⁵ hits/s per µA but none above the leg threshold',
                          'Per channel, per µA, E_p 1.10 MeV, window 45° (the dome is the same within 3 %)')
        + sd.table(['channel', '> 50 keV /s', '> 0.5 MIP /s', 'MeV/s'], srow, size=22,
                   align=['left', 'right', 'right', 'right'], widths=[560, 300, 380, 300])
        + sd.p('At 4 µA the big slab counts 1.2 × 10⁶ /s above 50 keV (≤ 311 keV Compton electrons): 12 % pile-up in 100 ns, '
               '+0.03 MeV on average; ~0.5 µA PMT anode current at 10 pe/MeV and gain 10⁶. The room (2 γ/cm²/s assumed) '
               'adds ~2 × 10³ /s.', 23, sd.MUT),
        '<p>Geant4 γ-line libraries (26 lines, 2.6 × 10⁷ γ per detector and design) folded with the line spectrum. Ask the '
        'PMT/base of the big slabs once chosen: keep the divider current ≥ 20× the anode current.</p>', short='scintillators')

# DAQ
def dl(det, des, I, P):
    q = DQ[(DQ.det == det) & (DQ.design == des) & (DQ.Ep_keV == 1100.0) & DQ.contam & np.isclose(DQ.I_uA, I) & (DQ.prescale == P)]
    return q.iloc[0]


def dvi(I, det='bigP', cfg='win45d200', ep=1100.0):
    """days at current I with the best prescale (days_vs_current.csv), rescaled to the reference-fit days at 1 µA"""
    q = DV[(DV.det == det) & (DV.config == cfg) & (DV.Ep_keV == ep) & np.isclose(DV.I_uA, I)].iloc[0]
    return float(q.days_bestP) / float(q.days_1uA) * g(det, cfg, ep)


drow = []
for det, des, lab in (('bigP', 'window', 'window, big plastics'), ('bigP', 'dome', 'dome, big plastics'),
                      ('asb', 'window', 'window, as built'), ('asb', 'dome', 'dome, as built')):
    r1 = dl(det, des, 1.0, 1)
    drow.append([lab, f'{r1.leg_per_s:.0f}', f'{r1.pair_per_s:.0f}',
                 ' / '.join(f'{dl(det, des, I, 1).live:.0%}' for I in (0.25, 1.0, 4.0)),
                 ' / '.join(f'{dl(det, des, I, 10).live:.0%}' for I in (1.0, 4.0))])
D.slide('daq', sd.title('DREAM copes if the single-arm trigger is prescaled: pairs stay at 25–80 /s up to 4 µA',
                        'Legs from the ⁸Be γ (×8 per µA with 20 µm Li), cosmics from L4; τ = 298 µs non-paralysable')
        + sd.table(['', 'legs /s at 1 µA', 'pairs /s', 'live, P = 1: 0.25 / 1 / 4 µA', 'live, P = 10: 1 / 4 µA'], drow,
                   size=22, align=['left', 'right', 'right', 'right', 'right'], widths=[420, 240, 180, 440, 380])
        + sd.p('478 keV fires SiPM bars but never the plastic: accidental legs 0.4 /s at 1 µA. Window, big plastics, P for ≥ 95 % '
               f'live: {dvi(0.25):.1f} d at 0.25 µA, {dvi(1.0):.2f} d at 1 µA (the documented current) to 3σ at ATOMKI; '
               f'{dvi(4.0):.2f} d at 4 µA if LNL can allow it at 1.1 MeV (ask).', 23, sd.MUT),
        '<p>With P = 10 there are still ~9 cosmic MIPs per arm per second for the gain. Data at 1 µA, P = 10: ~100 Hz, '
        '2.5 MB/s, 0.2 TB/day per FEU.</p>', short='DREAM')

# MM
D.slide('mm', sd.title('The window’s Mo K x-rays reach the Micromegas: 30–45 % occupancy per arm per µA. That dropped the Mo',
                       'Geant4 x-ray lines from the film × the x-ray yield. Corrected 11 Nov: the Geant4 yield check of 4 Nov is ×2.0–2.2 the 27 Oct estimate')
        + sd.table(['', 'reaches a drift gap', 'MM hits /arm/s/µA', 'occupancy /arm/µA (1.2 µs)'], [
            ['dome: Cu K 8 keV (1.3 × 10⁹ /s/µA)', '< 2 × 10⁻⁶', '< 3 × 10³', '—'],
            ['window 45°: Mo K 17.5 keV (≈ 3 × 10⁷ /s/µA, corrected)', '6–9 × 10⁻³', '≈ 2.7 × 10⁵', '30–45 % (27 Oct: 16 %)'],
            ['window 0°', '6 × 10⁻³', '≈ 2 × 10⁵', '≈ 20 % (27 Oct: 10 %)'],
            ['γ (478 keV and the rest), either', '—', '2.7 × 10³', '0.3 %']], size=22,
            align=['left', 'right', 'right', 'right'], widths=[620, 300, 320, 420])
        + sd.callout('A 17 keV point cluster per hit, bigger than a track’s ~8 keV in 30 mm. It triggers nothing, but it can '
                     'steal the segment. At 30–45 % the window would run at 0.2–0.5 µA, which gives back its advantage. The fix is '
                     'no Mo: a Cu stop on an aluminium face, whose 8 keV x-rays stop in 0.4 mm of Al (the proposed cap).', sd.ORANGE, 23),
        '<p>Diamond passes 96 % at 17.5 keV, mylar + 9 µm Cu ~60 %, the gas stops ~8 %. Ta instead of Mo is worse '
        '(L lines 8–10 keV from a larger σ_L). The occupancies in the table are the 27 Oct PIXE scaling multiplied by the ×2.0–2.2 of the '
        'Geant4 x-ray check of 4 Nov (lnl/target/CU_LINER.md §6, TARGET_REVIEW.md §4.3). The per-arm range is the arm-to-arm spread.</p>', short='Micromegas')

# what can go wrong
wrow = [['1', 'Cu shell scatters every lepton, converts the γ', 'dome', f'×{XDOME:.0f} days (big plastics)', 'commissioning only; Be and Mo cups dropped 11 Nov'],
        ['2', 'Mo K x-rays in the MM', 'window', '30–45 %/arm/µA', 'no Mo: Cu stop on an Al face (11 Nov)'],
        ['3', '¹⁹F at the Li/stop interface at 1.10 MeV', 'both', '60 % of γ₀ per µg/cm²', 'clean without fluorides; or 1.03 MeV'],
        ['4', 'window = vacuum wall + beam stop', 'window', 'vents the line', 'Al cap 0.4–0.5 mm, pressure test, fast valve'],
        ['5', 'Mo margin at 0° (7.5 of 8 µm without Li)', 'window 0°', 'H into diamond', 'tilt 45° or ≥ 10 µm Mo'],
        ['6', 'H blistering of the stop', 'both', '2e18 /cm²/d/µA', 'fine for 3σ; widen spot for long runs'],
        ['7', 'DREAM dead time', 'both', '75–83 % live at P = 1', 'prescale SINGLE (P 5–10 at 1 µA)'],
        ['8', 'the window’s Ø20 Al end piece in view', 'window', '9.1° vs 6.2° σ68', 'a 0.3 mm end piece (a wide adapter is no better, L11)'],
        ['9', 'Li₃N/LiOH from air; Na in Li', 'both', 'singles only', 'Ar transfer, vendor CoA'],
        ['10', 'grey flange material (insulator?)', 'both', 'charging, HCl', 'ask; keep the halo off']]
D.slide('wrong', sd.title('What could go wrong, ranked: the dome’s copper, the window’s x-rays, and fluorine at 1.10 MeV',
                          'Everything else checked is harmless or has a cheap fix')
        + sd.table(['#', 'risk', 'design', 'size', 'fix'], wrow, size=20,
                   align=['right', 'left', 'left', 'left', 'left'], widths=[50, 560, 170, 330, 550]),
        '<p>Rows 1, 2, 4 and 8 revised 11 Nov 2026 (TARGET_REVIEW.md). Not modelled: gate valve, tees, floor stand (no lepton reaches them); the grey parts are assumed PVC; PIXE is '
        'a scaling estimate; the room γ flux is a stand-in.</p>', short='what can go wrong')

D.slide('end', sd.kicker('next')
        + '<h1 style="font-size:46px;font-weight:600;line-height:1.15">Keep the 45° geometry, in aluminium: a one-piece Al end cap with '
          'a flat face at 45°, a Cu stop and 10–12 µm of LNL’s pressed lithium. Prescale the single-arm trigger. Measure the 6.13 MeV line early.</h1>'
        + sd.p('Revised 11 Nov 2026 (TARGET_REVIEW.md); a proposal, not yet discussed with Pierfrancesco. The 27 Oct recommendation '
               '(the diamond window with Ti rings and Mo 8 µm on a wide adapter) is superseded: the diamond buys nothing at 1.1 W, the Mo '
               'floods the Micromegas, the wide adapter is no better. Geant4 run L14 simulates the cap. All designs: '
               '<a href="lnl-target-compare.html" style="color:inherit">lnl-target-compare</a>.', 26, sd.DMUT),
        '', dark=True, short='next')

if __name__ == '__main__':
    OUTF.write_text(D.html())
    print('wrote', OUTF)
