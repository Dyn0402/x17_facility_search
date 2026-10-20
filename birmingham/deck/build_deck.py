"""Build the Birmingham HF-ADNeF X17 feasibility slide note.

Reads survey/soft_sim/out/ (soft_reach.py) and birmingham/out/ (bham_beam.py), writes
birmingham/out/birmingham-x17-feasibility.html:

    ~/PycharmProjects/nTof_x17/.venv/bin/python birmingham/deck/build_deck.py
    python3 ~/PycharmProjects/dylan-cern-site/scripts/add-note.py \\
        birmingham/out/birmingham-x17-feasibility.html --slug birmingham-x17-feasibility --force --deploy
"""
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / 'survey' / 'soft_sim'))
import deck_common as C  # noqa: E402
from deck_common import sd, sci  # noqa: E402
import cartoon  # noqa: E402

O = HERE.parent / 'out'
d = C.load()
K = 'bham_28_2m_pb5'                 # baseline: 2.8 MeV, cell 2 m from the Li, 5 cm Pb in the collimator
rho = C.R(d, K)
rho_ab = C.R(d, K, hw='as built')
rho0 = C.R(d, 'bham_28_2m_pb0')
rho26 = C.R(d, 'bham_26_2m_pb5')
floor = C.R(d, K, col='rho3_floor')
days = C.days_to_atomki(rho)
ok_arm = C.Cp(d, K, 'ok_singles_per_arm')
legs = C.Cp(d, K, 'legs_per_arm')
ncell = C.Cp(d, K, 'n_cell')
ipc = C.Cp(d, K, 'ipc_per_day')
corr_g = C.Cp(d, 'bham_28_2m_pb0', 'corr_fact_per_day')
beam = pd.read_csv(O / 'bham_beam.csv').set_index('ep')
shield = pd.read_csv(O / 'bham_shield.csv')
sv = d['survey']
old_lo = float(sv[(sv.key == 'bham2') & (sv.singles_model == 'geant')].rho3.iloc[0])
old_hi = float(sv[(sv.key == 'bham2') & (sv.singles_model == 'flat')].rho3.iloc[0])
bpe = shield.set_index('eps').bpe_cm

D = sd.Deck('Birmingham HF-ADNeF: X17 feasibility',
            'Could the MX17 apparatus test the ATOMKI ⁴He anomaly at the Birmingham 30 mA ⁷Li(p,n) neutron source? '
            'The facility, the beam port it would need, and the reach with its own Geant4 beam background.')

# --------------------------------------------------------------------------- #
cover = (sd.kicker('MX17 at Birmingham · HF-ADNeF ⁷Li(p,n) · feasibility · 20 Oct 2026')
         + '<h1 style="font-size:62px;font-weight:600;line-height:1.08;letter-spacing:-1.5px">'
           f'Birmingham’s lithium source runs today and would pass ATOMKI ⁴He ×{C.RHO / rho:.1f} in 50 days, '
           'given a shielded beam port</h1>'
         + sd.p('³He(n,e⁺e⁻)⁴He on the 30 bar × 40 cm cell 2 m from the Li target, 2.8 MeV protons at 30 mA, '
                'Ø8 cm collimator with 5 cm of Pb, big plastics. X17/IPC reached at 3σ with IPC, cosmics and the '
                'beam’s own Geant4 background (neutrons and target γ).', 30, sd.DMUT)
         + sd.row(
             sd.bignum(sci(rho, 1), 'X17/IPC at 3σ in 50 days', sd.DGREEN,
                       f'ATOMKI ⁴He: 1.5×10⁻³. As built: {sci(rho_ab, 1)}.',
                       tip=f'survey bracket before this run: {sci(old_lo, 1)} – {sci(old_hi, 1)}'),
             sd.bignum(C.fmt_days(days), 'of beam to reach the ATOMKI strength', sd.DGREEN,
                       'statistics only; full current, no throttle needed'),
             sd.bignum('no port', 'today: rigs sit at the target', sd.DRED,
                       f'the arms need ~{bpe.loc[1e-5]:.0f} cm of borated PE between them and a 3.7×10¹³ n/s source'),
             gap=56))
D.slide('cover', cover, dark=True, short='cover',
        notes=f"""Reach = the X17/IPC(E1) ratio a 50-day run detects at 3σ (Asimov over the θ histogram summed over E_n: a DC beam has no TOF tag). Every neutron is below 1.1 MeV, so the E* ≤ 22 MeV and all-E* conventions agree.

The beam needs no throttle: at the cell {ncell:.2g} n/s give {ok_arm:,.0f} singles and {legs:,.0f} trigger legs per arm per second, and DREAM stays > 95 % live. The reach is the statistics floor (IPC + cosmics): {sci(floor, 1)}.

Without the Pb filter: {sci(rho0, 1)}. At 2.6 MeV: {sci(rho26, 1)}.

Files: <code>birmingham/FEASIBILITY.md</code>, <code>birmingham/FACILITY.md</code>, <code>survey/soft_sim/</code>.""")

# --------------------------------------------------------------------------- #
facts = sd.col(
    sd.card(sd.p('<b>University of Birmingham</b>, Edgbaston (UK)', 28)
            + sd.p('HF-ADNeF, commissioned 7 Dec 2023: a ~€15M national user facility (NNUF/EPSRC).', 24, sd.MUT)),
    sd.card(sd.p('<b>30 mA of 2.6-2.8 MeV protons on lithium</b>', 28)
            + sd.p('A BNCT-type electrostatic accelerator on a rotating Li wheel: > 3×10¹³ n/s, all below 1.1 MeV.', 24, sd.MUT)),
    sd.card(sd.p('<b>Status: operating</b>', 28, sd.GREEN)
            + sd.p('Fusion/fission materials, BNCT, nuclear data; nuclear (astro)physics programme starting.', 24, sd.MUT)),
    w=700, gap=24)
D.slide('where', sd.title('Birmingham: the strongest accelerator neutron source in Europe',
                          'the facilities this study compares; hover the dots and dotted terms for details')
        + sd.row(C.europe_map(880, 660, 'Birmingham'), facts, gap=56),
        short='where',
        notes="""Site 52.45 N, 1.93 W, School of Physics and Astronomy. The accelerator sits in an underground bunker extension; the neutron target room is in the Medical Physics building, one floor below the MC40 cyclotron's switching magnet.

Team (public): M. Freer (PI), C. Wheldon (director), J. Bishop (neutron lead), B. Phoenix (technical lead), Tz. Kokalova.

"Strongest in Europe": among accelerator-driven continuous sources we found (FACILITY.md); SARAF and FRANZ are not running at their design currents.

Sources: Wheldon, STFC seminar 2025; Brooks et al. poster; Wheldon JINST 17 (2022) C10010. <code>birmingham/FACILITY.md</code>.""")

# --------------------------------------------------------------------------- #
cards = sd.row(
    sd.card(sd.p(f'<b>{beam.loc[2.8, "n_tot"]:.1e} n/s</b>'.replace('e+13', '×10¹³'), 34, sd.BLUE)
            + sd.p('at 30 mA, 2.8 MeV (3×10¹³ at 2.6)', 22, sd.MUT)),
    sd.card(sd.p(f'<b>≤ {beam.loc[2.8, "max_En0"]:.1f} MeV</b>', 34, sd.BLUE)
            + sd.p(f'mean {beam.loc[2.8, "mean_En0"]:.2f} MeV at 0°, forward ×{beam.loc[2.8, "forward_gain"]:.1f}', 22, sd.MUT)),
    sd.card(sd.p('<b>γ: 478 keV + 15-18 MeV</b>', 34, sd.ORANGE)
            + sd.p('⁷Li(p,p′γ), ⁷Be decay; ⁷Li(p,γ)⁸Be', 22, sd.MUT)),
    sd.card(sd.p('<b>no beam port</b>', 34, sd.RED) + sd.p('rigs are mounted at the Ti vessel', 22, sd.MUT)),
    gap=24)
D.slide('beamline', sd.title('A 1 m lithium wheel in a Ti vessel; the X17 station adds a wall',
                             'top view, not to scale; dashed green = what the X17 set-up adds (shield + collimator, tubes, dump)')
        + cartoon.beamline(1664, 500) + cards,
        short='beamline',
        notes=f"""Accelerator: Neutron Therapeutics hyperion-type electrostatic machine (as in the Helsinki BNCT centre), ECR source, 14 HV stages, 0.4–2.6 MeV nominal and 2.8 MeV maximum, < 50 mA; 117 kW on target at 45 mA. Target: 16 water-cooled Cu petals with ~300 µm of Li on a 1 m wheel at 600 rpm, inside a Ti vacuum vessel (4–6 mm exit wall), lead around it; a graphite moderator below gives ~10⁹ n/cm²/s thermal. A robot changes the petals (⁷Be reaches 6 TBq).

Through a Ø8 cm collimator 2 m from the Li at 2.8 MeV: {beam.loc[2.8, 'n_cell']:.2g} n/s (bham_beam.py: thick-target slowing-down Monte Carlo, CM-isotropic stand-in, normalised to the facility's 3×10¹³ n/s at 30 mA, 2.6 MeV).

The room's size is not public ("about 4 m³" for rigs at the target): whether a shield wall and the arms fit is the first question for Birmingham.""")

# --------------------------------------------------------------------------- #
sp, leg, fr = C.spectrum_plot(1100, 600, 'bham')
f_b = fr['Birmingham ⁷Li(p,n), 2.8 MeV']
f_nfs = fr['GANIL NFS d(40)+Be']
D.slide('spectrum', sd.title(f'Every neutron is below 1.1 MeV: {100 * f_b:.0f} % in the window and nothing above it',
                             'normalised E dN/dE at 0°; shaded: E_n 0.2–2.75 MeV (E* ≤ 22.1 MeV, X17 opening-angle edge ≥ 99°)')
        + sd.row(sp, sd.col(leg, sd.p('No IPC above E* = 21.5 MeV and no fast neutrons to fire the trigger plastics.', 26),
                            sd.p('2.8 MeV (the maximum) beats 2.6 MeV: ×1.17 the neutrons, and a harder spectrum where σ(n,γ) is larger.', 24, sd.MUT),
                            w=480, gap=24), gap=40),
        short='spectrum',
        notes=f"""Thick-target ⁷Li(p,n) at 0°: kinematics checked against Lee & Zhou 1999 (maximum 787 keV at 2.5 MeV) and the facility's 0.9 MeV (2.6) / 1.1 MeV (2.8). The CM angular distribution is a stand-in (isotropic); the real one is forward-peaked above 2.3 MeV, which would raise the 0° yield.

The rest of the window fraction is below 0.2 MeV ({100 * (1 - f_b):.0f} %): still ×40–200 the pairs of a thermal neutron per neutron.

<code>birmingham/bham_beam.py</code> → <code>out/bham_spectra.csv</code>, <code>out/bham_beam.csv</code>.""")

# --------------------------------------------------------------------------- #
sp, leg = C.singles_plot(d, 1120, 600)
D.slide('singles', sd.title('Geant4: below 1.7 MeV a neutron almost never fires a leg, so the trigger stays quiet',
                            'MX17_Full_Geant branch soft, NFS cell and arms, big plastics: forced-collision neutrons (N5) and photons (G5/G6)')
        + sd.row(sp, sd.col(leg, sd.p('A single = a trigger leg (SiPM + back plastic) with a Micromegas segment in the active area.', 24),
                            sd.p(f'Here: {ok_arm:,.0f} singles per arm per second at the full 30 mA.', 26, sd.BLUE),
                            w=460, gap=24), gap=40),
        short='Geant4 singles',
        notes="""The leg needs half a MIP (1.7 MeV) in the back plastic: proton recoils from < 1.7 MeV neutrons cannot give it. Soft neutrons make singles only through capture γ and rare multi-step histories: ~3×10⁻⁷ per arm per neutron, ×30 below the survey's flat bound.

Photons below ~2.7 MeV (the 478 keV line) make no legs at all. The 15–18 MeV ⁸Be lines do: ~6×10⁻⁵ singles per arm per photon.

N5: 9×10⁷ forced-collision neutrons per hardware set, 1/E on 1 keV–20 MeV. G5: 2×10⁸ photons 1/E on 0.1–20 MeV. G6: 2×10⁸ photons flat on 14–19 MeV. <code>survey/soft_sim/</code>.""")

# --------------------------------------------------------------------------- #
r = d['reach']
r = r[(r.site == 'bham') & (r.hw == C.HW) & (r.days == 50) & (r.signal == 'E* ≤ 22 MeV')]
P = sd.Plot(1060, 600, x=(-1, 11, 'lin'), y=(8e-5, 2e-3, 'log'), xlabel='Pb filter in the collimator [cm]',
            ylabel='X17/IPC at 3σ in 50 days')
P.xticks([(v, f'{v:g}') for v in (0, 5, 10)]).yticks([(1e-4, '10⁻⁴'), (3e-4, '3×10⁻⁴'), (1e-3, '10⁻³')])
P.hline(C.RHO, sd.GREEN, label='ATOMKI ⁴He 1.5×10⁻³')
legs_ = []
for ep, dist, col, dash in ((2.8, 1, sd.RED, '8 6'), (2.8, 2, sd.RED, None), (2.6, 1, sd.ORANGE, '8 6'), (2.6, 2, sd.ORANGE, None)):
    q = r[r.key.str.startswith(f'bham_{ep * 10:.0f}_{dist}m_')].copy()
    q['pb'] = q.key.str.extract(r'pb(\d+)').astype(float)
    q = q.sort_values('pb')
    lab = f'{ep} MeV, cell at {dist} m'
    P.line(list(q.pb), list(q.rho3), col, dash=dash, r=8,
           tips=[f'{lab}, {p:g} cm Pb: {v:.2g} ({C.fmt_days(C.days_to_atomki(v))} to ATOMKI)' for p, v in zip(q.pb, q.rho3)])
    legs_.append((lab, col, 'dash' if dash else 'line'))
P.points([5], [rho], sd.INK, r=13, tips=[f'baseline: {rho:.2g}'])
P.text(5.4, rho * 0.82, 'baseline', 22, sd.INK)
D.slide('filter', sd.title('Distance and the γ filter cost reach, but every option passes ATOMKI ×2 or more',
                           '50 days, big plastics, full 30 mA; the Pb filter attenuates the target γ and the neutron beam together')
        + sd.row(sd.col(P.svg('reach vs Pb filter'), sd.legend(legs_, size=22), w=1060, gap=8),
                 sd.col(sd.p('The reach is set by statistics: fewer neutrons through the cell, less reach.', 26),
                        sd.p('5 cm of Pb removes 478 keV γ ×10⁴ and the 15–18 MeV lines ×17, at ×0.37 in neutrons.', 24, sd.MUT),
                        sd.p(f'Without it {sci(rho0, 1)}, but ~10⁹ 478 keV γ/s and their conversion pairs cross the cell.', 24, sd.MUT),
                        w=540, gap=24), gap=48),
        short='γ filter',
        notes=f"""Pb attenuation (NIST XCOM): μ = 1.76 /cm at 478 keV, 0.57 /cm at 15–18 MeV; neutrons: uncollided only, Σ ≈ 0.20 /cm (σ_tot ≈ 6 b at 0.3–1 MeV), conservative because forward-scattered neutrons stay in the beam.

Target γ through the spot at 2 m, no filter: 478 keV ~1×10⁹ /s (⁷Li(p,p′γ) ~6×10⁻⁵ per proton, Taskaev et al.; plus ⁷Be decay, 10.4 % of up to 6 TBq) and 15–18 MeV ~2×10⁶ /s (⁷Li(p,γ)⁸Be ~1×10⁻⁷ per proton, an estimate). The 478 keV photons make no trigger legs; their Micromegas occupancy is not in the model. The ⁸Be lines convert in the cell's end cap and window: with no filter the correlated term is {corr_g:,.0f} per day after cuts (factorised).

1 m is optimistic: a shield wall (next slides) needs room between target and cell.""")

# --------------------------------------------------------------------------- #
hb, q = C.budget_bars(d, K, 700)
D.slide('budget', sd.title('At full current the background is IPC and cosmics; the beam adds almost nothing',
                           'events per day in θ = 100–150° after the vertex and E_sum > W/2 cuts; baseline (2.8 MeV, 2 m, 5 cm Pb), big plastics')
        + sd.row(sd.col(hb, C.rate_table(d, K), w=1000, gap=36), sd.col(sd.p(f'X17 at the ATOMKI ratio is {100 * q.X17_win_per_day / q.IPC_win_per_day:.1f} % of the IPC in the window.', 26),
                            sd.p('Cosmics are now a third of the background: a cosmic veto (arm-to-arm TOF, as at LNL) pays here.', 24, sd.MUT),
                            w=560, gap=24), gap=48),
        short='background budget',
        notes=f"""Window counts are for orientation; the reach uses the whole θ histogram.

Accidentals: two singles from different particles within ±5 ns, built from the source's own Geant4 singles and passed through the reconstruction (vertex: both Micromegas segments within 60 mm of the beam axis; E_sum > W/2). Correlated: same-event two-arm events, factorised (pooled vertex and E_sum pass fractions), because ~1 MC event passes every cut.

IPC into 4π: {ipc:,.0f} pairs per day.""")

# --------------------------------------------------------------------------- #
rows = [[sci(e, 0), sci(t, 1), f'{b:.0f} cm'] for e, t, b in zip(shield.eps, shield.T_needed, shield.bpe_cm)]
n_arm = float(shield.n_arm_unshielded.iloc[0])
ok_target = 0.1 * ok_arm
PS = sd.Plot(760, 520, x=(0, 80, 'lin'), y=(1, 1e8, 'log'), xlabel='borated PE between target and arms [cm]',
             ylabel='leakage singles per arm [/s]')
PS.xticks([(v, f'{v:g}') for v in (0, 20, 40, 60, 80)]).yticks(sd.log_ticks(0, 8))
PS.hline(ok_target, sd.GREEN, label='10 % of the beam’s own singles', anchor='start')
for e, col, dash in ((1e-6, sd.BLUE, '8 6'), (1e-5, sd.RED, None), (1e-4, sd.ORANGE, '4 6')):
    xs = list(range(0, 81, 5))
    ys = [n_arm * e * 10 ** (-x / 10) for x in xs]
    PS.line(xs, [y if y >= 1 else None for y in ys], col, dash=dash, markers=False, w=4,
            tip=f'{sci(e, 0)} singles per neutron entering an arm')
shield_leg = sd.legend([(f'{sci(e, 0)} singles per entering n', c, 'dash' if dsh else 'line')
                        for e, c, dsh in ((1e-6, sd.BLUE, 1), (1e-5, sd.RED, 0), (1e-4, sd.ORANGE, 1))], size=20)
D.slide('shield', sd.title(f'The 4π field needs ~{bpe.loc[1e-5]:.0f} cm of borated PE between the target and the arms',
                           'an estimate, not Geant4: what keeps the leakage singles below 10 % of the beam’s own')
        + sd.row(sd.col(PS.svg('leakage singles vs shield'), shield_leg, w=760, gap=8),
                 sd.col(sd.p(f'With no wall, one arm 2 m away sees <b>{sci(n_arm, 1)}</b> n/s, ×{n_arm / ncell:.0f} what '
                             'goes through the cell.', 28),
                        sd.table(['singles per entering n', 'transmission', 'borated PE'], rows, size=22, widths=[300, 220, 200]),
                        sd.callout('Today rigs sit at the Ti vessel, in the full 4π field. MX17 cannot.', sd.RED, 26),
                        sd.callout('A BNCT beam-shaping assembly is this wall with a moderator in the hole.', sd.GREEN, 24),
                        w=820, gap=24), gap=56),
        short='shield',
        notes=f"""Unshielded flux at 2 m, 2.8 MeV, 30 mA: the 0° yield {beam.loc[2.8, 'n_per_sr_0deg']:.2g} n/s/sr over (200 cm)², through one arm's 75 × 75 cm face. The arms sit near 0°, so this is close to right.

The singles per neutron entering an arm are not simulated: 10⁻⁶–10⁻⁴ spans capture γ in the plastics and SiPM wall. The tenth-value layer of borated polyethylene for 0.1–1 MeV neutrons with build-up is ~10 cm (stand-in). A Pb layer behind it stops the 2.2 MeV capture γ.

<code>birmingham/bham_beam.py</code> → <code>out/bham_shield.csv</code>. A Geant4 model of the wall and the room is the next simulation.""")

# --------------------------------------------------------------------------- #
D.slide('compare', sd.title(f'Against the other facilities: the best reach found, {C.fmt_days(days)} to ATOMKI',
                            'X17/IPC at 3σ in 50 days, E* ≤ 22 MeV, big plastics; shorter bars are better')
        + sd.row(C.compare_bars(d, [('medapp_std', 'FRM II MEDAPP', sd.ORANGE, 'frm2_medapp/ (reactor off)'),
                                    (K, 'Birmingham (baseline)', sd.RED, 'this note'),
                                    ('bham_28_2m_pb0', 'Birmingham, no Pb', sd.RED, 'this note: 2 m, no filter')], 800),
                 sd.col(sd.p('Same apparatus, same cuts, same fit: only the beam changes.', 26),
                        sd.p('Thermal beams stop at the detector’s rate walls (PF1B); pulsed white sources at their duty factor '
                             '(n_TOF); NFS at its hard spectrum.', 24, sd.MUT), w=520, gap=24), gap=48),
        short='comparison',
        notes=f"""Reference rows from the survey (<code>survey/SURVEY.md</code>): ILL PF1B {sci(d['pf1b'], 1)} at its best absorbed rate; GANIL NFS {sci(d['nfs'], 1)} and n_TOF EAR2 {sci(d['ear2'], 1)} (survey_fast.py, Geant4 singles table).

As built (16 SiPM bars, 2 × 20 × 30 cm plastics, LS): {sci(rho_ab, 1)}, still at the ATOMKI strength.""")

# --------------------------------------------------------------------------- #
flow = sd.flow([dict(label='a beam port', sub=f'~{bpe.loc[1e-5]:.0f} cm BPE + Pb wall, Ø8 cm collimator', color=sd.RED),
                dict(label='room for the arms', sub='≥ 2 m from the Li, ~2 × 2 m (ask)', color=sd.ORANGE),
                dict(label='γ filter + tubes + dump', sub='5 cm Pb; vacuum to the cell; dump behind', color=sd.GREEN),
                dict(label='protons, 2.8 MeV, 30 mA', sub='not the planned deuterons', color=sd.GREEN),
                dict(label='~1-2 weeks of beam', sub='a national user facility', color=sd.GREEN)], size=22)
D.slide('needs', sd.title('What it would take: a shielded port, a place for the arms, a few weeks of protons',
                          'in order of what decides it')
        + flow
        + sd.table(['ask Birmingham', 'why it matters'],
                   [['target-room and neighbouring-room dimensions; a port through the wall?', 'the arms cannot sit in the 4π field'],
                    ['could a BNCT-style collimator (no moderator) be built?', 'the vendor builds these for clinics'],
                    ['measured 0° spectrum, 478 keV and 15-18 MeV γ yields', 'stand-ins today'],
                    ['protons at 2.8 MeV kept available after the deuteron upgrade', 'deuterons give an NFS-like hard spectrum'],
                    ['user access for an external collaboration', f'{C.fmt_days(days)} of beam reach ATOMKI at 3σ']],
                   size=24, widths=[860, 600], align=['left', 'left']),
        short='what it needs',
        notes="""Contacts (public): C. Wheldon (director), J. Bishop (neutron lead), B. Phoenix (technical lead); FACILITY.md §2.""")

# --------------------------------------------------------------------------- #
end = (sd.title('What this does not settle yet', None)
       + sd.row(sd.col(sd.p('<b>Not in the simulation</b>', 30, sd.DINK),
                       sd.p('• The shield wall, the room and the dump: leakage is an estimate (×100 range).', 26, sd.DINK),
                       sd.p('• Micromegas occupancy from 478 keV γ, which make no trigger leg.', 26, sd.DINK),
                       sd.p('• Target γ yields and the 0° spectrum are stand-ins until measured.', 26, sd.DINK), gap=18),
                sd.col(sd.p('<b>Facility</b>', 30, sd.DINK),
                       sd.p('• There is no beam port today; the room size is not public.', 26, sd.DINK),
                       sd.p('• The deuteron upgrade must not replace the 2.8 MeV protons.', 26, sd.DINK),
                       sd.p('• No cosmic veto yet: a real one improves the reach.', 26, sd.DINK), gap=18), gap=80))
D.slide('end', end, dark=True, short='open questions')

out = D.write(O / 'birmingham-x17-feasibility.html',
              note_meta=dict(title='Birmingham HF-ADNeF X17 feasibility',
                             summary='Could the MX17 apparatus test the ATOMKI ⁴He anomaly at the Birmingham 30 mA ⁷Li(p,n) source? Facility, the beam port it needs, Geant4 soft-beam background and the reach.',
                             tags='x17, birmingham, feasibility', date='2026-10-20'),
              footer='Built by x17_facility_search/birmingham/deck/build_deck.py from survey/soft_sim/soft_reach.py and birmingham/bham_beam.py outputs.')
print(out)
