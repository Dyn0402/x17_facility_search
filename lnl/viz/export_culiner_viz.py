"""Data for the "Al ogive + Cu liner" tab of lnl_target_design.html (CU_LINER.md, 2026-11-04).

Writes the JSON blob between // CULINER_DATA_BEGIN and // CULINER_DATA_END in lnl/viz/lnl_target_design.html:
  - the ogive's inner surface (CAD, tip at y = 0, beam +y) with inward normals, from opt_cu_liner.surface;
  - the Cu / Li thickness profiles (culiner_profile.csv), the landing table (culiner_landing.csv);
  - the coating geometry: source on the axis, the aperture radii that stop Cu at r 10 and Li at r 4;
  - Geant4 L11/L12 rows for the comparison table (days: lnl/target/shapes/nd_reach_io.py, the reference fit; σ68 and
    EPC share: geant_acceptance.csv, geant_reach.csv);
  - 120 accepted X17 pairs (Geant4 L9, re-placed on the tip by opt_sketch.py), kept where the Li is (r <= 4), with the
    Al each leg crosses (thin-wall trace through a 0.4 mm wall, ESTIMATE).

    ~/PycharmProjects/nTof_x17/.venv/bin/python lnl/viz/export_culiner_viz.py
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
LNL = HERE.parent
sys.path.insert(0, str(LNL / 'target'))
import opt_cu_liner as CL  # noqa: E402

HTML = HERE / 'lnl_target_design.html'
OP = LNL / 'out' / 'target' / 'options'
SH = LNL / 'out' / 'target' / 'shapes'

R_CU, R_LI, T_AL = 10.0, 4.0, 0.4          # design: Cu to r 10, Li mask r 4, wall 0.4 mm
Y_SRC, Y_AP = -150.0, -72.0                # source on the axis 150 mm upstream of the tip; aperture plate 9 mm below the base


def r3(v, d=3):
    return [round(float(x), d) for x in v]


RIN_MAX = 24.776


def al_crossed(v, d, t=T_AL, x0=88.97):
    """% X0 of Al a leg from v (x, y, z) along d crosses: march to where it leaves the cavity, t / cos at that point."""
    p = v + d * 0.01
    for _ in range(4000):
        p = p + d * 0.05
        r = float(np.hypot(p[0], p[2]))
        if p[1] < -62.97:                       # out through the open base: no Al (the line is behind)
            return 0.0
        if r >= RIN_MAX or p[1] > float(CL.surface(np.array([r]))[0][0]):
            _, nr, ny, _ = CL.surface(np.array([min(r, RIN_MAX - 1e-3)]))
            ph = np.arctan2(p[2], p[0])
            n_out = -np.array([nr[0] * np.cos(ph), ny[0], nr[0] * np.sin(ph)])
            c = abs(float(d @ n_out))
            return 100 * t / max(c, 0.05) / x0
    return 0.0


def main():
    html = HTML.read_text()
    a, b = '// CULINER_DATA_BEGIN', '// CULINER_DATA_END'
    # ---- inner surface
    rr = np.r_[np.linspace(0, CL.RCE, 21), np.linspace(CL.RCE + 0.05, 24.77, 110)]
    y, nr, ny, cinc = CL.surface(rr)
    inner = [r3(q) for q in zip(rr, y, nr, ny, cinc)]
    y_base = float(y[-1])
    # ---- coating geometry: aperture radius that ends the deposit at wall radius r_w (rays from the source point)
    ap = {}
    for k, rw in (('cu', R_CU), ('li', R_LI)):
        yw = float(CL.surface(np.array([rw]))[0][0])
        ap[k] = rw * (Y_AP - Y_SRC) / (yw - Y_SRC)
    # ---- profiles, landing
    prof = pd.read_csv(OP / 'culiner_profile.csv')
    pcols = ['rho_mm', 'inc_deg', 'Cu_normal_uniform', 'Cu_beam_uniform', 'Cu_normal_los150', 'Cu_beam_los150',
             'Cu_normal_los400', 'Cu_beam_los400', 'Li_beam_uniform_ug', 'Li_beam_los150_ug']
    profile = {c: r3(prof[c], 3) for c in pcols}
    land = pd.read_csv(OP / 'culiner_landing.csv').round(6).to_dict('records')
    # ---- Geant4 rows
    GR, GA = pd.read_csv(SH / 'geant_reach.csv'), pd.read_csv(SH / 'geant_acceptance.csv')

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'target' / 'shapes'))
    import nd_reach_io as nd

    def g4(cfg, ep=1100.0, col='days_fit', det='bigP', resp=nd.CAL):
        if col == 'days_fit':     # days: the reference fit (nd_reach.csv, FEASIBILITY_SIM.md §19); EPC from geant_reach.csv
            v = nd.best(cfg, det, ep, resp)
            return round(v, 4) if np.isfinite(v) else None
        q = GR[(GR.config == cfg) & (GR.det == det) & (GR.Ep_keV == ep)]
        return round(float(q[col].iloc[0]), 4) if len(q) else None

    def sig(cfg):
        q = GA[(GA.config == cfg + '_bigP') & (GA['sample'] == 'x17')]
        return round(float(q.sigma68_deg.iloc[0]), 2) if len(q) else None

    # label, reach config, σ config, MM x-ray occupancy per arm per µA (CU_LINER §6–7), highlight
    des = [('his Cu ogive, 200 µm', 'ogCu200_los', 'ogCu200', 0.001, 0),
           ('Al 300 + Mo 8 (L11)', 'ogAl300mo8_los', 'ogAl300mo8', 0.19, 0),
           ('Al 300 + Cu 12 at r ≤ 8, Li r ≤ 4', 'ogAl300cu12r8m4', 'ogAl300cu12r8m4', 0.12, 1),
           ('Al 400 + Cu 12 at r ≤ 8, Li r ≤ 4', 'ogAl400cu12r8m4', 'ogAl400cu12r8m4', 0.025, 1),
           ('Al 300 + Cu 30 at r ≤ 8, Li r ≤ 4', 'ogAl300cu30r8m4', 'ogAl300cu30r8m4', 0.05, 0),
           ('Al 300 + Ti 15 at r ≤ 8, Li r ≤ 4', 'ogAl300ti15r8m4', 'ogAl300ti15r8m4', 0.0, 0)]
    rows = []
    for lab, rc, sc, occ, hl in des:
        rows.append(dict(label=lab, sigma68=sig(sc), days110=g4(rc), days103=g4(rc, 1030.0), asb=g4(rc, det='asb'),
                         asb_ntof=g4(rc, det='asb', resp=nd.AS_NTOF),
                         epc=g4(rc, col='B_epc_share'), occ=occ, hl=hl))
    # ---- pairs (re-use the sketch tab's L9 pairs, placed on the tip), keep r <= 4, Al crossed per leg
    s = html
    m = re.search(r'// SKETCH_DATA_BEGIN\nconst SKD = (.*?);\n// SKETCH_DATA_END', s, re.S)
    skd = json.loads(m.group(1))
    pairs = []
    for q in skd['pairs']['Be']:
        v = np.array(q[:3])
        rv = float(np.hypot(v[0], v[2]))
        if rv > R_LI:
            continue
        xs = []
        for o in (3, 6):
            d = np.array(q[o:o + 3]); d /= np.linalg.norm(d)
            xs.append(round(al_crossed(v, d), 3))
        pairs.append(r3(q[:9], 3) + xs)
    data = dict(inner=inner, y_base=round(y_base, 3), r_cu=R_CU, r_li=R_LI, t_al=T_AL, y_src=Y_SRC, y_ap=Y_AP,
                ap={k: round(v, 3) for k, v in ap.items()}, profile=profile, landing=land, rows=rows, pairs=pairs[:140])
    blob = f'{a}\nconst CLD = {json.dumps(data, separators=(",", ":"), ensure_ascii=False)};\n{b}'
    i, j = html.index(a), html.index(b) + len(b)
    HTML.write_text(html[:i] + blob + html[j:])
    print(f'{HTML}: {len(pairs)} pairs (kept {min(len(pairs), 140)}), apertures {ap}, base y {y_base:.2f}')


if __name__ == '__main__':
    main()
