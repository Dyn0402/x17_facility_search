"""Build the 'neutron route at Legnaro' X17 feasibility slide note (not published).

    ~/PycharmProjects/nTof_x17/.venv/bin/python lnl_neutrons/deck/build_deck.py   # -> lnl_neutrons/out/lnl-neutrons-x17-feasibility.html
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
d = C.load()
t = pd.read_csv(O / 'lnl_neutrons_reach.csv')
o = pd.read_csv(O / 'lnl_neutrons_other_reach.csv')
cp = pd.read_csv(O / 'lnl_neutrons_components.csv')
acc = pd.read_csv(O / 'lnl_neutrons_target_acceptance.csv')
bham = C.R(d, 'bham_28_2m_pb5')
BIG = 'big plastics'
SIG = 'E* ≤ 22 MeV'


def R(key='cn_3000_thin', scen='authorised', D=20, var='base', hw=BIG, col='rho3'):
    q = t[(t.key == key) & (t.scen == scen) & (t.D_cm == D) & (t.variant == var) & (t.hw == hw) & (t.days == 50) & (t.signal == SIG)]
    return float(q[col].iloc[0])


def Ot(key, hw=BIG, col='rho3'):
    q = o[(o.key == key) & (o.hw == hw) & (o.days == 50) & (o.signal == SIG)]
    return float(q[col].iloc[0])


days = C.days_to_atomki
best = R()
veto = R(var='veto90')
d5 = R(D=5)
d5t = R(D=5, var='tgt_pairs')
ath = Ot('anthem30_130_2m')
D = sd.Deck('Neutron route at Legnaro: X17 feasibility',
            'Could the MX17 apparatus, already at LNL for the ⁸Be run, also do ³He(n,e⁺e⁻)? The status of every LNL neutron source in 2026 and the reach with the shared Geant4 beam background.')

cover = (sd.kicker('MX17 · a neutron route at Legnaro · feasibility · 9 Nov 2026')
         + '<h1 style="font-size:58px;font-weight:600;line-height:1.08;letter-spacing:-1.5px">'
           f'The accelerators at Legnaro are ×{best / C.RHO:.0f} short of ATOMKI. The high-current RFQ is leaving for Caserta.</h1>'
         + sd.p('³He(n,e⁺e⁻)⁴He with the arms that will already be on site for the proton ⁸Be run; 30 bar × 40 cm cell behind a thin-stop Li target at the CN Van de Graaff.', 30, sd.DMUT)
         + sd.row(sd.bignum(sci(best, 1), 'CN at 3.3 µA, 50 days', sd.DRED, f'×{best / C.RHO:.0f} short of ATOMKI ⁴He; {days(best):,.0f} days to reach it', tip='cosmics-limited'),
                  sd.bignum(sci(veto, 1), 'with a 90 % cosmic veto', sd.ORANGE, f'×{veto / C.RHO:.1f} short; {days(veto):,.0f} days'),
                  sd.bignum('~1×10⁻³', 'ANTHEM, 1–3 mA + room factor', sd.ORANGE, 'estimate; not built, bare target view hypothetical'),
                  gap=56))
D.slide('cover', cover, dark=True, short='cover',
        notes="""Reach = X17/IPC at 3σ in 50 days (Asimov, shared Geant4 soft-beam engine, big plastics, E* ≤ 22 MeV). The engine reproduces soft_reach.csv's bham_28_2m_pb5 row to 0.01 %. Files: lnl_neutrons/FEASIBILITY.md, FACILITY.md, lnl_neutrons_beam.py.""")

D.slide('status', sd.title('Six neutron sources have the Legnaro name; only one is at Legnaro and running',
                           'status at 9 Nov 2026, from public documents')
        + sd.table(['source', 'beam', 'status', 'at LNL?'],
                   [['CN Van de Graaff', 'p ≤ 6 MV; ~4 µA authorised, ~0.5 µA on Li today', 'operating', 'yes'],
                    ['LENOS', 'keV Maxwellian; 7.3×10¹⁰ n/s design', 'exists only as a CN beam line', 'CN'],
                    ['MUNES / SPES-BNCT', 'RFQ + Be at LNL', 'not funded as a facility', 'no'],
                    ['ANTHEM BNCT', 'RFQ 5 MeV, 30 mA, Be, ~10¹⁴ n/s', 'RFQ being prepared at LNL, then shipped; building ~2027', 'no: Caserta'],
                    ['NEPIR-0', 'SPES p, ≤ 1 µA, 70 MeV, thick Be', 'in development (Aug 2025 thesis); no neutrons reported', 'planned'],
                    ['SPES cyclotron', '35–70 MeV, ≤ 750 µA', 'pit-floor crack, Feb 2026; "timeline cannot be better defined"', 'yes, no n port']],
                   size=24, widths=[300, 500, 620, 200], align=['left', 'left', 'left', 'left']),
        short='what exists',
        notes="""CN: arXiv:2605.12005 (2026), maintenance done 2026 (LNL users' minutes). ANTHEM: Grespan et al., HB2025 TUCDB01 ("the cavity will be shipped to Caserta"; "the RF conditioning of the full RFQ will take place in Caserta"). MUNES not funded: Pisent et al., LINAC 2024. SPES crack: LNL User Community Meeting minutes, 12–13 Feb 2026. NEPIR is the name in the literature; "NEPHIR" was a mis-spelling in the catalogue.""")

rows_i = [('today, ~0.5 µA (ESTIMATE)', R(scen='today'), sd.GREY), ('with shielding package, 2.5 µA', R(scen='shielded'), sd.ORANGE),
          ('authorised, 3.3 µA', best, sd.RED), ('technical, 6 µA', R(scen='technical'), sd.ORANGE), ('authorised + 90 % veto', veto, sd.GREEN)]
hb = sd.hbars([(n, v, c, f'{n}: {v:.2g}') for n, v, c in rows_i], 0.1, width=860, log=True, vmin=1e-3, label_w=340, fmt=lambda v: f'{v:.1e}')
ca = cp[(cp.key == 'cn_3000_thin') & (cp.hw == BIG) & (cp.scen == 'authorised') & (cp.D_cm == 20)].iloc[0]
D.slide('cn', sd.title('CN: cosmics set the floor, and the current cannot rise far enough',
                       '3.0 MeV thin-stop Li, cell 20 cm from the target, big plastics, 50 days, X17/IPC at 3σ (ATOMKI = 1.5×10⁻³)')
        + sd.row(hb, sd.col(sd.p(f'<b>{ca.n_win:.2g} n/s</b> through the cell window at 3.3 µA.', 28),
                            sd.p('The current is capped by radiation at the switching magnet, not the target (arXiv:2605.12005): 0.3 µA at 5.5 MeV today, 2–3 µA with shielding still under evaluation.', 24, sd.MUT),
                            sd.p(f'~430 days to ATOMKI with a veto; {days(best):,.0f} without.', 24), w=520, gap=20), gap=48),
        short='CN reach',
        notes="""Li model: franz_beam.mc rescaled to FRANZ (2.0 MeV) and Lee & Zhou (2.5 MeV), Birmingham's 1e9 n/s/µA at 2.6 MeV to 3 %. Every neutron < 1.3 MeV. Pulsed CN (700 nA, 3 MHz) gates cosmics but loses more current: ×2.4 worse (estimate). The technical 6 µA needs a licence change and a better target.""")

D.slide('target', sd.title('Moving closer does not help: the production target makes the same pairs next door',
                           '3.0 MeV, 3.3 µA, 30 bar cell, big plastics, 50 days')
        + sd.row(sd.table(['target to window', 'no target pairs', 'with target pairs (ESTIMATE)', 'target/IPC after geometry'],
                          [[f'{int(x)} cm', sci(R(D=int(x)), 1), sci(R(D=int(x), var='tgt_pairs'), 1),
                            f'×{float(t[(t.key == "cn_3000_thin") & (t.D_cm == x) & (t.scen == "authorised") & (t.variant == "base") & (t.hw == BIG) & (t.days == 50)].tgt_over_ipc.iloc[0]):.0f}'] for x in (5, 10, 20, 50)],
                          size=24, widths=[220, 240, 340, 320]),
                 sd.col(sd.callout('Thin-stop Li (protons stop at threshold) avoids the ⁸Be resonances, but direct capture still gives ~5×10⁻⁹ γ/p (σ ~ 10 µb, ESTIMATE).', sd.ORANGE, 24),
                        sd.p(f'Same verdict as Demokritos: at CN, the closer you get, the more the target\'s IPC pairs ({3e7:,.0f}/day) take over. At ≥ 20 cm they leave the acceptance, and cosmics remain.', 24, sd.MUT), w=600, gap=20), gap=48),
        short='target pairs',
        notes=f"""Toy acceptance relative to the cell (100–150°, two arms): {', '.join(f'{int(a.D_cm)} cm: {a.f:.3f}' for a in acc.itertuples())}. The thick-target case is ×26 larger at 5 cm. σ_DC needs measuring: the same set-up with the proton beam could do it. The n_TOF capsule at 1 cm (analytic, Demokritos' method): 17 d at 4 µA with every background off; the target's pairs are then 1 cm away, and it cannot be measured that way.""")

rows_a = [(f'30 mA, 130°, 2 m', Ot('anthem30_130_2m'), sd.GREEN), (f'30 mA, 0°, 2 m (DREAM-limited)', Ot('anthem30_0_2m'), sd.GREEN), ('3 mA, 0°, 2 m', Ot('anthem3_0_2m'), sd.GREEN), ('1 mA, 0°, 2 m', Ot('anthem1_0_2m'), sd.ORANGE),
          ('LENOS design (not built), 20 cm', Ot('lenos_20cm'), sd.GREY), ('SPES 35 MeV, 750 µA, 130° (hypothetical)', Ot('spes35_130_2m'), sd.ORANGE), ('CN 3.3 µA', best, sd.RED), ('Birmingham (engine)', bham, sd.BLUE), ('ATOMKI', C.RHO, sd.INK)]
rows_a.sort(key=lambda x: x[1])
hb2 = sd.hbars([(n, v, c, f'{n}: {v:.2g}') for n, v, c in rows_a], 0.02, width=860, log=True, vmin=5e-5, label_w=400, fmt=lambda v: f'{v:.1e}', size=22, h=28)
D.slide('others', sd.title('Only a ~mA machine helps, and the Caserta RFQ exists only on paper',
                           'X17/IPC at 3σ, 50 days, big plastics, engine (beam only; see the room caveat)')
        + sd.row(hb2, sd.col(sd.p('ANTHEM: 5 MeV on Be, 8.6×10¹³ n/s (model), mean 1.1–1.6 MeV.', 24),
                             sd.p('Clinical, building ~2027. A 36 m² research room is planned, but one target is described; clinical current may be 2–5× lower. 30 mA rows: hypothetical bare view.', 22, sd.MUT),
                             sd.callout('No room here: expect ~×1.7 worse, and ~1 m of shield (ESTIMATE).', sd.ORANGE, 22), w=560, gap=14), gap=36),
        short='other sources',
        notes="""bepn_beam ENDF/B-VIII.0 at 5 MeV reproduces the ~1e14 n/s design value (8.6e13). LENOS at its 7.3e10 n/s forward design: 5.0e-4 at 20 cm; not built. SPES 35 MeV is limited by correlated beam events, as for the 30 MeV cyclotrons.""")

D.slide('fit', sd.title('The ³He cell does fit where the proton target would go',
                        'the same arms, beam line and DAQ as the ⁸Be plan: only the central piece changes')
        + sd.row(sd.col(sd.card(sd.p('<b>Proton route</b>: Li target at the centre, CN or AN2000 0° line.', 26)),
                        sd.card(sd.p('<b>Neutron route</b>: a 40 cm × Ø8 cm ³He cell on the axis, Li + chamber 5–20 cm upstream of the window.', 26)),
                        sd.callout('~8 g ³He at 30 bar: the cell (he3_target/) is not built, and is the main new cost.', sd.ORANGE, 24), w=760, gap=20),
                 sd.table(['question', 'answer'],
                          [['arms moved?', 'no; faces at ±204 mm, active 36 cm along the beam'],
                           ['beam line', 'CN 0°, most-used line: contention'],
                           ['hall shield', 'CN programme tolerates 3 mSv/h at the target; local BPE needed (ask)'],
                           ['schedule', 'CN runs working days; 50 days of beam = a year or more (ask)']],
                          size=22, widths=[240, 560], align=['left', 'left']), gap=48),
        short='does it fit',
        notes="""See FACILITY.md §4 and lnl/FACILITY.md for the CN hall questions. The LNL director floated replacing AN2000 + CN with one machine (Feb 2026), a risk to a multi-year CN plan.""")

rows_c = [('Birmingham (full Geant4)', 5.5e-4, sd.BLUE), ('Birmingham (engine)', bham, sd.BLUE), ('FRANZ design', 3.3e-4, sd.BLUE), ('FRM II MEDAPP', 4.2e-4, sd.BLUE),
          ('ANTHEM 30 mA, bare view (hypothetical)', ath, sd.ORANGE), ('CN + veto', veto, sd.ORANGE), ('CN', best, sd.RED), ('ATOMKI', C.RHO, sd.INK)]
rows_c.sort(key=lambda x: x[1])
D.slide('call', sd.title('The call: WATCH. CN is not the route; ANTHEM is not an existing beam',
                         'X17/IPC at 3σ, 50 days, big plastics')
        + sd.row(sd.hbars([(n, v, c, f'{n}: {v:.2g}') for n, v, c in rows_c], 0.02, width=860, log=True, vmin=1e-4, label_w=330, fmt=lambda v: f'{v:.1e}', size=22, h=30),
                 sd.col(sd.p('<b>Ask Pierfrancesco:</b>', 28),
                        sd.p('1. What continuous current on Li is really allowed at 2.0–3.0 MeV, with the shielding package?', 24),
                        sd.p('2. Is the ANTHEM second room or experimental branch open to a non-clinical experiment?', 24),
                        sd.p('3. Can CN take a ~100 µm Li target, and is a short σ_DC measurement possible?', 24),
                        sd.p('A cell at LNL could also validate ³He handling and the target-pair number, if built anyway.', 22, sd.MUT), w=640, gap=18), gap=48),
        short='the call',
        notes="""Full list of questions: FACILITY.md §5. Nobody has been contacted. Not simulated: the room, target chamber, the n₁ branch, the diverging beam against the parallel Geant4 table. If ANTHEM opens, a dedicated Geant4 run (FEASIBILITY.md §8) replaces the engine number.""")

out = D.write(O / 'lnl-neutrons-x17-feasibility.html',
              note_meta=dict(title='Neutron route at Legnaro: X17 feasibility',
                             summary='Status of every LNL neutron source in 2026 and the X17 reach of a ³He(n,e⁺e⁻) run with the shared Geant4 engine.',
                             tags='x17, lnl, feasibility', date='2026-11-09'),
              footer='Built by x17_facility_search/lnl_neutrons/deck/build_deck.py.')
print(out)
