"""Build the target-options slide note (lnl/target/TARGET_OPTIONS.md).

Reads lnl/out/target/options/ (opt_thermal.py, opt_backing.py, opt_rates.py, opt_monitor.py,
opt_geant.py) and the buildability review of 11 Nov 2026 (review_data.py: verdicts, the proposed Al end cap, the
Li → LiOH table; days from nd_reach_io), writes lnl/out/target/lnl-target-options.html:

    ~/PycharmProjects/nTof_x17/.venv/bin/python lnl/target/deck/build_options_deck.py
    python3 ~/PycharmProjects/dylan-cern-site/scripts/add-note.py \\
        lnl/out/target/lnl-target-options.html --slug lnl-target-options --force --deploy
"""
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.expanduser(os.environ.get(
    'SLIDEDOC_DIR', '~/PycharmProjects/dylan-cern-site/scripts')))
import slidedoc as sd  # noqa: E402
from slidedoc import sci  # noqa: E402

HERE = Path(__file__).resolve().parent
O = HERE.parents[1] / 'out' / 'target' / 'options'
TS = pd.read_csv(O / 'thermal_scan.csv')
TL = pd.read_csv(O / 'thermal_limits.csv')
TSEN = pd.read_csv(O / 'thermal_sensitivity.csv')
ST = pd.read_csv(O / 'stacks.csv').set_index('stack')
HY = pd.read_csv(O / 'hydrogen.csv')
LC = pd.read_csv(O / 'li_chemistry.csv')
CS = pd.read_csv(O / 'carbon_shift.csv')
PG = pd.read_csv(O / 'pige.csv')
AW = pd.read_csv(O / 'al_window.csv')
RO = pd.read_csv(O / 'rates_options.csv')
GT = pd.read_csv(O / 'g4tendl_check.csv')
GR = pd.read_csv(O / 'geant_reach.csv') if (O / 'geant_reach.csv').exists() else None   # L9 scan: statistics-only, relative
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'shapes'))
import nd_reach_io as nd  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import review_data as rd  # noqa: E402
D_REC_ND = nd.best('li20_mo8_dia50', 'bigP', 1100)
D_REC_L9 = (float(GR.set_index('config').loc['li20_mo8_dia50', 'days_ref_1uA'])
            if GR is not None and 'li20_mo8_dia50' in set(GR.config) else float('nan'))
L9_NOTE = ('Days on the Geant4 L9 slide: a statistics-only fit (norms free), kept as a relative comparison of the L9 options. '
           'The flat Li / Mo / diamond design recommended on 22 Oct (dropped 11 Nov), re-run with the reference fit '
           f'(background shape floating, FEASIBILITY_SIM.md §19, 10 Nov 2026), gives {nd.fmt(D_REC_ND)} d per µA '
           f'(statistics only: {nd.fmt(D_REC_L9)}).')
GA = pd.read_csv(O / 'geant_acceptance.csv') if (O / 'geant_acceptance.csv').exists() else None

# --- the 11 Nov 2026 buildability review (TARGET_REVIEW.md), from review_data.py -------------------------------- #
COMPARE = 'lnl-target-compare.html'    # the comparison deck sits beside this note, locally and on the site
LVL = {'propose': sd.GREEN, 'ok': sd.BLUE, 'later': sd.GOLD, 'drop': sd.RED}
CD = rd.cap_days()
CAP_SRC = 'Geant4 run L14' if CD['g4'] else 'estimate, Geant4 running'
CAP_DAYS = (f'{nd.fmt(CD["big"])} d with the big plastics, {nd.fmt(CD["asb"])} / {nd.fmt(CD["asb_ntof"])} d as built '
            f'(liquid repaired / as at n_TOF)')
LIY = rd.li_yield_rel(1100)             # fresh γ₀ per proton relative to 20 µm
LIS, LIE = rd.li_table(1100), rd.li_eout(1100)       # 441 keV share and exit energy, by thickness and LiOH fraction
LIS03 = rd.li_table(1030)
HEAT_K = rd.CAP['heat_K']['t400']       # centre-to-edge rise of a 0.4 mm Al face at 1.1 W / 4.4 W
NOT_DISCUSSED = 'The review is a proposal. It has not yet been discussed with Pierfrancesco.'


def pc(x, d=0):
    """a fraction as '52 %' (the decks' style, with a space)"""
    return f'{100 * x:.{d}f} %'


def badge(level, text=None):
    c = LVL[level]
    return (f'<span style="display:inline-block;padding:1px 12px;border-radius:999px;border:2px solid {c};color:{c};'
            f'font-weight:600;white-space:nowrap">{text or rd.LEVELS[level]}</span>')


def link(text=None, color=sd.BLUE):
    return f'<a href="{COMPARE}" style="color:{color}">{text or "lnl-target-compare"}</a>'


def thin_days():
    """days3 by Li thickness (µm along the beam) for the cap if Geant4 L14 has every row, else for its stand-in, the
    45° window; (label of the source, {µm: (big, as built repaired, as built n_TOF)})"""
    sfx = {20: '', 15: '_li15', 12: '_li12', 10: '_li10'}
    tag = rd.CAP['tag']
    if not all(nd.has(tag + x) for x in sfx.values()):
        tag = rd.CAP['proxy']
        lab = 'the 45° window, Geant4 L10, as a stand-in for the cap'
    else:
        lab = 'the Al end cap, Geant4 L14'
    return lab, {um: rd.days3(tag + x) for um, x in sfx.items() if nd.has(tag + x)}

LI, DIA, TA, AL, CU, HEAT, OK, BAD = sd.BLUE, sd.PURPLE, sd.GREY, sd.ORANGE, sd.GOLD, sd.ORANGE, sd.GREEN, sd.RED
BASE = 'Li2O 300 / Al 10 µm (FEAS baseline)'
PF = 'Li 20 µm / diamond 1 mm (Pierfrancesco)'
REC = 'Li 20 µm / Ta 10 µm / diamond 1 mm'
gain = ST.loc[PF, 'rel_g0_vs_baseline']
f441_pf = ST.loc[PF, 'f441']


def tlim(key, sig=2.0):
    q = TL[(TL.key == key) & (TL.sigma_mm == sig)]
    return float(q.I_max_uA.iloc[0])


def tfilm(key, I, sig=2.0):
    q = TS[(TS.key == key) & (TS.sigma_mm == sig) & np.isclose(TS.I_uA, I)]
    return float(q.T_film_C.iloc[0])


I_F = tlim('F_dia1000_li20_clamp')
I_G = tlim('G_dia1000_li20_braze')
I_H = tlim('H_dia_mch_li20')
I_A = tlim('A_al10_disk')

D = sd.Deck('Target options for MX17 at LNL',
            'Film, backing, cooling, vacuum and monitoring for the ⁷Li(p,e⁺e⁻)⁸Be target: thermal model, nuclear yields '
            'from measured data, and Geant4 of the target assembly. Status of 11 Nov 2026: the lithium film and the '
            'physics hold, the Mo layer and the diamond are dropped.')

# --------------------------------------------------------------------------- #
# cover
big3 = sd.bignum(f'{nd.fmt(CD["big"])} d', 'per µA to 3σ at ATOMKI: the aluminium end cap now proposed, big plastics', sd.DGREEN,
                 f'as built {nd.fmt(CD["asb"])} / {nd.fmt(CD["asb_ntof"])} d (liquid repaired / as at n_TOF) · {CAP_SRC}',
                 tip=CD['note'])
cover = (sd.kicker('MX17 at LNL · target options · 22 Oct 2026 · status 11 Nov 2026')
         + '<h1 style="font-size:50px;font-weight:600;line-height:1.12;letter-spacing:-1.2px">'
           'Metallic lithium is the right film and at LNL the heat is easy: both still hold. The 22 Oct recommendation, '
           'lithium on molybdenum on a thin diamond, is superseded. The Mo and the diamond were dropped on 11 Nov, and the '
           'film should be 10–12 µm until its chemistry in the beam-line vacuum is measured.</h1>'
         + sd.p('A thermal model of every backing, nuclear yields from measured data for what the film and backing emit, '
                'and Geant4 (run L9) of the leptons through the target assembly. Slide 2 gives the status after the '
                'buildability review of 11 Nov and the design now proposed.', 26, sd.DMUT)
         + sd.row(
             sd.bignum(f'×{gain:.1f}', '⁸Be γ₀ per proton, 20 µm Li vs 1.5 µm Li₂O', sd.DBLUE,
                       f'still holds; 10–12 µm keeps {100 * LIY[10]:.0f}–{pc(LIY[12])} of it'),
             sd.bignum(f'+{HEAT_K[0]:.0f} K', 'across a 0.4 mm aluminium face at 1 µA (1.1 W)', '#f0a35e',
                       'the heat is a conduction-path problem; no diamond is needed (estimate, radial conduction)'),
             big3, gap=56)
         + sd.p(L9_NOTE, 20, '#f0a35e'))
D.slide('cover', cover, f'''
<p>Pierfrancesco's reply to the LNL slides: the target is the critical issue. No fluorine; heat; the backing's background
and the best backing; a cold trap for carbon; PIGE monitoring; the 441 keV γ and the window; the strip/clamp design; and his
proposal of 20 µm Li on 1 mm diamond with micro-channel cooling. Each slide answers one of these. Write-up:
<code>lnl/target/TARGET_OPTIONS.md</code>; the earlier fluorine/heat study is the note <code>lnl-lithium-target</code>.</p>
<p>Updated 11 Nov 2026 with the buildability review (<code>lnl/target/TARGET_REVIEW.md</code>). The study's first
recommendation (20 µm Li / Mo 8 µm / CVD diamond 50–100 µm, later the 45° diamond window) is kept as a record and marked
as superseded. The cap's days: {CD['note']}. {NOT_DISCUSSED}</p>''',
        dark=True, short='cover')

# --------------------------------------------------------------------------- #
# where this stands, 11 Nov 2026
_s50, _s12 = LIS.loc[20, 0.5], LIS.loc[12].max()
st_rows = [
    ['Film: metallic Li, 20 µm', badge('ok', 'holds, but thinner'),
     f'×{gain:.1f} per proton still holds, and LNL already rolls Li to ~20 µm and presses it on copper. New: half turned '
     f'to LiOH, a 20 µm film puts {pc(_s50)} of the γ₀ on the 441 keV resonance. Use 10–12 µm for now.'],
    ['Beam stop: Mo (or Ta), 8 µm', badge('drop'),
     rd.VERDICT['mo']['why'] + ' The stop is now Cu, ≥ 12 µm along the beam.'],
    ['Heat carrier: CVD diamond 50–100 µm, later the 45° diamond window', badge('drop'), rd.VERDICT['diamond']['why']],
    ['Heat: a conduction-path problem', badge('ok', 'holds'),
     f'At the documented 1 µA the beam is 1.1 W. A 0.4 mm aluminium face carries it with a {HEAT_K[0]:.0f} K rise '
     f'({HEAT_K[1]:.0f} K at 4 µA): no problem at all (estimate).'],
    ['Backing γ lines, PIGE, cold trap', badge('ok', 'hold'),
     'Nothing the stop emits reaches 13–18 MeV. The 478 keV line watches the lithium. The cold trap upstream stays, now '
     'also to slow the hydroxide.'],
]
D.slide('status', sd.title('Where this stands (11 Nov 2026): the lithium film and the physics hold, the Mo layer and the diamond are dropped',
                           'The buildability review checked every design against how lithium targets are really made. ' + NOT_DISCUSSED)
        + sd.table(['in this deck (22 Oct)', 'status 11 Nov', 'what changed, and why'], st_rows, size=20,
                   align=['left', 'left', 'left'], widths=[370, 230, 1064])
        + sd.callout(f'<b>Proposed now: a {rd.CAP["name"].lower()}</b> ({rd.CAP["sub"]}). {rd.CAP["stack"]}. '
                     f'To 3σ at the ATOMKI strength, 1 µA: {CAP_DAYS} ({CAP_SRC}). '
                     f'The current set of options, side by side: the comparison deck {link()}.', sd.GREEN, 22),
        f'''<p>Source: <code>lnl/target/TARGET_REVIEW.md</code> (11 Nov 2026), read into the decks through
<code>lnl/target/review_data.py</code>. Days: the reference fit of <code>nd_reach.csv</code> (θ × |y| × E_sum, background
shape floating). For the cap: {CD['note']}.</p>
<p>How lithium targets are really made: {rd.BEAM_PIPE}</p>
<p>The flat assembly this deck recommended (Li 20 µm / Mo 8 µm / diamond 50 µm on a Cu ring in a CFRP chamber) carries both
dropped parts, and most of its parts are new to LNL. With the reference fit it reached {nd.fmt(D_REC_ND)} d per µA with the
big plastics. {rd.VERDICT['thin_film']['why']}</p>
<p>The cap's numbers: at 1 bar the 0.4 mm face is at {rd.CAP['press']['t400'][0]} MPa (×{rd.CAP['press']['t400'][1]} on
yield), 0.5 mm at {rd.CAP['press']['t500'][0]} MPa (×{rd.CAP['press']['t500'][1]}) (estimate, clamped ellipse 20 × 28 mm).
Cost {rd.CAP['cost']}.</p>''',
        short='11 Nov status')

# --------------------------------------------------------------------------- #
# the assembly recommended on 22 Oct, drawn (superseded 11 Nov: the Mo and the diamond are dropped)
W, H = 1664, 400


def stack_diagram():
    s = []
    y0, x0, top, bot = 200, 300, 80, 320
    s.append(sd.arrow(30, y0, x0 - 20, y0, sd.INK, 5, 18))
    s.append(sd.T(160, y0 - 22, 'p, 1.10 MeV, ≤ 0.5 µA', 22, sd.INK))
    layers = [(40, LI, .85, 'metallic Li, 1.07 mg/cm²: the beam leaves it at 0.87 MeV, above the 441 keV resonance. '
                            'Kept (11 Nov), but 10–12 µm until the hydroxide rate is measured'),
              (14, TA, .4, 'Mo or Ta 8 µm: stops the beam (range 6 µm), holds the hydrogen, collects the charge, wets Li. '
                           'DROPPED 11 Nov: ' + rd.VERDICT['mo']['why']),
              (40, DIA, .4, 'CVD diamond 50–100 µm, k ≈ 1800 W/m/K: carries the heat to the ring. '
                            'DROPPED 11 Nov: ' + rd.VERDICT['diamond']['why'])]
    x = x0
    for w, c, op, tip in layers:
        s.append(f'<rect x="{x}" y="{top}" width="{w}" height="{bot - top}" fill="{c}" opacity="{op}"{sd.tipattr(tip)}/>')
        x += w
    s.append(sd.T(x0 - 12, 238, 'Li 20 µm: kept, thinner', 22, LI, anchor='end'))
    s.append(sd.T(x0 - 12, 268, 'Mo/Ta 8 µm', 22, TA, anchor='end'))
    s.append(sd.T(x0 - 12, 298, 'dropped 11 Nov', 22, BAD, anchor='end', weight=600))
    s.append(sd.T(x0 + 120, 196, 'CVD diamond 50–100 µm', 22, DIA, anchor='start'))
    s.append(sd.T(x0 + 120, 226, 'dropped 11 Nov', 22, BAD, anchor='start', weight=600))
    for yy in (top - 40, bot):
        s.append(f'<rect x="{x0 + 54}" y="{yy}" width="{x - x0 - 54 + 70}" height="40" fill="{CU}" opacity=".8"'
                 f'{sd.tipattr("Cu ring clamped or brazed to the membrane rim (r ≥ 8 mm), water-cooled")}/>')
        s.append(f'<circle cx="{x + 40}" cy="{yy + 20}" r="12" fill="#5aa9e6"{sd.tipattr("cooling water")}/>')
    s.append(sd.T(x + 90, top - 14, 'Cu ring, water-cooled', 21, CU, anchor='start'))
    s.append(f'<rect x="14" y="16" width="{x + 316}" height="{H - 32}" fill="none" stroke="#5aa9e6" '
             f'stroke-width="4" stroke-dasharray="12 8" rx="20"{sd.tipattr("LN₂-cooled shroud: pumps water (Li getter) and hydrocarbons (carbon)")}/>')
    s.append(sd.T(30, H - 30, 'LN₂ shroud', 21, '#3b86c6', anchor='start'))
    xt = x + 370
    for i, (t, c) in enumerate((('HPGe / LaBr₃ at 0.5–1 m: 478 keV PIGE (Li content)', sd.INK),
                                ('Si detector, backward: elastic protons (C, O on the Li)', sd.INK),
                                ('at the centre of the arms: < 0.15 % X₀ in the leptons’ path', sd.INK),
                                ('1 mm / micro-channel diamond: for ≥ 30 µA machines', sd.MUT))):
        s.append(sd.T(xt, 130 + 44 * i, t, 23, c, anchor='start'))
    return sd.svg(W, H, ''.join(s), 'the target assembly recommended on 22 Oct, superseded on 11 Nov')


D.slide('design', sd.title('Superseded on 11 Nov: the 22 Oct recommendation, Li on Mo on a thin diamond. The Mo and the diamond are dropped',
                           'A record. The lithium, the cold trap and the monitoring carry over to the aluminium end cap (slide 2). Hover the layers.')
        + stack_diagram()
        + sd.table(['Pierfrancesco’s point', 'answer on 22 Oct', 'status 11 Nov'], [
            ['no fluorine; a lot of heat', 'metallic Li (×2.2 Li per keV of beam) on 50 µm diamond: 35 °C at 4 µA',
             f'the Li holds. No diamond: 0.4 mm Al, +{HEAT_K[0]:.0f} K at 1 µA'],
            ['background from the backing', 'Mo/Ta stops the beam: no backing line above 1 MeV',
             'a Cu stop has no line either. Mo dropped: its K x-rays'],
            ['1 mm diamond, micro-channels', 'not needed below ~30 µA, and ×1.4–1.9 slower per µA (Geant4 L9)',
             'holds: at 1.1 W no diamond at all'],
            ['carbon; cold trap', 'one LN₂ shroud pumps carbon and water (Li is a getter)',
             'holds: a cold trap upstream of the end cap'],
            ['PIGE; germanium?', '478 keV to 1 % in 10–60 s; Ge is safe: no neutrons below 1.88 MeV',
             'holds. γ₀ per µC is also the hydroxide alarm'],
        ], size=20, align=['left', 'left', 'left'], widths=[360, 720, 584]),
        f'''<p>Mo (or Ta) between the Li and the diamond did three jobs: it stopped the 0.87 MeV protons (range 6 µm), so the hydrogen
landed in a metal that tolerates ≥ 3.4×10¹⁹ /cm²; it carried the beam current away (diamond is an insulator); and it gave
lithium something to wet, which an untreated diamond surface may not. The diamond's only job was to carry the heat.</p>
<p>11 Nov 2026 (TARGET_REVIEW.md §4.3, §4.5). Mo: {rd.VERDICT['mo']['why']} Diamond: {rd.VERDICT['diamond']['why']}
In the cap the copper does the Mo's three jobs and the aluminium wall carries the heat and the vacuum.</p>''',
        short='22 Oct design')

# --------------------------------------------------------------------------- #
# film thickness
rows = []
for k, lab in (('Li2O 300 / Al 10 µm (FEAS baseline)', 'Li₂O 1.5 µm (FEAS baseline)'),
               ('Li 10 µm / diamond 1 mm', 'Li 10 µm'), (PF, 'Li 20 µm'),
               ('Li 20 µm / diamond, E_p 1.20 MeV', 'Li 20 µm, E_p 1.20'), ('Li 40 µm / diamond 1 mm', 'Li 40 µm')):
    v = ST.loc[k]
    col = LI if v.f441 < 0.02 else HEAT
    rows.append((lab, v.rel_g0_vs_baseline, col,
                 f'{k}: beam leaves the film at {v.E_after_film_keV:.0f} keV; γ₀ {v.Y_g0_per_p:.3g}/p; '
                 f'441-keV share {v.f441:.2%}; 18.15 resonant share {v.f18res:.0%}',
                 f'out at {v.E_after_film_keV:.0f} keV · 441 share {v.f441:.1%}'))
rows.append(('Li stopping the beam', 78, BAD, '441 keV dominates: 77 % of γ₀', 'out at 0 · 441 share 77 %'))
for um in (15, 12):       # the thinner films of the 11 Nov review (review_li_conversion.csv), after the Li 10 µm row
    rows.insert(2, (f'Li {um} µm' + (' (11 Nov)' if um == 12 else ''), gain * LIY[um], OK if um == 12 else LI,
                    f'Li {um} µm, fresh: beam leaves the film at {LIE.loc[um, 0.0]:.0f} keV; {pc(LIY[um])} of the 20 µm γ₀; '
                    f'441-keV share {pc(LIS.loc[um, 0.0], 1)}, at most {pc(LIS.loc[um].max())} if all of it becomes LiOH',
                    f'out at {LIE.loc[um, 0.0]:.0f} keV · 441 share {LIS.loc[um, 0.0]:.1%}'))
rows[1] = (rows[1][0] + ' (11 Nov)', rows[1][1], OK) + rows[1][3:]
D.slide('film', sd.title(f'Metallic lithium gives ×{gain:.1f} the ⁸Be rate per proton at 20 µm (still holds). Use 10–12 µm until the hydroxide rate is measured',
                         'γ₀ per proton relative to the 1.5 µm Li₂O baseline, E_p = 1.10 MeV, fresh films (Zahnow 1995 cross sections)')
        + sd.hbars(rows, vmax=80, vmin=0.8, log=True, width=560, h=34, label_w=360,
                   fmt=lambda v: f'×{v:.1f}' if v < 50 else f'×{v:.0f}', size=24)
        + sd.callout('11 Nov: the film recommendation changes from “15–25 µm” to <b>10–12 µm until the conversion rate is '
                     f'measured</b> (green; slide “Li → LiOH”). That keeps {100 * LIY[10]:.0f}–{pc(LIY[12])} of the 20 µm yield, '
                     f'still ×{gain * LIY[10]:.1f}–{gain * LIY[12]:.1f} the thin Li₂O film. A fresh film of any thickness up to '
                     '20 µm stays clear of the 441 keV resonance. A converted one does not.', OK, 23),
        f'''<p><code>opt_backing.py</code> + <code>target_model.layered_yield</code> → <code>stacks.csv</code>. The X17 is normalised per
total γ₀ as in FEAS (ATOMKI 2022 reported the anomaly in direct capture too). If it came from the M1 resonance only, the
20 µm gain is ×6.7. The 3D fit absorbs a known energy profile; a 20 % 441 share biases it by < 0.06 R_ATOMKI
(TARGET_STUDY §8), so 0.85 % is negligible.</p>
<p>11 Nov 2026: the 12 and 15 µm bars and the film recommendation come from the buildability review
(<code>review_li_conversion.py</code> → <code>review_li_conversion.csv</code>, same yield model). The 441 shares on this slide
are for a fresh metal film. {rd.LI['headline']} {rd.LI['fix']} LNL's CN group rolls foils of 10–40 µm, “down to sub-10 µm”
(arXiv:2605.12005).</p>''', short='film')

# --------------------------------------------------------------------------- #
# heat
P = sd.Plot(1060, 520, x=(0.25, 300, 'log'), y=(0, 400), xlabel='beam current (µA), 1.10 MeV, σ = 2 mm',
            ylabel='film temperature (°C)')
P.xticks([(v, f'{v:g}') for v in (0.25, 1, 4, 10, 30, 100, 300)]).yticks([(v, str(v)) for v in range(0, 401, 100)])
OPTS = [('A_al10_disk', 'Li₂O / 10 µm Al disk', AL), ('B_graphite25', 'Li₂O / 25 µm graphite foil', sd.GREY),
        ('C_dia50_li2o', 'Li₂O / 50 µm diamond', sd.GREEN), ('E_dia300_li20', 'Li 20 µm / 300 µm diamond', sd.BLUE),
        ('F_dia1000_li20_clamp', 'Li 20 µm / 1 mm diamond, dry clamp', DIA),
        ('H_dia_mch_li20', 'Li 20 µm / micro-channel diamond', '#5aa9e6'),
        ('G_dia1000_li20_braze', 'Li 20 µm / 1 mm diamond, brazed rim', sd.INK)]
for k, lab, c in OPTS:
    q = TS[(TS.key == k) & (TS.sigma_mm == 2.0)].sort_values('I_uA')
    q = q[q.T_film_C < 420]
    P.line(q.I_uA, q.T_film_C, c, tips=[f'{lab}: {t:.0f} °C at {i:g} µA ({pw:.1f} W)' for i, t, pw in zip(q.I_uA, q.T_film_C, q.P_W)])
P.hline(150, BAD, label='Li film limit 150 °C (melts 180)', tip='metallic Li melts at 180.5 °C', anchor='start')
P.hline(300, sd.MUT, label='Li₂O working limit 300 °C', tip='LiOH / diffusion / evaporation', anchor='start')
P.vline(1, OK, label='LNL 1 µA', tip='the documented current at 1.1 MeV (beam sheet): 1.1 W')
P.vline(4, sd.MUT, label='4 µA (ask)', tip='CN up to ~4 µA if LNL can allow it at 1.1 MeV (ask)')
leg = sd.legend([(lab, c) for _, lab, c in OPTS], 19)
lims = [[lab, f'{tlim(k):.0f}', f'{tlim(k, 1.0):.0f}'] for k, lab, _ in OPTS]
D.slide('heat', sd.title(f'The heat is a conduction-path problem (still holds). At 1 µA a 0.4 mm aluminium face rises {HEAT_K[0]:.0f} K: no diamond needed',
                         'The 22 Oct thermal model: beam deposited where the protons stop, k(T), contacts, radiation')
        + sd.row(sd.col(P.svg('film temperature'), leg, gap=8, w=1060),
                 sd.col(sd.table(['option (22 Oct)', 'I max, σ 2 mm', 'σ 1 mm'], lims, size=20, widths=[330, 120, 90]),
                        sd.callout(f'11 Nov: at the documented 1 µA the beam is 1.1 W. A flat Al 6061 face 0.4 mm thick '
                                   f'over Ø20 carries it with a {HEAT_K[0]:.0f} K rise, {HEAT_K[1]:.0f} K at 4 µA (estimate). '
                                   'The diamond and the micro-channels are dropped for LNL.', OK, 21), w=560, gap=16), gap=36),
        f'''<p>11 Nov 2026 (TARGET_REVIEW.md §4.5, §6.1): the aluminium face is not in the 22 Oct model. Its rise is the closed
form ΔT = P/(2πkt)·[ln(a/r_spot) + ½] for a 0.4 mm 6061 disc ({HEAT_K[0]} K at 1.1 W, {HEAT_K[1]} K at 4.4 W; a 0.5 mm face
{rd.CAP['heat_K']['t500'][0]} K), plus about 6 K along the end piece. The film stays near room temperature. LNL's Cu cup is
air-cooled at about 10 °C per watt and safe to ~10 W (arXiv:2605.12005). The diamond curves stay as a record: micro-channels
({I_H:.0f} µA) and a brazed 1 mm diamond ({I_G:.0f} µA) are for machines of tens of µA.</p>
<p><code>opt_thermal.py</code>. Checks: a conduction-only disk agrees with the analytic Gaussian-source result to 0.7 %;
the 10 µm Al disk of the earlier study gives 97.6 °C against 95 °C. Contacts: dry clamp 5×10³–10⁴ W/m²/K, braze 2×10⁵,
water 2×10⁴, micro-channels as h_eff = 3×10⁴ (laminar, 200 × 300 µm channels at 400 µm pitch, 1 L/min, Δp 1.2 bar).
Limits: Li film 150 °C, Li₂O 300 °C. LNL beam power is 1.1 W/µA: the issue on a thin foil is the conduction path, not the power.</p>
<p>Why the slide-7 clamp failed: 20 µm of Li conducts k·t = 1.7 mW/K sideways, 1 mm of diamond 1.8 W/K. The backing must be the conductor.</p>''',
        foot='thermal_scan.csv, thermal_limits.csv · CVD diamond k 1800 W/m/K (thermal grade)', short='heat')

# --------------------------------------------------------------------------- #
# sensitivities
s1 = TSEN[TSEN.h_int.isna() & (TSEN.k_diamond == 1800.0) & (TSEN.I_uA == 100)].sort_values('h_clamp')
s2 = TSEN[TSEN.h_int.notna() & (TSEN.I_uA == 100)].sort_values('h_int')
P2 = sd.Plot(760, 520, x=(1e3, 1e6, 'log'), y=(0, 300), xlabel='conductance (W/m²/K)', ylabel='film °C at 100 µA (110 W)')
P2.xticks([(v, sci(v, 0)) for v in (1e3, 1e4, 1e5, 1e6)]).yticks([(v, str(v)) for v in range(0, 301, 50)])
P2.line(s1.h_clamp, s1.T_film_C, CU, tips=[f'rim clamp h = {h:.0e}: {t:.0f} °C' for h, t in zip(s1.h_clamp, s1.T_film_C)])
P2.line(s2.h_int, s2.T_film_C, LI, tips=[f'Li/diamond interface h = {h:.0e}: {t:.0f} °C' for h, t in zip(s2.h_int, s2.T_film_C)])
P2.hline(150, BAD, label='150 °C', anchor='start')
D.slide('contacts', sd.title('For high-current machines only, not LNL (diamond dropped 11 Nov): above ~30 µA the contacts set the temperature, not the diamond',
                             'A record of the diamond study. 1 mm diamond, 20 µm Li, 100 µA: vary the rim-clamp contact and the Li/diamond interface')
        + sd.row(sd.col(P2.svg('contacts'), sd.legend([('rim clamp to the cooled ring', CU), ('Li/diamond interface', LI)], 22), w=760),
                 sd.col(sd.callout('A dry clamp in vacuum (10³–10⁴) is the bottleneck: braze or indium. CVD-diamond gyrotron windows '
                                   'are brazed to Cu cuffs and edge-cooled the same way.', CU, 24),
                        sd.callout('Nobody seems to have measured evaporated Li on diamond. A Ta/Mo/Ti layer (carbide-forming) is the '
                                   'standard fix, and the same layer stops the beam: one bench test answers it.', LI, 24),
                        sd.callout('Diamond grade: k = 1000 instead of 1800 adds ~20 K at 100 µA. Irrelevant at LNL.', sd.GREY, 24),
                        w=820, gap=24), gap=60),
        '<p><code>thermal_sensitivity.csv</code>. At LNL’s ≤ 4 µA none of this matters (≤ 25 °C for any contact ≥ 10⁴). '
        '11 Nov 2026: the diamond is dropped for LNL (TARGET_REVIEW.md §4.5), so the braze and the Li-on-diamond bench test '
        'are no longer asked for.</p>',
        short='contacts (diamond)')

# --------------------------------------------------------------------------- #
# backing emissions
def cell(v, d=2):
    return '—' if not v or v <= 0 else (f'{v:.{d}g}' if v < 100 else f'{v:,.0f}')


rows, tips = [], []
for k, lab in ((BASE, 'Li₂O / Al 10 µm (FEAS baseline)'), ('Li2O 300 / diamond 50 µm', 'Li₂O / diamond 50 µm'),
               (PF, 'Li 20 µm / diamond 1 mm'), ('Li 20 µm / ¹²C diamond 1 mm (99.99 %)', 'Li 20 µm / ¹²C-enriched diamond'),
               (REC, 'Li 20 µm / Ta 10 µm / diamond'), ('Li 20 µm / Cu 1 mm (BNCT-style)', 'Li 20 µm / Cu 1 mm')):
    v = ST.loc[k]
    rows.append([lab, cell(v.L478_per_g0, 3), cell(v.Al_843_per_g0), cell(v.C12_237_per_g0), cell(v.C13_806_per_g0),
                 cell(v.Al_res_per_g0)])
    tips.append(f'{k}: beam stops in {v.beam_stops_in}')
eq = RO[((RO['stack'] == BASE) & (RO.I_uA == 1.0)) | ((RO['stack'].isin([PF, REC])) & (RO.I_uA == 0.125))]
eqrows = [[r[1].replace('Li2O', 'Li₂O').replace(' (FEAS baseline)', '').replace(' (Pierfrancesco)', ''), f'{r.I_uA:g}',
           f'{r.g0_per_s:,.0f}', f'{r.legs_per_arm_s:.2g}', f'{r.mm_hits_per_arm_s:,.0f}', f'{r.mm_occupancy:.1e}'] for r in eq.itertuples()]
D.slide('backing', sd.title('Nothing the backing emits reaches the 13–18 MeV window (still holds). Copper, the stop now proposed, has no line',
                            'γ-rays per ⁸Be γ₀ from measured cross sections; then trigger legs and Micromegas hits from Geant4 (L9 bklines, big plastics)')
        + sd.table(['film / backing', '478 keV (Li)', '843 keV (Al)', '2.37 MeV (¹²C)', '8.06 MeV (¹³C)', '10.8 MeV (²⁷Al)'],
                   rows, size=22, tips=tips, widths=[520, 200, 200, 220, 220, 220])
        + sd.table(['at the same X17 rate', 'µA', 'γ₀ /s', 'backing legs /arm/s', 'MM hits /arm/s', 'MM occupancy'],
                   eqrows, size=21, widths=[560, 90, 150, 260, 230, 200])
        + sd.p('Cosmics give ~15 legs/arm/s. The Al backing’s 10.8 MeV line (992 keV resonance) alone makes ~23 at 1 µA. '
               '11 Nov: in the aluminium end cap the beam stops in the copper, so the aluminium behind it makes no such line. '
               'What a stop does emit is K x-rays: they removed the Mo.', 22, sd.MUT),
        '''<p>Inputs: ⁷Li(p,p′γ) from Bykov et al. ARI 175 (2021) (thick Li 4.9×10⁶ /µC at 1.0 MeV); ¹³C(p,γ) 556 keV resonance from
Skowronski et al. PRC 111 064611 (2025); ¹²C(p,γ) 457 keV resonance (ωγ 0.6 eV); ²⁷Al(p,γ) 632/773/992 keV (ωγ 0.26/0.13/1.91 eV,
the first two ESTIMATE) and (p,p′)843 keV (2 mb, ESTIMATE ×3). Resonances are integrated analytically per energy step (checked
against (λ²/2)ωγ/ε). Ta/Cu Coulomb excitation (≤ 1.1 MeV) not computed. No neutrons below E_p = 1.88 MeV.</p>
<p>11 Nov 2026: this table has no x-rays. The Geant4 PIXE check of 4 Nov found the Mo K yield ×2.0–2.2 the first estimate
(<code>CU_LINER.md</code> §6), and that is what dropped every Mo stop (TARGET_REVIEW.md §4.3). Cu K x-rays (8 keV) stop in
0.4–0.5 mm of aluminium. In the cap the Cu covers the whole face and the first centimetre of the bore, so the beam does
not reach bare aluminium.</p>
<p>Detector response: Geant4 L9 <code>gam_7Li_bklines</code>, 10⁷ γ in nine lines from the spot, big plastics; a leg = SiPM bar AND
plastic ≥ 0.5 MIP. <code>opt_rates.py</code> → <code>line_response.csv</code>, <code>rates_options.csv</code>.</p>''',
        foot='stacks.csv, lines.csv, rates_options.csv', short='backing γ')

# --------------------------------------------------------------------------- #
# which backing
D.slide('which', sd.title('Which backing, revised 11 Nov: copper stops the beam, aluminium behind it carries the heat and the vacuum. Diamond, Mo and Be are dropped',
                          'Every criterion that matters for a ⁷Li(p,γ) target at 1 MeV, with the 22 Oct verdict and the verdict of the buildability review')
        + sd.table(['backing', 'k (W/m/K)', 'X₀', 'γ background', 'hydrogen', 'with Li', '22 Oct', '11 Nov'], [
            ['CVD diamond', '1800', '12 cm', '2.37, 8.06 MeV lines', 'unknown (gap)', 'inert; adhesion?', 'best, under a metal layer',
             badge('drop') + ' not needed at 1.1 W; brittle'],
            ['Ta 10 µm (or Mo)', '57 (138)', '0.4 cm', 'none', '≥ 3.4×10¹⁹ /cm²', 'excellent', 'the beam stop',
             badge('drop', 'Mo dropped') + ' K x-rays. Ta: an option'],
            ['<b>Cu ≥ 12 µm</b>', '400', '1.4 cm', 'none', 'blisters ~10¹⁹: watch', 'slow dissolution', 'thick + offset only',
             badge('propose', 'the stop') + ' LNL presses Li on Cu'],
            ['<b>Al 0.4–0.5 mm</b>', '237', '8.9 cm', '992 keV res. → 10.8 MeV', 'blisters ~10¹⁸', 'alloys with Li', 'avoid in the beam',
             badge('propose', 'the wall') + ' behind the Cu, out of the beam'],
            ['graphite foil', '400 ∥ / 5 ⊥', '19 cm', 'as diamond', 'outgasses', 'inert', 'thin option', 'not pursued'],
            ['Be, Si, SiC', '150–400', '9–35 cm', '(p,γ), (p,α) lines', '—', 'Si alloys with Li', 'no',
             badge('drop') + ' Be: no supplier'],
        ], size=20, align=['left'] * 8, widths=[200, 140, 90, 250, 220, 180, 200, 384]),
        f'''<p>X₀ only matters for a backing in the leptons’ path, i.e. a target at the centre; at +12 cm (Geant4 L9) the backing is behind the leptons.</p>
<p>11 Nov 2026 (TARGET_REVIEW.md §4.3, §4.5–4.7, §6.5). Mo: {rd.VERDICT['mo']['why']} Diamond: {rd.VERDICT['diamond']['why']}
Be: {rd.VERDICT['be']['why']} Copper: LNL's CN group presses its rolled Li on a 300 µm Cu cup that also stops the beam. Hydrogen
in copper is a watch item, not a blocker: the blister thresholds were measured at 2 MeV and BNCT current densities, and MEG II
stopped 8–11 µA in 25 µm of Cu for four weeks with no significant deterioration. Tantalum is the standard backing at this
energy (LUNA, PTB) because it takes up hydrogen without blistering: a 10 µm Ta stop costs +0.4° in the ray-trace and its L
x-rays stop in the same aluminium. Aluminium in the beam is still to be avoided (it alloys with Li and has the 992 keV
resonance): in the cap the Cu covers the whole face and the first centimetre of the bore.</p>''',
        short='which backing')

# --------------------------------------------------------------------------- #
# hydrogen and vacuum
h1 = HY[(HY.sigma_mm == 2.0) & (HY.I_uA == 1.0)].set_index('stop_material')
lc = LC.set_index(['p_partial_mbar', 'gas'])
cs = CS[(CS.I_uA == 1.0) & (CS.days == 14)]


def csv_(vac, film, col):
    return float(cs[(cs.vacuum.str.startswith(vac)) & (cs.film.str.startswith(film))][col].iloc[0])


D.slide('vacuum', sd.title('Lithium is a getter: the cold trap must pump the water as well as the carbon (still holds). Corrected 11 Nov: what the hydroxide does to a thick film',
                           'Hydrogen where the beam stops, residual-gas chemistry on metallic Li, and carbon build-up')
        + sd.row(
            sd.col(sd.p('Hydrogen at the spot: 2.1×10¹⁸ /cm² per day per µA', 26, sd.INK, 600),
                   sd.table(['beam stops in', 'days to blister onset, 1 µA'], [
                       ['Al', f'{h1.loc["Al", "days_to_onset"]:.1f}'], ['Cu', f'{h1.loc["Cu", "days_to_onset"]:.1f}'],
                       ['Ta', f'≥ {h1.loc["Ta", "days_to_onset"]:.0f}'], ['diamond', 'unknown (gap)'], ['Li (thick)', 'LiH, no blisters']],
                       size=22, widths=[280, 330]),
                   sd.p('Cu is a watch item, not a blocker (11 Nov): MEG II stopped 8–11 µA in 25 µm of Cu for four weeks.',
                        21, sd.MUT), w=640, gap=14),
            sd.col(sd.p('Water and O₂ convert metallic Li', 26, sd.INK, 600),
                   sd.table(['water pressure', 'Li → LiOH per day', 'half of 20 µm converted in'], [
                       [f'{p:.0e} mbar', f'{lc.loc[(p, "H2O"), "Li_consumed_um_per_day"]:.2g} µm',
                        f'{nd.fmt(lc.loc[(p, "H2O"), "days_to_eat_20um"] / 2)} d'] for p in (1e-6, 1e-7, 1e-8)],
                       size=22, widths=[220, 250, 330]),
                   sd.p('An upper limit: every molecule sticks. LiOH passivates the surface, so the real rate is lower. '
                        'Nobody has published it for a thick film under beam.', 21, sd.MUT), w=840, gap=14),
            gap=60)
        + sd.callout('Corrected 11 Nov. “The products stay on the target, so the Li is not lost” is true for the thin '
                     'Li₂O film only. In a 20 µm metal film the lithium atoms stay, but the added oxygen and hydrogen slow '
                     'the beam down to the 441 keV resonance (next slide).', BAD, 23)
        + sd.callout(f'Carbon, 14 days at 1 µA with no trap: γ₀ ×{csv_("diffusion", "Li 20", "g0_rel"):.2f} on the 20 µm Li, '
                     f'441 share {csv_("diffusion", "Li 20", "f441"):.1%}; with a cold shield ×{csv_("cold", "Li 20", "g0_rel"):.2f}. '
                     'Carbon is a 441 keV-calibration problem, not a 1 MeV one.', sd.GREY, 23),
        '''<p>Hydrogen: Budker INP in-situ blistering under 2 MeV protons (Cu from 10¹⁹ /cm², dense at 3×10¹⁹; Ta unchanged at 3.4×10¹⁹,
≥ 6.7×10²⁰ claimed); diamond: 1.2×10¹⁷ /cm² at 350 keV blistered only after a > 1400 °C anneal, no MeV/room-temperature data
found. Water/O₂: Hertz–Knudsen flux × sticking ≈ 1 on fresh Li (ESTIMATE ×3); the products stay on the target and dilute it. 11 Nov 2026 (TARGET_REVIEW.md §4.2): the
22 Oct conclusion “the yield per µC drops slowly” was checked for the thin Li₂O film only. For a 20 µm metal film the main
effect is the added stopping power, shown on the next slide. A vacuum transfer leaves ~6 nm of Li₂O (BINP) and even ~0.5 µm of
hydroxide from a short argon-bag or air transfer is 2–3 % of a 20 µm film: what converts the film is the days it spends in the
beam-line vacuum.
Carbon: ~1 C retained per proton without a trap (Peterson & Laubert 1977), ×10 less with a cold shield, none seen with a LN₂ trap
at 10⁻⁷ mbar (Redigolo 2024). <code>opt_backing.py</code>, <code>opt_monitor.py</code>.</p>''',
        short='vacuum')

# --------------------------------------------------------------------------- #
# new on 11 Nov 2026: a thick Li film that turns to hydroxide reaches the 441 keV resonance (TARGET_REVIEW.md §4.2)
# figure data: lnl/out/target/options/review_li_conversion.csv (review_li_conversion.py)
PL = sd.Plot(940, 560, x=(0, 1), y=(3e-3, 1.0, 'log'), xlabel='share of the lithium atoms converted to LiOH (outer part of the film)',
             ylabel='share of γ₀ from the 441 keV resonance')
PL.xticks([(v, pc(v)) for v in LIS.columns])
PL.yticks([(0.003, '0.3 %'), (0.01, '1 %'), (0.03, '3 %'), (0.1, '10 %'), (0.3, '30 %'), (1.0, '100 %')])
LICOL = {20: BAD, 15: HEAT, 12: OK, 10: sd.BLUE}
for um in (20, 15, 12, 10):
    ys = [float(LIS.loc[um, c]) for c in LIS.columns]
    eo = [float(LIE.loc[um, c]) for c in LIS.columns]
    PL.line(list(LIS.columns), ys, LICOL[um], tips=[
        f'Li {um} µm, {pc(c)} LiOH: {pc(y, 1)} of γ₀ from the 441 keV resonance; the beam '
        + (f'leaves the film at {e:.0f} keV' if e > 100 else 'stops in the film') for c, y, e in zip(LIS.columns, ys, eo)])
    PL.text(1.012, ys[-1] * (0.86 if um == 15 else 1.0) * (1.16 if um == 20 else 1.0), f'{um} µm', 21, LICOL[um], weight=600)
PL.hline(0.10, sd.MUT, label='10 %', tip='10 %: the largest share a 12 µm film reaches at 1.10 MeV, fully converted', anchor='start')
_t03 = [[f'Li {um} µm'] + [pc(LIS03.loc[um, c], 1) if LIS03.loc[um, c] < 0.095 else f'<b>{pc(LIS03.loc[um, c])}</b>'
                           for c in (0.0, 0.5, 1.0)] for um in (20, 15, 12, 10)]
_tl, _td = thin_days()
_dtxt = ' · '.join(f'{um} µm: {nd.fmt(_td[um][0])} d ({nd.fmt(_td[um][1])} as built)' for um in (20, 12, 10) if um in _td)
D.slide('lioh', sd.title(f'New (11 Nov): a 20 µm Li film half turned to LiOH gives {pc(LIS.loc[20, 0.5])} of its γ₀ at the 441 keV resonance. 12 µm: {pc(LIS.loc[12].max())} at most',
                         'Residual water turns lithium into LiOH. The lithium atoms stay, but the oxygen and hydrogen add stopping, so the beam slows further. E_p = 1.10 MeV')
        + sd.row(sd.col(PL.svg('share of γ₀ from the 441 keV resonance against the converted fraction'), w=1000),
                 sd.col(sd.callout(f'20 µm, half converted: the beam leaves the film at {LIE.loc[20, 0.5]:.0f} keV instead of '
                                   f'{LIE.loc[20, 0.0]:.0f}. The 441 keV resonance is ~50× stronger than the 18.15 MeV one, so the '
                                   '17.64 MeV line takes over and the trigger rate rises several-fold.', BAD, 21),
                        sd.callout(f'<b>Film: 10–12 µm until the conversion rate is measured</b>, not 15–25 µm. Fully converted, '
                                   f'12 µm gives at most {pc(LIS.loc[12].max())} and 10 µm {pc(LIS.loc[10].max(), 1)}, for '
                                   f'{pc(LIY[12])} and {pc(LIY[10])} of the 20 µm yield.', OK, 21),
                        sd.table(['at 1.03 MeV', 'fresh', 'half LiOH', 'all LiOH'], _t03, size=19, widths=[190, 120, 150, 140]),
                        sd.p('Run at 1.10 MeV, not 1.03: 70 keV more margin. The rate is unknown (upper limit 1.35 µm a day at '
                             '10⁻⁷ mbar of water). A one-week film test on the LNL line decides the thickness.', 20, sd.MUT),
                        w=620, gap=16), gap=44),
        f'''<p><code>lnl/target/review_li_conversion.py</code> (the repo's yield model, PSTAR stopping; the outer fraction of the Li
atoms converted, the rest metal) → <code>lnl/out/target/options/review_li_conversion.csv</code>. TARGET_REVIEW.md §4.2.</p>
<p>{rd.LI['headline']} {rd.LI['fix']} {rd.LI['rate']}</p>
<p>It applies to every design, the Cu cup and the Cu ogive included: it is a property of the film, not of the shell. It did
not matter for LNL's neutron work, where the film's energy loss only shapes the neutron spectrum. The fit-bias test of the
lithium-target note covered a drift of the 441 share up to 20 %, not this. With the repo's upper-limit rate half of a 20 µm
film is hydroxide after {nd.fmt(lc.loc[(1e-7, "H2O"), "days_to_eat_20um"] / 2)} days at 10⁻⁷ mbar of water and after
{nd.fmt(lc.loc[(1e-6, "H2O"), "days_to_eat_20um"] / 2)} days at 10⁻⁶ mbar. The real rate is lower: LiOH passivates the
surface, and BINP and PTB both report a compound layer that grows slowly during operation.</p>
<p>What the thinner film costs in days to 3σ at the ATOMKI strength, 1 µA, big plastics ({_tl}; a yield and line-mix change
only): {_dtxt}. With the big plastics the fit is limited by the background shape, so the cost is less than proportional.</p>
<p>What to do: (1) a 10–12 µm film; (2) run at 1.10 MeV; (3) watch the γ₀ yield per µC, which <i>rises</i> several times
when the beam reaches 441 keV (a LaBr₃ or the Ge planned for PIGE separates 17.64 from 18.15 MeV), and replace the target
when the share passes a few per cent; (4) measure the rate before the run: one film on the AN2000 or CN line for a week at
the vacuum we will have, following 478 keV and γ₀; (5) keep the cold trap upstream, and no PVC next to the target if it can
be avoided.</p>
<p>If Li₂O forms instead of LiOH the effect is much smaller: a fully oxidised 20 µm film gives
{pc(rd.li_table(1100, 'Li2O').loc[20, 1.0], 1)} at 1.10 MeV.</p>''',
        foot='review_li_conversion.csv · yield model of target_model.py, PSTAR stopping · the conversion rate is the unknown',
        short='Li → LiOH')

# --------------------------------------------------------------------------- #
# Geant4 L9
if GR is not None and GA is not None and len(GR) > 1:
    LAB = dict(zip(GR.config, GR.label))
    order = [c for c in ('base', 'al10_y120', 'dia50', 'li20_dia50', 'li20_mo8_dia50', 'li20_ta8_dia50', 'li20_ta_dia300',
                         'li20_dia1', 'li20_dia1_y120', 'li20_dia1_y180', 'li20_dia1_r8_y120', 'li20_mch_y120',
                         'cublock_y120') if c in set(GR.config)]
    g = GR.set_index('config')
    a = GA[GA['sample'] == 'x17'].set_index('config')
    ep = GA[GA['sample'].str.startswith('EPC') & GA['sample'].str.contains(r'\(13, 18\)')].set_index('config')
    rows = []
    for c in order:
        dd = g.loc[c, 'days_ref_1uA']
        col = sd.GREY if c == 'base' else (OK if dd < 0.25 else (DIA if dd < 1.0 else HEAT))
        rows.append((LAB[c].replace('Li₂O 300', 'Li₂O'), dd, col,
                     f'{LAB[c]}: X17 acceptance {a.loc[c, "acc"]:.3f}, σ68 {a.loc[c, "sigma68_deg"]:.1f}°, '
                     f'{a.loc[c, "frac_any_down"]:.0%} with a leg downstream; EPC share of B {g.loc[c, "B_epc_share"]:.1%}; '
                     f'E_sum {g.loc[c, "ecut"]}; per µA: {g.loc[c, "days_fit"]:.2g} d raw fit',
                     f'σ68 {a.loc[c, "sigma68_deg"]:.1f}° · acc {a.loc[c, "acc"] / a.loc["base", "acc"]:.2f}× · '
                     f'{g.loc[c, "uA_for_baseline_rate"]:.2g} µA for the baseline rate'))
    vmax = max(r[1] for r in rows) * 1.2
    D.slide('geant', sd.title('Geant4 L9, a record: keep the backing thin where the leptons cross it; no offset moves a thick one out of the way',
                              'Relative days per µA (big plastics, statistics-only fit). Every 20 µm Li stack here has Mo, Ta or diamond: dropped 11 Nov')
            + sd.legend([('reference', sd.GREY), ('thin backing, 20 µm Li', OK), ('thick diamond', DIA),
                         ('slower than the reference', HEAT)], 20)
            + sd.hbars(rows, vmax=vmax, width=520, h=22, label_w=560, fmt=lambda v: f'{v:.2g} d', size=20)
            + sd.p(L9_NOTE, 19, sd.ORANGE),
            f'''<p>11 Nov 2026: every 20 µm Li stack in this run carries Mo, Ta or diamond, all dropped by the buildability
review, and the flat target in a CFRP chamber is not pursued. The rule the run gave carries over: in the aluminium end cap
the leptons cross a 0.4–0.5 mm face at 45° and a 0.5 mm end piece. Its days: {CAP_DAYS} ({CD['note']}).</p>
<p>Geant4 L9 (MX17_Full_Geant branch <code>lnl_target</code>, multi-layer backings): per configuration 5×10⁵ X17 (m 16.8),
5×10⁵ M1 and 5×10⁵ E1 Born IPC at 18.15 MeV, 2×10⁷ ⁸Be γ (EPC). Big plastics, LNL-calibrated calorimetry, MM 15° + TOF, the
opening angle and pointing about the target position. Reach: Asimov/Fisher fit in θ × |y| × n_down with M1, E1, γ₁ and EPC
norms free, cosmics fixed, best E_sum window; scaled so the baseline equals the reference 3D fit (FEAS §14, 1.0 d at 1 µA).
γ₁ uses the baseline L2 templates for every configuration. Per µA: the 20 µm Li films make ×8.2 the γ₀, so their days per
µA include that gain; "µA for the baseline rate" is the current that gives the baseline's X17 rate.</p>
<p><code>opt_geant.py</code> → <code>geant_acceptance.csv</code>, <code>geant_reach.csv</code>.</p>''',
            foot=f'Geant4 L9, 2026-10-22 · relative comparison only · current days for every design: {link()}', short='Geant4 L9')

# --------------------------------------------------------------------------- #
# monitoring + window
pg = PG[(PG.I_uA == 1.0) & (PG.d_cm == 50)]
prow = [[r.film.replace(' at 1.10 MeV', ''), r.det, f'{r.peak_cps:,.0f}', f'{r.s_to_1pct:.0f} s', f'{r.total_cps_est:,.0f}'] for r in pg.itertuples()]
aw = AW[AW.Al_mm.isin([0.06, 1.0, 5.0])]
arow = [[f'{r.Al_mm:g} mm', f'{r.att_478:.1%}', f'{r.att_17p6:.1%}', f'{r.pair_conv_18MeV:.2%}', f'{r.highland_theta0_deg_8MeV:.1f}°'] for r in aw.itertuples()]
D.slide('monitor', sd.title('PIGE watches the lithium to 1 % in a minute (still holds); a thicker Al window would only add pairs',
                            'Left: 478 keV line at 50 cm, 1 µA. Right: what Al in front of the Micromegas does')
        + sd.row(sd.col(sd.table(['film', 'detector', 'peak cps', 'to 1 %', 'total cps'], prow, size=21,
                                 widths=[230, 180, 140, 110, 150]),
                        sd.callout('Ge is needed for Na (440), ¹⁰B (429) next to Li (478), not for Li alone. It is safe: nothing makes '
                                   'neutrons below E_p = 1.88 MeV. Add a backward Si detector for C and O (elastic p).', LI, 22), w=800, gap=18),
                 sd.col(sd.table(['Al', '478 keV absorbed', '17.6 MeV absorbed', '18 MeV → e⁺e⁻', 'θ₀ at 8.6 MeV'], arow, size=21,
                                 widths=[110, 190, 190, 180, 150]),
                        sd.callout('The 17.64 MeV line of the 441 keV resonance is 0.6–0.9 % of γ₀ in a fresh film and a calibration '
                                   'point; no window absorbs it. 11 Nov: watch it. It rises several-fold if the film turns to '
                                   'hydroxide.', HEAT, 22), w=800, gap=18),
                 gap=40),
        '''<p>Full-energy efficiency at 478 keV, 10 cm: 60 % HPGe 4×10⁻³, 3″×3″ LaBr₃ 6×10⁻³ (±30 %), scaled as 1/d². Total rate ~4× the
peak (ESTIMATE). Sensitivity: 10 % less Li → −7 to −9 % in the 478 yield; 10 µg/cm² carbon → −0.6 %. Window: XCOM μ/ρ(Al) 0.0838
(0.478 MeV), 0.0227 cm²/g (17.6 MeV); pair conversion (7/9) t/X₀; Highland at 8.6 MeV. <code>opt_monitor.py</code>.</p>
<p>11 Nov 2026: the monitoring carries over unchanged to the aluminium end cap, and it gains a second job. The 478 keV line
follows the lithium content, which does not change when the film turns to hydroxide. The alarm for the hydroxide is the γ₀
yield per µC and the 17.64 MeV line: both rise several-fold when the beam reaches 441 keV inside the film
(TARGET_REVIEW.md §4.2).</p>''',
        short='monitoring')

# --------------------------------------------------------------------------- #
# what geant4 can do
gt = GT.set_index('nucleus')
D.slide('g4', sd.title('Geant4 cannot make the target’s own γ-rays at 1 MeV; they come from measured data, Geant4 transports them',
                       'G4TENDL1.4, the proton data behind the *_AllHP physics lists below 200 MeV')
        + sd.table(['nucleus', 'σ_inel at 1.03 MeV in G4TENDL', 'what is missing'], [
            ['⁷Li', f'{gt.loc["3_7_Lithium", "sigma_b_1030keV"] * 1e3:.1f} mb, smooth ((p,α) only)', 'the 441 and 1030 keV resonances, (p,γ), (p,p′) 478 keV'],
            ['¹²C, ¹⁶O', '0 (nothing below 4.8 MeV)', '¹²C(p,γ) 457 keV resonance'],
            ['¹³C', f'{gt.loc["6_13_Carbon", "sigma_b_1030keV"] * 1e6:.0f} µb, one point per MeV', '556 keV resonance (peak ~1.4 mb)'],
            ['¹⁹F, ²⁷Al, ¹¹B', '2–6 points', 'all resonances (¹⁹F 872/935, ²⁷Al 992)'],
            ['⁶³Cu, ¹⁸¹Ta', '≈ 0', 'Coulomb excitation'],
        ], size=22, align=['left', 'left', 'left'], widths=[220, 560, 820])
        + sd.table(['quantity', 'reliability', 'from'], [
            ['lepton scattering, EPC, energy loss in the assembly', 'good', 'Geant4 L9'],
            ['⁷Li(p,γ) γ₀/γ₁; 478 keV; ¹²C/¹³C resonances', '±10–20 %', 'Zahnow 1995, Bykov 2021, Skowronski 2025'],
            ['²⁷Al minor resonances, (p,p′)843; Ta/Cu Coulex', '×2–3; not computed', 'ESTIMATE'],
            ['temperatures', '±20 % at fixed contacts', 'opt_thermal'],
            ['Li + water rate in the beam-line vacuum (decides the film thickness, 11 Nov)', 'unknown', 'gap: a one-week film test'],
        ], size=21, align=['left', 'left', 'left'], widths=[760, 330, 510]),
        '<p><code>lxplus/g4tendl_check.py</code> → <code>g4tendl_check.csv</code>.</p>', short='Geant4 limits')

# --------------------------------------------------------------------------- #
end = (sd.kicker('what to test and what to ask, revised 11 Nov 2026')
       + sd.row(
           sd.col(sd.p('Tests that decide the design now', 32, sd.DINK, 600),
                  sd.p('1. One Li film on the AN2000 or CN line for a week, at the vacuum we will have, following the 478 keV '
                       'and γ₀ lines: the conversion rate, and so the film thickness.', 24, sd.DMUT),
                  sd.p('2. 10–15 µm of Cu on a flat aluminium face, coated below ~150 °C: adhesion, a thermal-cycled coupon.', 24, sd.DMUT),
                  sd.p('3. A pressure test of every cap. A fast valve upstream.', 24, sd.DMUT),
                  sd.p(f'4. Geant4 run L14, the aluminium cap: {"done, its days are in this deck" if CD["g4"] else "running"}.', 24, sd.DMUT),
                  sd.p('No longer asked for (diamond and Mo dropped): protons on diamond, Li on coated diamond, a brazed '
                       'diamond membrane.', 22, '#f0a35e'),
                  w=820, gap=16),
           sd.col(sd.p('Questions for Pierfrancesco', 32, sd.DINK, 600),
                  sd.p('1. How will the Li go on his ogive: pressed foil, or the evaporator of his 2015 paper?', 24, sd.DMUT),
                  sd.p('2. Would he consider a flat face at 45°? It keeps his rolled and pressed Li and removes the flank.', 24, sd.DMUT),
                  sd.p('3. Can the workshop turn a 0.4–0.5 mm Al wall, and who puts 10–15 µm of Cu on it, cool?', 24, sd.DMUT),
                  sd.p('4. The vacuum at the target: pressure, residual gas, PVC or ceramic insulator.', 24, sd.DMUT),
                  sd.p('5. How thin can a rolled foil be made reproducibly (we would like 8–12 µm), and how does it travel?', 24, sd.DMUT),
                  sd.p(f'{NOT_DISCUSSED} Current options: {link(color=sd.DBLUE)}.', 22, '#f0a35e'),
                  w=760, gap=16), gap=64))
D.slide('end', end, '''<p>Revised 11 Nov 2026 from TARGET_REVIEW.md §4.2, §7 and §8. The 22 Oct list asked for five tests, three of them on
diamond (MeV protons on bare and coated CVD diamond, Li on Mo/Ta-coated diamond, a brazed 50–100 µm membrane), and asked
whether LNL could coat and mount a diamond membrane. The open point that remains from that list is the Li target at a known
water pressure followed by PIGE: it is now the test that decides the film thickness. The full list of questions is in
TARGET_REVIEW.md §7 (we do not need anything deposited in the beam pipe; the beam spot, as before).</p>''', dark=True, short='open')

out = D.write(HERE.parents[1] / 'out' / 'target' / 'lnl-target-options.html', note_meta=dict(
    title='Target options for MX17 at LNL',
    summary=('Film, backing, cooling, vacuum and monitoring for the ⁷Li(p,e⁺e⁻)⁸Be target: metallic Li gives ×8 the rate per '
             'proton at 20 µm; the heat is a conduction-path problem and no problem at 1 µA; backing γ-rays never reach the signal '
             'window; Geant4 L9 of the assembly. Status 11 Nov 2026: the Mo layer and the diamond are dropped, a film that turns '
             'to hydroxide reaches the 441 keV resonance (use 10–12 µm), and the proposal is a flat aluminium end cap.'),
    tags='x17, lnl, target', date='2026-10-22'),
    footer='Built by x17_facility_search/lnl/target/deck/build_options_deck.py from the opt_*.py outputs.')
print(out)
