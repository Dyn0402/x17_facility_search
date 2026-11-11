"""The lithium target as it stands after the buildability review of 11 Nov 2026 (lnl/target/TARGET_REVIEW.md).

The Geant4 reference of this deck was run with a thin Li₂O film in a CFRP chamber (the "baseline target"). The review
dropped that route and proposes 10–12 µm of lithium metal on a copper stop, on a flat aluminium end cap at 45° that
closes the beam pipe, with Pierfrancesco's Cu ogive as the simple fallback. This module holds

  * the dated slide "The target: where it stands (11 Nov 2026)" (``status_slide``), and
  * the few strings and numbers the other slide modules use to label the baseline and to quote the current options.

Nothing is typed in: verdicts, the cap's stack and the Li → LiOH table come from lnl/target/review_data.py, the days
from lnl/target/shapes/nd_reach_io.py (reference fit; the L13 / L14 / thin-Li rows win when their files exist), the
resolutions from lnl/out/target/shapes/geant_acceptance.csv. Until run L14 is in, the cap's days and resolution are
those of the 45° diamond window (same geometry) and every text says "estimate, Geant4 running".
"""
import math
import sys
from pathlib import Path

import pandas as pd

import slidedoc as sd

LNL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LNL / 'target'))
import review_data as RD  # noqa: E402

nd = RD.nd
SLIDE = 'target-status'
SHORT = 'Target status'
COMPARE = 'https://dylan-neff.web.cern.ch/notes/lnl-target-compare.html'
EP = 1100.0
BASE_TAG = 'base'                 # Li₂O 300 µg/cm² on Al 10 µm in the CFRP chamber: the Geant4 baseline of this deck
OGIVE_TAG = 'ogCu200_tip'         # Pierfrancesco's Cu ogive, 200 µm, Li on the tip only (how the review would build it)
THIN = 12                         # µm of Li along the beam: the thick end of the 10–12 µm the review asks for
BASE_TIP = ('The target the Geant4 reference of this deck was run with: a Li₂O film of 300 µg/cm² (1.5 µm) on 10 µm of '
            'aluminium, inside a carbon-fibre (CFRP) chamber with a 0.4 mm wall, the beam going on to a dump. '
            'It is not the target now proposed (review of 11 Nov 2026): see the slide "Target status".')


# --------------------------------------------------------------------------- #
# numbers
# --------------------------------------------------------------------------- #
def cap(li=None):
    """Days for the proposed end cap: big, asb (liquid repaired), asb_ntof, g4 (True once run L14 has the row), tag.
    ``li`` None is the 20 µm film of the Geant4 runs; 10 / 12 / 15 the thinner-Li yield variants."""
    if li is None:
        return RD.cap_days(EP)
    sfx = f'_li{li}'
    g4 = nd.has(RD.CAP['tag'] + sfx)
    tag = (RD.CAP['tag'] if g4 else RD.CAP['proxy']) + sfx
    b, a, an = RD.days3(tag, EP)
    return dict(big=b, asb=a, asb_ntof=an, g4=g4, tag=tag)


def est(c=None):
    """The label every quoted cap number carries."""
    c = c or cap()
    return 'Geant4 run L14' if c['g4'] else 'estimate, Geant4 running'


def span(key):
    """'0.31–0.43': the cap's days from 20 µm of Li to THIN µm (one number if the thin-Li row is missing)."""
    a, b = cap()[key], cap(THIN)[key]
    return nd.fmt(a) if b != b else f'{nd.fmt(a)}–{nd.fmt(b)}'


def sigma68(tag):
    """X17 opening-angle resolution σ68 (deg, big plastics) of a target-study configuration, NaN if not simulated."""
    g = pd.read_csv(nd.SH / 'geant_acceptance.csv')
    q = g[(g.det == 'bigP') & (g.config == f'{tag}_bigP') & (g['sample'] == 'x17')]
    return float(q.sigma68_deg.iloc[0]) if len(q) else math.nan


def cap_sigma():
    """(σ68 of the cap, True if it is the cap's own Geant4 run rather than the 45° diamond window's)."""
    s = sigma68(RD.CAP['tag'])
    return (s, True) if s == s else (sigma68(RD.CAP['proxy']), False)


def li_g0(um, ep=1100):
    """γ₀ per proton of a fresh metallic Li film (review_li_conversion.csv, the yield model of lnl_rates.py)."""
    d = pd.read_csv(RD.OPT / 'review_li_conversion.csv')
    d = d[(d.Ep_keV == ep) & (d['product'] == 'LiOH') & (d.converted == 0)].set_index('li_um')
    return float(d.g0_per_proton.loc[um])


# --------------------------------------------------------------------------- #
# strings for the other slides
# --------------------------------------------------------------------------- #
def base_term(word='baseline target'):
    return sd.term(word, BASE_TIP)


def link(text=None, color='inherit'):
    return (f'<a href="#{SLIDE}" style="color:{color};text-decoration:underline">'
            f'{text or "slide “" + SHORT + "”"}</a>')


def proposed_short():
    return '10–12 µm of lithium metal on a copper stop, on a flat aluminium end cap at 45° that closes the beam pipe'


def cap_days_text():
    """'0.31–0.43 d with big plastics, 4.2–5.5 d as built (liquid repaired), for 20 to 12 µm of lithium (estimate …)'."""
    thin = cap(THIN)['big'] == cap(THIN)['big']
    li = f'for 20 to {THIN} µm of lithium' if thin else 'for 20 µm of lithium'
    return (f'{span("big")} d with big plastics and {span("asb")} d as built with the liquid repaired, {li} '
            f'({est()})')


def sigma_text():
    s, own = cap_sigma()
    return f'{s:.1f}°' + ('' if own else ' (Geant4 of the same 45° geometry with a diamond face; run L14 in progress)')


# --------------------------------------------------------------------------- #
# the sketch: side view of the end cap
# --------------------------------------------------------------------------- #
AL, CU, LI, BEAM, LEP = sd.ORANGE, sd.GOLD, sd.BLUE, sd.RED, sd.PURPLE


def cap_svg():
    W, H = 800, 262
    cy, xc, R = 128, 460, 60          # axis, where the face crosses it, bore radius in px (6 px per mm, Ø20)
    x0 = xc - 270                     # the 55 mm end piece, shortened in the drawing
    q = 1 / math.sqrt(2)

    def P(a, o):                      # a along the face (down-right), o into the vacuum
        return xc + (a - o) * q, cy + (a + o) * q

    def strip(a0, a1, o0, o1, col, tip):
        pts = [P(a0, o0), P(a1, o0), P(a1, o1), P(a0, o1)]
        return (f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="{col}"'
                f'{sd.tipattr(tip)}/>')
    o = []
    # vacuum, collar, beam pipe
    o.append(f'<polygon points="{x0 - 170},{cy - R} {xc - R},{cy - R} {xc + R},{cy + R} {x0 - 170},{cy + R}" '
             f'fill="{sd.GREEN}" fill-opacity="0.08"{sd.tipattr("Vacuum: the beam pipe ends here. There is no target chamber.")}/>')
    for sgn in (-1, 1):
        y = cy + sgn * R
        o.append(f'<rect x="{x0 - 170}" y="{min(y, y + sgn * 34)}" width="170" height="34" fill="{sd.GREY}" fill-opacity="0.55"'
                 f'{sd.tipattr("Thick collar where the end piece joins the line, 50–60 mm upstream of the target: outside the cone the accepted leptons fly in.")}/>')
    o.append(sd.T(x0 - 85, cy + R + 56, 'collar, out of the', 18, sd.MUT))
    o.append(sd.T(x0 - 85, cy + R + 78, 'leptons’ view', 18, sd.MUT))
    wall = ('Aluminium 6061-T6 end piece, Ø20 bore, about 55 mm long, wall 0.5 mm, machined in one piece with the face. '
            'It is the vacuum wall, and the leptons that miss the face cross it.')
    o.append(f'<g{sd.tipattr(wall)}>' + sd.line(x0, cy - R, xc - R, cy - R, AL, 5) + sd.line(x0, cy + R, xc + R, cy + R, AL, 5) + '</g>')
    face = ('Flat face at 45° to the beam, aluminium 0.4–0.5 mm: ' + ', '.join(
        f'{k[1:4]} µm holds 1 bar with ×{v[1]:g} on yield' for k, v in RD.CAP['press'].items() if k in ('t400', 't500'))
            + ' (estimate, clamped ellipse 20 × 28 mm).')
    o.append(f'<g{sd.tipattr(face)}>' + sd.line(xc - R, cy - R, xc + R, cy + R, AL, 7) + '</g>')
    o.append(strip(-78, 70, 4, 11, CU, 'Copper, at least 12 µm along the beam (8.5 µm on the face): it stops the protons. '
                                       'An ordinary coating on a flat face, over the whole face. Thickness not to scale.'))
    o.append(strip(-34, 34, 11, 19, LI, 'Lithium metal, 10–12 µm along the beam: LNL’s rolled foil, pressed on with flat moulds. '
                                        'On a 45° face the film is equally thick along the beam everywhere. Thickness not to scale.'))
    # beam and two leptons
    xv = xc - 26
    o.append(sd.arrow(x0 - 190, cy, xv - 4, cy, BEAM, 4))
    o.append(sd.T(x0 - 150, cy - 12, 'p, 1.10 MeV', 20, BEAM, 'start'))
    for ang, lab, L in ((112, 'e⁺', 150), (-68, 'e⁻', 138)):
        a = math.radians(ang)
        x2, y2 = xv + L * math.cos(a), cy - L * math.sin(a)
        o.append(f'<g{sd.tipattr("A lepton of the pair. It leaves through the face or through the 0.5 mm wall of the end piece: that aluminium is what smears the opening angle.")}>'
                 + sd.arrow(xv, cy, x2, y2, LEP, 3) + '</g>')
        o.append(sd.T(x2 + 16, y2 + (4 if ang > 0 else 12), lab, 22, LEP, 'start'))
    # labels
    o.append(sd.T(x0 + 6, cy - R - 14, 'Al end piece, Ø20, wall 0.5 mm', 19, AL, 'start', 600))
    o.append(sd.T(x0 + 6, cy + 34, 'vacuum', 19, sd.GREEN, 'start'))
    xl = xc + R + 34
    for k, (txt, col) in enumerate((('Li 10–12 µm, pressed on', LI), ('Cu ≥ 12 µm, beam stop', CU),
                                    ('Al face 0.4–0.5 mm, 45°', AL), ('air outside', sd.MUT))):
        o.append(sd.T(xl, cy - 46 + 30 * k, txt, 19, col, 'start', 600 if k < 3 else 400))
    o.append(sd.T(W - 4, H - 4, 'side view, beam left → right; films not to scale', 17, sd.MUT, 'end'))
    return sd.svg(W, H, ''.join(o), 'the proposed target: a flat aluminium end cap at 45 degrees')


# --------------------------------------------------------------------------- #
# the slide
# --------------------------------------------------------------------------- #
NAMES = {
    'cap': 'a flat aluminium end cap at 45°, Cu stop, LNL’s rolled lithium pressed on',
    'cu_ogive': 'Pierfrancesco’s copper ogive, the simple fallback',
    'al_cu_plated': 'an aluminium ogive with copper plated over the whole inside',
    'cu_cup': 'the copper cup of LNL’s neutron line',
    'al_cu_liner': 'the aluminium ogive with a copper patch and masked, evaporated lithium (sent 4 Nov)',
    'al_ti': 'a titanium stop',
    'be': 'every beryllium shell',
    'mo': 'every molybdenum stop',
    'diamond': 'the diamond window',
    'thin_film': 'a thin Li₂O or LiF film in a chamber, the baseline of this deck',
}
GROUPS = [('propose', 'Proposed', sd.GREEN, ['cap']),
          ('ok', 'Buildable now', sd.BLUE, ['cu_ogive', 'al_cu_plated', 'cu_cup']),
          ('later', 'Possible, but a development project', sd.GOLD, ['al_cu_liner', 'al_ti']),
          ('drop', 'Dropped', sd.RED, ['thin_film', 'be', 'mo', 'diamond'])]


def _short(v):
    s = v['short']
    for pre in ('proposed: ', 'dropped: ', 'buildable now; '):
        s = s.removeprefix(pre)
    return s.replace('; ', ', ')


def verdict_list(size=21):
    keys = [k for g in GROUPS for k in g[3]]
    assert sorted(keys) == sorted(RD.VERDICT), 'review_data.VERDICT changed: update target_status.GROUPS'
    out = []
    for lev, lab, col, ks in GROUPS:
        assert all(RD.VERDICT[k]['level'] == lev for k in ks), f'a verdict level changed in review_data ({lev})'
        items = [f'{sd.term(NAMES[k], RD.VERDICT[k]["why"])} ({_short(RD.VERDICT[k])})' for k in ks]
        out.append(sd.callout(f'<b>{lab}:</b> ' + ', '.join(items) + '.', col, size))
    return out


def days_table(size=20):
    c20, c12 = cap(), cap(THIN)
    mark = '' if c20['g4'] else ' <span style="font-weight:400">(est.)</span>'

    def row(name, tag, d=None, bold=False, tip=None, m=''):
        b, a, an = (d['big'], d['asb'], d['asb_ntof']) if d else RD.days3(tag, EP)
        w = 'font-weight:600' if bold else ''
        return [f'<span style="{w}">{name}</span>', f'<span style="{w}">{nd.fmt(b)}{m}</span>',
                f'<span style="{w}">{nd.fmt(a)} / {nd.fmt(an)}{m}</span>'], tip
    rows = [row('Flat Al end cap at 45°, Li 20 µm', None, c20, True, RD.cap_days(EP)['note'], mark)]
    if c12['big'] == c12['big']:
        rows.append(row(f'the same, Li {THIN} µm', None, c12, True,
                        f'The Geant4 sample of the row above with the yields and line mix of a {THIN} µm film ({c12["tag"]}).', mark))
    rows.append(row('Cu ogive, Li 20 µm on the tip', OGIVE_TAG, tip=RD.VERDICT['cu_ogive']['why']))
    if nd.has(f'{OGIVE_TAG}_li{THIN}'):
        rows.append(row(f'the same, Li {THIN} µm', f'{OGIVE_TAG}_li{THIN}'))
    rows.append(row('Baseline of this deck: Li₂O film, chamber', BASE_TAG, tip=BASE_TIP + ' ' + RD.VERDICT['thin_film']['why']))
    return sd.table(['days to 3σ at 1 µA', 'big plastics', 'as built: liquid repaired / as at n_TOF'],
                    [r for r, _ in rows], size=size, widths=[400, 150, 250], tips=[t for _, t in rows])


def status_slide(D, NC=None):
    li = 100 * RD.li_table(int(EP))
    yr = RD.li_yield_rel(int(EP))
    c = cap()
    left = sd.col(
        cap_svg(),
        days_table(),
        sd.p(f'Reference fit with the background shape left free, 1.10 MeV, m<sub>X</sub> 16.8 MeV. '
             + ('The cap: Geant4 run L14.' if c['g4'] else
                'The cap’s days are an estimate: Geant4 of the same 45° geometry with a diamond face. Its own run (L14) is in progress.'),
             18, sd.MUT),
        gap=12, w=800)
    right = sd.col(
        *verdict_list(21),
        sd.callout(f'<b>Why 10–12 µm of lithium, not 20.</b> Residual water turns lithium into LiOH, which slows the beam more. '
                   f'With half of a 20 µm film converted, {li.loc[20, 0.5]:.0f} % of the 18 MeV photons come from the wrong '
                   f'resonance (441 keV). A {THIN} µm film stays at or below {li.loc[THIN, 1.0]:.0f} % even fully converted, for '
                   f'{100 * yr[THIN]:.0f} % of the yield. How fast this happens at LNL is not known: a one-week film test decides.',
                   sd.GREY, 20),
        sd.p(f'All designs side by side: <a href="{COMPARE}" style="color:{sd.BLUE}">lnl-target-compare</a>. '
             f'The review: <code style="font-size:19px">lnl/target/TARGET_REVIEW.md</code>.', 21),
        gap=13)
    base_cover = (f' The cover of this deck quotes ~{NC["bp_nd"]:.1f} and ~{NC["ab_nd"]:.0f} d for it, from the October fit '
                  f'(m<sub>X</sub> 16.7 MeV).' if NC else '')
    D.slide(SLIDE, sd.title('The target: where it stands (11 Nov 2026)',
                            f'Proposed: {proposed_short()}. No chamber and no thin Li₂O film. '
                            'This is our proposal after a buildability review. It has not yet been discussed with Pierfrancesco (LNL).')
            + sd.row(left, right, gap=40),
            f"""<p><b>What changed.</b> The Geant4 reference of this deck (October) was run around a thin Li₂O film
(300 µg/cm², 1.5 µm) on 10 µm of aluminium in a carbon-fibre chamber, the beam going on to a dump: ATOMKI's kind of target. Every
headline number of the other slides is for that <i>baseline target</i>. On 11 Nov 2026 a buildability review
(<code>lnl/target/TARGET_REVIEW.md</code>) checked all our target designs against how lithium targets are really made at LNL and
elsewhere. Its findings:</p>
<ul>
<li>{RD.BEAM_PIPE}</li>
<li>LNL's own routine ({RD.BASELINE[0][0]}, {RD.BASELINE[0][2]}): {RD.BASELINE[0][1]}. That is the film and the stop proposed
here, made without any evaporation.</li>
<li>The thin-film route is not a fallback at LNL. {RD.VERDICT['thin_film']['why']}</li>
<li>{RD.LI['headline']} {RD.LI['fix']} {RD.LI['rate']}</li>
<li>Dropped, beryllium. {RD.VERDICT['be']['why']}</li>
<li>Dropped, molybdenum stops. {RD.VERDICT['mo']['why']}</li>
<li>Dropped, the diamond. {RD.VERDICT['diamond']['why']}</li>
</ul>
<p><b>The proposed design.</b> {RD.CAP['name']}: {RD.CAP['stack']}. Cost {RD.CAP['cost']}.</p>
<p>For it:</p><ul>{''.join(f'<li>{x}</li>' for x in RD.CAP['pros'])}</ul>
<p>Against it:</p><ul>{''.join(f'<li>{x}</li>' for x in RD.CAP['cons'])}</ul>
<p>If the ogive is kept instead: first Pierfrancesco's copper ogive, electroformed in hard copper, with the lithium pressed on the
tip only. Then an aluminium ogive with copper plated over the whole inside.</p>
<p><b>The days.</b> Days to 3σ at the ATOMKI strength at 1 µA, from <code>lnl/out/target/shapes/nd_reach.csv</code> through
<code>nd_reach_io.py</code> (the reference fit in opening angle × energy split × energy sum with the background shape floating,
FEASIBILITY_SIM §19). The cap: {RD.cap_days(EP)['note']}. The {THIN} µm rows rescale the yields and the line mix of the same
Geant4 samples. {nd.ASB_NOTE}</p>
<p>In this table the baseline target needs {RD.fmt3(BASE_TAG, EP)} d (big plastics / as built with the liquid repaired / with the
liquid as at n_TOF).{base_cover} The cap is faster than the baseline although it scatters the leptons more (σ68 {sigma_text()}
against {sigma68(BASE_TAG):.1f}°), because {THIN} µm of lithium metal makes about ×{li_g0(THIN) / _base_g0():.0f} the photons of
the baseline film per proton.</p>
<p>Verdicts, the stack and the LiOH table: <code>lnl/target/review_data.py</code>
(<code>out/target/options/review_li_conversion.csv</code>). Hover a design in the list for the reason.</p>""",
            short=SHORT)


def _base_g0():
    y = pd.read_csv(LNL / 'out' / 'yields.csv').set_index('scenario')
    return float(y.loc['ATOMKI 2016 anomaly', 'Y_g0'])
