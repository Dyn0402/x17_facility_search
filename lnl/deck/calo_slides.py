"""Deck slides (2026-10-12, §14): the single-arm trigger with a prescale, the
calorimetry critique against the n_TOF response, and the fits in two and three
kinematic variables.

Reads lnl/out/trigger/ (lnl_trigger.py), lnl/out/calo/ (lnl_calo.py) and
lnl/out/nd/ (lnl_nd.py).  Called from build_deck.py after the systematics slides.
"""
import numpy as np
import pandas as pd

import slidedoc as sd

AB, BP = 'as built', 'big plastics'
RCOL = {'ideal': sd.GREY, 'n_TOF as is': sd.RED, 'LNL calibrated': sd.BLUE,
        'LNL calibrated, LS off': sd.GREEN, 'big plates, poor': sd.PURPLE}


def fd(d):
    if not np.isfinite(d) or d > 9999:
        return '> 10⁴'
    return f'{d:,.0f}' if d >= 10 else f'{d:.1f}'


def numbers(O):
    """realistic-response headline: m_ee robust days with the LNL-calibrated response."""
    dy = pd.read_csv(O / 'calo' / 'days.csv')

    def g(hw, resp, fit='m_ee fit'):
        return dy[(dy.hw == hw) & (dy.resp == resp) & (dy.fit == fit)].days_robust.iloc[0]
    out = {}
    t = nd_load(O)
    if t is not None:
        def n(hw, a, st='S_θ 2 % + S_θy 1 %', resp='LNL calibrated'):
            return t[(t.hw == hw) & (t.resp == resp) & (t.analysis == a) & (t.structure == st)].days.iloc[0]

        def worst(hw, a, resp='LNL calibrated'):
            return t[(t.hw == hw) & (t.resp == resp) & (t.analysis == a)].days.max()
        A3 = 'θ × |y| × E_sum'
        out = dict(bp_nd=n(BP, A3), ab_nd=n(AB, A3), bp_nd_worst=worst(BP, A3), ab_nd_worst=worst(AB, A3),
                   bp_m1d=n(BP, 'm_ee'), ab_m1d=n(AB, 'm_ee'), bp_m1d_worst=worst(BP, 'm_ee'), ab_m1d_worst=worst(AB, 'm_ee'),
                   bp_my=n(BP, 'm_ee × |y|'), ab_my=n(AB, 'm_ee × |y|'),
                   bp_nd_ideal=n(BP, A3, resp='ideal'), ab_nd_ideal=n(AB, A3, resp='ideal'))
    return dict(**out, ab_cal=g(AB, 'LNL calibrated'), bp_cal=g(BP, 'LNL calibrated'),
                ab_ntof=g(AB, 'n_TOF as is'), bp_ntof=g(BP, 'n_TOF as is'),
                ab_ideal=g(AB, 'ideal'), bp_ideal=g(BP, 'ideal'),
                ab_lsoff=g(AB, 'LNL calibrated, LS off'), bp_poor=g(BP, 'big plates, poor'))


def calo_slides(D, O):
    trigger_slide(D, O)
    calo_slide(D, O)
    if (O / 'nd').exists():
        nd_slide(D, O)


# --------------------------------------------------------------------------- #
def trigger_slide(D, O):
    t = pd.read_csv(O / 'trigger' / 'prescale.csv')
    ch = pd.read_csv(O / 'trigger' / 'prescale_choice.csv')
    a16 = 'ATOMKI 2016 anomaly'
    Q = sd.Plot(900, 600, x=(1, 100, 'log'), y=(84, 100.5, 'lin'), xlabel='single-arm prescale P (pairs never prescaled)',
                ylabel='DREAM live fraction [%]')
    Q.xticks([(v, f'{v}') for v in (1, 2, 5, 10, 20, 50, 100)]).yticks([(v, f'{v}') for v in (85, 90, 95, 100)])
    Q.hline(95, sd.GOLD, label='95 %')
    for hw, col in ((BP, sd.GREEN), (AB, sd.BLUE)):
        for I, dash in ((1.0, None), (4.0, '10 7'), (8.0, '3 5')):
            g = t[(t.hw == hw) & (t.scenario == a16) & (t.I_uA == I)]
            Q.line(list(g.prescale), list(100 * g.live), col, 3, dash=dash, r=5,
                   tips=[f'{hw}, {I:g} µA, P = {p}: {f:.0f} triggers/s ({pr:.1f} pairs/s), live {100 * l:.1f} %, '
                         f'{tb:.2f} TB/day per FEU' for p, f, pr, l, tb in zip(g.prescale, g.trig_per_s, g.pair_per_s, g.live,
                                                                               g.TB_per_day_per_FEU)])
    rows = []
    for hw in (AB, BP):
        for I in (1.0, 4.0):
            r = ch[(ch.hw == hw) & (ch.scenario == a16) & (ch.I_uA == I)].iloc[0]
            rows.append([f'{hw}, {I:g} µA', f'{r.leg_per_s:.0f}/s', f'{r.pair_per_s:.1f}/s', f'{100 * r.live_P1:.1f} %',
                         f'{int(r.P_for_95)}', f'{int(r.P_for_98)}'])
    tab = sd.table(['', 'arm legs', 'pairs', 'live, P = 1', 'P for 95 %', 'P for 98 %'], rows, size=18,
                   widths=[200, 110, 90, 120, 100, 100])
    r10 = ch[(ch.hw == AB) & (ch.scenario == a16) & (ch.I_uA == 1.0)].iloc[0]
    side = sd.col(
        sd.legend([('big plastics', sd.GREEN, 'line'), ('as built', sd.BLUE, 'line'),
                   ('solid 1 µA · dashed 4 µA · dotted 8 µA', sd.MUT, 'line')], 19),
        tab,
        sd.callout('<b>The logic:</b> each arm\'s leg (SiPM bar AND plastic ≥ 0.5 MIP) is a trigger. Two outputs into DREAM: '
                   '<b>PAIR</b> (≥ 2 legs in 20 ns) never prescaled, and <b>SINGLE</b> (≥ 1 leg) prescaled 1/P, plus a 1 Hz clock. '
                   'The trigger word (legs, output, prescale counter) goes with each event.', sd.BLUE, 18),
        sd.callout(f'<b>What singles buy:</b> cosmic MIPs per arm for the gain ({r10.cosmic_mip_per_arm_per_h_P10:,.0f}/h even at P = 10: '
                   f'~{100 * r10.gain_prec_1h_P10:.0f} % per hour, so σ_g ≈ 1–2 % is easy); the event-mixing acceptance (§13.3); '
                   'per-arm efficiency maps; and the 8Be γ single-arm spectra as a high-energy check of the scale.', sd.GREEN, 18),
        sd.callout('<b>P = 1 up to ~2–4 µA.</b> Above that, P = 2–10 keeps 95 %. Pairs, the physics, lose only the live time. '
                   'Not included: ¹⁹F(p,αγ) on a LiF target (ask).', sd.GREY, 18),
        gap=10, w=740)
    D.slide('trigger', sd.title('Take every single-arm trigger, with the prescale ready: it costs a few % of live time',
                                'DREAM RAW (τ = 298 µs, 20 samples), Geant4 8Be γ singles + cosmics, Li₂O at 1.04 MeV. Hover the points.')
            + sd.row(Q.svg('live time vs prescale'), side, gap=24),
            """<p>Rates from <code>lnl_geant.singles</code>: per-arm legs per γ of each 8Be line (L3) and per second of cosmics (L4).
Pair rate = correlated two-arm legs + 20 ns accidentals. Single-only events ≈ legs − 2 × pairs. Live = 1/(1 + fτ),
non-paralysable, the same for both outputs, so the prescale protects the pairs only through the live time.
Data: 83 MB/s per FEU at 3.35 kHz, ~25 kB per event per FEU.</p>
<p>The gain precision per hour uses σ(MPV)/MPV ≈ 0.35/√N for a Landau ⊗ Gauss with σ/MPV ≈ 0.2 (the n_TOF 2 cm bars) and the
weakest arm's cosmic rate. Per bar it is ×√(bars per arm) worse, still ≲ 1 % per day.</p>
<p>Offline, the single-arm sample is exactly normalised for any P. A design rule follows: never let a prescale touch the PAIR
output, and keep P a run-condition parameter, not a firmware constant.</p>""",
            foot='lnl/out/trigger/prescale.csv, prescale_choice.csv (lnl/sim/lnl_trigger.py)', short='Trigger')


# --------------------------------------------------------------------------- #
def calo_slide(D, O):
    sp = pd.read_csv(O / 'calo' / 'spectra.csv')
    dy = pd.read_csv(O / 'calo' / 'days.csv')
    rs = pd.read_csv(O / 'calo' / 'resolution.csv')
    ls = pd.read_csv(O / 'calo' / 'ls_scan.csv') if (O / 'calo' / 'ls_scan.csv').exists() else None
    N = numbers(O)

    def mplot(hw, ttl, ylab):
        Q = sd.Plot(470, 470, x=(13, 18.5, 'lin'), y=(0, 0.32, 'lin'), xlabel='m_ee [MeV]', ylabel=ylab,
                    margin=(56, 20, 92, 104), title=ttl)
        Q.xticks([(v, f'{v}') for v in range(13, 19)]).yticks([(v, f'{v:.1f}') for v in (0, 0.1, 0.2, 0.3)])
        resps = [r for r in RCOL if ((sp.hw == hw) & (sp.resp == r)).any()]
        for r in resps:
            for smp, dash in (('X17', None), ('γ0 IPC (M1)', '8 6')):
                g = sp[(sp.hw == hw) & (sp.resp == r) & (sp['sample'] == smp) & (sp['var'] == 'm_ee')]
                g = g[(g.x > 13) & (g.x < 18.5)]
                Q.line(list(g.x), list(g.frac), RCOL[r], 3 if dash is None else 2, dash=dash, markers=False,
                       tips=[f'{hw}, {r}, {smp}' for _ in g.x])
        return Q.svg(ttl)

    rows = []
    for hw in (BP, AB):
        for r in RCOL:
            q = rs[(rs.hw == hw) & (rs.resp == r)]
            if q.empty:
                continue
            q = q.iloc[0]
            d = dy[(dy.hw == hw) & (dy.resp == r) & (dy.fit == 'm_ee fit')].iloc[0]
            col = sd.GREEN if d.days_robust <= 7 else (sd.INK if d.days_robust <= 30 else sd.RED)
            rows.append([f'<span style="color:{RCOL[r]}">■</span> {hw}, {r}', q.ecut,
                         f'{q.x17_mass_w68:.2f}', f'{q.corr_y_ytrue:.2f}', f'{abs(q.g1_g0_sep) if abs(q.g1_g0_sep) < 0.05 else q.g1_g0_sep:.1f}',
                         f'<b style="color:{col}">{fd(d.days_robust)} d</b>'])
    tab = sd.table(['m_ee fit, robust', 'E_sum win.', 'σ₆₈(m) MeV', 'corr(y, y_true)', 'γ₁/γ₀ sep. σ', 'days 3σ'], rows,
                   size=16, widths=[330, 90, 100, 110, 100, 90])
    ab_note = ''
    if ls is not None:
        li = ls.set_index('resp')
        ab_note = (f' Split: plastic + SiPM real, LS ideal → {fd(li.loc["LNL cal., LS ideal"].days_robust)} d; LS real only → '
                   f'{fd(li.loc["LNL cal., all ideal but LS"].days_robust)} d; an LS at a = 0.2 → '
                   f'{fd(li.loc["LNL cal., LS a=0.2 c=5%"].days_robust)} d.')
    side = sd.col(
        tab,
        sd.callout(f'<b>Big plastics survive:</b> {fd(N["bp_ideal"])} d ideal → <b>{fd(N["bp_cal"])} d</b> calibrated, '
                   f'{fd(N["bp_ntof"])} d with n_TOF-quality calibration, {fd(N["bp_poor"])} d with poor plates. The m_ee peak barely widens: '
                   '5 cm stops the soft lepton and catches most of the hard one.', sd.GREEN, 17),
        sd.callout(f'<b>As built does not:</b> {fd(N["ab_ideal"])} d → {fd(N["ab_cal"])} d even with a repaired liquid, '
                   f'{fd(N["ab_ntof"])} d as at n_TOF, {fd(N["ab_lsoff"])} d without it. 2 cm of plastic stops neither lepton, so y and '
                   f'E_sum rest on a 18 mm liquid cell and ~10 photoelectrons/MeV.{ab_note}', sd.RED, 17),
        sd.callout('<b>Gains are not the problem:</b> a per-arm gain nuisance costs ≤ 15 % even at σ_g = 10 % (big plastics); '
                   'single-arm cosmics give 1–2 % anyway.', sd.BLUE, 17),
        gap=10, w=900)
    D.slide('calorimetry', sd.title(f'With a real response the m_ee fit holds for big plastics (~{N["bp_cal"]:.1f} d), not as built (~{N["ab_cal"]:.0f} d)',
                                    'Geant4 deposits per arm and layer with the n_TOF-anchored response; X17 (solid) and γ₀ IPC (dashed) in m_ee, θ 125–165°. '
                                    'Robust = 2 % structure + in-run controls, per-arm gain nuisance; E_sum window re-optimised per response.')
            + sd.row(mplot(BP, 'big plastics', 'fraction per 0.25 MeV'), mplot(AB, 'as built', None), side, gap=8),
            """<p><b>The response</b> (<code>lnl/sim/lnl_calo.py</code>), per arm and layer: E(1 + c·N) + a√E·N′, zero below threshold.
From n_TOF (<code>nTof_x17/ntof_calorimetry</code>, C1 and C4):</p>
<ul><li><b>2 cm plastic bars:</b> the cosmic MIP (3.41 MeV) has a Gauss σ/MPV of 0.13–0.24 per bar. The scint-stack per-cell maps
spread 4–5 % (arm B 9.5 %). Model: a = 0.32 √MeV, c = 5 % (2 % with an MM-position map). The n_TOF scale is known to ~10 %
(MIP vs source line 3–24 % apart).</li>
<li><b>SiPM wall:</b> a = 0.19 √MeV (25 % at the 0.6 MeV MIP), c = 8 % / 4 %.</li>
<li><b>Liquid:</b> MIP σ/MPV 0.46, 6–9 mV/MeV against a 16–18 mV zero suppression (1.8–2.8 MeV threshold), MIP efficiency 14–56 %
and position-dependent. n_TOF model: threshold 2.3 MeV, a = 0.78, log-normal light collection σ = 0.5. Repaired: threshold 0.5,
a = 0.5, c = 15 %.</li>
<li><b>5 cm big plates:</b> no data. a = 0.20–0.35 √MeV, c = 5–15 %.</li></ul>
<p>The per-arm gain error goes into the fit as four nuisances (σ_g: 10 % n_TOF as is, 2 % calibrated with single-arm cosmics,
5 % poor plates). The E_sum window is re-chosen for each response: e.g. 14–19 MeV with big plastics.</p>
<p>Not modelled: Birks quenching of stopping electrons (a few %); the SiPM-wall leg efficiency (75–91 % unbiased at n_TOF,
×1.2–1.8 in days if it stays); a non-linear plastic above 5 MeV (n_TOF checked linearity only to 1.45 MIP).</p>""",
            foot='lnl/out/calo/days.csv, resolution.csv, spectra.csv, ls_scan.csv (lnl/sim/lnl_calo.py)', short='Calorimetry')


# --------------------------------------------------------------------------- #
ND_COLS = ['none', 'S_θ 2 %', 'S_m 2 %', 'S_θ 2 % + S_θy 1 %', 'S_θ 5 %, ℓ/2', 'S_m 5 %, ℓ/2', 'S_θy 5 %, ℓ/2']
ND_ROWS = ['θ', 'θ, |y|<0.3', 'm_ee', 'θ × |y|', 'm_ee × |y|', 'm_ee × E_sum', 'θ × |y| × E_sum']


def nd_load(O):
    fs = sorted((O / 'nd').glob('nd_days_*.csv'))
    return pd.concat([pd.read_csv(f) for f in fs]) if fs else None


def nd_slide(D, O):
    t = nd_load(O)
    if t is None:
        return
    resp = 'LNL calibrated' if (t.resp == 'LNL calibrated').any() else 'ideal'

    def tab_for(hw):
        g = t[(t.hw == hw) & (t.resp == resp)]
        rows, tips = [], []
        for a in ND_ROWS:
            cells = [a.replace('<', '&lt;')]
            ga = g[g.analysis == a]
            worst = ga[ga.structure.isin(ND_COLS)].days.max()
            for s in ND_COLS:
                r = ga[ga.structure == s]
                if r.empty:
                    cells.append('–')
                    continue
                v = r.days.iloc[0]
                col = sd.GREEN if v <= (7 if hw == AB else 1.5) else (sd.INK if v <= (30 if hw == AB else 3) else sd.RED)
                h = ''
                if 'half_a' in r and np.isfinite(r.half_a.iloc[0]):
                    h = f' (MC halves {fd(r.half_a.iloc[0])} / {fd(r.half_b.iloc[0])} d)'
                cells.append(f'<span style="color:{col};font-weight:{700 if v == worst else 500}">{fd(v)}</span>')
                tips.append(f'{hw}, {a}, {s}: {v:.2f} d{h}')
            rows.append(cells)
        return sd.table(['fit in', 'no struct.', 'S_θ 2 %', 'S_m 2 %', 'S_θ 2 %<br>+ S_θy 1 %', 'S_θ 5 %<br>ℓ/2',
                         'S_m 5 %<br>ℓ/2', 'S_θy 5 %<br>ℓ/2'], rows, size=16, tips=None,
                        widths=[170, 82, 82, 82, 92, 82, 82, 82])
    N = numbers(O)
    side = sd.col(
        sd.callout(f'<b>More discovery power once the energies are real.</b> With the calibrated response the m_ee peak is smeared by '
                   f'the y resolution, but θ, |y| and E_sum each still separate. m_ee alone {fd(N["bp_m1d"])} d → m_ee × |y| {fd(N["bp_my"])} d → '
                   f'θ × |y| × E_sum <b>{fd(N["bp_nd"])} d</b> with big plastics; as built {fd(N["ab_m1d"])} → {fd(N["ab_my"])} → <b>{fd(N["ab_nd"])} d</b>.', sd.GREEN, 18),
        sd.callout(f'<b>And robust where 1D is not.</b> The worst structure tried (5 %, edge-like, in m_ee) takes m_ee alone to '
                   f'{fd(N["bp_m1d_worst"])} d (big plastics) and {fd(N["ab_m1d_worst"])} d (as built); the 3D fit stays at '
                   f'{fd(N["bp_nd_worst"])} and {fd(N["ab_nd_worst"])} d. The X17 is a curve in (θ, |y|) at fixed E_sum; acceptance '
                   'structure is a band in θ, a γ₁ leak a band in E_sum, a shape error in m_ee a diagonal: the fit tells them apart.', sd.BLUE, 18),
        sd.callout('<b>The angle-only fits are fragile:</b> with a free acceptance cubic their days swing ×2–3 between the two halves of '
                   'the Monte Carlo. The 2D and 3D fits agree between halves to ≲ 10 %.', sd.RED, 18),
        sd.callout('<b>Nothing new to record:</b> θ, E₁, E₂ are in every pair event. The E_sum axis replaces the γ₁ side-band cut by a fit; '
                   'the |y| axis replaces the |y| cut and keeps the asymmetric pairs as the control inside the same fit.', sd.GREY, 18),
        gap=10, w=700)
    D.slide('two-d', sd.title('A fit in angle × energy split × energy sum is faster and shrugs off background-shape errors',
                              f'Days to 3σ at R(ATOMKI), 1 µA, {resp} response. Columns: the same unknown structure (Gaussian process) on the '
                              'events, in θ, m_ee or (θ, |y|); "ℓ/2" = 5 % and edge-like. Bold: the worst column per row.')
            + sd.row(sd.col(sd.p('big plastics', 20, weight=600), tab_for(BP), sd.p('as built', 20, weight=600), tab_for(AB), gap=6),
                     side, gap=24),
            """<p><code>lnl/sim/lnl_nd.py</code>. The unknown structure is a weight 1 + Σcⱼφⱼ on every background event, with φⱼ the
Gaussian-process modes in physical variables: S_θ in the reconstructed angle (acceptance, geometry: the same at every |y| and
E_sum), S_m in m_ee (the §13 assumption), S_θy local in the (θ, |y|) plane (a background-physics shape error), all ℓ = 10° (0.55 MeV,
0.15 in |y|). Each analysis sees the same structure through its own binning, so the columns compare like with like.</p>
<p>Every fit floats M1, E1, γ₁ norms, the anisotropy, resolution and E scale, a free acceptance cubic in θ, a |y| tilt (±5 %), the four
arm gains and the |y| resolution. The θ-only fit is near-degenerate with the free cubic: its days swing ×2–3 between MC halves.
The 2D and 3D fits agree between halves to ≲ 10 %. Templates are KDE-smoothed (5° or 0.27 MeV) along their first axis; |y| (6 bins)
and E_sum (4 bins: two in the γ₁ side band, two in the window) are plain bins.</p>
<p>The 1D m_ee here (no in-run controls, acceptance cubic in θ rather than in m_ee) is a little slower than the Calorimetry slide's
m_ee fit (γ₁ side band as a control). The 3D fit contains that control as its E_sum axis.</p>""",
            foot='lnl/out/nd/nd_days_*.csv (lnl/sim/lnl_nd.py)', short='2D fit')
