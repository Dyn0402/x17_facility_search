"""Build the slide note comparing every LNL target design on the table (2026-10-27).

One overview slide (a drawing of each design + the headline numbers), then one slide per design.
Reads the Geant4 L9/L10 summaries (lnl/out/target/shapes/) and the ray-trace of opt_sketch.py
(lnl/out/target/options/sketch_*.csv); writes lnl/out/target/lnl-target-compare.html:

    ~/PycharmProjects/nTof_x17/.venv/bin/python lnl/target/opt_sketch.py          # trace (if changed)
    ~/PycharmProjects/nTof_x17/.venv/bin/python lnl/target/deck/build_compare_deck.py
    python3 ~/PycharmProjects/dylan-cern-site/scripts/add-note.py \\
        lnl/out/target/lnl-target-compare.html --slug lnl-target-compare --force --deploy
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

GR = pd.read_csv(SH / 'geant_reach.csv')
GA = pd.read_csv(SH / 'geant_acceptance.csv')
TR = pd.read_csv(OP / 'sketch_trace.csv').set_index('config')
TP = pd.read_csv(OP / 'sketch_theta_profile.csv')

CU, DIA, MO, TI, LI, AL, PVC, CF, BE = sd.GOLD, sd.PURPLE, sd.GREY, '#3f8f9b', sd.BLUE, sd.ORANGE, '#9aa0a6', '#4a4f5a', sd.GREEN
BEAM = sd.RED


def g4(cfg, col='days_fit', ep=1100.0, det='bigP'):
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


BANDS = [45, 60, 75, 90, 105, 120]
T_FLAT = 'design (flat Li/Mo 8/diamond 50, CFRP chamber)'

# --------------------------------------------------------------------------- #
# the designs.  Numbers come from the files above; the §4.1 diagnostic (window on a wide adapter) has no CSV and is
# quoted from SHAPES_GEANT.md §4.1 (X17-only Geant4 runs; days from the σ68 → days relation of the full runs).
DES = [
    dict(key='flat', name='Flat target in a chamber', sub='our first design (L9)', g4='li20_mo8_dia50', trace=T_FLAT,
         status='Geant4 L9', color=sd.INK,
         stack='Li 20 / Mo 8 / diamond 50 µm, ⊥ beam, Cu holder ring, inside a CFRP chamber',
         claim='Flat target in a chamber: the benchmark at {days} d/µA', mats=['Li', 'Mo', 'diamond', 'Cu', 'CFRP'],
         pros=['best measured reach of everything simulated', 'the target is not the vacuum wall: a crack does not vent the line',
               'film and stack fully characterised (thermal model, L9)'],
         cons=['needs a thin CFRP chamber around the target (Pierfrancesco wants none)',
               'Cu holder ring edge-on to the 75–90° legs (the tall bar)', 'heat leaves through a Cu arm to the chamber flange'],
         details='<p>Geant4 run L9 (<code>li20_mo8_dia50</code>), big plastics, 1.10 MeV. The film is perpendicular to the beam '
                 'inside a CFRP chamber (0.4 mm, r 25 mm). This is "our perpendicular design".</p>'
                 '<p>On 24 Oct Pierfrancesco proposed making the target the end of the beam pipe, with no chamber. The diamond window '
                 'is this same stack turned into that end wall. Sources: TARGET_OPTIONS §7, §14–16; SHAPES_GEANT.md §0.</p>'),
    dict(key='w45', name='Diamond window, 45°', sub='on its Ø20 Al end piece (L10)', g4='win45d200',
         trace='our window: Ø20, 45°, diamond 200, Ti rings, Al end 0.5', status='Geant4 L10', color=sd.BLUE,
         stack='Li 14 / Mo 8 / diamond 200 µm, Ø20 in 0.5 mm Ti rings, tilted 45°, on a 55 mm Al end piece (0.5 mm)',
         claim='45° window: {days} d/µA, and its Al end piece costs most of that', mats=['Li', 'Mo', 'diamond', 'Ti', 'Al', 'CFRP / PVC'],
         pros=['no chamber: the window is the end of the vacuum', 'safe at 1 bar (Ø20, 200–300 µm diamond)',
               'tilting moves the rings out of the 90° plane; spreads the spot ×√2'],
         cons=['the 0.5 mm Al end piece is grazed by legs at 90–140° (σ68 9.1° vs 6.2° without it)',
               'Mo K x-rays (17.5 keV) through the diamond: 16 % MM occupancy per arm per µA (est.)',
               'window = beam stop = vacuum wall: blistering or a crack vents the line (fast valve)'],
         details='<p>Geant4 run L10 (<code>win45d200</code>), big plastics, 1.10 MeV. 300 µm diamond: 0.28 d/µA. At 1.03 MeV the '
                 'reach is 15–18 % slower. Sources: SHAPES_GEANT.md §0, §4, §7.</p>'),
    dict(key='w45wide', name='Diamond window, 45°', sub='on a wide, short adapter', g4=None,
         trace='our window 45° on a wide adapter (no Ø20 end piece)', status='L10 diagnostic', color=sd.GREEN,
         days_q=0.21, sigma_q=6.2, acc_q=0.154,
         stack='the same window, with the Ø20 tube replaced by an adapter that opens wide within a few mm',
         claim='45° window on a wide adapter: {days} d/µA, as good as the chamber', mats=['Li', 'Mo', 'diamond', 'Ti', 'Al'],
         pros=['the bare window scatters less than the flat design (5.7° vs 6.6°)', 'keeps every advantage of the window',
               'the tube that carried it is out of the leptons’ view'],
         cons=['the adapter is not designed yet: conical or stepped Al/CFRP, Ø20 → ≥ Ø60 within a few mm',
               'only an X17-only Geant4 diagnostic so far (no full background run)', 'Mo K x-rays as for the window'],
         details='<p>Geant4 diagnostic runs (X17 only, big plastics), SHAPES_GEANT.md §4.1: "no end piece" gives σ68 6.2° '
                 '(acceptance 0.154). Read off the σ68 → days relation of the full runs, that is ≈ 0.21 d/µA. The bare window '
                 '(no rings, no line) gives 5.7°. The days are an estimate until a full run with a real adapter.</p>'
                 '<p>The trace has no adapter at all, so legs going upstream (90–135°) cross nothing and their bars are at the floor. '
                 'A real adapter wall will add something there; how much depends on its shape.</p>'),
    dict(key='w0', name='Diamond window, 0°', sub='perpendicular, Ø20 end piece (L10)', g4='win0d200',
         trace='our window 0°: Ø20, diamond 200, Ti rings, Al end 0.5', status='Geant4 L10', color=sd.PURPLE,
         stack='Li 20 / Mo 8 / diamond 200 µm, Ø20 in 0.5 mm Ti rings, ⊥ beam, on the 55 mm Al end piece',
         claim='0° window: {days} d/µA, ×{r45:.2f} slower than at 45°', mats=['Li', 'Mo', 'diamond', 'Ti', 'Al', 'CFRP / PVC'],
         pros=['simplest to build and to align', 'the same window and rings as the 45° design'],
         cons=['the Ti rings lie in the plane of the 90° leptons and are crossed edge-on',
               'twice the external conversion of the 45° window (EPC {epc} of the background)',
               'Mo margin at 1.10 MeV without Li: 7.5 of 8 µm'],
         details='<p>Geant4 run L10 (<code>win0d200</code>), big plastics, 1.10 MeV. 300 µm: 0.41 d/µA. The flat chamber design is '
                 'also perpendicular, but its film sits in the middle of a wide chamber, with no rings or tube nearby. The 0° window '
                 'has its rings and end piece right next to the film. Sources: SHAPES_GEANT.md §0, §4; TARGET_OPTIONS §17 '
                 '(why the tilt helps).</p>'),
    dict(key='hemi', name='Cu hemisphere', sub='Pierfrancesco’s cup (L10)', g4='dome200',
         trace='L10 hemisphere without its flange (rim only)', status='Geant4 L10', color=CU,
         stack='Li 20 µm inside a 200 µm Cu hemisphere, R 11, Cu rim 4 × 5 mm, on the grey flange',
         claim='Cu hemisphere: {days} d/µA, ×{rflat:.0f} slower than the flat target', mats=['Li', 'Cu', 'CFRP / PVC'],
         pros=['already built and used (CN paper)', 'the Cu stops the beam and absorbs its own x-rays', 'easy to cool with air'],
         cons=['every lepton crosses Cu, and legs near 90° graze it (≈ 7 % X₀)',
               'converts the ⁸Be γ: EPC is {epc} of the background', 'σ68 {sig:.0f}°: the opening-angle edge washes out'],
         details='<p>Geant4 run L10 (<code>dome200</code>), big plastics, 1.10 MeV. 300 µm (the CN-paper value): 3.4 d/µA. R 17.5 '
                 'glued on the DN40 tube: 1.7 d/µA. Sources: SHAPES_GEANT.md §0, §4.</p>'),
    dict(key='ogcu', name='Cu ogive', sub='Pierfrancesco’s CAD sketch, 27 Oct', g4=None,
         trace='sketch A: Cu ogive 200 µm, Ø50 × 63 mm, bare base', status='trace only', color=sd.ORANGE,
         stack='Li 20 µm inside a pointed 200 µm Cu shell, Ø50 × 63 mm, tip R 3; mount not drawn',
         claim='Cu ogive (his sketch): better than the hemisphere, still Cu', mats=['Li', 'Cu'],
         pros=['steep walls everywhere: 90° legs cross ≈ 1.1× the wall, not 10×', 'no flange in the arms’ view (base 63 mm back)',
               'large area for air cooling'],
         cons=['still ≥ 1.4 % X₀ of Cu on every lepton (median {xmed:.1f} %)',
               'the beam spot spills onto the 65° flank: 2.4× the Li along the path; at 1.03 MeV, 42 % of protons cross 441 keV',
               'the trace under-reads Cu shells (hemisphere: 12.6° traced, 22° in Geant4)'],
         details='<p>Ray-trace only (<code>opt_sketch.py</code>, TARGET_OPTIONS §19): exact solids from the STEP file, Cu assumed. '
                 'No days are quoted: the trace is calibrated on flat targets and leaves out EPC. Expect it between the window and '
                 'the hemisphere. Next: a G4Polycone shell in <code>lnl_shapes</code>.</p>'),
    dict(key='ogbe', name='Be ogive', sub='same shape, Be 200 µm + Mo liner', g4=None,
         trace='sketch A in Be 200 µm (no Mo liner)', status='trace only', color=BE,
         stack='the sketch’s shell in Be 200 µm, with an 8 µm Mo liner as the beam stop (liner not traced)',
         claim='Be ogive: the cleanest target traced, {xmed:.2f} % X₀ per lepton', mats=['Li', 'Be'],
         pros=['×25 less material per lepton than in Cu', 'no chamber, no tube in view', 'keeps the shell idea Pierfrancesco prefers'],
         cons=['Be machining and handling (toxic dust); a thin Be shell is a specialist part',
               'needs a Mo liner (Li alloys with Al; Be takes up H)', 'the same 441 keV issue on the flank as the Cu ogive'],
         details='<p>Ray-trace only (<code>opt_sketch.py</code>). An 8 µm Mo liner adds ≈ 0.08 % X₀ at normal incidence; it is not '
                 'included. An Al 200 µm shell traces at 0.46 %. Sources: TARGET_OPTIONS §17, §19.</p>'),
]

for d in DES:
    if d['g4']:
        d['days'], d['sigma'], d['acc'] = g4(d['g4']), acc(d['g4']), acc(d['g4'], 'acc')
        d['days03'] = g4(d['g4'], ep=1030.0)
        d['epc'] = g4(d['g4'], 'B_epc_share')
    else:
        d['days'], d['sigma'], d['acc'] = d.get('days_q', np.nan), d.get('sigma_q', np.nan), d.get('acc_q', np.nan)
        d['days03'] = d['epc'] = np.nan
    d['xmed'] = tr(d['trace'])
    d['conv'] = tr(d['trace'], 'p_conv_18MeV')
    d['prof'] = prof(d['trace'])
BYK = {d['key']: d for d in DES}


def fdays(d):
    if not np.isfinite(d['days']):
        return 'Geant4 pending'
    return ('≈ ' if not d['g4'] else '') + f'{d["days"]:.3g}'


def dcol(v):
    return sd.GREY if not np.isfinite(v) else sd.GREEN if v <= 0.25 else sd.GOLD if v <= 0.45 else sd.RED


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

    def lab(y, r, text, anchor='start', color=sd.INK):
        if labels:
            x, yy = P(y, r)
            out.append(sd.T(x, yy, text, 21, color, anchor))

    # beam
    xa, _ = P(y0 + 2, 0)
    stop = {'flat': -0.4, 'hemi': -0.3, 'ogcu': -0.3, 'ogbe': -0.3}.get(key, -1.0)
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
    elif key in ('w45', 'w45wide', 'w0'):
        th = np.radians(0 if key == 'w0' else 45)
        e = 1.0 if labels else 2.0
        tilted(-0.8 * e, 0, 0, 10, th, LI, 'Li (drawn thick)')
        tilted(0, 0.5 * e, 0, 15, th, MO, 'Mo 8 µm: the beam stop (drawn thick)')
        tilted(0.5 * e, 2.0 * e, 0, 15, th, DIA, 'CVD diamond 200 µm: the vacuum wall (drawn thick)')
        tilted(-0.8 * e - 0.8, -0.8 * e, 10, 15, th, TI, 'Ti ring 0.5 × 5 mm + 0.1 mm epoxy')
        tilted(2.0 * e, 2.0 * e + 0.8, 10, 15, th, TI, 'Ti ring 0.5 × 5 mm')
        if key != 'w45wide':
            # the end piece is cut on the window plane, so its length differs on the two sides of a tilted window
            y_lo = (-0.8 * e - 0.8 + 10.5 * np.sin(th)) / np.cos(th)
            y_hi = (-0.8 * e - 0.8 - 10.5 * np.sin(th)) / np.cos(th)
            for r_sign, ycut in ((1, y_hi), (-1, y_lo)):
                x0, _ = P(-55, 0)
                x1, _ = P(ycut, 0)
                _, yt = P(0, 10.5 if r_sign > 0 else -10)
                out.append(f'<rect x="{x0:.1f}" y="{yt:.1f}" width="{x1 - x0:.1f}" height="{max(0.5 * s, mn):.1f}" fill="{AL}" '
                           f'opacity=".85"{sd.tipattr("Al end piece 0.5 mm, 55 mm long, cut on the window plane (drawn thick)")}/>')
            rect(-66, -55, 15, 33, PVC, 'grey flange r 15–33 mm (PVC assumed)', .7)
            lab(-50, 12.5, 'Al end piece 0.5 × 55 mm')
            lab(-64, 35, 'grey flange')
        else:
            for sg in (1, -1):
                xs = [P(-1.5, sg * 15.5), P(-9, sg * 34)]
                out.append(sd.line(xs[0][0], xs[0][1], xs[1][0], xs[1][1], AL, 3 if labels else 2, '8 6'))
            lab(-30, 30, 'wide adapter (to design)', color=AL)
        lab(4, 16, 'Mo 8 / diamond 200 µm', 'start')
        lab(4, 11, 'Ti rings', 'start', TI)
    elif key == 'hemi':
        R, t = 11.0, (0.6 if labels else 1.0)
        ths = np.linspace(-np.pi / 2, np.pi / 2, 80)
        xo = [P(-R + (R + t) * np.cos(a), (R + t) * np.sin(a)) for a in ths]
        xi = [P(-R + R * np.cos(a), R * np.sin(a)) for a in ths[::-1]]
        out.append(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in xo + xi)}" fill="{CU}" opacity=".95"'
                   f'{sd.tipattr("Cu hemisphere R 11 mm, 200 µm (drawn thick)")}/>')
        li = [P(-R + (R - 0.4) * np.cos(a), (R - 0.4) * np.sin(a)) for a in np.linspace(-0.5, 0.5, 20)]
        out.append(sd.poly([x for x, _ in li], [y for _, y in li], LI, w=5 if labels else 3, tip='Li 20 µm where the spot lands'))
        rect(-R - 5, -R, R, R + 4, CU, 'Cu rim 4 × 5 mm')
        rect(-27, -16, 15, 33, PVC, 'grey flange r 15–33 mm (PVC assumed)', .7)
        rect(y0 + 4, -27, 21, 24, PVC, 'grey tube r 21–24 mm', .7)
        lab(1.5, 9, 'Cu 200 µm, R 11')
        lab(-12, 17, 'Cu rim')
        lab(-26, 35, 'grey flange')
    elif key in ('ogcu', 'ogbe'):
        import opt_sketch as OS
        pr = OS.profiles()
        dy = OS.Y_SHIFT
        color = CU if key == 'ogcu' else BE
        for sg in (1, -1):
            po = [P(y + dy, sg * r) for r, y in pr['ogive_out']]
            pi = [P(y + dy, sg * r) for r, y in pr['ogive_in']][::-1]
            # the 0.2 mm wall is drawn as a thick outline
            out.append(sd.poly([x for x, _ in po], [y for _, y in po], color, w=5 if labels else 3.2,
                               tip=('Cu' if key == 'ogcu' else 'Be') + ' shell 0.2 mm (drawn thick): Ø50 × 63 mm, tip R 3'))
        out.append(f'<circle cx="{P(-0.4, 0)[0]:.1f}" cy="{cy:.1f}" r="{max(2.8 * s * .35, 3):.1f}" fill="{LI}"'
                   f'{sd.tipattr("Li 20 µm inside the tip, where the beam lands")}/>')
        rect(-64.5, -63.2, 25, 31, PVC, 'mount: not drawn in the sketch (ask)', .35)
        lab(-40, 23, 'Cu 200 µm' if key == 'ogcu' else 'Be 200 µm + Mo liner')
        lab(-62, 33, 'mount?', color=sd.MUT)
    return sd.svg(W, H, ''.join(out), f'cross-section of {key}')


# --------------------------------------------------------------------------- #
D = sd.Deck('LNL target designs compared',
            'Every MX17 target design for LNL side by side: the flat target in a chamber, the diamond window at 45° and 0°, '
            'Pierfrancesco’s Cu hemisphere and his new pointed shell, with the Geant4 reach and the material each puts on the leptons.')

w45, flat, hemi, w0, wide = BYK['w45'], BYK['flat'], BYK['hemi'], BYK['w0'], BYK['w45wide']

# ---- cover
D.slide('cover', sd.kicker('MX17 at LNL · target designs · 27 Oct 2026') +
        f'<h1 style="font-size:76px;line-height:1.08;font-weight:600;max-width:1600px">The diamond window wins once its tube is out of '
        f'the way; the metal shells only work in Be</h1>' +
        sd.row(sd.bignum('7', 'designs compared', sd.DBLUE, 'flat in a chamber · window 45°, 45° wide, 0° · Cu hemisphere · Cu and Be ogive'),
               sd.bignum('5', 'simulated in Geant4', sd.DGREEN, 'runs L9 and L10, MX17 arms with the big plastics, 1.10 MeV'),
               sd.bignum('2', 'traced only', sd.DGREY, 'Pierfrancesco’s 27 Oct sketch: Geant4 still to do'), gap=56),
        notes='<p>Days are days of beam per µA to reach 3σ at the ATOMKI strength (R = 5.8 × 10⁻⁶, statistics only, '
              'Asimov fit in θ × |y| × n_down), MX17 with the big plastics, E_p = 1.10 MeV. Time scales as 1/current.</p>'
              '<p>"Material per lepton" is the median x/X₀ crossed by an X17 lepton on its way to the arms, from one ray-trace '
              'applied to every design in the same way (<code>opt_sketch.py</code>). It ranks the designs; it is not Geant4.</p>',
        dark=True, short='cover')

# ---- overview
def mini(d):
    tag = {'Geant4 L9': sd.GREEN, 'Geant4 L10': sd.GREEN, 'L10 diagnostic': sd.GOLD, 'trace only': sd.GREY}[d['status']]
    days = fdays(d)
    dsz = 44 if np.isfinite(d['days']) else 24
    sig = f'{d["sigma"]:.1f}°' if np.isfinite(d['sigma']) else '—'
    epc = sd.pct(d['epc']) if np.isfinite(d['epc']) else '—'
    tip_days = (f'{d["days"]:.3f} d per µA (Geant4, big plastics, 1.10 MeV)' + (f'; 1.03 MeV: {d["days03"]:.2f}' if np.isfinite(d['days03']) else '')
                if d['g4'] else 'SHAPES_GEANT §4.1: X17-only diagnostic, σ68 → days relation' if np.isfinite(d['days']) else
                'not simulated in Geant4 yet')
    rows = [('days per µA', f'<span style="font-size:{dsz}px;font-weight:600;color:{dcol(d["days"])}"{sd.tipattr(tip_days)}>{days}</span>'),
            ('σ68 opening angle', sig), ('material per lepton', f'{d["xmed"]:.2f} %'), ('bkg from γ converting', epc)]
    body = ''.join(f'<div style="display:flex;flex-direction:column;gap:2px;border-top:1px solid {sd.RULE};padding-top:8px">'
                   f'<p style="font-size:17px;color:{sd.MUT}">{a}</p><p style="font-size:26px;font-weight:600">{b}</p></div>'
                   for a, b in rows)
    return (f'<div style="width:220px;display:flex;flex-direction:column;gap:10px;background:{sd.CARD};border:1px solid {sd.RULE};'
            f'border-top:6px solid {d["color"]};border-radius:14px;padding:16px 14px">'
            f'<p style="font-size:22px;font-weight:600;line-height:1.15;min-height:52px">{d["name"]}</p>'
            f'<p style="font-size:16px;color:{sd.MUT};line-height:1.2;min-height:40px">{d["sub"]}</p>'
            + drawing(d['key'], 192, 150, 1.95) +
            f'<p style="font-size:15px;font-weight:600;color:{tag}">● {d["status"]}</p>' + body + '</div>')


D.slide('overview', sd.title(f'Seven designs: the window on a wide adapter and the flat target lead, the Cu shells trail ×{hemi["days"] / flat["days"]:.0f}',
                             'Days per µA to 3σ at ATOMKI (big plastics, 1.10 MeV); green ≤ 0.25, gold ≤ 0.45, red > 1') +
        f'<div style="display:flex;gap:20px">{"".join(mini(d) for d in DES)}</div>',
        notes='<table><tr><th>design</th><th>days/µA 1.10 MeV</th><th>1.03 MeV</th><th>σ68</th><th>X17 acceptance</th>'
              '<th>median x/X₀ per leg (trace)</th><th>18 MeV γ conversion (trace)</th><th>EPC share of background</th><th>source</th></tr>'
              + ''.join(f'<tr><td>{d["name"]}, {d["sub"]}</td><td>{fdays(d)}</td><td>{d["days03"]:.2f}</td><td>{d["sigma"]:.1f}°</td>'
                        f'<td>{d["acc"]:.3f}</td><td>{d["xmed"]:.2f} %</td><td>{100 * d["conv"]:.1f} %</td><td>{sd.pct(d["epc"]) if np.isfinite(d["epc"]) else "—"}</td>'
                        f'<td>{d["status"]}</td></tr>' for d in DES).replace('>nan<', '>—<').replace('>nan°<', '>—<') +
              '</table><p>The EPC share is the fraction of the selected background made by ⁸Be γ converting in the material '
              '(Geant4). The trace columns use one ray-trace on the 65 508 accepted X17 pairs of L9 for every design. For the 0° '
              'window and the hemisphere the trace is lower than Geant4 suggests: Cu shells were under-read by ×1.5 in σ68.</p>',
        short='overview')


# ---- one slide per design
def profile_plot(d, w=720, h=330):
    P = sd.Plot(w, h, x=(0, 6), y=(0.05, 60, 'log'), xlabel='lepton angle to the beam',
                ylabel='x/X₀ per lepton (%)', margin=(20, 20, 80, 96))
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
                   tip=f'{nm}: {v:.2f} % X₀ (median, {b}–{b + 15}°)' + (' — 0: drawn at the floor' if v < 0.05 else ''))
    P.hline(1.4, sd.GOLD)
    return P.svg(f'material per lepton by direction, {d["name"]}')


def kpi(v, label, color, tip=None):
    return (f'<div{sd.tipattr(tip)} style="flex:1;border-top:4px solid {color};padding-top:10px">'
            f'<p style="font-size:{44 if len(v) < 9 else 30}px;font-weight:600;color:{color};line-height:1.05">{v}</p>'
            f'<p style="font-size:20px;color:{sd.MUT};line-height:1.25">{label}</p></div>')


for d in DES:
    fmt = dict(days=fdays(d), r45=d['days'] / w45['days'] if d['g4'] else 0, rflat=d['days'] / flat['days'] if d['g4'] else 0,
               epc=sd.pct(d['epc']) if np.isfinite(d['epc']) else '—', sig=d['sigma'] if np.isfinite(d['sigma']) else 0,
               xmed=d['xmed'])
    ttl = d['claim'].format(**fmt)
    big = drawing(d['key'], 900, 540, 6.9, labels=True)
    sig = f'{d["sigma"]:.1f}°' if np.isfinite(d['sigma']) else '—'
    kp = sd.row(kpi(fdays(d), f'days per µA to 3σ ({d["status"]})', dcol(d['days'])),
                kpi(sig, 'σ68 opening angle', sd.INK, 'Geant4, X17 at 16.8 MeV, big plastics'),
                kpi(f'{d["xmed"]:.2f} %', 'X₀ per lepton (trace)', sd.INK, 'median over both legs of the accepted pairs'), gap=24)
    MATC = {'Li': LI, 'Mo': MO, 'diamond': DIA, 'Cu': CU, 'Ti': TI, 'Al': AL, 'Be': BE, 'CFRP': CF, 'CFRP / PVC': PVC}
    pc = ''.join(f'<li style="margin:4px 0">{x.format(**fmt)}</li>' for x in d['pros'])
    cc = ''.join(f'<li style="margin:4px 0">{x.format(**fmt)}</li>' for x in d['cons'])
    lists = sd.row(sd.col(sd.p('<b style="color:#2f8a5b">+</b> for', 22), f'<ul style="font-size:19px;line-height:1.25;padding-left:22px">{pc}</ul>', gap=4),
                   sd.col(sd.p('<b style="color:#c63d4f">−</b> against', 22), f'<ul style="font-size:19px;line-height:1.25;padding-left:22px">{cc}</ul>', gap=4), gap=28)
    hdr = (f'<div style="display:flex;flex-direction:column;gap:10px"><h2 style="font-size:52px;font-weight:600;line-height:1.1;'
           f'letter-spacing:-1px">{ttl}</h2><p style="font-size:28px;color:{sd.MUT}">{d["stack"]}</p></div>')
    lg_name = 'window 45°, wide adapter' if d['key'] == 'w45wide' else d['name']
    leg2 = sd.legend(([] if d['key'] == 'flat' else [('flat design', sd.GREY, 'box')]) + [(lg_name, d['color'] if d['key'] != 'flat' else sd.INK, 'box'),
                      ('one 200 µm Cu wall, square on (1.4 %)', sd.GOLD, 'dash')], size=18)
    body = (hdr +
            sd.row(sd.col(big, sd.legend([(m, MATC[m], 'box') for m in d['mats']] + [('beam', BEAM)], size=19), w=900, gap=6),
                   sd.col(kp, sd.col(profile_plot(d), leg2, gap=2), lists, w=720, gap=12), gap=44))
    D.slide(d['key'], body, notes=d['details'] +
            f'<p>Drawing to scale except the thin layers (thickened so they show). The bar chart is the trace’s median x/X₀ per lepton '
            f'in 15° bands, against the flat design in grey; the gold line is one 200 µm Cu wall crossed squarely (1.4 % X₀).</p>',
            short=d['name'] + (' (wide)' if d['key'] == 'w45wide' else ''))

# ---- closing
D.slide('end', sd.kicker('Decisions and what this does not settle') +
        sd.row(sd.col(sd.p('Decide', 34, sd.DINK, 600),
                      sd.p(f'Build the 45° window on a <b>wide, short adapter</b>: ≈ {wide["days"]:.2f} d/µA, no chamber, safe at 1 bar.', 28, sd.DINK),
                      sd.p(f'If Pierfrancesco keeps the shell: <b>Be or Al + Mo</b>, never Cu ({hemi["days"]:.1f} d/µA in Geant4 for the Cu hemisphere).', 28, sd.DINK),
                      sd.p(f'Perpendicular only in a chamber ({flat["days"]:.2f}); as a window, tilt it (0° costs ×{w0["days"] / w45["days"]:.2f}).', 28, sd.DINK), gap=22),
               sd.col(sd.p('Not settled', 34, sd.DINK, 600),
                      sd.p('The adapter and both ogives need Geant4 runs. Their numbers here are a diagnostic and a trace.', 26, sd.DMUT),
                      sd.p('The ogive’s flank sees 2.4× the Li, so the 441 keV resonance enters. Spot size and Li on the flank are unknown.', 26, sd.DMUT),
                      sd.p('Window: Mo K x-rays in the MM, and H blistering of the Mo stop. Both need a bench test.', 26, sd.DMUT),
                      sd.p('Reach is statistics only, at R(ATOMKI); no systematics.', 26, sd.DMUT), gap=22), gap=80),
        dark=True, short='decisions')

D.write(OUTF, note_meta=dict(title='LNL target designs compared',
                             summary='Seven MX17 target designs for LNL side by side: drawings, Geant4 days per µA, opening-angle '
                                     'resolution and the material on each lepton; one slide per design.',
                             tags='x17, lnl, target', date='2026-10-27'))
print(OUTF)
