"""Build the accelerator-BNCT X17 feasibility slide note (not published).

    ~/PycharmProjects/nTof_x17/.venv/bin/python bnct_accel/deck/build_deck.py   # -> bnct_accel/out/bnct-accel-x17-feasibility.html
"""
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'survey' / 'soft_sim'))
sys.path.insert(0, str(ROOT / 'survey'))
import deck_common as C  # noqa: E402
from deck_common import sd, sci  # noqa: E402

O = HERE.parent / 'out'
t = pd.read_csv(O / 'bnct_reach.csv')
comp = pd.read_csv(O / 'bnct_components.csv')


def R(key, hw=C.HW, days=50, col='rho3', sig='E* ≤ 22 MeV'):
    q = t[(t.key == key) & (t.hw == hw) & (t.days == days) & (t.signal == sig)]
    return float(q[col].iloc[0])


NAG, MODC, MOD7, MODN, MODSUB, BEM = ('nagoya_28_15_2m_pb5', 'mod_li_iaea_iaea1e9_40cm_cell', 'mod_li_7_iaea1e9_40cm_cell',
                                      'mod_li_nofast_iaea1e9_40cm_cell', 'mod_li_7_sub10_iaea1e9_40cm_cell', 'mod_be_7_kansai14e8_40cm_cell')
BHAM = 'bham_28_30_2m_pb5'
D = sd.Deck('Accelerator BNCT as an X17 source',
            'Could an accelerator BNCT machine serve as a source for MX17? Bare ⁷Li and moderated port, status in 2026, and the reach with the shared Geant4 engine.')

cover = (sd.kicker('MX17 at accelerator BNCT machines · feasibility · 9 Nov 2026')
         + '<h1 style="font-size:58px;font-weight:600;line-height:1.08;letter-spacing:-1.5px">'
           'The bare ⁷Li target is the better source, but no hospital machine offers one.</h1>'
         + sd.p('³He(n,e⁺e⁻)⁴He on the 30 bar × 40 cm cell, shared Geant4 soft-beam engine; X17/IPC at 3σ in 50 days, big plastics.', 30, sd.DMUT)
         + sd.row(sd.bignum(sci(R(NAG), 1), 'bare Li, Nagoya class, 2 m, 5 cm Pb', sd.DGREEN, f'BSA would have to come off. {C.fmt_days(C.days_to_atomki(R(NAG)))} to ATOMKI (engine)'),
                  sd.bignum(sci(R(MODC), 1), 'moderated Li port, IAEA contamination', sd.ORANGE, f'{C.fmt_days(C.days_to_atomki(R(MODC)))} to ATOMKI; DREAM live 0.5; ESTIMATE spectrum'),
                  sd.bignum('WATCH', 'not top-3', sd.DRED, 'ask Nagoya NUANS; Birmingham stays the reference'), gap=56))
D.slide('cover', cover, dark=True, short='cover',
        notes=f"""The survey said the unmoderated source behind the moderator is the real prize. The physics agrees: a bare Li target is ×2–4 better in reach. The opportunity does not: in a treatment machine the target sits in the beam-shaping assembly.

The bare numbers come from the Birmingham thick-Li model (and FRANZ's for thin Li); engine reproduced to 4 figures on the published Birmingham rows (<code>out/bnct_repro_check.csv</code>). The moderated port replaces the catalogue's ILL-scaled 2.5e-3. Everything in <code>bnct_accel/FEASIBILITY.md</code>.""")

status = sd.table(['machine', 'status 2026', 'bare target?'],
                  [['Birmingham HF-ADNeF', 'operating, research', '<b>yes</b> (the reference study)'],
                   ['BINP VITA, Novosibirsk', 'operating; external users until the war', 'yes, position B; CERN–Russia relations ended 30 Nov 2024'],
                   ['Nagoya NUANS (Dynamitron)', 'research; 11 mA reached in 2016; 2026 status (ask)', 'BSA fitted (ask)'],
                   ['nuBeam, Helsinki', 'first patients May 2025; 10-patient trial', 'no, Li in the BSA'],
                   ['NeuCure, Southern Tohoku / Kansai', 'insured clinical service since 2020', 'no'],
                   ['CICS, NCC Tokyo / Edogawa', 'clinical trials', 'no'],
                   ['Alphabeam, CNAO Pavia', 'agreement Dec 2024; installation not confirmed', 'no'],
                   ['Xiamen NeuPEX, Tsukuba, Gachon', 'clinical trials', 'no']], size=23, widths=[500, 620, 560], align=['left', 'left', 'left'])
D.slide('status', sd.title('Which machines run, and which let us at the target', 'checked by web search on 9 Nov 2026; (ask) = not public') + status, short='machines',
        notes='Project list: ISNCT 2021, reproduced in Tanaka BIPM webinar, Jan 2025; status lines updated from company and journal sources. Full table and URLs: <code>bnct_accel/FACILITY.md</code>.')

D.slide('value', sd.title('A moderated neutron is worth ~150× less', 'captures per neutron in the 30 bar cell: 10⁻⁸ below 1 keV, 1.5×10⁻⁶ at 0.5 MeV')
        + sd.row(sd.img(O / 'bnct_capture_value.png', w=900), sd.col(
            sd.p('Moderation gives ×6 more neutrons through the spot, not ×150.', 26),
            sd.p('Sub-keV handling: analytic captures from 0.5 eV (22 % of the epithermal captures at acceptance 0.5); background from N5\'s 1–3 keV bins as a proxy, ×1 and ×10.', 22, sd.MUT), w=620), gap=40),
        short='why bare wins')

fig = sd.img(O / 'bnct_reach_fig.png', w=1100)
D.slide('reach', sd.title('Reach: bare ⁷Li 2–6×10⁻⁴; moderated 0.8–1.8×10⁻³', 'X17/IPC at 3σ in 50 days, big plastics; beam-only engine (room factor ×1.7 not applied here)')
        + sd.row(fig, sd.col(sd.p(f'Bare: Nagoya 15 mA {sci(R(NAG), 1)}; Birmingham in the same engine {sci(R(BHAM), 1)}.', 26),
                             sd.p(f'Moderated: {sci(R(MOD7), 1)} (D_f 7×10⁻¹³) · {sci(R(MODC), 1)} (IAEA) · {sci(R(MODN), 1)} (no fast tail).', 24, sd.MUT),
                             sd.p('The moderated signal is largely the fast contamination: up to 64 % of captures.', 24, sd.MUT), w=560), gap=30),
        short='reach',
        notes=f'Reach rows: <code>out/bnct_reach.csv</code>. As built: bare {sci(R(NAG, "as built"), 1)}; moderated {sci(R(MODC, "as built"), 1)}. 14 d: {sci(R(NAG, days=14), 1)} / {sci(R(MODC, days=14), 1)}. Be port (NeuCure Kansai): {sci(R(BEM), 1)}. Pessimistic sub-keV ×10: {sci(R(MODSUB), 1)}.')

D.slide('walls', sd.title('The wall on the moderated port is DREAM, not the neutrons', 'at 10⁹ n/cm²/s, 40 cm from the port, big plastics')
        + sd.row(sd.card(sd.p('<b>Live 0.5</b>', 40, sd.ORANGE) + sd.p('legs from 2×10¹⁰ n/s through the spot; more flux gains 7–9 %.', 24, sd.MUT)),
                 sd.card(sd.p('<b>Sub-keV background</b>', 40, sd.RED) + sd.p(f'×10 proxy → {sci(R(MODSUB), 1)}; needs one Geant4 run below 1 keV.', 24, sd.MUT)),
                 sd.card(sd.p('<b>Room</b>', 40, sd.BLUE) + sd.p('Birmingham\'s room factor ×1.7 as an estimate; a treatment room has no dump.', 24, sd.MUT)), gap=28)
        + sd.p('Bare at 2 m + 5 cm Pb: statistics-limited, cosmics = IPC. A cosmic veto is the lever.', 26), short='walls')

D.slide('score', sd.title('Scorecard', 'bare at a research machine vs moderated port at a hospital')
        + sd.table(['', 'bare target', 'moderated port'],
                   [['beam exists today', 'Birmingham, VITA; Li in BSAs elsewhere', 'yes, clinical'],
                    ['access', 'university only (ask); VITA blocked', 'no user programme'],
                    ['space', 'BSA off + Birmingham-style shield wall', 'arms in the treatment room, no dump'],
                    ['³He cell', 'as at Birmingham', 'not in a patient room licence (ask)'],
                    ['reach', f'{sci(R(NAG), 1)} engine', f'{sci(R(MODC), 1)} (0.8–1.8×10⁻³)'],
                    ['vs Birmingham', '×1.5 weaker', '×4 weaker'],
                    ['call', 'WATCH: ask Nagoya', 'WATCH: not actionable']], size=24, widths=[280, 740, 660], align=['left', 'left', 'left']), short='scorecard',
        notes='Full scorecard with evidence: <code>bnct_accel/FEASIBILITY.md</code> §5.')

end = (sd.title('What this does not settle', None)
       + sd.row(sd.col(sd.p('<b>Not measured</b>', 30, sd.DINK),
                       sd.p('• No broad-band port spectrum is public; the fast tail is an ESTIMATE from dose limits.', 26, sd.DINK),
                       sd.p('• Sub-keV background is a proxy (N5 starts at 1 keV).', 26, sd.DINK), gap=18),
                sd.col(sd.p('<b>To ask</b>', 30, sd.DINK),
                       sd.p('• Nagoya: operating? BSA removable?', 26, sd.DINK),
                       sd.p('• INFN: CNAO Alphabeam, once installed.', 26, sd.DINK), gap=18), gap=80))
D.slide('end', end, dark=True, short='open questions')

print(D.write(O / 'bnct-accel-x17-feasibility.html',
              note_meta=dict(title='Accelerator BNCT X17 feasibility', summary='Accelerator BNCT machines as X17 sources: bare ⁷Li and moderated port, status in 2026, reach with the shared Geant4 engine.',
                             tags='x17, bnct, feasibility', date='2026-11-09'),
              footer='Built by x17_facility_search/bnct_accel/deck/build_deck.py from bnct_accel_beam.py outputs.'))
