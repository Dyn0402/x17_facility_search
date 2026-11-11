"""Slide note: Pierfrancesco's ogive in Al with a Cu liner where the beam stops (CU_LINER.md, 2026-11-04).

Brought up to date with the buildability review of 2026-11-11 (TARGET_REVIEW.md, review_data.py): a dated status
slide and the proposed flat Al end cap at the front, the Li-thickness finding, a corrected "how to make it", a new
bottom line and the questions of TARGET_REVIEW.md §7.  The 4 Nov design stays as the record.  Every day count and
every ratio comes from nd_reach_io / review_data, so a rebuild picks up runs L13 and L14.

Reads lnl/out/target/options/culiner_*.csv (opt_cu_liner.py), pixe_testem5.csv and the Geant4 L11/L12 summaries
(days: lnl/target/shapes/nd_reach_io.py, the reference fit; EPC shares and σ68: geant_reach.csv, geant_acceptance.csv); writes lnl/out/target/lnl-cu-liner.html:

    ~/PycharmProjects/nTof_x17/.venv/bin/python lnl/target/deck/build_culiner_deck.py
    python3 ~/PycharmProjects/dylan-cern-site/scripts/add-note.py lnl/out/target/lnl-cu-liner.html \\
        --slug lnl-cu-liner --force --deploy
"""
import math
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.expanduser(os.environ.get('SLIDEDOC_DIR', '~/PycharmProjects/dylan-cern-site/scripts')))
import slidedoc as sd  # noqa: E402

HERE = Path(__file__).resolve().parent
LNL = HERE.parents[1]
SH = LNL / 'out' / 'target' / 'shapes'
OP = LNL / 'out' / 'target' / 'options'
OUTF = LNL / 'out' / 'target' / 'lnl-cu-liner.html'
sys.path.insert(0, str(LNL / 'target'))
import opt_cu_liner as CL  # noqa: E402
import review_data as rd  # noqa: E402
sys.path.insert(0, str(LNL / 'target' / 'shapes'))
import nd_reach_io as nd  # noqa: E402

GR = pd.read_csv(SH / 'geant_reach.csv')
GA = pd.read_csv(SH / 'geant_acceptance.csv')
PROF = pd.read_csv(OP / 'culiner_profile.csv')
LIMIX = pd.read_csv(OP / 'culiner_li_mix.csv')
CU, AL, LI, BEAM, MO, TI = sd.GOLD, '#8a96a8', sd.BLUE, sd.RED, sd.GREY, '#3f8f9b'


def g4(cfg, ep=1100.0, col='days_fit'):
    if col == 'days_fit':     # days: the reference fit (nd_reach.csv); other columns from geant_reach.csv
        return nd.best(cfg, 'bigP', ep)
    q = GR[(GR.config == cfg) & (GR.det == 'bigP') & (GR.Ep_keV == ep)]
    return float(q[col].iloc[0]) if len(q) else np.nan


def sig(cfg):
    q = GA[(GA.config == cfg + '_bigP') & (GA['sample'] == 'x17')]
    return float(q.sigma68_deg.iloc[0]) if len(q) else np.nan


DES = [  # label, reach config, σ config, colour, MM occupancy per arm per µA (Geant4 L12 libraries / calibrated model)
    ('his Cu ogive 200 µm', 'ogCu200_los', 'ogCu200', sd.RED, 0.001),
    ('Al 300 + Mo 8', 'ogAl300mo8_los', 'ogAl300mo8', MO, 0.19),
    ('Al 300 + Cu 12, Li r ≤ 4', 'ogAl300cu12r8m4', 'ogAl300cu12r8m4', CU, 0.12),
    ('Al 400 + Cu 12, Li r ≤ 4', 'ogAl400cu12r8m4', 'ogAl400cu12r8m4', sd.GREEN, 0.025),
    ('Al 300 + Cu 30, Li r ≤ 4', 'ogAl300cu30r8m4', 'ogAl300cu30r8m4', sd.ORANGE, 0.05),
    ('Al 300 + Ti 15, Li r ≤ 4', 'ogAl300ti15r8m4', 'ogAl300ti15r8m4', TI, 0.0),
    ('Be 300 + Mo 8', 'ogBe300mo8_los', 'ogBe300mo8', sd.PURPLE, 0.35),
]
for i, d in enumerate(DES):
    DES[i] = dict(name=d[0], days=g4(d[1]), days103=g4(d[1], 1030.0), sigma=sig(d[2]), color=d[3], occ=d[4],
                  epc=g4(d[1], col='B_epc_share'), cfg=d[1])
BY = {d['name']: d for d in DES}
CUOG, ALCU, AL4 = BY['his Cu ogive 200 µm'], BY['Al 300 + Cu 12, Li r ≤ 4'], BY['Al 400 + Cu 12, Li r ≤ 4']


def best_days(d, cap=0.10, imax=1.0, live=0.97):
    """days at the best allowed current: ≤ imax (1 µA documented at 1.0–1.1 MeV; 4 µA only if LNL allows it, ask)
    and ≤ cap MM x-ray occupancy per arm"""
    I = imax if d['occ'] <= 0 else min(imax, cap / d['occ'])
    return d['days'] / (I * live), I


# ---- drawing of the tip region, to scale (thin layers thickened) ------------------------------------------------
def drawing(W=860, H=560, s=24.0, r_cu=8.0, r_li=4.0, t_al=0.4):
    cx, cy = W / 2, 40.0
    X = lambda r: cx + r * s                     # noqa: E731
    Y = lambda y: cy - y * s                     # noqa: E731  (y up = beam direction)
    rr = np.linspace(0, 13.0, 400)
    y, nr, ny, _ = CL.surface(rr)
    out = []
    # Al wall (offset outward along the normal by t_al, drawn ×3 for visibility)
    ta = t_al * 3
    for sg in (1, -1):
        xi, yi = X(sg * rr), Y(y)
        xo, yo = X(sg * (rr - nr * ta)), Y(y - ny * ta)
        pts = ' '.join(f'{a:.1f},{b:.1f}' for a, b in zip(np.r_[xi, xo[::-1]], np.r_[yi, yo[::-1]]))
        out.append(f'<polygon points="{pts}" fill="{AL}" stroke="none"{sd.tipattr(f"Al 6061-T6 wall, {t_al*1000:.0f} µm (drawn ×3)")}/>')
        m = rr <= r_cu
        tc = 0.012 * 25
        xc, yc = X(sg * (rr[m] + nr[m] * tc)), Y(y[m] + ny[m] * tc)
        pts = ' '.join(f'{a:.1f},{b:.1f}' for a, b in zip(np.r_[X(sg * rr[m]), xc[::-1]], np.r_[Y(y[m]), yc[::-1]]))
        out.append(f'<polygon points="{pts}" fill="{CU}"{sd.tipattr(f"Cu ≥ 12 µm along the beam, r ≤ {r_cu:.0f} mm (drawn ×25)")}/>')
        m = rr <= r_li
        tl = 0.012 * 25 + 0.02 * 12
        xl, yl = X(sg * (rr[m] + nr[m] * tl)), Y(y[m] + ny[m] * tl)
        xc2, yc2 = X(sg * (rr[m] + nr[m] * tc)), Y(y[m] + ny[m] * tc)
        pts = ' '.join(f'{a:.1f},{b:.1f}' for a, b in zip(np.r_[xc2, xl[::-1]], np.r_[yc2, yl[::-1]]))
        out.append(f'<polygon points="{pts}" fill="{LI}"{sd.tipattr(f"Li 20 µm along the beam, through a mask r ≤ {r_li:.0f} mm (drawn ×12)")}/>')
    # beam spot ±2σ
    for xx in (-4, -2, 0, 2, 4):
        yb = float(CL.surface(np.array([abs(xx)]))[0][0])
        out.append(sd.arrow(X(xx), H - 30, X(xx), Y(yb) + 8, BEAM, 2.5 if xx == 0 else 1.5, 10))
    out.append(sd.T(X(0), H - 8, 'beam, σ 2 mm (arrows at 0, ±1σ, ±2σ)', 20, BEAM))
    out.append(sd.T(X(9.5), Y(-11.5), f'Cu to r {r_cu:.0f} mm', 22, CU, 'start', 600))
    out.append(sd.T(X(5.0), Y(-3.0), f'Li to r {r_li:.0f} mm', 22, LI, 'start', 600))
    out.append(sd.T(X(-17.5), Y(-12), 'Al 0.35–0.4 mm', 22, sd.MUT, 'start', 600))
    # scale bar
    out.append(sd.line(X(-17), Y(-19), X(-12), Y(-19), sd.INK, 3))
    out.append(sd.T(X(-14.5), Y(-19) - 10, '5 mm', 18, sd.INK))
    return sd.svg(W, H, ''.join(out), 'the tip region of the ogive with the Cu liner and the Li mask')


# ---- the buildability review of 11 Nov 2026 (TARGET_REVIEW.md, review_data.py) -----------------------------------
VCOL = {'propose': sd.GREEN, 'ok': sd.BLUE, 'later': sd.ORANGE, 'drop': sd.RED}
V_THIS = rd.verdict('ogAl300cu12r8m4')
CMP = 'https://dylan-neff.web.cern.ch/notes/lnl-target-compare.html'
CU_REF = ('ogCu200', 'ogCu200_tip')            # his Cu ogive: the Li film of L11, and Li pressed on the tip only
LINER4, LINER3 = 'ogAl400cu12r8m4', 'ogAl300cu12r8m4'
# the same shell with Cu plated over the whole inside and Li on the tip: 0.4 mm once run L14 has it, 0.3 mm until then
PLATED, PLATED_WALL = (('ogAl400cu12_tip', '0.4') if nd.has('ogAl400cu12_tip') else ('ogAl300cu12_tip', '0.3'))
CD = rd.cap_days()
CAP_SRC = 'Geant4 run L14' if CD['g4'] else 'estimate, Geant4 running'


def stat(cfg):
    """the review's verdict for a configuration, as coloured text"""
    v = rd.verdict(cfg)
    return f'<span style="color:{VCOL[v["level"]]};font-weight:600;white-space:nowrap">{v["label"]}</span>'


def gain(tag, cols=(1, 2)):
    """days of his Cu ogive over days of `tag`, for both Li films on the Cu ogive.  cols index review_data.days3:
    0 big plastics, 1 as built with the liquid repaired, 2 as built with the liquid as at n_TOF."""
    return [rd.days3(c)[i] / rd.days3(tag)[i] for c in CU_REF for i in cols]


def times(vals):
    """'×1.0–1.4' from a list of ratios"""
    vals = [v for v in vals if v == v]
    if not vals:
        return '–'
    a, b = f'{min(vals):.1f}', f'{max(vals):.1f}'
    return f'×{a}' if a == b else f'×{a}–{b}'


G_ASB4, G_ASB3, G_ASBP = times(gain(LINER4)), times(gain(LINER3)), times(gain(PLATED))
G_BIG = times(gain(LINER4, (0,)) + gain(LINER3, (0,)))


def cap3(sfx=''):
    """(big plastics, as built, as built with the liquid as at n_TOF) for the cap with a thinner Li film: Geant4 L14 when
    it has the row, else the 45° diamond window's (the stand-in review_data.cap_days uses)."""
    t = rd.CAP['tag'] + sfx
    return rd.days3(t if nd.has(t) else rd.CAP['proxy'] + sfx)


def bars(rows, vmax, width=300, label_w=330, size=22, h=30):
    """horizontal bars with free text after each bar.  rows: (label, value, colour, text, tip)"""
    out = []
    for lab, v, c, txt, tip in rows:
        w = 0 if v != v else max(width * v / vmax, 2)
        out.append(f'<div{sd.tipattr(tip)} style="display:flex;align-items:center;gap:18px">'
                   f'<p style="width:{label_w}px;font-size:{size}px;font-weight:600;text-align:right;line-height:1.2">{lab}</p>'
                   f'<div style="width:{w:.0f}px;height:{h}px;background:{c};border-radius:6px"></div>'
                   f'<p style="font-size:{size}px;white-space:nowrap">{txt}</p></div>')
    return f'<div style="display:flex;flex-direction:column;gap:12px">{"".join(out)}</div>'


def cap_drawing(W=1000, H=500, s=11.0, li=LI):
    """the proposed flat Al end cap, cut along the beam (beam from the left).  To scale except the layers: the Al is
    drawn ×3, the Cu and Li films much thicker.  (The same drawing is in build_culiner_pf_deck.py.)"""
    z0, x0 = W - 390.0, H / 2 + 14.0             # where the beam axis meets the face
    Z = lambda z: z0 + z * s                     # noqa: E731  (z along the beam)
    X = lambda x: x0 - x * s                     # noqa: E731  (x across, up)
    R, L, q = 10.0, 55.0, math.sqrt(2.0)
    ta, tc, tl = 1.5, 0.6, 0.8                   # drawn thicknesses (mm) of the Al, the Cu and the Li
    Ro, xl = R + ta, 6.0 / q                     # outer radius as drawn, half-height of a Ø12 Li disc on the 45° face

    def pg(pts, fill, tip):
        return f'<polygon points="{" ".join(f"{Z(a):.1f},{X(b):.1f}" for a, b in pts)}" fill="{fill}"{sd.tipattr(tip)}/>'

    al = 'Al 6061-T6, one piece: tube wall 0.5 mm, flat face 0.4–0.5 mm (drawn ×3)'
    out = [pg([(-L, R), (R, R), (Ro, Ro), (-L, Ro)], AL, al), pg([(-L, -R), (-R, -R), (-Ro, -Ro), (-L, -Ro)], AL, al),
           pg([(-Ro, -Ro), (Ro, Ro), (Ro + ta * q, Ro), (-Ro + ta * q, -Ro)], AL, al)]
    for sg in (1, -1):                           # the collar where it joins the line
        out.append(pg([(-L, sg * Ro), (-L + 9, sg * Ro), (-L + 9, sg * (Ro + 3.5)), (-L, sg * (Ro + 3.5))], AL,
                      'thick collar where the cap joins the line, 55 mm upstream, out of the arms’ view'))
    out.append(pg([(-R, -R), (R, R), (R - tc * q, R), (-R - tc * q, -R)], CU,
                  'Cu ≥ 12 µm along the beam (8.5 µm on the face): the beam stop. An ordinary coating on a flat face'))
    out.append(pg([(-xl - tc * q, -xl), (xl - tc * q, xl), (xl - (tc + tl) * q, xl), (-xl - (tc + tl) * q, -xl)], li,
                  'Li 10–12 µm along the beam: LNL’s rolled foil, pressed on with flat moulds. Uniform along the beam by geometry'))
    for xx in (-4, -2, 0, 2, 4):                 # the beam, σ 2 mm
        out.append(sd.arrow(Z(-L + 14), X(xx), Z(xx - (tc + tl) * q - 0.5), X(xx), BEAM, 2.5 if xx == 0 else 1.5, 10))
    out.append(sd.T(Z(-L + 15), X(5.6), 'proton beam, σ 2 mm', 19, BEAM, 'start'))
    out.append(sd.T(Z(-L + 15), X(-7.6), 'vacuum, Ø20 bore', 19, sd.MUT, 'start'))
    zv = -(tc + tl / 2) * q                      # a pair leaves the film: one lepton through the wall, one through the face
    out.append(sd.arrow(Z(zv), X(0), Z(zv + 1.5), X(21), sd.GREEN, 2, 10) + sd.T(Z(zv + 2.6), X(19.5), 'e⁺', 20, sd.GREEN, 'start'))
    out.append(sd.arrow(Z(zv), X(0), Z(zv - 4.5), X(-21), sd.GREEN, 2, 10) + sd.T(Z(zv - 3.3), X(-21.5), 'e⁻', 20, sd.GREEN, 'start'))
    out.append(sd.T(Z(-L + 12), X(Ro) - 14, 'Al 6061-T6, one piece, wall 0.5 mm', 20, sd.MUT, 'start', 600))
    out.append(sd.T(Z(14.5), X(8.2), 'flat face at 45°, 0.4–0.5 mm', 20, sd.MUT, 'start', 600))
    out.append(sd.T(Z(8.5), X(-1.5), 'Li 10–12 µm along the beam', 20, li, 'start', 600))
    out.append(sd.T(Z(8.5), X(-4.0), 'rolled foil, pressed on with flat moulds', 18, sd.MUT, 'start'))
    out.append(sd.T(Z(8.5), X(-7.5), 'Cu ≥ 12 µm along the beam', 20, CU, 'start', 600))
    out.append(sd.T(Z(8.5), X(-10.0), '8.5 µm on the face: the beam stop', 18, sd.MUT, 'start'))
    out.append(sd.T(Z(-L + 4.5), X(-Ro - 3.5) + 24, 'collar to the line', 18, sd.MUT))
    out.append(sd.line(Z(-38), X(-Ro) + 30, Z(-28), X(-Ro) + 30, sd.INK, 3) + sd.T(Z(-33), X(-Ro) + 54, '10 mm', 18, sd.INK))
    return sd.svg(W, H, ''.join(out), 'the flat aluminium end cap at 45° with its Cu stop and pressed Li, cut along the beam')


def li_plot(W=860, H=500):
    """share of the γ₀ from the 441 keV resonance against the converted fraction (review_li_conversion.csv)"""
    t, e = 100 * rd.li_table(), rd.li_eout()
    P = sd.Plot(W, H, x=(0, 100), y=(0, 100), xlabel='share of the Li atoms turned into LiOH (%)',
                ylabel='γ₀ from the 441 keV resonance (%)')
    P.xticks([(v, str(v)) for v in (0, 25, 50, 75, 100)]).yticks([(v, str(v)) for v in (0, 20, 40, 60, 80, 100)])
    P.hline(10, sd.MUT, label='10 %')
    for um, c in LI_COL:
        P.line([100 * f for f in t.columns], list(t.loc[um]), c,
               tips=[f'Li {um} µm, {100 * f:.0f} % LiOH: {t.loc[um, f]:.1f} % of the γ₀ from 17.64 MeV. '
                     + (f'The beam leaves the film at {e.loc[um, f]:.0f} keV' if e.loc[um, f] > 100 else 'The beam stops in the film')
                     for f in t.columns])
    return P.svg('share of the gamma-0 yield from the 441 keV resonance against the fraction of the film converted to LiOH')


LI_COL = ((20, sd.RED), (15, sd.ORANGE), (12, sd.GREEN), (10, sd.BLUE))


def kpi(v, label, color, tip=None):
    return (f'<div{sd.tipattr(tip)} style="flex:1;border-top:4px solid {color};padding-top:10px">'
            f'<p style="font-size:46px;font-weight:600;color:{color};line-height:1.05">{v}</p>'
            f'<p style="font-size:21px;color:{sd.MUT};line-height:1.25">{label}</p></div>')


D = sd.Deck('LNL: his ogive in Al, Cu only where the beam stops',
            f'Technical note on Pierfrancesco’s ogive made of Al with a 12 µm Cu liner over the tip and a masked Li film. '
            f'Status {rd.DATE}: {V_THIS["label"]}. A flat aluminium end cap at 45° is proposed instead. '
            'Geant4 L12, PIXE, x-rays, how to make it.')

# ---- 1. where this stands (review of 11 Nov 2026) ------------------------------------------------------------------
STEPS = sd.table(['step', 'this note assumed (4 Nov)', 'the review found (11 Nov)'],
                 [['Al shell', 'wall 0.35–0.4 mm, 63 mm deep, ~1 k€',
                   'a comfortable turned wall is 0.5–0.8 mm. Feasible with care, one or two scrapped (estimate)'],
                  ['Cu at the tip', '≥ 12 µm sputtered from the axis in 1–2 h, a sleeve mask at r ≈ 10 mm',
                   '7–30 h at a 150–200 mm throw (estimate), below ~200 °C. Not line of sight, so the mask leaks. '
                   'No adhesion data above 10 µm on Al'],
                  ['Li', '20 µm evaporated from the axis through a mask r ≤ 4 mm',
                   '0.8–5.4 g of lithium per coating. LNL presses rolled foil, its lithium evaporator (2015) is unconfirmed']],
                 size=21, widths=[130, 270, 400], align=['left'] * 3)


def asb_row(lab, cfg, d3=None, extra=''):
    d3 = d3 or rd.days3(cfg)
    c = VCOL[rd.verdict(cfg)['level']]
    return (lab, d3[1], c, f'<b>{nd.fmt(d3[1])} d</b> ({nd.fmt(d3[2])} d){extra}',
            f'{lab}: {nd.fmt(d3[1])} d as built with the liquid repaired, {nd.fmt(d3[2])} d with the liquid as at n_TOF, '
            f'{nd.fmt(d3[0])} d with the big plastics. Review: {rd.verdict(cfg)["label"]}')


ASB = [asb_row('his Cu ogive, Li film as in L11', 'ogCu200'),
       asb_row('his Cu ogive, Li on the tip only', 'ogCu200_tip'),
       asb_row('this note, Al 0.4 mm wall', LINER4),
       asb_row('this note, Al 0.3 mm wall', LINER3),
       asb_row(f'Al {PLATED_WALL} mm, Cu plated everywhere', PLATED),
       asb_row('flat Al end cap at 45°', rd.CAP['tag'], (CD['big'], CD['asb'], CD['asb_ntof']),
               '' if CD['g4'] else ' estimate')]
D.slide('status',
        sd.title(f'Where this stands ({rd.DATE}): {V_THIS["label"]}',
                 'A buildability review checked this design against how lithium targets are really made. '
                 'Its proposal has not yet been discussed with Pierfrancesco.') +
        sd.row(sd.col(sd.p('Why: three steps LNL has not shown', 26, sd.INK, 600), STEPS, gap=10, w=840),
               sd.col(sd.p('What it buys with today’s detector: days to 3σ as built', 26, sd.INK, 600),
                      bars(ASB, max(r[1] for r in ASB if r[1] == r[1]) * 1.05, width=210, label_w=330, size=21, h=26),
                      sd.p('Liquid scintillator repaired (in brackets: as it ran at n_TOF). Colours: '
                           + ', '.join(f'<span style="color:{VCOL[k]};font-weight:600">{rd.LEVELS[k]}</span>'
                                       for k in ('propose', 'ok', 'later')) + '.', 19, sd.MUT),
                      sd.p(f'As built this design gains <b>{G_ASB4}</b> on his Cu ogive with the 0.4 mm wall, {G_ASB3} with 0.3 mm '
                           f'(which lets {100 * ALCU["occ"]:.0f} % x-ray occupancy through). The {G_BIG} needs the big plastics.', 22),
                      gap=12), gap=44) +
        sd.callout(f'<b>Proposed instead:</b> a flat aluminium end cap at 45° with a Cu stop and LNL’s rolled lithium, pressed on '
                   f'(next slide). <b>If the ogive is kept:</b> first his Cu ogive, electroformed in hard copper, Li pressed on the tip only. '
                   f'Then the Al ogive at 0.4 mm with Cu plated over the whole inside. All designs side by side: '
                   f'<a href="{CMP}" style="color:{sd.BLUE}">lnl-target-compare</a>.', sd.GREEN, 23),
        pad='84px 128px 100px',
        notes=f'Review: {rd.REVIEW}, §0, §4.1, §5. Verdict for this design: {V_THIS["label"]} ({V_THIS["short"]}). '
              'Days: nd_reach.csv through nd_reach_io.py (reference fit, θ × |y| × E_sum, background shape floating, 1 µA, 1.10 MeV). '
              f'Gains are days of his Cu ogive over days of the design, for both lithium films on the Cu ogive (as simulated in L11, and pressed '
              f'on the tip only) and both liquid states. Cu plated over the whole inside with Li on the tip: {G_ASBP} as built '
              f'(simulated at {PLATED_WALL} mm). The cap: {CD["note"]}. ' + nd.ASB_NOTE +
              ' The estimates (wall scrap, sputter time, lithium charge) are from the review and are labelled as such there.',
        short='where this stands')

# ---- 2. what is proposed instead ---------------------------------------------------------------------------------------
pm = rd.CAP['press']
k = sd.row(kpi(f'{nd.fmt(CD["big"])} d', f'to 3σ at 1 µA with the big plastics ({CAP_SRC})', sd.GREEN, CD['note']),
           kpi(f'{nd.fmt(CD["asb"])} / {nd.fmt(CD["asb_ntof"])} d', f'as built: liquid repaired / as at n_TOF ({CAP_SRC})',
               sd.GREEN, CD['note']), gap=24)
k2 = sd.row(kpi(f'×{pm["t400"][1]}–{pm["t500"][1]}', 'margin at 1 bar for a 0.4–0.5 mm face over the Ø20 bore (estimate)', sd.INK,
                'clamped ellipse 20 × 28 mm, yield 276 MPa (TARGET_REVIEW.md §6.1)'),
            kpi(f'+{rd.CAP["heat_K"]["t400"][0]:.0f} K', 'across a 0.4 mm face at 1 µA, 1.1 W (estimate)', sd.INK,
                'radial conduction in the face (TARGET_REVIEW.md §4.5)'), gap=24)
D.slide('instead',
        sd.title('Proposed instead: a flat aluminium end cap at 45°',
                 'One piece of Al 6061-T6, a flat Cu stop, LNL’s rolled lithium pressed on with flat moulds. '
                 'A proposal, not yet discussed with Pierfrancesco') +
        sd.row(cap_drawing(), sd.col(k, k2, *[sd.p('• ' + t[0].upper() + t[1:] + '.', 21) for t in rd.CAP['pros']], gap=18, w=620), gap=44),
        notes=f'{rd.REVIEW} §6.1. {rd.CAP["stack"]}. Days: {CD["note"]}, for 20 µm of Li along the beam '
              f'(with 12 µm: {nd.fmt(cap3("_li12")[0])} d with the big plastics, {nd.fmt(cap3("_li12")[1])} / {nd.fmt(cap3("_li12")[2])} d as built). '
              'What it does not fix: ' + '. '.join(t[0].upper() + t[1:] for t in rd.CAP['cons']) + f'. Cost: {rd.CAP["cost"]}. '
              'The drawing is to scale except the layers (Al ×3, the films much thicker). '
              f'The cap and every other design side by side: <a href="{CMP}">lnl-target-compare</a>.',
        short='proposed instead')

# ---- 3. the 4 Nov design ------------------------------------------------------------------------------------------
bd_cu, I_cu = best_days(CUOG)
bd_al4, I_al4 = best_days(AL4)
bd_al4_4, I_al4_4 = best_days(AL4, imax=4.0)


k = sd.row(kpi(f'{ALCU["sigma"]:.1f}°', f'σ68 opening angle (his Cu ogive {CUOG["sigma"]:.1f}°)', CU,
               'Geant4 L12, X17 m 16.8, big plastics'),
           kpi(f'{ALCU["days"]:.2f} d', f'per µA to 3σ at ATOMKI, 1.10 MeV, big plastics (his {CUOG["days"]:.2f})', CU,
               f'{nd.LABEL}; big plastics; line-of-sight Li for both'),
           kpi(f'×{CUOG["days"] / ALCU["days"]:.1f}', f'faster than his Cu ogive with the big plastics. As built: {G_ASB3} (0.4 mm wall: {G_ASB4})',
               sd.GREEN, 'days of his Cu ogive over days of this design, reference fit. As built: both lithium films on the Cu ogive, both liquid states'),
           gap=24)
k2 = sd.row(kpi(f'{100 * ALCU["epc"]:.0f} %', f'of the background from γ converting in the shell (his {100 * CUOG["epc"]:.0f} %)', sd.INK),
            kpi('590', 'single-arm legs/s per µA into DREAM (his 1630)', sd.INK),
            kpi(f'{100 * AL4["occ"]:.1f} %', 'MM x-ray occupancy per arm per µA with a 0.4 mm wall (0.3 mm: 12 %)', sd.ORANGE), gap=24)
D.slide('proposal',
        sd.title('The 4 Nov design: his ogive in Al, with Cu only where the beam stops',
                 f'Kept as the record of the study. Status {rd.DATE}: {V_THIS["label"]} (slide 1). Al 6061-T6 0.35–0.4 mm, '
                 '≥ 12 µm Cu (along the beam) over r ≤ 8–10 mm, 20 µm Li through a mask r ≤ 4 mm, both laid down from the beam axis') +
        sd.row(drawing(H=520, s=22.0), sd.col(k, k2, sd.callout(
            f'The leptons see the Al shell, not the Cu: the resolution of the Al + Mo ogive without a Mo coat inside a 63 mm deep cone. '
            f'The price is Cu K x-rays (8 keV), which a 0.4 mm Al wall stops: at the documented 1 µA they do not limit ({bd_al4:.2f} d to 3σ); '
            f'4 µA, if LNL can allow it at 1.1 MeV (ask), would give {bd_al4_4:.2f} d. These are big-plastics days. '
            f'With today’s detector the gain on his Cu ogive is {G_ASB4} with the 0.4 mm wall and {G_ASB3} with 0.3 mm.', sd.BLUE, 24),
            gap=26, w=880), gap=40),
        notes='Geant4 run L12 (MX17_Full_Geant lnl_culiner): the CAD ogive in Al with a 12 µm Cu liner only where the shell radius is ≤ 8 mm, '
              'vertices only where the beam lands at r ≤ 4 mm (the Li mask). Big plastics, MM 15° + TOF, 1 µA. Days: the reference fit '
              '(θ × |y| × E_sum, background shape floating, MC-safe; nd_reach.csv, FEASIBILITY_SIM.md §19; corrected 10 Nov 2026 from '
              f'the statistics-only fit). Days for his Cu ogive with a line-of-sight Li film ({CUOG["days"]:.2f} d); with L11’s uniform film it is '
              f'{nd.best("ogCu200", "bigP", 1100):.2f} d. '
              f'As built (liquid repaired / as at n_TOF): this design {nd.asb_pair(LINER3, 1100)} d at 0.3 mm and {nd.asb_pair(LINER4, 1100)} d at 0.4 mm, '
              f'his Cu ogive {nd.asb_pair("ogCu200", 1100)} d (Li film as in L11) or {nd.asb_pair("ogCu200_tip", 1100)} d (Li on the tip only). '
              f'Review of {rd.DATE}: {V_THIS["label"]} ({V_THIS["short"]}). '
              'The drawing is to scale except the layers (Al ×3, Cu ×25, Li ×12). CU_LINER.md §0, TARGET_REVIEW.md §4.1.', short='the 4 Nov design')

# ---- 4. where and how much Cu ---------------------------------------------------------------------------------------
P = sd.Plot(900, 560, x=(0, 12), y=(0, 36), xlabel='radius on the shell where the beam lands (mm)',
            ylabel='Cu thickness (µm)')
P.xticks([(v, str(v)) for v in (0, 2, 4, 6, 8, 10, 12)]).yticks([(v, str(v)) for v in (0, 6, 12, 18, 24, 30, 36)])
pr = PROF[PROF.rho_mm <= 12]
P.line(pr.rho_mm, pr.Cu_beam_uniform, sd.GREY, tips=[f'r {a:.1f}: {b:.1f} µm along the beam (uniform 12 µm coat)' for a, b in zip(pr.rho_mm, pr.Cu_beam_uniform)])
P.line(pr.rho_mm, pr.Cu_beam_los150, CU, tips=[f'r {a:.1f}: {b:.1f} µm along the beam (line of sight, 150 mm)' for a, b in zip(pr.rho_mm, pr.Cu_beam_los150)])
P.line(pr.rho_mm, pr.Cu_normal_los150, CU, dash='6 5', tips=[f'r {a:.1f}: {b:.1f} µm along the normal' for a, b in zip(pr.rho_mm, pr.Cu_normal_los150)])
P.hline(10.7, sd.RED, dash='4 4', label='needed along the beam: 10.7 µm')
lt = pd.read_csv(OP / 'culiner_landing.csv')
s2 = lt[lt.sigma_mm == 2.0].iloc[0]
tab = sd.table(['', 'Cu needed along the beam'],
               [['after 20 µm Li (872 keV)', '6.0 µm'], ['no Li, 1.15 MeV', '8.7 µm'], ['design (×1.12 + 1 µm)', '<b>10.7 → 12 µm</b>'],
                ['beam σ 2 mm: 99.9 % inside', f'r {s2.r999:.1f} mm'], ['on bare Al beyond r 8 mm', f'{s2.share_beyond_8mm:.1e}']],
               size=23)
D.slide('cu', sd.title('Where the Cu goes: r ≤ 8–10 mm, ≥ 12 µm along the beam',
                       'An evaporated coat laid from the beam axis lands ∝ cos(incidence): thin on the steep flank, constant along the beam. '
                       'Sputtered Cu at this throw does not (review, 11 Nov)') +
        sd.row(sd.col(P.svg('Cu thickness against radius'),
                      sd.legend([('uniform 12 µm (plating): along the beam', sd.GREY, 'line'), ('evaporated from the axis: along the beam', CU, 'line'),
                                 ('evaporated from the axis: along the normal', CU, 'dash')], size=19), gap=4),
               sd.col(tab, sd.p('Outside the Cu the beam hits Al: ²⁷Al(p,γ) 10.76 MeV. Even with a 1 % halo that is 0.4 % of the ⁸Be γ₀: '
                                'the Al does not set the extent, the Li mask and its alignment do (Cu ≥ 3 mm beyond the Li).', 23, sd.MUT),
                      sd.callout('Review, 11 Nov: any profile with ≥ 12 µm along the beam at the tip stops the beam. A uniform plated layer over '
                                 'the whole inside (grey line) does it without a mask, and loses nothing in the fit.', sd.GREEN, 22),
                      gap=22, w=760), gap=48),
        notes='PSTAR ranges; ×1.12 covers straggling (~4 %) and a 10 % thickness error, +1 µm roughness. A Li-free beam at 1.15 MeV '
              'must still stop in the Cu (film gone, protons outside the mask). Profiles for a small source on the axis 150 mm '
              'upstream of the tip (400 mm: ±10 % to r 8). CU_LINER.md §1–2, §4. Review of 11 Nov (TARGET_REVIEW.md §4.4): the '
              'cos(incidence) profile holds for evaporation only. Sputtered atoms at 10⁻³–10⁻² mbar have a mean free path of 1–10 cm, so at a '
              '150–400 mm throw the flux is diffuse and a sleeve mask leaks. For the stop this does not matter. '
              f'Plated over the whole inside with Li on the tip: {rd.fmt3(PLATED)} d (big plastics / as built / as built with the liquid as at n_TOF, '
              f'{PLATED_WALL} mm wall) against {rd.fmt3(LINER3)} d for the patch and the masked Li at 0.3 mm.', short='where the Cu goes')

# ---- 5. the Li ----------------------------------------------------------------------------------------------------
lm = LIMIX[LIMIX.Ep_keV == 1100.0].set_index('film')
lm3 = LIMIX[LIMIX.Ep_keV == 1030.0].set_index('film')
rows = []
for f, lab in (('uniform film, no mask (L11)', 'uniform along the normal (L11)'), ('line of sight (150 mm), no mask', 'line of sight, no mask'),
               ('line of sight (150 mm), mask r<=4', '<b>line of sight, mask r ≤ 4</b>')):
    rows.append([lab, f'{lm.loc[f].Yg0_rel_flat:.2f}', sd.pct(lm.loc[f].f17, 1), sd.pct(lm3.loc[f].f17, 1)])
D.slide('li', sd.title('Laid from the axis, the Li behaves like a flat film',
                       'L11’s flank problem (17.64 MeV) came from assuming a uniform film, not from the shape. '
                       'True for evaporated Li only, which needs 0.8–5.4 g of lithium per coating (review, 11 Nov)') +
        sd.row(sd.table(['Li film', 'γ₀ per proton / flat', '17.64 share, 1.10 MeV', '1.03 MeV'], rows, size=24),
               sd.col(sd.p('On the flank the beam meets the wall at ~65°. A film of fixed normal thickness is ×2.4 longer along the beam, '
                           'the protons leave it below 441 keV and 29–71 % of the γ₀ moves to 17.64 MeV.', 24),
                      sd.p('Evaporated from the axis, the Li lands ∝ cos(incidence), as the Cu: ~20 µm along the beam everywhere.', 24),
                      sd.p('Mask it to r ≤ 4 mm: beyond that the Li sits 5–14 mm upstream of the tip and the opening angle, taken from '
                           'the nominal vertex, degrades (Geant4: ~25 % in days).', 24, sd.MUT),
                      sd.callout('Review, 11 Nov: LNL presses rolled foil, it does not evaporate. A disc pressed on the tip cap only '
                                 '(r ≤ 2.5 mm) stays off the flank and takes 55 % of a σ 2 mm beam. A flat face has no flank at all.',
                                 sd.GREEN, 22), gap=20, w=700), gap=48),
        notes='opt_cu_liner.li_mix_table / los_yield_mix: share-weighted ⁸Be yields (target_model.layered_yield) over the σ 2 mm spot. '
              'CU_LINER.md §3 and §7. Review of 11 Nov (TARGET_REVIEW.md §4.4, §4.7): a small source far out on the axis needs '
              'm = π d² ρ t of lithium, 0.8 g at 150 mm and 5.4 g at 400 mm for 20 µm (estimate), nearly all of it on the mask and the chamber. '
              'The tip is a sphere of R 2.8 mm: a flat foil pressed into it stretches, and whatever overlaps the 65° flank is ×2.4 thicker along the beam.',
        short='the Li')

# ---- 6. the Li thickness (review of 11 Nov) -----------------------------------------------------------------------
yr, t100 = rd.li_yield_rel(), rd.li_table()
LI_DAYS = [(lab, tag) for lab, tag in (('his Cu ogive, Li on the tip', 'ogCu200_tip'), ('this shell, Cu plated', PLATED))
           if nd.has(tag + '_li12')]
CAP_G4_LI = nd.has(rd.CAP['tag'] + '_li12')
li_rows = []
for um, _c in LI_COL:
    sfx = '' if um == 20 else f'_li{um}'
    r = [f'<b>{um} µm</b>', sd.pct(yr[um]), sd.pct(float(t100.loc[um, 1.0]), 0 if t100.loc[um, 1.0] > 0.095 else 1)]
    r += [' / '.join(nd.fmt(x) for x in rd.days3(tag + sfx)[:2]) for _lab, tag in LI_DAYS]
    r.append(' / '.join(nd.fmt(x) for x in cap3(sfx)[:2]))
    li_rows.append(r)
li_tab = sd.table(['Li along the beam', 'γ₀ yield', '441 keV share if all of it is LiOH'] + [lab for lab, _t in LI_DAYS]
                  + ['flat Al cap' + ('' if CAP_G4_LI else ' (estimate)')], li_rows, size=20)
D.slide('lithick',
        sd.title('New on 11 Nov: a 20 µm lithium film is not safe against LiOH, 10–12 µm is',
                 'Residual water turns Li into LiOH. The lithium atoms stay, but the O and H add stopping, '
                 'so the beam slows down to the strong 441 keV resonance inside the film. This design assumed 20 µm') +
        sd.row(sd.col(li_plot(820, 480),
                      sd.legend([(f'Li {um} µm', c, 'line') for um, c in LI_COL], size=20), gap=4),
               sd.col(sd.callout(rd.LI['headline'], sd.RED, 23),
                      sd.callout(rd.LI['fix'], sd.GREEN, 23),
                      li_tab,
                      sd.p('Days to 3σ at 1 µA, 1.10 MeV: big plastics / as built with the liquid repaired. ' + rd.LI['rate'], 20, sd.MUT),
                      gap=18, w=800), gap=44),
        pad='84px 128px 100px',
        notes=f'{rd.REVIEW} §4.2. review_li_conversion.py → out/target/options/review_li_conversion.csv: the repo’s yield model with PSTAR '
              'stopping, the outer fraction of the Li atoms converted to LiOH and the rest metal, at 1.10 MeV. Hover a point for the energy at '
              'which the beam leaves the film. The 441 keV resonance (17.64 MeV) is about 50× stronger than the 18.15 MeV one. '
              'It applies to every design, his Cu cup and Cu ogive included: it is a property of the film, not of the shell. '
              'The thinner films are a yield change on the same Geant4 events (nd_reach_thinli.csv). '
              + ('' if CAP_G4_LI else 'The cap column is an estimate until run L14 is in: the 45° diamond window’s Geant4 days with the thinner film. ')
              + 'What to do: 10–12 µm, run at 1.10 MeV not 1.03, watch the γ₀ yield per µC (it rises as the beam reaches 441 keV), '
              'and measure the rate with one film on the LNL line for a week before the run.',
        short='Li thickness')

# ---- 7. Geant4 reach --------------------------------------------------------------------------------------------------
vmax = 1.8
hb = sd.hbars([(d['name'], d['days'], d['color'], f'{d["days"]:.2f} d/µA at 1.10 MeV, {d["days103"]:.2f} at 1.03; σ68 {d["sigma"]:.1f}°') for d in DES],
              vmax, width=240, label_w=300, fmt=lambda v: f'{v:.2f}', size=23)
tb = sd.table(['design', 'σ68', '1.03 MeV', 'EPC', 'as built', 'review, 11 Nov'],
              [[d['name'], f'{d["sigma"]:.1f}°', f'{d["days103"]:.2f}', sd.pct(d['epc']), nd.asb_pair(d['cfg'], 1100), stat(d['cfg'])]
               for d in DES], size=20, widths=[272, 64, 76, 56, 110, 312], align=['left', 'right', 'right', 'right', 'right', 'left'])
D.slide('reach', sd.title('Geant4 L12: the Cu liner costs nothing against Mo; the Al wall sets the resolution',
                          f'days per µA to 3σ at the ATOMKI ratio, big plastics, 1.10 MeV, {nd.LABEL} (line-of-sight Li everywhere). '
                          'Table: as built (liquid repaired / as at n_TOF) and the status of each design') +
        sd.row(hb, sd.col(tb, w=890), gap=30),
        notes=f'Days: {nd.LABEL} (nd_reach.csv, FEASIBILITY_SIM.md §19, 10 Nov 2026); EPC shares from geant_reach.csv. '
              f'+0.1 mm Al: +1° and +{100 * (AL4["days"] / ALCU["days"] - 1):.0f} % days; Cu 30 instead of 12: '
              f'+1.6° and +{100 * (BY["Al 300 + Cu 30, Li r ≤ 4"]["days"] / ALCU["days"] - 1):.0f} %. As built, 1.10 MeV, liquid repaired / '
              'liquid as at n_TOF: ' + '; '.join(f'{d["name"]} {nd.asb_pair(d["cfg"], 1100)} d' for d in DES) + '. ' + nd.ASB_NOTE
              + f' Status column: {rd.REVIEW} §5. The Mo and Be rows are kept as the record: '
              + f'{rd.verdict("ogAl300mo8")["short"]}. {rd.verdict("ogBe300mo8")["short"]}.',
        short='Geant4 reach')

# ---- 8. x-rays -------------------------------------------------------------------------------------------------------
xr = [(d['name'], 100 * d['occ'], d['color'], f'{100 * d["occ"]:.1f} % per arm per µA') for d in DES]
pt = pd.read_csv(OP / 'pixe_testem5.csv')


def py(el, model='Empirical', e=870.0):
    q = pt[(pt.el == el) & (pt.model == model) & (pt.E_keV == e)]
    return float(q.K_per_p.iloc[0]) if len(q) else np.nan


rows = [['Cu K, 8.0/8.9 keV', sd.sci(py('Cu')), '2.1 × 10⁻⁴'], ['Mo K, 17.5/19.6 keV', sd.sci(py('Mo')), '2.2 × 10⁻⁶'],
        ['Ti K, 4.5 keV', sd.sci(py('Ti')), '—']]
best = [(d['name'], *best_days(d)) for d in DES]
best4 = [(d['name'], *best_days(d, imax=4.0)) for d in DES]
D.slide('xrays', sd.title('The price: Cu K x-rays, paid by the Al wall',
                          'Cu makes 45× more K x-rays than Mo, but at 8 keV, where Al stops them; 0.1 mm more Al divides them by ~4') +
        sd.row(sd.col(sd.p('MM occupancy per arm per µA (1.2 µs)', 24, sd.INK, 600),
                      sd.hbars(xr, 40, width=420, label_w=360, fmt=lambda v: f'{v:.1f} %', size=24), gap=8),
               sd.col(sd.p('PIXE per proton at 872 keV, Geant4 TestEm5', 24, sd.INK, 600),
                      sd.table(['', 'Geant4', 'estimate (L10/L11)'], rows, size=22),
                      sd.p('Mo is ×2 the estimate: the Mo designs’ published occupancies are ×2 low. '
                           f'At {100 * BY["Al 300 + Mo 8"]["occ"]:.0f}–{100 * BY["Be 300 + Mo 8"]["occ"]:.0f} % per arm per µA, '
                           'every Mo stop was dropped on 11 Nov.', 22, sd.RED),
                      sd.p('Days to 3σ at the best current (≤ 1 µA documented, ≤ 10 % occupancy): ' +
                           '; '.join(f'{n}: {b:.2f} d ({I:.1f} µA)' for n, b, I in best[:4]) +
                           '. If LNL can allow 4 µA at 1.1 MeV (ask): ' +
                           '; '.join(f'{n}: {b:.2f} d ({I:.1f} µA)' for n, b, I in best4[:4]) + '.', 20, sd.MUT), gap=14, w=640), gap=40),
        notes='Geant4 L12 x-ray libraries (photons from the film, MM hits per arm) × the TestEm5 PIXE yields, protons outside the Li '
              'mask entering the Cu at 1.10 MeV; the calibrated analytic model (opt_cu_liner.escape) agrees to ~20 %. 10 % per arm is '
              'a working limit until the MM point-cluster cut is measured with a source. CU_LINER.md §6–7.', short='x-rays')

# ---- 9. how to make it (corrected by the review of 11 Nov) --------------------------------------------------------
FOUND = sd.table(['the 4 Nov recipe said', 'the review found (11 Nov)'],
                 [['Sputter 12 µm of Cu from the axis in 1–2 h',
                   '<b>7–30 h</b> at the 150–200 mm throw of a source outside the cone (estimate), with the aluminium kept below ~200 °C. '
                   'LNL’s own rate is 11 µm/h, close-coupled, on flat copper at 500 °C'],
                  ['Sputtered Cu lands by line of sight, and a sleeve stops it at r ≈ 10 mm',
                   '<b>Not at this throw.</b> The argon scatters the atoms, the flux is diffuse and a sleeve mask leaks. '
                   'Only evaporation is line of sight. For a beam stop it does not matter'],
                  ['Evaporate 20 µm of Li from the axis through a mask',
                   '<b>0.8 g (150 mm) to 5.4 g (400 mm) of lithium per coating</b>, nearly all of it on the mask and the chamber (estimate). '
                   'LNL’s routine is rolled foil pressed on Cu. Its lithium evaporator (2015) is unconfirmed (ask)'],
                  ['Plating the whole inside is the cheap fallback (Option B)',
                   f'<b>It loses nothing:</b> {rd.fmt3(PLATED)} d against {rd.fmt3(LINER3)} d for the patch and the mask '
                   f'(big plastics / as built / as built with the liquid as at n_TOF). It has a precedent and needs no mask']],
                 size=20, widths=[520, 1144], align=['left', 'left'])
D.slide('make', sd.title('How to make it: plate the whole inside, press the Li on the tip',
                         'The 4 Nov recipe (both films laid from the axis in one vacuum system) needs rates and tools LNL has not shown. '
                         'Option B, plating, is now the preferred way to make this shell') +
        sd.flow([dict(label='Al 6061-T6 ogive', sub='wall 0.4 mm, 63 mm deep, collar at the base. 0.8–2.5 k€, one or two scrapped (estimate)', color=AL),
                 dict(label='Cu over the whole inside', sub='sputtered seed on a Ti or Cr layer (or zincate), then acid Cu to ≥ 12 µm at the tip, '
                                                            'anode wire on the axis. No mask', color=CU),
                 dict(label='Bake, coupons, leak test', sub='150 °C bake. Coupon thickness, tape test, 20–150 °C cycles. He leak test'),
                 dict(label='Li pressed on the tip', sub='LNL’s rolled foil, in the argon glovebox. New moulds for the R 2.8 mm tip (ask)', color=LI),
                 dict(label='PIGE on the beam', sub='1.10 MeV: no Al lines (843, 1014 keV, 10.76 MeV), 478 keV present', color=sd.GREEN)],
                size=23, wrap=True) +
        FOUND,
        pad='84px 128px 100px',
        notes=f'{rd.REVIEW} §4.1, §4.4, §6.3, and the note at the top of CU_LINER.md (its §8 keeps the 4 Nov text as the record). '
              'Cu on Al: straight onto the oxide it adheres poorly, and no adhesion or stress data were found above 10 µm. The route with a precedent is '
              'a 1–3 µm sputtered seed with a Ti or Cr adhesion layer, then electroplating (CERN’s Cu on Al sequence). Uniform along the normal means '
              '×2.4 more Cu on the flank than needed, which costs nothing measurable. '
              f'Plated version simulated at {PLATED_WALL} mm. '
              'The lithium: a flat foil pressed into a tip of R 2.8 mm stretches and thins unevenly. A disc that stays on the tip cap (r ≤ 2.5 mm) takes '
              '55 % of a σ 2 mm beam. A rounder tip (R 6–8 mm) would take 95 % and is a question for Pierfrancesco. '
              'Margins (CU_LINER.md §5): 1 bar ×4.8 (0.3 mm) / ×10 (0.4 mm), tip +54–69 K at 4 µA. Hydrogen in the Cu is a watch item, not a blocker: '
              'MEG II stopped 8–11 µA in 25 µm of Cu for four weeks without significant deterioration. A plated-through layer is safer than a 12 µm film, '
              'where a 6 µm blister cap is half the film. Not a loose Cu cup: no thermal contact and a trapped volume.',
        short='how to make it')

# ---- 10. bottom line (review of 11 Nov) ------------------------------------------------------------------------------
V_CAP, V_CUOG, V_PL = rd.verdict(rd.CAP['tag']), rd.verdict('ogCu200_tip'), rd.verdict(PLATED)
BL = sd.table(['design', 'review, 11 Nov', 'days to 3σ: big plastics / as built / as built, liquid as at n_TOF', 'what it needs'],
              [['<b>Flat Al end cap at 45°</b>, Cu stop, pressed Li', stat(rd.CAP['tag']),
                f'{nd.fmt(CD["big"])} / {nd.fmt(CD["asb"])} / {nd.fmt(CD["asb_ntof"])} ({CAP_SRC})',
                'flat parts only, LNL’s pressed lithium'],
               ['His Cu ogive, electroformed, Li on the tip', stat('ogCu200_tip'), rd.fmt3('ogCu200_tip'),
                'hard copper, new moulds for the pointed tip'],
               [f'Al ogive, Cu plated over the whole inside, Li on the tip', stat(PLATED), rd.fmt3(PLATED) + f' ({PLATED_WALL} mm wall)',
                'a 0.4 mm wall, a seed and a plating bath'],
               ['<b>This note:</b> Al ogive, Cu patch, masked evaporated Li', stat(LINER3),
                f'{rd.fmt3(LINER4)} (0.4 mm), {rd.fmt3(LINER3)} (0.3 mm)', 'three steps LNL has not shown']],
              size=22, widths=[440, 330, 500, 394], align=['left'] * 4)
D.slide('bottom',
        sd.title(f'Bottom line ({rd.DATE}): simpler targets come first, this one waits',
                 'The proposal of the buildability review. It has not yet been discussed with Pierfrancesco') +
        BL +
        sd.row(sd.card(sd.p(f'<b>As built it buys little.</b> {G_ASB4} on his Cu ogive with the 0.4 mm wall, {G_ASB3} with 0.3 mm. '
                            f'The {G_BIG} needs the big plastics.', 23)),
               sd.card(sd.p('<b>If this shell is made, plate it.</b> Cu over the whole inside, Li pressed on the tip. '
                            'No patch, no sleeve mask, no lithium evaporator.', 23)),
               sd.card(sd.p('<b>Thinner lithium.</b> 10–12 µm, not 20, until a one-week film test on the LNL line shows how fast the film converts.', 23)),
               sd.card(sd.p('<b>Nothing in the beam pipe.</b> No laboratory deposits Li, Cu or Ti there, and no design here needs it.', 23)),
               gap=24, align='stretch'),
        notes=f'{rd.REVIEW} §0, §5. Verdicts: the cap, {V_CAP["label"]} ({V_CAP["short"]}). His Cu ogive, {V_CUOG["label"]} ({V_CUOG["short"]}). '
              f'The plated Al ogive, {V_PL["label"]} ({V_PL["short"]}). This note’s design, {V_THIS["label"]} ({V_THIS["short"]}). '
              f'Days: nd_reach_io (reference fit, 1 µA, 1.10 MeV, 20 µm of Li). The cap: {CD["note"]}. ' + nd.ASB_NOTE +
              f' Every design side by side: <a href="{CMP}">lnl-target-compare</a>.',
        short='bottom line')

# ---- 11. what to ask (TARGET_REVIEW.md §7) -------------------------------------------------------------------------
ASK = ['How will the lithium go on your ogive: pressed foil with new moulds for the pointed tip, or evaporation? '
       'Does the lithium evaporator of your 2015 paper exist and work today, and how does a target leave it?',
       'We do <b>not</b> need anything deposited in the beam pipe. On 4 Nov we meant a coating chamber. '
       'Would you rather have a part on which your rolled and pressed lithium works directly?',
       'Would you consider a <b>flat face at 45°</b> instead of the point? It keeps your method and removes the flank.',
       'Can the LNL workshop turn a 0.4–0.5 mm aluminium wall? Can the targets group put 10–15 µm of copper on a flat aluminium '
       'face below ~150 °C, or would a plating shop do it?',
       'The <b>vacuum at the target</b> on the line you have in mind: pressure, residual gas, PVC or ceramic insulator. '
       'Can a film sit there for a week under beam while we watch the 478 keV and γ₀ lines?',
       'How thin can a rolled foil be made reproducibly (we would like 8–12 µm), and how is it carried from the glovebox to the line?',
       'The beam spot (σ and halo) at the target, as before.']
D.slide('end', sd.kicker('For Pierfrancesco: the questions of 11 Nov (they replace those of 4 Nov)') +
        sd.row(sd.col(*[sd.p(f'<b>{i + 1}</b> · {q}', 26, sd.DINK) for i, q in enumerate(ASK[:3])], gap=24),
               sd.col(*[sd.p(f'<b>{i + 4}</b> · {q}', 26, sd.DINK) for i, q in enumerate(ASK[3:])],
                      sd.p(f'The designs side by side: <a href="{CMP}" style="color:{sd.DBLUE}">notes/lnl-target-compare</a>. '
                           'The short version: notes/lnl-culiner-pf.', 22, sd.DMUT), gap=24), gap=72),
        notes=f'{rd.REVIEW} §7, replacing the questions of CU_LINER.md §9. The proposal has not yet been discussed with Pierfrancesco.',
        dark=True, short='for Pierfrancesco')

D.write(OUTF, note_meta=dict(title='LNL target: his ogive in Al with a Cu liner',
                             summary=f'Pierfrancesco’s ogive made of Al with 12 µm of Cu only where the beam stops and a masked Li film: '
                                     f'Geant4 L12 reach, PIXE and Micromegas x-rays, how to make it. Status {rd.DATE}: {V_THIS["label"]}, '
                                     'a flat Al end cap at 45° is proposed instead.',
                             tags='x17, lnl, target', date='2026-11-11'))
print(OUTF)
