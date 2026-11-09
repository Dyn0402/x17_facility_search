"""Build the SARAF X17 feasibility slide note. Reads saraf/out/; writes saraf/out/saraf-x17-feasibility.html (not published).

    ~/PycharmProjects/nTof_x17/.venv/bin/python saraf/deck/build_deck.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'survey' / 'soft_sim'))
sys.path.insert(0, str(ROOT / 'survey'))
import deck_common as C  # noqa: E402
from deck_common import sd, sci  # noqa: E402

O = HERE.parent / 'out'
d = C.load()
r = pd.read_csv(O / 'saraf_reach.csv')
cp = pd.read_csv(O / 'saraf_components.csv')
beam = pd.read_csv(O / 'saraf_beam.csv')
shield = pd.read_csv(O / 'saraf_shield.csv')
SIG = 'E* ≤ 22 MeV'


def R(key, scen, dist=1.0, hw=C.HW, days=50, col='rho3', signal=SIG):
    q = r[(r.key == key) & (r.scen == scen) & (r.dist_m == dist) & (r.hw == hw) & (r.days == days) & (r.signal == signal)]
    return float(q[col].iloc[0])


K4 = 'lilit_4000_pb0'
K19 = 'lilit_1925_pb0'
rho = R(K4, 'phaseI')
rho_ab = R(K4, 'phaseI', hw='as built')
rho_ran = R(K19, 'as_ran', 0.5)
rho_ran_ab = R(K19, 'as_ran', 0.5, hw='as built')
rho_5 = R(K4, 'phaseII')
rho_d40 = R('dbe_40_0', 'phaseII')
rho_d40_all = R('dbe_40_0', 'phaseII', signal='all E*')
days = C.days_to_atomki(rho)
bham = C.R(d, 'bham_28_2m_pb5')
medapp = C.R(d, 'medapp_std')

D = sd.Deck('SARAF: X17 feasibility',
            'Could MX17 test the ATOMKI ⁴He anomaly at SARAF (Soreq)? LiLiT at higher proton energy, Phase II, and practical access.')

# ------------------------------------------------------------------ cover
cover = (sd.kicker('MX17 at SARAF · Soreq, Yavne · feasibility · 9 Nov 2026')
         + '<h1 style="font-size:58px;font-weight:600;line-height:1.08;letter-spacing:-1.5px">'
           'Raise the proton energy on the liquid-lithium jet and SARAF ties Birmingham on paper. Today the beam does not exist.</h1>'
         + sd.p('³He(n,e⁺e⁻)⁴He, 30 bar × 40 cm cell 1 m from a thick Li target. E_p = 4 MeV, 1 mA, big plastics. X17/IPC at 3σ, beam-only engine.', 30, sd.DMUT)
         + sd.row(sd.bignum(sci(rho, 1), 'X17/IPC at 3σ in 50 days', sd.DGREEN, f'as built: {sci(rho_ab, 1)}; {C.fmt_days(days)} to ATOMKI'),
                  sd.bignum(sci(rho_ran, 1), 'LiLiT as it actually ran (1.925 MeV)', sd.ORANGE, '×2.5 short of ATOMKI'),
                  sd.bignum('WATCH', 'no such beam today', sd.DRED, 'Phase I converted; Phase II first cryomodule commissioning, Oct 2025'),
                  gap=56))
D.slide('cover', cover, dark=True, short='cover',
        notes=f"""Reach = X17/IPC a 50-day run detects at 3σ (Asimov θ histogram, no TOF). E* ≤ 22 MeV and all E* agree for the Li family: every neutron is ≤ 2.3 MeV.

Birmingham engine value {sci(bham, 1)} (full-room Geant4 5.5×10⁻⁴). FRANZ design 3.3×10⁻⁴.

Files: <code>saraf/FEASIBILITY.md</code>, <code>saraf/FACILITY.md</code>, <code>saraf/saraf_beam.py</code>.""")

# ------------------------------------------------------------------ machine
tab = sd.table(['SARAF', ''],
               [['Phase I (2010 – ~2019)', 'p ≤ 4 MeV, 1–2 mA CW (≤ 4 kW); d ≤ 5 MeV. Replaced.'],
                ['LiLiT', '1.5 mm liquid-Li jet, ran 1–2 mA at 1.92 MeV, 3–5×10¹⁰ n/s (measured)'],
                ['⁸Be γ at LiLiT', '7×10⁸ γ/s/mA, 17.6 + 14.6 MeV (measured): the Birmingham stand-in confirmed'],
                ['Phase II', 'p 1.3–35 MeV, d 2.6–40 MeV, 5 mA CW, GaIn 200 kW, thermal source, 18 m TOF (planned)'],
                ['Status', 'MEBT commissioned; CM1 installed; "commissioning ongoing" Oct 2025; no beam report'],
                ['Access', 'no user programme found; a nuclear research site in an active conflict zone']],
               size=26, widths=[360, 1200], align=['left', 'left'])
D.slide('machine', sd.title('The machine: a CW SC proton/deuteron linac in the middle of a rebuild',
                            'sources: Mardor EPJA 2018; Tessler PLB 2015; M. Paul 2021; Pichoff LINAC 2024; Bazin LCWS 2025')
        + tab, short='machine',
        notes="""The Phase I linac delivered 1 mA at ~4 MeV or 1.5–2 mA at 2 MeV (3–4 kW). Its RFQ and superconducting module are being replaced by the Phase II linac. Since 2022 no report of Phase I beam was found, and the Phase II cryomodule CM1 was still commissioning in October 2025. <code>FACILITY.md</code> §1.""")

# ------------------------------------------------------------------ spectra
sp = pd.read_csv(O / 'saraf_spectra.csv')
P = sd.Plot(1100, 620, x=(0.01, 50, 'log'), y=(1e7, 3e13, 'log'), xlabel='E_n [MeV]', ylabel='0° dY/dE dΩ [n / (s mA sr MeV)]')
P.xticks([(v, f'{v:g}') for v in (0.01, 0.1, 1, 10)]).yticks(sd.log_ticks(7, 13))
P.band([0.2, 2.75], [1e7, 1e7], [3e13, 3e13], sd.GREEN, 0.08, tip='ATOMKI window E_n ≤ 2.75 MeV')
cur = [('LiLiT 1.925 MeV', sd.GREY), ('LiLiT 4.0 MeV', sd.RED), ('p+Be 4 MeV', sd.ORANGE), ('d+Be 5 MeV', sd.BLUE), ('d+Be 40 MeV', sd.INK)]
for n, c in cur:
    q = sp[sp.source == n]
    if len(q) > 200:
        q = q.iloc[::4]
    P.line(list(q.E_n), list(q.per_mA_sr_MeV), c, markers=False, w=3, tip=n)
s4 = beam[(beam.family == 'lilit') & (beam.e0 == 4.0)].iloc[0]
s19 = beam[(beam.family == 'lilit') & (beam.e0 == 1.925)].iloc[0]
D.slide('spectra', sd.title('The lever is the proton energy: every LiLiT-family neutron stays in the window',
                            'per mA at 0°; LiLiT scale measured at 1.925 MeV; dotted band is E_n ≤ 2.75 MeV')
        + sd.row(sd.col(P.svg('spectra'), sd.legend([(n, c) for n, c in cur], size=20), w=1100, gap=8),
                 sd.col(sd.p(f'1.925 MeV: {sci(s19.per_mA_total_n, 1)} n/s/mA, ≤ {s19.max_En_0deg_MeV * 1e3:.0f} keV: too few neutrons.', 26),
                        sd.p(f'4 MeV: {sci(s4.per_mA_total_n, 1)} n/s/mA, ≤ {s4.max_En_0deg_MeV:.1f} MeV: ×{s4.per_mA_total_n / s19.per_mA_total_n:.0f} more per mA, still all in the window.', 26, sd.GREEN),
                        sd.p('p + Be at 4 MeV: no ⁸Be γ, ~1×10¹² n/s/mA (ENDF extrapolation).', 24, sd.MUT),
                        sd.p('d + Be at 40 MeV: peak at 16 MeV, 2 % of neutrons in the window.', 24, sd.MUT), w=500, gap=24), gap=40),
        short='spectra',
        notes=f"""Thick-Li MC (franz/bham): model scale set by the measured 2.5×10¹⁰ n/s/mA at 1.925 MeV; at 2.6 MeV it gives 1.07×10¹², Birmingham's facility number is 1.0×10¹².

σ above 3 MeV is flat (ESTIMATE), ⁷Li(p,n₁) not modelled. d+Be at 5 MeV is an extrapolated Serber shape (ESTIMATE). <code>out/saraf_spectra.csv</code>.""")

# ------------------------------------------------------------------ scan
z = r[(r.days == 50) & (r.signal == SIG) & (r.hw == C.HW) & (r.dist_m == 1.0)]
P = sd.Plot(1100, 620, x=(1.8, 45, 'log'), y=(1e-4, 0.2, 'log'), xlabel='beam energy [MeV]', ylabel='X17/IPC at 3σ in 50 days, cell 1 m')
P.xticks([(v, f'{v:g}') for v in (2, 3, 4, 6, 10, 20, 40)]).yticks(sd.log_ticks(-4, -1))
P.hline(C.RHO, sd.GREEN, label='ATOMKI ⁴He 1.5×10⁻³')
P.hline(bham, sd.BLUE, label=f'Birmingham {bham:.1e}', anchor='start')
legs = []
for fam, th, scen, col, dash, lab in (('lilit', 0, 'phaseI', sd.RED, None, 'Li jet ≤ 4 kW'), ('lilit', 0, 'phaseII', sd.RED, '4 6', 'Li jet 5 mA'),
                                      ('pbe', 0, 'phaseII', sd.ORANGE, None, 'p+Be 0° 5 mA'), ('dbe', 0, 'phaseII', sd.INK, None, 'd+Be 0° 5 mA')):
    y = z[(z.family == fam) & (z.theta == th) & (z.scen == scen) & (z.pb_cm == 0)].sort_values('e0')
    P.line(list(y.e0), list(y.rho3), col, dash=dash, r=7, tips=[f'{lab}, {e:g} MeV: {v:.2g}' for e, v in zip(y.e0, y.rho3)])
    legs.append((lab, col, 'dash' if dash else 'line'))
P.points([4.0], [rho], sd.INK, r=12, tips=[f'best: {rho:.2g}'])
D.slide('scan', sd.title('Low energy wins; the 40 MeV beam does not, and the extra current is thrown away',
                         '50 days, E* ≤ 22 MeV, big plastics, cell at 1 m, engine only (no room)')
        + sd.row(sd.col(P.svg('reach vs energy'), sd.legend(legs, size=20), w=1100, gap=8),
                 sd.col(sd.p(f'Li jet at 4 MeV, 1 mA: {sci(rho, 1)} ({C.fmt_days(days)} to ATOMKI), statistics-limited.', 26, sd.GREEN),
                        sd.p(f'5 mA on the jet: {sci(rho_5, 1)} (≥ 20 kW, not demonstrated).', 24),
                        sd.p(f'd(40), 5 mA: {sci(rho_d40, 1)} in the window ({sci(rho_d40_all, 1)} all E*); the beam is throttled to 0.05 %.', 24, sd.MUT),
                        sd.p('p+Be above ~5 MeV also DREAM-limited (live ~0.5), so 5 mA is useless at 18 MeV.', 24, sd.MUT), w=500, gap=24), gap=40),
        short='reach',
        notes="""Li jet: components at 1 mA and 1 m re-weighted through N5/G5/G6; scaled with I and distance². Throttle scanned; never needed for the Li family at ≤ 4 kW at 1 m.

Reproduction first: <code>saraf_beam.py --check</code> returns Birmingham bham_28_2m_pb5 3.32e-4 and FRANZ design 3.31e-4, ratio 1.000.""")

# ------------------------------------------------------------------ distance + catalogue correction
rows = [('LiLiT as ran, 0.5 m', rho_ran, sd.GREY, 'catalogue had 6.7e-3'),
        ('LiLiT as ran, 0.3 m', R(K19, 'as_ran', 0.3), sd.GREY, 'near threshold is not enough'),
        ('Li 2.6 MeV, ≤ 4 kW, 1 m', R('lilit_2600_pb0', 'phaseI'), sd.ORANGE, 'demonstrated power'),
        ('Li 4 MeV, 1 mA, 1 m', rho, sd.GREEN, 'headline'),
        ('Li 4 MeV, 1 mA, 0.5 m', R(K4, 'phaseI', 0.5), sd.GREEN, 'needs ~50 cm BPE'),
        ('p+Be 4 MeV, 1 mA, 1 m', R('pbe_4_0', 'phaseI'), sd.ORANGE, 'ENDF extrapolation'),
        ('d+Be 5 MeV, 1 mA, 1 m', R('dbe_5_0', 'phaseI'), sd.BLUE, 'ESTIMATE')]
hb = sd.hbars([(n, v, c, f'{n}: {v:.2g}. {t}') for n, v, c, t in rows], 8e-3, width=900, log=True, vmin=5e-5, label_w=330, fmt=lambda v: f'{v:.1e}')
sh = shield[(shield.key == K4) & (shield.dist_m == 1.0) & (shield.scen == 'phaseI')]
D.slide('options', sd.title('Near threshold falls short; energy, not current, makes it work',
                            '50 days, E* ≤ 22 MeV, big plastics; shorter is better')
        + sd.row(sd.col(hb, w=1050), sd.col(
            sd.p('Thick Li: every proton crosses the ⁸Be resonances, but correlated pairs are only 3.5 % of IPC at 4 MeV.', 26),
            sd.callout(f'Around the target (estimate): {sh.bpe_cm.min():.0f}–{sh.bpe_cm.max():.0f} cm borated PE for the 4π MeV field. 1 m is the honest distance.', sd.ORANGE, 24),
            sd.p('Birmingham\'s full-room Geant4 lost ×1.7; same factor here ≈ 6×10⁻⁴ (ESTIMATE).', 24, sd.MUT), w=560, gap=24), gap=48),
        short='options',
        notes="""The 5 cm Pb option is worse (neutrons attenuate too). LiLiT at ≥ 2 MeV has not been tested: the jet handled 1.92 MeV at up to 4 kW. <code>out/saraf_shield.csv</code>.""")

# ------------------------------------------------------------------ comparison
crow = [('GANIL NFS', d['nfs'], sd.GREY, 'Geant4'), ('ATOMKI ⁴He', C.RHO, sd.GREEN, 'PRC 104 044003'),
        ('Birmingham', bham, sd.BLUE, 'operating; full Geant4 5.5e-4'), ('FRM II MEDAPP', medapp, sd.ORANGE, 'reactor off'),
        ('SARAF Li 4 MeV, 1 mA, 1 m', rho, sd.RED, 'no beam today'), ('SARAF as ran', rho_ran, sd.RED, 'LiLiT 2014-18'),
        ('SARAF Phase II d(40)', rho_d40, sd.RED, 'in window')]
crow.sort(key=lambda x: -x[1])
cb = sd.hbars([(n, v, c, f'{n}: {v:.2g}. {t}') for n, v, c, t in crow], 0.2, width=800, log=True, vmin=5e-5, label_w=340,
              fmt=lambda v: f'{v:.1e}', size=22, h=28)
D.slide('compare', sd.title('Against the others: on paper a tie with Birmingham, in practice no beam',
                            'X17/IPC at 3σ in 50 days, E* ≤ 22 MeV, big plastics')
        + sd.row(cb, sd.col(sd.p('Same apparatus, same cuts, same fit: only the beam changes.', 26),
                            sd.p('Compared with Birmingham (operating, needs a port) and FRANZ (design, 2 MeV not reported).', 24, sd.MUT), w=560, gap=24), gap=48),
        short='comparison')

# ------------------------------------------------------------------ scorecard
card = sd.table(['question', 'answer'],
                [['beam today?', 'no: Phase I converted; Phase II CM1 "commissioning ongoing" Oct 2025'],
                 ['access', 'no user programme or TNA found; Soreq is a state nuclear research centre'],
                 ['space / shield', 'target room unknown (ask); ~50 cm BPE at 1 m'],
                 ['cost (estimate)', '~€100–300 k apparatus and shield, no machine cost'],
                 ['safety', '~3 TBq ⁷Be at saturation; ³He cell on a nuclear site (ask)'],
                 ['competition', 'X17 would be a guest behind isotopes and thermal neutrons'],
                 ['access restriction', 'active conflict zone; commissioning reported as complicated']],
                size=26, widths=[420, 1140], align=['left', 'left'])
D.slide('score', sd.title('Scorecard: WATCH', 'the physics case is good; the machine and access are not') + card, short='scorecard')

# ------------------------------------------------------------------ what would have to be true
end = (sd.title('For SARAF to be top-3', None)
       + sd.row(sd.col(sd.p('<b>Three things must be true</b>', 30, sd.DINK),
                       sd.p('1. CM1 delivers 2–5 MeV protons at ≥ 1 mA CW.', 26, sd.DINK),
                       sd.p('2. LiLiT (or a Be converter) is re-installed in a room with ≥ 1 m free at 0°, tested at ≥ 2.6 MeV.', 26, sd.DINK),
                       sd.p('3. External access is possible at all: site rules, ³He, security.', 26, sd.DINK), gap=18),
                sd.col(sd.p('<b>Not settled</b>', 30, sd.DINK),
                       sd.p('• Room, shield, target chamber: no full Geant4 here.', 26, sd.DINK),
                       sd.p('• σ(E_p) above 3 MeV; d+Be 5 MeV (ESTIMATE).', 26, sd.DINK),
                       sd.p('• Whether LiLiT tolerates 4 MeV beam.', 26, sd.DINK), gap=18), gap=80))
D.slide('end', end, dark=True, short='what next')

out = D.write(O / 'saraf-x17-feasibility.html',
              note_meta=dict(title='SARAF X17 feasibility',
                             summary='MX17 at SARAF: LiLiT at higher proton energy, Phase II, and practical access. WATCH.',
                             tags='x17, saraf, feasibility', date='2026-11-09'),
              footer='Built by x17_facility_search/saraf/deck/build_deck.py from saraf/out/.')
print(out)
