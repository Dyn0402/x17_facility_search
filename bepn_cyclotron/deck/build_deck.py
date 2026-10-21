"""Build the cyclotron ⁹Be(p,n) (NPI Řež TR-24) X17 feasibility slide note.

Reads bepn_cyclotron/out/ (bepn_beam.py, bepn_reach.py) and survey/soft_sim/out/ (the MEDAPP and
Birmingham rows for comparison), writes bepn_cyclotron/out/bepn-cyclotron-x17-feasibility.html:

    ~/PycharmProjects/nTof_x17/.venv/bin/python bepn_cyclotron/deck/build_deck.py
    python3 ~/PycharmProjects/dylan-cern-site/scripts/add-note.py \\
        bepn_cyclotron/out/bepn-cyclotron-x17-feasibility.html --slug bepn-cyclotron-x17-feasibility --force --deploy
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(ROOT / 'survey' / 'soft_sim'))
import deck_common as C  # noqa: E402
from deck_common import sd, sci  # noqa: E402
import cartoon  # noqa: E402
import bepn_beam as BB  # noqa: E402

O = HERE.parent / 'out'
C.SITES['NPI Řež'] = (50.18, 14.36)
d = C.load()
r_b = pd.read_csv(O / 'bepn_reach.csv').assign(site='bepn')
d['reach'] = pd.concat([d['reach'], r_b], ignore_index=True)
d['comp'] = pd.concat([d['comp'], pd.read_csv(O / 'bepn_components.csv')], ignore_index=True)
d['thr'] = pd.concat([d['thr'], pd.read_csv(O / 'bepn_throttle.csv')], ignore_index=True)
tau4 = pd.read_csv(HERE.parent / 'out_tau4' / 'bepn_reach.csv')

K = 'npi18_0_2m'                     # baseline: TR-24 at 18 MeV, cell 2 m downstream at 0°
rho = C.R(d, K)
rho_ab = C.R(d, K, hw='as built')
rho_all = C.R(d, K, signal='all E*')
floor = C.R(d, K, col='rho3_floor')
thr = C.R(d, K, col='throttle')
live = C.R(d, K, col='live')
days = C.days_to_atomki(rho)
rho14 = C.R(d, K, days=14)
rho_bham = C.R(d, 'bham_28_2m_pb5')
rho_med = C.R(d, 'medapp_std')
rho_kur = C.R(d, 'kur30_130_2m')
rho_u120 = C.R(d, 'u120_0_3m')
rho_tau4 = float(tau4[(tau4.key == K) & (tau4.signal == 'E* ≤ 22 MeV')].rho3.iloc[0])
ok_arm = C.Cp(d, K, 'ok_singles_per_arm')
legs = C.Cp(d, K, 'legs_per_arm')
ncell = C.Cp(d, K, 'n_cell')
beam = pd.read_csv(O / 'bepn_beam.csv')
b0 = beam[(beam.key == 'npi18') & (beam.theta == 0) & (beam.dist_m == 2)].iloc[0]
anch = pd.read_csv(O / 'bepn_anchors.csv')
shield = pd.read_csv(O / 'bepn_shield.csv')
sh = shield[shield.key == K]
sv = d['survey']
old_lo = float(sv[(sv.key == 'bepn') & (sv.singles_model == 'geant')].rho3.iloc[0])
old_hi = float(sv[(sv.key == 'bepn') & (sv.singles_model == 'flat')].rho3.iloc[0])
f_hi = 1 - b0.f_below_2p75

D = sd.Deck('Cyclotron ⁹Be(p,n) at NPI Řež: X17 feasibility',
            'Could the MX17 apparatus test the ATOMKI ⁴He anomaly at a cyclotron-driven beryllium neutron source? '
            'The candidates, NPI Řež’s TR-24 converter, the ENDF-based beam model and the reach with its own Geant4 background.')

# --------------------------------------------------------------------------- #
cover = (sd.kicker('MX17 on a cyclotron Be(p,n) source · NPI Řež TR-24 · feasibility · 21 Oct 2026')
         + '<h1 style="font-size:60px;font-weight:600;line-height:1.08;letter-spacing:-1.5px">'
           f'A 0.3 mA cyclotron on beryllium passes ATOMKI ⁴He ×{C.RHO / rho:.1f} in 50 days, '
           f'but its fast neutrons spend the DAQ: Birmingham does ×{rho / rho_bham:.1f} better</h1>'
         + sd.p('³He(n,e⁺e⁻)⁴He on the 30 bar × 40 cm cell 2 m downstream of the TR-24 Be converter, 18 MeV protons, '
                'Ø8 cm collimator, big plastics. X17/IPC reached at 3σ with IPC, cosmics and the beam’s own Geant4 '
                'background (neutrons and target γ).', 30, sd.DMUT)
         + sd.row(
             sd.bignum(sci(rho, 1), 'X17/IPC at 3σ in 50 days', sd.DGREEN,
                       f'ATOMKI ⁴He: 1.5×10⁻³. As built: {sci(rho_ab, 1)}.',
                       tip=f'survey bracket before this study (30 MeV, 1 mA, 1 m): {sci(old_lo, 1)} – {sci(old_hi, 1)}'),
             sd.bignum(C.fmt_days(days), 'of beam to reach the ATOMKI strength', sd.DGREEN,
                       f'beam throttled to {thr:.2f} of 0.3 mA; DREAM live {live:.2f}'),
             sd.bignum(f'{100 * f_hi:.0f} %', 'of the neutrons above the ATOMKI window', sd.DRED,
                       'they fire the trigger plastics but bring no window signal'),
             gap=56))
D.slide('cover', cover, dark=True, short='cover',
        notes=f"""Reach = the X17/IPC(E1) ratio a 50-day run detects at 3σ (Asimov over the θ histogram summed over E_n: a DC beam has no TOF tag). X17 counted only from E_n ≤ 2.75 MeV (E* ≤ 22 MeV, ATOMKI-like); counted at every E*, the NFS convention: {sci(rho_all, 1)}. 14 days: {sci(rho14, 1)}.

The model's beam: ENDF/B-VIII.0 p + ⁹Be (LA150) through a Bethe slowing-down, checked against two published yields to 1 %.

Files: <code>bepn_cyclotron/FEASIBILITY.md</code>, <code>FACILITY.md</code>, <code>bepn_beam.py</code>, <code>bepn_reach.py</code>.""")

# --------------------------------------------------------------------------- #
facts = sd.col(
    sd.card(sd.p('<b>NPI CAS, Řež</b> (near Prague, CZ)', 28)
            + sd.p('Laboratory of Fast Neutron Generators: fast-neutron data for IFMIF-DONES, ITER, DEMO. Open access via CANAM.', 24, sd.MUT)),
    sd.card(sd.p('<b>TR-24: 18–24 MeV, 300 µA on a bare Be disk</b>', 28)
            + sd.p('High-power converter, 7.2 kW, forward-open: 2×10¹³ n/s at 18 MeV. U-120M (≤ 37 MeV, 35 µA) has a collimated beam today.', 24, sd.MUT)),
    sd.card(sd.p('<b>Status: converter (ask)</b>', 28, sd.ORANGE)
            + sd.p('“Not operational yet” in 2019; prototype tested at 24 MeV in 2020. The BNCT HM-30s (30 MeV, 1 mA, Japan) are all moderated.', 24, sd.MUT)),
    w=700, gap=24)
D.slide('where', sd.title('NPI Řež: the one bare, open-access Be converter at high current',
                          'the facilities this study compares; hover the dots and dotted terms for details')
        + sd.row(C.europe_map(880, 660, 'NPI Řež', labels={'NPI Řež': (16, -10, 'start')}), facts, gap=56),
        short='where',
        notes="""Candidates (FACILITY.md §1): Sumitomo HM-30 BNCT cyclotrons (KURNS C-BENS, Southern Tohoku, Kansai BNCT) give 30 MeV at 1 mA but bury the Be in a Pb/Fe/Al/CaF₂ moderator for epithermal beams; KURNS plans to open C-BENS to fundamental research after KUR's shutdown (May 2026), so a fast port is worth asking about. Atomki's MGC-20E and TENMAK's 30 MeV cyclotron are µA-class.

NPI: TR-24 (ACSI, commissioned 2015) and U-120M (K = 40). Contacts (public): M. Majerle, M. Štefánik (fast neutron generators), J. Štursa (cyclotrons).""")

# --------------------------------------------------------------------------- #
cards = sd.row(
    sd.card(sd.p(f'<b>{b0.n_tot:.1e} n/s</b>'.replace('e+13', '×10¹³'), 34, sd.BLUE)
            + sd.p('at 18 MeV, 0.3 mA (3.9×10¹³ at 24 MeV)', 22, sd.MUT)),
    sd.card(sd.p(f'<b>≤ {b0.E_max:.1f} MeV</b>', 34, sd.BLUE)
            + sd.p(f'mean {b0.mean_En:.1f} MeV at 0°, forward ×{b0.forward_gain:.1f}', 22, sd.MUT)),
    sd.card(sd.p('<b>γ: lines ≤ 7 MeV</b>', 34, sd.ORANGE)
            + sd.p('3×10⁻⁴ γ/p: < 0.2 % of the singles', 22, sd.MUT)),
    sd.card(sd.p('<b>no port at TR-24</b>', 34, sd.RED) + sd.p('U-120M has one, at 1/10 the current', 22, sd.MUT)),
    gap=24)
D.slide('beamline', sd.title('A Be disk in the TR-24 vault; the X17 station needs a port through the wall',
                             'top view, not to scale; dashed green = what the X17 set-up adds (port + collimator, tubes, dump)')
        + cartoon.beamline(1664, 500, f'{ncell:.1e}/s'.replace('e+09', '×10⁹')) + cards,
        short='beamline',
        notes=f"""TR-24: H⁻ multi-cusp source, stripping-foil extraction (energy set by the foil radius), two simultaneous beams; output 2 runs through a beamline and switching magnet to three target positions. High-power Be converter (CANAM): static Be disk 4 mm × Ø40 mm, ≤ 7.2 kW (0.9–3.5 kW/cm²), submerged-jet cooling, samples 20 mm from the target, ~2–3×10¹² n/cm²/s on axis.

Through a Ø8 cm collimator 2 m downstream at 0°, 18 MeV, 0.3 mA: {b0.n_cell:.2g} n/s (bepn_beam.py).

The U-120M thick-Be station already has the X17 geometry: a collimator in movable shielding doors (Ø3–25 cm), the beam into the adjacent hall, a 15 m flight path to a dump. At 35 µA of 18 MeV H⁻/p and the cell at 3 m: {sci(rho_u120, 1)}.""")

# --------------------------------------------------------------------------- #
e = np.geomspace(0.01, 40, 700)
fold = pd.read_csv(ROOT / 'ganil_nfs' / 'out' / 'fold_table.csv')
nfs = np.interp(e, fold.E_n, fold.n_per_s_MeV, left=0, right=0)
nfs = nfs / np.trapezoid(nfs, e)
import bham_beam as BHB  # noqa: E402
curves = [('NPI TR-24, 18 MeV, 0° (baseline)', BB.spectrum_on_grid(18.0, 0.0, e), sd.RED, None),
          ('NPI TR-24, 24 MeV, 130°', BB.spectrum_on_grid(24.0, 130.0, e), sd.ORANGE, None),
          ('HM-30, 30 MeV, 0°', BB.spectrum_on_grid(30.0, 0.0, e), sd.PURPLE, '8 6'),
          ('Birmingham ⁷Li(p,n), 2.8 MeV', BHB.spectrum_on_grid(2.8, e), sd.BLUE, None),
          ('GANIL NFS d(40)+Be', nfs, sd.GREY, None)]
P = sd.Plot(1100, 600, x=(0.01, 40, 'log'), y=(0, 1.0, 'lin'), xlabel='neutron energy E_n [MeV]', ylabel='E dN/dE (peak = 1)')
P.xticks([(v, f'{v:g}') for v in (0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30)]).yticks([(v, f'{v:g}') for v in (0, .25, .5, .75, 1)])
P.band([0.2, 2.75], [0, 0], [1.0, 1.0], sd.GREEN, 0.08, tip='E_n 0.2-2.75 MeV: E* ≤ 22.1 MeV, θ_min ≥ 99°: the ATOMKI-like window')
P.text(0.21, 0.95, 'ATOMKI-like window', 22, sd.GREEN)
fr = {}
_le = np.log(e)
_k = np.exp(-0.5 * ((_le[:, None] - _le[None, :]) / 0.12) ** 2)
_k /= _k.sum(1, keepdims=True)
for name, f, col, dash in curves:
    y = _k @ (e * f) if name.startswith(('NPI', 'HM-30')) else e * f   # display only: σ = 0.12 in ln E over the MT 5 peaks
    fr[name] = float(np.trapezoid(f[e <= 2.75], e[e <= 2.75]))
    P.line(list(e), list(y / y.max()), col, dash=dash, markers=False, w=4 if col == sd.RED else 3,
           tip=f'{name}: {100 * fr[name]:.0f} % of the neutrons below 2.75 MeV')
leg = sd.legend([(n, c, 'dash' if dsh else 'line') for n, _, c, dsh in curves], size=22)
D.slide('spectrum', sd.title(f'Only {100 * b0.f_below_2p75:.0f} % of the neutrons are in the window, at any angle or energy',
                             'normalised E dN/dE (Be curves smoothed by 12 % in E for display); thick Be from ENDF/B-VIII.0 (LA150) + Bethe slowing-down; shaded: E_n ≤ 2.75 MeV')
        + sd.row(P.svg('neutron spectra'),
                 sd.col(leg, sd.p('The soft half is evaporation and ⁹Be break-up, nearly isotropic. The hard half is the (p,n) continuum: '
                                  'forward-peaked, but its 3–10 MeV bulk is there at 130° too.', 24),
                        sd.p('18 MeV removes everything above 16 MeV, which is what makes the correlated background.', 24, sd.MUT),
                        w=480, gap=22), gap=40),
        short='spectrum',
        notes=f"""Anchors (out/bepn_anchors.csv): {'; '.join(f"{a.E_p:g} MeV {a.quantity}: model/reference {a.ratio:.2f}" for a in anch.itertuples())}. NPI's "5×10¹² n/s/sr forward" at 24 MeV, 0.3 mA matches the model at 30–40°, not at 0°.

The peaks at ~1.5 and ~6 MeV are the evaluation's MT 5 tables (sequential decay through ⁹B/⁸Be states); measured thick-target spectra (Brede 1989; NPI TOF, Majerle 2023) are smoother. The fractions above and below 2.75 MeV are what matter, and they move little.

Below 2.75 MeV: {', '.join(f'{n} {100 * v:.0f} %' for n, v in fr.items())}.""")

# --------------------------------------------------------------------------- #
sp, sleg = C.singles_plot(d, 1120, 600)
D.slide('singles', sd.title('Geant4: above ~2 MeV every neutron can fire a leg, and DREAM pays for it',
                            'MX17_Full_Geant branch soft, NFS cell and arms, big plastics: forced-collision neutrons (N5, NFS N4 above 20 MeV) and photons (G5/G6)')
        + sd.row(sp, sd.col(sleg, sd.p('A single = a trigger leg (SiPM + back plastic) with a Micromegas segment in the active area.', 24),
                            sd.p(f'Here, at full current: {ok_arm:,.0f} singles and <b>{legs:,.0f} legs</b> per arm per second.', 26, sd.RED),
                            sd.p(f'Random two-arm triggers ~10⁴/s; at the best throttle ({thr:.2f}) DREAM is live {live:.2f}.', 24, sd.MUT),
                            w=480, gap=22), gap=40),
        short='Geant4 singles',
        notes="""Legs need half a MIP (1.7 MeV) in the back plastic; proton recoils from fast neutrons give them freely, most without a Micromegas segment (legs/singles ≈ 30 here, against ≈ 7 at Birmingham).

Above 20 MeV (24 MeV at θ < 45°, the HM-30) the NFS forced run N4 is used; it has no leg tables, so its legs are its singles × 10.3 (N5's leg/single ratio at 10–20 MeV). At 18 MeV nothing is above 16.3 MeV and N5 alone carries the result.""")

# --------------------------------------------------------------------------- #
tp, tleg = C.throttle_plot(d, 1060, 600, [(K, sd.RED, 'NPI 18 MeV, 0° (baseline)', None),
                                          ('npi24_130_2m', sd.ORANGE, 'NPI 24 MeV, 130°', None),
                                          ('npi24_0_2m', sd.ORANGE, 'NPI 24 MeV, 0°', '8 6'),
                                          ('kur30_130_2m', sd.PURPLE, 'HM-30 1 mA, 130°', None),
                                          ('bham_28_2m_pb5', sd.BLUE, 'Birmingham (baseline)', '8 6')], refs=False)
D.slide('throttle', sd.title('More beam stops helping at ~2×10⁹ n/s on the cell: the DAQ, not the source, sets the reach',
                             'reach vs neutrons through the cell, beam throttled; 50 days, E* ≤ 22 MeV, big plastics, cell 2 m from the target')
        + sd.row(sd.col(tp, tleg, w=1060, gap=8),
                 sd.col(sd.p('At 24 MeV, 0° and on the 30 MeV HM-30 the > 16 MeV tail adds correlated two-arm events (as at NFS): throttled ×6–40.', 24),
                        sd.p(f'A 4× faster DAQ (5 samples): baseline {sci(rho_tau4, 1)} at full current.', 26, sd.GREEN),
                        sd.p('A bigger machine does not help: the HM-30’s current goes into its tail.', 24, sd.MUT),
                        w=540, gap=24), gap=48),
        short='rate and throttle',
        notes=f"""Best 50-day reach per configuration (big plastics, E* ≤ 22): NPI 18 MeV 0° {sci(rho, 2)}; 18 MeV 130° {sci(C.R(d, 'npi18_130_2m'), 2)}; 24 MeV 130° {sci(C.R(d, 'npi24_130_2m'), 2)}; 24 MeV 0° {sci(C.R(d, 'npi24_0_2m'), 2)}; HM-30 130° {sci(rho_kur, 2)}; HM-30 0° {sci(C.R(d, 'kur30_0_2m'), 2)}; U-120M 35 µA, 3 m {sci(rho_u120, 2)}.

The DAQ variant (τ/4) is <code>bepn_reach.py --tau-scale 0.25 --tag tau4</code> → <code>out_tau4/</code>.""")

# --------------------------------------------------------------------------- #
hb, q = C.budget_bars(d, K, 700)
D.slide('budget', sd.title('At the best rate the background is IPC, cosmics and some accidentals',
                           'events per day in θ = 100–150° after the vertex and E_sum > W/2 cuts; baseline (18 MeV, 0°, 2 m), big plastics')
        + sd.row(sd.col(hb, C.rate_table(d, K), w=1000, gap=36),
                 sd.col(sd.p(f'X17 at the ATOMKI ratio is {100 * q.X17_win_per_day / q.IPC_win_per_day:.1f} % of the IPC in the window '
                             f'(Birmingham 1.9 %): half the IPC comes from E* > 22 MeV.', 26),
                        sd.p(f'Statistics-only floor (live 1, no beam background): {sci(floor, 1)}.', 24, sd.MUT),
                        sd.p('No correlated beam term at 18 MeV: the neutrons that make it (> 16 MeV) are absent.', 24, sd.MUT),
                        w=560, gap=24), gap=48),
        short='background budget',
        notes="""Window counts are for orientation; the reach uses the whole θ histogram. Accidentals: two singles from different particles within ±5 ns, from the source's own Geant4 singles, through the reconstruction. Correlated: same-event two-arm events, factorised.""")

# --------------------------------------------------------------------------- #
n_arm = float(sh.n_arm_unshielded.iloc[0])
ok_target = 0.1 * ok_arm
PS = sd.Plot(760, 520, x=(0, 220, 'lin'), y=(1, 1e9, 'log'), xlabel='shield between the Be and the arms [cm]',
             ylabel='leakage singles per arm [/s]')
PS.xticks([(v, f'{v:g}') for v in (0, 50, 100, 150, 200)]).yticks(sd.log_ticks(0, 9))
PS.hline(ok_target, sd.GREEN, label='10 % of the beam’s own singles', anchor='start')
for eps, tvl, col, dash in ((1e-4, 20, sd.BLUE, None), (1e-3, 20, sd.RED, None), (1e-4, 35, sd.BLUE, '8 6'), (1e-3, 35, sd.RED, '8 6')):
    xs = list(range(0, 221, 10))
    ys = [n_arm * eps * 10 ** (-x / tvl) for x in xs]
    PS.line(xs, [y if y >= 1 else None for y in ys], col, dash=dash, markers=False, w=4,
            tip=f'{sci(eps, 0)} singles per entering n, TVL {tvl} cm')
shield_leg = sd.legend([('10⁻⁴ singles per entering n', sd.BLUE), ('10⁻³', sd.RED),
                        ('solid: BPE + Fe (TVL 20 cm)', sd.GREY), ('dashed: concrete (TVL 35 cm)', sd.GREY, 'dash')], size=20)
rows = [[sci(r.eps, 0), f'{r.tvl_cm:.0f} cm', sci(r.T_needed, 1), f'{r.thickness_cm:.0f} cm'] for r in sh.itertuples()]
D.slide('shield', sd.title('The fast 4π field needs a wall between rooms: ~1 m of BPE + Fe or ~2 m of concrete',
                           'an estimate, not Geant4: what keeps the leakage singles below 10 % of the beam’s own')
        + sd.row(sd.col(PS.svg('leakage singles vs shield'), shield_leg, w=760, gap=8),
                 sd.col(sd.p(f'With no wall, one arm 2 m away sees <b>{sci(n_arm, 1)}</b> n/s, ×{n_arm / ncell:.0f} what goes through the cell.', 28),
                        sd.table(['singles / entering n', 'TVL', 'transmission', 'thickness'], rows, size=22, widths=[260, 120, 200, 160]),
                        sd.callout('Samples sit 20 mm from the Be today. MX17 must sit beyond the vault wall.', sd.RED, 26),
                        sd.callout('U-120M already has this: a collimator through movable shielding into the next hall.', sd.GREEN, 24),
                        w=820, gap=24), gap=56),
        short='shield',
        notes=f"""Unshielded: the 0° yield {b0.n_per_sr:.2g} n/s/sr at 18 MeV, 0.3 mA, over (200 cm)², through one arm's 75 × 75 cm face.

Singles per neutron entering an arm are not simulated: 1–20 MeV neutrons make legs, so 10⁻⁴–10⁻³ (Birmingham used 10⁻⁶–10⁻⁴ for sub-MeV neutrons). Tenth-value layers are stand-ins (NCRP 144: ~40 cm concrete at 20–30 MeV). <code>bepn_beam.shield()</code> → <code>out/bepn_shield.csv</code>.""")

# --------------------------------------------------------------------------- #
D.slide('compare', sd.title(f'Against the other facilities: a pass, but ×{rho / rho_bham:.1f} behind Birmingham',
                            'X17/IPC at 3σ in 50 days, E* ≤ 22 MeV, big plastics; shorter bars are better')
        + sd.row(C.compare_bars(d, [('medapp_std', 'FRM II MEDAPP', sd.ORANGE, 'frm2_medapp/ (reactor off)'),
                                    ('bham_28_2m_pb5', 'Birmingham', sd.BLUE, 'birmingham/ (no port yet)'),
                                    (K, 'NPI TR-24 18 MeV', sd.RED, 'this note (baseline)'),
                                    ('kur30_130_2m', 'HM-30 30 MeV 1 mA', sd.PURPLE, 'this note: 130°, fast port (ask)'),
                                    ('u120_0_3m', 'NPI U-120M 35 µA', sd.RED, 'this note: existing collimated beam')], 800),
                 sd.col(sd.p('Same apparatus, cuts and fit: only the beam changes.', 26),
                        sd.p('The ranking is the spectrum: fission (MEDAPP) and ⁷Li(p,n) (Birmingham) put most neutrons in the window; '
                             'Be(p,n) puts 40 % there and the rest into the trigger.', 24, sd.MUT), w=520, gap=24), gap=48),
        short='comparison',
        notes=f"""Reference rows: ILL PF1B {sci(d['pf1b'], 1)}; GANIL NFS {sci(d['nfs'], 1)}; n_TOF EAR2 {sci(d['ear2'], 1)} (survey). MEDAPP {sci(rho_med, 1)} and Birmingham {sci(rho_bham, 1)} from survey/soft_sim.

As built (16 SiPM bars, 2 × 20 × 30 cm plastics, LS): {sci(rho_ab, 1)}.""")

# --------------------------------------------------------------------------- #
flow = sd.flow([dict(label='a port through the wall', sub='~1–2 m concrete-equiv., Ø8 cm collimator', color=sd.RED),
                dict(label='the converter at 0.2–0.3 mA', sub='status in 2026: ask', color=sd.ORANGE),
                dict(label='18 MeV protons', sub='the TR-24 minimum; softest spectrum', color=sd.GREEN),
                dict(label='room for the arms', sub='2 m downstream, ~2 × 2 m', color=sd.ORANGE),
                dict(label='~2–3 weeks of beam', sub='CANAM / EU transnational access', color=sd.GREEN)], size=22)
D.slide('needs', sd.title('What it would take: a port, a working converter, a few weeks of 18 MeV protons',
                          'in order of what decides it')
        + flow
        + sd.table(['ask NPI', 'why it matters'],
                   [['is the high-power Be converter operating, at what current, at 18 MeV?', 'the reach needs ~0.2 mA'],
                    ['a collimated port through the TR-24 vault wall, and the room beyond it?', 'the arms cannot sit in the 4π field'],
                    ['U-120M: H⁻ current at 18–20 MeV on the thick-Be station with the collimator', f'works today: {sci(rho_u120, 1)}'],
                    ['their measured TOF spectra (Majerle et al. 2023)', 'replace the LA150 model'],
                    ['beam time for an external collaboration (CANAM, EURO-LABS/RADNEXT)', f'{C.fmt_days(days)} of beam reach ATOMKI at 3σ']],
                   size=24, widths=[900, 560], align=['left', 'left']),
        short='what it needs',
        notes="""Contacts (public): M. Majerle, M. Štefánik (Laboratory of Fast Neutron Generators), J. Štursa (cyclotrons); FACILITY.md §5. KURNS (H. Tanaka): is there any way to run C-BENS with the moderator removed?""")

# --------------------------------------------------------------------------- #
end = (sd.title('What this does not settle yet', None)
       + sd.row(sd.col(sd.p('<b>Not in the simulation</b>', 30, sd.DINK),
                       sd.p('• The wall, the room, the target backing and cooling water (a moderated component).', 26, sd.DINK),
                       sd.p('• The spectrum is the LA150 evaluation, checked on two integrals only.', 26, sd.DINK),
                       sd.p('• A higher leg threshold (2.5–3 MeV) would cut the recoil legs: not run.', 26, sd.DINK), gap=18),
                sd.col(sd.p('<b>Facility</b>', 30, sd.DINK),
                       sd.p('• The TR-24 converter’s status and a port are unknown.', 26, sd.DINK),
                       sd.p('• No BNCT cyclotron has a fast port.', 26, sd.DINK),
                       sd.p('• Birmingham and MEDAPP reach further with softer beams.', 26, sd.DINK), gap=18), gap=80))
D.slide('end', end, dark=True, short='open questions')

out = D.write(O / 'bepn-cyclotron-x17-feasibility.html',
              note_meta=dict(title='Cyclotron Be(p,n) (NPI Řež) X17 feasibility',
                             summary='Could the MX17 apparatus test the ATOMKI ⁴He anomaly at a cyclotron Be(p,n) source? Candidates, NPI Řež TR-24, an ENDF-based thick-Be model, Geant4 background and the reach.',
                             tags='x17, npi, rez, cyclotron, feasibility', date='2026-10-21'),
              footer='Built by x17_facility_search/bepn_cyclotron/deck/build_deck.py from bepn_beam.py and bepn_reach.py outputs.')
print(out)
