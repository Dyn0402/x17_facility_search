"""The practical half of the LNL target comparison (TARGET_OPTIONS §21): can each design be built, at what cost, how fast,
and with what margin.  Used by build_compare_deck.py:

    import practical_slides as PS
    PS.enrich(DES)                      # after the Geant4 numbers are attached to DES
    ... PS.strip(d) on each design slide ...
    PS.slides(D, DES)                   # before the closing slide

Data: lnl/out/target/options/practical*.csv from lnl/target/opt_practical.py (run it first if the parts or checks change).
"""
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.expanduser(os.environ.get('SLIDEDOC_DIR', '~/PycharmProjects/dylan-cern-site/scripts')))
import slidedoc as sd  # noqa: E402

OP = Path(__file__).resolve().parents[2] / 'out' / 'target' / 'options'
PR = pd.read_csv(OP / 'practical.csv').set_index('key')
PARTS = pd.read_csv(OP / 'practical_parts.csv')
CK = pd.read_csv(OP / 'practical_checks.csv')
FC = pd.read_csv(OP / 'practical_flat_chamber.csv').set_index('chamber_mm')
COMMON = ('Common to every design (not in the costs): Li evaporation at LNL; a fast-closing valve upstream (~5–10 k€ if LNL has '
          'none), because in every design the target or its chamber is the vacuum wall; 2–3 spare targets per campaign.')
DIFF = {1: 'easy', 2: 'routine', 3: 'some development', 4: 'specialist part + approval', 5: 'at the edge of what shops do'}


def mcol(m):
    return sd.GREY if not np.isfinite(m) else sd.RED if m < 2 else sd.GOLD if m < 3 else sd.GREEN


def dcol(n):
    return {1: sd.GREEN, 2: sd.GREEN, 3: sd.GOLD, 4: sd.RED, 5: sd.RED}[int(n)]


def fk(lo, hi):
    return f'{lo:.0f}–{hi:.0f}' if hi >= 1 else '< 1'


def nw(t):
    return f'<span style="white-space:nowrap">{t}</span>'


def enrich(DES):
    for d in DES:
        d['pr'] = PR.loc[d['key']].to_dict() if d['key'] in PR.index else None
        d['parts'] = PARTS[PARTS.key == d['key']]


def _tip(d):
    q = d['pr']
    parts = '; '.join(f'{r.part} ({r.who}: {fk(r.keur_lo, r.keur_hi)} k€, {r.weeks_lo:.0f}–{r.weeks_hi:.0f} wk)'
                      for r in d['parts'].itertuples())
    return (f'Parts: {parts}. 1 bar: as simulated ×{q["margin_sim"]:.1f} ({q["margin_sim_check"]}); as recommended '
            f'×{q["margin_rec"]:.1f} ({q["margin_rec_check"]}). Failure: {q["failure"]}. ESTIMATE (TARGET_OPTIONS §21).')


def strip(d):
    """one line for the design's own slide: cost, lead time, 1 bar margin, heat, gate."""
    q = d.get('pr')
    if q is None:
        return ''
    ms, mr = q['margin_sim'], q['margin_rec']
    marg = (f'×{mr:.1f}' if abs(ms - mr) < 0.05 else
            f'<span style="color:{mcol(ms)}">×{ms:.1f}</span> → <span style="color:{mcol(mr)}">×{mr:.1f}</span>')
    cells = [('build', f'{fk(q["keur_lo"], q["keur_hi"])} k€', sd.INK),
             ('lead time', f'{q["weeks_lo"]:.0f}–{q["weeks_hi"]:.0f} wk', sd.INK),
             ('1 bar margin', marg, mcol(mr)),
             ('Li at 4 µA', f'+{q["dT_4uA"]:.0f} K', sd.GREEN if q['dT_4uA'] < 100 else sd.RED),
             ('difficulty', f'{int(q["difficulty"])}/5', dcol(q['difficulty']))]
    inner = ''.join(f'<div style="flex:1"><p style="font-size:17px;color:{sd.MUT}">{a}</p>'
                    f'<p style="font-size:28px;font-weight:600;color:{c}">{b}</p></div>' for a, b, c in cells)
    gate = '' if q['gate'] == 'none' else f'<p style="font-size:20px;color:#c63d4f;margin-top:4px">gate: {q["gate"]}</p>'
    return (f'<div{sd.tipattr(_tip(d))} style="border-top:2px solid {sd.RULE};padding-top:10px;margin-top:14px">'
            f'<div style="display:flex;gap:14px">{inner}</div>{gate}'
            f'<p style="font-size:19px;color:{sd.MUT}">first: {q["first"]}</p></div>')


def slides(D, DES):
    ds = [d for d in DES if d.get('pr') is not None]

    # ---- 1. the table
    rows, tips = [], []
    for d in ds:
        q = d['pr']
        days = f'{d["days"]:.2f}' if np.isfinite(d['days']) else '—'
        ms, mr = q['margin_sim'], q['margin_rec']
        m = (f'<b style="color:{mcol(mr)}">×{mr:.1f}</b>' if abs(ms - mr) < 0.05 else
             f'<span style="color:{mcol(ms)}">×{ms:.1f}</span> → <b style="color:{mcol(mr)}">×{mr:.1f}</b>')
        rows.append([f'<span style="color:{d["color"]}">■</span> {d["name"]} <span style="color:{sd.MUT}">{d["sub"]}</span>',
                     days, m, f'+{q["dT_4uA"]:.0f} K', nw(fk(q['keur_lo'], q['keur_hi'])), nw(f'{q["weeks_lo"]:.0f}–{q["weeks_hi"]:.0f}'),
                     f'<b style="color:{dcol(q["difficulty"])}">{int(q["difficulty"])}</b>',
                     '—' if q['gate'] == 'none' else '<span style="color:#c63d4f">Be: safety approval</span>'])
        tips.append(_tip(d))
    tab = sd.table(['design', 'days/µA (Geant4)', '1 bar margin: simulated → to build', 'Li at 4 µA', 'k€', 'weeks',
                    'difficulty', 'gate'], rows, size=21, tips=tips,
                   align=['left', 'right', 'right', 'right', 'right', 'right', 'center', 'left'])
    D.slide('build', sd.title('Can we build it? Every design holds 1 bar and stays cool once three walls are thickened',
                              'Practical check per design (ESTIMATE): margin to failure at 1 bar, Li temperature rise at LNL\'s 4 µA, '
                              'first-unit cost and lead time, difficulty 1–5 (hover a row for the parts)') +
            tab + sd.p(COMMON, 18, sd.MUT),
            notes='<p>Margin = failure pressure (buckling, with a knockdown: 0.56 for tubes and cones, 0.2 for spheres) or strength '
                  '(yield; CVD diamond 280 MPa, the growth side in tension) over the 1 bar load. CERN practice asks ≥ 3 for buckling. '
                  '"Simulated" is the geometry Geant4 ran; "to build" is the change recommended here. Li rise: the full heat path '
                  'to the air at 4 µA (4.4 W at 1.10 MeV) with a fan (h = 100 W/m²/K); the Li must stay below ~150 °C. The 20 µm '
                  'Li runs at 0.12–0.5 µA, ×8–30 less heat. Costs are first-unit ranges from public prices and quotes, not quotes '
                  '(TARGET_OPTIONS §21; <code>opt_practical.py</code>).</p>',
            short='can we build it?')

    # ---- 2. physics against practicality
    P = sd.Plot(1500, 640, x=(0.3, 60, 'log'), y=(0.1, 4, 'log'), xlabel='first-unit cost, k€ (range midpoint; bar = range)',
                ylabel='days per µA to 3σ (Geant4)', margin=(20, 30, 90, 110))
    P.xticks([(v, f'{v:g}') for v in (0.5, 1, 2, 5, 10, 20, 50)])
    P.yticks([(v, f'{v:g}') for v in (0.1, 0.2, 0.5, 1, 2)])
    placed = []                                               # label y positions (log), to keep labels apart
    for d in sorted(ds, key=lambda d: d['days'] if np.isfinite(d['days']) else 0):
        q = d['pr']
        if not np.isfinite(d['days']):
            continue
        lo, hi = max(q['keur_lo'], 0.3), max(q['keur_hi'], 0.4)
        x = np.sqrt(lo * hi)
        y = d['days']
        P.raw(sd.line(P.X(lo), P.Y(y), P.X(hi), P.Y(y), dcol(q['difficulty']), 3))
        P.points([x], [y], d['color'], r=11, tips=[f'{d["name"]}, {d["sub"]}: {y:.2f} d/µA; {fk(q["keur_lo"], q["keur_hi"])} k€; '
                                                    f'{q["weeks_lo"]:.0f}–{q["weeks_hi"]:.0f} weeks; difficulty {int(q["difficulty"])} '
                                                    f'({DIFF[int(q["difficulty"])]}); gate: {q["gate"]}'])
        ly = y * 1.06
        while any(abs(np.log10(ly / v)) < 0.05 for v in placed):
            ly *= 1.12
        placed.append(ly)
        if ly / y > 1.07:                                     # moved up: a leader back to its dot
            P.raw(sd.line(P.X(x), P.Y(y), P.X(x * 1.07), P.Y(ly) + 4, d['color'], 1.5))
        P.text(x * 1.08, ly, f'{d["name"]} · {d["sub"].split(" (")[0]}', 17, sd.INK)
    D.slide('tradeoff', sd.title('Physics against practicality: the cheap, routine designs are also the fast ones',
                                 'Each dot is a design (its colour as on the other slides); the bar is the cost range, coloured by difficulty '
                                 '(green routine, gold development, red specialist + approval). Lower-left is best.') +
            P.svg('days per µA against first-unit cost') +
            sd.legend([('difficulty 1–2', sd.GREEN), ('3', sd.GOLD), ('4–5 (Be)', sd.RED)], size=19),
            notes='<p>Days per µA from the Geant4 runs of the deck (big plastics, 1.10 MeV). The Be variants buy little reach for '
                  '×3–10 the cost and a safety approval, so take them only if the cheaper version of the same idea is not '
                  'enough. ESTIMATE costs (TARGET_OPTIONS §21).</p>',
            short='physics vs practicality')

    # ---- 3. what the simulated geometries must change
    f04, f10 = FC.loc[0.4], FC.loc[1.0]

    def ck(key, frag):
        q = CK[(CK.key == key) & CK.check.str.contains(frag, regex=False)]
        return q.iloc[0]
    cf = ck('flat', '0.4 mm, 600')
    d2, d3 = ck('w45', 'diamond 200'), ck('w45', 'diamond 300')
    a2, a3 = ck('ogal', '200 µm: buckling'), ck('ogal', '300 µm: buckling')
    oc = ck('ogcu', 'buckling')
    wc = CK[(CK.key == 'w45') & CK.check.str.contains('glued')].iloc[0]
    wparts = dict(x.split(' ') for x in wc.note.split(', '))
    wnote = (f'diamond {wparts["disc"]} K, Ti rings {wparts["Ti_rings"]} K, joint {wparts["joint"]} K, '
             f'end piece {wparts["end_piece"]} K')
    items = [
        ('Flat target: the CFRP chamber', f'0.4 mm × 600 mm, as in L9, buckles at {cf.value:.2f} bar. Make it ≥ 1 mm and ≤ 300 mm long '
         f'(×{ck("flat", "1.0 mm, 300").margin:.0f}). Cost to the leptons (trace): σ68 {f04.sigma68_trace:.1f}° → {f10.sigma68_trace:.1f}°.', sd.RED),
        ('Windows: the diamond', f'200 µm over Ø20 carries {d2.value:.0f} MPa at its clamped edge: margin ×{d2.margin:.1f} on the weak '
         f'(growth) side. 300 µm: {d3.value:.0f} MPa, ×{d3.margin:.1f}. Geant4 L10: 0.28 against 0.27 d/µA. Order 300 µm.', sd.GOLD),
        ('Ogives: the wall', f'Al 200 µm buckles at {a2.value:.1f} bar; 300 µm at {a3.value:.1f}. Be: 7 → 20 bar. His Cu 200 µm: '
         f'{oc.value:.1f} bar, just under CERN\'s ×3.', sd.GOLD),
        ('Heat is not the limit anywhere', f'≤ 70 K at 4 µA in every design. In the window it is the Ti rings and the 55 mm end piece '
         f'that carry it ({wnote}), not the diamond: braze or glue makes no difference.', sd.GREEN),
        ('Targets are consumables', 'Where the beam stops, H builds up: Cu blisters after ~5 days at 1 µA, Ta/Mo after ≥ 16 (§5); '
         'diamond is untested. At the 0.12–0.5 µA the 20 µm Li needs, plan 2–3 spares per campaign.', sd.GOLD),
        ('The real gates', 'Be (end piece, hemisphere, ogive): LNL safety approval and a Be-shop quote, 3–6 months. Everything '
         'else is the LNL workshop plus one CVD-diamond vendor (8–14 weeks).', sd.DBLUE),
    ]
    body = ''.join(f'<div style="border-left:6px solid {c};padding-left:18px"><p style="font-size:28px;font-weight:600">{a}</p>'
                   f'<p style="font-size:23px;color:{sd.MUT};line-height:1.3">{b}</p></div>' for a, b, c in items)
    D.slide('fixes', sd.title('Three of the simulated geometries must change before they are built',
                              'Closed-form shell, plate and fin estimates; the LNL mechanical office should confirm by FEA') +
            f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:26px 48px">{body}</div>',
            notes='<p>Sources and formulas: TARGET_OPTIONS §20 (ogive shells) and §21 (all designs); outputs '
                  '<code>practical_checks.csv</code>, <code>practical_flat_chamber.csv</code>.</p>',
            short='what must change')
