"""Deck slides (2026-10-12): is the significance real once the background shape
is uncertain?  ATOMKI's bump at truth level, the symmetric-pair cut, the ladder
of fit assumptions, and the control samples.

Reads lnl/out/syst/*.csv (lnl/sim/lnl_syst.py).  Called from build_deck.py
right after the reach slide; ``numbers(O)`` gives the headline figures that the
cover and the reach slide quote.
"""
import json

import numpy as np
import pandas as pd

import slidedoc as sd

AB, BP = 'as built', 'big plastics'


def load(O):
    S_ = O / 'syst'
    return dict(lad=pd.read_csv(S_ / 'ladder.csv'), yc=pd.read_csv(S_ / 'ycut.csv'),
                dl=pd.read_csv(S_ / 'delta_scan.csv'), sp=pd.read_csv(S_ / 'spectra_10d.csv'),
                atk=pd.read_csv(S_ / 'atomki_repro.csv'),
                summ=json.loads((S_ / 'summary.json').read_text()))


def numbers(O):
    """Headline days: statistics only vs |y| < 0.3 with 2 % unknown structure + in-run controls."""
    lad = load(O)['lad']

    def d(hw, ycat, short, col='days_3sigma'):
        return lad[(lad.hw == hw) & (lad.ycat == ycat) & (lad.short == short)][col].iloc[0]
    return dict(ab_stat=d(AB, 'all', 'count'), bp_stat=d(BP, 'all', 'count'),
                ab_robust_z30=d(AB, 'y<0.3', '+ in-run ctrl', 'Z_30d'), bp_robust_z30=d(BP, 'y<0.3', '+ in-run ctrl', 'Z_30d'),
                ab_robust=d(AB, 'y<0.3', '+ in-run ctrl'), bp_robust=d(BP, 'y<0.3', '+ in-run ctrl'),
                ab_all_s2=d(AB, 'all', 'struct 2 %'), bp_all_s2=d(BP, 'all', 'struct 2 %'),
                ab_y3_s2=d(AB, 'y<0.3', 'struct 2 %'), bp_y3_s2=d(BP, 'y<0.3', 'struct 2 %'))


def fd(d):
    if not np.isfinite(d) or d > 9999:
        return '> 10⁴'
    return f'{d:,.0f}' if d >= 10 else f'{d:.1f}'


def syst_slides(D, O):
    L = load(O)
    lad, yc, dl, sp, atk, summ = L['lad'], L['yc'], L['dl'], L['sp'], L['atk'], L['summ']
    N = numbers(O)

    # ---- 1. ATOMKI at truth level ---------------------------------------- #
    sty = [('ATOMKI 2016 as published: M1 + 23 % E1, |y| ≤ 0.5, σ 3°', sd.BLUE, None, 'ATOMKI cuts and mix'),
           ('our mix: 52 % E1 (direct capture), |y| ≤ 0.5, σ 3°', sd.ORANGE, None, 'our M1/E1 mix, ATOMKI cuts'),
           ('our mix, no y cut, σ 5° (≈ our Geant4 selection)', sd.GREY, '8 6', 'our mix, no |y| cut (as our Geant4 headline)'),
           ('pure M1, |y| ≤ 0.5, σ 3°', sd.GREEN, '3 5', 'pure M1 IPC')]
    P = sd.Plot(1000, 620, x=(80, 180, 'lin'), y=(-5, 50, 'lin'), xlabel='e⁺e⁻ opening angle [°] (10° bins)',
                ylabel='X17 excess over the IPC [%]')
    P.xticks([(v, f'{v}°') for v in range(80, 181, 20)]).yticks([(v, f'{v}') for v in (0, 10, 20, 30, 40, 50)])
    P.hline(0, sd.MUT, dash=None, w=1.5)
    for case, col, dash, lab in sty:
        g = atk[(atk.case == case) & (atk.theta >= 85)]
        P.line(list(g.theta), list((g.ratio - 1) * 100), col, 4 if dash is None else 3, dash=dash, r=5,
               tips=[f'{lab}, {t:.0f}°: +{(v - 1) * 100:.0f} %' for t, v in zip(g.theta, g.ratio)])
    f4 = pd.DataFrame(dict(theta=[85, 95, 105, 115, 125, 135, 145, 155, 165],
                           data=[0.0461, 0.0373, 0.0275, 0.0219, 0.0200, 0.0216, 0.0206, 0.0162, 0.0136],
                           ipc=[0.0461, 0.0373, 0.0277, 0.0224, 0.0198, 0.0172, 0.0153, 0.0134, 0.0121]))
    P.points(list(f4.theta), list((f4.data / f4.ipc - 1) * 100), sd.INK, r=9, marker='diamond',
             tips=[f'ATOMKI 2016 Fig. 4, {t}°: data {a:.4f} vs no-boson curve {b:.4f} (+{(a / b - 1) * 100:.0f} %)'
                   for t, a, b in zip(f4.theta, f4.data, f4.ipc)])
    a_ = summ['atomki']
    side = sd.col(
        sd.legend([(lab, col, 'dash' if d else 'line') for _, col, d, lab in sty] + [('ATOMKI 2016 Fig. 4 (read off)', sd.INK, 'dot')], 20),
        sd.callout('<b>Not raw counts, not background-subtracted.</b> ATOMKI plot acceptance-corrected correlations (acceptance from '
                   'event-mixed singles), cosmics subtracted (2022), on a log scale. The IPC is a simulated M1+E1 curve fitted at small angles; '
                   'the anomaly <i>is</i> data minus that curve. Their 6.8σ also assumes the IPC shape.', sd.BLUE, 21),
        sd.callout(f'<b>The bump is +{a_["atomki_fig4_excess_145"] * 100:.0f} % at 145°, not a peak.</b> Same scattering as ours (carbon-fibre tube, '
                   '10 µm Al backing). What makes it visible: 10° bins with ~3 % errors, and cuts.', sd.ORANGE, 21),
        sd.callout(f'<b>Their cut and mix give ×3.4 in S/B:</b> |y| ≤ 0.5 ×2, a 23 % instead of 52 % E1 share ×1.7. Even so, R = 5.8×10⁻⁶ gives half their '
                   f'excess in our generator: their figure needs R ≈ {a_["R_needed_for_fig4"] * 1e5:.1f}×10⁻⁵. Our signal is the conservative end.', sd.PURPLE, 21),
        gap=12, w=640)
    D.slide('atomki-bump', sd.title('ATOMKI\'s bump is only +25–35 %; their cuts make it visible',
                                    'Truth level, acceptance-corrected: Born IPC (M1, E1) + X17 (m = 16.7) at R = 5.8×10⁻⁶, 18.15 MeV, both leptons > 2 MeV. Hover the points.')
            + sd.row(P.svg('ATOMKI excess at truth level'), side, gap=28),
            f"""<p>You can't see our X17 by eye because S/B in the window is ~7 % (§0 table: per day {lad[(lad.hw == BP) & (lad.short == 'count') & (lad.ycat == 'all')].S_per_day.iloc[0]:.0f}
X17 against {lad[(lad.hw == BP) & (lad.short == 'count') & (lad.ycat == 'all')].B_per_day.iloc[0]:,.0f} background with big plastics). The headline days were S/√B with B known exactly, so the
significance came entirely from statistics.</p>
<p>ATOMKI 2016 (PRL 116 042501) Fig. 4 was digitised at 300 dpi (±3 % reading error). The data sit 26 %, 35 % and 21 % above the
dashed no-boson curve at 135°, 145° and 155°. Sas <i>et al.</i> 2022 (arXiv:2205.07744): raw correlations, cosmic background subtracted,
divided by the detector response; the anomaly is "the difference of the experimental and simulated distributions", with E1 and M1
fitted below ~110°. Their E1 share at 1.10 MeV moved from 23 % (2016) to ≳ 50 % (2022).</p>
<p>Generators: <code>lnl_rates.ipc_vectors</code> (Born, nTof_x17 ipc_born) and <code>x17_vectors</code>, 8Be* at rest, 2×10⁶ each, weighted by
Born α (ipc_alpha.csv) and the γ share. "R needed" scales R until the as-published case matches their +35 % at 145°. Leftover
differences: their efficiency vs lepton energy and y, the definition of the E1 share, and the 3.9×10⁻³ IPC coefficient they quote.</p>""",
            foot='lnl/out/syst/atomki_repro.csv (lnl/sim/lnl_syst.py --atomki part); ATOMKI read off arXiv:1504.01527 Fig. 4', short='ATOMKI bump')

    # ---- 2. the symmetric cut -------------------------------------------- #
    def spec_plot(ycat, ttl, ylab):
        g = sp[(sp.hw == BP) & (sp.ycat == ycat)]
        b = np.add.reduceat(g.B_10d.values, np.arange(0, len(g), 5))
        s = np.add.reduceat(g.S_10d.values, np.arange(0, len(g), 5))
        e = np.arange(90, 181, 10)
        top = 1.15 * (b + s).max()
        Q = sd.Plot(560, 520, x=(90, 180, 'lin'), y=(0, top, 'lin'), xlabel='opening angle [°]', ylabel=ylab,
                    margin=(56, 20, 92, 110), title=ttl)
        step = 2000 if top > 6000 else 1000
        Q.xticks([(v, f'{v}°') for v in (90, 120, 150, 180)]).yticks([(v, f'{v / 1000:.0f}k') for v in range(0, int(top), step)])
        for i in range(len(b)):
            Q.raw(f'<rect x="{Q.X(e[i]):.1f}" y="{Q.Y(b[i]):.1f}" width="{Q.X(e[i + 1]) - Q.X(e[i]):.1f}" height="{Q.Y(0) - Q.Y(b[i]):.1f}" '
                  f'fill="{sd.GREY}" fill-opacity="0.45"/>', back=True)
            Q.raw(f'<rect x="{Q.X(e[i]):.1f}" y="{Q.Y(b[i] + s[i]):.1f}" width="{Q.X(e[i + 1]) - Q.X(e[i]):.1f}" '
                  f'height="{Q.Y(b[i]) - Q.Y(b[i] + s[i]):.1f}" fill="{sd.RED}"'
                  f'{sd.tipattr(f"{e[i]}–{e[i + 1]}°: background {b[i]:,.0f}, X17 {s[i]:.0f} (+{s[i] / b[i] * 100:.0f} %, {s[i] / np.sqrt(b[i]):.1f}σ in this bin)")}/>')
        return Q.svg(ttl)
    ycb = yc[yc.hw == BP].set_index('ycat')
    yca = yc[yc.hw == AB].set_index('ycat')
    rows = []
    for yy, lab in (('all', 'all pairs'), ('y<0.5', '|y| < 0.5'), ('y<0.3', '|y| < 0.3'), ('y<0.2', '|y| < 0.2')):
        r = ycb.loc[yy]
        rows.append((lab, r.SB_best * 100, sd.PURPLE if yy == 'y<0.3' else sd.GREY,
                     f'{lab}, big plastics: keeps {r.eff_X17 * 100:.0f} % of the X17 and {r.eff_B * 100:.0f} % of the background in 130–160°; '
                     f'best window {r.best_win}°, S/B {r.SB_best * 100:.0f} %; statistics-only {r.days_count:.2f} d '
                     f'(as built: S/B {yca.loc[yy].SB_best * 100:.0f} %, {yca.loc[yy].days_count:.0f} d)'))
    side = sd.col(
        sd.p('S/B in the best window, big plastics', 22, weight=600),
        sd.hbars(rows, 25, width=200, h=28, label_w=170, fmt=lambda v: f'{v:.0f} %', size=21),
        sd.callout('<b>|y| = |E₁ − E₂| / (E₁ + E₂)</b> from the two arm energies (no charge needed). An X17 at the edge angle '
                   f'shares its energy equally: {ycb.loc["y<0.5"].eff_X17 * 100:.0f} % have |y| &lt; 0.5. The IPC at 140° is often lopsided.', sd.PURPLE, 21),
        sd.callout(f'<b>|y| &lt; 0.3 keeps {ycb.loc["y<0.3"].eff_X17 * 100:.0f} % of the X17 and {ycb.loc["y<0.3"].eff_B * 100:.0f} % of the IPC.</b> '
                   'Statistics barely change (S/√B ×1.2), but S/B goes ×2.6, and S/B is what systematics eat.', sd.BLUE, 21),
        sd.callout('ATOMKI use |y| ≤ 0.5 and show the asymmetric pairs as their null check. So can we.', sd.GREY, 21),
        gap=12, w=560)
    D.slide('symmetric', sd.title('Symmetric pairs: the X17 splits its energy evenly, the IPC does not',
                                  'Ten days at 1 µA with big plastics, MM 15° + TOF, E_sum 13–18 MeV, 10° bins: background (grey) and X17 at the ATOMKI ratio (red). Hover the bins.')
            + sd.row(spec_plot('all', 'all pairs', 'pairs per 10° in 10 days'), spec_plot('y<0.3', '|y| < 0.3', None), side, gap=14),
            """<p>Geant4 tables (L1 X17, L2 IPC), the same selection as the reach slide plus a cut on the measured energy asymmetry of the two
arms. E₁, E₂ are SiPM + plastic + LS of each arm, so containment smears y. In 130–160°, 99 % of the X17 have measured |y| &lt; 0.5
(truth 100 %), against ~60 % of the M1 and ~77 % of the E1 IPC. At |y| &lt; 0.3: 69 % of the X17, 23–27 % of M1, 39–44 % of E1.</p>
<p>The best window shrinks to 130–146°: symmetric X17 pairs pile up at the minimum opening angle, the edge. The IPC templates are
KDE-smoothed (5°). With the cut only ~170 M1 and ~1400 E1 IPC MC events are left in 130–160° for big plastics, and 12 and 112 as built.
A larger L2 run is needed before quoting the as-built numbers.</p>""",
            foot='lnl/out/syst/ycut.csv, spectra_10d.csv', short='Symmetric pairs')

    # ---- 3. the ladder ---------------------------------------------------- #
    order = list(lad[(lad.hw == BP) & (lad.ycat == 'all')].sort_values('step').short)
    labs = dict(zip(lad.short, lad.rung))
    cols_ = [(AB, 'all'), (AB, 'y<0.3'), (BP, 'all'), (BP, 'y<0.3')]
    trs, tips = [], []
    pretty = {'count': 'counting, B exact (the old headline)', 'fit 1 norm': 'fit, IPC shape exact',
              'M1/E1 free': '+ M1, E1, γ₁ norms free', 'detector ±2 %': '+ calibrated detector (±10 % res., ±2 % E, ±2 % acc.)',
              'acc. free': '+ acceptance shape free (cubic)', 'struct 1 %': '+ 1 % unknown structure',
              'struct 2 %': '+ 2 % unknown structure', 'struct 2 %, ℓ 5°': '  … 2 % at 5° scale (edge-like)',
              '+ in-run ctrl': '2 % + in-run controls', '+ 441 keV': '  … + 441 keV run (¼ time)'}
    for s in order:
        cells = [pretty.get(s, s)]
        for hw, ycat in cols_:
            r = lad[(lad.hw == hw) & (lad.ycat == ycat) & (lad.short == s)].iloc[0]
            v = r.days_3sigma
            col = sd.GREEN if v <= 7 else (sd.INK if v <= 30 else sd.RED)
            cells.append(f'<span style="color:{col};font-weight:600">{fd(v)} d</span>'
                         f'<span style="color:{sd.MUT};font-size:19px"> · {r.Z_30d:.1f}σ</span>')
        trs.append(cells)
        tips.append(labs[s])
    tab = sd.table(['fit assumption', 'as built<br>all pairs', 'as built<br>|y| &lt; 0.3', 'big plastics<br>all pairs', 'big plastics<br>|y| &lt; 0.3'],
                   trs, size=21, widths=[560, 250, 250, 250, 250], tips=tips)
    D.slide('ladder', sd.title('Without the symmetric cut, the IPC shape sets the reach',
                               'Days to 3σ at R(ATOMKI), 1 µA · significance after 30 days. Each row adds freedom to the fit. Green ≤ 1 week, red > 30 d.')
            + tab
            + sd.row(sd.callout(f'<b>All pairs:</b> a 2 % unknown wiggle in the IPC shape turns {fd(N["bp_stat"])} d into {fd(N["bp_all_s2"])} d with big plastics, '
                                f'and {fd(N["ab_stat"])} d into {fd(N["ab_all_s2"])} d as built. At S/B ≈ 7 % a few % of shape error looks like the signal.', sd.RED, 20),
                     sd.callout(f'<b>|y| &lt; 0.3:</b> S/B ≈ 18 %, so the same 2 % costs little: {fd(N["bp_y3_s2"])} d with big plastics. '
                                f'With in-run controls: <b>{fd(N["bp_robust"])} d</b> big plastics, <b>{fd(N["ab_robust"])} d</b> as built.', sd.GREEN, 20), gap=40),
            """<p>Asimov/Fisher on 2° bins, 90–180°, background-only expectation; σ(R) from the inverse Fisher matrix with priors added.
Rows, cumulative unless marked:</p>
<ul><li><b>counting</b>: S/√B in the best ≥ 10° window, B exact (the old headline).</li>
<li><b>fit, shape exact</b>: one IPC normalisation and one γ₁ normalisation free.</li>
<li><b>M1, E1, γ₁ free</b>: the resonant/direct mix is learned from the data (its own large-angle shape).</li>
<li><b>calibrated detector</b>: angular-resolution scale ±10 % (reco − truth scaled), E_sum scale ±2 %, and a multiplicative
acceptance 1 + Σaₙ Pₙ(x), n = 1–3, ±2 % each.</li>
<li><b>acceptance free</b>: the same cubic with no prior.</li>
<li><b>unknown structure δ</b>: a Gaussian process on the IPC shape (relative amplitude δ, correlation length 10° ≈ the X17 peak width).
These are the "detector effects and contributions we aren't expecting". At ℓ = 5° it mimics the sharp X17 edge.</li>
<li><b>in-run controls</b>: the asymmetric pairs (|y| ≥ 0.3) and the γ₁ E_sum side band (9–13 MeV) of the same run. They share the 2 %
structure, the acceptance cubic, the resolution and E scales and the M1/E1/γ₁ norms. Each also gets 1 % structure of its own
(the transfer error) and ±5 % normalisation (the MC category split). For "all pairs" only the γ₁ side band is available.</li>
<li><b>441 keV</b>: a ¼-length run on the 17.64 MeV resonance, no X17 assumed; counted in the beam days.</li></ul>
<p>Mass 16.7, Li₂O 300 µg/cm² at 1.10 MeV, MM 15° + TOF, E_sum 13–18 (big plastics) / 13–17 (as built), DREAM live time included.
The as-built IPC templates rest on few MC events (12 M1 in 130–160° at |y| &lt; 0.3): treat that column as indicative.</p>""",
            foot='lnl/out/syst/ladder.csv (lnl/sim/lnl_syst.py)', short='Systematics')

    # ---- 4. controls: days vs δ -------------------------------------------- #
    Q = sd.Plot(1000, 620, x=(0, 5.2, 'lin'), y=(0.5, 3e3, 'log'), xlabel='unknown structure δ in the IPC shape [%]',
                ylabel='beam days to 3σ at R(ATOMKI)')
    Q.xticks([(v, f'{v:g}') for v in (0, 1, 2, 3, 4, 5)]).yticks([(v, f'{v:g}') for v in (1, 3, 10, 30, 100, 300, 1000, 3000)])
    Q.hline(30, sd.GOLD, label='30 days')
    for (hw, ycat), col in (((BP, 'y<0.3'), sd.GREEN), ((BP, 'all'), sd.GREEN), ((AB, 'y<0.3'), sd.BLUE), ((AB, 'all'), sd.BLUE)):
        g = dl[(dl.hw == hw) & (dl.ycat == ycat)]
        tag = f'{hw}, {"all pairs" if ycat == "all" else "|y| < 0.3"}'
        dash = None if ycat != 'all' else '10 7'
        Q.line(list(g.delta * 100), [min(v, 3e3) for v in g.days_sig_only], col, 3, dash=dash, r=5, marker='open',
               tips=[f'{tag}, signal run only, δ = {d * 100:g} %: {fd(v)} d' for d, v in zip(g.delta, g.days_sig_only)])
        Q.line(list(g.delta * 100), [min(v, 3e3) for v in g.days_inrun_ctrl], col, 4, dash=dash, r=6,
               tips=[f'{tag}, + in-run controls (transfer δ/2), δ = {d * 100:g} %: {fd(v)} d' for d, v in zip(g.delta, g.days_inrun_ctrl)])
    side = sd.col(
        sd.legend([('big plastics', sd.GREEN, 'line'), ('as built', sd.BLUE, 'line'), ('solid: |y| < 0.3 · dashed: all pairs', sd.MUT, 'line'),
                   ('open: signal run only · filled: + in-run controls', sd.MUT, 'dot')], 20),
        sd.callout('<b>The controls come free with the run:</b> asymmetric pairs (|y| ≥ 0.3, no X17: ATOMKI\'s own null check) and the γ₁ '
                   'side band (15 MeV pairs at lower E_sum). They see the same detector, so they measure the acceptance shape.', sd.BLUE, 21),
        sd.callout('<b>441 keV (17.64 MeV)</b> is the physics null: ATOMKI 2016 saw nothing there, 2022 "much smaller". It adds little to the shape. '
                   '<b>0.80 MeV is not a null:</b> ATOMKI 2022 claim the X17 in direct capture.', sd.GREY, 21),
        sd.callout('<b>Event mixing</b> (singles from different events, as ATOMKI) measures the two-arm geometric acceptance without '
                   'pair correlations. That would be a third handle, not modelled here.', sd.GREY, 21),
        gap=12, w=620)
    D.slide('controls', sd.title('With symmetric pairs and in-run controls, shape errors cost little',
                                 'Days to 3σ against the size of unknown structure in the background shape (Gaussian process, ℓ = 10°). Hover the points.')
            + sd.row(Q.svg('days vs unknown structure'), side, gap=28),
            """<p>Same fit as the ladder (M1/E1/γ₁ free, ±10 % resolution, ±2 % E scale, acceptance cubic free). "Signal run only": the
structure δ is unconstrained except by the signal category itself. "+ in-run controls": δ is shared by the signal category, the
asymmetric pairs and the γ₁ side band; each has its own δ/2 structure (the transfer error) and ±5 % normalisation. As built, all
pairs: past δ ≈ 1 % no amount of beam reaches 3σ in a year.</p>
<p>What δ to expect: the template MC alone (KDE, 5°) carries ~3–5 % per bin with today's L2 statistics. A real analysis needs ×10–100
more IPC MC, and an acceptance check from event mixing and the 441 keV run.</p>""",
            foot='lnl/out/syst/delta_scan.csv (lnl/sim/lnl_syst.py)', short='Controls')
