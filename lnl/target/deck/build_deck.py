"""Build the lithium-target slide note (lnl/target/TARGET_STUDY.md).

Reads lnl/out/target/ (target_model.py, target_rates.py, target_fit_bias.py), writes
lnl/out/target/lnl-lithium-target.html:

    ~/PycharmProjects/nTof_x17/.venv/bin/python lnl/target/deck/build_deck.py
    python3 ~/PycharmProjects/dylan-cern-site/scripts/add-note.py \\
        lnl/out/target/lnl-lithium-target.html --slug lnl-lithium-target --force --deploy
"""
import math
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.expanduser(os.environ.get(
    'SLIDEDOC_DIR', '~/PycharmProjects/dylan-cern-site/scripts')))
import slidedoc as sd  # noqa: E402
from slidedoc import sci  # noqa: E402

HERE = Path(__file__).resolve().parent
O = HERE.parents[1] / 'out' / 'target'
XS = pd.read_csv(O / 'cross_sections.csv')
SC = pd.read_csv(O / 'scenarios.csv').set_index('scenario')
TH = pd.read_csv(O / 'thermal.csv')
LIM = pd.read_csv(O / 'limits.csv')
CB = pd.read_csv(O / 'carbon.csv')
RM = pd.read_csv(O / 'rates_mx17.csv')
RL = pd.read_csv(O / 'rates_lnl_like.csv').set_index('scenario')
FB = pd.read_csv(O / 'fit_bias.csv')

LI, F, B, C, HEAT, OK = sd.BLUE, sd.RED, sd.GOLD, sd.GREY, sd.ORANGE, sd.GREEN

LNL_THIN, LNL_THICK = 'LNL 2023-24, LiF 34 at 1.03', 'LNL 2023-24, LiF 935, 1.03 at centre'
LNL_441 = 'LNL 2023-24, LiF 34 at 441'
f_thin = SC.loc[LNL_THIN, 'F_pairs_per_8Be_pair']
f_thick = SC.loc[LNL_THICK, 'F_pairs_per_8Be_pair']
f_441 = SC.loc[LNL_441, 'F_pairs_per_8Be_pair']


def T_of(holder, ep, I):
    q = TH[(TH.holder == holder) & (TH.Ep_keV == ep) & (TH.I_uA == I)]
    return float(q.T_max_C.iloc[0])


def lim_T(col, v):
    i = int(np.argmax(LIM[col].values >= v))
    return float(LIM.T_C.values[i])


T_DIFF = lim_T('diff_len_1d_um', 10)
T_LIEV = lim_T('Li_evap_ug_cm2_h', 5.3)
T_LIFEV = lim_T('LiF_evap_ug_cm2_h', 300 / 168)
H16 = 'ATOMKI 2016: 10 µm Al strip, Plexiglas rods'
H22 = 'ATOMKI 2022: 10 µm Al strip, Al rods'
HD = '10 µm Al disk, clamped at r = 10 mm'
HG = '25 µm graphite foil disk, r = 10 mm'
HC = '25 µm Cu disk, clamped at r = 10 mm (MEG II-like)'
HN = '1 µm Ni disk, clamped at r = 10 mm (Hanoi Li2O)'
t16 = T_of(H16, 800, 1.0)
t16b = T_of(H16, 1050, 1.0)


def fb(scen, an, days=30, struct=None, col='fake_r'):
    q = FB[(FB.scenario == scen) & (FB.analysis == an) & (FB.days == days)]
    q = q[q.structure != 'none'] if struct is None else q[q.structure == struct]
    return float(q[col].iloc[0]) if len(q) else float('nan')


r3_20 = fb('441 keV share of γ₀ = 20%', 'θ × |y| × E_sum')
rt_20 = fb('441 keV share of γ₀ = 20%', 'θ')
chi3_20 = fb('441 keV share of γ₀ = 20%', 'θ × |y| × E_sum', col='chi2_resid')
HAVE_BORON = FB.scenario.str.startswith('boron').any()
HAVE_BIGP = (RM.hw == 'big plastics').any()

D = sd.Deck('The lithium target: what stopped LNL, and what could stop us',
            'Why the LNL 2023–24 ⁸Be run may not have produced a result, and a study of a thin lithium target for MX17 '
            'at LNL: fluorine, heat, diffusion, contamination, carbon build-up, hydrogen, and what each does to the fit.')

# --------------------------------------------------------------------------- #
cover = (sd.kicker('MX17 at LNL · the lithium target · 22 Oct 2026')
         + '<h1 style="font-size:58px;font-weight:600;line-height:1.1;letter-spacing:-1.5px">'
           f'LNL ran LiF at the 18.15 MeV resonance, where fluorine makes {f_thin / 1e3:.1f}–{f_thick / 1e3:.1f} thousand e⁺e⁻ pairs '
           'for every ⁸Be pair. For MX17 the target is a solved problem: no fluorine, keep it cool, and the 3D fit '
           'shrugs off a drifting target.</h1>'
         + sd.p('Measured ¹⁹F and ⁷Li cross sections, a heat model of the target foils checked against ATOMKI and Hanoi, '
                'and the MX17 Geant4 tables and 3D fit for every failure mode.', 28, sd.DMUT)
         + sd.row(
             sd.bignum(f'×{f_thick / 1e3:.1f}×10³', '¹⁹F E0 pairs per ⁸Be pair', sd.DRED,
                       f'LNL LiF 935 µg/cm² at 1.03 MeV ({f_thin:,.0f} for 34 µg/cm²); {f_441:.1f} at 441 keV',
                       tip='¹⁹F(p,α_π)¹⁶O* (6.05 MeV 0⁺ → e⁺e⁻), Redigolo 2024; ⁸Be IPC = 3.5×10⁻³ × (γ₀+γ₁), Zahnow 1995'),
             sd.bignum(f'{t16b:.0f}–{t16:.0f} °C', 'a 10 µm Al strip target at 1 µA', '#f0a35e',
                       f'ATOMKI-style strip; Li crosses 10 µm Al in a day above {T_DIFF:.0f} °C'),
             sd.bignum(f'{r3_20:+.2f}', 'fake X17 (× ATOMKI) from a 20 % 441-keV share', sd.DGREEN,
                       f'MX17 3D fit, 30 d; a θ-only fit gives {rt_20:+.2f}'),
             gap=56))
D.slide('cover', cover, '''
<p>Pierfrancesco's question: the LNL ⁸Be pair spectrometer took ~790 h of beam on AN2000 in 2023–24 and has
published nothing. Was it the lithium target, and would it hit us? This note answers both from public sources and
our own simulation. It cannot know what LNL actually saw: the inference about their run needs confirming with them.</p>
<p>Hover dotted terms and data points for definitions and values. Write-up: <code>lnl/target/TARGET_STUDY.md</code>.</p>''',
        dark=True, short='cover')

# --------------------------------------------------------------------------- #
# 2. what a target is and how each group's went wrong
W, H = 1664, 560


def target_diagram():
    s = []
    y0 = 250
    s.append(sd.arrow(20, y0, 330, y0, sd.INK, 5, 18))
    s.append(sd.T(170, y0 - 22, 'proton, 0.44–1.1 MeV', 24, sd.INK))
    # carbon
    s.append(f'<rect x="360" y="110" width="14" height="280" fill="{C}"{sd.tipattr("cracked hydrocarbons; 10 µg/cm² shifts 441 keV by 3.8 keV")}/>')
    s.append(sd.T(367, 92, 'carbon', 22, C))
    # film
    s.append(f'<rect x="378" y="110" width="40" height="280" fill="{LI}" opacity=".85"{sd.tipattr("Li₂O / LiF / Li / LiPON, 30–1000 µg/cm²")}/>')
    s.append(sd.T(330, 420, 'Li film', 24, LI, weight=600))
    # backing
    s.append(f'<rect x="418" y="70" width="34" height="360" fill="#b9c1cc"{sd.tipattr("10 µm Al (ATOMKI, Hanoi), 25 µm Cu (MEG II), 1 µm Ni, ?? (LNL)")}/>')
    s.append(sd.T(435, 455, 'backing', 24, sd.MUT))
    s.append(sd.arrow(470, y0, 690, y0, sd.MUT, 3, 14))
    s.append(sd.T(580, y0 - 20, 'to the dump', 22, sd.MUT))
    # failure annotations
    items = [
        (80, F, 'Fluorine (LiF)', f'¹⁹F(p,α)¹⁶O: 6–7 MeV γ and 6.05 MeV E0 pairs, ×{f_thin:.0f}–{f_thick:.0f} per ⁸Be pair at 1.03 MeV'),
        (165, HEAT, 'Heat', f'a strip at 1 µA: {t16b:.0f}–{t16:.0f} °C → Li melts, diffuses, LiF evaporates, foil punctures'),
        (250, LI, 'Diffusion', 'Li into the backing: the beam reaches 441 keV inside it, adding a 17.64 MeV M1 line'),
        (335, C, 'Air / carbon / boron', 'Li₂O → LiOH (×1.6 mass); carbon build-up; ¹¹B(p,γ) 16.9 MeV line'),
        (420, sd.PURPLE, 'Hydrogen', 'protons stopping in a metal backing: 10¹⁸–10¹⁹ /cm² per week → blistering'),
    ]
    for y, col, h, t in items:
        y = y - 30
        s.append(f'<circle cx="760" cy="{y}" r="11" fill="{col}"/>')
        s.append(sd.T(786, y + 9, h, 26, sd.INK, anchor='start', weight=600))
        s.append(sd.T(786, y + 40, t, 21, sd.MUT, anchor='start'))
    return sd.svg(W, 440, ''.join(s), 'target schematic with failure modes')


hist = sd.table(['group', 'target at the 18 MeV energies', 'what went wrong (their words or ours)'], [
    ['ATOMKI 2016', 'Li metal → “Li₂O”, 10 µm Al strip, Plexiglas rods', 'Li diffused into the Al: target “10 µm” thick, beam reached 441 keV'],
    ['Hanoi 2024', 'LiF 30 / Al 10 µm (≤ 0.8 MeV); Li₂O on 1 µm Ni', '“burned out (punctured) many times”; F E0 pairs “would overload” at 1.04'],
    ['MEG II 2023', 'LiPON 7 µm on 25 µm Cu', '25 % H₂⁺ beam put most data on 441 keV'],
    ['LNL 2023–24', '<b>LiF 34–935 µg/cm² at 1.03 MeV</b>', 'no result published; backing unknown'],
], size=22, align=['left', 'left', 'left'], widths=[220, 620, 820])
D.slide('setup', sd.title('A lithium target is a micron of film on a foil, and every group that ran one at 18 MeV hit a problem',
                          'Beam left to right. Hover the layers; the table is each group’s target and what they reported.')
        + target_diagram() + hist, '''
<p>The physics wants ⁷Li atoms at one proton energy (1.03–1.10 MeV for the 18.15 MeV state), so the film must be thin
(≲ 300 µg/cm², ≲ 60 keV of energy loss) and stay where it was put. Everything else in the stack is a source of other
γ-rays and pairs, of heat, and of scattering for the leptons.</p>
<p>Sources: Sas 2022 (arXiv:2205.07744) §V for ATOMKI 2016; Tran The Anh 2024 (arXiv:2401.11676) for Hanoi; MEG II EPJC 85,
763; Góngora-Servín 2025 (APPB Supp 18 2-A13) for LNL. The Hanoi spectrometer was built with ATOMKI.</p>''',
        short='targets')

# --------------------------------------------------------------------------- #
# 3. cross sections
P = sd.Plot(1080, 600, x=(300, 1300), y=(1e-6, 30, 'log'), xlabel='proton energy E_p (keV)',
            ylabel='cross section (mb)')
P.xticks([(e, str(e)) for e in (400, 600, 800, 1000, 1200)]).yticks(sd.log_ticks(-6, 1))
x = XS[(XS.Ep_keV >= 300) & (XS.Ep_keV <= 1300)].iloc[::4]
li_pairs = (x.Li7_g01_ub * 1e-3 * 3.5e-3).clip(lower=1.1e-6)
P.line(x.Ep_keV, (x.Li7_g01_ub * 1e-3).clip(lower=1.1e-6), LI, markers=False, w=3, dash='8 6',
       tip='⁷Li(p,γ₀+γ₁)⁸Be, Zahnow 1995 (EXFOR A0639)')
P.line(x.Ep_keV, li_pairs, LI, markers=False, w=4.5, tip='⁸Be IPC pairs = 3.5×10⁻³ × σ(γ₀+γ₁)')
P.line(x.Ep_keV, x.F19_gamma_mb.clip(lower=1.1e-6), F, markers=False, w=3, dash='8 6',
       tip='¹⁹F(p,αγ): 6.13 + 6.92 + 7.12 MeV γ (TUNL 2021PH03 × 4π × 1.6; 1991HE16 below 0.9 MeV)')
P.line(x.Ep_keV, x.F19_alpha_pi_mb.clip(lower=1.1e-6), F, markers=False, w=4.5,
       tip='¹⁹F(p,α_π)¹⁶O*(6.05, 0⁺) → e⁺e⁻ only: Redigolo 2024 Figs 6, 8; below E_cm 1.0 MeV extrapolated at constant S')
P.line(x.Ep_keV, (x.B11_g0_ub_est * 1e-3 * 0.01).clip(lower=1.1e-6), B, markers=False, w=3, dash='3 5',
       tip='¹¹B(p,γ₀) 16.9 MeV × B/Li = 1 % (ESTIMATE: Breit-Wigner of the 17.23 MeV 1⁻ level)')
P.vline(441, sd.MUT, label='441', tip='17.64 MeV 1⁺ resonance (Γ 12 keV)')
P.vline(1030, sd.MUT, label='1030', tip='18.15 MeV 1⁺ resonance (Γ 168 keV)')
i = int((XS.Ep_keV - 1030).abs().argmin())
ratio = XS.F19_alpha_pi_mb[i] / (XS.Li7_g01_ub[i] * 1e-3 * 3.5e-3)
P.text(470, 2.2e-6, f'at 1.03 MeV: ¹⁹F pairs / ⁸Be pairs ≈ {ratio:,.0f} per nucleus', 24, F, weight=600)
leg = sd.legend([('⁸Be: γ₀+γ₁', LI, 'dash'), ('⁸Be: IPC pairs', LI), ('¹⁹F: 6–7 MeV γ', F, 'dash'),
                 ('¹⁹F: 6.05 MeV E0 pairs', F), ('¹¹B γ₀ at B/Li = 1 %', B, 'dash')], 22)
side = sd.col(
    sd.callout('At 441 keV the ⁷Li resonance wins: LiF is a fine calibration target.', LI, 24),
    sd.callout(f'Above 0.8 MeV the order flips. At 1.03 MeV each F nucleus makes ×{ratio:,.0f} more pairs than each Li nucleus.', F, 24),
    sd.callout('ATOMKI/Hanoi: the E0 pairs “would overload our electronics” there. LNL ran LiF at 1.03 MeV.', sd.INK, 24),
    w=520, gap=24)
D.slide('xs', sd.title('Above 0.8 MeV fluorine out-produces lithium: every F nucleus makes ~10³× more pairs',
                       'Per-nucleus cross sections against proton energy. Dashed: γ-rays; solid: e⁺e⁻ pairs.')
        + sd.row(sd.col(P.svg('cross sections'), leg, gap=8, w=1080), side, gap=56),
        f'''<p>The 6.05 MeV first excited state of ¹⁶O is 0⁺, like the ground state, so it can only decay by internal pair creation
(E0): every ¹⁹F(p,α_π) reaction makes a pair, with 5.0 MeV of kinetic energy shared between the leptons. The 6.13/6.92/7.12 MeV
lines are real γ-rays that convert, Compton-scatter and pile up.</p>
<p>α_π: digitised from L. Redigolo et al., J. Phys. G 51 (2024) 075106 Figs 6 and 8 (E_cm 1.04–1.25 MeV data; R-matrix to 1.0 MeV);
below that a constant-S extrapolation, an upper-side estimate (±×3). αγ: TUNL compilation (2021PH03, 90° × 4π, isotropic ±30 %;
×1.6 for the 6.92/7.12 lines, ×2 uncertain). ¹¹B: Breit-Wigner of the 17.23 MeV 1⁻ level of ¹²C with (2J+1)Γγ₀ ≥ 115 eV (Kelley
2017), Γp/Γ = 0.5 assumed: ~{XS.B11_g0_ub_est[i]:.0f} µb at 1.03 MeV against ⁷Li(p,γ₀) {XS.Li7_g0_ub[i]:.0f} µb.</p>
<p>Table: <code>lnl/out/target/cross_sections.csv</code>; code <code>lnl/target/target_model.py</code>.</p>''',
        short='cross sections')

# --------------------------------------------------------------------------- #
# 4. per target
rows = []
for name, lab in (('ATOMKI 2016/2022, LiF 30 on-res', 'ATOMKI LiF 30, 441 keV'), (LNL_441, 'LNL LiF 34, 441 keV'),
                  ('Hanoi 2024, LiF 30 at 0.80', 'Hanoi LiF 30, 800 keV'), (LNL_THIN, 'LNL LiF 34, 1.03 MeV'),
                  (LNL_THICK, 'LNL LiF 935, 1.03 MeV'), ('MX17 candidate: LiF 100 at 1050', 'LiF 100, 1.05 MeV')):
    v = SC.loc[name, 'F_pairs_per_8Be_pair']
    g = SC.loc[name, 'F_gamma_per_8Be_gamma']
    col = LI if v < 3 else F
    rows.append((lab, v, col, f'{name}: ¹⁹F pairs / ⁸Be pairs = {v:.3g}; ¹⁹F γ / ⁸Be γ = {g:.3g}',
                 f'γ: ×{g:.2g}'))
rows.append(('Li₂O, Li, LiPON (any E)', 1e-1, OK, 'no fluorine', 'none'))
bars = sd.hbars(rows, vmax=1e4, vmin=1e-1, log=True, width=900, h=40, label_w=420,
                fmt=lambda v: '0' if v <= 0.1 else (f'{v:.1f}' if v < 10 else f'{v:,.0f}'), size=26)
D.slide('pertarget', sd.title(f'On LNL’s LiF at 1.03 MeV, ¹⁹F pairs outnumber ⁸Be pairs {f_thin:.0f}–{f_thick:.0f} to one',
                              '¹⁹F 6.05 MeV E0 pairs per ⁸Be IPC pair for the targets each group used (log scale); the note gives ¹⁹F γ per ⁸Be γ')
        + bars + sd.p('Blue: harmless (the 441 keV calibration). Red: fluorine dominates. Green: no fluorine at all.', 24, sd.MUT),
        '''<p>Integrated through each target with PSTAR stopping (Bragg additivity), the Zahnow ⁷Li cross sections and the ¹⁹F
cross sections of the previous slide. LNL’s “1.03 MeV at the centre” for the 935 µg/cm² target means ~1.12 MeV in, ~0.93 out
(190 keV of loss): the upper half sits where α_π rises to 3–7 mb.</p>
<p>The ratio counts every pair in 4π. A detector then cuts on energy: one E0 pair has 5.0 MeV, an 18 MeV IPC pair 17 MeV.
What fluorine costs is rate, dead time and pile-up (next two slides), not a fake 18 MeV pair from a single reaction.</p>
<p><code>lnl/out/target/scenarios.csv</code>, <code>fluorine_scan.csv</code> (thickness × energy grid).</p>''',
        foot='target_model.py layered_yield(); ⁸Be IPC = 3.5×10⁻³ × (γ₀ + γ₁)', short='per target')

# --------------------------------------------------------------------------- #
# 5. LNL-like array
rl = []
for name, lab in ((LNL_441, 'LiF 34, 441 keV'), (LNL_THIN, 'LiF 34, 1.03 MeV'), (LNL_THICK, 'LiF 935, 1.03 MeV')):
    r = RL.loc[name]
    rl.append((lab, r))
P = sd.Plot(1000, 600, x=(-0.5, 2.5), y=(1e-3, 1e5, 'log'), ylabel='two-clover coincidences per second (0.8 µA)')
P.xticks([(k, lab) for k, (lab, _) in enumerate(rl)]).yticks(sd.log_ticks(-3, 5))
for k, (lab, r) in enumerate(rl):
    tE = f'{lab}: ¹⁹F E0 two-clover {r.two_clover_E0_per_s:.3g}/s'
    tB = f'{lab}: ⁸Be IPC two-clover {r.two_clover_8Be_per_s:.3g}/s ({r.two_clover_8Be_per_s * 86400:,.0f}/day)'
    P.vbar(k - 0.17, r.two_clover_E0_per_s, 110, F, tip=tE, base=1e-3)
    P.vbar(k + 0.17, r.two_clover_8Be_per_s, 110, LI, tip=tB, base=1e-3)
    P.text(k, max(r.two_clover_E0_per_s, r.two_clover_8Be_per_s) * 4, f'×{r.E0_over_8Be_coinc:,.0f}', 26, sd.INK,
           anchor='middle', weight=600)
thick = RL.loc[LNL_THICK]
side = sd.col(
    sd.legend([('¹⁹F E0 pairs', F, 'box'), ('⁸Be IPC pairs', LI, 'box')], 24),
    sd.callout(f'Thick LiF at 1.03 MeV: ~{thick.clover_triples_per_s:,.0f} triple coincidences per second '
               'in <i>each</i> clover, almost all fluorine.', F, 24),
    sd.callout(f'The ⁸Be pairs: {thick.two_clover_8Be_per_s * 86400:,.0f}/day thick, '
               f'{RL.loc[LNL_THIN].two_clover_8Be_per_s * 86400:,.0f}/day thin, before any cut.', LI, 24),
    sd.callout('A cut on energy removes single E0 pairs; the DAQ still has to take them, and they pile up.', sd.INK, 24),
    w=560, gap=24)
D.slide('lnlarray', sd.title('In an LNL-like clover array the fluorine pairs outrun the ⁸Be pairs by thousands',
                             'A toy of the LNL 2023 geometry: 4 clovers, 10×10 cm at 12.75 cm, ΔE–E triple coincidence; 0.8 µA')
        + sd.row(P.svg('LNL-like coincidence rates'), side, gap=56), f'''
<p>A toy, to ×2: 4 clovers, each 4.9 % of 4π; a lepton above 1 MeV passes the triple coincidence; a 6–7 MeV γ does so with
6×10⁻⁴ per clover hit (Marchi 2021, slide 14) and leaves something in an E block 30 % of the time. Two-clover acceptance
1.2 % for 18 MeV IPC (Marchi 2021, slide 20); for the wide-angle E0 pairs 3 % × 0.64 (both leptons above 1 MeV).</p>
<p>Thick target at 0.8 µA: ¹⁹F pairs {thick.R_F_pairs:.2g}/s and γ {thick.R_F_gamma:.2g}/s into 4π; each clover sees
{thick.clover_hits_per_s:,.0f} hits/s, a {thick.pileup_prob_100ns:.1e} chance of a second hit in 100 ns. ⁸Be IPC pairs into 4π:
{thick.R_8Be_pairs:.1f}/s.</p>
<p>Not in the toy and possibly worse: if the telescopes sit in the vacuum without an absorber, ¹⁹F(p,α₀) α (~7 MeV),
⁷Li(p,α)α (8.7 MeV) and backscattered protons reach the ΔE bars, ~10⁵ α/s into 4π on the thick target. (ask)</p>
<p><code>lnl/target/target_rates.py</code> → <code>lnl/out/target/rates_lnl_like.csv</code>.</p>''',
        foot='TOY (×2). Triple coincidence and acceptances from Góngora-Servín 2025 and Marchi 2021', short='LNL array')

# --------------------------------------------------------------------------- #
# 6. MX17 with LiF
def mx_rows(hw):
    q = RM[(RM.hw == hw)].set_index(['scenario', 'I_uA'])
    out = []
    for scen, lab in (('MX17 candidate: Li2O 300 at 1070', 'Li₂O 300'), ('MX17 candidate: LiF 100 at 1050', 'LiF 100'),
                      (LNL_THICK, 'LiF 935 (LNL)')):
        for I in (1.0, 4.0):
            if (scen, I) in q.index:
                out.append((f'{lab}, {I:.0f} µA', q.loc[(scen, I)]))
    return out


hw_show = 'big plastics' if HAVE_BIGP else 'as built'
mr = mx_rows(hw_show)
P1 = sd.Plot(800, 560, x=(-0.6, len(mr) - 0.4), y=(1, 1e5, 'log'), ylabel='single-arm legs per arm per second',
             title='trigger legs')
SHORT = {'Li₂O 300': 'Li₂O', 'LiF 100': 'LiF', 'LiF 935 (LNL)': 'LNL'}
P1.xticks([(k, SHORT[lab.split(', ')[0]] + ' ' + lab.split(', ')[1].replace(' µA', '')) for k, (lab, _) in enumerate(mr)]).yticks(sd.log_ticks(0, 5))
P1.xlabel = 'target and current (µA): Li₂O 300, LiF 100, LNL LiF 935'
P2 = sd.Plot(800, 560, x=(-0.6, len(mr) - 0.4), y=(1e-4, 1, 'log'), ylabel='P(extra MM track in the 1.2 µs window)',
             title='Micromegas occupancy')
P2.xticks([(k, SHORT[lab.split(', ')[0]] + ' ' + lab.split(', ')[1].replace(' µA', '')) for k, (lab, _) in enumerate(mr)]).yticks(sd.log_ticks(-4, 0))
P2.xlabel = 'target and current (µA)'
for k, (lab, r) in enumerate(mr):
    col = OK if 'Li₂O' in lab else F
    P1.vbar(k, r.legs_per_arm_total, 70, col, base=1,
            tip=f'{lab}: {r.legs_per_arm_total:,.0f} legs/arm/s ({r.F_legs_per_arm:,.0f} from ¹⁹F); prescale {r.prescale_for_90pc_live:.0f} for ≥ 90 % DREAM live')
    P1.text(k, r.legs_per_arm_total * 1.6, f'P={r.prescale_for_90pc_live:.0f}', 20, sd.INK, anchor='middle')
    occ = max(r.mm_extra_track_prob, 1.1e-4)
    P2.vbar(k, occ, 70, col, base=1e-4, tip=f'{lab}: {r.mm_extra_track_prob:.2%} (0 drawn at the floor)')
P1.hline(15, sd.MUT, tip='cosmics: FEASIBILITY_SIM §4, 9–22 legs/s per arm')
labels = ''.join(f'<p style="width:{760 / len(mr):.0f}px;font-size:19px;text-align:center;color:{sd.MUT}">{lab}</p>' for lab, _ in mr)
q4 = RM[(RM.hw == hw_show) & (RM.scenario == LNL_THICK) & (RM.I_uA == 4.0)]
acc_tof = float(q4.F_acc_in_window_per_day_afterTOF.iloc[0]) if len(q4) else float('nan')
acc_no = float(q4.F_acc_in_window_per_day_noTOF.iloc[0]) if len(q4) else float('nan')
q1 = RM[(RM.hw == hw_show) & (RM.scenario == 'MX17 candidate: LiF 100 at 1050') & (RM.I_uA == 1.0)]
acc_tof_thin = float(q1.F_acc_in_window_per_day_afterTOF.iloc[0]) if len(q1) else float('nan')
D.slide('mx17', sd.title(f'MX17 could live with thin LiF, at a cost; Li₂O costs nothing ({hw_show})',
                         'Geant4 singles libraries (¹⁹F γ lines and 6.05 MeV E0 pairs) scaled to each target; green = no fluorine')
        + sd.row(P1.svg('legs'), P2.svg('mm occupancy'), gap=44)
        + sd.p(f'P = single-arm prescale for ≥ 90 % DREAM live; dashed line: cosmics, ~15 legs/s per arm. '
               f'Thick LNL LiF at 4 µA: ~{acc_tof:.0f} fluorine accidentals/day in E_sum 13–18 MeV after TOF ({acc_no:,.0f} without), '
               f'~1 % of the IPC there. LiF 100 at 1 µA: {acc_tof_thin:.3f}/day.', 24, sd.MUT), f'''
<p>Per E0 pair (as built): a leg in a given arm 2.0 %, in any arm 8.3 %, in two arms never (0 in 10⁶); a drift-gap track per
arm 28 %. Per ¹⁹F γ: a leg 0.08 % per arm. A ¹⁹F leg carries at most ~6.9 MeV, so an accidental two-arm event needs two
γ legs (or three hits) to reach the 13–18 MeV window.</p>
<p>Model: legs/arm = ¹⁹F + ⁸Be (0.39 %/4 per γ) + 15/s cosmics; two-arm accidentals 6 × 20 ns × R²; the pair trigger
(~22/s × I) never prescaled; DREAM 298 µs non-paralysable; the singles prescale P is the smallest power of 2 that keeps
≥ 90 % live. MM window 20 × 60 ns. TOF keeps 0.6/20 of accidentals (0.3 ns cut in a 20 ns window).
Accidental pile-up: leg energies drawn from the Geant4 library, 100 ns integration.</p>
<p><code>lnl/target/target_rates.py</code> → <code>rates_mx17.csv</code>; libraries from <code>target/lxplus/target_singles.py</code>
over L6/L8 (E0) and L3/L8 (γ) runs.</p>''',
        foot=f'Geant4 L3/L6/L8, hardware {hw_show}; rates from target_model.py yields', short='MX17 rates')

# --------------------------------------------------------------------------- #
# 7. heat
P = sd.Plot(1100, 640, x=(0.1, 4.0, 'log'), y=(0, 1100), xlabel='beam current (µA), 1.05 MeV',
            ylabel='peak temperature of the film (°C)')
P.xticks([(v, f'{v:g}') for v in (0.1, 0.2, 0.5, 1, 2, 4)]).yticks([(v, str(v)) for v in range(0, 1101, 200)])
cols = {H16: F, H22: HEAT, HN: sd.PURPLE, HD: LI, HG: OK, HC: sd.INK}
labs = {H16: 'ATOMKI 2016 strip, Plexiglas rods', H22: 'ATOMKI 2022 strip, Al rods', HN: '1 µm Ni disk (Hanoi Li₂O)',
        HD: '10 µm Al disk, clamped r = 10 mm', HG: '25 µm graphite disk', HC: '25 µm Cu disk'}
for h, col in cols.items():
    q = TH[(TH.holder == h) & (TH.Ep_keV == 1050)].sort_values('I_uA')
    P.line(q.I_uA, q.T_max_C, col, tips=[f'{labs[h]}: {t:.0f} °C at {i:g} µA ({pw:.2f} W)' for i, t, pw in zip(q.I_uA, q.T_max_C, q.P_W)])
for v, lab, tip in ((180, 'Li melts 180', 'lithium metal melting point'),
                    (T_DIFF, f'Li through 10 µm Al in a day {T_DIFF:.0f}', 'D = 4.5 exp(−139 kJ/RT) cm²/s (Costas 1963)'),
                    (T_LIFEV, f'300 µg/cm² LiF gone in a week {T_LIFEV:.0f}', 'Hertz-Knudsen; LiF vapour pressure ESTIMATE ±×3'),
                    (660, 'Al melts 660', 'aluminium melting point')):
    P.hline(v, sd.MUT, label=lab, tip=tip, anchor='start')
leg = sd.legend([(labs[h], c) for h, c in cols.items()], 21)
D.slide('heat', sd.title('A strip target at 1 µA runs at 400–700 °C; a clamped disk or graphite stays below 150 °C',
                         'Steady-state peak temperature against current at 1.05 MeV: conduction to the clamp plus radiation, σ = 1.5 mm spot')
        + sd.row(P.svg('target temperature'), sd.col(leg, sd.callout(
            f'ATOMKI 2016’s strip: {t16:.0f} °C at 1 µA and 0.8 MeV. That is where Li diffuses through the Al within hours, and why '
            'Hanoi’s foils “burned out many times” at 1–1.5 µA.', HEAT, 23), w=500, gap=28), gap=48), f'''
<p>Model (<code>target_model.py</code> temp_strip / temp_disk): finite-volume steady state, conduction in the foil to a clamp at 27 °C
(a strip 5 × 50 mm held at both ends 25 mm from the beam, as Gulyás 2016; or a disk clamped at r = 10 mm), radiation from both
faces (Al ε = 0.08, C 0.85, Cu 0.05), Gaussian beam σ = 1.5 mm. Power = I × energy lost in film + foil: at 1.05 MeV the beam leaves
10 µm Al at ~0.48 MeV (0.53 W/µA); at 0.8 MeV it stops in it (0.77 W/µA); graphite and Cu stop it (all of it).</p>
<p>Sensitivity: with ε = 0.3–0.6 the strip at 1 µA drops to 240–350 °C, and at 5 µA is still 590–800 °C; σ = 3 mm takes 10–25 %
off. Disks barely move (conduction-dominated). The Plexiglas rods (k = 0.2 W/m/K) are treated as insulators.</p>
<p>Limits: Li in Al D = 4.5 e^(−139 kJ/mol/RT) cm²/s (Costas 1963) → 10 µm in a day at {T_DIFF:.0f} °C; Li vapour pressure
(CRC) → 1 µm gone in 10 h at {T_LIEV:.0f} °C; LiF (ΔH_sub ≈ 256 kJ/mol, ESTIMATE) → 300 µg/cm² in a week at {T_LIFEV:.0f} °C.
Li₂O melts at 1438 °C; LiOH at 462 °C.</p>''',
        foot='thermal.csv, limits.csv · strip geometry: Gulyás 2016 (NIM A 808, 21) · emissivity is the main unknown', short='heat')

# --------------------------------------------------------------------------- #
# 8. diffusion -> 441 share
dif = [(k, v) for k, v in SC.iterrows() if 'diffused' in k and k.startswith('Li 53')]
rows = []
for k, v in dif:
    lab = k.replace('Li 53 at 1.04, ', '').replace(' diffused to ', ' → ').replace(' in 10 µm Al', ', 10 µm Al')
    rows.append((lab, v.f17, LI if v.f17 < 0.02 else (HEAT if v.f17 < 0.3 else F),
                 f'{k}: 441-keV share of γ₀ {v.f17:.1%}, direct E1 {v.fdc:.1%}, mean E* {v.mean_Estar:.2f} MeV'))
bars = sd.hbars(rows, vmax=1.0, width=820, h=34, label_w=520, fmt=lambda v: f'{v:.1%}', size=24)
D.slide('diffusion', sd.title('Lithium that diffuses into the backing meets the beam at 441 keV: up to 78 % of γ₀ becomes the 17.64 MeV line',
                              'Share of γ₀ from the 441 keV resonance, 1 µm Li at 1.04 MeV, as more of it diffuses into a 10 µm or a thick Al backing')
        + bars, '''
<p>In 10 µm of Al a 1.04 MeV proton slows to ~0.48 MeV at the back face, so Li that has diffused deep sees energies just above the
441 keV resonance (Γ 12 keV, σ 50× the 1.03 MeV one). If the backing stops the beam, any diffused Li sees 441 keV exactly:
ATOMKI 2016’s “actual target thickness = 10 µm” put most of their pairs on the 17.64 MeV M1 line.</p>
<p>Profile: half-Gaussian of width √(4Dt) from the film into the Al; the fraction diffused is a free parameter. LiF that loses
fluorine under beam (Redigolo 2024 normalise to elastic scattering because CaF₂ loses F) frees Li that can do the same: 10–30 %
freed → 0.8–1.1 % share.</p>
<p><code>scenarios.csv</code> (group “diffusion”).</p>''',
        foot='target_model.py al_with_li(); nominal thin Li₂O/Li at 1.04–1.10 MeV: 0.6 %', short='diffusion')

# --------------------------------------------------------------------------- #
# 9. fit bias
P = sd.Plot(1060, 620, x=(0, 21), y=(-0.1, 0.25), xlabel='441 keV share of γ₀ in the true target (%)',
            ylabel='fake X17 the fit reports (× R_ATOMKI), 30 days')
P.xticks([(v, str(v)) for v in (0, 1, 2, 5, 10, 15, 20)]).yticks([(v, f'{v:+.2f}' if v else '0') for v in (-0.1, -0.05, 0, 0.05, 0.1, 0.15, 0.2, 0.25)])
P.hline(0, sd.MUT, dash=None, w=1.5)
shares = [0.6, 1, 2, 5, 10, 20]
for an, col, lab in (('θ', HEAT, 'θ only (ATOMKI-like)'), ('m_ee', sd.PURPLE, 'm_ee'), ('θ × |y| × E_sum', OK, '3D (reference)')):
    ys = [0.0] + [fb(f'441 keV share of γ₀ = {s}%', an) for s in shares[1:]]
    ch = [0.0] + [fb(f'441 keV share of γ₀ = {s}%', an, col='chi2_resid') for s in shares[1:]]
    P.line(shares, ys, col, tips=[f'{lab}: share {s}% → fake r {y:+.3f}, χ² left {c:.1f}' for s, y, c in zip(shares, ys, ch)])
for k, (sc, mk) in enumerate((('hydrated: all LiOH', 'LiOH'), ('carbonated: all Li₂CO₃', 'Li₂CO₃'),
                              ('carbon 100 µg/cm² on the front', 'C 100'))):
    y = fb(sc, 'θ')
    y3 = fb(sc, 'θ × |y| × E_sum')
    P.points([16 + 1.6 * k], [y], HEAT, r=9, marker='open', tips=[f'{sc}: θ fit {y:+.3f}'])
    P.points([16 + 1.6 * k], [y3], OK, r=9, marker='open', tips=[f'{sc}: 3D fit {y3:+.3f}, χ² {fb(sc, "θ × |y| × E_sum", col="chi2_resid"):.0f}'])
    P.text(16 + 1.6 * k, y + 0.02, mk, 18, sd.MUT, anchor='middle')
P.text(1, 0.22, 'a drifting target fools an angle fit, not the 3D fit', 25, sd.INK, weight=600)
leg = sd.legend([('θ only', HEAT), ('m_ee', sd.PURPLE), ('θ × |y| × E_sum (MX17 reference)', OK),
                 ('hydration / carbon (open)', sd.MUT, 'open')], 22)
side = sd.col(leg, sd.callout(f'At a 20 % share the 3D fit reports {r3_20:+.2f} and its χ² rises by {chi3_20:.0f}: '
                              'the data reject the wrong target model.', OK, 23),
              sd.callout(f'The θ-only fit reports {rt_20:+.2f} with χ² ≈ 6: invisible. ATOMKI’s 6.8σ cannot come from this alone.', HEAT, 23),
              w=540, gap=24)
D.slide('fitbias', sd.title('A target that drifts biases an angle-only fit by up to 20 % of ATOMKI; MX17’s 3D fit by < 6 %',
                            'Fisher bias: truth = a degraded target, model = nominal Li₂O 300 at 1.10 MeV; big plastics, LNL-calibrated response')
        + sd.row(P.svg('fit bias'), side, gap=48), '''
<p><code>target_fit_bias.py</code>: Δ = background(truth) − background(model) per day, from the same Geant4 events reweighted
(lnl_nd.collect with the degraded target’s yields: γ₀/γ₁ totals, the 17.64 / 18.15 / direct split, the direct γ₁ share). The fitted
parameter bias after T days is (TF + P)⁻¹ T b, as in the impostor test (FEASIBILITY_SIM §16). The fit floats M1, E1 and γ₁ norms,
the γ* anisotropy, the θ resolution, the E_sum scale, the acceptance cubic, the |y| tilt, per-arm gains and the structure modes
S_θ 2 % + S_θy 1 %. The θ-only and m_ee rows use the same nuisances in one variable.</p>
<p>“χ² left” is what the data still say after the fit has absorbed what it can: ≫ 1 means a 30-day run would see that the target
model is wrong and could refit it (or fit the 441 share).</p>
<p>The 441 share is the knob for diffusion or a stopping backing (previous slide). Hydration: Li₂O fully converted to LiOH
(×1.6 mass) or Li₂CO₃ (×2.47); carbon: 100 µg/cm² in front.</p>''',
        foot='fit_bias.csv · reference: S_θ 2 % + S_θy 1 % structure; 30 days at 1 µA', short='fit bias')

# --------------------------------------------------------------------------- #
# 10. boron + carbon
cb441 = CB[CB.Ep_keV == 446].sort_values('t_C_ug_cm2')
cb107 = CB[CB.Ep_keV == 1070].sort_values('t_C_ug_cm2')
P1 = sd.Plot(800, 560, x=(0, 100), y=(0, 1.1), xlabel='carbon on the front (µg/cm²)', ylabel='γ₀ yield / clean target',
             title='carbon build-up')
P1.xticks([(v, str(v)) for v in (0, 20, 40, 60, 80, 100)]).yticks([(v, f'{v:.1f}') for v in (0, 0.2, 0.4, 0.6, 0.8, 1.0)])
P1.line(cb441.t_C_ug_cm2, cb441.Y_rel, LI, tips=[f'441 keV, LiF 30: {t:g} µg/cm² C → shift {s:.1f} keV, yield ×{y:.2f}'
                                                  for t, s, y in zip(cb441.t_C_ug_cm2, cb441.shift_keV, cb441.Y_rel)])
P1.line(cb107.t_C_ug_cm2, cb107.Y_rel, OK, tips=[f'1.07 MeV, Li₂O 300: {t:g} µg/cm² C → shift {s:.1f} keV, yield ×{y:.3f}'
                                                  for t, s, y in zip(cb107.t_C_ug_cm2, cb107.shift_keV, cb107.Y_rel)])
P1.text(42, 0.3, '441 keV calibration, LiF 30', 21, LI, weight=600)
P1.text(30, 0.9, '1.07 MeV, Li₂O 300', 21, OK, weight=600)
bb = SC[SC.index.str.startswith('Li2O 300 at 1.07, B/Li')]
bl = np.array([float(s.split('= ')[1]) for s in bb.index])
br = (bb.Y_B_g0 / bb.Y_g0).values
P2 = sd.Plot(800, 560, x=(1e-4, 1, 'log'), y=(1e-5, 0.3, 'log'), xlabel='boron atoms per lithium atom',
             ylabel='¹¹B γ₀ (16.9 MeV) / ⁸Be γ₀', title='boron (ESTIMATE)')
P2.xticks(sd.log_ticks(-4, 0)).yticks(sd.log_ticks(-5, -1))
P2.line(bl, br, B, tips=[f'B/Li = {b:g}: ¹¹B γ₀ / ⁸Be γ₀ = {r:.2g}' for b, r in zip(bl, br)])
P2.vline(0.24, sd.MUT, label='Zahnow ⁷LiF', tip='B/Li = 0.24 in atoms, the commercial ⁷LiF of Zahnow et al. 1995 (EXFOR A0639)')
P2.vline(1e-3, sd.MUT, label='spec', tip='what to ask for: B/Li < 10⁻³, measured by ¹¹B(p,α) NRA')
bnote = ''
if HAVE_BORON:
    b24 = fb('boron B/Li = 0.24', 'θ × |y| × E_sum')
    b24t = fb('boron B/Li = 0.24', 'θ')
    b1 = fb('boron B/Li = 0.01', 'θ × |y| × E_sum')
    bnote = (f'Fit (30 d): B/Li = 0.24 → fake r {b24:+.3f} in 3D ({b24t:+.3f} θ only); B/Li = 10⁻² → {b1:+.4f}.')
else:
    bnote = 'The fit with the 16.9 MeV E1 template is pending (Geant4 L8 E1_16.9).'
D.slide('contam', sd.title('Carbon only hurts the 441 keV calibration; boron can neither fake nor hide an X17',
                           'Left: γ₀ yield with carbon on the front, beam not retuned. Right: ¹¹B(p,γ₀) 16.9 MeV relative to ⁸Be γ₀ (estimate).')
        + sd.row(P1.svg('carbon'), P2.svg('boron'), gap=44) + sd.p(bnote, 24, sd.MUT), f'''
<p>Carbon: 0.38 keV per µg/cm² at 441 keV, 0.22 keV at 1.07 MeV (PSTAR). On the 12 keV-wide 441 keV resonance a 30 µg/cm² LiF
target loses 18 % of its yield for 10 µg/cm² of carbon; at 1.07 MeV the broad resonance makes it irrelevant. Build-up rates in the
literature run from ~10¹⁴ C/cm²/µC to unmeasurable with a cold trap at 10⁻⁷ mbar (Redigolo 2024): use a cold trap and redo a
short 441 keV scan per target.</p>
<p>Boron: ¹¹B(p,γ) has Q = 15.96 MeV, so γ₀ = 16.9 MeV at E_p ≈ 1.05 MeV, an E1 line between γ₁ (15 MeV) and γ₀ (18.15 MeV).
σ(γ₀) ≈ 7.6 µb at 1.05 MeV (ESTIMATE, ×2), ¼ of ⁷Li(p,γ₀). Brine lithium carries up to ~500 ppm B before purification; BN crucibles
are a common evaporation source. {bnote}</p>''',
        foot='carbon.csv, scenarios.csv (boron rows), fit_bias.csv', short='carbon & boron')

# --------------------------------------------------------------------------- #
# 11. make & monitor
steps = [
    dict(label='Deposit', sub='Li₂O by e-beam or reactive Li + O₂; or sputtered LiPON. 100–300 µg/cm². Low-B material.', color=LI,
         tip='ATOMKI’s “Li₂O” was Li metal left to oxidise: composition unknown. LiF only for the 441 keV calibration.'),
    dict(label='Mount', sub='edge-clamped disk on a cooled ring; 10 µm Al ≤ 2 µA, graphite/Cu at 4 µA', color=HEAT,
         tip='never a strip on rods (slide “heat”)'),
    dict(label='Keep dry', sub='Ar glovebox and transfer vessel', color=C,
         tip='Hanoi: 0.30 → 0.44 mg/cm² measured, ×1.47 ≈ LiOH'),
    dict(label='Measure', sub='RBS / NRA on AN2000: Li, O, F, B, C; 441 keV scan: thickness', color=sd.PURPLE,
         tip='the 441 keV yield edge gives the thickness and any carbon; its width gives the composition'),
    dict(label='Run & watch', sub='478 keV PIGE (Li content), γ₀ line shape (energy profile), cold trap', color=OK,
         tip='ATOMKI monitor with a LaBr₃/NaI; the γ₀ line width tracks the proton energy profile in the target'),
    dict(label='Swap', sub='when PIGE drops > 10 % or the 441 scan moves; weekly at 1 µA', color=sd.INK,
         tip='H fluence 1.5×10¹⁹/cm² per week at 1 µA, σ 2 mm, where the beam stops'),
]
D.slide('recipe', sd.title('The MX17 target: Li₂O on a cooled, clamped disk, kept dry, measured on the beam and swapped weekly',
                           'From film to run. Hover each step for the reason.')
        + sd.flow(steps, size=24) + sd.table(['risk', 'size for MX17', 'handled by'], [
            ['¹⁹F (LiF)', 'rate and occupancy, not a fake signal', 'Li₂O; LiF only at 441 keV'],
            ['heat → diffusion, evaporation, puncture', '400–700 °C on a strip at 1 µA', 'clamped disk / graphite, < 150 °C'],
            ['hydration, carbon, 441 share', '3D fit bias < 0.06 R_ATOMKI, χ² flags it', 'Ar transfer, cold trap, PIGE, 441 scans'],
            ['boron', '5 % of γ₀ at B/Li 0.24, fit bias ≤ 0.03 R_ATOMKI', 'spec B/Li < 10⁻³, NRA'],
            ['hydrogen blistering', 'only where the beam stops in metal', 'thin backing + distant dump, or graphite'],
        ], size=23, align=['left', 'left', 'left'], widths=[520, 620, 520]), '''
<p>Thin enough is easy: 100–300 µg/cm² is 0.5–1.5 µm of Li₂O, routine for evaporation (LiF was made to 184 µg/cm² with 6 %
non-uniformity on a rotating substrate, arXiv:2208.03425). Known composition is the hard part, and it is measured with the beam
itself, on the same machines.</p>
<p>Hydrogen: 2×10¹⁸ /cm² per day at 1 µA on a σ = 2 mm spot; Cu blisters somewhere between 10¹⁸ and 3×10¹⁹ /cm²
(Budker/OIST at 2 MeV). With a 10 µm Al backing at 1.1 MeV the beam leaves the target and stops in the dump.</p>''',
        short='recipe')

# --------------------------------------------------------------------------- #
end = (sd.kicker('what this does not rule out, and what to ask')
       + sd.row(
           sd.col(sd.p('Not ruled out', 34, sd.DINK, 600),
                  sd.p('• That LNL’s problem was elsewhere: acceptance drops near 140° (their own worry), cosmics (MEG II 2026), '
                       'or statistics. The fluorine case is an inference from public facts.', 25, sd.DMUT),
                  sd.p('• Their DAQ may have coped: the energy cuts remove single E0 pairs, and the problem is then rate and pile-up, '
                       'which a toy cannot size better than ×2.', 25, sd.DMUT),
                  sd.p('• Emissivity, spot size and LNL’s holder set the real temperature; the boron σ is an estimate (×2).', 25, sd.DMUT),
                  w=820, gap=18),
           sd.col(sd.p('Ask LNL (Marchi, Góngora-Servín)', 34, sd.DINK, 600),
                  sd.p('1. Trigger rate and dead time at 1.03 MeV vs 441 keV.', 25, sd.DMUT),
                  sd.p('2. Backing, holder, spot; target lifetime and PIGE history.', 25, sd.DMUT),
                  sd.p('3. α / proton absorber in front of the in-vacuum telescopes?', 25, sd.DMUT),
                  sd.p('4. The thesis and the LDMA 2025 slides.', 25, sd.DMUT),
                  sd.p('5. Target lab: Li₂O deposition, Ar transfer, B analysis.', 25, sd.DMUT),
                  w=760, gap=18), gap=64))
D.slide('end', end, '', dark=True, short='open')

out = D.write(O / 'lnl-lithium-target.html', note_meta=dict(
    title='The lithium target: what stopped LNL, and what could stop MX17',
    summary=(f'Why the LNL 2023–24 ⁸Be run may have stalled (LiF at 1.03 MeV: ¹⁹F makes {f_thin:.0f}–{f_thick:.0f} pairs per ⁸Be pair; '
             'hot strip targets), and a full study of a thin lithium target for MX17 at LNL: fluorine, heat, diffusion, boron, carbon, '
             'hydrogen, and what each does to the 3D fit.'),
    tags='x17, lnl, target', date='2026-10-22'),
    footer='Built by x17_facility_search/lnl/target/deck/build_deck.py from target_model.py, target_rates.py and target_fit_bias.py outputs.')
print(out)
