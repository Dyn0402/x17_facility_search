"""Deck slides (2026-10-09): why the big plastics win, how big they need to be,
and how much the target region widens the X17 peak.

Reads lnl/out/plastics/*.csv (lnl/plastic_size.py) and lnl/out/scatter/*.csv
(lnl/sim/lnl_scatter.py, lnl/sim/lnl_week.py). Called from build_deck.py: size_slides() after the
reach slide, scatter_slides() after the material slide.
"""
import math

import numpy as np
import pandas as pd

import slidedoc as sd


def size_slides(D, O):
    P_ = O / 'plastics'
    fm = pd.read_csv(P_ / 'footmap.csv')
    ins = pd.read_csv(P_ / 'footmap_inside.csv', index_col=0).frac_leptons
    ch = pd.read_csv(P_ / 'chain.csv').set_index('hw')
    dv = pd.read_csv(P_ / 'days_vs_size.csv')
    cal = pd.read_csv(P_ / 'calib.csv')
    ab, bp = ch.loc['as built'], ch.loc['big plastics']

    # ---- slide 1: where the x17 comes from -------------------------------- #
    M = sd.Plot(560, 560, x=(-50, 50, 'lin'), y=(-50, 50, 'lin'), xlabel='across the arm [cm]',
                ylabel='along the beam [cm]', margin=(20, 20, 92, 104))
    M.xticks([(v, str(v)) for v in (-40, -20, 0, 20, 40)]).yticks([(v, str(v)) for v in (-40, -20, 0, 20, 40)])
    vmax = fm.frac.max()
    M.cells([(r.u_lo / 10, r.u_hi / 10, r.v_lo / 10, r.v_hi / 10, r.frac, None) for r in fm.itertuples() if r.frac > 0],
            0, vmax, cmap=[(0.0, '#f4f1f6'), (0.5, '#b58bbb'), (1.0, '#4b1d52')])
    M.rect(-20.06, -0.15, -15.02, 15.02, sd.RED, 4, tip=f'as built: two 20×30×2 cm bars; {ins.iloc[0] * 100:.0f} % of the leptons')
    M.rect(0.15, 20.06, -15.02, 15.02, sd.RED, 4, tip=f'as built: two 20×30×2 cm bars; {ins.iloc[0] * 100:.0f} % of the leptons')
    sh = 25 * 41.05 / 33.2
    M.rect(-sh, sh, -sh, sh, sd.BLUE, 3, dash='10 7',
           tip=f'The 50×50 cm SiPM wall (20 bars), projected from the spot onto the plastic plane: {ins.iloc[2] * 100:.0f} % (16 bars: {ins.iloc[1] * 100:.0f} %)')
    M.rect(-37.5, 37.5, -37.5, 37.5, sd.GREEN, 4,
           tip=f'75×75 cm plastic: {ins.iloc[3] * 100:.0f} % of the leptons, {ins.iloc[4] * 100:.0f} % together with the 20-bar SiPM wall')
    stg = [('both legs tagged', bp.pair_tag / ab.pair_tag, sd.PURPLE,
            f'Pair-tag {ab.pair_tag * 100:.1f} % → {bp.pair_tag * 100:.1f} % of X17 decays. Geometry: each lepton has to hit a plastic, and the pair needs both.'),
           ('E_sum window kept', (bp.esum_window / bp.pair_tag) / (ab.esum_window / ab.pair_tag), sd.PURPLE,
            f'{ab.esum_window / ab.pair_tag * 100:.0f} % → {bp.esum_window / bp.pair_tag * 100:.0f} % of tagged X17 inside E_sum 13–17 MeV: 5 cm of plastic stops more of the lepton (a calorimeter).'),
           ('MM 15° + TOF kept', (bp.mm15_tof / bp.esum_window) / (ab.mm15_tof / ab.esum_window), sd.PURPLE,
            f'{ab.mm15_tof / ab.esum_window * 100:.0f} % → {bp.mm15_tof / bp.esum_window * 100:.0f} %'),
           ('in 125–155°', (bp.window_125_155 / bp.mm15_tof) / (ab.window_125_155 / ab.mm15_tof), sd.PURPLE,
            f'{ab.window_125_155 / ab.mm15_tof * 100:.0f} % → {bp.window_125_155 / bp.mm15_tof * 100:.0f} %: small plastics only catch leptons near the arm centres, which favours back-to-back pairs.')]
    S_r = bp.S_per_day / ab.S_per_day
    Bab = ab.B_ipc_per_day + ab.B_g1_per_day + ab.B_cos_per_day + ab.B_epc_per_day
    Bbp = bp.B_ipc_per_day + bp.B_g1_per_day + bp.B_cos_per_day + bp.B_epc_per_day
    B_r = Bbp / Bab
    rows = [(f'×{v:.2f}', v, c, tp) for _, v, c, tp in stg]
    rows = [(lab, v, c, tp) for (lab, _, c, tp), (_, v, _, _) in zip(stg, rows)]
    rows += [('X17 per day', S_r, sd.BLUE, f'{ab.S_per_day:.1f} → {bp.S_per_day:.0f} X17/day in 125–155° at R(ATOMKI)'),
             ('IPC per day', B_r, sd.GREY, f'{Bab:.0f} → {Bbp:,.0f} background/day in 125–155° (IPC γ₀ + γ₁, cosmics, EPC)')]
    side = sd.col(
        sd.p('Geant4, X17 m = 16.7, as built → big plastics', 24, weight=600),
        sd.hbars(rows, 16, width=300, h=32, label_w=250, fmt=lambda v: f'×{v:.1f}', size=23),
        sd.callout(f'<b>It is acceptance.</b> The X17 rate goes up ×{S_r:.0f}, but the IPC goes up ×{B_r:.0f} with it, so S/B hardly moves '
                   f'({ab.S_per_day / Bab:.3f} → {bp.S_per_day / Bbp:.3f}). Days ∝ B/S² then fall like 1/S: '
                   f'{ab.days_count_125_155:.0f} → {bp.days_count_125_155:.1f} d (×{S_r ** 2 / B_r:.0f}).', sd.BLUE, 22),
        sd.callout(f'<b>The picture (left):</b> where the leptons that cross a Micromegas land at the plastic. The as-built bars catch '
                   f'{ins.iloc[0] * 100:.0f} % per lepton, so a pair (both legs) ~{ins.iloc[0] ** 2 * 100:.0f} %. '
                   f'75×75 catches {ins.iloc[3] * 100:.0f} %; with the SiPM wall in front, {ins.iloc[4] * 100:.0f} %.', sd.PURPLE, 22),
        gap=14, w=860)
    D.slide('why-big', sd.title(f'Big plastics: ×{S_r:.0f} more X17, and the IPC grows with it',
                                'Left: the Micromegas cone at the plastic plane (toy, X17 leptons) and the three outlines. Right: Geant4 factors, as built → big plastics. Hover.')
            + sd.row(sd.col(M.svg('lepton footprint at the plastic plane'),
                            sd.legend([('as-built bars', sd.RED), ('SiPM wall shadow', sd.BLUE, 'dash'), ('75×75 cm', sd.GREEN)], 21), gap=6),
                     side, gap=36),
            f"""<p>Factors from the Geant4 chain (<code>lnl/out/plastics/chain.csv</code>, from <code>acceptance_geant.csv</code> and
<code>reach_geant.csv</code>): as built with the LS, E_sum {ab.esum}; big plastics, E_sum {bp.esum}; MM 15° + TOF; counting in
125–155°. The stage factors multiply to the X17 gain within a few % (the E_sum windows differ slightly).</p>
<p>Why the background follows: the IPC pairs come from the same spot, in the same arms, with similar energies, so a bigger plastic
tags them just as it tags the X17 (Geant4: M1 ×{0.023554 / 0.003080:.1f}, E1 ×{0.037004 / 0.005431:.1f}, X17 ×{bp.pair_tag / ab.pair_tag:.1f} in pair-tag).
With S/B fixed, significance grows as √S: ×15 in rate is ×15 in time.</p>
<p>The map is from the geometric toy (<code>lnl/plastic_size.py</code>): straight leptons from the spot, the surveyed arms, Highland
kicks behind the MM, an energy threshold. Fitted to the two Geant4 X17 pair-tags; the IPC big/as-built ratios match Geant4 to ~3 %.</p>""",
            foot='lnl/out/plastics/chain.csv, footmap.csv (toy); Geant4 reach_geant.csv', short='Why big')

    # ---- slide 2: days against size (plastics where the bars are now) ------ #
    P = sd.Plot(1060, 640, x=(20, 120, 'lin'), y=(0.5, 60, 'log'), xlabel='side of a square plastic, 5 cm thick [cm]',
                ylabel='days to 3σ at R(ATOMKI), 1 µA')
    P.xticks([(v, str(v)) for v in (20, 40, 60, 80, 100, 120)]).yticks([(v, f'{v:g}') for v in (0.5, 1, 2, 5, 10, 20, 50)])
    pl = [p for p in dv.placement.unique() if p.startswith('where the bars are now')][0]
    g = dv[dv.placement == pl].sort_values('S_mm')
    g = g[g.days < 60]
    tips = [f'{r.S_mm / 10:.1f}×{r.S_mm / 10:.1f} cm at R = {r.R_front_mm / 10:.1f} cm'
            + (' (pushed back so the plates clear)' if r.pushed_back else '')
            + f'\n{r.days:.2f} d; X17 in window ×{r.s_rel:.2f} of 75×75; plastic {r.plate_area_m2:.2f} m² for 4 arms'
            for r in g.itertuples()]
    P.line(list(g.S_mm / 10), list(g.days), sd.BLUE, 4, markers=False)
    pb = g[g.pushed_back]
    P.line(list(pb.S_mm / 10), list(pb.days), sd.BLUE, 12, markers=False)
    P.raw(f'<g opacity="0.25">{P.fore.pop()}</g>')
    P.points(list(g.S_mm / 10)[::2], list(g.days)[::2], sd.BLUE, r=5, tips=tips[::2])
    k = g.loc[g.days.idxmin()]
    k10 = g[g.days <= 1.1 * k.days].iloc[0]
    P.vline(k.S_mm / 10, sd.GREEN, '10 6', 3, label=f'optimum {k.S_mm / 10:.1f} cm: {k.days:.2f} d',
            tip=f'Minimum of the curve: {k.S_mm / 10:.1f} cm, {k.days:.2f} d. Beyond it the plates no longer fit '
                f'at R = 41 cm and move back, which loses acceptance.')
    abp = dv[dv.placement.str.startswith('as-built')].iloc[0]
    P.hline(abp.days, sd.MUT, '4 6', label=f'as-built bars, same cuts: {abp.days:.0f} d',
            tip='The 2×20×30 cm bars with the big-plastic E_sum and cuts (geometry only). With their own 2 cm calorimetry, Geant4 gives 15.5 d.')
    P.points([75], [dv.days_anchor.iloc[0]], sd.INK, r=9, tips=[f'Geant4: 75×75×5 cm at R = 41 cm, {dv.days_anchor.iloc[0]:.2f} d (the anchor)'])
    P.text(68, dv.days_anchor.iloc[0] * 0.72, 'Geant4 75×75', 20, sd.INK, anchor='end')
    side = sd.col(
        sd.legend([('plastics where the bars are now (fronts at R = 41 cm)', sd.BLUE), ('optimum', sd.GREEN, 'dash')], 20),
        sd.p('thick, faded: plates pushed back so neighbours clear', 20, sd.MUT),
        sd.callout(f'<b>Optimum at ~{k.S_mm / 10:.0f} cm</b> ({k.days:.2f} d, {k.plate_area_m2:.1f} m² of plastic for 4 arms). '
                   f'Within 10 % of it from ~{k10.S_mm / 10:.0f} cm ({k10.plate_area_m2:.1f} m²).', sd.GREEN, 22),
        sd.callout('<b>It saturates</b> because the 40×36 cm Micromegas set the acceptance: 75 cm already covers their cone at 41 cm.',
                   sd.BLUE, 22),
        sd.callout('<b>Past ~75 cm the plates collide</b> (centred square plates touch once S/2 ≳ R − 3 cm), so they move back '
                   'and lose a little. The footprint is not the limit before the optimum.', sd.GREY, 22),
        gap=14, w=600)
    D.slide('size', sd.title(f'~{k.S_mm / 10:.0f} cm plastics where the bars are now; past that the Micromegas set the acceptance',
                             'Days to 3σ against the side of four square 5 cm plastics at the current bar position. Toy, anchored to Geant4 at 75×75. Hover the points.')
            + sd.row(P.svg('days against plastic size'), side, gap=36),
            f"""<p><b>An analytic stand-in, not Geant4.</b> <code>lnl/plastic_size.py</code>: X17 and Born M1/E1 IPC with the Geant4 generator
kinematics, from a σ = 2 mm spot, into the surveyed arms (SimConfig.hh). A leg needs the lepton through the MM active area, a read-out
SiPM bar (20 bars) and the plastic face, after Highland kicks behind the MM (x/X₀ =
{cal.T_MM.iloc[0]:.2f}, fitted) and in the SiPM wall, with KE &gt; {cal.E_TH_MeV.iloc[0]:.2f} MeV (fitted). The two numbers fit the
Geant4 X17 pair-tags (as built 3.3 %, big plastics 23 %). Refitting with a 3 MeV threshold moves the curve by &lt; 7 %.</p>
<p>Days = 1.2 d × (B/B₇₅)/(S/S₇₅)², counting X17 and IPC (γ₀ mix of the ATOMKI 2016 run) in 125–155° after a 5° smear. The
E_sum, MM and TOF efficiencies are held at the Geant4 big-plastic values, so this is geometry only; a thin or small plate would
also lose calorimetry. Footprint: plates centred on each arm, fronts at 41 cm from the beam; neighbours touch when S/2 + 1.7 cm (pinwheel)
+ 1 cm (wrap) &gt; R, then R is increased. The SiPM wall stays where it is (fronts at 31.5 cm) and stays in the trigger leg (it gives the TOF).
Other placements (closer, behind the SiPM wall; no SiPM wall) are in <code>days_vs_size.csv</code> but are not considered practical.</p>
<p>To confirm before buying: one Geant4 run with an oversized plate (the <code>--big-plastic</code> option was made for this:
cut any smaller plate offline from its hits).</p>""",
            foot='lnl/out/plastics/days_vs_size.csv, calib.csv, footprint.csv', short='Plastic size')


def scatter_slides(D, O):
    S_ = O / 'scatter'
    w = pd.read_csv(S_ / 'widen.csv')
    st = pd.read_csv(S_ / 'widen_stats.csv').set_index('curve')
    sk = pd.read_csv(S_ / 'stacked.csv')
    cost = pd.read_csv(S_ / 'cost.csv')
    sty = [('truth (no scattering)', sd.GREEN, None, 'no scattering (Geant4 truth)'),
           ('no wall (model floor)', sd.BLUE, '4 6', 'no chamber wall (model)'),
           ('CFRP 0.4 mm chamber (baseline)', sd.PURPLE, None, 'CFRP 0.4 mm chamber (Geant4)'),
           ('Al 1.0 mm chamber', sd.ORANGE, '10 6', 'Al 1 mm chamber (Geant4 L5)'),
           ('n_TOF ³He capsule (σ68 14.5°)', sd.GREY, '3 5', 'n_TOF capsule resolution, 14.5°')]
    P = sd.Plot(1000, 620, x=(110, 180, 'lin'), y=(0, 0.15, 'lin'), xlabel='e⁺e⁻ opening angle [°]',
                ylabel='X17 pairs, fraction per 1°')
    P.xticks([(v, f'{v}°') for v in range(110, 181, 10)]).yticks([(v, f'{v:.2f}') for v in (0, 0.05, 0.10, 0.15)])
    for c, col, dash, lab in sty:
        g = w[(w.curve == c) & (w.theta_lo >= 110)]
        xs, ys = sd.step_xy(list(g.theta_lo) + [180.0], list(g.frac_per_deg))
        s = st.loc[c]
        P.line(xs, ys, col, 4 if dash is None else 3, dash=dash, markers=False,
               tip=f'{lab}: σ68 {s.sigma68:.1f}°, {s.frac_125_155 * 100:.0f} % in 125–155°, peak {s.peak_frac_per_deg * 100:.1f} %/°')
    cfrp = st.loc['CFRP 0.4 mm chamber (baseline)']
    tr = st.loc['truth (no scattering)']
    c = cost.set_index('case')
    d_tr = c.loc['truth (no scattering)'].days_anchored
    d_cf = c.loc['CFRP 0.4 mm chamber, Geant4 reco'].days_anchored
    d_nw = c.loc['no wall (model floor) (Gaussian)'].days_anchored
    d_al = c.loc['Al 1.0 mm chamber (L5 residuals)'].days_anchored
    d_al5 = c.loc['Al 0.5 mm chamber (L5 residuals)'].days_anchored
    d_nt = c.loc['n_TOF ³He capsule (σ68 14.5°) (Gaussian)'].days_anchored
    drows = [('no scattering', d_tr, sd.GREEN, 'Geant4 truth angles for X17 and IPC, same events, best counting window'),
             ('no chamber wall', d_nw, sd.BLUE, 'Gaussian 3.5° (the appendix model floor: spot, air, MM, centroid)'),
             ('CFRP 0.4 mm (baseline)', d_cf, sd.PURPLE, 'Geant4 reconstructed chord: the headline 1.2 d'),
             ('Al 0.5 mm', d_al5, sd.ORANGE, 'Geant4 L5 residuals applied to the same events'),
             ('Al 1.0 mm', d_al, sd.ORANGE, 'Geant4 L5 residuals applied to the same events'),
             ('n_TOF-like 14.5°', d_nt, sd.GREY, 'Gaussian 14.5° (the n_TOF capsule resolution) on the same events')]
    side = sd.col(
        sd.legend([(lab, col, 'dash' if d else 'line') for _, col, d, lab in sty], 20),
        sd.callout(f'<b>The CFRP chamber widens the edge to σ68 = {cfrp.sigma68:.1f}°</b> (no wall: ~3.5°). The peak drops from '
                   f'{tr.peak_frac_per_deg * 100:.0f} to {cfrp.peak_frac_per_deg * 100:.0f} %/°, but {cfrp.frac_125_155 * 100:.0f} % of the X17 '
                   f'stays in 125–155° ({tr.frac_125_155 * 100:.0f} % with no scattering).', sd.PURPLE, 22),
        sd.p('days to 3σ, same events, counting S/√B (IPC known)', 22, weight=600),
        sd.hbars(drows, 2.0, width=260, h=26, label_w=250, fmt=lambda v: f'{v:.2f} d', size=21),
        gap=12, w=680)
    D.slide('scatter', sd.title(f'The carbon chamber widens the X17 edge to {cfrp.sigma68:.1f}°; the wall costs ~{(d_cf / d_nw - 1) * 100:.0f} % in time',
                                'X17 (m = 16.7, 18.15 MeV) opening angle for the same selected events, big plastics, MM 15° + TOF. Hover the curves and bars.')
            + sd.row(P.svg('X17 peak widening'), side, gap=32),
            f"""<p>The LNL version of the n_TOF capsule "dilution" plot. Truth = the generated opening angle (no scattering, perfect detector).
CFRP = the Geant4 reconstructed chord (beam spot → MM centroids) of the same events, with the real chamber (CFRP 0.4 mm, r = 25 mm),
Al 10 µm backing, Al 1 mm holder, air, MM window and gas. Al 1 mm: the Geant4 L5 residual distribution (reco − truth) applied to the
same truth angles. No-wall and n_TOF curves are Gaussian illustrations (3.5° from the appendix model floor; 14.5° = σ68 at n_TOF).</p>
<p>Days: IPC (γ₀ + γ₁) and X17 at R(ATOMKI) per day, each smeared the same way, best counting window on 2° bins, scaled so the CFRP
case = {d_cf:.2f} d. The edge is sharp in truth ({c.loc['truth (no scattering)'].window}°), so scattering costs ×{d_cf / d_tr:.2f} overall,
of which the wall ~×{d_cf / d_nw:.2f}. Even an n_TOF-like 14.5° would only cost ×{d_nt / d_cf:.1f}: at LNL the IPC under the edge is smooth
and the edge sits where the IPC is falling.</p>""",
            foot='lnl/out/scatter/widen.csv, widen_stats.csv, cost.csv (lnl/sim/lnl_scatter.py)', short='Scattering')

    # ---- one week, as measured: pseudo-data and residuals ------------------- #
    wk = pd.read_csv(S_ / 'week.csv')
    zt = pd.read_csv(S_ / 'week_z.csv').set_index('days')
    xs = list(wk.theta_lo) + [180.0]

    def errbars(Q, x, y, e, col):
        for a_, b_, c_ in zip(x, y, e):
            Q.raw(sd.line(Q.X(a_), Q.Y(b_ - c_), Q.X(a_), Q.Y(b_ + c_), col, 2.5))

    xc = list(0.5 * (wk.theta_lo + wk.theta_hi))
    T_ = sd.Plot(1000, 330, x=(90, 180, 'lin'), y=(0, 3000, 'lin'), ylabel='pairs per week / 4°', margin=(16, 20, 20, 104))
    T_.xticks([]).yticks([(v, f'{v:,}') for v in (0, 1000, 2000, 3000)])
    T_.line(*sd.step_xy(xs, list(wk.ipc_exp)), sd.GREY, 3, markers=False, tip='IPC expectation (γ₀ + γ₁, Born M1 + E1), Geant4, 5° smoothing')
    T_.line(*sd.step_xy(xs, list(wk.ipc_exp + wk.x17_reco)), sd.RED, 3, markers=False, tip='IPC + X17 at R(ATOMKI), measured angle')
    errbars(T_, xc, list(wk.pseudo_data), list(np.sqrt(wk.pseudo_data)), sd.INK)
    T_.points(xc, list(wk.pseudo_data), sd.INK, r=5,
              tips=[f'{r.theta_lo:.0f}–{r.theta_hi:.0f}°: {r.pseudo_data} pairs; IPC {r.ipc_exp:.0f}, X17 {r.x17_reco:.0f}' for r in wk.itertuples()])
    R_ = sd.Plot(1000, 290, x=(90, 180, 'lin'), y=(-100, 300, 'lin'), xlabel='e⁺e⁻ opening angle [°]',
                 ylabel='data − IPC', margin=(10, 20, 84, 104))
    R_.xticks([(v, f'{v}°') for v in range(90, 181, 10)]).yticks([(v, str(v)) for v in (-100, 0, 100, 200, 300)])
    R_.hline(0, sd.MUT, None, 1.5)
    R_.line(*sd.step_xy(xs, list(wk.x17_truth)), sd.GREEN, 3, dash='8 6', markers=False, tip='X17, truth angle (no scattering)')
    R_.line(*sd.step_xy(xs, list(wk.x17_reco)), sd.RED, 4, markers=False, tip='X17, measured angle (CFRP chamber, σ68 4.6°)')
    errbars(R_, xc, list(wk.resid), list(wk.resid_err), sd.INK)
    R_.points(xc, list(wk.resid), sd.INK, r=5,
              tips=[f'{r.theta_lo:.0f}–{r.theta_hi:.0f}°: {r.resid:+.0f} ± {r.resid_err:.0f} (X17 expected {r.x17_reco:.0f})' for r in wk.itertuples()])
    z0 = zt.iloc[0]
    rows_z = [[f'{d} d', f'{zt.z_count_known_B[d]:.1f}', f'{zt.z_fit_ipc_norm_free[d]:.1f}', f'{zt.z_fit_m1_e1_g1_free[d]:.1f}',
               f'{zt.z_count_shape_2pct[d]:.1f}'] for d in (1, 3, 7, 14)]
    sb = z0.S_per_day / z0.B_per_day
    side = sd.col(
        sd.legend([('pseudo-data, one week', sd.INK), ('IPC expected', sd.GREY), ('IPC + X17 (ATOMKI)', sd.RED),
                   ('X17, no scattering', sd.GREEN, 'dash')], 19),
        sd.p('expected significance (σ), Asimov', 21, weight=600),
        sd.table(['beam', 'count, B known', 'fit, IPC norm free', 'fit, M1/E1/γ₁ free', 'count, 2 % shape'], rows_z, 18,
                 tips=None),
        sd.callout(f'<b>How:</b> counting is S/√B in {z0.window}° with the IPC expectation taken as exact: {z0.days_count:.1f} d to 3σ. '
                   f'Freeing the IPC norm (template fit over 90–180°): {z0.days_fit_1norm:.1f} d. Freeing the M1, E1 and γ₁ norms '
                   f'separately: {z0.days_fit_free:.1f} d. Statistical only; Z grows as √t.', sd.BLUE, 19),
        sd.callout(f'<b>The catch: S/B ≈ {sb * 100:.0f} %.</b> An uncertainty ε on the IPC shape under the edge (relative to the sidebands) '
                   f'caps Z at S/(εB): {sb / 0.02:.1f}σ for 2 %, {sb / 0.05:.1f}σ for 5 %. The result needs the IPC angular shape to ~1 %, '
                   'from the data (sidebands, E_sum) and the Born calculation.', sd.ORANGE, 19),
        gap=10, w=600)
    D.slide('scatter-week', sd.title('One week at 1 µA, as measured: the smeared X17 is a 3–4σ excess per 4° bin',
                                     f'One Poisson pseudo-experiment (top) and the excess over the IPC expectation (bottom). Big plastics, '
                                     f'MM 15° + TOF, CFRP chamber. Hover the points.')
            + sd.row(sd.col(T_.svg('one week of pseudo-data'), R_.svg('excess over the IPC'), gap=0), side, gap=24),
            f"""<p>{7 * z0.S_per_day:.0f} X17 on {7 * z0.B_per_day:,.0f} IPC pairs in {z0.window}° per week ({zt.z_toy_week.iloc[0]:.1f}σ in
this pseudo-experiment, {zt.z_count_known_B[7]:.1f}σ expected). Per day at 1 µA, Li₂O 300 µg/cm² at 1.10 MeV, × 7 days × live time:
IPC = Born M1 (resonances) + E1 (direct capture) + γ₁ (<code>yields.csv</code>), Geant4 reconstructed chord, smoothed with the 5°
kernel of the reach templates (the raw MC is noisier than a week of data). Cosmics and EPC (&lt; 1 %) are left out. The X17 is
Geant4 m = 16.7, measured (red) and truth (green) angles, same events. <code>lnl/sim/lnl_week.py</code>.</p>
<p>Significance. All Asimov (expected) and statistical only. Counting: the window that maximises S/√B on 2° bins, IPC known
exactly (the headline 1.2 d). Template fits: binned Fisher over 90–180°, signal shape fixed, the IPC components floating
(<code>lnl_geant.reach_one</code>). The last column is counting with a 2 % uncertainty on B in the window: Z = S/√(B + ε²B²).
With the M1/E1 mix free, 3σ takes {z0.days_fit_free:.1f} d; the fit pays for not knowing how much of the 130–172° IPC is M1 vs E1.</p>
<p>Not yet in: the look-elsewhere effect for a scanned mass, and the IPC shape systematic, which no MC study here constrains. The Al and CFRP per-layer scattering budget is in <code>lnl/out/scatter/budget.csv</code>: the chamber
wall dominates, the MM window and cathode cost nothing.</p>""",
            foot='lnl/out/scatter/week.csv, week_z.csv (lnl/sim/lnl_week.py); stacked.csv (lnl_scatter.py); reach_geant.csv',
            short='One week')
