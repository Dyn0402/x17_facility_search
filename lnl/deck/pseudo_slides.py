"""Pitch slides (2026-10-14): the analysis run end to end on one simulated week of data, as if it were
real, and the coupling scan over many simulated experiments.  Dylan: "show a full simulated
step-by-step analysis ... as if it were experimental data and we don't have perfect knowledge of
the background".

  pitch-pe-data     step 1: the data in (θ, |y|), window and γ₁ side band, against the raw Monte Carlo
  pitch-pe-zoom     step 2: the signal region, and why the raw Monte Carlo cannot simply be subtracted
  pitch-pe-blind    step 3: blind the signal region, measure the background in the control regions
  pitch-pe-unblind  step 4: data minus the predicted background
  pitch-pe-scan     can we measure the coupling, or exclude it?  pseudo-experiments at each injected r

Reads lnl/out/pseudo/ (lnl/sim/lnl_pseudo.py, FEASIBILITY_SIM §17).  Called from pitch_slides after
the impostor slides.
"""
import json
import math

import numpy as np
import pandas as pd

import slidedoc as sd

R_ATOMKI = 5.8e-6
R_MEG = 1.2e-5
CM_N = sd.VIRIDIS
CM_D = sd.DIVERGE
SRC = '#c8601a'     # the blinded signal region


def load(O):
    d = O / 'pseudo'
    if not (d / 'walk_summary.json').exists():
        return None
    out = dict(b=pd.read_csv(d / 'walk_bins.csv'), p=pd.read_csv(d / 'walk_proj.csv'),
               s=json.loads((d / 'walk_summary.json').read_text()))
    if (d / 'scan.csv').exists():
        sc = [pd.read_csv(d / 'scan.csv')]
        if (d / 'scan_widened.csv').exists():
            sc.append(pd.read_csv(d / 'scan_widened.csv'))
        out['scan'] = pd.concat(sc, ignore_index=True)
    return out


def agg(b, win, dth, cols, th=(90, 180), ymax=1.0):
    q = b[(b.ebin >= 2) if win else (b.ebin < 2)]
    q = q[(q.theta_lo >= th[0]) & (q.theta_lo < th[1]) & (q.y_lo < ymax - 1e-9)].copy()
    q['tc'] = th[0] + np.floor((q.theta_lo - th[0]) / dth) * dth
    g = q.groupby(['tc', 'y_lo'])
    a = g[cols].sum().reset_index()
    a['sr'] = g['sr'].any().values
    return a


def heat(title, cells, vmin, vmax, cmap, th=(90, 180), ymax=1.0, w=520, h=470, ylab=True, xt=None):
    P = sd.Plot(w, h, x=(th[0], th[1], 'lin'), y=(0, ymax, 'lin'), xlabel='opening angle θ [°]',
                ylabel='energy split |y|' if ylab else '', margin=(20, 18, 86, 92 if ylab else 50), title=title)
    P.xticks(xt or [(v, f'{v}°') for v in range(int(th[0]), int(th[1]) + 1, 30)])
    yt = [v for v in np.arange(0, ymax + 1e-9, 0.2 if ymax > 0.6 else 0.1)]
    P.yticks([(v, f'{v:.1f}' if ylab else '') for v in yt])
    P.cells(cells, vmin, vmax, cmap=cmap, gap=0.25)
    return P


def outline(P, a, dth, dy=0.05, color=SRC, w=3):
    """draw the boundary of the signal-region cells."""
    s = {(round(r.tc, 3), round(r.y_lo, 3)) for r in a.itertuples() if r.sr}
    o = []
    for (t, y) in s:
        for (dt_, dy_, x1, y1, x2, y2) in ((-dth, 0, t, y, t, y + dy), (dth, 0, t + dth, y, t + dth, y + dy),
                                           (0, -dy, t, y, t + dth, y), (0, dy, t, y + dy, t + dth, y + dy)):
            if (round(t + dt_, 3), round(y + dy_, 3)) not in s:
                o.append(sd.line(P.X(x1), P.Y(y1), P.X(x2), P.Y(y2), color, w))
    P.raw(''.join(o))


def errbars(P, xs, ys, es, color=sd.INK, r=5, tips=None):
    o = []
    for x, y, e in zip(xs, ys, es):
        o.append(sd.line(P.X(x), P.Y(y - e), P.X(x), P.Y(y + e), color, 2))
    P.raw(''.join(o))
    P.points(xs, ys, color, r=r, tips=tips)


def mass_curve(P, m=16.7, W=18.15, color=sd.INK):
    th = np.linspace(90, 180, 181)
    arg = 1 - 2 * m ** 2 / (W ** 2 * (1 - np.cos(np.radians(th))))
    ok = arg >= 0
    P.line(list(th[ok]), list(np.sqrt(arg[ok])), color, 2.5, dash='9 6', markers=False,
           tip=f'where a {m} MeV X17 lands for ideal energies')


def pseudo_slides(D, O):
    L = load(O)
    if L is None:
        D.slide('pitch-pe-data', sd.title('Simulated analysis: pending', 'Run lnl/sim/lnl_pseudo.py.'), short='Sim. data')
        return
    s = L['s']
    step_data(D, L)
    step_zoom(D, L)
    step_blind(D, L)
    step_unblind(D, L)
    if 'scan' in L:
        scan_slide(D, L)


def kicker(n, txt):
    return f'<p style="font-size:24px;font-weight:600;color:{SRC};letter-spacing:1px;margin-bottom:-18px">STEP {n} OF 4 · {txt}</p>'


# --------------------------------------------------------------------------- #
def step_data(D, L):
    b, p, s = L['b'], L['p'], L['s']
    T = s['days']
    aw = agg(b, True, 4, ['data', 'nominal_mc'])
    asb = agg(b, False, 4, ['data', 'nominal_mc'])
    vmax = math.ceil(max(aw.data.max(), asb.data.max()) / 100) * 100

    def cells(a, lab):
        return [(r.tc, r.tc + 4, r.y_lo, r.y_lo + 0.05, r.data if r.data > 0 else float('nan'),
                 f'{lab}: {r.tc:.0f}–{r.tc + 4:.0f}°, |y| {r.y_lo:.2f}–{r.y_lo + 0.05:.2f}: {r.data:.0f} pairs '
                 f'(raw Monte Carlo predicts {r.nominal_mc:.0f})') for r in a.itertuples()]
    E0, E1 = b[b.ebin == 2].E_lo.iloc[0], b[b.ebin == 3].E_hi.iloc[0]
    A = heat(f'data · window {E0:g}–{E1:g} MeV', cells(aw, 'window'), 0, vmax, CM_N)
    mass_curve(A)
    B = heat(f'data · γ₁ side band {E0 - 4:g}–{E0:g} MeV', cells(asb, 'side band'), 0, vmax, CM_N, ylab=False)
    cb = sd.colorbar(100, 470, 0, vmax, [(v, f'{v:g}') for v in np.linspace(0, vmax, 5)], f'pairs / cell', cmap=CM_N)
    q = p[p['sel'] == 'window, all |y|']
    q = q[q.theta_lo >= 100]
    C = sd.Plot(560, 470, x=(100, 180, 'lin'), y=(0, q.data.max() * 1.15, 'lin'), xlabel='opening angle θ [°]',
                ylabel='pairs per 2°', margin=(20, 18, 86, 96), title='window, all |y|, in 1D')
    C.xticks([(v, f'{v}°') for v in (100, 120, 140, 160, 180)])
    C.yticks([(v, f'{v:,.0f}') for v in np.arange(0, q.data.max() * 1.15, 500 if q.data.max() > 1500 else 200)])
    xc = list(q.theta_lo + 1)
    xx, yy = sd.step_xy(list(q.theta_lo) + [180], list(q.nominal_mc))
    C.line(xx, yy, sd.GREY, 3.5, markers=False, tip='raw Monte Carlo: nominal IPC + γ₁ + cosmics, as simulated')
    errbars(C, xc, list(q.data), list(np.sqrt(q.data)), sd.INK, 4,
            tips=[f'{t:.0f}–{t + 2:.0f}°: data {d:.0f}, raw MC {m:.0f}' for t, d, m in zip(q.theta_lo, q.data, q.nominal_mc)])
    D.slide('pitch-pe-data', kicker(1, 'THE DATA') + sd.title(f'One simulated week, as the experiment would record it',
                                                               f'{T:.0f} days, 1 µA, big plastics. The X17 is in at the ATOMKI ratio, and the true background '
                                                               'differs from our Monte Carlo in ways the fit is not told. Hover the cells and points.')
            + sd.row(A.svg('data window'), B.svg('data side band'), cb, C.svg('1D'), gap=4)
            + sd.row(
                sd.callout(f'<b>~{round(aw.data.sum(), -3):,.0f} pairs in the window</b> and ~{round(asb.data.sum(), -3):,.0f} in the '
                           '15 MeV side band. The dashed curve is where an X17 would land. By eye: nothing.', sd.GREY, 20),
                sd.callout('<b>How the "truth" differs from our model:</b> the IPC and γ₁ normalisations by ~10 %, the acceptance by '
                           '3 % per term, every nuisance within its prior. On top of that, 2 % shape errors in angle × energy sum '
                           'and in pair mass that the fit does not contain at all.', sd.ORANGE, 20),
                sd.callout(f'<b>In 1D the raw Monte Carlo (grey) does not describe the data</b> at the few-% level. The X17 is a '
                           '~10 % bump on this, so we cannot just subtract the simulation.', sd.BLUE, 20), gap=24),
            f"""<p><code>lnl/sim/lnl_pseudo.py</code> (FEASIBILITY_SIM §17). Pseudo-data: Poisson draws in θ (2°) × |y| (0.05) × E_sum
(10–12, 12–14 | 14–16.5, 16.5–19 MeV) from a "truth" built on the reference fit's Geant4 event list (big plastics, calibrated
response, MM 15° + TOF). Truth = nominal + random shifts of every background parameter (M1, E1, γ₁ norms σ 10 %; acceptance cubic
σ 3 %; anisotropy, resolutions, E scale, arm gains, |y| tilt at their priors; the modelled structure S_θ 2 % + S_θy 1 % at N(0, 1))
+ structure the fit does not have: S_θE 2 % and S_m 2 % (ℓ 0.55 MeV), {s['n_par_unmodelled']} modes in all. X17 at r = {s['r_inj']:g}
(R = R(ATOMKI)), seed {s['seed']}: one pseudo-experiment, not chosen. Display cells are 4° × 0.05.</p>""",
            foot='lnl/out/pseudo/walk_bins.csv (lnl/sim/lnl_pseudo.py)', short='Sim. 1: data')


# --------------------------------------------------------------------------- #
def step_zoom(D, L):
    b, p, s = L['b'], L['p'], L['s']
    th = (116, 172)
    a = agg(b, True, 2, ['data', 'nominal_mc', 'truth_sig'], th=th, ymax=0.6)
    vmax = math.ceil(a.data.max() / 20) * 20
    c1 = [(r.tc, r.tc + 2, r.y_lo, r.y_lo + 0.05, r.data,
           f'{r.tc:.0f}–{r.tc + 2:.0f}°, |y| {r.y_lo:.2f}–{r.y_lo + 0.05:.2f}: {r.data:.0f} pairs') for r in a.itertuples()]
    xt = [(v, f'{v}°') for v in (120, 135, 150, 165)]
    A = heat('data, zoomed', c1, 0, vmax, CM_N, th=th, ymax=0.6, w=500, xt=xt)
    mass_curve(A)
    zl = 3.0
    c2 = []
    for r in a.itertuples():
        z = (r.data - r.nominal_mc) / math.sqrt(r.nominal_mc) if r.nominal_mc > 2 else float('nan')
        c2.append((r.tc, r.tc + 2, r.y_lo, r.y_lo + 0.05, (z + zl) / (2 * zl),
                   f'{r.tc:.0f}–{r.tc + 2:.0f}°, |y| {r.y_lo:.2f}–{r.y_lo + 0.05:.2f}: data {r.data:.0f}, raw MC {r.nominal_mc:.0f}: {z:+.1f}σ'))
    B = heat('(data − raw MC) / √MC', c2, 0, 1, CM_D, th=th, ymax=0.6, w=470, ylab=False, xt=xt)
    mass_curve(B)
    cbz = sd.colorbar(90, 470, 0, 1, [(0, f'−{zl:g}σ'), (0.5, '0'), (1, f'+{zl:g}σ')], 'pull', cmap=CM_D)
    q = p[(p['sel'] == 'window, |y|<0.3') & (p.theta_lo >= 110) & (p.theta_lo < 170)]
    C = sd.Plot(540, 470, x=(110, 170, 'lin'), y=(0, q.data.max() * 1.2, 'lin'), xlabel='opening angle θ [°]',
                ylabel='pairs per 2°', margin=(20, 18, 86, 92), title='|y| < 0.3, window')
    C.xticks([(v, f'{v}°') for v in (110, 130, 150, 170)])
    C.yticks([(v, f'{v:g}') for v in np.arange(0, q.data.max() * 1.2, 50 if q.data.max() > 150 else 20)])
    xx, yy = sd.step_xy(list(q.theta_lo) + [170], list(q.nominal_mc))
    C.line(xx, yy, sd.GREY, 3.5, markers=False, tip='raw Monte Carlo (no X17)')
    errbars(C, list(q.theta_lo + 1), list(q.data), list(np.sqrt(q.data)), sd.INK, 4,
            tips=[f'{t:.0f}–{t + 2:.0f}°: data {d:.0f}, raw MC {m:.0f}' for t, d, m in zip(q.theta_lo, q.data, q.nominal_mc)])
    win = q[(q.theta_lo >= 128) & (q.theta_lo < 146)]
    exc = win.data.sum() - win.nominal_mc.sum()
    D.slide('pitch-pe-zoom', kicker(2, 'THE SIGNAL REGION') + sd.title('Zoomed in: a bump at the edge, on a rough background',
                                                                        'Same pseudo-data: 116–172°, |y| < 0.6, E_sum window, 2° × 0.05 cells. Middle: the data against the raw '
                                                                        'Monte Carlo, in standard deviations. Hover.')
            + sd.row(A.svg('zoom data'), B.svg('data - MC'), cbz, C.svg('1D zoom'), gap=4)
            + sd.row(
                sd.callout(f'<b>The X17 shows</b> as an excess along the dashed curve, strongest at 130–140° and small |y|: '
                           f'{exc:+.0f} pairs over the raw MC at 128–146°, |y| &lt; 0.3.', sd.RED, 20),
                sd.callout('<b>But the raw MC is also wrong elsewhere:</b> blue and red cells away from the curve are the '
                           'background mismodelling. Subtracting the simulation would give a "signal" of the wrong size, '
                           'and a 1D analysis could not tell which part is which.', sd.ORANGE, 20),
                sd.callout('<b>So the background has to come from the data</b>, in the regions where no X17 can be: '
                           'next step.', sd.BLUE, 20), gap=24),
            """<p>Pull per cell = (data − raw MC)/√MC, with the raw MC the nominal simulation (no X17, no fitted parameters). The
injected X17 in the plotted |y| &lt; 0.3 band is in the Details of step 4. Cells with fewer than 2 expected pairs are blank.</p>""",
            foot='lnl/out/pseudo/walk_bins.csv, walk_proj.csv', short='Sim. 2: zoom')


# --------------------------------------------------------------------------- #
def step_blind(D, L):
    b, p, s = L['b'], L['p'], L['s']
    a = agg(b, True, 2, ['data', 'truth_sig'], th=(90, 180), ymax=1.0)
    # region diagram: SR orange, control grey shades
    cells = []
    for r in a.itertuples():
        v = 0.9 if r.sr else (0.15 if r.y_lo >= 0.45 else 0.35)
        cells.append((r.tc, r.tc + 2, r.y_lo, r.y_lo + 0.05, v,
                      f'{r.tc:.0f}–{r.tc + 2:.0f}°, |y| {r.y_lo:.2f}: ' + ('SIGNAL REGION, blinded' if r.sr else 'control region')))
    cm = [(0.0, '#e9e6df'), (0.4, '#cfcac0'), (0.6, '#f5d2b3'), (1.0, '#e39a5c')]
    A = heat('the plan, E_sum window', cells, 0, 1, cm, w=560, h=470)
    outline(A, a, 2)
    mass_curve(A)
    A.text(96, 0.9, 'asymmetric pairs: background only', 19, sd.INK)
    A.text(94, 0.2, 'below the edge', 19, sd.INK)
    A.text(152, 0.02, 'blinded', 21, SRC, weight=600)
    # 1D: |y|<0.3 window, SR hidden, prediction band, truth
    q = p[(p['sel'] == 'window, |y|<0.3') & (p.theta_lo >= 110) & (p.theta_lo < 170)]
    B = sd.Plot(520, 470, x=(110, 170, 'lin'), y=(0, q.data.max() * 1.2, 'lin'), xlabel='opening angle θ [°]',
                ylabel='pairs per 2°', margin=(20, 18, 86, 92), title='|y| < 0.3, predicted from outside')
    B.xticks([(v, f'{v}°') for v in (110, 130, 150, 170)])
    B.yticks([(v, f'{v:g}') for v in np.arange(0, q.data.max() * 1.2, 50 if q.data.max() > 150 else 20)])
    srq = q[q.in_sr]
    B.raw(f'<rect x="{B.X(srq.theta_lo.min()):.1f}" y="{B.y0}" width="{B.X(srq.theta_lo.max() + 2) - B.X(srq.theta_lo.min()):.1f}" '
          f'height="{B.ph}" fill="{SRC}" fill-opacity="0.10"/>', back=True)
    B.text(0.5 * (srq.theta_lo.min() + srq.theta_lo.max() + 2), q.data.max() * 1.12, 'blinded', 20, SRC, 'middle', 600)
    edges = list(q.theta_lo) + [170]
    xx, lo = sd.step_xy(edges, list(q.blind_pred - q.blind_sig))
    _, hi = sd.step_xy(edges, list(q.blind_pred + q.blind_sig))
    B.band(xx, lo, hi, sd.BLUE, 0.25, tip='background predicted by the blinded fit, ±1σ')
    xx, yy = sd.step_xy(edges, list(q.blind_pred))
    B.line(xx, yy, sd.BLUE, 3.5, markers=False, tip='background predicted by the fit to the control regions')
    xx, yy = sd.step_xy(edges, list(q.truth_bkg))
    B.line(xx, yy, sd.GREEN, 2.5, dash='7 5', markers=False, tip='the TRUE background (known only because this is a simulation)')
    o = q[~q.in_sr]
    errbars(B, list(o.theta_lo + 1), list(o.data), list(np.sqrt(o.data)), sd.INK, 4,
            tips=[f'{t:.0f}–{t + 2:.0f}°: data {d:.0f}, predicted {m:.0f}' for t, d, m in zip(o.theta_lo, o.data, o.blind_pred)])
    tn, bn = s['truth_norms'], s['blind_norms']
    rows = [[k_, f'{tn[k]:+.0%}'.replace('%', ' %'), f'{bn[k]:+.0%}'.replace('%', ' %')] for k, k_ in (('E1', 'IPC E1 norm'), ('M1', 'IPC M1 norm'), ('g1', 'γ₁ norm'))]
    rows.append(['<b>background in the blinded region</b>', f'{s["sr_truth_bkg"]:,.0f}', f'<b>{s["sr_pred"]:,.0f} ± {s["sr_pred_sigma"]:.0f}</b>'])
    tab = sd.table(['', 'truth', 'measured'], rows, size=20, widths=[300, 110, 170])
    side = sd.col(
        sd.p('What the control regions measured', 22, weight=600), tab,
        sd.callout(f'<b>Blind first.</b> The {s["sr_cells"]} cells holding {s["sr_frac_signal"] * 100:.0f} % of the expected X17 are '
                   'hidden. The background-only fit uses everything else: the γ₁ side band (same acceptance, no 18 MeV '
                   'transition), the asymmetric pairs, and the angles below the edge.', SRC, 19),
        sd.callout(f'<b>It predicts the hidden background to {s["sr_pred_sigma"] / s["sr_pred"] * 100:.1f} %</b>, and it is right: '
                   f'{s["sr_pred"]:,.0f} against a true {s["sr_truth_bkg"]:,.0f} '
                   f'({(s["sr_pred"] - s["sr_truth_bkg"]) / s["sr_pred_sigma"]:+.1f}σ), even with shape errors it was not told about.', sd.BLUE, 19),
        gap=12, w=560)
    D.slide('pitch-pe-blind', kicker(3, 'BACKGROUND FROM THE DATA') + sd.title('Measure the background where the X17 cannot be',
                                                                                'Left: the plan in the E_sum window (orange = blinded; the side band is all control). '
                                                                                'Middle: the background predicted in the blinded region (blue band) and, because this is '
                                                                                'a simulation, the truth (green dashed).')
            + sd.row(A.svg('regions'), B.svg('blinded prediction'), side, gap=20),
            f"""<p>The blinded fit is the reference model with r fixed at 0 and the signal-region bins removed: M1, E1, γ₁ norms and the
acceptance cubic free; anisotropy, θ and |y| resolution, E scale, arm gains, |y| tilt and the S_θ 2 % + S_θy 1 % structure with their
priors ({s['n_par_fit']} parameters, {s['n_bins']} bins). The band is the fit covariance propagated to each bin. The S_θE and S_m
structure in the truth is not in this model at all.</p>
<p>About {100 - s['sr_frac_signal'] * 100:.0f} % of the X17 falls outside the blinded region (the response smears |y| and E_sum), so the
control regions carry a little signal; the blinded fit absorbs part of it into the background. That is why step 4's excess in the
blinded region is a little below the injected signal, and why the final number comes from the full fit, which models the signal
everywhere.</p>""",
            foot='lnl/out/pseudo/walk_proj.csv, walk_summary.json', short='Sim. 3: blind')


# --------------------------------------------------------------------------- #
def step_unblind(D, L):
    b, p, s = L['b'], L['p'], L['s']
    th = (116, 172)
    a = agg(b, True, 2, ['data', 'blind_pred', 'truth_sig'], th=th, ymax=0.6)
    zl = 3.0
    cells = []
    for r in a.itertuples():
        z = (r.data - r.blind_pred) / math.sqrt(r.blind_pred) if r.blind_pred > 2 else float('nan')
        cells.append((r.tc, r.tc + 2, r.y_lo, r.y_lo + 0.05, (z + zl) / (2 * zl),
                      f'{r.tc:.0f}–{r.tc + 2:.0f}°, |y| {r.y_lo:.2f}: data {r.data:.0f} − background {r.blind_pred:.0f} = {r.data - r.blind_pred:+.0f} '
                      f'({z:+.1f}σ); true X17 here {r.truth_sig:.1f}'))
    xt = [(v, f'{v}°') for v in (120, 135, 150, 165)]
    A = heat('(data − background) / √bkg', cells, 0, 1, CM_D, th=th, ymax=0.6, w=500, xt=xt)
    outline(A, a, 2)
    mass_curve(A)
    cbz = sd.colorbar(90, 470, 0, 1, [(0, f'−{zl:g}σ'), (0.5, '0'), (1, f'+{zl:g}σ')], 'pull', cmap=CM_D)

    def resid(sel, title, ylab):
        q = p[(p['sel'] == sel) & (p.theta_lo >= 110) & (p.theta_lo < 170)]
        d = q.data - q.blind_pred
        e = np.sqrt(q.data + q.blind_sig ** 2)
        top = max(q.truth_sig.max(), (d + e).max(), (e - d).max(), 30) * 1.15
        bot = -max((e - d).max() * 1.1, 0.45 * top)
        P = sd.Plot(480, 470, x=(110, 170, 'lin'), y=(bot, top, 'lin'), xlabel='opening angle θ [°]',
                    ylabel=ylab, margin=(20, 18, 86, 88), title=title)
        P.xticks([(v, f'{v}°') for v in (110, 130, 150, 170)])
        st = 20 if top < 120 else 50
        P.yticks([(v, f'{v:g}') for v in np.arange(-st * math.floor(-bot / st), top, st)])
        P.hline(0, sd.MUT, dash=None, w=1.5)
        edges = list(q.theta_lo) + [170]
        xx, yy = sd.step_xy(edges, list(q.truth_sig))
        P.line(xx, yy, sd.RED, 3.5, markers=False, tip='the X17 actually injected (truth)')
        xx, yy = sd.step_xy(edges, list(q.fit_sig))
        P.line(xx, yy, sd.BLUE, 3, dash='8 5', markers=False, tip=f'the X17 the full fit measures: r̂ = {s["r_hat"]:.2f} ± {s["sigma"]:.2f}')
        errbars(P, list(q.theta_lo + 1), list(d), list(e), sd.INK, 4,
                tips=[f'{t:.0f}–{t + 2:.0f}°: data − background = {v:+.0f} ± {u:.0f}' for t, v, u in zip(q.theta_lo, d, e)])
        return P
    B = resid('window, |y|<0.3', 'symmetric pairs |y| < 0.3', 'data − background per 2°')
    C = resid('window, |y|>0.45', 'asymmetric |y| > 0.45: control', '')
    exc, ex_e = s['sr_excess'], math.sqrt(s['sr_data'] + s['sr_pred_sigma'] ** 2)
    D.slide('pitch-pe-unblind', kicker(4, 'UNBLIND') + sd.title(f'Data − background: the X17 returns, r̂ = {s["r_hat"]:.2f} ± {s["sigma"]:.2f}',
                                                                 'The background predicted by the blinded fit is subtracted. Points: data − background, ±1σ (data and '
                                                                 'prediction). Red: the X17 injected. Blue dashed: what the full fit measures.')
            + sd.row(A.svg('residual map'), cbz, B.svg('residual sym'), C.svg('residual asym'), gap=4)
            + sd.row(
                sd.callout(f'<b>In the blinded region:</b> {s["sr_data"]:,.0f} pairs on a predicted {s["sr_pred"]:,.0f} ± {s["sr_pred_sigma"]:.0f}: '
                           f'an excess of {exc:,.0f} ± {ex_e:.0f} ({exc / ex_e:.1f}σ). The X17 put in there: {s["sr_truth_sig"]:,.0f}.', SRC, 20),
                sd.callout(f'<b>The full fit</b> (all bins, signal free): r̂ = {s["r_hat"]:.2f} ± {s["sigma"]:.2f}, '
                           f'{s["Z"]:.1f}σ, for a true r = {s["r_inj"]:g}. The excess sits on the X17 curve at small |y|.', sd.BLUE, 20),
                sd.callout('<b>And nowhere else:</b> the asymmetric pairs (right) are flat at zero. Mismodelled background would show '
                           'there too; an X17 cannot.', sd.GREEN, 20), gap=24),
            f"""<p>Residual = data − blinded-fit prediction; error = √(data + σ²_prediction). The excess in the blinded region is below the
injected {s['sr_truth_sig']:,.0f} because the blinded fit absorbs the ~30 % of the X17 that falls in the control regions (step 3
Details); the full fit, which models the signal in every bin, is the measurement: r̂ = {s['r_hat']:.3f} ± {s['sigma']:.3f}, 90 % CL
upper limit {s['UL90']:.2f}, χ² {s['chi2_full']:.0f} for {s['n_bins']} bins and {s['n_par_fit']} parameters (many with priors). One
pseudo-experiment; the next slide runs a thousand.</p>""",
            foot='lnl/out/pseudo/walk_bins.csv, walk_proj.csv, walk_summary.json', short='Sim. 4: unblind')


# --------------------------------------------------------------------------- #
def scan_slide(D, L):
    sc = L['scan']
    ref = sc[sc.variant == 'reference']
    days = sorted(ref.days.unique())
    cols = {1.0: sd.GOLD, 7.0: sd.BLUE, 30.0: sd.PURPLE}
    rmax = ref.r_inj.max()
    A = sd.Plot(600, 520, x=(0, rmax, 'lin'), y=(-0.4, rmax * 1.25, 'lin'), xlabel='true X17 strength r = R / R(ATOMKI)',
                ylabel='measured r̂ (median, 68 % band)', margin=(20, 18, 86, 96), title='do we measure what is there?')
    A.xticks([(v, f'{v:g}') for v in (0, 0.5, 1.0, 1.5)]).yticks([(v, f'{v:g}') for v in (0, 0.5, 1.0, 1.5)])
    A.line([0, rmax], [0, rmax], sd.MUT, 2, dash='6 6', markers=False, tip='r̂ = r: perfect measurement')
    for dd in days:
        g = ref[ref.days == dd].sort_values('r_inj')
        A.band(list(g.r_inj), list(g.r_16), list(g.r_84), cols.get(dd, sd.GREY), 0.15)
        A.line(list(g.r_inj), list(g.r_med), cols.get(dd, sd.GREY), 3.5, r=6,
               tips=[f'{dd:g} d, true r {r:g}: measured {m:.2f} (68 %: {a:.2f}–{b:.2f}), σ {sg:.2f}; pull mean {pm:+.2f}, width {ps:.2f}'
                     for r, m, a, b, sg, pm, ps in zip(g.r_inj, g.r_med, g.r_16, g.r_84, g.sigma_med, g.pull_mean, g.pull_sd)])
    B = sd.Plot(560, 520, x=(0, rmax, 'lin'), y=(0, 1.02, 'lin'), xlabel='true X17 strength r = R / R(ATOMKI)',
                ylabel='fraction of experiments', margin=(20, 18, 86, 96), title='how often we see it (Z > 3)')
    B.xticks([(v, f'{v:g}') for v in (0, 0.5, 1.0, 1.5)]).yticks([(v, f'{v * 100:.0f} %') for v in (0, 0.25, 0.5, 0.75, 1.0)])
    for dd in days:
        g = ref[ref.days == dd].sort_values('r_inj')
        B.line(list(g.r_inj), list(g.p_Z3), cols.get(dd, sd.GREY), 3.5, r=6,
               tips=[f'{dd:g} d, r {r:g}: Z > 3 in {p3 * 100:.1f} % of {n:.0f} experiments (Z > 2: {p2 * 100:.0f} %); median Z {zm:.1f}'
                     for r, p3, p2, n, zm in zip(g.r_inj, g.p_Z3, g.p_Z2, g.n, g.Z_med)])
    r7 = ref[ref.days == 7.0].set_index('r_inj')
    h7 = sc[(sc.variant == 'mc halves') & (sc.days == 7.0)].sort_values('r_inj')
    if len(h7):
        A.line(list(h7.r_inj), list(h7.r_med), sd.GREY, 2.5, dash='7 5', markers=False,
               tip='7 days, fit model from one half of the Monte Carlo, truth from the other: a +0.1 offset from template MC noise')
    leg = sd.legend([(f'{dd:g} day' + ('s' if dd > 1 else ''), cols.get(dd, sd.GREY)) for dd in days]
                    + ([('7 d, MC halves', sd.GREY, 'dash')] if len(h7) else []), 19)

    def row(variant, dd, lab):
        g = sc[(sc.variant == variant) & (sc.days == dd)].set_index('r_inj')
        if 0.0 not in g.index or 1.0 not in g.index:
            return None
        z0, r1 = g.loc[0.0], g.loc[1.0]
        bad = z0.p_Z3 > 0.01 or abs(r1.r_med - 1) > 0.05
        c = sd.RED if bad else sd.GREEN
        return [lab, f'{r1.r_med:.2f}&nbsp;±&nbsp;{r1.sigma_med:.2f}', f'{z0.pull_sd:.2f}',
                f'<span style="color:{c};font-weight:600">{z0.p_Z3 * 100:.1f} %</span>', f'{z0.UL_med:.2f}']
    trs = [r for r in (row('reference', 1.0, '1 day'), row('reference', 7.0, '7 days'), row('reference', 30.0, '30 days'),
                       row('widened', 30.0, '30 d, wider fit'), row('widened', 7.0, '7 d, wider fit'),
                       row('mc halves', 7.0, '7 d, MC halves')) if r]
    tab = sd.table(['', 'r̂ at r = 1', 'pull width', 'Z &gt; 3 with<br>no X17', '90 % limit<br>(r = 0)'], trs, size=18,
                   widths=[170, 130, 80, 110, 100])
    z0 = ref[ref.r_inj == 0].set_index('days')
    w30 = sc[(sc.variant == 'widened') & (sc.days == 30.0)].set_index('r_inj')
    fix = (f' Floating those shapes too ("wider fit") brings it to {w30.loc[0.0].p_Z3 * 100:.1f} % at the cost of σ ×'
           f'{w30.loc[1.0].sigma_med / ref[(ref.days == 30.0) & (ref.r_inj == 1.0)].sigma_med.iloc[0]:.1f}.') if len(w30) else ''
    side = [sd.p('Validation: 500–1,000 experiments per row (ideal: pull width 1, Z &gt; 3 in 0.13 %)', 19, sd.MUT), tab,
            sd.callout(f'<b>A week works as advertised:</b> the true coupling comes back without bias, r = 1 to ±{r7.loc[1.0].sigma_med * 100:.0f} % '
                       f'(ε ∝ √R to ±{r7.loc[1.0].sigma_med * 50:.0f} %). Background-only weeks almost never fake 3σ. '
                       f'No X17 → R &lt; {sd.sci(z0.loc[7.0].UL_med * R_ATOMKI)} (MEG II: {sd.sci(R_MEG)}).', sd.GREEN, 18),
            sd.callout('<b>Two warnings.</b> At 30 days the statistics are good enough that the 2 % shape errors the fit does not know '
                       f'about dominate: fake 3σ in {z0.loc[30.0].p_Z3 * 100:.1f} % of months.{fix} And the template Monte Carlo must be '
                       '~10× larger than now: half of it gives a +0.1 offset.', sd.ORANGE, 18)]
    n0 = int(ref[ref.r_inj == 0].n.max())
    D.slide('pitch-pe-scan', sd.title('Measured if it is there, excluded if not',
                                      f'The whole analysis on {n0:,} pseudo-experiments per point, each with a new imperfectly known background, at '
                                      'each true X17 strength; 1, 7, 30 days at 1 µA, big plastics. Hover the points.')
            + sd.row(sd.col(A.svg('r measured vs true'), leg, gap=4), B.svg('discovery probability'), sd.col(*side, gap=10, w=620), gap=16),
            f"""<p><code>lnl/out/pseudo/scan.csv</code> (<code>toys.csv</code>: every pseudo-experiment). Each one draws a new truth (all
background parameters, the modelled and the unmodelled structure, as in step 1) and new Poisson data, then runs the full fit. Z = r̂/σ
and the 90 % CL upper limit (one-sided, Δχ² = 2.71 from max(r̂, 0)) use the quadratic approximation of the profile likelihood.
Coverage of the 90 % upper limit for r &gt; 0 at 7 days: {r7[r7.index > 0].cover90.min() * 100:.0f}–{r7[r7.index > 0].cover90.max() * 100:.0f} %;
at 30 days {ref[(ref.days == 30.0) & (ref.r_inj > 0)].cover90.min() * 100:.0f}–{ref[(ref.days == 30.0) & (ref.r_inj > 0)].cover90.max() * 100:.0f} % (the pull width
again). "Wider fit": the fit also floats the S_θE and S_m structure that the truth contains (the real-life equivalent: let the
background model carry every class of shape error the controls cannot rule out). r = R/R(ATOMKI), R(ATOMKI) =
5.8×10⁻⁶; the X17 coupling ε goes as √R, so ε/ε(ATOMKI) = √r.</p>
<p>What is not in here: a background error shaped like the X17 in all three variables (the impostor slides), the MC statistics of a
larger-than-simulated γ₁ sample (the "mc halves" row uses half the MC for each side), and any look-elsewhere effect from scanning
the X17 mass.</p>""",
            foot='lnl/out/pseudo/scan.csv (lnl/sim/lnl_pseudo.py)', short='Sim. 5: coupling')
