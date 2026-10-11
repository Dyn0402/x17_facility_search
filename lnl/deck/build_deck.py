"""Build the LNL ⁸Be feasibility slide note from the lnl_rates.py outputs.

Reads lnl/out/*.csv, lnl/out/figures/*.csv, lnl/out/appendix/*.csv, lnl/out/geant/,
lnl/out/plastics/ and lnl/out/scatter/ (rerun ``lnl_rates.py``, ``appendix_calc.py``,
``sim/lnl_geant.py``, ``plastic_size.py`` and ``sim/lnl_scatter.py`` first if their inputs
changed) and writes a standalone slidedoc page to
lnl/out/lnl-x17-feasibility.html, for dylan-neff.web.cern.ch/notes:

    python lnl/deck/build_deck.py
    python ~/PycharmProjects/dylan-cern-site/scripts/add-note.py \
        lnl/out/lnl-x17-feasibility.html --slug lnl-x17-feasibility --force --deploy
"""
import math
import os
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, os.path.expanduser(os.environ.get(
    'SLIDEDOC_DIR', '~/PycharmProjects/dylan-cern-site/scripts')))
import slidedoc as sd  # noqa: E402
from slidedoc import term, sci  # noqa: E402

HERE = Path(__file__).resolve().parent
LNL = HERE.parent
O = LNL / 'out'
F = O / 'figures'

R_ATOMKI = 5.8e-6            # lnl_rates.R_ATOMKI_2016
R_MEG_181, R_MEG_176 = 1.2e-5, 1.8e-6
C = dict(x17=sd.BLUE, m1=sd.GREY, e1=sd.PURPLE, g1=sd.GOLD, cos=sd.RED, res=sd.ORANGE, dir=sd.PURPLE)

reach = pd.read_csv(O / 'reach.csv')
ytab = pd.read_csv(O / 'yields.csv').set_index('scenario')
acc = pd.read_csv(O / 'acceptance.csv')
acc_h = pd.read_csv(O / 'acceptance_hist.csv')
kin = pd.read_csv(O / 'kinematics.csv')
ex = pd.read_csv(F / 'excitation.csv')
thm = pd.read_csv(F / 'theta_min.csv')
yve = pd.read_csv(F / 'yield_vs_energy.csv')

VETO = 'MM segments + collinearity (ILL §10)'
NOVETO = 'no veto'


def per_day(scn, cur=1.0, g1=1.0, cos=VETO):
    """Accepted signal (at R_ATOMKI) and backgrounds per day, from the 1-day rows."""
    r = reach[(reach.scenario == scn) & (reach.I_uA == cur) & (reach.days == 1)
              & (reach.g1_leak == g1) & (reach.cosmics == cos)].iloc[0]
    return r


def days_to(scn, n_sigma=3, R=R_ATOMKI, **kw):
    """Counting: n = S/sqrt(B) with S, B linear in time -> d = n^2 B / S^2."""
    r = per_day(scn, **kw)
    b = r.B_ipc + r.B_ipc_g1 + r.B_cosmic
    s = r.S_at_ATOMKI * R / R_ATOMKI
    return n_sigma ** 2 * b / s ** 2


def fd(d):
    return f'{d:.0f}' if d >= 10 else f'{d:.1f}'


A16 = 'ATOMKI 2016 anomaly'
d3, d5 = days_to(A16), days_to(A16, 5)
d3c, d5c = days_to(A16, g1=0.0), days_to(A16, 5, g1=0.0)
d3_cn = days_to(A16, cur=4.0)
d3_nov = days_to(A16, cos=NOVETO)
d_meg = days_to(A16, R=R_MEG_181)
pa = per_day(A16)
pa_nov = per_day(A16, cos=NOVETO)
acc_w = acc[acc.window == '125-155'].set_index('case').acc_in_window
acc_geo = acc[acc.window == '125-155'].set_index('case').acc_geom_total
ax17 = acc_w['X17 m=16.7, 18.15']
ATOMKI_ACC = 0.025           # ESTIMATES.md §2: 5-telescope pair acceptance
y16 = ytab.loc[A16]
K = kin.set_index('Ep_keV')
edge_lo, edge_hi = K.loc[1030.0, 'theta_min_deg_m16.7'], K.loc[1030.0, 'theta_min_deg_m17.0']

# --------------------------------------------------------------------------- #
# Geant4 (2026-10-08): lnl/sim/lnl_geant.py -> lnl/out/geant
# --------------------------------------------------------------------------- #
OG = O / 'geant'
G = pd.read_csv(OG / 'reach_geant.csv')
G_chain = pd.read_csv(OG / 'figures' / 'geant_chain.csv')
G_esum = pd.read_csv(OG / 'figures' / 'geant_esum.csv')
G_mat = pd.read_csv(OG / 'material_scan.csv')
G_daq = pd.read_csv(OG / 'daq_load.csv')
G_acc = pd.read_csv(OG / 'acceptance_geant.csv')
G_cos = {k: pd.read_csv(OG / f'cosmics_{k}.csv') for k in ('asbuilt', 'asbuilt_noLS', 'bigP')}
REF = 'MM 15° + TOF'
AB, BP, NOLS = 'as built', 'big plastics', 'as built, LS off'


def g(scn=A16, hw=AB, lev=REF, I=1.0, m=16.7):
    return G[(G.scenario == scn) & (G.hw == hw) & (G.level == lev) & (G.I_uA == I) & (G.mass == m)].iloc[0]


def cos_day(key, lev, esum):
    c = G_cos[key]
    return c[(c.level == lev) & (c.esum == esum)].per_day_125_155.iloc[0]


ga, gb, gn = g(), g(hw=BP), g(hw=NOLS)
ga3 = g(lev='MM 3°')
ga_cn, gb_cn = g(I=4.0), g(hw=BP, I=4.0)
tag_ab = G_acc[(G_acc['sample'] == 'X17_m16.7') & (G_acc.hw == AB)].pair_tag.iloc[0]
tag_bp = G_acc[(G_acc['sample'] == 'X17_m16.7') & (G_acc.hw == BP)].pair_tag.iloc[0]
mm2 = G_acc[(G_acc['sample'] == 'X17_m16.7') & (G_acc.hw == AB)].mm_2arm_active.iloc[0]
s68 = G_acc[(G_acc['sample'] == 'X17_m16.7') & (G_acc.hw == AB) & (G_acc.level == 'trigger') & (G_acc.esum == 'none')].sigma68.iloc[0]


D = sd.Deck('LNL ⁸Be feasibility',
            'Could the MX17 apparatus repeat the ATOMKI ⁷Li(p,e⁺e⁻)⁸Be measurement on an LNL proton beam? '
            'Beam, physics, targets, rates, and the Geant4 reach with the n_TOF hardware and with big plastics.')

# --------------------------------------------------------------------------- #
# 1 cover
# --------------------------------------------------------------------------- #
cover = (sd.kicker('MX17 at LNL Legnaro · Geant4 feasibility · 8 Oct 2026')
         + f'<h1 style="font-size:70px;font-weight:600;line-height:1.08;letter-spacing:-1.5px">'
           f'MX17 tests the ATOMKI ⁸Be claim at 3σ in ~{ga.days_count_opt_live:.0f} days as built, '
           f'and in ~{gb.days_count_opt_live:.1f} days with big plastics</h1>'
         + sd.p('⁷Li(p,e⁺e⁻)⁸Be at the 18.15 MeV resonance, 1 µA. Geant4 of the full apparatus around a Li₂O target, '
                'with a selection that uses no Monte Carlo truth.', 32, sd.DMUT)
         + sd.row(
             sd.bignum(f'{ga.days_count_opt_live:.0f}–{ga.days_fisher_1norm_live:.0f} d', 'n_TOF hardware as built', sd.DBLUE,
                       f'3σ at R = 5.8×10⁻⁶, 1 µA (counting – template fit); {ga_cn.days_count_opt_live:.0f}–{ga_cn.days_fisher_1norm_live:.0f} d on CN at 4 µA. '
                       'Needs 3° MM segments or a 0.3 ns time-of-flight veto against cosmics.',
                       tip=f'Per day in 125–155°: {ga.S_ATOMKI:.1f} X17, {ga.B_ipc:.0f} IPC (γ₀), {ga.B_g1:.1f} IPC (γ₁), '
                           f'{ga.B_cos:.1f} cosmics. E_sum {ga.esum} MeV, MM 15° + TOF.'),
             sd.bignum(f'{gb.days_count_opt_live:.1f}–{gb.days_fisher_1norm_live:.1f} d', 'four 75×75×5 cm plastics', sd.DGREEN,
                       f'The trigger_scint calorimeter option (~€90–140k). {gb_cn.days_count_opt_live * 24:.0f}–{gb_cn.days_fisher_1norm_live * 24:.0f} h on CN at 4 µA.',
                       tip=f'Per day in 125–155°: {gb.S_ATOMKI:.0f} X17, {gb.B_ipc:,.0f} IPC (γ₀), {gb.B_g1:.0f} IPC (γ₁), {gb.B_cos:.1f} cosmics.'),
             sd.bignum(f'{tag_ab * 100:.1f} % → {tag_bp * 100:.0f} %', 'X17 pairs triggered', sd.DGREY,
                       f'Both leptons reach the Micromegas in {mm2 * 100:.0f} % of decays; the two 20×30 cm plastics per arm are the bottleneck.'),
             gap=56))
D.slide('cover', cover, f"""<p>Geant4 on the MX17_Full_Geant <code>lnl</code> branch (runs L1–L6, overnight 2026-10-08):
X17 at four masses, Born IPC M1/E1 at 18.15, 17.64, 15.1 and 14.6 MeV, γ lines, one live day of cosmics, a chamber/backing
scan, for the n_TOF stack as built and with four 75×75×5 cm plastics. Analysis: <code>lnl/sim/lnl_geant.py</code>; write-up
<code>lnl/FEASIBILITY_SIM.md</code>; this deck reads <code>lnl/out/geant/*.csv</code>.</p>
<p>The days use counting in the best window (typically 130–165°) and an Asimov template fit over 90–180° with the IPC and γ₁
normalisations free (the M1/E1 mix fixed); with the mix also free the fit is ×2.3–3 slower. Rates and yields are
<code>lnl_rates.py</code>.</p>""", dark=True, short='Answer')

# --------------------------------------------------------------------------- #
# 2 the setup
# --------------------------------------------------------------------------- #
def setup_svg():
    W, H = 860, 660
    cx, cy = 430, 310
    o = []
    # four arms, viewed along the beam (pinwheel offset not drawn)
    face, depth, half = 150, 120, 140
    for ang in (0, 90, 180, 270):
        a = math.radians(ang)
        ux, uy = math.cos(a), math.sin(a)
        vx, vy = -uy, ux
        def pt(r, s):
            return cx + ux * r + vx * s, cy + uy * r + vy * s
        layers = [(face, face + 22, sd.BLUE, 'Micromegas TPC, 30 mm drift, faces at ±204 mm'),
                  (face + 30, face + 44, sd.GREEN, 'SiPM scintillator wall, 20 bars'),
                  (face + 52, face + 74, sd.GOLD, 'two 20×30×2 cm plastic bars'),
                  (face + 82, face + depth, sd.ORANGE, 'liquid scintillators')]
        for r0, r1, col, tp in layers:
            q = [pt(r0, -half), pt(r1, -half), pt(r1, half), pt(r0, half)]
            o.append(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in q)}" fill="{col}" '
                     f'fill-opacity="0.75" stroke="none"{sd.tipattr(tp)}/>')
    # chamber + target
    o.append(f'<circle cx="{cx}" cy="{cy}" r="40" fill="none" stroke="{sd.MUT}" stroke-width="3"'
             f'{sd.tipattr("Thin target chamber: CFRP 0.4 mm, r ≈ 25 mm (MEG II / ATOMKI style)")}/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="10" fill="{sd.RED}"'
             f'{sd.tipattr("Li₂O / LiF film, ~300 µg/cm² on 10 µm Al, beam into the page")}/>')
    o.append(sd.T(cx, cy + 4, '⊗', 18, '#fff'))
    # an X17 pair at ~140 deg into opposite-ish arms
    for ang, lab in ((-160, 'e⁺'), (-20, 'e⁻')):
        a = math.radians(ang)
        x2, y2 = cx + 290 * math.cos(a), cy + 290 * math.sin(a)
        o.append(sd.arrow(cx, cy, x2, y2, sd.INK, 3))
        o.append(sd.T(x2 + (18 if x2 > cx else -18), y2 - 6, lab, 26, sd.INK))
    o.append(sd.T(cx, H - 6, 'transverse view, beam into the page (schematic, pinwheel offset not drawn)', 22, sd.MUT))
    return sd.svg(W, H, ''.join(o), 'MX17 arms around the Li target')


react = sd.flow([
    dict(label='p, 0.44–1.2 MeV', sub='AN2000 or CN Van de Graaff, ≤ 1–4 µA', color=sd.RULE,
         tip='No neutrons below the ⁷Li(p,n) threshold at E_p = 1.881 MeV, so radiation protection does not cap the current.'),
    dict(label='⁷Li film', sub='Li₂O or LiF, ~300 µg/cm²', color=sd.RED,
         tip='Thin, so the beam never slows into the 441 keV resonance (TARGETS.md).'),
    dict(label='⁸Be*', sub=f'E* = 17.255 + 0.875·E_p', color=sd.ORANGE,
         tip='Q(⁷Li(p,γ)) = 17.2551 MeV. Two M1 resonances (441 keV → 17.64, 1030 keV → 18.15) on a flat E1 direct capture.'),
], size=24)
outs = sd.col(
    sd.callout(f'<b>γ₀</b>, ~{y16.g0_per_s_1uA:,.0f}/s at 1 µA', sd.GREY, 24),
    sd.callout(f'<b>{term("IPC", "Internal pair conversion: the transition makes an e⁺e⁻ pair instead of a photon, ~3.5×10⁻³ of the time (Born, M1 at 18.15 MeV). Mostly small opening angles.")}</b> e⁺e⁻, ~3.5×10⁻³ per γ', sd.GREY, 24),
    sd.callout(f'<b>X17 → e⁺e⁻</b>, R = Γ_X/Γ_γ = 5.8×10⁻⁶ (ATOMKI): ~{y16.g0_per_s_1uA * R_ATOMKI * 86400:.0f}/day into 4π, '
               f'opening angle ≥ {edge_lo:.0f}–{edge_hi:.0f}°', sd.BLUE, 24),
    gap=14)
D.slide('setup', sd.title('A proton on a lithium film; four big arms catch the pairs',
                          'The reaction ATOMKI used, with the n_TOF apparatus around it. Hover the dotted terms, the boxes and the detector layers.')
        + sd.row(sd.col(react, outs, sd.p('The detector is the n_TOF one unchanged: Micromegas for the tracks, scintillators to trigger. '
                                          'Only the target region is new.', 24, sd.MUT), gap=28, w=780),
                 setup_svg(), gap=24),
        """<p>Arms going outward: air; Micromegas TPC (30 mm drift, 60 µm aluminised mylar window, active area 399.4 × 359.9 mm,
faces at ±204 mm); SiPM scintillator wall; two 20 × 30 × 2 cm plastic bars; liquid scintillators. The real layout is a
pinwheel, which the drawing leaves out; the toy acceptance uses plain planes at 204 mm.</p>
<p>Kinematics: the ⁸Be* recoils at β ≈ 0.006, which is negligible. The X17 edge (θ_min = 2·asin(m_X/E_X)) is
133.8–138.9° for m = 16.7–17.0 MeV at E_p = 1.03 MeV (<code>out/kinematics.csv</code>).</p>""",
        short='Setup')

# --------------------------------------------------------------------------- #
# 3 the beam
# --------------------------------------------------------------------------- #
P = sd.Plot(1060, 520, x=(0, 6, 'lin'), y=(0, 3, 'lin'), xlabel='proton energy E_p [MeV]', margin=(24, 30, 92, 190))
P.xticks([(v, str(v)) for v in range(7)])
rows = [(2.2, 'AN2000', 0.2, 2.0, sd.BLUE, 'AN2000 (bldg. 013): 0.2–2 MV, ≤ 1 µA H⁺, self-service; 0° line ≤ 20 nA.\nThe LNL ⁸Be spectrometer ran here in 2023–24 (LiF, ~800 nA, ~790 h).'),
        (1.2, 'CN', 0.8, 5.5, sd.GREEN, 'CN (bldg. 008): 0.8–5.5 MV, 1 µA in the beam sheet, ~4 µA authorised (~6 µA technical).\nPulsed mode: 3 MHz, < 2 ns. Mon–Fri daytime operation.')]
for y, lab, lo, hi, col, tp in rows:
    P.raw(f'<rect x="{P.X(lo):.1f}" y="{P.Y(y + 0.3):.1f}" width="{P.X(hi) - P.X(lo):.1f}" height="{P.Y(y - 0.3) - P.Y(y + 0.3):.1f}" '
          f'rx="8" fill="{col}" fill-opacity="0.8"{sd.tipattr(tp)}/>')
    P.raw(sd.T(P.x0 - 16, P.Y(y) + 8, lab, 26, sd.INK, 'end', 600))
P.raw(f'<rect x="{P.X(0.44):.1f}" y="{P.y0}" width="{P.X(1.23) - P.X(0.44):.1f}" height="{P.ph}" fill="{sd.ORANGE}" fill-opacity="0.12"/>', back=True)
P.vline(0.4414, sd.ORANGE, tip='1⁺ resonance → E* = 17.64 MeV, Γ_lab 12.2 keV, σ 5.9 mb')
P.vline(1.030, sd.ORANGE, tip='1⁺ resonance → E* = 18.15 MeV, Γ_lab 168 keV: the ATOMKI anomaly')
P.vline(1.881, sd.RED, tip='⁷Li(p,n)⁷Be opens at 1.881 MeV: no neutrons below it')
P.text(0.41, 2.78, '441 keV', 21, sd.ORANGE, 'end')
P.text(1.06, 2.78, '1030 keV', 21, sd.ORANGE)
P.text(1.91, 2.78, '(p,n) threshold, 1.88 MeV', 21, sd.RED)
P.text(0.835, 0.2, 'the physics window', 21, sd.ORANGE, 'middle')
beam_side = sd.col(
    sd.callout('<b>Both machines cover it.</b> 0.44–1.23 MeV is the whole programme: the two resonances and the off-resonance points ATOMKI and Hanoi used.', sd.ORANGE, 24),
    sd.callout('<b>No neutrons</b> below 1.88 MeV, so the current is limited by the target, not by radiation protection.', sd.RED, 24),
    sd.callout('<b>LNL already did this:</b> the Marchi / Góngora-Servín spectrometer ran on AN2000 in 2023–24. Unpublished; they are the first people to talk to.', sd.BLUE, 24),
    sd.callout('Access: the yearly LNL PAC (autumn). Contacts: A. Selva, pacbeams@lnl.infn.it.', sd.GREY, 24),
    gap=20, w=560)
D.slide('beam', sd.title('The beam is easy: both LNL Van de Graaffs cover the window',
                         'Energy range of the two machines against the ⁸Be resonances. Hover the bars and the lines.')
        + sd.row(P.svg('LNL machine energy ranges'), beam_side, gap=44),
        """<p>From LNL's own beam sheet (<code>lnl/refs/LNL_Beams_AN2000_CN.txt</code>) and the 2026 CN paper (arXiv:2605.12005). Details,
open questions and contacts are in <code>lnl/FACILITY.md</code>.</p>
<p><b>Ask LNL:</b> energy spread and current stability at 1 µA for days on AN2000; whether CN can sit at ~1 MV for weeks and run
overnight; floor plans of the AN2000 room and CN hall (the four-arm apparatus is ~1.5 m across); the next PAC deadline.</p>""",
        foot='Source: LNL beam sheet (2025 PAC call), CN paper arXiv:2605.12005. lnl/FACILITY.md', short='Beam')

# --------------------------------------------------------------------------- #
# 4 the cross section
# --------------------------------------------------------------------------- #
e = ex[(ex.Ep_keV >= 250) & (ex.Ep_keV <= 1500)].iloc[::4]
P = sd.Plot(1060, 600, x=(250, 1500, 'lin'), y=(1, 1e4, 'log'), xlabel='proton energy E_p [keV]',
            ylabel='σ(p,γ₀) [µb]')
P.xticks([(v, str(v)) for v in (250, 500, 750, 1000, 1250, 1500)]).yticks(sd.log_ticks(0, 4))
ff = lambda v: max(v, 1.0)
P.line(e.Ep_keV, [ff(v) for v in e.res_17_64_g0_ub], C['res'], 3, dash='8 6', markers=False,
       tip='Breit–Wigner, 441 keV resonance (17.64 MeV)')
P.line(e.Ep_keV, [ff(v) for v in e.res_18_15_g0_ub], C['res'], 3, markers=False,
       tip='Breit–Wigner, 1030 keV resonance (18.15 MeV), M1')
P.line(e.Ep_keV, [ff(v) for v in e.direct_g0_ub], C['dir'], 3, markers=False,
       tip='Direct E1 capture = Zahnow total − resonances')
pts = ex[ex.Ep_keV >= 250].iloc[::30]
tips = [f'E_p = {r.Ep_keV:.0f} keV\nσ(γ₀) = {r.sigma_g0_ub:.1f} µb\n  17.64 res {r.res_17_64_g0_ub:.1f}, 18.15 res {r.res_18_15_g0_ub:.1f}, direct {r.direct_g0_ub:.1f}'
        for r in pts.itertuples()]
P.line(e.Ep_keV, e.sigma_g0_ub, sd.INK, 4, markers=False)
P.line(pts.Ep_keV, pts.sigma_g0_ub, sd.INK, 0, r=5, tips=tips)
P.raw(f'<rect x="{P.X(1040):.1f}" y="{P.y0}" width="{P.X(1100) - P.X(1040):.1f}" height="{P.ph}" fill="{sd.BLUE}" fill-opacity="0.12"/>', back=True)
P.text(1060, 6000, 'ATOMKI 2016', 21, sd.BLUE, 'middle')
r1100 = ex.iloc[(ex.Ep_keV - 1100).abs().argmin()]
side = sd.col(
    sd.legend([('total σ(γ₀), Zahnow 1995', sd.INK), ('M1 resonances', C['res']), ('direct E1 capture', C['dir'])], 22),
    sd.callout(f'<b>{y16.frac_direct * 100:.0f} % of the γ₀ is direct E1 capture</b> in ATOMKI\'s 2016 anomaly run '
               f'(Li₂O 300 µg/cm² at 1.10 MeV); the 18.15 resonance makes the rest.', C['dir'], 24),
    sd.callout('That matters: E1 IPC has ~2.5× the M1 rate at 140°, and ATOMKI 2022 sees its excess in direct capture too.', sd.GREY, 24),
    sd.callout('The 441 keV resonance is 50× stronger and makes 17.64 MeV pairs, where MEG II already limits X17. A thick target walks into it.', C['res'], 24),
    gap=22, w=540)
D.slide('xs', sd.title('At 1.1 MeV, half the γ₀ is direct capture, not the resonance',
                       '⁷Li(p,γ₀)⁸Be cross section split into the two M1 resonances and a flat E1 direct capture. Hover the points.')
        + sd.row(P.svg('7Li(p,gamma0) cross section'), side, gap=48),
        """<p>Zahnow <i>et al.</i> 1995 (EXFOR A0639) S-factors for γ₀ and γ₀+γ₁, 98–1500 keV, converted to σ. The resonances are
Breit–Wigner with constant widths (Tilley 2004); direct capture is the remainder. The split is not meaningful below ~500 keV,
where the BW tail and the data disagree, but it is harmless at 1 MeV.</p>
<p>Checks against Tilley: σ(γ₀+γ₁) at 441 keV = 5.93 mb (5.9 ± 0.5); γ₀/(γ₀+γ₁) = 0.69 (0.69–0.72).
MEG II's own 2026 normalisation is reproduced when their n and σ are used (factor 2 in the inputs, not the method).</p>""",
        foot='lnl/out/figures/excitation.csv (lnl_rates.py). Curves below 1 µb are drawn at 1 µb.', short='Cross section')

# --------------------------------------------------------------------------- #
# 5 kinematics
# --------------------------------------------------------------------------- #
P = sd.Plot(1060, 600, x=(400, 1260, 'lin'), y=(125, 155, 'lin'), xlabel='proton energy E_p [keV]',
            ylabel='X17 minimum opening angle θ_min [°]')
P.xticks([(v, str(v)) for v in (400, 600, 800, 1000, 1200)]).yticks([(v, f'{v}°') for v in range(125, 156, 5)])
for m, col, dash in ((16.7, sd.BLUE, None), (16.85, sd.PURPLE, '10 6'), (17.0, sd.GREEN, '4 6')):
    k = f'theta_min_deg_m{m}'
    tps = [f'm_X = {m} MeV, E_p = {r.Ep_keV:.0f} keV\nE* = {r.Estar_MeV:.3f} MeV, θ_min = {r[k]:.1f}°'
           for _, r in kin.iterrows()]
    P.line(kin.Ep_keV, kin[k], col, 3.5, dash=dash, tips=tps)
P.vline(441.4, sd.ORANGE, label='17.64')
P.vline(1030, sd.ORANGE, label='18.15')
side = sd.col(
    sd.legend([('m = 16.7 MeV', sd.BLUE), ('16.85', sd.PURPLE, 'dash'), ('17.0', sd.GREEN, 'dash')], 22),
    sd.callout(f'<b>The X17 piles up above an edge at {edge_lo:.0f}–{edge_hi:.0f}°</b> at the 18.15 resonance; IPC falls steeply there.', sd.BLUE, 24),
    sd.callout('The edge moves by ~10° over the scanned energies, so a real signal must follow it. That is the test the off-resonance points make.', sd.GREY, 24),
    sd.callout('The Geant4 reach uses the window that maximises S/√B (~130–165°) and a template fit over 90–180°; the edge sits inside both for all three masses.', sd.GOLD, 24),
    gap=22, w=540)
D.slide('kin', sd.title(f'X17 pairs open to ≥ {edge_lo:.0f}°; the edge moves with E_p',
                        'θ_min = 2·asin(m_X/E_X) against E_p, for three masses. Hover the points.')
        + sd.row(P.svg('X17 minimum opening angle'), side, gap=48),
        """<p>E* = Q + (7/8)·E_p with Q = 17.2551 MeV; the X17 is emitted from the ⁸Be* at rest (β ≈ 0.006 is neglected), with
E_X = E*. <code>lnl/out/kinematics.csv</code>.</p>""",
        foot='lnl/out/kinematics.csv', short='Kinematics')

# --------------------------------------------------------------------------- #
# 6 targets
# --------------------------------------------------------------------------- #
TG = [('ATOMKI 2016 anomaly', 'Li₂O 300 µg/cm², 1.10 MeV'),
      ('LNL 2023-24, thin', 'LiF 34 µg/cm², 1.03 MeV'),
      ('LNL 2023-24, thick', 'LiF 935 µg/cm², 1.09 MeV'),
      ('MEG II-2026 normalisation', 'Li₂O 700 µg/cm², 1.03 MeV'),
      ('Li metal 1 um, enriched', 'Li metal 1 µm, 1.05 MeV'),
      ('Li metal stops beam (ATOMKI 2016 mishap)', 'Li metal, beam stops in it, 1.10 MeV')]
trows = []
for scn, lab in TG:
    y = ytab.loc[scn]
    col = sd.RED if y.frac_17_64 > 0.1 else sd.BLUE
    tp = (f'{lab}: ΔE in film {y.dE_keV:.0f} keV, ⟨E*⟩ = {y.mean_Estar_MeV:.2f} MeV\n'
          f'γ₀ at 1 µA: {y.g0_per_s_1uA:,.0f}/s; from 17.64 res {y.frac_17_64 * 100:.1f} %, '
          f'18.15 res {y.frac_18_15_res * 100:.0f} %, direct {y.frac_direct * 100:.0f} %')
    trows.append((lab, y.frac_17_64 * 100, col, tp))
bars = sd.hbars(trows, 100, width=520, h=60, label_w=470, fmt=lambda v: f'{v:.1f} %', size=28)
lm = ytab.loc['Li metal stops beam (ATOMKI 2016 mishap)']
side = sd.col(
    sd.callout('<b>Keep the film thin</b> (≲ 300 µg/cm² ≈ 60 keV of energy loss): then &lt; 1 % of the γ₀ is 17.64 MeV, and the signal sits at 18.15.', sd.BLUE, 24),
    sd.callout(f'A beam that stops in Li metal at 1.10 MeV gets <b>{lm.frac_17_64 * 100:.0f} %</b> of its γ₀ from 441 keV. '
               'That is what happened to ATOMKI\'s 2016 targets (Sas 2022).', sd.RED, 24),
    sd.callout('Use <b>boron-free</b> Li: ¹¹B(p,γ) puts 16–17 MeV γ in the window. LiF gives a free ¹⁹F E0 line (6.05 MeV) for calibration.', sd.GREY, 24),
    gap=22, w=560)
D.slide('targets', sd.title('Thin films only: a stopping target makes 17.64 MeV',
                            'Share of the ground-state photons made in the 441 keV resonance, per target configuration. Hover the bars.')
        + sd.row(sd.col(bars, gap=0, w=1060), side, gap=44, align='center'),
        """<p>Thin-target yields from the Zahnow σ and PSTAR stopping (Li by Bragg subtraction), integrated through the film
(<code>lnl_rates.thin_yield</code>). Recommendation (<code>lnl/TARGETS.md</code>): a few-hundred-nm film of LiF or Li₂O
(or Li metal, or sputtered LiPON) on a 10–25 µm Al/C/Cu foil, in a thin carbon-fibre chamber. Heat at 1 µA is ~0.06 W in
a 300 µg/cm² film.</p>""",
        foot='lnl/out/yields.csv (lnl_rates.yields_table)', short='Targets')

# --------------------------------------------------------------------------- #
# 7 Geant4: where the X17 pairs go
# --------------------------------------------------------------------------- #
steps = list(dict.fromkeys(G_chain.step.str.replace(r' E_sum .*', ' E_sum window', regex=True)))
crow = []
for hw, col in ((AB, C['m1']), (BP, sd.GREEN)):
    gg = G_chain[G_chain.hw == hw].reset_index(drop=True)
    for i, r in gg.iterrows():
        lab = ['MM, 2 arms', '+ trigger legs', '+ E_sum window', '+ MM 15° + TOF', '+ 125–155°'][i]
        crow.append((f'{lab}', r.acc * 100, col, f'{hw}: {r.step}: {r.acc * 100:.2f} % of X17 (m 16.7) decays', ''))
half = len(crow) // 2
side = sd.col(
    sd.callout(f'<b>Geometry is fine:</b> both leptons reach the active Micromegas in {mm2 * 100:.0f} % of X17 decays (the toy said 45 %).', C['x17'], 24),
    sd.callout(f'<b>The trigger keeps {tag_ab * 100:.1f} %.</b> The two 20×30×2 cm plastics per arm cover a fraction of the Micromegas cone. '
               f'Four 75×75×5 cm slabs keep {tag_bp * 100:.0f} %.', sd.RED, 24),
    sd.callout('Reading all 20 SiPM bars alone changes nothing (3.3 %): the plastics are the bottleneck.', sd.GREY, 24),
    sd.callout(f'Opening angle from the beam spot to the two MM centroids: σ68 = {s68:.1f}°.', sd.GREY, 24),
    gap=18, w=560)
D.slide('acc', sd.title(f'The trigger, not the geometry: {tag_ab * 100:.1f} % of X17 pairs as built, {tag_bp * 100:.0f} % with big plastics',
                        'Geant4, 10⁶ X17 (m = 16.7 MeV) at 18.15 MeV from the beam spot. Hover the bars.')
        + sd.row(sd.col(sd.p('n_TOF stack as built', 26, weight=600),
                        sd.hbars(crow[:half], 40, width=330, h=34, label_w=260, fmt=lambda v: f'{v:.1f} %', size=24),
                        sd.p('big plastics, all 20 SiPM bars', 26, weight=600),
                        sd.hbars(crow[half:], 40, width=330, h=34, label_w=260, fmt=lambda v: f'{v:.1f} %', size=24), gap=14),
                 side, gap=40),
        f"""<p>An arm is "ok" with a trigger leg (a SiPM bar AND a plastic, each ≥ 0.5 MIP) and a Micromegas segment whose charge
centroid is in the active area. Pairs = the two ok arms with most scintillator energy. The arm choice matches the true lepton
arms in 99.8 % of X17 events. The pre-Geant4 toy multiplied geometry by EPS_REST = 0.14 from the ILL; the real factor here
is {tag_ab / mm2:.3f} as built.</p>
<p>The accepted X17 spreads from the 134° edge to 170°: the four-arm geometry favours back-to-back pairs, so only ~64 % of the
tagged pairs fall in 125–155°. The template fit uses the rest.</p>""",
        foot='lnl/out/geant/figures/geant_chain.csv, acceptance_geant.csv', short='Acceptance')

# --------------------------------------------------------------------------- #
# 8 E_sum
# --------------------------------------------------------------------------- #
def esum_plot(hw, title_):
    P = sd.Plot(780, 520, x=(4, 18, 'lin'), y=(0, 0.36, 'lin'), xlabel='E_sum, two arms [MeV]',
                ylabel='fraction / 0.5 MeV' if hw == AB else None, margin=(24, 24, 92, 110))
    P.xticks([(v, str(v)) for v in (4, 8, 12, 16)]).yticks([(v, f'{v:.1f}') for v in (0, 0.1, 0.2, 0.3)])
    for smp, col, nm in (('X17_m16.7', C['x17'], 'X17'), ('M1_18.15', C['m1'], 'IPC M1 18.15'),
                         ('E1_18.15', C['e1'], 'IPC E1 18.15'), ('M1_15.1', C['g1'], 'IPC M1 15.1 (γ₁)'),
                         ('E1_15.1', sd.ORANGE, 'IPC E1 15.1 (γ₁)')):
        d = G_esum[(G_esum.hw == hw) & (G_esum['sample'] == smp)]
        d = d[(d.E_lo >= 4) & (d.E_lo < 18)]
        xs, ys = sd.step_xy(list(d.E_lo) + [float(d.E_lo.iloc[-1]) + 0.5], list(d.frac))
        P.line(xs, ys, col, 3, markers=False, tip=nm)
    return sd.col(sd.p(title_, 26, weight=600), P.svg(f'E_sum {hw}'), gap=6)


D.slide('esum', sd.title('The energy sum separates 15 from 18 MeV transitions',
                         'Two-arm E_sum (SiPM + plastic + LS) of pairs at 120–160°, Geant4. Hover the lines.')
        + sd.row(esum_plot(AB, 'n_TOF stack as built (with the LS)'), esum_plot(BP, 'big plastics, 75×75×5 cm'), gap=30)
        + sd.row(sd.legend([('X17', C['x17']), ('IPC 18.15 M1', C['m1']), ('IPC 18.15 E1', C['e1']),
                            ('IPC 15.1 M1 (γ₁)', C['g1']), ('IPC 15.1 E1 (γ₁)', sd.ORANGE)], 22),
                 sd.callout(f'As built, a 13–17 MeV window keeps 54 % of the X17 and leaves {ga.B_g1:.1f} γ₁-IPC/day. '
                            'Big plastics: 83 % and 1.5 %. Without the LS the peaks merge.', sd.GREEN, 24), gap=40),
        """<p>The pre-Geant4 estimate assumed the n_TOF stack (~40 % containment) could not separate the γ₁ transitions (to the
3.0 MeV state, W ≈ 15 MeV, twice as frequent as γ₀) and counted their IPC in full. Geant4 says the LS make the difference:
with them, nothing from 15.1 MeV reaches 13 MeV. The LS suffered pile-up at n_TOF; at LNL the rates are ~10³× lower,
but whether they can be read is to be checked <b>(ask)</b>. "As built, LS off": the window cannot exclude γ₁, and the reach
goes from 15 to 19 days.</p>""",
        foot='lnl/out/geant/figures/geant_esum.csv', short='Energy')

# --------------------------------------------------------------------------- #
# 9 cosmics
# --------------------------------------------------------------------------- #
LV = [('trigger', 'scintillators only'), ('MM 15°', 'MM segments at 15° (measured chambers) + 20° collinearity'),
      ('MM 3°', 'MM segments at 3°'), ('MM 15° + TOF', '15° segments + time of flight (σ_t 0.3 ns)'),
      ('MM 3° + TOF', '3° segments + time of flight')]
fmt_c = lambda v: f'{v:,.0f}' if v >= 1 else ('0' if v == 0 else f'{v:.1f}')
crows = [[f'<b>{lv}</b><br><span style="font-size:19px;color:{sd.MUT}">{d}</span>',
          fmt_c(cos_day('asbuilt', lv, 'none')), fmt_c(cos_day('asbuilt', lv, '13–17')),
          fmt_c(cos_day('asbuilt_noLS', lv, '8–16')), fmt_c(cos_day('bigP', lv, '13–17'))] for lv, d in LV]
D.slide('cosmics', sd.title('Cosmics are the one background that can sink it, and three cuts kill them',
                            'Cosmic two-arm pairs per day in 125–155°, Geant4, one live day (1.3×10⁸ μ). Compare: ~110 IPC/day as built, ~1,500 with big plastics.')
        + sd.row(sd.table(['level', 'as built<br>no E_sum cut', 'as built<br>E_sum 13–17', 'LS off<br>E_sum 8–16', 'big plastics<br>E_sum 13–17'],
                          crows, size=24, widths=[620, 170, 170, 170, 190]),
                 sd.col(sd.callout('<b>An upper E_sum edge:</b> a muon through two arms leaves 20–35 MeV (with LS); an X17 pair has 17.1 MeV. ×20.', sd.GOLD, 24),
                        sd.callout('<b>15° segments are not enough:</b> the collinearity veto cannot see one straight track when each segment is 15° off.', sd.RED, 24),
                        sd.callout('<b>3° segments or a 0.3 ns TOF</b> (the lower arm fires 2.3 ns after the upper) bring them to ~1/day; together, 0.', sd.GREEN, 24),
                        gap=18, w=520), gap=36, align='center'),
        """<p>Cosmic μ± from a 3×3 m plane, 1 /cm²/min, zenith perpendicular to the beam (sea level, no overburden). MEG II
members showed in 2026 that cosmic two-arm coincidences make a ~140° bump in ATOMKI-type spectrometers; this is that
effect quantified for MX17. Entries ≤ 2 are single events in one live day. The pointing cut keeps 90 % of X17 segments
per arm (D = 135 mm at 15°, 57 mm at 3°; scattering in the window and gas sets the 3° value). σ_t = 0.3 ns per arm is an
assumption <b>(ask)</b>: at 1 ns the veto no longer separates the 2.3 ns muon delay. Two-arm cosmic triggers: 3.5/s as built,
22/s with big plastics; DREAM stays &gt; 99 % live.</p>""",
        foot='lnl/out/geant/cosmics_*.csv', short='Cosmics')

# --------------------------------------------------------------------------- #
# 10 per-day budget
# --------------------------------------------------------------------------- #
def gbudget(r, title_):
    rows_ = [('X17 at ATOMKI R', r.S_ATOMKI, C['x17'], 'Accepted X17 per day at R = 5.8×10⁻⁶ in 125–155°'),
             ('IPC, γ₀ (18 MeV)', r.B_ipc, C['m1'], 'M1 from the resonances + E1 from direct capture'),
             ('IPC, γ₁ (15 MeV)', r.B_g1, C['g1'], 'After the E_sum window'),
             ('cosmic μ pairs', r.B_cos, C['cos'], 'After E_sum, MM 15° and TOF'),
             ('EPC + accidentals', r.B_epc + r.B_acc, sd.GREY, 'Conversions of target γ in the material; random two-arm pairs (2τ = 20 ns)')]
    return sd.col(sd.p(title_, 26, weight=600),
                  sd.hbars(rows_, 3e3, width=420, h=40, log=True, vmin=0.1, label_w=250,
                           fmt=lambda v: f'{v:,.0f}' if v >= 10 else f'{v:.1f}', size=24), gap=18)


D.slide('budget', sd.title('After the cuts, the background is IPC',
                           f'Accepted per day in 125–155°, ATOMKI 2016 conditions (Li₂O 300 µg/cm², 1.10 MeV), 1 µA, MM 15° + TOF. Log bars; hover them.')
        + sd.row(gbudget(ga, f'n_TOF as built, E_sum {ga.esum} MeV'), gbudget(gb, f'big plastics, E_sum {gb.esum} MeV'), gap=60)
        + sd.row(sd.callout(f'S/B in the window: {ga.S_ATOMKI / ga.B_ipc:.2f} as built, {gb.S_ATOMKI / gb.B_ipc:.3f} with big plastics: '
                            'the big plastics take more IPC, but 15× more X17 per day.', C['x17'], 26),
                 sd.callout('So the reach is set by the IPC statistics and by how well its angular shape is known (M1/E1 mix, interference).', sd.GREY, 26), gap=48),
        """<p>Per day = the ATOMKI 2016 anomaly, 1 µA rows of <code>lnl/out/geant/reach_geant.csv</code>. IPC = Born α × Geant4
acceptance × efficiency, weighted by the resonant/direct split of <code>lnl_rates.py</code>. EPC: 2×10⁸ γ of the four ⁸Be
lines through the target, holder, chamber and dump: as built none passes in 125–155° (&lt; 6×10⁻⁸ per γ); with the big
plastics a few do (~4×10⁻⁸ per γ, ~10/day), &lt; 1 % of the IPC.</p>""",
        foot='lnl/out/geant/reach_geant.csv', short='Background')

# --------------------------------------------------------------------------- #
# 11 days to significance
# --------------------------------------------------------------------------- #
SC = [('ATOMKI 2016 anomaly', 'ATOMKI 2016 anomaly', 'Li₂O 300, 1.10 MeV'),
      ('ATOMKI 2016, 18.15 res', 'ATOMKI 2016 on-res', 'Li₂O 300, 1.04 MeV'),
      ('LNL 2023-24, thick', 'LNL-style thick', 'LiF 935, 1.09 MeV'),
      ('MEG II-2026 normalisation', 'thicker Li₂O', 'Li₂O 700, 1.03 MeV'),
      ('ATOMKI 2022 direct', 'ATOMKI 2022 direct', 'LiF 300, 0.80 MeV'),
      ('Hanoi 2024', 'Hanoi', 'LiF 300, 1.225 MeV')]
n = len(SC)
P = sd.Plot(1100, 640, x=(0.03, 300, 'log'), y=(-0.6, n - 0.4, 'lin'), xlabel='days of beam to 3σ at the ATOMKI ratio',
            margin=(24, 30, 92, 360))
P.xticks([(v, f'{v:g}') for v in (0.03, 0.1, 0.3, 1, 3, 10, 30, 100, 300)])
for v in (0.1, 1, 10, 100):
    P.raw(sd.line(P.X(v), P.y0, P.X(v), P.y0 + P.ph, sd.RULE, 1), back=True)
for i, (scn, nm, sub) in enumerate(SC):
    y = n - 1 - i
    vals = []
    for hw, col in ((AB, C['m1']), (BP, sd.GREEN)):
        for I, mk in ((1.0, 'circle'), (4.0, 'open')):
            r = g(scn, hw, I=I)
            vals.append((r.days_count_opt_live, col, mk,
                         f'{nm} ({sub}), {hw}, {I:g} µA:\n3σ in {fd(r.days_count_opt_live)} d (counting, {r.win_opt}°), '
                         f'{fd(r.days_fisher_1norm_live)} d (template fit); 5σ ×25/9'))
    P.raw(sd.line(P.X(min(v[0] for v in vals)), P.Y(y), P.X(max(v[0] for v in vals)), P.Y(y), sd.RULE, 6), back=True)
    for d, col, mk, tp in vals:
        P.points([d], [y], col, r=11, marker=mk, tips=[tp])
    P.raw(sd.T(P.x0 - 18, P.Y(y) - 2, nm, 24, sd.INK, 'end', 600))
    P.raw(sd.T(P.x0 - 18, P.Y(y) + 24, sub, 20, sd.MUT, 'end'))
P.vline(14, sd.GOLD, dash='4 6', label='2 weeks')
side = sd.col(
    sd.legend([('n_TOF as built', C['m1'], 'dot'), ('big plastics', sd.GREEN, 'dot')], 22),
    sd.p('filled: 1 µA (AN2000) · open: 4 µA (CN)', 22, sd.MUT),
    sd.callout(f'<b>The anomaly point:</b> {ga.days_count_opt_live:.0f} d as built, {gb.days_count_opt_live:.1f} d with big plastics, at 1 µA.', C['x17'], 24),
    sd.callout(f'Off-resonance (0.80, 1.225 MeV), the direct-capture test: ~2 months as built, ~4 days with big plastics, ×4 faster on CN.', sd.GREY, 24),
    sd.callout('Mass: 17.0 MeV is ~2× faster than 16.7 (the edge moves to where the acceptance is larger).', sd.GREY, 24),
    gap=18, w=500)
D.slide('reach', sd.title(f'Two weeks as built, a day and a half with big plastics',
                          'Days to a 3σ excess at the ATOMKI ratio per target configuration, Geant4, MM 15° + TOF. Counting in the best window; hover for the template fit.')
        + sd.row(P.svg('days to 3 sigma'), side, gap=40),
        """<p>Counting: d = 9·B/S² in the window that maximises S/√B (130–165° typically). Template fit: Asimov over 90–180° in 2°
bins, IPC and γ₁ normalisations free, M1/E1 mix fixed by the Zahnow decomposition; with the mix free too, ×2.3–3 longer
(the accepted E1 IPC has its own 140–170° hump from the back-to-back geometry). All days divided by the DREAM live fraction (≥ 99 %).
Signal counts the 18.15 resonance and direct capture with the same R.</p>""",
        foot='lnl/out/geant/reach_geant.csv', short='Reach')

# why big plastics win, and how big (2026-10-09): lnl/plastic_size.py
sys.path.insert(0, str(HERE))
import plastics_scatter as PS  # noqa: E402
PS.size_slides(D, O)

# --------------------------------------------------------------------------- #
# 12 the small stuff + material
# --------------------------------------------------------------------------- #
mrow = []
for v, lab in (('baseline (CFRP 0.4, Al 10 µm)', 'CFRP 0.4 mm chamber, Al 10 µm backing'), ('chAl0.5', 'Al 0.5 mm chamber'),
               ('chAl1', 'Al 1.0 mm chamber'), ('bkC20', 'C 20 µm backing'), ('bkCu25', 'Cu 25 µm backing')):
    r = G_mat[(G_mat['sample'] == 'X17_m16.7') & (G_mat.variant == v) & (G_mat.level == 'MM 15°')].iloc[0]
    mrow.append((lab, r.sigma68, sd.RED if r.sigma68 > 7 else sd.BLUE, f'{lab}: X17 σ68(Δθ) = {r.sigma68:.1f}°, acc {r.acc * 100:.2f} %'))
D.slide('small', sd.title('Everything else is small; the chamber wall sets the resolution',
                          'Left: X17 opening-angle resolution against the target-region material (L5). Right: the backgrounds Geant4 found negligible.')
        + sd.row(sd.col(sd.p('X17 σ68(θ_reco − θ_true), MM 15°', 26, weight=600),
                        sd.hbars(mrow, 14, width=360, h=38, label_w=380, fmt=lambda v: f'{v:.1f}°', size=24),
                        sd.p('Acceptance does not change. Keep the CFRP chamber and a low-Z backing.', 24, sd.MUT), gap=16, w=900),
                 sd.col(sd.callout('<b>EPC</b> from the 8Be γ in the target, holder, chamber, dump: almost all at 25–92°: none in 125–155° as built (2×10⁸ γ), &lt; 1 % of the IPC with big plastics.', sd.GREY, 23),
                        sd.callout(f'<b>Accidentals</b> (2τ = 20 ns): ≲ 0.02/day. <b>DREAM</b>: {G_daq[(G_daq.hw == AB) & (G_daq.scenario == A16) & (G_daq.I_uA == 1)].trig_total.iloc[0]:.1f} two-arm triggers/s as built, '
                                   f'{G_daq[(G_daq.hw == BP) & (G_daq.scenario == A16) & (G_daq.I_uA == 1)].trig_total.iloc[0]:.0f}/s big plastics, all cosmics: &gt; 99 % live.', sd.GREY, 23),
                        sd.callout('<b>⁷Li(p,p′) 478 keV</b> never makes a leg. <b>²⁷Al(p,γ) 10.8 MeV</b> (Al backing above 992 keV) and <b>¹⁹F</b> lines (LiF): singles only; use Li₂O.', sd.GREY, 23),
                        sd.callout('<b>The 6.05 MeV E0 line is invisible</b> to the n_TOF trigger (0 in 10⁶ pairs). Calibrate on 441 keV (17.64 MeV).', sd.RED, 23),
                        gap=16, w=640), gap=40),
        """<p>L5: X17 and M1 IPC with the chamber in Al 0.5 / 1.0 mm instead of CFRP 0.4 mm, and the backing in C 20 µm or Cu 25 µm
instead of Al 10 µm, 5×10⁵ each. The resolution is the MM-centroid chord from the beam spot; multiple scattering in the
chamber wall dominates. L3: γ lines from the spot (⁸Be 18.15/17.64/15.1/14.6, ¹⁹F 6.13/6.92/7.12, ⁷Li 0.478, ²⁸Si 10.76/1.78).
L6: Born E0 pairs at 6.05 MeV.</p>""",
        foot='lnl/out/geant/material_scan.csv, epc_*.csv, daq_load.csv', short='Material')

# peak widening from the target region (2026-10-09): lnl/sim/lnl_scatter.py
PS.scatter_slides(D, O)

# --------------------------------------------------------------------------- #
# 13 the record
# --------------------------------------------------------------------------- #
def rec_svg():
    W, H = 1664, 430
    x0, x1 = 120, 1600
    lo, hi = -6.5, -4.3
    X = lambda v: x0 + (math.log10(v) - lo) / (hi - lo) * (x1 - x0)
    o = [sd.line(x0, 300, x1, 300, sd.MUT, 2)]
    for k in (-6, -5):
        for m in range(1, 10):
            v = m * 10 ** k
            if lo <= math.log10(v) <= hi:
                big = m == 1
                o.append(sd.line(X(v), 300, X(v), 300 + (16 if big else 8), sd.MUT, 2 if big else 1))
                if m in (1, 2, 5):
                    o.append(sd.T(X(v), 340, f'{m}×10{sd.sup(k)}' if m > 1 else f'10{sd.sup(k)}', 21))
    o.append(sd.T(x1, 390, 'R = Γ(X17)/Γ(γ), 18.15 MeV unless noted', 21, sd.MUT, 'end'))
    r30 = R_ATOMKI * math.sqrt(ga.days_count_opt_live / 30)
    r30b = R_ATOMKI * math.sqrt(gb.days_count_opt_live / 30)
    marks = [(R_ATOMKI, 'ATOMKI 2016', sd.ORANGE, 0, 'PRL 116, 042501: 6.8σ at 1.10 MeV, m = 16.70 MeV. Hanoi 2024 (≥ 4σ at 1.225 MeV) and ATOMKI 2022 (direct capture) agree.'),
             (R_MEG_181, 'MEG II 90 % CL', sd.RED, 1, 'EPJC 85, 763 (2025): R(18.1) < 1.2×10⁻⁵, no signal; ATOMKI hypothesis p = 6.2 %.'),
             (R_MEG_176, 'MEG II, 17.6 MeV', sd.RED, 0, 'R(17.6) < 1.8×10⁻⁶ (90 % CL).'),
             (r30, 'MX17 as built, 30 d', sd.BLUE, 1, f'3σ reach after 30 days at 1 µA, n_TOF hardware, Geant4: R = {r30:.1e}'),
             (r30b, 'MX17 big plastics, 30 d', sd.GREEN, 2, f'3σ reach after 30 days at 1 µA with four 75×75×5 cm plastics: R = {r30b:.1e}')]
    for v, lab, col, lvl, tp in marks:
        x = X(v)
        ytop = 230 - 80 * lvl
        o.append(f'<g{sd.tipattr(tp)}>' + sd.line(x, ytop + 14, x, 290, col, 2, '4 4')
                 + f'<circle cx="{x:.1f}" cy="300" r="11" fill="{col}"/>'
                 + sd.T(x, ytop - 8, lab, 23, col, 'middle', 600) + sd.T(x, ytop + 16 - 4, sci(v), 20, col) + '</g>')
    return sd.svg(W, H, ''.join(o), 'X17 ratio: claims, limits and MX17 reach'), r30, r30b


rs, r30, r30b = rec_svg()
D.slide('record', sd.title('A month reaches below the ATOMKI claim; with big plastics, ×5 below',
                           'The X17 ratio R on one log axis: ATOMKI\'s claim, MEG II\'s null, and MX17\'s 3σ reach after 30 days at 1 µA (Geant4). Hover the points.')
        + rs
        + sd.row(sd.callout('<b>The record is contradictory.</b> ATOMKI (2016, 2022) and Hanoi (2024) see ~140° excesses; MEG II (2025) sees nothing; '
                            'MEG II members (Sept 2026) show cosmics make a 140° bump in ATOMKI-type spectrometers.', sd.ORANGE, 25),
                 sd.callout(f'<b>What MX17 adds:</b> tracks + timing that remove cosmics, and with big plastics ~{tag_bp / ATOMKI_ACC:.0f}× ATOMKI\'s pair acceptance (as built, about equal: {tag_ab * 100:.1f} % vs ~{ATOMKI_ACC * 100:.1f} %). '
                            'LNL\'s own 2023–24 data (unpublished) are the other result to wait for.', sd.BLUE, 25), gap=48),
        """<p>Sources in <code>lnl/PHYSICS.md</code>: Krasznahorkay <i>et al.</i>, PRL 116, 042501 (2016); Sas <i>et al.</i>,
arXiv:2205.07744 (2022); Tran The Anh <i>et al.</i> (Hanoi, 2024); MEG II, EPJC 85, 763 (2025); Benmansour <i>et al.</i>,
arXiv:2609.18383 (2026). MX17 points: counting reach, R₃σ ∝ 1/√days, from the 1 µA ATOMKI-anomaly rows of
<code>lnl/out/geant/reach_geant.csv</code>.</p>""",
        foot='MX17 points: lnl/out/geant/reach_geant.csv (MM 15° + TOF).', short='Record')

# --------------------------------------------------------------------------- #
# 14 closing
# --------------------------------------------------------------------------- #
close = (sd.kicker('What Geant4 does not settle, and what comes next')
         + '<h2 style="font-size:64px;font-weight:600;line-height:1.1">Feasible as built; easy with big plastics</h2>'
         + sd.row(
             sd.col(sd.p('Still to know (ask)', 30, sd.DINK, 600),
                    sd.flow([dict(label='SiPM-wall timing', sub='σ_t ≲ 0.5 ns makes TOF kill cosmics without MM upgrades', color=sd.DRED,
                                  tip='Assumed 0.3 ns per arm. At 1 ns the TOF veto fails; then 3° MM segments are needed.'),
                             dict(label='Can the LS be read?', sub='as-built E_sum and γ₁ rejection need them', color=sd.DRED,
                                  tip='Without the LS: 19 instead of 15 days, and the cosmic E_sum edge is gone.'),
                             ], dark=True, size=24, arrow=''),
                    sd.flow([dict(label='IPC shape', sub='M1–E1 interference: ×2–3 on the fit if the mix is free', color=sd.DRED,
                                  tip='Zhang–Miller generator, or measured off-resonance E1 shape (0.8 MeV runs).'),
                             dict(label='Hall space', sub='AN2000 room, CN hall: ~1.5 m apparatus', color=sd.DRED)],
                            dark=True, size=24, arrow=''), gap=16),
             sd.col(sd.p('Next', 30, sd.DINK, 600),
                    sd.flow([dict(label='Email LNL', sub='A. Selva / pacbeams: hall plans, AN2000 vs CN, next PAC', color=sd.DBLUE),
                             dict(label='Email T. Marchi', sub='LNL 2023–24 ⁸Be data; Góngora-Servín thesis', color=sd.DBLUE)],
                            dark=True, size=24, arrow=''),
                    sd.flow([dict(label='Big plastics', sub='quotes for 4 × 75×75×5 cm + PMTs (trigger_scint)', color=sd.DBLUE),
                             dict(label='PAC case', sub='resonance + off-resonance + 441 keV in a week on AN2000', color=sd.DBLUE)],
                            dark=True, size=24, arrow=''), gap=16),
             gap=64))
D.slide('next', close, """<p>Run list, code and pipeline: <code>lnl/GEANT_PREP.md</code> §0 and <code>lnl/sim/lxplus/</code>. Not simulated:
¹¹B contamination (16 MeV γ), beam halo on the holder and flanges, the beam pipe beyond the chamber, and the M1–E1
interference in the IPC shape.</p>""", dark=True, short='Next')

# --------------------------------------------------------------------------- #
# appendix: the basics (lnl/deck/appendix.py; run lnl/appendix_calc.py first)
# --------------------------------------------------------------------------- #
import appendix  # noqa: E402
appendix.add(D, dict(O=O, ytab=ytab, ex=ex, acc_h=acc_h, ga=ga, gb=gb, g=g, G_acc=G_acc, R_ATOMKI=R_ATOMKI,
                     R_MEG_176=R_MEG_176, A16=A16, mm2=mm2, tag_ab=tag_ab, tag_bp=tag_bp))

out = D.write(O / 'lnl-x17-feasibility.html', note_meta=dict(
    title='LNL ⁸Be feasibility: MX17 on a proton beam',
    summary=f'Could the MX17 apparatus repeat the ATOMKI ⁷Li(p,e⁺e⁻)⁸Be measurement at LNL? Geant4: 3σ at the ATOMKI ratio in ~{ga.days_count_opt_live:.0f} days at 1 µA as built, ~{gb.days_count_opt_live:.1f} days with big plastics.',
    tags='x17, lnl, feasibility', date='2026-10-08'),
    footer='Built by x17_facility_search/lnl/deck/build_deck.py from lnl_rates.py and lnl/sim/lnl_geant.py outputs (Geant4, 2026-10-08).')
print(out, f'as built {ga.days_count_opt_live:.1f}/{ga.days_fisher_1norm_live:.1f} d, big plastics {gb.days_count_opt_live:.2f}/{gb.days_fisher_1norm_live:.2f} d')
