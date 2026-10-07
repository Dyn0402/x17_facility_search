"""Build the LNL ⁸Be feasibility slide note from the lnl_rates.py outputs.

Reads lnl/out/*.csv and lnl/out/figures/*.csv (rerun ``lnl_rates.py`` first if
the model changed) and writes a standalone slidedoc page to
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

D = sd.Deck('LNL ⁸Be feasibility',
            'Could the MX17 apparatus repeat the ATOMKI ⁷Li(p,e⁺e⁻)⁸Be measurement on an LNL proton beam? '
            'Beam, physics, targets, rates and reach before Geant4.')

# --------------------------------------------------------------------------- #
# 1 cover
# --------------------------------------------------------------------------- #
cover = (sd.kicker('MX17 at LNL Legnaro · pre-Geant4 estimate · 8 Oct 2026')
         + f'<h1 style="font-size:76px;font-weight:600;line-height:1.08;letter-spacing:-1.5px">'
           f'MX17 on a 1 µA proton beam tests the ATOMKI ⁸Be claim at 3σ in ~{d3:.0f} days</h1>'
         + sd.p(f'⁷Li(p,e⁺e⁻)⁸Be at the 18.15 MeV resonance, the reaction behind the X17 claim. '
                f'Good to a factor ~2 until Geant4 replaces the trigger efficiency.', 32, sd.DMUT)
         + sd.row(
             sd.bignum(f'{d3:.0f} / {d5:.0f} d', '3σ / 5σ at the ATOMKI ratio', sd.DBLUE,
                       f'1 µA, n_TOF stack as built. ×4 faster on CN at 4 µA ({fd(d3_cn)} d).',
                       tip=f'R = Γ_X/Γ_γ = 5.8×10⁻⁶, Li₂O 300 µg/cm², E_p = 1.10 MeV.\n'
                           f'Accepted per day: {pa.S_at_ATOMKI:.0f} X17, {pa.B_ipc:,.0f} IPC (γ₀), '
                           f'{pa.B_ipc_g1:,.0f} IPC (γ₁), {pa.B_cosmic:.0f} cosmics.'),
             sd.bignum(f'{d3c:.0f} / {d5c:.0f} d', 'if 15 MeV pairs can be rejected', sd.DGREEN,
                       'A calorimeter that separates the γ₁ (15 MeV) IPC from the 18 MeV signal.'),
             sd.bignum(f'{ax17 * 100:.0f} % vs {ATOMKI_ACC * 100:.1f} %', 'pair acceptance at 140°', sd.DGREY,
                       'Four big Micromegas arms around a point target, against ATOMKI\'s five telescopes.',
                       tip=f'Toy: X17 m = 16.7 MeV, both leptons in two different arms, measured in 125–155°. '
                           f'Two-arm geometric {acc_geo["X17 m=16.7, 18.15"] * 100:.0f} %.'),
             gap=56))
D.slide('cover', cover, f"""<p>The whole estimate is <code>lnl/lnl_rates.py</code> (run 2026-10-07); its outputs are
<code>lnl/out/*.csv</code>, and the write-up is <code>lnl/ESTIMATES.md</code>. This deck is built by
<code>lnl/deck/build_deck.py</code> from those CSVs.</p>
<p>Reach is a counting experiment in the 125–155° opening-angle window: background = IPC (M1 from the
resonances, E1 from direct capture, and the γ₁ transitions to the 3 MeV state) + cosmics after the ILL
Micromegas cuts. The number of days to an n σ excess is d = n² B / S², with S and B the accepted counts per
day. A template fit over all angles is typically ~1.5× better.</p>
<p>Every number after the geometry carries one factor, EPS_REST = 0.14, from the ILL G1 Geant4 campaign. That
is the factor-2 uncertainty, and it is the first thing Geant4 replaces.</p>""", dark=True, short='Answer')

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
    sd.callout('The counting window in this note is 125–155°, which holds the edge for all three masses.', sd.GOLD, 24),
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
# 7 acceptance
# --------------------------------------------------------------------------- #
th = acc_h.theta_lo_deg + 2.5
P = sd.Plot(1060, 600, x=(0, 180, 'lin'), y=(1e-4, 0.3, 'log'), xlabel='measured opening angle [°]',
            ylabel='accepted fraction per 5° bin')
P.xticks([(v, f'{v}°') for v in range(0, 181, 30)]).yticks([(1e-4, '10⁻⁴'), (1e-3, '10⁻³'), (1e-2, '10⁻²'), (1e-1, '10⁻¹')])
P.raw(f'<rect x="{P.X(125):.1f}" y="{P.y0}" width="{P.X(155) - P.X(125):.1f}" height="{P.ph}" fill="{sd.GOLD}" fill-opacity="0.12"/>', back=True)
for k, col, nm in (('X17 m=16.7, 18.15', C['x17'], 'X17, m = 16.7'), ('IPC E1, 18.15', C['e1'], 'IPC E1 (direct)'),
                   ('IPC M1, 18.15', C['m1'], 'IPC M1 (resonance)'), ('IPC M1, 15.1', C['g1'], 'IPC M1 15.1 (γ₁)')):
    i0 = int((acc_h[k] > 0).values.argmax())
    hh = acc_h.iloc[i0:]
    v = hh[k].clip(lower=1e-4)
    tps = [f'{nm}, {a:.0f}–{a + 5:.0f}°: {b:.2e}' for a, b in zip(hh.theta_lo_deg, hh[k])]
    xs, ys = sd.step_xy(list(hh.theta_lo_deg) + [180], list(v))
    P.line(xs, ys, col, 3, markers=False)
    P.line(hh.theta_lo_deg + 2.5, v, col, 0, r=3, tips=tps)
side = sd.col(
    sd.legend([('X17, m = 16.7 MeV', C['x17']), ('IPC M1, 18.15', C['m1']), ('IPC E1, 18.15', C['e1']), ('IPC M1, 15.1 (γ₁)', C['g1'])], 22),
    sd.callout(f'<b>{ax17 * 100:.0f} % of X17 pairs</b> land in 125–155° with each lepton in a different arm. ATOMKI\'s spectrometer: ~{ATOMKI_ACC * 100:.1f} %.', C['x17'], 24),
    sd.callout(f'IPC in the window: {acc_w["IPC M1, 18.15"] * 100:.2f} % (M1), {acc_w["IPC E1, 18.15"] * 100:.1f} % (E1). '
               'Most IPC pairs are nearly collinear and never reach two arms.', C['m1'], 24),
    sd.callout('<b>Geometry is not the problem; the trigger stack is.</b> As built it keeps 2.3 % of X17 pairs against 27.6 % for the Micromegas.', sd.RED, 24),
    gap=20, w=540)
D.slide('acc', sd.title('Four arms see 140° with ~15× ATOMKI\'s acceptance',
                        'Toy acceptance against measured opening angle: two different arms, KE > 1 MeV, σ_θ = 5°. Hover the bins.')
        + sd.row(P.svg('acceptance vs opening angle'), side, gap=48),
        f"""<p>Toy (<code>lnl_rates.acceptance</code>, 4×10⁵ events per case): the four n_TOF Micromegas faces at 204 mm from the
beam axis, active 399.4 (⊥ beam) × 359.9 mm (along the beam), a point source, both leptons in two <i>different</i> arms with
KE &gt; 1 MeV, opening angle smeared by 5°. No pinwheel offset, no scattering.</p>
<table><tr><th>case</th><th>two-arm geometric</th><th>in 125–155°</th></tr>
{''.join(f'<tr><td>{c}</td><td>{acc_geo[c] * 100:.1f} %</td><td>{acc_w[c] * 100:.2f} %</td></tr>' for c in acc_w.index)}</table>
<p>Everything after geometry (trigger, E_sum cut, reconstruction) is one factor, EPS_REST = 0.038/0.276 = 0.14, the ILL G1
ratio of X17 acceptance × efficiency to Micromegas acceptance.</p>""",
        foot='lnl/out/acceptance_hist.csv; window 125–155° shaded. X17 has no pairs below 115°.', short='Acceptance')

# --------------------------------------------------------------------------- #
# 8 per-day budget
# --------------------------------------------------------------------------- #
def budget(r, title_):
    rows_ = [('X17 at ATOMKI R', r.S_at_ATOMKI, C['x17'], 'Accepted X17 per day at R = 5.8×10⁻⁶ (125–155°)'),
             ('IPC, γ₀ (18 MeV)', r.B_ipc, C['m1'], 'M1 from the resonances + E1 from direct capture'),
             ('IPC, γ₁ (15 MeV)', r.B_ipc_g1, C['g1'], 'Transitions to the 3.0 MeV state; the n_TOF stack (~40 % containment) cannot tell 15 from 18 MeV'),
             ('cosmic μ pairs', r.B_cosmic, C['cos'], f'{r.cosmics}')]
    return sd.col(sd.p(title_, 26, weight=600),
                  sd.hbars(rows_, 3e4, width=440, h=40, log=True, vmin=10, label_w=250,
                           fmt=lambda v: f'{v:,.0f}', size=24), gap=18)


D.slide('budget', sd.title('With the Micromegas cosmic vetoes, the background is IPC',
                           f'Accepted events per day in 125–155°, ATOMKI 2016 conditions (Li₂O 300 µg/cm², 1.10 MeV), 1 µA. Log bars; hover them.')
        + sd.row(budget(pa_nov, 'Scintillators only, no cosmic veto'),
                 budget(pa, 'MM segments ≤ 3° + 20° collinearity veto (ILL §10)'), gap=60)
        + sd.row(sd.callout(f'Without the vetoes cosmics outnumber the IPC ×{pa_nov.B_cosmic / (pa_nov.B_ipc + pa_nov.B_ipc_g1):.0f} '
                            f'and the 3σ time grows from {d3:.0f} to {d3_nov:.0f} days. This is the failure mode MEG II members '
                            '(Benmansour 2026) attribute to ATOMKI: cosmic two-arm coincidences peak near 140°.', C['cos'], 26),
                 sd.callout(f'With them, the γ₁ IPC is the biggest single background ({pa.B_ipc_g1:,.0f}/day). '
                            f'Rejecting it by energy takes the 3σ time from {d3:.0f} to {d3c:.0f} days.', C['g1'], 26), gap=48),
        f"""<p>Per day = the 1-day rows of <code>lnl/out/reach.csv</code>. γ₀ in 4π at 1 µA: {y16.g0_per_s_1uA:,.0f}/s; ×86400; × IPC α
(Born) × window acceptance × EPS_REST.</p>
<p>Cosmics: ILL §10, n_TOF hardware, ~9×10⁵ pairs per 50 days without vetoes, ~10⁴ with ≤ 3° Micromegas segments and a 20°
collinearity veto. The ILL fit window was 60–180°, so these are conservative here. The LNL hall overburden is unknown
<b>(ask)</b>. A point-vertex cut (~/25) and CN's pulsed beam would cut cosmics further but change little at 1 µA.</p>""",
        foot='lnl/out/reach.csv (1-day rows). Cosmics from the ILL Geant4 study, not yet simulated in the LNL geometry.', short='Background')

# --------------------------------------------------------------------------- #
# 9 days to significance
# --------------------------------------------------------------------------- #
SC = [('ATOMKI 2016 anomaly', 'ATOMKI 2016 anomaly', 'Li₂O 300, 1.10 MeV'),
      ('ATOMKI 2016, 18.15 res', 'ATOMKI 2016 on-res', 'Li₂O 300, 1.04 MeV'),
      ('LNL 2023-24, thick', 'LNL-style thick', 'LiF 935, 1.09 MeV'),
      ('MEG II-2026 normalisation', 'thicker Li₂O', 'Li₂O 700, 1.03 MeV'),
      ('ATOMKI 2022 direct', 'ATOMKI 2022 direct', 'LiF 300, 0.80 MeV'),
      ('Hanoi 2024', 'Hanoi', 'LiF 300, 1.225 MeV')]
n = len(SC)
P = sd.Plot(1100, 640, x=(0.3, 300, 'log'), y=(-0.6, n - 0.4, 'lin'), xlabel='days of beam to 3σ at the ATOMKI ratio',
            margin=(24, 30, 92, 360))
P.xticks([(v, str(v) if v >= 1 else str(v)) for v in (0.3, 1, 3, 10, 30, 100, 300)])
for v in (1, 3, 10, 30, 100):
    P.raw(sd.line(P.X(v), P.y0, P.X(v), P.y0 + P.ph, sd.RULE, 1), back=True)
for i, (scn, nm, sub) in enumerate(SC):
    y = n - 1 - i
    vals = [(days_to(scn), C['m1'], 'circle', 'as built, 1 µA'), (days_to(scn, g1=0.0), sd.GREEN, 'circle', 'γ₁ rejected, 1 µA'),
            (days_to(scn, cur=4.0), C['m1'], 'open', 'as built, CN 4 µA'), (days_to(scn, cur=4.0, g1=0.0), sd.GREEN, 'open', 'γ₁ rejected, CN 4 µA')]
    P.raw(sd.line(P.X(min(v[0] for v in vals)), P.Y(y), P.X(max(v[0] for v in vals)), P.Y(y), sd.RULE, 6), back=True)
    for d, col, mk, lab in vals:
        r5 = d * 25 / 9
        P.points([d], [y], col, r=11, marker=mk, tips=[f'{nm} ({sub}), {lab}:\n3σ in {fd(d)} d, 5σ in {fd(r5)} d'])
    P.raw(sd.T(P.x0 - 18, P.Y(y) - 2, nm, 24, sd.INK, 'end', 600))
    P.raw(sd.T(P.x0 - 18, P.Y(y) + 24, sub, 20, sd.MUT, 'end'))
P.vline(14, sd.GOLD, dash='4 6', label='2 weeks')
side = sd.col(
    sd.legend([('as built', C['m1'], 'dot'), ('γ₁ rejected', sd.GREEN, 'dot')], 22),
    sd.p('filled: 1 µA (AN2000) · open: 4 µA (CN)', 22, sd.MUT),
    sd.callout(f'<b>The anomaly point is 3σ in {d3:.0f} d</b> at 1 µA ({d5:.0f} d for 5σ); {fd(d3_cn)} d on CN at 4 µA.', C['x17'], 24),
    sd.callout(f'MEG II\'s 90 % limit, R = 1.2×10⁻⁵, is crossed at 3σ in {fd(d_meg)} d.', sd.RED, 24),
    sd.callout('Thicker films buy rate but widen the E* spread; the off-resonance points (0.80, 1.225 MeV) are 3–4× slower and test the direct-capture claim.', sd.GREY, 24),
    gap=18, w=500)
D.slide('reach', sd.title('Two weeks at 1 µA, or days on CN, at the ATOMKI ratio',
                          'Days to a 3σ excess in 125–155° per target configuration. Counting only; a template fit is ~1.5× faster. Hover the points.')
        + sd.row(P.svg('days to 3 sigma'), side, gap=40),
        """<p>d = 9·B/S² from the 1-day rows of <code>lnl/out/reach.csv</code> (B and S per day, with the Micromegas cosmic vetoes).
5σ is 25/9 × longer. "γ₁ rejected" sets the 15 MeV IPC leak to 0, which needs real calorimetry (the thick plastics of
<code>../trigger_scint</code>); the n_TOF stack contains ~40 % of the lepton energy and cannot separate 15 from 18 MeV.</p>
<p>Signal counts only the 18.15 resonance and direct capture: R(17.6) is already limited by MEG II (&lt; 1.8×10⁻⁶), so
17.64 MeV captures are pure background. The same R is assumed for direct capture as for the resonance; that is a physics
question, and ATOMKI 2022's I(X17)/I(E1) ≈ 0.4–0.5 suggests it is not smaller.</p>""",
        foot='lnl/out/reach.csv; EPS_REST = 0.14 from the ILL (×2 uncertainty).', short='Reach')

# --------------------------------------------------------------------------- #
# 10 the record
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
    r30 = reach[(reach.scenario == A16) & (reach.I_uA == 1.0) & (reach.days == 30) & (reach.g1_leak == 1.0) & (reach.cosmics == VETO)].R_3sigma.item()
    r30c = reach[(reach.scenario == A16) & (reach.I_uA == 4.0) & (reach.days == 30) & (reach.g1_leak == 0.0) & (reach.cosmics == VETO)].R_3sigma.item()
    marks = [(R_ATOMKI, 'ATOMKI 2016', sd.ORANGE, 0, 'PRL 116, 042501: 6.8σ at 1.10 MeV, m = 16.70 MeV. Hanoi 2024 (≥ 4σ at 1.225 MeV) and ATOMKI 2022 (direct capture) agree.'),
             (R_MEG_181, 'MEG II 90 % CL', sd.RED, 1, 'EPJC 85, 763 (2025): R(18.1) < 1.2×10⁻⁵, no signal; ATOMKI hypothesis p = 6.2 %.'),
             (R_MEG_176, 'MEG II, 17.6 MeV', sd.RED, 0, 'R(17.6) < 1.8×10⁻⁶ (90 % CL). The 441 keV resonance is already excluded at ATOMKI-like strength.'),
             (r30, 'MX17, 30 d, 1 µA', sd.BLUE, 1, f'3σ reach after 30 days, as built, ATOMKI 2016 conditions: R = {r30:.1e}'),
             (r30c, 'MX17, 30 d, CN 4 µA, γ₁ rejected', sd.GREEN, 2, f'3σ reach after 30 days at 4 µA with 15 MeV IPC rejected: R = {r30c:.1e}')]
    for v, lab, col, lvl, tp in marks:
        x = X(v)
        ytop = 230 - 80 * lvl
        o.append(f'<g{sd.tipattr(tp)}>' + sd.line(x, ytop + 14, x, 290, col, 2, '4 4')
                 + f'<circle cx="{x:.1f}" cy="300" r="11" fill="{col}"/>'
                 + sd.T(x, ytop - 8, lab, 23, col, 'middle', 600) + sd.T(x, ytop + 16 - 4, sci(v), 20, col) + '</g>')
    return sd.svg(W, H, ''.join(o), 'X17 ratio: claims, limits and MX17 reach'), r30, r30c


rs, r30, r30c = rec_svg()
D.slide('record', sd.title('A month at 1 µA reaches below the ATOMKI claim',
                           'The X17 ratio R on one log axis: ATOMKI\'s claim, MEG II\'s null, and MX17\'s 3σ reach after 30 days. Hover the points.')
        + rs
        + sd.row(sd.callout('<b>The record is contradictory.</b> ATOMKI (2016, 2022) and Hanoi (2024) see ~140° excesses; MEG II (2025) sees nothing; '
                            'MEG II members (Sept 2026) show cosmics make a 140° bump in ATOMKI-type spectrometers.', sd.ORANGE, 25),
                 sd.callout('<b>What MX17 adds:</b> 15× the pair acceptance, and tracks that veto cosmics. '
                            'LNL\'s own 2023–24 data (unpublished) are the other result to wait for.', sd.BLUE, 25), gap=48),
        """<p>Sources (all in <code>lnl/PHYSICS.md</code>, texts in <code>lnl/refs/</code>): Krasznahorkay <i>et al.</i>, PRL 116, 042501 (2016);
Sas <i>et al.</i>, arXiv:2205.07744 (2022); Tran The Anh <i>et al.</i> (Hanoi, 2024); MEG II, EPJC 85, 763 (2025);
Benmansour <i>et al.</i>, arXiv:2609.18383 (2026); Góngora-Servín <i>et al.</i>, APPB Supp 18, 2-A13 (2025).</p>
<p>The MX17 reach points are counting estimates from <code>lnl/out/reach.csv</code> with EPS_REST = 0.14 (×2).</p>""",
        foot='MX17 points: lnl/out/reach.csv (30-day rows, MM cosmic vetoes).', short='Record')

# --------------------------------------------------------------------------- #
# 11 closing
# --------------------------------------------------------------------------- #
close = (sd.kicker('What this does not settle, and what comes next')
         + '<h2 style="font-size:64px;font-weight:600;line-height:1.1">Good to ×2: Geant4 and two emails close it</h2>'
         + sd.row(
             sd.col(sd.p('Not yet known', 30, sd.DINK, 600),
                    sd.flow([dict(label='EPS_REST = 0.14', sub='trigger × E_sum × reco, carried from the ILL: the ×2', color=sd.DRED,
                                  tip='The ILL G1 ratio of X17 acc × ε (3.8 %) to Micromegas acceptance (27.6 %). Replaced by Geant4 run L1.'),
                             dict(label='15 vs 18 MeV', sub='can the stack separate γ₁ IPC? worth 2.5×', color=sd.DRED,
                                  tip='Geant4 run L2: E_sum response for 15.1 and 18.15 MeV IPC.'),
                             ], dark=True, size=24, arrow=''),
                    sd.flow([dict(label='Cosmics in the LNL hall', sub='overburden, window; ×3', color=sd.DRED),
                             dict(label='Hall space', sub='AN2000 room, CN hall: ~1.5 m apparatus', color=sd.DRED)],
                            dark=True, size=24, arrow=''), gap=16),
             sd.col(sd.p('Next', 30, sd.DINK, 600),
                    sd.flow([dict(label='Geant4 L0–L2', sub='branch lnl from ill_ring: Li target, point vertices, γ lines', color=sd.DBLUE,
                                  tip='lnl/GEANT_PREP.md §2–3. L0 smoke, L1 X17 signal at 18.15 for m = 16.6–17.0, L2 IPC M1/E1 at 18.15, 17.64, 15.1, 14.6.'),
                             dict(label='Email LNL', sub='A. Selva / pacbeams: hall plans, AN2000 vs CN, next PAC', color=sd.DBLUE)],
                            dark=True, size=24, arrow=''),
                    sd.flow([dict(label='Email T. Marchi', sub='LNL 2023–24 ⁸Be data; Góngora-Servín thesis', color=sd.DBLUE),
                             dict(label='Off-resonance', sub='0.80 and 1.225 MeV once 1.04/1.10 works', color=sd.DBLUE)],
                            dark=True, size=24, arrow=''), gap=16),
             gap=64))
D.slide('next', close, """<p>The run plan L0–L6 and the code to write are in <code>lnl/GEANT_PREP.md</code>. The full assumption table, with what
replaces each input, is <code>lnl/ESTIMATES.md</code> §4. Also not modelled: external pair conversion in the chamber and backing,
¹⁹F/¹¹B γ lines, accidentals, and M1–E1 interference in the IPC shape (Gysbers 2023), which moves the large-angle tail by
tens of percent.</p>""", dark=True, short='Next')

out = D.write(O / 'lnl-x17-feasibility.html', note_meta=dict(
    title='LNL ⁸Be feasibility: MX17 on a proton beam',
    summary=f'Could the MX17 apparatus repeat the ATOMKI ⁷Li(p,e⁺e⁻)⁸Be measurement at LNL? 3σ at the ATOMKI ratio in ~{d3:.0f} days at 1 µA (pre-Geant4, ×2).',
    tags='x17, lnl, feasibility', date='2026-10-08'),
    footer='Built by x17_facility_search/lnl/deck/build_deck.py from lnl_rates.py outputs. Pre-Geant4, good to ~×2.')
print(out, f'3sigma {d3:.1f} d, 5sigma {d5:.1f} d, calo {d3c:.1f}/{d5c:.1f}, CN {d3_cn:.1f}, noveto {d3_nov:.1f}, MEG {d_meg:.1f}')
