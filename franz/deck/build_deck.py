"""Build the FRANZ X17 feasibility slide note.

Reads franz/out/ (franz_beam.py) and survey/soft_sim/out/ (for the comparison rows), writes
franz/out/franz-x17-feasibility.html:

    ~/PycharmProjects/nTof_x17/.venv/bin/python franz/deck/build_deck.py
    python3 ~/PycharmProjects/dylan-cern-site/scripts/add-note.py \\
        franz/out/franz-x17-feasibility.html --slug franz-x17-feasibility --force --deploy
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'survey' / 'soft_sim'))
sys.path.insert(0, str(ROOT / 'franz'))
sys.path.insert(0, str(ROOT / 'survey'))
import deck_common as C  # noqa: E402
from deck_common import sd, sci  # noqa: E402
import cartoon  # noqa: E402
import franz_beam as FB  # noqa: E402

O = HERE.parent / 'out'
C.SITES['FRANZ Frankfurt'] = (50.172, 8.630)
d = C.load()
r = pd.read_csv(O / 'franz_reach.csv')
cp = pd.read_csv(O / 'franz_components.csv')
beam = pd.read_csv(O / 'franz_beam.csv')
shield = pd.read_csv(O / 'franz_shield.csv')
K = 'franz_2000_thin_pb0'


def R(key=K, scen='design', dist=0.5, hw=C.HW, days=50, col='rho3'):
    q = r[(r.key == key) & (r.scen == scen) & (r.dist_m == dist) & (r.hw == hw) & (r.days == days)]
    return float(q[col].iloc[0])


def Cp(col, key=K, scen='design', dist=0.5, hw=C.HW):
    return float(cp[(cp.key == key) & (cp.scen == scen) & (cp.dist_m == dist) & (cp.hw == hw)][col].iloc[0])


rho = R()
rho_ab = R(hw='as built')
rho_lic = R(scen='licence')
rho_lic22 = R('franz_2200_thin_pb0', 'licence')
rho_first = R(scen='first')
rho_1m = R(dist=1.0)
rho_thick = R('franz_2000_thick_pb0')
floor = R(col='rho3_floor')
days = C.days_to_atomki(rho)
ok_arm, legs, ncell = Cp('ok_singles_per_arm'), Cp('legs_per_arm'), Cp('n_cell_pulse')
b20 = beam[(beam.ep == 2.0) & (beam.dist_m == 0.5) & (~beam.thick)].iloc[0]
b19 = beam[(beam.ep == 1.912) & (beam.dist_m == 0.5) & (~beam.thick)].iloc[0]
sh = shield[shield.scen == 'design'].set_index('eps')
bham = C.R(d, 'bham_28_2m_pb5')

D = sd.Deck('FRANZ: X17 feasibility',
            'Could the MX17 apparatus test the ATOMKI ⁴He anomaly at the Frankfurt Neutron Source FRANZ (near-threshold '
            '⁷Li(p,n), keV neutrons)? The facility, its status, and the reach with the shared Geant4 beam background.')

# --------------------------------------------------------------------------- #
cover = (sd.kicker('MX17 at FRANZ · Frankfurt near-threshold ⁷Li(p,n) · feasibility · 21 Oct 2026')
         + '<h1 style="font-size:60px;font-weight:600;line-height:1.08;letter-spacing:-1.5px">'
           f'At its design 10¹² n/s, FRANZ would pass ATOMKI ⁴He ×{C.RHO / rho:.1f} in 50 days, '
           'tying Birmingham. It has not yet run at 2 MeV.</h1>'
         + sd.p('³He(n,e⁺e⁻)⁴He on the 30 bar × 40 cm cell 0.5 m from a thin Li target, 20 mA DC at 2.0 MeV, big '
                'plastics. X17/IPC reached at 3σ with IPC, cosmics and the beam’s own Geant4 background.', 30, sd.DMUT)
         + sd.row(
             sd.bignum(sci(rho, 1), 'X17/IPC at 3σ in 50 days (design)', sd.DGREEN,
                       f'ATOMKI ⁴He: 1.5×10⁻³. As built: {sci(rho_ab, 1)}.',
                       tip='survey bracket before this study: 1.2×10⁻³ – 1.1×10⁻² (10 mA)'),
             sd.bignum(sci(rho_lic, 1), 'at the licence today: 10 mA, 5 % duty', sd.DORANGE if hasattr(sd, 'DORANGE') else sd.ORANGE,
                       f'×{rho_lic / C.RHO:.1f} short of ATOMKI; {C.fmt_days(C.days_to_atomki(rho_lic))} to reach it'),
             sd.bignum('no 2 MeV yet', 'RFQ at 0.7 MeV; 2 MeV planned end 2025', sd.DRED,
                       'no report of first neutrons found (Oct 2026)'),
             gap=56))
D.slide('cover', cover, dark=True, short='cover',
        notes=f"""Reach = the X17/IPC(E1) ratio a 50-day run detects at 3σ (Asimov over the θ histogram; a DC beam has no TOF tag). Every neutron is below 0.5 MeV.

Design baseline: 20 mA DC at 2.0 MeV = 10¹² n/s (the design yield, and the licence's neutron limit). {ncell:.2g} n/s through the Ø8 cm spot at 0.5 m give {ok_arm:,.0f} singles and {legs:,.0f} legs per arm per second; no throttle. The reach is at the IPC + cosmics floor ({sci(floor, 1)}): {C.fmt_days(days)} of beam to ATOMKI.

Licence (IPAC 2025): < 5 % duty and 10¹² n/s. At 10 mA, 5 %: {sci(rho_lic, 1)}; at 2.2 MeV (if possible) {sci(rho_lic22, 1)}. With today's ion source (1 %): {sci(rho_first, 1)}.

Files: <code>franz/FEASIBILITY.md</code>, <code>franz/FACILITY.md</code>, <code>franz/franz_beam.py</code>.""")

# --------------------------------------------------------------------------- #
facts = sd.col(
    sd.card(sd.p('<b>Goethe University Frankfurt</b>, Riedberg', 28)
            + sd.p('Institut für Angewandte Physik, Stern-Gerlach-Zentrum; a university nuclear-astrophysics source.', 24, sd.MUT)),
    sd.card(sd.p('<b>2.0 MeV protons on lithium, just above threshold</b>', 28)
            + sd.p('keV neutrons in a forward cone ("kinematic collimation"); design 10¹² n/s at 20 mA DC.', 24, sd.MUT)),
    sd.card(sd.p('<b>Status: commissioning</b>', 28, sd.ORANGE)
            + sd.p('RFQ beam at 0.7 MeV (2023–24); 2 MeV and first neutrons planned for end 2025, not yet reported.', 24, sd.MUT)),
    w=700, gap=24)
D.slide('where', sd.title('FRANZ: a university keV-neutron source in Frankfurt',
                          'the facilities this study compares; hover the dots for details')
        + sd.row(C.europe_map(880, 660, 'FRANZ Frankfurt', labels={'FRANZ Frankfurt': (16, -10, 'start')}), facts, gap=56),
        short='where',
        notes="""Site: experimental hall of the physics building, Max-von-Laue-Str. 1, 60438 Frankfurt (≈ 50.17 N, 8.63 E).

Built for s-process activations and TOF capture with the Karlsruhe 4π BaF₂ array. People (public): H. Hähnel (commissioning), H. Podlech, U. Ratzinger (IAP); users T. Heftrich, K. Göbel.

Sources: Hähnel et al. IPAC 2023 / LINAC 2024 / IPAC 2025; Reifarth et al. arXiv:1403.5670. <code>franz/FACILITY.md</code>.""")

# --------------------------------------------------------------------------- #
cards = sd.row(
    sd.card(sd.p('<b>10¹² n/s</b>', 34, sd.BLUE) + sd.p('design, 20 mA DC at 2.0 MeV = the licence limit', 22, sd.MUT)),
    sd.card(sd.p(f'<b>≤ {b20.max_En0_keV:.0f} keV</b>', 34, sd.BLUE)
            + sd.p(f'mean {b20.mean_En0_keV:.0f} keV at 0°, forward ×{b20.forward_gain:.1f}', 22, sd.MUT)),
    sd.card(sd.p('<b>&lt; 5 % duty today</b>', 34, sd.ORANGE) + sd.p('licence; ion source 0.5–1 ms at 10 Hz', 22, sd.MUT)),
    sd.card(sd.p('<b>thin Li: no ⁸Be lines</b>', 34, sd.GREEN) + sd.p('protons stop at threshold, not at 441 keV', 22, sd.MUT)),
    gap=24)
D.slide('beamline', sd.title('Ion source, one RFQ-IH-DTL cavity, a thin Li target; the X17 station is 0.5 m downstream',
                             'top view, not to scale; dashed = not yet commissioned (IH) or proposed for X17 (green)')
        + cartoon.beamline(1664, 500) + cards,
        short='beamline',
        notes=f"""Accelerator: CHORDIS volume source (GSI) + post-accelerator to 60 keV; LEBT; coupled 175 MHz 4-rod RFQ (700 keV) + 1.3 MV IH-DTL (2.03 MeV design). RFQ commissioned with up to 11 mA macro-pulse current (7.1 mA matched, 92.7 % transmission).

Through the Ø8 cm spot at 0.5 m, 2.0 MeV: {b20.n_cell:.2g} n/s per mA (franz_beam.py, normalised to the design 5×10¹⁰ n/s/mA; the absolute σ/S model gives ×1.5 more, LiLiT's measured yield agrees within ×1.3).

Target design as built, cooling and power limit: (ask). The hall layout: (ask).""")

# --------------------------------------------------------------------------- #
e = np.geomspace(1e-3, 40, 700)
fold = pd.read_csv(ROOT / 'ganil_nfs' / 'out' / 'fold_table.csv')
nfs = np.interp(e, fold.E_n, fold.n_per_s_MeV, left=0, right=0)
nfs = nfs / np.trapezoid(nfs, e)
import bham_beam as BB  # noqa: E402
curves = [('FRANZ, 1.912 MeV', FB.spectrum_on_grid(1.912, e), sd.ORANGE),
          ('FRANZ, 2.0 MeV', FB.spectrum_on_grid(2.0, e), sd.RED),
          ('Birmingham, 2.8 MeV', BB.spectrum_on_grid(2.8, e), sd.BLUE),
          ('GANIL NFS d(40)+Be', nfs, sd.GREY)]
P = sd.Plot(1100, 600, x=(1e-3, 40, 'log'), y=(0, 1.0, 'lin'), xlabel='neutron energy E_n [MeV]', ylabel='E dN/dE (peak = 1)')
P.xticks([(v, f'{v:g}') for v in (0.001, 0.01, 0.1, 1, 10)]).yticks([(v, f'{v:g}') for v in (0, .25, .5, .75, 1)])
P.band([0.2, 2.75], [0, 0], [1.0, 1.0], sd.GREEN, 0.08, tip='E_n 0.2-2.75 MeV: E* ≤ 22.1 MeV, θ_min ≥ 99°')
P.text(0.21, 0.95, 'ATOMKI-like window', 22, sd.GREEN)
for name, f, col in curves:
    y = e * f
    P.line(list(e), list(y / y.max()), col, markers=False, w=4 if 'FRANZ' in name else 3, tip=name)
D.slide('spectrum', sd.title('keV neutrons: ×2 fewer pairs per neutron than Birmingham’s, but all of them forward',
                             'normalised E dN/dE at 0°; FRANZ from the slowing-down MC with protons stopping at the (p,n) threshold')
        + sd.row(P.svg('neutron spectra'),
                 sd.col(sd.legend([(n, c) for n, _, c in curves], size=22),
                        sd.p('E* = S_n + ¾E_n ≈ 20.6–20.8 MeV: the X17 opening angle is at its widest (~110°).', 26),
                        sd.p('³He(n,γ) and IPC fall as 1/v: per neutron the 2.0 MeV spectrum makes 3.4×10⁻⁹ pairs, '
                             '0.5 MeV neutrons 6.8×10⁻⁹, thermal 4.8×10⁻¹¹.', 24, sd.MUT),
                        sd.p(f'At 1.912 MeV every neutron is inside 64°; at 2.0 MeV 0° gets ×{b20.forward_gain:.1f} the 4π average.', 24, sd.MUT),
                        w=500, gap=24), gap=40),
        short='spectrum',
        notes=f"""Kinematics: 0° maximum {b19.max_En0_keV:.0f} keV at 1.912 MeV (Karlsruhe quasi-stellar field: 25 keV Maxwellian), {b20.max_En0_keV:.0f} keV at 2.0 MeV. The low branch below ~30 keV is the backward-CM neutrons that the CM motion carries forward.

The Geant4 neutron run N5 starts at 1 keV: < 0.1 % of the 0° spectrum lies below it (dropped). The NFS signal and IPC tables (lowest bin 0.2–0.75 MeV) are applied at keV energies.

<code>franz/franz_beam.py</code> → <code>out/franz_spectra.csv</code>.""")

# --------------------------------------------------------------------------- #
q = r[(r.days == 50) & (r.hw == C.HW) & (~r.thick) & (r.pb_cm == 0)]
P = sd.Plot(1060, 600, x=(0.25, 1.1, 'log'), y=(1e-4, 3e-2, 'log'), xlabel='Li target to cell window [m]',
            ylabel='X17/IPC at 3σ in 50 days')
P.xticks([(v, f'{v:g}') for v in (0.3, 0.5, 1.0)]).yticks(sd.log_ticks(-4, -2))
P.hline(C.RHO, sd.GREEN, label='ATOMKI ⁴He 1.5×10⁻³')
P.hline(bham, sd.BLUE, label=f'Birmingham baseline {bham:.1e}', anchor='start')
legs_ = []
for scen, ep, col, dash, lab in (('design', 2.0, sd.RED, None, 'design: 20 mA DC, 2.0 MeV'),
                                 ('licence', 2.2, sd.ORANGE, '4 6', 'licence 5 %, 2.2 MeV (if possible)'),
                                 ('licence', 2.0, sd.ORANGE, None, 'licence: 10 mA at 5 %, 2.0 MeV'),
                                 ('first', 2.0, sd.GREY, None, 'today’s source: 10 mA at 1 %')):
    z = q[(q.scen == scen) & (q.ep == ep)].sort_values('dist_m')
    P.line(list(z.dist_m), list(z.rho3), col, dash=dash, r=8,
           tips=[f'{lab}, {x:g} m: {v:.2g} ({C.fmt_days(C.days_to_atomki(v))} to ATOMKI)' for x, v in zip(z.dist_m, z.rho3)])
    legs_.append((lab, col, 'dash' if dash else 'line'))
P.points([0.5], [rho], sd.INK, r=13, tips=[f'baseline: {rho:.2g}'])
D.slide('reach', sd.title('Duty factor decides it: DC passes ATOMKI ×4.5, the licence’s 5 % does not',
                          '50 days, big plastics, thin Li, no filter; statistics-limited everywhere (reach ∝ 1/√(duty · flux))')
        + sd.row(sd.col(P.svg('reach vs distance'), sd.legend(legs_, size=22), w=1060, gap=8),
                 sd.col(sd.p('The beam is never throttled: the reach is the IPC + cosmics floor.', 26),
                        sd.p('At the 10¹² n/s cap, 2.2 MeV gains nothing at DC; under the 5 % duty limit it gains ×2.2.', 24, sd.MUT),
                        sd.p('At a few % duty the DAQ is gated on the macro-pulse, which cuts cosmics ×20–100.', 24, sd.MUT),
                        w=540, gap=24), gap=48),
        short='reach',
        notes=f"""Pulsed handling (franz_beam.py): the Geant4 components at the in-pulse rate; signal, IPC, correlated, accidentals and cosmics × duty per day; DREAM live time and Micromegas occupancy at the in-pulse rate. The average yield is capped at 10¹² n/s.

As built hardware, design at 0.5 m: {sci(rho_ab, 1)}. At 1 m: {sci(rho_1m, 1)} ({C.fmt_days(C.days_to_atomki(rho_1m))}).

<code>out/franz_reach.csv</code>.""")

# --------------------------------------------------------------------------- #
z = r[(r.days == 50) & (r.hw == C.HW) & (r.scen == 'design') & (r.dist_m == 0.5) & (r.ep == 2.0)]
rows_t = [('thin Li', R('franz_2000_thin_pb0'), sd.GREEN, 'protons stop at the (p,n) threshold'),
          ('thick Li', R('franz_2000_thick_pb0'), sd.RED, 'protons cross the 441 and 1030 keV ⁸Be resonances'),
          ('thin + 5 cm Pb', R('franz_2000_thin_pb5'), sd.GREY, 'Pb removes keV neutrons almost as fast as 15–18 MeV γ'),
          ('thick + 5 cm Pb', R('franz_2000_thick_pb5'), sd.GREY, '')]
hb = sd.hbars([(n, v, c, f'{n}: {v:.2g}. {t}') for n, v, c, t in rows_t], 3e-3, width=900, log=True, vmin=1e-4,
              label_w=260, fmt=lambda v: f'{v:.1e}')
corr_thin = R('franz_2000_thin_pb0', col='corr_win_per_day')
corr_thick = R('franz_2000_thick_pb0', col='corr_win_per_day')
ipc_w = R(col='IPC_win_per_day')
D.slide('target', sd.title('A thin Li layer removes the 15–18 MeV γ that a thick target makes',
                           'design, 0.5 m, big plastics, 50 days: X17/IPC at 3σ (shorter is better)')
        + sd.row(sd.col(hb, w=1000), sd.col(
            sd.p(f'Thick Li: ⁷Li(p,γ)⁸Be ~10⁻⁷ γ/p → {corr_thick:,.0f} correlated pairs/day in the window, ×{corr_thick / ipc_w:.0f} the IPC.', 26),
            sd.p(f'Thin Li (~12 µm): direct capture only, ~5×10⁻¹⁰ γ/p → {corr_thin:,.0f}/day ({100 * corr_thin / ipc_w:.1f} % of IPC).', 26, sd.GREEN),
            sd.p('No Pb filter needed: FRANZ already uses ~10 µm evaporated Li (confirm).', 24, sd.MUT), w=600, gap=24), gap=48),
        short='thin target',
        notes="""γ/p: thick 10⁻⁷ (the Birmingham stand-in: 441 keV resonance + 1030 keV + direct capture); thin = n(⁷Li) × σ_DC (≈ 10 µb, estimate) × the 0.6 mg/cm² needed to bring 2.0 MeV protons to 1.881 MeV. ×10 on σ_DC would still leave the correlated term < 20 % of IPC.

Pb (estimate): keV neutrons Σ ≈ 0.36 /cm uncollided, 15–18 MeV γ μ = 0.57 /cm.

The 478 keV ⁷Li(p,p′γ) line makes no trigger legs; its Micromegas occupancy is not modelled.""")

# --------------------------------------------------------------------------- #
qq = r[(r.key == K) & (r.scen == 'design') & (r.dist_m == 0.5) & (r.hw == C.HW) & (r.days == 50)].iloc[0]
rows_b = [('IPC (E1)', qq.IPC_win_per_day, sd.BLUE, 'Born E1 IPC'), ('cosmics', qq.cosmic_win_per_day, sd.GREY, 'no veto'),
          ('accidentals', qq.acc_win_per_day, sd.ORANGE, '±5 ns'), ('correlated beam', qq.corr_win_per_day, sd.RED, 'thin-target γ'),
          ('X17 at ATOMKI', qq.X17_win_per_day, sd.GREEN, 'X17/IPC = 1.5×10⁻³')]
hb = sd.hbars([(n, max(v, 1), c, f'{n}: {v:,.0f} per day in 100–150°. {t}') for n, v, c, t in rows_b],
              max(v for _, v, _, _ in rows_b) * 1.2, width=700, log=True, vmin=1, label_w=260, fmt=lambda v: f'{v:,.0f}')
tab = sd.table(['design baseline, 0.5 m', ''],
               [['neutrons through the cell', f'{ncell:.2g} /s'], ['singles per arm', f'{ok_arm:,.0f} /s'],
                ['trigger legs per arm', f'{legs:,.0f} /s'], ['DREAM live time', f'{qq.live:.2f}'],
                ['Micromegas occupancy (1 µs)', f'{qq.occ:.4f}']], size=22, widths=[460, 220])
D.slide('budget', sd.title('The background is IPC and cosmics; the beam adds a few per cent',
                           'events per day in θ = 100–150° after vertex and E_sum > W/2 cuts; design baseline, big plastics')
        + sd.row(sd.col(hb, tab, w=1000, gap=36),
                 sd.col(sd.p(f'X17 at the ATOMKI ratio is {100 * qq.X17_win_per_day / qq.IPC_win_per_day:.1f} % of the IPC in the window.', 26),
                        sd.p('keV neutrons fire a leg only through capture γ: ~4×10⁻⁷ singles per arm per neutron, and no '
                             'same-event two-arm pair in the Geant4 sample.', 24, sd.MUT),
                        sd.p('A cosmic veto would remove a third of the background at DC.', 24, sd.MUT), w=560, gap=24), gap=48),
        short='background budget',
        notes="""Window counts are for orientation; the reach uses the whole θ histogram. Accidentals and the correlated term as in the Birmingham and MEDAPP notes (survey/soft_sim/soft_reach.py).""")

# --------------------------------------------------------------------------- #
n_arm = float(sh.n_arm_unshielded.iloc[0])
rows = [[sci(e_, 0), sci(t, 1), f'{b:.0f} cm'] for e_, t, b in zip(sh.index, sh.T_needed, sh.bpe_cm)]
D.slide('shield', sd.title(f'The arms need ~{sh.bpe_cm.loc[1e-5]:.0f} cm of borated PE around the target, inside 0.5 m',
                           'an estimate, not Geant4: what keeps the leakage singles below 10 % of the beam’s own (keV tenth-value layer 5 cm, stand-in)')
        + sd.row(sd.col(sd.p(f'With no shield, one arm 0.5 m from the target sees <b>{sci(n_arm, 1)}</b> n/s, '
                             f'×{n_arm / ncell:.0f} what goes through the cell.', 28),
                        sd.table(['singles per entering n', 'transmission', 'borated PE'], rows, size=22, widths=[300, 220, 200]),
                        w=820, gap=24),
                 sd.col(sd.callout('keV neutrons are easy to stop: ~5 cm of borated PE per decade, against ~10 cm at Birmingham’s 0.5 MeV.', sd.GREEN, 26),
                        sd.callout(f'But the arms reach ~0.2 m upstream of the cell window: at 0.5 m that leaves ~0.3 m for chamber + shield. '
                                   f'At 1 m: {sci(rho_1m, 1)}, {C.fmt_days(C.days_to_atomki(rho_1m))} to ATOMKI.', sd.ORANGE, 24),
                        w=760, gap=24), gap=56),
        short='shield',
        notes="""Birmingham's shield() estimate with a 5 cm tenth-value layer (H σ ≈ 18 b at 30 keV, ¹⁰B 1/v; a stand-in). The singles per neutron entering an arm are not simulated: 10⁻⁶–10⁻⁴ spans capture γ in the plastics and SiPM wall. A Geant4 model of the target chamber, shield and hall is the next simulation. <code>out/franz_shield.csv</code>.""")

# --------------------------------------------------------------------------- #
crow = [('n_TOF EAR2', d['ear2'], sd.GREY, 'survey'), ('GANIL NFS', d['nfs'], sd.GREY, 'Geant4'),
        ('ILL PF1B', d['pf1b'], sd.GREY, 'ILL Geant4 walls'), ('ATOMKI ⁴He', C.RHO, sd.GREEN, 'PRC 104 044003'),
        ('FRM II MEDAPP', C.R(d, 'medapp_std'), sd.ORANGE, 'reactor off since 2020'),
        ('Birmingham', bham, sd.BLUE, 'operating; needs a port'),
        ('FRANZ design (DC)', rho, sd.RED, 'this note'), ('FRANZ licence (5 %)', rho_lic, sd.RED, 'this note'),
        ('FRANZ today (1 %)', rho_first, sd.RED, 'this note')]
crow.sort(key=lambda x: -x[1])
cb = sd.hbars([(n, v, c, f'{n}: {v:.2g}. {t}') for n, v, c, t in crow], 0.2, width=800, log=True, vmin=5e-5,
              label_w=300, fmt=lambda v: f'{v:.1e}', size=22, h=28)
D.slide('compare', sd.title('Against the other facilities: FRANZ at DC ties Birmingham; pulsed, it does not',
                            'X17/IPC at 3σ in 50 days, E* ≤ 22 MeV, big plastics; shorter bars are better')
        + sd.row(cb, sd.col(sd.p('Same apparatus, same cuts, same fit: only the beam changes.', 26),
                            sd.p('FRANZ’s advantage is geometry (a forward cone 0.5 m away) and a clean thin target; '
                                 'its disadvantage is that it has not delivered 2 MeV yet.', 24, sd.MUT), w=560, gap=24), gap=48),
        short='comparison')

# --------------------------------------------------------------------------- #
flow = sd.flow([dict(label='2 MeV on target', sub='planned end 2025; not reported', color=sd.RED),
                dict(label='DC or more duty', sub='licence 5 %, CHORDIS 1 % today', color=sd.RED),
                dict(label='thin Li', sub='confirm ~10 µm on Cu', color=sd.GREEN),
                dict(label='room 0.5–1 m downstream', sub='+ 20–30 cm BPE around the target', color=sd.ORANGE),
                dict(label='a few weeks of beam', sub='a university machine', color=sd.GREEN)], size=22)
D.slide('needs', sd.title('What it would take: 2 MeV at all, then DC beam and a place for the arms',
                          'in order of what decides it')
        + flow
        + sd.table(['ask FRANZ (H. Hähnel, H. Podlech, T. Heftrich)', 'why it matters'],
                   [['has the coupled RFQ-IH-DTL delivered 2 MeV and neutrons? when?', 'nothing runs without it'],
                    ['the path from < 5 % duty to DC: licence, ion source, target power', 'reach ∝ 1/√duty'],
                    ['Li target as built: thickness, backing, cooling', 'thin Li removes the ⁸Be γ'],
                    ['hall layout and the space 0.5–1 m downstream of the target', 'the arms and a shield must fit'],
                    ['can the energy be raised to ~2.2 MeV?', '×2.2 at 5 % duty'],
                    ['beam time for an external collaboration', f'{C.fmt_days(days)} at DC reach ATOMKI']],
                   size=24, widths=[860, 600], align=['left', 'left']),
        short='what it needs')

# --------------------------------------------------------------------------- #
end = (sd.title('What this does not settle yet', None)
       + sd.row(sd.col(sd.p('<b>Not in the simulation</b>', 30, sd.DINK),
                       sd.p('• Target chamber, shield, hall and room return: leakage is an estimate.', 26, sd.DINK),
                       sd.p('• A diverging beam (±4.6° at 0.5 m): the Geant4 gun is parallel.', 26, sd.DINK),
                       sd.p('• Micromegas occupancy from the 478 keV γ; σ_DC of ⁷Li(p,γ) at 2 MeV.', 26, sd.DINK), gap=18),
                sd.col(sd.p('<b>Facility</b>', 30, sd.DINK),
                       sd.p('• No 2 MeV beam reported yet; schedules have slipped ~1 year per step.', 26, sd.DINK),
                       sd.p('• Licence < 5 % duty; DC at 10¹² n/s is the design, not the plan of record.', 26, sd.DINK),
                       sd.p('• No cosmic veto yet.', 26, sd.DINK), gap=18), gap=80))
D.slide('end', end, dark=True, short='open questions')

out = D.write(O / 'franz-x17-feasibility.html',
              note_meta=dict(title='FRANZ X17 feasibility',
                             summary='Could the MX17 apparatus test the ATOMKI ⁴He anomaly at the Frankfurt Neutron Source FRANZ? Status, thin-Li keV beam, duty factor and the reach with the shared Geant4 soft-beam background.',
                             tags='x17, franz, feasibility', date='2026-10-21'),
              footer='Built by x17_facility_search/franz/deck/build_deck.py from franz/franz_beam.py outputs.')
print(out)
