#!/usr/bin/env python3
"""
make_big_plastics_deck.py -- slide note on the big trigger plastics refresh (TRIGGER_OPTIONS.md §8, 2026-10-20).

    python3 trigger_scint/deck/make_big_plastics_deck.py      # -> trigger_scint/deck/out/big-plastics.html
    python3 ~/PycharmProjects/dylan-cern-site/scripts/add-note.py trigger_scint/deck/out/big-plastics.html \
        --slug big-trigger-plastics --force --deploy

Reads the study's own outputs: costs.py, out/optics_refresh.csv, sim/accept/thr_X17.csv, sim/accept/seams.csv,
out/gamma_rates.csv, out/bkg_reach.csv.
"""
import csv
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TS = HERE.parent
sys.path.insert(0, str(TS))
sys.path.insert(0, os.path.expanduser(os.environ.get('SLIDEDOC_DIR', '~/PycharmProjects/dylan-cern-site/scripts')))
import slidedoc as sd  # noqa: E402
import costs as CO     # noqa: E402
from slidedoc import (BLUE, ORANGE, RED, GOLD, PURPLE, GREY, GREEN, INK, MUT, RULE, CARD,  # noqa: E402
                      DBLUE, DRED, DGREEN, DINK, DMUT, T, line, arrow, poly, svg, term)


def rows(p):
    with open(p, newline='') as f:
        return list(csv.DictReader(f))


OPT = rows(TS / 'out' / 'optics_refresh.csv')
THR = rows(TS / 'sim' / 'accept' / 'thr_X17.csv')
SEAM = rows(TS / 'sim' / 'accept' / 'seams.csv')
GAM = rows(TS / 'out' / 'gamma_rates.csv')
BKG = rows(TS / 'out' / 'bkg_reach.csv')
SRC = 'x17_facility_search/trigger_scint'

# ------------------------------------------------------------------ numbers
diy5 = CO.arms_diy(1, 78, 80, 5)
diy4 = CO.arms_diy(1, 78, 80, 4)
diy2 = CO.arms_diy(1, 78, 80, 2)
split5 = CO.arms_diy(2, 78, 80, 5, pmts_bought_per_arm=2)
vend = tuple(sum(4 * CO.slab_cost(78, 80, 5, '3"', 2, 'PS', k)[p] for p in ('scint', 'guides', 'mech', 'pmts'))
             for k in range(3))


def acc13(T, thr):
    for r in THR:
        if r['W_cm'] == '78' and float(r['T_cm']) == T and abs(float(r['thr_MeV']) - thr) < 1e-6:
            return float(r['acc_E13'])


loss25 = 1 - acc13(5, 2.5) / acc13(5, 1.67)
loss3 = 1 - acc13(5, 3.0) / acc13(5, 1.67)


def best_reach(geom, air, gate):
    v = [float(r['reach3']) for r in BKG if r['geom'] == geom and float(r['air']) == air
         and r['scen'] == 'timing' and float(r['gate_ns']) == gate]
    return min(v) if v else None


r_ab, r_p5b = best_reach('asbuilt', 1.0, 0), best_reach('P5B', 1.0, 0)
gain = r_ab / r_p5b


def opt(study, mat, T, pmt, N=1):
    for r in OPT:
        if (r['study'] == study and r['material'] == mat and float(r['T_cm']) == T and r['pmt'] == pmt
                and int(r['n_bars']) == N):
            return r


def k(v):
    return f'€{v / 1e3:.0f}k'


D = sd.Deck('Big trigger plastics: build them ourselves',
            'Refresh of the big trigger-plastic plan: in-house cost, light vs thickness and splitting, γ sensitivity.')

# ------------------------------------------------------------------ 1 cover
cover = (sd.kicker('MX17 trigger upgrade · 2026-10-20')
         + sd.title(f'<span style="color:{DINK}">Build the big plates ourselves: {k(diy5[1])} instead of {k(vend[1])}. '
                    'Thick is fine for the light; γ need a per-facility check before we buy.</span>')
         + sd.row(
             sd.bignum(k(diy5[1]), 'four 78 × 80 × 5 cm plates, built in-house', DGREEN,
                       f'range {k(diy5[0])}–{k(diy5[2])}; vendor-finished with new PMTs: {k(vend[1])}',
                       tip='Raw plates + our polishing/wrapping + bought fishtail guides + the 8 borrowed PMTs.\n'
                           'No HV or digitizer (separate budget items).'),
             sd.bignum('2.5 MeV', 'leg threshold that hides H-capture and natural γ', DBLUE,
                       f'costs {loss25 * 100:.0f} % of the E_sum > 13 MeV signal'),
             sd.bignum(f'×{gain:.1f}', 'ILL reach, 5 cm + B₄C wrap vs as built (Geant4)', GOLD,
                       f'{sd.sci(r_p5b)} vs {sd.sci(r_ab)}, X17/IPC at 3σ per cycle'),
             gap=56))
D.slide('cover', cover, '''<p>Prompted by Pierfrancesco's comment on the budget page (2026-10-16): "if we buy the plastic plate and we produce
the detector, the cost for each can be within 2 [k]euros each, 8 [k]euros for all the 4" (Scionix), PMTs borrowed again.</p>
<p>Write-up: <code>trigger_scint/TRIGGER_OPTIONS.md</code> §8. Budget page: Upgrade €286k → €234k.</p>''',
        dark=True, short='Cover')

# ------------------------------------------------------------------ 2 setup cartoon
W, H = 1664, 560
g = []
cy = 290
g.append(T(40, 30, 'One arm, side view', 26, INK, 'start', 600))
g.append(f'<circle cx="80" cy="{cy}" r="16" fill="{GOLD}"/>')
g.append(T(80, cy + 50, 'target', 22, MUT))
g.append(f'<rect x="300" y="{cy - 150}" width="34" height="300" fill="#dfe8f3" stroke="{BLUE}" stroke-width="2"/>')
g.append(T(317, cy + 185, 'Micromegas', 22, BLUE))
for i in range(20):
    y0 = cy - 180 + i * 18
    g.append(f'<rect x="440" y="{y0}" width="18" height="16" fill="#e8def5" stroke="{PURPLE}" stroke-width="1"/>')
g.append(T(449, cy + 215, 'SiPM wall', 22, PURPLE))
g.append(f'<rect x="560" y="{cy - 200}" width="70" height="400" fill="#fbe7d3" stroke="{ORANGE}" stroke-width="3"'
         f'{sd.tipattr("78 × 80 × 4–5 cm plastic plate. Drawn thick for clarity.")}/>')
for sgn in (-1, 1):
    ye = cy + sgn * 200
    yp = cy + sgn * 245
    g.append(poly([560, 630, 608, 582], [ye, ye, yp, yp], ORANGE, fill='#f3d2b0',
                  tip='Fishtail light guide (bought, custom PMMA), glued to the polished end face.'))
    g.append(f'<rect x="578" y="{yp - (18 if sgn < 0 else 0)}" width="34" height="18" fill="{INK}"'
             f'{sd.tipattr("PMT: the 8 borrowed tubes, one at each end of each plate.")}/>')
g.append(T(650, cy - 20, 'big plate', 24, ORANGE, 'start', 600))
g.append(T(650, cy + 12, '4–5 cm thick', 22, ORANGE, 'start'))
g.append(T(650, cy - 225, 'guide + PMT', 22, MUT, 'start'))
g.append(T(650, cy + 240, 'guide + PMT', 22, MUT, 'start'))
g.append(arrow(96, cy - 6, 590, cy - 110, RED, 4))
g.append(T(120, cy - 60, 'e± from X17', 24, RED, 'start', 600))
for (x0, y0) in ((960, 150), (990, 300), (960, 430)):
    xs = [x0 - 20 * i for i in range(12)]
    ys = [y0 + (10 if i % 2 else -10) + i * 2 for i in range(12)]
    g.append(poly(xs, ys, GREEN, w=3, tip='Room or beam-induced γ: H capture 2.2 MeV, ¹⁴N capture 10.8 MeV, ...'))
g.append(T(990, 250, 'γ background', 24, GREEN, 'start', 600))
fx = 1200
g.append(T(fx, 30, 'Plate seen from the target', 26, INK, 'start', 600))
w, h, y0 = 180, 300, 120
for j, (n, lab) in enumerate(((1, 'one plate'), (2, 'split in 2'))):
    x0 = fx + j * 240
    for b in range(n):
        bw = w / n
        ww = bw - (6 if n > 1 else 0)
        g.append(f'<rect x="{x0 + b * bw:.0f}" y="{y0}" width="{ww:.0f}" height="{h}" '
                 f'fill="#fbe7d3" stroke="{ORANGE}" stroke-width="3"/>')
        cx = x0 + b * bw + ww / 2
        for sgn, yy in ((-1, y0), (1, y0 + h)):
            g.append(poly([cx - ww / 2 + 4, cx + ww / 2 - 4, cx + 12, cx - 12],
                          [yy, yy, yy + sgn * 36, yy + sgn * 36], ORANGE, fill='#f3d2b0'))
            g.append(f'<circle cx="{cx:.0f}" cy="{yy + sgn * 46}" r="11" fill="{INK}"/>')
    g.append(T(x0 + w / 2, y0 + h + 100, lab, 24, INK, weight=600))
    g.append(T(x0 + w / 2, y0 + h + 130, f'{2 * n} PMTs per arm', 22, MUT))
g.append(T(fx + 90, y0 + h / 2, '78 × 80 cm', 22, MUT, rot=-90))
g.append(T(fx + 440, y0 + h / 2, '↕ beam', 22, MUT, 'start'))
D.slide('setup', sd.title('Deciding: built how, how thick, one piece or two',
                          'The plate sits where the 20 × 30 cm bars were; it closes the trigger leg and measures E_sum')
        + svg(W, H, ''.join(g), 'arm cartoon') + sd.p(
            'Hover the dotted terms and the points on each chart for values and sources.', 22, MUT),
        '''<p>Each arm: Micromegas TPC → SiPM wall (all 20 bars read) → one big plate, read at both ends along the beam through
fishtail guides. The plate replaces the two 20 × 30 × 2 cm bars, which accepted 2.3 % of X17 pairs; 78 × 80 cm plates accept
~14 % (TRIGGER_OPTIONS §2).</p><p>The questions here: buy finished or build in-house; 2, 4 or 5 cm; one plate or two bars per arm;
and whether the thicker plate fires too often on γ.</p>''', short='Setup')

# ------------------------------------------------------------------ 3 cost
parts = [('scint', 'plastic', ORANGE), ('finish', 'polish, wrap, glue', GOLD), ('guides', 'light guides', BLUE),
         ('mech', 'housing', GREY), ('pmts', 'PMTs', PURPLE)]


def breakdown_diy(n, T, bought):
    d = CO.piece_cost_diy(78 / n, 80, T, 2, None, 1)
    out = {p: 4 * n * d[p] for p, _, _ in parts}
    out['pmts'] = 4 * bought * CO.PMT_ECON[1]
    return out


def breakdown_vend():
    d = CO.slab_cost(78, 80, 5, '3"', 2, 'PS', 1)
    return dict(scint=4 * d['scint'], finish=0, guides=4 * d['guides'], mech=4 * d['mech'], pmts=4 * d['pmts'])


opts = [('Vendor-finished PS, 5 cm, new 3"', breakdown_vend(), vend),
        ('In-house, 5 cm, split in 2', breakdown_diy(2, 5, 2), split5),
        ('In-house, 5 cm', breakdown_diy(1, 5, 0), diy5),
        ('In-house, 4 cm', breakdown_diy(1, 4, 0), diy4),
        ('In-house, 2 cm', breakdown_diy(1, 2, 0), diy2)]
P = sd.Plot(1100, 620, x=(0, 150), y=(0, len(opts)), xlabel='four arms, k€ (no HV / digitizer)',
            margin=(20, 40, 100, 390))
P.xticks([(v, f'{v}') for v in range(0, 151, 25)])
for i, (lab, br, rng) in enumerate(opts):
    yc = len(opts) - i - 0.5
    x = 0
    for pk, pname, c in parts:
        v = br[pk] / 1e3
        if v <= 0:
            continue
        X0, X1 = P.X(x), P.X(x + v)
        P.raw(f'<rect x="{X0:.1f}" y="{P.Y(yc) - 26:.1f}" width="{X1 - X0:.1f}" height="52" fill="{c}"'
              f'{sd.tipattr(f"{lab}: {pname} €{v:.1f}k (central)")}/>')
        x += v
    P.raw(line(P.X(rng[0] / 1e3), P.Y(yc), P.X(rng[2] / 1e3), P.Y(yc), INK, 2.5))
    for e in (rng[0], rng[2]):
        P.raw(line(P.X(e / 1e3), P.Y(yc) - 12, P.X(e / 1e3), P.Y(yc) + 12, INK, 2.5))
    P.raw(T(P.x0 - 16, P.Y(yc) + 8, lab, 23, INK, 'end'))
    P.raw(T(P.X(rng[2] / 1e3) + 12, P.Y(yc) + 8, f'{rng[1] / 1e3:.0f}', 24, INK, 'start', 600))
P.text(10, 0.12, "Pierfrancesco: €8k for 4 plates (plastic only)", 21, GREEN)
P.vline(8, GREEN,
        tip='Budget-page comment, 2026-10-16: ~€2k per plate (Scionix), PMTs borrowed. Plastic only, no guides.')
P.text(80, 1.55, f'×{vend[1] / diy5[1]:.1f} cheaper in-house', 30, GREEN, weight=600)
side = sd.col(
    sd.legend([(n, c, 'box') for _, n, c in parts] + [('low–high range', INK)], 22),
    sd.p('The raw plastic is about half of an in-house plate; the light guides are next.', 24),
    sd.p('The 8 borrowed PMTs make the single plate cheap. Splitting buys 8 more.', 24, MUT), gap=28, w=480)
D.slide('cost', sd.title('In-house plates cost a third of vendor-finished ones',
                         'Central cost per option (stacked) with the low–high range; four arms, 78 × 80 cm')
        + sd.row(P.svg('cost bars'), side, gap=40),
        f'''<p>Model: <code>costs.py</code> (<code>piece_cost_diy</code>, <code>arms_diy</code>). Raw plate
{CO.RAW_PER_CM3[0]}–{CO.RAW_PER_CM3[2]} €/cm³ (central {CO.RAW_PER_CM3[1]}).</p>
<ul><li>Low end: Pierfrancesco/Scionix, ~€2k per plate. That is consistent with cast scintillator at ~$40/kg in 2001
(NIM A 466, 482), ≈ €65/kg today.</li>
<li>High end: CERN 2025, an 80 × 80 × 2 cm EJ-200 sheet at 6k CHF (indico 1546121).</li>
<li>Scionix has built 5 cm, 0.5–1 m² EJ-200 panels (Felsenkeller veto, arXiv:2301.03905).</li></ul>
<p>Per piece, central: edge finishing €300, wrapping €150/m², cement €100, guide €600–1000 each (Eljen/Shalom make
them to order), housing €800. Extra PMTs (economy 2"): €600, from Pierfrancesco's LS rebuild (16 PMTs + cases €7k).
Workshop labour is in kind and not counted.</p>
<p><b>Ask Pierfrancesco:</b> is the €2k for 78 × 80 × <b>5</b> cm, and PVT or polystyrene? Which tubes are the
borrowed 8 (2" or 3")?</p>''', foot=f'Source: {SRC}/costs.py; budget page Upgrade €286k → €234k', short='Cost')

# ------------------------------------------------------------------ 4 light vs thickness
Ts = [2, 3, 4, 5, 6]
mats = [('PVT', 'PVT (EJ-200 class)', BLUE), ('PS', 'polystyrene', ORANGE), ('PS_DIY', 'polystyrene, edges polished in-house', RED)]
PL = sd.Plot(800, 560, x=(1.5, 6.5), y=(0, 180), xlabel='plate thickness [cm]', ylabel='light [pe/MeV], 2 × 3"',
             title='Light falls as 1/thickness')
PL.xticks([(t, str(t)) for t in Ts]).yticks([(v, str(v)) for v in range(0, 181, 30)])
PU = sd.Plot(800, 560, x=(1.5, 6.5), y=(0, 20), xlabel='plate thickness [cm]', ylabel='non-uniformity [% rms]',
             title='Uniformity does not get worse')
PU.xticks([(t, str(t)) for t in Ts]).yticks([(v, str(v)) for v in range(0, 21, 5)])
for m, lab, c in mats:
    r3 = [opt('thick', m, t, '3"') for t in Ts]
    r2 = [opt('thick', m, t, '2"') for t in Ts]
    PL.line(Ts, [float(r['pe_per_MeV']) for r in r3], c,
            tips=[f'{lab}, {t} cm, 2 × 3": {float(r["pe_per_MeV"]):.0f} pe/MeV (toy; real ~÷1.5–2)' for t, r in zip(Ts, r3)])
    PL.line(Ts, [float(r['pe_per_MeV']) for r in r2], c, dash='8 6', r=4,
            tips=[f'{lab}, {t} cm, 2 × 2" (borrowed?): {float(r["pe_per_MeV"]):.0f} pe/MeV' for t, r in zip(Ts, r2)])
    PU.line(Ts, [100 * float(r['nonunif_rms']) for r in r3], c,
            tips=[f'{lab}, {t} cm: {100 * float(r["nonunif_rms"]):.1f} % rms across the face, '
                  f'min/max {float(r["min_over_max"]):.2f}' for t, r in zip(Ts, r3)])
    if m == 'PVT':
        PU.line(Ts, [100 * float(r['depth_rms']) for r in r3], c, dash='3 5', r=4,
                tips=[f'PVT, {t} cm: {100 * float(r["depth_rms"]):.1f} % between emission at 0.1, 0.5, 0.9 T'
                      for t, r in zip(Ts, r3)])
PU.text(2.1, 2.6, 'PVT, through the depth (dotted)', 21, BLUE)
D.slide('light', sd.title('Thick plates collect less light, but just as evenly; polystyrene is the uniformity risk',
                          'Optics toy, 78 × 80 cm plate, a PMT at both ends, emission at three depths')
        + sd.row(PL.svg('light vs T'), PU.svg('uniformity vs T'), gap=44)
        + sd.legend([(lab, c) for _, lab, c in mats] + [('2 × 2" PMTs', MUT, 'dash')], 22),
        '''<p><code>optics_toy.py --refresh</code> → <code>out/optics_refresh.csv</code>. A photon ray-trace: TIR (0.98 per bounce,
0.95 for edges polished in-house), Al-foil wrap, fishtail guides with étendue loss, PMT QE and TTS. Bulk attenuation: 2.5 m for
PVT, 1 m for polystyrene (UPS-923A/ZEPLIN-III). Absolute pe/MeV are optimistic by ~1.5–2×: treat them as a ranking.</p>
<p>Light per MeV falls because the same PMT covers a smaller fraction of a thicker end face. The lepton deposit grows with thickness,
so pe per lepton falls more slowly than 1/T. Width is not the issue either: 78 cm with both ends read is 4–5 % (PVT). Light is lost
along the 80 cm length.</p>
<p>Polystyrene's non-uniformity is a smooth function of hit position, which the Micromegas measure. It can be mapped with cosmics,
but it eats into the energy resolution.</p>''', short='Light')

# ------------------------------------------------------------------ 5 split
Ns = [1, 2, 3, 4]
PS_ = sd.Plot(800, 540, x=(0.6, 4.4), y=(0, 280), xlabel='bars per arm (78/N × 80 × 5 cm each)',
              ylabel='light per bar [pe/MeV]', title='Each bar gets N× the light')
PS_.xticks([(n, str(n)) for n in Ns]).yticks([(v, str(v)) for v in range(0, 281, 40)])
PT = sd.Plot(800, 540, x=(0.6, 4.4), y=(0, 260), xlabel='bars per arm', ylabel='σt at 5 MeV [ps]',
             title='…and better timing')
PT.xticks([(n, str(n)) for n in Ns]).yticks([(v, str(v)) for v in range(0, 261, 50)])
for m, lab, c in (('PS_DIY', 'polystyrene', ORANGE), ('PVT_DIY', 'PVT', BLUE)):
    for pmt, dash in (('3"', None), ('2"', '8 6')):
        rr = []
        for n in Ns:
            r = opt('split', m, 5, pmt, n) if n > 1 else (opt('thick', 'PS_DIY', 5, pmt) if m == 'PS_DIY' else None)
            rr.append(r)
        xs = [n for n, r in zip(Ns, rr) if r]
        rs = [r for r in rr if r]
        PS_.line(xs, [float(r['pe_per_MeV']) for r in rs], c, dash=dash, r=6 if not dash else 4,
                 tips=[f'{lab}, {n} bar(s), 2 × {pmt} per bar: {float(r["pe_per_MeV"]):.0f} pe/MeV, '
                       f'{100 * float(r["nonunif_rms"]):.0f} % rms' for n, r in zip(xs, rs)])
        PT.line(xs, [1e3 * float(r['sigma_t_5MeV_ns']) for r in rs], c, dash=dash, r=6 if not dash else 4,
                tips=[f'{lab}, {n} bar(s), {pmt}: σt {1e3 * float(r["sigma_t_5MeV_ns"]):.0f} ps at 5 MeV'
                      for n, r in zip(xs, rs)])
PT.hline(200, RED, label='ILL requirement ~200 ps', tip='The ILL timing scenario assumes σt ≈ 0.2 ns.')
s2 = next(r for r in SEAM if r['N'] == '2')
D.slide('split', sd.title('Splitting a plate in two doubles the light per bar and halves the rate per channel',
                          'Optics toy, 5 cm, edges polished in-house; one plate (N = 1) vs N bars side by side')
        + sd.row(PS_.svg('split light'), PT.svg('split timing'), gap=44)
        + sd.legend([('polystyrene', ORANGE), ('PVT', BLUE), ('2 × 3" per bar', MUT), ('2 × 2" per bar', MUT, 'dash')], 22),
        f'''<p>Same PMT on half the end face → ×2 light per MeV, and shorter guides → less time spread. Uniformity stays set by the material.</p>
<p>Seams (<code>sim/accept/seams.csv</code>, Geant4 T1 entry points): with N = 2, {100 * float(s2["within_1cm"]):.1f} % of accepted legs land
within 1 cm of the seam, {100 * float(s2["within_2p5cm"]):.1f} % within 2.5 cm. E_sum sums both bars, so only a per-bar trigger threshold
would care. The wrap gap is ~2 mm, 0.5 % of the area.</p>
<p>Cost: +8 PMTs, +4 guides, +4 housings ≈ +€{(split5[1] - diy5[1]) / 1e3:.0f}k. The polystyrene single plate on the borrowed 2" tubes is the weakest
point (~240 ps in the toy, worse in reality); a split, 3" tubes or PVT each bring it under 200 ps.</p>''',
        foot=f'Source: {SRC}/out/optics_refresh.csv; N = 1 PVT not run with in-house edges', short='Split')

# ------------------------------------------------------------------ 6 gamma vs signal
EG = sorted({float(r['E_gamma']) for r in GAM})
EGp = [e for e in EG if e >= 1.4]


def grate(E, T, thr):
    for r in GAM:
        if float(r['E_gamma']) == E and float(r['T_cm']) == T:
            return float(r[f'Hz_gt_{thr:g}']) / 1e3


PG = sd.Plot(800, 560, x=(1.2, 20, 'log'), y=(0, 13), xlabel='γ energy [MeV]',
             ylabel='singles per plate [kHz per µSv/h]', title='γ: 5 cm fires ×2.5 as often')
PG.xticks([(1.5, '1.5'), (2, '2'), (3, '3'), (5, '5'), (10, '10'), (20, '20')]).yticks([(v, str(v)) for v in range(0, 14, 2)])
for (T_, thr, c, dash, lab) in ((2, 1.67, GREY, None, '2 cm, > 1.67 MeV'), (5, 1.67, ORANGE, None, '5 cm, > 1.67 MeV'),
                                (5, 2.5, GREEN, '8 6', '5 cm, > 2.5 MeV')):
    ys = [grate(e, T_, thr) for e in EGp]
    PG.line(EGp, ys, c, dash=dash, tips=[f'{lab}: {y:.1f} kHz per µSv/h of {e} MeV γ (75 × 75 plate, diffuse field)'
                                        for e, y in zip(EGp, ys)])
for e, lab in ((2.223, 'H capture'), (2.614, '²⁰⁸Tl'), (10.83, '¹⁴N capture')):
    PG.vline(e, RULE, label=None, tip=f'{lab}: {e} MeV')
PG.text(2.0, 12.3, 'H', 20, MUT).text(2.75, 12.3, 'Tl', 20, MUT).text(11.3, 12.3, '¹⁴N', 20, MUT)
PG.text(4.6, 11.0, '2.5 MeV threshold: blind below 2.6 MeV', 21, GREEN, weight=600)
thr_list = [0.5, 1.0, 1.67, 2.5, 3.0, 4.0, 5.0]
PS2 = sd.Plot(800, 560, x=(0, 5.5), y=(0, 14), xlabel='leg threshold [MeV]', ylabel='X17 acc × P(E_sum > 13) [%]',
              title='Signal: a 2.5 MeV threshold costs little')
PS2.xticks([(v, f'{v:g}') for v in (0, 1, 2, 3, 4, 5)]).yticks([(v, str(v)) for v in range(0, 15, 2)])
for T_, c in ((2, GREY), (4, BLUE), (5, ORANGE)):
    ys = [100 * acc13(T_, t) for t in thr_list]
    PS2.line(thr_list, ys, c, tips=[f'{T_} cm, threshold {t} MeV: {y:.1f} %' for t, y in zip(thr_list, ys)])
PS2.vline(2.5, GREEN, label=f'2.5 MeV: −{loss25 * 100:.0f} %')
PS2.text(0.3, 1.0 + 100 * acc13(2, 1.67), '2 cm', 21, GREY)
PS2.text(0.3, 100 * acc13(4, 1.0) - 1.1, '4 cm', 21, BLUE).text(0.3, 100 * acc13(5, 1.0) + 0.5, '5 cm', 21, ORANGE)
D.slide('gamma', sd.title('A thick plate sees more γ, but a 2.5 MeV threshold hides the soft ones for 6 % of the signal',
                          'Left: Compton toy, diffuse γ field, 75 × 75 plate. Right: Geant4 T1 X17 pairs, 78 × 80 plate, MM + 20 SiPM bars')
        + sd.row(PG.svg('gamma singles'), PS2.svg('threshold scan'), gap=44)
        + sd.legend([('2 cm, > 1.67 MeV', GREY), ('5 cm, > 1.67 MeV', ORANGE), ('5 cm, > 2.5 MeV', GREEN, 'dash'),
                     ('4 cm (signal)', BLUE)], 22),
        f'''<p><b>Why the threshold cannot scale with thickness:</b> the X17 leptons stop in the plate. An accepted lepton leaves a median
7.6 MeV even in 10 cm (middle half 4.7–10.8), so 4 MeV would cost 35 % and 3 MeV {loss3 * 100:.0f} %.</p>
<p><b>γ toy</b> (<code>gamma_toy.py</code>, an analytic stand-in): Klein–Nishina Compton, pair production, straight-line electrons,
no energy smearing. Use 2.7–3 MeV where ²⁰⁸Tl dominates. Normalised per µSv/h with ICRP 74 h*(10). The total per arm does not
change with a split; per channel it falls as 1/N.</p>
<p>Hard γ (Fe/Al/¹⁴N capture, ³He(n,γ), ⁸Be) pass any usable threshold. For them only shielding, a split, or a thinner plate help.</p>''',
        foot=f'Sources: {SRC}/gamma_toy.py → out/gamma_rates.csv; sim/trig_threshold.py → sim/accept/thr_X17.csv', short='γ vs signal')

# ------------------------------------------------------------------ 7 ILL Geant4
gates = [0, 10, 25, 50, 100]
geoms = [('asbuilt', 'n_TOF as built', INK), ('P2', '70 × 70 × 2', GREY), ('P5L', '75 × 75 × 5 + ⁶LiF', BLUE),
         ('P5B', '75 × 75 × 5 + B₄C', GREEN)]
panels = []
for air, ttl in ((1.0, 'Air around the beam'), (0.1, 'He flight tube (air × 0.1)')):
    PR = sd.Plot(800, 560, x=(0, 100), y=(0, 0.045), xlabel='pile-up window G [ns]',
                 ylabel='3σ reach [10⁻³ X17/IPC per cycle]', title=ttl)
    PR.xticks([(v, str(v)) for v in gates]).yticks([(v / 1000, f'{v:g}') for v in range(0, 46, 5)])
    for gm, lab, c in geoms:
        ys = [best_reach(gm, air, gg) for gg in gates]
        if not any(ys):
            continue
        PR.line(gates, ys, c, tips=[f'{lab}, G = {gg} ns: {sd.sci(y) if y else "–"}' for gg, y in zip(gates, ys)])
    PR.text(55, 0.040, 'lower is better', 21, MUT)
    if air == 1.0:
        yb = best_reach('P5B', 1.0, 10)
        PR.raw(arrow(PR.X(10), PR.Y(yb) + 22, PR.X(5), PR.Y(yb) + 22, GREEN, 3))
        PR.text(12, yb - 0.0022, 'split in 2 ≈ G/2', 21, GREEN, weight=600)
    panels.append(PR.svg(ttl))
D.slide('ill', sd.title(f'At the ILL, Geant4 says the shielded 5 cm plate wins: ×{gain:.1f} in reach over as built',
                        'Geant4 TB campaign (G1 cell), timing scenario (σt 0.2 ns + μ veto), E_sum > 13 MeV, best trigger menu')
        + sd.row(*panels, gap=44) + sd.legend([(lab, c) for _, lab, c in geoms], 22),
        '''<p>Runs finished 2026-10-02 but were analysed only now (<code>sim/bkg/*.json</code>, <code>bkg_figs.py</code>).
G is the window in which a foreign slab deposit piles onto a pair's E_sum. It is ~10 ns with waveform digitizers on the plate PMTs
and 50–100 ns with a shaping QDC. Splitting the plate into N bars divides the effective G by N.</p>
<p>Slab singles per arm above 1.67 MeV: 0.23 MHz as built, 0.33 MHz with P5L/P5B, mostly air ¹⁴N(n,γ). The 2 cm plate (P2) is
worse than as built: more area for cosmics and accidentals without the calorimetry.</p>
<p><b>Missing:</b> the bare 5 cm plate (P5). Its C1w contract was never produced. Unwrapped, it makes ~2×10⁷ H(n,γ)/s at
10¹⁰ absorbed n/s. A 2.5 MeV threshold would hide those from the leg, but not from pile-up.</p>''',
        foot='Source: /eos/experiment/ntof/data/x17/ill/TB/analysis/*.json (bkg_reach.py)', short='ILL Geant4')

# ------------------------------------------------------------------ 8 next
fac = [('ILL PF1B', 'Geant4 done for wrapped 5 cm: ×2 better', 'bare-plate run (C1w_P5); P5B at 2.5 MeV; hall dose rate (ask)', GOLD),
       ('LNL', 'Geant4: beam γ negligible, cosmic-dominated', 'low risk: Li₂O target, 2.5 MeV threshold', DGREEN),
       ('GANIL NFS', 'Geant4: singles ×5 with 5 cm (mostly fast n)', 'rerun with 4 cm, split, 2.5 MeV; add to accidentals', DRED),
       ('MEDAPP, Birmingham', 'not simulated; hard γ in the beam', 'add the plate (1 vs 2 bars) to the soft-beam run', DRED)]
cards = ''.join(
    f'<div style="flex:1;border-top:4px solid {c};padding-top:20px;display:flex;flex-direction:column;gap:10px">'
    f'<p style="font-size:30px;font-weight:600;color:{DINK}">{n}</p>'
    f'<p style="font-size:23px;color:{DMUT};line-height:1.3">{a}</p>'
    f'<p style="font-size:24px;color:{DINK};line-height:1.3">→ {b}</p></div>' for n, a, b, c in fac)
D.slide('next', sd.kicker('Is more work needed? Yes, before buying')
        + sd.title(f'<span style="color:{DINK}">The build route and the optics are settled enough; '
                   'γ sensitivity per facility and the split decide the design</span>')
        + f'<div style="display:flex;gap:40px">{cards}</div>'
        + sd.row(sd.col(sd.p('Ask first', 28, DBLUE, 600),
                        sd.p('Pierfrancesco: is the €2k for 78 × 80 × 5 cm, PVT or polystyrene? Which tubes are the 8 borrowed ones? '
                             'Scionix quote in writing.', 24, DINK)),
                 sd.col(sd.p('Then build', 28, DBLUE, 600),
                        sd.p('One prototype plate on the cosmic bench, with the Micromegas giving position: anchors the light toy, '
                             'and measures the hall γ rate above 2.5 MeV.', 24, DINK)),
                 sd.col(sd.p('Not covered here', 28, DRED, 600),
                        sd.p('The neutron sensitivity of the plastic (n–p recoils) at fast-neutron sites; a two-bar Geant4 geometry; '
                             'hall γ at any site (no facility has given a dose rate).', 24, DINK)), gap=56),
        '''<p>Follow-up table in full: <code>TRIGGER_OPTIONS.md</code> §8.6. The Geant4 change that would settle the split: a real
two-volume plate in <code>--big-plastic</code>, or per-bar scoring of the hits in <code>trig_reduce.py</code>.</p>''',
        dark=True, short='Next')

out = D.write(HERE / 'out' / 'big-plastics.html', note_meta=dict(
    title='Big trigger plastics: build them ourselves',
    summary=f'In-house plates {k(diy5[1])} vs {k(vend[1])}; thick plates stay uniform; a 2.5 MeV threshold hides soft γ; '
            'split-in-two option; per-facility γ follow-up.',
    tags='x17, facilities, detector', date='2026-10-20'))
print('wrote', out)
