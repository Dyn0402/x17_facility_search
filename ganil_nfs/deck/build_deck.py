"""Build the GANIL/NFS X17 feasibility slide note.

Reads ganil_nfs/out/ (nfs_fold.py; sim/nfs_reach.py with --beam none/N3c/N4 and --beam-fact)
and writes ganil_nfs/out/ganil-nfs-x17-feasibility.html:

    python3 ganil_nfs/deck/build_deck.py
    python3 ~/PycharmProjects/dylan-cern-site/scripts/add-note.py \\
        ganil_nfs/out/ganil-nfs-x17-feasibility.html --slug ganil-nfs-x17-feasibility --force --deploy
"""
import os
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, os.path.expanduser(os.environ.get(
    'SLIDEDOC_DIR', '~/PycharmProjects/dylan-cern-site/scripts')))
import slidedoc as sd  # noqa: E402
from slidedoc import term, sci  # noqa: E402

HERE = Path(__file__).resolve().parent
NFS = HERE.parent
O = NFS / 'out'
DAY = 86400.0
RHO = 1.5e-3
KEY = 'rho3_m_ee | E_n'

fold = pd.read_csv(O / 'fold_table.csv')
win = pd.read_csv(O / 'fold_windows.csv').set_index('window')
R = {k: pd.read_csv(O / d / 'reach.csv') for k, d in
     (('none', 'reach_nobeam'), ('direct', 'reach'), ('fact', 'reach_fact'))}
bins = pd.read_csv(O / 'reach_fact' / 'bins.csv')
beam4 = pd.read_csv(O / 'reach' / 'beam.csv').set_index('hw')
beam3 = pd.read_csv(O / 'reach_n3c' / 'beam.csv').set_index('hw')


def rho(kind, hw, window, key=KEY, delta=0.0):
    r = R[kind]
    return float(r[(r.hw == hw) & (r.window == window) & (r.delta == delta)][key].iloc[0])


def f3(v):
    return sci(v, 1) if v < 0.01 else f'{v:.3f}' if v < 0.1 else f'{v:.2f}'


bp_all, bp_low = rho('fact', 'big plastics', '0.2-25'), rho('fact', 'big plastics', '0.2-2.75')
ab_all, ab_low = rho('fact', 'as built', '0.2-25'), rho('fact', 'as built', '0.2-2.75')

D = sd.Deck('GANIL/NFS X17 feasibility',
            'Could the MX17 apparatus test the ATOMKI ⁴He anomaly with fast neutrons at GANIL/SPIRAL-2 NFS? '
            'The spectrum fold, Geant4 signal and IPC, and the beam-induced background from a forced-collision Geant4 run.')

# --------------------------------------------------------------------------- #
# 1 cover
# --------------------------------------------------------------------------- #
cover = (sd.kicker('MX17 at GANIL/NFS · feasibility · 19 Oct 2026')
         + '<h1 style="font-size:62px;font-weight:600;line-height:1.08;letter-spacing:-1.5px">'
           f'NFS falls short of ATOMKI ⁴He: ×{bp_all / RHO:.1f} with every neutron energy, '
           f'×{bp_low / RHO:.0f} below 2.75 MeV, where the physics is</h1>'
         + sd.p('³He(n,e⁺e⁻)⁴He on a 30 bar × 40 cm cell, d(40 MeV)+Be at 50 µA, 14 days, big plastics. '
                'X17/IPC(E1) reached at 3σ, Asimov, with IPC, cosmics and the beam-induced background '
                '(accidentals and correlated) from Geant4.', 30, sd.DMUT)
         + sd.row(
             sd.bignum(sci(bp_all, 1), 'X17/IPC at 3σ, all E_n ≤ 25 MeV', sd.DRED,
                       f'ATOMKI ⁴He: {sci(RHO, 1)}. Assumes X17/IPC constant up to E* ≈ 40 MeV.',
                       tip=f'as built: {sci(ab_all, 1)}; with no beam background {sci(rho("none", "big plastics", "0.2-25"), 1)}'),
             sd.bignum(f'{bp_low:.3f}', 'below 2.75 MeV', sd.DRED,
                       f'{win.loc["0.2-2", "vs_ILL_captures"] * 100:.0f} % of the ILL capture rate below 2 MeV.',
                       tip=f'as built: {ab_low:.2f}'),
             sd.bignum('×7.6', 'beam time per event, forced Geant4', sd.DGREEN,
                       'forced first collision + roulette: weights agree with the tracking to 3×10⁻⁵.'),
             gap=56))
D.slide('cover', cover, dark=True, short='cover',
        notes=f"""Reach = the X17/IPC(E1) ratio a 14-day, 50 µA run detects at 3σ (Asimov over m_ee histograms per E_n bin, E_n tagged event by event by TOF). ATOMKI ⁴He (PRC 104 044003) is 1.5×10⁻³ in these units.

Big plastics: {sci(bp_all, 1)} (all E_n, factorised correlated beam), {sci(rho('direct', 'big plastics', '0.2-25'), 1)} (direct), {sci(rho('none', 'big plastics', '0.2-25'), 1)} (no beam background). As built: {sci(ab_all, 1)} / {sci(rho('direct', 'as built', '0.2-25'), 1)} / {sci(rho('none', 'as built', '0.2-25'), 1)}.

Files: <code>ganil_nfs/FEASIBILITY_SIM.md</code>, <code>ganil_nfs/README.md</code> (beam reference), <code>docs/PLAN_GANIL_NFS.md</code>.""")

# --------------------------------------------------------------------------- #
# 2 the fold
# --------------------------------------------------------------------------- #
f = fold[fold.E_n >= 0.1]
P = sd.Plot(1100, 660, x=(0.1, 40, 'log'), y=(1e3, 3e7, 'log'),
            xlabel='neutron energy E_n [MeV]', ylabel='³He(n,γ) per day per MeV')
P.xticks([(v, f'{v:g}') for v in (0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 40)]).yticks(sd.log_ticks(3, 7))
P.band([0.1, 1.5], [1e3, 1e3], [3e7, 3e7], sd.GREY, 0.08, tip='d+Be spectrum unmeasured below 1.5 MeV')
P.band(list(f.E_n), list(f.cap_low_per_s_MeV * DAY), list(f.cap_per_s_MeV * DAY), sd.BLUE, 0.18,
       tip='band: total model down to its compound part')
P.line(list(f.E_n), list(f.cap_per_s_MeV * DAY), sd.BLUE, markers=False)
P.band([0.2, 2.75], [1e3, 1e3], [3e7, 3e7], sd.GREEN, 0.07, tip='θ_min 99–108°: where the X17 edge separates best')
P.text(0.21, 1.6e7, 'physics window', 21, sd.GREEN)
P.text(0.11, 2.2e3, 'unmeasured', 21, sd.GREY)
side = sd.col(
    sd.table(['E_n [MeV]', 'captures/s', 'θ_min', 'vs ILL'],
             [[w, f'{win.loc[w, "captures_per_s"]:.1f}', f'{win.loc[w, "theta_min_range"]}°',
               f'{win.loc[w, "vs_ILL_captures"]:.2f}'] for w in ('0.2-1', '0.2-2', '2-5', '5-10', '10-20', '0.2-40')],
             size=24),
    sd.p('30 bar × 40 cm ³He, 50 µA, beam solid angle 2.8×10⁻⁵ sr. Lowering E_d does not help: '
         'at 10 MeV deuterons the sub-2 MeV yield drops 10×.', 24, sd.MUT), w=560, gap=24)
D.slide('fold', sd.title('NFS delivers its neutrons at 10–20 MeV; below 2 MeV it gives 5 % of the ILL’s captures',
                         'd(40 MeV)+Be at 0°, folded with σ(n,γ) of ³He (ENDF/B) on the baseline cell')
        + sd.row(P.svg('captures per MeV vs neutron energy'), side, gap=40),
        short='the fold',
        notes="""<code>ganil_nfs/nfs_fold.py</code> → <code>out/fold_table.csv</code>, <code>fold_windows.csv</code>. The current at the low repetition rate we need (440 kHz, so that 0.2 MeV neutrons are not overtaken at 13.6 m) is an open question for GANIL (README §10 Q3).""")

# --------------------------------------------------------------------------- #
# 3 reach vs window
# --------------------------------------------------------------------------- #
P = sd.Plot(1200, 680, x=(0.6, 30, 'log'), y=(1e-3, 3, 'log'),
            xlabel='upper edge of the E_n window [MeV] (lower edge 0.2 MeV)', ylabel='X17/IPC reached at 3σ')
P.xticks([(v, f'{v:g}') for v in (0.75, 1.5, 2.75, 6, 12, 25)]).yticks(sd.log_ticks(-3, 0))
P.band([0.6, 2.75], [1e-3, 1e-3], [3, 3], sd.GREEN, 0.07, tip='physics window')
P.hline(RHO, sd.ORANGE, label='ATOMKI ⁴He 1.5×10⁻³')
for hw, col in (('as built', sd.GREY), ('big plastics', sd.PURPLE)):
    for kind, dash in (('none', '8 6'), ('fact', None)):
        r = R[kind]
        q = r[(r.hw == hw) & (r.delta == 0)]
        xs = [float(w.split('-')[1]) for w in q.window]
        P.line(xs, list(q[KEY]), col, dash=dash, r=5,
               tips=[f'{hw}, {"no beam" if kind == "none" else "with beam"}: 0.2–{x:g} MeV → {sci(v, 2)}'
                     for x, v in zip(xs, q[KEY])])
D.slide('reach', sd.title(f'With all energies big plastics reach {sci(bp_all, 1)}; the beam costs ×{bp_all / rho("none", "big plastics", "0.2-25"):.1f}',
                          '14 days, 50 µA; m_ee fit per TOF-tagged E_n bin (the X17 sits at 16.8 MeV whatever E_n)')
        + P.svg('reach vs energy window')
        + sd.legend([('big plastics, with beam', sd.PURPLE), ('big plastics, no beam', sd.PURPLE, 'dash'),
                     ('as built, with beam', sd.GREY), ('as built, no beam', sd.GREY, 'dash')], size=22),
        short='reach',
        notes=f"""The gain at high E_n assumes X17/IPC constant in E*: ATOMKI measured ⁴He at E* ≈ 20.5–21 MeV only. Above that the capture runs through broad ⁴He levels and nobody knows how the X17 branching evolves.

"With beam" = accidentals + the correlated beam term factorised (two-arm rate × f_vertex × f_E_sum, each event at its own θ and m_ee). The direct estimate (cuts applied event by event, 200 response draws each) gives {sci(rho('direct', 'big plastics', '0.2-25'), 1)} for big plastics; it rests on 1–2 MC events per bin.

TOF tagging gains ×1.5–1.8 over one untagged θ fit ({sci(rho('fact', 'big plastics', '0.2-25', 'rho3_θ, no TOF'), 1)}). A 2 % per-bin shape error moves the tagged reach ≤ 10 %, the untagged one ×1.9.

<code>sim/nfs_reach.py --beam none|N4 [--beam-fact]</code> → <code>out/reach_nobeam/</code>, <code>out/reach/</code>, <code>out/reach_fact/</code>.""")

# --------------------------------------------------------------------------- #
# 4 forced collision method + validation
# --------------------------------------------------------------------------- #
rows = []
for hw in ('as built', 'big plastics'):
    a, b = beam3.loc[hw], beam4.loc[hw]
    rows.append([f'<b>{hw}</b>', 'single-arm legs /s', f'{a.leg_any_per_s:,.0f}', f'{b.leg_any_per_s:,.0f}'])
    rows.append(['', 'two-arm triggers /s', f'{a.trig2_per_s:.1f}', f'{b.trig2_per_s:.1f}'])
    rows.append(['', 'two arms with MM tracks /s', f'{a.ok2_per_s:.1f} ({a.n_ok2_mc:.0f} ev)', f'{b.ok2_per_s:.1f} ({b.n_ok2_mc:.0f} ev)'])
flow = sd.flow([dict(label='trace the line', sub='τ of every volume from Geant4’s own σ', color=sd.BLUE),
                dict(label='pick a volume', sub='∝ e^(−Στ_upstream)(1 − e^(−τ))', color=sd.BLUE),
                dict(label='force the collision', sub='truncated exponential, one history', color=sd.INK),
                dict(label='roulette', sub='0/1-arm histories kept at 5 / 20 %', color=sd.GREEN)], size=22)
D.slide('method', sd.title('A forced first collision gives 7.6× the beam time per event, with weights checked against the tracking',
                           'MX17_Full_Geant branch nfs: --force-beam --roulette 0.2 0.05; 2×10⁸ events ≈ 2.2 s of NFS beam')
        + flow
        + sd.row(sd.table(['', 'per second at 50 µA', 'analog 10⁸ n (0.28 s)', 'forced 10⁸ ev (2.2 s)'], rows, size=24,
                          widths=[220, 380, 300, 300]),
                 sd.col(sd.p('The primary’s weight after the forced collision equals 1 − e^(−τ) to 3×10⁻⁵ on average: '
                             'the generator and the tracking use the same cross sections.', 24),
                        sd.p('Forced runs sit ~3 % low: first collisions in air are not sampled.', 24, sd.MUT),
                        sd.p('Arms are read in time clusters (gap > 50 ns): half the single-arm hits come µs to s late '
                             '(captures, activation).', 24, sd.MUT), w=560, gap=18), gap=48),
        short='method',
        notes="""BeamForceOperator is the forced branch of Geant4's G4BOptrForceCollision without the free-flight clone; the event weight is the total interaction probability along the line, ⟨ΣP⟩ = 0.137. StackingAction holds the primary's secondaries, predicts the arms they reach, and roulettes histories reaching 0 or 1 arm (weight 1/p) — unbiased for coincidences because whole histories are kept or dropped.

All beam two-arm events start in the beam line: Be cell window, Al end cap, Al tube window, ³He gas.

Brute force does not scale: one day of beam is 3×10¹³ neutrons. The correlated term after all cuts therefore rests on a handful of MC events (next slide).""")

# --------------------------------------------------------------------------- #
# 5 backgrounds per bin
# --------------------------------------------------------------------------- #
b = bins[bins.hw == 'big plastics']
P = sd.Plot(1180, 660, x=(0.4, 25, 'log'), y=(0.05, 2e5, 'log'),
            xlabel='E_n bin (TOF-tagged) [MeV]', ylabel='events per day after cuts')
P.xticks([(v, f'{v:g}') for v in b.E_n]).yticks(sd.log_ticks(-1, 5))
ser = [('cosmics (no veto)', 'cosmic_per_day', sd.GREY), ('accidentals', 'acc_per_day', sd.ORANGE),
       ('correlated beam (factorised)', 'beam_per_day', sd.RED), ('IPC', 'IPC_per_day', sd.BLUE),
       ('X17 at ATOMKI ratio', 'X17_per_day', sd.GREEN)]
for name, c, col in ser:
    ys = [v if v > 0 else None for v in b[c]]
    P.line(list(b.E_n), ys, col, r=6, tips=[f'{name}, {e:g} MeV: {v:.3g}/day' if v else '' for e, v in zip(b.E_n, b[c])])
side = sd.col(sd.legend([(n, c) for n, _, c in ser], size=22),
              sd.p('Cosmics sit at θ = 150–180° and accidentals spread over all θ; the correlated beam events '
                   'that pass every cut are back-to-back or collinear.', 24),
              sd.p('A real cosmic veto (arm-to-arm TOF, as at LNL) is not applied yet.', 22, sd.MUT), w=440, gap=24)
D.slide('backgrounds', sd.title('Below 3 MeV accidentals outnumber IPC ×10–100; at 12–25 MeV the correlated beam matches it',
                                'big plastics, 50 µA: vertex (both MM segments within 60 mm of the beam axis) and E_sum > W/2')
        + sd.row(P.svg('backgrounds per E_n bin'), side, gap=36),
        short='backgrounds',
        notes=f"""Accidentals: two single-arm clusters from different neutrons of one bunch within ±5 ns (assumed coincidence window), singles uniform in time inside each E_n bin's TOF window. Built from {beam4.loc['big plastics', 'n_ok2_mc']:.0f} correlated and ~32k single-arm MC clusters (big plastics). They scale linearly with the coincidence window.

Correlated beam: the factorised term weights every TOF-binned two-arm event by f_vertex = {beam4.loc['big plastics', 'f_vertex']:.2f} and f_E_sum = {beam4.loc['big plastics', 'f_esum']:.4f} (pooled, 200 response draws per event). 25 % of the two-arm events have θ in 55–110°, the X17 region.

Low bins are wide in TOF (0.2–0.75 MeV spans 1.1 µs of the 2.27 µs bunch period), so flat-in-time backgrounds (cosmics, delayed singles) pile up there.""")

# --------------------------------------------------------------------------- #
# 6 open
# --------------------------------------------------------------------------- #
end = (sd.title('What this does not settle yet', None)
       + sd.row(sd.col(sd.p('<b>Physics</b>', 30, sd.DINK),
                       sd.p('• X17/IPC at E* = 21–40 MeV is unknown: the whole high-E_n gain rests on it.', 26, sd.DINK),
                       sd.p('• Below 2.75 MeV NFS is ×20 short even before any detector upgrade pays off.', 26, sd.DINK), gap=18),
                sd.col(sd.p('<b>Simulation</b>', 30, sd.DINK),
                       sd.p('• Correlated beam after cuts: a handful of MC events; factorised estimate used.', 26, sd.DINK),
                       sd.p('• Coincidence window (±5 ns) and calorimeter integration time are assumptions.', 26, sd.DINK),
                       sd.p('• No cosmic veto; no γ flash; no beam dump or room in the geometry.', 26, sd.DINK),
                       sd.p('• Ask GANIL: current at 440 kHz.', 26, sd.DINK), gap=18), gap=80))
D.slide('end', end, dark=True, short='open questions')

out = D.write(O / 'ganil-nfs-x17-feasibility.html',
              note_meta=dict(title='GANIL/NFS X17 feasibility',
                             summary='Can fast neutrons at GANIL/NFS test the ATOMKI ⁴He anomaly with the MX17 apparatus? Spectrum fold, Geant4 reach, and the beam background from a forced-collision Geant4 run.',
                             tags='x17, ganil, nfs, feasibility', date='2026-10-19'),
              footer='Built by x17_facility_search/ganil_nfs/deck/build_deck.py from nfs_fold.py and sim/nfs_reach.py outputs.')
print(out)
