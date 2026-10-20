"""deck_common.py -- pieces shared by the FRM II MEDAPP and Birmingham slide notes
(frm2_medapp/deck/build_deck.py, birmingham/deck/build_deck.py): the Europe map, the cartoon
primitives, and the Geant4 soft-beam singles slide.
"""
from __future__ import annotations

import json
import math
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.expanduser(os.environ.get(
    'SLIDEDOC_DIR', '~/PycharmProjects/dylan-cern-site/scripts')))
import slidedoc as sd  # noqa: E402
from slidedoc import term, sci  # noqa: E402,F401

HERE = Path(__file__).resolve().parent
WORLD = Path(os.path.expanduser('~/PycharmProjects/dylan-cern-site/data/world-map.json'))
A1, A2, A3, A4 = 1.340264, -0.081106, 0.000893, 0.003796
M = math.sqrt(3) / 2

# lat, lon; the facilities this study compares
SITES = {
    'CERN n_TOF': (46.234, 6.046),
    'ILL Grenoble': (45.207, 5.693),
    'GANIL NFS': (49.214, -0.367),
    'LNL Legnaro': (45.353, 11.948),
    'FRM II Garching': (48.266, 11.671),
    'Birmingham': (52.450, -1.930),
    'Demokritos': (37.999, 23.817),
}


def equal_earth(lon, lat):
    lam, phi = math.radians(lon), math.radians(lat)
    th = math.asin(M * math.sin(phi))
    t2 = th * th
    t6 = t2 * t2 * t2
    x = lam * math.cos(th) / (M * (A1 + 3 * A2 * t2 + t6 * (7 * A3 + 9 * A4 * t2)))
    y = th * (A1 + A2 * t2 + t6 * (A3 + A4 * t2))
    return x, -y


def europe_map(w, h, highlight, lon=(-11.0, 27.0), lat=(35.0, 59.5), labels=None):
    """Europe from the site's pre-projected Natural Earth 110m map, with the study sites.
    highlight: the site drawn large; labels: {site: (dx, dy, anchor)} offsets in px."""
    d = json.loads(WORLD.read_text())
    x0, y1 = equal_earth(lon[0], lat[0])
    x1, y0 = equal_earth(lon[1], lat[1])
    x0 = min(x0, equal_earth(lon[0], lat[1])[0])
    sx = w / (x1 - x0)
    sy = h / (y1 - y0)
    s = min(sx, sy)
    ox, oy = -x0 * s, -y0 * s
    land = (f'<g transform="translate({ox:.2f},{oy:.2f}) scale({s:.3f})">'
            f'<path d="{d["land"]}" fill="#e2ddd2" stroke="#c9c2b4" stroke-width="{1.2 / s:.5f}"/>'
            f'<path d="{d["borders"]}" fill="none" stroke="#cfc8ba" stroke-width="{0.8 / s:.5f}"/></g>')
    out = [f'<rect x="0" y="0" width="{w}" height="{h}" rx="16" fill="#eef1f4"/>',
           f'<clipPath id="eu"><rect x="0" y="0" width="{w}" height="{h}" rx="16"/></clipPath>',
           f'<g clip-path="url(#eu)">{land}</g>']
    labels = {'ILL Grenoble': (-14, 20, 'end'), 'CERN n_TOF': (14, -6, 'start'), **(labels or {})}
    for name, (la, lo) in SITES.items():
        px, py = equal_earth(lo, la)
        px, py = px * s + ox, py * s + oy
        big = name == highlight
        col = sd.RED if big else sd.GREY
        r = 13 if big else 7
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r}" fill="{col}" stroke="#fff" stroke-width="3"'
                   f'{sd.tipattr(f"{name}: {la:.2f} N, {lo:.2f} E")}/>')
        dx, dy, anc = labels.get(name, (16, 8, 'start'))
        out.append(sd.T(px + dx, py + dy, name, 30 if big else 21, sd.INK if big else sd.MUT, anc, 600 if big else 400))
    return sd.svg(w, h, ''.join(out), f'map: {highlight}')


def box(x, y, w, h, label, fill='#fff', stroke=sd.INK, size=21, sub=None, tip=None, color=sd.INK, rx=8):
    """a labelled rectangle for beamline cartoons."""
    s = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" '
         f'stroke-width="2.5"{sd.tipattr(tip)}/>')
    if label:
        cy = y + h / 2 + (size * 0.35 if not sub else -2)
        s += sd.T(x + w / 2, cy, label, size, color, 'middle', 600)
    if sub:
        s += sd.T(x + w / 2, y + h / 2 + size, sub, size - 4, sd.MUT)
    return s


def arms(cx, cy, scale=1.0, tip='the four MX17 arms (Micromegas TPC, SiPM wall, 75 cm plastics) around the cell'):
    """side/top view of the MX17 cell + arms, beam along +x, centred at (cx, cy): the two in-plane arms
    as slabs above and below the beam, the two out-of-plane ones as a dashed outline over the cell."""
    L, R = 120 * scale, 16 * scale
    g, t, hw = 52 * scale, 46 * scale, 70 * scale
    out = [f'<rect x="{cx - hw:.1f}" y="{cy - hw:.1f}" width="{2 * hw:.1f}" height="{2 * hw:.1f}" fill="none" '
           f'stroke="{sd.PURPLE}" stroke-width="2" stroke-dasharray="6 5"{sd.tipattr("the out-of-plane pair of arms")}/>']
    for sgn in (-1, 1):
        y0 = cy + sgn * g - (t if sgn < 0 else 0)
        out.append(f'<rect x="{cx - hw:.1f}" y="{y0:.1f}" width="{2 * hw:.1f}" height="{t:.1f}" rx="4" fill="#dccff0" '
                   f'stroke="{sd.PURPLE}" stroke-width="2.5"{sd.tipattr(tip)}/>')
    out.append(f'<rect x="{cx - L / 2:.1f}" y="{cy - R:.1f}" width="{L:.1f}" height="{2 * R:.1f}" rx="6" '
               f'fill="#f6e8c9" stroke="{sd.GOLD}" stroke-width="2.5"'
               f'{sd.tipattr("³He cell: 30 bar × 40 cm, Ø10 cm (the NFS cell)")}/>')
    return ''.join(out)


def beam_arrow(x1, x2, y, color=sd.BLUE, w=8, label=None, size=21):
    s = sd.arrow(x1, y, x2, y, color, w, 22)
    if label:
        s += sd.T((x1 + x2) / 2, y - 14, label, size, color)
    return s


def plain(s):
    return re.sub('<[^>]+>', '', s)


# --------------------------------------------------------------------------- #
# data shared by both decks
# --------------------------------------------------------------------------- #
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / 'frm2_medapp'))
sys.path.insert(0, str(ROOT / 'birmingham'))
if not hasattr(np, 'trapezoid'):
    np.trapezoid = np.trapz
RHO = 1.5e-3                     # ATOMKI ⁴He, X17/IPC
HW = 'big plastics'


def load():
    o = HERE / 'out'
    d = dict(reach=pd.read_csv(o / 'soft_reach.csv'), comp=pd.read_csv(o / 'soft_components.csv'),
             thr=pd.read_csv(o / 'soft_throttle.csv'), sing=pd.read_csv(o / 'singles_vs_E.csv'))
    f = pd.read_csv(ROOT / 'survey' / 'out' / 'fast_reach.csv')
    f = f[(f.hw == HW) & (f.days == 50) & (f.signal == 'E* ≤ 22 MeV')]
    d['survey'] = f
    a = pd.read_csv(ROOT / 'survey' / 'out' / 'absorbed_reach.csv')
    d['pf1b'] = float(a[(a.key == 'pf1b') & (a.scenario == 'MM occ + DREAM')].rho3_50d.iloc[0])
    d['nfs'] = float(f[(f.key == 'nfs') & (f.singles_model == 'geant')].rho3.iloc[0])
    d['ear2'] = float(f[(f.key == 'ear2') & (f.singles_model == 'geant')].rho3.iloc[0])
    return d


def R(d, key, hw=HW, days=50, signal='E* ≤ 22 MeV', col='rho3'):
    r = d['reach']
    q = r[(r.key == key) & (r.hw == hw) & (r.days == days) & (r.signal == signal)]
    return float(q[col].iloc[0]) if len(q) else float('nan')


def Cp(d, key, col, hw=HW):
    c = d['comp']
    return float(c[(c.key == key) & (c.hw == hw)][col].iloc[0])


def days_to_atomki(rho):
    return 50.0 * (rho / RHO) ** 2


def fmt_days(x):
    return f'{x:.1f} d' if x < 10 else f'{x:.0f} d'


def spectrum_plot(w, h, highlight):
    """E dN/dE (unit area in ln E) for MEDAPP, Birmingham 2.8 MeV and NFS, with the 0.2-2.75 MeV window."""
    import medapp_beam as MB
    import bham_beam as BB
    e = np.geomspace(0.01, 40, 600)
    fold = pd.read_csv(ROOT / 'ganil_nfs' / 'out' / 'fold_table.csv')
    nfs = np.interp(e, fold.E_n, fold.n_per_s_MeV, left=0, right=0)
    nfs = nfs / np.trapezoid(nfs, e)
    curves = [('FRM II MEDAPP (fission)', MB.neutron_spectrum(e), sd.RED if highlight == 'medapp' else sd.ORANGE),
              ('Birmingham ⁷Li(p,n), 2.8 MeV', BB.spectrum_on_grid(2.8, e), sd.RED if highlight == 'bham' else sd.ORANGE),
              ('GANIL NFS d(40)+Be', nfs, sd.GREY)]
    P = sd.Plot(w, h, x=(0.01, 40, 'log'), y=(0, 1.0, 'lin'), xlabel='neutron energy E_n [MeV]',
                ylabel='E dN/dE (peak = 1)')
    P.xticks([(v, f'{v:g}') for v in (0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30)]).yticks([(v, f'{v:g}') for v in (0, .25, .5, .75, 1)])
    P.band([0.2, 2.75], [0, 0], [1.0, 1.0], sd.GREEN, 0.08, tip='E_n 0.2-2.75 MeV: E* ≤ 22.1 MeV, θ_min ≥ 99°: the ATOMKI-like window')
    P.text(0.21, 0.95, 'ATOMKI-like window', 22, sd.GREEN)
    fr = {}
    for name, f, col in curves:
        y = e * f
        m = (e >= 0.2) & (e <= 2.75)
        fr[name] = float(np.trapezoid(f[m], e[m]))
        tip = f'{name}: {100 * fr[name]:.0f} % of the neutrons in 0.2-2.75 MeV'
        P.line(list(e), list(y / y.max()), col, markers=False, w=4 if col == sd.RED else 3, tip=tip)
    leg = sd.legend([(n, c) for n, _, c in curves], size=22)
    return P.svg('neutron spectra'), leg, fr


def singles_plot(d, w, h, hw=HW):
    """ok singles per arm per incident neutron / photon vs its energy (N5, G5, G6), with the survey's
    N4 table and its flat bound."""
    s = d['sing'][d['sing'].hw == hw]
    P = sd.Plot(w, h, x=(1e-3, 20, 'log'), y=(1e-8, 3e-4, 'log'), xlabel='energy of the incident neutron or photon [MeV]',
                ylabel='singles per arm per incident particle')
    P.xticks([(v, f'{v:g}') for v in (0.001, 0.01, 0.1, 1, 10)]).yticks(sd.log_ticks(-8, -4))
    P.band([0.2, 2.75], [1e-8, 1e-8], [3e-4, 3e-4], sd.GREEN, 0.07, tip='the ATOMKI-like window')
    flat = float(s[s.kind == 'survey flat'].per_arm.iloc[0])
    P.hline(flat, sd.GREY, label='survey pessimistic bound (NFS average)', anchor='start', tip=f'{flat:.2g} per arm per neutron')
    for part, col, lab in (('neutron', sd.BLUE, 'neutrons (N5)'), ('gamma', sd.ORANGE, 'photons (G5/G6)')):
        q = s[(s.particle == part) & (s.kind == 'ok')].sort_values('E')
        if part == 'gamma' and 'run' in q:
            q = pd.concat([q[(q.run == 'G5_beam_gamma') & ((q.hi <= 14) | ~q.run.eq('G6_beam_gamma').any())],
                           q[q.run == 'G6_beam_gamma']]).sort_values('E')
        ys = [v if v > 0 else None for v in q.per_arm]
        tips = [f'{lab}, {a:.3g}-{b:.3g} MeV: {v:.2g} per arm ({int(k)} MC singles)' if v > 0 else ''
                for a, b, v, k in zip(q.lo, q.hi, q.per_arm, q.n_mc)]
        P.line(list(q.E), ys, col, r=6, tips=tips)
    q = s[s.kind == 'survey N4']
    P.points([x for x, v in zip(q.E, q.per_arm) if v > 0], [v for v in q.per_arm if v > 0], sd.GREY, r=7,
             tips=[f'survey N4 table (NFS forced run), {a:g}-{b:g} MeV: {v:.2g}' for a, b, v in zip(q.lo, q.hi, q.per_arm) if v > 0])
    leg = sd.legend([('neutrons, Geant4 N5', sd.BLUE), ('photons, Geant4 G5/G6', sd.ORANGE),
                     ('survey: NFS N4 table', sd.GREY, 'dot'), ('survey: flat bound', sd.GREY, 'dash')], size=22)
    return P.svg('singles per incident particle'), leg


def throttle_plot(d, w, h, keys, refs=True):
    """reach (50 d, E* ≤ 22, big plastics) vs neutrons/s through the cell, one curve per source key."""
    t = d['thr'][(d['thr'].signal == 'E* ≤ 22')]
    P = sd.Plot(w, h, x=(1e6, 5e10, 'log'), y=(5e-5, 0.05, 'log'), xlabel='neutrons/s through the Ø8 cm cell spot (throttled)',
                ylabel='X17/IPC at 3σ in 50 days')
    P.xticks(sd.log_ticks(6, 10)).yticks(sd.log_ticks(-4, -2))
    P.hline(RHO, sd.GREEN, label='ATOMKI ⁴He 1.5×10⁻³', tip='PRC 104 044003, X17/IPC; the repo convention')
    if refs:
        P.hline(d['pf1b'], sd.GREY, label=f'ILL PF1B, best ({d["pf1b"]:.1e})', anchor='start',
                tip='survey_absorbed.py: the ILL Geant4 walls at the best absorbed rate')
    legs = []
    for key, col, lab, dash in keys:
        q = t[t.key == key].sort_values('n_cell')
        ys = [v if np.isfinite(v) and v < 0.05 else None for v in q.rho3]
        P.line(list(q.n_cell), ys, col, dash=dash, markers=False, w=4,
               tip=f'{lab}: best {np.nanmin(q.rho3):.2g}')
        b = q.loc[q.rho3.idxmin()]
        P.points([b.n_cell], [b.rho3], col, r=10, tips=[f'{lab}: best {b.rho3:.2g} at {b.n_cell:.2g} n/s (throttle {b.throttle:.2g})'])
        legs.append((lab, col, 'dash' if dash else 'line'))
    return P.svg('reach vs rate'), sd.legend(legs, size=22)


def budget_bars(d, key, width=760):
    """per day in the 100-150° window at the best throttle (50 d), big plastics."""
    r = d['reach']
    q = r[(r.key == key) & (r.hw == HW) & (r.days == 50) & (r.signal == 'E* ≤ 22 MeV')].iloc[0]
    rows = [('IPC (E1)', q.IPC_win_per_day, sd.BLUE, 'Born E1 IPC through the same cuts'),
            ('cosmics', q.cosmic_win_per_day, sd.GREY, 'LNL L4 cosmic tables, no veto'),
            ('accidentals', q.acc_win_per_day, sd.ORANGE, 'two singles from different particles within ±5 ns'),
            ('correlated beam', q.corr_win_per_day, sd.RED, 'same-event two-arm beam background (factorised)'),
            ('X17 at ATOMKI', q.X17_win_per_day, sd.GREEN, 'X17/IPC = 1.5×10⁻³')]
    vmax = max(v for _, v, _, _ in rows) * 1.2
    vmin = 1.0
    hb = sd.hbars([(n, max(v, vmin), c, f'{n}: {v:,.0f} per day in 100-150°. {t}') for n, v, c, t in rows],
                  vmax, width=width, log=True, vmin=vmin, label_w=260, fmt=lambda v: f'{v:,.0f}')
    return hb, q


def compare_bars(d, here_keys, width=420):
    """the 50-day reach of the studied facilities (same convention), with this note's options."""
    rows = [('n_TOF EAR2', d['ear2'], sd.GREY, 'survey_fast.py (duty-limited)'),
            ('GANIL NFS', d['nfs'], sd.GREY, 'Geant4 N1-N4, ganil_nfs'),
            ('ILL PF1B', d['pf1b'], sd.GREY, 'ILL Geant4 walls, best rate'),
            ('ATOMKI ⁴He', RHO, sd.GREEN, 'PRC 104 044003')]
    rows += [(lab, R(d, k), col, tip) for k, lab, col, tip in here_keys]
    rows.sort(key=lambda r: -r[1])
    return sd.hbars([(n, v, c, f'{n}: X17/IPC {v:.2g} at 3σ in 50 d. {t}') for n, v, c, t in rows], 0.2, width=width,
                    log=True, vmin=5e-5, label_w=230, fmt=lambda v: f'{v:.1e}', size=22, h=28)


def rate_table(d, key):
    r = d['reach']
    q = r[(r.key == key) & (r.hw == HW) & (r.days == 50) & (r.signal == 'E* ≤ 22 MeV')].iloc[0]
    s = q.throttle
    rows = [['beam fraction used (throttle)', f'{s:.2g}'],
            ['singles per arm', f'{Cp(d, key, "ok_singles_per_arm") * s:,.0f} /s'],
            ['trigger legs per arm', f'{Cp(d, key, "legs_per_arm") * s:,.0f} /s'],
            ['random two-arm triggers', f'{q.rand_trig_per_s:,.0f} /s'],
            ['DREAM live time', f'{q.live:.2f}'],
            ['Micromegas occupancy (1 µs)', f'{q.occ:.3f}']]
    return sd.table(['at the best rate', ''], rows, size=22, widths=[460, 220])
