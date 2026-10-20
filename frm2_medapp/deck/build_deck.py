"""Build the FRM II MEDAPP X17 feasibility slide note.

Reads survey/soft_sim/out/ (soft_reach.py) and frm2_medapp/out/ (medapp_beam.py), writes
frm2_medapp/out/frm2-medapp-x17-feasibility.html:

    ~/PycharmProjects/nTof_x17/.venv/bin/python frm2_medapp/deck/build_deck.py
    python3 ~/PycharmProjects/dylan-cern-site/scripts/add-note.py \\
        frm2_medapp/out/frm2-medapp-x17-feasibility.html --slug frm2-medapp-x17-feasibility --force --deploy
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / 'survey' / 'soft_sim'))
import deck_common as C  # noqa: E402
from deck_common import sd, term, sci  # noqa: E402,F401
import cartoon  # noqa: E402
import medapp_beam as MB  # noqa: E402

O = HERE.parent / 'out'
d = C.load()
K = 'medapp_std'
rho = C.R(d, K)
rho_ab = C.R(d, K, hw='as built')
rho_g3 = C.R(d, 'medapp_g3')
floor = C.R(d, K, col='rho3_floor')
thr = C.R(d, K, col='throttle')
live = C.R(d, K, col='live')
days = C.days_to_atomki(rho)
ok_arm = C.Cp(d, K, 'ok_singles_per_arm')
gfrac = C.Cp(d, K, 'ok_singles_gamma_frac')
legs = C.Cp(d, K, 'legs_per_arm')
ipc_soft = C.Cp(d, K, 'ipc_soft_per_day')
sv = d['survey']
old_lo = float(sv[(sv.key == 'medapp') & (sv.singles_model == 'geant')].rho3.iloc[0])
old_hi = float(sv[(sv.key == 'medapp') & (sv.singles_model == 'flat')].rho3.iloc[0])

D = sd.Deck('FRM II MEDAPP: X17 feasibility',
            'Could the MX17 apparatus test the ATOMKI ⁴He anomaly in the FRM II fission-neutron beam (MEDAPP, '
            'Garching)? The facility, its beamline, and the reach with its own Geant4 beam background.')

# --------------------------------------------------------------------------- #
cover = (sd.kicker('MX17 at FRM II · MEDAPP fission beam · feasibility · 20 Oct 2026')
         + '<h1 style="font-size:62px;font-weight:600;line-height:1.08;letter-spacing:-1.5px">'
           f'FRM II’s fission beam would pass the ATOMKI ⁴He strength ×{C.RHO / rho:.1f} in 50 days, '
           f'once the reactor runs again</h1>'
         + sd.p('³He(n,e⁺e⁻)⁴He on the 30 bar × 40 cm cell in the SR10 fission beam (3.2×10⁸ n/cm²/s, collimated '
                'to Ø8 cm), big plastics. X17/IPC reached at 3σ, E* ≤ 22 MeV, with IPC, cosmics and the beam’s own '
                'Geant4 background (neutrons and γ).', 30, sd.DMUT)
         + sd.row(
             sd.bignum(sci(rho, 1), 'X17/IPC at 3σ in 50 days', sd.DGREEN,
                       f'ATOMKI ⁴He: 1.5×10⁻³. As built: {sci(rho_ab, 1)}.',
                       tip=f'survey bracket before this run: {sci(old_lo, 1)} – {sci(old_hi, 1)}'),
             sd.bignum(C.fmt_days(days), 'of beam to reach the ATOMKI strength', sd.DGREEN,
                       'statistics only, at the best beam rate', tip='50 d × (ρ/1.5×10⁻³)²: the reach falls as 1/√T'),
             sd.bignum('2020', 'last reactor cycle', sd.DRED,
                       'the new central channel is not installed; no restart date (Mar 2026)'),
             gap=56))
D.slide('cover', cover, dark=True, short='cover',
        notes=f"""Reach = the X17/IPC(E1) ratio that a 50-day run detects at 3σ (Asimov over the θ histogram summed over E_n: a DC beam has no TOF tag). The E* ≤ 22 MeV convention counts X17 only from E_n ≤ 2.75 MeV (ATOMKI measured ⁴He at E* ≈ 20.5–21 MeV); IPC from every energy is background.

The beam is throttled to its best rate: here ×{thr:.2g} of the full 1.6×10¹⁰ n/s through the cell spot (DREAM live time {live:.2f} there). The statistics floor (IPC + cosmics only, full beam) is {sci(floor, 1)}.

Pessimistic γ field (3 photons per neutron instead of 1): {sci(rho_g3, 1)}.

Files: <code>frm2_medapp/FEASIBILITY.md</code>, <code>frm2_medapp/FACILITY.md</code>, <code>survey/soft_sim/</code>.""")

# --------------------------------------------------------------------------- #
facts = sd.col(
    sd.card(sd.p('<b>FRM II, Garching</b> (TU München), 15 km north of Munich', 28)
            + sd.p('20 MW research reactor, D₂O moderator; 4 cycles × 60 d a year when running.', 24, sd.MUT)),
    sd.card(sd.p('<b>SR10: the only beamline fission converter in the world</b>', 28)
            + sd.p('Two ²³⁵U plates beside the core make fission neutrons that look straight down the tube. '
                   'Rooms in line: MEDAPP, then NECTAR.', 24, sd.MUT)),
    sd.card(sd.p('<b>Status: off since 16 March 2020</b>', 28, sd.RED)
            + sd.p('New central channel not delivered (Mar 2026); restart ~6 months after it is.', 24, sd.MUT)),
    w=700, gap=24)
D.slide('where', sd.title('Garching: a 20 MW reactor with a beam of fission neutrons',
                          'the facilities this study compares; hover the dots and dotted terms for details')
        + sd.row(C.europe_map(880, 660, 'FRM II Garching'), facts, gap=56),
        short='where',
        notes="""Site 48.27 N, 11.67 E. Operator: TU München (Forschungs-Neutronenquelle Heinz Maier-Leibnitz), within the Heinz Maier-Leibnitz Zentrum (MLZ).

Restart: Bavarian parliament Drucksache 19/11406 (23 Mar 2026), question 29; late-2025 press quotes ~6 months from delivery of the channel to start-up. Earliest plausible beam is 2027 (ask).

Sources: <code>frm2_medapp/FACILITY.md</code> §1, §3.""")

# --------------------------------------------------------------------------- #
cards = sd.row(
    sd.card(sd.p('<b>3.2×10⁸ n/cm²/s</b>', 34, sd.BLUE) + sd.p('free in air at MEDAPP with the standard filters '
            '; up to 7×10⁸ with other filters', 22, sd.MUT)),
    sd.card(sd.p('<b>mean 1.9 MeV</b>', 34, sd.BLUE) + sd.p('fission spectrum, maximum ~10 MeV', 22, sd.MUT)),
    sd.card(sd.p('<b>γ ≈ 1 per neutron</b>', 34, sd.ORANGE) + sd.p('mean 2.4 MeV behind the Pb', 22, sd.MUT)),
    sd.card(sd.p('<b>field ≤ 27 × 19 cm</b>', 34, sd.INK) + sd.p('MLC 5.9 m from the source: Ø8 cm for the cell', 22, sd.MUT)),
    gap=24)
D.slide('beamline', sd.title('SR10: a uranium converter, a 6 m beam tube, two rooms',
                             'side view, not to scale; dashed green = what the X17 set-up adds (flight tubes)')
        + cartoon.beamline(1664, 500) + cards,
        short='beamline',
        notes="""Converter: 2 U₃Si₂-Al plates, 540 g of 93 % ²³⁵U, 80 kW of fission power, driven down a chute into the D₂O tank next to the nose of SR10, ~1 m from the core. Beam tube with 4 shutter drums (a therapy requirement), pneumatic filters, a multi-leaf collimator (Fe/PE/Pb leaves 60 cm deep). Source-to-surface distance at MEDAPP 592 cm, effective source 15 × 15 cm².

The arms need an evacuated tube from the collimator to the cell window and an exit tube to a dump: in air ~1 % of the beam scatters per metre next to the arms. MEDAPP's room is a treatment room; NECTAR, behind it, takes permanent set-ups up to 80 × 80 × 80 cm and 500 kg but sees a lower flux (0.9–47 ×10⁶ n/cm²/s through its imaging collimator). Whether the 1.6–2 m arms fit in either room is the first question for FRM II.

Sources: Wagner et al. 2007; Wagner 2011 (ÖMPG); MLZ JLSRF A18/A19 (2015); MLZ 2025 poster. <code>frm2_medapp/FACILITY.md</code> §2, §4.""")

# --------------------------------------------------------------------------- #
sp, leg, fr = C.spectrum_plot(1100, 600, 'medapp')
f_med = fr['FRM II MEDAPP (fission)']
f_nfs = fr['GANIL NFS d(40)+Be']
P_txt = sd.col(leg, sd.p(f'{100 * f_med:.0f} % of the fission neutrons fall in the window, against {100 * f_nfs:.0f} % at NFS.', 26),
               sd.p('Per neutron in the window the cell gives ~200× the pairs of a thermal neutron.', 24, sd.MUT), w=480, gap=24)
D.slide('spectrum', sd.title(f'A fission spectrum puts {100 * f_med:.0f} % of the neutrons where ATOMKI measured, NFS {100 * f_nfs:.0f} %',
                             'normalised E dN/dE; shaded: E_n 0.2–2.75 MeV (E* ≤ 22.1 MeV, X17 opening-angle edge ≥ 99°)')
        + sd.row(sp, P_txt, gap=40),
        short='spectrum',
        notes=f"""MEDAPP: ²³⁵U Watt spectrum (a = 0.988 MeV, b = 2.249 /MeV) plus 5 % of a 1/E part between 1 keV and 0.5 MeV (a stand-in for the measured "intermediate" component behind the B4C filter: ask FRM II). 24 % of the neutrons are above 2.75 MeV: they make IPC at E* > 22 MeV (background in this convention) and most of the trigger legs (next slides).

Through the Ø8 cm spot: 1.6×10¹⁰ n/s, {ipc_soft:,.0f} IPC pairs per day in the window before acceptance.

<code>frm2_medapp/medapp_beam.py</code> → <code>out/medapp_spectra.csv</code>; <code>survey/survey_yield.py</code> for P(E).""")

# --------------------------------------------------------------------------- #
sp, leg = C.singles_plot(d, 1120, 600)
D.slide('singles', sd.title('Geant4: a soft neutron makes ~3×10⁻⁷ singles per arm, ×30 below the survey’s pessimistic bound',
                            'MX17_Full_Geant branch soft, NFS cell and arms, big plastics: forced-collision neutrons (N5) and photons (G5/G6)')
        + sd.row(sp, sd.col(leg, sd.p('A single = a trigger leg (SiPM + back plastic) with a Micromegas segment in the active area.', 24),
                            sd.p(f'At MEDAPP {100 * gfrac:.0f} % of the singles come from the γ, not the neutrons.', 26, sd.ORANGE),
                            w=460, gap=24), gap=40),
        short='Geant4 singles',
        notes=f"""The survey (SURVEY.md §4.1) had to bracket the singles of < 3 MeV neutrons between the NFS forced run's sparse per-energy table and a flat bound (every neutron as bad as NFS's average, which is set by its > 10 MeV neutrons). These two runs measure it.

N5: 9×10⁷ neutrons per hardware set, dN/dE ∝ 1/E from 1 keV to 20 MeV, forced first collision on the beam line + roulette (0.2 / 0.05). G5: 2×10⁸ photons, ∝ 1/E on 0.1–20 MeV. G6: 2×10⁸ photons flat on 14–19 MeV. Same Ø8 cm disc 1 m upstream of the cell window, vacuum flight tube, Be window, Al end cap.

Photons below ~2.7 MeV make no trigger leg at all: the leg needs half a MIP in the back plastic. So only the hard tail of the reactor γ field counts. MEDAPP at full beam: {ok_arm:,.0f} singles and {legs:,.0f} legs per arm per second.

Each source is the same rows re-weighted by f(E)/g(E): <code>survey/soft_sim/soft_reach.py</code> → <code>out/singles_vs_E.csv</code>.""")

# --------------------------------------------------------------------------- #
hb, q = C.budget_bars(d, K, 700)
D.slide('budget', sd.title('At the best rate the background is IPC itself; cosmics and accidentals come next',
                           f'events per day in θ = 100–150° after the vertex and E_sum > W/2 cuts, beam throttled to ×{thr:.2g}, big plastics')
        + sd.row(sd.col(hb, C.rate_table(d, K), w=1000, gap=36), sd.col(sd.p(f'X17 at the ATOMKI ratio is {100 * q.X17_win_per_day / q.IPC_win_per_day:.1f} % of the IPC in the window: a '
                                 'shape measurement on a large, known background.', 26),
                            sd.p('A cosmic veto (arm-to-arm TOF, as at LNL) would remove most of the cosmics.', 24, sd.MUT),
                            w=560, gap=24), gap=48),
        short='background budget',
        notes=f"""Window counts are for orientation; the reach uses the whole θ histogram (0–180°).

Accidentals: two singles from different particles within ±5 ns (assumed scintillator coincidence), built from the source's own Geant4 singles and passed through the full reconstruction (vertex: both Micromegas segments within 60 mm of the beam axis; E_sum > W/2 with the LNL-calibrated response). Correlated: same-event two-arm beam events, factorised (all two-arm events × pooled vertex and E_sum pass fractions), because ~1 MC event passes every cut.

Why throttle: at full beam the trigger legs from fission neutrons above ~2 MeV and the γ tail make {legs:,.0f} legs per arm per second, so random two-arm triggers keep DREAM (298 µs per event) mostly dead. At ×{thr:.2g} the live time is {live:.2f}.""")

# --------------------------------------------------------------------------- #
tp, leg = C.throttle_plot(d, 1000, 600, [('medapp_std', sd.RED, 'standard filters, γ/n = 1', None),
                                          ('medapp_g3', sd.ORANGE, 'standard filters, γ/n = 3', '10 7'),
                                          ('medapp_nopb', sd.PURPLE, 'no Pb (7×10⁸), γ/n = 3', '4 6')])
D.slide('reach', sd.title(f'Every γ assumption passes ATOMKI at its best rate: {sci(rho, 1)}–{sci(rho_g3, 1)}',
                          'X17/IPC at 3σ in 50 days vs the neutron rate through the cell; dots: best rate; big plastics, E* ≤ 22 MeV')
        + sd.row(sd.col(tp, leg, w=1000, gap=8),
                 sd.col(sd.p('<b>50-day reach, same convention</b> (shorter is better)', 24),
                        C.compare_bars(d, [('medapp_std', 'MEDAPP', sd.RED, 'this note'),
                                           ('bham_28_2m_pb5', 'Birmingham', sd.ORANGE, 'birmingham/ (2.8 MeV, 2 m, 5 cm Pb)')], 260),
                        w=620, gap=12), gap=40),
        short='reach',
        notes=f"""Left of the best point the reach is statistics-limited; right of it the random triggers (DREAM dead time), Micromegas occupancy and accidentals take over. Taking the Pb filter out buys flux but not reach: the extra γ fill the trigger.

As built (16 SiPM bars read out, 2 × 20 × 30 cm plastics, LS): {sci(rho_ab, 1)}. Comparison, same convention: ILL PF1B {sci(d['pf1b'], 1)} at its best rate (detector-limited), GANIL NFS {sci(d['nfs'], 1)}, n_TOF EAR2 {sci(d['ear2'], 1)} (survey_fast.py).

The survey bracket for MEDAPP was {sci(old_lo, 1)} (Geant4 N4 table) to {sci(old_hi, 1)} (flat): the measured singles land near the optimistic end. The γ field per neutron and its spectrum (a stand-in, mean 2.4 MeV) are now the biggest input to check with FRM II.""")

# --------------------------------------------------------------------------- #
flow = sd.flow([dict(label='reactor restart', sub='central channel delivered, installed, accepted', color=sd.RED,
                     tip='no date as of Mar 2026'),
                dict(label='room for the arms', sub='MEDAPP treatment room or NECTAR behind it (ask)', color=sd.ORANGE),
                dict(label='flight + exit tubes, dump', sub='vacuum MLC → cell; beam dump behind the arms', color=sd.GREEN),
                dict(label='γ field + filters', sub='γ/n and the >3 MeV γ tail at the cell (ask)', color=sd.ORANGE),
                dict(label='~1-2 weeks of beam', sub='shared with therapy and NECTAR', color=sd.GREEN)], size=22)
D.slide('needs', sd.title('What it would take: a running reactor, a place for the arms, tubes and a dump',
                          'in order of what decides it')
        + flow
        + sd.row(sd.callout(f'Beam time is not the problem: {C.fmt_days(days)} of beam reach the ATOMKI strength at 3σ, '
                            'statistics only.', sd.GREEN, 28),
                 sd.callout('The restart is: FRM II has been off since 2020 and has no date.', sd.RED, 28), gap=48)
        + sd.table(['ask FRM II', 'why it matters'],
                   [['restart date; first cycles’ user programme', 'nothing runs before it'],
                    ['free space around the beam in MEDAPP / NECTAR', 'arms ~1.6 m across (2 m with 75 cm plates)'],
                    ['γ flux and spectrum at the cell, standard filters', '95 % of the singles here; a stand-in today'],
                    ['MLC at ~8 × 8 cm; vacuum tube from its exit; beam dump', 'the beam-line model assumes all three'],
                    ['a few weeks of beam for a non-medical user', f'{C.fmt_days(days)} of beam at the best rate']],
                   size=24, widths=[760, 700], align=['left', 'left']),
        short='what it needs',
        notes="""Questions for FRM II / MLZ (contacts in FACILITY.md §4):
<ol><li>Restart date and the first cycles' user programme.</li>
<li>Free space around the beam axis in MEDAPP and in NECTAR (the arms are ~1.6 m across, ~2 m with the 75 cm plates); floor loading; where the beam ends.</li>
<li>The γ flux and spectrum at the reference position with the standard filters, and the measured intermediate-neutron fraction (Breitkreutz et al. 2008).</li>
<li>Can the MLC close to ~8 × 8 cm, and can a vacuum tube run from the MLC exit?</li>
<li>Beam time for a non-medical user: a few weeks across cycles.</li></ol>""")

# --------------------------------------------------------------------------- #
end = (sd.title('What this does not settle yet', None)
       + sd.row(sd.col(sd.p('<b>Not in the simulation</b>', 30, sd.DINK),
                       sd.p('• The room, the beam dump and the MLC itself: only the beam line from 1 m upstream of the cell.', 26, sd.DINK),
                       sd.p('• The γ field is a stand-in (1 photon per neutron, mean 2.4 MeV); ×3 more costs ×1.5.', 26, sd.DINK),
                       sd.p('• Micromegas occupancy from γ that make no trigger leg.', 26, sd.DINK), gap=18),
                sd.col(sd.p('<b>Physics and facility</b>', 30, sd.DINK),
                       sd.p('• X17/IPC is taken from E_n ≤ 2.75 MeV only; 24 % of the neutrons are above.', 26, sd.DINK),
                       sd.p('• No cosmic veto yet: a real one improves the reach.', 26, sd.DINK),
                       sd.p('• Restart date, space for the arms, beam time: ask FRM II.', 26, sd.DINK), gap=18), gap=80))
D.slide('end', end, dark=True, short='open questions')

out = D.write(O / 'frm2-medapp-x17-feasibility.html',
              note_meta=dict(title='FRM II MEDAPP X17 feasibility',
                             summary='Could the MX17 apparatus test the ATOMKI ⁴He anomaly in the FRM II fission-neutron beam? Facility, beamline, Geant4 soft-beam background and the reach.',
                             tags='x17, frm2, medapp, feasibility', date='2026-10-20'),
              footer='Built by x17_facility_search/frm2_medapp/deck/build_deck.py from survey/soft_sim/soft_reach.py and frm2_medapp/medapp_beam.py outputs.')
print(out)
