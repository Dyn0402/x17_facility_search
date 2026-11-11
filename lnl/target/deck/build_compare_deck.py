"""Build the slide note comparing every LNL target design on the table (27 Oct 2026, revised 11 Nov 2026).

Revised after the buildability review of 11 Nov 2026 (lnl/target/TARGET_REVIEW.md): the proposed flat aluminium end
cap at 45° comes first, then the options the review keeps, then the designs it dropped (kept as a record, each with
its verdict).  Slides: cover, "where this stands", the overview (a drawing of each design + the days in three
columns), how lithium targets are really made, the Li thickness finding, one slide per design, the practical slides
(practical_slides.py) and the recommendation.

Reads: the verdicts, the cap and the Li table from lnl/target/review_data.py; the days from shapes/nd_reach_io.py
(the reference fit; rows of runs L13 / L14 and the thin-Li variants win when their files exist, so a rebuild picks
them up); σ68, acceptance and EPC share from geant_acceptance.csv / geant_reach.csv (lnl/out/target/shapes/); the
ray-traces of opt_sketch.py and review_alt.py (lnl/out/target/options/).  Writes lnl/out/target/lnl-target-compare.html:

    ~/PycharmProjects/nTof_x17/.venv/bin/python lnl/target/opt_sketch.py          # trace (if changed)
    ~/PycharmProjects/nTof_x17/.venv/bin/python lnl/target/deck/build_compare_deck.py
    python3 ~/PycharmProjects/dylan-cern-site/scripts/add-note.py \\
        lnl/out/target/lnl-target-compare.html --slug lnl-target-compare --force --deploy

No day count and no ratio of days is typed into the text below: they are all computed from nd_reach_io.
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
LNL = HERE.parents[1]
SH = LNL / 'out' / 'target' / 'shapes'
OP = LNL / 'out' / 'target' / 'options'
OUTF = LNL / 'out' / 'target' / 'lnl-target-compare.html'
sys.path.insert(0, str(LNL / 'target'))
sys.path.insert(0, str(LNL / 'target' / 'shapes'))
sys.path.insert(0, str(HERE))
import nd_reach_io as nd  # noqa: E402
import review_data as RV  # noqa: E402  (the 11 Nov review as data: verdicts, the cap, the Li table, the baseline)
import practical_slides as PS  # noqa: E402  (cost, lead time, 1 bar, heat; the badge helpers)

GR = pd.read_csv(SH / 'geant_reach.csv')
GA = pd.read_csv(SH / 'geant_acceptance.csv')
TR = pd.concat([pd.read_csv(OP / 'sketch_trace.csv'), pd.read_csv(OP / 'shell_trace.csv')]).set_index('config')   # shell_trace: opt_shell_material.py (§20)
TP = pd.read_csv(OP / 'sketch_theta_profile.csv')
ALT = pd.read_csv(OP / 'review_alt_trace.csv').set_index('config')      # review_alt.py: the cap against the diamond window

CU, DIA, MO, TI, LI, AL, PVC, CF, BE = sd.GOLD, sd.PURPLE, sd.GREY, '#3f8f9b', sd.BLUE, sd.ORANGE, '#9aa0a6', '#4a4f5a', sd.GREEN
BEAM = sd.RED
LVC, pill, reason = PS.LVC, PS.pill, PS.reason
COLS3 = 'big plastics / as built with the liquid scintillator repaired / as built with the liquid as it ran at n_TOF'
H3 = ['big plastics', 'as built, liquid repaired', 'as built, liquid as at n_TOF']


def g4(cfg, col='days_fit', ep=1100.0, det='bigP'):
    if col == 'days_fit':     # days: the reference fit (nd_reach.csv); other columns from geant_reach.csv
        return nd.best(cfg, det, ep)
    q = GR[(GR.det == det) & (GR.config == cfg) & (GR.Ep_keV == ep)]
    return float(q[col].iloc[0]) if len(q) else np.nan


def acc(cfg, col='sigma68_deg', det='bigP'):
    q = GA[(GA.det == det) & (GA.config == f'{cfg}_{det}') & (GA['sample'] == 'x17')]
    return float(q[col].iloc[0]) if len(q) else np.nan


def tr(key, col='x_med_pct'):
    return float(TR.loc[key, col]) if key in TR.index else np.nan


def prof(key):
    q = TP[TP.geometry == key].set_index('theta_lo')
    return [float(q.x_med_pct.get(lo, np.nan)) for lo in BANDS]


def pick(*tags):
    """the first tag that has reach rows (so a design moves to its newer Geant4 run when the file lands)."""
    for t in tags:
        if nd.has(t):
            return t
    return tags[-1]


def f3(v3, sep=' / '):
    return sep.join(x if isinstance(x, str) else nd.fmt(x) for x in v3)     # rng3() already gives strings


def rng(tags, det, resp=nd.CAL, ep=1100.0):
    """'lo–hi' of the days over several configurations (one number if they print the same)."""
    v = [x for x in (nd.best(t, det, ep, resp) for t in tags) if np.isfinite(x)]
    if not v:
        return '–'
    lo, hi = nd.fmt(min(v)), nd.fmt(max(v))
    return lo if lo == hi else f'{lo}–{hi}'


def rng3(tags):
    return [rng(tags, 'bigP'), rng(tags, 'asb'), rng(tags, 'asb', nd.AS_NTOF)]


def ratio_range(num, den, dets=(('asb', nd.CAL), ('asb', nd.AS_NTOF))):
    """(lo, hi) of days(num) / days(den) over the given configurations and detector states."""
    r = [nd.best(a, det, 1100, resp) / nd.best(b, det, 1100, resp) for a in num for b in den for det, resp in dets]
    r = [x for x in r if np.isfinite(x)]
    return (min(r), max(r)) if r else (np.nan, np.nan)


BANDS = [45, 60, 75, 90, 105, 120]
T_FLAT = 'design (flat Li/Mo 8/diamond 50, CFRP chamber)'
T_W45 = 'our window: Ø20, 45°, diamond 200, Ti rings, Al end 0.5'

# --------------------------------------------------------------------------- #
# numbers the texts need (all from the readers)
CAP = RV.CAP
CD = RV.cap_days()
CAP_G4 = bool(CD['g4'])
EST = '' if CAP_G4 else ' (estimate, Geant4 running)'
L13_IN = (SH / 'nd_reach_L13.csv').exists()
ALCU = pick('ogAl400cu12_tip', 'ogAl300cu12_tip')          # Al ogive, Cu plated over the whole inside, Li on the tip
ALCU_W = 400 if 'Al400' in ALCU else 300
LINER = ('ogAl400cu12r8m4', 'ogAl300cu12r8m4')            # the 4 Nov design at the two simulated walls
# gain of the 4 Nov design on the Cu ogive, as the review counts it (TARGET_REVIEW §4.1): as built against the Cu ogive
# with the L11 film and with clean (line-of-sight) Li; with the big plastics like for like on the Li
G_ASB = ratio_range(('ogCu200', 'ogCu200_los'), LINER)
G_BIG = ratio_range(('ogCu200_los',), LINER, dets=(('bigP', nd.CAL),))
WALL = ratio_range(('ogAl400cu12r8m4',), ('ogAl300cu12r8m4',), dets=(('asb', nd.CAL),))[0]     # 0.4 mm against 0.3 mm, as built
CAP_ALT = 'one-piece Al cap: Cu 12 / Al 400, 45 deg, Al end piece 0.5 mm'

# --------------------------------------------------------------------------- #
# the designs, live options first (the proposal, then the fallback order of the review), then the dropped ones.
# 'g4' is the headline Geant4 configuration; 'variants' are further (label, tag) rows shown where they have days.
DES = [
    # ---------------- live ----------------
    dict(key='cap', name=CAP['name'], short='Flat Al end cap at 45°', sub=CAP['sub'], g4=CAP['tag'], proxy=CAP['proxy'], trace=None,
         status='Geant4 L14' if CAP_G4 else 'estimate, Geant4 running', color=sd.GREEN,
         stack=CAP['stack'],
         claim=('Proposed: a flat aluminium end cap at 45°. {big} d with big plastics, {asb} to {asbN} d as built (Geant4 L14)' if CAP_G4 else
                'Proposed: a flat aluminium end cap at 45°. About {big} d with big plastics, {asb} to {asbN} d as built (estimate, Geant4 running)'),
         mats=['Li', 'Cu', 'Al', 'CFRP / PVC'], pros=CAP['pros'], cons=CAP['cons'],
         variants=[('face 0.5 mm', 'cap45al500cu'), ('face 0.4 mm, end piece 0.3 mm', 'cap45al400cu_ep03'),
                   ('face 0.4 mm, Li 12 µm', 'cap45al400cu_li12'), ('face 0.4 mm, Li 10 µm', 'cap45al400cu_li10'),
                   ('for scale: the 45° diamond window, 200 µm (dropped)', 'win45d200')],
         note=('' if CAP_G4 else 'Geant4 run L14 (faces of 0.4 and 0.5 mm, a 0.3 mm end piece) is running. Until it lands these are the '
               '45° diamond window’s days: the same geometry, and the ray-trace says aluminium for diamond changes σ68 by 0.0 to 0.5°.'),
         details='<p>The diamond-window design with the diamond, the Ti rings, the glue and the Mo removed (TARGET_REVIEW.md §6.1). '
                 'A short Al 6061-T6 tube end, Ø20 bore, wall 0.5 mm, closed by a flat face at 45° to the beam, machined in one piece '
                 'from bar, with a thick collar 50–60 mm upstream where it joins the line. The stop is ≥ 12 µm of Cu along the beam, '
                 'which is 8.5 µm along the normal of a 45° face: a sputtered seed on a Ti or Cr adhesion layer and electroplated Cu, '
                 'or plain sputtering for an hour or two. The lithium is LNL’s rolled foil pressed on with flat moulds. For 12 µm '
                 'along the beam that is an 8.5 µm foil.</p>'
                 '<p>1 bar on the face (ESTIMATE, clamped ellipse 20 × 28 mm, yield 276 MPa): 0.4 mm → 80 MPa, margin ×3.5. 0.5 mm → '
                 '51 MPa, ×5.4. 0.3 mm → 142 MPa, ×1.9, too thin. Heat: +5 K across the face at 1 µA, plus about 6 K along the end '
                 'piece. Cost: ' + CAP['cost'] + '.</p>'
                 '<p>The bar chart is the ray-trace of <code>review_alt.py</code> (<code>review_alt_trace.csv</code>), the same method '
                 'for every row. The trace reads about 2° below Geant4 for these designs, so only the differences should be used. '
                 '<b>Days: ' + CD['note'] + '.</b> Geant4 configuration <code>cap45al400cu</code> (variants <code>cap45al500cu</code>, '
                 '<code>cap45al400cu_ep03</code>), run L14.</p>'),
    dict(key='ogcu', name='Cu ogive', short='Cu ogive', sub='Pierfrancesco’s CAD sketch (L11)', g4='ogCu200',
         trace='sketch A: Cu ogive 200 µm, Ø50 × 63 mm, bare base', status='Geant4 L11', color=sd.ORANGE,
         stack='Li 20 µm inside a pointed 200 µm Cu shell, Ø50 × 63 mm, tip R 3, on an Al ring and the DN40 line',
         claim='Cu ogive (his sketch): buildable now, {asb} to {asbN} d as built. Electroform it and press the Li on the tip only',
         mats=['Li', 'Cu', 'Al'],
         pros=['the simplest step up from the cup that exists: copper stops the beam and absorbs its own x-rays',
               'steep walls everywhere: the 90° legs cross ≈ 1.1× the wall, not 10×, and no flange is in the arms’ view',
               'as built, the 4 Nov design gains only ×{glo:.1f} to ×{ghi:.1f} on it. The light wall pays with the big plastics (×{blo:.1f} to ×{bhi:.1f})'],
         cons=['200 µm of soft annealed Cu has only ×2–3 on buckling at 1 bar: electroform it in hard copper, or make it 0.25 mm',
               'pressing a rolled foil into a tip of R 2.8 mm needs new moulds, and Li on the 65° flank is ×2.4 thicker along the beam',
               'still 200 µm of Cu on every lepton, and the Cu converts the ⁸Be γ (EPC {epc} of the background)'],
         variants=[('Li on the tip only', 'ogCu200_tip'), ('Li by line of sight', 'ogCu200_los'),
                   ('tip only, Li 12 µm', 'ogCu200_tip_li12'), ('tip only, Li 10 µm', 'ogCu200_tip_li10')],
         details='<p>Geant4 run L11 (<code>ogCu200</code>), 1.10 MeV: the exact CAD profile as G4Polycone layers '
                 '(<code>OgiveProfile.hh</code>), vertices on the inner surface where the σ 2 mm spot lands (cap and flank). The yields fold '
                 'the flank path (<code>opt_sketch.ogive_yield_mix</code>): γ₀ ×2.2 per proton at 1.10 MeV, of which 28 % is the 17.64 MeV '
                 'line, counted as IPC background and not as signal. The "tip only" row has the Li on the tip sphere alone, which is '
                 'what a pressed disc gives. SHAPES_GEANT.md §10.</p>'
                 '<p>Electroforming: copper plated on a turned aluminium mandrel that is then dissolved. CERN made a 200 µm-wall Cu '
                 'chamber this way (DC-plated copper, UTS 352 MPa). A disc that stays on the tip cap (r ≤ 2.5 mm) takes 55 % of a '
                 'σ 2 mm beam. A rounder tip (R 6–8 mm) would take 95 %, and needs a Geant4 check. TARGET_REVIEW.md §4.7, §6.3.</p>'),
    dict(key='ogalcu', name='Al ogive, Cu plated inside', short='Al ogive, Cu plated inside',
         sub=f'Cu over the whole inside, Li on the tip ({"L14" if ALCU_W == 400 else "L12"})', g4=ALCU,
         trace=f'Al {ALCU_W} µm + Mo 8 µm', status='Geant4 L14' if ALCU_W == 400 else 'Geant4 L12', color=AL,
         stack=f'the sketch’s shell in Al 6061-T6 (simulated at {ALCU_W / 1000:.1f} mm, build 0.4 mm), ≥ 12 µm of Cu plated over the '
               f'whole inside as the beam stop, Li pressed on the tip only',
         claim='Al ogive with Cu plated over the whole inside: the ogive to try after the Cu one. {big} d big plastics, {asb} to {asbN} d as built',
         mats=['Li', 'Cu', 'Al'],
         pros=['no sputtering deep in the cone, no mask, no lithium evaporator: a sputtered seed, then electroplating, the route with a precedent (CERN)',
               'plating everywhere loses nothing against the Cu patch: {p300} against {l300} d with big plastics at the same 0.3 mm wall',
               'aluminium is ×3 lighter per lepton than copper, and 0.4 mm of it stops the Cu K x-rays'],
         cons=['a 0.4 mm aluminium wall turned 63 mm deep needs care: plan one or two scrapped parts and a leak test per part',
               'Cu on aluminium must be laid down cool (6061-T6 softens above ~200 °C), and nobody has shown that > 10 µm sticks',
               'the Li on a pointed tip needs new moulds, as for the Cu ogive'],
         variants=[('0.3 mm wall, Li on the tip only', 'ogAl300cu12_tip'), ('0.3 mm wall, Li on the flank too', 'ogAl300cu12'),
                   ('0.4 mm wall, Li on the flank too', 'ogAl400cu12'), ('0.3 mm, tip only, Li 12 µm', 'ogAl300cu12_tip_li12'),
                   ('0.4 mm, tip only, Li 12 µm', 'ogAl400cu12_tip_li12')],
         note=('' if ALCU_W == 400 else 'Simulated at 0.3 mm only. The 0.4 mm wall to build is in Geant4 run L14. For the Cu-patch '
               'design the thicker wall costs about ×{wall:.1f} as built.'),
         details='<p>Geant4 run L12 (<code>ogAl300cu12</code>, and <code>ogAl300cu12_tip</code> with the Li on the tip sphere only), '
                 '1.10 MeV. Run L14 adds the 0.4 mm wall (<code>ogAl400cu12</code>, <code>ogAl400cu12_tip</code>), and this slide moves '
                 'to it when its rows exist. "Option B" of CU_LINER.md §8. The plating route: zincate or a sputtered seed, then acid '
                 'copper to ≥ 12 µm at the tip with an anode wire on the axis, baked, Li pressed on the tip. TARGET_REVIEW.md §4.1, §6.3.</p>'
                 '<p>The material per lepton is the trace of the same shell with an 8 µm Mo liner, which has the radiation length of '
                 '12 µm of Cu (a stand-in, not a new trace).</p>'),
    dict(key='hemi', name='Cu cup', short='Cu cup (exists)', sub='the CN neutron-line target, 300 µm (L10)', g4='dome300',
         trace='L10 hemisphere without its flange (rim only)', status='Geant4 L10', color=CU,
         stack='Li 20 µm rolled and pressed inside a 300 µm Cu hemisphere, R 11, Cu rim 4 × 5 mm, on the grey flange',
         claim='Cu cup: it exists and works today, but needs {asb} to {asbN} d as built. The commissioning target',
         mats=['Li', 'Cu', 'CFRP / PVC'],
         pros=['already built and used at 0.07–0.43 µA: rolled Li pressed on with paired moulds is LNL’s routine',
               'the Cu stops the beam and absorbs its own x-rays', 'easy to cool with air (about 10 °C per watt)'],
         cons=['every lepton crosses Cu, and legs near 90° graze it (≈ 7 % X₀)',
               'converts the ⁸Be γ: EPC is {epc} of the background', 'σ68 {sig:.0f}°: the opening-angle edge washes out'],
         variants=[('200 µm wall', 'dome200'), ('200 µm, R 17.5, glued on the DN40 tube', 'dome200glued')],
         details='<p>Geant4 run L10 (<code>dome300</code>, the 300 µm of the CN paper; <code>dome200</code> is a 200 µm wall), '
                 '1.10 MeV. The material per lepton and the bar chart are the trace at 200 µm. This is the target of the CN 0° line '
                 '(arXiv:2605.12005): lithium rolled to about 20 µm in an argon glovebox and pressed onto the cup. '
                 'Sources: SHAPES_GEANT.md §0, §4; TARGET_REVIEW.md §2.1.</p>'),
    dict(key='ogalli', name='Al ogive + Cu patch + masked Li', short='Al ogive + Cu patch + masked Li', sub='the design sent on 4 Nov (L12)',
         g4='ogAl400cu12r8m4', trace='Al 400 µm + Mo 8 µm', status='Geant4 L12', color=AL,
         stack='Al 6061-T6 shell 0.35–0.4 mm (simulated at 0.4 mm), Cu ≥ 12 µm at the tip only (r ≤ 8 mm), Li 20 µm evaporated from '
               'the axis through a mask (r ≤ 4 mm)',
         claim='Al ogive + Cu patch + masked Li (sent 4 Nov): three steps LNL has not shown, for ×{glo:.1f} to ×{ghi:.1f} on the Cu ogive as built',
         mats=['Li', 'Cu', 'Al'],
         pros=['the lightest ogive without Be or Mo: ×{blo:.1f} to ×{bhi:.1f} faster than the Cu ogive with the big plastics',
               'masked, line-of-sight Li is the same thickness along the beam everywhere, so the flank’s 441 keV excess goes away',
               'Cu K x-rays stop in the 0.4 mm of aluminium'],
         cons=['a 0.35–0.4 mm wall turned 63 mm deep, ≥ 12 µm of Cu stuck to aluminium at the bottom of the cone, Li evaporated through a mask: LNL has shown none of them',
               'sputtering from outside the cone takes 7–30 h for 12 µm and is not line of sight. Evaporating the Li takes 0.8–5 g per coating (estimates)',
               'the Cu patch and its sleeve mask buy nothing: Cu plated over the whole inside gives the same days'],
         variants=[('0.3 mm wall (more Cu K x-rays)', 'ogAl300cu12r8m4'), ('0.4 mm wall, Li mask r ≤ 6', 'ogAl400cu12r8m4_m6'),
                   ('0.3 mm wall, Ti 15 µm instead of Cu', 'ogAl300ti15r8m4'), ('0.3 mm wall, Cu 30 µm', 'ogAl300cu30r8m4')],
         details='<p>Geant4 run L12 (<code>ogAl400cu12r8m4</code>, 0.3 mm: <code>ogAl300cu12r8m4</code>), 1.10 MeV. This is the '
                 'design of CU_LINER.md and of the slides sent on 4 Nov. It was meant for one coating chamber with the source on the '
                 'ogive’s axis, not for the beam pipe. What the baseline says about each step (TARGET_REVIEW.md §4.1): machining '
                 'guides put the comfortable wall for turned 6061 at 0.5–0.8 mm. LNL’s close-coupled sputter rate is 11 µm/h on flat '
                 'hot copper, and at a 150–200 mm throw a magnetron gives 0.1–0.5 nm/s, with the aluminium kept below ~200 °C. LNL '
                 'presses rolled lithium and reported a "dedicated evaporator" in 2015 with no result since.</p>'
                 '<p>The titanium variant (15 µm of Ti as the stop) takes up hydrogen without blistering and makes no x-rays that '
                 'escape, but a 15 µm Ti film has never been tested under MeV protons. Keep it only if LNL already coats thick Ti.</p>'
                 '<p>The material per lepton is the trace of the same shell with an 8 µm Mo liner (a stand-in).</p>'),
    # ---------------- dropped on 11 Nov ----------------
    dict(key='w45', name='Diamond window, 45°', short='Diamond window 45°', sub='on its Ø20 Al end piece (L10)', g4='win45d200',
         trace=T_W45, status='Geant4 L10', color=sd.BLUE,
         stack='Li 14 / Mo 8 / diamond 200 µm, Ø20 in 0.5 mm Ti rings, tilted 45°, on a 55 mm Al end piece (0.5 mm)',
         claim='45° diamond window: dropped on 11 Nov. Its 45° geometry is kept, in aluminium, as the proposed cap',
         mats=['Li', 'Mo', 'diamond', 'Ti', 'Al', 'CFRP / PVC'],
         pros=['no chamber: the window is the end of the vacuum', 'the best buildable geometry simulated: σ68 {sig:.1f}°',
               'tilting moves the rings out of the 90° plane and spreads the spot ×√2'],
         cons=['at 1 µA the beam is 1.1 W: a 0.4 mm aluminium face carries it with a 5 K rise, so the diamond is not needed',
               'Mo K x-rays (17.5 keV) pass the diamond: 30–45 % Micromegas occupancy per arm per µA (Geant4 check of 4 Nov)',
               'brittle, glued in rings, never hydrogen-tested, 6–15 k€ mounted (estimate), and it is the vacuum wall'],
         variants=[('300 µm diamond', 'win45d300'), ('200 µm, Li 12 µm', 'win45d200_li12'), ('200 µm, Li 10 µm', 'win45d200_li10')],
         details='<p>Geant4 run L10 (<code>win45d200</code>, 300 µm: <code>win45d300</code>), 1.10 MeV. The 0.5 mm Al end piece is '
                 'grazed by legs at 90–140° (σ68 9.1° against 6.2° without it). Sources: SHAPES_GEANT.md §0, §4, §7, §11. '
                 'Why it was dropped: TARGET_REVIEW.md §4.3, §4.5.</p>'),
    dict(key='w45be', name='Diamond window, 45°', short='Diamond window 45°, Be end piece', sub='on a Be end piece (L11)', g4='win45be',
         trace='our window 45° on a wide adapter (no Ø20 end piece)', status='Geant4 L11', color=sd.GREEN,
         stack='the same window and rings, on a Ø20 end piece of 0.5 mm Be instead of 0.5 mm Al',
         claim='45° window on a Be end piece: dropped. Nobody supplies the Be part, and the diamond is not needed',
         mats=['Li', 'Mo', 'diamond', 'Ti', 'Be', 'CFRP / PVC'],
         pros=['the end piece stays in the leptons’ view, but Be puts ×4 less material there than Al (0.14 % vs 0.56 % X₀)',
               'at 1 bar the Be end piece has a margin of ~9', 'the 0.3 mm Al end piece of the cap gets part of the way'],
         cons=['a 0.5 mm Be end piece is a custom part: the last supplier of machined Be vacuum tubes stopped in 2023',
               '20–60 k€ and 6–12 months (estimate), plus LNL’s safety approval',
               'the Mo stop and the diamond, as for the window on its Al end piece'],
         details='<p>Geant4 run L11 (<code>win45be</code>), 1.10 MeV. Why the wall and not its shape: any closed vacuum '
                 'envelope around a tilted window must cross the arms’ view on the downstream side of the tilt, and the solid angle it '
                 'subtends from the vertex is the same for a Ø20 tube, a cone or a wide step (the window plane is the only radial surface). '
                 'So the material in view can only be made thinner or lighter. Diagnostics (X17 only): Al 0.25 mm, CFRP 0.5 and 1 mm, '
                 'a 16 mm Al end piece straight on the grey flange. SHAPES_GEANT.md §10. Standard flat Be windows in CF flanges are '
                 'still catalogue parts, a thin Be tube or shell is not (TARGET_REVIEW.md §4.6).</p>'),
    dict(key='w45wide', name='Diamond window, 45°', short='Diamond window 45°, wide adapter', sub='on a wide adapter (L11)', g4='win45wide',
         trace='our window 45° on a wide adapter (no Ø20 end piece)', status='Geant4 L11', color=sd.PURPLE,
         stack='the window on a 2 mm Al plate (r 10–30) in its own plane, then a 0.5 mm Al tube of r 30 cut on that plane, the grey flange behind',
         claim='45° window on a wide adapter: dropped with the diamond, and it was no better than the Ø20 tube',
         mats=['Li', 'Mo', 'diamond', 'Ti', 'Al', 'CFRP / PVC'],
         pros=['the plate lies in the window plane, a radial surface: the leptons hardly cross it',
               'easy to machine, with a standard tube behind it'],
         cons=['the r 30 tube on the downstream side of the tilt stands 30 mm in front of the vertex, in full view of that arm',
               'the same solid angle of wall as the Ø20 end piece: widening moves the material, it does not remove it',
               'the Mo stop and the diamond, as for the window on its Al end piece'],
         details='<p>Geant4 run L11 (<code>win45wide</code>), 1.10 MeV. This is the "open to ≥ Ø60 within a few mm" idea of '
                 'SHAPES_GEANT.md §4.1, run in full. The wall a tilted window needs on its downstream side subtends the same solid angle '
                 'whatever its radius. The plate (radial) costs little and the big tube costs what the small one did. §10.</p>'),
    dict(key='w0', name='Diamond window, 0°', short='Diamond window 0°', sub='perpendicular, Ø20 end piece (L10)', g4='win0d200',
         trace='our window 0°: Ø20, diamond 200, Ti rings, Al end 0.5', status='Geant4 L10', color=sd.PURPLE,
         stack='Li 20 / Mo 8 / diamond 200 µm, Ø20 in 0.5 mm Ti rings, ⊥ beam, on the 55 mm Al end piece',
         claim='0° diamond window: dropped with the diamond. It was ×{r45:.2f} slower than at 45° in any case',
         mats=['Li', 'Mo', 'diamond', 'Ti', 'Al', 'CFRP / PVC'],
         pros=['simplest to build and to align', 'the same window and rings as the 45° design'],
         cons=['the Ti rings lie in the plane of the 90° leptons and are crossed edge-on',
               'twice the external conversion of the 45° window (EPC {epc} of the background)',
               'the Mo stop and the diamond, as for the 45° window'],
         variants=[('300 µm diamond', 'win0d300')],
         details='<p>Geant4 run L10 (<code>win0d200</code>, 300 µm: <code>win0d300</code>), 1.10 MeV. The flat chamber design is '
                 'also perpendicular, but its film sits in the middle of a wide chamber, with no rings or tube nearby. The 0° window '
                 'has its rings and end piece right next to the film. Sources: SHAPES_GEANT.md §0, §4; TARGET_OPTIONS §17 '
                 '(why the tilt helps). The ray-trace gives the same sign for an aluminium cap: a face ⊥ beam costs +0.4° '
                 'against 45° (TARGET_REVIEW.md §4.5).</p>'),
    dict(key='flat', name='Flat target in a chamber', short='Flat target in a chamber', sub='our first design (L9)', g4='li20_mo8_dia50', trace=T_FLAT,
         status='Geant4 L9', color=sd.INK,
         stack='Li 20 / Mo 8 / diamond 50 µm, ⊥ beam, Cu holder ring, inside a CFRP chamber',
         claim='Flat target in a chamber: dropped. Most parts are new, and its Mo stop makes too many x-rays at 1 µA',
         mats=['Li', 'Mo', 'diamond', 'Cu', 'CFRP'],
         pros=['the best resolution of the flat stacks as simulated in L9 ({sig:.1f}°)', 'the target is not the vacuum wall: a crack does not vent the line',
               'film and stack fully characterised (thermal model, L9)'],
         cons=['a 50 µm free-standing diamond membrane with a Mo stop: Mo K x-rays, and most parts are new',
               'needs a CFRP chamber around the target, which Pierfrancesco does not want. The 0.4 mm × 600 mm one of L9 would buckle at 0.35 bar',
               'simulated with the big plastics only: there are no as-built days'],
         variants=[('in a 1 mm × 300 mm chamber that holds vacuum (L11)', 'flat1mm')],
         details='<p>Geant4 run L9 (<code>li20_mo8_dia50</code>), big plastics, 1.10 MeV. The film is perpendicular to the beam '
                 'inside a CFRP chamber (0.4 mm, r 25 mm). This is "our perpendicular design".</p>'
                 '<p>On 24 Oct Pierfrancesco proposed making the target the end of the beam pipe, with no chamber. The diamond window '
                 'is this same stack turned into that end wall. Sources: TARGET_OPTIONS §7, §14–16; SHAPES_GEANT.md §0. '
                 'The thin Li₂O or LiF film on a foil in the same kind of chamber (the ATOMKI-style baseline) is not a fallback either: '
                 'the AN2000 group’s films lasted hours to two days (TARGET_REVIEW.md §2.1, §5).</p>'),
    dict(key='hemibe', name='Be hemisphere', short='Be hemisphere + Mo', sub='his cup in Be + Mo liner (L11)', g4='domeBe200mo8',
         trace=None, status='Geant4 L11', color=BE,
         stack='Li 20 µm on an 8 µm Mo liner inside a 200 µm Be hemisphere, R 11, rim 4 × 5 mm, on the grey flange',
         claim='Be + Mo hemisphere: dropped. Nobody supplies a thin Be shell, and the Mo stop makes too many x-rays',
         mats=['Li', 'Mo', 'Be', 'CFRP / PVC'],
         pros=['the same part and mount as his Cu cup, only the metal changes', 'Be is ×25 lighter per lepton than Cu',
               'the grazing geometry of the hemisphere matters little once the wall is light'],
         cons=['a 200 µm Be hemisphere is a custom part with no supplier: 20–60 k€ and 6–12 months (estimate), plus a safety case',
               'Mo K x-rays escape through 200 µm of Be: about 29 % Micromegas occupancy per arm per µA',
               'still a cup at the vertex: the grey flange is in view of the 130° legs'],
         details='<p>Geant4 run L11 (<code>domeBe200mo8</code>), 1.10 MeV: the "Al/Be cup with a Mo liner" of SHAPES_GEANT.md §8 '
                 'risk #1. Same R 11, rim and grey flange as the Cu hemisphere (L10). §10. No ray-trace was made for this shell.</p>'),
    dict(key='ogbe', name='Be ogive', short='Be ogive + Mo', sub='same shape, Be 300 µm + Mo liner (L11)', g4='ogBe300mo8',
         trace='Be 300 µm + Mo 8 µm', status='Geant4 L11', color=BE,
         stack='the sketch’s shell in Be 300 µm (200 µm variant), with an 8 µm Mo liner as the beam stop, Li 20 µm inside',
         claim='Be ogive: dropped. The fastest shell on paper ({big} d), but nobody supplies thin machined beryllium any more',
         mats=['Li', 'Mo', 'Be', 'Al'],
         pros=['×8 less material per lepton than in Cu, and almost no γ conversion (EPC {epc})', 'no chamber, no tube in view',
               'at 1 bar the 300 µm shell has ×20 margin (§20)'],
         cons=['the last supplier of machined and welded Be vacuum tubes stopped in 2023: 20–60 k€ and 6–12 months for a custom shell (estimate)',
               'needs LNL safety approval (EU carcinogen, 0.2 µg/m³ limit). Brittle, so a failure leaves Be fragments in the line',
               'Mo K x-rays escape through the Be: about 29 % Micromegas occupancy per arm per µA'],
         variants=[('200 µm wall', 'ogBe200mo8'), ('300 µm, Li on the tip only', 'ogBe300mo8_tip')],
         details='<p>Geant4 run L11 (<code>ogBe300mo8</code>, 200 µm: <code>ogBe200mo8</code>), 1.10 MeV, with the flank Li path '
                 'folded in as for the Cu ogive. Material check (TARGET_OPTIONS §20, ESTIMATE): at 1 bar the 300 µm Be shell has ×20 margin on '
                 'buckling and on stress (200 µm: ×7). The cost of 27 Oct (5–25 k€, 3–6 months) was written before the supplier '
                 'situation was known (TARGET_REVIEW.md §4.6). If a lighter wall than 0.4 mm Al is ever needed, a catalogue flat Be '
                 'window at 45° is the only realistic beryllium part.</p>'),
    dict(key='ogal', name='Al ogive + Mo liner', short='Al ogive + Mo liner', sub='same shape, Al 300 µm + Mo 8 µm (L11)', g4='ogAl300mo8',
         trace='Al 300 µm + Mo 8 µm', status='Geant4 L11', color=AL,
         stack='the sketch’s shell in Al 6061 300 µm (200 µm variant), with an 8 µm Mo liner as the beam stop, Li 20 µm inside',
         claim='Al ogive + Mo liner: dropped for the Mo K x-rays. The same shell with a copper stop is the live option',
         mats=['Li', 'Mo', 'Al'],
         pros=['ordinary machining, cheap, no toxic dust', 'light enough: Al is ×3 lighter per lepton than Cu',
               'the liner keeps the Li off the Al (Li alloys with Al) and stops the beam'],
         cons=['Mo K x-rays (17.5 keV) pass 0.3 mm of Al: about 19 % Micromegas occupancy per arm per µA, so it would run at 0.2–0.5 µA',
               'Mo deep inside a cone is a development project', '0.2 mm Al buckles at 1.8 bar: 0.3–0.4 mm is the buildable wall (§20)'],
         variants=[('200 µm wall', 'ogAl200mo8'), ('300 µm, Li on the tip only', 'ogAl300mo8_tip')],
         details='<p>Geant4 run L11 (<code>ogAl300mo8</code>, 200 µm: <code>ogAl200mo8</code>), 1.10 MeV, with the flank Li path '
                 'folded in as for the Cu ogive. TARGET_OPTIONS §20 (27 Oct) put Al 6061-T6 at 0.3–0.4 mm + Mo first and Be 0.3 mm + Mo '
                 'second. The review of 11 Nov withdrew both: the Geant4 x-ray check of 4 Nov found the Mo K yield ×2.0–2.2 the '
                 'estimate used until then (TARGET_REVIEW.md §4.3, §4.6). §10.</p>'),
]

for d in DES:
    tag = d['g4']
    d['v'] = RV.verdict(tag)
    d['est'] = d['key'] == 'cap' and not CAP_G4
    src = tag if nd.has(tag) else d.get('proxy', tag)            # the cap reads its stand-in until L14 lands
    d['days3'] = (CD['big'], CD['asb'], CD['asb_ntof']) if d['key'] == 'cap' else RV.days3(tag)
    d['days'] = d['days3'][0]
    d['days03'] = nd.best(src, 'bigP', 1030)
    stat = tag if np.isfinite(acc(tag)) else d.get('proxy', tag)   # σ68, acceptance, EPC: the tag's rows, else the stand-in's
    d['stat_proxy'] = stat != tag
    d['sigma'], d['acc'], d['epc'] = acc(stat), acc(stat, 'acc'), g4(stat, 'B_epc_share')
    if d['key'] == 'cap':
        d['xmed'], d['conv'] = 100 * float(ALT.loc[CAP_ALT, 'x_med']), float(ALT.loc[CAP_ALT, 'p_conv'])
        d['prof'] = [np.nan] * len(BANDS)
    else:
        d['xmed'] = tr(d['trace']) if d['trace'] else np.nan
        d['conv'] = tr(d['trace'], 'p_conv_18MeV') if d['trace'] else np.nan
        d['prof'] = prof(d['trace']) if d['trace'] else [np.nan] * len(BANDS)
    d['vrows'] = [(lab, t) for lab, t in d.get('variants', []) if t != tag and nd.has(t)
                  and not (d['key'] == 'cap' and t == d.get('proxy') and not CAP_G4)]   # the stand-in is the headline until L14
BYK = {d['key']: d for d in DES}
PS.enrich(DES)
LIVE = [d for d in DES if d['v']['level'] != 'drop']
DROP = [d for d in DES if d['v']['level'] == 'drop']
w45, flat, hemi, w0, cap = BYK['w45'], BYK['flat'], BYK['hemi'], BYK['w0'], BYK['cap']


def sig_s(d):
    return (f'{d["sigma"]:.1f}°' + ('*' if d['stat_proxy'] else '')) if np.isfinite(d['sigma']) else '–'


def x_s(d):
    return f'{d["xmed"]:.2f} %' if np.isfinite(d['xmed']) else '–'


# --------------------------------------------------------------------------- #
# cross-section drawings, (y along the beam → right, r up), both signs of r
def drawing(key, W, H, s, cy=None, y0=-72.0, labels=False):
    out = []
    cx = -y0 * s + 18                                                 # y0 at the left edge
    cy = H / 2 if cy is None else cy
    mn = 2.4                                                          # minimum drawn thickness, px

    def P(y, r):
        return cx + y * s, cy - r * s

    def rect(ya, yb, ra, rb, color, tip, op=.9, both=True):
        for sg in ((1, -1) if both else (1,)):
            x0, _ = P(ya, 0)
            x1, _ = P(yb, 0)
            r_lo, r_hi = (ra, rb) if sg > 0 else (-rb, -ra)
            _, yt = P(0, r_hi)
            _, yb_ = P(0, r_lo)
            w, h = max(x1 - x0, mn), max(yb_ - yt, mn)
            out.append(f'<rect x="{x0:.1f}" y="{yt:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{color}" opacity="{op}"'
                       f'{sd.tipattr(tip)}/>')

    def tilted(z0, z1, r0, r1, th, color, tip, op=.92):     # slab between planes n·x = z0..z1, radial r0..r1 (n tilted by th)
        for sg in (1, -1):
            q = []
            for z, rr in ((z0, r0), (z1, r0), (z1, r1), (z0, r1)):
                y = (z - rr * sg * np.sin(th)) / np.cos(th)
                q.append(P(y, rr * sg))
            out.append(f'<polygon points="{" ".join(f"{x:.1f},{yy:.1f}" for x, yy in q)}" fill="{color}" opacity="{op}"'
                       f'{sd.tipattr(tip)}/>')

    def endpiece(th, zcut, color, tip, r_out=10.5, r_in=10.0, y_up=-55):
        # a thin tube cut on the plane n·x = zcut, so its length differs on the two sides of a tilted face
        for r_sign in (1, -1):
            ycut = (zcut - r_sign * r_out * np.sin(th)) / np.cos(th)
            x0, _ = P(y_up, 0)
            x1, _ = P(ycut, 0)
            _, yt = P(0, r_out if r_sign > 0 else -r_in)
            out.append(f'<rect x="{x0:.1f}" y="{yt:.1f}" width="{max(x1 - x0, mn):.1f}" height="{max((r_out - r_in) * s, mn):.1f}" fill="{color}" '
                       f'opacity=".85"{sd.tipattr(tip)}/>')

    def lab(y, r, text, anchor='start', color=sd.INK):
        if labels:
            x, yy = P(y, r)
            out.append(sd.T(x, yy, text, 21, color, anchor))

    # beam
    e = 1.0 if labels else 2.0                                        # how much the thin layers of a window are thickened
    xa, _ = P(y0 + 2, 0)
    stop = {'flat': -0.4, 'hemi': -0.3, 'ogcu': -0.3, 'ogbe': -0.3, 'ogalcu': -0.3, 'ogalli': -0.3, 'cap': -1.7 * e}.get(key, -1.0)
    xb, _ = P(stop, 0)
    out.append(sd.arrow(xa, cy, xb, cy, BEAM, 3.5 if labels else 2.5, 14 if labels else 8))
    if labels:
        out.append(sd.T(xa + 4, cy - 10, 'p, 1.03–1.10 MeV', 20, BEAM, 'start'))

    if key == 'flat':
        ex = 0.35 if labels else 0.8                                     # mm drawn per µm-layer
        rect(-ex, 0, 0, 20, LI, 'Li 20 µm (drawn thick)')
        rect(0, ex * .6, 0, 20, MO, 'Mo 8 µm (drawn thick)')
        rect(ex * .6, ex * 1.6, 0, 20, DIA, 'CVD diamond 50 µm (drawn thick)')
        rect(ex * 1.6, ex * 1.6 + 2, 10, 20, CU, 'Cu holder ring r 10–20 mm, 2 mm')
        rect(y0 + 4, 26, 25, 25.4, CF, 'CFRP chamber, 0.4 mm, r 25 mm (drawn thick)', .85)
        lab(1.2, 21.5, 'Li / Mo / diamond, ⊥ beam')
        lab(3.5, 13.5, 'Cu holder ring')
        lab(y0 + 6, 27.5, 'CFRP chamber 0.4 mm (vacuum inside)')
    elif key == 'cap':
        # the 45° window with the diamond, the rings and the glue taken out: one piece of aluminium (face + end piece),
        # a thin Cu layer and the Li on the vacuum side
        th = np.radians(45)
        tf = 2.2 * e                                                     # the Al face, drawn thick
        tilted(-1.2 * e, -0.5 * e, 0, 6.5, th, LI, 'Li 10–12 µm along the beam: LNL’s rolled foil, pressed on with flat moulds (drawn thick)')
        tilted(-0.5 * e, 0, 0, 10, th, CU, 'Cu ≥ 12 µm along the beam (8.5 µm on the face): the beam stop, over the whole face (drawn thick)')
        tilted(0, tf, 0, 10.5, th, AL, 'Al 6061-T6 face 0.4–0.5 mm at 45°: the vacuum wall, one piece with the end piece (drawn thick)', .95)
        endpiece(th, tf / 2, AL, 'Al end piece 0.5 mm, 55 mm long: the same piece of aluminium as the face (drawn thick)')
        rect(-57, -55, 10.5, 15, AL, 'thick Al collar where the cap joins the line, out of the arms’ view', .85)
        rect(-66, -57, 15, 33, PVC, 'grey flange r 15–33 mm (PVC assumed)', .7)
        lab(9, 15, 'Al face 0.4–0.5 mm', 'start')
        lab(9, 11, 'Cu ≥ 12 µm, Li 10–12 µm', 'start', '#8a6410')
        lab(-52, 13, 'Al end piece 0.5 × 55 mm, one part')
        lab(-64, 35, 'grey flange')
        lab(5, -14, 'one piece: no diamond,', 'start', sd.MUT)
        lab(5, -18, 'no rings, no glue, no Mo', 'start', sd.MUT)
    elif key in ('w45', 'w45wide', 'w0', 'w45be'):
        th = np.radians(0 if key == 'w0' else 45)
        tilted(-0.8 * e, 0, 0, 10, th, LI, 'Li (drawn thick)')
        tilted(0, 0.5 * e, 0, 15, th, MO, 'Mo 8 µm: the beam stop (drawn thick)')
        tilted(0.5 * e, 2.0 * e, 0, 15, th, DIA, 'CVD diamond 200 µm: the vacuum wall (drawn thick)')
        tilted(-0.8 * e - 0.8, -0.8 * e, 10, 15, th, TI, 'Ti ring 0.5 × 5 mm + 0.1 mm epoxy')
        tilted(2.0 * e, 2.0 * e + 0.8, 10, 15, th, TI, 'Ti ring 0.5 × 5 mm')
        if key != 'w45wide':
            # the end piece is cut on the window plane, so its length differs on the two sides of a tilted window
            epc_, epm = (BE, 'Be') if key == 'w45be' else (AL, 'Al')
            endpiece(th, -0.8 * e - 0.8, epc_, epm + ' end piece 0.5 mm, 55 mm long, cut on the window plane (drawn thick)')
            rect(-66, -55, 15, 33, PVC, 'grey flange r 15–33 mm (PVC assumed)', .7)
            lab(-50, 12.5, f'{epm} end piece 0.5 × 55 mm')
            lab(-64, 35, 'grey flange')
        else:
            # the plate in the window plane (r 10-30) and the r 30 tube cut on that plane, 60 mm long
            tilted(-0.8 * e - 0.8 - 2.0, -0.8 * e - 0.8, 10, 30, th, AL, 'Al plate 2 mm, r 10–30 mm, in the window plane')
            endpiece(th, -0.8 * e - 2.8, AL, 'Al tube 0.5 mm, r 30 mm, cut on the window plane, 60 mm long (drawn thick)', 30.5, 30.0, -60)
            rect(-72, -61, 15, 33, PVC, 'grey flange r 15–33 mm (PVC assumed), moved back', .7)
            lab(-45, 32, 'Al tube 0.5 mm, r 30')
            lab(-14, 22, 'Al plate 2 mm', 'start')
            lab(-70, 35, 'grey flange')
        lab(4, 16, 'Mo 8 / diamond 200 µm', 'start')
        lab(4, 11, 'Ti rings', 'start', TI)
    elif key in ('hemi', 'hemibe'):
        R, t = 11.0, (0.6 if labels else 1.0)
        CUP, cupnm = (BE, 'Be hemisphere R 11 mm, 200 µm + Mo 8 µm liner') if key == 'hemibe' else (CU, 'Cu hemisphere R 11 mm, 300 µm (the cup that exists)')
        ths = np.linspace(-np.pi / 2, np.pi / 2, 80)
        xo = [P(-R + (R + t) * np.cos(a), (R + t) * np.sin(a)) for a in ths]
        xi = [P(-R + R * np.cos(a), R * np.sin(a)) for a in ths[::-1]]
        out.append(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in xo + xi)}" fill="{CUP}" opacity=".95"'
                   f'{sd.tipattr(cupnm + " (drawn thick)")}/>')
        li = [P(-R + (R - 0.4) * np.cos(a), (R - 0.4) * np.sin(a)) for a in np.linspace(-0.5, 0.5, 20)]
        out.append(sd.poly([x for x, _ in li], [y for _, y in li], LI, w=5 if labels else 3, tip='Li 20 µm where the spot lands'))
        rect(-R - 5, -R, R, R + 4, CUP, ('Be' if key == 'hemibe' else 'Cu') + ' rim 4 × 5 mm')
        rect(-27, -16, 15, 33, PVC, 'grey flange r 15–33 mm (PVC assumed)', .7)
        rect(y0 + 4, -27, 21, 24, PVC, 'grey tube r 21–24 mm', .7)
        lab(1.5, 9, ('Be 200 + Mo 8 µm' if key == 'hemibe' else 'Cu 300 µm') + ', R 11')
        lab(-12, 17, ('Be' if key == 'hemibe' else 'Cu') + ' rim')
        lab(-26, 35, 'grey flange')
    elif key in ('ogcu', 'ogbe', 'ogal', 'ogalcu', 'ogalli'):
        import opt_sketch as OS
        pr = OS.profiles()
        dy = OS.Y_SHIFT
        color = {'ogcu': CU, 'ogbe': BE}.get(key, AL)
        shell = {'ogcu': 'Cu shell 0.2 mm', 'ogbe': 'Be shell 0.3 mm', 'ogal': 'Al shell 0.3 mm',
                 'ogalcu': 'Al 6061-T6 shell, 0.4 mm to build', 'ogalli': 'Al 6061-T6 shell 0.35–0.4 mm'}[key]
        extra = {'ogbe': ' + Mo 8 µm liner', 'ogal': ' + Mo 8 µm liner'}.get(key, '')
        for sg in (1, -1):
            po = [P(y + dy, sg * r) for r, y in pr['ogive_out']]
            # the thin wall is drawn as a thick outline
            out.append(sd.poly([x for x, _ in po], [y for _, y in po], color, w=5 if labels else 3.2,
                               tip=shell + ' (drawn thick): Ø50 × 63 mm, tip R 3' + extra))
            if key in ('ogalcu', 'ogalli'):
                # the Cu layer on the inside: the inner profile moved inward along its normal so that it shows
                rmax = 1e9 if key == 'ogalcu' else 8.0
                pin = np.array([P(y + dy, sg * r) for r, y in pr['ogive_in'] if r <= rmax])
                tg = np.gradient(pin, axis=0)
                nrm = np.stack([-tg[:, 1], tg[:, 0]], axis=1)
                nrm /= np.maximum(np.hypot(nrm[:, 0], nrm[:, 1]), 1e-9)[:, None]
                inside = np.array(P(-30, 0)) - pin
                nrm *= np.sign((nrm * inside).sum(axis=1))[:, None]
                pin = pin + nrm * (4.5 if labels else 2.8)
                out.append(sd.poly(pin[:, 0], pin[:, 1], CU, w=3.2 if labels else 2.0,
                                   tip='Cu ≥ 12 µm plated over the whole inside: the beam stop, no mask (drawn thick, moved inward)'
                                   if key == 'ogalcu' else 'Cu ≥ 12 µm at the tip only, r ≤ 8 mm, through a sleeve mask (drawn thick, moved inward)'))
        litip = {'ogalcu': 'Li pressed on the tip only', 'ogalli': 'Li 20 µm evaporated through a mask, r ≤ 4 mm'}.get(
            key, 'Li 20 µm inside the tip, where the beam lands')
        ldx = (4.5 if labels else 2.8) / s if key in ('ogalcu', 'ogalli') else 0.0
        out.append(f'<circle cx="{P(-0.4 - 1.4 * ldx, 0)[0]:.1f}" cy="{cy:.1f}" r="{max(2.8 * s * .35, 3):.1f}" fill="{LI}"'
                   f'{sd.tipattr(litip)}/>')
        rect(-68, -63, 19.05, 30, AL, 'Al adapter ring r 19–30 mm, 5 mm (assumed; out of the arms\' view)', .6)
        rect(y0 + 4, -68, 17.4, 19.05, sd.GREY, 'DN40 steel tube', .6)
        lab(-40, 23, {'ogcu': 'Cu 200 µm', 'ogbe': 'Be 300 µm + Mo liner', 'ogal': 'Al 300 µm + Mo liner',
                      'ogalcu': 'Al 0.4 mm, Cu plated over the whole inside', 'ogalli': 'Al 0.35–0.4 mm'}[key])
        if key == 'ogalli':
            lab(-16, 13, 'Cu patch at the tip (r ≤ 8)', 'start', '#8a6410')
            lab(-16, -15.5, 'Li through a mask (r ≤ 4)', 'start', LI)
        if key == 'ogalcu':
            lab(-16, -15.5, 'Li pressed on the tip', 'start', LI)
        lab(-66, 33, 'Al ring (assumed)', color=sd.MUT)
    return sd.svg(W, H, ''.join(out), f'cross-section of {key}')


# --------------------------------------------------------------------------- #
def table(heads, rows, al, wd=None, size=21, hsize=None, pad='.3em .55em'):
    """a light table whose rows are lists of cell HTML, (cells, tr-attributes) pairs, or ready '<tr>' strings."""
    wd = wd or [None] * len(heads)
    th = ''.join(f'<th style="text-align:{a};padding:{pad};line-height:1.15;{f"font-size:{hsize}px;" if hsize else ""}'
                 f'{f"width:{w}px;" if w else ""}">{c}</th>' for c, a, w in zip(heads, al, wd))
    trs = []
    for r in rows:
        if isinstance(r, str):
            trs.append(r)
            continue
        cells, attr = r if isinstance(r, tuple) else (r, '')
        trs.append(f'<tr{attr}>' + ''.join(f'<td style="text-align:{a};padding:{pad}">{c}</td>' for c, a in zip(cells, al)) + '</tr>')
    return f'<table style="font-size:{size}px"><thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table>'


def divider(ncol, text, color=sd.RED):
    return (f'<tr><td colspan="{ncol}" style="padding:.55em .55em .2em;font-size:17px;font-weight:600;letter-spacing:1.5px;'
            f'text-transform:uppercase;color:{color};border-bottom:2px solid {color}">{text}</td></tr>')


N_LIVE, N_DROP = len(LIVE), len(DROP)
NUM = {5: 'five', 6: 'six', 7: 'seven', 8: 'eight', 9: 'nine', 10: 'ten', 11: 'eleven', 12: 'twelve', 13: 'thirteen', 14: 'fourteen'}
NOT_PF = 'A proposal from the review of 11 Nov. It has not yet been discussed with Pierfrancesco.'
CAP3 = f3(cap['days3'])
OGCU3 = rng3(('ogCu200', 'ogCu200_tip'))
ALCU3 = rng3((ALCU,))
LINER3 = rng3(LINER)

D = sd.Deck('LNL target designs compared',
            'Every MX17 target design for LNL side by side after the buildability review of 11 Nov 2026: the proposed flat aluminium '
            'end cap at 45°, the Cu ogive and the Cu-plated Al ogive as fallbacks, and the designs that were dropped (diamond, '
            'beryllium, molybdenum stops), with the days to 3σ for three detector states.')

# ---- cover
D.slide('cover', sd.kicker('MX17 at LNL · target designs · 27 Oct 2026, revised 11 Nov 2026') +
        '<h1 style="font-size:70px;line-height:1.08;font-weight:600;max-width:1640px">Build a flat aluminium end cap at 45°. '
        'The Cu ogive is the fallback. Beryllium, molybdenum and diamond are dropped</h1>' +
        sd.row(sd.bignum(str(len(DES)), 'designs compared', sd.DBLUE,
                         f'{N_LIVE} live options and {N_DROP} dropped on 11 Nov, kept as a record with the reason'),
               sd.bignum(CAP3, 'days to 3σ at 1 µA, the proposed cap', sd.DGREEN,
                         COLS3 + ('. An estimate from the 45° diamond window: Geant4 run L14 is running' if not CAP_G4 else '. Geant4 run L14'), size=60),
               sd.bignum(f3(BYK['ogcu']['days3']), 'days, the Cu ogive (the fallback)', sd.DGREY,
                         'as built it is within the reach of anything that can be built quickly', size=60), gap=56) +
        sd.p(NOT_PF, 26, sd.DMUT),
        notes='<p>On 11 Nov 2026 a buildability review (<code>lnl/target/TARGET_REVIEW.md</code>) checked every design against how '
              'lithium targets are really made, at LNL and elsewhere. This deck is the comparison of 27 Oct brought in line with it. '
              'Earlier designs stay as a record, each with its verdict.</p>'
              '<p>Days are days of beam at 1 µA (the documented current at 1.0–1.1 MeV) to reach 3σ at the ATOMKI strength '
              '(R = 5.8 × 10⁻⁶), E_p = 1.10 MeV, m_X = 16.8 MeV. They come from the reference fit, θ × |y| × E_sum with the '
              'background shape floating, made safe against thin Monte Carlo (<code>nd_reach.csv</code>, FEASIBILITY_SIM.md §19; '
              'interim until run L13 is folded in). Three detector states: MX17 with the big plastics, the detector as built with '
              'the liquid scintillator repaired, and as built with the liquid as it ran at n_TOF. ' + nd.ASB_NOTE + '</p>'
              '<p>"Material per lepton" is the median x/X₀ crossed by an X17 lepton on its way to the arms, from one ray-trace '
              'applied to every design in the same way (<code>opt_sketch.py</code>). It ranks the designs. It is not Geant4.</p>',
        dark=True, short='cover')

# ---- where this stands
AL3 = ['left', 'left', 'right', 'right', 'right', 'left']
WD3 = [300, None, 130, 130, 140, 440]


def srow(vtag, name, role, v3, tip_extra='', star=False):
    v = RV.verdict(vtag)
    g = v['level'] == 'drop'
    st = '*' if star else ''
    cells = [pill(v, 15), f'<b>{name}</b>' + (f' <span style="color:{sd.MUT};font-size:15px">{role}</span>' if role else ''),
             v3[0] + st, v3[1] + st, v3[2] + st, reason(v)]
    return (cells, sd.tipattr(v['why'] + tip_extra) + (f' style="color:{sd.MUT}"' if g else ''))


def names_of(vkey):
    return [d['short'] for d in DES if d['v']['key'] == vkey]


def tags_of(vkey):
    return [t for t, k in RV.VERDICT_OF.items() if k == vkey]


DROPNAME = {'be': 'Everything in beryllium', 'mo': 'Every molybdenum stop', 'diamond': 'The diamond',
            'thin_film': 'Thin LiF / Li₂O films'}
stand_rows = [
    srow(CAP['tag'], 'Flat aluminium end cap at 45°', 'the proposal', [nd.fmt(x) for x in cap['days3']],
         ' Days: ' + CD['note'] + '.', star=not CAP_G4),
    srow('ogCu200', 'Cu ogive, electroformed', 'fallback 1 if the ogive stays', OGCU3,
         ' Days: from the Li film of run L11 to Li on the tip only.'),
    srow(ALCU, 'Al ogive, Cu plated over the whole inside', 'fallback 2', ALCU3,
         f' Days: simulated at {ALCU_W / 1000:.1f} mm, Li on the tip only.'),
    srow('dome300', 'Cu cup', 'exists: the commissioning target', rng3(('dome300', 'dome200')), ' Days: 200 to 300 µm wall.'),
    srow('ogAl400cu12r8m4', 'Al ogive + Cu patch + masked Li', 'sent 4 Nov: not now', LINER3, ' Days: 0.3 to 0.4 mm wall.'),
    srow('ogAl300ti15r8m4', 'The same with a Ti stop', 'a variant to ask about', rng3(('ogAl300ti15r8m4',))),
    divider(6, 'Dropped on 11 Nov, kept in this deck as a record'),
] + [srow(tags_of(k)[0], DROPNAME[k], '', rng3(tags_of(k)),
          ' Takes out: ' + ', '.join(names_of(k)) + '.' if names_of(k) else '') for k in ('be', 'mo', 'diamond', 'thin_film')]
D.slide('stand', sd.title('Where this stands (11 Nov 2026): build a flat aluminium cap at 45°, keep the Cu ogive as the fallback',
                          'The buildability review checked every design against how lithium targets are really made. Days to 3σ at '
                          'the ATOMKI strength, 1 µA, 1.10 MeV') +
        table(['verdict', 'design', H3[0], H3[1], H3[2], 'why, in one line (hover for more)'], stand_rows, AL3, WD3, size=19, hsize=16, pad='.16em .5em') +
        sd.row(sd.callout(NOT_PF + ' The proposed design is on <a href="#cap" style="color:inherit">its own slide</a>. '
                          + ('* Estimate from the 45° diamond window, Geant4 run L14 is running.' if not CAP_G4 else 'The cap’s days are Geant4 run L14.'),
                          sd.GREEN, 21),
               sd.callout('For every design: make the lithium 10–12 µm, not 20. A 20 µm film that turns to hydroxide reaches the '
                          '441 keV resonance (<a href="#lithium" style="color:inherit">the lithium slide</a>).', sd.RED, 21), gap=40),
        notes='<p>The review (<code>lnl/target/TARGET_REVIEW.md</code>, 11 Nov 2026) in one table. The verdicts come from '
              '<code>lnl/target/review_data.py</code> and the days from <code>nd_reach.csv</code> (reference fit). A range covers '
              'the simulated variants of a design. For a dropped family it covers every simulated design in it.</p>'
              + ''.join(f'<p><b>{nm}: {RV.verdict(t)["label"]}.</b> {RV.verdict(t)["why"]}</p>' for nm, t in (
                  ('Flat aluminium end cap at 45°', CAP['tag']), ('Cu ogive', 'ogCu200'), ('Al ogive, Cu plated over the whole inside', ALCU),
                  ('Cu cup', 'dome300'), ('Al ogive + Cu patch + masked Li', 'ogAl400cu12r8m4'), ('Ti stop', 'ogAl300ti15r8m4'),
                  ('Beryllium', 'ogBe300mo8'), ('Molybdenum stops', 'ogAl300mo8'), ('The diamond', 'win45d200'),
                  ('Thin LiF / Li₂O films', 'base')))
              + '<p>The thin-film row is the ATOMKI-style baseline (a 300 µg/cm² Li₂O film on 10 µm of Al in a chamber, beam to a '
              'dump). It has no slide of its own here. ' + nd.ASB_NOTE + '</p>',
        short='where this stands')


# ---- overview
def mini(d):
    c = LVC[d['v']['level']]
    v3 = d['days3']
    st = '*' if d['est'] else ''
    tip_days = (f'{f3(v3)} d at 1 µA, 1.10 MeV ({COLS3})' + (f'. Big plastics at 1.03 MeV: {nd.fmt(d["days03"])}' if np.isfinite(d['days03']) else '')
                + ('. Estimate: the 45° diamond window’s Geant4 days, Geant4 run L14 is running' if d['est'] else f'. {d["status"]}'))
    drows = ''.join(f'<div style="display:flex;justify-content:space-between;align-items:baseline;border-top:1px solid {sd.RULE};padding-top:2px">'
                    f'<p style="font-size:13px;color:{sd.MUT};line-height:1.1;max-width:84px">{a}</p>'
                    f'<p style="font-size:25px;font-weight:600;line-height:1.1">{nd.fmt(x)}{st}</p></div>' for a, x in zip(H3, v3))
    return (f'<div{sd.tipattr(d["v"]["why"])} style="width:316px;display:flex;flex-direction:column;gap:6px;background:{sd.CARD};border:1px solid {sd.RULE};'
            f'border-top:7px solid {c};border-radius:14px;padding:10px 14px">'
            f'<p style="font-size:21px;font-weight:600;line-height:1.12">{d["name"]} <span style="font-weight:400;color:{sd.MUT};font-size:15px">{d["sub"]}</span></p>'
            f'<div>{pill(d["v"], 13)}</div><p style="font-size:15px;line-height:1.2;color:{c};font-weight:600">{reason(d["v"])}</p>'
            f'<div style="display:flex;gap:8px;align-items:center"{sd.tipattr(tip_days)}>{drawing(d["key"], 150, 112, 1.5)}'
            f'<div style="display:flex;flex-direction:column;gap:3px;flex:1">{drows}</div></div>'
            f'<p style="font-size:14px;color:{sd.MUT}">● {d["status"]} · σ68 {sig_s(d)} · {x_s(d)} X₀ per leg</p></div>')


def mini_drop(d):
    return (f'<div{sd.tipattr(d["v"]["why"])} style="width:193px;display:flex;flex-direction:column;gap:3px;background:{sd.BG2};border:1px solid {sd.RULE};'
            f'border-top:5px solid {sd.GREY};border-radius:12px;padding:8px 10px;color:{sd.MUT}">'
            f'<p style="font-size:16px;font-weight:600;line-height:1.12">{d["short"]}</p>'
            f'<div style="filter:grayscale(.75);opacity:.7;align-self:center">{drawing(d["key"], 150, 96, 1.3)}</div>'
            f'<p style="font-size:17px;font-weight:600;line-height:1.1"{sd.tipattr(COLS3)}>{f3(d["days3"])} d</p>'
            f'<p style="font-size:13px;line-height:1.2;color:{sd.RED}">{reason(d["v"])}</p></div>')


D.slide('overview', sd.title(f'{NUM.get(len(DES), len(DES)).capitalize()} designs: {NUM.get(N_LIVE, N_LIVE)} live options, led by the flat '
                             f'aluminium cap, and {NUM.get(N_DROP, N_DROP)} dropped on 11 Nov',
                             'Days to 3σ at the ATOMKI strength, 1 µA, 1.10 MeV (' + nd.LABEL + '), in three detector states') +
        f'<div style="display:flex;gap:20px">{"".join(mini(d) for d in LIVE)}</div>'
        f'<div style="display:flex;align-items:center;gap:16px;margin-top:-10px"><p style="font-size:17px;font-weight:600;letter-spacing:1.5px;'
        f'text-transform:uppercase;color:{sd.RED};white-space:nowrap">Dropped on 11 Nov, kept as a record '
        f'<span style="font-weight:400;text-transform:none;letter-spacing:0;color:{sd.MUT}">(days: {H3[0]} / {H3[1]} / {H3[2]})</span></p>'
        f'<div style="flex:1;border-top:2px solid {sd.RED}"></div></div>'
        f'<div style="display:flex;gap:16px;margin-top:-14px">{"".join(mini_drop(d) for d in DROP)}</div>'
        + (sd.p('* The cap: an estimate from the 45° diamond window (the same geometry), until Geant4 run L14 lands.', 16, sd.MUT, extra='margin-top:-18px') if not CAP_G4 else ''),
        notes=table(['design', 'verdict (11 Nov)', 'big plastics', 'as built, liquid repaired', 'as built, liquid as at n_TOF',
                     'big plastics, 1.03 MeV', 'σ68', 'X17 acceptance', 'median x/X₀ per leg (trace)', '18 MeV γ conversion (trace)',
                     'EPC share of background', 'source'],
                    [[f'{d["name"]}, {d["sub"]}', f'{d["v"]["label"]}: {reason(d["v"])}', *[nd.fmt(x) for x in d['days3']],
                      nd.fmt(d['days03']), sig_s(d), f'{d["acc"]:.3f}' if np.isfinite(d['acc']) else '–', x_s(d),
                      f'{100 * d["conv"]:.1f} %' if np.isfinite(d['conv']) else '–', sd.pct(d['epc']) if np.isfinite(d['epc']) else '–',
                      d['status']] for d in DES], ['left'] * 2 + ['right'] * 10, size=14, pad='3px 8px') +
              '<p>Days to 3σ at the ATOMKI strength at 1 µA and 1.10 MeV, reference fit. ' +
              ('The cap’s days, σ68, acceptance and EPC share are the 45° diamond window’s (marked *), the same geometry, until '
               'Geant4 run L14 lands. Its x/X₀ and γ conversion are the ray-trace of <code>review_alt.py</code> for a 0.4 mm face. '
               if not CAP_G4 else 'The cap’s x/X₀ and γ conversion are the ray-trace of <code>review_alt.py</code> for a 0.4 mm face. ') +
              'The EPC share is the fraction of the selected background made by ⁸Be γ converting in the material '
              '(Geant4). The trace columns use one ray-trace on the 65 508 accepted X17 pairs of L9. For the 0° '
              'window and the hemisphere the trace is lower than Geant4 suggests: Cu shells were under-read by ×1.5 in σ68. '
              'The Cu-plated and Cu-patch Al ogives use the trace of the same shell with an 8 µm Mo liner (the same radiation '
              'length as 12 µm of Cu). ' + nd.ASB_NOTE + '</p>',
        short='overview')

# ---- how lithium targets are really made
brow = [([f'<b style="color:{sd.BLUE if lab.startswith("LNL") else sd.INK}">{lab}</b>', how,
          f'<span style="color:{sd.MUT};font-size:17px">{src}</span>'], '') for lab, how, src in RV.BASELINE]
D.slide('baseline', sd.title('Nobody deposits lithium inside a beam pipe. LNL rolls it to 20 µm in a glovebox and presses it on copper',
                             'How lithium targets are really made: the baseline the verdicts rest on (literature search of 11 Nov)') +
        sd.row(sd.col(table(['laboratory', 'how the lithium is made and moved', 'source'], brow, ['left', 'left', 'left'],
                            [270, None, 220], size=20), w=1060),
               sd.col(sd.callout(RV.BEAM_PIPE, sd.RED, 22),
                      sd.callout('20 µm of lithium metal on copper is LNL’s routine. That is exactly our film and our stop, made '
                                 'without any evaporation.', sd.GREEN, 22),
                      sd.callout('Thin compound films on thin backings are what the pair experiments chose. At LNL they broke in '
                                 'hours. A film on a metal stop that carries the heat is the robust layout.', sd.BLUE, 22), gap=22), gap=44),
        notes='<p>TARGET_REVIEW.md §2 and §3, with the sources in its §10. The quotes were read in the papers listed, and should be '
              'checked in their source before they go into a talk or a message.</p>'
              '<p>Our proposal of 4 Nov asked for "one vacuum system, the source on the axis". That is a coating chamber, not the '
              'beam pipe. If the question Pierfrancesco received says "in the beam pipe", he may say no to something we do not need. '
              'Depositing in place would not help in any case: what converts a lithium film is the days it then spends in the '
              'beam-line vacuum.</p>'
              '<p>LNL’s targets group (separately from the lithium work) sputters thick films as a speciality: 110–125 µm of Mo on '
              'flat Cu at 11 µm/h, 30–45 µm of Nb inside copper cavities. Both were grown at 500–550 °C on copper. Aluminium '
              '6061-T6 loses its temper above about 200 °C, so on aluminium the coating has to be done cool. The same group '
              'reported in 2015 that it was "depositing lithium by evaporation in a dedicated evaporator", with nothing published '
              'since: a question for Pierfrancesco.</p>',
        short='how Li targets are made')

# ---- the Li thickness finding
LT = {ep: 100 * RV.li_table(ep) for ep in (1100, 1030)}
EO = {ep: RV.li_eout(ep) for ep in (1100, 1030)}
YR = RV.li_yield_rel(1100)
LIC = {20: sd.RED, 15: sd.GOLD, 12: sd.BLUE, 10: sd.GREEN}


def li_plot(ep, w=800, h=300):
    P = sd.Plot(w, h, x=(-0.05, 1.05), y=(0, 100), xlabel='fraction of the Li atoms turned into LiOH',
                ylabel='γ₀ from the 441 keV resonance (%)', margin=(20, 24, 84, 100), title=f'E_p = {ep / 1000:.2f} MeV')
    P.xticks([(c, f'{100 * c:.0f} %') for c in LT[ep].columns])
    P.yticks([(v, f'{v}') for v in (0, 20, 40, 60, 80, 100)])
    P.hline(10, sd.MUT, label='10 %', anchor='start')
    for t in (20, 15, 12, 10):
        ys = [float(LT[ep].loc[t, c]) for c in LT[ep].columns]
        tips = [f'Li {t} µm, {100 * c:.0f} % LiOH, {ep / 1000:.2f} MeV: {y:.1f} % of the γ₀ from the 441 keV resonance. '
                + (f'The beam leaves the film at {EO[ep].loc[t, c]:.0f} keV' if EO[ep].loc[t, c] > 100 else 'The beam stops in the film')
                for c, y in zip(LT[ep].columns, ys)]
        P.line(list(LT[ep].columns), ys, LIC[t], w=4, tips=tips, r=7)
    return P.svg(f'share of γ₀ from the 441 keV resonance against the converted fraction, E_p {ep} keV')


THIN = [(t, lab) for t, lab in (('cap45al400cu', 'the cap, face 0.4 mm'), ('cap45al500cu', 'the cap, face 0.5 mm'),
                                 ('ogCu200_tip', 'Cu ogive, Li on the tip'), ('ogAl400cu12_tip', 'Al ogive, Cu plated, 0.4 mm'),
                                 ('ogAl300cu12_tip', 'Al ogive, Cu plated, 0.3 mm'),
                                 ('win45d200', '45° diamond window (dropped, the cap’s geometry)'))
        if any(nd.has(f'{t}_li{n}') for n in (10, 12, 15))]
if any(t.startswith('cap45') for t, _ in THIN):                 # the cap's own rows replace its stand-in
    THIN = [(t, lab) for t, lab in THIN if t != 'win45d200']
THIN = THIN[:4]
li_rows = [(['γ₀ yield of a fresh film'] + [f'{100 * YR[t]:.0f} %' for t in (20, 15, 12, 10)], '')] + [
    ([f'days, {lab}'] + [RV.fmt3(tag if t == 20 else f'{tag}_li{t}') for t in (20, 15, 12, 10)], sd.tipattr(COLS3)) for tag, lab in THIN]
li20h, li12max = float(LT[1100].loc[20, 0.5]), float(LT[1100].loc[[10, 12]].max().max())
D.slide('lithium', sd.title(f'Half of a 20 µm lithium film turned to hydroxide: {li20h:.0f} % of the γ₀ comes from the 441 keV '
                            f'resonance. At 10–12 µm and 1.10 MeV it stays at or below {li12max:.0f} %',
                            'Residual water turns Li into LiOH: the O and H add stopping, so the beam leaves the film lower. Run at 1.10 MeV, not 1.03') +
        sd.row(li_plot(1100), li_plot(1030), gap=40) +
        sd.legend([(f'Li {t} µm along the beam', LIC[t]) for t in (20, 15, 12, 10)] + [('10 % line', sd.MUT, 'dash')], size=20) +
        table(['', 'Li 20 µm', 'Li 15 µm', 'Li 12 µm', 'Li 10 µm'], li_rows, ['left', 'right', 'right', 'right', 'right'],
              [520, None, None, None, None], size=21) +
        sd.p(f'Days to 3σ at 1 µA, 1.10 MeV: {COLS3}. The conversion rate at LNL’s vacuum is unknown. A one-week film test decides the thickness.',
             18, sd.MUT, extra='margin-top:-16px'),
        notes=f'<p>{RV.LI["headline"]} {RV.LI["fix"]} {RV.LI["rate"]}</p>'
              '<p>What it means: the 441 keV resonance is about 50 times stronger than the 18.15 MeV one. Once the beam reaches it '
              'inside the film, the 17.64 MeV γ-rays and their pairs become most of what the detector sees, the trigger rate rises '
              'several-fold, and the 18.15 MeV signal sits under a background that was not in the design. This is the ATOMKI 2016 '
              'accident by another route. It is a property of the film, not of the shell, so it applies to every design here.</p>'
              '<p>What to do (TARGET_REVIEW.md §4.2): make the film 10–12 µm, which LNL already rolls ("down to sub-10 µm"). Run at '
              '1.10 MeV, not 1.03, for 70 keV more margin. Watch the γ₀ yield per µC, which rises by several times as the beam '
              'reaches 441 keV. Measure the rate before the run with one film on the AN2000 or CN line for a week. Keep the cold '
              'trap upstream, and no PVC next to the target if it can be avoided.</p>'
              '<p>Model: <code>review_li_conversion.py</code> → <code>out/target/options/review_li_conversion.csv</code> (the repo’s '
              'yield model, PSTAR stopping, the outer fraction of the Li atoms converted and the rest metal). With Li₂O instead of '
              'LiOH the effect is much smaller at 1.10 MeV. The thin-film days fold the lower yield and the changed line mix into '
              'the reference fit (<code>nd_reach_thinli.csv</code>). They are shown for the configurations that have rows.</p>',
        short='Li thickness')


# ---- one slide per design
def profile_plot(d, w=720, h=205):
    P = sd.Plot(w, h, x=(0, 6), y=(0.05, 60, 'log'), xlabel='lepton angle to the beam',
                ylabel='x/X₀ per lepton (%)', margin=(30, 20, 76, 96))
    P.yticks([(0.1, '0.1'), (1, '1'), (10, '10')])
    P.xticks([(i + 0.5, f'{b}–{b + 15}°') for i, b in enumerate(BANDS)])
    for i, b in enumerate(BANDS):
        for j, (src, c, nm) in enumerate(((flat, sd.GREY, 'flat design'), (d, d['color'] if d['key'] != 'flat' else sd.INK, d['name']))):
            if d['key'] == 'flat' and j == 0:
                continue
            v = src['prof'][i]
            if not np.isfinite(v):
                continue
            off = 0 if d['key'] == 'flat' else (j - 0.5) * 0.36
            P.vbar(i + 0.5 + off, max(v, 0.05), 38 if d['key'] != 'flat' else 60, c,
                   tip=f'{nm}: {v:.2f} % X₀ (median, {b}–{b + 15}°)' + (', 0: drawn at the floor' if v < 0.05 else ''))
    P.hline(1.4, sd.GOLD)
    return P.svg(f'material per lepton by direction, {d["name"]}')


def cap_trace_plot(w=720, h=200):
    """the review's ray-trace: aluminium for diamond (review_alt_trace.csv)."""
    rows = [('REF diamond window: Mo 8 / diamond 300, 45 deg, Ti rings 0.5 mm, Al end piece 0.5 mm', 'diamond 300', sd.GREY),
            ('one-piece Al cap: Cu 12 / Al 300, 45 deg, Al end piece 0.5 mm', 'Al 0.3', sd.GREEN),
            ('one-piece Al cap: Cu 12 / Al 400, 45 deg, Al end piece 0.5 mm', 'Al 0.4', sd.GREEN),
            ('one-piece Al cap: Cu 12 / Al 500, 45 deg, Al end piece 0.5 mm', 'Al 0.5', sd.GREEN),
            ('one-piece Al cap: Cu 12 / Al 300, 45 deg, Al end piece 0.3 mm', 'end 0.3', sd.BLUE),
            ('one-piece Al cap: Cu 12 / Al 300, 0 deg, Al end piece 0.5 mm', '⊥ beam', sd.GOLD)]
    P = sd.Plot(w, h, x=(0, len(rows)), y=(0, 0.9), xlabel='Al face, mm (ray-trace; end piece 0.5 mm unless said)',
                ylabel='x/X₀ per leg (%)', margin=(30, 10, 76, 96))
    P.yticks([(v, f'{v:g}') for v in (0, 0.2, 0.4, 0.6, 0.8)])
    P.xticks([(i + 0.5, lab) for i, (_, lab, _) in enumerate(rows)])
    for i, (k, lab, c) in enumerate(rows):
        x, ds_ = 100 * float(ALT.loc[k, 'x_med']), float(ALT.loc[k, 'sigma68_minus_ref'])
        P.vbar(i + 0.5, x, 64, c, tip=f'{k}: median {x:.2f} % X₀ per leg, σ68 {ALT.loc[k, "sigma68_est"]:.2f}° in the trace '
                                         f'({ds_:+.1f}° against the diamond window)',
               label='reference' if i == 0 else f'{ds_:+.1f}°'.replace('-', '−'))
    return P.svg('ray-trace: material per leg and the change of σ68 against the diamond window')


def kpi(v, label, color, tip=None, size=38):
    return (f'<div{sd.tipattr(tip)} style="flex:1;border-top:4px solid {color};padding-top:6px">'
            f'<p style="font-size:{size}px;font-weight:600;color:{color};line-height:1.05;white-space:nowrap">{v}</p>'
            f'<p style="font-size:16px;color:{sd.MUT};line-height:1.2">{label}</p></div>')


MATC = {'Li': LI, 'Mo': MO, 'diamond': DIA, 'Cu': CU, 'Ti': TI, 'Al': AL, 'Be': BE, 'CFRP': CF, 'CFRP / PVC': PVC}
for d in DES:
    v, c = d['v'], LVC[d['v']['level']]
    v3 = d['days3']
    st = '*' if d['est'] else ''
    fmt = dict(big=nd.fmt(v3[0]), asb=nd.fmt(v3[1]), asbN=nd.fmt(v3[2]),
               r45=d['days'] / w45['days'], glo=G_ASB[0], ghi=G_ASB[1], blo=G_BIG[0], bhi=G_BIG[1], wall=WALL,
               p300=nd.fmt(nd.best('ogAl300cu12_tip', 'bigP', 1100)), l300=nd.fmt(nd.best('ogAl300cu12r8m4', 'bigP', 1100)),
               epc=sd.pct(d['epc']) if np.isfinite(d['epc']) else '–', sig=d['sigma'] if np.isfinite(d['sigma']) else 0)
    ttl = d['claim'].format(**fmt)
    big = drawing(d['key'], 900, 400 if d['key'] == 'cap' else 470, 6.3, labels=True, cy=218 if d['key'] == 'cap' else None)
    src_s = ('estimate, Geant4 running' if d['est'] else d['status'])
    kp = sd.row(kpi(nd.fmt(v3[0]) + st, H3[0], c, f'days to 3σ at 1 µA, MX17 with the big plastics ({src_s})'),
                kpi(nd.fmt(v3[1]) + st, H3[1], c, f'days to 3σ at 1 µA, the detector as built with the liquid scintillator repaired ({src_s})'),
                kpi(nd.fmt(v3[2]) + st, H3[2], c, f'days to 3σ at 1 µA, the detector as built with the liquid as it ran at n_TOF ({src_s})'),
                kpi(sig_s(d), 'σ68 opening angle', sd.INK, 'Geant4, X17 at 16.8 MeV, big plastics'
                    + (' (* the 45° diamond window’s value, as a stand-in until run L14)' if d['stat_proxy'] else '')),
                kpi(x_s(d), 'X₀ per lepton (trace)', sd.INK, 'median over both legs of the accepted pairs (ray-trace, not Geant4)'), gap=14)
    cap_line = (f'<p style="font-size:17px;color:{sd.MUT}">Days to 3σ at the ATOMKI strength, 1 µA, 1.10 MeV · '
                f'<b style="color:{c if d["est"] else sd.MUT}">{src_s}</b></p>')
    vt = ''
    if d['vrows']:
        vt = table(['variant'] + H3, [([lab] + [nd.fmt(x) for x in RV.days3(t)], '') for lab, t in d['vrows'][:3]],
                   ['left', 'right', 'right', 'right'], [None, 96, 120, 130], size=17, hsize=14, pad='.14em .5em')
    note = f'<p style="font-size:17px;color:{sd.MUT};line-height:1.25">{d["note"].format(**fmt)}</p>' if d.get('note') else ''
    has_prof = any(np.isfinite(x) for x in d['prof'])
    if d['key'] == 'cap':
        fig = sd.col(cap_trace_plot(), sd.p('Number on each bar: the change of σ68 against the diamond window (ray-trace). '
                                            'Aluminium for diamond changes almost nothing a lepton can see.', 16, sd.MUT), gap=2)
    elif has_prof:
        lg_name = 'window 45°, wide adapter' if d['key'] == 'w45wide' else d['name']
        leg2 = sd.legend(([] if d['key'] == 'flat' else [('flat design', sd.GREY, 'box')]) + [(lg_name, d['color'] if d['key'] != 'flat' else sd.INK, 'box'),
                          ('one 200 µm Cu wall, square on (1.4 %)', sd.GOLD, 'dash')], size=16)
        fig = sd.col(profile_plot(d), leg2, gap=2)
    else:
        fig = ''
    pc = ''.join(f'<li style="margin:3px 0">{x.format(**fmt)}</li>' for x in d['pros'])
    cc = ''.join(f'<li style="margin:3px 0">{x.format(**fmt)}</li>' for x in d['cons'])
    lsz = 16 if (has_prof or d['key'] == 'cap') else 19
    lists = sd.row(sd.col(sd.p('<b style="color:#2f8a5b">+</b> for', 20), f'<ul style="font-size:{lsz}px;line-height:1.22;padding-left:20px">{pc}</ul>', gap=2),
                   sd.col(sd.p('<b style="color:#c63d4f">−</b> against', 20), f'<ul style="font-size:{lsz}px;line-height:1.22;padding-left:20px">{cc}</ul>', gap=2), gap=24)
    hdr = (f'<div style="display:flex;flex-direction:column;gap:8px">'
           f'<div style="display:flex;align-items:center;gap:14px">{pill(v, 19, date=True)}'
           f'<p style="font-size:22px;font-weight:600;color:{c}">{reason(v)}</p></div>'
           f'<h2 style="font-size:46px;font-weight:600;line-height:1.1;letter-spacing:-1px">{ttl}</h2>'
           f'<p style="font-size:24px;color:{sd.MUT};line-height:1.25">{d["stack"]}</p></div>')
    body = hdr + (
            sd.row(sd.col(big, sd.legend([(m, MATC[m], 'box') for m in d['mats']] + [('beam', BEAM)], size=18), PS.strip(d), w=900, gap=4),
                   sd.col(sd.col(cap_line, kp, gap=4), vt, note, fig, lists, w=720, gap=10), gap=44)
            if d['key'] != 'cap' else      # the cap: pros and cons under the drawing, which leaves room there
            sd.row(sd.col(big, sd.legend([(m, MATC[m], 'box') for m in d['mats']] + [('beam', BEAM)], size=18), PS.strip(d), lists, w=900, gap=4),
                   sd.col(sd.col(cap_line, kp, gap=4), vt, note, fig, w=720, gap=10), gap=44))
    D.slide(d['key'], body, pad='84px 128px 60px',
            notes=f'<p><b>Review of 11 Nov 2026: {v["label"]}.</b> {v["why"]}</p>' + d['details'] +
            f'<p>The three day numbers are days to 3σ at the ATOMKI strength at 1 µA and 1.10 MeV ({COLS3}), from the reference fit. '
            f'Drawing to scale except the thin layers (thickened so they show).'
            + (' The bar chart is the trace’s median x/X₀ per lepton in 15° bands, against the flat design in grey. The gold line is '
               'one 200 µm Cu wall crossed squarely (1.4 % X₀).' if has_prof else '') + '</p>',
            short=d['short'] + (' (dropped)' if v['level'] == 'drop' else ''))
    if d is LIVE[-1]:
        # ---- the divider: what was dropped, and why
        cards = []
        for k in ('be', 'mo', 'diamond', 'thin_film'):
            vv = RV.verdict(tags_of(k)[0])
            nm = names_of(k)
            cards.append(
                f'<div style="border-left:6px solid {sd.RED};padding-left:20px;display:flex;flex-direction:column;gap:6px">'
                f'<p style="font-size:30px;font-weight:600">{DROPNAME[k]} <span style="font-weight:400;color:{sd.DMUT};font-size:24px">{reason(vv)}</span></p>'
                f'<p style="font-size:22px;color:{sd.DMUT};line-height:1.32">{vv["why"]}</p>'
                f'<p style="font-size:20px;color:{sd.DINK};line-height:1.3">Takes out: {", ".join(nm) if nm else "the ATOMKI-style film on a foil in a chamber (no slide here)"}. '
                f'Days {f3(rng3(tags_of(k)))}.</p></div>')
        D.slide('dropped', sd.kicker('Dropped on 11 Nov 2026 · the next slides are kept as a record') +
                '<h2 style="font-size:58px;font-weight:600;line-height:1.1;letter-spacing:-1px">Beryllium has no supplier, molybdenum '
                'floods the Micromegas with x-rays, the diamond is not needed, thin films break</h2>'
                f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:30px 56px">{"".join(cards)}</div>'
                + sd.p(f'Days to 3σ at 1 µA, 1.10 MeV: {COLS3}, over every simulated design of the family. '
                       'What the dropped designs would gain is on the slide "physics against practicality".', 20, sd.DMUT),
                notes='<p>TARGET_REVIEW.md §4.3 (molybdenum), §4.5 (the diamond), §4.6 (beryllium), §2.1 and §5 (thin films). '
                      'The 45° geometry of the diamond window is the valuable part of that design, and it is kept in the proposed '
                      'aluminium cap. All the beryllium designs and all the diamond windows also carry the molybdenum stop.</p>'
                      '<p>Micromegas occupancy per arm per µA from Mo K x-rays (17.5 keV), with the Geant4 x-ray yield of 4 Nov: '
                      'Al 0.3 mm + Mo about 19 %, the diamond window about 30–45 %, Be + Mo about 29 %. With a working limit of 10 % '
                      'per arm these designs would run at 0.2–0.5 µA, which gives back their advantage.</p>',
                dark=True, short='what was dropped')

PS.slides(D, DES)

# ---- closing: the recommendation
P24 = lambda t: sd.p(t, 25, sd.DINK)          # noqa: E731
P24m = lambda t: sd.p(t, 24, sd.DMUT)         # noqa: E731
D.slide('end', sd.kicker('Recommendation of the 11 Nov review · a proposal, not yet discussed with Pierfrancesco') +
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:34px 72px">'
        + sd.col(sd.p(f'<span style="color:{sd.DGREEN}">Propose</span>', 34, sd.DINK, 600),
                 P24(f'<b>A one-piece aluminium end cap with a flat face at 45°.</b> Al 6061-T6, face 0.4–0.5 mm over a Ø20 bore, '
                     f'Cu ≥ 12 µm along the beam as the stop, 10–12 µm of LNL’s rolled Li pressed on with flat moulds.'),
                 P24(f'<b>{CAP3} d</b> to 3σ at 1 µA ({COLS3})' +
                     ('. An estimate from the 45° diamond window until Geant4 run L14 lands.' if not CAP_G4 else ', Geant4 run L14.')), gap=12)
        + sd.col(sd.p(f'<span style="color:{sd.DBLUE}">If the ogive stays, in this order</span>', 34, sd.DINK, 600),
                 P24(f'1. His <b>Cu ogive</b>, electroformed in hard copper, Li pressed on the tip only: {f3(OGCU3)} d.'),
                 P24(f'2. The <b>Al ogive at 0.4 mm with Cu plated over the whole inside</b>, Li on the tip: {f3(ALCU3)} d'
                     + (' (simulated at 0.3 mm).' if ALCU_W == 300 else '.')),
                 P24m(f'Not now: the Cu patch with masked, evaporated Li ({f3(LINER3)} d). Three steps LNL has not shown, for '
                      f'×{G_ASB[0]:.1f} to ×{G_ASB[1]:.1f} as built. Commission with the Cu cup that exists.'), gap=12)
        + sd.col(sd.p(f'<span style="color:{sd.DRED}">Dropped</span>', 34, sd.DINK, 600),
                 P24m(' '.join(f'<b style="color:{sd.DINK}">{DROPNAME[k]}</b>: {reason(RV.verdict(tags_of(k)[0]))}.'
                               for k in ('be', 'mo', 'diamond', 'thin_film'))),
                 P24m('The lithium: 10–12 µm instead of 20, for every design. A one-week film test at LNL’s vacuum decides.'), gap=12)
        + sd.col(sd.p('Not settled, and what to ask', 34, sd.DINK, 600),
                 P24m('Ask Pierfrancesco: how he means to put the Li on his ogive. Would a flat face at 45° do? Can the workshop turn '
                      '0.4–0.5 mm of aluminium, and who coats 10–15 µm of Cu on it below ~150 °C? What is the vacuum at the target?'),
                 P24m(('Geant4 run L14 (the cap) is running. ' if not CAP_G4 else '') +
                      ('Run L13 (a larger as-built Monte Carlo) is not folded in yet. ' if not L13_IN else '') +
                      'The days are the reference fit with the background shape floating. As built they assume a 0.3 ns arm-to-arm '
                      'time of flight that no measurement backs yet.'), gap=12)
        + '</div>',
        notes='<p>TARGET_REVIEW.md §0 (bottom line), §5 (verdict by design), §6 (better ideas) and §7 (what to ask Pierfrancesco). '
              'The questions in full: (1) How does he intend to put the lithium on his ogive: pressed foil with new moulds for the '
              'pointed tip, or evaporation? Does the 2015 evaporator exist and work today? (2) We do not need anything deposited in '
              'the beam pipe. We meant a coating chamber. Would he rather have a part on which his rolled-and-pressed lithium works '
              'directly? (3) Would he consider a flat face at 45° instead of the point? (4) Can the LNL workshop turn a 0.4–0.5 mm '
              'aluminium wall, and can the targets group put 10–15 µm of copper on a flat aluminium face below about 150 °C, or '
              'would a plating shop do it? (5) The vacuum at the target, and whether a film can sit there for a week under beam '
              'while we watch the 478 keV and γ₀ lines. (6) How thin can a rolled foil be made reproducibly (we would like '
              '8–12 µm), and how is it carried from the glovebox to the line? (7) The beam spot at the target.</p>'
              f'<p>{nd.ASB_NOTE} The other systematics of FEASIBILITY_SIM §19 (EPC and cosmic Monte Carlo, timing) are not in the days.</p>',
        dark=True, short='recommendation')

D.write(OUTF, note_meta=dict(title='LNL target designs compared',
                             summary=f'{NUM.get(len(DES), len(DES)).capitalize()} MX17 target designs for LNL side by side, revised after the '
                                     'buildability review of 11 Nov 2026: the proposed flat aluminium end cap at 45°, the fallback '
                                     'order, what was dropped and why, with drawings and the days to 3σ for three detector states.',
                             tags='x17, lnl, target', date='2026-10-27'))
print(OUTF)
