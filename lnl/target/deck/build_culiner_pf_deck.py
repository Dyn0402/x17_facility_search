"""Short slide note for Pierfrancesco: where the LNL lithium target stands after the buildability review of 2026-11-11.

Until 10 Nov this deck presented his ogive in Al with a Cu patch and a masked, evaporated Li film (CU_LINER.md,
2026-11-04) as the proposal.  The review (TARGET_REVIEW.md, review_data.py) changed that, so the deck is now a short
update he can read cold: what we learned from how lithium targets are really made, how close his Cu ogive is with
today's detector, why the Li should be 10-12 µm, the proposed flat Al end cap at 45°, the two ogive versions that
need no new coating tools, and the questions of TARGET_REVIEW.md §7.  The 4 Nov design stays in the technical note
(build_culiner_deck.py).  Every day count and ratio comes from nd_reach_io / review_data, so a rebuild picks up runs
L13 and L14 (the cap is labelled an estimate until nd_reach_L14.csv exists).

Seven slides, figure-first.  Writes lnl/out/target/lnl-culiner-pf.html (the note) and lnl/out/target/lnl-culiner-pf.pdf
(one 1920 × 1080 page per slide, headless Chrome, to email):

    bash lnl/viz/render_culiner_shots.sh                       # 3D renders of the ogive → lnl/out/target/culiner_pf/*.jpg
    ~/PycharmProjects/nTof_x17/.venv/bin/python lnl/target/deck/build_culiner_pf_deck.py
    python3 ~/PycharmProjects/dylan-cern-site/scripts/add-note.py lnl/out/target/lnl-culiner-pf.html \\
        --slug lnl-culiner-pf --force --deploy
"""
import math
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.expanduser(os.environ.get('SLIDEDOC_DIR', '~/PycharmProjects/dylan-cern-site/scripts')))
import slidedoc as sd  # noqa: E402

HERE = Path(__file__).resolve().parent
LNL = HERE.parents[1]
sys.path.insert(0, str(LNL / 'target'))
import review_data as rd  # noqa: E402
sys.path.insert(0, str(LNL / 'target' / 'shapes'))
import nd_reach_io as nd  # noqa: E402
SH = LNL / 'out' / 'target' / 'shapes'
IMG = LNL / 'out' / 'target' / 'culiner_pf'
OUTF = LNL / 'out' / 'target' / 'lnl-culiner-pf.html'
PDF = OUTF.with_suffix('.pdf')
PAGE = 'https://dylan-neff.web.cern.ch/facilities/lnl-target.html'
CMP = 'https://dylan-neff.web.cern.ch/notes/lnl-target-compare.html'
NOTE = 'https://dylan-neff.web.cern.ch/notes/lnl-cu-liner.html'

GA = pd.read_csv(SH / 'geant_acceptance.csv')
CU, AL, LI, BEAM = sd.GOLD, '#8a96a8', sd.PURPLE, sd.RED
VCOL = {'propose': sd.GREEN, 'ok': sd.BLUE, 'later': sd.ORANGE, 'drop': sd.RED}
LI_COL = ((20, sd.RED), (15, sd.ORANGE), (12, sd.GREEN), (10, sd.BLUE))


def sig(cfg):
    q = GA[(GA.config == cfg + '_bigP') & (GA['sample'] == 'x17')]
    return float(q.sigma68_deg.iloc[0]) if len(q) else np.nan


# ---- the designs, and the numbers the slides quote (all from the reader) -------------------------------------------
CUP, CUOG, LINER4, LINER3 = 'dome300', 'ogCu200_tip', 'ogAl400cu12r8m4', 'ogAl300cu12r8m4'
CU_REF = ('ogCu200', 'ogCu200_tip')            # his Cu ogive: the Li film as simulated in L11, and Li pressed on the tip only
# the Al ogive with Cu plated over the whole inside and Li on the tip: 0.4 mm once run L14 has it, 0.3 mm until then
PLATED, PLATED_WALL = (('ogAl400cu12_tip', '0.4') if nd.has('ogAl400cu12_tip') else ('ogAl300cu12_tip', '0.3'))
CD = rd.cap_days()
CAP_SRC = 'Geant4 run L14' if CD['g4'] else 'estimate, Geant4 running'
CAP3 = (CD['big'], CD['asb'], CD['asb_ntof'])
V_LINER = rd.verdict(LINER3)


def cap3(sfx=''):
    """(big plastics, as built, as built with the liquid as at n_TOF) for the cap with a thinner Li film: Geant4 L14 when
    it has the row, else the 45° diamond window's (the stand-in review_data.cap_days uses)."""
    t = rd.CAP['tag'] + sfx
    return rd.days3(t if nd.has(t) else rd.CAP['proxy'] + sfx)


def times(vals, x='×'):
    """'×1.0–2.1' from a list of ratios"""
    vals = [v for v in vals if v == v]
    if not vals:
        return '–'
    a, b = f'{min(vals):.1f}', f'{max(vals):.1f}'
    return f'{x}{a}' if a == b else f'{x}{a}–{b}'


LIGHT = [rd.days3(LINER4), rd.days3(PLATED), CAP3]           # the light shells of the comparison slide
R_ASB = [rd.days3(c)[1] / d[1] for c in CU_REF for d in LIGHT]   # as built, liquid repaired: Cu ogive over light shell
R_ASB_NTOF = [rd.days3(c)[2] / d[2] for c in CU_REF for d in LIGHT]
R_BIG = [rd.days3(c)[0] / d[0] for c in CU_REF for d in LIGHT]
R_LINER = [rd.days3(c)[i] / rd.days3(t)[i] for c in CU_REF for t in (LINER4, LINER3) for i in (1, 2)]
R_CUP = rd.days3(CUP)[1] / rd.days3(CUOG)[1]


def stat(cfg):
    v = rd.verdict(cfg)
    return f'<span style="color:{VCOL[v["level"]]};font-weight:600;white-space:nowrap">{v["label"]}</span>'


def sent(t):
    """a review_data phrase as sentences: capitalised, clauses split at semicolons"""
    return '. '.join(q[0].upper() + q[1:] for q in t.split('; ')) + '.'


def pic(name, w=None, h=None, tip=None):
    return sd.img(IMG / f'{name}.jpg', w=w, h=h, tip=tip, fit='cover')


def cap(t, size=22):
    return sd.p(t, size, sd.MUT)


def kpi(v, label, color, tip=None):
    return (f'<div{sd.tipattr(tip)} style="flex:1;border-top:4px solid {color};padding-top:8px">'
            f'<p style="font-size:44px;font-weight:600;color:{color};line-height:1.05">{v}</p>'
            f'<p style="font-size:21px;color:{sd.MUT};line-height:1.25">{label}</p></div>')


def point(head, text, color):
    """a headline with two lines under it, coloured rule on top"""
    return (f'<div style="flex:1;border-top:4px solid {color};padding-top:12px;display:flex;flex-direction:column;gap:10px">'
            f'<p style="font-size:32px;font-weight:600;color:{color};line-height:1.15">{head}</p>'
            f'<p style="font-size:23px;color:{sd.INK};line-height:1.35">{text}</p></div>')


def bars2(rows, heads, label_w=450, width=300, size=22, h=30):
    """two bar panels sharing their labels.  rows: (label, colour, (value, text), (value, text), tip)"""
    vm = [max(r[2 + j][0] for r in rows if r[2 + j][0] == r[2 + j][0]) for j in (0, 1)]
    cell = f'width:{width + 250}px;display:flex;align-items:center;gap:14px'
    out = [f'<div style="display:flex;align-items:end;gap:24px"><p style="width:{label_w}px"></p>'
           + ''.join(f'<p style="width:{width + 250}px;font-size:{size + 2}px;font-weight:600;line-height:1.25">{t}</p>' for t in heads)
           + '</div>']
    for lab, c, a, b, tip in rows:
        cells = ''
        for j, (v, txt) in enumerate((a, b)):
            w = 0 if v != v else max(width * v / vm[j], 3)
            cells += (f'<div style="{cell}"><div style="width:{w:.0f}px;height:{h}px;background:{c};border-radius:6px"></div>'
                      f'<p style="font-size:{size}px;white-space:nowrap">{txt}</p></div>')
        out.append(f'<div{sd.tipattr(tip)} style="display:flex;align-items:center;gap:24px">'
                   f'<p style="width:{label_w}px;font-size:{size}px;font-weight:600;text-align:right;line-height:1.2">{lab}</p>{cells}</div>')
    return f'<div style="display:flex;flex-direction:column;gap:14px">{"".join(out)}</div>'


def cap_drawing(W=1000, H=500, s=11.0, li=LI):
    """the proposed flat Al end cap, cut along the beam (beam from the left).  To scale except the layers: the Al is
    drawn ×3, the Cu and Li films much thicker.  (The same drawing is in build_culiner_deck.py.)"""
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
                  'Li 10–12 µm along the beam: rolled foil, pressed on with flat moulds. Uniform along the beam by geometry'))
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


D = sd.Deck('LNL lithium target: where we stand, and a simpler proposal',
            f'A short update for Pierfrancesco ({rd.DATE}): what we learned from how lithium targets are really made, how close the Cu '
            'ogive is with today’s detector, why the Li should be 10–12 µm, a flat aluminium end cap at 45° that keeps the pressed-Li '
            'method, the ogive options, and our questions.')

# ---- 1. where this stands ----------------------------------------------------------------------------------------------
ST = sd.table(['design', 'where it stands', 'why'],
              [['<b>Flat Al end cap at 45°</b>, Cu stop, your pressed Li', stat(rd.CAP['tag']),
                'flat parts only, and the lithium is made the way you make it now'],
               ['Your Cu ogive, Li pressed on the tip', stat(CUOG), 'the simplest step up from the cup. We would electroform it in hard copper'],
               ['Al ogive, Cu plated over the whole inside, Li on the tip', stat(PLATED), 'plating Cu on Al has a precedent. No mask, no evaporator'],
               ['Al ogive, Cu at the tip only, Li evaporated through a mask (sent 4 Nov)', stat(LINER3),
                'three steps we found no precedent for. It gains little with today’s detector']],
              size=22, widths=[640, 350, 674], align=['left'] * 3)
D.slide('status',
        sd.title(f'Where this stands ({rd.DATE}): a simpler target than the one we sent on 4 Nov',
                 'We checked every design against how lithium targets are really made, at LNL and elsewhere. '
                 'This is what changed. It is a proposal for discussion, and we would like your view') +
        sd.row(point('Nothing in the beam pipe', 'On 4 Nov we meant a coating chamber. With your pressed lithium not even that is needed.', sd.BLUE),
               point(f'Your Cu ogive is close: {times(R_ASB)}', 'That is what the light shells gain on it with today’s detector. '
                     f'The {times(R_BIG)} needs the new calorimeter.', sd.BLUE),
               point('Li 10–12 µm, not 20', 'A 20 µm film that turns into LiOH brings the beam down to the 441 keV resonance.', sd.ORANGE),
               point('A flat face at 45°', 'One piece of aluminium, a Cu stop, your rolled lithium pressed on with flat moulds.', sd.GREEN),
               gap=32, align='stretch') +
        ST +
        sd.p(f'Every design side by side, with the numbers: <a href="{CMP}" style="color:{sd.BLUE}">dylan-neff.web.cern.ch/notes/lnl-target-compare.html</a>',
             22, sd.MUT),
        pad='84px 128px 100px',
        notes=f'Buildability review, {rd.REVIEW}. It has not yet been discussed with Pierfrancesco: this deck is how we put it to him. '
              f'Gains are days of his Cu ogive over days of a light shell (reference fit, 1 µA, 1.10 MeV, 20 µm of Li, liquid scintillator repaired), '
              f'for the Al ogive with Cu at the tip (0.4 mm), the Al ogive with Cu plated everywhere ({PLATED_WALL} mm) and the flat cap '
              f'({CAP_SRC}), and for both lithium films on the Cu ogive (as simulated, and pressed on the tip only). With the liquid as it ran at '
              f'n_TOF: {times(R_ASB_NTOF)}. The 4 Nov design alone, both walls and both liquid states: {times(R_LINER)}. '
              f'Status of the 4 Nov design: {V_LINER["label"]}.',
        short='where this stands')

# ---- 2. what we learned ------------------------------------------------------------------------------------------------
BASE = sd.table(['laboratory', 'how the lithium target is made', 'source'],
                [[f'<b>{lab.replace("Mastinu’s group", "your group")}</b>', how.replace('; ', '. '), src.replace('see §10', 'several papers')]
                 for lab, how, src in rd.BASELINE],
                size=20, widths=[230, 520, 190], align=['left'] * 3)
D.slide('learned',
        sd.title('What we learned from how you and others make lithium targets',
                 'Lithium metal is always made off the beam line, then carried to it under argon or under vacuum. '
                 'Nothing needs to be deposited in the beam pipe') +
        sd.row(sd.col(BASE, w=960),
               sd.col(sd.callout('<b>Your layout is the robust one.</b> A film on a metal stop that carries the heat lasts. '
                                 'The thin-film route broke at LNL: on AN2000 most LiF films gave 6–8 h of stable rate, the best two days. '
                                 'The one that lasted elsewhere, at MEG II, sat on 25 µm of copper.', sd.GREEN, 23),
                      sd.callout('<b>20 µm of rolled lithium pressed on copper is already your routine.</b> '
                                 'It is exactly our film and our stop, made without any evaporation.', sd.BLUE, 23),
                      sd.callout('<b>We do not need anything deposited in the beam pipe.</b> If our question of last week read that way, '
                                 'it was not what we meant: we had a coating chamber in mind. We found no laboratory that deposits Li, Cu or Ti on the line.',
                                 sd.BLUE, 23),
                      gap=26), gap=44),
        pad='84px 128px 100px',
        notes=f'{rd.REVIEW} §2 and §3, sources in its §10 (literature search of 11 Nov; quotes should be checked in the source before they go '
              f'into a talk). {rd.BEAM_PIPE} The closest thing to in-place deposition is Novosibirsk’s separate evaporation stand, whose target '
              'leaves under vacuum behind its own gate valve. Compound films (LiF, Li₂O, LiPON) are what the pair experiments chose for '
              'chemical stability. They pay ×4–8 in yield.',
        short='what we learned')

# ---- 3. the Cu ogive against the light shells -----------------------------------------------------------------------------
def brow(lab, cfg, d3=None, est=''):
    d3 = d3 or rd.days3(cfg)
    return (lab, VCOL[rd.verdict(cfg)['level']], (d3[1], f'<b>{nd.fmt(d3[1])} d</b> ({nd.fmt(d3[2])} d){est}'),
            (d3[0], f'<b>{nd.fmt(d3[0])} d</b>{est}'),
            f'{nd.fmt(d3[1])} d as built with the liquid scintillator repaired, {nd.fmt(d3[2])} d with the liquid as it ran at n_TOF, '
            f'{nd.fmt(d3[0])} d with the big plastics')


BR = [brow('Cu cup 300 µm, the target you have now', CUP),
      brow('Your Cu ogive 200 µm, Li on the tip', CUOG),
      brow('Al ogive 0.4 mm, Cu at the tip (sent 4 Nov)', LINER4),
      brow(f'Al ogive {PLATED_WALL} mm, Cu plated everywhere', PLATED),
      brow('Flat Al end cap at 45°', rd.CAP['tag'], CAP3, '' if CD['g4'] else ', estimate')]
D.slide('compare',
        sd.title(f'With today’s detector your Cu ogive is within a factor of {times(R_ASB, "")} of the light shells',
                 'Days of beam to 3σ at the ATOMKI strength, at 1 µA and 1.10 MeV, all with 20 µm of Li. '
                 'The light wall pays once the calorimeter is upgraded') +
        bars2(BR, ['As built: today’s detector, liquid scintillator repaired<br>'
                   f'<span style="font-weight:400;color:{sd.MUT};font-size:20px">in brackets: the liquid as it ran at n_TOF</span>',
                   'With the big plastics: the calorimeter upgrade<br>'
                   f'<span style="font-weight:400;color:{sd.MUT};font-size:20px">75 × 75 × 5 cm plastic walls, not funded yet</span>']) +
        sd.row(sd.callout(f'<b>The big step is yours: from the cup to the ogive, ×{R_CUP:.1f} as built.</b> On top of it the light shells gain '
                          f'{times(R_ASB)} today. The low end is inside what our simulation can resolve, and a larger one is running.', sd.BLUE, 23),
               sd.callout(f'<b>With the big plastics the light shells gain {times(R_BIG)}.</b> The detector then measures the pair energy well enough '
                          'for the cleaner opening angle to count. That is when the aluminium wall is worth its trouble.', sd.GREEN, 23),
               gap=40),
        pad='84px 128px 100px',
        notes=f'Days: nd_reach.csv through nd_reach_io.py ({nd.LABEL}; θ × |y| × E_sum; FEASIBILITY_SIM.md §19). They are statistics plus a '
              'floating background shape, at 1 µA with 20 µm of Li. Gains are days of the Cu ogive over days of each light shell, for both '
              'lithium films on the Cu ogive (as simulated in L11, and pressed on the tip only). '
              f'With the liquid as at n_TOF the gain is {times(R_ASB_NTOF)}. The 4 Nov design alone (0.3 and 0.4 mm walls, both liquid states): '
              f'{times(R_LINER)}. The cap: {CD["note"]}. ' + nd.ASB_NOTE +
              ' Colours: ' + ', '.join(f'{rd.LEVELS[k]}' for k in ('propose', 'ok', 'later')) + ' (green, blue, orange).',
        short='Cu ogive against the light shells')

# ---- 4. the Li thickness -------------------------------------------------------------------------------------------------
yr, t100 = rd.li_yield_rel(), rd.li_table()
CAP_G4_LI = nd.has(rd.CAP['tag'] + '_li12')
li_rows = []
for um, _c in LI_COL:
    sfx = '' if um == 20 else f'_li{um}'
    li_rows.append([f'<b>{um} µm</b>', sd.pct(yr[um]), sd.pct(float(t100.loc[um, 1.0]), 0 if t100.loc[um, 1.0] > 0.095 else 1),
                    ' / '.join(nd.fmt(x) for x in rd.days3(CUOG + sfx)[:2]), ' / '.join(nd.fmt(x) for x in cap3(sfx)[:2])])
li_tab = sd.table(['Li along the beam', 'γ₀ yield', '441 keV share if all of it is LiOH', 'days, your Cu ogive',
                   'days, flat Al cap' + ('' if CAP_G4_LI else ' (estimate)')], li_rows, size=20)
D.slide('lithick',
        sd.title('The lithium: 10–12 µm instead of 20',
                 'Residual water turns Li into LiOH. The lithium atoms stay, but the O and H add stopping, so the beam slows down '
                 'to the strong 441 keV resonance inside the film. This holds for every target, the cup and the ogive included') +
        sd.row(sd.col(li_plot(820, 480),
                      sd.legend([(f'Li {um} µm', c, 'line') for um, c in LI_COL], size=20), gap=4),
               sd.col(sd.callout(rd.LI['headline'], sd.RED, 23),
                      sd.callout(rd.LI['fix'] + ' You already roll foils below 10 µm.', sd.GREEN, 23),
                      li_tab,
                      sd.p('Days to 3σ at 1 µA, 1.10 MeV: big plastics / as built with the liquid repaired. ' + rd.LI['rate'], 20, sd.MUT),
                      gap=18, w=800), gap=44),
        pad='84px 128px 100px',
        notes=f'{rd.REVIEW} §4.2. review_li_conversion.py → out/target/options/review_li_conversion.csv: our yield model with PSTAR stopping, '
              'the outer fraction of the Li atoms converted to LiOH and the rest metal, at 1.10 MeV. Hover a point for the energy at which the '
              'beam leaves the film. The 441 keV resonance (17.64 MeV) is about 50× stronger than the 18.15 MeV one, so once the beam reaches it '
              'the 17.64 MeV pairs become most of what the detector sees. It did not matter for the neutron work, where the film’s energy loss '
              'only shapes the neutron spectrum. '
              + ('' if CAP_G4_LI else 'The cap column is an estimate until run L14 is in: the 45° diamond window’s Geant4 days with the thinner film. ')
              + 'What we would do: 10–12 µm, run at 1.10 MeV rather than 1.03, watch the γ₀ yield per µC (it rises as the beam reaches 441 keV), '
              'and measure the rate with one film on the line for a week before the run.',
        short='the lithium thickness')

# ---- 5. the proposal -----------------------------------------------------------------------------------------------------
pm, c12 = rd.CAP['press'], cap3('_li12')
k = sd.row(kpi(f'{nd.fmt(c12[0])} d', f'to 3σ at 1 µA with the big plastics and 12 µm of Li (20 µm: {nd.fmt(CD["big"])} d). {CAP_SRC[0].upper() + CAP_SRC[1:]}',
               sd.GREEN, CD['note']),
           kpi(f'{nd.fmt(c12[1])} d', f'as built with 12 µm of Li, liquid repaired (as at n_TOF: {nd.fmt(c12[2])} d. 20 µm: {nd.fmt(CD["asb"])} d). '
               f'{CAP_SRC[0].upper() + CAP_SRC[1:]}', sd.GREEN, CD['note']), gap=24)
k2 = sd.row(kpi(f'×{pm["t400"][1]}–{pm["t500"][1]}', 'margin at 1 bar for a 0.4–0.5 mm face over the Ø20 bore (estimate)', sd.INK,
                'clamped ellipse 20 × 28 mm, yield 276 MPa'),
            kpi(f'+{rd.CAP["heat_K"]["t400"][0]:.0f} K', 'across a 0.4 mm face at 1 µA, 1.1 W (estimate)', sd.INK,
                'radial conduction in the face'), gap=24)
D.slide('proposal',
        sd.title('Proposal: a flat aluminium end cap at 45°, with your pressed lithium',
                 'Your window idea at 45°, in plain aluminium: no diamond, no rings, no glue, no Mo. '
                 'Flat parts only, and the lithium goes on the way you put it on the cup') +
        sd.row(cap_drawing(), sd.col(k, k2, *[sd.p('• ' + sent(t), 21) for t in rd.CAP['pros'][:3]],
                                     sd.p('• Still open: ' + sent(rd.CAP['cons'][0]), 21, sd.MUT), gap=18, w=620), gap=44),
        pad='84px 128px 100px',
        notes=f'{rd.REVIEW} §6.1. {rd.CAP["stack"]}. Days: {CD["note"]}. The thinner film is a yield change on the same simulated events. '
              'At 1 µA the beam is 1.1 W, so the diamond’s heat conduction is not needed: a 0.4 mm aluminium face carries it with a few kelvin. '
              'The Cu K x-rays from the stop are absorbed in the 0.4–0.5 mm of aluminium. '
              'Also open: ' + ' '.join(sent(t) for t in rd.CAP['cons'][1:]) + f' Cost: {rd.CAP["cost"]}. '
              'The drawing is to scale except the layers (Al ×3, the films much thicker).',
        short='the proposal')

# ---- 6. if the ogive stays -------------------------------------------------------------------------------------------------
def ocard(head, cfg, text, days_note=''):
    c = VCOL[rd.verdict(cfg)['level']]
    return sd.card(sd.p(f'<b>{head}</b>', 25) +
                   f'<p style="font-size:21px;line-height:1.3">{stat(cfg)} <span style="color:{sd.MUT}">· {rd.fmt3(cfg)} d{days_note}</span></p>' +
                   sd.p(text, 22), pad=24, tip=f'{rd.verdict(cfg)["short"]}').replace('border:1px solid', f'border-left:6px solid {c};border:1px solid', 1)


D.slide('ogive',
        sd.title('If the ogive stays: two versions that need no new coating tools',
                 'Days: big plastics / as built / as built with the liquid as at n_TOF, at 1 µA with 20 µm of Li') +
        sd.row(sd.col(pic('d_his', w=700, h=516, tip='3D views from the target page: legs of accepted X17 pairs (Geant4)'),
                      cap('Top: your Cu ogive, every lepton crosses 200 µm of Cu (red). Bottom: the Al ogive, legs coloured by the Al they cross.', 20),
                      gap=8, w=700),
               sd.col(ocard('1 · Your Cu ogive, electroformed', CUOG,
                            'Hard copper grown on an aluminium mandrel, 200–250 µm. A spun, annealed 200 µm shell has only ×2–3 on buckling at 1 bar. '
                            'Li pressed on the tip cap only, so none sits on the steep flank.'),
                      ocard('2 · The Al ogive, 0.4 mm, Cu plated over the whole inside', PLATED,
                            'A thin sputtered seed or a zincate, then electroplated Cu to ≥ 12 µm at the tip, with an anode wire on the axis. '
                            'Li pressed on the tip. No mask and no evaporator.', f' ({PLATED_WALL} mm wall simulated)'),
                      ocard('What we sent on 4 Nov: Cu at the tip only, Li evaporated through a mask', LINER4,
                            'It needs a long sputtering run deep in the cone (7–30 h, estimate) and 0.8–5.4 g of lithium per coating. '
                            'Plating the whole inside loses nothing against it.', ' (0.4 mm wall)'),
                      gap=20), gap=40),
        pad='84px 128px 100px',
        notes=f'{rd.REVIEW} §6.3, §4.1, §4.7. Electroforming: CERN made a 200 µm-wall Cu chamber this way. Pressing a flat foil into a tip of '
              'R 2.8 mm stretches it, and lithium that overlaps the 65° flank is ×2.4 thicker along the beam. A disc that stays on the tip cap '
              '(r ≤ 2.5 mm) takes 55 % of a σ 2 mm beam. A rounder tip (R 6–8 mm) would take 95 %, which is a question for Pierfrancesco and '
              'needs a Geant4 check. '
              f'σ68 of the opening angle with the big plastics: Cu ogive {sig("ogCu200"):.1f}°, Al 0.4 mm {sig(LINER4):.1f}°. '
              f'The full study of the 4 Nov design, kept as the record: <a href="{NOTE}">notes/lnl-cu-liner</a>. '
              f'The interactive 3D views: <a href="{PAGE}">facilities/lnl-target.html</a>.',
        short='if the ogive stays')

# ---- 7. questions (TARGET_REVIEW.md §7) ---------------------------------------------------------------------------------------
ASK = ['How do you intend to put the lithium on your ogive: pressed foil with new moulds for the pointed tip, or evaporation? '
       'Your 2015 paper mentions a lithium evaporator. Does it work today, and how does a target leave it?',
       'Given how your group works, would you rather have a part on which your rolled and pressed lithium works directly?',
       'Would you consider a <b>flat face at 45°</b> instead of the point? It keeps your method and removes the flank.',
       'Can the LNL workshop turn a <b>0.4–0.5 mm aluminium wall</b>? Can the targets group put 10–15 µm of copper on a flat '
       'aluminium face below ~150 °C, or would a plating shop do it?',
       'The <b>vacuum at the target</b> on the line you have in mind: pressure, residual gas, PVC or ceramic insulator. '
       'Could a film sit there for a week under beam while we watch the 478 keV and γ₀ lines?',
       'How thin can a rolled foil be made reproducibly (we would like <b>8–12 µm</b>), and how is it carried from the glovebox to the line?',
       'The <b>beam spot</b> at the target, σ and halo, as before.']
D.slide('questions', sd.kicker('Your view?') +
        sd.row(sd.col(*[sd.p(f'<b>{i + 1}</b> · {q}', 26, sd.DINK) for i, q in enumerate(ASK[:3])], gap=26),
               sd.col(*[sd.p(f'<b>{i + 4}</b> · {q}', 26, sd.DINK) for i, q in enumerate(ASK[3:])], gap=26), gap=72) +
        sd.p(f'Every design side by side: <a href="{CMP}" style="color:{sd.DBLUE}">dylan-neff.web.cern.ch/notes/lnl-target-compare.html</a>'
             f' &nbsp;·&nbsp; Interactive 3D: <a href="{PAGE}" style="color:{sd.DBLUE}">dylan-neff.web.cern.ch/facilities/lnl-target.html</a>',
             22, sd.DMUT),
        notes=f'{rd.REVIEW} §7. To be clear about 4 Nov: we do not need anything deposited in the beam pipe (slide 2).',
        dark=True, short='questions')

D.write(OUTF, note_meta=dict(title='LNL target: where we stand, and a simpler proposal (short, for Pierfrancesco)',
                             summary='Seven slides: what we learned from how lithium targets are really made, the Cu ogive against the light '
                                     'shells with today’s detector, 10–12 µm of Li instead of 20, a flat aluminium end cap at 45° that keeps '
                                     'the pressed-Li method, the ogive options, and the questions.',
                             tags='x17, lnl, target', date='2026-11-11'))
print(OUTF)

# ---- PDF, one 1920 × 1080 page per slide ----------------------------------------------------------------------------------
pr_html = OUTF.with_name('lnl-culiner-pf.print.html')
body = '\n'.join(f'<div class="pg">{h}</div>' for _i, h, _n, _s in D.slides)
css = sd._CSS % dict(SANS=sd.SANS)
pr_html.write_text('<!doctype html><html><head><meta charset="utf-8">'
                   '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,400;0,600;1,400&display=swap">'
                   f'<style>{css}@page{{size:1920px 1080px;margin:0}}body{{background:#fff}}'
                   '.pg{position:relative;width:1920px;height:1080px;overflow:hidden;page-break-after:always}'
                   '.pg>section{position:absolute;inset:0;width:1920px;height:1080px;box-sizing:border-box}</style></head>'
                   f'<body>{body}</body></html>')
subprocess.run(['google-chrome', '--headless=new', '--no-sandbox', '--no-pdf-header-footer', '--virtual-time-budget=4000',
                f'--print-to-pdf={PDF}', pr_html.as_uri()], check=True, capture_output=True)
pr_html.unlink()
print(PDF)
