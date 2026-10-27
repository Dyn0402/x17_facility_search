#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
opt_sketch.py -- Pierfrancesco's CAD sketch (27 Oct, `lnl/mech_models/sketch li target X17.step`), seen by the
X17 leptons.  TARGET_OPTIONS.md §19.  ESTIMATE: the same ray-trace as opt_shapes.py (§17), which Geant4 L10
showed to be far too kind to Cu shells (traced 0.40 d/µA, Geant4 2.4 d/µA for the hemisphere).  Read the
numbers here as a comparison with the hemisphere traced the same way, not as days.

    ~/PycharmProjects/nTof_x17/.venv/bin/python lnl/target/opt_sketch.py

The STEP file holds four separate bodies, laid side by side (not an assembly).  Dimensions read from it (mm):
  A  "Corpo 01": a pointed shell of revolution (ogive), wall 0.2, open base Ø50 (outer r 24.98) at y = −60,
     tip at y = +3.19 rounded by a sphere (outer R 3.0, inner R 2.8, centre y = 0.193).  The flank is an arc of
     radius 375.29 (outer) / 375.09 (inner) whose centre lies 337.66 off the axis, on the far side, at
     y = −156.61 (a "lemon"): half-angle 15° at the base, 25° near the tip.  Height 63.2.
  B  "Corpo 02": a SOLID hemisphere R 25 on the same Ø50 base (y = −60 → −35).  Not shelled.
  C  "Corpo 04": a tube r 19.56–20.56 (1 mm wall), 300 long, open at its end (y = 7); a closed ring channel
     0.56 × 0.56 (r 19.78–20.34, y 7.22–7.78) inside the wall at the end; two Ø0.56 bores along the wall
     (r 20.06, at ±x) from the far end to 0.2 short of the ring channel.
  D  "Corpo 03": a Li disc Ø40 × 20 µm on the end face of C.
No material is given in the file.

Here A is traced as a Cu shell (his 24 Oct "200 µm Cu dome"; 200 µm is exactly the CAD wall), with the beam going
+y into it and the Li lining the inside near the tip; C+D as the flat end of a Ø41 × 1 mm tube.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import opt_shapes as SH   # noqa: E402

OUT = SH.OUT

# ---- body A: the ogive (his coordinates shifted so the inner tip sits at y = 0) ----------------------
Y_SHIFT = -2.993                      # inner tip (2.993 in the CAD) → 0
RM, YC = 337.656185, -156.606553 + Y_SHIFT
A_OUT, A_IN = 375.286576, 375.086576
TIP_C, TIP_RO, TIP_RI = 0.193096 + Y_SHIFT, 3.0, 2.8
Y_CAP_O, Y_CAP_I = 1.5 + Y_SHIFT, 1.414 + Y_SHIFT      # where the flank meets the tip sphere
Y_BASE = -60.0 + Y_SHIFT


def lemon_r(y, a):
    """flank radius at height y (outer a = A_OUT, inner a = A_IN)"""
    return np.sqrt(np.maximum(a * a - (y - YC) ** 2, 0)) - RM


def _exit(inside, p, u, smax=400.0, n=40):
    """first s > 0 where a convex region that contains p is left (bisection, vectorised)."""
    lo, hi = np.zeros(len(p)), np.full(len(p), smax)
    for _ in range(n):
        m = 0.5 * (lo + hi)
        ins = inside(p + m[:, None] * u)
        lo, hi = np.where(ins, m, lo), np.where(ins, hi, m)
    return lo


def _in_ogive(x, a, ycap, rtip):
    rho = np.hypot(x[:, 0], x[:, 2])
    y = x[:, 1]
    flank = ((rho + RM) ** 2 + (y - YC) ** 2 <= a * a) & (y <= ycap)
    tip = ((x - np.array([0, TIP_C, 0])) ** 2).sum(1) <= rtip * rtip
    return (flank | tip) & (y >= Y_BASE)


def ogive_path(p, u):
    """mm of shell crossed from a vertex inside the cavity: exit(outer solid) − exit(inner solid).  The solids
    are convex (lemon ∩ slab, plus the tip sphere) so a ray from inside leaves each once.  A leg that leaves
    through the open base (y < −60) crosses no shell."""
    so = _exit(lambda x: _in_ogive(x, A_OUT, Y_CAP_O, TIP_RO), p, u)
    si = _exit(lambda x: _in_ogive(x, A_IN, Y_CAP_I, TIP_RI), p, u)
    through_base = (p[:, 1] + si * u[:, 1]) <= Y_BASE + 1e-3
    return np.where(through_base, 0.0, np.clip(so - si, 0, None))


class Ogive:
    def __init__(self, mat='Cu'):
        self.mat = mat

    def path(self, p, u):
        return ogive_path(p, u)


def on_ogive(V):
    """vertex mid-film (Li 20 µm along the inward normal) where a beam proton at (x, z) meets the inner wall."""
    p = V.copy()
    rho = np.hypot(p[:, 0], p[:, 2])
    y_cap = TIP_C + np.sqrt(np.maximum(TIP_RI ** 2 - rho ** 2, 0))
    rho_cap_edge = np.sqrt(TIP_RI ** 2 - (Y_CAP_I - TIP_C) ** 2)
    # flank: solve lemon_r(y, A_IN) = rho for y (on the tip side of YC)
    y_fl = YC + np.sqrt(np.maximum(A_IN ** 2 - (rho + RM) ** 2, 0))
    y = np.where(rho <= rho_cap_edge, y_cap, y_fl)
    # inward normal: cap → toward the sphere centre; flank → toward the torus generating circle
    n_cap = np.c_[-p[:, 0], -(y - TIP_C), -p[:, 2]]
    with np.errstate(invalid='ignore', divide='ignore'):
        er = np.c_[p[:, 0], np.zeros(len(p)), p[:, 2]] / np.maximum(rho, 1e-9)[:, None]
    n_fl = -(er * (rho + RM)[:, None] + np.c_[np.zeros(len(p)), y - YC, np.zeros(len(p))])
    n = np.where((rho <= rho_cap_edge)[:, None], n_cap, n_fl)
    n /= np.linalg.norm(n, axis=1, keepdims=True)
    p[:, 1] = y
    return p + 0.010 * n


def main():
    V, U, T = SH.legs()
    th = np.degrees(np.arccos(np.concatenate([u[:, 1] for u in U])))
    tr = pd.read_csv(OUT / 'shapes_trace.csv')
    cal = tr[tr.kind.str.startswith('flat')]
    A = np.c_[np.ones(len(cal)), cal.sig_ms ** 2]
    (s2, k2), *_ = np.linalg.lstsq(A, cal.sigma68_g4 ** 2, rcond=None)

    geos = {
        'design (flat Li/Mo 8/diamond 50, CFRP chamber)': (SH.flat([('Mo', 8), ('Dia', 50)], 2), SH.on_film),
        'L10 hemisphere: Cu 200 µm, R 11, rim 4×5, SS flange': (SH.dome(11.0, t_um=200, rim=(4.0, 5.0)), SH.on_dome(11.0)),
        'L10 hemisphere without its flange (rim only)': (SH.dome(11.0, t_um=200, rim=(4.0, 5.0), flange_mm=0, tube='Al',
                                                                 tube_t=1e-6), SH.on_dome(11.0)),
        'sketch A: Cu ogive 200 µm, Ø50 × 63 mm, bare base': ([Ogive('Cu')], on_ogive),
        'sketch A in Al 200 µm (no Mo liner)': ([Ogive('Al')], on_ogive),
        'sketch A in Be 200 µm (no Mo liner)': ([Ogive('Be')], on_ogive),
        'sketch B as a 200 µm Cu shell, R 25, bare base': (SH.dome(25.0, t_um=200, flange_mm=0, tube='Al', tube_t=1e-6),
                                                       SH.on_dome(25.0)),
    }
    for tube, X in (('Al', 'Al'), ('SS', 'SS'), ('Cu', 'Cu')):
        g, n = SH.window(layers=(('Mo', 8), ('Dia', 200)), R=19.56, tilt_deg=0, ring_mm=1e-6, ring_w=1.0,
                         tube=X, tube_t=1.0, glue_mm=1e-6)
        geos[f'sketch C+D: flat end of the Ø41 × 1 mm tube, {tube} (+Mo 8/dia 200 stop)'] = (g, SH.on_plane(n))
    g, n = SH.window(layers=(('Mo', 8), ('Dia', 200)), R=10.0, tilt_deg=45, ring_mm=0.5, ring_w=5.0, ring_mat='Ti',
                     tube='Al', tube_t=0.5)
    geos['our window: Ø20, 45°, diamond 200, Ti rings, Al end 0.5'] = (g, SH.on_plane(n))
    g, n = SH.window(layers=(('Mo', 8), ('Dia', 200)), R=10.0, tilt_deg=0, ring_mm=0.5, ring_w=5.0, ring_mat='Ti',
                     tube='Al', tube_t=0.5)
    geos['our window 0°: Ø20, diamond 200, Ti rings, Al end 0.5'] = (g, SH.on_plane(n))
    g, n = SH.window(layers=(('Mo', 8), ('Dia', 200)), R=10.0, tilt_deg=45, ring_mm=0.5, ring_w=5.0, ring_mat='Ti',
                     tube='Al', tube_t=1e-6)
    geos['our window 45° on a wide adapter (no Ø20 end piece)'] = (g, SH.on_plane(n))

    rows, prof = [], []
    for lab, (geo, vf) in geos.items():
        r = SH.trace(geo, V, U, T, vf)
        sig = float(np.sqrt(s2 + k2 * r['sig_ms'] ** 2))
        p = vf(V)
        x = np.concatenate([SH.xx0(geo, p, u) for u in U])
        rows.append(dict(config=lab, x_med_pct=100 * r['x_med'], x_mean_pct=100 * r['x_mean'],
                         f_pair_gt1pct=r['f_pair_gt1pct'], p_conv_18MeV=r['p_conv'], sigma68_trace=sig))
        for lo in range(30, 180, 15):
            s = (th >= lo) & (th < lo + 15)
            if s.sum() < 20:
                continue
            prof.append(dict(geometry=lab, theta_lo=lo, x_med_pct=100 * np.median(x[s]), x_p84_pct=100 * np.percentile(x[s], 84)))
    df, pr = pd.DataFrame(rows), pd.DataFrame(prof)
    df.to_csv(OUT / 'sketch_trace.csv', index=False)
    pr.to_csv(OUT / 'sketch_theta_profile.csv', index=False)
    pd.set_option('display.width', 250)
    pd.set_option('display.max_colwidth', 80)
    print(df.to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    print(pr.pivot(index='theta_lo', columns='geometry', values='x_med_pct').round(2).T.to_string())

    # where the beam lands on the ogive: share on the tip cap, and the area the spot covers (for heat)
    rho = np.hypot(V[:, 0], V[:, 2])
    rce = np.sqrt(TIP_RI ** 2 - (Y_CAP_I - TIP_C) ** 2)
    print(f'beam spot rms r = {np.sqrt((rho ** 2).mean()):.2f} mm; share on the tip cap (r < {rce:.2f}): {(rho < rce).mean():.2f}')




# ---- where the beam lands, and what Li it crosses (the flank is hit at grazing incidence) -------------
def beam_on_ogive(ep_kev=1100.0, li_ug=1068.0):
    """per-proton Li path = li_ug / cos(incidence) for a film of li_ug along the normal; ⁸Be yields with
    target_model.layered_yield, binned in the path.  The Li beyond what the beam can cross just stops it."""
    import target_model as TM
    V, _, _ = SH.legs()
    p = on_ogive(V)
    rho = np.hypot(V[:, 0], V[:, 2])
    rce = np.sqrt(TIP_RI ** 2 - (Y_CAP_I - TIP_C) ** 2)
    y = p[:, 1]
    # cos(incidence) = |n_y|: cap normal from the sphere centre, flank normal from the generating circle
    ny_cap = np.abs(y - TIP_C) / TIP_RI
    ny_fl = np.abs(y - YC) / np.hypot(rho + RM, y - YC)
    cosi = np.clip(np.where(rho <= rce, ny_cap, ny_fl), 0.05, 1)
    path = li_ug / cosi
    edges = np.r_[np.quantile(path, np.linspace(0, 1, 13))]
    flat = TM.layered_yield(ep_kev, [TM.film('Li', li_ug)])
    rows = []
    for a, b in zip(edges[:-1], edges[1:]):
        s = (path >= a) & (path <= b)
        t = float(np.median(path[s]))
        r = TM.layered_yield(ep_kev, [TM.film('Li', t)])
        rows.append(dict(path_ug=t, share=s.mean(), cos_inc=float(np.median(cosi[s])), E_out_keV=r['E_out_keV'],
                         Y_g0=r['Y_g0'], f17=r['f17'], Y_g1=r['Y_g1']))
    d = pd.DataFrame(rows)
    w = d.share / d.share.sum()
    summ = dict(Ep_keV=ep_kev, li_ug_normal=li_ug, share_on_cap=float((rho <= rce).mean()),
                share_exit_below_441=float(w[d.E_out_keV < 441].sum()),
                Y_g0_rel_flat=float((w * d.Y_g0).sum() / flat['Y_g0']),
                f17_mix=float((w * d.Y_g0 * d.f17).sum() / (w * d.Y_g0).sum()), f17_flat=flat['f17'],
                Y_g1_rel_flat=float((w * d.Y_g1).sum() / flat['Y_g1']))
    d.to_csv(OUT / 'sketch_beam_li.csv', index=False)
    print(d.to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    print(summ)
    return summ


# ---- data for the 3D page (lnl/viz/lnl_target_design.html, "His sketch (27 Oct)" tab) --------------------
def profiles(n=60):
    """meridian (r, y) of the four bodies, in the CAD frame (mm), for LatheGeometry on the page."""
    def ogive(a, rt, ycap):
        ys = np.linspace(-60.0, ycap, n)
        pts = [(float(lemon_r(y + Y_SHIFT, a)), float(y)) for y in ys]     # lemon_r works in the shifted frame
        c = 0.193096
        ang0 = np.arcsin((ycap - c) / rt)
        for t in np.linspace(ang0, np.pi / 2, 16)[1:]:
            pts.append((float(rt * np.cos(t)), float(c + rt * np.sin(t))))
        pts[-1] = (0.0, pts[-1][1])
        return [[round(r, 3), round(y, 3)] for r, y in pts]
    return dict(ogive_out=ogive(A_OUT, TIP_RO, 1.5), ogive_in=ogive(A_IN, TIP_RI, 1.414))


def export_viz(n_pairs=160, seed=3):
    import json
    V, U, T = SH.legs()
    tr = pd.read_csv(OUT / 'sketch_trace.csv')
    pr = pd.read_csv(OUT / 'sketch_theta_profile.csv')
    bl = {ep: beam_on_ogive(ep) for ep in (1030.0, 1100.0)}
    pick = np.random.default_rng(seed).choice(len(V), n_pairs, replace=False)
    p = on_ogive(V)
    pairs = {}
    for m in ('Cu', 'Be'):
        x = [SH.xx0([Ogive(m)], p, u) for u in U]
        pairs[m] = [[*np.round(p[i], 2), *np.round(U[0][i], 3), *np.round(U[1][i], 3),
                     round(float(x[0][i]) * 100, 2), round(float(x[1][i]) * 100, 2)] for i in pick]
    out = dict(prof=profiles(), y_shift=Y_SHIFT, pairs=pairs,
               trace=tr.round(4).to_dict('records'),
               theta=pr.round(3).to_dict('records'),
               beam={str(int(k)): {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items()} for k, v in bl.items()})
    js = json.dumps(out, ensure_ascii=False, separators=(',', ':'))
    (OUT / 'sketch_viz.json').write_text(js)
    page = HERE.parent / 'viz' / 'lnl_target_design.html'
    t = page.read_text()
    a, b = '// SKETCH_DATA_BEGIN', '// SKETCH_DATA_END'
    if a in t:
        i, j = t.index(a), t.index(b)
        page.write_text(t[:i] + a + '\nconst SKD = ' + js + ';\n' + t[j:])
        print(f'sketch data → {page.name} ({len(js) / 1e3:.0f} kB)')


if __name__ == '__main__':
    main()
    export_viz()
