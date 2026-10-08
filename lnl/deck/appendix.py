"""The "basics" appendix of the LNL deck: proton beams, targets, the physics channel.

Called from build_deck.py (``appendix.add(D, ctx)``) after the main slides. Reads
lnl/out/appendix/*.csv (rerun ``lnl/appendix_calc.py`` first) plus the tables the
main deck already loads, passed in ``ctx``.
"""
import math

import pandas as pd

import slidedoc as sd
from slidedoc import term, sci

E_CHARGE = 1.602176634e-19
DAY = 86400.0
Q_PG = 17.2551
M_X = 16.7


def _num(v):
    """1.2×10⁵ above 10⁴, else with thousands separators."""
    if v >= 1e4:
        return sci(v)
    return f'{v:,.0f}' if v >= 10 else f'{v:.1f}'


def add(D, ctx):
    O = ctx['O']
    A = O / 'appendix'
    depth = pd.read_csv(A / 'depth.csv')
    offres = pd.read_csv(A / 'offres.csv')
    hl = pd.read_csv(A / 'highland.csv')
    xdec = pd.read_csv(A / 'x17_decay.csv')
    boost = pd.read_csv(A / 'boost.csv')
    bdt = pd.read_csv(A / 'boost_dtheta.csv').iloc[0]
    alpha = pd.read_csv(O / 'ipc_alpha.csv').set_index(['W_MeV', 'multipole']).alpha_pair
    ytab, ex, acc_h = ctx['ytab'], ctx['ex'], ctx['acc_h']
    ga, gb, g = ctx['ga'], ctx['gb'], ctx['g']
    G_acc = ctx['G_acc']
    R_ATOMKI, R_MEG_176 = ctx['R_ATOMKI'], ctx['R_MEG_176']
    A16 = ctx['A16']
    y16 = ytab.loc[A16]
    a_m1, a_e1 = alpha[(18.15, 'M1')], alpha[(18.15, 'E1')]
    a_m1_176 = alpha[(17.64, 'M1')]
    mm2 = ctx['mm2']
    tag_ab, tag_bp = ctx['tag_ab'], ctx['tag_bp']

    # ======================================================================= #
    # 0 divider
    # ======================================================================= #
    sec = lambda lab, sub, col: dict(label=lab, sub=sub, color=col)
    div = (sd.kicker('Appendix · the basics, for someone new to proton beams')
           + '<h2 style="font-size:64px;font-weight:600;line-height:1.1">How a proton-beam X17 measurement works, '
             'from the accelerator to the opening angle</h2>'
           + sd.p('Each slide answers one question and points back to the main slide it explains. '
                  'Hover the dotted terms and every drawn element; the Details drop-downs carry the numbers and sources.', 30, sd.DMUT)
           + sd.flow([sec('A · The beam', 'how a Van de Graaff makes it; energy, time structure; protons vs neutrons; the rate chain', sd.DBLUE),
                      sec('B · The target', 'thin vs stopping targets (slide 6); why we count photons; the chamber and its scattering', sd.DGREEN),
                      sec('C · The physics', 'capture and de-excitation like ³He; where the beam energy goes (E*); M1/E1/E0; the X17 bump; kinematics; off-resonance', sd.DRED),
                      sec('D · Glossary', 'every acronym in the deck', sd.DGREY)], dark=True, size=26)
           + sd.p('The short answers', 30, sd.DINK, 600)
           + sd.row(sd.col(sd.callout('<b>Beam:</b> one energy you dial in (0.2–2 MeV on AN2000), ~1 keV wide, continuous, 6×10¹² protons/s per µA. No neutrons below 1.88 MeV.', sd.DBLUE, 24),
                           sd.callout('<b>Target:</b> thin, so the beam spends only 1.10 → 1.04 MeV in lithium. A target that stops the beam makes 77 % of its pairs at 17.64 MeV, where there is no X17.', sd.DGREEN, 24), gap=18),
                    sd.col(sd.callout('<b>Chamber:</b> needed for the vacuum; its wall sets the angular resolution (5.1° for 0.4 mm CFRP). ~4° is reachable with a thinner or wider wall.', sd.DGREEN, 24),
                           sd.callout('<b>Physics:</b> like ³He, capture then de-excitation. No useful boost (β = 0.006); the X17\'s own speed sets the ~134° edge, which drops as E_p rises. Off resonance is a test, not more X17.', sd.DRED, 24), gap=18), gap=48))
    D.slide('appx', div, """<p>Written 2026-10-08 for readers new to the ⁸Be channel and to proton beams. Everything quantitative comes
from <code>lnl_rates.py</code> (cross sections, stopping, yields), <code>lnl/appendix_calc.py</code> (depth profiles,
scattering model, decay kinematics, off-resonance yields) or the Geant4 tables of the main deck. Analytic stand-ins are
labelled as such.</p>""", dark=True, short='Appendix')

    # ======================================================================= #
    # A1 the machine
    # ======================================================================= #
    def vdg_svg():
        W, H = 1664, 520
        o = []
        by = 250                                        # beam height
        # pressure tank
        o.append(f'<rect x="20" y="40" width="560" height="420" rx="80" fill="{sd.BG2}" stroke="{sd.MUT}" stroke-width="2" stroke-dasharray="8 6"'
                 f'{sd.tipattr("Pressure tank filled with insulating gas (SF₆ or N₂/CO₂) so the terminal can hold MV without sparking.")}/>')
        o.append(sd.T(560, 30, 'pressure tank (insulating gas)', 21, sd.MUT, 'end'))
        # terminal
        o.append(f'<rect x="60" y="120" width="190" height="260" rx="60" fill="#e6c9a8" stroke="{sd.ORANGE}" stroke-width="3"'
                 f'{sd.tipattr("High-voltage terminal at +V. Everything inside it floats at +V: the ion source, its gas bottle and power supplies.")}/>')
        o.append(sd.T(155, 108, 'terminal at +V', 23, sd.ORANGE, weight=600))
        o.append(sd.T(155, 350, '0.2–2.0 MV', 21, sd.ORANGE))
        # ion source + gas
        o.append(f'<rect x="85" y="{by - 40}" width="40" height="80" rx="10" fill="{sd.GREY}"'
                 f'{sd.tipattr("H₂ gas bottle feeding the source.")}/>')
        o.append(sd.T(105, by + 64, 'H₂', 21, sd.INK))
        o.append(f'<rect x="140" y="{by - 34}" width="90" height="68" rx="8" fill="{sd.CARD}" stroke="{sd.INK}" stroke-width="2"'
                 f'{sd.tipattr("RF ion source: a plasma strips electrons off hydrogen. It makes H⁺, H₂⁺ and H₃⁺ ions; all of them get accelerated.")}/>')
        o.append(sd.T(185, by - 6, 'ion', 20, sd.INK))
        o.append(sd.T(185, by + 18, 'source', 20, sd.INK))
        # belt
        o.append(f'<rect x="80" y="250" width="0" height="0"/>')
        o.append(sd.line(120, 380, 120, 470, sd.GOLD, 6) + sd.line(190, 380, 190, 470, sd.GOLD, 6))
        o.append(f'<path d="M120 470 Q155 500 190 470" fill="none" stroke="{sd.GOLD}" stroke-width="6"'
                 f'{sd.tipattr("Charging belt: sprays charge on at ground and carries it up into the terminal. The belt current sets how much beam current the terminal can supply.")}/>')
        o.append(sd.T(250, 500, 'charging belt', 21, sd.GOLD, 'start'))
        # accelerating tube
        for i in range(12):
            x = 260 + i * 26
            o.append(sd.line(x, by - 34, x, by + 34, sd.MUT, 3))
        o.append(f'<rect x="255" y="{by - 40}" width="315" height="80" fill="transparent"'
                 f'{sd.tipattr("Accelerating tube: rings on a resistor chain divide V evenly; the ions fall from +V to ground and gain kinetic energy q·V. For H⁺ at 1.03 MV: 1.03 MeV.")}/>')
        o.append(sd.T(412, by - 52, 'accelerating tube: gains q·V', 21, sd.INK))
        # beam out of tank to magnet
        o.append(sd.line(230, by, 760, by, sd.RED, 5))
        # magnet
        mx, my = 820, by
        o.append(f'<path d="M760 {by - 50} L880 {by - 50} L880 {by + 50} L760 {by + 50} Z" fill="{sd.BLUE}" fill-opacity="0.25" stroke="{sd.BLUE}" stroke-width="2"'
                 f'{sd.tipattr("Analysing magnet (90°): bends ions on a radius set by p/q. Only ions with the right momentum pass the exit slits: this picks H⁺ at the wanted energy and dumps H₂⁺, H₃⁺.")}/>')
        o.append(sd.T(820, by - 62, 'analysing magnet', 22, sd.BLUE, weight=600))
        o.append(f'<path d="M760 {by} Q 840 {by} 840 {by + 90}" fill="none" stroke="{sd.RED}" stroke-width="5"/>')
        o.append(f'<path d="M760 {by} Q 830 {by} 870 {by + 40}" fill="none" stroke="{sd.PURPLE}" stroke-width="3" stroke-dasharray="6 5"'
                 f'{sd.tipattr("H₂⁺ from the same terminal has the same energy but √2 more momentum per charge, so it bends less and is lost. MEG II (no full analysis) had 25 % H₂⁺: each of its protons carries E/2, which put most of their data on the 441 keV resonance.")}/>')
        o.append(sd.T(882, by + 30, 'H₂⁺, H₃⁺: bend less, lost', 19, sd.PURPLE, 'start'))
        # slits + feedback
        o.append(sd.line(820, by + 110, 832, by + 110, sd.INK, 6) + sd.line(848, by + 110, 860, by + 110, sd.INK, 6))
        o.append(f'<rect x="805" y="{by + 100}" width="70" height="22" fill="transparent"'
                 f'{sd.tipattr("Energy slits: if the beam drifts left or right the two jaws see different currents. That error signal corrects the terminal voltage (corona feedback), holding E to ~1 keV.")}/>')
        o.append(sd.T(880, by + 118, 'slits', 20, sd.INK, 'start'))
        o.append(sd.T(880, by + 144, 'slit currents correct V: ΔE ≈ 1 keV', 19, sd.MUT, 'start'))
        # beam line down then right
        o.append(sd.line(840, by + 90, 840, by + 170, sd.RED, 5))
        o.append(f'<path d="M840 {by + 170} Q 840 {by + 200} 870 {by + 200}" fill="none" stroke="{sd.RED}" stroke-width="5"/>')
        o.append(sd.line(870, by + 200, 1480, by + 200, sd.RED, 5))
        # quads
        for qx in (960, 1010):
            o.append(f'<ellipse cx="{qx}" cy="{by + 200}" rx="12" ry="36" fill="{sd.GREEN}" fill-opacity="0.55"'
                     f'{sd.tipattr("Quadrupole magnets: focus the beam to a few-mm spot on the target, like lenses.")}/>')
        o.append(sd.T(985, by + 260, 'focusing', 20, sd.GREEN))
        o.append(f'<rect x="1060" y="{by + 172}" width="34" height="56" fill="{sd.GOLD}" fill-opacity="0.6"'
                 f'{sd.tipattr("Steerers and beam-profile monitors: centre the beam on the target.")}/>')
        o.append(sd.T(1077, by + 260, 'steer', 20, sd.GOLD))
        o.append(sd.T(1112, by + 236, 'vacuum beam pipe', 20, sd.MUT, 'start'))
        # target chamber + dump
        o.append(f'<rect x="1260" y="{by + 150}" width="140" height="100" rx="10" fill="none" stroke="{sd.INK}" stroke-width="3"'
                 f'{sd.tipattr("Target chamber: still vacuum. The Li film sits at its centre; the MX17 arms are outside it.")}/>')
        o.append(sd.line(1330, by + 165, 1330, by + 235, sd.RED, 6))
        o.append(sd.T(1330, by + 140, 'target', 22, sd.INK, weight=600))
        o.append(f'<rect x="1480" y="{by + 165}" width="40" height="70" fill="{sd.INK}"'
                 f'{sd.tipattr("Beam dump / Faraday cup: stops the protons and counts their charge. 1 µA = 6.24×10¹² protons/s. This is the absolute normalisation; neutron beams have nothing as direct.")}/>')
        o.append(sd.T(1500, by + 270, 'dump = Faraday cup', 21, sd.INK))
        o.append(sd.T(1500, by + 296, 'counts the charge', 19, sd.MUT))
        # caption numbers
        o.append(sd.T(1180, 70, 'E_p = q·V: set the voltage, get the energy', 30, sd.INK, weight=600))
        o.append(sd.T(1180, 108, 'one energy at a time, ~1 keV wide, continuous current', 24, sd.MUT))
        return sd.svg(W, H, ''.join(o), 'Van de Graaff accelerator schematic')

    callouts = sd.row(
        sd.callout('<b>Choose any E_p</b> in 0.2–2.0 MeV on AN2000 (0.8–5.5 on CN). Self-service AN2000: one change per day, which suits a plan of a few energies held for days.', sd.BLUE, 23),
        sd.callout(f'<b>Continuous (DC):</b> protons arrive at random, 6.2×10¹² /s at 1 µA. CN can also pulse: 2 ns every 333 ns (≤ 700 nA).', sd.RED, 23),
        sd.callout(f'<b>Energy calibration</b> on known narrow lines: the 441 keV resonance itself, ²⁷Al(p,γ) at 992 keV, the ⁷Li(p,n) threshold at 1.881 MeV.', sd.GOLD, 23),
        gap=36)
    D.slide('a-vdg', sd.title('A Van de Graaff gives one proton energy, set by a voltage',
                              'Schematic of a single-ended electrostatic accelerator like AN2000 or CN (not to scale). Hover the parts.')
            + vdg_svg() + callouts,
            """<p>An electrostatic accelerator keeps one electrode (the terminal) at a steady high voltage V. Ions are made inside the
terminal and fall to ground through the accelerating tube, gaining q·V. For protons (q = e), E_p in MeV equals V in MV. There is no
RF and no bunching, so the beam is continuous.</p>
<p>The analysing magnet is what fixes the energy precisely. It passes only one momentum per charge onto the slits, and the slit
currents correct V. The LNL sheet quotes σ_E/E ~ 10⁻³ for CN (~1 keV at 1 MeV); AN2000 is not quoted <b>(ask)</b>, but it is the
same kind of machine. 1 keV is small compared to the target thickness (~60 keV in 300 µg/cm² Li₂O) and to the 168 keV width of
the 18.15 MeV resonance, though not to the 12 keV of the 441 keV one.</p>
<p>Contamination: the source also makes H₂⁺ (two protons at E/2 each) and H₃⁺. A properly tuned analysing magnet removes them.
MEG II's Cockcroft–Walton beam had 25 % H₂⁺ and put most of its data on 441 keV (<code>TARGETS.md</code> §6). Specify H⁺ only.</p>
<p>Sources: LNL beam sheet (<code>refs/LNL_Beams_AN2000_CN.txt</code>), CN paper arXiv:2605.12005, <code>lnl/FACILITY.md</code>.</p>""",
            foot='Main slide 3 (Beam) gives the machine ranges. lnl/FACILITY.md', short='A1 machine')

    # ======================================================================= #
    # A2 energy and time structure, against n_TOF and ILL
    # ======================================================================= #
    P = sd.Plot(980, 560, x=(1e-10, 1e4, 'log'), y=(-0.6, 4.6, 'lin'), xlabel='beam particle energy [MeV]', margin=(24, 30, 92, 250))
    P.xticks([(10 ** k, f'10{sd.sup(k)}') for k in range(-10, 5, 2)])
    lanes = [(4, 'n_TOF neutrons', 2.5e-8, 1e3, sd.GREY, 'n_TOF: a white spectrum from thermal (25 meV) to GeV in every pulse. Each neutron\'s energy is measured by its time of flight. The X17 physics only wants E_n ≲ 2 MeV.'),
             (3, 'ILL neutrons', 5e-10, 5e-8, sd.PURPLE, 'ILL PF1B: a cold/thermal beam, meV energies. Every neutron is captured at rest, so E* = S_n = 20.58 MeV, with no spread.'),
             (2, 'LNL AN2000 range', 0.2, 2.0, sd.BLUE, 'AN2000 terminal range 0.2–2.0 MV: any E_p in this range, chosen by the operator.'),
             (1, 'LNL CN range', 0.8, 5.5, sd.GREEN, 'CN: 0.8–5.5 MV (above 1.881 MeV the beam makes neutrons on Li).')]
    for y, lab, lo, hi, col, tp in lanes:
        P.raw(f'<rect x="{P.X(lo):.1f}" y="{P.Y(y + 0.28):.1f}" width="{P.X(hi) - P.X(lo):.1f}" height="{P.Y(y - 0.28) - P.Y(y + 0.28):.1f}" '
              f'rx="8" fill="{col}" fill-opacity="0.8"{sd.tipattr(tp)}/>')
        P.raw(sd.T(P.x0 - 16, P.Y(y) + 8, lab, 24, sd.INK, 'end', 600))
    # one LNL setting: a spike
    x1 = P.X(1.04)
    P.raw(f'<rect x="{x1 - 2:.1f}" y="{P.Y(0.4):.1f}" width="4" height="{P.Y(-0.4) - P.Y(0.4):.1f}" fill="{sd.RED}"'
          f'{sd.tipattr("One LNL setting: 1.04 MeV ± ~1 keV. Every proton has the same energy until it enters the target.")}/>')
    P.raw(sd.T(P.x0 - 16, P.Y(0) + 8, 'one LNL setting', 24, sd.INK, 'end', 600))
    P.raw(sd.T(x1 + 14, P.Y(0) + 8, '1.04 MeV, ~1 keV wide', 21, sd.RED, 'start'))
    P.raw(f'<rect x="{P.X(0.44):.1f}" y="{P.y0}" width="{P.X(1.23) - P.X(0.44):.1f}" height="{P.ph}" fill="{sd.ORANGE}" fill-opacity="0.12"/>', back=True)
    P.text(0.74, 4.45, '⁸Be window', 20, sd.ORANGE, 'middle')

    def lanes_svg():
        W, H = 620, 560
        o, x0, x1 = [], 20, 600
        L = [('n_TOF', 'a 7 ns proton bunch every ≥ 1.2 s; neutrons arrive over ~0.1 s by energy', sd.GREY, 'n'),
             ('ILL', 'reactor: continuous', sd.PURPLE, 'c'),
             ('LNL AN2000', 'DC: continuous, random arrivals', sd.BLUE, 'c'),
             ('LNL CN, pulsed', '2 ns every 333 ns (3 MHz), ≤ 700 nA', sd.GREEN, 'p')]
        for i, (nm, sub, col, kind) in enumerate(L):
            yb = 80 + i * 125
            o.append(sd.T(x0, yb - 46, nm, 24, sd.INK, 'start', 600))
            o.append(sd.T(x0, yb - 20, sub, 19, sd.MUT, 'start'))
            o.append(sd.line(x0, yb + 30, x1, yb + 30, sd.RULE, 2))
            if kind == 'c':
                o.append(f'<rect x="{x0}" y="{yb + 6}" width="{x1 - x0}" height="24" fill="{col}" fill-opacity="0.7"/>')
            elif kind == 'n':
                for xx in (60, 330):
                    o.append(f'<rect x="{xx}" y="{yb - 4}" width="5" height="34" fill="{col}"/>')
                    o.append(f'<path d="M{xx + 5} {yb + 10} Q {xx + 40} {yb + 26} {xx + 120} {yb + 29}" fill="none" stroke="{col}" stroke-width="2"/>')
            else:
                for k in range(26):
                    xx = x0 + 6 + k * 22
                    o.append(f'<rect x="{xx}" y="{yb + 2}" width="4" height="28" fill="{col}"/>')
        o.append(sd.T(x1, H - 8, 'time → (schematic, each lane its own scale)', 19, sd.MUT, 'end'))
        return sd.svg(W, H, ''.join(o), 'beam time structures')

    D.slide('a-spec', sd.title('One energy at a time, all the time: the opposite of n_TOF',
                               'Left: energies each beam delivers (log scale). Right: when the particles arrive. Hover the bars.')
            + sd.row(P.svg('beam energies'), lanes_svg(), gap=40)
            + sd.row(sd.callout('<b>No time of flight needed:</b> E_p is known from the machine. The only energy spread that matters is the ~60 keV lost in the film.', sd.BLUE, 23),
                     sd.callout('<b>Beam off = pure cosmics:</b> with a DC beam you measure the cosmic background directly by switching the beam off.', sd.GREY, 23),
                     sd.callout('<b>CN pulsed:</b> a pair must arrive in a 2 ns window every 333 ns, a ×~50 cut on cosmics.', sd.GREEN, 23), gap=36),
            """<p><b>Energy.</b> n_TOF gives every energy at once and sorts them afterwards by time of flight; most of the beam is at
energies the X17 does not want. The ILL gives one energy (thermal). LNL gives one energy that we choose. There is no "yield
spectrum" of the beam itself: it is a line. What has a spectrum is the <i>reaction</i> as the beam slows inside the target (A6, and
main slide 4 for σ(E_p)).</p>
<p><b>Time.</b> A continuous beam means no beam-off window to measure cosmics in, but also no instantaneous rate spikes: at 1 µA the
two-arm trigger rate is a few per second, dominated by cosmics (main slide 12). CN's pulsed mode is a cosmic and accidental veto
nobody has used for ⁸Be yet (a pair must arrive in the 2 ns window): ×~50 against cosmics in <code>PHYSICS.md</code> §4.</p>
<p>n_TOF numbers are the facility's standard ones (20 GeV/c PS bunches of ~7 ns, ≥ 1.2 s apart); they are here only for contrast.</p>""",
            foot='LNL beam sheet; CN paper arXiv:2605.12005. Energy bands are ranges, not flux shapes.', short='A2 energy & time')

    # ======================================================================= #
    # A3 protons vs neutrons
    # ======================================================================= #
    ill_rate = 1.9e10 * 1.03e-8
    lnl_rate = y16.g0_per_s_1uA
    rows = [
        ['what the beam does in the target',
         'no charge: flies straight until it is captured or scatters',
         f'ionises continuously: loses ~20 keV per 100 µg/cm², stops in {term("~17 µm of Al", "PSTAR CSDA range of a 1.1 MeV proton in Al: ~17 µm. In air: ~2.7 cm.")}'],
        ['so the target is',
         'thick: the ILL ³He cell absorbs 99.5 % of the beam',
         'thin: a ~1.5 µm film that only ~60 keV of the beam energy is spent in; the beam goes on to a dump'],
        ['fraction of beam that makes a 20 MeV γ',
         f'{term("1.03×10⁻⁸", "Radiative captures per absorbed thermal neutron in ³He: σ(n,γ)/σ(n,p) ≈ 55 µb / 5333 b.")} per absorbed n',
         f'{term(sci(y16.Y_g0), "γ₀ per proton, Li₂O 300 µg/cm² at 1.10 MeV (lnl_rates.thin_yield).")} per proton (γ₀)'],
        ['20 MeV-class γ per second',
         f'~{ill_rate:.0f}/s at the ILL (1.9×10¹⁰ n/s absorbed)',
         f'~{lnl_rate:,.0f}/s at 1 µA (γ₀ only; γ₁ adds 2×)'],
        ['why the cross section is small',
         'radiative capture competes with (n,p), which is 10⁸× bigger',
         f'{term("Coulomb barrier", "The proton must tunnel through the ⁷Li charge. At 1 MeV the tunnelling probability (Gamow factor) is still small, so σ(p,γ) is µb, with sharp resonances where a ⁸Be state sits.")}: σ(p,γ₀) ~ 20–30 µb near 1 MeV'],
        ['beam-made background in the detector',
         'yes, the dominant one: stray neutrons captured everywhere (MM occupancy, accidentals)',
         'almost none: no neutrons below 1.881 MeV; γ from other nuclei (¹⁹F, ²⁷Al, ¹¹B) and the dump. Cosmics dominate.'],
        ['beam path', 'air or He is fine; windows', 'vacuum all the way to the target, so a chamber wall the leptons must cross (B3)'],
        ['normalisation', 'flux monitors, simulated beam profile', 'the charge on the Faraday cup: protons counted directly'],
        ['what wears out', 'the gas cell leaks ³He', '1.1 W/µA of heat, implanted hydrogen, Li diffusion: replace targets ~weekly'],
    ]
    D.slide('a-pvn', sd.title('Protons stop in microns: thin targets, vacuum, no neutrons',
                              'What changes when the beam is protons instead of neutrons. Hover the dotted terms.')
            + sd.table(['', 'neutrons (n_TOF, ILL)', 'protons (LNL)'], rows, size=22, widths=[360, 560, 744], align=['left', 'left', 'left']),
            """<p>The headline difference is that a proton beam interacts with every electron it passes, so it slows down and stops,
while a neutron beam passes through matter almost freely until it is captured. Three consequences run through the whole deck:</p>
<ol><li>The target has to be thin, and its thickness sets which ⁸Be energies are made (B1).</li>
<li>The beam has to be in vacuum, so there is a chamber whose wall scatters the leptons (B3–B4).</li>
<li>The beam does not fill the hall with neutrons. At the ILL the stray neutrons set the walls on rate (MM occupancy,
accidentals). Here the beam-related background is tiny and the cosmics are what is left (main slides 9 and 12).</li></ol>
<p>The ILL rate is R_MAX 1.9×10¹⁰ n/s (the Ø2 cm spot) × 1.03×10⁻⁸; the ILL also has the M1/E0 pair channels at a similar α. The LNL
rate is the ATOMKI-2016 target at 1 µA from <code>out/yields.csv</code>. Ranges: PSTAR (<code>lnl/data/pstar_stopping.csv</code>).
ILL numbers: <code>ill/FEASIBILITY_SIM.md</code>.</p>""", short='A3 p vs n')

    # ======================================================================= #
    # A4 the rate chain
    # ======================================================================= #
    p_day = 1e-6 / E_CHARGE * DAY
    g0_day = y16.g0_per_s_1uA * DAY
    g1_day = (y16.g01_per_s_1uA - y16.g0_per_s_1uA) * DAY
    a_mix = (y16.frac_18_15_res + y16.frac_17_64) * a_m1 + y16.frac_direct * a_e1
    ipc_day = g0_day * a_mix
    x_day = g0_day * R_ATOMKI
    chain = [('protons on target', p_day, sd.GREY, '1 µA = 6.24×10¹² protons/s'),
             ('⁸Be* → γ₁ (15 MeV)', g1_day, sd.GOLD, 'γ₁ transitions (to the 3.0 MeV state), ~2× γ₀ at 1 MeV'),
             ('⁸Be* → γ₀ (18 MeV)', g0_day, sd.ORANGE, f'γ₀ per proton {sci(y16.Y_g0)}: Li₂O 300 µg/cm², 1.10 MeV'),
             ('IPC e⁺e⁻ pairs, 4π', ipc_day, sd.GREY, f'γ₀ × α, α = {a_mix:.2e} (M1 {a_m1:.2e} on the resonant half, E1 {a_e1:.2e} on the direct half)'),
             ('X17 → e⁺e⁻, 4π', x_day, sd.BLUE, 'γ₀ × R, R = 5.8×10⁻⁶ (ATOMKI)'),
             ('X17, both leptons in the MM', x_day * mm2, sd.BLUE, f'× {mm2 * 100:.0f} % geometric (Geant4)'),
             ('X17 triggered, as built', x_day * tag_ab, sd.BLUE, f'× {tag_ab * 100:.1f} % pair-tag (Geant4)'),
             ('X17 in the window, as built', ga.S_ATOMKI, sd.DBLUE, 'after E_sum, MM 15° + TOF, 125–155° (main slide 10)'),
             ('IPC in the window, as built', ga.B_ipc, sd.GREY, 'the background the X17 must beat (main slide 10)')]
    rows_ = [(lab, v, col, f'{lab}: {v:.3g} per day. {tp}') for lab, v, col, tp in chain]
    D.slide('a-chain', sd.title(f'1 proton in {1 / y16.Y_g0 / 1e9:.0f}×10⁹ makes an 18 MeV γ; ~{ga.S_ATOMKI:.0f} X17/day survive',
                                'Per day at 1 µA, ATOMKI-2016 target (Li₂O 300 µg/cm², 1.10 MeV), n_TOF hardware as built. Log bars; hover them.')
            + sd.row(sd.hbars(rows_, 1e18, width=620, h=46, log=True, vmin=1, label_w=400, fmt=_num, size=24),
                     sd.col(sd.callout('<b>Every step after the γ₀ is a fixed fraction of it.</b> That is why the main deck counts photons: γ₀ per second is the unit everything scales with (B2).', sd.ORANGE, 23),
                            sd.callout(f'<b>The detector costs ×{x_day / ga.S_ATOMKI:.0f}</b> on the X17 as built (×{x_day / gb.S_ATOMKI:.0f} with big plastics: {gb.S_ATOMKI:.0f}/day).', sd.BLUE, 23),
                            sd.callout(f'<b>The IPC is ~{ipc_day / x_day:.0f}× the X17</b> in 4π but only ~{ga.B_ipc / ga.S_ATOMKI:.0f}× in the window: the X17 sits where IPC is rare (C3).', sd.GREY, 23),
                            gap=18, w=520), gap=40),
            """<p>Each bar is the previous physics bar times one factor. Protons → γ₀ is the thin-target yield (cross section × ⁷Li
atoms per cm², integrated as the beam slows through the film). γ₀ → IPC is the Born internal-conversion coefficient α at
18.15 MeV (<code>out/ipc_alpha.csv</code>), weighted by the resonance (M1) and direct-capture (E1) shares. γ₀ → X17 is the
ATOMKI ratio R. The detector bars are the Geant4 chain of main slide 7 and the per-day budget of main slide 10.</p>""",
            foot='lnl/out/yields.csv, ipc_alpha.csv, geant/reach_geant.csv, geant/acceptance_geant.csv', short='A4 rate chain')

    # ======================================================================= #
    # B1 thin vs stopping target (explains main slide 6)
    # ======================================================================= #
    thin = depth[depth.target == 'Li2O']
    thick = depth[depth.target == 'Li metal']
    yl = ytab.loc['Li metal stops beam (ATOMKI 2016 mishap)']

    def cartoon():
        W, H = 1664, 170
        o = []
        # thin
        o.append(sd.T(20, 26, 'thin film (what we want)', 24, sd.BLUE, 'start', 600))
        o.append(sd.arrow(20, 95, 250, 95, sd.RED, 5))
        o.append(sd.T(30, 80, 'p, 1.10 MeV', 20, sd.RED, 'start'))
        o.append(f'<rect x="258" y="45" width="10" height="100" fill="{sd.BLUE}"{sd.tipattr("Li₂O 300 µg/cm² = 1.5 µm: the beam loses 61 keV crossing it")}/>')
        o.append(f'<rect x="268" y="45" width="16" height="100" fill="{sd.GREY}"{sd.tipattr("10 µm Al backing: the proton loses more energy here, but there is no lithium, so no ⁸Be")}/>')
        o.append(sd.arrow(290, 95, 640, 95, sd.RED, 4))
        o.append(sd.T(300, 80, 'exits at ~0.5 MeV → dump far away', 20, sd.RED, 'start'))
        o.append(sd.T(258, 168, 'only 1.10 → 1.04 MeV spent in lithium', 20, sd.MUT, 'start'))
        # thick
        o.append(sd.T(860, 26, 'stopping target (ATOMKI 2016 accident)', 24, sd.RED, 'start', 600))
        o.append(sd.arrow(860, 95, 1060, 95, sd.RED, 5))
        o.append(sd.T(870, 80, 'p, 1.10 MeV', 20, sd.RED, 'start'))
        o.append(f'<rect x="1068" y="45" width="430" height="100" fill="{sd.RED}" fill-opacity="0.25" stroke="{sd.RED}"'
                 f'{sd.tipattr("Li metal 63 µm (or Li diffused deep into the backing): the proton stops inside the lithium")}/>')
        dmax = thick.depth_um.max()
        for i in range(9):
            xx = 1068 + i * 47
            e = float(thick.E_keV.iloc[(thick.depth_um - dmax * i / 9).abs().argmin()])
            o.append(sd.T(xx + 4, 70 if i % 2 else 128, f'{e:.0f}', 17, sd.RED, 'start',
                          tip=f'{dmax * i / 9:.0f} µm deep: E_p = {e:.0f} keV'))
        o.append(sd.line(1068, 95, 1440, 95, sd.RED, 4, '10 6'))
        o.append(sd.T(1440, 102, '✕ stops', 20, sd.RED, 'start'))
        o.append(sd.T(1068, 168, 'every energy 1100 → 0 keV is spent in lithium, including 441 keV', 20, sd.MUT, 'start'))
        return sd.svg(W, H, ''.join(o), 'thin and stopping targets')

    P1 = sd.Plot(800, 470, x=(0.01, 100, 'log'), y=(0, 1200, 'lin'), xlabel='depth into the target [µm]', ylabel='proton energy E_p [keV]',
                 margin=(20, 24, 86, 110))
    P1.xticks([(v, f'{v:g}') for v in (0.01, 0.1, 1, 10, 100)]).yticks([(v, str(v)) for v in (0, 200, 400, 600, 800, 1000, 1200)])
    P1.hline(1030, sd.ORANGE, label='18.15 res (1030 keV)', tip='1⁺ resonance → E* = 18.15 MeV, Γ_lab 168 keV')
    P1.hline(441.4, sd.ORANGE, label='17.64 res (441 keV)', tip='1⁺ resonance → E* = 17.64 MeV, Γ_lab 12 keV, 50× stronger at its peak')
    for d, col, nm in ((thin, sd.BLUE, 'Li₂O 300 µg/cm²'), (thick, sd.RED, 'Li metal, stops the beam')):
        dd = d.iloc[::max(1, len(d) // 60)]
        P1.line(dd.depth_um, dd.E_keV, col, 4, markers=False, tip=nm)
    d441 = float(thick.depth_um.iloc[(thick.E_keV - 441.4).abs().argmin()])
    P1.text(0.012, 940, 'thin Li₂O: 1.10 → 1.04 MeV in 1.5 µm', 20, sd.BLUE)
    P1.text(0.012, 270, 'stopping Li metal: walks down,', 20, sd.RED)
    P1.text(0.012, 200, f'crosses 441 keV at {d441:.0f} µm', 20, sd.RED)

    e = ex[(ex.Ep_keV >= 300) & (ex.Ep_keV <= 1150)].iloc[::2]
    P2 = sd.Plot(800, 470, x=(300, 1150, 'lin'), y=(5, 1e4, 'log'), xlabel='proton energy E_p [keV]', ylabel='σ(p,γ₀) [µb]',
                 margin=(20, 24, 86, 110))
    P2.xticks([(v, str(v)) for v in (300, 500, 700, 900, 1100)]).yticks(sd.log_ticks(1, 4))
    P2.raw(f'<rect x="{P2.X(300):.1f}" y="{P2.y0}" width="{P2.X(1100) - P2.X(300):.1f}" height="{P2.ph}" fill="{sd.RED}" fill-opacity="0.08"/>', back=True)
    P2.raw(f'<rect x="{P2.X(1039):.1f}" y="{P2.y0}" width="{P2.X(1100) - P2.X(1039):.1f}" height="{P2.ph}" fill="{sd.BLUE}" fill-opacity="0.3"'
           f'{sd.tipattr("Thin Li₂O 300 µg/cm²: the beam samples only 1039–1100 keV")}/>', back=True)
    P2.line(e.Ep_keV, e.sigma_g0_ub.clip(lower=5), sd.INK, 3.5, markers=False, tip='σ(p,γ₀), Zahnow 1995')
    P2.text(1069, 6000, 'thin', 20, sd.BLUE, 'middle')
    P2.text(470, 6000, 'stopping target samples all of this', 20, sd.RED)
    side_fr = (f'Thin: {y16.g0_per_s_1uA:,.0f} γ₀/s, {y16.frac_17_64 * 100:.1f} % at 17.64 MeV. '
               f'Stopping: {yl.g0_per_s_1uA:,.0f} γ₀/s, {yl.frac_17_64 * 100:.0f} % at 17.64 MeV.')
    D.slide('b-thick', sd.title('A stopping target walks the beam through 441 keV',
                                'Main slide 6 explained. Top: the two targets. Left: proton energy against depth. Right: where that puts the beam on σ(E_p).')
            + cartoon()
            + sd.row(P1.svg('energy vs depth'), P2.svg('sigma window'), gap=48),
            f"""<p><b>"Stopping" refers to the proton beam, not to photons.</b> A stopping (or "thick") target is one in which the protons
lose all their energy. A thin target lets them through having lost only a little. Slide 6 asks: of the 18 MeV-class photons the
target makes, how many come from the 441 keV resonance (and so are 17.64 MeV transitions, not 18.15)?</p>
<p>The answer depends only on which proton energies are spent inside lithium. In the thin film the protons go from 1100 to
{thin.E_keV.min():.0f} keV, nowhere near 441, so {y16.frac_17_64 * 100:.1f} % of γ₀ are 17.64 (the BW tail). In a target that stops
the beam, every energy down to zero is spent in lithium. The 441 keV resonance is only 12 keV wide, but its peak is ~50× the 18.15 one,
so it ends up making {yl.frac_17_64 * 100:.0f} % of all γ₀. {side_fr}</p>
<p>This happened to ATOMKI in 2016: their "300 µg/cm² Li₂O" was really metallic Li diffused ~10 µm into the Al backing (Sas 2022).
The fix is a stable compound (LiF, Li₂O) on a cool backing, checked during the run (478 keV PIGE line, γ₀ line width).</p>
<p>Curves: <code>out/appendix/depth.csv</code> (PSTAR stopping, the integration of <code>lnl_rates.thin_yield</code>). Li metal at
0.534 g/cm³; the Li₂O film at bulk density, 300 µg/cm² = 1.49 µm.</p>""",
            foot='lnl/out/appendix/depth.csv, lnl/out/figures/excitation.csv, lnl/out/yields.csv', short='B1 thin vs thick')

    # ======================================================================= #
    # B2 why we count photons
    # ======================================================================= #
    def branch_svg():
        W, H = 900, 600
        o = []
        cx, cy = 150, 300
        o.append(f'<rect x="{cx - 120}" y="{cy - 60}" width="240" height="120" rx="20" fill="{sd.ORANGE}" fill-opacity="0.2" stroke="{sd.ORANGE}" stroke-width="3"'
                 f'{sd.tipattr("The ⁸Be nucleus excited to 18.15 MeV (or 17.64, or a direct-capture state near it).")}/>')
        o.append(sd.T(cx, cy - 8, '⁸Be*', 34, sd.INK, weight=600))
        o.append(sd.T(cx, cy + 30, '18.15 MeV', 22, sd.MUT))
        br = [(60, 'p + ⁷Li (elastic)', 'by far the most likely; no γ', sd.GREY, 'Most ⁸Be* just re-emit the proton. Not seen.'),
              (165, 'γ₁ → ⁸Be(3.0 MeV)', '≈ 2 × γ₀ at 1 MeV', sd.GOLD, '15.1 MeV transitions; their IPC is removed by the E_sum cut.'),
              (270, 'γ₀: a real photon', '1 (the unit)', sd.ORANGE, 'The ground-state transition, 18.15 MeV. Mostly flies through the detector unseen.'),
              (380, 'IPC e⁺e⁻ pair', f'α = {a_m1:.1e} (M1) – {a_e1:.1e} (E1) × γ₀', sd.GREY, 'Internal pair creation: the same transition, but via a virtual photon that makes e⁺e⁻. The background.'),
              (490, 'X17 → e⁺e⁻', 'R = 5.8×10⁻⁶ × γ₀ (ATOMKI)', sd.BLUE, 'The claim: a 16.7 MeV boson emitted instead of the photon, decaying to e⁺e⁻.')]
        for y, lab, sub, col, tp in br:
            o.append(sd.arrow(cx + 120, cy, 470, y + 10, col, 3))
            o.append(f'<g{sd.tipattr(tp)}>' + sd.T(480, y + 6, lab, 26, col if col != sd.GREY else sd.INK, 'start', 600)
                     + sd.T(480, y + 36, sub, 21, sd.MUT, 'start') + '</g>')
        o.append(f'<rect x="465" y="345" width="420" height="200" rx="12" fill="none" stroke="{sd.BLUE}" stroke-width="2" stroke-dasharray="6 6"/>')
        o.append(sd.T(675, 575, 'what the arms record: pairs', 21, sd.BLUE))
        return sd.svg(W, H, ''.join(o), 'decay branches of 8Be*')

    f17 = yl.frac_17_64
    side = sd.col(
        sd.callout('<b>We never count the photons themselves.</b> We count γ₀ because both the background (IPC = α·γ₀) and the signal (X17 = R·γ₀) are fixed fractions of it. Double the γ₀, double both.', sd.ORANGE, 24),
        sd.callout(f'<b>So "{f17 * 100:.0f} % of γ₀ at 17.64 MeV" means {f17 * 100:.0f} % of the pairs come from the wrong state.</b> '
                   f'17.64 MeV makes IPC (α = {a_m1_176:.1e}) but no X17 (MEG II: R(17.6) &lt; 1.8×10⁻⁶).', sd.RED, 24),
        sd.callout(f'<b>The energy sum cannot tell them apart:</b> 17.64 and 18.15 are 0.5 MeV apart, well inside the E_sum resolution. '
                   f'For the same X17 a stopping target gives ×{1 / (1 - f17):.1f} the IPC.', sd.GREY, 24),
        gap=22, w=680)
    D.slide('b-why', sd.title('Every pair channel is a fixed fraction of the photons',
                              'What an excited ⁸Be nucleus does next, per 18 MeV photon. Hover the branches.')
            + sd.row(branch_svg(), side, gap=40),
            f"""<p>Slides 6 and 10 of the main deck express target yields as "γ₀ per second". γ₀ is the transition to the ⁸Be ground
state. It is what earlier experiments measured (Zahnow's σ(p,γ₀)), and it is the denominator of R = Γ_X/Γ_γ. The pairs follow
from it: IPC is α·γ₀ with α ≈ 3.5–4.4×10⁻³ (Born, <code>out/ipc_alpha.csv</code>), X17 is R·γ₀.</p>
<p>The fraction of γ₀ from the 441 keV resonance is the fraction of the pair background that comes with no X17. That holds for
ATOMKI's 2016 non-observation at 17.64 and MEG II's limit there. With {f17 * 100:.0f} % of the IPC coming from 17.64, the
signal-to-background in the window drops by ×{1 / (1 - f17):.1f}, and the IPC shape changes (pure M1, no E1).</p>
<p>γ₁ (to the broad 3.0 MeV state) is twice as frequent but 3 MeV lower. The E_sum window removes it (main slide 8).</p>""",
            foot='Tilley 2004 (A = 8); lnl/out/ipc_alpha.csv; lnl/PHYSICS.md §1', short='B2 why photons')

    # ======================================================================= #
    # B3 the chamber
    # ======================================================================= #
    def chamber_svg():
        W, H = 1000, 660
        cx, cy = 430, 340
        sx = 1.1                                          # px per mm along the beam
        R_IN, PX_IN = 25.0, 110.0                         # inner region r <= 25 mm drawn 4.4 px/mm
        PX_OUT = 300.0                                    # r = 25 -> 240 mm in the remaining 190 px

        def rad(mm):
            a = abs(mm)
            v = a / R_IN * PX_IN if a <= R_IN else PX_IN + (a - R_IN) / (240 - R_IN) * (PX_OUT - PX_IN)
            return v if mm >= 0 else -v
        X = lambda mm: cx + mm * sx
        Y = lambda mm: cy - rad(mm)
        o = []
        o.append(f'<rect x="{X(-320):.1f}" y="{Y(240):.1f}" width="{640 * sx:.1f}" height="{Y(R_IN) - Y(240):.1f}" fill="{sd.BG2}" opacity="0.6"/>')
        o.append(sd.T(X(-310), Y(150), 'air', 22, sd.MUT, 'start'))
        for sgn in (1, -1):
            ya, yb = Y(sgn * 204), Y(sgn * 234)
            o.append(f'<rect x="{X(-180):.1f}" y="{min(ya, yb):.1f}" width="{360 * sx:.1f}" height="{abs(yb - ya):.1f}" fill="{sd.BLUE}" fill-opacity="0.35"'
                     f'{sd.tipattr("Micromegas TPC, 30 mm drift, faces at ±204 mm; it measures the lepton position to 0.6–0.8 mm")}/>')
        o.append(sd.T(X(186), Y(219) + 8, 'Micromegas', 22, sd.BLUE, 'start', 600))
        o.append(f'<rect x="{X(-300):.1f}" y="{Y(R_IN):.1f}" width="{600 * sx:.1f}" height="{2 * PX_IN:.1f}" fill="{sd.GREEN}" fill-opacity="0.08"'
                 f'{sd.tipattr("Vacuum inside the chamber: CFRP tube, 0.4 mm wall, radius 25 mm, ±300 mm long (Geant4 baseline)")}/>')
        for sgn in (1, -1):
            o.append(f'<rect x="{X(-300):.1f}" y="{Y(sgn * R_IN) - 3:.1f}" width="{600 * sx:.1f}" height="6" fill="{sd.INK}"'
                     f'{sd.tipattr("CFRP wall 0.4 mm (0.15 % X₀): the leptons cross it once")}/>')
        o.append(sd.T(X(-300), Y(R_IN) - 12, 'CFRP wall 0.4 mm, r = 25 mm', 21, sd.INK, 'start'))
        o.append(sd.T(X(-290), Y(-R_IN) - 14, 'vacuum', 21, sd.GREEN, 'start'))
        o.append(sd.arrow(X(-330), Y(0), X(-6), Y(0), sd.RED, 4))
        o.append(sd.T(X(-290), Y(0) - 12, 'p beam', 21, sd.RED, 'start'))
        o.append(sd.line(X(4), Y(0), X(246), Y(0), sd.RED, 2, '6 5'))
        o.append(f'<rect x="{X(0) - 3:.1f}" y="{Y(9):.1f}" width="6" height="{rad(18):.1f}" fill="{sd.RED}"{sd.tipattr("Li₂O film (1.5 µm) on 10 µm Al backing, ⊥ beam, 2 mm beam spot")}/>')
        for sgn in (1, -1):
            o.append(f'<rect x="{X(2):.1f}" y="{Y(20) if sgn > 0 else Y(-10):.1f}" width="6" height="{rad(10):.1f}" fill="{sd.GREY}"'
                     f'{sd.tipattr("Al holder annulus, r 10–20 mm, 1 mm thick, just behind the backing: keep it out of the lepton paths")}/>')
        o.append(sd.T(X(12), Y(-22) + 4, 'film + holder', 19, sd.MUT, 'start'))
        o.append(f'<rect x="{X(250):.1f}" y="{Y(15):.1f}" width="8" height="{rad(30):.1f}" fill="{sd.INK}"'
                 f'{sd.tipattr("Ta beam dump at +250 mm: stops the protons away from the target")}/>')
        o.append(sd.T(X(246), Y(-15) + 22, 'dump', 20, sd.INK, 'end'))
        # one lepton, 62 deg to the beam, kinked in the wall
        th, kink, L = math.radians(62), math.radians(8), 219.0
        rx = R_IN / math.tan(th)
        hx = rx + (L - R_IN) / math.tan(th - kink)
        tx = L / math.tan(th)
        o.append(sd.line(X(0), Y(0), X(rx), Y(R_IN), sd.PURPLE, 3.5))
        o.append(sd.line(X(rx), Y(R_IN), X(hx), Y(L), sd.PURPLE, 3.5))
        o.append(sd.line(X(rx), Y(R_IN), X(tx), Y(L), sd.MUT, 2, '5 5'))
        o.append(f'<circle cx="{X(hx):.1f}" cy="{Y(L):.1f}" r="7" fill="{sd.PURPLE}"/>')
        o.append(f'<circle cx="{X(rx):.1f}" cy="{Y(R_IN):.1f}" r="11" fill="none" stroke="{sd.RED}" stroke-width="2.5"'
                 f'{sd.tipattr("The lepton crosses the wall and scatters by a random small angle (rms 2.6° per plane for CFRP 0.4 mm at 8.6 MeV). Kink exaggerated here.")}/>')
        o.append(sd.T(X(rx) + 18, Y(R_IN) + 30, 'kink in the wall', 20, sd.RED, 'start', 600))
        o.append(sd.T(X(hx) + 12, Y(L) + 36, 'measured hit', 20, sd.PURPLE, 'start'))
        o.append(sd.T(X(tx) - 10, Y(L) + 36, 'unscattered', 20, sd.MUT, 'end'))
        o.append(sd.line(X(0), Y(0), X(hx), Y(L), sd.GOLD, 2.5, '3 6'))
        o.append(sd.T(X(170), Y(110), 'reconstructed chord', 20, sd.GOLD, 'start'))
        o.append(sd.T(X(170), Y(110) + 24, '(beam spot → hit)', 20, sd.GOLD, 'start'))
        th3 = math.radians(-70)
        r3 = 219.0
        o.append(sd.line(X(0), Y(0), X(-r3 / math.tan(-th3)), Y(-r3), sd.PURPLE, 3.5))
        o.append(sd.T(W - 10, H - 6, 'side view, beam left → right; radii inside the tube drawn ×4', 19, sd.MUT, 'end'))
        return sd.svg(W, H, ''.join(o), 'target chamber side view')

    hb = hl.set_index(['material', 't_mm', 'r_mm'])
    th_c, th_a = hb.loc[('CFRP', 0.4, 25)].theta0_deg, hb.loc[('Al', 0.5, 25)].theta0_deg
    side = sd.col(
        sd.callout('<b>Why a chamber at all:</b> the beam must be in vacuum. A 1.1 MeV proton stops in ~2.7 cm of air; the film would oxidise; the beam line is pumped anyway.', sd.GREEN, 23),
        sd.callout(f'<b>What it costs:</b> each lepton crosses the wall and scatters, by {th_c:.1f}° rms in 0.4 mm CFRP and {th_a:.1f}° in 0.5 mm Al (Highland, 8.6 MeV). '
                   'The opening angle is the chord from the beam spot to the hit, so the kink becomes an angle error.', sd.RED, 23),
        sd.callout('<b>Geant4 (L5):</b> X17 σ68 = 5.1° (CFRP 0.4), 8.8° (Al 0.5), 12.2° (Al 1.0). The wall is the largest single term; acceptance does not change.', sd.PURPLE, 23),
        sd.callout('The backing and holder matter less: a Cu 25 µm backing gives 7.5°, C 20 µm the same as Al 10 µm.', sd.GREY, 23),
        gap=16, w=620)
    D.slide('b-chamber', sd.title('The beam needs vacuum, and the leptons pay for the wall',
                                  'Side view of the Geant4 target region with one X17 lepton crossing the chamber wall. Hover the parts.')
            + sd.row(chamber_svg(), side, gap=40),
            """<p>Geometry (MX17_Full_Geant <code>lnl</code>, <code>--target li</code>): Li₂O 300 µg/cm² film on Al 10 µm, Al 1 mm holder
annulus at r 10–20 mm, CFRP 0.4 mm chamber tube of inner radius 25 mm and half-length 300 mm, Al 5 mm flanges, Ta 2 mm dump at
+250 mm. The leptons of an X17 pair leave at ~25–155° to the beam, so each crosses the tube wall once, at ~68° on average, over a
path of t/sin θ.</p>
<p>Why it matters: the X17 makes a sharp edge in the opening angle at ~134°. A resolution σ smears the edge over ~σ, so the
analysis window has to be wider and lets more IPC in. Main slide 12 has the scan; B4 extrapolates it to other walls.</p>
<p>The Micromegas measure positions well (0.6–0.8 mm) and directions poorly (11–26°), so the opening angle is reconstructed as the
chord from the beam spot (a point, here) to the hit. A kink at radius r moves the hit by θ·(L − r), an angle error of
θ·(L − r)/L at the Micromegas (L ≈ 215 mm).</p>""",
            foot='Geant4 L5 chamber scan: lnl/out/geant/material_scan.csv. Highland: PDG formula, plane-projected, β = 1.', short='B3 chamber')

    # ======================================================================= #
    # B4 improving the chamber
    # ======================================================================= #
    s0, kfit = hl.s0_deg.iloc[0], hl.k.iloc[0]
    lab = {('CFRP', 0.4, 25): 'CFRP 0.4 mm, r 25 (baseline)', ('Al', 0.5, 25): 'Al 0.5 mm, r 25', ('Al', 1.0, 25): 'Al 1.0 mm, r 25',
           ('CFRP', 0.2, 25): 'CFRP 0.2 mm, r 25', ('CFRP', 0.4, 60): 'CFRP 0.4 mm, r 60', ('CFRP', 0.4, 100): 'CFRP 0.4 mm, r 100',
           ('Kapton', 0.05, 25): 'Kapton 50 µm window band', ('Be', 0.25, 25): 'Be 0.25 mm, r 25', ('none', 0.0, 25): 'no wall (floor)'}
    order = [('Al', 1.0, 25), ('Al', 0.5, 25), ('CFRP', 0.4, 25), ('CFRP', 0.4, 60), ('CFRP', 0.2, 25), ('Be', 0.25, 25),
             ('CFRP', 0.4, 100), ('Kapton', 0.05, 25), ('none', 0.0, 25)]
    brows = []
    for key in order:
        r_ = hb.loc[key]
        geant = not math.isnan(r_.sigma68_geant_deg)
        v = r_.sigma68_geant_deg if geant else r_.sigma68_model_deg
        col = sd.PURPLE if geant else sd.BLUE
        tp = (f'{lab[key]}: x/X₀ = {r_.x_over_X0 * 100:.2f} %, θ₀ = {r_.theta0_deg:.2f}° per plane, lever (L−r)/L = {r_.lever:.2f}. '
              + (f'Geant4 σ68 = {r_.sigma68_geant_deg:.1f}° (model {r_.sigma68_model_deg:.1f}°)' if geant else f'model σ68 = {r_.sigma68_model_deg:.1f}° (not simulated)'))
        brows.append((lab[key], v, col, tp))
    side = sd.col(
        sd.legend([('Geant4 (L5)', sd.PURPLE, 'box'), ('calibrated Highland model', sd.BLUE, 'box')], 22),
        sd.callout(f'<b>The floor is {s0:.1f}°</b> with no wall at all: the beam spot, air, the Micromegas window and gas, the backing. Past ~4° the wall is no longer the main term.', sd.GREY, 23),
        sd.callout('<b>Thinner or lighter wall:</b> CFRP 0.2 mm or Be 0.25 mm → ~4.3°. A thin Kapton window band in the lepton path → ~3.7°, but it must hold vacuum over the band (engineering to check).', sd.BLUE, 23),
        sd.callout('<b>Wider tube:</b> the kink happens closer to the Micromegas, so it matters less. r = 100 mm → ~4.2°. It does not cost acceptance.', sd.GREEN, 23),
        sd.callout('<b>Avoid Al</b> anywhere between the film and the arms (×2 on σ).', sd.RED, 23),
        gap=16, w=620)
    D.slide('b-improve', sd.title(f'The wall can come down from 5.1° to ~4°, never below {s0:.1f}°',
                                  'X17 opening-angle resolution σ68 for chamber options. Purple: Geant4. Blue: a Highland model fitted to the Geant4 points. Hover the bars.')
            + sd.row(sd.hbars(brows, 13, width=480, h=40, label_w=420, fmt=lambda v: f'{v:.1f}°', size=24), side, gap=40),
            f"""<p>Model (<code>lnl/appendix_calc.py</code>, an analytic stand-in until Geant4 runs these walls):
σ68² = s₀² + (k·θ₀·(L − r)/L)², with θ₀ the Highland angle of an 8.6 MeV lepton in the wall (normal incidence), L = 215 mm and r
the wall radius. s₀ = {s0:.2f}° and k = {kfit:.2f} are fitted to the three Geant4 walls (CFRP 0.4, Al 0.5, Al 1.0) and reproduce
them to 0.1°. X₀: CFRP 27.5 cm (carbon at 1.55 g/cm³), Al 8.9, Be 35.3, Kapton 28.6 cm.</p>
<p>Not modelled: the oblique path (×1/sin θ, the same for every option, so it is in k), a window band's frame, and how much reach a
better σ buys. The last needs the Geant4 reach machinery (<code>sim/lnl_geant.py</code>) on new L5-type runs. Worth doing before
designing the chamber. The ATOMKI and MEG II chambers are carbon-fibre tubes (Ø48 mm, 400 µm); the LNL group's chamber
drawings are <b>(ask)</b>.</p>""",
            foot='lnl/out/appendix/highland.csv (model) and lnl/out/geant/material_scan.csv (Geant4 L5).', short='B4 better chamber')

    # ======================================================================= #
    # C1 the same idea as 3He: level schemes
    # ======================================================================= #
    def levels_svg():
        W, H = 1100, 640
        o = []

        def scheme(x0, name, lv, thr, cap, top, breaks, arrows, cap_tip):
            # energy axis broken: [0, b0] and [b1, top]
            b0, b1 = breaks
            y_lo, y_mid, y_hi = 600, 470, 110

            def Y(e):
                if e <= b0:
                    return y_lo - (e / b0) * (y_lo - y_mid)
                return y_mid - 30 - (e - b1) / (top - b1) * (y_mid - 30 - y_hi)
            o.append(sd.T(x0 + 150, 60, name, 32, sd.INK, weight=600))
            o.append(sd.line(x0 + 10, y_mid - 6, x0 + 290, y_mid - 6, sd.RULE, 1, '4 6'))
            o.append(sd.line(x0 + 10, y_mid - 24, x0 + 290, y_mid - 24, sd.RULE, 1, '4 6'))
            for e, jp, col, tp, wide in lv:
                y = Y(e)
                if wide:
                    o.append(f'<rect x="{x0 + 40}" y="{y - 10:.1f}" width="220" height="20" fill="{col}" fill-opacity="0.25"/>')
                o.append(f'<g{sd.tipattr(tp)}>' + sd.line(x0 + 40, y, x0 + 260, y, col, 4)
                         + sd.T(x0 + 30, y + 7, f'{e:g}', 20, sd.INK, 'end') + sd.T(x0 + 44, y + 26 if e == 0 else y - 8, jp, 19, col, 'start') + '</g>')
            ty = Y(thr[0])
            o.append(sd.line(x0 + 40, ty, x0 + 260, ty, sd.MUT, 2, '8 6'))
            o.append(sd.T(x0 + 30, ty + 7, f'{thr[0]:g}', 20, sd.MUT, 'end'))
            o.append(sd.T(x0 + 44, ty + 24, thr[1], 19, sd.MUT, 'start'))
            cy_ = Y(cap[0])
            o.append(f'<g{sd.tipattr(cap_tip)}>' + sd.arrow(x0 + 470, cy_ - 50, x0 + 268, cy_, sd.RED, 3)
                     + sd.T(x0 + 470, cy_ - 60, cap[1], 21, sd.RED, 'end', 600) + '</g>')
            for e1, e2, lab_, col, dx in arrows:
                o.append(sd.arrow(x0 + dx, Y(e1), x0 + dx, Y(e2) - 4, col, 3.5))
                o.append(sd.T(x0 + dx + 8, Y(e2) - 56, lab_, 22, col, 'start', 600))
            return Y

        scheme(20, '⁸Be (LNL)',
               [(0, '0⁺ ground → 2α', sd.INK, 'Ground state: unbound, falls apart into two α (no γ). The pair is what we detect.', False),
                (3.03, '2⁺, broad', sd.GOLD, '3.03 MeV 2⁺, Γ ≈ 1.5 MeV: γ₁ ends here', True),
                (17.64, '1⁺ T=1', sd.ORANGE, '17.640 MeV 1⁺, isovector; reached at E_p = 441 keV; Γ_lab 12 keV', False),
                (18.15, '1⁺ T=0', sd.ORANGE, '18.150 MeV 1⁺, isoscalar; reached at E_p = 1030 keV; Γ_lab 168 keV; the ATOMKI anomaly', False)],
               (17.255, 'p + ⁷Li'), (18.15, 'p (E_p) + ⁷Li'), 18.6, (4, 17.0),
               [(18.15, 0, 'γ₀', sd.ORANGE, 135), (18.15, 3.03, 'γ₁', sd.GOLD, 215)],
               'E* = 17.255 + (7/8)·E_p: the proton adds its centre-of-mass energy to the 17.255 MeV binding')
        scheme(570, '⁴He (n_TOF / ILL)',
               [(0, '0⁺ ground', sd.INK, '⁴He ground state: stable. Transitions here are the n_TOF signal.', False),
                (20.21, '0⁺', sd.PURPLE, '20.21 MeV first excited 0⁺ (just below the n + ³He threshold)', False),
                (21.01, '0⁻', sd.PURPLE, '21.01 MeV 0⁻', False)],
               (20.577, 'n + ³He'), (20.58, 'n (thermal) + ³He'), 21.4, (4, 19.6),
               [(20.58, 0, 'M1, E0', sd.PURPLE, 150)],
               'E* = 20.577 + 0.75·E_n: thermal neutrons land right at threshold, in the continuum (s-wave, 0⁺ or 1⁺)')
        o.append(sd.T(W / 2, H - 4, 'energies in MeV; the axis is broken between ~4 and ~17 MeV', 19, sd.MUT))
        return sd.svg(W, H, ''.join(o), 'level schemes of 8Be and 4He')

    side = sd.col(
        sd.callout('<b>Yes, the same premise.</b> Capture makes an excited nucleus (⁸Be* here, ⁴He* at n_TOF). It de-excites to the ground state by a photon, by IPC, or (the claim) by an X17.', sd.BLUE, 23),
        sd.callout('<b>Difference 1: the Coulomb barrier.</b> The neutron is captured at any energy, even at rest. The proton needs ~MeV and is captured mostly where a ⁸Be state sits: the resonances.', sd.ORANGE, 23),
        sd.callout('<b>Difference 2: which state you make is chosen by E_p.</b> On a resonance you make one 1⁺ state; between them, direct capture. At n_TOF E_n sets E* too, but the beam is white.', sd.PURPLE, 23),
        sd.callout('<b>Difference 3: the ⁸Be ground state breaks into 2α</b>, harmless, at 92 keV total.', sd.GREY, 23),
        gap=16, w=540)
    D.slide('c-levels', sd.title('Like ³He: a capture, then a de-excitation',
                                 'Level schemes (simplified) of ⁸Be and ⁴He, with the capture entry point and the transitions we look at. Hover the levels.')
            + sd.row(levels_svg(), side, gap=24),
            """<p>Energies from Tilley 2004 (A = 8) and the ⁴He compilation; only the levels that matter here are drawn. The excitation is
the binding of the projectile (Q = 17.2551 MeV for p + ⁷Li, S_n = 20.577 MeV for n + ³He) plus the centre-of-mass kinetic
energy, which is the lab energy × M_target/(M_target + m_projectile): 7/8 here, 3/4 at n_TOF.</p>
<p>The two ⁸Be 1⁺ levels differ in isospin. 17.64 is mostly T = 1 and 18.15 mostly T = 0 (mixed ~95/5 %). ATOMKI's anomaly is in
the isoscalar one and absent in the isovector one, which is part of why theorists care (a protophobic vector boson couples
differently to the two).</p>""",
            foot='Tilley et al., NPA 745 (2004); lnl/PHYSICS.md §1', short='C1 like ³He')

    energy_slides(D, A, ex)

    # ======================================================================= #
    # C2 multipolarity
    # ======================================================================= #
    def mcard(title_, init, how, where, col, tip):
        inner = (f'<p style="font-size:27px;font-weight:600;color:{col}">{title_}</p>'
                 f'<p style="font-size:22px;line-height:1.25"><b>{init}</b></p>'
                 f'<p style="font-size:21px;line-height:1.3">{where}</p>')
        return sd.card(inner, pad=18, tip=how + ' ' + tip)
    cards = sd.col(
        mcard('M1 · magnetic dipole', '1⁺ → 0⁺: spin flips, parity stays',
              'The photon carries 1 unit of angular momentum and no parity change: a magnetic (spin-flip) transition.',
              f'<b>Here:</b> both resonances (p-wave proton, l = 1). IPC α = {a_m1:.1e}. Pairs mostly at small angles.', sd.GREY,
              'A p-wave proton (l = 1, odd) on ⁷Li (3/2⁻) gives even-parity states, among them the 1⁺ resonances. 1⁺ → 0⁺ with no parity change needs M1.'),
        mcard('E1 · electric dipole', '1⁻ → 0⁺: parity flips',
              'The charge distribution oscillates like a dipole antenna; 1 unit of angular momentum, parity changes.',
              f'<b>Here:</b> direct capture (s-wave proton, l = 0), ~half the γ₀ at 1.1 MeV. α = {a_e1:.1e}. Pairs spread to larger angles.', sd.PURPLE,
              'An s-wave proton (l = 0) on ⁷Li (3/2⁻) gives 1⁻ and 2⁻ capture states. 1⁻ → 0⁺ with parity change is E1.'),
        mcard('E0 · electric monopole', '0⁺ → 0⁺: no photon allowed',
              'A real photon must carry ≥ 1 unit of angular momentum, so 0 → 0 can only go by e⁺e⁻ pairs (or a conversion electron).',
              '<b>Here:</b> only the ¹⁹F(p,α)¹⁶O 6.05 MeV calibration line (LiF). <b>At n_TOF/ILL:</b> the ⁴He E0 branch.', sd.GREEN,
              'Pure pair transition: invisible in γ, but a clean IPC calibration. At n_TOF and the ILL the fits carry an E0 pair component next to M1.'),
        gap=10, w=760)
    hm1 = acc_h['IPC M1, 18.15 (generated)']
    he1 = acc_h['IPC E1, 18.15 (generated)']
    th = acc_h.theta_lo_deg + 2.5
    P = sd.Plot(860, 600, x=(0, 180, 'lin'), y=(1e-4, 0.2, 'log'), xlabel='e⁺e⁻ opening angle [°]', ylabel='fraction of pairs / 5°',
                margin=(24, 30, 92, 110))
    P.xticks([(v, f'{v}°') for v in range(0, 181, 30)]).yticks(sd.log_ticks(-4, -1))
    for hh, col, nm in ((hm1, sd.GREY, 'M1'), (he1, sd.PURPLE, 'E1')):
        tps = [f'{nm} IPC at 18.15 MeV, {a:.0f}–{a + 5:.0f}°: {v:.4f} of all pairs' for a, v in zip(acc_h.theta_lo_deg, hh)]
        P.line(th, hh.clip(lower=1e-4), col, 4, r=4, tips=tps)
    P.raw(f'<rect x="{P.X(125):.1f}" y="{P.y0}" width="{P.X(155) - P.X(125):.1f}" height="{P.ph}" fill="{sd.BLUE}" fill-opacity="0.1"/>', back=True)
    P.text(140, 0.12, 'X17 region', 21, sd.BLUE, 'middle')
    r140 = he1[acc_h.theta_lo_deg == 140].iloc[0] * a_e1 / (hm1[acc_h.theta_lo_deg == 140].iloc[0] * a_m1)
    P.text(8, 3e-4, f'per photon at 140°, E1 makes ×{r140:.1f} the pairs of M1', 21, sd.PURPLE)
    D.slide('c-multi', sd.title('M1, E1, E0: what the transition carries off',
                                'Left: the three kinds of transition. Right: IPC opening-angle shapes at 18.15 MeV, Born, 4π. Hover the cards and points.')
            + sd.row(cards, sd.col(P.svg('IPC shapes'), sd.legend([('M1 IPC', sd.GREY), ('E1 IPC', sd.PURPLE)], 22), gap=6, w=860), gap=40),
            f"""<p>The "multipolarity" of a transition is the angular momentum L and parity the emitted photon carries away. An electric
transition (EL) changes parity by (−1)^L; a magnetic one (ML) by (−1)^(L+1). The initial and final spins and parities fix which ones are
allowed, and the lowest allowed one wins. Here the final state is always the 0⁺ ground state (or the 2⁺ for γ₁).</p>
<p>The same rules apply when the photon is virtual and makes a pair (IPC). Each multipolarity then has its own
opening-angle distribution. All of them peak at small angles (the pair "remembers" it was almost a real photon), but E1 falls more
slowly. At 140° an E1 transition makes {r140:.1f}× more pairs per photon than an M1. This is why the direct-capture (E1) share matters
for the background: main slide 4, and C6.</p>
<p>Curves: Born IPC from nTof_x17 <code>ipc_born</code> through <code>lnl_rates.py</code>, generated (before the detector), the
"(generated)" columns of <code>out/acceptance_hist.csv</code>. A real transition can be an M1–E1 mixture with interference, which
changes the shape. That is open item 3 in HANDOFF.md.</p>""", short='C2 M1/E1/E0')

    # ======================================================================= #
    # C3 what we look for
    # ======================================================================= #
    hx = acc_h['X17 m=16.7, 18.15 (generated)']
    f_m1 = y16.frac_18_15_res + y16.frac_17_64
    ipc = 1e6 * (f_m1 * a_m1 * hm1 + y16.frac_direct * a_e1 * he1)
    x17 = 1e6 * R_ATOMKI * hx
    P1 = sd.Plot(800, 560, x=(0, 180, 'lin'), y=(0.1, 1e3, 'log'), xlabel='e⁺e⁻ opening angle [°]', ylabel='pairs per 10⁶ γ₀, per 5°',
                 margin=(24, 24, 92, 110))
    P1.xticks([(v, f'{v}°') for v in range(0, 181, 30)]).yticks(sd.log_ticks(-1, 3))
    tps = [f'{a:.0f}–{a + 5:.0f}°: IPC {i:.2f}, X17 {x:.2f} per 10⁶ γ₀' for a, i, x in zip(acc_h.theta_lo_deg, ipc, x17)]
    P1.line(th, ipc.clip(lower=0.1), sd.GREY, 4, r=4, tips=tps)
    xm = x17 > 0
    P1.line(th[xm], x17[xm], sd.BLUE, 4, r=4, tips=[t for t, m in zip(tps, xm) if m])
    P1.text(20, 300, 'IPC (M1 + E1 mix)', 21, sd.GREY)
    P1.text(160, 3, 'X17, R = 5.8×10⁻⁶', 21, sd.BLUE, 'end')
    ratio = (ipc + x17) / ipc
    m90 = acc_h.theta_lo_deg >= 90
    P2 = sd.Plot(800, 560, x=(90, 180, 'lin'), y=(0.98, 1.10, 'lin'), xlabel='e⁺e⁻ opening angle [°]', ylabel='(IPC + X17) / IPC',
                 margin=(24, 24, 92, 110))
    P2.xticks([(v, f'{v}°') for v in range(90, 181, 15)]).yticks([(v, f'{v:.2f}') for v in (1.0, 1.02, 1.04, 1.06, 1.08, 1.10)])
    P2.hline(1.0, sd.MUT)
    tps2 = [f'{a:.0f}–{a + 5:.0f}°: ×{v:.3f}' for a, v in zip(acc_h.theta_lo_deg[m90], ratio[m90])]
    xs_, ys_ = sd.step_xy(list(acc_h.theta_lo_deg[m90]) + [180], list(ratio[m90]))
    P2.line(xs_, ys_, sd.BLUE, 4, markers=False)
    P2.line(th[m90], ratio[m90], sd.BLUE, 0, r=5, tips=tps2)
    P2.vline(133.8, sd.ORANGE, label='edge 133.8°', tip='θ_min = 2·asin(m/E) for m = 16.7, E = 18.15 MeV')
    pk = ratio[m90].max()
    D.slide('c-bump', sd.title(f'What we look for: a {(pk - 1) * 100:.0f} % step at the edge of the IPC',
                               'Opening angle at the ATOMKI-2016 point, 4π (no detector), per 10⁶ γ₀. Left: log scale. Right: the ratio. Hover the points.')
            + sd.row(P1.svg('IPC and X17'), P2.svg('ratio'), gap=48),
            f"""<p>This is the measurement in one picture. The IPC falls by ~100× from small angles to 140°. The X17 is emitted with a
fixed energy, so its pairs pile up just above a kinematic edge (C4) and show up as a step of ~{(pk - 1) * 100:.0f} % over the IPC
at R = 5.8×10⁻⁶. ATOMKI's 2016 plot is this, after their detector acceptance.</p>
<p>The detector reshapes both curves (main slide 7: the four arms favour back-to-back pairs, and the trigger keeps a few %), and
γ₁ IPC and cosmics add to the background (main slides 8–9). What the analysis needs: the IPC shape known well enough (M1/E1 mix)
that a few-% step is not a shape error. That is why the main slides fit a template over 90–180° and why ATOMKI calibrate on the
pure-M1 441 keV line.</p>
<p>Weights: IPC = γ₀ × [(f_res) α_M1 shape_M1 + (f_direct) α_E1 shape_E1], with f_direct = {y16.frac_direct:.2f} (Li₂O 300, 1.10 MeV);
X17 = γ₀ × R × shape_X17 (m = 16.7, W = 18.15). Shapes from <code>out/acceptance_hist.csv</code> (generated).</p>""",
            foot='lnl/out/acceptance_hist.csv, ipc_alpha.csv, yields.csv', short='C3 the bump')

    # ======================================================================= #
    # C4 kinematics: the boost question
    # ======================================================================= #
    W_, mx_ = 18.15, M_X
    gx = W_ / mx_
    bx = math.sqrt(1 - 1 / gx ** 2)
    ps = math.sqrt((mx_ / 2) ** 2 - 0.511 ** 2)

    def lab_vectors(cs):
        sn = math.sqrt(1 - cs * cs)
        out = []
        for sgn in (1, -1):
            out.append((sgn * ps * sn, gx * (sgn * ps * cs + bx * mx_ / 2)))
        return out

    def decay_svg():
        W, H = 820, 600
        o = []
        sc = 15                                            # px per MeV/c
        panels = [(150, 'X17 at rest', None), (450, 'lab: decay ⊥ motion', 0.0), (700, 'lab: cos θ* = 0.8', 0.8)]
        for x0, nm, cs in panels:
            y0 = 360
            o.append(sd.T(x0, 60, nm, 23, sd.INK, weight=600))
            if cs is None:
                for sgn in (1, -1):
                    o.append(sd.arrow(x0, y0, x0 + sgn * ps * sc * 0.6, y0 - sgn * ps * sc * 0.8, sd.PURPLE, 3.5))
                o.append(f'<circle cx="{x0}" cy="{y0}" r="10" fill="{sd.BLUE}"/>')
                o.append(sd.T(x0, y0 + 160, '180°, 8.35 MeV/c each', 20, sd.MUT))
                continue
            o.append(sd.arrow(x0, y0 + 140, x0, y0 + 40, sd.BLUE, 4))
            o.append(sd.T(x0 + 12, y0 + 110, f'X17, β = {bx:.2f}', 19, sd.BLUE, 'start'))
            vs = lab_vectors(cs)
            for px, pz in vs:
                o.append(sd.arrow(x0, y0, x0 + px * sc, y0 - pz * sc, sd.PURPLE, 3.5))
            a = math.degrees(math.acos((vs[0][0] * vs[1][0] + vs[0][1] * vs[1][1]) / math.hypot(*vs[0]) / math.hypot(*vs[1])))
            o.append(f'<circle cx="{x0}" cy="{y0}" r="8" fill="{sd.BLUE}"/>')
            o.append(sd.T(x0, y0 + 180, f'opening {a:.1f}°', 23, sd.PURPLE, weight=600))
        o.append(sd.T(W / 2, H - 6, f'X17 m = {mx_} MeV from E* = {W_} MeV: momenta to scale (arrows in MeV/c)', 19, sd.MUT))
        return sd.svg(W, H, ''.join(o), 'X17 decay in rest and lab frame')

    P = sd.Plot(820, 540, x=(-1, 1, 'lin'), y=(125, 182, 'lin'), xlabel='cos θ* (decay angle in the X17 frame)', ylabel='lab opening angle [°]',
                margin=(24, 24, 92, 110))
    P.xticks([(v, f'{v:g}') for v in (-1, -0.5, 0, 0.5, 1)]).yticks([(v, f'{v}°') for v in (130, 140, 150, 160, 170, 180)])
    for w, col, dash in ((17.64, sd.ORANGE, '8 6'), (18.15, sd.BLUE, None), (18.33, sd.GREEN, '3 6')):
        k = f'open_deg_W{w}'
        sub = xdec.iloc[::10]
        P.line(sub.cos_star, sub[k], col, 3.5, dash=dash, r=4,
               tips=[f'E* = {w} MeV, cos θ* = {c:.1f}: {v:.1f}°' for c, v in zip(sub.cos_star, sub[k])])
    P.raw(f'<rect x="{P.X(-0.5):.1f}" y="{P.y0}" width="{P.X(0.5) - P.X(-0.5):.1f}" height="{P.ph}" fill="{sd.BLUE}" fill-opacity="0.08"/>', back=True)
    P.text(0, 176, 'half of all decays', 20, sd.BLUE, 'middle')
    P.text(0, 171, '(isotropic: flat in cos θ*)', 20, sd.BLUE, 'middle')
    b8 = bdt.beta_8Be
    xc = xdec.set_index(xdec.cos_star.round(2))['open_deg_W18.15']
    half_w = xc.loc[0.5] - xc.min()
    D.slide('c-kin', sd.title(f'The X17\'s own speed (β = {bx:.2f}) sets the angle, not the recoil',
                              'Left: an X17 decay at rest and in the lab. Right: lab opening angle against the decay angle, for three E*. Hover the points.')
            + sd.row(decay_svg(), sd.col(P.svg('opening vs cos theta*'),
                                         sd.legend([('E* 17.64', sd.ORANGE, 'dash'), ('18.15', sd.BLUE), ('18.33 (E_p 1.225)', sd.GREEN, 'dash')], 21), gap=6), gap=24)
            + sd.row(sd.callout(f'<b>No useful boost along the beam:</b> the ⁸Be* recoils at β = {b8:.4f} at 1.03 MeV. It changes the X17 opening angle by {bdt.mean_abs_dtheta_deg:.2f}° on average '
                                f'(99 % &lt; {bdt.p99_abs_dtheta_deg:.1f}°), against a 5° resolution. At n_TOF the ⁴He* moves at β = 0.016 (2 MeV) to 0.043 (14 MeV).', sd.GREY, 22),
                     sd.callout(f'<b>The edge is where the decay is ⊥ to the X17 motion</b>, and half of all decays (|cos θ*| &lt; 0.5) land within {half_w:.1f}° of it. That pile-up is the bump of C3.', sd.BLUE, 22), gap=40),
            f"""<p>The X17 is heavy compared to the energy available: m = 16.7 MeV out of E* = 18.15 MeV, so it moves at only
β = {bx:.2f} (γ = {gx:.3f}). In its own frame the e⁺ and e⁻ fly apart back to back, 8.35 MeV/c each. In the lab its motion pushes
both forward, closing the angle; the smallest opening, 2·asin(m/E) = 133.8°, is for a decay perpendicular to the X17 direction.
A decay along the motion stays at 180°. Because the decay is isotropic (flat in cos θ*) and the curve is flat near cos θ* = 0, most
decays land just above the minimum.</p>
<p>The recoil of the whole ⁸Be* is a second, much smaller boost. The toy MC in <code>appendix_calc.py</code> (2×10⁵ isotropic X17
decays, boosted along the beam by β = {b8:.4f}) gives the numbers above. MEG II also neglects it. Tables:
<code>out/appendix/x17_decay.csv</code>, <code>boost.csv</code>, <code>boost_dtheta.csv</code>.</p>""",
            short='C4 boost')

    # ======================================================================= #
    # C5 why the X17 angle changes with E_p
    # ======================================================================= #
    Ws = (17.64, 18.15, 18.33)
    bxs = [math.sqrt(1 - (M_X / w) ** 2) for w in Ws]
    edges = [xdec[f'open_deg_W{w}'].min() for w in Ws]
    chain = sd.flow([
        dict(label='E_p ↑ 100 keV', sub='set by the accelerator', color=sd.RED),
        dict(label='E* ↑ 87.5 keV', sub='E* = 17.255 + 0.875·E_p', color=sd.ORANGE),
        dict(label='X17 kinetic energy ↑', sub='E_X = E*, m fixed', color=sd.BLUE),
        dict(label='X17 faster', sub=f'β {bxs[0]:.2f} → {bxs[1]:.2f} → {bxs[2]:.2f}', color=sd.BLUE,
             tip='β_X at E* = 17.64, 18.15, 18.33 MeV for m = 16.7 MeV'),
        dict(label='edge moves down', sub=f'{edges[0]:.0f}° → {edges[1]:.0f}° → {edges[2]:.0f}°', color=sd.PURPLE)], size=22)
    P = sd.Plot(1060, 520, x=(120, 180, 'lin'), y=(0, 0.4, 'lin'), xlabel='e⁺e⁻ opening angle [°]', ylabel='fraction of X17 / 5°',
                margin=(24, 30, 92, 110))
    P.xticks([(v, f'{v}°') for v in range(120, 181, 10)]).yticks([(v, f'{v:.1f}') for v in (0, 0.1, 0.2, 0.3, 0.4)])
    for col_, colr, nm, dash in (('X17 m=16.7, 17.64 (generated)', sd.ORANGE, 'X17 m 16.7 at E* 17.64 (E_p 441 keV)', '8 6'),
                                 ('X17 m=16.7, 18.15 (generated)', sd.BLUE, 'X17 m 16.7 at E* 18.15 (E_p 1030 keV)', None),
                                 ('X17 m=17.0, 18.15 (generated)', sd.GREEN, 'X17 m 17.0 at E* 18.15', '3 6'),
                                 ('IPC M1, 17.64 (generated)', sd.GREY, None, None)):
        if nm is None:
            continue
        hh = acc_h[col_]
        xs_, ys_ = sd.step_xy(list(acc_h.theta_lo_deg) + [180], list(hh))
        mk = acc_h.theta_lo_deg >= 120
        xs2, ys2 = sd.step_xy(list(acc_h.theta_lo_deg[mk]) + [180], list(hh[mk]))
        P.line(xs2, ys2, colr, 4, dash=dash, markers=False, tip=nm)
    side = sd.col(
        sd.legend([('m 16.7, E* 17.64', sd.ORANGE, 'dash'), ('m 16.7, E* 18.15', sd.BLUE), ('m 17.0, E* 18.15', sd.GREEN, 'dash')], 21),
        sd.callout('<b>A real particle must move with E_p</b>; a mass shift moves it the other way. The IPC shape (and cosmics) do not move. Scanning E_p is the cleanest test there is.', sd.BLUE, 23),
        sd.callout('ATOMKI 2016 saw no excess at 17.64 MeV. Hanoi (1.225 MeV) found m = 16.66 ± 0.47 ± 0.35 MeV, consistent with 2016 at a different E_p.', sd.GREY, 23),
        gap=18, w=520)
    D.slide('c-edge', sd.title('More proton energy, a faster X17, a smaller opening angle',
                               'Generated X17 opening-angle distributions (4π, before the detector) for two excitation energies and two masses. Hover the curves.')
            + chain + sd.row(P.svg('X17 shapes vs E*'), side, gap=40),
            f"""<p>θ_min = 2·asin(m_X/E_X): with the mass fixed, a larger E_X means a larger velocity and a smaller minimum angle. E_X is
E* (the ⁸Be ground-state recoil takes negligible energy), and E* follows E_p with slope 7/8. Over the 0.44–1.23 MeV programme,
E* goes 17.64 → 18.33 MeV and the edge from {edges[0]:.0f}° to {edges[2]:.0f}° (m = 16.7). Main slide 5 plots θ_min against E_p for three masses.</p>
<p>The width of the distribution is the same kinematics: the faster the X17, the wider the range from θ_min to 180°. At 17.64 MeV
the X17 moves slowest (β = {bxs[0]:.2f}) and the pairs crowd into 140–150°.</p>""",
            foot='lnl/out/acceptance_hist.csv (generated columns), lnl/out/kinematics.csv', short='C5 edge vs E_p')

    # ======================================================================= #
    # C6 off resonance
    # ======================================================================= #
    o_ = offres[(offres.Ep_keV >= 620) & (offres.Ep_keV <= 1400)]
    tot = o_.g0_per_s_1uA
    res18 = tot * o_.frac_18_15_res
    dirc = tot * o_.frac_direct
    P = sd.Plot(940, 560, x=(600, 1400, 'lin'), y=(0, 2600, 'lin'), xlabel='beam energy E_p [keV] (Li₂O 300 µg/cm²)',
                ylabel='γ₀ per second at 1 µA', margin=(24, 30, 92, 120))
    P.xticks([(v, str(v)) for v in (600, 800, 1000, 1200, 1400)]).yticks([(v, f'{v:,}') for v in (0, 500, 1000, 1500, 2000, 2500)])
    sub = o_.iloc[::3]
    tips_ = [f'E_p {r.Ep_keV:.0f} keV: {r.g0_per_s_1uA:,.0f} γ₀/s; 18.15 resonance {r.frac_18_15_res * 100:.0f} %, direct {r.frac_direct * 100:.0f} %, 17.64 {r.frac_17_64 * 100:.1f} %'
             for r in sub.itertuples()]
    P.line(o_.Ep_keV, tot, sd.INK, 4, markers=False)
    P.line(sub.Ep_keV, sub.g0_per_s_1uA, sd.INK, 0, r=5, tips=tips_)
    P.line(o_.Ep_keV, res18, sd.ORANGE, 3, markers=False, tip='from the 18.15 resonance (M1)')
    P.line(o_.Ep_keV, dirc, sd.PURPLE, 3, markers=False, tip='from direct capture (E1)')
    pts = [('ATOMKI 2022 direct', 800, 'ATOMKI 2022, 0.80 (LiF)'), (A16, 1100, 'ATOMKI 2016, 1.10'), ('Hanoi 2024', 1225, 'Hanoi, 1.225')]
    for scn, ep, nm in pts:
        P.vline(ep, sd.BLUE, dash='4 6', tip=nm)
    P.text(808, 2450, '0.80', 20, sd.BLUE)
    P.text(1108, 2450, '1.10', 20, sd.BLUE)
    P.text(1233, 2450, '1.225', 20, sd.BLUE)
    gr = offres.set_index('Ep_keV').g0_per_s_1uA
    r08, r12 = gr.loc[800.0] / gr.loc[1100.0], gr.iloc[(gr.index - 1225).argsort()[:1]].iloc[0] / gr.loc[1100.0]
    dslow = [g(sc).days_count_opt_live / g(A16).days_count_opt_live for sc in ('ATOMKI 2022 direct', 'Hanoi 2024')]
    drow = []
    for scn, ep, nm in pts:
        ra, rb = g(scn), g(scn, hw='big plastics')
        drow.append([nm.replace(', ', ' · ').replace(' (LiF)', '') + ' MeV' + (', LiF' if 'LiF' in nm else ''), f'{ra.S_ATOMKI:.1f}', f'{ra.days_count_opt_live:.0f} d', f'{rb.days_count_opt_live:.1f} d'])
    side = sd.col(
        sd.legend([('total γ₀', sd.INK), ('18.15 resonance (M1)', sd.ORANGE), ('direct capture (E1)', sd.PURPLE)], 21),
        sd.callout('<b>No: off resonance is not more X17.</b> The total γ₀ is lowest there, and the E1 IPC it leaves is worse at 140°. Off-resonance points are tests, not yield.', sd.RED, 23),
        sd.table(['', 'X17/day', 'as built', 'big pl.'], drow, size=21, widths=[230, 100, 100, 90]),
        sd.p('3σ days at the ATOMKI R, 1 µA, assuming the X17 rides on every γ₀ (resonant and direct alike).', 19, sd.MUT),
        sd.callout('<b>Two hypotheses:</b> X17 only from the 1⁺ resonance → it follows the orange curve and vanishes off resonance. X17 from every transition (ATOMKI 2022) → it follows the black one.', sd.ORANGE, 22),
        gap=14, w=560)
    D.slide('c-offres', sd.title('On resonance for rate; off resonance to test the X17',
                                 'Thin-target γ₀ rate against E_p, split into the 18.15 MeV resonance and direct capture. Hover the points.')
            + sd.row(P.svg('gamma0 vs Ep split'), side, gap=36),
            f"""<p>The question from main slide 4: if half the γ₀ at 1.1 MeV is direct E1 capture, should we sit where E1 dominates to get
more X17? It depends on what the X17 couples to, which is exactly what is unknown:</p>
<ol><li><b>X17 from the 1⁺ resonance only</b> (the 2016 picture: an M1-like emission from the 18.15 MeV state). Then the X17 rate is
the orange curve × R, which falls to ~zero off resonance. Off-resonance runs should show nothing.</li>
<li><b>X17 from any transition at the same R</b> (ATOMKI 2022 claim an excess in direct capture too; this is what the main deck's
reach assumes). Then the X17 follows the black curve, which is highest on the resonance and {(1 - r08) * 100:.0f} % / {(1 - r12) * 100:.0f} % lower at 0.80 / 1.225 MeV.</li></ol>
<p>In both cases the rate is best at ~1.03–1.10 MeV. Off resonance, the background is also worse: the leftover E1 IPC makes
~{r140:.1f}× more pairs per photon at 140° than M1 (C2). Hence the table: 0.80 and 1.225 MeV take ×{dslow[0]:.1f} and ×{dslow[1]:.1f} longer than 1.10 as built.</p>
<p>The value of the off-resonance points is that they separate hypotheses 1 and 2, and that the edge moves with E_p (C5). A
sensible plan: calibrate at 441 keV (pure M1, known shape), take most data at 1.03–1.10 MeV, then 0.80 and 1.225 MeV.</p>
<p>Curve: <code>out/appendix/offres.csv</code> (<code>lnl_rates.thin_yield</code> at each E_p, Li₂O 300 µg/cm²). The x axis is
the energy entering the film; the peak sits ~30 keV above 1030 keV because the film is 60 keV thick. The wiggle of the
direct-capture curve under the resonance is an artefact of subtracting constant-width Breit–Wigners from the Zahnow data
(main slide 4); only the sum is measured. The 0.80 MeV
row of the table is ATOMKI's LiF 300 target, so its rate is lower than this Li₂O curve.</p>""",
            foot='lnl/out/appendix/offres.csv; days: lnl/out/geant/reach_geant.csv (MM 15° + TOF, m = 16.7)', short='C6 off resonance')

    # ======================================================================= #
    # D glossary
    # ======================================================================= #
    g1 = [
        ('µA', '10⁻⁶ A of protons = 6.24×10¹² protons/s'),
        ('Van de Graaff / terminal', 'electrostatic accelerator; the terminal holds the high voltage V; E_p = e·V'),
        ('analysing magnet', 'bends by p/q; selects H⁺ at one energy'),
        ('Faraday cup', 'collects and measures the beam charge: the proton count'),
        ('µg/cm²', 'target thickness as areal mass; 100 µg/cm² Li₂O ≈ 0.5 µm ≈ 20 keV of proton energy loss'),
        ('stopping power, ΔE', 'proton energy lost per areal mass (PSTAR); ΔE across the film'),
        ('thin / stopping target', 'beam crosses it losing little / beam stops inside it'),
        ('backing, dump', 'foil the film sits on / thick block that stops the beam'),
        ('PIGE, 478 keV', '⁷Li(p,p′γ) line: monitors how much Li is left'),
        ('Coulomb barrier', 'repulsion the proton tunnels through; makes σ(p,γ) µb'),
        ('resonance, Γ', 'E_p at which capture forms one ⁸Be state; Γ its width'),
        ('direct capture', 'non-resonant capture straight to the ground state (E1)'),
        ('S-factor', 'σ with the Coulomb tunnelling divided out; smooth in E'),
    ]
    g2 = [
        ('E*, Q', 'excitation of ⁸Be; Q = 17.255 MeV is the p + ⁷Li binding'),
        ('γ₀, γ₁', 'transitions to the ground state / to the 3.0 MeV 2⁺ state'),
        ('IPC', 'internal pair creation: a transition makes e⁺e⁻ instead of a γ'),
        ('α', 'IPC pairs per γ (3.5×10⁻³ M1, 4.4×10⁻³ E1 at 18.15)'),
        ('EPC', 'external pair creation: a real γ converts in material'),
        ('R = Γ_X/Γ_γ', 'X17 emissions per γ₀; ATOMKI: 5.8×10⁻⁶'),
        ('M1, E1, E0', 'magnetic dipole, electric dipole, monopole (C2)'),
        ('T (isospin)', '0 or 1: the two 1⁺ states differ in it'),
        ('θ_min, edge', '2·asin(m_X/E_X): smallest X17 opening angle'),
        ('X₀, Highland', 'radiation length; formula for multiple-scattering angle'),
        ('σ68', 'half-width holding 68 % of the opening-angle error'),
        ('E_sum, LS', 'two-arm scintillator energy; liquid scintillators'),
        ('MM segment, TOF', 'Micromegas track direction; arm-to-arm time of flight'),
    ]
    tb = lambda rows: sd.table(['term', 'meaning'], [[f'<b>{a}</b>', b] for a, b in rows], size=20, widths=[250, 560], align=['left', 'left'])
    D.slide('d-gloss', sd.title('Glossary', 'Beam and target terms on the left, physics and detector terms on the right.')
            + sd.row(tb(g1), tb(g2), gap=40),
            """<p>Longer explanations: <code>lnl/PHYSICS.md</code> (reaction and record), <code>lnl/TARGETS.md</code> (targets for
someone who has never seen a target ladder), <code>lnl/FACILITY.md</code> (the two machines and access).</p>""",
            short='D glossary')


def energy_slides(D, A, ex):
    """C1a-c: where the beam energy goes, why any E_p works, and why the X17 angle cares."""
    en = pd.read_csv(A / 'energy.csv')
    row_ = lambda ep: en.iloc[(en.Ep_keV - ep).abs().argmin()]
    r0, r8, r1, r2 = row_(441.4), row_(800.0), row_(1030.0), row_(1225.0)

    # ------------------------------------------------------------------ C1a
    def ladder_svg():
        W, H = 1000, 660
        lo, hi, y_lo, y_hi = 16.95, 18.45, 520, 120
        Y = lambda e: y_lo - (e - lo) / (hi - lo) * (y_lo - y_hi)
        y_gs = 625
        o = []
        q, tot, es = r1.Q_MeV, r1.Q_MeV + r1.Ep_keV / 1e3, r1.Estar_MeV
        ecm, rec = r1.Ecm_keV / 1e3, r1.recoil_keV / 1e3
        # broken axis and the ground state
        for yb in (552, 566):
            o.append(sd.poly([30, 980], [yb, yb], sd.RULE, 1.5, dash='4 6'))
        o.append(sd.T(250, 563, 'axis broken: 0 → 17 MeV not to scale', 18, sd.MUT, 'start'))
        o.append(f'<g{sd.tipattr("The ⁸Be ground state, the zero of the excitation energy. Unbound by 92 keV: it splits into two α.")}>'
                 + sd.line(60, y_gs, 940, y_gs, sd.INK, 4) + sd.T(460, y_gs - 12, '⁸Be ground state (E* = 0)', 21, sd.INK) + '</g>')
        # guide lines
        for e, col in ((q, sd.MUT), (tot, sd.MUT), (es, sd.ORANGE)):
            o.append(sd.line(60, Y(e), 940, Y(e), col, 1, '3 7'))
        hdr = [(150, '① masses'), (330, '② + beam'), (545, '③ split'), (820, '④ ⁸Be* made')]
        for x, s in hdr:
            o.append(sd.T(x, 70, s, 24, sd.INK, weight=600))
        # 1: Q bracket from ground to Q
        qtip = ('Q = m(p) + m(⁷Li) − m(⁸Be) = 938.272 + 6533.833 − 7454.850 = 17.255 MeV (nuclear masses).\n'
                'A proton at rest touching ⁷Li already has this much energy above the ⁸Be ground state.')
        o.append(f'<g{sd.tipattr(qtip)}>' + sd.line(120, Y(q), 220, Y(q), sd.GREY, 5)
                 + sd.arrow(170, y_gs - 4, 170, Y(q) + 6, sd.GREY, 3) + sd.T(160, 470, 'Q', 30, sd.GREY, 'end', 600)
                 + sd.T(160, 500, '17.255', 21, sd.GREY, 'end')
                 + sd.T(170, Y(q) - 12, 'p + ⁷Li at rest', 20, sd.GREY) + '</g>')
        # 2: beam kinetic energy on top
        ktip = f'The proton\'s kinetic energy from the accelerator, E_p = {r1.Ep_keV / 1e3:.3f} MeV (lab). Energy is conserved, so it adds on top of Q.'
        o.append(f'<g{sd.tipattr(ktip)}>' + sd.line(280, Y(q), 380, Y(q), sd.GREY, 5) + sd.line(280, Y(tot), 380, Y(tot), sd.RED, 5)
                 + sd.arrow(330, Y(q) - 2, 330, Y(tot) + 6, sd.RED, 4)
                 + sd.T(330, Y(tot) - 14, f'{tot:.3f}', 21, sd.RED, weight=600)
                 + sd.T(320, (Y(q) + Y(tot)) / 2 + 8, f'E_p = {r1.Ep_keV / 1e3:.3f}', 21, sd.RED, 'end') + '</g>')
        # 3: split
        x0, x1 = 450, 520
        stip = (f'⅞ of E_p = {ecm:.3f} MeV is the energy of p and ⁷Li moving towards each other (centre-of-mass energy): it can become excitation.\n'
                f'⅛ = {rec:.3f} MeV is the motion of the whole system, which must survive the merger (momentum conservation).')
        o.append(f'<g{sd.tipattr(stip)}>'
                 + f'<rect x="{x0}" y="{Y(q + ecm):.1f}" width="{x1 - x0}" height="{Y(q) - Y(q + ecm):.1f}" fill="{sd.ORANGE}" fill-opacity="0.85"/>'
                 + f'<rect x="{x0}" y="{Y(tot):.1f}" width="{x1 - x0}" height="{Y(q + ecm) - Y(tot):.1f}" fill="{sd.GREY}" fill-opacity="0.45"/>'
                 + sd.T(x1 + 12, (Y(q) + Y(q + ecm)) / 2 - 4, f'⅞ · E_p = {ecm:.3f}', 21, sd.ORANGE, 'start', 600)
                 + sd.T(x1 + 12, (Y(q) + Y(q + ecm)) / 2 + 22, '→ excitation', 20, sd.ORANGE, 'start')
                 + sd.T(x1 + 12, (Y(q + ecm) + Y(tot)) / 2 + 2, f'⅛ · E_p = {rec:.3f}', 21, sd.MUT, 'start', 600)
                 + sd.T(x1 + 12, Y(tot) - 14, '→ ⁸Be* keeps moving', 20, sd.MUT, 'start') + '</g>')
        # 4: the state
        g15 = 0.138 / 2
        lvtip = (f'E* = Q + ⅞·E_p = 17.255 + {ecm:.3f} = {es:.3f} MeV. The shaded band is the 18.15 MeV 1⁺ level ± Γ/2 (Γ = 138 keV): '
                 'E* inside it forms the resonance; outside it, capture is direct (C1b).')
        o.append(f'<g{sd.tipattr(lvtip)}>'
                 + f'<rect x="740" y="{Y(18.15 + g15):.1f}" width="160" height="{Y(18.15 - g15) - Y(18.15 + g15):.1f}" fill="{sd.ORANGE}" fill-opacity="0.15"/>'
                 + sd.line(740, Y(es), 900, Y(es), sd.ORANGE, 5)
                 + sd.T(820, Y(es) - 46, f'E* = {es:.3f}', 23, sd.ORANGE, weight=600) + '</g>')
        o.append(sd.T(905, Y(18.15 + g15) - 4, '18.15 level ± Γ/2', 17, sd.ORANGE, 'end'))
        dtip = (f'The excited ⁸Be* lives ~10⁻²¹ s and decays to the ground state. The photon gets E* minus a tiny recoil: '
                f'{r1.Egamma0_MeV:.3f} MeV. An IPC pair or an X17 gets the same energy.')
        o.append(f'<g{sd.tipattr(dtip)}>' + sd.arrow(800, Y(es) + 4, 800, y_gs - 6, sd.ORANGE, 3.5)
                 + sd.T(812, 400, 'γ₀, e⁺e⁻', 22, sd.ORANGE, 'start', 600) + sd.T(812, 426, 'or X17', 22, sd.BLUE, 'start', 600)
                 + sd.T(812, 452, f'carry {r1.Egamma0_MeV:.2f} MeV', 20, sd.ORANGE, 'start') + '</g>')
        o.append(sd.T(W / 2, H - 4, f'one capture at E_p = {r1.Ep_keV / 1e3:.3f} MeV; energies in MeV above the ⁸Be ground state', 19, sd.MUT))
        return sd.svg(W, H, ''.join(o), 'energy ladder of the capture')

    trows = [[f'{r.Ep_keV:.0f}' if r.Ep_keV != 441.4 else '441', f'{r.recoil_keV:.0f}', f'{r.Ecm_keV:.0f}', f'{r.Estar_MeV:.3f}']
             for r in (r0, r8, r1, r2)]
    side = sd.col(
        sd.callout('<b>① The masses.</b> ⁷Li plus a proton weigh 17.255 MeV more than ⁸Be. Merging them releases that, even with the proton at rest: the "Q value".', sd.GREY, 22),
        sd.callout('<b>② The beam adds on top.</b> Energy is conserved, so the proton\'s kinetic energy joins the pot. More E_p, more energy in the ⁸Be*: that is all "more beam energy gives a higher E*" means.', sd.RED, 22),
        sd.callout('<b>③ Only ⅞ of it counts.</b> The proton brings momentum; the merged ⁸Be* must carry it, so it moves, and that motion costs E_p·m_p/(m_p+m_Li) ≈ E_p/8. A ball thrown into a parked cart: they roll on together; only the rest becomes heat.', sd.ORANGE, 22),
        sd.table(['E_p [keV]', 'to motion', 'to E*', 'E* [MeV]'], trows, size=20, widths=[130, 120, 100, 130]),
        gap=12, w=620)
    D.slide('c-energy', sd.title('E* = 17.255 MeV from the masses + ⅞ of the beam energy',
                                 'The energy bookkeeping of one capture, to scale above 17 MeV. Hover each step.')
            + sd.row(ladder_svg(), side, gap=40),
            f"""<p><b>The rule.</b> Energy and momentum are both conserved when the proton and the ⁷Li merge. Before: a proton with kinetic
energy E_p and momentum p, a ⁷Li at rest, and the extra mass Q = m(p) + m(⁷Li) − m(⁸Be) = 17.255 MeV. After: a single ⁸Be*,
which must carry the momentum p, so it moves with kinetic energy p²/(2M₈) = E_p·m_p/M₈ ≈ E_p/8. What is left is the internal
(excitation) energy:</p>
<p style="text-align:center"><b>E* = Q + E_p · M(⁷Li)/(M(⁷Li) + m_p) = 17.255 + 0.875 · E_p</b></p>
<p>The 0.875·E_p is the <b>centre-of-mass energy</b>: the kinetic energy seen by someone riding along with the centre of mass, the only
frame in which the merged nucleus ends at rest. Physicists quote resonances in either frame; the deck uses lab E_p because that is
what the accelerator sets (441 keV lab = 386 keV cm).</p>
<p><b>Same at n_TOF:</b> E* = S_n + 0.75·E_n, because ³He is 3 mass units and the neutron 1 (¾ instead of ⅞). S_n = 20.577 MeV is the
same "masses" term. A thermal neutron brings ~0 kinetic energy, so the ILL makes ⁴He* right at 20.58 MeV.</p>
<p><b>The proton has a minimum it needs, the neutron does not.</b> The Coulomb barrier (≈1.3 MeV between p and ⁷Li) makes capture
rare below a few hundred keV; it falls off exponentially but is never zero (tunnelling). That is a probability statement (C1b),
not an energy one: the bookkeeping above holds at any E_p.</p>
<p>Numbers: <code>out/appendix/energy.csv</code> from <code>appendix_calc.energy_table</code> (relativistic; the ⅛ is exact to
0.1 %). Masses: AME2020 via <code>lnl_rates.py</code>; Q from Tilley 2004 (17.2551 MeV).</p>""",
            foot='Tilley et al., NPA 745 (2004); lnl/out/appendix/energy.csv', short='C1a E* bookkeeping')

    # ------------------------------------------------------------------ C1b
    e_ = ex[(ex.Ep_keV >= 300) & (ex.Ep_keV <= 1500)]
    P = sd.Plot(1000, 660, x=(300, 1500, 'lin'), y=(1, 1e4, 'log'), xlabel='beam energy E_p [keV]',
                ylabel='σ(p + ⁷Li → ⁸Be + γ₀) [µb]', margin=(64, 30, 92, 120))
    P.xticks([(v, str(v)) for v in range(300, 1501, 200)]).yticks(sd.log_ticks(0, 4))
    for es_ in (17.6, 17.8, 18.0, 18.2, 18.4):
        ep_ = (es_ - Q_PG) * 8 / 7 * 1e3
        P.raw(sd.T(P.X(ep_), P.y0 - 14, f'{es_:.1f}', 20, sd.ORANGE) + sd.line(P.X(ep_), P.y0, P.X(ep_), P.y0 + 10, sd.ORANGE, 2))
    P.raw(sd.T(P.X(300) - 8, P.y0 - 14, 'E* [MeV]:', 20, sd.ORANGE, 'end'))
    for ep_, gl, nm in ((441.4, 12.2, '17.64'), (1030.0, 168.0, '18.15')):
        P.band([ep_ - gl / 2, ep_ + gl / 2], [1, 1], [1e4, 1e4], sd.ORANGE, 0.12, tip=f'{nm} MeV level ± Γ/2 (Γ_lab = {gl:.0f} keV)')
    for c_, dsh, nm in (('res_17_64_g0_ub', '8 6', '17.64'), ('res_18_15_g0_ub', '3 6', '18.15')):
        r_ = e_[e_[c_] > 1]
        P.line(r_.Ep_keV, r_[c_], sd.ORANGE, 2.5, dash=dsh, markers=False, tip=f'the {nm} MeV resonance (M1)')
    d_ = e_[e_.Ep_keV >= 500]
    P.line(d_.Ep_keV, d_.direct_g0_ub, sd.PURPLE, 3, markers=False, tip='direct capture (E1): the measured σ minus both resonances')
    P.line(e_.Ep_keV, e_.sigma_g0_ub, sd.INK, 4, markers=False)
    pts = e_[e_.Ep_keV.isin([400, 441.0, 442.0, 600, 800, 1000, 1030, 1100, 1200, 1300, 1400])]
    pts = pts.drop_duplicates('Ep_keV')
    en_i = en.set_index('Ep_keV')
    tps = []
    for r in pts.itertuples():
        rr = en.iloc[(en.Ep_keV - r.Ep_keV).abs().argmin()]
        tps.append(f'E_p {r.Ep_keV:.0f} keV → E* = {Q_PG + 0.875 * r.Ep_keV / 1e3:.3f} MeV\nσ_γ₀ = {r.sigma_g0_ub:.1f} µb '
                   f'({r.res_17_64_g0_ub + r.res_18_15_g0_ub:.1f} resonant, {r.direct_g0_ub:.1f} direct)\nphoton energy ≈ {rr.Egamma0_MeV:.2f} MeV')
    P.line(pts.Ep_keV, pts.sigma_g0_ub, sd.INK, 0, r=6, tips=tps)
    P.text(470, 2500, '17.64: narrow and strong', 20, sd.ORANGE)
    P.text(1060, 60, '18.15: broad', 20, sd.ORANGE)
    P.text(1150, 9, 'direct capture', 20, sd.PURPLE)
    pk = e_.sigma_g0_ub.max()
    dmid = float(e_.set_index('Ep_keV').direct_g0_ub.loc[800])
    s18 = float(e_.set_index('Ep_keV').sigma_g0_ub.loc[1030])
    side = sd.col(
        sd.legend([('total γ₀ (measured)', sd.INK), ('17.64 resonance', sd.ORANGE, 'dash'), ('18.15 resonance', sd.ORANGE, 'dash'), ('direct capture', sd.PURPLE)], 20),
        sd.callout('<b>Levels this high are not sharp.</b> They fall apart in ~10⁻²¹ s, nearly always by throwing the proton back out. A short life means a spread in energy, the width Γ. An E* within ~Γ of a level still forms it.', sd.ORANGE, 22),
        sd.callout(f'<b>Between levels, capture still happens:</b> the proton is caught directly and radiates on the way in (E1). ~{dmid:.0f} µb, against {s18:.0f} µb on the 18.15 peak and {pk / 1e3:.1f} mb on 17.64.', sd.PURPLE, 22),
        sd.callout(f'<b>Either way, energy is exact.</b> The ⁸Be* forms at E* = 17.255 + ⅞E_p, whatever E_p is, and the photon (or pair, or X17) leaves with it: {r8.Egamma0_MeV:.2f} MeV at 0.80, {r2.Egamma0_MeV:.2f} at 1.225.', sd.BLUE, 22),
        sd.callout('<b>Like a radio dial:</b> you can tune to any frequency (E_p); the stations (levels) are where the signal is loud. 17.64 is a sharp, loud station; 18.15 a broad one, heard over ±80 keV of E_p.', sd.GREY, 22),
        gap=14, w=600)
    D.slide('c-res', sd.title('Any E_p makes ⁸Be*; the resonances are where it is likely',
                              'Capture cross section to the ground state against E_p (bottom) and the E* it makes (top). Hover the points and bands.')
            + sd.row(P.svg('sigma vs Ep with Estar axis'), side, gap=40),
            f"""<p><b>A common confusion.</b> If ⁸Be has levels at 17.64 and 18.15 MeV, how can E* take any value in between? Because the
states above the p + ⁷Li threshold (17.255 MeV) are unbound: the proton can leave again, and almost always does (Γ_p = 132 of the
138 keV width of the 18.15 level; the photon width is only 1.9 eV). Anything that lives ~10⁻²¹ s has an energy spread ħ/τ ≈ Γ.
So a "level" is a bump in probability, not a single allowed energy.</p>
<p><b>The cross section σ is that probability</b> (per proton, per ⁷Li per cm²). The curve is ATOMKI-independent data (Zahnow 1995),
split into two Breit–Wigner resonances and a smooth remainder, the direct E1 capture (main slide 4). Resonant capture: the proton
enters, a ⁸Be* lingers briefly at the level, then decays. Direct capture: the proton emits the photon as it passes, with no
intermediate state; it has no peak, just a slow rise as the Coulomb barrier gets easier.</p>
<p><b>What the beam energy does, then:</b> it sets E* exactly (C1a) and, through σ, how often a capture happens at all. On the 18.15
peak about half of the γ₀ is resonant (M1) and half direct (E1); at 0.80 MeV almost all is direct. This is why off-resonance runs
(C6) test whether the X17 comes from the 1⁺ state or from any transition at that E*.</p>
<p><b>In a real target</b> the beam slows as it crosses the film, so a thin film at 1.10 MeV spans E_p 1.10 → 1.04 MeV, i.e. E* 18.22 →
18.17 MeV: a 52 keV spread of photon energies, well inside the 18.15 level. A target that stops the beam spans everything down to 0
and so also crosses 441 keV (B1).</p>
<p>Curves: <code>out/figures/excitation.csv</code> (<code>lnl_rates.CrossSection</code>). Widths from Tilley 2004; Γ_lab = Γ_cm × 8/7. The direct-capture
curve is drawn from 500 keV: under the 441 keV peak it cannot be separated from the resonance.</p>""",
            foot='Zahnow et al., Z. Phys. A 351 (1995) via EXFOR A0639; Tilley et al., NPA 745 (2004)', short='C1b any E_p')

    # ------------------------------------------------------------------ C1c
    def budget_svg():
        W, H = 1080, 520
        xa, xb, elo, ehi = 220, 760, 16.0, 18.5
        X = lambda e: xa + (e - elo) / (ehi - elo) * (xb - xa)
        o = []
        rows = [(r0, '441 keV'), (r8, '800 keV'), (r1, '1030 keV'), (r2, '1225 keV')]
        y0, dy, bh = 90, 90, 50
        o.append(sd.T(80, 50, 'E_p', 22, sd.INK, 'middle', 600))
        o.append(sd.T(X(17.2), 50, 'the X17 energy E_X = E*', 22, sd.INK, 'middle', 600))
        o.append(sd.T(910, 50, 'leftover → speed → edge', 22, sd.INK, 'middle', 600))
        for i, (r, lab) in enumerate(rows):
            y = y0 + i * dy
            ke, bx_, th_ = r['KE_X_m16.7'], r['beta_X_m16.7'], r['theta_min_m16.7']
            o.append(sd.T(80, y + bh / 2 + 8, lab, 22, sd.RED, 'middle', 600))
            mt = f'16.7 MeV of the X17 energy is its mass: locked away, it cannot move the particle.'
            o.append(f'<g{sd.tipattr(mt)}><rect x="{xa - 40}" y="{y}" width="{X(16.7) - xa + 40:.1f}" height="{bh}" fill="{sd.GREY}" fill-opacity="0.35"/>'
                     + sd.T((xa - 40 + X(16.7)) / 2, y + bh / 2 + 8, 'mass 16.7', 21, sd.INK) + '</g>')
            kt = (f'E_p {r.Ep_keV:.0f} keV: E* = {r.Estar_MeV:.3f} MeV, E_X = {r["EX_m16.7"]:.3f} MeV, '
                  f'kinetic energy {ke:.3f} MeV → β = {bx_:.3f}, smallest opening angle {th_:.1f}°')
            o.append(f'<g{sd.tipattr(kt)}><rect x="{X(16.7):.1f}" y="{y}" width="{X(16.7 + ke) - X(16.7):.1f}" height="{bh}" fill="{sd.BLUE}" fill-opacity="0.8"/>'
                     + sd.T(X(16.7 + ke) - 8, y + bh / 2 + 8, f'+{ke:.2f}', 21, '#fff', 'end', 600)
                     + sd.T(830, y + bh / 2 + 8, f'β {bx_:.2f}', 22, sd.BLUE, 'start', 600)
                     + sd.T(925, y + bh / 2 + 8, f'edge {th_:.0f}°', 22, sd.PURPLE, 'start', 600) + '</g>')
        # zigzag break at the left of the bars
        yb0, yb1 = y0 - 10, y0 + 3 * dy + bh + 10
        zz = ' '.join(f'{xa - 40 + (8 if k % 2 else -8)},{yb0 + k * (yb1 - yb0) / 24:.1f}' for k in range(25))
        o.append(f'<polyline points="{zz}" fill="none" stroke="#fff" stroke-width="7"/>')
        ya = y0 + 3 * dy + bh + 30
        o.append(sd.line(xa - 40, ya, xb, ya, sd.MUT, 1.5))
        for e in (16.5, 17.0, 17.5, 18.0, 18.5):
            o.append(sd.line(X(e), ya, X(e), ya + 8, sd.MUT, 1.5) + sd.T(X(e), ya + 32, f'{e:g}', 20, sd.MUT))
        o.append(sd.T((xa + xb) / 2, ya + 62, 'MeV (axis starts at 16; the first 16 MeV of mass not drawn)', 19, sd.MUT))
        return sd.svg(W, H, ''.join(o), 'X17 energy budget against Ep')

    def perp_svg():
        W, H = 560, 520
        o = []
        ps_ = math.sqrt((M_X / 2) ** 2 - 0.511 ** 2)
        sc = 15
        for x0, r, lab, col in ((140, r0, 'E_p 441 keV', sd.ORANGE), (420, r2, 'E_p 1225 keV', sd.GREEN)):
            bx_ = r['beta_X_m16.7']
            gx_ = 1 / math.sqrt(1 - bx_ ** 2)
            pl = gx_ * bx_ * M_X / 2                        # each lepton's forward momentum
            y0 = 290
            o.append(sd.T(x0, 50, lab, 23, col, weight=600))
            o.append(sd.arrow(x0, y0 + 190, x0, y0 + 190 - gx_ * bx_ * M_X * sc, sd.BLUE, 5))
            o.append(sd.T(x0 + 10, y0 + 180, f'X17 p = {gx_ * bx_ * M_X:.1f}', 19, sd.BLUE, 'start'))
            for sgn in (1, -1):
                o.append(sd.arrow(x0, y0, x0 + sgn * ps_ * sc, y0 - pl * sc, sd.PURPLE, 3.5))
            a = 2 * math.degrees(math.atan2(ps_, pl))
            o.append(f'<circle cx="{x0}" cy="{y0}" r="8" fill="{sd.BLUE}"/>')
            o.append(sd.T(x0, y0 - pl * sc - 40, f'{a:.0f}°', 30, sd.PURPLE, weight=700))
            o.append(sd.T(x0, y0 - pl * sc - 16, f'forward push {pl:.1f} each', 18, sd.MUT))
        o.append(sd.T(W / 2, 100, 'e⁺ and e⁻ (purple): sideways 8.35 MeV/c each,', 19, sd.MUT))
        o.append(sd.T(W / 2, 124, 'the same in both cases', 19, sd.MUT))
        o.append(sd.T(W / 2, H - 6, 'decay ⊥ to the X17 motion (the edge); MeV/c, to scale', 18, sd.MUT))
        return sd.svg(W, H, ''.join(o), 'perpendicular decay slow vs fast X17')

    de = (r2.Estar_MeV - r0.Estar_MeV)
    dke = r2['KE_X_m16.7'] / r0['KE_X_m16.7'] - 1
    D.slide('c-lever', sd.title(f'Only E* − m ≈ {r1["KE_X_m16.7"]:.1f} MeV moves the X17, so E_p has leverage',
                                'Left: the X17 energy split into mass and motion (m = 16.7 MeV). Right: the decay at the edge, slow vs fast X17.')
            + sd.row(budget_svg(), perp_svg(), gap=24)
            + sd.row(sd.callout(f'<b>E_p 441 → 1225 keV raises E* by only {de * 1e3:.0f} keV ({de / r0.Estar_MeV * 100:.1f} %)</b>, but almost all of the X17\'s energy is its mass. The part left over to move it grows by {dke * 100:.0f} %.', sd.BLUE, 22),
                     sd.callout('<b>Faster X17, more forward push</b> on both leptons, smaller angle between them. The sideways part is fixed by the mass (m/2 each), so the edge is a mass measurement once E* is known.', sd.PURPLE, 22),
                     sd.callout('<b>Why IPC does not move:</b> a virtual photon has no fixed mass; its pairs take every opening angle, peaked at small ones. Only a real particle has an edge to move.', sd.GREY, 22), gap=28),
            f"""<p><b>The chain.</b> The X17 (if it exists) is emitted by the ⁸Be*, which sits nearly at rest (β ≈ 0.006, C4). The ⁸Be ground
state is 7455 MeV heavy and takes almost no recoil, so the X17 gets essentially all of E*: E_X = E* − ~0.003 MeV. Of that, m = 16.7 MeV is
rest mass; only the leftover E_X − m is kinetic energy, and it sets the speed: β = √(1 − (m/E_X)²).</p>
<p><b>The leverage.</b> Because E_X − m is small, a small change in E* is a big fractional change in kinetic energy: {r0['KE_X_m16.7']:.2f} MeV at
441 keV, {r1['KE_X_m16.7']:.2f} at 1030, {r2['KE_X_m16.7']:.2f} at 1225. The speed goes {r0['beta_X_m16.7']:.2f} → {r1['beta_X_m16.7']:.2f} → {r2['beta_X_m16.7']:.2f}.
A heavier X17 (m = 17.0) has even less left over ({r1['KE_X_m17.0']:.2f} MeV at 1030 keV) and opens wider, {r1['theta_min_m17.0']:.0f}° instead of {r1['theta_min_m16.7']:.0f}°.</p>
<p><b>The angle.</b> In the X17 frame the e⁺ and e⁻ leave back to back with p* = √((m/2)² − m_e²) = 8.35 MeV/c each. The edge (smallest
lab angle) is the decay perpendicular to the X17 motion: each lepton keeps its 8.35 MeV/c sideways and gains γβ·m/2 forward, so
tan(θ_min/2) = p*/(γβ·m/2), i.e. θ_min = 2·asin(m/E_X). A photon is the limit m → 0: no rest mass, all motion, θ → 0, which is why
IPC pairs crowd at small angles.</p>
<p>Numbers: <code>out/appendix/energy.csv</code> (<code>lnl_rates.x17_energy</code>, <code>theta_min</code>); main slide 5 plots θ_min
against E_p for three masses; C5 shows the full distributions.</p>""",
            foot='lnl/out/appendix/energy.csv', short='C1c E* → angle')
