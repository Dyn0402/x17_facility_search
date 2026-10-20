#!/usr/bin/env python3
"""
trig_threshold.py -- how high can the big-plastic leg threshold go, and what does splitting a plate cost?
=========================================================================================================
    python3 trig_threshold.py --t1 <T1 parts dir> -o <outdir>

Input: the T1 trig_reduce.py parts (oversized 78 x 120 x 10 cm slab per arm, G1 cell), as for trig_accept.py.
Selection as trig_accept.py (MM active area, all 20 SiPM bars > 0.5 MIP, both legs, different arms), but the
plastic leg threshold is scanned, for the 78 x 80 and 70 x 70 cut-outs at T = 2-6 cm.

Why: a gamma's Compton deposit is capped near E_gamma whatever the thickness, while a lepton crossing the slab
leaves ~2 MeV per cm.  A thick slab can therefore run a threshold that scales with T and stays blind to
H-capture (2.22 MeV) and natural (<= 2.6 MeV) gammas.  This scan gives the signal price of that threshold.

Splitting: one plate per arm cut into N bars along u (bars run along the beam, read at both v ends as now).
The leptons' entry points (ent_uv) give the fraction landing within d of a seam, where the deposit can be
shared between two bars.  The arm's E_sum is the sum of its bars, so sharing only matters for a per-bar trigger
threshold.  Outputs: thr_X17.csv / thr_M1.csv and seams.csv.
"""
import argparse
import csv
from pathlib import Path

import numpy as np

from trig_accept import load, mm_ok, sipm, summarize, SIPM_THR

THRS = [0.5, 1.0, 1.67, 2.5, 3.0, 4.0, 5.0, 6.0, 8.0]
SIZES = [(78, 80), (70, 70)]
TS = [2, 3, 4, 5, 6]


def scan(R, rng):
    W, Lc, T = list(R["W_cm"]), list(R["L_cm"]), list(R["T_cm"])
    mm = [mm_ok(R, p) for p in ("em", "ep")]
    s20 = [sipm(R, p, 20) for p in ("em", "ep")]
    g = [R[f"{p}_grid"] for p in ("em", "ep")]
    rows = []
    for w, l in SIZES:
        iw, il = W.index(w), Lc.index(l)
        for t in TS:
            it = T.index(t)
            pl = [g[i][:, iw, il, it] for i in range(2)]
            for thr in THRS:
                legs = [mm[i] & (s20[i] > SIPM_THR) & (pl[i] > thr) for i in range(2)]
                r = summarize(R, legs, [s20[i] + pl[i] for i in range(2)], rng)
                rows.append(dict(W_cm=w, L_cm=l, T_cm=t, thr_MeV=thr, thr_per_cm=round(thr / t, 3), **r))
    return rows


def seams(R, w=78.0, l=80.0, t=5.0, thr=1.67):
    """Fraction of accepted legs entering within d of a bar boundary, for N bars across u."""
    W, Lc, T = list(R["W_cm"]), list(R["L_cm"]), list(R["T_cm"])
    iw, il, it = W.index(w), Lc.index(l), T.index(t)
    u = []
    for p in ("em", "ep"):
        ok = mm_ok(R, p) & (sipm(R, p, 20) > SIPM_THR) & (R[f"{p}_grid"][:, iw, il, it] > thr)
        u.append(R[f"{p}_ent_uv"][ok, 0] / 10.0)          # cm, centred on the plate
    u = np.concatenate(u)
    u = u[np.isfinite(u)]
    out = []
    for n in (1, 2, 3, 4):
        edges = -w / 2 + w * np.arange(1, n) / n
        dmin = np.min(np.abs(u[:, None] - edges[None, :]), 1) if n > 1 else np.full(len(u), np.inf)
        bar = np.clip(((u + w / 2) // (w / n)).astype(int), 0, n - 1)
        occ = np.bincount(bar, minlength=n) / len(u)
        out.append(dict(N=n, bar_width_cm=round(w / n, 1), n_legs=len(u),
                        within_1cm=float(np.mean(dmin < 1)), within_2p5cm=float(np.mean(dmin < 2.5)),
                        within_5cm=float(np.mean(dmin < 5)), max_bar_share=float(occ.max())))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--t1", required=True)
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(23)
    for ch in ("X17", "M1"):
        R = load(a.t1, ch)
        rows = scan(R, rng)
        with open(out / f"thr_{ch}.csv", "w", newline="") as f:
            wr = csv.DictWriter(f, fieldnames=list(rows[0]))
            wr.writeheader()
            wr.writerows(rows)
        if ch == "X17":
            sm = seams(R)
            with open(out / "seams.csv", "w", newline="") as f:
                wr = csv.DictWriter(f, fieldnames=list(sm[0]))
                wr.writeheader()
                wr.writerows(sm)
            for r in sm:
                print(r)
        for r in rows:
            if r["W_cm"] == 78:
                print(ch, r["T_cm"], r["thr_MeV"], round(r["acc"], 4), round(r["acc_E13"], 4))


if __name__ == "__main__":
    main()
