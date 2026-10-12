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
                ladm=pd.read_csv(S_ / 'ladder_mass.csv'), dlm=pd.read_csv(S_ / 'delta_scan_mass.csv'),
                spm=pd.read_csv(S_ / 'spectra_10d_mass.csv'),
                summ=json.loads((S_ / 'summary.json').read_text()))


def numbers(O):
    """Headline days.  'robust' = fitted in m_ee, all pairs, 2 % unknown structure in the
    background shape + in-run controls (γ₁ side band).  θ-fit numbers kept as *_theta."""
    L = load(O)
    lad, ladm = L['lad'], L['ladm']

    def d(hw, ycat, short, col='days_3sigma', t=None):
        t = lad if t is None else t
        return t[(t.hw == hw) & (t.ycat == ycat) & (t.short == short)][col].iloc[0]
    return dict(ab_stat=d(AB, 'all', 'count'), bp_stat=d(BP, 'all', 'count'),
                ab_robust=d(AB, 'all', '+ in-run ctrl', t=ladm), bp_robust=d(BP, 'all', '+ in-run ctrl', t=ladm),
                ab_robust_z30=d(AB, 'all', '+ in-run ctrl', 'Z_30d', ladm), bp_robust_z30=d(BP, 'all', '+ in-run ctrl', 'Z_30d', ladm),
                ab_mass_stat=d(AB, 'all', 'count', t=ladm), bp_mass_stat=d(BP, 'all', 'count', t=ladm),
                ab_mass_s2=d(AB, 'all', 'struct 2 %', t=ladm), bp_mass_s2=d(BP, 'all', 'struct 2 %', t=ladm),
                ab_theta_robust=d(AB, 'y<0.3', '+ in-run ctrl'), bp_theta_robust=d(BP, 'y<0.3', '+ in-run ctrl'),
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
    symmetric_why(D, O)
    mass_slide(D, O)

    # ---- 3. the ladder ---------------------------------------------------- #
    order = list(lad[(lad.hw == BP) & (lad.ycat == 'all')].sort_values('step').short)
    labs = dict(zip(lad.short, lad.rung))
    ladm = L['ladm']
    cols_ = [(AB, 'all', lad), (AB, 'y<0.3', lad), (AB, 'all', ladm), (BP, 'all', lad), (BP, 'y<0.3', lad), (BP, 'all', ladm)]
    trs, tips = [], []
    pretty = {'count': 'counting, B exact (the old headline)', 'fit 1 norm': 'fit, IPC shape exact',
              'M1/E1 free': '+ M1, E1, γ₁ norms free', 'anisotropy': '+ γ* anisotropy (a₁, a₂)',
              'detector ±2 %': '+ calibrated detector (±10 % res., ±2 % E, ±2 % acc.)',
              'acc. free': '+ acceptance shape free (cubic)', 'struct 1 %': '+ 1 % unknown structure',
              'struct 2 %': '+ 2 % unknown structure', 'struct 2 %, ℓ 5°': '  … 2 % at 5° scale (edge-like)',
              '+ in-run ctrl': '2 % + in-run controls', '+ 441 keV': '  … + 441 keV run (¼ time)'}
    for s in order:
        cells = [pretty.get(s, s)]
        for hw, ycat, tb in cols_:
            r = tb[(tb.hw == hw) & (tb.ycat == ycat) & (tb.short == s)].iloc[0]
            v = r.days_3sigma
            col = sd.GREEN if v <= 7 else (sd.INK if v <= 30 else sd.RED)
            cells.append(f'<span style="color:{col};font-weight:600">{fd(v)} d</span>'
                         f'<span style="color:{sd.MUT};font-size:17px"> · {r.Z_30d:.1f}σ</span>')
        trs.append(cells)
        tips.append(labs[s])
    tab = sd.table(['fit assumption', 'as built<br>θ, all', 'as built<br>θ, |y| &lt; 0.3', 'as built<br><b>m_ee</b>, all',
                    'big plastics<br>θ, all', 'big plastics<br>θ, |y| &lt; 0.3', 'big plastics<br><b>m_ee</b>, all'],
                   trs, size=19, widths=[470, 200, 200, 200, 200, 200, 200], tips=tips)
    D.slide('ladder', sd.title('Fitting the angle alone, the IPC shape sets the reach; fitting m_ee, it does not',
                               'Days to 3σ at R(ATOMKI), 1 µA · significance after 30 days. Each row adds freedom to the fit. Green ≤ 1 week, red > 30 d.')
            + tab
            + sd.row(sd.callout(f'<b>θ, all pairs:</b> a 2 % unknown wiggle in the IPC shape turns {fd(N["bp_stat"])} d into {fd(N["bp_all_s2"])} d with big plastics, '
                                f'and {fd(N["ab_stat"])} d into {fd(N["ab_all_s2"])} d as built: at S/B ≈ 7 % shape error looks like signal.', sd.RED, 19),
                     sd.callout(f'<b>m_ee:</b> the X17 is a narrow peak on a smooth continuum, so the same 2 % costs little: '
                                f'{fd(N["bp_mass_s2"])} d big plastics, {fd(N["ab_mass_s2"])} d as built; with the γ₁ side band '
                                f'<b>{fd(N["bp_robust"])} d</b> and <b>{fd(N["ab_robust"])} d</b>.', sd.GREEN, 19), gap=40),
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
    checks_slide(D, O)


def symmetric_why(D, O):
    """How |y| separates X17 from IPC, where the statistics go when we cut, and
    why it is an offline cut (2026-10-12, Dylan's question)."""
    S_ = O / 'syst'
    m2 = pd.read_csv(S_ / 'y_theta_map.csv')
    m1 = pd.read_csv(S_ / 'y_window.csv')
    sc = pd.read_csv(S_ / 'y_scan.csv')
    hw = BP
    g2 = m2[m2.hw == hw].pivot_table(index=['theta_lo', 'y_lo'], columns='comp', values='per_day').reset_index()

    # ---- panel 1: S/B in (θ, |y|) -------------------------------------------- #
    A = sd.Plot(540, 470, x=(90, 180, 'lin'), y=(0, 1, 'lin'), xlabel='opening angle [°]', ylabel='|y| = |E₁ − E₂| / (E₁ + E₂)',
                margin=(56, 20, 92, 110), title='X17 / background per cell, one day')
    A.xticks([(v, f'{v}°') for v in (90, 120, 150, 180)]).yticks([(v, f'{v:.1f}') for v in (0, 0.2, 0.4, 0.6, 0.8, 1.0)])
    cells = []
    for r in g2.itertuples():
        sb = r.X17 / r.IPC if r.IPC > 0.5 else float('nan')
        cells.append((r.theta_lo, r.theta_lo + 5, r.y_lo, r.y_lo + 0.05, sb,
                      f'{r.theta_lo:.0f}–{r.theta_lo + 5:.0f}°, |y| {r.y_lo:.2f}–{r.y_lo + 0.05:.2f}: '
                      f'X17 {r.X17:.1f}/day, background {r.IPC:.0f}/day, S/B {sb * 100:.0f} %' if r.IPC > 0.5 else None))
    cmap = [(0.0, '#f4f1f6'), (0.5, '#b58bbb'), (1.0, '#4b1d52')]
    A.cells(cells, 0, 0.4, cmap=cmap, gap=0.5)
    A.hline(0.3, sd.RED, dash='8 6', w=3, label='cut |y| < 0.3')
    for mm, dash in ((16.7, None), (16.0, '4 5'), (17.25, '4 5')):
        th = np.linspace(90, 180, 181)
        arg = 1 - 2 * mm ** 2 / (18.15 ** 2 * (1 - np.cos(np.radians(th))))
        ok = arg >= 0
        A.line(list(th[ok]), list(np.sqrt(arg[ok])), sd.BLUE, 3 if dash is None else 2, dash=dash, markers=False,
               tip=f'constant pair mass m_ee = {mm} MeV: (1 − y²)(1 − cos θ) = 2m²/W²')
    cb = sd.colorbar(110, 440, 0, 0.4, [(0, '0'), (0.1, '10 %'), (0.2, '20 %'), (0.3, '30 %'), (0.4, '≥ 40 %')], 'S/B', cmap=cmap)

    # ---- panel 2: |y| in the window ------------------------------------------ #
    w1 = m1[m1.hw == hw].pivot_table(index='y_lo', columns='comp', values='per_day').reset_index()
    xs = list(w1.y_lo) + [1.0]
    sX, sB = w1.X17 / w1.X17.sum(), w1.IPC / w1.IPC.sum()
    B_ = sd.Plot(520, 470, x=(0, 1, 'lin'), y=(0, 0.25, 'lin'), xlabel='|y| in 130–160°', ylabel='fraction per 0.05',
                 margin=(56, 20, 92, 104), title='energy sharing in the window')
    B_.xticks([(v, f'{v:.1f}') for v in (0, 0.2, 0.4, 0.6, 0.8, 1.0)]).yticks([(v, f'{v:.2f}') for v in (0, 0.05, 0.1, 0.15, 0.2, 0.25)])
    B_.raw(f'<rect x="{B_.X(0):.1f}" y="{B_.y0}" width="{B_.X(0.3) - B_.X(0):.1f}" height="{B_.ph}" fill="{sd.GREEN}" fill-opacity="0.08"/>', back=True)
    xx, yy = sd.step_xy(xs, list(sB))
    B_.line(xx, yy, sd.GREY, 4, markers=False, tip=f'Background (IPC γ₀ + γ₁) in 130–160°: {w1.IPC.sum():,.0f}/day; spread over all |y|')
    xx, yy = sd.step_xy(xs, list(sX))
    B_.line(xx, yy, sd.RED, 4, markers=False, tip=f'X17 in 130–160°: {w1.X17.sum():.0f}/day at R(ATOMKI); almost all below |y| = 0.45')
    B_.vline(0.3, sd.RED, dash='8 6')
    kx, kb = sX[w1.y_lo < 0.3].sum(), sB[w1.y_lo < 0.3].sum()
    B_.text(0.32, 0.23, f'kept: {kx * 100:.0f} % of X17, {kb * 100:.0f} % of bkg', 20, sd.INK)

    # ---- panel 3: the scan ------------------------------------------------------ #
    s = sc[sc.hw == hw].sort_values('ycut')
    C = sd.Plot(500, 470, x=(0.05, 1.0, 'lin'), y=(0.5, 30, 'log'), xlabel='cut: keep |y| below', ylabel='beam days to 3σ',
                margin=(56, 20, 92, 96), title='days to 3σ against the cut')
    C.xticks([(v, f'{v:.1f}') for v in (0.2, 0.4, 0.6, 0.8, 1.0)]).yticks([(v, f'{v:g}') for v in (0.5, 1, 2, 5, 10, 20)])
    for col, lab, c in (('days_count', 'statistics only (shape exact)', sd.GREY),
                        ('days_struct2', '2 % unknown shape, no controls', sd.ORANGE),
                        ('days_ctrl', '2 % shape + in-run controls', sd.GREEN)):
        C.line(list(s.ycut), [min(v, 30) for v in s[col]], c, 4, r=6,
               tips=[f'{lab}, |y| < {yc:g}: {v:.2f} d; S/B {sb * 100:.0f} % ({w}°); X17 {sx:.0f}, bkg {bb:,.0f} per day in 130–160°'
                     for yc, v, sb, w, sx, bb in zip(s.ycut, s[col], s.SB_best, s.best_win, s.S_130_160, s.B_130_160)])
    C.vline(0.3, sd.RED, dash='8 6')
    side_leg = sd.legend([('stats only', sd.GREY), ('2 % shape', sd.ORANGE), ('+ controls', sd.GREEN)], 18)

    r3, r10 = s[s.ycut == 0.3].iloc[0], s[s.ycut == 1.0].iloc[0]
    D.slide('symmetric-why', sd.title('Why |y| works, where the statistics go, and why it is offline',
                                      'Big plastics, 1 µA, MM 15° + TOF, E_sum 13–18 MeV, Geant4. Hover the cells, curves and points.')
            + sd.row(sd.col(A.svg('S/B map'), gap=0), cb, B_.svg('|y| in the window'), sd.col(C.svg('days vs cut'), side_leg, gap=4), gap=4)
            + sd.row(
                sd.callout('<b>Why.</b> An X17 is a particle of fixed mass. Its pairs reach the smallest opening angle '
                           '(the ~134° edge) only when the two leptons share the energy equally. An IPC pair at 140° is a virtual photon '
                           'of any mass, with any energy split. The X17 band is a line of constant pair mass (blue, left): next slide.', sd.PURPLE, 19),
                sd.callout(f'<b>Where the statistics go.</b> |y| &lt; 0.3 keeps {r3.S_130_160:.0f} of {r10.S_130_160:.0f} X17 '
                           f'but only {r3.B_130_160:,.0f} of {r10.B_130_160:,.0f} background a day (130–160°). '
                           f'S/√B barely changes (statistics-only days {r10.days_count:.2f} → {r3.days_count:.2f}). '
                           f'S/B goes {r10.SB_best * 100:.0f} → {r3.SB_best * 100:.0f} %, so a shape error '
                           f'costs {r10.days_struct2:.0f} → {r3.days_struct2:.1f} d.', sd.BLUE, 19),
                sd.callout('<b>Offline, not trigger.</b> The trigger stays the two-arm leg coincidence; E₁ and E₂ are recorded for every pair. '
                           'The cut is chosen after the run, and the rejected pairs are the control sample. Fix it blind '
                           '(on Monte Carlo, 441 keV, asymmetric pairs), not by tuning on the 140° bump.', sd.GREEN, 19),
                gap=28),
            f"""<p>|y| is computed from the two arms' measured energies (SiPM bar + plastic + LS), so it needs no charge sign and no
magnetic field. The arm energies contain the leptons only partly, so measured |y| is smeared. Still, 99 % of X17 pairs in 130–160°
have |y| &lt; 0.5, and about half of the IPC has |y| &gt; 0.3. The left map is X17/background per 5° × 0.05 cell (cells with
&lt; 0.5 background a day left blank). The best cells sit at 130–145° and |y| &lt; 0.2.</p>
<p>The scan (right): statistics alone barely care about the cut between 0.3 and 0.5 (the X17 lives below 0.45). With a 2 % unknown
structure in the IPC shape (Gaussian process, ℓ = 10°), the best is 0.2–0.3. The asymmetric pairs that the cut throws away are then
used as a control (green), which brings the robust number back to the statistics-only one. The background includes the γ₀ IPC
anisotropy about the beam (a₂ = 0.36, Hayes <i>et al.</i> 2021).</p>
<p>Because the cut is offline, nothing is lost by choosing it later. The one rule is to fix it without looking at the signal region,
or to quote the look-elsewhere/trials cost of scanning it.</p>""",
            foot='lnl/out/syst/y_theta_map.csv, y_window.csv, y_scan.csv (lnl/sim/lnl_syst.py)', short='Why |y|')


def mass_slide(D, O):
    """Fit the reconstructed mass, not the opening angle (2026-10-12)."""
    L = load(O)
    spm, ladm, lad = L['spm'], L['ladm'], L['lad']
    N = numbers(O)

    def mplot(hw, ttl, ylab):
        g = spm[(spm.hw == hw) & (spm.ycat == 'all')]
        e0 = g.theta.values - 0.125
        keep = (e0 >= 12) & (e0 < 19)
        b = np.add.reduceat(g.B_10d.values[keep], np.arange(0, keep.sum(), 2))
        s = np.add.reduceat(g.S_10d.values[keep], np.arange(0, keep.sum(), 2))
        e = np.arange(12, 19.001, 0.5)
        top = 1.15 * (b + s).max()
        Q = sd.Plot(480, 480, x=(12, 19, 'lin'), y=(0, top, 'lin'), xlabel='m_ee [MeV]',
                    ylabel=ylab, margin=(56, 20, 92, 110), title=ttl)
        st = 10 ** int(np.log10(top / 2))
        Q.xticks([(v, f'{v}') for v in range(12, 20)]).yticks([(v, f'{v:,.0f}') for v in np.arange(0, top, st * (2 if top / st > 6 else 1))])
        for i in range(len(b)):
            Q.raw(f'<rect x="{Q.X(e[i]):.1f}" y="{Q.Y(b[i]):.1f}" width="{Q.X(e[i + 1]) - Q.X(e[i]):.1f}" height="{Q.Y(0) - Q.Y(b[i]):.1f}" '
                  f'fill="{sd.GREY}" fill-opacity="0.45"/>', back=True)
            tip = (f'{e[i]:.1f}–{e[i + 1]:.1f} MeV: background {b[i]:,.0f}, X17 {s[i]:.0f} '
                   f'(+{s[i] / max(b[i], 1e-9) * 100:.0f} %, {s[i] / np.sqrt(max(b[i], 1e-9)):.1f}σ in this bin)')
            Q.raw(f'<rect x="{Q.X(e[i]):.1f}" y="{Q.Y(b[i] + s[i]):.1f}" width="{Q.X(e[i + 1]) - Q.X(e[i]):.1f}" '
                  f'height="{Q.Y(b[i]) - Q.Y(b[i] + s[i]):.1f}" fill="{sd.RED}"{sd.tipattr(tip)}/>')
        return Q.svg(ttl)

    def d(t, hw, ycat, short):
        return t[(t.hw == hw) & (t.ycat == ycat) & (t.short == short)].days_3sigma.iloc[0]
    rows = []
    for lab, t, yc in (('θ, all pairs', lad, 'all'), ('θ, |y| &lt; 0.3', lad, 'y<0.3'), ('<b>m_ee</b>, all pairs', ladm, 'all')):
        rows.append([lab] + [f'{fd(d(t, hw, yc, k))} d' for hw in (BP, AB) for k in ('count', 'struct 2 %', '+ in-run ctrl')])
    tab = sd.table(['fitted in', 'big pl.,<br>stats', 'big pl.,<br>2 % shape', 'big pl.,<br>+ ctrl', 'as built,<br>stats',
                    'as built,<br>2 % shape', 'as built,<br>+ ctrl'], rows, size=17, widths=[200, 110, 110, 110, 110, 110, 110])
    side = sd.col(
        sd.p('days to 3σ at R(ATOMKI), 1 µA', 21, weight=600), tab,
        sd.callout('<b>Why it works.</b> W = 18.15 MeV is known, so θ and y give the pair mass, m_ee² = W²(1 − y²)(1 − cos θ)/2. '
                   'The X17 edge in θ becomes a peak (FWHM ≈ 0.6 MeV); a smooth shape error cannot fake a peak. y is a ratio: the energy scale cancels.', sd.BLUE, 18),
        sd.callout('<b>The same idea as ATOMKI\'s mass fit</b> (their Fig. 5); the |y| cut was its crude projection. '
                   'Still offline: same trigger, same recorded E₁, E₂, θ.', sd.GREEN, 18),
        sd.callout('<b>New sensitivity:</b> the arm-to-arm energy calibration (it moves y). Small for symmetric pairs; not yet in the fit.', sd.ORANGE, 18),
        gap=10, w=860)
    D.slide('mass', sd.title(f'Fit the pair mass, not the angle: ~{N["bp_robust"]:.1f} d big plastics, ~{N["ab_robust"]:.0f} d as built',
                             'Ten days at 1 µA, all pairs, MM 15° + TOF, E_sum window: background (grey) and X17 at the ATOMKI ratio (red) in m_ee. Hover the bins.')
            + sd.row(mplot(BP, 'big plastics', 'pairs per 0.5 MeV in 10 days'), mplot(AB, 'as built', None), side, gap=10),
            """<p>m_ee² = W² (1 − y²)(1 − cos θ)/2 for massless leptons sharing W = 18.15 MeV (the 1.10 MeV run; E* = 18.22 MeV with
the direct-capture share, a 0.4 % shift). θ = the reconstructed chord angle, y = (E₁ − E₂)/(E₁ + E₂) from the arms. The X17 (m = 16.7)
reconstructs at 16.6 MeV with FWHM ≈ 0.6 MeV. The IPC γ₀ is a falling continuum with no structure at 16–17 MeV, and the γ₁ (15.1 MeV
transitions) pile up below 15.</p>
<p>The fit is the same Asimov/Fisher ladder as the Systematics slide, now on 0.25 MeV bins over 8–20 MeV. Nuisances: M1/E1/γ₁ norms,
γ* anisotropy, resolution and E scale, a cubic acceptance in m_ee, and 2 % Gaussian-process structure with ℓ ≈ 0.55 MeV
(= 10° at the edge). In-run control: the γ₁ E_sum side band. All pairs; no |y| cut is needed.</p>
<p>Caveats: the IPC templates in m_ee are KDE-smoothed (0.27 MeV) from limited Monte Carlo; the L7 large-angle samples
(×10–20 statistics) replace them. An arm-to-arm gain mismatch shifts y and smears the peak; it has to be calibrated
(the 441 keV, 17.64 MeV pairs reconstruct with the same shape).</p>""",
            foot='lnl/out/syst/ladder_mass.csv, spectra_10d_mass.csv (lnl/sim/lnl_syst.py, use_var("mass"))', short='Mass fit')


def checks_slide(D, O):
    """Two checks on the background shape: the γ* anisotropy and event mixing (2026-10-12)."""
    an = pd.read_csv(O / 'syst' / 'aniso.csv')
    mc = pd.read_csv(O / 'mixing' / 'mixing_curves.csv')
    ms = pd.read_csv(O / 'mixing' / 'mixing_summary.csv')
    run = 'L7' if (mc.run == 'L7').any() else 'L2'

    def mplot(meth, ttl, ylab):
        Q = sd.Plot(520, 470, x=(90, 180, 'lin'), y=(0.5, 1.5, 'lin'), xlabel='opening angle [°]', ylabel=ylab,
                    margin=(56, 20, 92, 104), title=ttl)
        Q.xticks([(v, f'{v}°') for v in (90, 120, 150, 180)]).yticks([(v, f'{v:.1f}') for v in (0.6, 0.8, 1.0, 1.2, 1.4)])
        Q.band([90, 180], [0.98, 0.98], [1.02, 1.02], sd.GREY, 0.18, tip='±2 %')
        Q.hline(1.0, sd.MUT, dash=None, w=1.5)
        for (smp, yc), col, dash in ((('E1_18.15', 'all'), sd.ORANGE, None), (('M1_18.15', 'all'), sd.BLUE, None),
                                     (('M1_18.15', 'y<0.3 (truth)'), sd.BLUE, '8 6')):
            g = mc[(mc.hw == BP) & (mc.run == run) & (mc.method == meth) & (mc['sample'] == smp) & (mc.ycat == yc)]
            t = ms[(ms.hw == BP) & (ms.run == run) & (ms.method == meth) & (ms['sample'] == smp) & (ms.ycat == yc)]
            if g.empty:
                continue
            t = t.iloc[0]
            lab = (f'{smp[:2]} IPC, {yc}: rms {t.rms_pct:.0f} %, after a smooth cubic {t.rms_after_cubic_pct:.1f} % '
                   f'(χ² {t.chi2_after_cubic:.0f}/{t.ndf_after_cubic}; MC stat {t.mc_stat_per_bin_pct:.1f} %)')
            Q.line(list(g.theta), list(g.ratio.clip(0.5, 1.5)), col, 3, dash=dash, r=4,
                   tips=[f'{lab}; {x:.0f}°: {r:.2f} ± {e:.2f}' for x, r, e in zip(g.theta, g.ratio, g.err)])
        return Q.svg(ttl)

    rows = []
    for var, yc, lab in (('theta', 'all', 'θ, all pairs'), ('theta', 'y<0.3', 'θ, |y| &lt; 0.3'), ('mass', 'all', 'm_ee, all pairs')):
        r = []
        for smp in ('M1_18.15', 'E1_18.15'):
            g = an[(an['var'] == var) & (an.hw == BP) & (an.ycat == yc) & (an['sample'] == smp)]
            r.append(f'{g.shape_change_pct.iloc[0]:+.0f} %' if len(g) else '–')
        rows.append([lab] + r)
    tab = sd.table(['big plastics', 'M1 IPC', 'E1 IPC'], rows, size=19, widths=[220, 120, 120])
    sel = (ms.hw == BP) & (ms.run == run) & ms['sample'].isin(['M1_18.15', 'E1_18.15'])
    sg, pl = ms[sel & (ms.method == 'singles')], ms[sel & (ms.method == 'pair legs')]
    side = sd.col(
        sd.p('γ* anisotropy a₂ = 0.36: IPC in the window vs side band', 20, weight=600), tab,
        sd.callout('<b>Anisotropy.</b> ⁷Li(p,γ₀) photons are not isotropic about the beam: σ(0°)/σ(150°) = 7.6 at 1.10 MeV '
                   '(Zahnow 1995, M1–E1 interference) and a₂ ≈ 0.36 (Hayes et al. 2021). The interference (P₁) cancels in '
                   'arms symmetric about 90°; the P₂ term reshapes the IPC by the amounts above. In the fit: a₁ ± 0.3, a₂ ± 0.15.', sd.PURPLE, 17),
        sd.callout(f'<b>Event mixing</b> (ATOMKI\'s method) gets the smooth tilt wrong by up to ~20 % (M1: the soft lepton\'s '
                   f'efficiency depends on its energy), but after a free cubic, mixing <b>single-arm</b> events matches the true '
                   f'acceptance to {sg.rms_after_cubic_pct.min():.1f}–{sg.rms_after_cubic_pct.max():.1f} % per 5° (big plastics): '
                   f'the local structure the fit allows (δ = 2 %). Mixing legs of triggered pairs is worse '
                   f'({pl.rms_after_cubic_pct.min():.1f}–{pl.rms_after_cubic_pct.max():.1f} %). So: a prescaled single-arm trigger, '
                   f'and the tilt floats in the fit.', sd.BLUE, 17),
        gap=10, w=560)
    D.slide('checks', sd.title('Two checks on the background shape: the γ* anisotropy and event mixing',
                               f'Geant4 {run} IPC, big plastics. Left: true pair acceptance / event-mixing estimate, normalised over 125–175°. Hover the curves.')
            + sd.row(mplot('pair legs', 'mixing legs of triggered pairs', 'true / mixed acceptance'),
                     mplot('singles', 'mixing single-arm events', None), side, gap=10),
            """<p><b>Anisotropy.</b> W(θ_k) = 1 + a₁P₁ + a₂P₂ in the angle θ_k between the γ* (e⁺ + e⁻ momentum) and the beam,
applied event by event to the γ₀ IPC Monte Carlo. a₁ ≈ 1.0 from Zahnow's 0°/150° ratio (7.6 ± 1.3 at 1100 keV) is the E1–M1
interference; it cancels for an acceptance symmetric about 90° (Hayes, Friar, Hale, Garvey, arXiv:2106.06834), and the Geant4
tables confirm ⟨P₁⟩ ≈ 0 in every bin. a₂: Hayes et al.'s R-matrix gives 4πσ(90°)/σ_int = 1 − a₂/2 = 0.82, so a₂ = 0.36; the physical
range is 0–0.5. The table gives the change of the IPC in the window relative to the side band (θ: 90–120°; m_ee: 12–15 MeV).</p>
<p><b>Mixing.</b> True acceptance = selected / generated Born in truth θ, at the two-arm trigger level (no E_sum, no pointing):
the geometric part. Singles = one-arm hits from the 8Be γ-line runs (Compton and conversion electrons), the stand-in for a
single-arm trigger. Mixing pair legs works for E1 but not for M1: M1 pairs at large angles are lopsided in energy, and the soft lepton's
efficiency depends on its energy, which mixing cannot see. With |y| &lt; 0.3 (both leptons hard) the singles agree for M1 too.
The energy-dependent part of the efficiency has to come from Monte Carlo, checked on the 441 keV run.</p>""",
            foot='lnl/out/syst/aniso.csv; lnl/out/mixing/ (lnl/sim/lnl_mixing.py)', short='Checks')
