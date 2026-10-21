"""Build the LANSCE WNR X17 feasibility slide note.

Reads lansce_wnr/out/ (wnr_beam.py) and the survey / soft-sim tables for the comparison, writes
lansce_wnr/out/lansce-wnr-x17-feasibility.html:

    ~/PycharmProjects/nTof_x17/.venv/bin/python lansce_wnr/deck/build_deck.py
    python3 ~/PycharmProjects/dylan-cern-site/scripts/add-note.py \\
        lansce_wnr/out/lansce-wnr-x17-feasibility.html --slug lansce-wnr-x17-feasibility --force --deploy
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / 'survey' / 'soft_sim'))
import deck_common as C  # noqa: E402
from deck_common import sd, sci  # noqa: E402
import cartoon  # noqa: E402

O = HERE.parent / 'out'
K = '90L_10m'                       # headline: 4FP90L, cell 10 m from the W, 1.8 µs, big plastics
t = pd.read_csv(O / 'wnr_reach.csv')
sc = pd.read_csv(O / 'wnr_scan.csv')
comp = pd.read_csv(O / 'wnr_components.csv')
sens = pd.read_csv(O / 'wnr_khi_sensitivity.csv')
spec = pd.read_csv(O / 'wnr_spectra.csv')
ssum = pd.read_csv(O / 'wnr_spectra_summary.csv').set_index('angle')
prof = pd.read_csv(O / 'wnr_time_profile.csv')
d = C.load()


def R(key, hw=C.HW, days=50, signal='E* ≤ 22 MeV', col='rho3'):
    q = t[(t.key == key) & (t.hw == hw) & (t.days == days) & (t.signal == signal)]
    return float(q[col].iloc[0])


rho = R(K)
rho_ab = R(K, 'as built')
rho7_ab = R('90L_7m', 'as built')
rho_all = R(K, signal='all E*')
rho100 = R('90L_10m_100Hz')
rho_ice = R('30L_20m')
floor = R(K, col='rho3_floor')
days = C.days_to_atomki(rho)
row = t[(t.key == K) & (t.hw == C.HW) & (t.days == 50) & (t.signal == 'E* ≤ 22 MeV')].iloc[0]
sv = d['survey']
old_lo = float(sv[(sv.key == 'wnr') & (sv.singles_model == 'geant')].rho3.iloc[0])
old_hi = float(sv[(sv.key == 'wnr') & (sv.singles_model == 'flat')].rho3.iloc[0])
S = lambda k, lab, hw=C.HW: float(sens[(sens.key == K) & (sens.hw == hw) & (sens.signal == 'E* ≤ 22') & (sens.K_HI.astype(str) == lab)].rho3.iloc[0])  # noqa: E731

D = sd.Deck('LANSCE WNR: X17 feasibility',
            'Could the MX17 apparatus test the ATOMKI ⁴He anomaly on a white spallation beam at Los Alamos? '
            'The WNR Target 4 flight paths, the beam’s time structure, and the reach with time of flight.')

# --------------------------------------------------------------------------- #
cover = (sd.kicker('MX17 at LANSCE · WNR Target 4 · feasibility · 21 Oct 2026')
         + '<h1 style="font-size:60px;font-weight:600;line-height:1.08;letter-spacing:-1.5px">'
           f'On the 90° flight path at 10 m, WNR would pass ATOMKI ⁴He ×{C.RHO / rho:.1f} in 50 days, '
           'using only neutrons below 2.75 MeV</h1>'
         + sd.p('³He(n,e⁺e⁻)⁴He on the 30 bar × 40 cm cell, the bare W target’s 800 MeV spallation beam, '
                'Ø8 cm spot, 1.8 µs micropulses, time of flight selecting 0.2–2.75 MeV, big plastics. Re-weighted '
                'from the NFS and soft-beam Geant4 runs: IPC, cosmics, accidentals and correlated beam background.',
                28, sd.DMUT)
         + sd.row(
             sd.bignum(sci(rho, 1), 'X17/IPC at 3σ in 50 days', sd.DGREEN,
                       f'ATOMKI ⁴He: 1.5×10⁻³. As built: {sci(rho_ab, 1)} ({sci(rho7_ab, 1)} at 7 m).',
                       tip=f'survey bracket (30°, estimated spectrum): {sci(old_lo, 1)} – {sci(old_hi, 1)}'),
             sd.bignum(C.fmt_days(days), 'of beam to reach the ATOMKI strength', sd.DGREEN,
                       'statistics only; E_n ≤ 2.75 MeV (E* ≤ 22 MeV)'),
             sd.bignum('operating', 'a user facility today', sd.DGREEN,
                       '…but 90L beam time is “very limited” (2026 call)'),
             gap=56))
D.slide('cover', cover, dark=True, short='cover',
        notes=f"""Reach = the X17/IPC(E1) ratio a 50-day run detects at 3σ (Asimov over m_ee histograms in each time-of-flight E_n bin). Only E_n 0.2–2.75 MeV carry X17 here (E* ≤ 22.1 MeV, the ATOMKI-like excitation); the trigger is gated to those arrival times. With X17/IPC constant at all E* the best analysis is the same one (the gate keeps DREAM alive): {sci(rho_all, 1)}.

The beam is used in full: {row.n_cell:.2g} n/s through the spot, {row.ok_singles_per_arm:.0f} singles per arm per second (time-averaged), DREAM {row.live:.2f} live. The reach sits on its IPC + cosmic floor ({sci(floor, 1)}).

The survey had WNR at {sci(old_lo, 1)}–{sci(old_hi, 1)} on the 30° path with an estimated spectrum; here the spectrum is LANL's per-angle yield, the singles come from the soft-beam Geant4 run, and the cell sits at the softest, shortest path.

Files: <code>lansce_wnr/FEASIBILITY.md</code>, <code>lansce_wnr/FACILITY.md</code>, <code>lansce_wnr/wnr_beam.py</code>.""")

# --------------------------------------------------------------------------- #
facts = sd.col(
    sd.card(sd.p('<b>Los Alamos, New Mexico (US)</b>', 28)
            + sd.p('LANSCE: an 800 MeV proton linac feeding five areas. WNR Target 4 is the unmoderated tungsten source.', 24, sd.MUT)),
    sd.card(sd.p('<b>Six flight paths at 15–90°</b>', 28)
            + sd.p('The more forward, the harder the spectrum. 90L: 7–15 m, the softest, used by fission chambers and the fission TPC.', 24, sd.MUT)),
    sd.card(sd.p('<b>Status: operating, user programme</b>', 28, sd.GREEN)
            + sd.p('Annual calls (nuclear science: February); run cycle June–December. Industry testing on the 30° paths.', 24, sd.MUT)),
    w=760, gap=24)
cards = sd.col(
    sd.card(sd.p('<b>~1.5 µA</b>', 34, sd.BLUE) + sd.p('40 × 625 µs macropulses/s, 7×10⁸ p every 1.8 µs', 22, sd.MUT)),
    sd.card(sd.p('<b>2.5 % duty</b>', 34, sd.BLUE) + sd.p('13 889 micropulses/s; the walls see the average', 22, sd.MUT)),
    sd.card(sd.p('<b>0.1–800 MeV</b>', 34, sd.ORANGE) + sd.p('bare W: no moderator, a γ flash every pulse', 22, sd.MUT)),
    w=700, gap=24)
D.slide('where', sd.title('WNR: the white neutron source of the Los Alamos linac',
                          'Target 4 and its flight paths; hover the dotted terms and the cartoon for details')
        + sd.row(facts, cards, gap=56),
        short='where',
        notes="""LANSCE, Los Alamos National Laboratory (35.87 N, 106.32 W). Target 4: W cylinder 7.5 cm × Ø3 cm in a 4 mm water jacket (Nowicki, Wender & Mocko, Physics Procedia 90 (2017) 374).

Timing (LANL time-of-flight page): macropulses 625 µs at 40 Hz for Target 4 (the linac can do 120 Hz); micropulses < 100 ps, 7×10⁸ protons each, 1.8 µs apart (3.6 or 7.2 µs on request). The LANL page quotes ~1.5 µA and an RF upgrade to ×2.5 (up to 5 µA); older documents quote ~4 µA (100 Hz).

Contacts: LANSCE User Office (lansce-user-office@lanl.gov); P-3 group leader C. Lee; WNR physicists S. Wender, M. Mocko. <code>lansce_wnr/FACILITY.md</code>.""")

# --------------------------------------------------------------------------- #
D.slide('beamline', sd.title('Six flight paths fan out from a bare W target; MX17 would sit on 90L',
                             'top view, not to scale; dashed green = what the X17 set-up adds (collimator to Ø8 cm, dump, ToF trigger gate)')
        + cartoon.beamline(1664, 560, L=10.0),
        short='beamline',
        notes="""4FP90L is the softest path and the shortest (7–15 m); it hosts fission chambers and the NIFFTE fission TPC, a detector of comparable size to one MX17 arm. Its collimation, the beam size at 7–10 m and the room around the beam are not public (ask).

The 30° paths (ICE House ~20 m, ICE-II ~10 m: placed from their quoted fluxes) are electronics-testing stations booked by industry; 15L hosts Chi-Nu; 60R radiography.""")

# --------------------------------------------------------------------------- #
cols = {15: sd.RED, 30: sd.ORANGE, 60: sd.BLUE, 90: sd.PURPLE}
P = sd.Plot(1060, 600, x=(0.1, 800, 'log'), y=(1e5, 3e8, 'log'), xlabel='neutron energy E_n [MeV]',
            ylabel='E·dN/dE through Ø8 cm at 10 m [n/s]')
P.xticks([(v, f'{v:g}') for v in (0.1, 1, 10, 100)]).yticks(sd.log_ticks(5, 8))
P.band([0.2, 2.75], [1e5, 1e5], [3e8, 3e8], sd.GREEN, 0.08, tip='E_n 0.2-2.75 MeV: E* ≤ 22.1 MeV, the ATOMKI-like window')
P.text(0.21, 2.2e8, 'ATOMKI-like window', 22, sd.GREEN)
for ang, c in cols.items():
    q = spec[(spec.angle == ang) & (spec.n_per_s_lethargy_10m > 0)]
    P.line(list(q.E), list(q.n_per_s_lethargy_10m), c, markers=False, w=5 if ang == 90 else 3,
           tip=f'{ang}°: {100 * ssum.loc[ang, "frac_0p2_2p75"]:.0f} % of neutrons in 0.2-2.75 MeV, '
               f'{100 * ssum.loc[ang, "frac_above_45"]:.1f} % above 45 MeV')
leg = sd.legend([(f'{a}°', c) for a, c in cols.items()], size=22)
D.slide('spectrum', sd.title(f'At 90° the beam is {100 * ssum.loc[90, "frac_0p2_2p75"]:.0f} % in the window and only '
                             f'{100 * ssum.loc[90, "frac_above_45"]:.0f} % above 45 MeV',
                             'LANL’s measured-and-calculated yield per proton vs angle (Nowicki 2017 Fig. 2, digitised), at 1.56 µA, 10 m, Ø8 cm')
        + sd.row(sd.col(P.svg('WNR spectra by angle'), leg, w=1060, gap=8),
                 sd.col(sd.p('The evaporation peak (0.1–3 MeV) is almost isotropic; the cascade tail is forward.', 26),
                        sd.p('So the soft flux barely depends on the path, but the hard tail does: ×8 fewer neutrons above 45 MeV at 90° than at 15°.', 24, sd.MUT),
                        sd.p('Cross-check: at 30°, 20 m the curve gives 1.2×10⁶ n/cm²/s above 1.5 MeV; LANL quotes 1.5×10⁶ for ICE House.', 22, sd.MUT),
                        w=520, gap=24), gap=48),
        short='spectrum',
        notes="""Y(E) in n/proton/MeV/sr read off Fig. 2 at 20 energies per angle (±10 %). Below 0.1 MeV (no data) Y ∝ √E is assumed; it only feeds wrap-around and singles.

Through the Ø8 cm spot at 10 m and 1.56 µA: ~3.7×10⁸ n/s at 90°, the same as all of NFS, but 55 % of it in the window against NFS's 2 %.

<code>lansce_wnr/out/wnr_spectra.csv</code>, <code>wnr_spectra_summary.csv</code>.""")

# --------------------------------------------------------------------------- #
P = sd.Plot(1500, 360, x=(0.0, 1.85, 'lin'), y=(10, 3e5, 'log'), xlabel='time after the micropulse [µs] (one 1.8 µs period, cell at 10 m)',
            ylabel='singles/s per arm (in a macropulse)')
P.xticks([(v, f'{v:g}') for v in (0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75)]).yticks(sd.log_ticks(1, 5))
c10 = comp[comp.key == K]
for _, b in c10.iterrows():
    if np.isfinite(b.u0_ns):
        soft = b.bin <= 2
        P.band([b.u0_ns / 1e3, b.u1_ns / 1e3], [10, 10], [3e5, 3e5], sd.PURPLE if soft else sd.GREY, 0.10 if soft else 0.04,
               tip=f'E_n {b.E_lo:g}-{b.E_hi:g} MeV arrive {b.u0_ns:.0f}-{b.u1_ns:.0f} ns')
P.line(list(prof.u_ns / 1e3), list(prof.rho_mean), sd.INK, markers=False, w=3,
       tip='ok singles per arm: prompt ones arrive with their neutron, delayed ones (captures) are flat')
D.slide('timing', sd.title('Time of flight does the work: the window is clean of the fast neutrons',
                           'top: the beam at the cell; bottom: Geant4 singles per arm within one period (purple: 0.2–2.75 MeV, grey: faster bins)')
        + cartoon.timing(1600, 320, L=10.0) + P.svg('singles vs time'),
        short='timing',
        notes=f"""At 10 m the 0.2 MeV neutrons arrive at 1.62 µs, before the next γ flash at 1.83 µs: no frame overlap in the window (wrap-around energy 0.16 MeV, as LANL's table gives). Beyond ~11 m the slowest bin starts to lose its low end to the next frame; 3.6 µs spacing fixes that but halves the protons.

Trigger gate: two-arm triggers accepted only in the purple windows (LANSCE provides the micropulse timing). Inside the gate: {row.trig_rand:.0f} random + {row.trig_corr:.2f} correlated triggers/s, DREAM {row.live:.2f} live (non-paralysable, 298 µs, triggers bunched in the 625 µs macropulses).

The singles come from Geant4 (N5 soft forced run below 8.5 MeV, the NFS N4 forced run up to 45 MeV, the 25–45 MeV value above). Prompt ones (within 100 ns of the neutron) fold into the period by their neutron's arrival; delayed ones are flat. Micromegas occupancy (1 µs memory) {row.occ_max:.3f}.""")

# --------------------------------------------------------------------------- #
q = sc[(sc.hw == C.HW) & (sc.signal == 'E* ≤ 22')]
P = sd.Plot(1060, 600, x=(4, 31, 'lin'), y=(5e-4, 1e-2, 'log'), xlabel='target → cell distance L [m]',
            ylabel='X17/IPC at 3σ in 50 days')
P.xticks([(v, f'{v:g}') for v in (5, 10, 15, 20, 25, 30)]).yticks([(5e-4, '5×10⁻⁴'), (1e-3, '10⁻³'), (3e-3, '3×10⁻³'), (1e-2, '10⁻²')])
P.hline(C.RHO, sd.GREEN, label='ATOMKI ⁴He 1.5×10⁻³')
P.band([7, 15], [5e-4, 5e-4], [1e-2, 1e-2], sd.PURPLE, 0.06, tip='4FP90L: 7-15 m')
legs = []
for ang, c in cols.items():
    for T_, dash in ((1.8, None), (3.6, '8 6')):
        z = q[(q.angle == ang) & (q.T_us == T_)].sort_values('L')
        P.line(list(z.L), list(z.rho3), c, dash=dash, r=5, w=4 if ang == 90 and T_ == 1.8 else 3,
               tips=[f'{ang}°, {T_:g} µs, {L:g} m: {v:.2g} (throttle {s:.2g}, live {lv:.2f})'
                     for L, v, s, lv in zip(z.L, z.rho3, z.throttle, z.live)])
    legs.append((f'{ang}°', c))
legs.append(('3.6 µs spacing', sd.GREY, 'dash'))
P.points([10], [rho], sd.INK, r=12, tips=[f'baseline 90L, 10 m: {rho:.2g}'])
g15 = float(q[(q.angle == 15) & (q.T_us == 1.8) & (q.L == 15)].rho3.iloc[0])
g90 = float(q[(q.angle == 90) & (q.T_us == 1.8) & (q.L == 15)].rho3.iloc[0])
P.text(10.5, rho * 0.8, 'baseline', 22, sd.INK)
D.slide('distance', sd.title('Distance decides; the angle matters less. Best near 10 m, 1.8 µs',
                             '50 days, E* ≤ 22 MeV, big plastics, best throttle; the window is cut at the next γ flash')
        + sd.row(sd.col(P.svg('reach vs distance'), sd.legend(legs, size=22), w=1060, gap=8),
                 sd.col(sd.p('Statistics-limited everywhere beyond ~10 m: flux ∝ 1/L².', 26),
                        sd.p('Closer than 10 m the random two-arm triggers from capture γ bunch inside the macropulses and DREAM goes dead: the beam must be throttled.', 24, sd.MUT),
                        sd.p(f'At equal distance (15 m) 90° beats 15° by ×{g15 / g90:.1f}: more soft neutrons, fewer hard ones.', 24, sd.MUT),
                        sd.p('3.6 µs halves the protons; 1.8 µs already has no frame overlap below ~11 m.', 24, sd.MUT),
                        w=520, gap=24), gap=48),
        short='distance',
        notes=f"""The real paths: 90L at 7–15 m ({sci(R('90L_7m'), 1)} at 7 m, {sci(rho, 1)} at 10 m, {sci(R('90L_15m'), 1)} at 15 m); ICE-II (30R, ~10 m) {sci(R('30R_10m'), 1)}; ICE House (30L, ~20 m) {sci(rho_ice, 1)}; 15L at 22 m {sci(R('15L_22m'), 1)}.

As built, the reach is statistics-limited even at 7 m ({sci(rho7_ab, 1)}): its smaller plastics make fewer trigger legs.

<code>lansce_wnr/out/wnr_scan.csv</code>.""")

# --------------------------------------------------------------------------- #
c3 = c10[c10.bin <= 2]
tot = c3[['X17', 'IPC', 'acc', 'corr', 'cosmic']].sum()
rows = [('IPC (E1)', tot['IPC'], sd.BLUE, 'Born E1 IPC from the cell, same cuts'),
        ('cosmics', tot['cosmic'], sd.GREY, 'LNL L4 cosmic tables; only while the gate is open (2.5 % duty × window)'),
        ('accidentals', tot['acc'], sd.ORANGE, 'two singles in different arms within ±5 ns, NFS pass fraction per bin'),
        ('correlated beam', tot['corr'], sd.RED, 'same-event two-arm events from the beam neutrons (factorised NFS cuts)'),
        ('X17 at ATOMKI', tot['X17'], sd.GREEN, 'X17/IPC = 1.5×10⁻³, E_n ≤ 2.75 MeV')]
hb = sd.hbars([(n, max(v, 0.1), c, f'{n}: {v:,.1f} per day after cuts (0.2-2.75 MeV bins). {tp}') for n, v, c, tp in rows],
              tot.max() * 1.3, width=640, log=True, vmin=0.1, label_w=260, fmt=lambda v: f'{v:,.1f}' if v < 10 else f'{v:,.0f}')
tbl = sd.table(['E_n bin', 'X17', 'IPC', 'cosmics', 'acc.', 'corr.'],
               [[f'{b.E_lo:g}–{b.E_hi:g} MeV', f'{b.X17:.1f}', f'{b.IPC:,.0f}', f'{b.cosmic:,.0f}', f'{b.acc:.1f}', f"{b['corr']:.2f}"]
                for _, b in c3.iterrows()], size=22)
D.slide('budget', sd.title('The background is the IPC itself; the beam adds almost nothing',
                           'events per day after the vertex and E_sum > W/2 cuts, all m_ee, 0.2–2.75 MeV bins; 90L, 10 m, big plastics')
        + sd.row(sd.col(hb, tbl, w=1060, gap=36),
                 sd.col(sd.p('Accidentals and the correlated beam term are ×100 below the IPC: the macropulse duty and the ToF window put the fast neutrons elsewhere in time.', 26),
                        sd.p('Cosmics are as many as the IPC but sit at m_ee ≈ W (back to back): 1-2 % of them fall in 14-19 MeV, against 36 % of the IPC. '
                             f'a veto leaving 10 % gains only {100 * (1 - S(K, "veto 0.1") / rho):.0f} %.', 24, sd.MUT),
                        w=560, gap=24), gap=48),
        short='background budget',
        notes=f"""The fit uses the m_ee histogram in each time-of-flight bin (W known from E_n). X17 at the ATOMKI ratio is {100 * tot['X17'] / tot['IPC']:.1f} % of the IPC after cuts.

Exposure per bin = DREAM live {row.live:.2f} × exp(−2 × Micromegas occupancy). Accidentals: the pairing integral of the singles' time profile over each bin, ×2δ (δ = 5 ns), scaled to the NFS histogram of that bin by the same integral for NFS's own beam (so the NFS vertex + E_sum pass fraction is used).

<code>lansce_wnr/out/wnr_components.csv</code>.""")

# --------------------------------------------------------------------------- #
CMP = sorted([('n_TOF EAR2', d['ear2'], sd.GREY, 'survey_fast.py (duty-limited)'),
              ('GANIL NFS', d['nfs'], sd.GREY, 'Geant4 N1-N4, ganil_nfs'),
              ('ILL PF1B', d['pf1b'], sd.GREY, 'ILL Geant4 walls, best rate'),
              ('ATOMKI ⁴He', C.RHO, sd.GREEN, 'PRC 104 044003'),
              ('FRM II MEDAPP', C.R(d, 'medapp_std'), sd.ORANGE, 'frm2_medapp/ (reactor off since 2020)'),
              ('Birmingham', C.R(d, 'bham_28_2m_pb5'), sd.ORANGE, 'birmingham/ (needs a shielded port)'),
              ('WNR ICE House 30L', rho_ice, sd.RED, 'this note: 20 m'),
              ('WNR 90L, 10 m', rho, sd.RED, 'this note: baseline'),
              ('WNR 90L, 100 Hz', rho100, sd.RED, 'this note: the ×2.5 current upgrade')], key=lambda r: -r[1])
CMP = [(n, v, c, f'{n}: X17/IPC {v:.2g} at 3σ in 50 d. {tp}') for n, v, c, tp in CMP]
D.slide('compare', sd.title(f'Against the other facilities: third, after the two continuous soft sources',
                            'X17/IPC at 3σ in 50 days, E* ≤ 22 MeV, big plastics; shorter bars are better')
        + sd.row(sd.hbars(CMP, 0.2, width=760, log=True, vmin=5e-5, label_w=300, fmt=lambda v: f'{v:.1e}', size=22, h=28),
                 sd.col(sd.p('Same apparatus, same cuts, same fit: only the beam changes.', 26),
                        sd.p('WNR is the only white pulsed source that passes ATOMKI: its micropulses spread the beam over 13 889 bursts a second, and time of flight throws the fast neutrons away.', 24, sd.MUT),
                        sd.p('Unlike MEDAPP (reactor off) and Birmingham (no port), it runs today with a flight path built for TPC-sized detectors.', 24, sd.MUT),
                        w=520, gap=24), gap=48),
        short='comparison',
        notes=f"""Reference rows: ILL PF1B {sci(d['pf1b'], 1)}; GANIL NFS {sci(d['nfs'], 1)}; n_TOF EAR2 {sci(d['ear2'], 1)} (survey_fast.py); FRM II MEDAPP and Birmingham from survey/soft_sim/soft_reach.py. WNR at 100 Hz (×2.5 current, the LANL upgrade): {sci(rho100, 1)}, {C.fmt_days(C.days_to_atomki(rho100))} to ATOMKI.""")

# --------------------------------------------------------------------------- #
srows = [['baseline (90L, 10 m, 1.8 µs)', sci(rho, 1)],
         ['no response above 45 MeV (K_HI = 0)', sci(S(K, '0.0'), 1)],
         ['×10 response above 45 MeV', sci(S(K, '10.0'), 1)],
         ['background shape ±1 % per m_ee bin', sci(S(K, 'delta 0.01'), 1)],
         ['background shape ±2 % per m_ee bin', sci(S(K, 'delta 0.02'), 1)],
         ['cosmic veto leaving 10 %', sci(S(K, 'veto 0.1'), 1)],
         ['100 Hz macropulses (×2.5 current)', sci(rho100, 1)],
         ['as built (16 SiPM bars, 2 × 20 × 30 cm plastics, LS)', sci(rho_ab, 1)]]
D.slide('robust', sd.title('What moves it: the IPC shape, not the beam model',
                           'X17/IPC at 3σ in 50 days, E* ≤ 22 MeV, big plastics unless noted')
        + sd.row(sd.table(['variation', 'reach'], srows, size=24, widths=[760, 200]),
                 sd.col(sd.callout(f'S/B ≈ {100 * tot['X17'] / tot['IPC']:.1f} %: an uncorrelated 2 % shape error per m_ee bin costs '
                                   f'×{S(K, "delta 0.02") / rho:.1f}. The IPC m_ee shape must be known (or fitted from the fast bins).', sd.ORANGE, 26),
                        sd.p('The > 45 MeV neutrons (4 % at 90°) have no Geant4 behind them; scaling their response ×10 moves the reach little, because time of flight puts them outside the window.', 24, sd.MUT),
                        w=640, gap=24), gap=56),
        short='robustness',
        notes="""K_HI: singles, legs, triggers and correlated pairs per neutron above 45 MeV, as a multiple of the 25–45 MeV values (N4). δ: an uncorrelated relative uncertainty on the background in every m_ee bin (nfs_reach.z2_asimov's δ term). <code>lansce_wnr/out/wnr_khi_sensitivity.csv</code>.""")

# --------------------------------------------------------------------------- #
flow = sd.flow([dict(label='90L beam time', sub='"very limited" (2026 call): ask the instrument scientist', color=sd.RED),
                dict(label='room at 7-10 m', sub='~2 × 2 m for the arms, a dump behind', color=sd.ORANGE),
                dict(label='Ø8 cm at the cell', sub='collimator (the fission TPC has one)', color=sd.ORANGE),
                dict(label='micropulse timing', sub='for the ToF trigger gate', color=sd.GREEN),
                dict(label='~3-4 weeks', sub=f'{C.fmt_days(days)} reach ATOMKI; 50 d → ×{C.RHO / rho:.1f}', color=sd.GREEN)], size=22)
D.slide('needs', sd.title('What it would take: time on 90L, room for the arms, the micropulse clock',
                          'in order of what decides it')
        + flow
        + sd.table(['ask LANSCE', 'why it matters'],
                   [['90L: length range, collimators, beam size at 7–10 m, floor space, dump', 'the arms need ~2 × 2 m around the beam'],
                    ['γ flash at 90° per micropulse; is a Pb filter used?', 'it lands in the Micromegas drift just before the window'],
                    ['current in 2027–28 (40 Hz / 100 Hz, the ×2.5 RF upgrade)', f'reach ∝ 1/√current: {sci(rho100, 1)} at 100 Hz'],
                    ['the measured 90° spectrum below 1 MeV', 'Fig. 2 starts at 0.1 MeV and is read by eye'],
                    ['access for an external team with a 30 bar ³He cell and its own DAQ', 'LANL site rules']],
                   size=24, widths=[860, 620], align=['left', 'left']),
        short='what it needs',
        notes="""Contacts (public): LANSCE User Office (505-667-6797, lansce-user-office@lanl.gov); P-3 group leader C. Lee; S. A. Wender, M. Mocko. FACILITY.md §4.""")

# --------------------------------------------------------------------------- #
end = (sd.title('What this does not settle yet', None)
       + sd.row(sd.col(sd.p('<b>Not in the simulation</b>', 30, sd.DINK),
                       sd.p('• The γ flash in the Micromegas (1 µs drift) at the start of the window.', 26, sd.DINK),
                       sd.p('• The flight-path room, the collimator and the dump: re-weighted from the NFS geometry (vacuum tube, no hall).', 26, sd.DINK),
                       sd.p('• Neutrons above 45 MeV: response extrapolated (×0–10 checked).', 26, sd.DINK), gap=18),
                sd.col(sd.p('<b>Facility</b>', 30, sd.DINK),
                       sd.p('• 90L beam time is scarce; the ICE paths are booked by industry.', 26, sd.DINK),
                       sd.p('• The spectrum is digitised by eye from one figure (±10 %).', 26, sd.DINK),
                       sd.p('• X17/IPC for E1 capture at E* 20.6–22 MeV vs ATOMKI’s p + t: the physics question under every neutron number.', 26, sd.DINK), gap=18), gap=80))
D.slide('end', end, dark=True, short='open questions')

out = D.write(O / 'lansce-wnr-x17-feasibility.html',
              note_meta=dict(title='LANSCE WNR X17 feasibility',
                             summary='Could the MX17 apparatus test the ATOMKI ⁴He anomaly on the LANSCE WNR white spallation beam? Flight paths, time structure, and the reach with time of flight.',
                             tags='x17, lansce, wnr, feasibility', date='2026-10-21'),
              footer='Built by x17_facility_search/lansce_wnr/deck/build_deck.py from lansce_wnr/wnr_beam.py outputs.')
print(out)
