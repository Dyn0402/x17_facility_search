#!/usr/bin/env python3
"""
gdiag.py -- why G (³He(n,γ) correlated two-arm fakes) is 143/cycle in the CFRP
fit and exactly 0 in the flight-tube fits, which read the same C1g_G1 table.

conservative.py draws every table's segment smearing from one shared rng, in
the order S1, C1, C1w, C1g, K1.  C1/C1w differ per variant, so C1g sees a
different draw.  Here: the raw ³He(n,γ) two-arm events, and the G template
over many independent seeds (light: C1g is 6 MB; runs on the login node).

    python3 gdiag.py [--seeds 400]
"""
from __future__ import annotations

import argparse

import numpy as np

import conservative as C
import sim_feasibility as SF

R, DAYS = 1.9e10, 50.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=400)
    a = ap.parse_args()
    C.COLL_DEG = 20.0
    t0 = SF.load_table(C.E / "contracts", "C1g", "G1")
    g = C.seg_for_table(C.E / "C1g" / "G1", t0)
    he = SF.he3ng_rows(t0)
    nabs = R * DAYS * SF.DAY
    print(f"C1g: {len(t0['ev'])} rows, ³He(n,γ) rows {he.sum()}, absorbed {t0['absorbed']:.3g}, "
          f"weight/row {np.median(t0['w'][he]):.3g}")
    w = (SF.CENTRES >= 60) & (SF.CENTRES <= 180)
    for menu, ecut in (("strict", 13.0), ("strict", 14.0)):
        # raw events before any segment cut
        t = dict(t0)
        m, th, es, _, p = C._two_arm_events(t, menu, ecut)
        m &= he
        idx = np.flatnonzero(m & (p > 1e-3))
        per = t["w"][idx].astype(float) * p[idx] / t["absorbed"] * nabs
        print(f"\n== {menu}, Esum > {ecut}: {len(idx)} raw ³He(n,γ) two-arm events with P(Esum) > 1e-3, "
              f"no segment cut: {per.sum():.0f} / cycle (1.9e10, 50 d, before live/occ)")
        # per seed, with segments + collinearity
        Gs, passes = [], np.zeros(len(idx))
        for s in range(a.seeds):
            rng = np.random.default_rng(1000 + s)
            t = dict(t0)
            t["segok"], t["segd"] = C.seg_pass(g["c_dom"], g["d_dom"], g["fdom"], g["n_dom"], 3, 30, 0.0, rng, True)
            m2, th2, _, _, p2 = C.two_arm_events(t, menu, ecut)
            m2 &= he
            passes += m2[idx] * p2[idx]
            h, _ = np.histogram(th2[m2], SF.BINS, weights=t["w"][m2].astype(float) * p2[m2])
            Gs.append(h[w].sum() / t["absorbed"] * nabs)
        Gs = np.array(Gs)
        print(f"   with 3°/30 mm segments + 20° collinearity, {a.seeds} seeds: mean {Gs.mean():.1f}, "
              f"median {np.median(Gs):.1f}, P(G = 0) {np.mean(Gs == 0):.2f}, p16-p84 "
              f"{np.percentile(Gs, 16):.0f}-{np.percentile(Gs, 84):.0f}, max {Gs.max():.0f} / cycle")
        print("   raw events: θ  Esum  P(Esum)  per-cycle  P(seg+coll pass)  arms-with-segment")
        o = np.argsort(-per)
        for k in o[:15]:
            i = idx[k]
            nseg = int(np.sum(np.nan_to_num(g["n_dom"][i]) >= 3))
            print(f"   {th[i]:6.1f} {es[i]:6.2f} {p[i]:6.3f} {per[k]:8.1f} {passes[k] / a.seeds:8.3f}   {nseg}")


if __name__ == "__main__":
    main()
