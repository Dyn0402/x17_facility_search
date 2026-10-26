"""opt_beamline.py -- the LNL beam line as photographed (26 Oct) around the MX17 arms: which parts the
X17 leptons cross, how much each scatters them, and what clashes with the arms.

    ~/PycharmProjects/nTof_x17/.venv/bin/python lnl/target/opt_beamline.py

Added 2026-10-26 (TARGET_OPTIONS §18).  Same method as opt_shapes.py (ray-trace of the 65 k accepted X17 legs of
Geant4 L9 li20_mo8_dia50, Highland toy, σ68 and days calibrated on the six flat L9 configs), with the target at
the detector centre (the L9 legs are accepted there).

Geometry (ESTIMATE, read off pictures/LNL_beam_with_li_cu_hemi_target.png): the steel tube is 31 px across; taken
as DN40 CF (38.1 mm OD), so 1.23 mm/px, ±20 %.  The right-hand flange is 3.0× the tube, i.e. DN63 CF (114 mm).
Going upstream from the Li at the cup's apex (y = 0, beam +y, z up):
  Cu cup (R 11, 300 µm, CN paper)  0 … −16 mm, rim to r 15
  grey tube flange                −16 … −27 mm, r 15 … 33           (material: ask; PVC assumed)
  grey tube Ø48                   −27 … −165 mm, wall 3 mm (ask)
  KF40 clamp + floor stand        −165 … −185 mm; the stand's post goes down to the floor
  DN40 steel tube                 −185 mm onwards
  tee down + bellows to a pump    −260 mm; bellows run back at z ≈ −150 to −430 mm
  VAT gate valve                  −350 … −395 mm; body z −45 … +75, actuator to z +210
  tee down to the pump cross      −480 mm
  DN63 CF flange pair             −580 … −620 mm
  a Ø6 mm Cu air(?) line under the pipe at z ≈ −45, curling up to the cup
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import opt_shapes as SH   # noqa: E402
from opt_shapes import Solid, S, cyl, slab, sph, Y, INF, X0   # noqa: E402

OUT = SH.OUT
X0.update({'PVC': 196.3, 'PEEK': 314.0, 'Alumina': 70.4})   # mm (PDG; PEEK from C19H12O3 at 1.32 g/cm³)
Xv, Zv = np.array([1.0, 0, 0]), np.array([0, 0, 1.0])

GREY = {'PVC': ('PVC', 3.0), 'PEEK': ('PEEK', 3.0), 'Alumina': ('Alumina', 3.0), 'SS': ('SS', 1.65), 'CFRP': ('CFRP', 3.0)}
# the cup glued straight onto the tube (Pierfrancesco, 26 Oct: "much less material, gluing it directly to the CF tube"):
# CF read as ConFlat (steel); carbon fibre as the alternative
GLUED = {'SS': ('SS', 1.65), 'CFRP': ('CFRP', 1.0)}


def box(mat, x, y, z, hollow=None):
    """axis-aligned box (x0, x1), (y0, y1), (z0, z1) in mm; hollow = wall thickness"""
    A = [S(slab, Xv, *x), S(slab, Y, *y), S(slab, Zv, *z)]
    B = None
    if hollow:
        w = hollow
        B = [S(slab, Xv, x[0] + w, x[1] - w), S(slab, Y, y[0] + w, y[1] - w), S(slab, Zv, z[0] + w, z[1] - w)]
    return Solid(mat, A, B)


def tube(mat, axis, c, r_in, r_out, lo, hi):
    """cylindrical shell about the line c + t·axis, axis·x ∈ [lo, hi]"""
    ax = np.asarray(axis, float) / np.linalg.norm(axis)
    A = [S(cyl, ax, r_out, c), S(slab, ax, lo, hi)]
    return Solid(mat, A, [S(cyl, ax, r_in, c)] if r_in > 0 else None)


def cup(R=11.0, t_um=300.0, rim_r=15.0, rim_h=5.0):
    t = t_um * 1e-3
    c = (0, -R, 0)
    return [Solid('Cu', [S(sph, c, R + t), S(slab, Y, -R, INF)], [S(sph, c, R)]),
            tube('Cu', Y, (0, 0, 0), R, rim_r, -R - rim_h, -R)]


def grey(mat='PVC', wall=3.0, y0=-16.0):
    """the grey tube and its flange; y0 = where the flange face meets the target piece"""
    return [tube(mat, Y, (0, 0, 0), 15.0, 33.0, y0 - 11, y0),
            tube(mat, Y, (0, 0, 0), 24.0 - wall, 24.0, y0 - 149, y0 - 11)]


def hardware(dy=0.0):
    """everything upstream of the grey tube, as photographed; dy shifts it all along y (dy < 0: further back)"""
    def yy(a, b):
        return (a + dy, b + dy)
    out = {
        'KF clamp': [tube('Al', Y, (0, 0, 0), 20.5, 40.0, *yy(-185, -165))],
        'stand post': [box('Al', (-20, 20), yy(-195, -155), (-1200, -40), hollow=2.5)],
        'DN40 steel tube': [tube('SS', Y, (0, 0, 0), 17.4, 19.05, *yy(-620, -185))],
        'tee + bellows': [tube('SS', Zv, (0, -260 + dy, 0), 17.4, 19.05, -120, -19),
                          tube('SS', Y, (0, 0, -150), 24.0, 25.0, *yy(-430, -260))],
        'gate valve': [box('SS', (-45, 45), yy(-395, -350), (-45, 75), hollow=6),
                       tube('Al', Zv, (0, -372 + dy, 0), 0, 20.0, 75, 210)],
        'tee to pump': [tube('SS', Zv, (0, -480 + dy, 0), 17.4, 19.05, -400, -19)],
        'DN63 CF flanges': [tube('SS', Y, (0, 0, 0), 31.0, 57.0, *yy(-620, -585))],
    }
    # the Cu line (air for cooling, or a cable duct): along y under the pipe, then up toward the cup
    a, b = np.array([0, -60.0, -45]), np.array([0, -20.0, -28])
    ax = (b - a) / np.linalg.norm(b - a)
    out['Cu line (air?)'] = [tube('Cu', Y, (0, 0, -45), 2.0, 3.0, *yy(-600, -60)),
                             tube('Cu', ax, a, 2.0, 3.0, a @ ax, b @ ax)]
    return out


def on_cup(R=11.0):
    return SH.on_dome(R)


# ---- the clash check: arm envelopes (mm), from MX17_Full_Geant SimConfig via lnl_setup_3d.html -------------
ARM = dict(mm_face=204.0, mm_half=180.0, stack_half=250.0)


def calib():
    tr = pd.read_csv(OUT / 'shapes_trace.csv')
    cal = tr[tr.kind.str.startswith('flat')]
    A = np.c_[np.ones(len(cal)), cal.sig_ms ** 2]
    (s2, k2), *_ = np.linalg.lstsq(A, cal.sigma68_g4 ** 2, rcond=None)
    c = cal.sort_values('sigma68_g4')

    def est(sig_ms):
        s = float(np.sqrt(s2 + k2 * sig_ms ** 2))
        d = float(np.interp(s, c.sigma68_g4, c.days_g4)) if s <= c.sigma68_g4.max() else np.nan
        return s, d
    return est


def variants(grey_mat='PVC', glue_mat='SS'):
    gm, gw = GREY[grey_mat]
    hw = hardware()
    hw_all = [s for v in hw.values() for s in v]
    win, n = SH.window(layers=(('Mo', 8), ('Dia', 200)), R=10.0, tilt_deg=45, ring_mm=0.5, ring_w=5.0,
                       ring_mat='Ti', tube='Al', tube_t=0.5)
    # its 0.5 mm Al tube (r 10, cut on the window plane) becomes a 55 mm end piece; the grey line starts behind it
    end = [s for s in win if s.mat == 'Al']
    win = [s for s in win if s.mat != 'Al']
    for s in end:
        s.A.append(S(slab, Y, -55.0, INF))
    return {
        'photo': dict(label='as photographed: Cu cup on the grey tube, all hardware',
                      parts={'Cu cup (target backing)': cup(), f'grey flange + tube ({gm})': grey(gm, gw), **hw},
                      vf=on_cup()),
        'window': dict(label='Ø20 tilted diamond window (200 µm, Ti rings) on a 55 mm Al end piece, same line behind',
                       parts={'window + Ti rings (target backing)': win, 'Al end piece 0.5 mm': end,
                              f'grey flange + tube ({gm})': grey(gm, gw, y0=-55.0), **hardware(dy=-39.0)},
                       vf=SH.on_plane(n)),
        'glued': dict(label=f'Cu cup R 17.5 mm, 300 µm, glued straight onto a DN40 tube ({glue_mat}), no rim or flange',
                      parts={'Cu cup (target backing)': SH.dome(17.5, t_um=300, flange_mm=0, tube=glue_mat,
                                                                tube_t=GLUED[glue_mat][1])[:1],
                             f'tube behind the cup ({glue_mat})': SH.dome(17.5, t_um=300, flange_mm=0, tube=glue_mat,
                                                                          tube_t=GLUED[glue_mat][1])[1:], **hw},
                      vf=on_cup(17.5)),
        'window_on_grey': dict(label='the same window straight on the grey flange (16 mm end piece), line as photographed',
                               parts={'window + Ti rings (target backing)': win,
                                      'Al end piece 0.5 mm': short_end(end),
                                      f'grey flange + tube ({gm})': grey(gm, gw), **hw},
                               vf=SH.on_plane(n)),
    }, hw_all


def short_end(end):
    return [Solid(s.mat, s.A[:-1] + [S(slab, Y, -16.0, INF)], s.B) for s in end]


def main():
    V, U, T = SH.legs()
    est = calib()
    th = np.degrees(np.arccos(np.concatenate([u[:, 1] for u in U])))
    rows, prof = [], []
    for gmat in GREY:
        vs, _ = variants(gmat, gmat if gmat in GLUED else 'SS')
        for key, v in vs.items():
            if key == 'glued' and gmat not in GLUED:
                continue
            parts = v['parts']
            if gmat != 'PVC' and key not in ('photo', 'glued'):  # material scans only for the cups
                continue
            p = v['vf'](V)
            allg = [s for g in parts.values() for s in g]
            r_all = SH.trace(allg, V, U, T, v['vf'])
            s_all, d_all = est(r_all['sig_ms'])
            rows.append(dict(variant=key, grey=gmat, part='all', pairs_crossing=1.0, legs_crossing=1.0,
                             x_med_crossing=np.median(np.concatenate([SH.xx0(allg, p, u) for u in U])),
                             theta0_med_crossing=np.nan, sigma68_est=s_all, days_est=d_all,
                             d_sigma68=np.nan, d_days=np.nan))
            for name, geo in parts.items():
                xl = [SH.xx0(geo, p, u) for u in U]
                x = np.concatenate(xl)
                hit = x > 0
                t0 = np.degrees(SH.highland(x, np.concatenate(T)))
                rest = [s for nm, g in parts.items() if nm != name for s in g]
                s_wo, d_wo = est(SH.trace(rest, V, U, T, v['vf'])['sig_ms'])
                rows.append(dict(variant=key, grey=gmat, part=name,
                                 pairs_crossing=((xl[0] > 0) | (xl[1] > 0)).mean(), legs_crossing=hit.mean(),
                                 x_med_crossing=np.median(x[hit]) if hit.any() else 0.0,
                                 theta0_med_crossing=np.median(t0[hit]) if hit.any() else 0.0,
                                 sigma68_est=np.nan, days_est=np.nan,
                                 d_sigma68=s_all - s_wo, d_days=d_all - d_wo))
                if gmat == 'PVC':
                    for lo in range(45, 135, 15):
                        s = (th >= lo) & (th < lo + 15)
                        prof.append(dict(variant=key, part=name, theta_lo=lo, x_med=np.median(x[s]),
                                         f_cross=(x[s] > 0).mean()))
    df = pd.DataFrame(rows)
    df.to_csv(OUT / 'beamline_trace.csv', index=False)
    pd.DataFrame(prof).to_csv(OUT / 'beamline_theta_profile.csv', index=False)
    pd.set_option('display.width', 220)
    print(df.to_string(index=False, float_format=lambda v: f'{v:.3g}'))
    clash()
    export_viz(V, U, T)


def clash():
    """which hardware enters the arms' envelopes or their view, as a function of the target position y_t
    (y_t > 0: target downstream of the detector centre).  Hardware positions are relative to the target."""
    hw = [  # name, y range rel. target (mm), radial reach (mm), direction
        ('Cu cup + rim', (-16, 0), 15, 'all'), ('grey flange', (-27, -16), 33, 'all'),
        ('grey tube', (-165, -27), 24, 'all'), ('KF clamp', (-185, -165), 40, 'all'),
        ('stand post (to the floor)', (-195, -155), 1200, 'down'), ('tee + bellows', (-430, -240), 175, 'down'),
        ('gate valve body', (-395, -350), 75, 'up'), ('valve actuator', (-392, -352), 210, 'up'),
        ('tee to pump cross', (-500, -460), 400, 'down'), ('DN63 CF flanges', (-620, -585), 57, 'all')]
    rows = []
    for yt in (-100, -50, 0, 50, 120, 180):
        for name, (a, b), r, d in hw:
            ya, yb = a + yt, b + yt        # in detector coordinates
            near = min(abs(ya), abs(yb)) if ya * yb > 0 else 0.0
            in_view = r >= 1.134 * near and r > 0 and near < ARM['mm_half'] * 1.2
            hits_mm = r >= ARM['mm_face'] and yb > -ARM['mm_half'] and ya < ARM['mm_half']
            hits_stack = r >= ARM['mm_face'] + 110 and yb > -ARM['stack_half'] and ya < ARM['stack_half']
            rows.append(dict(y_target=yt, part=name, y_from=ya, y_to=yb, r_max=r, side=d,
                             clash=bool(hits_mm or hits_stack), in_view_of_vertex=bool(in_view)))
    c = pd.DataFrame(rows)
    c.to_csv(OUT / 'beamline_clash.csv', index=False)
    print(c[c.y_target == 0].to_string(index=False))


def export_viz(V, U, T, n_pairs=160, seed=3):
    vs, _ = variants('PVC')
    pick = np.random.default_rng(seed).choice(len(V), n_pairs, replace=False)
    out = {}
    for key, v in vs.items():
        p = v['vf'](V)
        parts = list(v['parts'].items())
        xs = [[SH.xx0(g, p, u) for u in U] for _, g in parts]   # part × leg × pair
        pairs = []
        for i in pick:
            per = [[round(float(xs[k][j][i]) * 100, 3) for k in range(len(parts))] for j in range(2)]
            pairs.append([*np.round(p[i], 2), *np.round(U[0][i], 3), *np.round(U[1][i], 3), per[0], per[1]])
        out[key] = dict(label=v['label'], parts=[nm for nm, _ in parts], pairs=pairs)
    tr = pd.read_csv(OUT / 'beamline_trace.csv')
    out['table'] = json.loads(tr.round(5).to_json(orient='records'))
    out['clash'] = json.loads(pd.read_csv(OUT / 'beamline_clash.csv').to_json(orient='records'))
    pr = pd.read_csv(OUT / 'beamline_theta_profile.csv')
    out['prof'] = json.loads(pr.round(5).to_json(orient='records'))
    js = json.dumps(out, ensure_ascii=False, separators=(',', ':'))
    (OUT / 'beamline_viz.json').write_text(js)
    page = HERE.parent / 'viz' / 'lnl_beamline_3d.html'
    if page.exists():
        t = page.read_text()
        a, b = '// BEAMLINE_DATA_BEGIN', '// BEAMLINE_DATA_END'
        if a in t:
            i, j = t.index(a), t.index(b)
            page.write_text(t[:i] + a + '\nconst BL = ' + js + ';\n' + t[j:])
            print(f'beamline data → {page.name} ({len(js) / 1e3:.0f} kB)')


if __name__ == '__main__':
    main()
