"""The practical half of the LNL target comparison: can each design be built, at what cost, how fast, with what margin.
Brought in line with the buildability review of 11 Nov 2026 (TARGET_REVIEW.md §4.6–§4.8, §5).  Used by
build_compare_deck.py:

    import practical_slides as PS
    PS.enrich(DES)                      # after the days (d['days3']) and the verdict (d['v']) are attached to DES
    ... PS.strip(d) on each design slide ...
    PS.slides(D, DES)                   # before the closing slide

Data: the 1 bar and heat checks of lnl/out/target/options/practical*.csv (lnl/target/opt_practical.py, TARGET_OPTIONS
§20–21); the costs, lead times and budget verdicts of TARGET_REVIEW.md §4.8 (BUDGET below, ESTIMATE); the verdicts,
the cap's pressure and heat numbers and the Li table from lnl/target/review_data.py.  Days are never typed in here:
they come from d['days3'] (nd_reach_io through review_data).
"""
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.expanduser(os.environ.get('SLIDEDOC_DIR', '~/PycharmProjects/dylan-cern-site/scripts')))
import slidedoc as sd  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'shapes'))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nd_reach_io as _nd  # noqa: E402  (days: the reference fit, FEASIBILITY_SIM.md §19)
import review_data as RV  # noqa: E402  (the 11 Nov review as data)

OP = Path(__file__).resolve().parents[2] / 'out' / 'target' / 'options'
PR = pd.read_csv(OP / 'practical.csv').set_index('key')
PARTS = pd.read_csv(OP / 'practical_parts.csv')
CK = pd.read_csv(OP / 'practical_checks.csv')
FC = pd.read_csv(OP / 'practical_flat_chamber.csv').set_index('chamber_mm')
COMMON = ('Common to every design (not in the costs): the lithium itself, rolled and pressed in LNL’s argon glovebox. '
          'A fast-closing valve upstream (5–10 k€ if LNL has none, not in the budget yet), because the target or its '
          'chamber is the vacuum wall. 2–3 spare targets per campaign.')

#: verdict level → colour, used for every badge in the deck
LVC = {'propose': sd.GREEN, 'ok': sd.BLUE, 'later': sd.GOLD, 'drop': sd.RED}

#: first-unit cost (k€: range for the plot, text for the tables), lead time and the budget verdict after the review
#: (TARGET_REVIEW.md §4.8; ESTIMATE, no quotes).  Keys are the design keys of build_compare_deck.DES.
BUDGET = {
    'cap':     dict(k=(0.3, 1.0), ks='&lt; 1', lead='1–3 weeks', note='fine: flat parts, any workshop'),
    'ogcu':    dict(k=(1.5, 5.0), ks='1.5–5', lead='2–6 weeks',
                    note='fine: electroformed in hard copper (about 0.5 k€ if done in-house)'),
    'ogalcu':  dict(k=(1.0, 4.0), ks='1–4 + plating', lead='3–8 weeks', note='fine. The time is in making it work'),
    'hemi':    dict(k=(0.0, 0.0), ks='0', lead='exists', note='nothing to buy: the CN neutron-line cup'),
    'ogalli':  dict(k=(1.0, 4.0), ks='1–4, parts only', lead='months',
                    note='the hidden cost: thin-film development at LNL, not costed'),
    'w45':     dict(k=(6.0, 15.0), ks='6–15', lead='8–16 weeks', note='affordable, not justified (a mounted diamond window)'),
    'w45wide': dict(k=(6.0, 15.0), ks='6–15', lead='8–16 weeks', note='affordable, not justified (a mounted diamond window)'),
    'w0':      dict(k=(6.0, 15.0), ks='6–15', lead='8–16 weeks', note='affordable, not justified (a mounted diamond window)'),
    'w45be':   dict(k=(26.0, 75.0), ks='26–75', lead='6–12 months',
                    note='no: the Be end piece alone is 20–60 k€, with no supplier since 2023'),
    'flat':    dict(k=(4.0, 15.0), ks='4–15', lead='8–14 weeks', note='fine on budget (the chamber line), dropped for other reasons'),
    'hemibe':  dict(k=(20.0, 60.0), ks='20–60', lead='6–12 months', note='no: no supplier of thin machined Be since 2023'),
    'ogbe':    dict(k=(20.0, 60.0), ks='20–60', lead='6–12 months', note='no: no supplier of thin machined Be since 2023'),
    'ogal':    dict(k=(1.0, 4.0), ks='1–4 + coating', lead='3–8 weeks + Mo development',
                    note='fine on budget, dropped for the Mo K x-rays'),
}
GATE = {'w45be': 'Be', 'hemibe': 'Be', 'ogbe': 'Be'}


def mcol(m):
    return sd.GREY if not np.isfinite(m) else sd.RED if m < 2 else sd.GOLD if m < 3 else sd.GREEN


def nw(t):
    return f'<span style="white-space:nowrap">{t}</span>'


def reason(v):
    """the verdict's one-line reason, without the level word it may start with (the badge already says it)."""
    s = v['short']
    for pre in ('proposed: ', 'dropped: ', 'buildable now; '):
        if s.startswith(pre):
            return s[len(pre):]
    return s


def pill(v, size=18, date=False):
    """the verdict badge: 'PROPOSED', 'BUILDABLE NOW', 'POSSIBLE, A DEVELOPMENT PROJECT', 'DROPPED'."""
    c = LVC[v['level']]
    t = v['label'].upper() + (' · 11 NOV' if date else '')
    return (f'<span{sd.tipattr(v["why"] + " (" + RV.REVIEW + ")")} style="display:inline-block;white-space:nowrap;background:{c};'
            f'color:#fff;font-size:{size}px;font-weight:600;letter-spacing:.6px;padding:.16em .7em;border-radius:999px">{t}</span>')


def _ck(key, frag):
    return CK[(CK.key == key) & CK.check.str.contains(frag, regex=False)].iloc[0]


def enrich(DES):
    """attach to each design: the CSV row (d['pr'], may be None), the review's budget line (d['bud']), the 1 bar margin
    as HTML (d['m1bar']) and as a number (d['m1']), the Li rise at 4 µA (d['dT4'], K) and a tooltip (d['ptip'])."""
    al300 = _ck('ogal', '300 µm: buckling')
    al_dt = float(_ck('ogal', 'Li rise at 4 µA, 300 µm').value)
    ep_dt = float(dict(x.split(' ') for x in _ck('w45', 'glued').note.split(', '))['end_piece'])   # the 0.5 × 55 mm Al end piece
    for d in DES:
        k = d['key']
        d['pr'] = q = PR.loc[k].to_dict() if k in PR.index else None
        d['parts'] = PARTS[PARTS.key == k]
        d['bud'] = BUDGET[k]
        if k == 'cap':
            (s4, m4), (s5, m5) = RV.CAP['press']['t400'], RV.CAP['press']['t500']
            d['m1'], d['m1bar'] = m4, f'<b style="color:{mcol(m4)}">×{m4:.1f}–{m5:.1f}</b>'
            d['dT4'] = RV.CAP['heat_K']['t400'][1] + ep_dt
            d['ptip'] = (f'1 bar on the flat face (clamped ellipse 20 × 28 mm, yield 276 MPa): 0.4 mm → {s4} MPa, ×{m4}; 0.5 mm → {s5} MPa, '
                         f'×{m5}; 0.3 mm → {RV.CAP["press"]["t300"][0]} MPa, ×{RV.CAP["press"]["t300"][1]} (too thin). Heat: '
                         f'+{RV.CAP["heat_K"]["t400"][0]:.0f} K across a 0.4 mm face at 1 µA (1.1 W), +{RV.CAP["heat_K"]["t400"][1]:.0f} K at 4 µA, '
                         f'plus the end piece. Cost: {RV.CAP["cost"]}. ESTIMATE (TARGET_REVIEW §6.1).')
        elif k in ('ogalcu', 'ogalli'):
            d['m1'], d['m1bar'] = float(al300.margin), f'<b style="color:{mcol(al300.margin)}">×{al300.margin:.1f}</b> at 0.3 mm'
            d['dT4'] = al_dt
            d['ptip'] = (f'1 bar: the Al 6061-T6 ogive at 0.3 mm buckles at {al300.value:.1f} bar (more at 0.4 mm). Li rise at 4 µA: '
                         f'+{al_dt:.0f} K (0.3 mm wall, fan). {BUDGET[k]["note"]}. ESTIMATE (TARGET_OPTIONS §20, TARGET_REVIEW §4.8).')
        else:
            if k == 'hemi':                                   # the cup that exists is 300 µm (the CN paper)
                c3 = _ck('hemi', 'Cu 300 µm (the CN cup) hemisphere R 11: membrane')
                ms = mr = float(c3.margin)
            else:
                ms, mr = q['margin_sim'], q['margin_rec']
            d['m1'] = mr
            d['m1bar'] = (f'<b style="color:{mcol(mr)}">×{mr:.1f}</b>' if abs(ms - mr) < 0.05 else
                          f'<span style="color:{mcol(ms)}">×{ms:.1f}</span> → <b style="color:{mcol(mr)}">×{mr:.1f}</b>')
            d['dT4'] = q['dT_4uA']
            parts = '; '.join(r.part for r in d['parts'].itertuples())
            d['ptip'] = (f'Parts as listed on 27 Oct: {parts}. 1 bar: as simulated ×{q["margin_sim"]:.1f} ({q["margin_sim_check"]}); '
                         f'thickened ×{q["margin_rec"]:.1f} ({q["margin_rec_check"]}). Failure: {q["failure"]}. Cost and lead time as '
                         f'revised on 11 Nov: {BUDGET[k]["ks"].replace("&lt;", "<")} k€, {BUDGET[k]["lead"]} ({BUDGET[k]["note"]}). ESTIMATE.')


def strip(d):
    """one line for the design's own slide: first-unit cost, lead time, 1 bar margin, heat, and the review's budget verdict."""
    b = d['bud']
    cells = [('first unit (estimate)', nw(f'{b["ks"]} k€'), sd.INK),
             ('lead time', b['lead'], sd.INK),
             ('1 bar margin', d['m1bar'], sd.INK),
             ('Li at 4 µA (4× the beam sheet)', f'+{d["dT4"]:.0f} K', sd.GREEN if d['dT4'] < 100 else sd.RED)]
    inner = ''.join(f'<div style="flex:1"><p style="font-size:16px;color:{sd.MUT}">{a}</p>'
                    f'<p style="font-size:24px;font-weight:600;color:{c};line-height:1.2">{v}</p></div>' for a, v, c in cells)
    gate = ('' if d['key'] not in GATE else
            f'<p style="font-size:18px;color:#c63d4f">gate: no supplier of machined Be vacuum parts since 2023, and LNL’s safety approval</p>')
    return (f'<div{sd.tipattr(d["ptip"])} style="border-top:2px solid {sd.RULE};padding-top:8px;margin-top:8px">'
            f'<div style="display:flex;gap:14px">{inner}</div>{gate}'
            f'<p style="font-size:18px;color:{sd.MUT}">budget (11 Nov review): {b["note"]}</p></div>')


def slides(D, DES):
    ds = list(DES)
    live = [d for d in ds if d['v']['level'] != 'drop']
    dropped = [d for d in ds if d['v']['level'] == 'drop']
    n_now = sum(d['v']['level'] in ('propose', 'ok') for d in ds)
    cap = next(d for d in ds if d['key'] == 'cap')
    est = ' (estimate)' if cap.get('est') else ''
    COLS3 = 'big plastics / as built with the liquid repaired / as built with the liquid as at n_TOF'

    # ---- 1. the table
    def tr(d):
        g = d['v']['level'] == 'drop'
        b = d['bud']
        dd = [_nd.fmt(x) for x in d['days3']]
        star = '*' if d.get('est') else ''
        cs = [f'{d["name"]} <span style="color:{sd.MUT};font-size:14px">{d["sub"]}</span>',
              f'{pill(d["v"], 12)} <span style="font-size:15px">{reason(d["v"])}</span>',
              dd[0] + star, dd[1] + star, dd[2] + star, d['m1bar'], nw(b['ks']), nw(b['lead'])]
        al = ['left', 'left', 'right', 'right', 'right', 'right', 'right', 'right']
        return (f'<tr{sd.tipattr(d["v"]["why"] + " " + d["ptip"])} style="{"color:" + sd.MUT if g else ""}">' +
                ''.join(f'<td style="text-align:{a};padding:.12em .45em;line-height:1.15">{c}</td>' for c, a in zip(cs, al)) + '</tr>')

    heads = ['design', 'verdict of the 11 Nov review', 'big plastics', 'as built, liquid repaired', 'as built, liquid as at n_TOF',
             '1 bar margin', 'first unit, k€', 'lead time']
    al = ['left', 'left', 'right', 'right', 'right', 'right', 'right', 'right']
    wd = [None, None, 92, 118, 126, 150, 150, 160]
    th = ''.join(f'<th style="text-align:{a};padding:.2em .45em;font-size:15px;line-height:1.15;{f"width:{w}px;" if w else ""}">{c}</th>'
                 for c, a, w in zip(heads, al, wd))
    div = (f'<tr><td colspan="8" style="padding:.5em .5em .2em;font-size:17px;font-weight:600;letter-spacing:1.5px;'
           f'text-transform:uppercase;color:{sd.RED};border-bottom:2px solid {sd.RED}">Dropped on 11 Nov, kept as a record</td></tr>')
    tab = (f'<table style="font-size:18px"><thead><tr>{th}</tr></thead><tbody>{"".join(tr(d) for d in live)}{div}'
           f'{"".join(tr(d) for d in dropped)}</tbody></table>')
    D.slide('build', sd.title(f'Can we build it? {n_now} designs can be built now. Only beryllium fails on budget',
                              'Days to 3σ at 1 µA in three columns, the margin at 1 bar, first-unit cost and lead time '
                              '(ESTIMATE; hover a row)') +
            tab + sd.p(('* The cap’s days are an estimate from the 45° diamond window, Geant4 run L14 is running. ' if cap.get('est') else '') +
                       COMMON, 17, sd.MUT),
            notes='<p>Every target but the beryllium ones costs 1–15 k€ against a 100–266 k€ budget. The real cost is people and '
                  'time in LNL’s thin-film lab, and that is what should decide (TARGET_REVIEW.md §4.8, 11 Nov 2026). Costs are '
                  'first-unit ranges from public prices, not quotes: the Cu ogive electroformed 1.5–5 k€ (about 0.5 k€ in-house), '
                  'the cap under 1 k€, a mounted 0.3 mm diamond window 6–15 k€ and 8–16 weeks (no mounted price is published), a '
                  'custom thin Be shell or end piece 20–60 k€ and 6–12 months (the estimate of 27 Oct was 5–25 k€ and 3–6 months, '
                  'before it was known that the last supplier of machined and welded Be vacuum tubes stopped in 2023).</p>'
                  '<p>Margin = failure pressure (buckling, with a knockdown: 0.56 for tubes and cones, 0.2 for spheres) or strength '
                  '(yield; CVD diamond 280 MPa, the growth side in tension) over the 1 bar load. CERN practice asks ≥ 3 for buckling. '
                  'An arrow goes from the geometry Geant4 ran to the thickened one. The cap: a clamped ellipse 20 × 28 mm, '
                  'Al 6061-T6 (TARGET_REVIEW §6.1). Heat is not shown here because it limits nothing: at 1 µA the beam is 1.1 W '
                  '(TARGET_OPTIONS §21; <code>opt_practical.py</code>).</p>'
                  '<p>The budget (<code>budget/items.py</code>) was brought in line on 11 Nov: the CFRP chamber line became the '
                  'target end caps (Al caps 2–6 k€ for about five, or Cu ogives 3–15 k€ as the fallback), the lithium line is LNL’s '
                  'rolled Li metal, and a fast-closing valve upstream (5–10 k€ if LNL has none) was added because the cap is the '
                  'vacuum wall. The self-sufficient and upgrade totals rose by about 3.5 k€.</p>'
                  f'<p>{_nd.ASB_NOTE}</p>',
            short='can we build it?')

    # ---- 2. physics against practicality: the three day columns per design, with the cost beside them
    n = len(ds)
    rowh = 37
    P = sd.Plot(1664, rowh * n + 44 + 96, x=(0.1, 60, 'log'), y=(0, n + 1.15),
                xlabel='days to 3σ at the ATOMKI strength, 1 µA, 1.10 MeV (reference fit, background shape floating)',
                margin=(8, 330, 88, 430))
    ticks = (0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50)
    P.xticks([(v, f'{v:g}') for v in ticks])
    for v in ticks:
        P.raw(sd.line(P.X(v), P.y0, P.X(v), P.y0 + P.ph, sd.RULE, 1), back=True)
    xr = P.x0 + P.pw + 16
    P.raw(sd.T(xr, P.Y(n + 0.62), 'first unit · lead time (estimate)', 18, sd.MUT, 'start'))
    yy = float(n + 0.15)
    for grp, is_drop in ((live, False), (dropped, True)):
        if is_drop:
            yd = P.Y(yy - 0.42)
            P.raw(sd.line(P.x0 - 420, yd, P.w - 10, yd, sd.RED, 2))
            P.raw(sd.T(P.x0 - 420, yd + 24, 'DROPPED ON 11 NOV', 16, sd.RED, 'start', 600))
            yy -= 1.0
        for d in grp:
            yy -= 1.0
            y = P.Y(yy + 0.5)
            c = LVC[d['v']['level']]
            b = d['bud']
            v3 = d['days3']
            fin = [x for x in v3 if np.isfinite(x)]
            P.raw(sd.T(P.x0 - 14, y + 7, d['short'] + (est if d['key'] == 'cap' else ''), 20, sd.MUT if is_drop else sd.INK, 'end',
                       600 if d['key'] == 'cap' else 400))
            if len(fin) > 1:
                P.raw(sd.line(P.X(min(fin)), y, P.X(max(fin)), y, c, 2, extra=' opacity=".45"'))
            tip0 = f'{d["name"]}, {d["sub"]}: ' + ' / '.join(_nd.fmt(x) for x in v3) + f' d ({COLS3}). {d["v"]["label"]}: {reason(d["v"])}.'
            for x, mk, r in zip(v3, ('circle', 'diamond', 'open'), (9, 7, 8)):
                if np.isfinite(x):
                    P.points([x], [yy + 0.5], c, r=r, tips=[tip0], marker=mk)
            P.raw(sd.T(xr, y + 7, f'{b["ks"]} k€ · {b["lead"]}', 19, sd.RED if d['key'] in GATE else (sd.MUT if is_drop else sd.INK), 'start'))
    asb = {d['key']: d['days3'][1] for d in ds if np.isfinite(d['days3'][1])}
    best_drop = min(asb[d['key']] for d in dropped if d['key'] in asb)
    ratio = asb['cap'] / best_drop
    gain = (f'as built, the dropped designs buy at most ×{ratio:.1f} over the cap{est}' if ratio > 1.05 else
            'as built, none of the dropped designs beats the cap')
    D.slide('tradeoff', sd.title(f'Physics against practicality: {gain}',
                                 'One row per design. Colour is the review’s verdict. The cost and lead time are at the right') +
            P.svg('days to 3σ per design in three detector states, with first-unit cost and lead time') +
            sd.legend([('big plastics', sd.INK, 'dot'), ('as built, liquid scintillator repaired (◆)', sd.INK, 'box'),
                       ('as built, liquid as it ran at n_TOF', sd.INK, 'open'),
                       ('proposed', LVC['propose'], 'box'), ('buildable now', LVC['ok'], 'box'),
                       ('a development project', LVC['later'], 'box'), ('dropped', LVC['drop'], 'box')], size=19),
            notes='<p>Days to 3σ at the ATOMKI strength, 1 µA, 1.10 MeV, from the reference fit (<code>nd_reach.csv</code>, '
                  'FEASIBILITY_SIM.md §19; interim until run L13 is folded in). Circle: MX17 with the big plastics. Diamond: the '
                  'detector as built with the liquid scintillator repaired. Open circle: as built with the liquid as it ran at '
                  'n_TOF. The flat target in a chamber was simulated with the big plastics only.</p>'
                  '<p>With the detector we have, the light walls gain little: the as-built points of the live options and of '
                  'the dropped ones overlap. The big gains of the light designs exist with the big plastics, which are the '
                  '266 k€ budget. So the as-built comparison is what changed the verdict on the Cu ogive: it is within a '
                  'factor of about 1.5 of anything that can be built quickly (TARGET_REVIEW.md §4.1). ' +
                  ('The cap’s row is an estimate: the 45° diamond window’s Geant4 days, the same geometry. Geant4 run L14 is running. '
                   if cap.get('est') else 'The cap’s row is Geant4 run L14. ') +
                  f'{_nd.ASB_NOTE}</p>'
                  '<p>Costs: TARGET_REVIEW.md §4.8, ESTIMATE. The beryllium designs are the only ones the budget rules out '
                  '(20–60 k€ and 6–12 months for a custom thin shell, and no supplier since 2023).</p>',
            short='physics vs practicality')

    # ---- 3. what must change before a target is built
    a2, a3 = _ck('ogal', '200 µm: buckling'), _ck('ogal', '300 µm: buckling')
    oc = _ck('ogcu', 'buckling')
    cf = _ck('flat', '0.4 mm, 600')
    d2, d3 = _ck('w45', 'diamond 200'), _ck('w45', 'diamond 300')
    li = 100 * RV.li_table(1100)
    yr = RV.li_yield_rel(1100)
    pr_ = RV.CAP['press']
    hk = RV.CAP['heat_K']
    dtmax = max(d['dT4'] for d in ds)
    items = [
        ('Every design: thinner lithium',
         f'Half of a 20 µm film turned to hydroxide puts {li.loc[20, 0.5]:.0f} % of the γ₀ on the 441 keV resonance. A 12 µm film '
         f'stays at {li.loc[12, 1.0]:.0f} % even fully converted, for {100 * yr[12]:.0f} % of the yield. A one-week film test at '
         f'LNL decides the thickness.', sd.RED),
        ('Cu ogive: hard copper',
         f'At 200 µm, soft annealed copper buckles at {oc.value:.1f} bar, just under CERN’s margin of 3. Electroform it in hard '
         f'copper on an aluminium mandrel, or make it 0.25 mm. Press the Li on the tip cap only.', sd.GOLD),
        ('Al ogives: the wall',
         f'Al 200 µm buckles at {a2.value:.1f} bar, 300 µm at {a3.value:.1f}. Build 0.4 mm: it also stops the Cu K x-rays. '
         f'Turned 6061 is comfortable at 0.5–0.8 mm, so plan one or two scrapped parts.', sd.GOLD),
        ('The flat cap: the face',
         f'Over a Ø20 bore, 0.4 mm of Al 6061-T6 carries 1 bar at {pr_["t400"][0]} MPa (margin ×{pr_["t400"][1]}), 0.5 mm at '
         f'{pr_["t500"][0]} MPa (×{pr_["t500"][1]}). 0.3 mm is too thin (×{pr_["t300"][1]}). Coat the copper cool: 6061-T6 softens '
         f'above about 200 °C.', sd.GREEN),
        ('Heat is not the limit anywhere',
         f'At 1 µA the beam is 1.1 W. The cap’s face rises {hk["t400"][0]:.0f} K, and no design passes {dtmax:.0f} K even at '
         f'4 µA. This is why the diamond is not needed.', sd.GREEN),
        ('Hydrogen in copper: watch it',
         'The "blisters after 5 days" came from much higher current densities. MEG II stopped 8–11 µA in 25 µm of Cu for four '
         'weeks without damage. A 12 µm Cu film is the weak case, so prefer plated-through or foil copper, and plan 2–3 spares.',
         sd.BLUE),
    ]
    body = ''.join(f'<div style="border-left:6px solid {c};padding-left:18px"><p style="font-size:28px;font-weight:600">{a}</p>'
                   f'<p style="font-size:23px;color:{sd.MUT};line-height:1.3">{b}</p></div>' for a, b, c in items)
    D.slide('fixes', sd.title('What must change before a target is built: thinner lithium, hard copper, a 0.4 mm aluminium wall',
                              'Closed-form shell, plate and fin estimates (ESTIMATE). The LNL mechanical office should confirm by FEA') +
            f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:26px 48px">{body}</div>',
            notes='<p>Sources: TARGET_REVIEW.md §4.2 (lithium to hydroxide, <code>review_li_conversion.csv</code>), §4.7 (the Cu '
                  'ogive’s buckling margin, electroforming, pressing a foil into the tip, hydrogen in copper), §6.1 (the cap: '
                  'Roark’s clamped ellipse, radial conduction); TARGET_OPTIONS §20–21 (<code>practical_checks.csv</code>).</p>'
                  '<p>The tip of the ogive is a sphere of R 2.8 mm. A flat foil pressed into it thins unevenly, and whatever '
                  'overlaps the 65° flank is ×2.4 thicker along the beam. A disc that stays on the tip cap (r ≤ 2.5 mm) takes '
                  '55 % of a σ 2 mm beam. A flat face does not have this problem.</p>'
                  f'<p>Kept as a record, for designs dropped on 11 Nov: the 0.4 mm × 600 mm CFRP chamber of run L9 buckles at '
                  f'{cf.value:.2f} bar (≥ 1 mm and ≤ 300 mm long holds, trace σ68 {FC.loc[0.4].sigma68_trace:.1f}° → '
                  f'{FC.loc[1.0].sigma68_trace:.1f}°). A 200 µm diamond over Ø20 carries {d2.value:.0f} MPa at its clamped edge '
                  f'(margin ×{d2.margin:.1f}), 300 µm {d3.value:.0f} MPa (×{d3.margin:.1f}). Be shells: ×7 at 200 µm, ×20 at 300 µm.</p>',
            short='what must change')
