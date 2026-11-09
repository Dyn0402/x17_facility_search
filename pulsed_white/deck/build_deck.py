"""Build the pulsed-white-source X17 slide note from pulsed_white/out/ (pw_beam.py).

    ~/PycharmProjects/nTof_x17/.venv/bin/python pulsed_white/deck/build_deck.py
Built, not published.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'survey' / 'soft_sim'))
import deck_common as C  # noqa: E402
from deck_common import sd, sci  # noqa: E402

O = HERE.parent / 'out'
t = pd.read_csv(O / 'pw_reach.csv')
f = pd.read_csv(O / 'pw_flash_scan.csv')
spec = pd.read_csv(O / 'pw_spectra.csv')
pul = pd.read_csv(O / 'pw_pulse_table.csv').set_index('key')
BHAM, WNR_D = 5.5e-4, 15.8


def R(key, hw=C.HW, col='rho3', signal='E* ≤ 22 MeV', days=50):
    q = t[(t.key == key) & (t.hw == hw) & (t.days == days) & (t.signal == signal)]
    return float(q[col].iloc[0])


es2, es1 = R('backn_es2_185_fw'), R('backn_es1_185_fw')
es2_def, es1_def = R('backn_es2_185'), R('backn_es1_185')
gel_nf, gel = R('gelina_10m_nf'), R('gelina_10m')
wnr_nf, wnr = R('90L_10m_nf'), R('90L_10m')
days = C.days_to_atomki

D = sd.Deck('Pulsed white neutron sources: X17 feasibility',
            'GELINA and CSNS Back-n given a proper time-of-flight treatment on the LANSCE WNR engine: what sets each one, and what would have to change.')

cover = (sd.kicker('MX17 · pulsed white sources re-examined · 9 Nov 2026')
         + '<h1 style="font-size:58px;font-weight:600;line-height:1.08;letter-spacing:-1.5px">'
           'Back-n was closed for the wrong reason; GELINA stays behind WNR</h1>'
         + sd.p('The Back-n wall is one DREAM readout per 25 Hz pulse, not Micromegas occupancy. Read the whole time-of-flight '
                'window as one event and ES#2 reaches ATOMKI, if the γ flash allows it. Neither source is a top-3 option today.', 28, sd.DMUT)
         + sd.row(sd.bignum(sci(es2, 1), 'Back-n ES#2, 185 kW, full-window readout', sd.DGREEN, f'{C.fmt_days(days(es2))} to ATOMKI. Today’s DAQ: {sci(es2_def, 1)}.'),
                  sd.bignum(sci(gel, 1), 'GELINA 10 m, 0.87 µs flash cut', sd.ORANGE, f'{sci(gel_nf, 1)} with no flash loss (isotropic upper bound on the flux).'),
                  sd.bignum(sci(wnr, 1), 'WNR 90L 10 m, same flash cut', sd.GREY, f'{sci(wnr_nf, 1)} without it (the published number).'), gap=56))
D.slide('cover', cover, dark=True, short='cover',
        notes='X17/IPC at 3σ in 50 days, E* ≤ 22 MeV, big plastics. Re-weighted from the N5/N4 Geant4 runs on the WNR engine (beam only: no room, vacuum flight tube). The engine was checked by reproducing WNR 90L 10 m (8.42e-4) and Birmingham bham_28_2m_pb5 (3.32e-4) exactly. <code>pulsed_white/FEASIBILITY.md</code>.')

D.slide('machines', sd.title('Two very different pulse structures', 'what each source delivers per pulse into the Ø8 cm or collimated spot')
        + sd.table(['', 'GELINA 10 m (upper bound)', 'Back-n ES#1, 185 kW', 'Back-n ES#2, 185 kW', 'WNR 90L 10 m'],
                   [['driver', '100 MeV e⁻, 100 µA, U target', '1.6 GeV p, W target', 'same', '800 MeV p, W target'],
                    ['pulses per second', '800', '25 (two bunches, 410 ns)', '25', '13 889 (2.5 % duty)'],
                    ['neutrons per pulse through the spot', f"{pul.loc['gelina_10m', 'n_per_pulse_full']:.2g}", f"{pul.loc['backn_es1_185', 'n_per_pulse_full']:.2g}", f"{pul.loc['backn_es2_185', 'n_per_pulse_full']:.2g}", f"{pul.loc['90L_10m', 'n_per_pulse_full']:.2g}"],
                    ['0.2–2.75 MeV arrive after flash', '0.4–1.6 µs', '2.4–8.9 µs', '3.3–12 µs', '0.4–1.6 µs'],
                    ['Micromegas occupancy, full beam', f"{pul.loc['gelina_10m', 'occ_full']:.3f}", f"{pul.loc['backn_es1_185', 'occ_full']:.2f}", f"{pul.loc['backn_es2_185', 'occ_full']:.3f}", f"{pul.loc['90L_10m', 'occ_full']:.3f}"],
                    ['gated triggers per pulse, full beam', f"{pul.loc['gelina_10m', 'mu_full']:.2f}", f"{pul.loc['backn_es1_185', 'mu_full']:.0f}", f"{pul.loc['backn_es2_185', 'mu_full']:.0f}", '0.003 (in-macropulse average)']],
                   size=24, widths=[470, 300, 300, 300, 300], align=['left'] * 5),
        short='machines',
        notes='GELINA: JRC source strength 3.4e13 n/s, isotropic at 10 m: an upper bound, because the fast flux at a named station could not be retrieved. Back-n: Tang et al. 2021 Table 1, measured. Full sources in <code>pulsed_white/FACILITY.md</code>.')

P = sd.Plot(1060, 600, x=(0.01, 200, 'log'), y=(1e5, 3e9, 'log'), xlabel='neutron energy E_n [MeV]', ylabel='E·dN/dE through the spot [n/s]')
P.xticks([(v, f'{v:g}') for v in (0.01, 0.1, 1, 10, 100)]).yticks(sd.log_ticks(5, 9))
P.band([0.2, 2.75], [1e5, 1e5], [3e9, 3e9], sd.GREEN, 0.08, tip='the 0.2-2.75 MeV window')
cols = [('GELINA 10 m (isotropic bound)', sd.ORANGE), ('Back-n ES#1, 185 kW, Φ50', sd.BLUE), ('Back-n ES#2, 185 kW, Φ60', sd.PURPLE), ('WNR 90L, 10 m', sd.GREY)]
for n, c in cols:
    q = spec[spec[n] > 1e5]
    P.line(list(q.E), list(q[n]), c, markers=False, w=4, tip=n)
D.slide('spectra', sd.title('Back-n has the flux; GELINA’s is a ceiling', 'time-averaged, before any throttle; the 0.2–2.75 MeV window is shaded')
        + sd.row(sd.col(P.svg('spectra'), sd.legend([(n, c) for n, c in cols], size=22), w=1060, gap=8),
                 sd.col(sd.p('The catalogue used the n_TOF spectrum and 2.5×10¹³ n/s for GELINA. The JRC page gives 3.4×10¹³ n/s peaking at 1–2 MeV.', 26),
                        sd.p(f'That moves the no-flash reach from 3.2×10⁻³ to {sci(gel_nf, 1)}, still an upper bound and still behind WNR.', 24, sd.MUT),
                        w=520, gap=24), gap=48),
        short='spectra',
        notes='GELINA spectrum: Watt shape (ESTIMATE); Maxwellians with T = 0.8 and 1.5 MeV give 1.10e-3 and 1.27e-3 without a flash loss. Back-n: the measured per-decade spectrum already in survey_yield.py.')

rows = [('Back-n ES#1, today’s DAQ', es1_def, sd.GREY), ('Back-n ES#2, today’s DAQ', es2_def, sd.GREY),
        ('Back-n ES#1, full-window', es1, sd.BLUE), ('Back-n ES#2, full-window', es2, sd.BLUE),
        ('GELINA 10 m, no flash loss', gel_nf, sd.ORANGE), ('GELINA 10 m, 0.87 µs cut', gel, sd.ORANGE),
        ('WNR 90L 10 m, no flash loss', wnr_nf, sd.GREY), ('WNR 90L 10 m, 0.87 µs cut', wnr, sd.GREY), ('Birmingham (full Geant4)', BHAM, sd.GREEN)]
rows = sorted(rows, key=lambda r: -r[1])
D.slide('walls', sd.title('Each source has its own wall, and it is not the one the catalogue named',
                          'X17/IPC at 3σ in 50 days, E* ≤ 22 MeV, big plastics; shorter is better; ATOMKI is 1.5×10⁻³')
        + sd.row(sd.hbars([(n, v, c, f'{n}: {v:.2g}, {C.fmt_days(days(v))} to ATOMKI') for n, v, c in rows], 1e-2, width=800, log=True, vmin=2e-4, label_w=340, fmt=lambda v: f'{v:.1e}', size=22, h=34),
                 sd.col(sd.callout('Back-n: 298 µs dead time allows one trigger per pulse, and random two-arm triggers fill it (175 per pulse at ES#1, full beam). The throttle answers DREAM, not occupancy.', sd.BLUE, 24),
                        sd.p('A beam-synchronous readout of the whole window (~150 of 512 DREAM cells) removes it. ES#1 then meets occupancy 0.93; ES#2, at 0.07, sits on its statistics floor.', 22, sd.MUT),
                        sd.p('GELINA: statistics, then the flash, because its window starts 0.4 µs after it.', 22, sd.MUT),
                        w=660, gap=14), gap=36),
        short='walls',
        notes='Full-window readout is an assumption about the existing DREAM hardware, not a tested mode: 150 samples means τ ≈ 2.2 ms, a 5.6 % loss at 25 Hz that is not included (about 3 % on the reach). The Birmingham number is full Geant4 with its room; the others are beam-only re-weightings, so it is not a like-for-like bar.')

g = f[f.hw == C.HW]
P = sd.Plot(1060, 560, x=(0.1, 40, 'log'), y=(5e-4, 3e-2, 'log'), xlabel='dead time after the flash [µs] (0 plotted at 0.1)', ylabel='X17/IPC at 3σ in 50 days')
P.xticks([(v, f'{v:g}') for v in (0.1, 0.3, 1, 3, 10, 30)]).yticks([(1e-3, '10⁻³'), (3e-3, '3×10⁻³'), (1e-2, '10⁻²')])
P.hline(C.RHO, sd.GREEN, label='ATOMKI ⁴He')
sel = [('backn_es2_185_fw', 'Back-n ES#2, full-window', sd.PURPLE), ('backn_es1_185_fw', 'Back-n ES#1, full-window', sd.BLUE),
       ('gelina_10m', 'GELINA 10 m', sd.ORANGE), ('gelina_30m', 'GELINA 30 m', sd.RED), ('90L_10m', 'WNR 90L 10 m', sd.GREY)]
for k, n, c in sel:
    q = g[(g.key == k) & np.isfinite(g.rho3)].sort_values('t_dead_us')
    P.line(list(np.maximum(q.t_dead_us, 0.1)), list(np.clip(q.rho3, 5e-4, 3e-2)), c, r=5, w=4, tip=n)
D.slide('flash', sd.title('The flash decides: long flight paths survive it, 10 m paths do not',
                          'exposure removed before the dead time ends; big plastics, best throttle; a line ends where nothing is left')
        + sd.row(sd.col(P.svg('flash scan'), sd.legend([(n, c) for _, n, c in sel], size=22), w=1060, gap=8),
                 sd.col(sd.p('Measured at n_TOF: the chamber recovers in 0.87 µs, but the DREAM front end rails for 0.5 to more than 25 ms.', 26),
                        sd.callout('Scaling that with neutrons per pulse as a proxy puts unfiltered Back-n at tens of µs or more, longer than its window. It needs a Pb filter and a test.', sd.ORANGE, 24),
                        w=520, gap=24), gap=48),
        short='flash',
        notes='The flash is modelled only as a time cut on each bin. Its size at GELINA and Back-n is not known here; the proxy is neutrons per pulse relative to n_TOF EAR2 (~7e7 above 0.1 MeV): Back-n ES#2 ×0.2, ES#1 ×0.36, GELINA 10 m ×2e-3 (an electron machine makes more γ per neutron, so this one is a lower bound). A Pb filter costs neutrons: 3-5 cm takes ES#2 to about 1.3-1.5e-3 by √flux scaling (ESTIMATE).')

D.slide('score', sd.title('Scorecard: existing beams only', 'no new machines, no facility contact yet; (ask) items are held until contact is allowed')
        + sd.table(['', 'CSNS Back-n ES#2', 'JRC GELINA 10 m'],
                   [['beam exists today', 'yes, 185 kW', 'yes; last call found: 2026 (one source)'],
                    ['reach, today’s DAQ', f'{sci(es2_def, 1)}, {C.fmt_days(days(es2_def))}', f'{sci(gel, 1)}, {C.fmt_days(days(gel))} (flash cut)'],
                    ['reach, best case', f'{sci(es2, 1)}, {C.fmt_days(days(es2))} (full-window, flash under ~3 µs)', f'{sci(gel_nf, 1)}, {C.fmt_days(days(gel_nf))} (no flash loss, flux at its bound)'],
                    ['limiting wall', 'DREAM per pulse, then the flash', 'statistics, then the flash'],
                    ['access', 'CSNS user call; foreign terms (ask); ³He cell shipped to China', 'EUFRAT, free, but Euratom-relevant work and EU-based lead'],
                    ['space, shielding', 'existing halls, size for the arms (ask)', '10 m station, hosting a 2 × 2 m apparatus (ask)'],
                    ['overall call', 'WATCH: reopened, not top-3', 'CLOSED: dominated by WNR']],
                   size=24, widths=[340, 680, 680], align=['left'] * 3),
        short='scorecard',
        notes=f'Comparison: Birmingham 5.5e-4, 6.7 d (full Geant4); WNR {WNR_D} d without a flash loss, {C.fmt_days(days(wnr))} with the same 0.87 µs cut; FRANZ 3.3e-4 at its 20 mA design, 2.2e-3 at its licence; FRM II MEDAPP 4.2e-4 with the reactor off since 2020. CSNS-II at 500 kW would give 6.2e-4 at ES#2 with full-window readout but is not an existing beam.')

end = (sd.title('What is not settled', None)
       + sd.row(sd.col(sd.p('<b>Not modelled</b>', 30, sd.DINK),
                       sd.p('• Room, dump and flight-path return: Birmingham’s full Geant4 cost ×1.7 in reach.', 26, sd.DINK),
                       sd.p('• The flash as anything other than a time cut.', 26, sd.DINK),
                       sd.p('• Only the 30 bar × 40 cm cell: the runs do not cover the capsule.', 26, sd.DINK), gap=18),
                sd.col(sd.p('<b>Can be done without any facility</b>', 30, sd.DINK),
                       sd.p('• Pulser-bench test of a 150-sample beam-synchronous DREAM readout.', 26, sd.DINK),
                       sd.p('• Geant4 of the Back-n flash with a Pb filter through the arms.', 26, sd.DINK),
                       sd.p('• The DREAM recovery scaling below the measured 0.5 ms.', 26, sd.DINK), gap=18), gap=80))
D.slide('end', end, dark=True, short='open questions')

out = D.write(O / 'pulsed-white-x17-feasibility.html',
              note_meta=dict(title='Pulsed white sources X17 feasibility',
                             summary='GELINA and CSNS Back-n with proper time of flight: which wall sets each and what would have to change.',
                             tags='x17, gelina, csns, back-n, feasibility', date='2026-11-09'),
              footer='Built by x17_facility_search/pulsed_white/deck/build_deck.py from pulsed_white/pw_beam.py outputs.')
print(out)
for k in ('backn_es2_185_fw', 'backn_es1_185_fw', 'backn_es2_185', 'backn_es1_185', 'gelina_10m', 'gelina_10m_nf', 'gelina_15m', 'gelina_30m'):
    print(k, *(f'{hw} {R(k, hw):.3g} / all {R(k, hw, signal="all E*"):.3g};' for hw in ('big plastics', 'as built')))
