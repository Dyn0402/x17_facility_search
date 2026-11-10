"""Short slide note for Pierfrancesco: his ogive in Al with a Cu liner, how it is built (CU_LINER.md, 2026-11-04).

Six slides, figure-first, built on the 3D renders of the target page's "Al ogive + Cu liner" tab. Writes
lnl/out/target/lnl-culiner-pf.html (the note) and lnl/out/target/lnl-culiner-pf.pdf (one slide per page, to email):

    bash lnl/viz/render_culiner_shots.sh                       # 3D renders → lnl/out/target/culiner_pf/*.jpg
    ~/PycharmProjects/nTof_x17/.venv/bin/python lnl/target/deck/build_culiner_pf_deck.py
    python3 ~/PycharmProjects/dylan-cern-site/scripts/add-note.py lnl/out/target/lnl-culiner-pf.html \\
        --slug lnl-culiner-pf --force --deploy
"""
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
sys.path.insert(0, str(LNL / 'target' / 'shapes'))
import nd_reach_io as nd  # noqa: E402
SH, OP = LNL / 'out' / 'target' / 'shapes', LNL / 'out' / 'target' / 'options'
IMG = LNL / 'out' / 'target' / 'culiner_pf'
OUTF = LNL / 'out' / 'target' / 'lnl-culiner-pf.html'
PDF = OUTF.with_suffix('.pdf')
PAGE = 'https://dylan-neff.web.cern.ch/facilities/lnl-target.html#culiner'

GR, GA = pd.read_csv(SH / 'geant_reach.csv'), pd.read_csv(SH / 'geant_acceptance.csv')
PROF = pd.read_csv(OP / 'culiner_profile.csv')
LIMIX = pd.read_csv(OP / 'culiner_li_mix.csv')
CU, AL, LI = sd.GOLD, '#8a96a8', sd.PURPLE


def g4(cfg, ep=1100.0, col='days_fit', det='bigP'):
    if col == 'days_fit':     # days: the reference fit (nd_reach.csv); EPC share from geant_reach.csv
        return nd.best(cfg, det, ep)
    q = GR[(GR.config == cfg) & (GR.det == det) & (GR.Ep_keV == ep)]
    return float(q[col].iloc[0]) if len(q) else np.nan


def sig(cfg):
    q = GA[(GA.config == cfg + '_bigP') & (GA['sample'] == 'x17')]
    return float(q.sigma68_deg.iloc[0]) if len(q) else np.nan


ROWS = [('his Cu ogive, 200 µm', 'ogCu200_los', 'ogCu200', '~0.1 %'),
        ('Al 300 + Cu 12', 'ogAl300cu12r8m4', 'ogAl300cu12r8m4', '12 %'),
        ('<b>Al 400 + Cu 12</b>', 'ogAl400cu12r8m4', 'ogAl400cu12r8m4', '2.5 %'),
        ('Al 300 + Ti 15', 'ogAl300ti15r8m4', 'ogAl300ti15r8m4', '0')]
R = [dict(name=n, sigma=sig(s), d110=g4(c), d103=g4(c, 1030.0), epc=g4(c, col='B_epc_share'), occ=o) for n, c, s, o in ROWS]
HIS, A3, A4 = R[0], R[1], R[2]


def pic(name, w=None, h=None, tip=None):
    return sd.img(IMG / f'{name}.jpg', w=w, h=h, tip=tip, fit='cover')


def cap(t, size=22):
    return sd.p(t, size, sd.MUT)


def kpi(v, label, color):
    return (f'<div style="border-top:4px solid {color};padding-top:8px">'
            f'<p style="font-size:44px;font-weight:600;color:{color};line-height:1.05">{v}</p>'
            f'<p style="font-size:21px;color:{sd.MUT};line-height:1.25">{label}</p></div>')


D = sd.Deck('LNL target: your ogive in Al, with Cu only where the beam stops',
            'A short proposal for Pierfrancesco: his ogive made of Al 0.4 mm with a 12 µm Cu liner over the tip and a masked Li film, '
            'both laid from the beam axis. 3D views, how it is built, the Geant4 numbers, and the questions.')

# ---- 1. the proposal ------------------------------------------------------------------------------------------------
D.slide('proposal',
        sd.title('Your ogive, in Al, with Cu only where the beam stops',
                 'Same shape as your 27 Oct CAD. Al 6061-T6 0.35–0.4 mm · ≥ 12 µm Cu over r ≤ 10 mm · 20 µm Li over r ≤ 4 mm · '
                 'both films laid from the beam axis') +
        sd.row(pic('d_design', w=1020, h=640, tip='3D view of the target page: legs of 139 accepted X17 pairs (Geant4), coloured by the Al they cross'),
               sd.col(kpi(f'{A4["sigma"]:.1f}° <span style="font-size:26px;color:{sd.MUT}">vs {HIS["sigma"]:.1f}°</span>',
                          'σ68 of the opening angle, against the Cu ogive (Geant4 L12/L11)', sd.GREEN),
                      kpi(f'×{HIS["d110"] / A4["d110"]:.1f}–{HIS["d110"] / A3["d110"]:.1f}',
                          'faster to 3σ at the ATOMKI strength at the same current (Al 0.4–0.3 mm)', sd.GREEN),
                      kpi(f'{100 * A4["epc"]:.0f} % <span style="font-size:26px;color:{sd.MUT}">vs {100 * HIS["epc"]:.0f} %</span>',
                          'of the background from γ converting in the shell', sd.GREEN),
                      sd.p('The leptons cross 0.4 mm of Al instead of 0.2 mm of Cu. The Cu is only a beam stop: '
                           'the protons end in it, never in the Al.', 23), gap=26, w=560), gap=48),
        notes='Geant4 run L12 (MX17_Full_Geant branch lnl_culiner): the CAD ogive in Al with a 12 µm Cu liner where the shell radius is '
              '≤ 8 mm, pair vertices only where the Li is (r ≤ 4 mm). Big plastics, 1 µA; days from the reference fit (θ × |y| × E_sum, '
              'background shape floating; FEASIBILITY_SIM.md §19, 10 Nov 2026). Legs in the picture '
              'are coloured by the Al crossed (green < 1 % X₀, orange 1–3 %, red > 3 %; thin-wall trace). CU_LINER.md §0, §7.',
        short='the proposal')

# ---- 2. the layers ----------------------------------------------------------------------------------------------------
lay = sd.table(['layer', 'how thick', 'where', 'why'],
               [['Al 6061-T6', '0.35–0.4 mm', 'the whole shell + a 2.5 × 10 mm collar', 'holds 1 bar (×10 margin at 0.4); stops the Cu K x-rays'],
                ['Cu', '≥ 12 µm along the beam', 'r ≤ 10 mm (the tip and first ~19 mm of flank)', 'stops the protons (10.7 µm needed); Li must not touch Al'],
                ['Li', '20 µm along the beam', 'r ≤ 4 mm, inside the Cu', 'the target; r > 4 sits up to 9 mm upstream of the tip']],
               size=22, widths=[170, 260, 420, 820], align=['left'] * 4)
D.slide('layers',
        sd.title('Three layers, the thin ones only at the tip',
                 'A σ 2 mm beam puts 99.9 % of its protons inside r 7.4 mm, so nothing needs to be coated beyond r ≈ 10 mm') +
        sd.row(sd.col(pic('d_explode', w=900, h=470), cap('Pulled apart along the beam: the Al shell, the Cu cap, the Li cap (thin layers drawn ×20–30).'), gap=8),
               sd.col(pic('d_tip', w=780, h=470), cap('The tip, cut open: Li (purple) on Cu (orange) on Al; dots are where a σ 2 mm beam lands.'), gap=8), gap=40) +
        lay,
        notes='PSTAR ranges: 6.0 µm of Cu after the Li (872 keV), 8.7 µm with no Li at 1.15 MeV; ×1.12 + 1 µm for straggling, thickness '
              'error and roughness gives 10.7 µm, design 12 µm. Cu reaches ≥ 3 mm beyond the Li so no proton meets Li-on-Al or bare Al '
              'at full energy. Bare Al outside r 8 mm even with a 1 % halo makes 0.4 % of the γ₀ in ²⁷Al(p,γ). CU_LINER.md §1–4.',
        short='the layers')

# ---- 3. how it is built -------------------------------------------------------------------------------------------------
def stepcard(name, head, text, color):
    return sd.col(pic(name, w=820, h=305), sd.p(f'<b style="color:{color}">{head}</b> {text}', 22), gap=8)


D.slide('build',
        sd.title('How it is built: one vacuum system, the source on the axis',
                 'the open base faces the source 150–400 mm away; aperture plates decide where each film ends') +
        sd.row(stepcard('b_shell', '1 · Shell.', 'Machine or spin the Al ogive, 0.35–0.4 mm, with a thick collar at the base for the joint '
                        '(63 mm behind the tip, out of the arms\' view).', sd.INK),
               stepcard('b_cu', '2 · Cu.', 'Ar-ion etch the inside, then sputter or evaporate 12–16 µm of Cu through a Ø12 mm aperture: '
                        'it lands to r ≈ 10 mm. 1–2 h at 0.1–0.3 µm/min.', CU), gap=40) +
        sd.row(stepcard('b_li', '3 · Li.', 'Without breaking vacuum (or under Ar), evaporate 20 µm of Li through a Ø4 mm aperture: '
                        'it lands to r ≈ 4 mm, inside the Cu. A witness coupon records both thicknesses.', LI),
               stepcard('b_beam', '4 · On the line.', 'Clamp the collar on an O-ring flange, adapter to DN40, He leak test. '
                        'Minutes of PIGE at 1.10 MeV: no Al lines, 478 keV present.', sd.GREEN), gap=40),
        pad='64px 128px 60px',
        notes='Schematic: the chamber, sources and masks show the geometry, not a real station. Aperture radii are for a point source '
              'on the axis 150 mm upstream of the tip, plate 78 mm in front of the source (Cu Ø11.9 mm, Li Ø4.3 mm); a real magnetron '
              'gives a penumbra of a few mm, which is why the Cu edge sits 6 mm beyond the Li edge. Plating instead (any shop): double '
              'zincate, Cu strike, acid Cu 15–20 µm with an anode wire on the axis, bake 150 °C; the Li still goes on from the axis. '
              'CU_LINER.md §8. The interactive version (rotate, step through) is on the target page.',
        short='how it is built')

# ---- 4. why from the axis ------------------------------------------------------------------------------------------------
P = sd.Plot(860, 520, x=(0, 12), y=(0, 36), xlabel='radius on the shell where the beam lands (mm)', ylabel='Cu thickness (µm)')
P.xticks([(v, str(v)) for v in (0, 2, 4, 6, 8, 10, 12)]).yticks([(v, str(v)) for v in (0, 6, 12, 18, 24, 30, 36)])
pr = PROF[PROF.rho_mm <= 12]
P.line(pr.rho_mm, pr.Cu_beam_uniform, sd.GREY, tips=[f'r {a:.1f}: {b:.1f} µm along the beam' for a, b in zip(pr.rho_mm, pr.Cu_beam_uniform)])
P.line(pr.rho_mm, pr.Cu_beam_los150, CU, tips=[f'r {a:.1f}: {b:.1f} µm along the beam' for a, b in zip(pr.rho_mm, pr.Cu_beam_los150)])
P.line(pr.rho_mm, pr.Cu_normal_los150, CU, dash='6 5', tips=[f'r {a:.1f}: {b:.1f} µm along the normal' for a, b in zip(pr.rho_mm, pr.Cu_normal_los150)])
P.hline(10.7, sd.RED, dash='4 4', label='needed along the beam: 10.7 µm')
lm = LIMIX.set_index(['Ep_keV', 'film'])
li_rows = [[lab, sd.pct(lm.loc[(1100.0, f)].f17, 1), sd.pct(lm.loc[(1030.0, f)].f17, 1)]
           for f, lab in (('uniform film, no mask (L11)', 'same thickness along the normal'),
                          ('line of sight (150 mm), mask r<=4', '<b>laid from the axis, r ≤ 4</b>'))]
D.slide('axis',
        sd.title('Why lay both films from the axis',
                 'a line-of-sight coat lands ∝ cos(incidence), the same factor by which the beam\'s path through it grows') +
        sd.row(sd.col(P.svg('Cu thickness against radius'),
                      sd.legend([('plated, uniform 12 µm: along the beam', sd.GREY, 'line'), ('from the axis: along the beam', CU, 'line'),
                                 ('from the axis: along the normal', CU, 'dash')], size=19), gap=4),
               sd.col(sd.p('On the 65° flank a film of fixed normal thickness is ×2.4 longer along the beam. For the Cu that is only wasted '
                           'metal; for the Li it is a problem: the protons leave it below 441 keV and the 17.64 MeV line grows.', 24),
                      sd.p('17.64 MeV share of the γ₀', 24, sd.INK, 600),
                      sd.table(['Li film', '1.10 MeV', '1.03 MeV'], li_rows, size=23),
                      sd.p('From the axis both films come out constant along the beam: 12–14 µm of Cu to r 8 mm, ~20 µm of Li everywhere. '
                           f'1.03 MeV then costs only ~{100 * (A4["d103"] / A4["d110"] - 1):.0f} % in days against 1.10.', 24, sd.MUT), gap=18, w=760), gap=48),
        notes='culiner_profile.csv (source 150 mm upstream of the tip; at 400 mm the Cu along the beam is flat to ±10 % to r 8 mm) and '
              'culiner_li_mix.csv (share-weighted ⁸Be yields over the σ 2 mm spot, target_model.layered_yield). CU_LINER.md §2–3.',
        short='why from the axis')

# ---- 5. against his Cu ogive -------------------------------------------------------------------------------------------
tab = sd.table(['', 'σ68', 'days/µA 1.10', '1.03 MeV', 'EPC', 'MM x-rays /arm /µA'],
               [[r['name'], f'{r["sigma"]:.1f}°', f'{r["d110"]:.2f}', f'{r["d103"]:.2f}', sd.pct(r['epc']), r['occ']] for r in R],
               size=22, widths=[260, 90, 150, 120, 80, 200])
D.slide('compare',
        sd.title('Against the Cu ogive: same shape, the metal changes',
                 f'Geant4 L11/L12, big plastics, days to 3σ at the ATOMKI strength per µA ({nd.LABEL})') +
        sd.row(sd.col(pic('d_his', w=760, h=560), cap('Top: Cu 200 µm, every leg crosses the Cu (red). Bottom: Al 0.4 mm + Cu liner, legs by Al crossed.'), gap=8),
               sd.col(tab,
                      sd.p('<b>The price is Cu K x-rays (8 keV)</b> from where the beam stops. Al absorbs them hard: each 0.1 mm divides '
                           'what reaches the Micromegas by ~3.7. Hence <b>0.4 mm</b>: 2.5 % occupancy per arm per µA, so they never limit at 1 µA '
                           '(and would allow ~4 µA, if LNL can give that at 1.1 MeV).', 23),
                      sd.p('<b>Ti instead of Cu</b> (15 µm) makes no x-ray that escapes and gives σ68 9.8°, but takes up hydrogen.', 23, sd.MUT),
                      sd.p(f'At 1 µA the x-rays limit neither design, so the Al one is ×{HIS["d110"] / A4["d110"]:.1f} faster. It also wins on '
                           'what matters for a claim: resolution, ×6 less EPC, ×2.8 fewer trigger legs.', 23, sd.MUT), gap=20, w=940), gap=48),
        notes='Days: nd_reach.csv (the reference fit, background shape floating, MC-safe; FEASIBILITY_SIM.md §19, 10 Nov 2026; '
              'the statistics-only days sent earlier were optimistic by ×1.3–1.5). EPC and σ68: geant_reach.csv / geant_acceptance.csv; '
              'occupancies from the Geant4 L12 x-ray libraries × the Geant4 TestEm5 PIXE yields '
              '(Cu K as estimated, Mo K ×2 the earlier estimate). As built (1.10 MeV, liquid repaired / as at n_TOF): '
              + '; '.join(f'{n} {nd.asb_pair(c, 1100)} d' for n, c, _s, _o in ROWS).replace('<b>', '').replace('</b>', '')
              + '. ' + nd.ASB_NOTE + ' Single-arm legs per µA into DREAM: 590 against 1630. CU_LINER.md §6–7.',
        short='against the Cu ogive')

# ---- 6. questions -----------------------------------------------------------------------------------------------------
D.slide('questions', sd.kicker('Your view?') +
        sd.row(sd.col(sd.p('What we would like to know', 34, sd.DINK, 600),
                      sd.p('1 · The <b>beam spot</b> at the target, σ and halo: it sets the Cu and mask radii (we assume σ 2 mm).', 27, sd.DINK),
                      sd.p('2 · Can the <b>thin-film lab</b> ion-etch, then sputter or evaporate ~15 µm of Cu inside the ogive from the axis, '
                           'and Li through a mask, ideally without breaking vacuum?', 27, sd.DINK),
                      sd.p('3 · Can the workshop make the shell in <b>Al 6061-T6 at 0.35–0.4 mm</b> with a collar (not 0.2 mm)?', 27, sd.DINK),
                      sd.p('4 · What <b>current</b> do you expect at 1.1 MeV? Our numbers assume 1 µA; there the x-rays never matter.', 27, sd.DINK),
                      sd.p('5 · Would <b>Ti</b> (15 µm) be as easy as Cu?', 27, sd.DINK), gap=22, w=1060),
               sd.col(sd.p('Interactive 3D, and every number:', 24, sd.DMUT),
                      sd.p(f'<a href="{PAGE}" style="color:{sd.DBLUE}">dylan-neff.web.cern.ch/facilities/lnl-target.html</a> (tab “Al ogive + Cu liner”)', 24, sd.DINK),
                      sd.p('The full study: notes/lnl-cu-liner', 24, sd.DMUT), gap=14, w=520), gap=80),
        dark=True, short='questions')

D.write(OUTF, note_meta=dict(title='LNL target: your ogive in Al, with Cu only where the beam stops (short, for Pierfrancesco)',
                             summary='Six slides: the Al ogive with a 12 µm Cu liner and a masked Li film, 3D views, how it is built '
                                     'from the beam axis, the Geant4 numbers against the Cu ogive, and the questions.',
                             tags='x17, lnl, target', date='2026-11-04'))
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
