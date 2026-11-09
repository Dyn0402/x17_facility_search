"""Build the reactor fast/epithermal beam X17 slide note: reactor_fast/out/reactor-fast-x17-feasibility.html

    ~/PycharmProjects/nTof_x17/.venv/bin/python reactor_fast/deck/build_deck.py
"""
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'survey' / 'soft_sim'))
import deck_common as C  # noqa: E402
from deck_common import sd, sci  # noqa: E402

O = HERE.parent / 'out'
r = pd.read_csv(O / 'rf_reach.csv')
g = pd.read_csv(O / 'rf_flux_grid.csv')
s = pd.read_csv(O / 'rf_spectra.csv')
b = pd.read_csv(O / 'rf_beam.csv')
d = C.load()
C.SITES['TAPIRO Casaccia'] = (42.045, 12.302)
C.SITES['LVR-15 Řež'] = (50.180, 14.356)


def R(key, col='rho3', var='subkev', hw=C.HW, days=50, signal='E* ≤ 22 MeV'):
    q = r[(r.key == key) & (r.variant == var) & (r.hw == hw) & (r.days == days) & (r.signal == signal)]
    return float(q[col].iloc[0])


t_pb = R('tapiro_open_pb5')
t_ab = R('tapiro_open_pb5', hw='as built')
lv = R('lvr15')
D = sd.Deck('Operating reactor beams: X17 feasibility',
            'Can an operating reactor replace the FRM II MEDAPP fission beam for MX17? A survey of fast and epithermal reactor beams, their status in 2026, and the reach with the shared Geant4 background.')

# --------------------------------------------------------------------------- #
cover = (sd.kicker('MX17 at reactor fast and epithermal beams · feasibility · 9 Nov 2026')
         + '<h1 style="font-size:60px;font-weight:600;line-height:1.08;letter-spacing:-1.5px">'
           f'No operating reactor has a MEDAPP-class fast beam. BNCT beams reach ~1×10⁻³; ENEA’s TAPIRO could reach {sci(t_pb, 1)} if a channel is opened.</h1>'
         + sd.p('X17/IPC reached at 3σ in 50 days, big plastics, E* ≤ 22 MeV, shared Geant4 re-weighting. TAPIRO is a concept; LVR-15 is operating.', 30, sd.DMUT)
         + sd.row(sd.bignum(sci(t_pb, 1), 'TAPIRO open channel + 5 cm Pb', sd.DGREEN, f'{C.fmt_days(C.days_to_atomki(t_pb))} to ATOMKI; ESTIMATE; as built {sci(t_ab, 1)}'),
                  sd.bignum(sci(lv, 1), 'LVR-15 BNCT beam (measured)', sd.DGOLD if hasattr(sd, 'DGOLD') else sd.GOLD, f'{C.fmt_days(C.days_to_atomki(lv))} to ATOMKI; operating reactor'),
                  sd.bignum('4.2×10⁻⁴', 'FRM II MEDAPP', sd.DRED, 'off since March 2020, no restart date'), gap=56))
D.slide('cover', cover, dark=True, short='cover',
        notes=f"""Reach: the shared engine (survey/soft_sim/soft_reach.py) reproduces medapp_std and bham_28_2m_pb5 exactly (out/rf_engine_check.csv). The BNCT reach depends on treating the neutrons below the N5 lower edge (1 keV): see the sub-keV slide. Engine numbers have no room: Birmingham moved ×1.7 worse in its full Geant4.

Files: <code>reactor_fast/FEASIBILITY.md</code>, <code>FACILITY.md</code>, <code>reactor_fast_beam.py</code>.""")

# --------------------------------------------------------------------------- #
tab = sd.table(['reactor', 'beam', 'flux at a port', 'status 2026', 'engine'],
               [['TAPIRO, ENEA Rome (5 kW)', 'fast source; no beam', 'S = 3×10¹⁴ n/s; open channel ~1.6×10⁸ ESTIMATE', 'runs (06/2026 brochure); no 2026 log (ask)', 'modelled'],
                ['LVR-15, Řež (10 MW)', 'BNCT epithermal', '7.1×10⁸ epi, 6×10⁷ fast, 2 Gy/h γ', 'operating; BNCT line (ask)', 'modelled'],
                ['MITR FCB (6 MW)', 'BNCT epithermal', '8.4×10⁹ epi', 'filter being removed (2025)', 'historical'],
                ['THOR (2 MW)', 'BNCT', '1.7×10⁹ epi / MW', 'clinical', 'modelled'],
                ['RA-6 (0.5 MW)', 'BNCT mixed', '1.1×10⁹ design', 'licence to 07/2026 (ask)', 'modelled'],
                ['OSU, UT TRIGA fast ports', 'fission-like', '2×10⁷, 4×10⁶', 'small ports', 'flux grid'],
                ['KUR (5 MW)', 'BNCT', '—', 'ended 23 Apr 2026', 'closed']],
               size=22, widths=[300, 200, 480, 400, 150], align=['left'] * 5)
D.slide('survey', sd.title('The survey: reactors have flux inside the core, not in beams', 'operating reactors that could stand in for a fission beam')
        + tab, short='survey',
        notes="""FACILITY.md §1 has the full list with sources: BR1, BR2, JSI, Pavia, MARIA, Penn State, UMass, IBR-2 etc. Most lack a beam that can reach a Ø8 cm cell with arms around it, or are not accessible.""")

# --------------------------------------------------------------------------- #
gg = g[(g.hw == C.HW) & (g.signal == 'E* ≤ 22 MeV')].copy()
gg['flux'] = gg.key.str.extract(r'watt_(.*)_g')[0].astype(float)
gg['gk'] = gg.key.str.extract(r'_g([\d.]+)$')[0].astype(float)
P = sd.Plot(1100, 600, x=(1e6, 3e9, 'log'), y=(2e-4, 1e-2, 'log'), xlabel='flux at the cell [n/cm²/s], Watt spectrum', ylabel='X17/IPC at 3σ in 50 d')
P.xticks([(v, f'{v:.0e}') for v in (1e6, 1e7, 1e8, 1e9)]).yticks(sd.log_ticks(-4, -2))
P.hline(1.5e-3, sd.GREEN, label='ATOMKI 1.5×10⁻³')
leg = []
for gk, col in ((0.3, sd.BLUE), (1.0, sd.ORANGE), (3.0, sd.RED), (10.0, sd.GREY)):
    z = gg[gg.gk == gk].sort_values('flux')
    P.line(list(z.flux), list(z.rho3), col, r=8, tips=[f'{f:.0e}, γ/n {gk:g}: {v:.2g}' for f, v in zip(z.flux, z.rho3)])
    leg.append((f'γ/n = {gk:g}', col))
D.slide('map', sd.title('What a reactor fast beam must deliver: 3×10⁷ n/cm²/s, γ/n ≤ 3',
                        'engine map for a Watt spectrum; above ~10⁸ the beam is throttled and γ/n sets the plateau')
        + sd.row(sd.col(P.svg('reach vs flux'), sd.legend(leg, size=22), w=1100, gap=8),
                 sd.col(sd.p('Below 10⁷ a port is statistics-starved: OSU, UT Austin.', 26),
                        sd.p('Above 10⁸ the DAQ is the limit: more flux does not help (MEDAPP’s situation).', 26),
                        sd.p('Plateau: 3.5×10⁻⁴ (γ/n 0.3) to 6.5×10⁻⁴ (γ/n 3).', 26, sd.MUT), w=520, gap=24), gap=48),
        short='flux map', notes="out/rf_flux_grid.csv; Ø8 cm beam on the 30 bar × 40 cm cell.")

# --------------------------------------------------------------------------- #
P = sd.Plot(1100, 600, x=(1e-8, 20, 'log'), y=(1e4, 3e9, 'log'), xlabel='E_n [MeV]', ylabel='E dΦ/dE [n/cm²/s]')
P.xticks([(10.0**x, f'1e{x}') for x in (-8, -6, -4, -2, 0)]).yticks(sd.log_ticks(4, 9))
P.band([0.2, 2.75], [1e4, 1e4], [3e9, 3e9], sd.GREEN, 0.08)
P.text(1.2e-3, 2.0e9, 'N5 starts at 1 keV', 20, sd.GREY)
curves = [('tapiro_open_pb5', 'TAPIRO open + 5 cm Pb (ESTIMATE)', sd.RED), ('lvr15_at_exit', 'LVR-15 BNCT beam (exit)', sd.BLUE),
          ('mitr', 'MITR FCB (historical)', sd.ORANGE), ('thor_1mw', 'THOR 1 MW', sd.GREY)]
for k, n, col in curves:
    m = s.E > 1e-8
    x, y = s.E[m].values[::15], (s.E * s[k])[m].values[::15]
    good = y > 1e4
    P.line(list(x[good]), list(y[good]), col, markers=False, w=4, tip=n)
D.slide('spectrum', sd.title('Epithermal beams carry most neutrons below the Geant4 edge; TAPIRO is all above it',
                             'beam spectra at the cell, MCNP/measured normalisation; shaded: E_n 0.2–2.75 MeV')
        + sd.row(sd.col(P.svg('spectra'), sd.legend([(n, c) for _, n, c in curves], size=22), w=1100, gap=8),
                 sd.col(sd.p('LVR-15’s fast group is still most of its pairs: 1 keV–2.75 MeV gives 75–85 %.', 26),
                        sd.p('Sub-keV neutrons give pairs at 4.8×10⁻¹¹; they count as 1–3 keV neutrons in the background: an ESTIMATE, ×10 → 3×10⁻³.', 24, sd.MUT),
                        w=520, gap=24), gap=48), short='spectra',
        notes="BNCT spectra: 1/E epithermal, fast group 1/E·exp(-E/E_c) with E_c fitted to the published dose per fast neutron. TAPIRO: Watt mixed with a 1/E softened part, fixed by 20 % > 1.35 MeV at core centre (Rosa 2009).")

# --------------------------------------------------------------------------- #
rows = [('TAPIRO open + 5 cm Pb', t_pb, sd.RED, 'concept'), ('TAPIRO open, no filter', R('tapiro_open'), sd.ORANGE, 'γ/n = 1'),
        ('LVR-15, 35 cm from exit', lv, sd.BLUE, 'measured free beam'), ('THOR 1 MW', R('thor_1mw'), sd.BLUE, 'design'),
        ('RA-6', R('ra6'), sd.BLUE, 'design'), ('MITR FCB', R('mitr'), sd.GREY, 'historical'), ('TAPIRO epithermal column', R('tapiro_epi'), sd.GREY, 'calculated')]
rows.sort(key=lambda x: x[1])
ref = [('FRM II MEDAPP', 4.18e-4, sd.GREEN, 'off'), ('Birmingham (Geant4 engine)', 3.32e-4, sd.GREEN, 'full Geant4 5.5e-4'), ('FRANZ design', 3.3e-4, sd.GREEN, 'not at 2 MeV yet')]
all_ = sorted(rows + ref, key=lambda x: -x[1])
hb = sd.hbars([(n, v, c, f'{n}: {v:.2g}. {t}') for n, v, c, t in all_], 2.2e-3, width=860, log=True, vmin=2e-4, label_w=320, fmt=lambda v: f'{v:.1e}')
D.slide('reach', sd.title('The BNCT beams cluster near 1×10⁻³; TAPIRO + Pb is the only one in MEDAPP’s class',
                          'X17/IPC at 3σ in 50 days, E* ≤ 22 MeV, big plastics; shorter is better')
        + sd.row(hb, sd.col(sd.p(f'TAPIRO: {sci(t_pb, 1)}; flux ×0.3 lower gives {sci(R("tapiro_open_f015_pb5"), 1)}. Pb makes it robust to the unknown γ field.', 26),
                            sd.p('A 5.6 cm Pb window already appears in the published TAPIRO column design: ENEA to confirm.', 24, sd.MUT),
                            sd.p('Engine only: expect ×1.5 worse with room and shield leakage.', 24, sd.ORANGE), w=560, gap=18), gap=40),
        short='reach')

# --------------------------------------------------------------------------- #
D.slide('scorecard', sd.title('Scorecard', 'what stands between each option and beam')
        + sd.table(['', 'TAPIRO', 'LVR-15', 'THOR', 'MITR'],
                   [['beam today?', 'no: channel to build', 'BNCT line exists (ask)', 'clinical', 'being removed'],
                    ['access', 'ENEA bilateral', 'commercial operator', 'patients first', 'no'],
                    ['biggest risk', 'reactor modification, sustained 5 kW', 'sub-keV background (×3)', 'schedule', '—'],
                    ['call', 'WATCH (enquiry on hold)', 'KEEP AS BACKUP', 'CLOSED', 'CLOSED']], size=26, widths=[280, 420, 420, 300, 280], align=['left'] * 5),
        short='scorecard')

end = (sd.title('Open questions', None)
       + sd.row(sd.col(sd.p('<b>If revisited, ask ENEA</b>', 30, sd.DINK),
                       sd.p('• is the BNCT column installed? window and channel sizes', 26, sd.DINK),
                       sd.p('• sustained running at 5 kW; measured γ field; openness to a modification', 26, sd.DINK), gap=18),
                sd.col(sd.p('<b>Ask CVŘ</b>', 30, sd.DINK),
                       sd.p('• BNCT line and room availability; flux with the filter blocks out', 26, sd.DINK),
                       sd.p('<b>Simulate</b>: a sub-keV extension of N5 (1 meV–1 keV)', 26, sd.DINK), gap=18), gap=80))
D.slide('end', end, dark=True, short='open questions')

print(D.write(O / 'reactor-fast-x17-feasibility.html',
              note_meta=dict(title='Reactor fast beams X17 feasibility', summary='Operating reactor fast and epithermal beams as alternatives to FRM II MEDAPP.',
                             tags='x17, reactor, feasibility', date='2026-11-09'),
              footer='Built by x17_facility_search/reactor_fast/deck/build_deck.py.'))
