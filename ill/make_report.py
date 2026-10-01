#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_report.py -- ``report.html`` for the ILL feasibility study.

One question: if the n_TOF apparatus ran on a reactor cold beam, what do our
own thermal results say it would see?  Built entirely from :mod:`ill_rates`,
so re-running after a number changes moves the figures, tables and prose
together.

    python ill/make_report.py          # -> ill/out/report.html
"""
from __future__ import annotations

import datetime as dt
import html
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import figstyle as FS  # noqa: E402  (vendored from nTof_x17)
from report_style import CSS, FONT_LINK  # noqa: E402
import ill_rates as R  # noqa: E402


def figure(name: str, caption: str, alt: str = '') -> str:
    return (f'<figure><a href="figures/{name}.png">'
            f'<img src="figures/{name}.png" alt="{html.escape(alt or caption)}">'
            f'</a><figcaption>{caption} '
            f'<a class="src" href="figures/{name}.csv">numbers &#8599;</a>'
            f'</figcaption></figure>')


def _number_sections(page: str) -> str:
    """Number the <h2> sections in document order."""
    import re
    n = [0]

    def sub(m):
        n[0] += 1
        return f'<h2><span class="n">{n[0]}</span>'
    return re.sub(r'<h2><span class="n">\d+</span>', sub, page)


def sci(x: float, d: int = 1) -> str:
    """1.2&times;10⁸ -- for rates that span ten decades."""
    if not np.isfinite(x) or x == 0:
        return '&mdash;'
    e = int(np.floor(np.log10(abs(x))))
    if -2 <= e <= 3:
        return f'{x:,.{max(0, d - e)}f}' if e < 1 else f'{x:,.0f}'
    m = x / 10 ** e
    sup = str(e).translate(str.maketrans('0123456789-', '⁰¹²³⁴⁵⁶⁷⁸⁹⁻'))
    return f'{m:.{d}f}&times;10{sup}'


# --------------------------------------------------------------------------- #
# figures
# --------------------------------------------------------------------------- #
def fig_reach(T: pd.DataFrame, od) -> None:
    """The smallest X17/IPC(M1) one cycle can see, against the absorbed rate,
    with where each configuration's ceiling and n_TOF sit on the same line."""
    FS.use()
    he3 = R.he3_per_absorption()
    r = np.logspace(5, 11.5, 200)
    y = np.array([R.min_ratio_3sigma(x, he3) for x in r])
    fig, ax = FS.figure(FS.FIG)
    ax.plot(r, y, color=FS.INK, lw=1.6)
    ax.axhline(R.X17_PER_M1_PAIR_REF, color=FS.COPPER, lw=1.0, ls='--')
    ax.text(1.3e5, R.X17_PER_M1_PAIR_REF * 1.15,
            'rate-table reference, X17/IPC = 2.5×10⁻²', color=FS.MUTED,
            fontsize=FS.BASE_PT * 0.85, va='bottom')
    pts = [('n_TOF >1 ms gate', 'n_TOF EAR2, >1 ms gate (reference)', 'o', 'right'),
           ('A: as-built capsule\n(Micromegas-limited)', 'A: capsule @ PF1B', 's', 'right'),
           ('B: Be-window cell,\ndesign point', 'B: Be-window cell @ PF1B, design point', 'D', 'left'),
           ('B: detector ceiling', 'B: Be-window cell @ PF1B', '^', 'left')]
    rows = []
    for lab, key, mk, side in pts:
        row = T.set_index('scenario').loc[key]
        x, yy = row.rate, row.min_ratio_3sigma_cycle
        ax.plot(x, yy, mk, ms=8, color=FS.ACCENT,
                markeredgecolor=FS.SURFACE, markeredgewidth=1.5, zorder=5)
        dx = 1.6 if side == 'right' else 1 / 1.6
        # left-hand labels sit below the line, right-hand ones above it
        ax.text(x * dx, yy * (1.05 if side == 'right' else 0.8), lab,
                fontsize=FS.BASE_PT * 0.85,
                ha='left' if side == 'right' else 'right',
                va='bottom' if side == 'right' else 'top', color=FS.INK)
        rows.append(dict(point=lab.replace('\n', ' '), rate=x, min_ratio=yy))
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('neutrons absorbed in the ³He per second')
    ax.set_ylabel('smallest X17 / IPC(M1) seen at 3σ\nin one 50-day cycle')
    FS.title(ax, 'One ILL cycle reaches 100× below the n_TOF thermal gate',
             'against the ³He wide-angle continuum only; ε = 4 % for both; '
             'any surviving wall pair raises the curve')
    FS.save(fig, od / 'figures' / 'reach', data={
        '': pd.DataFrame(dict(rate=r, min_ratio=y)), 'points': pd.DataFrame(rows)})


def fig_windows(W: pd.DataFrame, od) -> None:
    FS.use()
    W = W.iloc[::-1].reset_index(drop=True)
    fig, ax = FS.figure(FS.FIG)
    yy = np.arange(len(W))
    ax.barh(yy, W.captures_per_n, height=0.55, color=FS.ACCENT, left=1e-9)
    for i, v in enumerate(W.captures_per_n):
        ax.text(v * 1.25, i, f'{v:.1e}', va='center', fontsize=FS.BASE_PT * 0.85,
                color=FS.INK)
    he3 = R.he3_per_absorption()['ngamma']
    ax.axvline(he3, color=FS.COPPER, lw=1.0, ls='--')
    ax.text(he3 * 1.3, len(W) - 0.6, '³He(n,γ) itself', color=FS.MUTED,
            fontsize=FS.BASE_PT * 0.85)
    ax.set_yticks(yy, W.window)
    ax.set_xscale('log')
    ax.set_xlim(3e-9, 0.2)
    ax.grid(axis='y', visible=False)
    ax.set_xlabel('wall captures per neutron absorbed in the gas, PF1B spectrum')
    FS.title(ax, 'Dropping the 500 bar vessel removes 99 % of the wall captures',
             'single-pass n·σ·t·⟨λ/λ_th⟩; the capsule bar is the Geant4 contract '
             'rescaled to 4.25 Å')
    FS.save(fig, od / 'figures' / 'windows', data=W)


# --------------------------------------------------------------------------- #
# tables
# --------------------------------------------------------------------------- #
def scenario_table(T: pd.DataFrame) -> str:
    rows = []
    for _, r in T.iterrows():
        ref = 'n_TOF' in r.scenario
        cls = ' class="ref"' if ref else ''
        rows.append(
            f'<tr{cls}><th class="s">{html.escape(r.scenario)}'
            f'<span class="why">{html.escape(r.basis)}</span></th>'
            f'<td class="n">{sci(r.rate)}</td><td>{html.escape(r.binding)}</td>'
            f'<td class="n"><b>{sci(r.ntof_days_per_day)}</b></td>'
            f'<td class="n">{sci(r.ipc_gt109_per_day)}</td>'
            f'<td class="n">{sci(r.x17_ref_detected_per_cycle_lo)}&ndash;'
            f'{sci(r.x17_ref_detected_per_cycle_hi)}</td>'
            f'<td class="n">{sci(r.min_ratio_3sigma_cycle, 1)}</td>'
            f'<td class="n">{sci(r.trigger_hz)}</td>'
            f'<td class="n">{sci(r.s_over_b_trigger)}</td>'
            f'<td class="n">{sci(r.tritium_GBq_per_cycle, 2)}</td></tr>')
    return ('<div class="scroll"><table class="t"><thead><tr><th>scenario</th>'
            '<th>absorbed<br><span class="u">n/s</span></th><th>set by</th>'
            '<th>n_TOF gate-days<br><span class="u">per day</span></th>'
            '<th>³He pairs &gt;109&deg;<br><span class="u">made per day</span></th>'
            '<th>X17 in the trigger<br><span class="u">per cycle, at the reference'
            '</span></th>'
            '<th>smallest X17/IPC<br><span class="u">3&sigma;, one cycle</span></th>'
            '<th>trigger<br><span class="u">Hz</span></th>'
            '<th>S/B at trigger<br><span class="u">reference X17 : pair-tags</span></th>'
            '<th>tritium<br><span class="u">GBq per cycle</span></th>'
            '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>')


def limits_table(T: pd.DataFrame) -> str:
    rows = []
    for _, r in T[~T.scenario.str.contains('n_TOF')].iterrows():
        rows.append(f'<tr><th class="s">{html.escape(r.scenario)}</th>'
                    f'<td class="n">{sci(r.limit_beam)}</td>'
                    f'<td class="n">{sci(r.limit_trigger)}</td>'
                    f'<td class="n">{sci(r.limit_mm)}</td></tr>')
    return ('<table class="t"><thead><tr><th>scenario</th>'
            '<th>beam on the spot</th><th>DREAM &le; 1&nbsp;kHz</th>'
            '<th>Micromegas &le; 10&nbsp;% pile-up per &micro;s</th>'
            '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table>')


def beam_table() -> str:
    rows = []
    for b in R.BEAMS.values():
        rows.append(f'<tr><th class="s">{html.escape(b.label)}</th>'
                    f'<td class="n">{sci(b.capture_flux)}</td>'
                    f'<td class="n">{b.mean_lambda_A:.2f}&nbsp;&Aring;</td>'
                    f'<td class="n">{sci(b.particle_flux)}</td>'
                    f'<td class="n">{b.max_area_cm2:.0f}&nbsp;cm&sup2;</td>'
                    f'<td class="n">{sci(b.particle_flux * b.max_area_cm2)}</td></tr>')
    return ('<table class="t"><thead><tr><th>beam</th>'
            '<th>capture flux<br><span class="u">n/cm&sup2;/s</span></th>'
            '<th>mean &lambda;</th>'
            '<th>particle flux<br><span class="u">n/cm&sup2;/s</span></th>'
            '<th>cross-section</th><th>whole beam<br><span class="u">n/s</span></th>'
            '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table>')


def absorption_table(A: pd.DataFrame) -> str:
    P = A.pivot(index='pressure_bar', columns='lambda_A', values='abs_length_cm')
    hdr = ''.join(f'<th>{l:g}&nbsp;&Aring;</th>' for l in P.columns)
    body = ''.join(f'<tr><th class="s">{p:g} bar</th>'
                   + ''.join(f'<td class="n">{v:.2g}&nbsp;cm</td>' for v in r)
                   + '</tr>' for p, r in P.iterrows())
    return (f'<table class="t"><thead><tr><th>³He pressure</th>{hdr}</tr></thead>'
            f'<tbody>{body}</tbody></table>')


def polarised_table() -> str:
    rows = []
    for p in (0.6, 0.7, 0.8, 0.85):
        d = R.polarised(p, p_n=0.997)
        rows.append(f'<tr><th class="s">P(³He) = {p:.0%}</th>'
                    f'<td class="n">{d["parallel_m1_gain"]:.1f}&times;</td>'
                    f'<td class="n">{d["antiparallel_m1_gain"]:.2f}&times;</td>'
                    f'<td class="n"><b>{d["m1_contrast"]:.0f}</b></td>'
                    f'<td class="n"><b>{d["unpolarised_beam_m1_gain"]:.1f}&times;</b></td>'
                    f'<td class="n">{d["parallel_length_factor"]:.1f}&times;</td></tr>')
    return ('<table class="t"><thead><tr><th></th>'
            '<th>M1 pairs per absorption<br><span class="u">spins parallel</span></th>'
            '<th>M1 pairs per absorption<br><span class="u">antiparallel</span></th>'
            '<th>flip contrast<br><span class="u">P<sub>n</sub> = 99.7 %</span></th>'
            '<th>unpolarised beam<br><span class="u">on a polarised cell</span></th>'
            '<th>absorption length<br><span class="u">parallel neutrons</span></th>'
            '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table>')


# --------------------------------------------------------------------------- #
# page
# --------------------------------------------------------------------------- #
EXTRA_CSS = """
.scroll{overflow-x:auto}
tr.ref th,tr.ref td{color:var(--muted)}
"""


def build_html(T: pd.DataFrame, W: pd.DataFrame, A: pd.DataFrame) -> str:
    he3 = R.he3_per_absorption()
    s = T.set_index('scenario')
    nt = s.loc['n_TOF EAR2, >1 ms gate (reference)']
    a = s.loc['A: capsule @ PF1B']
    fi = s.loc['A: capsule @ FIPPS']
    b = s.loc['B: Be-window cell @ PF1B, design point']
    bc = s.loc['B: Be-window cell @ PF1B']
    pf = R.BEAMS['PF1B']
    kr = pf.k / R.K_NTOF
    wb = W.set_index('window')
    be_vs = float(wb.loc['0.5 mm Be', 'vs_capsule'])
    pol = R.polarised(0.75, p_n=0.997)
    gain_a = a.ntof_days_per_day
    gain_b = b.ntof_days_per_day

    return _number_sections(f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>The thermal X17 search at the ILL</title>
{FONT_LINK}
<style>{CSS}{EXTRA_CSS}</style>
</head>
<body>
<div class="wrap">
<header>
  <div class="eyebrow"><span class="badge">ILL</span>
    <span>X17 &middot; feasibility from our own thermal results</span>
    <span>{dt.date.today().isoformat()}</span></div>
  <h1>The thermal X17 search at the ILL</h1>
  <p class="sub">The same physics as n_TOF's &gt;1&nbsp;ms gate &middot; no flash
     &middot; no duty cycle &middot; and no reason left for a 500&nbsp;bar vessel</p>
</header>

<p class="lede"><b>Feasible, and the only way the thermal measurement becomes a
statistics-rich one &mdash; but it is the s-wave half of the physics only.</b>
Everything a reactor gives us is below 0.1&nbsp;eV, which is exactly n_TOF's
&gt;1&nbsp;ms gate, so the signal side is already settled: per neutron absorbed in
the gas, {sci(he3['pairs_total'])} pairs ({sci(he3['pairs_gt109'])} above 109&deg;),
whatever the wavelength. What changes is the neutron count. With the capsule
unchanged, PF1B is Micromegas-limited at <b>{sci(a.rate)}&nbsp;n/s</b> &mdash; one
ILL day is <b>{gain_a:,.0f}</b> n_TOF gate-days. Replace the 500&nbsp;bar vessel
with a few-bar cell behind a 0.5&nbsp;mm Be window, which a reactor beam allows
and n_TOF's never did, and the wall captures fall to <b>{be_vs:.1%}</b> of the
capsule's; at a conservative 10<sup>10</sup>&nbsp;n/s that is <b>{gain_b:,.0f}</b>
gate-days per day. One cycle then reaches X17/IPC(M1) of
<b>{b.min_ratio_3sigma_cycle:.1e}</b> against the &sup3;He continuum, against
{nt.min_ratio_3sigma_cycle:.2f} for n_TOF's thermal gate over the same 50 days.
What it cannot do is reach the p-wave states (0<sup>&minus;</sup>,
1<sup>&minus;</sup>, 2<sup>&minus;</sup>) that the ATOMKI &sup3;H(p,e<sup>+</sup>e<sup>&minus;</sup>)
fit is built on. That is n_TOF's MeV window, and the ILL does not replace it.</p>

<div class="cards">
  <div class="card"><div class="v">{gain_a:,.0f}&times;</div>
    <div class="l">n_TOF thermal-gate days per ILL day, as-built capsule
      (detector-limited)</div></div>
  <div class="card"><div class="v">{gain_b:,.0f}&times;</div>
    <div class="l">the same, with a Be-window cell at a conservative
      10<sup>10</sup>&nbsp;n/s</div></div>
  <div class="card"><div class="v">{1 / be_vs:.0f}&times;</div>
    <div class="l">fewer wall captures per neutron: 0.5&nbsp;mm Be against the
      5.5&nbsp;mm Al nose</div></div>
  <div class="card"><div class="v">{nt.min_ratio_3sigma_cycle / b.min_ratio_3sigma_cycle:.0f}&times;</div>
    <div class="l">smaller X17/IPC reachable in one cycle than in 50 days of the
      n_TOF thermal gate</div></div>
</div>

<h2><span class="n">1</span>Why our thermal results transfer directly</h2>
<p>Below a few eV both &sup3;He channels and every wall capture go as
1/<i>v</i>. Two consequences follow, and they are what this whole page rests on.
<b>The gas is wavelength-blind:</b> it absorbs essentially every neutron that
enters, and the fraction of absorptions that are radiative,
55&nbsp;&micro;b&nbsp;/&nbsp;5333&nbsp;b = {he3['ngamma']:.2e}, is a ratio of two
1/<i>v</i> cross sections. The pair yield is set by the two s-wave channels in
<code>ipc_channels</code>: M1 from the 1<sup>+</sup> (&sup3;S&#8321;) and E0 from
the 0<sup>+</sup> (&sup1;S&#8320;), {he3['e0_share']:.0%} E0. None of it moves
between n_TOF's gate and a cold beam. <b>A thin wall is not wavelength-blind:</b>
its capture probability per neutron goes as
<i>n</i>&sigma;<sub>th</sub><i>t</i>&#10216;&lambda;/&lambda;<sub>th</sub>&#10217;.
For the EAR2 in-gate flux that weight is {R.K_NTOF:.2f} (computed from the
Ph3 flux file; a 5.5&nbsp;mm Al nose then gives 4.96&times;10<sup>&minus;3</sup>
against the Geant4 contract's 4.99&times;10<sup>&minus;3</sup>). At PF1B it is
{pf.k:.2f}. So <b>the same capsule makes {kr:.1f}&times; more wall background per
absorbed neutron at the ILL</b>, and that factor is the bridge that carries every
Geant4 number across.</p>

<h2><span class="n">2</span>The beams</h2>
{beam_table()}
<p>The capture flux is the thermal-equivalent flux that 1/<i>v</i> rates scale
with. The opaque gas counts particles, not capture flux, so particle flux is the
capture flux divided by &lambda;/&lambda;<sub>th</sub>. The FIPPS wavelength is an
assumption (thermal guide H22). Fluxes are quoted at full power. The 2025&ndash;26
cycles ran at 41&ndash;56&nbsp;MW against ~57 nominal. That matters only when
the beam is the binding limit, and for PF1B it is not.
<code>FACILITY.md</code> has the sources and everything else found about the
site.</p>

<h2><span class="n">3</span>What limits the rate</h2>
{limits_table(T)}
<p>Three ceilings, each on the neutrons absorbed per second. <b>Beam</b>: the
particle flux on the target face. That is a Ø20&nbsp;mm spot for the capsule,
20&nbsp;cm&sup2; for a cell, and never more than the whole guide.
<b>Trigger</b>: the production thermal menu (2 SiPM legs &ge;&nbsp;0.5&nbsp;MIP
+ &ge;&nbsp;1 plastic at 1&nbsp;MIP) fires on
{R.NTOF_PAIRTAGS_MENU:.1e} pair-tags per neutron at n_TOF. DREAM is held to
1&nbsp;kHz, which is about what it ran in a beam burst; a sustained continuous
rate has never been measured. <b>Micromegas</b>: the Geant4 rate of prompt drift-gap
charge, shared over four arms, with at most 10&nbsp;% chance of a second event
in a 1&nbsp;&micro;s drift window. With the capsule the trigger and the
chambers bind together at {sci(a.rate)}&nbsp;n/s, well below what PF1B can
deliver to a 2&nbsp;cm spot, so the capsule wastes most of PF1B. FIPPS's
halo-free pencil beam fits the capsule's bore almost exactly, and there the
beam binds at {sci(fi.rate)}&nbsp;n/s, which is still {fi.ntof_days_per_day:,.0f}
gate-days per day.</p>

<h2><span class="n">4</span>The capsule is the problem, and at a reactor it is optional</h2>
{figure('windows', 'Wall captures per neutron absorbed in the gas, on the PF1B '
        'spectrum. The capsule bar is the Geant4 nose-first contract rescaled '
        'by the 1/v weight; the windows are single-pass n&sigma;t. The dashed '
        'line is the &sup3;He radiative capture itself, the thing being '
        'measured.')}
<p>The 500&nbsp;bar vessel was forced by n_TOF: the gas had to be opaque at
eV energies with only a 2&nbsp;cm bore, so the &sup3;He went to 500&nbsp;bar and
the nose went to 5.5&nbsp;mm of aluminium. At 4&nbsp;&Aring; the gas is
11,000&nbsp;b per atom. A few bar absorbs everything within centimetres:</p>
{absorption_table(A)}
<p>Three things follow from that table.
<b>(i) The window can be thin and need not be aluminium.</b> 0.5&nbsp;mm of Be,
a standard pressure-window material that is also transparent to coherent
scattering above its 3.96&nbsp;&Aring; Bragg edge, makes {1 / be_vs:.0f}&times;
fewer captures than the nose. External conversion in the window falls a further
{R.NTOF_NOSE_T_OVER_X0 / R.WINDOWS['be05'].t_over_x0:.0f}&times; (t/X<sub>0</sub>).
Graphite or CVD diamond is better again, and its 4.95&nbsp;MeV line is the
softest on offer.
<b>(ii) The cell is its own beam stop.</b> An opaque &sup3;He volume makes no
capture &gamma; except the one we want, so there is no downstream wall at all.
That is the reason &sup3;He beam stops are used at PGAA stations.
<b>(iii) Below ~0.3&nbsp;bar the source has length.</b> The absorption length
becomes longer than our pair-vertex blur along the beam (~28&nbsp;mm, from
<code>ntof_athens_26/pair_vertex_imaging</code>). Window-born pairs then sit at
one end of a measured distribution instead of on top of the gas pairs, as they
did at 500&nbsp;bar, where half the absorptions are within 0.19&nbsp;mm of the
nose. The cost is an extended source in a detector built around a point source,
and that trade is exactly what the simulation has to settle.</p>

<h2><span class="n">5</span>What one cycle buys</h2>
{scenario_table(T)}
{figure('reach', 'The smallest X17/IPC(M1) ratio one 50-day cycle sees at '
        '3&sigma;, against the absorbed-neutron rate, counting only the '
        '&sup3;He wide-angle continuum as background (4&nbsp;% efficiency for '
        'both). The markers put the n_TOF thermal gate and the ILL options on '
        'the same line; the configurations differ only in how far along it '
        'their detector ceiling lets them go.')}
<p>Read the table in this order. <b>Gate-days per day</b> is the only number
that does not depend on any signal model, and it is what the ILL is: n_TOF's
thermal gate at {gain_a:,.0f}&ndash;{gain_b:,.0f}&times; the speed, with no flash
and no 1&ndash;5&nbsp;ms recovery band. <b>The X17 columns</b> use the rate
table's X17/IPC&nbsp;=&nbsp;2.5&times;10<sup>&minus;2</sup>, applied to the M1
pairs only, because a vector, axial or pseudoscalar boson cannot leave a
0<sup>+</sup>&rarr;0<sup>+</sup> transition. That number is a reference
normalisation, not a prediction, and that is why the next column quotes the
smallest ratio a cycle can see instead. <b>S/B at the trigger</b> is the
uncomfortable column. The menu's pair-tags are 92&nbsp;% two Compton photons of
one wall capture, and the capsule leaves the triggered sample at
{a.s_over_b_trigger:.0e}. The Be cell improves that {b.s_over_b_trigger / a.s_over_b_trigger:.0f}&times;,
but the offline rejection (two MM tracks pointing at the cell, opening angle,
LS energy) still has to supply the remaining orders of magnitude, at the ILL
exactly as at n_TOF. Wall <i>internal</i> pairs carry at most 6.7&nbsp;MeV
between both legs, so they cannot pass a &ge;&nbsp;4&nbsp;MeV-per-leg menu.
<b>Tritium</b>: every absorption makes a triton. At the design point the
cell holds {b.tritium_GBq_per_cycle:.2f}&nbsp;GBq after a cycle, and at PF1B's
detector ceiling it holds {bc.tritium_GBq_per_cycle:.1f}&nbsp;GBq. ILL health
physics will want this in the proposal.</p>

<h2><span class="n">6</span>What the ILL can do that n_TOF cannot</h2>
<p><b>Choose the entrance channel.</b> The &sup3;He(n,p) and the E0 pairs come
only from the spin-singlet 0<sup>+</sup>, and the (n,&gamma;) and the M1 pairs
only from the triplet 1<sup>+</sup>. PF1B delivers a 99.7&nbsp;% polarised beam
(at 3&times;10<sup>9</sup> capture flux), and the ILL's own Tyrex station fills
&sup3;He spin-filter cells at 70&ndash;80&nbsp;%. With both polarised, flipping
the neutron spin moves the pair yield between the two channels:</p>
{polarised_table()}
<p>At P(&sup3;He)&nbsp;=&nbsp;75&nbsp;% the M1 share swings
{pol['m1_contrast']:.0f}&times; between the two spin states, at the same cell,
detector and background. That measures the E0 fraction directly. It is the
6&ndash;52&nbsp;% band that <code>IPC_MISSING.md</code> cannot close by
calculation, and it is tied to the &alpha;-particle monopole matrix element that
ab initio theory does not reproduce. For the X17 search, a V, A or P boson can
only come from the 1<sup>+</sup>, and an S boson only from the 0<sup>+</sup>. So a
spin-flip asymmetry in an angular excess would identify the boson's quantum
numbers, which nothing at n_TOF can do. The parallel state also makes the gas
{pol['parallel_length_factor']:.0f}&times; more transparent, so that cell must be
longer.</p>
<p><b>A polarised cell raises the yield even without a polarised beam.</b>
In an opaque polarised cell, the antiparallel half of an unpolarised beam is
absorbed at the front by (n,p). The parallel half penetrates and captures
mostly through the triplet. Per absorbed neutron that gives
{pol['unpolarised_beam_m1_gain']:.1f}&times; the M1 pairs at
P(³He)&nbsp;=&nbsp;75&nbsp;%, the only way found past the thermal
self-shielding ceiling. The price is the cell itself: polarised ³He needs
glass or Si walls, not Be, and those put back ~10&times; of the wall captures
(<code>POLARISED.md</code> &sect;3). There is also a real in-beam risk, since
(n,p) ionisation relaxes polarised ³He (&sect;5 there).</p>

<h2><span class="n">7</span>What the result does not rule out</h2>
<ul>
<li><b>Ambient, cosmic and beam-borne backgrounds are not in any number here.</b>
They are site properties and do not scale from n_TOF. Configuration B makes the
capsule term small enough that these probably become the floor. Continuous running
also gives cosmics ~150&times; the live time per day of n_TOF's gate, though per
absorbed neutron they are ~10&times; less. A cosmic muon through two opposite
arms looks like a back-to-back pair. Measure the hall before designing to it.</li>
<li><b>Configuration B is an analytic scaling</b> of the Geant4 contract by
window captures and t/X<sub>0</sub>. Material-specific cascades (Be's 3.4&nbsp;MeV
lines, Mg's 11&nbsp;MeV line), scattering into the scintillators and the cell's
side walls are not modelled. <code>GEANT_PLAN.md</code> replaces this with a
simulation.</li>
<li><b>The signal strength at thermal energies is unknown.</b> The ATOMKI
&sup4;He fit (Viviani et&nbsp;al., PRC&nbsp;105, 014001) is driven by the
0<sup>&minus;</sup>/1<sup>&minus;</sup> p-wave states, which are suppressed by
10<sup>&minus;5</sup> below 2&nbsp;eV. What the fitted vector or axial couplings
predict for the 1<sup>+</sup>&rarr;0<sup>+</sup> thermal channel is one run of
their code at E<sub>n</sub>&nbsp;&lt;&nbsp;10&nbsp;eV. The thermal M1 photon is
itself strongly hindered (it is meson-exchange dominated), so the X17-to-photon
ratio there could be far from the MeV value in either direction. Until that is
asked, an ILL run is a precision measurement of the thermal pair continuum with
an X17 search attached, not the other way round.</li>
<li><b>DREAM's continuous trigger rate</b> is assumed to be 1&nbsp;kHz. If it
is lower, the as-built capsule's ceiling falls with it, but the Be cell's
design point does not move.</li>
<li><b>The efficiencies</b> (4&ndash;7&nbsp;% trigger, 28&nbsp;% MM-double) are
for a point source at the capsule position. An extended low-pressure source
changes them.</li>
</ul>
<p class="foot">Generated by <code>x17_facility_search/ill/make_report.py</code>
from <code>ill_rates.py</code>; the n_TOF side is the Geant4 thermal-accounting
contract (nTof_x17 <code>ntof_athens_26/data/thermal_accounting/accounting.json</code>),
re-checked on every run when that checkout is present.</p>
</div>
</body>
</html>
""")


def main() -> int:
    od = R.out_dir()
    T = R.scenario_table()
    W = R.window_table()
    A = R.he3_cell_design()
    fig_reach(T, od)
    fig_windows(W, od)
    T.to_csv(od / 'scenarios.csv', index=False)
    (od / 'report.html').write_text(build_html(T, W, A))
    print(f'  -> {od / "report.html"}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
