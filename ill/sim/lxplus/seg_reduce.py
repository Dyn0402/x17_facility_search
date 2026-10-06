#!/usr/bin/env python3
"""
seg_reduce.py -- per-arm Micromegas track segments from mx17_full_sim output.

The feasibility tables (ill_accounting.py) keep only the charge centroid of each
arm's drift gap.  This adds what a micro-TPC reconstruction would see: a line fit
of the charged-particle steps in each arm's 30 mm drift gap, so the analysis can
ask "does this segment point back to the beam spot?" and "is it one clean track?".

    python3 seg_reduce.py <file_t0.root> -o <part_seg.npz>

Per event with charged DriftGas steps, per arm (shape (n_ev, 4[, 3])):
    e, n           summed edep [MeV] and number of steps
    c_all, d_all   centroid and principal axis of all charged steps (positions
    lam_all        smeared 0.5 mm, as ill_pairs.py) and the three PCA eigenvalues
                   [mm^2, ascending]
    c_dom, d_dom,  the same for the dominant track only (trackID with the largest
    lam_dom, n_dom edep in that arm): what a micro-TPC fit locks onto
    fdom           dominant track's share of the arm's edep (1 = one clean track)
NaN where a fit has < 3 steps.  Event IDs are those of the ROOT file, so rows join
to ill_accounting tables (ev + file_index * 1e9) and to ill_pairs parts.
"""
from __future__ import annotations

import argparse
import zlib
from pathlib import Path

import numpy as np

SMEAR_MM = 0.5
BR = ["eventID", "trackID", "armID", "detType", "particle", "edep", "gx", "gy", "gz"]
NEUTRAL = {"gamma", "neutron"}


def _s(a):
    return np.array([x.decode() if isinstance(x, bytes) else str(x) for x in a])


def _pca(inv, X, ng):
    n = np.bincount(inv, minlength=ng).astype(float)
    nn = np.maximum(n, 1)[:, None]
    mean = np.stack([np.bincount(inv, X[:, k], minlength=ng) for k in range(3)], 1) / nn
    Xc = X - mean[inv]
    M = np.empty((ng, 3, 3))
    for a in range(3):
        for b in range(a, 3):
            M[:, a, b] = M[:, b, a] = np.bincount(inv, Xc[:, a] * Xc[:, b], minlength=ng) / nn[:, 0]
    lam, vec = np.linalg.eigh(M)
    d = vec[:, :, 2]
    bad = n < 3
    d[bad] = np.nan
    lam[bad] = np.nan
    return n, mean, d, lam


def process(t, rng, out):
    det = _s(t["detType"])
    prt = _s(t["particle"])
    m = (det == "DriftGas") & ~np.isin(prt, list(NEUTRAL))
    if not m.any():
        return
    ev = t["eventID"][m].astype(np.int64)
    arm = t["armID"][m].astype(np.int64)
    tid = t["trackID"][m].astype(np.int64)
    e = t["edep"][m].astype(float) * 1e-6
    X = np.stack([t["gx"][m], t["gy"][m], t["gz"][m]], 1).astype(float)
    X = X + rng.normal(0, SMEAR_MM, X.shape)
    key = ev * 4 + arm
    uk, inv = np.unique(key, return_inverse=True)
    ng = len(uk)
    E = np.bincount(inv, e, minlength=ng)
    n, c, d, lam = _pca(inv, X, ng)
    # dominant track per (event, arm)
    k2 = inv.astype(np.int64) * (int(tid.max()) + 1) + tid
    u2, i2 = np.unique(k2, return_inverse=True)
    e2 = np.bincount(i2, e)
    g2 = u2 // (int(tid.max()) + 1)
    order = np.lexsort((-e2, g2))
    first = np.r_[True, g2[order][1:] != g2[order][:-1]]
    dom = np.full(ng, -1, np.int64)
    dom[g2[order][first]] = u2[order][first]
    fdom = np.zeros(ng)
    fdom[g2[order][first]] = e2[order][first]
    fdom /= np.maximum(E, 1e-30)
    md = k2 == dom[inv]
    nd, cd, dd, ld = _pca(inv[md], X[md], ng)
    out.append(dict(ev=uk // 4, arm=uk % 4, e=E, n=n, c_all=c, d_all=d, lam_all=lam,
                    c_dom=cd, d_dom=dd, lam_dom=ld, n_dom=nd, fdom=fdom))


def reduce_file(fp, outp, step="200 MB"):
    import uproot
    rng = np.random.default_rng(zlib.crc32(Path(fp).name.encode()))
    out = []
    keep = {k: [] for k in BR}
    with uproot.open(fp) as f:
        # ill_accounting sorts hits by event, so do not assume stepping order
        for t in f["HitTree"].iterate(BR, library="np", step_size=step):
            m = _s(t["detType"]) == "DriftGas"
            for k in BR:
                keep[k].append(t[k][m])
    t = {k: np.concatenate(v) for k, v in keep.items()}
    if len(t["eventID"]):
        process(t, rng, out)
    if not out:
        np.savez_compressed(outp, ev=np.zeros(0, np.int64))
        return
    R = {k: np.concatenate([o[k] for o in out]) for k in out[0]}
    evs, row = np.unique(R["ev"], return_inverse=True)
    res = dict(ev=evs)
    for k, v in R.items():
        if k in ("ev", "arm"):
            continue
        shp = (len(evs), 4) + v.shape[1:]
        a = np.full(shp, np.nan if k not in ("e", "n", "n_dom", "fdom") else 0, np.float32)
        a[row, R["arm"]] = v
        res[k] = a
    np.savez_compressed(outp, **res)
    print(f"{fp}: {len(evs)} events with gap charge -> {outp}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    reduce_file(a.file, a.out)
