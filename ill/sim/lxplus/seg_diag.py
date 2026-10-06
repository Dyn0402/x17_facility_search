#!/usr/bin/env python3
"""
seg_diag.py -- who survives the Micromegas segment cut?

Pass fractions of the per-arm segment cut (conservative.seg_pass) for
  X17 (both legs), selected as the analysis (strict, Esum > 13 MeV)
  accidental singles: strict arms of C1 + C1w, weight-summed, split hard
      (arm energy > 6 MeV, the ones that make the Esum tail) / all
  ³He(n,γ) correlated two-arm events (C1g)
  cosmic two-arm events (K1), Esum > 13 MeV
vs direction error sigma_theta and DCA cut D, and with/without fdom > 0.7.
Also writes the DCA distributions for the plots.

    python3 seg_diag.py -o seg_diag_G1.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import conservative as C              # noqa: E402
import sim_feasibility as SF          # noqa: E402

MENU, ECUT = "strict", 13.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", type=Path, required=True)
    a = ap.parse_args()
    rng = np.random.default_rng(9)
    E = C.E
    x = SF.load_s1(E / "S1" / "summary", C.CFG, "X17")
    xs = C.seg_for_s1("X17")
    selx = C._s1_select(x, MENU, ECUT)
    tabs = {r: SF.load_table(E / "contracts", r, C.CFG) for r in ("C1", "C1w", "C1g")}
    tabs["K1"] = SF.load_table(E / "contracts", "K1", "G5")
    seg = {r: C.seg_for_table(E / (r if r != "K1" else "K1") / (C.CFG if r != "K1" else "G5"), t)
           for r, t in tabs.items()}

    # populations: list of (weights, list of per-arm (c, d, f, n) tuples that must all pass)
    pops = {}
    lp = lambda p: (xs[f"{p}_c_dom"][selx], xs[f"{p}_d_dom"][selx], xs[f"{p}_fdom"][selx], xs[f"{p}_n_dom"][selx])  # noqa: E731
    pops["X17"] = (np.ones(selx.sum()), [lp("em"), lp("ep")])
    for hard in (False, True):
        W, legs = [], []
        for r in ("C1", "C1w"):
            t, g = tabs[r], seg[r]
            ok = C._arm_ok(t, MENU, "a") & ~SF.he3ng_rows(t)[:, None]
            if hard:
                ok &= SF.arm_E(t, "a") > 6.0
            i, k = np.nonzero(ok)
            W.append(t["w"][i].astype(float))
            legs.append((g["c_dom"][i, k], g["d_dom"][i, k], g["fdom"][i, k], g["n_dom"][i, k]))
        cat = [np.concatenate([L[j] for L in legs]) for j in range(4)]
        pops["singles (hard >6 MeV)" if hard else "singles (all)"] = (np.concatenate(W), [tuple(cat)])
    for r, name in (("C1g", "3He(n,g) 2-arm"), ("K1", "cosmic 2-arm")):
        t, g = tabs[r], seg[r]
        ok = C._arm_ok(t, MENU, "p")
        Ea = np.where(ok, SF.arm_E(t, "p"), -1.0)
        o = np.argsort(-Ea, 1)
        rr = np.arange(len(Ea))
        a1, a2 = o[:, 0], o[:, 1]
        m = (Ea[rr, a1] >= 0) & (Ea[rr, a2] >= 0) & (Ea[rr, a1] + Ea[rr, a2] > ECUT)
        if r == "C1g":
            m &= SF.he3ng_rows(t)
        leg = lambda aa: tuple(g[k][rr[m], aa[m]] for k in C.SEG_KEYS)  # noqa: E731
        pops[name] = (t["w"][m].astype(float), [leg(a1), leg(a2)])

    out = dict(raw={k: int(len(v[0])) for k, v in pops.items()}, grid=[], dca={})
    for deg in (0, 2, 5, 10, 20):
        for D in (25, 40, 60, 100):
            for fq in (0.0, 0.7):
                row = dict(deg=deg, D=D, fq=fq)
                for name, (w, legs) in pops.items():
                    ok = np.ones(len(w), bool)
                    for (c, d, f, n) in legs:
                        ok &= C.seg_pass(c, d, f, n, deg, D, fq, rng)
                    row[name] = float((w * ok).sum() / max(w.sum(), 1e-300))
                out["grid"].append(row)
                print(" ".join(f"{k}={v:.3g}" if isinstance(v, float) else f"{k}={v}" for k, v in row.items()),
                      flush=True)
    bins = np.r_[0:200:5]
    for name, (w, legs) in pops.items():
        c, d = legs[0][0], legs[0][1]
        r, y = C.dca_beam(np.nan_to_num(c), np.nan_to_num(d, nan=1.0))
        out["dca"][name] = np.histogram(r, bins, weights=w)[0].tolist()
    out["dca_bins"] = bins.tolist()
    a.out.write_text(json.dumps(out, indent=1))
    print("wrote", a.out, out["raw"])


if __name__ == "__main__":
    main()
