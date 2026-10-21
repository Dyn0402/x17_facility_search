#!/usr/bin/env python3
"""
bepn_beam.py -- thick-target ⁹Be(p,n) neutron and γ source for the cyclotron X17 study
(bepn_cyclotron/FACILITY.md, FEASIBILITY.md).

    python bepn_cyclotron/bepn_beam.py         # -> bepn_cyclotron/out/bepn_{spectra,angles,gamma,anchors,beam}.*

Nuclear data: ENDF/B-VIII.0 incident-proton file for ⁹Be (LANL LA150, Young & Arthur 1988/1990, valid to
113 MeV), as translated to GNDS 2.0 and shipped with Geant4 (refs/p-004_Be_009.endf.gnds.xml, copied from
/cvmfs/geant4.cern.ch/share/data/LEND_GNDS2.0_ENDF.BVIII.0/protons/).  It has

  MT 50-55   ⁹Be(p,n)⁹B to the ground state and five levels: σ(E_p), Q, CM Legendre angular distributions;
  MT 5       everything else (p,np), (p,nα), … : σ, neutron multiplicity, Kalbach-Mann f(E'|E) and r(E'|E)
             in the CM; photon multiplicity and spectrum (continuum + discrete lines), isotropic.

Thick (stopping) target: each proton energy E_p between the beam energy and the threshold contributes
n_Be σ(E_p) dE_p / S(E_p), S the Bethe stopping power of protons in Be (I = 63.7 eV).  Neutrons are sampled
per E_p from those distributions (Kalbach a from Kalbach's 1988 systematics, as ENDF prescribes), boosted
to the lab non-relativistically (≤ 3 % on the energy at 28 MeV), and histogrammed in (E_n, θ_lab).  The
target is bare: no backing, water, flange or room (all of which add a moderated low-energy component).

Anchors (out/bepn_anchors.csv): the 0° yield at 16 MeV (Fenyvesi, arXiv:1504.07399, from Brede et al.
NIM A 274 (1989) 332: 9.07×10¹⁵ n/sr/C above 0.4 MeV), NPI's 5×10¹² n/s/sr forward at 24 MeV, 0.3 mA
(UCANS-8, EPJ WoC 231 (2020) 03005), and Sumitomo/KURRI's 1.9×10¹⁴ n/s at 30 MeV, 1 mA (Cyclotrons 2010
FRM2CCO04).
"""
from __future__ import annotations

import functools
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import pandas as pd
if not hasattr(np, 'trapezoid'):
    np.trapezoid = np.trapz

HERE = Path(__file__).resolve().parent
OUT = HERE / 'out'
GNDS = HERE / 'refs' / 'p-004_Be_009.endf.gnds.xml'
M_P, M_N, M_BE9 = 938.272, 939.565, 8392.75                  # MeV, nuclear masses
M_B9 = 8393.31
N_BE = 1.848 / 9.0122 * 6.02214e23                            # Be atoms / cm³
E_CHARGE = 1.602176634e-19
S_P10B, S_N10B = 6.586, 8.437                                 # p and n separation energies of ¹⁰B [MeV]
EP_MIN = 2.06                                                 # MeV, below every neutron channel

ANCHORS = [  # (E_p, quantity, value, source)
    (16.0, 'y0_above_0.4', 9.07e15 * E_CHARGE, 'Fenyvesi arXiv:1504.07399 (Brede 1989 extrapolated): 9.07e15 n/sr/C, E_n > 0.4 MeV, 0°'),
    (24.0, 'y0', 5e12 / (0.3e-3 / E_CHARGE), 'NPI TR-24 design, UCANS-8 (2020): 5e12 n/s/sr forward at 0.3 mA'),
    (30.0, 'ytot', 1.9e14 / (1e-3 / E_CHARGE), 'Sumitomo/KURRI, Cyclotrons 2010 FRM2CCO04: 1.9e14 n/s fast neutrons at 1 mA'),
]


# --------------------------------------------------------------------------- #
def _vals(e):
    return np.array(e.find('values').text.split(), float)


@functools.lru_cache(maxsize=None)
def gnds():
    """the parts of the GNDS file this model uses."""
    root = ET.parse(GNDS).getroot()
    D = dict(levels=[], mt5=None, lines=[])
    for rx in root.iter('reaction'):
        mt = int(rx.get('ENDF_MT'))
        xs = _vals(rx.find('crossSection/XYs1d')).reshape(-1, 2)
        if 50 <= mt <= 55:
            q = float(rx.find('outputChannel/Q/constant1d').get('value'))
            leg = rx.find('.//product[@pid="n"]/distribution/angularTwoBody[@label="eval"]/XYs2d/function1ds')
            le = [(float(L.get('outerDomainValue')), _vals(L)) for L in leg]
            D['levels'].append(dict(mt=mt, q=q, xs=xs, leg=le))
        elif mt == 5:
            pn = rx.find('.//product[@pid="n"]')
            mult = _vals(pn.find('multiplicity/XYs1d')).reshape(-1, 2)
            km = pn.find('distribution/KalbachMann[@label="eval"]')
            f = [(float(x.get('outerDomainValue')), _vals(x).reshape(-1, 2)) for x in km.find('f/XYs2d/function1ds')]
            r = [(float(x.get('outerDomainValue')), _vals(x).reshape(-1, 2)) for x in km.find('r/XYs2d/function1ds')]
            gam = []
            for p in rx.iter('product'):
                if p.get('pid') != 'photon':
                    continue
                m = _vals(p.find('multiplicity/XYs1d')).reshape(-1, 2)
                dg = p.find('.//discreteGamma')
                if dg is not None:
                    gam.append(dict(line=float(dg.get('value')), mult=m))
                else:
                    sp = p.find('distribution/uncorrelated[@label="eval"]/energy/XYs2d/function1ds')
                    gam.append(dict(line=None, mult=m,
                                    spec=[(float(x.get('outerDomainValue')), _vals(x).reshape(-1, 2)) for x in sp]))
            D['mt5'] = dict(xs=xs, mult=mult, f=f, r=r, gam=gam)
    return D


def stopping(ep):
    """Bethe stopping power of protons in Be [MeV/cm] (no shell/Barkas corrections: > 2 MeV only)."""
    g = 1 + ep / M_P
    b2 = 1 - 1 / g ** 2
    tmax = 2 * 0.511 * b2 * g ** 2 / (1 + 2 * g * 0.511 / M_P + (0.511 / M_P) ** 2)
    L = 0.5 * np.log(2 * 0.511 * b2 * g ** 2 * tmax / (63.7e-6) ** 2) - b2
    return 0.307075 * 4 / 9.0122 / b2 * L * 1.848


def _legendre_pdf(coef, mu):
    p = np.zeros_like(mu)
    for l, a in enumerate(coef):
        c = np.zeros(l + 1)
        c[l] = 1
        p += (2 * l + 1) / 2 * a * np.polynomial.legendre.legval(mu, c)
    return np.clip(p, 0, None)


def _interp_table(tab, e):
    """nearest-below / above tabulated incident energies and the linear weight."""
    es = np.array([t[0] for t in tab])
    i = int(np.clip(np.searchsorted(es, e) - 1, 0, len(es) - 2))
    w = float(np.clip((e - es[i]) / (es[i + 1] - es[i]), 0, 1))
    return i, w


def _sample_pw(x, p, n, rng):
    """inverse-CDF sampling of a piecewise-linear pdf p(x) (trapezoid CDF, linear inside bins)."""
    c = np.concatenate([[0], np.cumsum(0.5 * (p[1:] + p[:-1]) * np.diff(x))])
    if c[-1] <= 0:
        return np.full(n, x[0])
    u = rng.uniform(0, c[-1], n)
    return np.interp(u, c, x)


def kalbach_a(e_in_cm, e_out_cm):
    """Kalbach (1988) systematics for p in, n out (ENDF-6 manual, LAW=1 LANG=2)."""
    ea = e_in_cm + S_P10B
    eb = e_out_cm + S_N10B
    r1, r3 = np.minimum(ea, 130.0), np.minimum(ea, 41.0)
    x1, x3 = r1 * eb / ea, r3 * eb / ea
    return 0.04 * x1 + 1.8e-6 * x1 ** 3 + 6.7e-7 * 1.0 * 0.5 * x3 ** 4


def _kalbach_mu(a, r, rng):
    n = len(a)
    a = np.maximum(a, 1e-6)
    x1, x2 = rng.uniform(size=n), rng.uniform(size=n)
    t = (2 * x2 - 1) * np.sinh(a)
    mu_r = np.log(t + np.sqrt(t * t + 1)) / a
    mu_s = np.log(x2 * np.exp(a) + (1 - x2) * np.exp(-a)) / a
    return np.clip(np.where(x1 < r, mu_r, mu_s), -1, 1)


def _to_lab(ep, e_cm_n, mu_cm, rng):
    """neutron CM energy + CM cosine -> (E_lab, cosθ_lab)."""
    V = np.sqrt(2 * ep / M_P) * M_P / (M_P + M_BE9)
    v = np.sqrt(2 * e_cm_n / M_N)
    vz = v * mu_cm + V
    vx = v * np.sqrt(np.clip(1 - mu_cm ** 2, 0, None))
    v2 = vx ** 2 + vz ** 2
    return 0.5 * M_N * v2, vz / np.sqrt(np.maximum(v2, 1e-30))


def mc(ep0, n_per_step=40_000, dE=0.1, seed=7):
    """(E_n, cosθ_lab, w) neutrons per proton for a stopping Be target at beam energy ep0.
    Also returns the γ list (E_γ, w) (isotropic)."""
    D = gnds()
    rng = np.random.default_rng(seed)
    steps = np.arange(EP_MIN + dE / 2, ep0, dE)
    E, C, W, G = [], [], [], []
    mu_grid = np.linspace(-1, 1, 401)
    for ep in steps:
        dx = dE / stopping(ep)                                    # cm of Be for this slice
        e_cm_in = ep * M_BE9 / (M_P + M_BE9)
        # ---- discrete levels
        for L in D['levels']:
            s = np.interp(ep, L['xs'][:, 0], L['xs'][:, 1], left=0, right=0)
            ef = e_cm_in + L['q']
            if s <= 0 or ef <= 0:
                continue
            m_res = M_B9 + (-1.8506 - L['q'])                       # ⁹B in the level (E_x = Q_gs − Q)
            e_n_cm = ef * m_res / (M_N + m_res)
            i, w = _interp_table(L['leg'], ep)
            c1, c2 = L['leg'][i][1], L['leg'][i + 1][1]
            k = max(len(c1), len(c2))
            coef = (1 - w) * np.pad(c1, (0, k - len(c1))) + w * np.pad(c2, (0, k - len(c2)))
            nn = n_per_step // 4
            mu = _sample_pw(mu_grid, _legendre_pdf(coef, mu_grid), nn, rng)
            el, cl = _to_lab(ep, np.full(nn, e_n_cm), mu, rng)
            E.append(el), C.append(cl), W.append(np.full(nn, N_BE * s * 1e-24 * dx / nn))
        # ---- MT 5 continuum
        M5 = D['mt5']
        s = np.interp(ep, M5['xs'][:, 0], M5['xs'][:, 1], left=0, right=0)
        mlt = np.interp(ep, M5['mult'][:, 0], M5['mult'][:, 1], left=0, right=0)
        if s > 0 and mlt > 0:
            i, w = _interp_table(M5['f'], ep)
            pick = rng.uniform(size=n_per_step) < w                 # sample from the bracketing tables
            eo = np.empty(n_per_step)
            rr = np.empty(n_per_step)
            for j, sel in ((i, ~pick), (i + 1, pick)):
                t = M5['f'][j][1]
                eo[sel] = _sample_pw(t[:, 0], t[:, 1], int(sel.sum()), rng)
                rt = M5['r'][j][1]
                rr[sel] = np.interp(eo[sel], rt[:, 0], rt[:, 1])
            eo = np.minimum(eo, max(e_cm_in - 1.8506, 1e-3))        # stay inside the kinematic limit
            mu = _kalbach_mu(kalbach_a(e_cm_in, eo), rr, rng)
            el, cl = _to_lab(ep, eo, mu, rng)
            E.append(el), C.append(cl), W.append(np.full(n_per_step, N_BE * s * mlt * 1e-24 * dx / n_per_step))
            # γ from MT 5 (isotropic; CM motion of the emitter neglected)
            for g in M5['gam']:
                gm = np.interp(ep, g['mult'][:, 0], g['mult'][:, 1], left=0, right=0)
                if gm <= 0:
                    continue
                yld = N_BE * s * gm * 1e-24 * dx
                if g['line'] is not None:
                    G.append((np.array([g['line']]), np.array([yld])))
                else:
                    ig, wg = _interp_table(g['spec'], ep)
                    t = g['spec'][ig + (1 if rng.uniform() < wg else 0)][1]
                    eg = _sample_pw(t[:, 0], t[:, 1], 2000, rng)
                    G.append((eg, np.full(2000, yld / 2000)))
    E, C, W = (np.concatenate(x) for x in (E, C, W))
    G = (np.concatenate([g[0] for g in G]), np.concatenate([g[1] for g in G])) if G else (np.zeros(0), np.zeros(0))
    return E, C, W, G


EBINS = np.concatenate([np.geomspace(0.01, 0.5, 20)[:-1], np.arange(0.5, 35.01, 0.25)])
CBINS_DEG = np.array([0, 8, 30, 40, 50, 60, 80, 100, 120, 140, 180])     # θ_lab bins; "0°" is θ < 8°


@functools.lru_cache(maxsize=None)
def spectra(ep0):
    """per proton: dY/dE dΩ [n/p/MeV/sr] in the θ bins; total yield; γ yield and spectrum."""
    e, c, w, (eg, wg) = mc(ep0)
    th = np.degrees(np.arccos(np.clip(c, -1, 1)))
    rows = {}
    for lo, hi in zip(CBINS_DEG[:-1], CBINS_DEG[1:]):
        sel = (th >= lo) & (th < hi)
        dom = 2 * np.pi * (np.cos(np.radians(lo)) - np.cos(np.radians(hi)))
        h, _ = np.histogram(e[sel], EBINS, weights=w[sel])
        rows[(lo, hi)] = h / dom / np.diff(EBINS)
    gb = np.arange(0, 20.01, 0.1)
    hg, _ = np.histogram(eg, gb, weights=wg)
    return dict(dydedo=rows, ytot=float(w.sum()), emax=float(e.max()), gbins=gb, dydeg=hg / np.diff(gb),
                gtot=float(wg.sum()), g_hi=float(wg[eg > 2.7].sum()))


def at_angle(ep0, th_deg):
    """dY/dE dΩ [n/p/MeV/sr] at the θ bin containing th_deg."""
    s = spectra(ep0)
    for (lo, hi), v in s['dydedo'].items():
        if lo <= th_deg < hi:
            return v
    raise ValueError(th_deg)


def y_per_sr(ep0, th_deg, e_lo=0.0, e_hi=99.0):
    v = at_angle(ep0, th_deg)
    x = 0.5 * (EBINS[1:] + EBINS[:-1])
    m = (x >= e_lo) & (x < e_hi)
    return float((v * np.diff(EBINS))[m].sum())


def spectrum_on_grid(ep0, th_deg, e_grid):
    """normalised dN/dE at θ on an arbitrary grid [MeV]."""
    v = at_angle(ep0, th_deg)
    x = 0.5 * (EBINS[1:] + EBINS[:-1])
    f = np.interp(e_grid, x, v, left=0.0, right=0.0)
    return f / np.trapezoid(f, e_grid)


def gamma_on_grid(ep0, e_grid):
    s = spectra(ep0)
    x = 0.5 * (s['gbins'][1:] + s['gbins'][:-1])
    f = np.interp(e_grid, x, s['dydeg'], left=0.0, right=0.0)
    return f / max(np.trapezoid(f, e_grid), 1e-300)


def beam(ep0, current_a, th_deg=0.0, dist_m=2.0, area_cm2=50.0):
    """neutrons and γ/s through a collimated area at dist_m and angle th_deg."""
    s = spectra(ep0)
    p_s = current_a / E_CHARGE
    om = area_cm2 / (dist_m * 100) ** 2
    y = y_per_sr(ep0, th_deg)
    f = spectrum_on_grid(ep0, th_deg, EBINS)
    frac = lambda lo, hi: y_per_sr(ep0, th_deg, lo, hi) / y            # noqa: E731
    return dict(E_p=ep0, current_mA=current_a * 1e3, theta=th_deg, dist_m=dist_m,
                n_tot=s['ytot'] * p_s, n_per_sr=y * p_s, forward_gain=y * 4 * np.pi / s['ytot'],
                n_cell=y * p_s * om, flux_at_cell=y * p_s * om / area_cm2,
                f_below_2p75=frac(0, 2.75), f_above_10=frac(10, 99), f_above_20=frac(20, 99),
                mean_En=float(np.trapezoid(f * EBINS, EBINS)), E_max=s['emax'],
                g_tot=s['gtot'] * p_s, g_cell=s['gtot'] * p_s * om / (4 * np.pi),
                g_hi_cell=s['g_hi'] * p_s * om / (4 * np.pi))


def shield(ok_pencil_per_arm, n_per_sr, dist_m=2.0, arm_cm2=75 * 75, eps=(1e-4, 1e-3), tvl_cm=(20.0, 35.0), margin=0.1):
    """How much shield the 4π field needs (estimate, not Geant4), as birmingham/bham_beam.shield() but for
    a fast spectrum: tenth-value layers of ~20 cm (borated PE + Fe) to ~35 cm (concrete) for 1-20 MeV
    neutrons (stand-ins; NCRP 144 quotes ~40 cm concrete TVL at 20-30 MeV).  ε = ok singles per neutron
    entering an arm: 10⁻⁴-10⁻³ for 1-20 MeV neutrons (they make legs; Birmingham's sub-MeV ones do not)."""
    n_arm = n_per_sr / (dist_m * 100) ** 2 * arm_cm2
    rows = []
    for e in eps:
        T = margin * ok_pencil_per_arm / (n_arm * e)
        for tvl in tvl_cm:
            rows.append(dict(eps=e, tvl_cm=tvl, n_arm_unshielded=n_arm, T_needed=T,
                             thickness_cm=max(0.0, -tvl * np.log10(T))))
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
def anchors():
    rows = []
    for ep, kind, val, src in ANCHORS:
        if kind == 'ytot':
            m = spectra(ep)['ytot']
        elif kind == 'y0':
            m = y_per_sr(ep, 0.0)
        else:
            m = y_per_sr(ep, 0.0, 0.4)
        rows.append(dict(E_p=ep, quantity=kind, model=m, reference=val, ratio=m / val, source=src))
    return pd.DataFrame(rows)


SITES = [  # (key, label, E_p, current A)
    ('npi24', 'NPI Řež TR-24, 24 MeV, 0.3 mA (design)', 24.0, 0.3e-3),
    ('npi18', 'NPI Řež TR-24, 18 MeV, 0.3 mA', 18.0, 0.3e-3),
    ('kur30', 'KURNS HM-30, 30 MeV, 1 mA (fast port: ask)', 30.0, 1e-3),
    ('u120', 'NPI Řež U-120M, H⁻ extraction, 18 MeV, 35 µA, collimated beam to the hall', 18.0, 35e-6),
]
ANGLES = (0.0, 45.0, 90.0, 130.0)


def main():
    OUT.mkdir(exist_ok=True)
    pd.set_option('display.width', 220)
    a = anchors()
    a.to_csv(OUT / 'bepn_anchors.csv', index=False, float_format='%.4g')
    print(a.drop(columns='source').to_string(index=False))
    rows, sp, ang = [], [], []
    x = 0.5 * (EBINS[1:] + EBINS[:-1])
    for ep in (16.0, 18.0, 24.0, 30.0):
        s = spectra(ep)
        for (lo, hi), v in s['dydedo'].items():
            sp += [dict(E_p=ep, th_lo=lo, th_hi=hi, E_n=xi, dYdEdO_per_uC=vi / E_CHARGE * 1e-6) for xi, vi in zip(x, v)]
            ang.append(dict(E_p=ep, th_lo=lo, th_hi=hi, Y_per_sr_per_p=float((v * np.diff(EBINS)).sum()),
                            Y_below_2p75=y_per_sr(ep, 0.5 * (lo + hi), 0, 2.75),
                            Y_above_10=y_per_sr(ep, 0.5 * (lo + hi), 10, 99)))
    for key, lab, ep, cur in SITES:
        for th in ANGLES:
            for d in (1.0, 2.0, 3.0):
                b = beam(ep, cur, th, d)
                b.update(key=key, site=lab)
                rows.append(b)
    t = pd.DataFrame(rows)
    t.to_csv(OUT / 'bepn_beam.csv', index=False, float_format='%.4g')
    print(t[t.dist_m == 2.0][['key', 'theta', 'n_tot', 'n_per_sr', 'n_cell', 'f_below_2p75', 'f_above_10',
                              'f_above_20', 'mean_En', 'g_tot', 'g_cell']].to_string(index=False))
    cpath = OUT / 'bepn_components.csv'
    if cpath.exists():                                         # after bepn_reach.py
        c = pd.read_csv(cpath)
        sh = []
        for key, ep, cur, th in (('npi18_0_2m', 18.0, 0.3e-3, 0.0), ('npi24_130_2m', 24.0, 0.3e-3, 130.0),
                                 ('kur30_130_2m', 30.0, 1e-3, 130.0)):
            r = c[(c.key == key) & (c.hw == 'big plastics')]
            if len(r):
                q = shield(float(r.ok_singles_per_arm.iloc[0]), beam(ep, cur, th, 2.0)['n_per_sr'])
                q.insert(0, 'key', key)
                sh.append(q)
        if sh:
            sh = pd.concat(sh, ignore_index=True)
            sh.to_csv(OUT / 'bepn_shield.csv', index=False, float_format='%.4g')
            print(sh.to_string(index=False))
    ga = pd.DataFrame([dict(E_p=ep, E_g=xi, dYdE_per_p=v) for ep in (18.0, 24.0, 30.0)
                       for xi, v in zip(0.5 * (spectra(ep)['gbins'][1:] + spectra(ep)['gbins'][:-1]), spectra(ep)['dydeg'])])
    d = pd.DataFrame(sp)
    an = pd.DataFrame(ang)
    an.to_csv(OUT / 'bepn_angles.csv', index=False, float_format='%.4g')
    print(an.to_string(index=False))

    sys.path.insert(0, str(HERE.parent / 'ill'))
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use()
    fig, ax = fs.figure()
    for ep, col in zip((18.0, 24.0, 30.0), (fs.MUTED, fs.ACCENT, fs.TRACK)):
        for (lo, hi), ls in (((0, 8), '-'), ((80, 100), '--')):
            q = d[(d.E_p == ep) & (d.th_lo == lo)]
            ax.plot(q.E_n, q.dYdEdO_per_uC, color=col, lw=1.5, ls=ls,
                    label=f'E_p = {ep:.0f} MeV, θ {"< 8°" if lo == 0 else "80–100°"}')
    ax.axvline(2.75, color=fs.COPPER, lw=0.8, ls=':')
    ax.text(2.85, 1e8, 'E* ≤ 22 MeV', color=fs.COPPER, fontsize=8)
    ax.set_yscale('log')
    ax.set_ylim(1e6, None)
    ax.set_xlabel('E_n [MeV]')
    ax.set_ylabel('dY/dE dΩ [n / (µC sr MeV)]')
    ax.legend(frameon=False, fontsize=7.5)
    fs.title(ax, 'Thick-Be ⁹Be(p,n): a hard forward tail, a soft sideways field',
             'ENDF/B-VIII.0 (LA150) σ and Kalbach-Mann, Bethe slowing-down, bare target')
    fs.save(fig, OUT / 'bepn_spectra', data=d)

    fig, ax = fs.figure()
    for ep, col in zip((18.0, 24.0, 30.0), (fs.MUTED, fs.ACCENT, fs.TRACK)):
        q = an[an.E_p == ep]
        xm = 0.5 * (q.th_lo + q.th_hi)
        ax.plot(xm, q.Y_per_sr_per_p / E_CHARGE * 1e-6, color=col, marker='o', lw=1.5, label=f'{ep:.0f} MeV, all')
        ax.plot(xm, q.Y_below_2p75 / E_CHARGE * 1e-6, color=col, marker='s', lw=1.0, ls='--', label=f'{ep:.0f} MeV, E_n < 2.75')
    ax.set_yscale('log')
    ax.set_xlabel('θ_lab [deg]')
    ax.set_ylabel('neutrons / (µC sr)')
    ax.legend(frameon=False, fontsize=7.5, ncol=2)
    fs.title(ax, 'The forward peak is the hard part', 'neutrons per µC per sr vs angle; the < 2.75 MeV part is nearly isotropic')
    fs.save(fig, OUT / 'bepn_angles_fig', data=an)

    fig, ax = fs.figure()
    for ep, col in zip((18.0, 24.0, 30.0), (fs.MUTED, fs.ACCENT, fs.TRACK)):
        q = ga[ga.E_p == ep]
        ax.step(q.E_g, q.dYdE_per_p, color=col, where='mid', lw=1.2, label=f'E_p = {ep:.0f} MeV')
    ax.set_yscale('log')
    ax.set_xlabel('E_γ [MeV]')
    ax.set_ylabel('γ per proton per MeV (4π)')
    ax.legend(frameon=False, fontsize=8)
    fs.title(ax, 'Target γ: lines below 7 MeV only', 'ENDF/B-VIII.0 MT 5 photons; no ⁹Be(p,γ)¹⁰B in the evaluation')
    fs.save(fig, OUT / 'bepn_gamma', data=ga)


if __name__ == '__main__':
    main()
