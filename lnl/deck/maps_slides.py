"""Pitch slides (2026-10-14): the θ × |y| × E_sum reference fit drawn in 2D, and the
"impostor" test, for the 15 Oct talk.  Dylan's question: in the 1D angle spectrum a
slightly wrong background shape kills any claim, so how do we know an excess is not
mismodelled background?

  pitch-2d          one week in the (θ, |y|) plane: background counts, X17 counts, S/B
  pitch-impostor    a background error that copies the X17 in angle exactly, seen in
                    angle, energy split and energy sum
  pitch-impostor-2d the same in 2D, in the E_sum window and the γ₁ side band, and the
                    fake X17 that each fit reports

Reads lnl/out/nd/maps/{maps,proj,bias}.csv (lnl/sim/lnl_nd_maps.py, FEASIBILITY_SIM §16).
Called from pitch_slides.pitch_slides right after the S/B slide.
"""
import math

import numpy as np
import pandas as pd

import slidedoc as sd

BP = 'big plastics'
DAYS = 7
W_TR = 18.15
REF_STRUCT = 'S_θ 2 % + S_θy 1 %'
CM_B = sd.VIRIDIS
CM_X = [(0.0, '#f7efe9'), (0.35, '#eba08f'), (0.7, '#c63d4f'), (1.0, '#6e1424')]
CM_SB = [(0.0, '#f4f1f6'), (0.5, '#b58bbb'), (1.0, '#4b1d52')]
CM_Z = [(0.0, '#f5f3ee'), (0.3, '#f1c48f'), (0.65, '#d9692a'), (1.0, '#7a2a0c')]
IMP = '#c8601a'         # the impostor (orange), X17 red throughout


def load(O):
    d = O / 'nd' / 'maps'
    if not (d / 'bias.csv').exists():
        return None
    return dict(maps=pd.read_csv(d / 'maps.csv'), proj=pd.read_csv(d / 'proj.csv'), bias=pd.read_csv(d / 'bias.csv'))


def mass_curve(P, m=16.7, color=sd.INK, w=3, dash='10 7', tip=None):
    th = np.linspace(90, 180, 181)
    arg = 1 - 2 * m ** 2 / (W_TR ** 2 * (1 - np.cos(np.radians(th))))
    ok = arg >= 0
    P.line(list(th[ok]), list(np.sqrt(arg[ok])), color, w, dash=dash, markers=False,
           tip=tip or f'constant pair mass m_ee = {m} MeV: where an X17 of that mass lands, (1 − y²)(1 − cos θ) = 2m²/W²')


def heat(title, cells, vmin, vmax, cmap, w=500, h=500, ylab=True, curve=True, tip_curve=None,
         ylabel='energy split |y| = |E₁ − E₂| / (E₁ + E₂)'):
    P = sd.Plot(w, h, x=(90, 180, 'lin'), y=(0, 1, 'lin'), xlabel='opening angle θ [°]',
                ylabel=ylabel if ylab else '',
                margin=(20, 18, 88, 100 if ylab else 56), title=title)
    P.xticks([(v, f'{v}°') for v in (90, 120, 150, 180)])
    P.yticks([(v, f'{v:.1f}') for v in (0, 0.2, 0.4, 0.6, 0.8, 1.0)] if ylab else [(v, '') for v in (0, 0.2, 0.4, 0.6, 0.8, 1.0)])
    P.cells(cells, vmin, vmax, cmap=cmap, gap=0.3)
    if curve:
        mass_curve(P, tip=tip_curve)
    return P


def pitch_maps(D, O):
    L = load(O)
    if L is None:
        D.slide('pitch-2d', sd.title('2D maps: pending', 'Run lnl/sim/lnl_nd_maps.py.'), short='2D maps')
        return
    two_d_counts(D, L)
    impostor_1d(D, L)
    impostor_2d(D, L)


# --------------------------------------------------------------------------- #
def two_d_counts(D, L):
    m = L['maps']
    g = m[(m.hw == BP) & (m.grid == 'fine') & (m.slice == 'window')].copy()
    E0, E1 = g.E_lo.iloc[0], g.E_hi.iloc[0]
    g['B'], g['S'] = g.bkg * DAYS, g.X17 * DAYS
    bmax = g.B.max()
    smax = g.S.max()
    bst = 20 if bmax < 120 else 50
    bhi = math.ceil(bmax / bst) * bst

    def tip(r):
        sb = f'S/B {r.S / r.B * 100:.0f} %' if r.B > 1 else 'S/B –'
        return (f'{r.theta_lo:.0f}–{r.theta_hi:.0f}°, |y| {r.y_lo:.2f}–{r.y_hi:.2f}, {DAYS} days: '
                f'background {r.B:,.1f} (IPC M1 {r.M1 * DAYS:.1f}, E1 {r.E1 * DAYS:.1f}, γ₁ {r.g1 * DAYS:.1f}, cosmics {r.cos * DAYS:.1f}), '
                f'X17 {r.S:.1f}; {sb}')
    cb_ = [(r.theta_lo, r.theta_hi, r.y_lo, r.y_hi, r.B if r.B >= 1 else float('nan'), tip(r)) for r in g.itertuples()]
    cs_ = [(r.theta_lo, r.theta_hi, r.y_lo, r.y_hi, r.S if r.S >= 0.05 else float('nan'), tip(r)) for r in g.itertuples()]
    csb = [(r.theta_lo, r.theta_hi, r.y_lo, r.y_hi, r.S / r.B if r.B >= 3 else float('nan'), tip(r)) for r in g.itertuples()]
    A = heat(f'background, {DAYS} days', cb_, 0, bhi, CM_B)
    B = heat(f'X17 at the ATOMKI ratio, {DAYS} days', cs_, 0, smax, CM_X, ylab=False)
    C = heat('signal / background', csb, 0, 0.4, CM_SB, ylab=False)
    C.hline(0.3, sd.RED, dash='8 6', w=2.5, label='|y| = 0.3', anchor='start', tip='The §12 cut. The fit does not cut: it uses every |y| bin, and the asymmetric pairs measure the background.')
    cbB = sd.colorbar(96, 480, 0, bhi, [(v, f'{v:g}') for v in np.arange(0, bhi + 0.01, bst)], 'pairs', cmap=CM_B)
    st = 5 if smax > 12 else 2
    cbS = sd.colorbar(90, 480, 0, smax, [(v, f'{v:g}') for v in np.arange(0, smax + 0.01, st)], 'X17', cmap=CM_X)
    cbR = sd.colorbar(110, 480, 0, 0.4, [(0, '0'), (0.1, '10 %'), (0.2, '20 %'), (0.3, '30 %'), (0.4, '≥ 40 %')], 'S/B', cmap=CM_SB)

    # the numbers the callouts quote
    tot_B, tot_S = g.B.sum(), g.S.sum()
    w = g[(g.theta_lo >= 125) & (g.theta_hi <= 155)]
    sb1d = w.S.sum() / w.B.sum()
    best = g[(g.B >= 3)].assign(sb=lambda q: q.S / q.B).sort_values('sb', ascending=False)
    top = best.head(int(len(best) * 0.05))
    sbtop = top.S.sum() / top.B.sum()
    low = w[w.y_hi <= 0.3]
    D.slide('pitch-2d', sd.title('One week of pairs in the plane of opening angle × energy split',
                                 f'Big plastics, 1 µA, {DAYS} days, E_sum {E0:g}–{E1:g} MeV, calibrated response, MM 15° + TOF (Geant4). '
                                 'Dashed: where a 16.7 MeV X17 lands. Hover any cell.')
            + sd.row(A.svg('background counts'), cbB, B.svg('X17 counts'), cbS, C.svg('S/B'), cbR, gap=0)
            + sd.row(
                sd.callout(f'<b>Raw counts.</b> ~{round(tot_B, -3):,.0f} background pairs in the window this week, spread over every |y|; '
                           f'~{round(tot_S, -1):.0f} X17. In the 1D spectrum at 125–155° that is S/B ≈ {sb1d * 100:.0f} %: '
                           'a background shape error of a few % competes with the signal.', sd.GREY, 21),
                sd.callout('<b>The X17 is a line, not a bump.</b> A particle of fixed mass reaches the smallest angle only when the '
                           'leptons share the energy equally, so its pairs follow the constant-mass curve. The IPC is a '
                           'virtual photon of any mass: it fills the plane.', sd.RED, 21),
                sd.callout(f'<b>S/B in 2D.</b> The best 5 % of cells reach S/B ≈ {sbtop * 100:.0f} %; at |y| &lt; 0.3, 125–155° it is '
                           f'{low.S.sum() / low.B.sum() * 100:.0f} %. Everything off the curve is background-only: '
                           'the fit measures the background shape there, in the same run.', sd.PURPLE, 21),
                gap=28),
            f"""<p><code>lnl/sim/lnl_nd_maps.py</code> → <code>lnl/out/nd/maps/maps.csv</code> (FEASIBILITY_SIM §16). The event list is the
reference fit's (<code>lnl_nd.collect</code>): Geant4 L1 (X17 m = 16.7 MeV, at R(ATOMKI)), L2 (IPC M1, E1 and γ₁), L3 (EPC), L4
(cosmics), big plastics, MM 15° + TOF, the n_TOF-anchored calibrated response, E_sum window {E0:g}–{E1:g} MeV, 1 µA, live-corrected.
Cells are 3° × 0.05. Each lepton must reach the plastic to make a trigger leg, so neither carries less than a few MeV:
that is the top edge of the background near |y| ≈ 0.8. The background map is KDE-smoothed in θ (5°) as in the fit; the X17 map is not. Cells with fewer than one
background pair (left) or three (right) are blank. The calibrated response smears |y| (measured energies, partial containment),
so the X17 band is wider than the ideal curve. Compare the backup slide "Why |y|", which shows S/B for ideal energies.</p>
<p>The reference fit uses this plane with E_sum as a third axis (two side-band bins, two window bins): 45 θ bins × 6 |y| bins × 4
E_sum bins.</p>""",
            foot='lnl/out/nd/maps/maps.csv (lnl/sim/lnl_nd_maps.py)', short='2D counts')


# --------------------------------------------------------------------------- #
def _excess_plot(pr, var, x, xlab, ylab, xt, title, unit, w=540, h=420, shade=None):
    pr = pr[(pr.lo >= x[0] - 1e-9) & (pr.hi <= x[1] + 1e-9)]
    b = pr[pr.comp == 'bkg'].sort_values('lo')
    s = pr[pr.comp == 'X17'].sort_values('lo')
    im = pr[pr.comp == 'impA'].sort_values('lo')
    edges = list(b.lo) + [b.hi.iloc[-1]]
    sig = np.sqrt(np.maximum(b.per_day.values * DAYS, 0))
    S, I = s.per_day.values * DAYS, im.per_day.values * DAYS
    top = max(S.max(), I.max(), sig.max()) * 1.15
    P = sd.Plot(w, h, x=x, y=(-0.35 * top, top, 'lin'), xlabel=xlab, ylabel=ylab, margin=(20, 20, 88, 96), title=title)
    P.xticks(xt)
    yt = [v for v in sd_nice(top)]
    P.yticks([(v, f'{v:g}') for v in yt])
    if shade:
        for lo, hi, col, lab in shade:
            P.raw(f'<rect x="{P.X(lo):.1f}" y="{P.y0}" width="{P.X(hi) - P.X(lo):.1f}" height="{P.ph}" fill="{col}" fill-opacity="0.09"/>', back=True)
            P.text(0.5 * (lo + hi), top * 0.93, lab, 19, col, 'middle')
    xx, lo_ = sd.step_xy(edges, list(-sig))
    _, hi_ = sd.step_xy(edges, list(sig))
    P.band(xx, lo_, hi_, sd.GREY, 0.22, tip=f'±1σ statistical fluctuation of the background per {unit} in {DAYS} days')
    P.hline(0, sd.MUT, dash=None, w=1.5)
    xx, yy = sd.step_xy(edges, list(S))
    P.line(xx, yy, sd.RED, 4, markers=False, tip=f'X17 at the ATOMKI ratio: {S.sum():.0f} pairs in {DAYS} days here')
    xx, yy = sd.step_xy(edges, list(I))
    P.line(xx, yy, IMP, 4, dash='10 6', markers=False, tip=f'impostor (background error copying the X17 angle spectrum): {I.sum():.0f} pairs here')
    return P


def sd_nice(top):
    for st in (1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000):
        if top / st <= 5:
            return list(np.arange(0, top, st))
    return [0]


def impostor_1d(D, L):
    p = L['proj']
    p = p[p.hw == BP]
    m = L['maps']
    g = m[(m.hw == BP) & (m.grid == 'fine') & (m.slice == 'window')]
    E0, E1 = g.E_lo.iloc[0], g.E_hi.iloc[0]
    A = _excess_plot(p[p['var'] == 'theta'], 'theta', (100, 180, 'lin'), 'opening angle θ [°]', f'excess per 2°, {DAYS} days',
                     [(v, f'{v}°') for v in (100, 120, 140, 160, 180)], 'angle (all |y|, E_sum window)', '2°')
    B = _excess_plot(p[p['var'] == 'y'], 'y', (0, 1, 'lin'), 'energy split |y|', 'per 0.05',
                     [(v, f'{v:.1f}') for v in (0, 0.2, 0.4, 0.6, 0.8, 1.0)], 'energy split (125–155°)', '0.05 in |y|')
    pe = p[p['var'] == 'Esum']
    C = _excess_plot(pe, 'Esum', (pe.lo.min(), pe.hi.max(), 'lin'), 'energy sum E₁ + E₂ [MeV]', 'per 0.5 MeV',
                     [(v, f'{v:g}') for v in range(int(pe.lo.min()) + 1, int(pe.hi.max()) + 1, 2)], 'energy sum (125–155°, all |y|)', '0.5 MeV',
                     shade=[(E0 - 4, E0, sd.GOLD, 'γ₁ side band'), (E0, E1, sd.BLUE, 'window')])
    yy = p[p['var'] == 'y']
    xs, xi = yy[yy.comp == 'X17'], yy[yy.comp == 'impA']
    fx = xs[xs.hi <= 0.3001].per_day.sum() / xs.per_day.sum()
    fi = xi[xi.hi <= 0.3001].per_day.sum() / xi.per_day.sum()
    ee = pe
    win = lambda c, a, b: ee[(ee.comp == c) & (ee.lo >= a - 1e-6) & (ee.hi <= b + 1e-6)].per_day.sum()
    rx = win('X17', E0 - 4, E0) / win('X17', E0, E1)
    ri = win('impA', E0 - 4, E0) / win('impA', E0, E1)
    D.slide('pitch-impostor', sd.title('A background error can fake the angle, not the energies',
                                       f'Excess above the background model in {DAYS} days, big plastics, 1 µA. Red: X17 at the ATOMKI ratio. '
                                       'Orange dashed: an "impostor", a background error built to match the X17 angle spectrum exactly. Grey: ±1σ statistics.')
            + sd.row(A.svg('excess in angle'), B.svg('excess in energy split'), C.svg('excess in energy sum'), gap=20)
            + sd.row(sd.legend([('X17 (ATOMKI ratio)', sd.RED), ('impostor: background error', IMP, 'dash'), ('±1σ background statistics', sd.GREY, 'box')], 20))
            + sd.row(
                sd.callout('<b>In angle alone they are identical</b>, by construction. Any 1D analysis, ours or ATOMKI\'s, '
                           'cannot tell a real X17 from a background shape that is a few % wrong under the edge.', sd.GREY, 20),
                sd.callout(f'<b>Energy split:</b> {fx * 100:.0f} % of the X17 is at |y| &lt; 0.3, against {fi * 100:.0f} % of the impostor. '
                           'A background error has the background\'s energy sharing; the X17 has its own.', sd.RED, 20),
                sd.callout(f'<b>Energy sum:</b> an acceptance or efficiency error does not know the lepton energies, so it appears in the '
                           f'15 MeV γ₁ side band too: ×{ri:.1f} its window size there, against ×{rx:.1f} for the X17.', sd.BLUE, 20),
                gap=28),
            """<p><code>lnl/sim/lnl_nd_maps.py</code>: the impostor takes every X17 event (E_sum window) with its reconstructed angle and
gives it the |y| and E_sum of a background event at the same angle (±1.5°, 30 draws each). Its angle spectrum in the window is
the X17's exactly; its energy sharing and energy sum are the background's. This is impostor A ("acceptance"): a geometry, material
or efficiency error, which is the same at every lepton energy, so it also appears in the γ₁ side band with the background's
weight there. Impostor B (an error only in the 18 MeV IPC physics, absent in the side band) is on the next slide.</p>
<p>The X17 also leaks into the side band (the calibrated response smears E_sum: part of each lepton escapes the plate). The fit
models that; it is in the X17 template.</p>""",
            foot='lnl/out/nd/maps/proj.csv (lnl/sim/lnl_nd_maps.py)', short='Impostor')


# --------------------------------------------------------------------------- #
def impostor_2d(D, L):
    m = L['maps']
    g = m[(m.hw == BP) & (m.grid == 'coarse')].copy()
    E0, E1 = g[g.slice == 'window'].E_lo.iloc[0], g[g.slice == 'window'].E_hi.iloc[0]
    zmax = 3.0

    def panel(sl, comp, title, ylab):
        q = g[g.slice == sl]
        cells = []
        for r in q.itertuples():
            B = r.bkg * DAYS
            v = getattr(r, comp) * DAYS
            z = v / math.sqrt(B) if B >= 3 else float('nan')
            cells.append((r.theta_lo, r.theta_hi, r.y_lo, r.y_hi, z,
                          f'{r.theta_lo:.0f}–{r.theta_hi:.0f}°, |y| {r.y_lo:.1f}–{r.y_hi:.1f}, E_sum {r.E_lo:g}–{r.E_hi:g} MeV, {DAYS} d: '
                          f'{"X17" if comp == "X17" else "impostor"} {v:.1f} on background {B:,.0f}: {z:+.1f}σ in this cell' if B >= 3 else None))
        return heat(title, cells, 0, zmax, CM_Z, w=420, h=330, ylab=ylab, ylabel='energy split |y|')
    P = [[panel('window', 'X17', f'X17 · window {E0:g}–{E1:g} MeV', True), panel('side band', 'X17', f'X17 · side band {E0 - 4:g}–{E0:g} MeV', False)],
         [panel('window', 'impA', 'impostor · window', True), panel('side band', 'impA', 'impostor · side band', False)]]
    cb = sd.colorbar(110, 640, 0, zmax, [(0, '0'), (1, '1σ'), (2, '2σ'), (3, '≥ 3σ')], 'excess / √B', cmap=CM_Z)
    grid = sd.row(sd.col(sd.row(P[0][0].svg('X17 window'), P[0][1].svg('X17 side band'), gap=0),
                         sd.row(P[1][0].svg('impostor window'), P[1][1].svg('impostor side band'), gap=0), gap=0), cb, gap=4)

    b = L['bias']
    b0 = b[(b.hw == BP) & (b.days == DAYS) & (b.structure == 'none') & (b.impostor == 'A')].set_index('analysis')
    r0, r10 = b0.loc['θ × |y| × E_sum'], b0.loc['θ']
    b = b[(b.hw == BP) & (b.days == DAYS) & (b.structure == REF_STRUCT)].set_index(['analysis', 'impostor'])
    lab = {'θ': 'angle alone', 'm_ee': 'pair mass m_ee', 'θ × |y|': 'angle × split', 'θ × |y| × E_sum': 'angle × split × sum'}
    rows = []
    for a in ('θ', 'm_ee', 'θ × |y|', 'θ × |y| × E_sum'):
        r = b.loc[(a, 'A')]
        col = sd.RED if r.fake_r > 0.5 else (sd.BLUE if a == 'θ × |y| × E_sum' else sd.GREY)
        rows.append((lab[a], r.fake_r * 100, col,
                     f'{lab[a]} fit, {DAYS} days: the impostor (a full ATOMKI-size bump in angle) is reported as r = {r.fake_r:.2f} of an X17, '
                     f'{r.fake_Z:+.1f}σ; a real X17 would be {r.true_Z:.1f}σ. χ² the fit cannot absorb: {r.chi2_resid:.1f}.'))
    rB = b.loc[('θ × |y| × E_sum', 'B')]
    rA = b.loc[('θ × |y| × E_sum', 'A')]
    r1 = b.loc[('θ', 'A')]
    side = sd.col(
        sd.p(f'How much of the impostor each fit calls X17 ({DAYS} d)', 22, weight=600),
        sd.hbars(rows, 100, width=230, h=30, label_w=210, fmt=lambda v: f'{v:.0f} %', size=20),
        sd.callout(f'<b>The angle-only fit is fooled completely</b>: it reads the impostor as {r1.fake_r * 100:.0f} % of an X17, exactly '
                   'as significant as the real thing however long we run. The 2D and 3D fits report ≤ ¼ of it '
                   f'(~{rA.fake_Z:.0f}σ in a week), while a real X17 is {rA.true_Z:.1f}σ.', sd.BLUE, 19),
        sd.callout(f'<b>And the data say so.</b> The impostor leaves χ² ≈ {rA.chi2_resid:.0f} the 3D fit cannot absorb in a week '
                   f'(≈ {r1.chi2_resid:.0f} in 1D): the excess sits at high |y| and in the side band, where no X17 can be.', sd.GREEN, 19),
        sd.callout(f'<b>What no fit catches:</b> a background error that is symmetric, at the edge and only at 18 MeV, i.e. shaped '
                   f'like the X17 in all three. An error only in the 18 MeV IPC physics (impostor B) still reads as {rB.fake_r * 100:.0f} %. '
                   'The checks for that are physics: QED fixes the IPC shape, and the X17 edge moves with E_p (441 keV, off-resonance) '
                   'where a detector effect does not.', sd.ORANGE, 19),
        gap=10, w=640)
    D.slide('pitch-impostor-2d', sd.title('In 2D the X17 is a spot and a background error is a stripe',
                                          f'Local significance per 6° × 0.1 cell after {DAYS} days, big plastics, 1 µA: the X17 (top) and the impostor of the last slide (bottom), '
                                          'in the E_sum window (left) and the γ₁ side band (right). Hover the cells and bars.')
            + sd.row(grid, side, gap=24),
            f"""<p><code>lnl/sim/lnl_nd_maps.py</code> → <code>maps.csv</code> (coarse grid) and <code>bias.csv</code>. The bars are the
linear (Asimov) response of each fit to a background model that is wrong by the impostor: the fitted X17 strength moves by
(T F + P)⁻¹ T Σ g Δ/μ, with F, P the fit's Fisher and prior matrices after T = {DAYS} days, g the parameter derivatives and Δ the
impostor. The fits are the reference ones (lnl_nd.py): M1, E1, γ₁ norms, anisotropy, θ and |y| resolution, E scale, four arm gains,
a free acceptance cubic in θ, a |y| tilt, and unknown structure S_θ 2 % + S_θy 1 %. The impostor is as large as the X17 itself at the
ATOMKI ratio. "χ² left" is the part of Σ Δ²/μ the free parameters cannot absorb, i.e. the Asimov goodness-of-fit penalty
for the wrong model; over ~1000 bins a Δχ² of 20 is not a subtle effect but not a single-bin alarm either.</p>
<p>Impostor B (an error confined to the 18 MeV window, every |y|): {rB.fake_r * 100:.0f} % in the 3D fit, {rB.fake_Z:+.1f}σ, χ² left
{rB.chi2_resid:.0f}. With no structure terms at all, the 3D fit reads impostor A as {r0.fake_r * 100:.0f} % (the angle-only fit
{r10.fake_r * 100:.0f} %): the |y| and E_sum axes do most of the work, not the Gaussian-process freedom.</p>
<p>Why n_TOF could not do this: the edge was smeared to σ68 14.5° by the capsule, the excitation energy changes with the neutron
energy (no fixed E_sum line, no signal-free side band from the same reaction), the arms contained ~40 % of the lepton energy, and the
background was neutron capture in the capsule, whose shape QED does not predict. So the n_TOF search had to rest on the opening
angle, the top bar.</p>""",
            foot='lnl/out/nd/maps/maps.csv, bias.csv (lnl/sim/lnl_nd_maps.py)', short='Impostor 2D')
