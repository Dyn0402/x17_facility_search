"""Deck slides (2026-10-09): why the big plastics win, how big they need to be,
and how much the target region widens the X17 peak.

Reads lnl/out/plastics/*.csv (lnl/plastic_size.py) and lnl/out/scatter/*.csv
(lnl/sim/lnl_scatter.py). Called from build_deck.py: size_slides() after the
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

    # ---- slide 2: days against size ---------------------------------------- #
    P = sd.Plot(1060, 640, x=(20, 120, 'lin'), y=(0.5, 60, 'log'), xlabel='side of a square plastic, 5 cm thick [cm]',
                ylabel='days to 3σ at R(ATOMKI), 1 µA')
    P.xticks([(v, str(v)) for v in (20, 40, 60, 80, 100, 120)]).yticks([(v, f'{v:g}') for v in (0.5, 1, 2, 5, 10, 20, 50)])
    cols = [sd.BLUE, sd.GREEN, sd.ORANGE]
    labs = ['plastics where the bars are now (R = 41 cm)', 'right behind the SiPM wall (R = 35 cm)',
            'no SiPM wall, right behind the MM (R = 26 cm)']
    places = [p for p in dv.placement.unique() if not p.startswith('as-built')]
    best = {}
    for pl, col, lab in zip(places, cols, labs):
        g = dv[dv.placement == pl].sort_values('S_mm')
        g = g[g.days < 60]
        tips = [f'{lab}\n{r.S_mm / 10:.0f}×{r.S_mm / 10:.0f} cm at R = {r.R_front_mm / 10:.1f} cm'
                + (' (pushed back so the plates clear)' if r.pushed_back else '')
                + f'\n{r.days:.2f} d; X17 in window ×{r.s_rel:.2f} of 75×75; plastic {r.plate_area_m2:.2f} m² for 4 arms'
                for r in g.itertuples()]
        P.line(list(g.S_mm / 10), list(g.days), col, 4, markers=False)
        pb = g[g.pushed_back]
        if len(pb):
            P.line(list(pb.S_mm / 10), list(pb.days), col, 12, markers=False)
            P.raw(f'<g opacity="0.25">{P.fore.pop()}</g>')
        P.points(list(g.S_mm / 10)[::2], list(g.days)[::2], col, r=5, tips=tips[::2])
        flat = g.days.min()
        k = g[g.days <= 1.1 * flat].iloc[0]
        best[pl] = (k, flat)
    abp = dv[dv.placement.str.startswith('as-built')].iloc[0]
    P.hline(abp.days, sd.MUT, '4 6', label=f'as-built bars, same cuts: {abp.days:.0f} d',
            tip='The 2×20×30 cm bars with the big-plastic E_sum and cuts (geometry only). With their own 2 cm calorimetry, Geant4 gives 15.5 d.')
    P.points([75], [dv.days_anchor.iloc[0]], sd.INK, r=9, tips=[f'Geant4: 75×75×5 cm at R = 41 cm, {dv.days_anchor.iloc[0]:.2f} d (the anchor)'])
    P.text(77, dv.days_anchor.iloc[0] * 0.78, 'Geant4 75×75', 20, sd.INK)
    k0, f0 = best[places[0]]
    k1, f1 = best[places[1]]
    k2, f2 = best[places[2]]
    side = sd.col(
        sd.legend([(l, c) for l, c in zip(labs, cols)], 20),
        sd.p('thick, faded: plates pushed back so neighbours clear', 20, sd.MUT),
        sd.callout(f'<b>It saturates.</b> At 41 cm, days stop falling at ~{k0.S_mm / 10:.0f} cm: 75 cm already covers the Micromegas cone. '
                   'Bigger buys nothing, because the 40×36 cm Micromegas set the acceptance.', sd.BLUE, 22),
        sd.callout(f'<b>The footprint never binds first.</b> Centred square plates at R collide once S/2 ≳ R − 3 cm; the cone at R is only '
                   f'~0.91·R wide each side. At 41 cm, 75 cm fits with ~1 cm to spare; past ~77 cm they move back and lose a little.', sd.GREY, 22),
        sd.callout(f'<b>Closer is cheaper.</b> Right behind the SiPM wall, ~{k1.S_mm / 10:.0f} cm does the same job ({k1.plate_area_m2:.1f} m² vs 2.3 m² of plastic). '
                   f'Without the SiPM wall in the leg, ~{k2.S_mm / 10:.0f} cm at 26 cm reaches {f2:.2f} d: the 50 cm wall itself cuts {(1 - ins.iloc[4] / ins.iloc[3]) * 100:.0f} % per lepton.', sd.GREEN, 22),
        gap=14, w=600)
    D.slide('size', sd.title(f'~{k0.S_mm / 10:.0f} cm is enough at today\'s distance; past that the Micromegas set the acceptance',
                             'Days to 3σ against the side of four square 5 cm plastics, for three placements. Toy, anchored to Geant4 at 75×75. Hover the points.')
            + sd.row(P.svg('days against plastic size'), side, gap=36),
            f"""<p><b>An analytic stand-in, not Geant4.</b> <code>lnl/plastic_size.py</code>: X17 and Born M1/E1 IPC with the Geant4 generator
kinematics, from a σ = 2 mm spot, into the surveyed arms (SimConfig.hh). A leg needs the lepton through the MM active area, a read-out
SiPM bar (20 bars; none in the orange curve) and the plastic face, after Highland kicks behind the MM (x/X₀ =
{cal.T_MM.iloc[0]:.2f}, fitted) and in the SiPM wall, with KE &gt; {cal.E_TH_MeV.iloc[0]:.2f} MeV (fitted). The two numbers fit the
Geant4 X17 pair-tags (as built 3.3 %, big plastics 23 %). Refitting with a 3 MeV threshold moves the curve by &lt; 7 %.</p>
<p>Days = 1.2 d × (B/B₇₅)/(S/S₇₅)², counting X17 and IPC (γ₀ mix of the ATOMKI 2016 run) in 125–155° after a 5° smear. The
E_sum, MM and TOF efficiencies are held at the Geant4 big-plastic values, so this is geometry only; a thin or small plate would
also lose calorimetry. Footprint: plates centred on each arm, fronts at R from the beam; neighbours touch when S/2 + 1.7 cm (pinwheel)
+ 1 cm (wrap) &gt; R, then R is increased. The SiPM wall stays where it is (fronts at 31.5 cm).</p>
<p>To confirm before buying: one Geant4 run with an oversized plate (the <code>--big-plastic</code> option was made for this:
cut any smaller plate offline from its hits), at 35 cm.</p>""",
            foot='lnl/out/plastics/days_vs_size.csv, calib.csv, footprint.csv', short='Plastic size')


def scatter_slides(D, O):
    S_ = O / 'scatter'
    w = pd.read_csv(S_ / 'widen.csv')
    st = pd.read_csv(S_ / 'widen_stats.csv').set_index('curve')
    sk = pd.read_csv(S_ / 'stacked.csv')
    cost = pd.read_csv(S_ / 'cost.csv')
    bud = pd.read_csv(S_ / 'budget.csv')
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
        sd.p('days to 3σ, same events, counting', 22, weight=600),
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

    # ---- stacked truth vs measured + budget ---------------------------------- #
    def stack_plot(kind, ttl, ylab):
        Q = sd.Plot(540, 500, x=(90, 180, 'lin'), y=(0, 230, 'lin'), xlabel='opening angle [°]', ylabel=ylab,
                    margin=(56, 20, 92, 104), title=ttl)
        Q.xticks([(v, f'{v}°') for v in (90, 120, 150, 180)]).yticks([(v, str(v)) for v in (0, 50, 100, 150, 200)])
        for r in sk.itertuples():
            b, s = getattr(r, f'ipc_{kind}'), getattr(r, f'x17_{kind}')
            Q.raw(f'<rect x="{Q.X(r.theta_lo):.1f}" y="{Q.Y(b):.1f}" width="{Q.X(r.theta_lo + 2) - Q.X(r.theta_lo):.1f}" '
                  f'height="{Q.Y(0) - Q.Y(b):.1f}" fill="{sd.GREY}" fill-opacity="0.45"/>', back=True)
            Q.raw(f'<rect x="{Q.X(r.theta_lo):.1f}" y="{Q.Y(b + s):.1f}" width="{Q.X(r.theta_lo + 2) - Q.X(r.theta_lo):.1f}" '
                  f'height="{Q.Y(b) - Q.Y(b + s):.1f}" fill="{sd.RED}"'
                  f'{sd.tipattr(f"{r.theta_lo:.0f}–{r.theta_lo + 2:.0f}°: IPC {b:.0f}/day, X17 {s:.1f}/day")}/>')
        return Q.svg(ttl)
    brow = []
    for r in bud.itertuples():
        nt = r.layer.startswith('n_TOF')
        brow.append((r.layer.split(',')[0].replace('n_TOF: ³He capsule wall', 'n_TOF capsule wall'), r.sigma68_term_deg,
                     sd.GREY if nt else sd.PURPLE,
                     f'{r.layer}: x/X₀ = {r.x_over_X0 * 100:.3f} %, θ₀ = {r.theta0_deg:.2f}° at 8.6 MeV, lever {r.lever:.2f} → '
                     f'{r.sigma68_term_deg:.2f}° on σ68 (k = {r.k_model:.2f})'))
    side = sd.col(
        sd.p('scattering budget per layer (Highland, 8.6 MeV)', 22, weight=600),
        sd.hbars(brow, 12, width=170, h=22, label_w=200, fmt=lambda v: f'{v:.1f}°', size=19),
        sd.callout('<b>The wall kinks the lepton at r = 25 mm</b>: almost all of it becomes chord error. The MM window and cathode sit at the end of the lever and cost nothing.', sd.PURPLE, 20),
        sd.callout('The n_TOF capsule wall is ~7× more material at the same lever: why n_TOF is 14.5°.', sd.GREY, 20),
        gap=10, w=500)
    D.slide('scatter-stack', sd.title('One day of beam, truth vs measured: the X17 stays visible on the IPC',
                                      'One day at 1 µA with big plastics: IPC (grey) and the X17 at the ATOMKI ratio (red), truth vs measured angle (Geant4, same events). Hover the bins.')
            + sd.row(stack_plot('truth', 'truth angle (no scattering)', 'pairs per day / 2°'),
                     stack_plot('reco', 'as measured (CFRP chamber)', None), side, gap=14),
            f"""<p>Per day at 1 µA, Li₂O 300 µg/cm² at 1.10 MeV, big plastics, MM 15° + TOF, E_sum 13–18 MeV. The IPC is the Born M1 (resonances)
+ E1 (direct capture) + γ₁ mix of <code>yields.csv</code>; Geant4 MC statistics, no smoothing (hence the bin-to-bin noise). Same
style as the n_TOF capsule figure (MX17_Full_Geant docs/angular_resolution, fig_theta_money).</p>
<p>Budget: θ₀ = Highland (plane-projected) for one 8.6 MeV lepton at normal incidence; lever = (L − r)/L with L = 215 mm (air: rms
over its length); × k = {bud.k_model.iloc[0]:.2f} from the appendix model fitted to the three Geant4 L5 walls. The backing row applies only
to leptons that go backward through the foil (an oblique 2× path is assumed). Terms add in quadrature with a ~3.5° floor that is not
material (spot, centroid). <b>Analytic stand-in</b> for the per-layer split; the totals are Geant4.</p>""",
            foot='lnl/out/scatter/stacked.csv, budget.csv', short='Scattering 2')
