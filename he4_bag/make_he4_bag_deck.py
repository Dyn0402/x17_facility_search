#!/usr/bin/env python3
"""make_he4_bag_deck.py -- the ⁴He-bag and ³He-leak study as a slide note.

Reads the numbers from he4_bag.py (its functions and out/*.csv), so rerunning
after an assumption changes updates charts and titles together.

    python3 he4_bag/he4_bag.py
    python3 he4_bag/make_he4_bag_deck.py [--out PATH]
    python3 ~/PycharmProjects/dylan-cern-site/scripts/add-note.py PATH --slug ill-he4-bag-3he-leak --force --deploy
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, os.path.expanduser(os.environ.get(
    'SLIDEDOC_DIR', '~/PycharmProjects/dylan-cern-site/scripts')))

import slidedoc as sd                                                  # noqa: E402
from slidedoc import (BLUE, ORANGE, RED, GOLD, PURPLE, GREY, GREEN,     # noqa: E402
                      INK, MUT, RULE, DBLUE, DRED, DGREEN, DMUT)
import he4_bag as H                                                    # noqa: E402

OUT = HERE / 'out'
L_PER_DAY_TO_MBARLS = 1013.25 / 86400          # 1 L(STP)/day in mbar·L/s
WALL_CAPT_G1 = 3.77e-4                          # C1_G1 wall captures per absorbed n (contract_ladders.csv)
BE_WINDOW, AL_RING = 1.4e-4, (1.5e-4, 1.9e-4)   # SIM_STATUS V0
AIR_ALL_C1 = 2.7e-4                             # FEASIBILITY_SIM §2

G = dict(
    bif='Barrier improvement factor: how many times less gas a coated film passes than the bare film.',
    barrer='1 barrer = 10⁻¹⁰ cm³(STP)·cm / (cm²·s·cmHg). Bare PET passes ~1 barrer of He.',
    tau='Time constant: the cell’s ³He inventory divided by its loss rate.',
    cycle='One ILL reactor cycle: 50 days.',
    G1='G1: 1 bar ³He, R 40 mm, L 300 mm, 12 µm mylar wrapped on a 6-rod carbon cage (zero-Δp).',
    G5='G5: 3 bar ³He, R 40 mm, L 100 mm, 0.23 mm Kapton pressure wall.',
    v0='Geant4 V0: 10⁶ unbiased H113 neutrons per cell, ILL branch of MX17_Full_Geant (SIM_STATUS.md).',
    esum='The analysis cut Esum > 13 MeV on the two-arm energy: no single capture except ³He(n,γ) gets there.',
)


def lam_w():
    return H.h113_spectrum()


def per_n(gas, ch, L=H.L_FLIGHT):
    lam, w = lam_w()
    s = H.sigma_per_cm(gas, lam)[ch]
    return float(np.sum(w * (1 - np.exp(-s * L))))


# --------------------------------------------------------------------------- #
def s_cover(D, nd, perm, sk):
    air = nd.iloc[0]
    g1 = perm[1.0].set_index('id').loc['G1']
    lam = sk.set_index('skin').loc['12 µm PET + 9 µm Al foil laminate']
    bare = sk.set_index('skin').loc['12 µm PET, bare (G1 as simulated)']
    dth = 100 * (lam.theta0_6p3MeV_deg / bare.theta0_6p3MeV_deg - 1)
    nums = ''.join([
        sd.bignum(f'{0.9 * 100:.0f} %', 'of the air ¹⁴N(n,γ) is the beam’s 30 cm air path', DRED,
                  'A He flight tube removes it. A balloon around the target buys almost nothing more.',
                  tip=f'Analytic {air["14N(n,g) per n, 30 cm"]:.2e}/n on the 30 cm path vs Geant4 V0 2.5e-4; '
                      f'all air in C1: 2.7e-4/n.'),
        sd.bignum(f'{g1.he3_loss_L_per_cycle:.0f} L', '³He lost per cycle through bare 12 µm mylar', '#f0a36b',
                  f'τ = {g1.tau_he3_days:.1f} days, ~{g1.he3_cost_eur_per_cycle / 1e3:.0f} k€ per cycle at '
                  f'{H.HE3_EUR_PER_L:.0f} €/L.', tip=G['G1'] + '\nPET He permeability ≈ 1 barrer, uncertain ~2×.'),
        sd.bignum(f'+{dth:.0f} %', 'scattering for a 9 µm Al-foil laminate skin', DGREEN,
                  f'Loss falls to ~{lam.loss_hi_L * 1e3:.0f} cm³ per cycle, set by the O-rings. '
                  'Still 1 bar, still no pressure wall.',
                  tip='Highland θ0 at 6.3 MeV, G1 skin + Micromegas entrance + 16 cm air.')])
    body = (sd.kicker('ILL X17 search · ³He target · analytic, calibrated on the Geant4 campaign · 2 Oct 2026')
            + '<h1 style="font-size:80px;font-weight:600;line-height:1.08;letter-spacing:-2px;width:1640px">'
              'Put the beam path in helium, not the target, and give the 1 bar cell a metal-foil skin</h1>'
            + '<div style="flex:1"></div>'
            + f'<div style="display:flex;gap:64px">{nums}</div>')
    D.slide('cover', body, '''
<p>Two questions. (1) Air ¹⁴N is a significant background at the ILL: would a ⁴He balloon around the ³He target remove it, and what would it do to lepton scattering and to ³He diffusion? (2) The ³He leak rate of the zero-Δp mylar cell turned out to be large: how do we make the cell tight without adding background or scattering, and does that mean staying at atmospheric pressure?</p>
<p>Answers. (1) ⁴He captures no neutrons, but the air that matters is the open beam path upstream of the cell, so a He-filled (or evacuated) flight tube does the job; a balloon around the cell adds little and makes the ³He problem worse. (2) Yes, stay at 1 bar, but the reason is that a skin that carries no load can be chosen purely as a barrier. A thin rolled-Al-foil laminate is impermeable to helium and costs a few per cent in scattering and nothing in background.</p>
<p>Everything here is analytic (<code>he4_bag/he4_bag.py</code>), calibrated against the ILL Geant4 campaign where it has a number. The analytic ¹⁴N(n,γ) rate on the air path reproduces Geant4 V0 to 1 %.</p>''',
            dark=True, short='Answer')


def s_setup(D, nd, perm):
    air = nd.iloc[0]
    g1 = perm[1.0].set_index('id').loc['G1']
    W, Hh = 1040, 640
    yc = 300
    o = []
    # collimator
    o.append(f'<rect x="20" y="{yc - 120}" width="60" height="95" fill="#9aa3b2"'
             f'{sd.tipattr("Collimator / guide exit with the aperture. The beam leaves it into open air.")}/>')
    o.append(f'<rect x="20" y="{yc + 25}" width="60" height="95" fill="#9aa3b2"/>')
    o.append(sd.T(50, yc + 150, 'aperture', 20, MUT))
    # air path
    x_air0, x_w = 80, 380
    an = air['14N(n,g) per n, 30 cm']
    air_tip = (f'300 mm of open air between the aperture and the Be window. ¹⁴N(n,γ): {an:.2e}/n analytic, '
               '2.5e-4 Geant4. ¹⁴N(n,p): 0.6 %. Scattered: ~2 %.')
    o.append(f'<rect x="{x_air0}" y="{yc - 25}" width="{x_w - x_air0}" height="50" fill="{RED}" fill-opacity="0.16" '
             f'stroke="{RED}" stroke-dasharray="6 5"{sd.tipattr(air_tip)}/>')
    o.append(sd.arrow(90, yc, x_w + 30, yc, BLUE, 4, 16))
    o.append(sd.T((x_air0 + x_w) / 2, yc - 44, '30 cm open air', 24, RED, weight=600))
    o.append(sd.T((x_air0 + x_w) / 2, yc + 62, '¹⁴N(n,γ) 10.8 MeV γ', 21, RED))
    o.append(sd.T((x_air0 + x_w) / 2, yc + 88, '→ He flight tube', 21, GREEN, weight=600,
                  tip='Proposed: a tube from the aperture to the Be window, He-filled (or evacuated), '
                      'sealed onto the cell flange. Mylar entrance window, not Kapton (Kapton has N).'))
    # cell
    x_c1 = x_w + 420
    o.append(f'<rect x="{x_w}" y="{yc - 55}" width="{x_c1 - x_w}" height="110" rx="6" fill="#e9eef6" '
             f'stroke="{ORANGE}" stroke-width="3"{sd.tipattr(G["G1"])}/>')
    o.append(f'<rect x="{x_w - 6}" y="{yc - 60}" width="8" height="120" fill="{GREY}"'
             f'{sd.tipattr("Be window, 0.5 mm. Captures 1.4e-4/n (6.8 MeV), whatever gas is upstream.")}/>')
    o.append(f'<rect x="{x_c1}" y="{yc - 60}" width="14" height="120" fill="{GREY}"'
             f'{sd.tipattr("Al end cap, 8 mm, with the ⁶LiF layer.")}/>')
    xs = np.linspace(x_w + 10, x_w + 300, 60)
    o.append(f'<polygon points="{x_w},{yc - 18} {x_w + 90},{yc - 30} {x_w + 330},{yc - 50} '
             f'{x_w + 330},{yc + 50} {x_w + 90},{yc + 30} {x_w},{yc + 18}" fill="{BLUE}" fill-opacity="0.18"/>')
    o.append(sd.T(x_w + 210, yc + 8, '³He, 1 bar', 24, INK, weight=600))
    # permeation arrows
    for xx in (x_w + 110, x_w + 260):
        o.append(sd.arrow(xx, yc - 58, xx, yc - 108, ORANGE, 3.5, 13))
        o.append(sd.arrow(xx, yc + 58, xx, yc + 108, ORANGE, 3.5, 13))
    tipp = f'Fick: J = P·p(³He)·A/t. Bare 12 µm PET, 754 cm²: {g1.he3_loss_L_per_day:.2f} L/day.'
    o.append(sd.T(x_w + 185, yc - 122, '³He permeates the 12 µm skin', 22, ORANGE, weight=600, tip=tipp))
    # detector arms
    for y in (yc - 250, yc + 215):
        o.append(f'<rect x="{x_w - 60}" y="{y}" width="{x_c1 - x_w + 120}" height="36" fill="#d9d4c8"'
                 f'{sd.tipattr("Micromegas + plastic/LS arm at ~22 cm from the axis (two of four shown).")}/>')
    o.append(sd.T(x_c1 + 75, yc - 258, 'Micromegas arms', 21, MUT, 'end'))
    o.append(sd.T(x_c1 + 40, yc - 175, '16 cm air', 21, MUT, 'end',
                  tip='Cell → Micromegas entrance. Scattered neutrons are captured here too: ~10 % of the air '
                      '¹⁴N(n,γ). Leptons scatter in it: ~1/3 of the X0 on the chord.'))
    schem = sd.svg(W, Hh, ''.join(o), 'ILL cell, air path and detector, side view')
    right = sd.col(
        sd.p('<b>Two problems with one cell.</b>', 28),
        sd.callout(f'<b>Air ¹⁴N</b> makes the hardest single-capture line present, 10.83 MeV. Where is the air '
                   'that matters, and does ⁴He fix it?', RED, 26),
        sd.callout(f'<b>³He leaks</b> through the {sd.term("zero-Δp", G["G1"])} 12 µm mylar skin. How fast, and '
                   'what skin stops it without adding scattering or capture lines?', ORANGE, 26),
        sd.p(f'Hover the {sd.term("dotted terms", "Like this one. Chart points and bars work the same way.")}, '
             'the drawing and the chart points for numbers and sources.', 23, MUT),
        gap=24, w=560)
    body = sd.title('The setup: a 1 bar ³He cell behind 30 cm of open air',
                    'Side view, not to scale. Beam from the left (H113 / PF1B, mean λ 4.9 Å); two of the four detector arms.')
    body += sd.row(schem, right, gap=56)
    D.slide('setup', body, '''
<p>The cell is G1 from the ILL campaign (<code>ill/HANDOFF_SIM.md</code> §4): 1 bar ³He, R = 40 mm, 300 mm long, a 12 µm mylar sheet wrapped on a six-rod carbon cage, a 0.5 mm Be entrance window and an 8 mm Al end cap. The mylar carries no pressure, so it is a gas barrier only. The Geant4 world is air, and the collimator aperture sits 300 mm upstream of the window.</p>
<p>The other cells (G2–G6) appear where they matter: G3/G5 are the 2 and 3 bar Kapton pressure-wall alternatives.</p>''',
            short='Setup')


def s_air(D, nd):
    air = nd.iloc[0]
    an = air['14N(n,g) per n, 30 cm']
    rows = [
        ('air path, Geant4', 2.5e-4, RED, G['v0'] + '\n300 mm aperture → Be window.'),
        ('air path, analytic', an, RED, f'{an:.3e}/n: thermal σ(n,γ) = 79.8 mb × λ/1.8 Å, H113 spectrum, 30 cm.'),
        ('air elsewhere', AIR_ALL_C1 - 2.5e-4, '#e3a0a8',
         'Inferred: all air in C1 (2.7e-4/n) minus the air path (V0). Scattered neutrons captured around the detector.'),
        ('Al ring', np.mean(AL_RING), GREY, 'Upstream Al ring, 1.5–1.9e-4/n (V0, by cell). Lines ≤ 7.7 MeV.'),
        ('Be window', BE_WINDOW, GREY, '0.5 mm Be, 1.4e-4/n (V0). Ground-state line 6.8 MeV.'),
    ]
    bars = sd.hbars([(a, b, c, t) for a, b, c, t in rows], 4e-4, width=560, log=True, vmin=1e-6, h=44,
                    label_w=260, fmt=lambda v: sd.sci(v, 1) + '/n', size=26)
    right = sd.col(
        sd.callout(f'The analytic rate on the 30 cm path is {sd.sci(an, 2)}/n; Geant4 gives 2.5×10⁻⁴. '
                   f'Ratio {an / 2.5e-4:.2f}.', BLUE, 26),
        sd.callout('So ~90 % of the air ¹⁴N(n,γ) is the <b>direct beam</b> crossing open air, not scattered '
                   'neutrons around the detector.', RED, 26),
        sd.callout(f'¹⁴N is the hardest single line present (10.83 MeV); Be and Al stay ≤ 7.7 MeV, '
                   f'below the {sd.term("Esum cut", G["esum"])} with margin.', GREY, 26),
        gap=26, w=620)
    body = sd.title('~90 % of the air ¹⁴N(n,γ) is the beam’s 30 cm air path',
                    'Radiative captures per beam neutron near the cell, by source (log scale). G1–G5, ILL Geant4.')
    body += sd.row(sd.col(bars, w=980), right, gap=60, align='center')
    D.slide('air', body, '''
<p>The ILL Geant4 V0 validation (10⁶ unbiased neutrons per cell) tallied the 300 mm air path at 2.5×10⁻⁴ ¹⁴N(n,γ) per neutron, plus 0.6 % ¹⁴N(n,p) and ~2 % scattering. The C1 contract runs give 2.7×10⁻⁴/n for all air. The difference, ~2×10⁻⁵, is the air around the detector capturing scattered neutrons. That split comes from two different runs and was not tallied directly.</p>
<p>Analytic check: the H113 particle-flux spectrum (mean λ 4.87 Å), ¹⁴N σ(n,γ) = 79.8 mb and σ(n,p) = 1.83 b at 2200 m/s scaled as 1/v, 2 N per molecule, 0.781 N₂ in air at 20 °C. It gives 2.54×10⁻⁴ (n,γ) and 5.8×10⁻³ (n,p), i.e. 1.01 and 0.97 of Geant4.</p>
<p>Why this line matters: in <code>ill/FEASIBILITY_SIM.md</code> §4 the single-neutron fakes are capped by the hardest capture line, ¹⁴N at 10.83 MeV, and Esum > 13 MeV sits only ~3.5σ above it. It is also the strongest single source of hard singles for accidentals.</p>''',
            foot='Sources: SIM_STATUS.md (V0), FEASIBILITY_SIM.md §2 (C1 air total), he4_bag.py §1.', short='Where the air is')


def s_purity(D):
    fr = np.logspace(-4, 0, 41)
    P = sd.Plot(1040, 640, x=(1e-4, 1, 'log'), y=(1e-8, 1e-1, 'log'),
                xlabel='air fraction left in the He flight tube', ylabel='per beam neutron, 30 cm path')
    P.xticks([(1e-4, '0.01 %'), (1e-3, '0.1 %'), (1e-2, '1 %'), (1e-1, '10 %'), (1, 'air')])
    P.yticks(sd.log_ticks(-8, -1))
    series = [('14N(n,g)', '¹⁴N(n,γ) 10.8 MeV', RED, None), ('14N(n,p)', '¹⁴N(n,p) beam loss', ORANGE, '10 7'),
              ('scatter', 'scattered out of the beam', BLUE, '4 6')]
    for ch, lab, c, dash in series:
        ys = [per_n(H.bag_gas(f), ch) for f in fr]
        tips = [f'{lab}\nair {100 * f:.2g} %\n{y:.2e} per n' for f, y in zip(fr, ys)]
        P.line(list(fr), ys, c, 4, dash, markers=False, tips=None, tip=lab)
        P.points(list(fr[::5]), ys[::5], c, r=7, tips=tips[::5])
    P.hline(BE_WINDOW, GREY, '8 6', 2, label='Be window captures (any gas)', anchor='start',
            tip='1.4e-4/n, 6.8 MeV: independent of the gas upstream.')
    y1 = per_n(H.bag_gas(0.01), '14N(n,g)')
    P.points([0.01], [y1], RED, r=11, marker='open',
             tips=[f'1 % air: {y1:.1e}/n, ×{2.54e-4 / y1:.0f} below open air'])
    leg = sd.legend([(l, c, 'dash' if d else 'line') for _ch, l, c, d in series], 22)
    pure = per_n(H.bag_gas(0), 'scatter')
    right = sd.col(
        sd.callout('<b>⁴He captures nothing</b>: there is no bound ⁵He. The ¹⁴N terms fall in proportion '
                   'to the air left in the tube.', GREEN, 26),
        sd.callout(f'At 1 % air: ¹⁴N(n,γ) {sd.sci(y1, 1)}/n, ×{2.54e-4 / y1:.0f} down. A flushed bag holds this easily.',
                   RED, 26),
        sd.callout(f'Pure ⁴He still scatters {100 * pure:.2f} % of the beam (free-gas σ), against 1.6 % for air.',
                   BLUE, 26),
        sd.callout('An evacuated tube does the same job; He needs no pressure-bearing windows.', GREY, 24),
        gap=22, w=580)
    body = sd.title('A 99 % clean He flight tube cuts the ¹⁴N ×100',
                    'Analytic, H113 spectrum, 30 cm path, 20 °C, 1 atm.')
    body += sd.row(sd.col(P.svg('purity'), leg, gap=8, w=1040), right, gap=44)
    D.slide('purity', body, '''
<p>Cross sections (Sears / NIST thermal values): ¹⁴N (n,γ) 79.8 mb, (n,p) 1.83 b, bound scattering 11.5 b; O 4.23 b; Ar (n,γ) 0.675 b; ⁴He scattering 1.34 b, absorption 0. Absorption scales as 1/v. Scattering uses the free-atom cross section (σ_bound·(A/(A+1))², with the molecular mass for N₂ and O₂) times the free-gas factor for a cold neutron on a 20 °C gas, which is 1.1–1.8 (largest for the light, fast He atoms).</p>
<p>The air scattering comes out at 1.6 % against ~2 % in Geant4, which uses its own thermal treatment. The ⁴He scattering is ~13× lower.</p>
<p>Design notes: seal the tube onto the cell flange so the Be window is its downstream end (no extra window). Use a thin mylar (PET) entrance window: Kapton contains nitrogen.</p>''',
            foot='he4_bag.py §1. Points carry values; the open circle is the 1 % working point.', short='He purity')


def s_balloon(D, lep):
    P = sd.Plot(860, 600, x=(3, 14, 'lin'), y=(0, 6, 'lin'),
                xlabel='lepton kinetic energy [MeV]', ylabel='Highland θ₀ per leg [deg]')
    P.xticks([(v, str(v)) for v in (4, 6, 8, 10, 12, 14)]).yticks([(v, str(v)) for v in range(0, 7)])
    cols = list(lep.columns[1:])
    cc = [RED, GREEN, BLUE, GREY]
    dd = [None, None, '10 7', '4 6']
    for c, col_, dash in zip(cols, cc, dd):
        tips = [f'{c}\n{k} MeV: {v:.2f}°' for k, v in zip(lep['KE [MeV]'], lep[c])]
        P.line(list(lep['KE [MeV]']), list(lep[c]), col_, 4, dash, tips=tips)
    leg = sd.legend([(c, col_, 'dash' if d else 'line') for c, col_, d in zip(cols, cc, dd)], 21)
    gain = 100 * (1 - lep[cols[1]].iloc[1] / lep[cols[0]].iloc[1])
    right = sd.col(
        sd.p('<b>What a balloon around the cell would add</b>', 27),
        sd.callout(f'The remaining ~10 % of the air ¹⁴N(n,γ).<br>~{gain:.0f} % less lepton scattering, worth '
                   f'{sd.term("< 2 % in reach", "Ideal vertexing gains only 13 % (FEASIBILITY_SIM §1): the resolution is set by the assumed vertex (7.8° vs 2.2°), not by scattering.")}.',
                   GREEN, 25),
        sd.p('<b>What it would cost</b>', 27),
        sd.callout('⁴He floods the mylar cell (next slides).<br>He permeates the Micromegas entrance windows into '
                   'their gas and shifts the gain.<br>HV breaks down far more easily in He than in air.', RED, 25),
        gap=18, w=700)
    body = sd.title('A target balloon buys scattering the reach doesn’t need',
                    f'−{gain:.0f} % in Highland θ₀. G1 skin + Micromegas entrance (40 µm mylar, 50 µm Kapton, 9 µm Cu) + 16 cm gas.')
    body += sd.row(sd.col(P.svg('scattering'), leg, gap=8, w=860), right, gap=60)
    D.slide('balloon', body, '''
<p>Radiation lengths: air 304 m, ⁴He 5.7 km at 1 atm, so 16 cm of air is 5.3×10⁻⁴ X₀ against 2.8×10⁻⁵ for He. The Micromegas entrance is 9.4×10⁻⁴ X₀ and dominates. Energies: 4.1 / 6.3 / 9.1 MeV are the p10/50/90 of the softer accepted X17 lepton, 13.3 MeV the median of the harder one (FEASIBILITY_SIM §1).</p>
<p>The best case seals the bag directly onto the Micromegas entrance windows, so no foil is added. A separate 25 µm mylar balloon gives back a quarter of the gain; 100 µm gives back most of it.</p>
<p>The cost side is qualitative: He permeation through the 40 µm Micromegas mylar would be estimated the same way as the cell (next slides) once the window area and gas flow are known.</p>''',
            short='Balloon: scattering')


def s_inflow(D, perm):
    g1 = perm[1.0].set_index('id').loc['G1']
    q3, q4, qa = g1.he3_loss_L_per_day, g1.he4_in_L_per_day_bag, g1.air_in_L_per_day
    W, Hh = 1100, 600
    o = []
    for k, (cx, envlab, inlab, qin, cin) in enumerate([
            (270, 'cell in air', 'N₂ + O₂ in', qa, GREY), (830, 'cell in a ⁴He bag', '⁴He in', q4, PURPLE)]):
        bg = '#f3efe6' if k == 0 else '#efe9f7'
        o.append(f'<rect x="{cx - 260}" y="40" width="520" height="520" rx="20" fill="{bg}" stroke="{RULE}"/>')
        o.append(sd.T(cx, 82, envlab, 28, INK, weight=600))
        o.append(f'<circle cx="{cx}" cy="320" r="120" fill="#e9eef6" stroke="{ORANGE}" stroke-width="4"/>')
        o.append(sd.T(cx, 328, '³He', 30, INK, weight=600))
        o.append(sd.arrow(cx + 100, 250, cx + 210, 170, ORANGE, 5, 16))
        o.append(sd.T(cx + 140, 152, f'³He out {q3:.2f} L/d', 23, ORANGE, 'middle', 600,
                      tip=f'Driven by the ³He partial pressure, ~0 outside in both cases. G1 bare: {q3:.3f} L/day.'))
        w_ar = 2 + 10 * min(qin / q3, 1)
        o.append(sd.arrow(cx - 220, 480, cx - 95, 400, cin, w_ar, 18))
        o.append(sd.T(cx - 120, 525, f'{inlab} {qin:.3f} L/d', 23, cin, 'middle', 600,
                      tip=('N₂ 0.006 and O₂ 0.03 barrer through PET, at their partial pressures in air.'
                           if k == 0 else '⁴He at 1 bar outside, ~0 inside: about the ³He rate (³He assumed 10 % faster).')))
    schem = sd.svg(W, Hh, ''.join(o), 'flows in and out of the G1 cell')
    right = sd.col(
        sd.callout('<b>³He out: unchanged.</b> It follows the ³He partial pressure, ~0 outside in air and in ⁴He alike.',
                   ORANGE, 25),
        sd.callout(f'<b>What comes in changes ×{q4 / qa:.0f}.</b> In air the cell would deflate; in the bag ⁴He replaces '
                   'the ³He, the pressure holds, and the ³He is diluted.', PURPLE, 25),
        sd.callout('Holding ⁴He &lt; 5 % in G1 means flushing ~8 L/day of fresh ³He, out into a ³He/⁴He mix '
                   'that needs isotope separation.', RED, 25),
        gap=22, w=520)
    body = sd.title('In a ⁴He bag ³He leaks just as fast, and ⁴He floods in',
                    f'Bare 12 µm mylar, {sd.term("G1", G["G1"])}, Fick’s law per species, barrel area only. ⁴He enters ×{q4 / qa:.0f} faster than air.')
    body += sd.row(schem, right, gap=40, align='center')
    D.slide('inflow', body, '''
<p>Each gas permeates on its own partial-pressure difference. Permeabilities (DuPont Mylar sheet, Polymer Handbook): He ~1 barrer (0.6–1.3), O₂ 0.03, N₂ 0.006. ³He is taken 10 % faster than ⁴He (roughly √(4/3) in diffusivity; unmeasured for these films).</p>
<p>In air, a sealed zero-Δp cell loses ³He and takes in only ~1/90 of that volume of air, so it collapses; it needs a ³He feed at the loss rate. Over a sealed cycle the N₂ that does enter makes ~6 % of the cell gas and 2×10⁻⁶/n of in-cell ¹⁴N(n,γ), which is negligible.</p>
<p>In the bag the cell stays inflated, but the ³He partial pressure falls with τ = 3.4 days and the stopping length grows as 1/p(³He). Fresh-³He flush to hold ⁴He below 5 %: G1 8 L/day, G3 0.44, G5 0.14 (<code>out/he4_flush_bif1.csv</code>). The permeated ³He ends up in the bag instead of the hall, but at &lt; 1 % in a flowing bag it is not practically recoverable.</p>''',
            short='Balloon: inflow')


def s_leak(D, perm):
    p1 = perm[1.0].set_index('id')
    p10 = perm[10.0].set_index('id')
    t = np.linspace(0, H.CYCLE_D, 51)
    P = sd.Plot(900, 600, x=(0, 50, 'lin'), y=(0, 1.02, 'lin'),
                xlabel='days, sealed cell', ylabel='fraction of the ³He left')
    P.xticks([(v, str(v)) for v in range(0, 51, 10)]).yticks([(v / 4, f'{25 * v}%') for v in range(5)])
    for cid, bif, c, dash in [('G1', 1.0, BLUE, None), ('G1', 10.0, BLUE, '10 7'),
                              ('G3', 1.0, PURPLE, None), ('G5', 1.0, ORANGE, None), ('G5', 10.0, ORANGE, '10 7')]:
        tau = (p1 if bif == 1 else p10).loc[cid].tau_he3_days
        ys = np.exp(-t / tau)
        lab = f'{cid} {"bare" if bif == 1 else "BIF 10"}'
        tips = [f'{lab}, τ = {tau:.1f} d\nday {d:.0f}: {100 * y:.0f} %' for d, y in zip(t, ys)]
        P.line(list(t), list(ys), c, 4, dash, markers=False, tip=f'{lab}: τ = {tau:.1f} days')
        P.points(list(t[::10]), list(ys[::10]), c, r=6, tips=tips[::10])
    leg = sd.legend([('G1 bare', BLUE), ('G1 BIF 10', BLUE, 'dash'), ('G3 bare', PURPLE),
                     ('G5 bare', ORANGE), ('G5 BIF 10', ORANGE, 'dash')], 21)
    rows = []
    for cid in p1.index:
        r = p1.loc[cid]
        tip = (f'{cid}: {r.he3_barL:.1f} bar·L ³He, {r.wall} {r.t_um:.0f} µm\n'
               f'{r.he3_loss_L_per_day:.3f} L/day, τ = {r.tau_he3_days:.1f} d\n'
               f'~{r.he3_cost_eur_per_cycle / 1e3:.1f} k€/cycle at {H.HE3_EUR_PER_L:.0f} €/L\n'
               f'BIF 10: {p10.loc[cid].he3_loss_L_per_cycle:.2f} L/cycle')
        rows.append((cid, r.he3_loss_L_per_cycle, ORANGE if r.wall == 'kapton' else BLUE, tip))
    bars = sd.hbars(rows, 60, width=380, log=True, vmin=0.1, label_w=70, fmt=lambda v: f'{v:.1f} L', size=25)
    g1 = p1.loc['G1']
    body = sd.title(f'Bare 12 µm mylar: G1 loses {g1.he3_loss_L_per_day:.2f} L of ³He a day',
                    f'τ = {g1.tau_he3_days:.1f} days. Fick’s law, He 1 {sd.term("barrer", G["barrer"])} in PET and (placeholder) Kapton; '
                    f'{sd.term("BIF", G["bif"])} = metallisation factor.')
    right = sd.col(sd.p(f'<b>³He lost per {sd.term("cycle", G["cycle"])}</b>, bare film, log scale', 25),
                   bars,
                   sd.callout(f'G1: ~{g1.he3_cost_eur_per_cycle / 1e3:.0f} k€ of ³He a cycle, or a measured '
                              '≳ 10× barrier from the aluminising.', RED, 24),
                   gap=18, w=640)
    body += sd.row(sd.col(P.svg('3He left'), leg, gap=8, w=900), right, gap=60)
    D.slide('leak', body, '''
<p>Barrel only: the Be window and the Al cap do not pass helium; seals and bonds are on a later slide. G1 has 754 cm² of 12 µm film around 1.5 bar·L of ³He, which is the worst possible ratio of area/thickness to inventory. The Kapton cells are 10–20× thicker and hold their inventory at higher pressure in a shorter cell.</p>
<p>The PET number is a literature value, uncertain by ~2×. The Kapton value is a placeholder: sources disagree by 10× (0.2–2.5 barrer). The vapour-deposited aluminium on the mylar (2 × 40 nm) has an unmeasured He barrier factor. Experience with foil party balloons (metallised nylon, which lose their He in one to three weeks) suggests it is a few, not hundreds.</p>
<p>The sealed-cell curves are shown for intuition. In practice the cell is regulated (fed at the loss rate) and what matters is the loss per cycle on the right. ³He price: 2500 €/L(STP) is an order of magnitude; the market has been 2–5 k$/L.</p>''',
            foot='he4_bag.py §3, out/permeation_bif1.csv and _bif10.csv.', short='³He leak')


def s_options(D, sk):
    P = sd.Plot(1060, 660, x=(1e-5, 2e-3, 'log'), y=(1e-3, 100, 'log'),
                xlabel='skin thickness x/X₀', ylabel='³He lost per cycle [L STP]')
    P.xticks([(1e-5, '10⁻⁵'), (1e-4, '10⁻⁴'), (1e-3, '10⁻³')]).yticks(sd.log_ticks(-3, 2))
    # Kapton pressure walls: t = (p-1) R / σ, same 1.5 bar·L
    ps = np.linspace(1.25, 6, 40)
    kx, ky, ktips = [], [], []
    for pb in ps:
        t = (pb - 1) * 0.1 * 40 / 35 / 10                  # cm
        a = 2 * np.pi * 4.0 * 30 / pb
        loss = H._loss_per_cycle(a / t, 1.0, pb)
        kx.append(t / H.X0['kapton'])
        ky.append(loss)
    P.line(kx, ky, ORANGE, 3.5, '10 7', markers=False,
           tip='Kapton pressure walls, p = 1.25–6 bar: t = Δp·R/σ (σ 35 MPa), 1.5 bar·L. loss × x/X₀ is constant.')
    for pb in (1.5, 5):
        t = (pb - 1) * 0.1 * 40 / 35 / 10
        P.text(t / H.X0['kapton'] * 1.1, H._loss_per_cycle(2 * np.pi * 4 * 30 / pb / t, 1.0, pb) * 0.45,
               f'{pb:g} bar', 20, ORANGE, 'start')
    # PET thickness family
    tt = np.logspace(np.log10(6e-4), np.log10(5e-2), 30)
    a1 = 2 * np.pi * 4 * 30
    P.line(list(tt / H.X0['PET']), [H._loss_per_cycle(a1 / t, 1.0, 1.0) for t in tt], BLUE, 3, '4 6',
           markers=False, tip='Bare PET at 1 bar, 6–500 µm: loss ∝ 1/t, x/X₀ ∝ t.')
    seal = sk.loss_lo_L.min()
    P.hline(seal, GREY, '8 6', 2, label='seal floor: Viton O-rings', anchor='start', where='below',
            tip=f'{seal * 1e3:.1f} cm³/cycle through the two Viton face seals (Be window, Al cap). Metal seals go lower.')
    colours = [BLUE, BLUE, BLUE, GREEN, GREEN, PURPLE, ORANGE]
    for (_, r), c in zip(sk.iterrows(), colours):
        y = np.sqrt(r.loss_lo_L * r.loss_hi_L)
        tip = (f'{r.skin}\nx/X₀ = {r.x_X0:.2e}\nloss {r.loss_lo_L:.3g}–{r.loss_hi_L:.3g} L/cycle\n'
               f'θ₀(6.3 MeV) {r.theta0_6p3MeV_deg:.2f}°\n{r.note}')
        if r.loss_hi_L / r.loss_lo_L > 1.5 and r.loss_hi_L > 0.1:
            P.raw(sd.line(P.X(r.x_X0), P.Y(r.loss_lo_L), P.X(r.x_X0), P.Y(r.loss_hi_L), c, 5))
            y = r.loss_hi_L
        P.points([r.x_X0], [y], c, r=11, tips=[tip], marker='open' if 'Al foil' in r.skin else 'circle')
    labels = {'12 µm PET, bare (G1 as simulated)': ('G1 bare', 1.25, 1.0, 'start'),
              '12 µm PET, double-aluminised': ('aluminised', 0.8, 0.25, 'end'),
              '50 µm PET': ('50 µm PET', 0.8, 2.6, 'end'),
              '12 µm PET + 9 µm Al foil laminate': ('+ 9 µm Al foil', 1.0, 3.0, 'middle'),
              '12 µm PET + 25 µm Al foil laminate': ('+ 25 µm', 1.0, 3.0, 'middle'),
              'G3: 0.11 mm Kapton, 2 bar': ('G3 (2 bar)', 1.1, 1.9, 'start'),
              'G5: 0.23 mm Kapton, 3 bar': ('G5 (3 bar)', 0.85, 0.45, 'end')}
    for (_, r), c in zip(sk.iterrows(), colours):
        lab, fx, fy, an = labels[r.skin]
        y = r.loss_hi_L if r.loss_hi_L > 0.1 else r.loss_lo_L
        P.text(r.x_X0 * fx, y * fy, lab, 21, c, an, 600)
    leg = sd.legend([('Kapton pressure wall vs p', ORANGE, 'dash'), ('bare PET vs thickness', BLUE, 'dash'),
                     ('Al-foil laminate (open)', GREEN, 'dot')], 21)
    lam = sk.set_index('skin').loc['12 µm PET + 9 µm Al foil laminate']
    right = sd.col(
        sd.callout('<b>Permeation follows the ³He pressure, not the wall load.</b> Going to 2–3 bar does not help '
                   'by itself: the wall must thicken, and every polymer wall sits on loss × x/X₀ ≈ constant.',
                   ORANGE, 24),
        sd.callout('<b>So stay at 1 bar</b>, but because a skin that carries no load can be chosen purely as a '
                   '<b>barrier</b>.', BLUE, 24),
        sd.callout(f'<b>Rolled Al foil is impermeable to He.</b> 12 µm PET + 9 µm Al: x/X₀ {sd.sci(lam.x_X0, 1)}, '
                   f'loss ~{lam.loss_hi_L * 1e3:.0f} cm³/cycle, all of it at the O-rings.', GREEN, 24),
        gap=20, w=560)
    body = sd.title('At 1 bar a metal-foil skin beats any polymer wall >100×',
                    '³He loss per 50-day cycle vs skin radiation length. 1.5 bar·L of ³He, R 40 mm. Bars: BIF range.')
    body += sd.row(sd.col(P.svg('loss vs thickness'), leg, gap=6, w=1060), right, gap=44)
    D.slide('options', body, '''
<p>Why pressure does not buy tightness: the flux through a wall is J = P·p₃·A/t, with p₃ the ³He partial pressure. A pressure wall needs t = Δp·R/σ. At fixed inventory (bar·L) the barrel area goes as 1/p, so the loss goes as 1/(p − 1) while x/X₀ goes as (p − 1). Their product is fixed by the material (permeability × radiation length / strength). Thin bare PET follows the same rule (loss ∝ 1/t, x ∝ t). A polymer at any pressure cannot get off its line.</p>
<p>A metal foil is not a polymer: helium does not dissolve in or diffuse through a sound metal lattice at room temperature (which is why He leak detection works). A rolled Al foil laminated to the mylar leaks only at pinholes. At 9 µm, typical foil has tens of pinholes per m², each fed through the 12 µm PET by a spreading conductance ~4a (a ≈ 5 µm). Even with 100× more from creasing on the rods, the barrel passes &lt; 10⁻⁴ L per cycle (<code>out/seals.csv</code>). ≥ 25 µm foil is pinhole-free in practice.</p>
<p>Vapour-deposited aluminium (40 nm) is a different thing: it is full of nanoscale defects and its He barrier factor is small and unmeasured (the 1–10 bar on the plot). Other coatings worth a bench test: ALD Al₂O₃ on PET, or a SiOx barrier film; their He factors are not known to us.</p>''',
            short='Skin options')


def s_cost(D, sk):
    s = sk.set_index('skin')
    order = ['12 µm PET, bare (G1 as simulated)', '12 µm PET + 9 µm Al foil laminate',
             '12 µm PET + 25 µm Al foil laminate', '50 µm PET', 'G3: 0.11 mm Kapton, 2 bar',
             'G5: 0.23 mm Kapton, 3 bar']
    short = {order[0]: 'G1 bare PET', order[1]: '+ 9 µm Al', order[2]: '+ 25 µm Al', order[3]: '50 µm PET',
             order[4]: 'G3 Kapton', order[5]: 'G5 Kapton'}
    col_ = {order[0]: BLUE, order[1]: GREEN, order[2]: GREEN, order[3]: BLUE, order[4]: PURPLE, order[5]: ORANGE}
    base = H.highland(np.sqrt((6.3 + H.ME) ** 2 - H.ME ** 2),
                      sum(t / H.X0[m] for m, t in H.MM_ENTRANCE) + H.L_CHORD_AIR / H.X0['air'])
    th = [(short[k], s.loc[k].theta0_6p3MeV_deg, col_[k],
           f'{k}\nθ₀ = {s.loc[k].theta0_6p3MeV_deg:.2f}° (no skin: {base:.2f}°)\nx/X₀ {s.loc[k].x_X0:.2e}')
          for k in order]
    cap = [(short[k], s.loc[k].barrel_captures_per_n, col_[k],
            f'{k}\n{s.loc[k].barrel_captures_per_n:.1e} captures per beam n in the barrel\n'
            f'hardest line {s.loc[k].gamma_max_MeV:.2f} MeV') for k in order]
    cap.append(('all cell walls', WALL_CAPT_G1, GREY,
                'C1_G1 Geant4: all cell-solid captures per absorbed n (Be window, Al ring and cap, LiF, skin).'))
    b1 = sd.hbars(th, 4.4, width=360, label_w=200, h=44, fmt=lambda v: f'{v:.2f}°', size=26)
    b2 = sd.hbars(cap, 1e-3, width=360, log=True, vmin=1e-9, label_w=200, h=40, fmt=lambda v: sd.sci(v, 0), size=26)
    lam = s.loc[order[1]]
    g1 = s.loc[order[0]]
    dth = 100 * (lam.theta0_6p3MeV_deg / g1.theta0_6p3MeV_deg - 1)
    left = sd.col(sd.p('<b>Scattering</b>: θ₀ per leg at 6.3 MeV, whole chord', 25), b1, gap=20)
    right = sd.col(sd.p('<b>Background</b>: barrel captures per beam neutron (log)', 25), b2,
                   sd.callout('Al lines stop at 7.7 MeV, under ¹⁴N (10.8) and far under the 13 MeV cut. '
                              'Kapton brings its own ¹⁴N.', GREY, 23), gap=20)
    body = sd.title(f'The 9 µm foil adds +{dth:.0f} % scattering and ~10⁻⁸ captures/n',
                    'G1 geometry. θ₀ includes the Micromegas entrance and 16 cm air; captures are analytic (barrel only).')
    body += sd.row(card_wrap(left), card_wrap(right), gap=44)
    D.slide('cost', body, '''
<p>Scattering: Highland on the sum of the skin, the Micromegas entrance (9.4×10⁻⁴ X₀) and 16 cm of air (5.3×10⁻⁴), at 6.3 MeV (the median softer X17 lepton). The skin is a small part of the chord for every option except the 3 bar Kapton wall. Scattering is not what limits the reach anyway (FEASIBILITY_SIM §1).</p>
<p>Captures: the beam (r99 = 12.9 mm) never reaches the barrel at r = 40 mm. Only neutrons scattered in the ³He do, before they are absorbed: σs/σa ≈ 3.15 b / 14 400 b = 2.2×10⁻⁴, and about half reach the wall (absorption length 2.8 cm at 1 bar). That gives ~10⁻⁴ wall crossings per neutron at ~60° (path ≈ 2t). Capture probability per crossing: PET is mostly H (0.33 b, 2.2 MeV γ), Al 0.23 b (7.7 MeV), Kapton adds ¹⁴N. Even with a factor 10 error on the crossing rate, the barrel stays 10³–10⁴ below the cell's other solids. The C1w Geant4 run biased the walls ×300 and found no correlated wall event above 12 MeV, for mylar or Kapton.</p>
<p>Activation: ²⁷Al(n,γ)²⁸Al (2.2 min, β⁻ 2.9 MeV + 1.78 MeV γ) at ~10⁻⁸/n adds nothing measurable to the singles rate.</p>''',
            short='Foil: cost')


def card_wrap(inner):
    return sd.card(inner, pad=36)


def s_seals(D, se):
    rows = []
    for _, r in se.iterrows():
        c = RED if 'bare' in r.component else (GREEN if 'Al' in r.component else GREY)
        tip = (f'{r.component}\nconductance g = area/path = {r.g_cm:.3g} cm, He {r.perm_barrer:g} barrer\n'
               f'{r.he3_L_per_cycle:.2e} L/cycle = {r.he3_L_per_cycle / H.CYCLE_D * L_PER_DAY_TO_MBARLS:.1e} mbar·L/s')
        rows.append((r.component.replace('barrel, ', ''), r.he3_L_per_cycle, c, tip))
    order = [3, 0, 4, 5, 1, 2]
    bars = sd.hbars([rows[i] for i in order], 50, width=480, log=True, vmin=1e-7, label_w=520, h=44,
                    fmt=lambda v: sd.sci(v, 1) + ' L', size=24)
    g1 = se.iloc[3].he3_L_per_cycle / H.CYCLE_D * L_PER_DAY_TO_MBARLS
    ring = se.iloc[0].he3_L_per_cycle / H.CYCLE_D * L_PER_DAY_TO_MBARLS
    right = sd.col(
        sd.callout('With a foil barrier the barrel drops out and the <b>O-rings</b> carry the loss. Indium or '
                   'metal (Helicoflex) seals take that lower if it matters.', GREY, 24),
        sd.callout(f'<b>Measurable on the bench.</b> Bare G1 leaks {sd.sci(g1, 0)} mbar·L/s; a foil cell ~{sd.sci(ring, 0)}. '
                   'A standard He leak detector reaches 10⁻¹⁰, and can be tuned to mass 3.', BLUE, 24),
        gap=22, w=520)
    body = sd.title('With a foil skin the O-rings become the leak',
                    f'~{se.iloc[0].he3_L_per_cycle * 1e3:.0f} cm³ per cycle. Leak budget of a 1 bar G1-size cell, ³He L per 50-day cycle (log).')
    body += sd.row(sd.col(bars, w=1100), right, gap=44, align='center')
    D.slide('seals', body, '''
<p>Each path is a conductance g = area / path length times a He permeability. Viton face O-rings at the Be window and the end cap: Parker’s rule g ≈ 0.7·π·D·(1 − S)² with D = 9 cm and 20 % squeeze, He ~9 barrer. Epoxy bondlines (skin onto the endcap lands, the overlap seam along the flat rod): 30 µm thick, 10–15 mm wide, He ~5 barrer. Foil pinholes: ~50/m² at 9 µm, radius 5 µm, fed by spreading conductance 4a through the 12 µm PET; the creased case multiplies the count by 100.</p>
<p>All of these are estimates to be replaced by a measurement. The leak test is cheap: a cell filled with ⁴He (which permeates ~10 % slower than ³He) in a bag or chamber sniffed by a mass-spectrometer leak detector. 1 L(STP)/day = 1.2×10⁻² mbar·L/s.</p>''',
            foot='he4_bag.py §5, out/seals.csv.', short='Seals')


def s_close(D):
    left = sd.col(
        sd.p('<b>Decisions</b>', 30, '#eef0f3'),
        sd.p('1. Put the 30 cm beam path in a He-filled (or evacuated) tube sealed onto the Be window; mylar '
             'window, ≥ 99 % He.', 26, '#d6dae2'),
        sd.p('2. Keep the cell at 1 bar and make the skin a barrier: 12 µm PET + 9–25 µm rolled Al foil laminate '
             'on the rod cage.', 26, '#d6dae2'),
        sd.p('3. Do not bag the target or the detector.', 26, '#d6dae2'),
        sd.p('4. Bench-test a short prototype cell with a He leak detector before the design freeze.', 26, '#d6dae2'),
        gap=18)
    right = sd.col(
        sd.p('<b>What this does not rule out</b>', 30, '#eef0f3'),
        sd.p('Permeabilities are literature values (PET ~2×, Kapton ~10×); the metallised-mylar and laminate '
             'factors are unmeasured.', 25, DMUT),
        sd.p('Wrapping a foil laminate on six rods may crack or crease it; the flat-rod seam must stay sealed.',
             25, DMUT),
        sd.p('The air split (90/10) is inferred from two runs; air-scattered neutrons may also feed captures in the '
             'detector. One Geant4 rerun, C1 on G1 with the flight path in He, settles both.', 25, DMUT),
        sd.p('The Micromegas He sensitivity and HV-in-He arguments are qualitative.', 25, DMUT),
        gap=18)
    body = (sd.kicker('Summary')
            + '<h2 style="font-size:64px;font-weight:600;line-height:1.1;color:#eef0f3">'
              'Helium belongs in the beam pipe and aluminium belongs in the skin</h2>'
            + sd.row(left, right, gap=80))
    D.slide('close', body, '''
<p>Reproduce: <code>python3 he4_bag/he4_bag.py</code> (tables in <code>he4_bag/out/</code>) then <code>python3 he4_bag/make_he4_bag_deck.py</code>. Inputs from the ILL study: <code>ill/out/h113_spectrum.csv</code>, the V0 and C1 numbers quoted in <code>ill/SIM_STATUS.md</code> and <code>ill/FEASIBILITY_SIM.md</code>, and <code>ill/sim/analysis_v3/contract_ladders.csv</code>.</p>''',
            dark=True, short='Decisions')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(OUT / 'he4_bag_deck.html'))
    a = ap.parse_args()
    (OUT / 'figures').mkdir(parents=True, exist_ok=True)
    nd = H.neutrons()
    lep = H.leptons()
    perm = {b: H.permeation(b) for b in (1.0, 10.0)}
    sk = H.skins()
    se = H.seals()

    D = sd.Deck('He bag and ³He leak', 'ILL ³He target: a He flight tube against air ¹⁴N, and a metal-foil '
                'skin against ³He permeation.')
    s_cover(D, nd, perm, sk)
    s_setup(D, nd, perm)
    s_air(D, nd)
    s_purity(D)
    s_balloon(D, lep)
    s_inflow(D, perm)
    s_leak(D, perm)
    s_options(D, sk)
    s_cost(D, sk)
    s_seals(D, se)
    s_close(D)
    p = D.write(a.out, note_meta=dict(
        title='ILL ³He target: helium bag and ³He leak rate',
        summary='Air ¹⁴N comes from the 30 cm beam path, so a He flight tube fixes it; a balloon around the target '
                'does not help and floods the mylar cell. Bare 12 µm mylar loses ~22 L of ³He per cycle; a 1 bar '
                'cell with an Al-foil laminate skin cuts that >1000× for +4 % scattering.',
        tags='x17, ill, target, he3', date='2026-10-02'),
        footer='Analytic study, he4_bag/ in x17_facility_search; calibrated on the ILL Geant4 campaign.')
    print(f'-> {p}')


if __name__ == '__main__':
    main()
