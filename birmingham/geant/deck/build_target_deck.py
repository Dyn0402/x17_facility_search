"""Build the Birmingham target / background slide note (TARGET_GEANT.md).

    ~/PycharmProjects/nTof_x17/.venv/bin/python birmingham/geant/deck/build_target_deck.py
    python3 ~/PycharmProjects/dylan-cern-site/scripts/add-note.py birmingham/out/birmingham-target-geant.html \\
        --slug birmingham-target-geant --force --deploy

Reads birmingham/out/targets/target_trade.csv (bham_targets.py) and birmingham/out/geant/*.csv (bham_geant.py,
bham_rates.py).
"""
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.expanduser('~/PycharmProjects/dylan-cern-site/scripts'))
import slidedoc as sd  # noqa: E402
from slidedoc import sci  # noqa: E402

HERE = Path(__file__).resolve().parent
B = HERE.parents[1]
O = B / 'out'
G0 = O / 'geant'                      # the wall as first modelled (20 BPE + 80 concrete + 5 Pb)
G = G0 / 'combo'                      # headline: + 10 cm Pb + 10 cm borated PE on the exit face
tt = pd.read_csv(O / 'targets' / 'target_trade.csv').set_index('key')
re_ = pd.read_csv(G / 'reach.csv')
rmm = pd.read_csv(G / 'mm_penalty' / 'reach.csv') if (G / 'mm_penalty' / 'reach.csv').exists() else None
lg = pd.read_csv(G / 'rates_legs.csv')
ch = pd.read_csv(G / 'rates_channels.csv')
dq = pd.read_csv(G / 'daq_live.csv')
ds = pd.read_csv(G / 'daq_scan.csv')
dc = pd.read_csv(G / 'days_vs_current.csv') if (G / 'days_vs_current.csv').exists() else None
rv = pd.read_csv(G0 / 'room_variants.csv') if (G0 / 'room_variants.csv').exists() else None
wall = pd.read_csv(G0 / 'wall_depth.csv') if (G0 / 'wall_depth.csv').exists() else None
WALLS = {'20 BPE + 80 concrete + 5 Pb (as first modelled)': G0, '+ 10 cm Pb on the exit': G0 / 'leakpb',
         '+ 10 cm Pb + 10 cm borated PE (headline)': G}
TG = ['c30', 'c10', 'cap500', 'bal10', 'bal5']
NAME = {'cap500': 'n_TOF capsule, 500 bar', 'c30': '30 bar cell, R 5 × 40 cm', 'c10': '10 bar cell, R 5 × 40 cm',
        'bal5': '1 bar mylar balloon, R 5 × 40 cm', 'bal10': '1 bar mylar balloon, R 10 × 40 cm'}
COL = {'cap500': sd.MUT, 'c30': sd.BLUE, 'c10': sd.TEAL if hasattr(sd, 'TEAL') else sd.GREEN, 'bal5': sd.ORANGE,
       'bal10': sd.RED}


def R(t, det='bigP', col='days_3sigma_ATOMKI', d=re_):
    q = d[(d.target == t) & (d.det == det)]
    return float(q[col].iloc[0]) if len(q) else np.nan


def L(t, det, src, col='legs_max_arm'):
    q = lg[(lg.target == t) & (lg.det == det) & (lg.source == src)]
    return float(q[col].iloc[0]) if len(q) else 0.0


def CH(t, det, kind, col, src='all'):
    q = ch[(ch.target == t) & (ch.det == det) & (ch.source == src) & (ch.kind == kind)]
    return float(q[col].max()) if len(q) else np.nan


def fd(x):
    if not np.isfinite(x):
        return '—'
    return f'{x:.1f} d' if x < 10 else (f'{x:.0f} d' if x < 1000 else f'{x / 365:.0f} y')


D = sd.Deck('Birmingham: the ³He target and the background, in Geant4',
            'Which ³He target for MX17 at the Birmingham HF-ADNeF ⁷Li(p,n) source, and what the beam, the room and the '
            'shield wall do to the trigger, DREAM, the scintillators and the Micromegas. Geant4 study, 27 Oct 2026.')

c30, cap, b10, b5 = R('c30'), R('cap500'), R('bal10'), R('bal5')
D.slide('cover', sd.kicker('MX17 at Birmingham · target and background · Geant4 · 27 Oct 2026')
        + '<h1 style="font-size:58px;font-weight:600;line-height:1.1;letter-spacing:-1.2px">'
          'No capsule, no balloon: the ³He in the beam sets the rate, and a 1 bar balloon holds ×30 less of it. '
          'What floods the detector is the room and the shield wall, not the target.</h1>'
        + sd.row(
            sd.bignum(fd(c30), '30 bar cell to ATOMKI', sd.DGREEN, f'big plastics, 30 mA; {tt.loc["c30", "he3_L_STP"]:.0f} L of ³He',
                      tip='days of beam to 3σ at X17/IPC = 1.5×10⁻³ (statistics + DREAM live time)'),
            sd.bignum(fd(cap), 'n_TOF capsule', sd.DMUT, f'{tt.loc["cap500", "he3_L_STP"]:.1f} L; its walls convert the ⁸Be γ'),
            sd.bignum(fd(b5), 'balloon R 5 cm', sd.DRED, f'{tt.loc["bal5", "he3_L_STP"]:.1f} L; σ68 as good as the cell'),
            gap=40),
        dark=True, short='cover')

# ---- the target question
rows = []
for t in TG:
    r = tt.loc[t]
    rows.append([NAME[t], f'{r.he3_L_STP:.1f}', f'{r.he3_cost_keur:.0f}', f'{r.beam_r_cm * 2:.0f}',
                 f'{r.captures_per_s:.3g}', f'{r.x_over_X0_pct:.2f} %', f'{r.theta0_10MeV_deg:.1f}°'])
D.slide('trade', sd.title('At a broad fast beam, captures go with the litres of ³He inside it, whatever the pressure',
                          'thin target: captures/s = N(³He in the beam) · φ · ⟨σ_nγ⟩; 2.8 MeV × 30 mA, cell centre 2 m from the Li, no Pb')
        + sd.table(['target', '³He [L STP]', '³He cost [k€]', 'beam Ø [cm]', 'captures/s', 'radial x/X₀', 'θ₀ at 10 MeV/c'], rows,
                   size=24)
        + sd.p('φ = 1.4×10⁸ n/cm²/s at 2 m, ⟨σ_nγ⟩ = 53 µb, ⟨α⟩ = 4.7×10⁻³ pairs per capture. A 1 bar balloon needs ×30 the volume '
               'of the 30 bar cell for the same rate — and a ×30 wider beam through the apparatus. The capsule needs a Ø2 cm beam '
               'but has 1 % X₀ of walls. Nothing from n_TOF is in hand: every option buys its ³He (2.5 k€/L, he4_bag).', 24, sd.MUT),
        short='target trade',
        notes='bham_targets.py → out/targets/target_trade.csv. The Highland angle is for the radial walls + gas a 90° lepton crosses.')

# ---- reach per target
rows = []
for t in TG:
    rows.append([NAME[t], f"{R(t, col='x17_acc'):.3f}", f"{R(t, col='sigma68_deg'):.1f}°", fd(R(t)),
                 sci(R(t, col='rho3_50d'), 1), fd(R(t, 'asb')), fd(R(t, d=rmm)) if rmm is not None else '—'])
D.slide('reach', sd.title('Geant4: the 30 bar cell wins; the balloon matches its resolution but not its rate',
                          'days of 30 mA to 3σ at the ATOMKI strength; MM 15° + TOF, LNL-calibrated calorimetry with beam pile-up, '
                          'θ × |y| × n_down fit, DREAM live time; big plastics unless noted')
        + sd.table(['target', 'X17 acc.', 'σ68', 'days', 'X17/IPC at 3σ, 50 d', 'as built', 'with MM occupancy'], rows, size=24)
        + sd.p('σ68 ≈ 11° for every R 5 cell, balloon included: over a 40 cm gas column the vertex is set by the Micromegas '
               'segments (15°), not by the walls. The capsule (1 % X₀) is at 14°; the wide balloon at 18° (vertex across the beam).',
               24, sd.MUT),
        short='reach')

# ---- the scattered neutrons
D.slide('scatter', sd.title('Every capture comes with ~36 000 neutrons scattered off the ³He itself',
                            'σ_el(³He, 0.5 MeV) ≈ 1.9 b against σ_nγ ≈ 53 µb: the load per X17 is the same for every target design')
        + sd.row(
            sd.card(sd.p('<b>beam through the target region</b>', 28, sd.BLUE)
                    + sd.p(f'30 bar cell, big slab: {sci(CH("c30", "bigP", "plastic", "rate_50keV", "beam"), 1)} /s above 50 keVee '
                           f'(quenched proton recoils); capsule {sci(CH("cap500", "bigP", "plastic", "rate_50keV", "beam"), 1)}, '
                           f'balloon R 5 {sci(CH("bal5", "bigP", "plastic", "rate_50keV", "beam"), 1)}.', 24)),
            sd.card(sd.p('<b>it scales with the captures</b>', 28, sd.ORANGE)
                    + sd.p('Less ³He, less load — and less signal in the same ratio. A balloon buys nothing here; only the '
                           'current (or the distance) trades load against rate.', 24)),
            gap=32),
        short='³He scatter')

# ---- legs by source
rows = []
for t in TG:
    rows.append([NAME[t]] + [f'{L(t, "bigP", s):,.0f}' for s in ('beam', 'room', 'wall', 'cosmic')]
                + [f'{L(t, "bigP", "room", "trig2_corr") + L(t, "bigP", "beam", "trig2_corr") + L(t, "bigP", "wall", "trig2_corr"):,.0f}'])
D.slide('legs', sd.title('The legs come from the room and the wall, not from the target: neutrons returning as capture γ',
                         'legs per second in the busiest arm (SiPM bar ≥ ½ MIP AND back plastic ≥ ½ MIP), big plastics, 30 mA')
        + sd.table(['target', 'beam (target region)', 'room return', 'through the wall', 'cosmic', 'correlated 2-arm /s'], rows, size=24)
        + sd.p('The room term goes with the beam rate (beam area × flux), not with the ³He: the wide balloon (Ø18 cm beam) gets ×5 '
               'the 30 bar cell\'s room load for a fifth of its signal. Neutrons < 1.1 MeV never fire a leg directly: the legs are '
               '2.2 MeV H-capture γ and concrete capture γ.', 24, sd.MUT),
        short='legs')

# ---- DREAM
rows = []
for t in TG:
    for det in ('bigP', 'asb'):
        q = dq[(dq.target == t) & (dq.det == det)]
        if not len(q):
            continue
        q = q.iloc[0]
        P = 'PAIR only' if not np.isfinite(q.P) else f'{q.P:.0f}'
        rows.append([NAME[t], 'big plastics' if det == 'bigP' else 'as built', P, f'{q.pair_trig:,.0f}', f'{q.live:.0%}',
                     f'{q.MB_s_per_feu:.1f}'])
D.slide('dream', sd.title('DREAM: switch off the single-arm output; the pair trigger alone runs at 84–96 % live',
                          'τ = 298 µs non-paralysable; the prescale kept is the smallest with ≥ 95 % live, else the best one')
        + sd.table(['target', 'detector', 'single-arm prescale', 'two-arm triggers /s', 'live', 'MB/s per FEU'], rows, size=22),
        short='DREAM')

# ---- scintillators
rows = []
for t in ('c30', 'cap500', 'bal5', 'bal10'):
    for det, kinds in (('bigP', ('plastic',)), ('asb', ('plastic', 'ls'))):
        for k in kinds:
            rows.append([NAME[t], 'big slab' if det == 'bigP' else ('20×30×2 plastic' if k == 'plastic' else 'LS cell'),
                         sci(CH(t, det, k, 'rate_50keV'), 1), sci(CH(t, det, k, 'rate_thr'), 1),
                         f'{CH(t, det, k, "anode_uA"):.1f}', f'{CH(t, det, k, "pileup_100ns"):.2f}'])
D.slide('scint', sd.title('Scintillators: the big slab takes 5×10⁷ hits/s and 33 µA at gain 10⁶ — run it at 10⁵ with a short gate',
                          'busiest channel, all sources, 30 mA; light quenched (Cecil proton curve); anode current at 10 pe/MeV (plastic), '
                          '150 pe/MeV (LS), gain 10⁶')
        + sd.table(['target', 'channel', '> 50 keVee /s', '> leg threshold /s', 'anode µA', 'hits per 100 ns'], rows, size=21)
        + sd.p('Mostly neutrons leaking through the wall (proton recoils, quenched). Not saturated in the sense of the PMT '
               'physics, but at gain 10⁶ the anode current is in the range where gain drifts; at 10⁵ it is 3 µA. The pile-up '
               'is in the reach (added to each arm\'s calorimetry): it moves the best E_sum cut up to 14 MeV.', 23, sd.MUT),
        short='scintillators')

# ---- Micromegas
rows = []
for t in TG:
    for det in ('bigP', 'asb'):
        q = dq[(dq.target == t) & (dq.det == det)]
        if len(q):
            rows.append([NAME[t], 'big plastics' if det == 'bigP' else 'as built', f'{q.mm_occ.iloc[0]:.0%}'])
D.slide('mm', sd.title('The new risk: neutron recoils in the Micromegas, 0.3–1 cluster per arm per 1.2 µs at 30 mA',
                       'clusters > 2 keV per arm × 1.2 µs; beam, room and wall together; a MIP leaves ~8 keV in the 30 mm gap')
        + sd.row(sd.table(['target', 'detector', 'occupancy per arm'], rows, size=22),
                 sd.col(sd.p('Recoil protons from the isobutane and heavy recoils from argon: short, dense clusters. A charge / '
                             'size cut should remove most; not modelled here. Most come through the wall (3×10⁵ /s per arm). Charged in '
                             'full (e^(−2·occ)), the 30 bar cell needs '
                             f'{fd(R("c30", d=rmm)) if rmm is not None else "—"} instead of {fd(c30)}.', 24),
                        w=640), gap=40),
        short='Micromegas')

if dc is not None:
    rows = []
    for t in ('c30', 'cap500', 'bal5'):
        q = dc[(dc.target == t) & (dc.det == 'bigP')].sort_values('beam_fraction', ascending=False)
        rows.append([NAME[t]] + [fd(v) for v in q.days])
    D.slide('current', sd.title('Running harder still pays: days fall with the current despite pile-up and dead time',
                                'days to 3σ at ATOMKI against the beam current, big plastics')
            + sd.table(['target'] + [f'{30 * s:g} mA' for s in sorted(dc.beam_fraction.unique(), reverse=True)], rows, size=24),
            short='current')

if rv is not None:
    D.slide('room', sd.title('Moving the dump from 2.5 m to 6 m halves the room load on the slab',
                             'room return of the 30 bar cell\'s Ø8 cm beam (R3 vs R4 minus the beam without a room)')
            + sd.table(list(rv.columns), rv.astype(str).values.tolist(), size=22), short='dump')

if wall is not None:
    D.slide('wall', sd.title('The wall works; the collimator leaks',
                             '20 cm borated PE + 80 cm concrete + 5 cm Pb, 4π source 0.4 m in front of it; per source neutron at '
                             'each depth (first crossings at the stage planes)')
            + sd.table(list(wall.columns), wall.astype(str).values.tolist(), size=22)
            + sd.p('At the exit, 70 % of the collided neutrons are within 30 cm of the Ø8 cm bore: the halo scattered in the '
                   'bore walls and the Pb plug, not bulk transmission. The ⁸Be γ that cross the exit plane mostly went round the '
                   'wall through the 50 cm side walls of the model\'s target room (an artefact of the bunker model).', 24, sd.MUT),
            short='wall')

rows = []
for lab, g in WALLS.items():
    if not (g / 'reach.csv').exists():
        continue
    r_ = pd.read_csv(g / 'reach.csv')
    d_ = pd.read_csv(g / 'daq_live.csv')
    q = d_[(d_.target == 'c30') & (d_.det == 'bigP')].iloc[0]
    rows.append([lab, f'{q.legs_max_arm:,.0f}', f'{q.pair_trig:,.0f}', f'{q.live:.0%}', f'{q.mm_occ:.2f}',
                 fd(R('c30', d=r_))])
D.slide('walls', sd.title('The wall decides: 5 cm of Pb on the exit is not enough; +10 cm Pb and +10 cm borated PE recover it',
                          '30 bar cell, big plastics, 30 mA; legs in the busiest arm from all sources; DREAM pair trigger only')
        + sd.table(['shield wall', 'legs /s', 'two-arm triggers /s', 'DREAM live', 'MM occupancy', 'days to ATOMKI'], rows, size=23)
        + sd.p('Pb kills the capture γ of the concrete (hard: 60 % above 1.5 MeV, lines up to 10 MeV): legs ×33 down. Borated '
               'PE kills the slow neutrons that make capture γ inside the detector: legs ×9 down. The two exit layers were '
               'simulated one at a time from the same exit phase space; the headline combines them (photons behind the Pb, '
               'neutrons behind the PE), an estimate.', 24, sd.MUT),
        short='wall options')

D.slide('next', sd.title('What to do with this', None)
        + sd.p('1. Target: the 30 bar Be/CFRP cell (or as much ³He as the budget allows, as dense as walls permit). The balloon '
               'and the capsule are both worse per euro of ³He; the capsule is not available anyway.', 26)
        + sd.p('2. Beam dump far away and lined (⁶Li / borated PE), the experimental room lined; the dump decides the trigger load.', 26)
        + sd.p('3. A stepped collimator with a borated / ⁶Li liner instead of a straight Ø8 cm bore.', 26)
        + sd.p('4. Pair trigger only on DREAM; cosmic calibration in separate runs.', 26)
        + sd.p('5. Bench test: MM cluster cut against neutron recoils (AmBe or a D-D source).', 26)
        + sd.p('6. Ask Birmingham: room layout, wall thickness, where a dump could go.', 26),
        short='next')

out = O / 'birmingham-target-geant.html'
D.write(out)
print(out)
