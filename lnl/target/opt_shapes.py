#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
opt_shapes.py -- Pierfrancesco's two target shapes (2026-10-24), seen by the X17 leptons.
TARGET_OPTIONS.md §17.  ESTIMATE until Geant4 replaces it.

    ~/PycharmProjects/nTof_x17/.venv/bin/python lnl/target/opt_shapes.py

  1. a hemispherical Cu dome, 200 µm thick, ending the beam pipe; 20 µm Li on its inside, the beam
     on its apex, forced air on the outside; the dome is brazed to a CF flange on a steel tube;
  2. the design stack (Mo 8 µm / CVD diamond 50 µm) as the end window of the CF tube, held between
     two Cu rings glued to the tube, perpendicular or tilted 45° to the beam, forced air outside.

The accepted X17 pairs of the Geant4 L9 design run (li20_mo8_dia50, 'MM 15° + TOF', any E_sum) give
the true lepton directions and energies.  Each leg is traced from its vertex through the solids of a
geometry (analytic ray / solid intervals), giving x/X0 per leg; a toy deflects each leg by the
Highland angle and gives σ68 of the opening-angle change from multiple scattering, and
(7/9)·x/X0 along the same directions gives the conversion probability of an 18 MeV γ (EPC).
The flat Geant4 configurations (Mo/diamond design, Cu 25 µm … 1 mm) are traced the same way and
calibrate σ68(G4)² = σ_int² + (k·σ_ms)² and days per µA against the trace.
Dome and window sizes are assumptions (ask): R = 17.5 mm (DN40 tube), CF flange 12.7 mm SS,
tube wall 1.65 mm SS.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'out' / 'target' / 'options'
sys.path.insert(0, str(HERE))
import opt_geant as OG   # noqa: E402

X0 = {'Cu': 14.36, 'Mo': 9.59, 'Dia': 121.3, 'SS': 17.6, 'Al': 88.97, 'CFRP': 267.0,
      'Li': 1550.0, 'Glue': 360.0, 'Be': 352.8, 'Ti': 35.6}                              # mm
INF = 1e9


# ---- convex primitives: entry/exit parameters [a, b] along x = p + s u (vectorised over rays) ----
def slab(p, u, n, lo, hi):
    """lo ≤ n·x ≤ hi"""
    n = np.asarray(n, float) / np.linalg.norm(n)
    pn, un = p @ n, u @ n
    with np.errstate(divide='ignore', invalid='ignore'):
        s1, s2 = (lo - pn) / un, (hi - pn) / un
    a, b = np.minimum(s1, s2), np.maximum(s1, s2)
    par = np.abs(un) < 1e-12
    inside = (pn >= lo) & (pn <= hi)
    a = np.where(par, np.where(inside, -INF, INF), a)
    b = np.where(par, np.where(inside, INF, -INF), b)
    return a, b


def cyl(p, u, axis, r, c=(0, 0, 0)):
    """distance from the line c + t·axis ≤ r"""
    ax = np.asarray(axis, float) / np.linalg.norm(axis)
    q = p - np.asarray(c, float)
    qp = q - np.outer(q @ ax, ax)
    up = u - np.outer(u @ ax, ax)
    A, B, C = (up * up).sum(1), 2 * (qp * up).sum(1), (qp * qp).sum(1) - r * r
    D = B * B - 4 * A * C
    with np.errstate(divide='ignore', invalid='ignore'):
        sq = np.sqrt(np.maximum(D, 0))
        a, b = (-B - sq) / (2 * A), (-B + sq) / (2 * A)
    par = A < 1e-14
    a = np.where(par, np.where(C <= 0, -INF, INF), np.where(D < 0, INF, a))
    b = np.where(par, np.where(C <= 0, INF, -INF), np.where(D < 0, -INF, b))
    return a, b


def sph(p, u, c, R):
    q = p - np.asarray(c, float)
    B, C = (q * u).sum(1), (q * q).sum(1) - R * R
    D = B * B - C
    sq = np.sqrt(np.maximum(D, 0))
    return np.where(D < 0, INF, -B - sq), np.where(D < 0, -INF, -B + sq)


def inter(*iv):
    return np.max([i[0] for i in iv], 0), np.min([i[1] for i in iv], 0)


def length(iv):
    a, b = iv
    return np.clip(np.minimum(b, INF) - np.maximum(a, 0.0), 0, None)


class Solid:
    """convex A minus convex B (B ⊂ anything); path = L(A ∩ ray) − L(A ∩ B ∩ ray)."""

    def __init__(self, mat, A, B=None):
        self.mat, self.A, self.B = mat, A, B

    def path(self, p, u):
        a = inter(*[f(p, u) for f in self.A])
        L = length(a)
        if self.B:
            L = L - length(inter(a, *[f(p, u) for f in self.B]))
        return np.clip(L, 0, None)


Y = np.array([0, 1.0, 0])


def S(fn, *a, **k):
    return lambda p, u: fn(p, u, *a, **k)


# ---- geometries -------------------------------------------------------------------------------
def chamber_cfrp():      # the L9 chamber: CFRP 0.4 mm, bore r 25, |y| ≤ 300; Al 5 mm flanges
    return [Solid('CFRP', [S(cyl, Y, 25.4), S(slab, Y, -300, 300)], [S(cyl, Y, 25.0)]),
            Solid('Al', [S(cyl, Y, 25.4), S(slab, Y, 300, 305)]),
            Solid('Al', [S(cyl, Y, 25.4), S(slab, Y, -305, -300)], [S(cyl, Y, 10.0)])]


def flat(layers, holder_mm, rdisk=20.0, chamber=True):
    """film at y < 0, backing layers from y = 0, Cu holder annulus r 10–20 behind (as the L9 sim)."""
    out, y = [], 0.0
    for mat, um in layers:
        t = um * 1e-3
        out.append(Solid(mat, [S(slab, Y, y, y + t), S(cyl, Y, rdisk)]))
        y += t
    out.append(Solid('Cu', [S(slab, Y, y, y + holder_mm), S(cyl, Y, 20.0)], [S(cyl, Y, 10.0)]))
    return out + (chamber_cfrp() if chamber else [])


def dome(R=17.5, t_um=200, flange_mm=12.7, flange_rout=None, tube='SS', tube_t=1.65, mat='Cu', liner=None,
         rim=None):
    """hemisphere, centre (0, −R, 0), inner radius R; apex (inner) at y = 0; joined at its equator
    to a CF flange y ∈ [−R − flange, −R], then the tube upstream.  rim = (width, height) mm: a thick
    ring of the dome material at the equator, r ∈ [R, R + width], y ∈ [−R − height, −R] (the machined
    cup in Pierfrancesco's 26 Oct photo has one; 2026-10-26)."""
    t = t_um * 1e-3
    c = (0, -R, 0)
    fo = flange_rout if flange_rout is not None else R + 17.0
    out = [Solid(mat, [S(sph, c, R + t), S(slab, Y, -R, INF)], [S(sph, c, R)])]
    if rim:
        out.append(Solid(mat, [S(cyl, Y, R + rim[0]), S(slab, Y, -R - rim[1], -R)], [S(cyl, Y, R)]))
    if liner:                                    # (mat, µm) on the inside, under the Li
        lm, lt = liner[0], liner[1] * 1e-3
        out.append(Solid(lm, [S(sph, c, R), S(slab, Y, -R, INF)], [S(sph, c, R - lt)]))
    if flange_mm > 0:
        out.append(Solid('SS', [S(cyl, Y, fo), S(slab, Y, -R - flange_mm, -R)], [S(cyl, Y, R)]))
    out.append(Solid(tube, [S(cyl, Y, R + tube_t), S(slab, Y, -400, -R - flange_mm)], [S(cyl, Y, R)]))
    return out


def window(layers=(('Mo', 8), ('Dia', 50)), R=17.5, tilt_deg=0.0, tilt_axis='x', ring_mm=2.0,
           ring_w=5.0, tube='SS', tube_t=1.65, glue_mm=0.1, ring_mat='Cu'):
    """the stack closes the tube end; vacuum side (film) faces upstream.  Plane normal n (tilted
    about x or about the x = z diagonal); the stack spans the tube bore (for
    the tilt: the tube's oblique cut, an ellipse); Cu rings of ring_w on both faces outside the bore,
    cut on the same plane; the tube wall below the plane."""
    th = np.radians(tilt_deg)
    if tilt_axis == 'x':
        n = np.array([0, np.cos(th), np.sin(th)])
    else:   # tilt about (1,0,-1)/√2: normal leans toward (1,0,1)
        n = np.array([np.sin(th) / np.sqrt(2), np.cos(th), np.sin(th) / np.sqrt(2)])
    out, z = [], 0.0
    for mat, um in layers:
        tt = um * 1e-3
        out.append(Solid(mat, [S(slab, n, z, z + tt), S(cyl, Y, R + ring_w)]))
        z += tt
    # rings: upstream (in vacuum, z < 0) and downstream (in air) of the stack; glue line under the upstream one
    out.append(Solid(ring_mat, [S(slab, n, -ring_mm - glue_mm, -glue_mm), S(cyl, Y, R + ring_w)], [S(cyl, Y, R)]))
    out.append(Solid('Glue', [S(slab, n, -glue_mm, 0), S(cyl, Y, R + ring_w)], [S(cyl, Y, R)]))
    out.append(Solid(ring_mat, [S(slab, n, z, z + ring_mm), S(cyl, Y, R + ring_w)], [S(cyl, Y, R)]))
    # tube: below the upstream ring
    out.append(Solid(tube, [S(cyl, Y, R + tube_t), S(slab, n, -INF, -ring_mm - glue_mm), S(slab, Y, -400, INF)],
                     [S(cyl, Y, R)]))
    return out, n


# ---- legs ---------------------------------------------------------------------------------------
def legs():
    z = OG.load('x17', 'li20_mo8_dia50')
    m = OG.mask(z, (0, 99))
    V = z['V'][m].astype(float)
    U = [z['em_p'][m].astype(float), z['ep_p'][m].astype(float)]
    U = [u / np.linalg.norm(u, axis=1, keepdims=True) for u in U]
    T = [z['em_ke'][m].astype(float), z['ep_ke'][m].astype(float)]
    return V, U, T


def xx0(solids, p, u):
    tot = np.zeros(len(p))
    for s in solids:
        tot += s.path(p, u) / X0[s.mat]
    return tot


def highland(x, ke):
    pc = ke + 0.511
    beta = np.sqrt(1 - (0.511 / pc) ** 2)
    xs = np.maximum(x, 1e-7)
    return 13.6 / (beta * pc) * np.sqrt(xs) * np.clip(1 + 0.038 * np.log(xs), 0.1, None) * (x > 0)


def deflect(u, th0, rng):
    a = np.cross(u, np.array([0.3, 0.1, 0.95]))
    a /= np.linalg.norm(a, axis=1, keepdims=True)
    b = np.cross(u, a)
    t1, t2 = rng.normal(size=len(u)) * th0, rng.normal(size=len(u)) * th0
    v = u + a * t1[:, None] + b * t2[:, None]
    return v / np.linalg.norm(v, axis=1, keepdims=True)


def trace(solids, V, U, T, vfix=None, seed=5):
    """per-leg x/X0, σ68 of the MS opening-angle change, γ conversion probability."""
    p = V if vfix is None else vfix(V)
    x = [xx0(solids, p, u) for u in U]
    rng = np.random.default_rng(seed)
    op = np.degrees(np.arccos(np.clip((U[0] * U[1]).sum(1), -1, 1)))
    d = []
    for _ in range(5):
        w = [deflect(U[i], highland(x[i], T[i]), rng) for i in range(2)]
        d.append(np.degrees(np.arccos(np.clip((w[0] * w[1]).sum(1), -1, 1))) - op)
    d = np.concatenate(d)
    q = np.percentile(d, [16, 84])
    xa = np.concatenate(x)
    return dict(x_med=np.median(xa), x_mean=xa.mean(), f_leg_gt1pct=(xa > 0.01).mean(),
                f_pair_gt1pct=((x[0] > 0.01) | (x[1] > 0.01)).mean(),
                sig_ms=0.5 * (q[1] - q[0]), p_conv=(7 / 9) * np.minimum(xa, 1).mean())


def on_film(V):            # flat: vertex mid-film (Li 20 µm upstream of y = 0)
    p = V.copy()
    p[:, 1] = -0.010
    return p


def on_dome(R, liner_mm=0.0):
    def f(V):
        p = V.copy()
        r2 = p[:, 0] ** 2 + p[:, 2] ** 2
        p[:, 1] = np.sqrt(R * R - r2) - R - 0.010 - liner_mm
        # mid-film, along the inward normal
        return p
    return f


def on_plane(n):
    def f(V):
        p = V.copy()
        p[:, 1] = -(n[0] * p[:, 0] + n[2] * p[:, 2]) / n[1] - 0.010 / n[1]
        return p
    return f


def main():
    V, U, T = legs()
    print(f'{len(V)} accepted X17 pairs (L9 li20_mo8_dia50)')
    acc = pd.read_csv(OUT / 'geant_acceptance.csv')
    reach = pd.read_csv(OUT / 'geant_reach.csv').set_index('config')
    g4 = acc[acc['sample'] == 'x17'].set_index('config')

    rows = []
    calib = {'li20_mo8_dia50': flat([('Mo', 8), ('Dia', 50)], 2),
             'li20_dia50': flat([('Dia', 50)], 2),
             'li20_cu25': flat([('Cu', 25)], 2), 'li20_cu100': flat([('Cu', 100)], 2),
             'li20_cu300': flat([('Cu', 300)], 3), 'li20_cu1000': flat([('Cu', 1000)], 3)}
    for tag, geo in calib.items():
        r = trace(geo, V, U, T, on_film)
        rows.append(dict(config=tag, kind='flat (Geant4 L9)', **r, sigma68_g4=g4.loc[tag, 'sigma68_deg'],
                         acc_g4=g4.loc[tag, 'acc'], days_g4=reach.loc[tag, 'days_ref_1uA']))
    cal = pd.DataFrame(rows)
    # σ68² = σ_int² + (k σ_ms)²: least squares in (σ_int², k²)
    A = np.c_[np.ones(len(cal)), cal.sig_ms ** 2]
    (s2, k2), *_ = np.linalg.lstsq(A, cal.sigma68_g4 ** 2, rcond=None)
    sint, k = np.sqrt(max(s2, 0)), np.sqrt(max(k2, 0))
    print(f'calibration: σ_int = {sint:.2f}°, k = {k:.2f}')

    new = {
        'dome R17.5 Cu200 + CF flange, SS tube': (dome(17.5), on_dome(17.5)),
        'dome R10 Cu200 + CF flange, SS tube': (dome(10.0), on_dome(10.0)),
        'dome R25 Cu200 + CF flange, SS tube': (dome(25.0), on_dome(25.0)),
        'dome R17.5 Cu200, no flange (thin Al tube 0.5)': (dome(17.5, flange_mm=0, tube='Al', tube_t=0.5), on_dome(17.5)),
        'dome R17.5 Cu100 + CF flange, SS tube': (dome(17.5, t_um=100), on_dome(17.5)),
        'dome R17.5 Cu50 + CF flange, SS tube': (dome(17.5, t_um=50), on_dome(17.5)),
        'dome R17.5 Al200 + Mo8 liner, flange 40 mm back, Al tube 0.5': (
            dome(17.5, t_um=200, mat='Al', liner=('Mo', 8), flange_mm=0, tube='Al', tube_t=0.5), on_dome(17.5, 0.008)),
        'dome R17.5 Be250 + Mo8 liner, flange 40 mm back, Al tube 0.5': (
            dome(17.5, t_um=250, mat='Be', liner=('Mo', 8), flange_mm=0, tube='Al', tube_t=0.5), on_dome(17.5, 0.008)),
    }
    for lab, (geo, vf) in new.items():
        rows.append(dict(config=lab, kind='dome', **trace(geo, V, U, T, vf)))
    for tilt, ax in ((0, 'x'), (45, 'x'), (45, 'd')):
        for tube, tt in (('SS', 1.65), ('Al', 0.5)):
            geo, n = window(tilt_deg=tilt, tilt_axis=ax, tube=tube, tube_t=tt)
            lab = f'window Mo8/dia50, tilt {tilt}°' + (f' about {"x" if ax == "x" else "x=z"}' if tilt else '') + \
                  f', {tube} tube {tt} mm'
            rows.append(dict(config=lab, kind='window', **trace(geo, V, U, T, on_plane(n))))
    for R, d in ((17.5, 100), (17.5, 200), (12.5, 100), (10.0, 100)):
        geo, n = window(layers=(('Mo', 8), ('Dia', d)), R=R, tilt_deg=45, tube='Al', tube_t=0.5)
        rows.append(dict(config=f'window Mo8/dia{d}, tilt 45° about x, R {R:g}, Al tube 0.5 mm', kind='window',
                         **trace(geo, V, U, T, on_plane(n))))
    geo, n = window(tilt_deg=45, tube='CFRP', tube_t=1.0)
    rows.append(dict(config='window Mo8/dia50, tilt 45° about x, CFRP tube 1 mm', kind='window', **trace(geo, V, U, T, on_plane(n))))
    # an LN₂ shroud around the design target (Cu can r 30 mm, |y| ≤ 50) vs a cold trap upstream (out of view)
    for t_sh in (0.5, 1.0):
        geo = flat([('Mo', 8), ('Dia', 50)], 2) + [Solid('Cu', [S(cyl, Y, 30 + t_sh), S(slab, Y, -50, 50)], [S(cyl, Y, 30)])]
        rows.append(dict(config=f'design + LN2 Cu shroud {t_sh} mm around the target', kind='shroud',
                         **trace(geo, V, U, T, on_film)))
    geo, n = window(layers=(('Mo', 8), ('Dia', 100)), tube='SS')
    rows.append(dict(config='window Mo8/dia100, tilt 0°, SS tube 1.65 mm', kind='window', **trace(geo, V, U, T, on_plane(n))))
    # ---- added 2026-10-26 (AUDIT_2026-10-26.md): the cup in the 26 Oct photo (CN paper: 300 µm Cu, R ~ 11 mm,
    # a thick machined rim at the equator), diamond windows thick enough for 1 bar over Ø35 mm (≥ 300 µm, see
    # plate_stress), and a Ø20 mm window in thin Ti rings instead of 2 mm Cu.
    for R, t in ((11.0, 300), (11.0, 200), (17.5, 300)):
        rows.append(dict(config=f'dome R{R:g} Cu{t} + Cu rim 3×3 mm + CF flange, SS tube (photo)', kind='dome',
                         **trace(dome(R, t_um=t, rim=(3.0, 3.0)), V, U, T, on_dome(R))))
    for d in (300, 500):
        for tube, tt in (('Al', 0.5), ('CFRP', 1.0)):
            geo, n = window(layers=(('Mo', 8), ('Dia', d)), tilt_deg=45, tube=tube, tube_t=tt)
            rows.append(dict(config=f'window Mo8/dia{d}, tilt 45° about x, {tube} tube {tt} mm', kind='window',
                             **trace(geo, V, U, T, on_plane(n))))
    for d in (200, 300):
        geo, n = window(layers=(('Mo', 8), ('Dia', d)), R=10.0, tilt_deg=45, ring_mm=0.5, ring_w=5.0, ring_mat='Ti',
                        tube='Al', tube_t=0.5)
        rows.append(dict(config=f'window Mo8/dia{d}, tilt 45°, R 10 in Ti rings 0.5 mm, Al tube 0.5 mm', kind='window',
                         **trace(geo, V, U, T, on_plane(n))))

    df = pd.DataFrame(rows)
    df['sigma68_est'] = np.sqrt(sint ** 2 + (k * df.sig_ms) ** 2)
    # days per µA: interpolate the Geant4 flat set in σ68 (monotone in the Cu scan); EPC is not separate
    c = cal.sort_values('sigma68_g4')
    df['days_est'] = np.interp(df.sigma68_est, c.sigma68_g4, c.days_g4)
    df.loc[df.sigma68_est > c.sigma68_g4.max(), 'days_est'] = np.nan
    df.to_csv(OUT / 'shapes_trace.csv', index=False)
    pd.set_option('display.width', 250)
    pd.set_option('display.max_columns', 20)
    print(df.drop(columns=['kind']).to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    # per-direction map for the dome and the design: x/X0 vs polar angle of the leg
    th = np.degrees(np.arccos(np.concatenate([u[:, 1] for u in U])))
    prof = []
    for lab, (geo, vf) in [('design', (calib['li20_mo8_dia50'], on_film)),
                           ('dome R17.5', new['dome R17.5 Cu200 + CF flange, SS tube']),
                           ('window 0° SS', (window()[0], on_plane(window()[1]))),
                           ('window 45° x SS', (window(tilt_deg=45)[0], on_plane(window(tilt_deg=45)[1])))]:
        p = vf(V)
        x = np.concatenate([xx0(geo, p, u) for u in U])
        for lo in range(0, 180, 15):
            s = (th >= lo) & (th < lo + 15)
            if s.sum() > 20:
                prof.append(dict(geometry=lab, theta_lo=lo, n=int(s.sum()), x_med=np.median(x[s]),
                                 x_p84=np.percentile(x[s], 84)))
    pr = pd.DataFrame(prof)
    pr.to_csv(OUT / 'shapes_theta_profile.csv', index=False)
    print(pr.pivot(index='theta_lo', columns='geometry', values='x_med').to_string(float_format=lambda v: f'{v:.4f}'))
    print(pr.groupby('theta_lo').n.first().to_string())



# ---- heat and pressure (ESTIMATE) --------------------------------------------------------------
def shell_temp(kt, h, P=4.4, sigma=2.0, Rarc=27.5, T_edge=10.0, n=600):
    """thin shell/disk as a radial fin: (1/r)(r kt T')' − h T + q = 0, T(Rarc) = T_edge, T'(0) = 0.
    T is above the cooling air; q is a Gaussian beam spot of power P [W]; lengths mm, kt W/K, h W/m²/K.
    Returns the peak temperature rise."""
    r = np.linspace(0, Rarc, n) * 1e-3
    dr = r[1] - r[0]
    s = sigma * 1e-3
    q = P / (2 * np.pi * s * s) * np.exp(-r ** 2 / (2 * s * s))
    A = np.zeros((n, n))
    b = -q.copy()
    for i in range(1, n - 1):
        rp, rm = r[i] + dr / 2, r[i] - dr / 2
        A[i, i - 1] = kt * rm / (r[i] * dr * dr)
        A[i, i + 1] = kt * rp / (r[i] * dr * dr)
        A[i, i] = -kt * (rp + rm) / (r[i] * dr * dr) - h
    A[0, 0], A[0, 1] = -4 * kt / dr ** 2 - h, 4 * kt / dr ** 2
    A[-1, -1], b[-1] = 1.0, T_edge
    T = np.linalg.solve(A, b)
    return T[0]


def membrane(t_um, a_mm, E=1.05e12, p=1e5):
    """clamped circular MEMBRANE under 1 bar (Hencky, no bending stiffness): stress [MPa], deflection [mm].
    Kept for reference only: it omits the bending stress at a clamped edge and is low by ×2.7–3.3 for the
    diamond windows considered here (AUDIT_2026-10-26.md §B1).  Use plate_stress()."""
    t, a = t_um * 1e-6, a_mm * 1e-3
    return 0.423 * (E * p * p * a * a / t ** 2) ** (1 / 3) / 1e6, 0.662 * a * (p * a / (E * t)) ** (1 / 3) * 1e3


def plate_stress(t_um, a_mm, E=1.05e6, nu=0.07, q=0.1013):
    """clamped ("fixed and held") circular plate under uniform pressure q [MPa] with large deflection,
    Roark Table 11.11 case 3:  q a⁴/(E t⁴) = K1 (y/t) + K2 (y/t)³,  σ a²/(E t²) = K3 (y/t) + K4 (y/t)²,
    K1 = 5.33/(1−ν²), K2 = 2.6/(1−ν²); edge K3 = 4/(1−ν²), K4 = 1.73; centre K3 = 2/(1−ν), K4 = 0.976.
    Small-deflection limit: σ_edge = 0.75 q a²/t², y = q a⁴/(64 D).  Large-deflection limit: ∝ (q a/t)^(2/3)
    like the membrane, with the clamped-edge boundary layer on top.  Returns (edge MPa, centre MPa, y mm)."""
    t, a = t_um * 1e-3, a_mm
    k1, k2 = 5.33 / (1 - nu ** 2), 2.6 / (1 - nu ** 2)
    r = np.roots([k2, 0, k1, -q * a ** 4 / (E * t ** 4)])
    x = float(r[np.isreal(r)].real.max())
    f = E * t * t / (a * a)
    return f * (4 / (1 - nu ** 2) * x + 1.73 * x * x), f * (2 / (1 - nu) * x + 0.976 * x * x), x * t


def heat():
    rows = []
    cases = [('Cu dome 200 µm', 400 * 200e-6, 27.5, 2.0), ('Cu dome 50 µm', 400 * 50e-6, 27.5, 2.0),
             ('Al dome 200 µm + Mo 8', 237 * 200e-6 + 138 * 8e-6, 27.5, 2.0),
             ('Be dome 250 µm + Mo 8', 200 * 250e-6 + 138 * 8e-6, 27.5, 2.0),
             ('diamond 50 µm + Mo 8, window, 0°', 1800 * 50e-6 + 138 * 8e-6, 17.5, 2.0),
             ('diamond 50 µm + Mo 8, window, 45°', 1800 * 50e-6 + 138 * 8e-6, 17.5 * 1.19, 2.0 * 2 ** 0.25)]
    for lab, kt, Ra, sg in cases:
        for h in (30, 100, 300):     # free → forced air → an air jet on the spot
            rows.append(dict(case=lab, kt_W_per_K=kt, h=h, dT_peak_4uA=shell_temp(kt, h, Rarc=Ra, sigma=sg)))
    df = pd.DataFrame(rows)
    df.to_csv(OUT / 'shapes_thermal.csv', index=False)
    print(df.pivot(index='case', columns='h', values='dT_peak_4uA').to_string(float_format=lambda v: f'{v:.0f}'))
    mem = []
    for a in (17.5, 12.5, 10.0):
        for t in (50, 100, 200, 300, 500):
            e, c, y = plate_stress(t, a)
            mem.append(dict(window=f'diamond {t} µm, r {a} mm', stress_MPa=e, stress_centre_MPa=c, deflection_mm=y,
                            membrane_only_MPa=membrane(t, a)[0]))
    mem.append(dict(window='Cu dome 200 µm, R 17.5 mm (pR/2t)', stress_MPa=1e5 * 17.5e-3 / (2 * 200e-6) / 1e6,
                    stress_centre_MPa=np.nan, deflection_mm=0.0, membrane_only_MPa=np.nan))
    m = pd.DataFrame(mem)
    m.to_csv(OUT / 'shapes_pressure.csv', index=False)
    print(m.to_string(index=False, float_format=lambda v: f'{v:.3g}'))


# ---- data for the 3D page (lnl/viz/lnl_target_design.html, "His two shapes" tab) ------------------
VIZ = {   # key: (label, kind, geometry kwargs, vertex placement)
    'cu200':   ('Cu 200 µm dome (as proposed)', 'dome', dict(R=17.5, t_um=200)),
    'cu50':    ('Cu 50 µm dome', 'dome', dict(R=17.5, t_um=50)),
    'al200':   ('Al 200 µm + Mo 8 µm dome, thin tube end', 'dome',
                dict(R=17.5, t_um=200, mat='Al', liner=('Mo', 8), flange_mm=0, tube='Al', tube_t=0.5)),
    'be250':   ('Be 250 µm + Mo 8 µm dome, thin tube end', 'dome',
                dict(R=17.5, t_um=250, mat='Be', liner=('Mo', 8), flange_mm=0, tube='Al', tube_t=0.5)),
    't0_ss':   ('⊥ beam, steel CF tube 1.65 mm', 'window', dict(tilt_deg=0, tube='SS', tube_t=1.65)),
    't45_ss':  ('45°, steel CF tube 1.65 mm (as proposed)', 'window', dict(tilt_deg=45, tube='SS', tube_t=1.65)),
    't0_al':   ('⊥ beam, Al tube end 0.5 mm', 'window', dict(tilt_deg=0, tube='Al', tube_t=0.5)),
    't45_al':  ('45°, Al tube end 0.5 mm (diamond 50 µm)', 'window', dict(tilt_deg=45, tube='Al', tube_t=0.5)),
    't45_al100': ('45°, Al tube end 0.5 mm, diamond 100 µm', 'window',
                  dict(layers=(('Mo', 8), ('Dia', 100)), tilt_deg=45, tube='Al', tube_t=0.5)),
}


def export_viz(n_pairs=160, seed=3):
    """per variant: summary, x/X0 vs θ profile, and n_pairs sample pairs (vertex, directions, x/X0 per leg)."""
    import json
    V, U, T = legs()
    tr = pd.read_csv(OUT / 'shapes_trace.csv')
    cal = tr[tr.kind.str.startswith('flat')]
    A = np.c_[np.ones(len(cal)), cal.sig_ms ** 2]
    (s2, k2), *_ = np.linalg.lstsq(A, cal.sigma68_g4 ** 2, rcond=None)
    c = cal.sort_values('sigma68_g4')
    pick = np.random.default_rng(seed).choice(len(V), n_pairs, replace=False)
    th = np.degrees(np.arccos(np.concatenate([u[:, 1] for u in U])))
    dgeo, dp = flat([('Mo', 8), ('Dia', 50)], 2), on_film(V)
    dx = np.concatenate([xx0(dgeo, dp, u) for u in U])
    out = {'design': dict(label='design: Li 20 / Mo 8 / diamond 50, Cu holder, CFRP chamber (Geant4 6.6°)',
                          sigma68=6.6, days=0.22, x_med=round(float(np.median(dx)) * 100, 2), f_pair=28,
                          prof=[round(float(np.median(dx[(th >= lo) & (th < lo + 15)])) * 100, 3) for lo in range(45, 135, 15)])}
    for key, (lab, kind, kw) in VIZ.items():
        if kind == 'dome':
            geo = dome(**kw)
            lt = kw.get('liner', (None, 0))[1] * 1e-3
            vf = on_dome(kw.get('R', 17.5), lt)
        else:
            geo, n = window(**kw)
            vf = on_plane(n)
        r = trace(geo, V, U, T, vf)
        sig = float(np.sqrt(s2 + k2 * r['sig_ms'] ** 2))
        days = float(np.interp(sig, c.sigma68_g4, c.days_g4)) if sig <= c.sigma68_g4.max() else None
        p = vf(V)
        x = [xx0(geo, p, u) for u in U]
        xa = np.concatenate(x)
        prof = [round(float(np.median(xa[(th >= lo) & (th < lo + 15)])) * 100, 3) for lo in range(45, 135, 15)]
        pairs = [[*np.round(p[i], 2), *np.round(U[0][i], 3), *np.round(U[1][i], 3),
                  round(float(x[0][i]) * 100, 2), round(float(x[1][i]) * 100, 2)] for i in pick]
        out[key] = dict(label=lab, kind=kind, geo={k: v for k, v in kw.items() if k != 'layers'},
                        layers=[list(l) for l in kw.get('layers', (('Mo', 8), ('Dia', 50)))] if kind == 'window' else None,
                        sigma68=round(sig, 1), days=None if days is None else round(days, 2),
                        x_med=round(float(np.median(xa)) * 100, 2),
                        f_pair=round(float(((x[0] > 0.01) | (x[1] > 0.01)).mean()) * 100),
                        prof=prof, pairs=pairs)
    js = json.dumps(out, ensure_ascii=False, separators=(',', ':'))
    (OUT / 'shapes_viz.json').write_text(js)
    page = HERE.parent / 'viz' / 'lnl_target_design.html'
    t = page.read_text()
    a, b = '// SHAPES_DATA_BEGIN', '// SHAPES_DATA_END'
    if a in t:
        i, j = t.index(a), t.index(b)
        page.write_text(t[:i] + a + '\nconst SHP = ' + js + ';\n' + t[j:])
        print(f'shapes data → {page.name} ({len(js) / 1e3:.0f} kB)')


if __name__ == '__main__':
    main()
    heat()
    export_viz()
